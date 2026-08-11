from __future__ import annotations

import json
from typing import ClassVar

import pytest

import cfdc.web.service as web_service
from cfdc.diagnosis import (
    build_diagnostic_checklist,
    build_measurement_plan,
    migrate_diagnostic_session_payload,
    start_diagnostic_session,
)
from cfdc.diagnosis.engine import infer_structural_diagnosis
from cfdc.diagnosis.llm import OpenAICompatibleDiagnosticAdapter
from cfdc.models import MeasuredFact, MeasurementAssessment, SystemDescription
from cfdc.runtime import run_cfdc_route
from cfdc.web.service import start_app_run, submit_app_measurement_response
from cfdc.workflow import deterministic_profile_selection

_VALID_FIELD_FACTS = {
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
    "coupling_severity": "one main physical route from actuation to the measured motion",
    "uncertainty_magnitude": (
        "change the response rate and final level by a modest amount"
    ),
}


class GuidedFakeAdapter:
    """Complete fake for the structured operations used by the guided flow."""

    def diagnose(self, description):
        return infer_structural_diagnosis(description).model_dump(mode="json")

    def guide_description(self, description, guidance):
        return {
            "guidance": [
                {
                    **item.model_dump(mode="json"),
                    "response": (
                        _VALID_FIELD_FACTS[item.diagnostic_field_id]
                        if _VALID_FIELD_FACTS[item.diagnostic_field_id]
                        in description.text
                        else "unknown"
                    ),
                }
                for item in guidance
            ],
            "observed_outputs": [
                {"name": "temperature", "source_excerpt": "temperature"}
            ],
            "actuators": [{"name": "heater", "source_excerpt": "heater change"}],
        }

    def phrase_measurement_plan(self, description, checklist, plan):
        del description, checklist
        return plan.model_dump(mode="json")

    def extract_measurements(
        self, description, measurement_plan, measurement_response, previous_assessment
    ):
        del description
        if measurement_response == "need another record":
            return MeasurementAssessment(
                status="need_more",
                gaps=[
                    request.diagnostic_field_id for request in measurement_plan.requests
                ],
                rationale="The supplied response did not identify an existing record.",
            ).model_dump(mode="json")
        if previous_assessment is not None and previous_assessment.status == "ready":
            return previous_assessment.model_dump(mode="json")
        return MeasurementAssessment(
            status="ready",
            facts=[
                MeasuredFact(
                    request_id=request.request_id,
                    source_excerpt=_VALID_FIELD_FACTS[request.request_id],
                    text_value=_VALID_FIELD_FACTS[request.request_id],
                )
                for request in measurement_plan.requests
            ],
            rationale="All eight record findings were supplied and verified.",
        ).model_dump(mode="json")

    def select_profile(self, description, diagnosis, classification, catalog):
        return deterministic_profile_selection(
            description, diagnosis, classification, catalog
        ).model_dump(mode="json")


class EvidenceDrivenAdapter(GuidedFakeAdapter):
    """Fake whose deterministic diagnosis depends on persisted extracted facts."""

    _facts: ClassVar[dict[str, str]] = _VALID_FIELD_FACTS

    def diagnose(self, description):
        raise AssertionError("guided formal diagnosis must never call the adapter")

    def extract_measurements(
        self,
        description,
        measurement_plan,
        measurement_response,
        previous_assessment,
    ):
        del description
        if "changing any one of several actuators" in measurement_response:
            assert previous_assessment.status == "ready"
            severe = "changing any one of several actuators noticeably changes several outputs"
            return MeasurementAssessment(
                status="ready",
                facts=[
                    (
                        MeasuredFact(
                            request_id="coupling_severity",
                            source_excerpt=severe,
                            text_value=severe,
                        )
                        if fact.request_id == "coupling_severity"
                        else fact
                    )
                    for fact in previous_assessment.facts
                ],
                rationale="New validated coupling evidence.",
            ).model_dump(mode="json")
        return MeasurementAssessment(
            status="ready",
            facts=[
                MeasuredFact(
                    request_id=request.request_id,
                    source_excerpt=self._facts[request.request_id],
                    text_value=self._facts[request.request_id],
                )
                for request in measurement_plan.requests
            ],
            rationale="All eight diagnostic facts are verified.",
        ).model_dump(mode="json")


def _description() -> SystemDescription:
    return SystemDescription(
        text=(
            "A first order temperature process settles after a heater change. "
            + " ".join(_VALID_FIELD_FACTS.values())
        ),
        observed_outputs=["temperature"],
        actuators=["heater power"],
    )


def _complete_diagnostic_response() -> str:
    return "\n".join(
        f"{request_id}: {source_excerpt}"
        for request_id, source_excerpt in _VALID_FIELD_FACTS.items()
    )


def _migrated_measurement_verified_session():
    adapter = GuidedFakeAdapter()
    routed = run_cfdc_route(
        "generic",
        diagnostic_session_state=start_diagnostic_session(
            _description(), route_id="generic"
        ),
        diagnostic_adapter=adapter,
        measurement_response=_complete_diagnostic_response(),
    )
    return migrate_diagnostic_session_payload(
        routed.diagnostic_session.model_dump(mode="json")
    )


def test_generic_route_releases_grounded_description_without_measurement_round():
    adapter = GuidedFakeAdapter()

    initial = run_cfdc_route(
        "generic", description=_description(), diagnostic_adapter=adapter
    )

    assert initial.status == "awaiting_profile_measurements"
    assert initial.classification is not None
    assert initial.semantic_selection is not None
    assert initial.diagnostic_session is not None
    assert initial.diagnostic_session.schema_version == "4.0"
    assert initial.diagnostic_session.evidence_level == "description_grounded"
    assert initial.diagnostic_session.description_assessment is not None
    assert initial.diagnostic_session.measurement_round_count == 0
    assert initial.diagnostic_session.measurement_history == []
    assert initial.specification_assessment.questions


def test_route_rejects_ungrounded_ready_adapter_output_without_releasing_session():
    class UngroundedAdapter(GuidedFakeAdapter):
        def extract_measurements(
            self,
            description,
            measurement_plan,
            measurement_response,
            previous_assessment,
        ):
            del description, measurement_response, previous_assessment
            return MeasurementAssessment(
                status="ready",
                facts=[
                    MeasuredFact(
                        request_id=request.request_id,
                        source_excerpt=f"invented excerpt for {request.request_id}",
                        text_value=_VALID_FIELD_FACTS[request.request_id],
                    )
                    for request in measurement_plan.requests
                ],
                rationale="The adapter claims every field is ready.",
            ).model_dump(mode="json")

    adapter = UngroundedAdapter()
    initial = start_diagnostic_session(_description(), route_id="generic")

    with pytest.raises(ValueError, match="not grounded"):
        run_cfdc_route(
            "generic",
            diagnostic_session_state=initial,
            diagnostic_adapter=adapter,
            measurement_response="The user supplied no field-specific excerpts.",
        )

    assert initial.classification is None
    assert initial.semantic_selection is None
    assert initial.measurement_history == []
    assert initial.measurement_response_history == []


def test_formal_diagnosis_ignores_poisoned_adapter_diagnosis():
    class PoisonedDiagnosisAdapter(GuidedFakeAdapter):
        def diagnose(self, description):
            payload = super().diagnose(description)
            payload["open_loop_stability"] = {
                "status": "known",
                "value": "poisoned adapter claim",
                "assessment": "unstable",
                "confidence": 1.0,
                "evidence": ["not validated measurement evidence"],
            }
            payload["coupling_severity"] = {
                "status": "known",
                "value": "poisoned adapter claim",
                "assessment": "severe_mimo",
                "confidence": 1.0,
                "evidence": ["not validated measurement evidence"],
            }
            return payload

    adapter = PoisonedDiagnosisAdapter()
    initial = run_cfdc_route(
        "generic", description=_description(), diagnostic_adapter=adapter
    )
    released = run_cfdc_route(
        "generic",
        diagnostic_session_state=initial.diagnostic_session,
        diagnostic_adapter=adapter,
        measurement_response=_complete_diagnostic_response(),
    )

    assert released.diagnosis.open_loop_stability.assessment == "stable"
    assert released.diagnosis.coupling_severity.assessment == "siso"
    assert released.classification.primary_class == "class_i_first_order_lag"


