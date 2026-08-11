from __future__ import annotations

import pytest

from cfdc.diagnosis import (
    continue_description_session,
    migrate_diagnostic_session_payload,
    start_diagnostic_session,
)
from cfdc.diagnosis.engine import infer_description_field_assessment
from cfdc.diagnosis.measurements import description_excerpt_answers_field
from cfdc.models import SystemDescription
from cfdc.runtime import run_cfdc_route
from cfdc.web import service as web_service
from cfdc.web import ui as web_ui
from cfdc.web.presentation import render_report
from cfdc.workflow import deterministic_profile_selection

AUTOMOTIVE_DESCRIPTION = (
    "这是一个在道路上行驶、由发动机牵引力克服空气与滚动阻力的汽车纵向运动系统。"
    "控制输入是油门角度，输出是由传感器或同步记录器连续获取的车速。"
    "在多次小幅且可逆的试验中，车速开始时就沿最终方向变化，不会先向相反方向运动；"
    "油门角度改变后，车速在一个采样周期内就开始变化，不会出现独立静默区间，而且"
    "从执行作用到可见响应只涉及一到两个主导储能或积分过程。"
    "把油门角度恢复到基准值后，车速最终会收敛或保持有界，不会出现自行增长的运动。"
    "分别施加小幅正向和反向的油门角度变化时，响应平滑、可逆且近似成比例，在限定"
    "范围内没有明显死区、滞回或幅值截断。油门角度与车速采用同一时钟记录，因此这些"
    "同步记录足以重建所有相关运动；装置只有一条从执行作用到被测运动的主要物理通道，"
    "其他给定量只作为扰动进入。在安全范围内改变负载、元件或运行条件并重复试验时，"
    "车速的运动方向、响应时机和最终水平都几乎不变。"
)

_EXCERPTS = {
    "open_loop_stability": (
        "把油门角度恢复到基准值后，车速最终会收敛或保持有界，不会出现自行增长的运动。"
    ),
    "minimum_phase": (
        "在多次小幅且可逆的试验中，车速开始时就沿最终方向变化，不会先向相反方向运动；"
        "油门角度改变后，车速在一个采样周期内就开始变化，不会出现独立静默区间，而且"
        "从执行作用到可见响应只涉及一到两个主导储能或积分过程。"
    ),
    "significant_delay": (
        "油门角度改变后，车速在一个采样周期内就开始变化，不会出现独立静默区间"
    ),
    "relative_degree": "从执行作用到可见响应只涉及一到两个主导储能或积分过程",
    "controllability_observability": (
        "油门角度与车速采用同一时钟记录，因此这些同步记录足以重建所有相关运动"
    ),
    "nonlinearity_strength": (
        "分别施加小幅正向和反向的油门角度变化时，响应平滑、可逆且近似成比例，在限定"
        "范围内没有明显死区、滞回或幅值截断"
    ),
    "coupling_severity": (
        "装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入"
    ),
    "uncertainty_magnitude": (
        "在安全范围内改变负载、元件或运行条件并重复试验时，车速的运动方向、响应时机"
        "和最终水平都几乎不变"
    ),
}


class DescriptionGroundedAdapter:
    def __init__(self, responses: dict[str, str] | None = None):
        self.responses = responses or _EXCERPTS

    def guide_description(self, description, guidance):
        del description
        return {
            "guidance": [
                {
                    **item.model_dump(mode="json"),
                    "response": self.responses.get(item.diagnostic_field_id, "unknown"),
                }
                for item in guidance
            ],
            "observed_outputs": [],
            "actuators": [],
        }

    def phrase_measurement_plan(self, description, checklist, plan):
        del description, checklist
        return plan.model_dump(mode="json")

    def extract_measurements(
        self, description, measurement_plan, measurement_response, previous_assessment
    ):
        del description, measurement_plan, measurement_response, previous_assessment
        raise AssertionError(
            "a complete problem description must not trigger the repeated eight-item reply"
        )

    def select_profile(self, description, diagnosis, classification, catalog):
        return deterministic_profile_selection(
            description, diagnosis, classification, catalog
        ).model_dump(mode="json")


_PROFILE_RESPONSE = (
    "已有记录表明油门角变化 1 deg 时，稳态车速变化 10 mph，达到最终变化约 63% "
    "需要 5 s。软件仿真油门范围为 -3 deg 至 3 deg，车速停止边界为 45 mph 至 "
    "80 mph。"
)


def _profile_fact(fact_id: str, value: float, unit: str, source_text: str):
    return {
        "fact_id": fact_id,
        "value": value,
        "unit": unit,
        "source_type": "user_known_behavior",
        "source_text": source_text,
        "derivation": None,
        "lower_bound": None,
        "upper_bound": None,
    }


