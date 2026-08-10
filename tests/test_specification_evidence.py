import math

import pytest
from pydantic import ValidationError

from cfdc.diagnosis import (
    migrate_diagnostic_session_payload,
    start_diagnostic_session,
    submit_measurement_assessment,
    submit_specifications_to_session,
)
from cfdc.diagnosis.llm import build_specification_prompt
from cfdc.models import (
    DiagnosticSessionState,
    MeasuredFact,
    MeasurementAssessment,
    SpecificationAssessment,
    SpecificationFact,
    SystemDescription,
)
from cfdc.runtime import run_cfdc_route
from cfdc.specifications import (
    assess_specification_text,
    build_initial_specification_assessment,
    compile_specification_model,
    default_specification_template_catalog,
    normalize_scalar_unit,
    validate_specification_assessment_payload,
)

_DIAGNOSTIC_FACTS = {
    "open_loop_stability": "settles or remains bounded",
    "minimum_phase": (
        "starts in its final direction rather than moving the opposite way first"
    ),
    "significant_delay": (
        "begins within one sample without a separate silent interval"
    ),
    "relative_degree": "one or two dominant storage or integration processes",
    "controllability_observability": (
        "all relevant motion can be reconstructed from these synchronized records"
    ),
    "nonlinearity_strength": (
        "small positive and negative trials are smooth, reversible, and nearly proportional"
    ),
    "coupling_severity": (
        "one main physical route from actuation to the measured motion"
    ),
    "uncertainty_magnitude": (
        "change the response rate and final level by a modest amount"
    ),
}


def _heater_description() -> SystemDescription:
    return SystemDescription(
        text="A measured electric heater settles after a small power change.",
        observed_outputs=["temperature"],
        actuators=["heater power"],
    )


def _profile_measurement_session():
    report = run_cfdc_route("generic", description=_heater_description())
    session = start_diagnostic_session(
        report.system_description, diagnosis=report.diagnosis
    )
    measurement_assessment = MeasurementAssessment(
        status="ready",
        facts=[
            MeasuredFact(
                request_id=request.request_id,
                source_excerpt=_DIAGNOSTIC_FACTS[request.request_id],
                text_value=_DIAGNOSTIC_FACTS[request.request_id],
            )
            for request in session.measurement_plan.requests
        ],
    )
    verified = submit_measurement_assessment(
        session,
        measurement_assessment,
        raw_response="\n".join(
            fact.source_excerpt for fact in measurement_assessment.facts
        ),
        expected_revision=session.revision,
    )
    payload = verified.model_dump(mode="python")
    payload.update(
        {
            "revision": verified.revision + 1,
            "classification": report.classification,
            "semantic_selection": report.semantic_selection,
            "experiment_plan": report.experiment_plan,
            "evidence_requirement_plan": report.evidence_requirement_plan,
            "specification_templates": report.specification_templates,
            "specification_assessment": report.specification_assessment,
            "candidate_route": report.candidate_route,
            "compiled_route": report.compiled_route,
            "status": "awaiting_profile_measurements",
        }
    )
    return DiagnosticSessionState.model_validate(payload)


def test_complete_diagnosis_enters_object_specific_specification_stage():
    report = run_cfdc_route("generic", description=_heater_description())

    assert report.status == "awaiting_specifications"
    assert report.specification_assessment is not None
    assert report.experiment_results == []
    assert report.features == []
    assert report.controller is None
    rendered = " ".join(
        item.prompt for item in report.specification_assessment.questions
    )
    assert "heater power" in rendered or "temperature" in rendered
    assert "三次" not in rendered
    assert "CSV" not in rendered
    assert "natural_frequency" not in rendered


@pytest.mark.parametrize(
    ("profile_id", "expected_phrase"),
    [
        ("first_order_lag", "最终变化"),
        ("second_order_oscillator", "相邻两次"),
        ("double_integrator", "加速度"),
        ("nmp_inverse_response", "反向"),
        ("generic_unstable_higher_order", "完整数值模型"),
        ("underactuated_cartpole", "小车"),
        ("vtol_cascaded", "飞行器"),
        ("mimo_2x2_coupled", "交叉影响"),
    ],
)
def test_each_method_profile_has_plain_language_specification_guidance(
    profile_id, expected_phrase
):
    catalog = default_specification_template_catalog()
    template = next(
        item for item in catalog.templates if item.method_profile_id == profile_id
    )
    description = SystemDescription(
        text=f"A user described {profile_id} object.",
        observed_outputs=["measured output"],
        actuators=["available actuator"],
    )
    assessment = build_initial_specification_assessment(description, template)

    text = " ".join(item.prompt for item in assessment.questions)
    assert expected_phrase in text
    assert all(item.why_needed for item in assessment.questions)
    assert all(item.where_to_find for item in assessment.questions)
    assert all(item.answer_options for item in assessment.questions)
    assert len(assessment.questions) <= 4


def test_continuous_dynamic_questions_exclude_discrete_status_outputs():
    template = next(
        item
        for item in default_specification_template_catalog().templates
        if item.method_profile_id == "first_order_lag"
    )
    description = SystemDescription(
        text="A binary heater controls room temperature through thermostat hysteresis.",
        observed_outputs=["室温", "加热器状态"],
        actuators=["二值加热命令"],
    )

    assessment = build_initial_specification_assessment(description, template)
    dynamic_questions = [
        item
        for item in assessment.questions
        if item.requested_fact_ids[0] in {"steady_output_change", "response_time_s"}
    ]

    assert dynamic_questions
    assert all("室温" in item.prompt for item in dynamic_questions)
    assert all("加热器状态" not in item.prompt for item in dynamic_questions)