def test_verified_measurement_facts_persist_across_session_serialization():
    adapter = GuidedFakeAdapter()
    released = run_cfdc_route(
        "generic",
        diagnostic_session_state=start_diagnostic_session(
            _description(), route_id="generic"
        ),
        diagnostic_adapter=adapter,
        measurement_response=_complete_diagnostic_response(),
    )

    serialized = released.diagnostic_session.model_dump_json()
    restored = type(released.diagnostic_session).model_validate_json(serialized)
    assert "open_loop_stability" in restored.accumulated_description.text
    assert "settles or remains bounded" in restored.accumulated_description.text
    assert _complete_diagnostic_response() not in restored.accumulated_description.text


def test_persisted_measurement_facts_drive_later_deterministic_invalidation():
    adapter = EvidenceDrivenAdapter()
    vague_description = SystemDescription(
        text="temperature and heater change records are available.",
        observed_outputs=["temperature"],
        actuators=["heater"],
    )
    released = run_cfdc_route(
        "generic",
        diagnostic_session_state=start_diagnostic_session(
            vague_description, route_id="generic"
        ),
        diagnostic_adapter=adapter,
        measurement_response=_complete_diagnostic_response(),
    )
    restored = type(released.diagnostic_session).model_validate_json(
        released.diagnostic_session.model_dump_json()
    )

    invalidated = run_cfdc_route(
        "generic",
        diagnostic_session_state=restored,
        diagnostic_adapter=adapter,
        measurement_response=(
            "changing any one of several actuators noticeably changes several outputs"
        ),
    )

    assert invalidated.status == "need_more_information"
    assert invalidated.diagnosis.open_loop_stability.assessment == "stable"
    assert invalidated.diagnosis.coupling_severity.assessment == "severe_mimo"
    assert "settles or remains bounded" in (
        invalidated.diagnostic_session.accumulated_description.text
    )


def test_invalidation_does_not_request_a_replacement_measurement_plan():
    class InvalidationPlanMutator(EvidenceDrivenAdapter):
        phrase_calls = 0

        def phrase_measurement_plan(self, description, checklist, plan):
            del description, checklist
            self.phrase_calls += 1
            payload = plan.model_dump(mode="json")
            if self.phrase_calls == 2:
                payload["requests"] = list(reversed(payload["requests"]))
            return payload

    adapter = InvalidationPlanMutator()
    legacy_session = start_diagnostic_session(
        SystemDescription(
            text="temperature and heater change records are available.",
            observed_outputs=["temperature"],
            actuators=["heater"],
        ),
        route_id="generic",
    )
    released = run_cfdc_route(
        "generic",
        diagnostic_session_state=legacy_session,
        diagnostic_adapter=adapter,
        measurement_response=_complete_diagnostic_response(),
    )

    invalidated = run_cfdc_route(
        "generic",
        diagnostic_session_state=released.diagnostic_session,
        diagnostic_adapter=adapter,
        measurement_response=(
            "changing any one of several actuators noticeably changes several outputs"
        ),
    )

    assert invalidated.status == "need_more_information"
    assert adapter.phrase_calls == 0


@pytest.mark.parametrize(
    "mutation",
    ["omit", "reorder", "request_id", "rationale", "unsafe_instruction"],
)
def test_llm_phrasing_cannot_replace_the_authoritative_measurement_plan(mutation):
    class MutatingPlanAdapter(GuidedFakeAdapter):
        def phrase_measurement_plan(self, description, checklist, plan):
            payload = super().phrase_measurement_plan(description, checklist, plan)
            if mutation == "omit":
                payload["requests"] = payload["requests"][:-1]
            elif mutation == "reorder":
                payload["requests"][0], payload["requests"][1] = (
                    payload["requests"][1],
                    payload["requests"][0],
                )
            elif mutation == "request_id":
                payload["requests"][0]["request_id"] = "mutated"
            elif mutation == "rationale":
                payload["rationale"] = "Perform a new hardware experiment."
            else:
                payload["requests"][0]["instruction"] = "Apply 10 V to the heater."
            return payload

    with pytest.raises(ValueError):
        run_cfdc_route(
            "generic",
            description=_description(),
            diagnostic_adapter=MutatingPlanAdapter(),
        )


def test_description_guidance_extracts_only_verbatim_signals():
    description = SystemDescription(
        text="The manual says room temperature is recorded and heater voltage is commanded."
    )

    class ExtractingAdapter(GuidedFakeAdapter):
        def guide_description(self, description, guidance):
            del description
            return {
                "guidance": [item.model_dump(mode="json") for item in guidance],
                "observed_outputs": [
                    {
                        "name": "ROOM   TEMPERATURE",
                        "source_excerpt": "room temperature is recorded",
                    }
                ],
                "actuators": [
                    {
                        "name": "heater voltage",
                        "source_excerpt": "heater voltage is commanded",
                    }
                ],
            }

    report = run_cfdc_route(
        "generic", description=description, diagnostic_adapter=ExtractingAdapter()
    )

    accumulated = report.diagnostic_session.accumulated_description
    assert accumulated.observed_outputs == ["ROOM   TEMPERATURE"]
    assert accumulated.actuators == ["heater voltage"]
    assert len(report.diagnostic_session.description_guidance) == 8


@pytest.mark.parametrize(
    "mutation",
    [
        "extra",
        "order",
        "hardware_prompt",
        "hardware_why_needed",
    ],
)
def test_description_guidance_rejects_shape_order_and_provenance_mutations(mutation):
    class MutatingGuidanceAdapter(GuidedFakeAdapter):
        def guide_description(self, description, guidance):
            payload = super().guide_description(description, guidance)
            if mutation == "extra":
                payload["unexpected"] = True
            elif mutation == "order":
                payload["guidance"][0], payload["guidance"][1] = (
                    payload["guidance"][1],
                    payload["guidance"][0],
                )
            elif mutation == "hardware_prompt":
                payload["guidance"][0]["prompt"] = (
                    "Review an existing record and apply 10 V to the heater."
                )
            else:
                payload["guidance"][0]["why_needed"] = (
                    "Apply 10 V to the heater before recording the result."
                )
            return payload

    with pytest.raises(ValueError):
        run_cfdc_route(
            "generic",
            description=_description(),
            diagnostic_adapter=MutatingGuidanceAdapter(),
        )


@pytest.mark.parametrize("mutation", ["provenance", "invented_name"])
def test_description_guidance_ignores_ungrounded_signal_extraction(mutation):
    class UngroundedSignalAdapter(GuidedFakeAdapter):
        def guide_description(self, description, guidance):
            payload = super().guide_description(description, guidance)
            if mutation == "provenance":
                payload["observed_outputs"][0]["source_excerpt"] = (
                    "temperature appears only in a fictional source"
                )
            else:
                payload["observed_outputs"][0] = {
                    "name": "pressure",
                    "source_excerpt": "pressure appears only in a fictional source",
                }
            return payload

    report = run_cfdc_route(
        "generic",
        description=SystemDescription(text=_description().text),
        diagnostic_adapter=UngroundedSignalAdapter(),
    )

    assert "pressure" not in report.system_description.observed_outputs
    if mutation == "provenance":
        assert "temperature" not in report.system_description.observed_outputs


@pytest.mark.parametrize(
    "missing_capability",
    [
        "guide_description",
        "phrase_measurement_plan",
        "extract_measurements",
        "select_profile",
    ],
)
def test_guided_route_rejects_partial_adapter_capabilities(missing_capability):
    adapter = GuidedFakeAdapter()
    setattr(adapter, missing_capability, None)

    with pytest.raises(ValueError, match=missing_capability):
        run_cfdc_route(
            "generic",
            description=_description(),
            diagnostic_adapter=adapter,
        )