_PROFILE_FACTS = [
    _profile_fact("input_change", 1.0, "deg", "油门角变化 1 deg"),
    _profile_fact("steady_output_change", 10.0, "mph", "稳态车速变化 10 mph"),
    _profile_fact("response_time_s", 5.0, "s", "达到最终变化约 63% 需要 5 s"),
    _profile_fact("input_min", -3.0, "deg", "软件仿真油门范围为 -3 deg 至 3 deg"),
    _profile_fact("input_max", 3.0, "deg", "软件仿真油门范围为 -3 deg 至 3 deg"),
    _profile_fact("output_min", 45.0, "mph", "车速停止边界为 45 mph 至 80 mph"),
    _profile_fact("output_max", 80.0, "mph", "车速停止边界为 45 mph 至 80 mph"),
]


class ProfileReplyAdapter(DescriptionGroundedAdapter):
    def extract_measurements(
        self, description, measurement_plan, measurement_response, previous_assessment
    ):
        del description, measurement_plan
        assert measurement_response == _PROFILE_RESPONSE
        assert previous_assessment is not None
        assert previous_assessment.status == "ready"
        return previous_assessment.model_dump(mode="json")

    def assess_specifications(
        self,
        description,
        diagnosis,
        classification,
        method_profile_id,
        allowed_specification_templates,
        accumulated_specification_answers,
        previous_assessment,
    ):
        del description, diagnosis, classification, previous_assessment
        assert method_profile_id == "first_order_lag"
        assert accumulated_specification_answers == [_PROFILE_RESPONSE]
        assert [item.template_id for item in allowed_specification_templates] == [
            "spec_first_order_lag"
        ]
        return {
            "status": "ready",
            "template_id": "spec_first_order_lag",
            "facts": _PROFILE_FACTS,
            "missing_fact_ids": [],
            "conflicts": [],
            "rejected_facts": [],
            "questions": [],
            "rationale": "All selected-Profile facts are grounded in the reply.",
            "no_progress": False,
        }


def test_complete_description_is_grounded_and_routes_without_measurement_round():
    report = run_cfdc_route(
        "generic",
        description=SystemDescription(text=AUTOMOTIVE_DESCRIPTION),
        diagnostic_adapter=DescriptionGroundedAdapter(),
    )

    session = report.diagnostic_session
    assert report.status == "awaiting_profile_measurements"
    assert report.classification is not None
    assert report.semantic_selection is not None
    assert session is not None
    assert session.status == "awaiting_profile_measurements"
    assert session.evidence_level == "description_grounded"
    assert session.description_assessment is not None
    assert session.description_assessment.status == "ready"
    assert session.measurement_round_count == 0
    assert session.measurement_history == []
    assert session.measurement_response_history == []
    assert report.specification_assessment is not None
    assert report.specification_assessment.questions


def test_incomplete_description_uses_collecting_description_as_real_state():
    responses = dict(_EXCERPTS)
    responses.pop("uncertainty_magnitude")

    session = start_diagnostic_session(
        SystemDescription(text=AUTOMOTIVE_DESCRIPTION),
        diagnostic_adapter=DescriptionGroundedAdapter(responses),
    )

    assert session.status == "collecting_description"
    assert session.evidence_level == "description_only"
    assert session.description_assessment is None
    assert session.checklist[-1].status == "unknown"
    assert session.classification is None
    assert session.semantic_selection is None


def test_persisted_description_grounding_is_revalidated_without_repeating_measurement():
    adapter = DescriptionGroundedAdapter()
    initial = run_cfdc_route(
        "generic",
        description=SystemDescription(text=AUTOMOTIVE_DESCRIPTION),
        diagnostic_adapter=adapter,
    )

    migrated = migrate_diagnostic_session_payload(
        initial.diagnostic_session.model_dump(mode="json")
    )

    assert migrated.status == "description_grounded"
    assert migrated.evidence_level == "description_grounded"
    assert migrated.classification is None
    assert migrated.semantic_selection is None
    assert migrated.description_assessment is not None
    assert migrated.measurement_round_count == 0
    assert migrated.measurement_history == []

    resumed = run_cfdc_route(
        "generic",
        diagnostic_session_state=migrated,
        diagnostic_adapter=adapter,
    )

    assert resumed.status == "awaiting_profile_measurements"
    assert resumed.classification is not None
    assert resumed.semantic_selection is not None
    assert resumed.diagnostic_session.measurement_round_count == 0


