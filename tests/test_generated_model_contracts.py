from __future__ import annotations

import hashlib

import pytest
from pydantic import TypeAdapter, ValidationError

from cfdc.lab.model_contracts import (
    DiscoveryQuestion,
    ExperimentProposal,
    GeneratedModelEnvelopeV1,
    GeneratedModelResult,
    NeedMoreModelResult,
    OperatingPoint,
    ParameterEvidence,
    ReadyModelResult,
    RejectedModelResult,
    ValidityRegion,
)
from cfdc.models import RegisteredNonlinearModelSpec, TransferFunctionModelSpec
from cfdc.sim.registered_runtime import registered_run_envelope


def generated_first_order_envelope(
    *,
    model_role: str = "user_evidence_model",
    evidence_source: str = "user_supplied",
    operating_point: OperatingPoint | None = None,
    validity_region: ValidityRegion | None = None,
) -> GeneratedModelEnvelopeV1:
    return GeneratedModelEnvelopeV1(
        model_role=model_role,
        model=TransferFunctionModelSpec(
            numerator=[2.0],
            denominator=[5.0, 1.0],
            input_signal_id="heater_power",
            output_signal_id="temperature",
            input_units="W",
            output_units="degC",
        ),
        operating_point=operating_point,
        validity_region=validity_region,
        parameter_evidence=[
            ParameterEvidence(
                parameter_path="model.numerator[0]",
                value=2.0,
                unit="degC/W",
                source=evidence_source,
                source_fact_ids=["input_step", "output_step"],
            ),
            ParameterEvidence(
                parameter_path="model.denominator[0]",
                value=5.0,
                unit="s",
                source="user_supplied",
                source_fact_ids=["response_time_63"],
            ),
        ],
        assumptions=["在给定输入范围内可近似为一阶线性对象。"],
        limitations=["不代表真实硬件安全验证。"],
        plain_language_summary="加热功率上升后，温度按一阶惯性过程上升。",
        equation_latex=[r"G(s)=\frac{2}{5s+1}"],
        experiment_proposal=ExperimentProposal(
            initial_state={},
            reference={"temperature": 24.0},
            horizon_s=30.0,
            sample_time_s=0.1,
            actuator_bounds={"heater_power": (0.0, 1000.0)},
            state_bounds={},
            output_bounds={"temperature": (15.0, 80.0)},
            signal_units={"heater_power": "W", "temperature": "degC"},
            evidence_fact_ids=["input_step", "output_step", "response_time_63"],
        ),
    )


def local_operating_point() -> OperatingPoint:
    return OperatingPoint(
        description="阀门在一半开度附近的平衡状态。",
        states={},
        inputs={"valve": 50.0},
        outputs={"flow": 12.0},
        signal_units={"valve": "%", "flow": "L/min"},
    )


def local_validity_region() -> ValidityRegion:
    return ValidityRegion(
        description="只适用于阀门中等开度。",
        input_ranges={"valve": (40.0, 60.0)},
        output_ranges={"flow": (9.0, 15.0)},
        state_ranges={},
        signal_units={"valve": "%", "flow": "L/min"},
        constant_conditions=["上游压力保持不变。"],
        out_of_range_effect="离开此范围时局部线性模型失效。",
    )


def test_generated_envelope_wraps_without_changing_executable_model_schema():
    model = TransferFunctionModelSpec(
        numerator=[2.0],
        denominator=[5.0, 1.0],
        input_signal_id="heater_power",
        output_signal_id="temperature",
        input_units="W",
        output_units="degC",
    )
    before = hashlib.sha256(model.model_dump_json().encode()).hexdigest()

    envelope = generated_first_order_envelope()

    assert envelope.envelope_schema_version == "generated_model_envelope/v1"
    assert envelope.model.kind == "transfer_function"
    assert "model_role" not in envelope.model.model_dump()
    assert (
        hashlib.sha256(envelope.model.model_dump_json().encode()).hexdigest() == before
    )


