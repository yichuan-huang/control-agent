"""Explicit allowlist for converting five-stage candidates into runtime specs."""

from __future__ import annotations

from typing import Mapping

import numpy as np
from pydantic import Field

from cfdc.lab.contracts import (
    ControllerRuntimeSpec,
    FilteredPDControllerSpec,
    FilteredPIDControllerSpec,
    LagControllerSpec,
    LeadControllerSpec,
    NotchControllerSpec,
    PControllerSpec,
    PIControllerSpec,
    RegisteredControllerSpec,
    StateFeedbackControllerSpec,
)
from cfdc.lab.session import TuningProfile, make_tuning_profile
from cfdc.models.schemas import (
    CFDCModel,
    ControllerCandidate,
    ExecutableModelSpec,
    RegisteredNonlinearModelSpec,
    TransferFunctionModelSpec,
)


class ControllerBootstrapResult(CFDCModel):
    status: str = Field(pattern=r"^(ready|locked)$")
    controller: ControllerRuntimeSpec | None = None
    tuning_profile: TuningProfile | None = None
    lock_reason: str | None = None


_PI_ARCHITECTURES = {
    "detuned_PI",
    "delay_detuned_PI",
    "detuned_PI_with_NMP_undershoot_guard",
}
_PD_ARCHITECTURES = {
    "detuned_PD",
    "small_saturated_PD",
    "unstable_mode_conservative_PD",
    "safe_online_gain_search",
}


def _locked(reason: str) -> ControllerBootstrapResult:
    return ControllerBootstrapResult(status="locked", lock_reason=reason)


def _open_loop_behavior(
    model: ExecutableModelSpec,
) -> str:
    if isinstance(model, RegisteredNonlinearModelSpec):
        return "unstable"
    if isinstance(model, TransferFunctionModelSpec):
        poles = np.roots(np.asarray(model.denominator, dtype=float))
    else:
        poles = np.linalg.eigvals(np.asarray(model.a, dtype=float))
    if model.time_domain == "continuous":
        return "stable" if all(pole.real < -1e-6 for pole in poles) else "unstable"
    return "stable" if all(abs(pole) < 1.0 - 1e-6 for pole in poles) else "unstable"