def test_first_user_reply_after_complete_description_is_profile_data_only():
    adapter = ProfileReplyAdapter()
    initial = run_cfdc_route(
        "generic",
        description=SystemDescription(text=AUTOMOTIVE_DESCRIPTION),
        diagnostic_adapter=adapter,
    )

    completed = run_cfdc_route(
        "generic",
        diagnostic_session_state=initial.diagnostic_session,
        diagnostic_adapter=adapter,
        measurement_response=_PROFILE_RESPONSE,
        simulation_bounds_confirmed=True,
    )

    session = completed.diagnostic_session
    assert completed.status == "candidate_unvalidated"
    assert completed.compiled_specification_model is not None
    assert completed.controller is not None
    assert session.measurement_round_count == 0
    assert session.measurement_history == []
    assert session.measurement_response_history == []
    assert session.profile_measurement_round_count == 1
    assert session.specification_answer_history == [_PROFILE_RESPONSE]
    assert (
        session.description_assessment
        == initial.diagnostic_session.description_assessment
    )


def test_complete_description_view_shows_profile_questions_not_eight_item_plan():
    report = run_cfdc_route(
        "generic",
        description=SystemDescription(text=AUTOMOTIVE_DESCRIPTION),
        diagnostic_adapter=DescriptionGroundedAdapter(),
    )

    view = render_report(report)

    assert view["checklist_collapsed"] is True
    assert view["checklist_title"] == "诊断检查清单（8/8 已完成）"
    assert [row[1] for row in view["checklist"]] == ["✓ 描述证据已核验"] * 8
    assert "补充当前设备的已知规格" in view["measurement_guidance"]
    assert "63% 响应时间" in view["measurement_guidance"]
    assert "open_loop_stability" not in view["measurement_guidance"]
    assert "Review an existing record" not in view["measurement_guidance"]
    assert view["route"]
    assert view["progress"].index("系统分类") < view["progress"].index(
        "核心参数测量计划"
    )


def test_incomplete_description_view_keeps_checklist_open_and_hides_parameters():
    responses = dict(_EXCERPTS)
    responses.pop("uncertainty_magnitude")
    report = run_cfdc_route(
        "generic",
        description=SystemDescription(text=AUTOMOTIVE_DESCRIPTION),
        diagnostic_adapter=DescriptionGroundedAdapter(responses),
    )

    view = render_report(report)

    assert report.status == "need_more_information"
    assert view["checklist_collapsed"] is False
    assert view["checklist_title"] == "诊断检查清单（7/8 已完成）"
    assert view["measurement_guidance"].startswith("### 八项问题描述尚未完成")
    assert "63% 响应时间" not in view["measurement_guidance"]
    assert view["route"] == []


def test_gradio_callback_collapses_only_a_completed_grounded_checklist():
    complete = run_cfdc_route(
        "generic",
        description=SystemDescription(text=AUTOMOTIVE_DESCRIPTION),
        diagnostic_adapter=DescriptionGroundedAdapter(),
    )
    incomplete_responses = dict(_EXCERPTS)
    incomplete_responses.pop("uncertainty_magnitude")
    incomplete = run_cfdc_route(
        "generic",
        description=SystemDescription(text=AUTOMOTIVE_DESCRIPTION),
        diagnostic_adapter=DescriptionGroundedAdapter(incomplete_responses),
    )

    complete_outputs = web_ui._outputs(complete, {})
    incomplete_outputs = web_ui._outputs(incomplete, {})

    assert complete_outputs[5]["label"] == "诊断检查清单（8/8 已完成）"
    assert complete_outputs[5]["open"] is False
    assert incomplete_outputs[5]["label"] == "诊断检查清单（7/8 已完成）"
    assert incomplete_outputs[5]["open"] is True