def test_contracts_reject_extra_fields_placeholder_units_and_non_finite_values():
    with pytest.raises(ValidationError, match="extra"):
        DiscoveryQuestion(
            question_id="q",
            fact_id="sample_time",
            fact_type="sample_time",
            prompt="采样周期是多少？",
            answer_kind="number",
            unit_family="time",
            example_id="sampling.sample_time.seconds.v1",
            why_needed="用于离散模型。",
            executable_code="print('unsafe')",
        )
    with pytest.raises(ValidationError, match="placeholder"):
        generated_first_order_envelope().model_copy(
            update={
                "model": TransferFunctionModelSpec(
                    numerator=[2.0],
                    denominator=[5.0, 1.0],
                    input_signal_id="heater_power",
                    output_signal_id="temperature",
                )
            }
        ).__class__.model_validate(
            {
                **generated_first_order_envelope().model_dump(mode="json"),
                "model": {
                    **generated_first_order_envelope().model.model_dump(mode="json"),
                    "input_units": "unspecified",
                },
            }
        )
    with pytest.raises(ValidationError):
        ParameterEvidence(
            parameter_path="model.numerator[0]",
            value=float("nan"),
            unit="degC/W",
            source="user_supplied",
            source_fact_ids=["input_step"],
        )


def test_ranges_and_experiment_sample_budget_are_strict():
    with pytest.raises(ValidationError, match="below"):
        ValidityRegion(
            description="无效范围。",
            input_ranges={"u": (1.0, 1.0)},
            output_ranges={},
            state_ranges={},
            signal_units={"u": "V"},
            constant_conditions=["环境不变。"],
            out_of_range_effect="模型失效。",
        )
    payload = generated_first_order_envelope().experiment_proposal.model_dump()
    payload.update(horizon_s=200.0, sample_time_s=0.01)
    with pytest.raises(ValidationError, match="20,000"):
        ExperimentProposal.model_validate(payload)


def test_local_linear_role_requires_operating_point_and_validity_region():
    with pytest.raises(ValidationError, match="operating point"):
        generated_first_order_envelope(model_role="local_linear_hypothesis")

    envelope = generated_first_order_envelope(
        model_role="local_linear_hypothesis",
        operating_point=local_operating_point(),
        validity_region=local_validity_region(),
    )
    assert envelope.validity_region is not None


def test_adopted_example_evidence_forces_example_hypothesis_role():
    with pytest.raises(ValidationError, match="example_hypothesis"):
        generated_first_order_envelope(evidence_source="user_adopted_example")

    envelope = generated_first_order_envelope(
        model_role="example_hypothesis",
        evidence_source="user_adopted_example",
    )
    assert envelope.model_role == "example_hypothesis"


def test_generated_model_results_are_strictly_discriminated():
    question = DiscoveryQuestion(
        question_id="q-sample",
        fact_id="sample_time",
        fact_type="sample_time",
        prompt="采样周期是多少？",
        answer_kind="number",
        unit_family="time",
        example_id="sampling.sample_time.seconds.v1",
        why_needed="用于确定离散模型。",
    )
    results = [
        NeedMoreModelResult(
            missing_fact_ids=["sample_time"],
            questions=[question],
            rationale="仍缺少采样周期。",
        ),
        ReadyModelResult(
            envelope=generated_first_order_envelope(),
            confidence=0.42,
            rationale="证据完整且模型可校验。",
        ),
        RejectedModelResult(
            reason="当前问题需要未注册的非线性运行时。",
            next_steps=["提供工作点附近的阶跃响应数据。"],
        ),
    ]
    adapter = TypeAdapter(GeneratedModelResult)

    assert [
        adapter.validate_python(item.model_dump(mode="json")).status for item in results
    ] == ["need_more", "ready", "rejected"]
    with pytest.raises(ValidationError):
        adapter.validate_python({"status": "unknown"})


def test_need_more_allows_only_one_to_four_questions():
    question = DiscoveryQuestion(
        question_id="q",
        fact_id="fact",
        fact_type="signal_definition",
        prompt="信号是什么？",
        answer_kind="text",
        unit_family="signal",
        example_id="signals.siso.definition.v1",
        why_needed="用于建立信号映射。",
    )
    with pytest.raises(ValidationError):
        NeedMoreModelResult(
            missing_fact_ids=["fact"],
            questions=[],
            rationale="缺少事实。",
        )
    with pytest.raises(ValidationError):
        NeedMoreModelResult(
            missing_fact_ids=["fact"],
            questions=[question] * 5,
            rationale="问题过多。",
        )


