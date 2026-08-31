from __future__ import annotations

import json

import pytest

from cfdc.diagnosis import DiagnosticEngine, OpenAICompatibleDiagnosticAdapter
from cfdc.lab import (
    ModelProposal,
    ModelProposalContext,
    approve_llm_proposal,
    build_gain_proposal_context,
    create_free_input_session,
    export_session,
    request_gain_for_session,
    request_gain_proposal,
    request_model_for_session,
    run_next_trial,
    sanitize_for_audit,
    validate_model_proposal_payload,
)
from cfdc.lab.model_discovery_llm import ModelDiscoveryContext
from cfdc.models import (
    StructuralDiagnosis,
    SystemDescription,
)
from tests.simulation_fixtures import (
    cartpole_model,
    cartpole_session,
    vtol_model,
)


def siso_context():
    description = SystemDescription(
        text=(
            "A stable first-order heater has one voltage input, one "
            "temperature output, and no transport delay."
        ),
        observed_outputs=["temperature"],
        actuators=["heater_voltage"],
    )
    diagnosis, classification = DiagnosticEngine().run(description)
    return ModelProposalContext(
        description=description,
        diagnosis=diagnosis,
        classification=classification,
    )


def tf_payload(*, discrete=False, confidence=0.9, units=True):
    return {
        "status": "ready",
        "model": {
            "kind": "transfer_function",
            "numerator": [0.1] if discrete else [1.0],
            "denominator": [1.0, -0.9] if discrete else [5.0, 1.0],
            "time_domain": "discrete" if discrete else "continuous",
            "sample_time_s": 0.1 if discrete else None,
            "input_delay_s": 0.0,
            "input_signal_id": "heater_voltage",
            "output_signal_id": "temperature",
            "input_units": "V" if units else "unspecified",
            "output_units": "degC" if units else "unknown",
            "parameter_uncertainty": {},
        },
        "confidence": confidence,
        "assumptions": ["local LTI behavior near the declared operating point"],
        "evidence": ["the user supplied the first-order structure and signals"],
        "questions": [],
    }


def _coupling_context(case_id, coupling):
    fixture = cartpole_model() if case_id == 27 else vtol_model()
    if case_id == 27:
        description = SystemDescription(
            text="An underactuated CartPole software model.",
            observed_outputs=list(fixture.output_signal_ids),
            actuators=list(fixture.input_signal_ids),
        )
    else:
        description = SystemDescription(
            text="A cascaded planar VTOL software model.",
            observed_outputs=list(fixture.output_signal_ids),
            actuators=list(fixture.input_signal_ids),
        )
    base = siso_context()
    diagnosis_payload = base.diagnosis.model_dump(mode="python")
    diagnosis_payload["open_loop_stability"].update(
        {
            "status": "known",
            "assessment": "unstable",
            "value": "unstable equilibrium",
            "confidence": 0.95,
            "evidence": ["explicit registered equilibrium"],
        }
    )
    field = diagnosis_payload["coupling_severity"]
    field.update(
        {
            "status": "known",
            "assessment": coupling,
            "value": coupling,
            "confidence": 0.95,
            "evidence": ["explicit structure"],
        }
    )
    diagnosis = StructuralDiagnosis.model_validate(diagnosis_payload)
    return ModelProposalContext(
        description=description,
        diagnosis=diagnosis,
        classification=base.classification,
    ), fixture


@pytest.mark.parametrize("discrete", [False, True])
def test_valid_continuous_and_discrete_tf_proposals(discrete):
    result = validate_model_proposal_payload(
        tf_payload(discrete=discrete), siso_context()
    )
    assert result.status == "ready"
    assert result.model.time_domain == ("discrete" if discrete else "continuous")
    assert result.evidence_boundary == "llm_proposed_model_hypothesis"


def test_valid_state_space_model_proposal():
    payload = tf_payload()
    payload["model"] = {
        "kind": "state_space",
        "a": [[-1.0]],
        "b": [[1.0]],
        "c": [[1.0]],
        "d": [[0.0]],
        "time_domain": "continuous",
        "sample_time_s": None,
        "state_names": ["temperature_state"],
        "input_signal_ids": ["heater_voltage"],
        "output_signal_ids": ["temperature"],
        "initial_state": [0.0],
        "signal_units": {
            "temperature_state": "degC",
            "heater_voltage": "V",
            "temperature": "degC",
        },
        "parameter_uncertainty": {},
    }
    assert validate_model_proposal_payload(payload, siso_context()).status == "ready"