def test_profile_parameters_already_in_description_are_prefilled_without_a_round():
    input_excerpt = "已有规格记录写明油门角变化 1 deg"
    output_excerpt = "对应稳态车速变化 10 mph"
    description_text = f"{AUTOMOTIVE_DESCRIPTION}{input_excerpt}，{output_excerpt}。"

    class DescriptionPrefillAdapter(DescriptionGroundedAdapter):
        def assess_specifications(
            self,
            description,
            diagnosis,
            classification,
            method_profile_id,
            allowed_specification_templates,
            accumulated_specification_answers,
            previous_assessment,
        ):
            del diagnosis, classification, previous_assessment
            assert description.text == description_text
            assert method_profile_id == "first_order_lag"
            assert accumulated_specification_answers == [description_text]
            template = allowed_specification_templates[0]
            return {
                "status": "need_more",
                "template_id": template.template_id,
                "facts": [
                    _profile_fact("input_change", 1.0, "deg", input_excerpt),
                    _profile_fact("steady_output_change", 10.0, "mph", output_excerpt),
                ],
                "missing_fact_ids": [
                    "response_time_s",
                    "input_min",
                    "input_max",
                    "output_min",
                    "output_max",
                ],
                "conflicts": [],
                "rejected_facts": [],
                "questions": [],
                "rationale": "Two explicit description facts were grounded.",
            }

    report = run_cfdc_route(
        "generic",
        description=SystemDescription(text=description_text),
        diagnostic_adapter=DescriptionPrefillAdapter(),
    )

    assessment = report.specification_assessment
    assert report.status == "awaiting_profile_measurements"
    assert {fact.fact_id for fact in assessment.facts} == {
        "input_change",
        "steady_output_change",
    }
    assert "input_change" not in assessment.missing_fact_ids
    assert "steady_output_change" not in assessment.missing_fact_ids
    assert report.diagnostic_session.profile_measurement_round_count == 0
    assert report.diagnostic_session.specification_answer_history == []


def test_optional_description_parameter_prefill_timeout_falls_back_to_questions():
    description_text = (
        f"{AUTOMOTIVE_DESCRIPTION}已有记录写明油门角变化 1 deg，"
        "但其余对象参数尚未整理。"
    )

    class TimeoutPrefillAdapter(DescriptionGroundedAdapter):
        def assess_specifications(self, *args):
            del args
            raise TimeoutError("provider timed out during optional parameter prefill")

    report = run_cfdc_route(
        "generic",
        description=SystemDescription(text=description_text),
        diagnostic_adapter=TimeoutPrefillAdapter(),
    )

    assert report.status == "awaiting_profile_measurements"
    assert report.classification is not None
    assert report.semantic_selection is not None
    assert report.specification_assessment.status == "need_more"
    assert report.specification_assessment.facts == []


def test_description_parameter_prefill_rejects_unattested_value_and_unit():
    unrelated_excerpt = "Temperature is recorded"
    description_text = (
        f"{AUTOMOTIVE_DESCRIPTION}{unrelated_excerpt}; an unrelated note says 1 deg."
    )

    class HallucinatedPrefillAdapter(DescriptionGroundedAdapter):
        def assess_specifications(
            self,
            description,
            diagnosis,
            classification,
            method_profile_id,
            allowed_specification_templates,
            accumulated_specification_answers,
            previous_assessment,
        ):
            del (
                description,
                diagnosis,
                classification,
                method_profile_id,
                accumulated_specification_answers,
                previous_assessment,
            )
            template = allowed_specification_templates[0]
            return {
                "status": "need_more",
                "template_id": template.template_id,
                "facts": [
                    _profile_fact(
                        "input_change",
                        999.0,
                        "deg",
                        unrelated_excerpt,
                    )
                ],
                "missing_fact_ids": [
                    field.fact_id
                    for field in template.fields
                    if field.fact_id != "input_change"
                ],
                "conflicts": [],
                "rejected_facts": [],
                "questions": [],
                "rationale": "The provider invented a value.",
            }

    report = run_cfdc_route(
        "generic",
        description=SystemDescription(text=description_text),
        diagnostic_adapter=HallucinatedPrefillAdapter(),
    )

    assessment = report.specification_assessment
    assert report.status == "awaiting_profile_measurements"
    assert assessment.facts == []
    assert "input_change" in assessment.missing_fact_ids
    assert any("source number" in item for item in assessment.rejected_facts)


def test_profile_extractor_failure_cannot_mutate_description_grounded_session():
    class MutatingExtractionAdapter(DescriptionGroundedAdapter):
        def extract_measurements(
            self,
            description,
            measurement_plan,
            measurement_response,
            previous_assessment,
        ):
            del measurement_response
            description.text = "poisoned description"
            measurement_plan.requests.clear()
            previous_assessment.facts.clear()
            raise RuntimeError("provider failed after mutating its inputs")

    adapter = MutatingExtractionAdapter()
    initial = run_cfdc_route(
        "generic",
        description=SystemDescription(text=AUTOMOTIVE_DESCRIPTION),
        diagnostic_adapter=adapter,
    )
    session = initial.diagnostic_session
    snapshot = session.model_dump(mode="json")

    with pytest.raises(RuntimeError, match="provider failed"):
        run_cfdc_route(
            "generic",
            diagnostic_session_state=session,
            diagnostic_adapter=adapter,
            measurement_response="暂时不知道这些 Profile 参数。",
        )

    assert session.model_dump(mode="json") == snapshot


