from __future__ import annotations

from cfdc.diagnosis import DiagnosticEngine
from cfdc.lab import (
    ModelFactAnswer,
    Stage5DiscoverySnapshot,
    adopt_model_question_example,
    confirm_generated_model,
    create_model_discovery_session,
    create_simulation_from_discovery,
    evaluate_controller_compatibility,
    request_model_for_discovery_session,
    run_next_trial,
)
from cfdc.models import SystemDescription
from cfdc.web.model_discovery_presentation import render_model_discovery
from tests.test_model_discovery_llm import _evidence
from tests.test_model_discovery_session import stage5_snapshot

_EXAMPLE_QUESTIONS = [
    (
        "signals",
        "signal_definition",
        "signal",
        "signals.siso.definition.v1",
        "输入和输出分别是什么，单位是什么？",
    ),
    (
        "input_step",
        "input_step",
        "power",
        "thermal.input_step.power.v1",
        "你把加热功率从多少调到多少？",
    ),
    (
        "output_step",
        "output_step",
        "temperature",
        "thermal.output_step.temperature.v1",
        "温度原来是多少，最后稳定在多少？",
    ),
    (
        "response_time_63",
        "response_time_63",
        "time",
        "process.response_time_63.seconds.v1",
        "大约多久达到最终温度变化的 63%？",
    ),
    (
        "actuator_bounds",
        "actuator_bounds",
        "bounds",
        "thermal.actuator_bounds.power.v1",
        "软件试验允许的加热功率范围是多少？",
    ),
    (
        "output_bounds",
        "output_bounds",
        "bounds",
        "thermal.output_bounds.temperature.v1",
        "软件试验允许的温度范围是多少？",
    ),
]


def _question_payload(item):
    fact_id, fact_type, unit_family, example_id, prompt = item
    return {
        "question_id": f"q-{fact_id}",
        "fact_id": fact_id,
        "fact_type": fact_type,
        "prompt": prompt,
        "answer_kind": "text",
        "unit_family": unit_family,
        "example_id": example_id,
        "why_needed": "该数值用于建立并限制可运行的软件模型。",
    }


def _example_ready_payload():
    return {
        "status": "ready",
        "envelope": {
            "envelope_schema_version": "generated_model_envelope/v1",
            "model_role": "example_hypothesis",
            "model": {
                "kind": "transfer_function",
                "numerator": [0.04],
                "denominator": [5.0, 1.0],
                "time_domain": "continuous",
                "sample_time_s": None,
                "input_delay_s": 0.0,
                "input_signal_id": "heater_power",
                "output_signal_id": "temperature",
                "input_units": "W",
                "output_units": "degC",
                "parameter_uncertainty": {},
            },
            "operating_point": None,
            "validity_region": None,
            "parameter_evidence": [
                _evidence(
                    "model.numerator[0]",
                    0.04,
                    "degC/W",
                    ["input_step", "output_step"],
                    source="deterministic_derivation",
                    derivation_rule_id="step_ratio_gain/v1",
                ),
                _evidence(
                    "model.denominator[0]",
                    5.0,
                    "s",
                    ["response_time_63"],
                    source="deterministic_derivation",
                    derivation_rule_id="response_time_63/v1",
                ),
                _evidence(
                    "model.denominator[1]",
                    1.0,
                    "1",
                    ["response_time_63"],
                    source="deterministic_derivation",
                    derivation_rule_id="normalized_one/v1",
                ),
                _evidence(
                    "model.input_delay_s",
                    0.0,
                    "s",
                    ["response_time_63"],
                    source="deterministic_derivation",
                    derivation_rule_id="normalized_zero/v1",
                ),
                _evidence(
                    "experiment_proposal.reference.temperature",
                    4.0,
                    "degC",
                    ["output_step"],
                    source="deterministic_derivation",
                    derivation_rule_id="output_step_delta_reference/v1",
                ),
                _evidence(
                    "experiment_proposal.horizon_s",
                    30.0,
                    "s",
                    ["response_time_63"],
                    source="deterministic_derivation",
                    derivation_rule_id="six_time_constants_horizon/v1",
                ),
                _evidence(
                    "experiment_proposal.sample_time_s",
                    0.1,
                    "s",
                    ["response_time_63"],
                    source="deterministic_derivation",
                    derivation_rule_id="time_constant_div_50_sample/v1",
                ),
                *[
                    _evidence(
                        f"experiment_proposal.actuator_bounds.heater_power[{index}]",
                        value,
                        "W",
                        ["input_step", "actuator_bounds"],
                        source="deterministic_derivation",
                        derivation_rule_id=(
                            "center_actuator_bounds_at_input_before/v1"
                        ),
                    )
                    for index, value in enumerate((-500.0, 500.0))
                ],
                *[
                    _evidence(
                        f"experiment_proposal.output_bounds.temperature[{index}]",
                        value,
                        "degC",
                        ["output_step", "output_bounds"],
                        source="deterministic_derivation",
                        derivation_rule_id=("center_output_bounds_at_output_before/v1"),
                    )
                    for index, value in enumerate((-5.0, 60.0))
                ],
            ],
            "assumptions": ["输入和输出都以采用示例时的初始值作为零偏差工作点。"],
            "limitations": ["该模型全部使用固定示例值，只能用于可重复软件演示。"],
            "plain_language_summary": (
                "示例加热功率增加 100 W 后，温度最终增加 4 degC，"
                "并按约 5 s 的时间尺度逐渐接近新值。"
            ),
            "equation_latex": [r"G(s)=\frac{0.04}{5s+1}"],
            "experiment_proposal": {
                "initial_state": {},
                "reference": {"temperature": 4.0},
                "horizon_s": 30.0,
                "sample_time_s": 0.1,
                "actuator_bounds": {"heater_power": [-500.0, 500.0]},
                "state_bounds": {},
                "output_bounds": {"temperature": [-5.0, 60.0]},
                "signal_units": {
                    "heater_power": "W",
                    "temperature": "degC",
                },
                "evidence_fact_ids": [
                    "signals",
                    "input_step",
                    "output_step",
                    "response_time_63",
                    "actuator_bounds",
                    "output_bounds",
                ],
                "registry_policy_id": None,
            },
        },
        "confidence": 0.8,
        "rationale": "All required facts were explicitly adopted.",
    }