def test_web_guided_start_rejects_partial_adapter_capabilities(monkeypatch):
    class PartialAdapter:
        def guide_description(self, description, guidance):
            raise AssertionError("capability validation must run first")

    monkeypatch.setattr(web_service, "build_adapter", lambda *args: PartialAdapter())

    with pytest.raises(ValueError, match="phrase_measurement_plan"):
        start_app_run(
            "temperature settles after a heater change",
            "temperature",
            "heater",
            "",
            "generic",
            True,
            None,
            "fake",
            "secret",
        )


def test_same_measurement_response_input_advances_profile_facts_to_model():
    adapter = GuidedFakeAdapter()
    routed = run_cfdc_route(
        "generic", description=_description(), diagnostic_adapter=adapter
    )

    completed = run_cfdc_route(
        "generic",
        diagnostic_session_state=routed.diagnostic_session,
        diagnostic_adapter=adapter,
        measurement_response=(
            "Manual: input_change=1 normalized_input; "
            "steady_output_change=10 degC; response_time_s=20 s; "
            "input_min=-2 normalized_input; input_max=2 normalized_input; "
            "output_min=-30 degC; output_max=80 degC."
        ),
        simulation_bounds_confirmed=True,
    )

    assert completed.status == "candidate_unvalidated"
    assert completed.compiled_specification_model is not None
    assert completed.controller is not None
    assert completed.controller.release_level == "candidate_unvalidated"
    assert completed.diagnostic_session.measurement_round_count == 0
    assert completed.diagnostic_session.measurement_history == []
    assert completed.diagnostic_session.measurement_assessment is None
    assert completed.diagnostic_session.description_assessment is not None


def test_profile_only_response_keeps_ready_diagnosis_and_compiles_specifications():
    class ProfileCarryForwardAdapter(GuidedFakeAdapter):
        def extract_measurements(
            self,
            description,
            measurement_plan,
            measurement_response,
            previous_assessment,
        ):
            if measurement_response.startswith("Manual: input_change"):
                assert previous_assessment.status == "ready"
                return previous_assessment.model_dump(mode="json")
            return super().extract_measurements(
                description,
                measurement_plan,
                measurement_response,
                previous_assessment,
            )

    adapter = ProfileCarryForwardAdapter()
    initial = run_cfdc_route(
        "generic", description=_description(), diagnostic_adapter=adapter
    )
    routed = run_cfdc_route(
        "generic",
        diagnostic_session_state=initial.diagnostic_session,
        diagnostic_adapter=adapter,
        measurement_response=_complete_diagnostic_response(),
    )
    original_classification = routed.classification
    original_selection = routed.semantic_selection

    completed = run_cfdc_route(
        "generic",
        diagnostic_session_state=routed.diagnostic_session,
        diagnostic_adapter=adapter,
        measurement_response=(
            "Manual: input_change=1 normalized_input; "
            "steady_output_change=10 degC; response_time_s=20 s; "
            "input_min=-2 normalized_input; input_max=2 normalized_input; "
            "output_min=-30 degC; output_max=80 degC."
        ),
        simulation_bounds_confirmed=True,
    )

    assert completed.status == "candidate_unvalidated"
    assert completed.classification == original_classification
    assert completed.semantic_selection == original_selection
    assert completed.diagnostic_session.current_diagnosis.complete is True
    assert completed.compiled_specification_model is not None
    assert completed.controller is not None


def test_truncated_profile_llm_json_keeps_ui_flow_and_uses_grounded_local_facts(
    monkeypatch,
):
    description = _description()
    bootstrap_adapter = GuidedFakeAdapter()
    initial = run_cfdc_route(
        "generic", description=description, diagnostic_adapter=bootstrap_adapter
    )
    routed = run_cfdc_route(
        "generic",
        diagnostic_session_state=initial.diagnostic_session,
        diagnostic_adapter=bootstrap_adapter,
        measurement_response=_complete_diagnostic_response(),
    )

    class TruncatedCompletions:
        def create(self, **kwargs):
            del kwargs
            content = '{"status":"need_more","facts":[],"rationale":"截断'
            message = type("Message", (), {"content": content})()
            choice = type("Choice", (), {"message": message})()
            return type("Response", (), {"choices": [choice]})()

    class TruncatedOpenAI:
        def __init__(self, **kwargs):
            del kwargs
            self.chat = type("Chat", (), {"completions": TruncatedCompletions()})()

    monkeypatch.setattr("cfdc.diagnosis.llm.OpenAI", TruncatedOpenAI)
    live_adapter = OpenAICompatibleDiagnosticAdapter(
        base_url="https://provider.example/v1",
        model="provider-model",
        api_key="provider-secret",
    )
    measurement_response = (
        "在 65 mph 附近令油门角变化 1 deg，并采用每度油门对应 10 mph "
        "稳态车速变化；把 1% 上坡作为 -5 mph 扰动，为动态仿真补入 5 s "
        "响应时间，并比较开环与比例增益 10 的反馈。\n\n"
        "为便于未启用 LLM 时一次解析，可在同一次提交末尾附上："
        "`input_change=1 deg; steady_output_change=10 mph; "
        "response_time_s=5 s; input_min=-3 deg; input_max=3 deg; "
        "output_min=45 mph; output_max=80 mph;`"
    )

    completed = run_cfdc_route(
        "generic",
        diagnostic_session_state=routed.diagnostic_session,
        diagnostic_adapter=live_adapter,
        measurement_response=measurement_response,
        simulation_bounds_confirmed=True,
    )

    assert completed.status == "candidate_unvalidated"
    assert completed.compiled_specification_model is not None
    assert completed.controller is not None


def test_chinese_ready_record_advances_web_state_and_accepts_profile_facts(
    monkeypatch,
):
    diagnostic_facts = {
        "open_loop_stability": (
            "油门角度恢复到基准值 0 deg 后，车速偏差逐渐减小并最终保持有界，"
            "没有出现自行增长或持续振荡。"
        ),
        "minimum_phase": (
            "油门角度增加 1 deg 后，车速最初向增加方向变化；油门角度减少 1 deg 后，"
            "车速最初向降低方向变化，初始方向与最终方向一致，没有反向响应。"
        ),
        "significant_delay": (
            "油门角度在 10.0 s 改变，车速在 10.1 s 首次出现可辨识变化，记录到的"
            "响应开始时间为 0.1 s，没有独立的静默延迟区间。"
        ),
        "relative_degree": (
            "车速响应呈单调的一阶形状，主要响应时间约为 5 s，只观察到一个明显的"
            "快慢阶段，没有第二个独立动态阶段。"
        ),
        "controllability_observability": (
            "每次油门角度变化都会引起可记录的车速变化，油门角度和车速采用同一时钟"
            "连续记录，相关运动可以由这些同步记录重建。"
        ),
        "nonlinearity_strength": (
            "油门角度分别变化 +0.5 deg、-0.5 deg、+1 deg 和 -1 deg 时，稳态车速变化"
            "约为 +5 mph、-5 mph、+10 mph 和 -10 mph，正反方向近似对称且成比例，"
            "没有明显死区、滞回或幅值截断。"
        ),
        "coupling_severity": (
            "系统只有一个主要控制输入油门角度和一个被测输出车速，油门角度主要影响"
            "车速，其他量只作为外部扰动进入。"
        ),
        "uncertainty_magnitude": (
            "在不同软件负载条件下，稳态增益保持在 9 至 11 mph/deg，响应时间保持在 "
            "4.5 至 5.5 s，响应方向和单输入单输出通道结构没有改变。"
        ),
    }
    diagnostic_response = "\n".join(
        f"{request_id}：{excerpt}" for request_id, excerpt in diagnostic_facts.items()
    )

    class ChineseRecordAdapter(GuidedFakeAdapter):
        def guide_description(self, description, guidance):
            del description
            return {
                "guidance": [
                    {
                        **item.model_dump(mode="json"),
                        "response": diagnostic_facts[item.diagnostic_field_id],
                    }
                    for item in guidance
                ],
                "observed_outputs": [{"name": "车速", "source_excerpt": "车速"}],
                "actuators": [{"name": "油门角度", "source_excerpt": "油门角度"}],
            }

        def extract_measurements(
            self,
            description,
            measurement_plan,
            measurement_response,
            previous_assessment,
        ):
            del description
            if measurement_response == diagnostic_response:
                return MeasurementAssessment(
                    status="ready",
                    facts=[
                        MeasuredFact(
                            request_id=request.request_id,
                            source_excerpt=diagnostic_facts[request.request_id],
                            text_value=diagnostic_facts[request.request_id],
                        )
                        for request in measurement_plan.requests
                    ],
                    rationale="八项现有记录均已提取。",
                ).model_dump(mode="json")
            assert previous_assessment is not None
            assert previous_assessment.status == "ready"
            return previous_assessment.model_dump(mode="json")

    adapter = ChineseRecordAdapter()
    monkeypatch.setattr("cfdc.web.service.build_adapter", lambda *args: adapter)
    description = (
        "这是一个在道路上行驶的汽车纵向运动系统。控制输入是油门角度，输出是车速。"
        + "".join(diagnostic_facts.values())
    )
    report, state = start_app_run(
        description,
        "车速",
        "油门角度",
        "",
        None,
        True,
        "https://provider.example/v1",
        "provider-model",
        "provider-secret",
    )
    assert report.status == "awaiting_profile_measurements"
    assert report.diagnostic_session.status == "awaiting_profile_measurements"
    assert state["session"]["status"] == "awaiting_profile_measurements"

    completed, completed_state = submit_app_measurement_response(
        state,
        (
            "input_change=1 deg; steady_output_change=10 mph; "
            "response_time_s=5 s; input_min=-3 deg; input_max=3 deg; "
            "output_min=45 mph; output_max=80 mph;"
        ),
        base_url="https://provider.example/v1",
        model="provider-model",
        api_key="provider-secret",
        simulation_bounds_confirmed=True,
    )

    assert completed.status == "candidate_unvalidated"
    assert completed.compiled_specification_model is not None
    assert completed.controller is not None
    assert completed_state["session"] is None