@pytest.mark.parametrize(
    ("case_id", "coupling"),
    [(27, "underactuated"), (192, "cascaded")],
)
def test_valid_registered_cartpole_and_vtol_proposals(case_id, coupling):
    context, fixture_model = _coupling_context(case_id, coupling)
    result = validate_model_proposal_payload(
        {
            "status": "ready",
            "model": fixture_model.model_dump(mode="json"),
            "confidence": 0.9,
            "assumptions": ["registered deterministic template"],
            "evidence": ["complete user-supplied physical parameters"],
            "questions": [],
        },
        context,
    )
    assert result.status == "ready"
    assert result.model.template_id == fixture_model.template_id


@pytest.mark.parametrize(
    "mutation",
    [
        lambda payload: payload.update({"python_code": "import os"}),
        lambda payload: payload["model"].update({"input_units": "unspecified"}),
        lambda payload: payload.update({"confidence": 0.69}),
        lambda payload: payload.update({"evidence": []}),
        lambda payload: payload["model"].update(
            {"input_signal_id": "different_actuator"}
        ),
        lambda payload: payload["model"].update({"denominator": [1.0, -1.0]}),
        lambda payload: payload["model"].update({"unknown": 1}),
    ],
)
def test_model_safety_rejects_or_keeps_in_model_review(mutation):
    payload = tf_payload()
    mutation(payload)
    result = validate_model_proposal_payload(payload, siso_context())
    assert result.status in {"need_more", "rejected"}
    assert result.model is None
    assert result.validation_errors


def test_low_confidence_has_two_to_four_plain_questions():
    result = validate_model_proposal_payload(tf_payload(confidence=0.2), siso_context())
    assert result.status == "need_more"
    assert 2 <= len(result.questions) <= 4


class FakeProposalAdapter:
    base_url = "https://user:password@example.test/v1?token=URLSECRET"
    model = "fake-model"
    api_key = "LITERAL-API-KEY"

    def __init__(self, *, model_payload=None, gain_payload=None):
        self.model_payload = model_payload
        self.gain_payload = gain_payload
        self.model_calls = 0
        self.gain_calls = 0

    def propose_model(self, context):
        self.model_calls += 1
        return self.model_payload

    def propose_gain_update(self, context):
        self.gain_calls += 1
        return self.gain_payload


def test_model_call_is_audited_and_ready_model_still_requires_confirmation():
    adapter = FakeProposalAdapter(model_payload=tf_payload())
    session = create_free_input_session()
    updated, result = request_model_for_session(
        session, adapter, siso_context(), expected_revision=0
    )
    assert isinstance(result.proposal, ModelProposal)
    assert result.proposal.status == "ready"
    assert updated.state == "model_review"
    assert updated.pending_model is not None
    assert updated.confirmed_model is None
    assert len(updated.llm_calls) == 1
    serialized = export_session(updated)
    assert "LITERAL-API-KEY" not in serialized
    assert "URLSECRET" not in serialized


def adjustment_session():
    session = cartpole_session()
    session = run_next_trial(session)
    assert session.state == "needs_adjustment"
    return session


def test_valid_gain_call_registers_pending_and_requires_user_approval():
    session = adjustment_session()
    context = build_gain_proposal_context(session)
    new = {name: value * 1.05 for name, value in context.current_parameters.items()}
    adapter = FakeProposalAdapter(
        gain_payload={
            "new_parameters": new,
            "rationale": "increase registered stabilizing gains by five percent",
        }
    )
    pending, _result = request_gain_for_session(session, adapter)
    assert pending.state == "needs_adjustment"
    assert pending.pending_proposal.approval_state == "pending"
    assert pending.trial_controller == session.trial_controller
    approved = approve_llm_proposal(pending)
    assert approved.state == "trial_pending"
    assert approved.pending_proposal.approval_state == "approved"
    assert adapter.gain_calls == 1


def test_unchanged_gain_call_is_rejected_and_explained():
    session = adjustment_session()
    context = build_gain_proposal_context(session)
    adapter = FakeProposalAdapter(
        gain_payload={
            "new_parameters": dict(context.current_parameters),
            "rationale": "keep the current values",
        }
    )

    updated, result = request_gain_for_session(session, adapter)

    assert result.proposal is None
    assert result.call_record.validation_status == "rejected"
    assert any(
        "change at least one" in error for error in result.call_record.validation_errors
    )
    assert updated.pending_proposal is None
    assert updated.llm_calls[-1].validation_status == "rejected"


