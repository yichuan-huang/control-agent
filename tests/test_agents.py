from __future__ import annotations

import pytest

from cfdc.agents import (
    AgentReviewBlocked,
    AgentRole,
    AgentRuntime,
    RetrievalSnippet,
)


class ScriptedCompletion:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.requests = []

    def __call__(self, request):
        self.requests.append(request)
        response = next(self.responses)
        if isinstance(response, Exception):
            raise response
        return response


def test_role_context_keeps_system_description_immutable_and_isolates_rag_feedback():
    description = {
        "text": "A heater uses voltage to regulate temperature.",
        "observed_outputs": ["temperature"],
        "actuators": ["voltage"],
    }
    completion = ScriptedCompletion([{"answer": "ok"}])
    runtime = AgentRuntime(completion=completion)

    record = runtime.execute(
        AgentRole.DIAGNOSIS,
        stage="diagnose",
        request={"task": "extract structure", "description": description},
        retrieval=[RetrievalSnippet(source_id="manual-7", content="thermal lag")],
        feedback="do not invent a delay",
    )

    assert description == {
        "text": "A heater uses voltage to regulate temperature.",
        "observed_outputs": ["temperature"],
        "actuators": ["voltage"],
    }
    assert record.payload == {"answer": "ok"}
    request = completion.requests[0]
    assert request.request["description"] is description
    assert request.retrieval[0].source_id == "manual-7"
    assert request.feedback == "do not invent a delay"
    assert "manual-7" in request.prompt
    assert "do not invent a delay" in request.prompt
    assert "A heater uses voltage to regulate temperature." in request.prompt
    assert request.role is AgentRole.DIAGNOSIS


def test_agent_audit_preserves_curated_reference_metadata():
    runtime = AgentRuntime(completion=ScriptedCompletion([{"answer": "ok"}]))
    citation = {
        "source_id": "caltech-feedback-systems-2008",
        "url": "https://authors.library.caltech.edu/records/yzs24-xsx88",
        "license": "Source terms apply; citation metadata only",
    }

    record = runtime.execute(
        AgentRole.CRITIC,
        stage="review",
        request={"task": "review"},
        retrieval=[
            RetrievalSnippet(
                source_id="source-1",
                content="Advisory reference.",
                artifact_id="minimum_phase_inverse_response.en",
                artifact_group_id="minimum_phase_inverse_response",
                language="en",
                authority="advisory",
                artifact_version="1.0.0",
                citation_refs=(citation,),
            )
        ],
    )

    assert record.source_refs[0]["artifact_group_id"] == (
        "minimum_phase_inverse_response"
    )
    assert record.source_refs[0]["language"] == "en"
    assert record.source_refs[0]["authority"] == "advisory"
    assert record.source_refs[0]["artifact_version"] == "1.0.0"
    assert record.source_refs[0]["citation_refs"] == [citation]


def test_runtime_revises_once_then_submits_only_after_critic_passes():
    completion = ScriptedCompletion(
        [
            {"decision": "revise", "feedback": "add units"},
            {"proposal": "revised", "units": "V"},
            {"decision": "pass", "feedback": ""},
        ]
    )
    runtime = AgentRuntime(completion=completion)
    result = runtime.review_and_correct(
        role=AgentRole.MODELING,
        stage="model",
        request={"session": "s1"},
        candidate={"proposal": "initial"},
    )

    assert result == {"proposal": "revised", "units": "V"}
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


def test_runtime_blocks_failed_review_without_returning_candidate():
    completion = ScriptedCompletion([{"decision": "block", "feedback": "unsafe"}])
    runtime = AgentRuntime(completion=completion)

    with pytest.raises(AgentReviewBlocked, match="unsafe"):
        runtime.review_and_correct(
            role=AgentRole.MODELING,
            stage="model",
            request={"session": "s1"},
            candidate={"proposal": "initial"},
        )


@pytest.mark.parametrize("response", [{"decision": "maybe"}, TimeoutError("timed out")])
def test_invalid_or_timed_out_critic_review_fails_closed(response):
    completion = ScriptedCompletion([response])
    runtime = AgentRuntime(completion=completion)

    with pytest.raises(AgentReviewBlocked):
        runtime.review_candidate(
            role=AgentRole.CONTROLLER,
            stage="gain_update",
            request={"candidate": "K"},
            candidate={"gain": 1.0},
        )