def test_semantically_unresolved_ready_assessment_becomes_retryable_gaps():
    class UnresolvedRecordAdapter(GuidedFakeAdapter):
        def extract_measurements(
            self,
            description,
            measurement_plan,
            measurement_response,
            previous_assessment,
        ):
            del description, previous_assessment
            return MeasurementAssessment(
                status="ready",
                facts=[
                    MeasuredFact(
                        request_id=request.request_id,
                        source_excerpt=(
                            f"opaque record statement for {request.request_id}"
                        ),
                        text_value=(
                            f"opaque record statement for {request.request_id}"
                        ),
                    )
                    for request in measurement_plan.requests
                ],
                rationale="The adapter claimed every field was covered.",
            ).model_dump(mode="json")

    adapter = UnresolvedRecordAdapter()
    initial = start_diagnostic_session(_description(), route_id="generic")
    response = "\n".join(
        f"opaque record statement for {request.request_id}"
        for request in initial.measurement_plan.requests
    )

    retryable = run_cfdc_route(
        "generic",
        diagnostic_session_state=initial,
        diagnostic_adapter=adapter,
        measurement_response=response,
    )

    assert retryable.status == "measurement_needs_more"
    assert retryable.diagnostic_session.status == "measurement_needs_more"
    assert retryable.diagnostic_session.measurement_assessment.status == "need_more"
    assert retryable.diagnostic_session.measurement_assessment.facts == []
    assert retryable.diagnostic_session.measurement_assessment.gaps == [
        "open_loop_stability",
        "minimum_phase",
        "significant_delay",
        "relative_degree",
        "controllability_observability",
        "nonlinearity_strength",
        "coupling_severity",
        "uncertainty_magnitude",
    ]
    assert all(
        assessment.status != "ready"
        for assessment in retryable.diagnostic_session.measurement_history
    )


def test_explicit_profile_unknown_gap_retracts_prior_fact_and_invalidates_release():
    unknown_response = (
        "The current record does not establish the initial response direction; "
        "minimum phase is unknown."
    )

    class ExplicitUnknownAdapter(GuidedFakeAdapter):
        def extract_measurements(
            self,
            description,
            measurement_plan,
            measurement_response,
            previous_assessment,
        ):
            if measurement_response == unknown_response:
                assert previous_assessment.status == "ready"
                return MeasurementAssessment(
                    status="need_more",
                    facts=[
                        fact
                        for fact in previous_assessment.facts
                        if fact.request_id != "minimum_phase"
                    ],
                    gaps=["minimum_phase"],
                    rationale=(
                        "The latest response explicitly retracts the prior phase fact."
                    ),
                ).model_dump(mode="json")
            return super().extract_measurements(
                description,
                measurement_plan,
                measurement_response,
                previous_assessment,
            )

    adapter = ExplicitUnknownAdapter()
    initial = run_cfdc_route(
        "generic", description=_description(), diagnostic_adapter=adapter
    )
    invalidated = run_cfdc_route(
        "generic",
        diagnostic_session_state=initial.diagnostic_session,
        diagnostic_adapter=adapter,
        measurement_response=unknown_response,
    )

    assert invalidated.status == "need_more_information"
    assert invalidated.diagnostic_session.status == "collecting_description"
    assert invalidated.diagnosis.minimum_phase.assessment == "unknown"
    assert invalidated.classification is None
    assert invalidated.semantic_selection is None
    assert invalidated.experiment_plan is None
    assert invalidated.evidence_requirement_plan is None
    assert invalidated.specification_templates == []
    assert invalidated.specification_assessment is None
    assert invalidated.compiled_specification_model is None
    assert invalidated.diagnostic_session.candidate_route is None
    assert invalidated.diagnostic_session.compiled_route is None
    assert invalidated.controller is None
    checklist = {
        item.diagnostic_field_id: item
        for item in invalidated.diagnostic_session.checklist
    }
    assert checklist["minimum_phase"].status == "unknown"
    assert checklist["minimum_phase"].evidence == []
    assert sum(item.status != "unknown" for item in checklist.values()) == 7
    assert invalidated.diagnostic_session.description_assessment is None
    assert invalidated.diagnostic_session.measurement_assessment is None
    assert invalidated.diagnostic_session.measurement_history == []


def test_profile_gap_without_an_explicit_user_retraction_keeps_prior_diagnosis():
    response = (
        "I do not know the output limit. The previously established stability result "
        "remains unchanged. Profile parameter response: input_change=1 W."
    )

    class HallucinatedGapAdapter(GuidedFakeAdapter):
        def extract_measurements(
            self,
            description,
            measurement_plan,
            measurement_response,
            previous_assessment,
        ):
            if measurement_response == response:
                assert previous_assessment.status == "ready"
                return MeasurementAssessment(
                    status="need_more",
                    facts=[
                        fact
                        for fact in previous_assessment.facts
                        if fact.request_id != "open_loop_stability"
                    ],
                    gaps=["open_loop_stability"],
                    rationale="The provider hallucinated a diagnostic gap.",
                ).model_dump(mode="json")
            return super().extract_measurements(
                description,
                measurement_plan,
                measurement_response,
                previous_assessment,
            )

    adapter = HallucinatedGapAdapter()
    initial = run_cfdc_route(
        "generic", description=_description(), diagnostic_adapter=adapter
    )
    original_diagnosis = initial.diagnosis

    updated = run_cfdc_route(
        "generic",
        diagnostic_session_state=initial.diagnostic_session,
        diagnostic_adapter=adapter,
        measurement_response=response,
    )

    assert updated.status == "awaiting_profile_measurements"
    assert updated.diagnosis == original_diagnosis
    assert updated.classification is not None
    assert updated.semantic_selection is not None
    assert all(item.status != "unknown" for item in updated.diagnostic_session.checklist)