@pytest.mark.parametrize(
    "payload",
    [
        {
            "new_parameters": {"kp": 99.0, "kd": 99.0},
            "rationale": "too large",
        },
        {
            "new_parameters": {"kp": 15.1, "unknown": 7.1},
            "rationale": "unknown",
        },
        {
            "new_parameters": {"kp": 15.1, "kd": 7.1},
            "rationale": "inject",
            "approval_state": "approved",
        },
        {
            "new_parameters": {"kp": float("nan"), "kd": 7.1},
            "rationale": "nan",
        },
    ],
)
def test_invalid_gain_calls_are_audited_but_never_registered(payload):
    session = adjustment_session()
    result = request_gain_proposal(session, FakeProposalAdapter(gain_payload=payload))
    assert result.proposal is None
    assert result.call_record.validation_status in {"rejected", "error"}


def test_sanitizer_redacts_nested_keys_literals_bearer_and_url_credentials():
    sanitized = sanitize_for_audit(
        {
            "nested": {
                "Authorization": "Bearer abc.def",
                "note": (
                    "key=MYSECRET https://user:pass@example.test/a?api_key=q&ok=1"
                ),
            }
        },
        secret_literals=["MYSECRET"],
    )
    rendered = json.dumps(sanitized)
    for secret in ("abc.def", "MYSECRET", "user:pass", "api_key=q"):
        assert secret not in rendered
    assert "[REDACTED]" in rendered


def test_openai_adapter_stage6_methods_use_strict_json_prompts(monkeypatch):
    calls = []

    class FakeCompletions:
        def create(self, **kwargs):
            calls.append(kwargs)
            content = (
                json.dumps(tf_payload())
                if len(calls) == 1
                else json.dumps(
                    {
                        "new_parameters": {"kp": 1.0},
                        "rationale": "stability only",
                    }
                )
            )
            message = type("Message", (), {"content": content})()
            choice = type("Choice", (), {"message": message})()
            return type("Response", (), {"choices": [choice]})()

    class FakeOpenAI:
        def __init__(self, **kwargs):
            self.chat = type("Chat", (), {"completions": FakeCompletions()})()

    monkeypatch.setattr("cfdc.diagnosis.llm.OpenAI", FakeOpenAI)
    adapter = OpenAICompatibleDiagnosticAdapter(
        base_url="https://api.deepseek.com",
        model="test-model",
        api_key="key",
    )
    adapter.propose_model(siso_context())
    session = adjustment_session()
    gain_context = build_gain_proposal_context(session)
    adapter.propose_gain_update(gain_context)

    assert len(calls) == 2
    assert all(call["response_format"] == {"type": "json_object"} for call in calls)
    assert all(
        call["extra_body"] == {"thinking": {"type": "disabled"}} for call in calls
    )
    assert "Never emit Python" in calls[0]["messages"][0]["content"]
    assert "within 10%" in calls[1]["messages"][1]["content"]
    assert "Change at least one" in calls[1]["messages"][1]["content"]


def test_openai_adapter_routes_typed_discovery_context_to_three_state_prompt(
    monkeypatch,
):
    calls = []

    class FakeCompletions:
        def create(self, **kwargs):
            calls.append(kwargs)
            message = type(
                "Message",
                (),
                {
                    "content": json.dumps(
                        {
                            "status": "rejected",
                            "reason": "more physical evidence is required",
                            "next_steps": ["provide a measured step response"],
                        }
                    )
                },
            )()
            return type(
                "Response",
                (),
                {"choices": [type("Choice", (), {"message": message})()]},
            )()

    class FakeOpenAI:
        def __init__(self, **kwargs):
            self.chat = type("Chat", (), {"completions": FakeCompletions()})()

    monkeypatch.setattr("cfdc.diagnosis.llm.OpenAI", FakeOpenAI)
    adapter = OpenAICompatibleDiagnosticAdapter(
        base_url="https://api.deepseek.com",
        model="test-model",
        api_key="key",
    )
    legacy = siso_context()
    context = ModelDiscoveryContext(
        description=legacy.description,
        diagnosis=legacy.diagnosis,
        classification=legacy.classification,
        facts=[],
    )

    adapter.propose_model(context)

    prompt = calls[0]["messages"]
    assert "status=need_more|ready|rejected" in prompt[0]["content"]
    assert "fixed_examples=" in prompt[1]["content"]
    assert calls[0]["response_format"] == {"type": "json_object"}