class ExampleJourneyAdapter:
    base_url = "https://llm.example.test/v1"
    model = "example-journey-model"
    api_key = "not-persisted"

    def propose_model_with_messages(self, context, messages):
        del messages
        existing = {fact.fact_id for fact in context.facts}
        missing = [item for item in _EXAMPLE_QUESTIONS if item[0] not in existing]
        if missing:
            batch = missing[:4]
            return {
                "status": "need_more",
                "missing_fact_ids": [item[0] for item in batch],
                "questions": [_question_payload(item) for item in batch],
                "rationale": "还需要固定示例事实。",
            }
        return _example_ready_payload()


def _user_fact(
    fact_id,
    fact_type,
    unit_family,
    answer_text,
    value_payload,
):
    return ModelFactAnswer(
        fact_id=fact_id,
        fact_type=fact_type,
        unit_family=unit_family,
        answer_text=answer_text,
        value_payload=value_payload,
        source="user_supplied",
    )


def _delayed_heater_stage5():
    description = SystemDescription(
        text=(
            "A custom thermal chamber outside the research dataset has a "
            "measured two-second pure delay before temperature starts "
            "changing, then settles monotonically after heater power changes."
        ),
        actuators=["heater_power"],
        observed_outputs=["temperature"],
    )
    diagnosis, classification = DiagnosticEngine().run(description)
    base = stage5_snapshot()
    return Stage5DiscoverySnapshot(
        source_run_id="run-user-custom-delayed-heater",
        description=description,
        diagnosis=diagnosis,
        classification=classification,
        initial_controller_candidate=base.initial_controller_candidate,
    )


def _delayed_heater_facts():
    return [
        _user_fact(
            "signals",
            "signal_definition",
            "signal",
            "Input heater_power is W and output temperature is degC.",
            {
                "inputs": [{"signal_id": "heater_power", "unit": "W"}],
                "outputs": [{"signal_id": "temperature", "unit": "degC"}],
            },
        ),
        _user_fact(
            "input_step",
            "input_step",
            "power",
            "Heater power changed from 500 W to 600 W.",
            {"before": 500.0, "after": 600.0, "unit": "W"},
        ),
        _user_fact(
            "output_step",
            "output_step",
            "temperature",
            "Temperature changed from 20 degC to 24 degC.",
            {"before": 20.0, "after": 24.0, "unit": "degC"},
        ),
        _user_fact(
            "response_time_63",
            "response_time_63",
            "time",
            "After the delay, 63 percent response takes 5 s.",
            {"value": 5.0, "unit": "s"},
        ),
        _user_fact(
            "response_delay",
            "response_delay",
            "time",
            "The measured response delay is 2 s.",
            {"value": 2.0, "unit": "s"},
        ),
        _user_fact(
            "actuator_bounds",
            "actuator_bounds",
            "bounds",
            "Heater power is limited to 0-1000 W.",
            {
                "ranges": {"heater_power": [0.0, 1000.0]},
                "signal_units": {"heater_power": "W"},
            },
        ),
        _user_fact(
            "output_bounds",
            "output_bounds",
            "bounds",
            "Temperature is limited to 15-80 degC.",
            {
                "ranges": {"temperature": [15.0, 80.0]},
                "signal_units": {"temperature": "degC"},
            },
        ),
    ]


