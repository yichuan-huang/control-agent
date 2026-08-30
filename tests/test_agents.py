from __future__ import annotations

import pytest

from cfdc.agents import (
    AgentReviewBlocked,
    AgentRole,
    AgentRuntime,
    CompositeAgentAdapter,
    RetrievalSnippet,
)
from cfdc.models import SystemDescription


class ScriptedCompletion:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.requests = []

    def __call__(self, request):
        self.requests.append(request)
        return next(self.responses)


class ProposalAdapter:
    def __init__(self):
        self.calls = 0

    def propose_model(self, context):
        self.calls += 1
        return {"proposal": "initial", "context": context}


def test_role_context_keeps_system_description_immutable_and_isolates_rag_feedback():
    description = SystemDescription(
        text="A heater uses voltage to regulate temperature.",
        observed_outputs=["temperature"],
        actuators=["voltage"],
    )
    completion = ScriptedCompletion([{"answer": "ok"}])
    runtime = AgentRuntime(completion=completion)

    record = runtime.execute(
        AgentRole.DIAGNOSIS,
        description=description,
        stage="diagnose",
        request={"task": "extract structure"},
        retrieval=[RetrievalSnippet(source_id="manual-7", content="thermal lag")],
        feedback="do not invent a delay",
    )

    assert description.model_dump() == {
        "text": "A heater uses voltage to regulate temperature.",
        "observed_outputs": ["temperature"],
        "actuators": ["voltage"],
        "safety_bounds": {},
        "forbidden_actions": [],
        "time_scale_hint_s": None,
        "simulation_boundary_confirmation": None,
        "metadata": {},
    }
    assert record.payload == {"answer": "ok"}
    request = completion.requests[0]
    assert request.description is description
    assert request.retrieval[0].source_id == "manual-7"
    assert request.feedback == "do not invent a delay"
    assert "manual-7" in request.prompt
    assert "do not invent a delay" in request.prompt
    assert "A heater uses voltage to regulate temperature." in request.prompt
    assert request.role is AgentRole.DIAGNOSIS


def test_composite_adapter_revises_once_then_submits_only_after_critic_passes():
    description = SystemDescription(text="A heater.")
    completion = ScriptedCompletion(
        [
            {"decision": "revise", "feedback": "add units"},
            {"proposal": "revised", "units": "V"},
            {"decision": "pass", "feedback": ""},
        ]
    )
    runtime = AgentRuntime(completion=completion)
    adapter = ProposalAdapter()
    wrapped = CompositeAgentAdapter(
        adapter, runtime, description_provider=lambda _: description
    )

    result = wrapped.propose_model({"session": "s1"})

    assert result == {"proposal": "revised", "units": "V"}
    assert adapter.calls == 1
    assert [request.role for request in completion.requests] == [
        AgentRole.CRITIC,
        AgentRole.MODELING,
        AgentRole.CRITIC,
    ]
    assert [record.attempt for record in runtime.audit_log] == [1, 1, 2]
    assert all(
        record.request_hash and record.response_hash for record in runtime.audit_log
    )
    assert runtime.audit_log[0].source_ids == ()


def test_composite_adapter_blocks_failed_review_without_returning_candidate():
    completion = ScriptedCompletion([{"decision": "block", "feedback": "unsafe"}])
    runtime = AgentRuntime(completion=completion)
    wrapped = CompositeAgentAdapter(ProposalAdapter(), runtime)

    with pytest.raises(AgentReviewBlocked, match="unsafe"):
        wrapped.propose_model({"session": "s1"})


@pytest.mark.parametrize("response", [{"decision": "maybe"}, TimeoutError("timed out")])
def test_invalid_or_timed_out_critic_review_fails_closed(response):
    completion = ScriptedCompletion([response])
    runtime = AgentRuntime(completion=completion)

    with pytest.raises(AgentReviewBlocked):
        runtime.review_candidate(
            role=AgentRole.CONTROLLER,
            description=SystemDescription(text="A plant."),
            stage="gain_update",
            request={"candidate": "K"},
            candidate={"gain": 1.0},
        )