def test_first_order_template_calls_user_ranges_simulation_boundaries():
    template = next(
        item
        for item in default_specification_template_catalog().templates
        if item.method_profile_id == "first_order_lag"
    )
    rendered = " ".join(
        [
            template.user_summary,
            *(field.label for field in template.fields),
            *(field.prompt_template for field in template.fields),
            *(field.why_needed for field in template.fields),
        ]
    )

    assert "仿真运行" in rendered
    assert "真实安全范围" not in rendered
    assert "真实执行器" not in rendered


def test_specification_prompt_contains_object_profile_templates_and_history():
    report = run_cfdc_route("generic", description=_heater_description())
    prompt = build_specification_prompt(
        report.system_description,
        report.diagnosis,
        report.classification,
        report.semantic_selection.simulation_profile_id,
        report.specification_templates,
        ["The manual says a 1 kW change produces 10 degC."],
        report.specification_assessment,
    )

    assert "electric heater" in prompt
    assert "first_order_lag" in prompt
    assert "1 kW change produces 10 degC" in prompt
    assert "Do not infer or invent" in prompt
    assert "derived_from_declared_physics" in prompt
    assert "thermal_time_constant_c_over_h" in prompt
    assert "backend will recompute" in prompt
    assert "Do not produce controller gains" in prompt


def test_explicit_thermostat_physics_complete_first_order_specifications_without_llm():
    report = run_cfdc_route(
        "generic",
        description=SystemDescription(
            text=(
                "A binary heater command controls room temperature through fixed "
                "thermostat hysteresis. The temperature settles, starts promptly in "
                "the final direction, and has no repeated peaks."
            ),
            observed_outputs=["room temperature", "heater state"],
            actuators=["binary heater command"],
        ),
    )
    assert report.status == "awaiting_specifications"
    assert report.semantic_selection.simulation_profile_id == "first_order_lag"

    assessment = assess_specification_text(
        report.system_description,
        report.specification_templates[0],
        (
            "室外温度 50 degF、白天设定值 65 degF；等效热容 C = 20000 Btu/degF、"
            "传热系数 H = 500 Btu/(h degF)、炉子供热率 25000 Btu/h、"
            "滞环半宽 0.5 degF。令初温为下阈值 64.5 degF 且炉子开启，"
            "以 60 s 采样仿真 6 h。"
        ),
        previous=report.specification_assessment,
    )

    facts = {item.fact_id: item for item in assessment.facts}
    assert assessment.status == "ready"
    assert facts["input_change"].value == pytest.approx(1.0)
    assert facts["input_change"].unit == "binary_command"
    assert facts["steady_output_change"].value == pytest.approx(50.0)
    assert facts["steady_output_change"].unit == "degF"
    assert facts["steady_output_change"].source_type == "derived_from_declared_physics"
    assert (
        facts["steady_output_change"].derivation.rule_id
        == "thermal_steady_rise_q_over_h"
    )
    assert facts["response_time_s"].value == pytest.approx(144000.0)
    assert (
        facts["response_time_s"].derivation.rule_id == "thermal_time_constant_c_over_h"
    )
    assert facts["output_min"].value == pytest.approx(64.5)
    assert facts["output_max"].value == pytest.approx(65.5)
    assert (
        facts["output_min"].derivation.rule_id
        == "thermostat_band_setpoint_plus_minus_half_width"
    )
    assert facts["input_min"].derivation.rule_id == "binary_command_domain"
    compiled = compile_specification_model(
        plant_id="thermostat-room",
        description=report.system_description,
        template=report.specification_templates[0],
        assessment=assessment,
    )
    assert compiled.derived_features["static_gain"] == pytest.approx(50.0)
    assert compiled.derived_features["time_constant"] == pytest.approx(144000.0)


def test_explicit_thermostat_physics_complete_specifications_with_llm_enabled():
    report = run_cfdc_route(
        "generic",
        description=SystemDescription(
            text=(
                "A binary heater command controls room temperature through fixed "
                "thermostat hysteresis. The temperature settles promptly."
            ),
            observed_outputs=["room temperature", "heater state"],
            actuators=["binary heater command"],
        ),
    )
    paragraph = (
        "室外温度 50 degF、白天设定值 65 degF；等效热容 C = 20000 Btu/degF、"
        "传热系数 H = 500 Btu/(h degF)、炉子供热率 25000 Btu/h、"
        "滞环半宽 0.5 degF。"
    )

    class ConservativeAdapter:
        def assess_specifications(self, *args):
            del args
            return {
                "status": "need_more",
                "template_id": report.specification_templates[0].template_id,
                "facts": [],
                "missing_fact_ids": [
                    "input_change",
                    "steady_output_change",
                    "response_time_s",
                    "input_min",
                    "input_max",
                    "output_min",
                    "output_max",
                ],
                "conflicts": [],
                "questions": [],
                "rationale": "No direct numeric fact was extracted.",
            }

    assessment = assess_specification_text(
        report.system_description,
        report.specification_templates[0],
        paragraph,
        previous=report.specification_assessment,
        adapter=ConservativeAdapter(),
        diagnosis=report.diagnosis,
        classification=report.classification,
        method_profile_id=report.semantic_selection.simulation_profile_id,
    )

    facts = {item.fact_id: item for item in assessment.facts}
    assert assessment.status == "ready"
    assert facts["steady_output_change"].value == pytest.approx(50.0)
    assert facts["response_time_s"].value == pytest.approx(144000.0)
    assert facts["output_min"].value == pytest.approx(64.5)
    assert facts["output_max"].value == pytest.approx(65.5)