def bootstrap_controller_candidate(
    candidate: ControllerCandidate,
    model: ExecutableModelSpec,
    *,
    filter_cutoff_rad_s: float | None = None,
    explicit_controller: ControllerRuntimeSpec | None = None,
    parameter_bindings: Mapping[str, str] | None = None,
) -> ControllerBootstrapResult:
    """Convert only exact, audited architectures; never infer from gain names."""

    if candidate.status == "refuse":
        return _locked("the five-stage candidate explicitly refused release")
    architecture = candidate.architecture
    open_loop_behavior = _open_loop_behavior(model)
    declared_cutoff = (
        filter_cutoff_rad_s
        if filter_cutoff_rad_s is not None
        else candidate.design_parameters.get("filter_cutoff_rad_s")
    )

    if architecture in {"P", "proportional", "conservative_P"}:
        if set(candidate.gains) != {"kp"} or set(
            candidate.tunable_gain_names
        ) != {"kp"}:
            return _locked("P conversion requires exact kp tunable")
        controller = PControllerSpec(kp=candidate.gains["kp"])
        bindings = {"kp": "kp"}
    elif architecture in _PI_ARCHITECTURES:
        if set(candidate.gains) < {"kp", "ki"} or set(
            candidate.tunable_gain_names
        ) != {"kp", "ki"}:
            return _locked("PI conversion requires exact kp/ki tunables")
        controller = PIControllerSpec(
            kp=candidate.gains["kp"],
            ki=candidate.gains["ki"],
        )
        bindings = {"kp": "kp", "ki": "ki"}
    elif architecture in _PD_ARCHITECTURES:
        if declared_cutoff is None or declared_cutoff <= 0.0:
            return _locked(
                "filtered PD conversion requires a declared positive cutoff"
            )
        if set(candidate.gains) != {"kp", "kd"} or set(
            candidate.tunable_gain_names
        ) != {"kp", "kd"}:
            return _locked("PD conversion requires exact kp/kd gains")
        controller = FilteredPDControllerSpec(
            kp=candidate.gains["kp"],
            kd=candidate.gains["kd"],
            derivative_source="measurement",
            filter_cutoff_rad_s=declared_cutoff,
        )
        bindings = {"kp": "kp", "kd": "kd"}
    elif architecture in {"filtered_PID", "detuned_PID"}:
        if declared_cutoff is None or declared_cutoff <= 0.0:
            return _locked(
                "filtered PID conversion requires a declared positive cutoff"
            )
        if set(candidate.gains) != {"kp", "ki", "kd"} or set(
            candidate.tunable_gain_names
        ) != {"kp", "ki", "kd"}:
            return _locked("PID conversion requires exact kp/ki/kd gains")
        integrator_limit = candidate.design_parameters.get(
            "integrator_limit"
        )
        if integrator_limit is not None and integrator_limit <= 0.0:
            return _locked("PID integrator_limit must be positive")
        controller = FilteredPIDControllerSpec(
            kp=candidate.gains["kp"],
            ki=candidate.gains["ki"],
            kd=candidate.gains["kd"],
            derivative_source="measurement",
            filter_cutoff_rad_s=declared_cutoff,
            integrator_limit=integrator_limit,
        )
        bindings = {"kp": "kp", "ki": "ki", "kd": "kd"}
    elif architecture in {"lead", "lead_compensator"}:
        if set(candidate.gains) != {"gain"} or set(
            candidate.tunable_gain_names
        ) != {"gain"}:
            return _locked("lead conversion requires exact gain tunable")
        zero = candidate.design_parameters.get("zero_rad_s")
        pole = candidate.design_parameters.get("pole_rad_s")
        if zero is None or pole is None:
            return _locked("lead conversion requires zero_rad_s and pole_rad_s")
        try:
            controller = LeadControllerSpec(
                gain=candidate.gains["gain"],
                zero_rad_s=zero,
                pole_rad_s=pole,
            )
        except ValueError as exc:
            return _locked(f"invalid lead fixed design: {exc}")
        bindings = {"gain": "gain"}
    elif architecture in {"lag", "lag_compensator"}:
        if set(candidate.gains) != {"gain"} or set(
            candidate.tunable_gain_names
        ) != {"gain"}:
            return _locked("lag conversion requires exact gain tunable")
        zero = candidate.design_parameters.get("zero_rad_s")
        pole = candidate.design_parameters.get("pole_rad_s")
        if zero is None or pole is None:
            return _locked("lag conversion requires zero_rad_s and pole_rad_s")
        try:
            controller = LagControllerSpec(
                gain=candidate.gains["gain"],
                zero_rad_s=zero,
                pole_rad_s=pole,
            )
        except ValueError as exc:
            return _locked(f"invalid lag fixed design: {exc}")
        bindings = {"gain": "gain"}
    elif architecture in {"notch", "notch_filter"}:
        if set(candidate.gains) != {"gain"} or set(
            candidate.tunable_gain_names
        ) != {"gain"}:
            return _locked("notch conversion requires exact gain tunable")
        required = {
            "center_frequency_rad_s",
            "zero_damping_ratio",
            "pole_damping_ratio",
        }
        if not required <= set(candidate.design_parameters):
            return _locked(
                "notch conversion requires center frequency and both damping ratios"
            )
        try:
            controller = NotchControllerSpec(
                gain=candidate.gains["gain"],
                center_frequency_rad_s=candidate.design_parameters[
                    "center_frequency_rad_s"
                ],
                zero_damping_ratio=candidate.design_parameters[
                    "zero_damping_ratio"
                ],
                pole_damping_ratio=candidate.design_parameters[
                    "pole_damping_ratio"
                ],
            )
        except ValueError as exc:
            return _locked(f"invalid notch fixed design: {exc}")
        bindings = {"gain": "gain"}
    elif architecture == "cascaded_PD_with_hover_feedforward":
        if (
            not isinstance(model, RegisteredNonlinearModelSpec)
            or model.template_id != "vtol_cascaded"
        ):
            return _locked("VTOL cascade requires the registered VTOL model")
        expected = {
            "kp_z",
            "kd_z",
            "kp_theta",
            "kd_theta",
            "kp_y",
            "kd_y",
        }
        if set(candidate.gains) != expected or set(
            candidate.tunable_gain_names
        ) != expected:
            return _locked("VTOL cascade requires the exact six gains")
        hover = candidate.feedforward.get("hover_thrust")
        tilt = candidate.saturation.get("max_tilt_rad")
        if hover is None or tilt is None or hover <= 0.0 or tilt <= 0.0:
            return _locked(
                "VTOL cascade requires hover thrust and positive tilt limit"
            )
        controller = RegisteredControllerSpec(
            controller_id="vtol_cascaded",
            parameters={name: candidate.gains[name] for name in expected},
            reference={"x_m": 0.0, "z_m": 0.0},
            feedforward={"hover_thrust_n": hover},
            configuration={"tilt_reference_limit_rad": tilt},
        )
        bindings = {name: f"parameters.{name}" for name in expected}
    elif architecture in {
        "state_feedback",
        "explicit_state_feedback",
    }:
        if not isinstance(explicit_controller, StateFeedbackControllerSpec):
            return _locked(
                "state feedback requires an explicit typed controller snapshot"
            )
        if parameter_bindings is None or set(parameter_bindings) != set(
            candidate.tunable_gain_names
        ):
            return _locked(
                "state feedback requires exact matrix parameter bindings"
            )
        controller = explicit_controller
        bindings = dict(parameter_bindings)
    else:
        return _locked(
            f"controller architecture is not in the Stage-6 allowlist: {architecture}"
        )

    try:
        profile = make_tuning_profile(
            controller,
            tunable_parameters=list(bindings),
            parameter_bindings=bindings,
            open_loop_behavior=open_loop_behavior,
            step_fraction=0.05,
            zero_step_scales={
                name: 1.0
                for name, binding in bindings.items()
                if _binding_value(controller, binding) == 0.0
            },
            profile_id=f"bootstrap:{architecture}:v1",
        )
    except ValueError as exc:
        return _locked(f"typed controller/profile validation failed: {exc}")
    return ControllerBootstrapResult(
        status="ready",
        controller=controller,
        tuning_profile=profile,
    )


def _binding_value(
    controller: ControllerRuntimeSpec,
    binding: str,
) -> float:
    value = controller.model_dump(mode="python")
    for part in binding.split("."):
        value = value[int(part)] if isinstance(value, list) else value[part]
    return float(value)


__all__ = ["ControllerBootstrapResult", "bootstrap_controller_candidate"]