def test_description_completion_on_the_final_allowed_turn_is_not_refused():
    adapter = DescriptionGroundedAdapter()
    session = start_diagnostic_session(
        SystemDescription(text="这是一个需要补充记录的控制对象。"),
        diagnostic_adapter=adapter,
    ).model_copy(update={"maximum_turns": 1})

    completed = continue_description_session(
        session,
        "\n".join(_EXCERPTS.values()),
        expected_revision=session.revision,
        diagnostic_adapter=adapter,
    )

    assert completed.status == "description_grounded"
    assert completed.description_turn_count == 1
    assert completed.description_assessment is not None
    assert completed.refusal_reason is None


def test_profile_diagnostic_retraction_after_final_description_turn_is_refused():
    unknown_response = (
        "The current record does not establish the initial response direction; "
        "minimum phase is unknown."
    )

    class RetractionAdapter(DescriptionGroundedAdapter):
        def extract_measurements(
            self,
            description,
            measurement_plan,
            measurement_response,
            previous_assessment,
        ):
            del description, measurement_plan
            assert measurement_response == unknown_response
            return {
                "status": "need_more",
                "facts": [
                    fact.model_dump(mode="json")
                    for fact in previous_assessment.facts
                    if fact.request_id != "minimum_phase"
                ],
                "gaps": ["minimum_phase"],
                "conflicts": [],
                "conflict_request_ids": [],
                "rationale": "The user explicitly retracted phase evidence.",
            }

    adapter = RetractionAdapter()
    session = start_diagnostic_session(
        SystemDescription(text="这是一个需要补充记录的控制对象。"),
        diagnostic_adapter=adapter,
    ).model_copy(update={"maximum_turns": 1})
    completed = continue_description_session(
        session,
        "\n".join(_EXCERPTS.values()),
        expected_revision=session.revision,
        diagnostic_adapter=adapter,
    )
    released = run_cfdc_route(
        "generic",
        diagnostic_session_state=completed,
        diagnostic_adapter=adapter,
    )

    refused = run_cfdc_route(
        "generic",
        diagnostic_session_state=released.diagnostic_session,
        diagnostic_adapter=adapter,
        measurement_response=unknown_response,
    )

    assert refused.status == "rejected"
    assert refused.diagnostic_session.status == "refused"
    assert (
        refused.diagnostic_session.refusal_reason == "maximum_description_turns_reached"
    )


def test_one_generic_excerpt_cannot_satisfy_all_eight_description_fields():
    generic_excerpt = (
        "Temperature is recorded, and all relevant motion can be reconstructed "
        "from these synchronized records."
    )
    description = SystemDescription(text=generic_excerpt)
    adapter = DescriptionGroundedAdapter(
        {field_id: generic_excerpt for field_id in _EXCERPTS}
    )

    report = run_cfdc_route(
        "generic",
        description=description,
        diagnostic_adapter=adapter,
    )

    session = report.diagnostic_session
    assert report.status == "need_more_information"
    assert report.classification is None
    assert report.semantic_selection is None
    assert session.status == "collecting_description"
    assert session.description_assessment is None
    assert session.evidence_level == "description_only"
    by_id = {item.diagnostic_field_id: item for item in session.checklist}
    assert by_id["controllability_observability"].status == "inferred"
    assert by_id["controllability_observability"].evidence == [generic_excerpt]
    for field_id in set(_EXCERPTS) - {"controllability_observability"}:
        assert by_id[field_id].status == "unknown"
        assert by_id[field_id].evidence == []


def test_negated_canonical_phrases_do_not_complete_the_description_checklist():
    description_text = (
        "This note explicitly states that none of the following facts is known or "
        "supported by any record: "
        + "; ".join(excerpt for excerpt in _EXCERPTS.values())
    )

    report = run_cfdc_route(
        "generic",
        description=SystemDescription(text=description_text),
        diagnostic_adapter=DescriptionGroundedAdapter(),
    )

    assert report.status == "need_more_information"
    assert report.classification is None
    assert report.diagnostic_session.description_assessment is None
    assert {item.status for item in report.diagnostic_session.checklist} == {"unknown"}