def test_migrated_session_ignores_tampered_compatible_profile_and_reselects():
    source_adapter = GuidedFakeAdapter()
    initial = run_cfdc_route(
        "generic", description=_description(), diagnostic_adapter=source_adapter
    )
    payload = initial.diagnostic_session.model_dump(mode="json")
    payload["semantic_selection"].update(
        {
            "simulation_profile_id": "first_order_lag_with_delay",
            "feature_bundle_id": "class_i_delay_minimal",
            "selected_feature_ids": ["static_gain", "time_constant", "dead_time"],
        }
    )
    restored = migrate_diagnostic_session_payload(payload)

    class ReselectingAdapter(GuidedFakeAdapter):
        def __init__(self):
            self.selection_calls = 0

        def select_profile(self, description, diagnosis, classification, catalog):
            self.selection_calls += 1
            return super().select_profile(
                description, diagnosis, classification, catalog
            )

    adapter = ReselectingAdapter()
    resumed = run_cfdc_route(
        "generic",
        diagnostic_session_state=restored,
        diagnostic_adapter=adapter,
    )

    assert restored.status == "description_grounded"
    assert restored.semantic_selection is None
    assert adapter.selection_calls == 1
    assert resumed.status == "awaiting_profile_measurements"
    assert resumed.diagnostic_session.status == "awaiting_profile_measurements"
    assert resumed.semantic_selection.simulation_profile_id == "first_order_lag"
    assert resumed.specification_assessment is not None
    assert resumed.diagnostic_session.revision == restored.revision + 1


def test_migrated_session_reselects_then_consumes_profile_response_in_same_call():
    restored = _migrated_measurement_verified_session()
    events = []

    class ResumeAdapter(GuidedFakeAdapter):
        def select_profile(self, description, diagnosis, classification, catalog):
            events.append("select_profile")
            return super().select_profile(
                description, diagnosis, classification, catalog
            )

        def extract_measurements(
            self,
            description,
            measurement_plan,
            measurement_response,
            previous_assessment,
        ):
            if measurement_response.startswith("Manual: input_change"):
                events.append("extract_profile_response")
                assert previous_assessment.status == "ready"
                return previous_assessment.model_dump(mode="json")
            return super().extract_measurements(
                description,
                measurement_plan,
                measurement_response,
                previous_assessment,
            )

    profile_response = (
        "Manual: input_change=1 normalized_input; "
        "steady_output_change=10 degC; response_time_s=20 s; "
        "input_min=-2 normalized_input; input_max=2 normalized_input; "
        "output_min=-30 degC; output_max=80 degC."
    )
    completed = run_cfdc_route(
        "generic",
        diagnostic_session_state=restored,
        diagnostic_adapter=ResumeAdapter(),
        measurement_response=profile_response,
        simulation_bounds_confirmed=True,
    )

    assert events == ["select_profile", "extract_profile_response"]
    assert completed.status == "candidate_unvalidated"
    assert completed.compiled_specification_model is not None
    assert completed.diagnostic_session.revision == restored.revision + 2
    assert completed.diagnostic_session.profile_measurement_round_count == 1
    assert completed.diagnostic_session.specification_answer_history == [
        profile_response
    ]


def test_migrated_session_profile_adapter_failure_is_atomic():
    restored = _migrated_measurement_verified_session()
    before = restored.model_dump(mode="json")

    class FailingReselectionAdapter(GuidedFakeAdapter):
        def select_profile(self, description, diagnosis, classification, catalog):
            description.text = "MUTATED BY FAILING ADAPTER"
            raise RuntimeError("profile provider unavailable")

        def extract_measurements(self, *args, **kwargs):
            raise AssertionError(
                "Profile response must not be consumed before selection"
            )

    with pytest.raises(RuntimeError, match="profile provider unavailable"):
        run_cfdc_route(
            "generic",
            diagnostic_session_state=restored,
            diagnostic_adapter=FailingReselectionAdapter(),
            measurement_response="Manual: input_change=1 normalized_input.",
        )

    assert restored.model_dump(mode="json") == before


def test_diagnostic_round_eight_can_enter_and_complete_profile_collection():
    class RoundEightAdapter(GuidedFakeAdapter):
        def extract_measurements(
            self,
            description,
            measurement_plan,
            measurement_response,
            previous_assessment,
        ):
            if measurement_response.startswith("Diagnostic gap round"):
                return MeasurementAssessment(
                    status="need_more",
                    gaps=[
                        request.diagnostic_field_id
                        for request in measurement_plan.requests
                    ],
                    rationale="The diagnostic record is still incomplete.",
                ).model_dump(mode="json")
            if measurement_response.startswith("Manual: input_change"):
                assert previous_assessment.status == "ready"
                return previous_assessment.model_dump(mode="json")
            return super().extract_measurements(
                description,
                measurement_plan,
                measurement_response,
                previous_assessment,
            )

    adapter = RoundEightAdapter()
    report = run_cfdc_route(
        "generic",
        diagnostic_session_state=start_diagnostic_session(
            _description(), route_id="generic"
        ),
        diagnostic_adapter=adapter,
    )
    for round_index in range(1, 8):
        report = run_cfdc_route(
            "generic",
            diagnostic_session_state=report.diagnostic_session,
            diagnostic_adapter=adapter,
            measurement_response=f"Diagnostic gap round {round_index}.",
        )
        assert report.status == "measurement_needs_more"
    routed = run_cfdc_route(
        "generic",
        diagnostic_session_state=report.diagnostic_session,
        diagnostic_adapter=adapter,
        measurement_response=_complete_diagnostic_response(),
    )
    assert routed.diagnostic_session.measurement_round_count == 8
    assert routed.status == "awaiting_profile_measurements"

    completed = run_cfdc_route(
        "generic",
        diagnostic_session_state=routed.diagnostic_session,
        diagnostic_adapter=adapter,
        measurement_response=(
            "Manual: input_change=1 normalized_input; "
            "steady_output_change=10 degC; response_time_s=20 s; "
            "input_min=-2 normalized_input; input_max=2 normalized_input; "
            "output_min=-30 degC; output_max=80 degC."
        ),
        simulation_bounds_confirmed=True,
    )

    assert completed.status == "candidate_unvalidated"
    assert completed.diagnostic_session.measurement_round_count == 8
    assert completed.diagnostic_session.profile_measurement_round_count == 1


def test_profile_collection_refuses_after_its_own_eighth_incomplete_round():
    class IncompleteProfileAdapter(GuidedFakeAdapter):
        def extract_measurements(
            self,
            description,
            measurement_plan,
            measurement_response,
            previous_assessment,
        ):
            if measurement_response.startswith("Profile specification round"):
                assert previous_assessment.status == "ready"
                return previous_assessment.model_dump(mode="json")
            return super().extract_measurements(
                description,
                measurement_plan,
                measurement_response,
                previous_assessment,
            )

    adapter = IncompleteProfileAdapter()
    report = run_cfdc_route(
        "generic", description=_description(), diagnostic_adapter=adapter
    )

    for round_index in range(1, 8):
        report = run_cfdc_route(
            "generic",
            diagnostic_session_state=report.diagnostic_session,
            diagnostic_adapter=adapter,
            measurement_response=(
                f"Profile specification round {round_index}: still incomplete."
            ),
        )
        assert report.status == "awaiting_profile_measurements"
    refused = run_cfdc_route(
        "generic",
        diagnostic_session_state=report.diagnostic_session,
        diagnostic_adapter=adapter,
        measurement_response="Profile specification round 8: still incomplete.",
    )

    assert refused.status == "rejected"
    assert refused.diagnostic_session.status == "refused"
    assert refused.diagnostic_session.profile_measurement_round_count == 8
    assert (
        refused.diagnostic_session.refusal_reason
        == "maximum_profile_measurement_rounds_reached"
    )


