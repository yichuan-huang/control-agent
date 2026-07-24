"""Deterministic controller/model compatibility and replacement policies."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Literal

import numpy as np
from pydantic import Field, model_validator
from scipy import signal

from cfdc.lab.bootstrap import bootstrap_controller_candidate
from cfdc.lab.contracts import (
    ControllerRuntimeSpec,
    PControllerSpec,
    RegisteredControllerSpec,
    StateFeedbackControllerSpec,
)
from cfdc.lab.session import (
    SessionActionError,
    SimulationRunConfig,
    SimulationSession,
    TuningProfile,
    create_discovery_simulation_session,
    make_tuning_profile,
)
from cfdc.models.schemas import (
    CFDCModel,
    ExecutableModelSpec,
    RegisteredNonlinearModelSpec,
    StateSpaceModelSpec,
    TransferFunctionModelSpec,
)

if TYPE_CHECKING:
    from cfdc.lab.model_discovery import ModelDiscoverySession


class ControllerCompatibilityResult(CFDCModel):
    schema_version: Literal[
        "controller_compatibility/v1"
    ] = "controller_compatibility/v1"
    status: Literal["compatible", "replacement_required", "blocked"]
    reasons: list[str] = Field(min_length=1, max_length=20)
    bound_model_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    original_architecture: str = Field(min_length=1)
    selected_controller: ControllerRuntimeSpec | None = None
    selected_tuning_profile: TuningProfile | None = None
    recommended_controller: ControllerRuntimeSpec | None = None
    recommended_tuning_profile: TuningProfile | None = None
    replacement_sha256: str | None = Field(
        default=None, pattern=r"^[0-9a-f]{64}$"
    )
    replacement_policy_id: str | None = Field(
        default=None, min_length=1, max_length=200
    )
    run_config: SimulationRunConfig

    @model_validator(mode="after")
    def validate_decision(self) -> "ControllerCompatibilityResult":
        selected_pair = (
            self.selected_controller,
            self.selected_tuning_profile,
        )
        recommended_pair = (
            self.recommended_controller,
            self.recommended_tuning_profile,
        )
        if (selected_pair[0] is None) != (selected_pair[1] is None):
            raise ValueError("selected controller/profile must resolve together")
        if (recommended_pair[0] is None) != (recommended_pair[1] is None):
            raise ValueError(
                "recommended controller/profile must resolve together"
            )
        if self.status == "compatible":
            if selected_pair[0] is None or any(
                value is not None
                for value in (
                    *recommended_pair,
                    self.replacement_sha256,
                    self.replacement_policy_id,
                )
            ):
                raise ValueError(
                    "compatible decisions require only a selected controller"
                )
        elif self.status == "replacement_required":
            if selected_pair[0] is not None:
                raise ValueError(
                    "replacement decisions cannot preselect a controller"
                )
            if recommended_pair[0] is None:
                if (
                    self.replacement_sha256 is not None
                    or self.replacement_policy_id is not None
                ):
                    raise ValueError(
                        "a blocked replacement cannot carry approval metadata"
                    )
            elif (
                self.replacement_sha256 is None
                or self.replacement_policy_id is None
            ):
                raise ValueError(
                    "a recommended replacement requires hash and policy ID"
                )
        elif any(
            value is not None
            for value in (
                *selected_pair,
                *recommended_pair,
                self.replacement_sha256,
                self.replacement_policy_id,
            )
        ):
            raise ValueError("blocked decisions cannot carry controllers")
        return self


def _experiment_run_config(
    session: "ModelDiscoverySession",
) -> SimulationRunConfig:
    assert session.confirmed_envelope is not None
    experiment = session.confirmed_envelope.experiment_proposal
    return SimulationRunConfig(
        reference=experiment.reference,
        horizon_s=experiment.horizon_s,
        sample_time_s=experiment.sample_time_s,
        actuator_bounds=experiment.actuator_bounds,
        state_bounds=experiment.state_bounds,
        output_bounds=experiment.output_bounds,
    )


def _open_loop_behavior(
    model: ExecutableModelSpec,
) -> Literal["stable", "unstable"]:
    if isinstance(model, RegisteredNonlinearModelSpec):
        return "unstable"
    if isinstance(model, TransferFunctionModelSpec):
        poles = np.roots(np.asarray(model.denominator, dtype=float))
    else:
        poles = np.linalg.eigvals(np.asarray(model.a, dtype=float))
    if model.time_domain == "continuous":
        return (
            "stable"
            if all(pole.real < -1e-6 for pole in poles)
            else "unstable"
        )
    return (
        "stable"
        if all(abs(pole) < 1.0 - 1e-6 for pole in poles)
        else "unstable"
    )


def _profile_for_controller(
    controller: ControllerRuntimeSpec,
    model: ExecutableModelSpec,
    *,
    policy_id: str,
) -> TuningProfile:
    if isinstance(controller, StateFeedbackControllerSpec):
        bindings = {
            f"k_{row}_{column}": f"gain_matrix.{row}.{column}"
            for row, values in enumerate(controller.gain_matrix)
            for column in range(len(values))
        }
        values = {
            name: controller.gain_matrix[int(binding.split(".")[1])][
                int(binding.split(".")[2])
            ]
            for name, binding in bindings.items()
        }
    elif isinstance(controller, RegisteredControllerSpec):
        bindings = {
            name: f"parameters.{name}"
            for name in controller.parameters
        }
        values = dict(controller.parameters)
    elif isinstance(controller, PControllerSpec):
        bindings = {"kp": "kp"}
        values = {"kp": controller.kp}
    else:
        raise ValueError(
            "replacement policy produced an unsupported tunable controller"
        )
    scale = max(
        [abs(value) for value in values.values()] + [1.0]
    )
    return make_tuning_profile(
        controller,
        tunable_parameters=list(bindings),
        parameter_bindings=bindings,
        open_loop_behavior=_open_loop_behavior(model),
        step_fraction=0.05,
        zero_step_scales={
            name: scale
            for name, value in values.items()
            if value == 0.0
        },
        profile_id=policy_id,
    )


def _state_feedback_replacement(
    model: StateSpaceModelSpec,
    run_config: SimulationRunConfig,
) -> tuple[StateFeedbackControllerSpec, TuningProfile]:
    a = np.asarray(model.a, dtype=float)
    b = np.asarray(model.b, dtype=float)
    c = np.asarray(model.c, dtype=float)
    d = np.asarray(model.d, dtype=float)
    n = a.shape[0]
    blocks = [b]
    power = np.eye(n)
    for _ in range(1, n):
        power = power @ a
        blocks.append(power @ b)
    controllability = np.concatenate(blocks, axis=1)
    if np.linalg.matrix_rank(controllability) != n:
        raise ValueError(
            "状态空间模型不可控，无法确定性生成状态反馈替代控制器。"
        )
    if not np.allclose(d, 0.0, rtol=0.0, atol=1e-12):
        raise ValueError(
            "普通 MIMO 自动状态反馈要求 D=0，以避免未审计的直接通道。"
        )
    time_scale = max(
        run_config.horizon_s / 6.0,
        run_config.sample_time_s,
    )
    rates = np.linspace(1.0, 2.0, n) / time_scale
    desired_poles = (
        -rates
        if model.time_domain == "continuous"
        else np.exp(-rates * run_config.sample_time_s)
    )
    try:
        gain = np.asarray(
            signal.place_poles(a, b, desired_poles).gain_matrix,
            dtype=float,
        )
    except ValueError as exc:
        raise ValueError(
            "确定性极点配置失败，当前 MIMO 结构不能生成受支持的替代控制器。"
        ) from exc
    closed_loop = a - b @ gain
    if model.time_domain == "continuous":
        steady_map = -c @ np.linalg.solve(closed_loop, b)
    else:
        steady_map = c @ np.linalg.solve(
            np.eye(n) - closed_loop,
            b,
        )
    reference_gain = np.linalg.pinv(steady_map)
    if not np.allclose(
        steady_map @ reference_gain,
        np.eye(c.shape[0]),
        rtol=1e-7,
        atol=1e-9,
    ):
        raise ValueError(
            "输出参考维度不能由当前输入通道独立跟踪，无法生成参考增益矩阵。"
        )
    controller = StateFeedbackControllerSpec(
        gain_matrix=gain.tolist(),
        reference_gain_matrix=reference_gain.tolist(),
        equilibrium_state=[0.0] * n,
        equilibrium_input=[0.0] * b.shape[1],
    )
    return (
        controller,
        _profile_for_controller(
            controller,
            model,
            policy_id="deterministic_mimo_state_feedback/v1",
        ),
    )


def _registered_replacement(
    model: RegisteredNonlinearModelSpec,
) -> tuple[RegisteredControllerSpec, TuningProfile, str]:
    if model.template_id == "underactuated_cartpole":
        controller = RegisteredControllerSpec(
            controller_id="cartpole_cascaded",
            parameters={
                "kp": 18.15,
                "kd": 8.47,
                "kp_y": 0.02,
                "kd_y": 0.05,
            },
            reference={"position_m": 0.0},
            feedforward={"position_reference_prefilter": 1.0},
            configuration={"theta_reference_limit_rad": 0.08},
        )
        policy_id = "registered_cartpole_conservative_controller/v1"
    else:
        controller = RegisteredControllerSpec(
            controller_id="vtol_cascaded",
            parameters={
                "kp_z": 1.44,
                "kd_z": 2.16,
                "kp_theta": 0.3698,
                "kd_theta": 0.1548,
                "kp_y": 0.34,
                "kd_y": 0.70,
            },
            reference={"x_m": 0.0, "z_m": 0.0},
            feedforward={
                "hover_thrust_n": (
                    model.parameters["mass_kg"]
                    * model.parameters["gravity_m_s2"]
                )
            },
            configuration={"tilt_reference_limit_rad": 0.48},
        )
        policy_id = "registered_vtol_conservative_controller/v1"
    return (
        controller,
        _profile_for_controller(
            controller,
            model,
            policy_id=policy_id,
        ),
        policy_id,
    )


def _is_scalar_controller(
    controller: ControllerRuntimeSpec,
) -> bool:
    return controller.kind in {
        "p",
        "pi",
        "filtered_pd",
        "filtered_pid",
        "lead",
        "lag",
        "notch",
    }


def _linear_io_dimensions(
    model: TransferFunctionModelSpec | StateSpaceModelSpec,
) -> tuple[int, int]:
    if isinstance(model, TransferFunctionModelSpec):
        return 1, 1
    return len(model.input_signal_ids), len(model.output_signal_ids)


def _replacement_hash(
    controller: ControllerRuntimeSpec,
    profile: TuningProfile,
) -> str:
    from cfdc.lab.model_discovery import _sha256

    return _sha256(
        {
            "controller": controller,
            "tuning_profile": profile,
        }
    )


def _decision(
    session: "ModelDiscoverySession",
    *,
    all_states_available: bool,
) -> ControllerCompatibilityResult:
    assert session.confirmed_envelope is not None
    assert session.confirmed_envelope_sha256 is not None
    model = session.confirmed_envelope.model
    candidate = session.stage5.initial_controller_candidate
    run_config = _experiment_run_config(session)
    cutoff = candidate.design_parameters.get("filter_cutoff_rad_s")
    boot = bootstrap_controller_candidate(
        candidate,
        model,
        filter_cutoff_rad_s=cutoff,
    )
    compatible = False
    incompatibility: list[str] = []
    if boot.status == "ready":
        assert boot.controller is not None
        assert boot.tuning_profile is not None
        controller = boot.controller
        if isinstance(model, RegisteredNonlinearModelSpec):
            expected = (
                "cartpole_cascaded"
                if model.template_id == "underactuated_cartpole"
                else "vtol_cascaded"
            )
            compatible = (
                isinstance(controller, RegisteredControllerSpec)
                and controller.controller_id == expected
            )
            if not compatible:
                incompatibility.append(
                    "第五步控制器不是该注册非线性模型的受支持控制器。"
                )
        else:
            input_count, output_count = _linear_io_dimensions(model)
            if _is_scalar_controller(controller):
                compatible = input_count == output_count == 1
                if not compatible:
                    incompatibility.append(
                        "第五步 SISO 控制器不能直接驱动当前 MIMO 模型。"
                    )
            elif isinstance(controller, StateFeedbackControllerSpec):
                compatible = isinstance(model, StateSpaceModelSpec)
                if not compatible:
                    incompatibility.append(
                        "状态反馈要求显式状态空间模型。"
                    )
    else:
        incompatibility.append(
            boot.lock_reason or "第五步控制器无法转换为类型化运行时。"
        )
    if compatible:
        return ControllerCompatibilityResult(
            status="compatible",
            reasons=[
                "第五步控制器的结构、信号维度和运行域与已确认模型兼容。"
            ],
            bound_model_sha256=session.confirmed_envelope_sha256,
            original_architecture=candidate.architecture,
            selected_controller=boot.controller,
            selected_tuning_profile=boot.tuning_profile,
            run_config=run_config,
        )

    recommendation: ControllerRuntimeSpec | None = None
    profile: TuningProfile | None = None
    policy_id: str | None = None
    try:
        if isinstance(model, RegisteredNonlinearModelSpec):
            recommendation, profile, policy_id = _registered_replacement(
                model
            )
        elif isinstance(model, StateSpaceModelSpec) and (
            len(model.input_signal_ids) > 1
            or len(model.output_signal_ids) > 1
        ):
            if not all_states_available:
                incompatibility.append(
                    "只有用户确认所有状态都可获得后，才能生成普通 MIMO 状态反馈。"
                )
            else:
                recommendation, profile = _state_feedback_replacement(
                    model,
                    run_config,
                )
                policy_id = "deterministic_mimo_state_feedback/v1"
        elif candidate.gains.get("kp") is not None:
            recommendation = PControllerSpec(kp=candidate.gains["kp"])
            policy_id = "siso_candidate_gain_fallback/v1"
            profile = _profile_for_controller(
                recommendation,
                model,
                policy_id=policy_id,
            )
    except (ValueError, np.linalg.LinAlgError) as exc:
        incompatibility.append(str(exc))
    if recommendation is None or profile is None or policy_id is None:
        return ControllerCompatibilityResult(
            status="replacement_required",
            reasons=incompatibility
            or ["当前控制器与模型不兼容，且没有可安全生成的替代控制器。"],
            bound_model_sha256=session.confirmed_envelope_sha256,
            original_architecture=candidate.architecture,
            run_config=run_config,
        )
    return ControllerCompatibilityResult(
        status="replacement_required",
        reasons=incompatibility
        or ["第五步控制器与已确认模型不兼容，需要确认替代控制器。"],
        bound_model_sha256=session.confirmed_envelope_sha256,
        original_architecture=candidate.architecture,
        recommended_controller=recommendation,
        recommended_tuning_profile=profile,
        replacement_sha256=_replacement_hash(recommendation, profile),
        replacement_policy_id=policy_id,
        run_config=run_config,
    )


def evaluate_controller_compatibility(
    session: "ModelDiscoverySession",
    *,
    all_states_available: bool = False,
    expected_revision: int | None = None,
) -> "ModelDiscoverySession":
    from cfdc.lab.model_discovery import _expect_revision, _transition

    _expect_revision(
        session,
        session.revision
        if expected_revision is None
        else expected_revision,
    )
    if session.state != "controller_compatibility_check":
        raise SessionActionError(
            "controller compatibility requires a confirmed generated model"
        )
    result = _decision(
        session,
        all_states_available=all_states_available,
    )
    if result.status == "compatible":
        return _transition(
            session,
            action="evaluate_controller_compatibility",
            to_state="simulation_ready",
            updates={
                "compatibility_result": result,
                "selected_controller": result.selected_controller,
                "selected_tuning_profile": (
                    result.selected_tuning_profile
                ),
                "recommended_controller": None,
                "recommended_tuning_profile": None,
                "replacement_sha256": None,
                "bound_model_sha256": result.bound_model_sha256,
                "run_config": result.run_config,
            },
            reason=result.reasons[0],
        )
    return _transition(
        session,
        action="evaluate_controller_compatibility",
        to_state="controller_replacement_review",
        updates={
            "compatibility_result": result,
            "selected_controller": None,
            "selected_tuning_profile": None,
            "recommended_controller": result.recommended_controller,
            "recommended_tuning_profile": (
                result.recommended_tuning_profile
            ),
            "replacement_sha256": result.replacement_sha256,
            "bound_model_sha256": result.bound_model_sha256,
            "run_config": result.run_config,
        },
        reason=result.reasons[0],
    )


def confirm_recommended_controller(
    session: "ModelDiscoverySession",
    *,
    replacement_sha256: str,
    expected_revision: int,
) -> "ModelDiscoverySession":
    from cfdc.lab.model_discovery import _expect_revision, _transition

    _expect_revision(session, expected_revision)
    if session.state != "controller_replacement_review":
        raise SessionActionError(
            "controller replacement confirmation requires replacement review"
        )
    if (
        session.recommended_controller is None
        or session.recommended_tuning_profile is None
        or session.replacement_sha256 is None
    ):
        raise SessionActionError(
            "no safe replacement controller is available for confirmation"
        )
    if replacement_sha256 != session.replacement_sha256:
        raise SessionActionError("replacement controller hash mismatch")
    return _transition(
        session,
        action="confirm_recommended_controller",
        to_state="simulation_ready",
        updates={
            "selected_controller": session.recommended_controller,
            "selected_tuning_profile": (
                session.recommended_tuning_profile
            ),
        },
        reason="The user explicitly approved the hashed replacement controller.",
    )


def create_simulation_from_discovery(
    session: "ModelDiscoverySession",
    *,
    expected_revision: int,
) -> SimulationSession:
    from cfdc.lab.model_discovery import _expect_revision, _sha256

    _expect_revision(session, expected_revision)
    if session.state != "simulation_ready":
        qualifier = (
            "replacement confirmation"
            if session.state == "controller_replacement_review"
            else "model and controller confirmation"
        )
        raise SessionActionError(
            f"simulation requires {qualifier} before it can run"
        )
    if (
        session.confirmed_envelope is None
        or session.confirmed_envelope_sha256 is None
        or session.selected_controller is None
        or session.selected_tuning_profile is None
        or session.run_config is None
        or session.bound_model_sha256
        != session.confirmed_envelope_sha256
    ):
        raise SessionActionError(
            "simulation-ready discovery state is incomplete or unbound"
        )
    link_sha256 = _sha256(
        {
            "stage5_sha256": session.stage5_sha256,
            "model_sha256": session.confirmed_envelope_sha256,
            "controller": session.selected_controller,
            "tuning_profile": session.selected_tuning_profile,
            "run_config": session.run_config,
        }
    )
    return create_discovery_simulation_session(
        source_run_id=session.stage5.source_run_id,
        source_plant_id=session.confirmed_envelope_sha256,
        source_candidate_plant_id=(
            session.stage5.initial_controller_candidate.plant_id
        ),
        source_controller_architecture=(
            session.stage5.initial_controller_candidate.architecture
        ),
        source_link_sha256=link_sha256,
        model=session.confirmed_envelope.model,
        controller=session.selected_controller,
        tuning_profile=session.selected_tuning_profile,
        run_config=session.run_config,
        model_assumptions=[
            *session.confirmed_envelope.assumptions,
            *session.confirmed_envelope.limitations,
            (
                "Stability conclusions apply only to the user-confirmed "
                "software model."
            ),
        ][:20],
    )


__all__ = [
    "ControllerCompatibilityResult",
    "confirm_recommended_controller",
    "create_simulation_from_discovery",
    "evaluate_controller_compatibility",
]