def test_validated_llm_questions_are_used_for_the_current_object_and_gap():
    report = run_cfdc_route("generic", description=_heater_description())
    template = report.specification_templates[0]

    class TailoredSpecificationAdapter:
        def assess_specifications(self, *args):
            return {
                "status": "need_more",
                "template_id": template.template_id,
                "facts": [
                    {
                        "fact_id": "input_change",
                        "value": 1.0,
                        "unit": "kW",
                        "source_type": "manufacturer_document",
                        "source_text": "input change is 1 kW",
                        "lower_bound": None,
                        "upper_bound": None,
                    }
                ],
                "missing_fact_ids": ["steady_output_change"],
                "conflicts": [],
                "questions": [
                    {
                        "question_id": "heater_final_temperature_change",
                        "requested_fact_ids": ["steady_output_change"],
                        "prompt": "加热功率增加 1 kW 后，这台恒温箱最终升温多少？",
                        "why_needed": "用来计算这台恒温箱的实际加热作用。",
                        "where_to_find": "可查看恒温箱手册中的温升/功率规格。",
                        "answer_kind": "number",
                        "unit_hint": "degC / K",
                        "example": "例如：最终升高 10 degC。",
                        "answer_options": [
                            "填写已知数值",
                            "粘贴手册规格",
                            "暂时不知道",
                            "改用完整数值模型",
                        ],
                    }
                ],
                "rationale": "One explicit fact was extracted.",
            }

    assessment = assess_specification_text(
        report.system_description,
        template,
        "The manual says the input change is 1 kW.",
        previous=report.specification_assessment,
        adapter=TailoredSpecificationAdapter(),
        diagnosis=report.diagnosis,
        classification=report.classification,
        method_profile_id=report.semantic_selection.simulation_profile_id,
    )

    assert assessment.facts[0].fact_id == "input_change"
    assert assessment.questions[0].question_id == "heater_final_temperature_change"
    assert "恒温箱" in assessment.questions[0].prompt


def test_llm_fact_with_fabricated_source_is_reported_as_rejected_no_progress():
    report = run_cfdc_route("generic", description=_heater_description())
    template = report.specification_templates[0]

    class FabricatedSourceAdapter:
        def assess_specifications(self, *args):
            del args
            return {
                "status": "need_more",
                "template_id": template.template_id,
                "facts": [
                    {
                        "fact_id": "input_change",
                        "value": 1.0,
                        "unit": "kW",
                        "source_type": "user_known_behavior",
                        "source_text": "the manual explicitly says 1 kW",
                    }
                ],
                "missing_fact_ids": ["input_change"],
                "conflicts": [],
                "questions": [],
                "rationale": "A candidate fact was found.",
            }

    assessment = assess_specification_text(
        report.system_description,
        template,
        "I do not know the heater power change.",
        previous=report.specification_assessment,
        adapter=FabricatedSourceAdapter(),
        diagnosis=report.diagnosis,
        classification=report.classification,
        method_profile_id=report.semantic_selection.simulation_profile_id,
    )

    assert assessment.facts == []
    assert assessment.no_progress is True
    assert any("verbatim" in item for item in assessment.rejected_facts)


def test_specification_fact_requires_numeric_value_unit_and_source_text():
    with pytest.raises(ValidationError):
        SpecificationFact(
            fact_id="response_time_s",
            value=30.0,
            unit="s",
            source_type="user_known_behavior",
            source_text="",
        )


def test_vague_language_cannot_become_a_numeric_fact():
    session = _profile_measurement_session()

    updated = submit_specifications_to_session(
        session,
        specification_text="The heater responds very quickly and has a strong effect.",
    )

    assert updated.status == "awaiting_profile_measurements"
    assert updated.specification_assessment.facts == []
    assert updated.compiled_specification_model is None


def test_multiple_plain_language_turns_reduce_gaps_and_compile_only_when_complete():
    session = _profile_measurement_session()
    partial = submit_specifications_to_session(
        session,
        "Manual: input_change=1 normalized_input; steady_output_change=10 degC; response_time_s=20 s.",
    )

    assert partial.status == "awaiting_profile_measurements"
    assert len(partial.specification_assessment.missing_fact_ids) == 4
    assert partial.compiled_specification_model is None

    complete = submit_specifications_to_session(
        partial,
        "Manual: input_min=-2 normalized_input; input_max=2 normalized_input; output_min=-30 degC; output_max=80 degC.",
        simulation_bounds_confirmed=True,
    )

    assert complete.status == "specification_model_ready"
    assert complete.compiled_specification_model is not None
    assert complete.specification_answer_history == [
        "Manual: input_change=1 normalized_input; steady_output_change=10 degC; response_time_s=20 s.",
        "Manual: input_min=-2 normalized_input; input_max=2 normalized_input; output_min=-30 degC; output_max=80 degC.",
    ]


def test_conflicting_specification_values_stop_model_compilation():
    session = _profile_measurement_session()
    first = submit_specifications_to_session(
        session,
        "input_change=1 normalized_input;",
    )
    conflict = submit_specifications_to_session(
        first,
        "input_change=2 normalized_input;",
    )

    assert conflict.status == "specification_conflict"
    assert conflict.specification_assessment.conflicts
    assert conflict.compiled_specification_model is None

    corrected = submit_specifications_to_session(
        conflict,
        "input_change=2 normalized_input;",
    )
    assert corrected.status == "awaiting_profile_measurements"
    assert corrected.specification_assessment.conflicts == []


def test_cross_field_unit_conflict_stops_before_model_compilation():
    report = run_cfdc_route(
        "generic",
        description=_heater_description(),
        specification_text=(
            "input_change=1 kW; steady_output_change=10 degC; response_time_s=20 s; "
            "input_min=0 N; input_max=2 N; output_min=-30 degC; output_max=80 degC."
        ),
    )

    assert report.status == "specification_conflict"
    assert report.compiled_specification_model is None
    assert report.features == []
    assert report.controller is None
    assert any(
        "incompatible units" in item
        for item in report.specification_assessment.conflicts
    )