def registered_model(template_id: str) -> RegisteredNonlinearModelSpec:
    if template_id == "underactuated_cartpole":
        return RegisteredNonlinearModelSpec(
            template_id=template_id,
            parameters={
                "cart_mass_kg": 1.0,
                "pole_mass_kg": 0.1,
                "com_length_m": 0.5,
                "pole_inertia_kg_m2": 0.025,
                "cart_friction_n_s_m": 0.05,
                "gravity_m_s2": 9.81,
                "force_limit_n": 20.0,
                "cart_position_limit_m": 2.0,
            },
            initial_state={
                "position_m": 0.0,
                "velocity_m_s": 0.0,
                "angle_rad": 0.0,
                "angular_rate_rad_s": 0.0,
            },
            input_signal_ids=["force_n"],
            output_signal_ids=["position_m", "angle_rad"],
            signal_units={
                "position_m": "m",
                "velocity_m_s": "m/s",
                "angle_rad": "rad",
                "angular_rate_rad_s": "rad/s",
                "force_n": "N",
            },
        )
    return RegisteredNonlinearModelSpec(
        template_id="vtol_cascaded",
        parameters={
            "mass_kg": 1.5,
            "pitch_inertia_kg_m2": 0.25,
            "gravity_m_s2": 9.81,
            "linear_drag_n_s_m": 0.1,
            "pitch_damping_n_m_s": 0.05,
            "thrust_min_n": 0.0,
            "thrust_max_n": 30.0,
            "torque_limit_n_m": 5.0,
        },
        initial_state={
            "x_m": 0.0,
            "z_m": 0.0,
            "pitch_rad": 0.0,
            "x_velocity_m_s": 0.0,
            "z_velocity_m_s": 0.0,
            "pitch_rate_rad_s": 0.0,
        },
        input_signal_ids=["thrust_n", "torque_n_m"],
        output_signal_ids=["x_m", "z_m", "pitch_rad"],
        signal_units={
            "x_m": "m",
            "z_m": "m",
            "pitch_rad": "rad",
            "x_velocity_m_s": "m/s",
            "z_velocity_m_s": "m/s",
            "pitch_rate_rad_s": "rad/s",
            "thrust_n": "N",
            "torque_n_m": "N*m",
        },
    )


def registered_envelope(
    template_id: str,
    *,
    policy_id: str | None,
    actuator_bounds: dict[str, tuple[float, float]] | None = None,
    state_bounds: dict[str, tuple[float, float]] | None = None,
    output_bounds: dict[str, tuple[float, float]] | None = None,
) -> GeneratedModelEnvelopeV1:
    model = registered_model(template_id)
    runtime = registered_run_envelope(model)
    fact_id = (
        "cartpole_parameters"
        if template_id == "underactuated_cartpole"
        else "vtol_parameters"
    )
    return GeneratedModelEnvelopeV1(
        model_role="registered_nonlinear_model",
        model=model,
        parameter_evidence=[
            ParameterEvidence(
                parameter_path="model.parameters.gravity_m_s2",
                value=9.81,
                unit="m/s^2",
                source="registry_policy",
                source_fact_ids=[fact_id],
            )
        ],
        assumptions=["使用注册的五场景软件模型验证策略。"],
        limitations=["不代表真实硬件安全验证。"],
        plain_language_summary="使用注册的非线性对象和固定五场景策略。",
        equation_latex=[r"\dot{x}=f_{\mathrm{registry}}(x,u)"],
        experiment_proposal=ExperimentProposal(
            initial_state=model.initial_state,
            reference=runtime["reference"],
            horizon_s=runtime["horizon_s"],
            sample_time_s=runtime["sample_time_s"],
            actuator_bounds=(
                runtime["actuator_bounds"]
                if actuator_bounds is None
                else actuator_bounds
            ),
            state_bounds=(
                runtime["state_bounds"] if state_bounds is None else state_bounds
            ),
            output_bounds=(
                runtime["output_bounds"] if output_bounds is None else output_bounds
            ),
            signal_units=model.signal_units,
            evidence_fact_ids=[fact_id],
            registry_policy_id=policy_id,
        ),
    )


@pytest.mark.parametrize(
    ("template_id", "expected_policy_id"),
    [
        (
            "underactuated_cartpole",
            "registered_cartpole_five_scenario/v1",
        ),
        ("vtol_cascaded", "registered_vtol_five_scenario/v1"),
    ],
)
def test_registered_envelope_requires_exact_versioned_policy_id(
    template_id,
    expected_policy_id,
):
    with pytest.raises(ValidationError, match="registry policy"):
        registered_envelope(template_id, policy_id=None)
    with pytest.raises(ValidationError, match="registry policy"):
        registered_envelope(template_id, policy_id="wrong-policy/v1")

    assert (
        registered_envelope(
            template_id, policy_id=expected_policy_id
        ).experiment_proposal.registry_policy_id
        == expected_policy_id
    )