def test_cross_field_tokens_do_not_resolve_either_diagnostic_field():
    class CrossFieldAdapter(EvidenceDrivenAdapter):
        def extract_measurements(
            self,
            description,
            measurement_plan,
            measurement_response,
            previous_assessment,
        ):
            if not measurement_response.startswith("cross-field fragments"):
                return super().extract_measurements(
                    description,
                    measurement_plan,
                    measurement_response,
                    previous_assessment,
                )
            assert previous_assessment.status == "ready"
            return MeasurementAssessment(
                status="ready",
                facts=[
                    (
                        MeasuredFact(
                            request_id=fact.request_id,
                            source_excerpt=(
                                "initially points"
                                if fact.request_id == "minimum_phase"
                                else "opposite"
                            ),
                            text_value=(
                                "initially points"
                                if fact.request_id == "minimum_phase"
                                else "opposite"
                            ),
                        )
                        if fact.request_id in {"minimum_phase", "significant_delay"}
                        else fact
                    )
                    for fact in previous_assessment.facts
                ],
                rationale="Two unrelated fields contain incomplete fragments.",
            ).model_dump(mode="json")

    adapter = CrossFieldAdapter()
    initial = start_diagnostic_session(
        SystemDescription(
            text="temperature and heater change records are available.",
            observed_outputs=["temperature"],
            actuators=["heater"],
        ),
        route_id="generic",
    )
    released = run_cfdc_route(
        "generic",
        diagnostic_session_state=initial,
        diagnostic_adapter=adapter,
        measurement_response=_complete_diagnostic_response(),
    )
    invalidated = run_cfdc_route(
        "generic",
        diagnostic_session_state=released.diagnostic_session,
        diagnostic_adapter=adapter,
        measurement_response="cross-field fragments: initially points; opposite",
    )

    assert invalidated.status == "need_more_information"
    assert invalidated.classification is None
    assert invalidated.diagnosis.minimum_phase.assessment == "unknown"
    assert invalidated.diagnosis.significant_delay.assessment == "unknown"
    assert invalidated.diagnostic_session.measurement_history == []


def test_later_same_request_fact_supersedes_and_triggers_invalidation():
    class SupersedingAdapter(EvidenceDrivenAdapter):
        def extract_measurements(
            self,
            description,
            measurement_plan,
            measurement_response,
            previous_assessment,
        ):
            if "first moves in an unfavorable" not in measurement_response:
                return super().extract_measurements(
                    description,
                    measurement_plan,
                    measurement_response,
                    previous_assessment,
                )
            inverse = (
                "first moves in an unfavorable or opposite direction before turning"
            )
            assert previous_assessment.status == "ready"
            return MeasurementAssessment(
                status="ready",
                facts=[
                    (
                        MeasuredFact(
                            request_id="minimum_phase",
                            source_excerpt=inverse,
                            text_value=inverse,
                        )
                        if fact.request_id == "minimum_phase"
                        else fact
                    )
                    for fact in previous_assessment.facts
                ],
                rationale="The latest phase record supersedes the earlier phase fact.",
            ).model_dump(mode="json")

    adapter = SupersedingAdapter()
    initial = run_cfdc_route(
        "generic", description=_description(), diagnostic_adapter=adapter
    )
    invalidated = run_cfdc_route(
        "generic",
        diagnostic_session_state=initial.diagnostic_session,
        diagnostic_adapter=adapter,
        measurement_response=(
            "first moves in an unfavorable or opposite direction before turning"
        ),
    )

    assert invalidated.status == "need_more_information"
    assert invalidated.classification is None
    assert invalidated.diagnosis.minimum_phase.assessment == "nonminimum_phase"
    assert invalidated.diagnostic_session.measurement_history == []
    assert invalidated.diagnostic_session.description_assessment is None


def test_exact_eight_isolated_facts_produce_complete_diagnosis_and_classification():
    adapter = EvidenceDrivenAdapter()
    initial = start_diagnostic_session(
        SystemDescription(
            text="temperature and heater change records are available.",
            observed_outputs=["temperature"],
            actuators=["heater"],
        ),
        route_id="generic",
    )

    released = run_cfdc_route(
        "generic",
        diagnostic_session_state=initial,
        diagnostic_adapter=adapter,
        measurement_response=_complete_diagnostic_response(),
    )

    assert released.diagnosis.complete
    assert released.classification.primary_class == "class_i_first_order_lag"


def test_profile_measurement_response_enforces_its_independent_session_round_cap():
    adapter = GuidedFakeAdapter()
    initial = run_cfdc_route(
        "generic", description=_description(), diagnostic_adapter=adapter
    )
    capped = initial.diagnostic_session.model_copy(update={"maximum_turns": 1})

    refused = run_cfdc_route(
        "generic",
        diagnostic_session_state=capped,
        diagnostic_adapter=adapter,
        measurement_response="another profile record",
    )

    assert refused.status == "rejected"
    assert refused.diagnostic_session.profile_measurement_round_count == 1
    assert (
        refused.diagnostic_session.refusal_reason
        == "maximum_profile_measurement_rounds_reached"
    )


def test_grounded_profile_diagnostic_contradiction_clears_all_downstream_artifacts():
    class ReclassifyingAdapter(GuidedFakeAdapter):
        def extract_measurements(
            self,
            description,
            measurement_plan,
            measurement_response,
            previous_assessment,
        ):
            if "multivariable interaction" not in measurement_response:
                return super().extract_measurements(
                    description,
                    measurement_plan,
                    measurement_response,
                    previous_assessment,
                )
            assert previous_assessment.status == "ready"
            severe = (
                "changing any one of several actuators noticeably changes several "
                "outputs"
            )
            return MeasurementAssessment(
                status="ready",
                facts=[
                    (
                        MeasuredFact(
                            request_id="coupling_severity",
                            source_excerpt=severe,
                            text_value=severe,
                        )
                        if fact.request_id == "coupling_severity"
                        else fact
                    )
                    for fact in previous_assessment.facts
                ],
                rationale="New structural evidence changes the coupling assessment.",
            ).model_dump(mode="json")

    adapter = ReclassifyingAdapter()
    initial = run_cfdc_route(
        "generic", description=_description(), diagnostic_adapter=adapter
    )
    routed = initial
    assert routed.classification.primary_class == "class_i_first_order_lag"

    invalidated = run_cfdc_route(
        "generic",
        diagnostic_session_state=routed.diagnostic_session,
        diagnostic_adapter=adapter,
        measurement_response=(
            "changing any one of several actuators noticeably changes several "
            "outputs with significant multivariable interaction."
        ),
    )

    assert invalidated.status == "need_more_information"
    assert invalidated.classification is None
    assert invalidated.semantic_selection is None
    assert invalidated.specification_assessment is None
    assert invalidated.specification_templates == []
    assert invalidated.compiled_specification_model is None
    assert invalidated.experiment_plan is None
    assert invalidated.evidence_requirement_plan is None
    assert invalidated.diagnostic_session.candidate_route is None
    assert invalidated.diagnostic_session.compiled_route is None
    assert invalidated.controller is None
    checklist = {
        item.diagnostic_field_id: item
        for item in invalidated.diagnostic_session.checklist
    }
    assert checklist["coupling_severity"].status == "unknown"
    assert checklist["coupling_severity"].evidence == []
    assert sum(item.status != "unknown" for item in checklist.values()) == 7


def test_grounded_profile_diagnostic_conflict_returns_to_measurement_collection():
    conflict_text = (
        "One manual says the output starts in its final direction, while another "
        "manual says it first moves in the opposite direction."
    )

    class ConflictingAdapter(GuidedFakeAdapter):
        def extract_measurements(
            self,
            description,
            measurement_plan,
            measurement_response,
            previous_assessment,
        ):
            if measurement_response == conflict_text:
                assert previous_assessment.status == "ready"
                return MeasurementAssessment(
                    status="conflict",
                    facts=[
                        fact
                        for fact in previous_assessment.facts
                        if fact.request_id != "minimum_phase"
                    ],
                    conflicts=[conflict_text],
                    conflict_request_ids=["minimum_phase"],
                    rationale="The newly submitted phase evidence conflicts.",
                ).model_dump(mode="json")
            return super().extract_measurements(
                description,
                measurement_plan,
                measurement_response,
                previous_assessment,
            )

    adapter = ConflictingAdapter()
    initial = run_cfdc_route(
        "generic", description=_description(), diagnostic_adapter=adapter
    )
    routed = initial

    invalidated = run_cfdc_route(
        "generic",
        diagnostic_session_state=routed.diagnostic_session,
        diagnostic_adapter=adapter,
        measurement_response=conflict_text,
    )

    assert invalidated.status == "need_more_information"
    assert invalidated.classification is None
    assert invalidated.semantic_selection is None
    assert invalidated.specification_assessment is None
    assert invalidated.diagnostic_session.compiled_route is None
    assert invalidated.diagnostic_session.profile_measurement_round_count == 1


