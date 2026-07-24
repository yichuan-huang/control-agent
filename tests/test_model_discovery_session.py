from __future__ import annotations

import pytest

from cfdc.diagnosis import DiagnosticEngine
from cfdc.lab import (
    StaleRevisionError,
    Stage5DiscoverySnapshot,
    adopt_model_question_example,
    confirm_generated_model,
    create_model_discovery_session,
    record_model_answers,
    request_model_for_discovery_session,
    return_to_model_answers,
)
from cfdc.models import ControllerCandidate, SystemDescription
from tests.test_model_discovery_llm import model_facts, ready_payload


def stage5_snapshot() -> Stage5DiscoverySnapshot:
    description = SystemDescription(
        text=(
            "A room heater changes temperature using electrical power. "
            "The requested controller is a conservative PI candidate."
        ),
        actuators=["heater_power"],
        observed_outputs=["temperature"],
    )
    diagnosis, classification = DiagnosticEngine().run(description)
    controller = ControllerCandidate(
        plant_id=None,
        method_profile_id="generic-first-order",
        architecture="detuned_PI",
        gains={"kp": 0.1, "ki": 0.01},
        tunable_gain_names=["kp", "ki"],
        release_level="candidate_unvalidated",
        status="ready_for_conservative_trial",
        notes=["This candidate is not bound to a plant model yet."],
    )
    return Stage5DiscoverySnapshot(
        source_run_id="run-generic-heater",
        description=description,
        diagnosis=diagnosis,
        classification=classification,
        initial_controller_candidate=controller,
    )


def test_new_discovery_session_has_no_simulation_model():
    session = create_model_discovery_session(stage5=stage5_snapshot())

    assert session.state == "collecting_model_information"
    assert session.pending_envelope is None
    assert session.confirmed_envelope is None
    assert session.simulation_session_id is None
    assert session.revision == 0
    assert session.content_sha256


class NeedMoreAdapter:
    base_url = "https://llm.example.test/v1"
    model = "discovery-test-model"
    api_key = "TEST-SECRET-KEY"

    def propose_model_with_messages(self, context, messages):
        assert "TEST-SECRET-KEY" not in str(messages)
        return {
            "status": "need_more",
            "missing_fact_ids": ["input_step"],
            "questions": [
                {
                    "question_id": "q-heater-input-step",
                    "fact_id": "input_step",
                    "fact_type": "input_step",
                    "prompt": "你把加热功率从多少调到多少？",
                    "answer_kind": "text",
                    "unit_family": "power",
                    "example_id": "thermal.input_step.power.v1",
                    "why_needed": "用于计算输入变化量。",
                }
            ],
            "rationale": "还缺少一次明确的输入变化。",
        }


def test_need_more_result_becomes_current_plain_questions_and_keeps_audit():
    created = create_model_discovery_session(stage5=stage5_snapshot())

    updated = request_model_for_discovery_session(
        created,
        NeedMoreAdapter(),
        expected_revision=created.revision,
    )

    assert updated.state == "collecting_model_information"
    assert [item.question_id for item in updated.current_questions] == [
        "q-heater-input-step"
    ]
    assert updated.missing_fact_ids == ["input_step"]
    assert updated.revision == 1
    assert len(updated.llm_calls) == 1
    assert "TEST-SECRET-KEY" not in updated.model_dump_json()


def session_with_questions():
    created = create_model_discovery_session(stage5=stage5_snapshot())
    return request_model_for_discovery_session(
        created,
        NeedMoreAdapter(),
        expected_revision=created.revision,
    )


def test_blank_answers_do_not_adopt_examples_or_change_revision():
    session = session_with_questions()

    updated = record_model_answers(
        session,
        {"q-heater-input-step": "   "},
        expected_revision=session.revision,
    )

    assert updated.answers == session.answers
    assert updated.revision == session.revision
    assert updated.answer_history == session.answer_history


def test_natural_language_answer_is_recorded_without_silently_using_example():
    session = session_with_questions()

    updated = record_model_answers(
        session,
        {"q-heater-input-step": "从 500 W 调到 1200 W。"},
        expected_revision=session.revision,
    )

    assert updated.revision == session.revision + 1
    assert updated.answers[0].answer_text == "从 500 W 调到 1200 W。"
    assert updated.answers[0].source == "user_supplied"
    assert updated.answers[0].typed_fact is None
    assert updated.answers[0].example_id is None