def test_common_unit_spellings_and_scales_are_normalized():
    assert normalize_scalar_unit(1000.0, "mV") == pytest.approx((1.0, "V"))
    assert normalize_scalar_unit(180.0, "deg") == pytest.approx((math.pi, "rad"))
    assert normalize_scalar_unit(100.0, "ms") == pytest.approx((0.1, "s"))
    assert normalize_scalar_unit(1.0, "rad/s²") == pytest.approx((1.0, "rad/s^2"))
    assert normalize_scalar_unit(1.0, "N·m") == pytest.approx((1.0, "Nm"))


def test_consistent_opaque_command_units_are_allowed_for_behavioral_specs():
    report = run_cfdc_route(
        "generic",
        description=_heater_description(),
        specification_text=(
            "Manual: input_change=100 DAC_count; steady_output_change=10 ADC_count; "
            "response_time_s=20 sec; input_min=0 DAC_count; "
            "input_max=4095 DAC_count; output_min=0 ADC_count; "
            "output_max=32767 ADC_count."
        ),
    )

    assert report.status == "candidate_unvalidated"
    assert report.compiled_specification_model.model.input_units == "DAC_count"
    assert report.compiled_specification_model.model.output_units == "ADC_count"


def test_inconsistent_opaque_command_units_request_a_conversion_relationship():
    report = run_cfdc_route(
        "generic",
        description=_heater_description(),
        specification_text=(
            "Manual: input_change=100 DAC_count; steady_output_change=10 degC; "
            "response_time_s=20 s; input_min=0 V; input_max=4095 DAC_count; "
            "output_min=-30 degC; output_max=80 degC."
        ),
    )

    assert report.status == "specification_conflict"
    assert any(
        "conversion relationship" in item
        for item in report.specification_assessment.conflicts
    )


def test_number_without_a_unit_remains_a_specification_gap():
    report = run_cfdc_route(
        "generic",
        description=_heater_description(),
        specification_text=(
            "Manual: input_change=1; steady_output_change=10 degC; "
            "response_time_s=20 s; input_min=0 W; input_max=2 W; "
            "output_min=-30 degC; output_max=80 degC."
        ),
    )

    assert report.status == "need_more_specifications"
    assert "input_change" in report.specification_assessment.missing_fact_ids
    assert all(
        item.fact_id != "input_change" for item in report.specification_assessment.facts
    )
    assert any(
        "单位" in item.prompt for item in report.specification_assessment.questions
    )


def test_llm_specification_payload_rejects_unknown_facts_and_extra_keys_but_recovers_unit_issues():
    template = next(
        item
        for item in default_specification_template_catalog().templates
        if item.method_profile_id == "first_order_lag"
    )
    base = {
        "status": "need_more",
        "template_id": template.template_id,
        "facts": [],
        "missing_fact_ids": ["input_change"],
        "conflicts": [],
        "questions": [],
        "rationale": "More explicit specifications are required.",
    }
    with pytest.raises(ValidationError):
        SpecificationAssessment.model_validate({**base, "invented": 1})

    unknown = {
        **base,
        "facts": [
            {
                "fact_id": "invented_gain",
                "value": 1.0,
                "unit": "ratio",
                "source_type": "user_known_behavior",
                "source_text": "gain=1",
            }
        ],
    }
    with pytest.raises(ValueError, match="unknown specification fact"):
        validate_specification_assessment_payload(
            unknown, template=template, source_texts=["gain=1"]
        )

    wrong_unit = {
        **base,
        "facts": [
            {
                "fact_id": "response_time_s",
                "value": 1.0,
                "unit": "kg",
                "source_type": "manufacturer_document",
                "source_text": "time=1 kg",
            }
        ],
    }
    incompatible = validate_specification_assessment_payload(
        wrong_unit, template=template, source_texts=["time=1 kg"]
    )
    assert incompatible.status == "conflict"
    assert incompatible.facts == []
    assert any("response_time_s" in item for item in incompatible.conflicts)

    missing_unit = {
        **base,
        "facts": [
            {
                "fact_id": "response_time_s",
                "value": 1.0,
                "unit": "",
                "source_type": "manufacturer_document",
                "source_text": "time=1",
            }
        ],
    }
    recovered = validate_specification_assessment_payload(
        missing_unit, template=template, source_texts=["time=1"]
    )
    assert recovered.status == "need_more"
    assert recovered.facts == []
    assert "response_time_s" in recovered.missing_fact_ids

    leaked_protocol = {
        **base,
        "questions": [
            {
                "question_id": "bad_internal_question",
                "requested_fact_ids": ["response_time_s"],
                "prompt": "Please provide time_constant by uploading CSV three times.",
                "why_needed": "Needed for natural_frequency.",
                "where_to_find": "CSV",
                "answer_kind": "number",
                "unit_hint": "s",
                "example": "time_constant=1",
                "answer_options": [
                    "填写已知数值",
                    "粘贴手册规格",
                    "暂时不知道",
                    "改用完整数值模型",
                ],
            }
        ],
    }
    with pytest.raises(ValueError, match="user-facing specification question"):
        validate_specification_assessment_payload(
            leaked_protocol, template=template, source_texts=[]
        )