def test_registered_envelope_rejects_state_bounds_wider_than_registry():
    model = registered_model("underactuated_cartpole")
    runtime = registered_run_envelope(model)
    widened = dict(runtime["state_bounds"])
    lower, upper = widened["angle_rad"]
    widened["angle_rad"] = (lower - 0.01, upper)

    with pytest.raises(ValidationError, match="inside"):
        registered_envelope(
            "underactuated_cartpole",
            policy_id="registered_cartpole_five_scenario/v1",
            state_bounds=widened,
        )


def test_registered_envelope_allows_all_runtime_bounds_inside_registry():
    model = registered_model("vtol_cascaded")
    runtime = registered_run_envelope(model)
    actuator_bounds = dict(runtime["actuator_bounds"])
    actuator_bounds["thrust_n"] = (1.0, 29.0)
    actuator_bounds["torque_n_m"] = (-4.0, 4.0)
    output_bounds = {
        "x_m": (-2.5, 2.5),
        "z_m": (-1.5, 1.5),
        "pitch_rad": (-0.5, 0.5),
    }
    state_bounds = dict(runtime["state_bounds"])
    state_bounds["pitch_rad"] = (-0.5, 0.5)

    envelope = registered_envelope(
        "vtol_cascaded",
        policy_id="registered_vtol_five_scenario/v1",
        actuator_bounds=actuator_bounds,
        state_bounds=state_bounds,
        output_bounds=output_bounds,
    )

    assert envelope.experiment_proposal.actuator_bounds == actuator_bounds
    assert envelope.experiment_proposal.output_bounds == output_bounds
    assert envelope.experiment_proposal.state_bounds["pitch_rad"] == (
        -0.5,
        0.5,
    )


@pytest.mark.parametrize(
    ("field_name", "signal_name"),
    [
        ("actuator_bounds", "thrust_n"),
        ("output_bounds", "x_m"),
        ("state_bounds", "pitch_rad"),
    ],
)
def test_registered_envelope_rejects_widened_runtime_bounds(
    field_name,
    signal_name,
):
    valid = registered_envelope(
        "vtol_cascaded",
        policy_id="registered_vtol_five_scenario/v1",
    ).model_dump(mode="json")
    lower, upper = valid["experiment_proposal"][field_name][signal_name]
    valid["experiment_proposal"][field_name][signal_name] = [
        lower - 0.01,
        upper,
    ]

    with pytest.raises(ValidationError, match="inside"):
        GeneratedModelEnvelopeV1.model_validate(valid)


@pytest.mark.parametrize(
    ("field_name", "mutation"),
    [
        ("actuator_bounds", "missing"),
        ("actuator_bounds", "unknown"),
        ("output_bounds", "missing"),
        ("output_bounds", "unknown"),
        ("state_bounds", "missing"),
        ("state_bounds", "unknown"),
    ],
)
def test_registered_envelope_rejects_missing_or_unknown_bound_signals(
    field_name,
    mutation,
):
    valid = registered_envelope(
        "vtol_cascaded",
        policy_id="registered_vtol_five_scenario/v1",
    ).model_dump(mode="json")
    bounds = valid["experiment_proposal"][field_name]
    if mutation == "missing":
        bounds.pop(next(iter(bounds)))
    else:
        bounds["unknown_signal"] = [-1.0, 1.0]

    proposal = valid["experiment_proposal"]
    signal_names = (
        set(proposal["initial_state"])
        | set(proposal["reference"])
        | set(proposal["actuator_bounds"])
        | set(proposal["state_bounds"])
        | set(proposal["output_bounds"])
    )
    proposal["signal_units"] = {
        name: proposal["signal_units"].get(name, "dimensionless")
        for name in signal_names
    }

    with pytest.raises(ValidationError, match="exact registry signal-name set"):
        GeneratedModelEnvelopeV1.model_validate(valid)


def test_non_registered_envelope_cannot_claim_registry_policy():
    payload = generated_first_order_envelope().model_dump(mode="json")
    payload["experiment_proposal"]["registry_policy_id"] = (
        "registered_cartpole_five_scenario/v1"
    )

    with pytest.raises(ValidationError, match="non-registered"):
        GeneratedModelEnvelopeV1.model_validate(payload)
