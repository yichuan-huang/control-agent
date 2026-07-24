from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from types import SimpleNamespace

import pytest

from cfdc.diagnosis import DiagnosticEngine, OpenAICompatibleDiagnosticAdapter
from cfdc.lab.llm import ProposalCallResult
from cfdc.lab.model_contracts import (
    DiscoveryQuestion,
    ModelFactAnswer,
    ModelQuestionExampleCatalog,
    NaturalLanguageModelAnswer,
)
from cfdc.lab.model_discovery_llm import (
    ModelDiscoveryCallResult,
    ModelDiscoveryContext,
    build_model_discovery_messages,
    request_model_discovery,
)
from cfdc.lab.model_questions import adopt_example_answer, load_model_question_examples
from cfdc.lab.model_validation import (
    ModelValidationContext,
    validate_generated_model_envelope,
    validate_generated_model_payload,
)
from cfdc.models import ArchetypeClassification, StructuralDiagnosis, SystemDescription
from cfdc.sim.registered_runtime import registered_run_envelope
from tests.simulation_fixtures import cartpole_model


def example_catalog():
    return load_model_question_examples()


def test_catalog_includes_explicit_runtime_target_and_bound_facts():
    assert {
        "reference_target",
        "actuator_bounds",
        "output_bounds",
    } <= {example.fact_type for example in example_catalog().examples}


def model_facts():
    return [
        ModelFactAnswer(
            fact_id="signals",
            fact_type="signal_definition",
            answer_text="The input is heater power and the output is temperature.",
            value_payload={
                "inputs": [{"signal_id": "heater_power", "unit": "W"}],
                "outputs": [{"signal_id": "temperature", "unit": "degC"}],
            },
            unit_family="signal",
            source="user_supplied",
        ),
        ModelFactAnswer(
            fact_id="input_step",
            fact_type="input_step",
            answer_text="Power changed from 0 W to 1 W.",
            value_payload={"before": 0.0, "after": 1.0, "unit": "W"},
            unit_family="power",
            source="user_supplied",
        ),
        ModelFactAnswer(
            fact_id="output_step",
            fact_type="output_step",
            answer_text="Temperature changed from 20 degC to 22 degC.",
            value_payload={"before": 20.0, "after": 22.0, "unit": "degC"},
            unit_family="temperature",
            source="user_supplied",
        ),
        ModelFactAnswer(
            fact_id="response_time_63",
            fact_type="response_time_63",
            answer_text="The 63 percent response time is 5 seconds.",
            value_payload={"value": 5.0, "unit": "s"},
            unit_family="time",
            source="user_supplied",
        ),
        ModelFactAnswer(
            fact_id="operating_point",
            fact_type="operating_point",
            answer_text="At the operating point, power is 0 W and temperature is 24 degC.",
            value_payload={
                "inputs": {"heater_power": 0.0},
                "outputs": {"temperature": 24.0},
                "signal_units": {
                    "heater_power": "W",
                    "temperature": "degC",
                },
            },
            unit_family="operating_region",
            source="user_supplied",
        ),
        ModelFactAnswer(
            fact_id="validity_region",
            fact_type="validity_region",
            answer_text="The declared software range is 0-1000 W and 15-80 degC.",
            value_payload={
                "input_ranges": {"heater_power": [0.0, 1000.0]},
                "output_ranges": {"temperature": [15.0, 80.0]},
                "signal_units": {
                    "heater_power": "W",
                    "temperature": "degC",
                },
            },
            unit_family="operating_region",
            source="user_supplied",
        ),
    ]


def discovery_context():
    description = SystemDescription(
        text="A stable first-order heater driven by power.",
        actuators=["heater_power"],
        observed_outputs=["temperature"],
    )
    diagnosis, classification = DiagnosticEngine().run(description)
    return ModelDiscoveryContext(
        description=description,
        diagnosis=diagnosis,
        classification=classification,
        facts=model_facts(),
    )


def context_variant(
    *,
    primary_class=None,
    diagnosis_updates=None,
):
    payload = discovery_context().model_dump(mode="python")
    if primary_class is not None:
        payload["classification"]["primary_class"] = primary_class
    for field_name, updates in (diagnosis_updates or {}).items():
        payload["diagnosis"][field_name].update(updates)
    return ModelDiscoveryContext.model_validate(payload)


def _evidence(
    path,
    value,
    unit,
    fact_ids,
    *,
    source="user_supplied",
    derivation_rule_id=None,
    unit_conversion=None,
):
    return {
        "parameter_path": path,
        "value": value,
        "unit": unit,
        "source": source,
        "source_fact_ids": fact_ids,
        "derivation_rule_id": derivation_rule_id,
        "unit_conversion": unit_conversion,
    }