def test_llm_registered_derivation_is_recomputed_from_verbatim_inputs():
    template = next(
        item
        for item in default_specification_template_catalog().templates
        if item.method_profile_id == "first_order_lag"
    )
    heat_capacity_source = "thermal capacitance is 20000 Btu/degF"
    heat_transfer_source = "envelope conductance is 500 Btu/(h degF)"
    payload = {
        "status": "need_more",
        "template_id": template.template_id,
        "facts": [
            {
                "fact_id": "response_time_s",
                "value": 144000.0,
                "unit": "s",
                "source_type": "derived_from_declared_physics",
                "source_text": "C/H = 40 h = 144000 s",
                "derivation": {
                    "rule_id": "thermal_time_constant_c_over_h",
                    "expression": "3600 * heat_capacity / heat_transfer_coefficient",
                    "inputs": [
                        {
                            "name": "heat_capacity",
                            "value": 20000.0,
                            "unit": "Btu/degF",
                            "source_text": heat_capacity_source,
                        },
                        {
                            "name": "heat_transfer_coefficient",
                            "value": 500.0,
                            "unit": "Btu/(h degF)",
                            "source_text": heat_transfer_source,
                        },
                    ],
                    "source_excerpts": [heat_capacity_source, heat_transfer_source],
                },
            }
        ],
        "missing_fact_ids": [
            "input_change",
            "steady_output_change",
            "input_min",
            "input_max",
            "output_min",
            "output_max",
        ],
        "conflicts": [],
        "questions": [],
        "rationale": "The time constant was derived from declared physics.",
    }

    assessment = validate_specification_assessment_payload(
        payload,
        template=template,
        source_texts=[f"{heat_capacity_source}; {heat_transfer_source}."],
    )

    fact = assessment.facts[0]
    assert fact.value == pytest.approx(144000.0)
    assert fact.source_type == "derived_from_declared_physics"
    assert fact.derivation.rule_id == "thermal_time_constant_c_over_h"


def test_all_registered_thermostat_derivation_rules_are_backend_verified():
    template = next(
        item
        for item in default_specification_template_catalog().templates
        if item.method_profile_id == "first_order_lag"
    )
    binary_source = "binary heater command"
    rate_source = "furnace rate is 25000 Btu/h"
    transfer_source = "heat transfer coefficient is 500 Btu/(h degF)"
    setpoint_source = "setpoint is 65 degF"
    band_source = "hysteresis half-width is 0.5 degF"

    def derived_fact(fact_id, value, unit, rule_id, expression, inputs, excerpts):
        return {
            "fact_id": fact_id,
            "value": value,
            "unit": unit,
            "source_type": "derived_from_declared_physics",
            "source_text": expression,
            "derivation": {
                "rule_id": rule_id,
                "expression": expression,
                "inputs": inputs,
                "source_excerpts": excerpts,
            },
        }

    binary_facts = [
        derived_fact(
            fact_id,
            value,
            "binary_command",
            "binary_command_domain",
            "binary command domain {0, 1}",
            [],
            [binary_source],
        )
        for fact_id, value in (
            ("input_change", 1.0),
            ("input_min", 0.0),
            ("input_max", 1.0),
        )
    ]
    transfer_input = {
        "name": "heat_transfer_coefficient",
        "value": 500.0,
        "unit": "Btu/(h degF)",
        "source_text": transfer_source,
    }
    steady_fact = derived_fact(
        "steady_output_change",
        50.0,
        "degF",
        "thermal_steady_rise_q_over_h",
        "furnace_rate / heat_transfer_coefficient",
        [
            {
                "name": "furnace_rate",
                "value": 25000.0,
                "unit": "Btu/h",
                "source_text": rate_source,
            },
            transfer_input,
        ],
        [rate_source, transfer_source],
    )
    band_inputs = [
        {
            "name": "setpoint",
            "value": 65.0,
            "unit": "degF",
            "source_text": setpoint_source,
        },
        {
            "name": "hysteresis_half_width",
            "value": 0.5,
            "unit": "degF",
            "source_text": band_source,
        },
    ]
    band_facts = [
        derived_fact(
            fact_id,
            value,
            "degF",
            "thermostat_band_setpoint_plus_minus_half_width",
            expression,
            band_inputs,
            [setpoint_source, band_source],
        )
        for fact_id, value, expression in (
            ("output_min", 64.5, "setpoint - hysteresis_half_width"),
            ("output_max", 65.5, "setpoint + hysteresis_half_width"),
        )
    ]
    payload = {
        "status": "need_more",
        "template_id": template.template_id,
        "facts": [*binary_facts, steady_fact, *band_facts],
        "missing_fact_ids": ["response_time_s"],
        "conflicts": [],
        "questions": [],
        "rationale": "Registered thermostat rules were proposed.",
    }

    assessment = validate_specification_assessment_payload(
        payload,
        template=template,
        source_texts=[
            (
                f"{binary_source}; {rate_source}; {transfer_source}; "
                f"{setpoint_source}; {band_source}."
            )
        ],
    )

    facts = {item.fact_id: item.value for item in assessment.facts}
    assert facts == {
        "input_change": 1.0,
        "input_min": 0.0,
        "input_max": 1.0,
        "steady_output_change": 50.0,
        "output_min": 64.5,
        "output_max": 65.5,
    }
    assert assessment.rejected_facts == []


