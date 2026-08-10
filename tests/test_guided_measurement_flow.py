from __future__ import annotations

import json
from typing import ClassVar

import pytest

import cfdc.web.service as web_service
from cfdc.diagnosis import build_diagnostic_checklist, build_measurement_plan
from cfdc.diagnosis.engine import infer_structural_diagnosis
from cfdc.diagnosis.llm import OpenAICompatibleDiagnosticAdapter
from cfdc.models import MeasuredFact, MeasurementAssessment, SystemDescription
from cfdc.runtime import run_cfdc_route
from cfdc.web.service import start_app_run, submit_app_measurement_response
from cfdc.workflow import deterministic_profile_selection


class GuidedFakeAdapter:
    """Complete fake for the structured operations used by the guided flow."""

    def diagnose(self, description):
        return infer_structural_diagnosis(description).model_dump(mode="json")

    def guide_description(self, description, guidance):
        return {
            "guidance": [item.model_dump(mode="json") for item in guidance],
            "observed_outputs": [
                {"name": "temperature", "source_excerpt": "temperature"}
            ],
            "actuators": [
                {"name": "heater", "source_excerpt": "heater change"}
            ],
        }

    def phrase_measurement_plan(self, description, checklist, plan):
        del description, checklist
        return plan.model_dump(mode="json")

    def extract_measurements(
        self, description, measurement_plan, measurement_response, previous_assessment
    ):
        del description, previous_assessment
        if measurement_response == "need another record":
            return MeasurementAssessment(
                status="need_more",
                gaps=[request.diagnostic_field_id for request in measurement_plan.requests],
                rationale="The supplied response did not identify an existing record.",
            ).model_dump(mode="json")
        return MeasurementAssessment(
            status="ready",
            facts=[
                MeasuredFact(
                    request_id=request.request_id,
                    source_excerpt=f"Manual record for {request.title}.",
                    text_value="verified observation",
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

    _facts: ClassVar[dict[str, str]] = {
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

    def diagnose(self, description):
        raise AssertionError("guided formal diagnosis must never call the adapter")

    def extract_measurements(
        self,
        description,
        measurement_plan,
        measurement_response,
        previous_assessment,
    ):
        del description, previous_assessment
        if measurement_response == "new multivariable interaction":
            severe = (
                "changing any one of several actuators noticeably changes several outputs"
            )
            return MeasurementAssessment(
                status="need_more",
                facts=[
                    MeasuredFact(
                        request_id="coupling_severity",
                        source_excerpt=severe,
                        text_value=severe,
                    )
                ],
                gaps=[
                    request.diagnostic_field_id
                    for request in measurement_plan.requests
                    if request.request_id != "coupling_severity"
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
        text="A first order temperature process settles after a heater change.",
        observed_outputs=["temperature"],
        actuators=["heater power"],
    )


def test_generic_route_gates_classification_until_verified_measurements():
    adapter = GuidedFakeAdapter()

    initial = run_cfdc_route(
        "generic", description=_description(), diagnostic_adapter=adapter
    )

    assert initial.status == "awaiting_measurements"
    assert initial.classification is None
    assert initial.semantic_selection is None
    assert initial.diagnostic_session is not None
    assert initial.diagnostic_session.schema_version == "4.0"

    incomplete = run_cfdc_route(
        "generic",
        diagnostic_session_state=initial.diagnostic_session,
        diagnostic_adapter=adapter,
        measurement_response="need another record",
    )

    assert incomplete.status == "measurement_needs_more"
    assert incomplete.classification is None
    assert incomplete.semantic_selection is None

    released = run_cfdc_route(
        "generic",
        diagnostic_session_state=incomplete.diagnostic_session,
        diagnostic_adapter=adapter,
        measurement_response="all records attached",
    )

    assert released.status == "awaiting_profile_measurements"
    assert released.classification is not None
    assert released.semantic_selection is not None
    assert released.diagnostic_session.status == "awaiting_profile_measurements"
    assert released.specification_assessment.questions


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
        measurement_response="all records attached",
    )

    assert released.diagnosis.open_loop_stability.assessment == "stable"
    assert released.diagnosis.coupling_severity.assessment == "siso"
    assert released.classification.primary_class == "class_i_first_order_lag"


def test_verified_measurement_facts_persist_across_session_serialization():
    adapter = GuidedFakeAdapter()
    initial = run_cfdc_route(
        "generic", description=_description(), diagnostic_adapter=adapter
    )
    released = run_cfdc_route(
        "generic",
        diagnostic_session_state=initial.diagnostic_session,
        diagnostic_adapter=adapter,
        measurement_response="all records attached",
    )

    serialized = released.diagnostic_session.model_dump_json()
    restored = type(released.diagnostic_session).model_validate_json(serialized)
    assert "open_loop_stability" in restored.accumulated_description.text
    assert "verified observation" in restored.accumulated_description.text
    assert "Manual record for Open-loop stability." in restored.accumulated_description.text
    assert "all records attached" not in restored.accumulated_description.text


def test_persisted_measurement_facts_drive_later_deterministic_invalidation():
    adapter = EvidenceDrivenAdapter()
    vague_description = SystemDescription(
        text="temperature and heater change records are available.",
        observed_outputs=["temperature"],
        actuators=["heater"],
    )
    initial = run_cfdc_route(
        "generic", description=vague_description, diagnostic_adapter=adapter
    )
    released = run_cfdc_route(
        "generic",
        diagnostic_session_state=initial.diagnostic_session,
        diagnostic_adapter=adapter,
        measurement_response="verified records",
    )
    restored = type(released.diagnostic_session).model_validate_json(
        released.diagnostic_session.model_dump_json()
    )

    invalidated = run_cfdc_route(
        "generic",
        diagnostic_session_state=restored,
        diagnostic_adapter=adapter,
        measurement_response="new multivariable interaction",
    )

    assert invalidated.status == "awaiting_measurements"
    assert invalidated.diagnosis.open_loop_stability.assessment == "stable"
    assert invalidated.diagnosis.coupling_severity.assessment == "severe_mimo"
    assert "settles or remains bounded" in (
        invalidated.diagnostic_session.accumulated_description.text
    )


def test_invalidation_rejects_a_replacement_measurement_plan():
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
    initial = run_cfdc_route(
        "generic",
        description=SystemDescription(
            text="temperature and heater change records are available.",
            observed_outputs=["temperature"],
            actuators=["heater"],
        ),
        diagnostic_adapter=adapter,
    )
    released = run_cfdc_route(
        "generic",
        diagnostic_session_state=initial.diagnostic_session,
        diagnostic_adapter=adapter,
        measurement_response="verified records",
    )

    with pytest.raises(ValueError, match="authoritative request"):
        run_cfdc_route(
            "generic",
            diagnostic_session_state=released.diagnostic_session,
            diagnostic_adapter=adapter,
            measurement_response="new multivariable interaction",
        )


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
        "provenance",
        "invented_name",
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
            elif mutation == "provenance":
                payload["observed_outputs"][0]["source_excerpt"] = "not in source"
            elif mutation == "invented_name":
                payload["observed_outputs"][0] = {
                    "name": "pressure",
                    "source_excerpt": "temperature",
                }
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
    initial = run_cfdc_route(
        "generic", description=_description(), diagnostic_adapter=adapter
    )
    routed = run_cfdc_route(
        "generic",
        diagnostic_session_state=initial.diagnostic_session,
        diagnostic_adapter=adapter,
        measurement_response="all records attached",
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
    assert len(completed.diagnostic_session.measurement_history) == 2
    assert (
        completed.diagnostic_session.measurement_assessment
        == completed.diagnostic_session.measurement_history[-1]
    )


def test_profile_measurement_responses_accumulate_before_joint_invalidation():
    class CumulativeAdapter(EvidenceDrivenAdapter):
        def extract_measurements(
            self,
            description,
            measurement_plan,
            measurement_response,
            previous_assessment,
        ):
            if measurement_response not in {"first fragment", "second fragment"}:
                return super().extract_measurements(
                    description,
                    measurement_plan,
                    measurement_response,
                    previous_assessment,
                )
            request_id, fragment = (
                ("minimum_phase", "initially points")
                if measurement_response == "first fragment"
                else ("significant_delay", "opposite")
            )
            return MeasurementAssessment(
                status="need_more",
                facts=[
                    MeasuredFact(
                        request_id=request_id,
                        source_excerpt=fragment,
                        text_value=fragment,
                    )
                ],
                gaps=[
                    request.diagnostic_field_id
                    for request in measurement_plan.requests
                    if request.request_id != request_id
                ],
                rationale="One additional validated diagnostic observation.",
            ).model_dump(mode="json")

    adapter = CumulativeAdapter()
    initial = run_cfdc_route(
        "generic",
        description=SystemDescription(
            text="temperature and heater change records are available.",
            observed_outputs=["temperature"],
            actuators=["heater"],
        ),
        diagnostic_adapter=adapter,
    )
    released = run_cfdc_route(
        "generic",
        diagnostic_session_state=initial.diagnostic_session,
        diagnostic_adapter=adapter,
        measurement_response="verified records",
    )
    first = run_cfdc_route(
        "generic",
        diagnostic_session_state=released.diagnostic_session,
        diagnostic_adapter=adapter,
        measurement_response="first fragment",
    )

    assert first.status == "awaiting_profile_measurements"
    assert first.diagnostic_session.revision == released.diagnostic_session.revision + 1
    assert len(first.diagnostic_session.measurement_history) == 2
    assert (
        first.diagnostic_session.measurement_assessment
        == first.diagnostic_session.measurement_history[-1]
    )
    restored = type(first.diagnostic_session).model_validate_json(
        first.diagnostic_session.model_dump_json()
    )
    assert "initially points" in restored.accumulated_description.text

    invalidated = run_cfdc_route(
        "generic",
        diagnostic_session_state=restored,
        diagnostic_adapter=adapter,
        measurement_response="second fragment",
    )

    assert invalidated.status == "awaiting_measurements"
    assert invalidated.diagnostic_session.revision == restored.revision + 1
    assert invalidated.classification is None
    assert invalidated.diagnosis.minimum_phase.assessment == "nonminimum_phase"
    assert len(invalidated.diagnostic_session.measurement_history) == 3
    assert (
        invalidated.diagnostic_session.measurement_assessment
        == invalidated.diagnostic_session.measurement_history[-1]
    )
    serialized = invalidated.diagnostic_session.model_dump_json()
    assert "initially points" in serialized
    assert "opposite" in serialized


def test_profile_measurement_response_enforces_the_session_round_cap():
    adapter = GuidedFakeAdapter()
    initial = run_cfdc_route(
        "generic", description=_description(), diagnostic_adapter=adapter
    )
    released = run_cfdc_route(
        "generic",
        diagnostic_session_state=initial.diagnostic_session,
        diagnostic_adapter=adapter,
        measurement_response="all records attached",
    )
    capped = released.diagnostic_session.model_copy(update={"maximum_turns": 1})

    with pytest.raises(ValueError, match="maximum measurement rounds"):
        run_cfdc_route(
            "generic",
            diagnostic_session_state=capped,
            diagnostic_adapter=adapter,
            measurement_response="another profile record",
        )


def test_new_profile_evidence_that_changes_classification_clears_downstream_artifacts():
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
            return MeasurementAssessment(
                status="need_more",
                facts=[
                    MeasuredFact(
                        request_id="coupling_severity",
                        source_excerpt=(
                            "changing any one of several actuators noticeably changes "
                            "several outputs"
                        ),
                        text_value=(
                            "changing any one of several actuators noticeably changes "
                            "several outputs"
                        ),
                    )
                ],
                gaps=[
                    request.diagnostic_field_id
                    for request in measurement_plan.requests
                    if request.request_id != "coupling_severity"
                ],
                rationale="New structural evidence changes the coupling assessment.",
            ).model_dump(mode="json")

    adapter = ReclassifyingAdapter()
    initial = run_cfdc_route(
        "generic", description=_description(), diagnostic_adapter=adapter
    )
    routed = run_cfdc_route(
        "generic",
        diagnostic_session_state=initial.diagnostic_session,
        diagnostic_adapter=adapter,
        measurement_response="all records attached",
    )
    assert routed.classification.primary_class == "class_i_first_order_lag"

    invalidated = run_cfdc_route(
        "generic",
        diagnostic_session_state=routed.diagnostic_session,
        diagnostic_adapter=adapter,
        measurement_response=(
            "An existing manual now reports several inputs visibly affect several "
            "outputs with significant multivariable interaction."
        ),
    )

    assert invalidated.status == "awaiting_measurements"
    assert invalidated.classification is None
    assert invalidated.semantic_selection is None
    assert invalidated.specification_assessment is None
    assert invalidated.diagnostic_session.compiled_route is None


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
        measurement_response="all records attached",
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
        raise AssertionError("profile facts compiled without confirmed simulation bounds")


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
    assert report.status == "awaiting_measurements"

    advanced, next_state = submit_app_measurement_response(
        state,
        "all records attached",
        base_url="https://provider.example/v1",
        model="provider-model",
        api_key="secret-that-must-not-be-persisted",
    )
    assert advanced.status == "awaiting_profile_measurements"
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
            self.chat = type(
                "Chat", (), {"completions": FakeCompletions()}
            )()

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
            self.chat = type(
                "Chat", (), {"completions": FakeCompletions()}
            )()

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