def test_explicitly_unknown_field_sentences_keep_all_checklist_items_open():
    responses = {
        "open_loop_stability": (
            "After input returns to baseline, whether output settles is unknown."
        ),
        "minimum_phase": "The initial response direction is unknown.",
        "significant_delay": "The input delay is unknown.",
        "relative_degree": "The number of integration stages is unknown.",
        "controllability_observability": (
            "Whether synchronized sensor records can reconstruct the state is unknown."
        ),
        "nonlinearity_strength": (
            "Whether positive and negative trials are proportional is unknown."
        ),
        "coupling_severity": "Whether one input affects one output is unknown.",
        "uncertainty_magnitude": "How load changes the response is unknown.",
    }
    description_text = " ".join(responses.values())

    report = run_cfdc_route(
        "generic",
        description=SystemDescription(text=description_text),
        diagnostic_adapter=DescriptionGroundedAdapter(responses),
    )

    assert report.status == "need_more_information"
    assert report.diagnostic_session.description_assessment is None
    assert {item.status for item in report.diagnostic_session.checklist} == {"unknown"}


def test_persisted_description_assessment_rejects_field_mismatched_excerpts():
    report = run_cfdc_route(
        "generic",
        description=SystemDescription(text=AUTOMOTIVE_DESCRIPTION),
        diagnostic_adapter=DescriptionGroundedAdapter(),
    )
    payload = report.diagnostic_session.model_dump(mode="json")
    generic_excerpt = _EXCERPTS["controllability_observability"]
    for fact in payload["description_assessment"]["facts"]:
        if fact["request_id"] == "open_loop_stability":
            fact["source_excerpt"] = generic_excerpt
            fact["text_value"] = generic_excerpt
            break

    with pytest.raises(ValueError, match="does not answer diagnostic field"):
        migrate_diagnostic_session_payload(payload)


def test_valid_field_specific_stability_paraphrase_is_accepted():
    stability_excerpt = "油门角度恢复到基准值 0 deg 后，车速偏差逐渐减小并最终保持有界"
    responses = dict(_EXCERPTS)
    responses["open_loop_stability"] = stability_excerpt

    report = run_cfdc_route(
        "generic",
        description=SystemDescription(
            text=f"{AUTOMOTIVE_DESCRIPTION}{stability_excerpt}。"
        ),
        diagnostic_adapter=DescriptionGroundedAdapter(responses),
    )

    assert report.status == "awaiting_profile_measurements"
    assert report.diagnostic_session.description_assessment is not None


def test_description_parameter_prefill_supports_a_chinese_time_unit():
    time_excerpt = "已有记录说明响应时间为 5 秒"
    description_text = f"{AUTOMOTIVE_DESCRIPTION}{time_excerpt}。"

    class ChineseUnitPrefillAdapter(DescriptionGroundedAdapter):
        def assess_specifications(
            self,
            description,
            diagnosis,
            classification,
            method_profile_id,
            allowed_specification_templates,
            accumulated_specification_answers,
            previous_assessment,
        ):
            del (
                description,
                diagnosis,
                classification,
                method_profile_id,
                accumulated_specification_answers,
                previous_assessment,
            )
            template = allowed_specification_templates[0]
            return {
                "status": "need_more",
                "template_id": template.template_id,
                "facts": [_profile_fact("response_time_s", 5.0, "s", time_excerpt)],
                "missing_fact_ids": [
                    field.fact_id
                    for field in template.fields
                    if field.fact_id != "response_time_s"
                ],
                "conflicts": [],
                "rejected_facts": [],
                "questions": [],
                "rationale": "The Chinese time value is explicit.",
            }

    report = run_cfdc_route(
        "generic",
        description=SystemDescription(text=description_text),
        diagnostic_adapter=ChineseUnitPrefillAdapter(),
    )

    fact = next(
        item
        for item in report.specification_assessment.facts
        if item.fact_id == "response_time_s"
    )
    assert fact.value == pytest.approx(5.0)
    assert fact.unit == "s"


@pytest.mark.parametrize(
    ("field_id", "excerpt", "forbidden_assessment"),
    [
        (
            "open_loop_stability",
            "恢复输入后，车速最终不会收敛或保持有界",
            "stable",
        ),
        (
            "minimum_phase",
            "车速不会开始时就沿最终方向变化",
            "minimum_phase",
        ),
        (
            "significant_delay",
            "输入改变后，车速不会在一个采样周期内开始变化",
            "not_significant",
        ),
        (
            "controllability_observability",
            "这些同步记录不足以重建所有相关运动",
            "adequate",
        ),
        (
            "nonlinearity_strength",
            "Positive and negative responses differ unpredictably.",
            "weak",
        ),
        (
            "uncertainty_magnitude",
            "Load changes the response unpredictably.",
            "small",
        ),
    ],
)
def test_field_grounding_never_turns_negative_or_ambiguous_evidence_positive(
    field_id, excerpt, forbidden_assessment
):
    assert infer_description_field_assessment(field_id, excerpt) != forbidden_assessment