def test_measurement_response_is_exclusive_with_legacy_text_inputs():
    adapter = GuidedFakeAdapter()
    initial = run_cfdc_route(
        "generic", description=_description(), diagnostic_adapter=adapter
    )

    for conflicting in (
        {"diagnostic_answers": {"q": "answer"}},
        {"supplemental_description": "another description"},
        {"specification_text": "manual facts"},
    ):
        try:
            run_cfdc_route(
                "generic",
                diagnostic_session_state=initial.diagnostic_session,
                diagnostic_adapter=adapter,
                measurement_response="record response",
                **conflicting,
            )
        except ValueError as exc:
            assert "measurement_response" in str(exc)
        else:
            raise AssertionError("mutually exclusive inputs were accepted")


def test_v4_session_rejects_specification_text_even_without_measurement_response():
    adapter = GuidedFakeAdapter()
    initial = run_cfdc_route(
        "generic", description=_description(), diagnostic_adapter=adapter
    )

    with pytest.raises(ValueError, match="measurement_response"):
        run_cfdc_route(
            "generic",
            diagnostic_session_state=initial.diagnostic_session,
            diagnostic_adapter=adapter,
            specification_text="manual facts",
        )


def test_measurement_response_requires_an_existing_v4_session():
    with pytest.raises(ValueError, match="diagnostic_session_state"):
        run_cfdc_route(
            "generic",
            description=_description(),
            diagnostic_adapter=GuidedFakeAdapter(),
            measurement_response="record response",
        )


def test_profile_facts_require_explicit_simulation_boundary_confirmation():
    adapter = GuidedFakeAdapter()
    initial = run_cfdc_route(
        "generic", description=_description(), diagnostic_adapter=adapter
    )
    routed = run_cfdc_route(
        "generic",
        diagnostic_session_state=initial.diagnostic_session,
        diagnostic_adapter=adapter,
        measurement_response=_complete_diagnostic_response(),
    )

    try:
        run_cfdc_route(
            "generic",
            diagnostic_session_state=routed.diagnostic_session,
            diagnostic_adapter=adapter,
            measurement_response=(
                "Manual: input_change=1 normalized_input; "
                "steady_output_change=10 degC; response_time_s=20 s; "
                "input_min=-2 normalized_input; input_max=2 normalized_input; "
                "output_min=-30 degC; output_max=80 degC."
            ),
        )
    except ValueError as exc:
        assert "simulation bounds" in str(exc)
    else:
        raise AssertionError(
            "profile facts compiled without confirmed simulation bounds"
        )


def test_web_guided_flow_requires_llm_and_uses_measurement_callback(monkeypatch):
    try:
        start_app_run(
            _description().text,
            "temperature",
            "heater power",
            "",
            None,
            False,
            None,
            None,
            None,
        )
    except ValueError as exc:
        assert "LLM" in str(exc)
    else:
        raise AssertionError("generic web flow ran without an LLM")

    adapter = GuidedFakeAdapter()
    monkeypatch.setattr("cfdc.web.service.build_adapter", lambda *args: adapter)
    report, state = start_app_run(
        _description().text,
        "temperature",
        "heater power",
        "",
        None,
        True,
        "https://provider.example/v1",
        "provider-model",
        "secret-that-must-not-be-persisted",
    )
    assert report.status == "awaiting_profile_measurements"

    advanced, next_state = submit_app_measurement_response(
        state,
        "No selected-Profile parameter values are currently known.",
        base_url="https://provider.example/v1",
        model="provider-model",
        api_key="secret-that-must-not-be-persisted",
    )
    assert advanced.status == "awaiting_profile_measurements"
    assert advanced.diagnostic_session.profile_measurement_round_count == 1
    assert "secret-that-must-not-be-persisted" not in str(next_state)


def test_live_measurement_extraction_rejects_non_strict_payload(monkeypatch):
    class FakeCompletions:
        def create(self, **kwargs):
            del kwargs
            content = json.dumps(
                {
                    "status": "need_more",
                    "facts": [],
                    "gaps": ["open_loop_stability"],
                    "conflicts": [],
                    "conflict_request_ids": [],
                    "rationale": "More records are needed.",
                    "unexpected": "not allowed",
                }
            )
            message = type("Message", (), {"content": content})()
            choice = type("Choice", (), {"message": message})()
            return type("Response", (), {"choices": [choice]})()

    class FakeOpenAI:
        def __init__(self, **kwargs):
            del kwargs
            self.chat = type("Chat", (), {"completions": FakeCompletions()})()

    monkeypatch.setattr("cfdc.diagnosis.llm.OpenAI", FakeOpenAI)
    adapter = OpenAICompatibleDiagnosticAdapter(
        base_url="https://provider.example/v1",
        model="provider-model",
        api_key="provider-secret",
    )
    checklist = build_diagnostic_checklist(_description())
    plan = build_measurement_plan(checklist)

    with pytest.raises(ValueError, match="Extra inputs are not permitted"):
        adapter.extract_measurements(_description(), plan, "record", None)


def test_live_profile_recheck_falls_back_and_steering_reply_compiles(monkeypatch):
    steering_description = SystemDescription(
        text=(
            "A first order steering-to-heading process uses 方向盘转角 to change 航向角. "
            + " ".join(_VALID_FIELD_FACTS.values())
        ),
        observed_outputs=["航向角"],
        actuators=["方向盘转角"],
    )

    class SteeringGuidedFakeAdapter(GuidedFakeAdapter):
        def guide_description(self, description, guidance):
            payload = super().guide_description(description, guidance)
            payload["observed_outputs"] = [
                {"name": "航向角", "source_excerpt": "航向角"}
            ]
            payload["actuators"] = [
                {"name": "方向盘转角", "source_excerpt": "方向盘转角"}
            ]
            return payload

    initial = run_cfdc_route(
        "generic",
        description=steering_description,
        diagnostic_adapter=SteeringGuidedFakeAdapter(),
    )
    previous = initial.diagnostic_session.description_assessment
    assert previous is not None and previous.status == "ready"
    invalid_delay_fact = MeasuredFact(
        request_id="significant_delay",
        source_excerpt="输入延迟为0 s",
        numeric_value=1.5,
        unit="s",
    )
    invalid_recheck = previous.model_copy(
        update={
            "facts": [
                invalid_delay_fact
                if fact.request_id == "significant_delay"
                else fact
                for fact in previous.facts
            ],
            "rationale": "The Profile response was incorrectly treated as delay evidence.",
        }
    )

    class FakeCompletions:
        def create(self, **kwargs):
            del kwargs
            message = type(
                "Message", (), {"content": invalid_recheck.model_dump_json()}
            )()
            choice = type("Choice", (), {"message": message})()
            return type("Response", (), {"choices": [choice]})()

    class FakeOpenAI:
        def __init__(self, **kwargs):
            del kwargs
            self.chat = type("Chat", (), {"completions": FakeCompletions()})()

    monkeypatch.setattr("cfdc.diagnosis.llm.OpenAI", FakeOpenAI)
    live_adapter = OpenAICompatibleDiagnosticAdapter(
        base_url="https://provider.example/v1",
        model="provider-model",
        api_key="provider-secret",
    )

    class SteeringProfileAdapter(SteeringGuidedFakeAdapter):
        def extract_measurements(
            self,
            description,
            measurement_plan,
            measurement_response,
            previous_assessment,
        ):
            return live_adapter.extract_measurements(
                description,
                measurement_plan,
                measurement_response,
                previous_assessment,
            )

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
            facts = [
                (
                    "input_change",
                    5.0,
                    "deg",
                    "- **已知输入变化量：** 方向盘转角变化5 deg。",
                ),
                (
                    "steady_output_change",
                    8.0,
                    "deg",
                    "- **最终输出变化量：** 航向角的稳态变化为8 deg。",
                ),
                (
                    "response_time_s",
                    1.5,
                    "s",
                    "- **63% 响应时间：** 1.5 s。",
                ),
                (
                    "input_min",
                    -30.0,
                    "deg",
                    "- **输入仿真下限：** 方向盘转角采用-30 deg。",
                ),
                (
                    "input_max",
                    30.0,
                    "deg",
                    "- **输入仿真上限：** 方向盘转角采用30 deg。",
                ),
                (
                    "output_min",
                    -180.0,
                    "deg",
                    "- **输出仿真下限：** 航向角采用-180 deg作为停止下限。",
                ),
                (
                    "output_max",
                    180.0,
                    "deg",
                    "- **输出仿真上限：** 航向角采用180 deg作为停止上限。",
                ),
            ]
            return {
                "status": "ready",
                "template_id": template.template_id,
                "facts": [
                    {
                        "fact_id": fact_id,
                        "value": value,
                        "unit": unit,
                        "source_type": "user_known_behavior",
                        "source_text": source_text,
                    }
                    for fact_id, value, unit, source_text in facts
                ],
                "missing_fact_ids": [],
                "conflicts": [],
                "rejected_facts": [],
                "questions": [],
                "rationale": "All seven Profile values are grounded in the reply.",
            }

    response = """- **已知输入变化量：** 方向盘转角变化5 deg。
- **最终输出变化量：** 航向角的稳态变化为8 deg。
- **63% 响应时间：** 1.5 s。
- **输入仿真下限：** 方向盘转角采用-30 deg。
- **输入仿真上限：** 方向盘转角采用30 deg。
- **输出仿真下限：** 航向角采用-180 deg作为停止下限。
- **输出仿真上限：** 航向角采用180 deg作为停止上限。

额外信息：

已有软件模型采用从方向盘转角（单位 deg）到航向角（单位 deg）的传递函数。
分子系数为1.6；分母系数为1.5, 1；输入延迟为0 s。"""

    completed = run_cfdc_route(
        "generic",
        diagnostic_session_state=initial.diagnostic_session,
        diagnostic_adapter=SteeringProfileAdapter(),
        measurement_response=response,
        simulation_bounds_confirmed=True,
    )

    assert completed.status == "candidate_unvalidated"
    assert completed.diagnostic_session.current_diagnosis == initial.diagnosis
    assert completed.compiled_specification_model is not None
    assert completed.controller is not None