@pytest.mark.parametrize(
    ("rule_id", "declared_value", "source_override", "expected_reason"),
    [
        ("thermal_time_constant_c_over_h", 1.0, None, "backend recomputation"),
        ("unregistered_formula", 144000.0, None, "unregistered"),
        (
            "thermal_time_constant_c_over_h",
            144000.0,
            "a fabricated heat capacity excerpt",
            "verbatim",
        ),
    ],
)
def test_unverified_llm_derivations_are_rejected_as_remaining_gaps(
    rule_id, declared_value, source_override, expected_reason
):
    template = next(
        item
        for item in default_specification_template_catalog().templates
        if item.method_profile_id == "first_order_lag"
    )
    heat_capacity_source = "thermal capacitance is 20000 Btu/degF"
    heat_transfer_source = "envelope conductance is 500 Btu/(h degF)"
    payload = {
        "status": "need_more",
        "template_id": template.template_id,
        "facts": [
            {
                "fact_id": "response_time_s",
                "value": declared_value,
                "unit": "s",
                "source_type": "derived_from_declared_physics",
                "source_text": "candidate thermal time constant",
                "derivation": {
                    "rule_id": rule_id,
                    "expression": "3600 * C / H",
                    "inputs": [
                        {
                            "name": "heat_capacity",
                            "value": 20000.0,
                            "unit": "Btu/degF",
                            "source_text": source_override or heat_capacity_source,
                        },
                        {
                            "name": "heat_transfer_coefficient",
                            "value": 500.0,
                            "unit": "Btu/(h degF)",
                            "source_text": heat_transfer_source,
                        },
                    ],
                    "source_excerpts": [
                        source_override or heat_capacity_source,
                        heat_transfer_source,
                    ],
                },
            }
        ],
        "missing_fact_ids": ["response_time_s"],
        "conflicts": [],
        "questions": [],
        "rationale": "Candidate derivation requires verification.",
    }

    assessment = validate_specification_assessment_payload(
        payload,
        template=template,
        source_texts=[f"{heat_capacity_source}; {heat_transfer_source}."],
    )

    assert assessment.status == "need_more"
    assert assessment.facts == []
    assert assessment.missing_fact_ids == ["response_time_s"]
    assert any(expected_reason in item for item in assessment.rejected_facts)


def test_motor_voltage_paragraph_compiles_with_unicode_units_and_no_unit_whitelist_error():
    template = next(
        item
        for item in default_specification_template_catalog().templates
        if item.method_profile_id == "double_integrator"
    )
    description = SystemDescription(
        text=(
            "A low-friction motor positioning axis accelerates under applied voltage "
            "and keeps moving without a restoring spring."
        ),
        observed_outputs=["motor position"],
        actuators=["motor voltage"],
    )
    paragraph = (
        "The held motor voltage has a baseline of 0.0 V and an allowed operating "
        "range of −5.0 V to +5.0 V. For the safe identification test, the voltage "
        "is changed by +0.5 V and then by −0.5 V in a separate reverse-direction "
        "trial. A +0.5 V voltage change produces an angular-acceleration change of "
        "approximately +1.0 rad/s², while a −0.5 V change produces approximately "
        "−1.0 rad/s². The corresponding estimated input gain is therefore "
        "approximately 2.0 rad/s²/V. In normal operation, a typical motor-position "
        "target change of 1.0 rad takes approximately 2.0 s to enter and remain within "
        "±2% of the target. The permitted position range is −2.5 rad to +2.5 rad, "
        "and identification tests are stopped if the absolute position exceeds 2.0 rad. "
        "Motor position is sampled at 100 Hz."
    )

    class MotorSpecificationAdapter:
        def assess_specifications(self, *args):
            del args
            return {
                "status": "ready",
                "template_id": template.template_id,
                "facts": [
                    {
                        "fact_id": "input_change",
                        "value": 0.5,
                        "unit": "V",
                        "source_type": "user_known_behavior",
                        "source_text": "voltage is changed by +0.5 V",
                    },
                    {
                        "fact_id": "acceleration_change",
                        "value": 1.0,
                        "unit": "rad/s²",
                        "source_type": "user_known_behavior",
                        "source_text": "angular-acceleration change of approximately +1.0 rad/s²",
                    },
                    {
                        "fact_id": "motion_time_scale_s",
                        "value": 2.0,
                        "unit": "sec",
                        "source_type": "user_known_behavior",
                        "source_text": "takes approximately 2.0 s",
                    },
                    {
                        "fact_id": "input_min",
                        "value": -5.0,
                        "unit": "V",
                        "source_type": "user_known_behavior",
                        "source_text": "range of −5.0 V to +5.0 V",
                    },
                    {
                        "fact_id": "input_max",
                        "value": 5.0,
                        "unit": "V",
                        "source_type": "user_known_behavior",
                        "source_text": "range of −5.0 V to +5.0 V",
                    },
                    {
                        "fact_id": "output_min",
                        "value": -2.5,
                        "unit": "rad",
                        "source_type": "user_known_behavior",
                        "source_text": "permitted position range is −2.5 rad to +2.5 rad",
                    },
                    {
                        "fact_id": "output_max",
                        "value": 2.5,
                        "unit": "rad",
                        "source_type": "user_known_behavior",
                        "source_text": "permitted position range is −2.5 rad to +2.5 rad",
                    },
                ],
                "missing_fact_ids": [],
                "conflicts": [],
                "questions": [],
                "rationale": "All required facts were explicitly stated.",
            }

    assessment = assess_specification_text(
        description,
        template,
        paragraph,
        previous=build_initial_specification_assessment(description, template),
        adapter=MotorSpecificationAdapter(),
    )
    compiled = compile_specification_model(
        plant_id="motor-axis",
        description=description,
        template=template,
        assessment=assessment,
    )

    assert assessment.status == "ready"
    assert {item.fact_id: item.unit for item in assessment.facts}[
        "acceleration_change"
    ] == "rad/s^2"
    assert compiled.model.input_units == "V"
    assert compiled.model.output_units == "rad"
    assert compiled.derived_features["input_gain"] == pytest.approx(2.0)


def test_known_acceleration_and_position_dimensions_must_describe_the_same_motion():
    template = next(
        item
        for item in default_specification_template_catalog().templates
        if item.method_profile_id == "double_integrator"
    )
    description = SystemDescription(
        text="A motor axis accelerates under voltage and has no restoring spring.",
        observed_outputs=["shaft angle"],
        actuators=["motor voltage"],
    )

    assessment = assess_specification_text(
        description,
        template,
        (
            "input_change=0.5 V; acceleration_change=1 m/s^2; "
            "motion_time_scale_s=2 s; input_min=-5 V; input_max=5 V; "
            "output_min=-2.5 rad; output_max=2.5 rad."
        ),
    )

    assert assessment.status == "conflict"
    assert any(
        "acceleration" in item and "position" in item for item in assessment.conflicts
    )