def test_explicit_dead_time_is_significant_but_ambiguous_delay_remains_open():
    assert (
        infer_description_field_assessment(
            "significant_delay",
            "A 3 s dead time precedes the output response.",
        )
        == "significant"
    )
    assert (
        infer_description_field_assessment(
            "significant_delay",
            "The input delay is 3 s.",
        )
        is None
    )


@pytest.mark.parametrize(
    ("field_id", "excerpt"),
    [
        ("open_loop_stability", "恢复原输入后，输出是否稳定尚未知"),
        ("significant_delay", "输入时延未知"),
        (
            "controllability_observability",
            "这些同步记录能否重建运动尚不清楚",
        ),
    ],
)
def test_chinese_unknown_claims_leave_their_checklist_fields_open(field_id, excerpt):
    assert not description_excerpt_answers_field(
        field_id,
        excerpt,
        context=excerpt,
    )


def test_unrelated_unknown_clause_does_not_taint_a_grounded_stability_excerpt():
    excerpt = "把油门恢复到基准值后，车速逐渐减小并最终保持有界"
    context = f"输入时延未知，但{excerpt}。"

    assert description_excerpt_answers_field(
        "open_loop_stability",
        excerpt,
        context=context,
    )


def test_description_parameter_prefill_rejects_a_number_from_the_wrong_signal():
    wrong_role_excerpt = "temperature is 10 degC"
    description_text = f"{AUTOMOTIVE_DESCRIPTION}{wrong_role_excerpt}."

    class WrongRolePrefillAdapter(DescriptionGroundedAdapter):
        def assess_specifications(self, *args):
            template = args[4][0]
            return {
                "status": "need_more",
                "template_id": template.template_id,
                "facts": [
                    _profile_fact("input_change", 10.0, "degC", wrong_role_excerpt)
                ],
                "missing_fact_ids": [
                    field.fact_id
                    for field in template.fields
                    if field.fact_id != "input_change"
                ],
                "conflicts": [],
                "rejected_facts": [],
                "questions": [],
                "rationale": "The provider relabeled an output value.",
            }

    report = run_cfdc_route(
        "generic",
        description=SystemDescription(text=description_text),
        diagnostic_adapter=WrongRolePrefillAdapter(),
    )

    assert report.specification_assessment.facts == []
    assert "input_change" in report.specification_assessment.missing_fact_ids
    assert any(
        "signal role" in item for item in report.specification_assessment.rejected_facts
    )


def test_description_parameter_prefill_rejects_a_negated_numeric_claim():
    negated_excerpt = "input change is not 1 V"
    description_text = f"{AUTOMOTIVE_DESCRIPTION}{negated_excerpt}."

    class NegatedFactAdapter(DescriptionGroundedAdapter):
        def assess_specifications(self, *args):
            template = args[4][0]
            return {
                "status": "need_more",
                "template_id": template.template_id,
                "facts": [_profile_fact("input_change", 1.0, "V", negated_excerpt)],
                "missing_fact_ids": [
                    field.fact_id
                    for field in template.fields
                    if field.fact_id != "input_change"
                ],
                "conflicts": [],
                "rejected_facts": [],
                "questions": [],
                "rationale": "The provider ignored negation.",
            }

    report = run_cfdc_route(
        "generic",
        description=SystemDescription(text=description_text),
        diagnostic_adapter=NegatedFactAdapter(),
    )

    assert report.specification_assessment.facts == []
    assert "input_change" in report.specification_assessment.missing_fact_ids
    assert any(
        "negates" in item for item in report.specification_assessment.rejected_facts
    )


def test_fully_prefilled_profile_uses_a_confirmation_only_action():
    description_text = f"{AUTOMOTIVE_DESCRIPTION}{_PROFILE_RESPONSE}"

    class FullyPrefilledAdapter(DescriptionGroundedAdapter):
        def assess_specifications(self, *args):
            template = args[4][0]
            return {
                "status": "ready",
                "template_id": template.template_id,
                "facts": _PROFILE_FACTS,
                "missing_fact_ids": [],
                "conflicts": [],
                "questions": [],
                "rationale": "Every Profile parameter is verbatim in the description.",
            }

        def extract_measurements(self, *args):
            del args
            raise AssertionError(
                "confirmation-only continuation must not re-run diagnostic extraction"
            )

    adapter = FullyPrefilledAdapter()
    initial = run_cfdc_route(
        "generic",
        description=SystemDescription(text=description_text),
        diagnostic_adapter=adapter,
    )

    outputs = web_ui._outputs(initial, {})
    assert initial.specification_assessment.status == "ready"
    assert outputs[17]["visible"] is False
    assert outputs[18]["visible"] is True
    assert outputs[19]["visible"] is True

    completed = run_cfdc_route(
        "generic",
        diagnostic_session_state=initial.diagnostic_session,
        diagnostic_adapter=adapter,
        measurement_response="",
        simulation_bounds_confirmed=True,
    )

    assert completed.status == "candidate_unvalidated"
    assert completed.diagnostic_session.profile_measurement_round_count == 0
    assert completed.diagnostic_session.specification_answer_history == []