def test_live_profile_recheck_preserves_a_grounded_changed_fact(monkeypatch):
    description = _description()
    plan = build_measurement_plan(build_diagnostic_checklist(description))
    previous = MeasurementAssessment.model_validate(
        GuidedFakeAdapter().extract_measurements(
            description,
            plan,
            _complete_diagnostic_response(),
            None,
        )
    )
    changed_excerpt = "A newer record says the output grows without bound."
    changed = previous.model_copy(
        update={
            "facts": [
                MeasuredFact(
                    request_id="open_loop_stability",
                    source_excerpt=changed_excerpt,
                    text_value=changed_excerpt,
                )
                if fact.request_id == "open_loop_stability"
                else fact
                for fact in previous.facts
            ],
            "rationale": "One diagnostic fact changed with explicit evidence.",
        }
    )

    class FakeCompletions:
        def create(self, **kwargs):
            del kwargs
            message = type("Message", (), {"content": changed.model_dump_json()})()
            choice = type("Choice", (), {"message": message})()
            return type("Response", (), {"choices": [choice]})()

    class FakeOpenAI:
        def __init__(self, **kwargs):
            del kwargs
            self.chat = type("Chat", (), {"completions": FakeCompletions()})()

    monkeypatch.setattr("cfdc.diagnosis.llm.OpenAI", FakeOpenAI)
    adapter = OpenAICompatibleDiagnosticAdapter(
        base_url="https://provider.example/v1",
        model="provider-model",
        api_key="provider-secret",
    )

    result = MeasurementAssessment.model_validate(
        adapter.extract_measurements(description, plan, changed_excerpt, previous)
    )

    assert result == changed


@pytest.mark.parametrize(
    ("operation", "content"),
    [
        ("guidance", '{"guidance":"invalid"}'),
        ("plan", '{"requests":[]}'),
    ],
)
def test_live_guidance_contract_errors_fall_back_to_deterministic_data(
    monkeypatch,
    operation,
    content,
):
    class FakeCompletions:
        def create(self, **kwargs):
            del kwargs
            message = type("Message", (), {"content": content})()
            choice = type("Choice", (), {"message": message})()
            return type("Response", (), {"choices": [choice]})()

    class FakeOpenAI:
        def __init__(self, **kwargs):
            del kwargs
            self.chat = type("Chat", (), {"completions": FakeCompletions()})()

    monkeypatch.setattr("cfdc.diagnosis.llm.OpenAI", FakeOpenAI)
    adapter = OpenAICompatibleDiagnosticAdapter(
        base_url="https://provider.example/v1",
        model="provider-model",
        api_key="provider-secret",
    )
    checklist = build_diagnostic_checklist(_description())
    plan = build_measurement_plan(checklist)

    if operation == "guidance":
        result = adapter.guide_description(
            _description(), [item.guidance for item in checklist]
        )
        assert [item["response"] for item in result["guidance"]] == ["unknown"] * 8
        assert result["observed_outputs"] == []
        assert result["actuators"] == []
    else:
        assert adapter.phrase_measurement_plan(
            _description(), checklist, plan
        ) == plan.model_dump(mode="json")


def test_live_measurement_prompt_never_contains_provider_secret(monkeypatch):
    captured = {}

    class FakeCompletions:
        def create(self, **kwargs):
            captured.update(kwargs)
            plan = build_measurement_plan(build_diagnostic_checklist(_description()))
            message = type("Message", (), {"content": plan.model_dump_json()})()
            choice = type("Choice", (), {"message": message})()
            return type("Response", (), {"choices": [choice]})()

    class FakeOpenAI:
        def __init__(self, **kwargs):
            del kwargs
            self.chat = type("Chat", (), {"completions": FakeCompletions()})()

    monkeypatch.setattr("cfdc.diagnosis.llm.OpenAI", FakeOpenAI)
    adapter = OpenAICompatibleDiagnosticAdapter(
        base_url="https://provider.example/v1",
        model="provider-model",
        api_key="provider-secret",
    )
    checklist = build_diagnostic_checklist(_description())
    plan = build_measurement_plan(checklist)

    adapter.phrase_measurement_plan(_description(), checklist, plan)

    assert "provider-secret" not in json.dumps(captured)


def test_live_measurement_prompt_carries_facts_from_partial_previous_assessment(
    monkeypatch,
):
    captured = {}
    checklist = build_diagnostic_checklist(_description())
    plan = build_measurement_plan(checklist)
    previous = MeasurementAssessment(
        status="need_more",
        facts=[
            MeasuredFact(
                request_id="open_loop_stability",
                source_excerpt="settles or remains bounded",
                text_value="settles or remains bounded",
            )
        ],
        gaps=[request.diagnostic_field_id for request in plan.requests[1:]],
        rationale="One fact is known and seven remain missing.",
    )

    class FakeCompletions:
        def create(self, **kwargs):
            captured.update(kwargs)
            message = type("Message", (), {"content": previous.model_dump_json()})()
            choice = type("Choice", (), {"message": message})()
            return type("Response", (), {"choices": [choice]})()

    class FakeOpenAI:
        def __init__(self, **kwargs):
            del kwargs
            self.chat = type("Chat", (), {"completions": FakeCompletions()})()

    monkeypatch.setattr("cfdc.diagnosis.llm.OpenAI", FakeOpenAI)
    adapter = OpenAICompatibleDiagnosticAdapter(
        base_url="https://provider.example/v1",
        model="provider-model",
        api_key="provider-secret",
    )

    adapter.extract_measurements(
        _description(),
        plan,
        "A later response addresses another field.",
        previous,
    )

    prompt = captured["messages"][-1]["content"].lower()
    assert "whether previous_assessment is need_more, conflict, or ready" in prompt
    assert "copy each exact prior fact" in prompt
    assert "if previous_assessment is ready" not in prompt