def test_physical_acceleration_requires_conversion_for_opaque_position_units():
    template = next(
        item
        for item in default_specification_template_catalog().templates
        if item.method_profile_id == "double_integrator"
    )
    description = SystemDescription(
        text="A motor axis reports position in encoder counts.",
        observed_outputs=["encoder position"],
        actuators=["motor voltage"],
    )

    assessment = assess_specification_text(
        description,
        template,
        (
            "input_change=0.5 V; acceleration_change=1 rad/s^2; "
            "motion_time_scale_s=2 s; input_min=-5 V; input_max=5 V; "
            "output_min=-2000 encoder_count; output_max=2000 encoder_count."
        ),
    )

    assert assessment.status == "conflict"
    assert any("conversion relationship" in item for item in assessment.conflicts)


def test_opaque_position_and_its_second_derivative_form_a_valid_behavioral_path():
    template = next(
        item
        for item in default_specification_template_catalog().templates
        if item.method_profile_id == "double_integrator"
    )
    description = SystemDescription(
        text="A motor axis reports position in encoder counts.",
        observed_outputs=["encoder position"],
        actuators=["motor voltage"],
    )
    assessment = assess_specification_text(
        description,
        template,
        (
            "input_change=0.5 V; acceleration_change=100 encoder_count/s^2; "
            "motion_time_scale_s=2 s; input_min=-5 V; input_max=5 V; "
            "output_min=-2000 encoder_count; output_max=2000 encoder_count."
        ),
    )

    assert assessment.status == "ready"
    compiled = compile_specification_model(
        plant_id="encoder-axis",
        description=description,
        template=template,
        assessment=assessment,
    )
    assert compiled.model.output_units == "encoder_count"
    assert compiled.derived_features["input_gain"] == pytest.approx(200.0)


def test_physical_mass_and_actuator_units_must_belong_to_the_same_motion_domain():
    template = next(
        item
        for item in default_specification_template_catalog().templates
        if item.method_profile_id == "double_integrator"
    )
    assessment = assess_specification_text(
        SystemDescription(
            text="A translating stage is driven by a voltage-controlled actuator.",
            observed_outputs=["position"],
            actuators=["voltage"],
        ),
        template,
        (
            "mass_kg=10 kg; actuator_force_per_input=2 Nm/V; "
            "motion_time_scale_s=2 s; input_min=-5 V; input_max=5 V; "
            "output_min=-1 m; output_max=1 m."
        ),
    )

    assert assessment.status == "conflict"
    assert any("mass" in item and "torque" in item for item in assessment.conflicts)


def _first_order_specification_text(*, input_change, output_change, tau):
    return (
        f"From the equipment manual: input_change={input_change} normalized_input; "
        f"steady_output_change={output_change} degC; "
        f"response_time_s={tau} s; input_min=-2 normalized_input; "
        "input_max=2 normalized_input; output_min=-30 degC; output_max=80 degC."
    )


def test_two_same_class_natural_language_specifications_produce_different_candidates():
    description = _heater_description()
    first = run_cfdc_route(
        "generic",
        description=description,
        specification_text=_first_order_specification_text(
            input_change=1.0,
            output_change=10.0,
            tau=20.0,
        ),
    )
    second = run_cfdc_route(
        "generic",
        description=description,
        specification_text=_first_order_specification_text(
            input_change=2.0,
            output_change=6.0,
            tau=80.0,
        ),
    )

    assert first.status == second.status == "candidate_unvalidated"
    assert (
        first.controller.release_level
        == second.controller.release_level
        == "candidate_unvalidated"
    )
    assert (
        first.evidence_boundary
        == second.evidence_boundary
        == "declared_specification_model_only"
    )
    assert first.final_gains != second.final_gains
    first_features = {item.feature_id: item.value for item in first.features}
    second_features = {item.feature_id: item.value for item in second.features}
    assert first_features["static_gain"] != pytest.approx(
        second_features["static_gain"]
    )
    assert first_features["time_constant"] != pytest.approx(
        second_features["time_constant"]
    )
    assert first.controller_validation is None
    assert all(
        item.model_sha256 == first.compiled_specification_model.model_sha256
        for item in first.features
    )


def test_natural_language_specifications_reject_reversed_safety_bounds():
    report = run_cfdc_route(
        "generic",
        description=_heater_description(),
        specification_text=(
            "input_change=1 V; steady_output_change=10 degC; response_time_s=20 s; "
            "input_min=5 V; input_max=-5 V; "
            "output_min=-30 degC; output_max=80 degC."
        ),
    )

    assert report.status == "specification_conflict"
    assert report.controller is None
    assert any(
        "input_min" in item for item in report.specification_assessment.conflicts
    )


def test_equivalent_declared_units_compile_to_the_same_canonical_object_model():
    description = _heater_description()
    kilowatts = run_cfdc_route(
        "generic",
        description=description,
        specification_text=(
            "Manual: input_change=1 kW; steady_output_change=10 degC; "
            "response_time_s=20 s; input_min=0 kW; input_max=2 kW; "
            "output_min=-30 degC; output_max=80 degC."
        ),
    )
    watts = run_cfdc_route(
        "generic",
        description=description,
        specification_text=(
            "Manual: input_change=1000 W; steady_output_change=10 degC; "
            "response_time_s=20 s; input_min=0 W; input_max=2000 W; "
            "output_min=-30 degC; output_max=80 degC."
        ),
    )

    assert kilowatts.status == watts.status == "candidate_unvalidated"
    assert kilowatts.compiled_specification_model.model.input_units == "W"
    assert kilowatts.compiled_specification_model.model.numerator == pytest.approx(
        watts.compiled_specification_model.model.numerator
    )
    assert kilowatts.final_gains == pytest.approx(watts.final_gains)


