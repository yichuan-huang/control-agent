from __future__ import annotations

import json

import pytest

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


def test_new_profile_evidence_that_changes_classification_clears_downstream_artifacts():
    class ReclassifyingAdapter(GuidedFakeAdapter):
        def diagnose(self, description):
            if "multivariable interaction" in description.text:
                payload = infer_structural_diagnosis(description).model_dump(
                    mode="json"
                )
                payload["coupling_severity"] = {
                    "status": "known",
                    "value": "several inputs affect several outputs",
                    "assessment": "severe_mimo",
                    "confidence": 0.95,
                    "evidence": ["Existing manual reports multivariable interaction."],
                }
                return payload
            return super().diagnose(description)

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