def test_description_grounded_profile_cap_remains_terminal_after_migration():
    report = run_cfdc_route(
        "generic",
        description=SystemDescription(text=AUTOMOTIVE_DESCRIPTION),
        diagnostic_adapter=DescriptionGroundedAdapter(),
    )
    payload = report.diagnostic_session.model_dump(mode="json")
    payload.update(
        {
            "status": "refused",
            "profile_measurement_round_count": 8,
            "refusal_reason": "maximum_profile_measurement_rounds_reached",
        }
    )

    restored = migrate_diagnostic_session_payload(payload)

    assert restored.status == "refused"
    assert restored.profile_measurement_round_count == 8
    assert restored.refusal_reason == "maximum_profile_measurement_rounds_reached"


def test_migration_does_not_trust_a_persisted_simulation_confirmation():
    report = run_cfdc_route(
        "generic",
        description=SystemDescription(text=AUTOMOTIVE_DESCRIPTION),
        diagnostic_adapter=DescriptionGroundedAdapter(),
    )
    payload = report.diagnostic_session.model_dump(mode="json")
    confirmation = {
        "confirmed": True,
        "scope": "software_simulation_only",
        "statement_version": "v1",
    }
    payload["initial_description"]["simulation_boundary_confirmation"] = confirmation
    payload["accumulated_description"]["simulation_boundary_confirmation"] = (
        confirmation
    )

    restored = migrate_diagnostic_session_payload(payload)

    assert restored.initial_description.simulation_boundary_confirmation is None
    assert restored.accumulated_description.simulation_boundary_confirmation is None


def test_session_owns_the_caller_description_and_adapter_inputs():
    description = SystemDescription(text="original description")
    session = start_diagnostic_session(description)
    description.text = "caller mutation"

    assert session.initial_description.text == "original description"
    assert session.accumulated_description.text == "original description"

    class MutatingGuideAdapter(DescriptionGroundedAdapter):
        def guide_description(self, description, guidance):
            description.text = "adapter mutation"
            guidance[0].prompt = "Apply a command to physical hardware."
            raise RuntimeError("provider mutated then failed")

    guided_description = SystemDescription(text="still original")
    with pytest.raises((RuntimeError, ValueError)):
        start_diagnostic_session(
            guided_description,
            diagnostic_adapter=MutatingGuideAdapter(),
        )
    assert guided_description.text == "still original"


def test_incomplete_web_start_uses_one_description_guidance_call(monkeypatch):
    class CountingAdapter(DescriptionGroundedAdapter):
        def __init__(self):
            super().__init__({field_id: "unknown" for field_id in _EXCERPTS})
            self.guide_calls = 0

        def guide_description(self, description, guidance):
            self.guide_calls += 1
            return super().guide_description(description, guidance)

    adapter = CountingAdapter()
    monkeypatch.setattr(web_service, "build_adapter", lambda *args: adapter)

    report, state = web_service.start_app_run(
        "这是一个住宅供暖系统。",
        "",
        "",
        "",
        "generic",
        True,
        "https://provider.example/v1",
        "provider-model",
        "test-secret",
    )

    assert report.status == "need_more_information"
    assert adapter.guide_calls == 1
    assert state["session"]["session_id"] == report.diagnostic_session.session_id


def test_profile_selection_cannot_add_dead_time_to_a_no_delay_diagnosis():
    class DelayProfileAdapter(DescriptionGroundedAdapter):
        def select_profile(self, description, diagnosis, classification, catalog):
            selection = super().select_profile(
                description, diagnosis, classification, catalog
            )
            selection.update(
                {
                    "simulation_profile_id": "first_order_lag_with_delay",
                    "feature_bundle_id": "class_i_delay_minimal",
                    "selected_feature_ids": [
                        "static_gain",
                        "time_constant",
                        "dead_time",
                    ],
                }
            )
            return selection

    with pytest.raises(ValueError, match="contradicts the grounded"):
        run_cfdc_route(
            "generic",
            description=SystemDescription(text=AUTOMOTIVE_DESCRIPTION),
            diagnostic_adapter=DelayProfileAdapter(),
        )