class DelayedHeaterAdapter:
    base_url = "https://llm.example.test/v1"
    model = "delayed-heater-model"
    api_key = "not-persisted"

    def propose_model_with_messages(self, context, messages):
        del context, messages
        payload = _example_ready_payload()
        envelope = payload["envelope"]
        envelope["model_role"] = "user_evidence_model"
        envelope["model"]["input_delay_s"] = 2.0
        envelope["parameter_evidence"][3] = _evidence(
            "model.input_delay_s",
            2.0,
            "s",
            ["response_delay"],
            source="deterministic_derivation",
            derivation_rule_id="response_delay/v1",
        )
        envelope["experiment_proposal"]["evidence_fact_ids"].append("response_delay")
        envelope["limitations"] = [
            "The conclusion is limited to this user-supplied software model."
        ]
        payload["rationale"] = (
            "All coefficients and the two-second delay are evidence-bound."
        )
        return payload


def test_all_explicit_examples_reach_confirmed_simulation_without_initial_bound_failure():
    session = create_model_discovery_session(stage5=stage5_snapshot())
    adapter = ExampleJourneyAdapter()

    while session.state == "collecting_model_information":
        session = request_model_for_discovery_session(
            session,
            adapter,
            expected_revision=session.revision,
        )
        if session.state != "collecting_model_information":
            break
        for question in list(session.current_questions):
            session = adopt_model_question_example(
                session,
                question.question_id,
                expected_revision=session.revision,
            )

    assert session.state == "model_review"
    assert session.current_questions == []
    assert session.pending_envelope.model_role == "example_hypothesis"
    assert {answer.source for answer in session.answers} == {"user_adopted_example"}
    model_card = render_model_discovery(session)["model_card_markdown"]
    assert "偏差坐标" in model_card
    assert "相对起始值的目标变化 temperature" in model_card
    confirmed = confirm_generated_model(
        session,
        expected_revision=session.revision,
    )
    ready = evaluate_controller_compatibility(
        confirmed,
        expected_revision=confirmed.revision,
    )
    simulation = create_simulation_from_discovery(
        ready,
        expected_revision=ready.revision,
    )
    completed = run_next_trial(simulation)

    assert completed.trials
    assert completed.evidence_boundary == ("llm_proposed_model_hypothesis")
    assert completed.model_assumptions
    assert not any(
        event.kind == "declared_hard_bound_violation" and event.time_s == 0.0
        for event in completed.trials[-1].traces[0].events
    )


def test_out_of_dataset_user_facts_generate_and_run_explicit_delay_tf():
    session = create_model_discovery_session(
        stage5=_delayed_heater_stage5(),
        initial_facts=_delayed_heater_facts(),
    )
    proposed = request_model_for_discovery_session(
        session,
        DelayedHeaterAdapter(),
        expected_revision=session.revision,
    )

    assert proposed.state == "model_review"
    assert proposed.pending_envelope.model.input_delay_s == 2.0
    confirmed = confirm_generated_model(
        proposed,
        expected_revision=proposed.revision,
    )
    ready = evaluate_controller_compatibility(
        confirmed,
        expected_revision=confirmed.revision,
    )
    simulation = create_simulation_from_discovery(
        ready,
        expected_revision=ready.revision,
    )
    completed = run_next_trial(simulation)
    trace = completed.trials[-1].traces[0]

    assert completed.confirmed_model.input_delay_s == 2.0
    assert len(trace.time_s) > 20
    assert all(
        abs(value) < 1e-12
        for time_s, value in zip(
            trace.time_s,
            trace.outputs["temperature"],
        )
        if time_s < 2.0
    )