def ready_payload(*, confidence=0.9):
    evidence = [
        _evidence(
            "model.numerator[0]",
            2.0,
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
            24.0,
            "degC",
            ["operating_point"],
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
        _evidence(
            "experiment_proposal.actuator_bounds.heater_power[0]",
            0.0,
            "W",
            ["validity_region"],
        ),
        _evidence(
            "experiment_proposal.actuator_bounds.heater_power[1]",
            1000.0,
            "W",
            ["validity_region"],
        ),
        _evidence(
            "experiment_proposal.output_bounds.temperature[0]",
            15.0,
            "degC",
            ["validity_region"],
        ),
        _evidence(
            "experiment_proposal.output_bounds.temperature[1]",
            80.0,
            "degC",
            ["validity_region"],
        ),
    ]
    return {
        "status": "ready",
        "envelope": {
            "envelope_schema_version": "generated_model_envelope/v1",
            "model_role": "user_evidence_model",
            "model": {
                "kind": "transfer_function",
                "numerator": [2.0],
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
            "parameter_evidence": evidence,
            "assumptions": ["The plant is locally linear over the declared range."],
            "limitations": ["This software model is not hardware validation."],
            "plain_language_summary": "Power drives a first-order temperature response.",
            "equation_latex": [r"G(s)=\frac{2}{5s+1}"],
            "experiment_proposal": {
                "initial_state": {},
                "reference": {"temperature": 24.0},
                "horizon_s": 30.0,
                "sample_time_s": 0.1,
                "actuator_bounds": {"heater_power": [0.0, 1000.0]},
                "state_bounds": {},
                "output_bounds": {"temperature": [15.0, 80.0]},
                "signal_units": {
                    "heater_power": "W",
                    "temperature": "degC",
                },
                "evidence_fact_ids": [
                    "input_step",
                    "output_step",
                    "response_time_63",
                    "operating_point",
                    "validity_region",
                ],
                "registry_policy_id": None,
            },
        },
        "confidence": confidence,
        "rationale": "All numeric fields are bound to supplied evidence.",
    }


def need_more_payload(count):
    example_ids = [
        "thermal.input_step.power.v1",
        "thermal.output_step.temperature.v1",
        "process.response_time_63.seconds.v1",
        "sampling.sample_time.seconds.v1",
    ]
    fact_types = [
        "input_step",
        "output_step",
        "response_time_63",
        "sample_time",
    ]
    unit_families = ["power", "temperature", "time", "time"]
    return {
        "status": "need_more",
        "missing_fact_ids": [f"missing-{index}" for index in range(count)],
        "questions": [
            {
                "question_id": f"q-{index}",
                "fact_id": f"missing-{index}",
                "fact_type": fact_types[index],
                "prompt": f"Please provide fact {index}.",
                "answer_kind": "number",
                "unit_family": unit_families[index],
                "example_id": example_ids[index],
                "why_needed": "It is required for a deterministic model.",
            }
            for index in range(count)
        ],
        "rationale": "More evidence is required.",
    }


@pytest.mark.parametrize("count", [1, 2, 3, 4])
def test_need_more_accepts_one_to_four_plain_questions(count):
    result = validate_generated_model_payload(
        need_more_payload(count), discovery_context(), example_catalog()
    )
    assert result.status == "need_more"
    assert len(result.questions) == count


def test_need_more_rejects_unknown_or_mismatched_catalog_example():
    payload = need_more_payload(1)
    payload["questions"][0]["example_id"] = "unknown.example"
    result = validate_generated_model_payload(
        payload, discovery_context(), example_catalog()
    )
    assert result.status == "rejected"


def test_low_confidence_does_not_reject_complete_evidence_bound_model():
    payload = ready_payload(confidence=0.42)
    result = validate_generated_model_payload(
        payload, discovery_context(), example_catalog()
    )
    assert result.status == "ready", result
    assert result.confidence == pytest.approx(0.42)


def test_absolute_operating_facts_recompute_as_deviation_trial_values():
    context_payload = discovery_context().model_dump(mode="python")
    input_step = next(
        fact for fact in context_payload["facts"] if fact["fact_id"] == "input_step"
    )
    input_step["answer_text"] = "Power changed from 500 W to 600 W."
    input_step["value_payload"] = {
        "before": 500.0,
        "after": 600.0,
        "unit": "W",
    }
    context_payload["facts"].extend(
        [
            ModelFactAnswer(
                fact_id="actuator_bounds",
                fact_type="actuator_bounds",
                answer_text="Absolute heater power is limited to 0-1000 W.",
                value_payload={
                    "ranges": {"heater_power": [0.0, 1000.0]},
                    "signal_units": {"heater_power": "W"},
                },
                unit_family="bounds",
                source="user_supplied",
            ).model_dump(mode="python"),
            ModelFactAnswer(
                fact_id="output_bounds",
                fact_type="output_bounds",
                answer_text="Absolute temperature is limited to 15-80 degC.",
                value_payload={
                    "ranges": {"temperature": [15.0, 80.0]},
                    "signal_units": {"temperature": "degC"},
                },
                unit_family="bounds",
                source="user_supplied",
            ).model_dump(mode="python"),
        ]
    )
    payload = ready_payload()
    envelope = payload["envelope"]
    envelope["model_role"] = "user_evidence_model"
    envelope["model"]["numerator"] = [0.02]
    envelope["parameter_evidence"][0]["value"] = 0.02
    envelope["experiment_proposal"]["reference"]["temperature"] = 2.0
    envelope["parameter_evidence"][4] = _evidence(
        "experiment_proposal.reference.temperature",
        2.0,
        "degC",
        ["output_step"],
        source="deterministic_derivation",
        derivation_rule_id="output_step_delta_reference/v1",
    )
    envelope["experiment_proposal"]["actuator_bounds"]["heater_power"] = [-500.0, 500.0]
    for index, value in enumerate((-500.0, 500.0)):
        envelope["parameter_evidence"][7 + index] = _evidence(
            f"experiment_proposal.actuator_bounds.heater_power[{index}]",
            value,
            "W",
            ["input_step", "actuator_bounds"],
            source="deterministic_derivation",
            derivation_rule_id="center_actuator_bounds_at_input_before/v1",
        )
    envelope["experiment_proposal"]["output_bounds"]["temperature"] = [-5.0, 60.0]
    for index, value in enumerate((-5.0, 60.0)):
        envelope["parameter_evidence"][9 + index] = _evidence(
            f"experiment_proposal.output_bounds.temperature[{index}]",
            value,
            "degC",
            ["output_step", "output_bounds"],
            source="deterministic_derivation",
            derivation_rule_id="center_output_bounds_at_output_before/v1",
        )

    result = validate_generated_model_payload(
        payload,
        ModelDiscoveryContext.model_validate(context_payload),
        example_catalog(),
    )

    assert result.status == "ready", result
    assert result.envelope.experiment_proposal.reference == {"temperature": 2.0}
    assert result.envelope.experiment_proposal.actuator_bounds == {
        "heater_power": (-500.0, 500.0)
    }
    assert result.envelope.experiment_proposal.output_bounds == {
        "temperature": (-5.0, 60.0)
    }


def test_derived_use_of_adopted_fact_requires_example_hypothesis_role():
    catalog = example_catalog()
    adopted = adopt_example_answer(
        DiscoveryQuestion(
            question_id="q-input-step",
            fact_id="input_step",
            fact_type="input_step",
            prompt="你把加热功率从多少调到多少？",
            answer_kind="text",
            unit_family="power",
            example_id="thermal.input_step.power.v1",
            why_needed="用于计算输入变化。",
        ),
        catalog,
        adopted_at="2026-07-23T12:00:00+00:00",
    )
    context_payload = discovery_context().model_dump(mode="python")
    context_payload["facts"] = [
        (adopted.model_dump(mode="python") if fact["fact_id"] == "input_step" else fact)
        for fact in context_payload["facts"]
    ]
    payload = ready_payload()
    payload["envelope"]["model"]["numerator"] = [0.02]
    payload["envelope"]["parameter_evidence"][0]["value"] = 0.02

    result = validate_generated_model_payload(
        payload,
        ModelDiscoveryContext.model_validate(context_payload),
        catalog,
    )

    assert result.status == "rejected"


def mutate_ready_payload(mutation):
    payload = deepcopy(ready_payload())
    envelope = payload["envelope"]
    if mutation == "unknown_field":
        envelope["unknown"] = "not allowed"
    elif mutation == "code":
        envelope["assumptions"].append("```python\nimport os\n```")
    elif mutation == "non_finite":
        envelope["model"]["numerator"][0] = float("nan")
    elif mutation == "missing_unit":
        envelope["model"]["input_units"] = "unspecified"
    elif mutation == "missing_parameter_evidence":
        envelope["parameter_evidence"] = envelope["parameter_evidence"][1:]
    elif mutation == "unadopted_example":
        envelope["parameter_evidence"][0]["source"] = "user_adopted_example"
    elif mutation == "too_many_samples":
        envelope["experiment_proposal"]["horizon_s"] = 2000.0
    else:
        raise AssertionError(mutation)
    return payload


@pytest.mark.parametrize(
    "mutation",
    [
        "unknown_field",
        "code",
        "non_finite",
        "missing_unit",
        "missing_parameter_evidence",
        "unadopted_example",
        "too_many_samples",
    ],
)
def test_unsafe_or_unproven_ready_payload_is_not_runnable(mutation):
    result = validate_generated_model_payload(
        mutate_ready_payload(mutation), discovery_context(), example_catalog()
    )
    assert result.status != "ready"


def test_safe_latex_is_display_only_and_unknown_derivation_rule_is_rejected():
    payload = ready_payload()
    payload["envelope"]["equation_latex"] = [
        r"G(s)=\frac{2}{5s+1}",
        r"\operatorname{eval}(x)",
    ]
    accepted = validate_generated_model_payload(
        payload, discovery_context(), example_catalog()
    )
    assert accepted.status == "ready"

    unsafe_latex = deepcopy(payload)
    unsafe_latex["envelope"]["equation_latex"] = ["```python\nimport os\n```"]
    assert (
        validate_generated_model_payload(
            unsafe_latex, discovery_context(), example_catalog()
        ).status
        == "rejected"
    )

    payload["envelope"]["parameter_evidence"][0].update(
        {
            "source": "deterministic_derivation",
            "derivation_rule_id": "arbitrary-expression/v1",
        }
    )
    rejected = validate_generated_model_payload(
        payload, discovery_context(), example_catalog()
    )
    assert rejected.status == "rejected"


def test_registered_derivation_is_recomputed_from_referenced_facts():
    payload = ready_payload()
    result = validate_generated_model_payload(
        payload, discovery_context(), example_catalog()
    )
    assert result.status == "ready"

    payload["envelope"]["parameter_evidence"][0]["value"] = 2.1
    result = validate_generated_model_payload(
        payload, discovery_context(), example_catalog()
    )
    assert result.status == "rejected"


@pytest.mark.parametrize(
    "attack",
    [
        "response_time_as_numerator",
        "step_gain_as_denominator",
    ],
)
def test_derivation_rules_are_bound_to_closed_semantic_parameter_paths(attack):
    payload = ready_payload()
    evidence = payload["envelope"]["parameter_evidence"]
    model = payload["envelope"]["model"]
    if attack == "response_time_as_numerator":
        model["numerator"][0] = 5.0
        evidence[0] = _evidence(
            "model.numerator[0]",
            5.0,
            "s",
            ["response_time_63"],
            source="deterministic_derivation",
            derivation_rule_id="response_time_63/v1",
        )
    elif attack == "step_gain_as_denominator":
        model["denominator"][0] = 2.0
        evidence[1] = _evidence(
            "model.denominator[0]",
            2.0,
            "degC/W",
            ["input_step", "output_step"],
            source="deterministic_derivation",
            derivation_rule_id="step_ratio_gain/v1",
        )
    result = validate_generated_model_payload(
        payload, discovery_context(), example_catalog()
    )

    assert result.status == "rejected"


def test_dual_normalized_one_cannot_self_attest_first_order_denominator():
    payload = ready_payload()
    payload["envelope"]["model"]["denominator"] = [1.0, 1.0]
    payload["envelope"]["parameter_evidence"][1] = _evidence(
        "model.denominator[0]",
        1.0,
        "1",
        ["response_time_63"],
        source="deterministic_derivation",
        derivation_rule_id="normalized_one/v1",
    )

    assert (
        validate_generated_model_payload(
            payload, discovery_context(), example_catalog()
        ).status
        == "rejected"
    )


def test_discrete_tf_coefficients_cannot_use_continuous_step_rules():
    context_payload = discovery_context().model_dump(mode="python")
    context_payload["facts"].append(
        ModelFactAnswer(
            fact_id="sample_time",
            fact_type="sample_time",
            answer_text="The sample time is 0.1 seconds.",
            value_payload={"value": 0.1, "unit": "s"},
            unit_family="time",
            source="user_supplied",
        ).model_dump(mode="python")
    )
    payload = ready_payload()
    payload["envelope"]["model"].update(time_domain="discrete", sample_time_s=0.1)
    payload["envelope"]["parameter_evidence"].append(
        _evidence(
            "model.sample_time_s",
            0.1,
            "s",
            ["sample_time"],
            source="deterministic_derivation",
            derivation_rule_id="sample_time/v1",
        )
    )

    assert (
        validate_generated_model_payload(
            payload,
            ModelDiscoveryContext.model_validate(context_payload),
            example_catalog(),
        ).status
        == "rejected"
    )


def test_response_time_derivation_cannot_attest_uncertainty():
    payload = ready_payload()
    payload["envelope"]["model"]["parameter_uncertainty"] = {"gain_relative": 5.0}
    payload["envelope"]["parameter_evidence"].append(
        _evidence(
            "model.parameter_uncertainty.gain_relative",
            5.0,
            "s",
            ["response_time_63"],
            source="deterministic_derivation",
            derivation_rule_id="response_time_63/v1",
        )
    )

    result = validate_generated_model_payload(
        payload, discovery_context(), example_catalog()
    )

    assert result.status == "rejected"


def test_time_derivation_requires_seconds_target_unit():
    context_payload = discovery_context().model_dump(mode="python")
    response_fact = next(
        fact
        for fact in context_payload["facts"]
        if fact["fact_id"] == "response_time_63"
    )
    response_fact["value_payload"]["unit"] = "ms"
    context = ModelDiscoveryContext.model_validate(context_payload)
    payload = ready_payload()
    for evidence in payload["envelope"]["parameter_evidence"]:
        if evidence["source_fact_ids"] == ["response_time_63"] and evidence[
            "derivation_rule_id"
        ] not in {"normalized_one/v1", "normalized_zero/v1"}:
            evidence["unit"] = "ms"

    result = validate_generated_model_payload(payload, context, example_catalog())

    assert result.status == "rejected"


@pytest.mark.parametrize(
    "mutation",
    ["unrelated_fact", "mismatched_value", "mismatched_unit", "conversion"],
)
def test_direct_evidence_must_match_a_referenced_numeric_leaf_and_unit(
    mutation,
):
    payload = ready_payload()
    evidence = payload["envelope"]["parameter_evidence"][4]
    if mutation == "unrelated_fact":
        evidence["source_fact_ids"] = ["input_step"]
    elif mutation == "mismatched_value":
        payload["envelope"]["experiment_proposal"]["reference"]["temperature"] = 25.0
        evidence["value"] = 25.0
    elif mutation == "mismatched_unit":
        evidence["unit"] = "K"
    else:
        evidence["unit"] = "K"
        evidence["unit_conversion"] = "arbitrary_conversion/v1"
    result = validate_generated_model_payload(
        payload, discovery_context(), example_catalog()
    )
    assert result.status == "rejected"


def test_direct_evidence_uses_exact_semantic_leaf_not_same_valued_fact():
    context_payload = discovery_context().model_dump(mode="python")
    context_payload["facts"].append(
        ModelFactAnswer(
            fact_id="unrelated_temperature",
            fact_type="operating_point",
            answer_text="Another sensor happens to read 24 degC.",
            value_payload={
                "inputs": {},
                "outputs": {"other_temperature": 24.0},
                "signal_units": {"other_temperature": "degC"},
            },
            unit_family="operating_region",
            source="user_supplied",
        ).model_dump(mode="python")
    )
    context = ModelDiscoveryContext.model_validate(context_payload)
    payload = ready_payload()
    payload["envelope"]["parameter_evidence"][4]["source_fact_ids"] = [
        "unrelated_temperature"
    ]

    result = validate_generated_model_payload(payload, context, example_catalog())

    assert result.status == "rejected"


def test_registered_unit_conversion_is_recomputed_on_exact_fact_leaf():
    context_payload = discovery_context().model_dump(mode="python")
    context_payload["facts"].append(
        ModelFactAnswer(
            fact_id="actuator_kw_bounds",
            fact_type="actuator_bounds",
            answer_text="The actuator limit is 0-1 kW.",
            value_payload={
                "ranges": {"heater_power": [0.0, 1.0]},
                "signal_units": {"heater_power": "kW"},
            },
            unit_family="bounds",
            source="user_supplied",
        ).model_dump(mode="python")
    )
    context = ModelDiscoveryContext.model_validate(context_payload)
    payload = ready_payload()
    upper = payload["envelope"]["parameter_evidence"][8]
    upper.update(
        {
            "source_fact_ids": ["actuator_kw_bounds"],
            "unit_conversion": "kilowatts_to_watts/v1",
        }
    )

    result = validate_generated_model_payload(payload, context, example_catalog())

    assert result.status == "ready"


@pytest.mark.parametrize("mutation", ["runtime_signal", "runtime_unit"])
def test_experiment_signals_and_units_must_match_the_model(mutation):
    payload = ready_payload()
    experiment = payload["envelope"]["experiment_proposal"]
    if mutation == "runtime_signal":
        experiment["reference"] = {"room_temperature": 24.0}
        experiment["output_bounds"] = {"room_temperature": [15.0, 80.0]}
        experiment["signal_units"] = {
            "heater_power": "W",
            "room_temperature": "degC",
        }
        for item in payload["envelope"]["parameter_evidence"]:
            item["parameter_path"] = item["parameter_path"].replace(
                ".temperature", ".room_temperature"
            )
    else:
        experiment["signal_units"]["temperature"] = "K"
    result = validate_generated_model_payload(
        payload, discovery_context(), example_catalog()
    )
    assert result.status == "rejected"


def test_operating_point_and_validity_region_require_complete_leaf_evidence():
    payload = ready_payload()
    envelope = payload["envelope"]
    envelope["model_role"] = "local_linear_hypothesis"
    envelope["operating_point"] = {
        "description": "The measured heater operating point.",
        "states": {},
        "inputs": {"heater_power": 0.0},
        "outputs": {"temperature": 24.0},
        "signal_units": {"heater_power": "W", "temperature": "degC"},
    }
    envelope["validity_region"] = {
        "description": "The measured local range.",
        "input_ranges": {"heater_power": [0.0, 1000.0]},
        "output_ranges": {"temperature": [15.0, 80.0]},
        "state_ranges": {},
        "signal_units": {"heater_power": "W", "temperature": "degC"},
        "constant_conditions": ["Ambient conditions remain fixed."],
        "out_of_range_effect": "The local model is invalid outside this range.",
    }
    envelope["parameter_evidence"].extend(
        [
            _evidence(
                "operating_point.inputs.heater_power",
                0.0,
                "W",
                ["operating_point"],
            ),
            _evidence(
                "operating_point.outputs.temperature",
                24.0,
                "degC",
                ["operating_point"],
            ),
            _evidence(
                "validity_region.input_ranges.heater_power[0]",
                0.0,
                "W",
                ["validity_region"],
            ),
            _evidence(
                "validity_region.input_ranges.heater_power[1]",
                1000.0,
                "W",
                ["validity_region"],
            ),
            _evidence(
                "validity_region.output_ranges.temperature[0]",
                15.0,
                "degC",
                ["validity_region"],
            ),
            _evidence(
                "validity_region.output_ranges.temperature[1]",
                80.0,
                "degC",
                ["validity_region"],
            ),
        ]
    )
    accepted = validate_generated_model_payload(
        payload, discovery_context(), example_catalog()
    )
    assert accepted.status == "ready"

    payload["envelope"]["parameter_evidence"].pop()
    rejected = validate_generated_model_payload(
        payload, discovery_context(), example_catalog()
    )
    assert rejected.status == "rejected"


def test_envelope_validator_accepts_typed_context_and_rejects_improper_tf():
    result = validate_generated_model_payload(
        ready_payload(), discovery_context(), example_catalog()
    )
    assert result.status == "ready"
    context = ModelValidationContext.model_validate(
        discovery_context().model_dump(mode="python")
    )
    assert (
        validate_generated_model_envelope(result.envelope, context) is result.envelope
    )

    invalid = result.envelope.model_copy(deep=True)
    invalid.model.numerator = [1.0, 2.0, 3.0]
    with pytest.raises(ValueError, match="proper"):
        validate_generated_model_envelope(invalid, context)


@pytest.mark.parametrize(
    "primary_class",
    [
        "class_ii_second_order_oscillator",
        "class_iii_double_or_pure_integrator",
        "class_iv_higher_order_unstable_nonlinear_or_nmp",
        "class_v_multivariable_significant_coupling",
    ],
)
def test_archetype_class_must_match_deterministically_inspectable_structure(
    primary_class,
):
    result = validate_generated_model_payload(
        ready_payload(),
        context_variant(primary_class=primary_class),
        example_catalog(),
    )
    assert result.status == "rejected"


def second_order_payload():
    payload = ready_payload()
    payload["envelope"]["model"]["denominator"] = [5.0, 1.0, 1.0]
    payload["envelope"]["parameter_evidence"].append(
        _evidence(
            "model.denominator[2]",
            1.0,
            "1",
            ["response_time_63"],
            source="deterministic_derivation",
            derivation_rule_id="normalized_one/v1",
        )
    )
    return payload


def test_step_derived_coefficients_fail_closed_for_second_order_models():
    assert (
        validate_generated_model_payload(
            second_order_payload(),
            discovery_context(),
            example_catalog(),
        ).status
        == "rejected"
    )
    class_ii = context_variant(
        primary_class="class_ii_second_order_oscillator",
        diagnosis_updates={
            "relative_degree": {
                "assessment": "low",
                "estimated_order": 2,
            }
        },
    )
    assert (
        validate_generated_model_payload(
            second_order_payload(), class_ii, example_catalog()
        ).status
        == "rejected"
    )


@pytest.mark.parametrize(
    "diagnosis_updates",
    [
        {
            "significant_delay": {
                "assessment": "significant",
                "value": "measured significant delay",
            }
        },
        {
            "minimum_phase": {
                "assessment": "nonminimum_phase",
                "value": "measured inverse response",
            }
        },
        {
            "relative_degree": {
                "assessment": "high",
                "estimated_order": 3,
                "value": "three integrations",
            }
        },
        {
            "nonlinearity_strength": {
                "assessment": "strong_dynamic",
                "value": "strong operating-point dependence",
            }
        },
    ],
)
def test_diagnosis_must_match_inspectable_delay_phase_degree_and_nonlinearity(
    diagnosis_updates,
):
    result = validate_generated_model_payload(
        ready_payload(),
        context_variant(diagnosis_updates=diagnosis_updates),
        example_catalog(),
    )
    assert result.status == "rejected"


def test_significant_delay_tf_passes_with_explicit_proven_delay():
    context_payload = discovery_context().model_dump(mode="python")
    context_payload["diagnosis"]["significant_delay"].update(
        assessment="significant", value="measured two-second delay"
    )
    context_payload["facts"].append(
        ModelFactAnswer(
            fact_id="response_delay",
            fact_type="response_delay",
            answer_text="The measured response delay is 2 seconds.",
            value_payload={"value": 2.0, "unit": "s"},
            unit_family="time",
            source="user_supplied",
        ).model_dump(mode="python")
    )
    payload = ready_payload()
    payload["envelope"]["model"]["input_delay_s"] = 2.0
    payload["envelope"]["parameter_evidence"][3] = _evidence(
        "model.input_delay_s",
        2.0,
        "s",
        ["response_delay"],
        source="deterministic_derivation",
        derivation_rule_id="response_delay/v1",
    )

    assert (
        validate_generated_model_payload(
            payload,
            ModelDiscoveryContext.model_validate(context_payload),
            example_catalog(),
        ).status
        == "ready"
    )


def state_space_ready_payload_and_context():
    context_payload = discovery_context().model_dump(mode="python")
    context_payload["diagnosis"]["significant_delay"].update(
        {
            "status": "known",
            "assessment": "significant",
            "value": "measured significant delay",
            "confidence": 0.95,
            "evidence": ["measured delayed response"],
        }
    )
    operating = next(
        fact
        for fact in context_payload["facts"]
        if fact["fact_id"] == "operating_point"
    )
    operating["value_payload"]["states"] = {"temperature_state": 0.0}
    operating["value_payload"]["signal_units"]["temperature_state"] = "degC"
    validity = next(
        fact
        for fact in context_payload["facts"]
        if fact["fact_id"] == "validity_region"
    )
    validity["value_payload"]["state_ranges"] = {"temperature_state": [-10.0, 100.0]}
    validity["value_payload"]["signal_units"]["temperature_state"] = "degC"
    context_payload["facts"].append(
        ModelFactAnswer(
            fact_id="state_space_data",
            fact_type="state_space_data",
            answer_text="A complete measured one-state realization.",
            value_payload={
                "a": [[-0.2]],
                "b": [[0.4]],
                "c": [[1.0]],
                "d": [[0.0]],
                "matrix_units": {
                    "a": [["1/s"]],
                    "b": [["degC/(W*s)"]],
                    "c": [["1"]],
                    "d": [["degC/W"]],
                },
            },
            unit_family="state_space",
            source="user_supplied",
        ).model_dump(mode="python")
    )
    context = ModelDiscoveryContext.model_validate(context_payload)

    payload = ready_payload()
    envelope = payload["envelope"]
    envelope["model"] = {
        "kind": "state_space",
        "a": [[-0.2]],
        "b": [[0.4]],
        "c": [[1.0]],
        "d": [[0.0]],
        "time_domain": "continuous",
        "sample_time_s": None,
        "state_names": ["temperature_state"],
        "input_signal_ids": ["heater_power"],
        "output_signal_ids": ["temperature"],
        "initial_state": [0.0],
        "signal_units": {
            "temperature_state": "degC",
            "heater_power": "W",
            "temperature": "degC",
        },
        "parameter_uncertainty": {},
    }
    envelope["experiment_proposal"]["initial_state"] = {"temperature_state": 0.0}
    envelope["experiment_proposal"]["signal_units"]["temperature_state"] = "degC"
    envelope["experiment_proposal"]["state_bounds"] = {
        "temperature_state": [-10.0, 100.0]
    }
    envelope["parameter_evidence"] = [
        _evidence("model.a[0][0]", -0.2, "1/s", ["state_space_data"]),
        _evidence("model.b[0][0]", 0.4, "degC/(W*s)", ["state_space_data"]),
        _evidence("model.c[0][0]", 1.0, "1", ["state_space_data"]),
        _evidence("model.d[0][0]", 0.0, "degC/W", ["state_space_data"]),
        _evidence(
            "model.initial_state[0]",
            0.0,
            "degC",
            ["operating_point"],
        ),
        _evidence(
            "experiment_proposal.initial_state.temperature_state",
            0.0,
            "degC",
            ["operating_point"],
        ),
        _evidence(
            "experiment_proposal.state_bounds.temperature_state[0]",
            -10.0,
            "degC",
            ["validity_region"],
        ),
        _evidence(
            "experiment_proposal.state_bounds.temperature_state[1]",
            100.0,
            "degC",
            ["validity_region"],
        ),
        *envelope["parameter_evidence"][4:],
    ]
    return payload, context


def test_significant_delay_state_space_without_delay_representation_fails_closed():
    payload, context = state_space_ready_payload_and_context()
    baseline_payload = context.model_dump(mode="python")
    baseline_payload["diagnosis"]["significant_delay"].update(
        {
            "assessment": "not_significant",
            "value": "no measured delay",
        }
    )
    baseline = ModelDiscoveryContext.model_validate(baseline_payload)

    accepted = validate_generated_model_payload(payload, baseline, example_catalog())

    result = validate_generated_model_payload(payload, context, example_catalog())

    assert accepted.status == "ready"
    assert result.status == "rejected"


def test_response_time_derivation_cannot_attest_state_space_matrix():
    payload, context = state_space_ready_payload_and_context()
    context_payload = context.model_dump(mode="python")
    context_payload["diagnosis"]["significant_delay"].update(
        {
            "assessment": "not_significant",
            "value": "no measured delay",
        }
    )
    context = ModelDiscoveryContext.model_validate(context_payload)
    payload["envelope"]["model"]["b"][0][0] = 5.0
    payload["envelope"]["parameter_evidence"][1] = _evidence(
        "model.b[0][0]",
        5.0,
        "s",
        ["response_time_63"],
        source="deterministic_derivation",
        derivation_rule_id="response_time_63/v1",
    )

    result = validate_generated_model_payload(payload, context, example_catalog())

    assert result.status == "rejected"


@pytest.mark.parametrize(
    ("matrix_name", "evidence_index"),
    [("a", 0), ("b", 1), ("c", 2), ("d", 3)],
)
def test_state_space_matrix_fact_units_must_match_derived_dimensions(
    matrix_name, evidence_index
):
    payload, context = state_space_ready_payload_and_context()
    context_payload = context.model_dump(mode="python")
    context_payload["diagnosis"]["significant_delay"].update(
        assessment="not_significant", value="no measured delay"
    )
    matrix_fact = next(
        fact
        for fact in context_payload["facts"]
        if fact["fact_id"] == "state_space_data"
    )
    matrix_fact["value_payload"]["matrix_units"][matrix_name] = [["kg"]]
    payload["envelope"]["parameter_evidence"][evidence_index]["unit"] = "kg"

    assert (
        validate_generated_model_payload(
            payload,
            ModelDiscoveryContext.model_validate(context_payload),
            example_catalog(),
        ).status
        == "rejected"
    )


def test_discrete_state_space_matrix_units_omit_per_second_dimension():
    payload, context = state_space_ready_payload_and_context()
    context_payload = context.model_dump(mode="python")
    context_payload["diagnosis"]["significant_delay"].update(
        assessment="not_significant", value="no measured delay"
    )
    context_payload["facts"].append(
        ModelFactAnswer(
            fact_id="sample_time",
            fact_type="sample_time",
            answer_text="The sample time is 0.1 seconds.",
            value_payload={"value": 0.1, "unit": "s"},
            unit_family="time",
            source="user_supplied",
        ).model_dump(mode="python")
    )
    matrix_fact = next(
        fact
        for fact in context_payload["facts"]
        if fact["fact_id"] == "state_space_data"
    )
    matrix_fact["value_payload"]["matrix_units"]["a"] = [["1"]]
    matrix_fact["value_payload"]["matrix_units"]["b"] = [["degC/W"]]
    payload["envelope"]["model"].update(time_domain="discrete", sample_time_s=0.1)
    payload["envelope"]["parameter_evidence"][0]["unit"] = "1"
    payload["envelope"]["parameter_evidence"][1]["unit"] = "degC/W"
    payload["envelope"]["parameter_evidence"].append(
        _evidence(
            "model.sample_time_s",
            0.1,
            "s",
            ["sample_time"],
            source="deterministic_derivation",
            derivation_rule_id="sample_time/v1",
        )
    )

    assert (
        validate_generated_model_payload(
            payload,
            ModelDiscoveryContext.model_validate(context_payload),
            example_catalog(),
        ).status
        == "ready"
    )


def test_exact_registered_cartpole_policy_passes_the_deterministic_gate():
    model = cartpole_model()
    runtime = registered_run_envelope(model)
    base = discovery_context()
    diagnosis_payload = base.diagnosis.model_dump(mode="python")
    diagnosis_payload["open_loop_stability"].update(
        {
            "status": "known",
            "assessment": "unstable",
            "value": "unstable equilibrium",
            "confidence": 0.95,
            "evidence": ["registered CartPole equilibrium"],
        }
    )
    diagnosis_payload["coupling_severity"].update(
        {
            "status": "known",
            "assessment": "underactuated",
            "value": "underactuated",
            "confidence": 0.95,
            "evidence": ["one actuator and two outputs"],
        }
    )
    classification_payload = base.classification.model_dump(mode="python")
    classification_payload["primary_class"] = (
        "class_iv_higher_order_unstable_nonlinear_or_nmp"
    )
    context = ModelDiscoveryContext(
        description=SystemDescription(
            text="A registered underactuated CartPole software model.",
            actuators=model.input_signal_ids,
            observed_outputs=model.output_signal_ids,
        ),
        diagnosis=StructuralDiagnosis.model_validate(diagnosis_payload),
        classification=ArchetypeClassification.model_validate(classification_payload),
        facts=[
            ModelFactAnswer(
                fact_id="cartpole_parameters",
                fact_type="cartpole_parameters",
                answer_text="Use these complete registered CartPole parameters.",
                value_payload=model.parameters,
                unit_family="registered_parameters",
                source="user_supplied",
            ),
            ModelFactAnswer(
                fact_id="cartpole_initial_state",
                fact_type="operating_point",
                answer_text="The registered initial state is the upright zero state.",
                value_payload={
                    "states": model.initial_state,
                    "inputs": {},
                    "outputs": {},
                    "signal_units": {
                        name: model.signal_units[name] for name in model.initial_state
                    },
                },
                unit_family="operating_region",
                source="user_supplied",
            ),
            ModelFactAnswer(
                fact_id="cartpole_uncertainty",
                fact_type="parameter_uncertainty",
                answer_text="Relative uncertainty for each declared parameter.",
                value_payload={
                    "values": model.parameter_uncertainty,
                    "parameter_units": {
                        name: "1" for name in model.parameter_uncertainty
                    },
                },
                unit_family="uncertainty",
                source="user_supplied",
            ),
        ],
    )
    parameter_units = {
        "cart_mass_kg": "kg",
        "pole_mass_kg": "kg",
        "com_length_m": "m",
        "pole_inertia_kg_m2": "kg*m^2",
        "cart_friction_n_s_m": "N*s/m",
        "gravity_m_s2": "m/s^2",
        "force_limit_n": "N",
        "cart_position_limit_m": "m",
    }
    evidence = []
    for name, value in model.parameters.items():
        evidence.append(
            _evidence(
                f"model.parameters.{name}",
                value,
                parameter_units[name],
                ["cartpole_parameters"],
            )
        )
    for name, value in model.initial_state.items():
        evidence.append(
            _evidence(
                f"model.initial_state.{name}",
                value,
                model.signal_units[name],
                ["cartpole_initial_state"],
            )
        )
        evidence.append(
            _evidence(
                f"experiment_proposal.initial_state.{name}",
                value,
                model.signal_units[name],
                ["cartpole_initial_state"],
            )
        )
    for name, value in model.parameter_uncertainty.items():
        evidence.append(
            _evidence(
                f"model.parameter_uncertainty.{name}",
                value,
                "1",
                ["cartpole_uncertainty"],
            )
        )
    for name, value in runtime["reference"].items():
        evidence.append(
            _evidence(
                f"experiment_proposal.reference.{name}",
                value,
                model.signal_units[name],
                ["cartpole_parameters"],
                source="registry_policy",
            )
        )
    evidence.extend(
        [
            _evidence(
                "experiment_proposal.horizon_s",
                runtime["horizon_s"],
                "s",
                ["cartpole_parameters"],
                source="registry_policy",
            ),
            _evidence(
                "experiment_proposal.sample_time_s",
                runtime["sample_time_s"],
                "s",
                ["cartpole_parameters"],
                source="registry_policy",
            ),
        ]
    )
    for group_name in ("actuator_bounds", "state_bounds", "output_bounds"):
        for name, bounds in runtime[group_name].items():
            evidence.extend(
                [
                    _evidence(
                        f"experiment_proposal.{group_name}.{name}[0]",
                        bounds[0],
                        model.signal_units[name],
                        ["cartpole_parameters"],
                        source="registry_policy",
                    ),
                    _evidence(
                        f"experiment_proposal.{group_name}.{name}[1]",
                        bounds[1],
                        model.signal_units[name],
                        ["cartpole_parameters"],
                        source="registry_policy",
                    ),
                ]
            )
    envelope = {
        "envelope_schema_version": "generated_model_envelope/v1",
        "model_role": "registered_nonlinear_model",
        "model": model.model_dump(mode="json"),
        "operating_point": None,
        "validity_region": None,
        "parameter_evidence": evidence,
        "assumptions": ["Use the registered five-scenario policy."],
        "limitations": ["This is software-model evidence only."],
        "plain_language_summary": "Registered CartPole model and policy.",
        "equation_latex": [r"\dot{x}=f_{\mathrm{registry}}(x,u)"],
        "experiment_proposal": {
            "initial_state": model.initial_state,
            "reference": runtime["reference"],
            "horizon_s": runtime["horizon_s"],
            "sample_time_s": runtime["sample_time_s"],
            "actuator_bounds": runtime["actuator_bounds"],
            "state_bounds": runtime["state_bounds"],
            "output_bounds": runtime["output_bounds"],
            "signal_units": model.signal_units,
            "evidence_fact_ids": ["cartpole_parameters"],
            "registry_policy_id": "registered_cartpole_five_scenario/v1",
        },
    }
    result = validate_generated_model_payload(
        {
            "status": "ready",
            "envelope": envelope,
            "confidence": 0.35,
            "rationale": "Complete registered evidence.",
        },
        context,
        example_catalog(),
    )
    assert result.status == "ready"

    delayed_context_payload = context.model_dump(mode="python")
    delayed_context_payload["diagnosis"]["significant_delay"].update(
        assessment="significant", value="measured significant delay"
    )
    delayed = validate_generated_model_payload(
        {
            "status": "ready",
            "envelope": envelope,
            "confidence": 0.35,
            "rationale": "Complete registered evidence.",
        },
        ModelDiscoveryContext.model_validate(delayed_context_payload),
        example_catalog(),
    )
    assert delayed.status == "rejected"

    unsafe_policy = deepcopy(
        {
            "status": "ready",
            "envelope": envelope,
            "confidence": 0.35,
            "rationale": "Complete registered evidence.",
        }
    )
    unsafe_policy["envelope"]["parameter_evidence"][0]["source"] = "registry_policy"
    rejected = validate_generated_model_payload(
        unsafe_policy, context, example_catalog()
    )
    assert rejected.status == "rejected"


class FakeDiscoveryAdapter:
    base_url = "https://user:password@example.test/v1?token=URLSECRET"
    model = "fake-MODELSECRET"
    api_key = "LITERAL-API-KEY"

    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.captured_context = None
        self.captured_messages = None
        self.calls = 0

    def propose_model(self, context):
        self.calls += 1
        self.captured_context = context
        self.captured_messages = build_model_discovery_messages(
            context, example_catalog()
        )
        if self.error is not None:
            raise ValueError(self.error)
        return self.response

    def propose_model_with_messages(self, context, messages):
        self.calls += 1
        self.captured_context = context
        self.captured_messages = messages
        if self.error is not None:
            raise ValueError(self.error)
        return self.response

    def propose_gain_update(self, context):
        raise AssertionError("gain path must remain separate")


def test_discovery_fails_closed_when_adapter_cannot_send_exact_messages():
    class LegacyOnlyAdapter:
        base_url = "custom-adapter"
        model = "legacy"
        api_key = ""

        def __init__(self):
            self.calls = 0

        def propose_model(self, _context):
            self.calls += 1
            return need_more_payload(1)

    adapter = LegacyOnlyAdapter()
    result = request_model_discovery(adapter, discovery_context(), example_catalog())

    assert adapter.calls == 0
    assert result.result is None
    assert result.call_record.validation_status == "error"


def alternate_example_catalog():
    payload = example_catalog().model_dump(mode="json")
    payload["examples"][0]["answer_text"] += " Alternate audited wording test-key."
    identity = {key: value for key, value in payload.items() if key != "content_sha256"}
    payload["content_sha256"] = hashlib.sha256(
        json.dumps(
            identity,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()
    return ModelQuestionExampleCatalog.model_validate(payload)


def test_openai_provider_receives_exactly_the_audited_alternate_catalog_prompt(
    monkeypatch,
):
    calls = []

    class FakeCompletions:
        def create(self, **kwargs):
            calls.append(kwargs)
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(
                            content=json.dumps(need_more_payload(1))
                        )
                    )
                ]
            )

    class FakeOpenAI:
        def __init__(self, **_kwargs):
            self.chat = SimpleNamespace(completions=FakeCompletions())

    monkeypatch.setattr("cfdc.diagnosis.llm.OpenAI", FakeOpenAI)
    adapter = OpenAICompatibleDiagnosticAdapter(
        base_url="https://provider.example/v1",
        model="test-model",
        api_key="test-key",
    )
    catalog = alternate_example_catalog()

    result = request_model_discovery(adapter, discovery_context(), catalog)

    audited = [
        message.model_dump(mode="json") for message in result.call_record.messages
    ]
    assert result.result is not None
    assert calls[0]["messages"] == audited
    assert "Alternate audited wording" in calls[0]["messages"][1]["content"]
    assert "test-key" not in json.dumps(calls[0]["messages"])


def test_discovery_call_result_is_separate_and_all_audit_paths_are_sanitized():
    payload = ready_payload()
    payload["envelope"]["plain_language_summary"] += " LITERAL-API-KEY"
    adapter = FakeDiscoveryAdapter(response=payload)
    result = request_model_discovery(
        adapter,
        discovery_context(),
        example_catalog(),
        secret_literals=("MODELSECRET", "URLSECRET"),
    )
    assert isinstance(result, ModelDiscoveryCallResult)
    assert not isinstance(result, ProposalCallResult)
    assert result.result is not None
    assert result.result.status == "ready"
    rendered = result.call_record.model_dump_json()
    for secret in (
        "LITERAL-API-KEY",
        "MODELSECRET",
        "URLSECRET",
        "user:password",
    ):
        assert secret not in rendered
    assert "LITERAL-API-KEY" not in result.model_dump_json()


def test_discovery_error_is_audited_without_leaking_secret():
    adapter = FakeDiscoveryAdapter(error="provider leaked LITERAL-API-KEY")
    result = request_model_discovery(adapter, discovery_context(), example_catalog())
    assert result.result is None
    assert result.call_record.validation_status == "error"
    assert "LITERAL-API-KEY" not in result.call_record.model_dump_json()


def test_secret_literals_are_removed_before_the_provider_receives_context():
    context_payload = discovery_context().model_dump(mode="python")
    context_payload["description"]["text"] += " XYZZY-42"
    context_payload["description"]["metadata"]["nested-XYZZY-42"] = "metadata"
    context_payload["facts"][0]["answer_text"] += " XYZZY-42"
    context = ModelDiscoveryContext.model_validate(context_payload)
    adapter = FakeDiscoveryAdapter(response=need_more_payload(1))

    result = request_model_discovery(
        adapter,
        context,
        example_catalog(),
        secret_literals=("XYZZY-42",),
    )

    assert result.result is not None
    assert adapter.calls == 1
    assert "XYZZY-42" not in adapter.captured_context.model_dump_json()
    assert "XYZZY-42" not in json.dumps(adapter.captured_messages)
    assert "XYZZY-42" not in result.model_dump_json()


@pytest.mark.parametrize(
    "unsafe_text",
    [
        "run os.system('id')",
        "use subprocess.run(['sh'])",
        "execute rm -rf /tmp/model",
        "define dx/dt = user_expression",
        "read ../../etc/passwd",
        "open /Users/alice/model.py",
        "load package.module.Controller",
        "set x_dot = dynamics(x, u)",
        "evaluate eval(user_input)",
    ],
)
def test_unsafe_context_fails_before_adapter_invocation_and_is_audited(
    unsafe_text,
):
    context_payload = discovery_context().model_dump(mode="python")
    context_payload["description"]["text"] = unsafe_text
    context = ModelDiscoveryContext.model_validate(context_payload)
    adapter = FakeDiscoveryAdapter(response=need_more_payload(1))

    result = request_model_discovery(adapter, context, example_catalog())

    assert result.result is None
    assert adapter.calls == 0
    assert result.call_record.validation_status == "error"
    assert "unsafe" in " ".join(result.call_record.validation_errors).casefold()


@pytest.mark.parametrize(
    ("field_name", "malicious_value"),
    [
        ("fact_id", "https://evil.example/fact"),
        ("question_id", "os.system"),
        ("source_fact_ids", ["../../etc/passwd"]),
    ],
)
def test_malicious_identifiers_fail_before_provider_and_never_enter_audit(
    field_name,
    malicious_value,
):
    context_payload = discovery_context().model_dump(mode="python")
    if field_name == "fact_id":
        context_payload["facts"][0]["fact_id"] = malicious_value
    else:
        context_payload["description"]["metadata"][field_name] = malicious_value
    context = ModelDiscoveryContext.model_validate(context_payload)
    adapter = FakeDiscoveryAdapter(response=need_more_payload(1))

    result = request_model_discovery(adapter, context, example_catalog())

    assert adapter.calls == 0
    assert result.result is None
    rendered = result.call_record.model_dump_json()
    if isinstance(malicious_value, list):
        malicious_value = malicious_value[0]
    assert malicious_value not in rendered


@pytest.mark.parametrize(
    ("attack", "malicious"),
    [
        ("metadata_key", "https://evil.example/key"),
        ("nested_key", "../../etc/passwd"),
        ("signal_name", "heater/power"),
    ],
)
def test_unsafe_arbitrary_mapping_keys_fail_before_provider(attack, malicious):
    context_payload = discovery_context().model_dump(mode="python")
    if attack == "metadata_key":
        context_payload["description"]["metadata"][malicious] = "value"
    elif attack == "nested_key":
        context_payload["description"]["metadata"]["nested"] = {malicious: "value"}
    else:
        fact = next(
            item
            for item in context_payload["facts"]
            if item["fact_id"] == "operating_point"
        )
        fact["value_payload"]["inputs"] = {malicious: 0.0}
        fact["value_payload"]["signal_units"].pop("heater_power")
        fact["value_payload"]["signal_units"][malicious] = "W"
    adapter = FakeDiscoveryAdapter(response=need_more_payload(1))

    result = request_model_discovery(
        adapter,
        ModelDiscoveryContext.model_validate(context_payload),
        example_catalog(),
    )

    assert adapter.calls == 0
    assert result.result is None
    assert malicious not in result.call_record.model_dump_json()


@pytest.mark.parametrize(
    ("location", "unsafe_text"),
    [
        ("assumption", "invoke os.system('id')"),
        ("summary", "call subprocess.run(['sh'])"),
        ("rationale", "execute rm -rf /tmp/model"),
        ("question", "read ../../etc/passwd"),
        ("reason", "use dx/dt = eval(user_input)"),
    ],
)
def test_non_executable_text_gate_covers_all_result_text_fields(
    location,
    unsafe_text,
):
    if location == "question":
        payload = need_more_payload(1)
        payload["questions"][0]["prompt"] = unsafe_text
    elif location == "reason":
        payload = {
            "status": "rejected",
            "reason": unsafe_text,
            "next_steps": ["Provide safe numeric facts."],
        }
    else:
        payload = ready_payload()
        if location == "assumption":
            payload["envelope"]["assumptions"][0] = unsafe_text
        elif location == "summary":
            payload["envelope"]["plain_language_summary"] = unsafe_text
        else:
            payload["rationale"] = unsafe_text
    result = validate_generated_model_payload(
        payload, discovery_context(), example_catalog()
    )
    assert result.status == "rejected"


def test_discovery_prompt_demands_typed_three_state_json_and_fixed_examples():
    messages = build_model_discovery_messages(discovery_context(), example_catalog())
    rendered = json.dumps(messages)
    assert "need_more|ready|rejected" in rendered
    assert "equation_latex" in rendered
    assert "thermal.input_step.power.v1" in rendered
    assert "confidence is not a gate" in rendered
    assert "step_ratio_gain/v1" in rendered
    assert "center_actuator_bounds_at_input_before/v1" in rendered
    assert "registry_policy may attest only exact registered experiment" in rendered


def test_ready_result_can_type_a_verbatim_natural_language_answer():
    all_facts = model_facts()
    input_step = next(item for item in all_facts if item.fact_id == "input_step")
    base = discovery_context()
    context = ModelDiscoveryContext(
        description=base.description,
        diagnosis=base.diagnosis,
        classification=base.classification,
        facts=[item for item in all_facts if item.fact_id != "input_step"],
        natural_language_answers=[
            NaturalLanguageModelAnswer(
                question_id="q-input-step",
                fact_id="input_step",
                fact_type="input_step",
                unit_family="power",
                answer_text=input_step.answer_text,
            )
        ],
    )
    payload = ready_payload()
    payload["recognized_facts"] = [input_step.model_dump(mode="json")]

    result = validate_generated_model_payload(
        payload,
        context,
        example_catalog(),
    )

    assert result.status == "ready"
    assert result.recognized_facts == [input_step]


def test_typed_natural_answer_cannot_introduce_an_unwritten_number():
    all_facts = model_facts()
    input_step = next(item for item in all_facts if item.fact_id == "input_step")
    base = discovery_context()
    context = ModelDiscoveryContext(
        description=base.description,
        diagnosis=base.diagnosis,
        classification=base.classification,
        facts=[item for item in all_facts if item.fact_id != "input_step"],
        natural_language_answers=[
            NaturalLanguageModelAnswer(
                question_id="q-input-step",
                fact_id="input_step",
                fact_type="input_step",
                unit_family="power",
                answer_text=input_step.answer_text,
            )
        ],
    )
    invented = input_step.model_copy(
        update={
            "value_payload": {
                "before": 0.0,
                "after": 3.0,
                "unit": "W",
            }
        }
    )
    payload = ready_payload()
    payload["recognized_facts"] = [invented.model_dump(mode="json")]

    assert (
        validate_generated_model_payload(
            payload,
            context,
            example_catalog(),
        ).status
        == "rejected"
    )