def test_second_order_behavioral_specs_compile_with_deterministic_formulas():
    catalog = default_specification_template_catalog()
    template = next(
        item
        for item in catalog.templates
        if item.method_profile_id == "second_order_oscillator"
    )
    facts = [
        SpecificationFact(
            fact_id="oscillation_period_s",
            value=2.0,
            unit="s",
            source_type="manufacturer_document",
            source_text="period=2 s",
        ),
        SpecificationFact(
            fact_id="successive_peak_ratio",
            value=0.5,
            unit="ratio",
            source_type="user_known_behavior",
            source_text="next peak is 50%",
        ),
        SpecificationFact(
            fact_id="input_change",
            value=2.0,
            unit="N",
            source_type="manufacturer_document",
            source_text="input change 2 N",
        ),
        SpecificationFact(
            fact_id="acceleration_change",
            value=4.0,
            unit="m/s^2",
            source_type="manufacturer_document",
            source_text="acceleration 4 m/s^2",
        ),
    ]
    assessment = SpecificationAssessment(
        status="ready",
        template_id=template.template_id,
        facts=facts,
        missing_fact_ids=[],
        conflicts=[],
        questions=[],
        rationale="All behavioral specification fields were explicitly provided.",
    )

    from cfdc.specifications import compile_specification_model

    compiled = compile_specification_model(
        plant_id="spring-1",
        description=SystemDescription(
            text="spring mass", observed_outputs=["position"], actuators=["force"]
        ),
        template=template,
        assessment=assessment,
    )

    assert compiled.model.kind == "transfer_function"
    assert compiled.derived_features["natural_frequency"] == pytest.approx(math.pi)
    assert 0.0 < compiled.derived_features["damping_ratio"] < 1.0
    assert compiled.derived_features["input_gain"] == pytest.approx(2.0)
    assert compiled.evidence_boundary == "declared_specification_model_only"


def test_second_order_plain_language_specs_generate_an_unvalidated_candidate():
    report = run_cfdc_route(
        "generic",
        description=SystemDescription(
            text="A measured spring vibrates and its free motion decays after release.",
            observed_outputs=["position"],
            actuators=["force"],
        ),
        specification_text=(
            "Manual: oscillation_period_s=2 s; successive_peak_ratio=0.5 ratio; "
            "input_change=2 N; acceleration_change=4 m/s^2; "
            "input_min=-10 N; input_max=10 N; output_min=-1 m; output_max=1 m."
        ),
    )

    assert report.status == "candidate_unvalidated"
    assert {item.feature_id for item in report.features} == {
        "natural_frequency",
        "damping_ratio",
        "input_gain",
    }
    assert report.controller.release_level == "candidate_unvalidated"


def test_cartpole_specifications_do_not_relabel_an_unsupported_controller_as_candidate():
    report = run_cfdc_route(
        "generic",
        description=SystemDescription(
            text=(
                "A rod hinged on a cart falls over when upright. The cart motor pushes "
                "left and right. Cart position and rod angle are measured."
            ),
            observed_outputs=["cart position", "rod angle"],
            actuators=["cart motor force"],
        ),
        specification_text=(
            "cart_mass_kg=0.5 kg; pole_mass_kg=0.2 kg; com_length_m=0.3 m; "
            "pole_inertia_kg_m2=0.006 kg*m^2; "
            "cart_friction_n_s_m=0.1 N*s/m; gravity_m_s2=9.81 m/s^2; "
            "force_limit_n=10 N; cart_position_limit_m=2.4 m."
        ),
    )

    assert report.status == "rejected"
    assert report.controller.status == "refuse"
    assert report.controller.release_level == "refuse"
    assert report.evidence_boundary == "declared_specification_model_only"


def test_inverse_response_specs_compile_without_reusing_demo_severity():
    report = run_cfdc_route(
        "generic",
        description=SystemDescription(
            text="A stable tank settles but first moves opposite after a valve change.",
            observed_outputs=["level"],
            actuators=["valve"],
        ),
        specification_text=(
            "Manual: input_change=1 input_unit; steady_output_change=10 output_unit; "
            "inverse_peak_change=-2 output_unit; inverse_recovery_time_s=3 s; "
            "response_time_s=20 s; input_min=-2 input_unit; input_max=2 input_unit; "
            "output_min=-30 output_unit; output_max=80 output_unit."
        ),
    )

    assert report.status == "candidate_unvalidated"
    severity = next(
        item.value
        for item in report.features
        if item.feature_id == "inverse_response_severity"
    )
    assert severity == pytest.approx(0.2, rel=0.2)
    assert report.controller.release_level == "candidate_unvalidated"


def test_schema_v2_evidence_session_restarts_at_v4_measurement_gate():
    report = run_cfdc_route("generic", description=_heater_description())
    session = start_diagnostic_session(
        report.system_description, diagnosis=report.diagnosis
    )
    legacy = session.model_dump(mode="json")
    legacy["schema_version"] = "2.0"
    legacy["status"] = "awaiting_evidence"
    legacy.pop("specification_assessment", None)
    legacy.pop("specification_templates", None)

    migrated = migrate_diagnostic_session_payload(legacy)

    assert migrated.schema_version == "4.0"
    assert migrated.status == "awaiting_measurements"
    assert migrated.current_diagnosis == session.current_diagnosis
    assert migrated.specification_assessment is None