def test_example_value_is_adopted_only_by_explicit_action():
    session = session_with_questions()

    updated = adopt_model_question_example(
        session,
        "q-heater-input-step",
        expected_revision=session.revision,
    )

    answer = updated.answers[0]
    assert answer.source == "user_adopted_example"
    assert answer.typed_fact is not None
    assert answer.typed_fact.source == "user_adopted_example"
    assert answer.example_id == "thermal.input_step.power.v1"
    assert answer.typed_fact.example_content_sha256


class ReadyAdapter(NeedMoreAdapter):
    def propose_model_with_messages(self, context, messages):
        assert "TEST-SECRET-KEY" not in str(messages)
        return ready_payload()


def session_with_ready_result():
    created = create_model_discovery_session(
        stage5=stage5_snapshot(),
        initial_facts=model_facts(),
    )
    return request_model_for_discovery_session(
        created,
        ReadyAdapter(),
        expected_revision=created.revision,
    )


def test_ready_model_is_frozen_only_after_explicit_confirmation():
    proposed = session_with_ready_result()

    assert proposed.state == "model_review"
    assert proposed.pending_envelope is not None
    assert proposed.confirmed_envelope is None
    confirmed = confirm_generated_model(
        proposed,
        expected_revision=proposed.revision,
    )

    assert confirmed.state == "controller_compatibility_check"
    assert confirmed.confirmed_envelope == proposed.pending_envelope
    assert (
        confirmed.confirmed_envelope_sha256
        == proposed.pending_envelope_sha256
    )
    assert proposed.confirmed_envelope is None


def test_confirmation_rejects_a_stale_browser_revision():
    proposed = session_with_ready_result()

    with pytest.raises(StaleRevisionError, match="stale discovery revision"):
        confirm_generated_model(
            proposed,
            expected_revision=proposed.revision - 1,
        )


def test_return_to_answers_clears_model_but_keeps_audit_history():
    proposed = session_with_ready_result()
    confirmed = confirm_generated_model(
        proposed,
        expected_revision=proposed.revision,
    )

    returned = return_to_model_answers(
        confirmed,
        expected_revision=confirmed.revision,
    )

    assert returned.state == "collecting_model_information"
    assert returned.pending_envelope is None
    assert returned.confirmed_envelope is None
    assert returned.llm_calls == confirmed.llm_calls
    assert returned.facts == confirmed.facts
    assert len(returned.transition_history) == 3


class ReadyFromNaturalAnswerAdapter(NeedMoreAdapter):
    def propose_model_with_messages(self, context, messages):
        input_step = next(
            item for item in model_facts() if item.fact_id == "input_step"
        )
        payload = ready_payload()
        payload["recognized_facts"] = [
            input_step.model_dump(mode="json")
        ]
        return payload


def test_natural_answer_is_typed_and_retained_by_the_audited_model_call():
    initial_facts = [
        item for item in model_facts() if item.fact_id != "input_step"
    ]
    created = create_model_discovery_session(
        stage5=stage5_snapshot(),
        initial_facts=initial_facts,
    )
    questioned = request_model_for_discovery_session(
        created,
        NeedMoreAdapter(),
        expected_revision=created.revision,
    )
    answered = record_model_answers(
        questioned,
        {
            "q-heater-input-step": (
                "Power changed from 0 W to 1 W."
            )
        },
        expected_revision=questioned.revision,
    )

    proposed = request_model_for_discovery_session(
        answered,
        ReadyFromNaturalAnswerAdapter(),
        expected_revision=answered.revision,
    )

    assert proposed.state == "model_review"
    assert {item.fact_id for item in proposed.facts} == {
        item.fact_id for item in model_facts()
    }
    input_answer = next(
        item
        for item in proposed.answers
        if item.fact_id == "input_step"
    )
    assert input_answer.typed_fact is not None
    assert input_answer.answer_text == "Power changed from 0 W to 1 W."
