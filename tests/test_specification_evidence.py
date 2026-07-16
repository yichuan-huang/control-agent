import math

import pytest
from pydantic import ValidationError

from cfdc.diagnosis import (
    migrate_diagnostic_session_payload,
    start_diagnostic_session,
    submit_specifications_to_session,
)
from cfdc.diagnosis.llm import build_specification_prompt
from cfdc.models import (
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


def _heater_description() -> SystemDescription:
    return SystemDescription(
        text="A measured electric heater settles after a small power change.",
        observed_outputs=["temperature"],
        actuators=["heater power"],
    )


def test_complete_diagnosis_enters_object_specific_specification_stage():
    report = run_cfdc_route("generic", description=_heater_description())

    assert report.status == "awaiting_specifications"
    assert report.specification_assessment is not None
    assert report.experiment_results == []
    assert report.features == []
    assert report.controller is None
    rendered = " ".join(item.prompt for item in report.specification_assessment.questions)
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
    template = next(item for item in catalog.templates if item.method_profile_id == profile_id)
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
    assert "Do not produce controller gains" in prompt


def test_validated_llm_questions_are_used_for_the_current_object_and_gap():
    report = run_cfdc_route("generic", description=_heater_description())
    template = report.specification_templates[0]

    class TailoredSpecificationAdapter:
        def assess_specifications(self, *args):
            return {
                "status": "need_more",
                "template_id": template.template_id,
                "facts": [{
                    "fact_id": "input_change",
                    "value": 1.0,
                    "unit": "kW",
                    "source_type": "manufacturer_document",
                    "source_text": "input change is 1 kW",
                    "lower_bound": None,
                    "upper_bound": None,
                }],
                "missing_fact_ids": ["steady_output_change"],
                "conflicts": [],
                "questions": [{
                    "question_id": "heater_final_temperature_change",
                    "requested_fact_ids": ["steady_output_change"],
                    "prompt": "加热功率增加 1 kW 后，这台恒温箱最终升温多少？",
                    "why_needed": "用来计算这台恒温箱的实际加热作用。",
                    "where_to_find": "可查看恒温箱手册中的温升/功率规格。",
                    "answer_kind": "number",
                    "unit_hint": "degC / K",
                    "example": "例如：最终升高 10 degC。",
                    "answer_options": [
                        "填写已知数值", "粘贴手册规格", "暂时不知道", "改用完整数值模型"
                    ],
                }],
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
    report = run_cfdc_route("generic", description=_heater_description())
    session = start_diagnostic_session(
        report.system_description,
        diagnosis=report.diagnosis,
    )

    updated = submit_specifications_to_session(
        session,
        specification_text="The heater responds very quickly and has a strong effect.",
    )

    assert updated.status == "need_more_specifications"
    assert updated.specification_assessment.facts == []
    assert updated.compiled_specification_model is None


def test_multiple_plain_language_turns_reduce_gaps_and_compile_only_when_complete():
    report = run_cfdc_route("generic", description=_heater_description())
    session = start_diagnostic_session(report.system_description, diagnosis=report.diagnosis)
    partial = submit_specifications_to_session(
        session,
        "Manual: input_change=1 normalized_input; steady_output_change=10 degC; response_time_s=20 s.",
    )

    assert partial.status == "need_more_specifications"
    assert len(partial.specification_assessment.missing_fact_ids) == 4
    assert partial.compiled_specification_model is None

    complete = submit_specifications_to_session(
        partial,
        "Manual: input_min=-2 normalized_input; input_max=2 normalized_input; output_min=-30 degC; output_max=80 degC.",
    )

    assert complete.status == "specification_model_ready"
    assert complete.compiled_specification_model is not None
    assert complete.specification_answer_history == [
        "Manual: input_change=1 normalized_input; steady_output_change=10 degC; response_time_s=20 s.",
        "Manual: input_min=-2 normalized_input; input_max=2 normalized_input; output_min=-30 degC; output_max=80 degC.",
    ]


def test_conflicting_specification_values_stop_model_compilation():
    report = run_cfdc_route("generic", description=_heater_description())
    session = start_diagnostic_session(report.system_description, diagnosis=report.diagnosis)
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
    assert corrected.status == "need_more_specifications"
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
    assert any("incompatible units" in item for item in report.specification_assessment.conflicts)


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
    assert all(item.fact_id != "input_change" for item in report.specification_assessment.facts)
    assert any("单位" in item.prompt for item in report.specification_assessment.questions)


def test_llm_specification_payload_rejects_unknown_facts_and_extra_keys_but_recovers_unit_issues():
    template = next(
        item for item in default_specification_template_catalog().templates
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
        "facts": [{
            "fact_id": "invented_gain", "value": 1.0, "unit": "ratio",
            "source_type": "user_known_behavior", "source_text": "gain=1",
        }],
    }
    with pytest.raises(ValueError, match="unknown specification fact"):
        validate_specification_assessment_payload(
            unknown, template=template, source_texts=["gain=1"]
        )

    wrong_unit = {
        **base,
        "facts": [{
            "fact_id": "response_time_s", "value": 1.0, "unit": "kg",
            "source_type": "manufacturer_document", "source_text": "time=1 kg",
        }],
    }
    incompatible = validate_specification_assessment_payload(
        wrong_unit, template=template, source_texts=["time=1 kg"]
    )
    assert incompatible.status == "conflict"
    assert incompatible.facts == []
    assert any("response_time_s" in item for item in incompatible.conflicts)

    missing_unit = {
        **base,
        "facts": [{
            "fact_id": "response_time_s", "value": 1.0, "unit": "",
            "source_type": "manufacturer_document", "source_text": "time=1",
        }],
    }
    recovered = validate_specification_assessment_payload(
        missing_unit, template=template, source_texts=["time=1"]
    )
    assert recovered.status == "need_more"
    assert recovered.facts == []
    assert "response_time_s" in recovered.missing_fact_ids

    leaked_protocol = {
        **base,
        "questions": [{
            "question_id": "bad_internal_question",
            "requested_fact_ids": ["response_time_s"],
            "prompt": "Please provide time_constant by uploading CSV three times.",
            "why_needed": "Needed for natural_frequency.",
            "where_to_find": "CSV",
            "answer_kind": "number",
            "unit_hint": "s",
            "example": "time_constant=1",
            "answer_options": [
                "填写已知数值", "粘贴手册规格", "暂时不知道", "改用完整数值模型"
            ],
        }],
    }
    with pytest.raises(ValueError, match="user-facing specification question"):
        validate_specification_assessment_payload(
            leaked_protocol, template=template, source_texts=[]
        )


def test_motor_voltage_paragraph_compiles_with_unicode_units_and_no_unit_whitelist_error():
    template = next(
        item for item in default_specification_template_catalog().templates
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
                        "fact_id": "input_change", "value": 0.5, "unit": "V",
                        "source_type": "user_known_behavior",
                        "source_text": "voltage is changed by +0.5 V",
                    },
                    {
                        "fact_id": "acceleration_change", "value": 1.0,
                        "unit": "rad/s²", "source_type": "user_known_behavior",
                        "source_text": "angular-acceleration change of approximately +1.0 rad/s²",
                    },
                    {
                        "fact_id": "motion_time_scale_s", "value": 2.0,
                        "unit": "sec", "source_type": "user_known_behavior",
                        "source_text": "takes approximately 2.0 s",
                    },
                    {
                        "fact_id": "input_min", "value": -5.0, "unit": "V",
                        "source_type": "user_known_behavior",
                        "source_text": "range of −5.0 V to +5.0 V",
                    },
                    {
                        "fact_id": "input_max", "value": 5.0, "unit": "V",
                        "source_type": "user_known_behavior",
                        "source_text": "range of −5.0 V to +5.0 V",
                    },
                    {
                        "fact_id": "output_min", "value": -2.5, "unit": "rad",
                        "source_type": "user_known_behavior",
                        "source_text": "permitted position range is −2.5 rad to +2.5 rad",
                    },
                    {
                        "fact_id": "output_max", "value": 2.5, "unit": "rad",
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
    assert {item.fact_id: item.unit for item in assessment.facts}["acceleration_change"] == "rad/s^2"
    assert compiled.model.input_units == "V"
    assert compiled.model.output_units == "rad"
    assert compiled.derived_features["input_gain"] == pytest.approx(2.0)


def test_known_acceleration_and_position_dimensions_must_describe_the_same_motion():
    template = next(
        item for item in default_specification_template_catalog().templates
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
    assert any("acceleration" in item and "position" in item for item in assessment.conflicts)


def test_physical_acceleration_requires_conversion_for_opaque_position_units():
    template = next(
        item for item in default_specification_template_catalog().templates
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
        item for item in default_specification_template_catalog().templates
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
        item for item in default_specification_template_catalog().templates
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
    assert first.controller.release_level == second.controller.release_level == "candidate_unvalidated"
    assert first.evidence_boundary == second.evidence_boundary == "declared_specification_model_only"
    assert first.final_gains != second.final_gains
    first_features = {item.feature_id: item.value for item in first.features}
    second_features = {item.feature_id: item.value for item in second.features}
    assert first_features["static_gain"] != pytest.approx(second_features["static_gain"])
    assert first_features["time_constant"] != pytest.approx(second_features["time_constant"])
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
    assert any("input_min" in item for item in report.specification_assessment.conflicts)


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
        item for item in catalog.templates
        if item.method_profile_id == "second_order_oscillator"
    )
    facts = [
        SpecificationFact(
            fact_id="oscillation_period_s", value=2.0, unit="s",
            source_type="manufacturer_document", source_text="period=2 s",
        ),
        SpecificationFact(
            fact_id="successive_peak_ratio", value=0.5, unit="ratio",
            source_type="user_known_behavior", source_text="next peak is 50%",
        ),
        SpecificationFact(
            fact_id="input_change", value=2.0, unit="N",
            source_type="manufacturer_document", source_text="input change 2 N",
        ),
        SpecificationFact(
            fact_id="acceleration_change", value=4.0, unit="m/s^2",
            source_type="manufacturer_document", source_text="acceleration 4 m/s^2",
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
        "natural_frequency", "damping_ratio", "input_gain"
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
        item.value for item in report.features
        if item.feature_id == "inverse_response_severity"
    )
    assert severity == pytest.approx(0.2, rel=0.2)
    assert report.controller.release_level == "candidate_unvalidated"


def test_schema_v2_evidence_session_migrates_to_specifications_without_losing_diagnosis():
    report = run_cfdc_route("generic", description=_heater_description())
    session = start_diagnostic_session(report.system_description, diagnosis=report.diagnosis)
    legacy = session.model_dump(mode="json")
    legacy["schema_version"] = "2.0"
    legacy["status"] = "awaiting_evidence"
    legacy.pop("specification_assessment", None)
    legacy.pop("specification_templates", None)

    migrated = migrate_diagnostic_session_payload(legacy)

    assert migrated.schema_version == "3.0"
    assert migrated.status == "awaiting_specifications"
    assert migrated.current_diagnosis == session.current_diagnosis
    assert migrated.specification_assessment is not None
