from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest

from cfdc.agents import AgentRole, AgentRuntime
from cfdc.kernel import WorkflowService
from cfdc.kernel.agents import KernelAgentCoordinator
from cfdc.web import service as web_service


def _diagnostic_state(tmp_path):
    _, state = web_service.start_kernel_app_run(
        {
            "description": "保持温度 / Hold temperature.",
            "task_type": "local_setpoint_hold",
            "measured_signals": ["temperature"],
            "control_inputs": ["heater"],
            "input_min": -1,
            "input_max": 1,
            "state_stop": 12,
        },
        session_dir=tmp_path,
        use_rag=False,
    )
    _, state = web_service.continue_kernel_app_run(
        state, action="confirm_task", payload={}
    )
    return state


@pytest.mark.parametrize(
    "locale,label", [("en", "English"), ("zh-CN", "Simplified Chinese")]
)
@pytest.mark.parametrize("stage", ["model", "user_reply"])
def test_runtime_language_applies_to_generation_review_and_correction(
    locale, label, stage
):
    observed = []
    responses = iter(
        [
            {"answer": "initial"},
            {"decision": "revise", "feedback": "correct the formatting"},
            {"answer": "corrected"},
            {"decision": "pass", "feedback": ""},
        ]
    )

    def complete(request):
        observed.append(request)
        return next(responses)

    runtime = AgentRuntime(complete, response_language=locale)
    task = {"source_text": "温度为 2 degC / temperature is 2 degC", "value": 2.0}
    candidate = runtime.execute(AgentRole.MODELING, stage=stage, request=task).payload
    result = runtime.review_and_correct(
        role=AgentRole.MODELING, stage=stage, request=task, candidate=candidate
    )
    assert result == {"answer": "corrected"}
    assert [request.role for request in observed] == [
        AgentRole.MODELING,
        AgentRole.CRITIC,
        AgentRole.MODELING,
        AgentRole.CRITIC,
    ]
    for request in observed:
        assert request.response_language == locale
        system = request.messages[0]["content"]
        assert label in system
        assert "prose" in system
        for boundary in (
            "schema",
            "enum",
            "evidence",
            "source_text",
            "verbatim",
            "numbers",
        ):
            assert boundary in system
        assert task["source_text"] in request.prompt


def test_runtime_language_defaults_to_english():
    observed = []
    runtime = AgentRuntime(lambda request: observed.append(request) or {})
    runtime.execute(AgentRole.DIAGNOSIS, stage="diagnosis", request={})
    assert observed[0].response_language == "en"
    assert "English" in observed[0].messages[0]["content"]


def test_custom_corrector_audit_retains_response_language():
    responses = iter(
        [
            {"decision": "revise", "feedback": "correct the formatting"},
            {"decision": "pass", "feedback": ""},
        ]
    )
    runtime = AgentRuntime(lambda request: next(responses), response_language="zh-CN")
    result = runtime.review_and_correct(
        role=AgentRole.MODELING,
        stage="model",
        request={},
        candidate={"value": 1},
        corrector=lambda feedback: {"value": 1, "explanation": "格式已修正"},
    )
    assert result["explanation"] == "格式已修正"
    assert len(runtime.audit_log) == 3
    assert all(
        "Simplified Chinese" in record.messages[0]["content"]
        for record in runtime.audit_log
    )


@pytest.mark.parametrize("locale,expected", [("en", "en"), ("zh-CN", "zh")])
def test_coordinator_retrieval_preference_does_not_enable_user_reply_rag(
    tmp_path, locale, expected
):
    state = _diagnostic_state(tmp_path)
    session = WorkflowService(tmp_path).read(state["kernel_session_id"])
    requests = []

    class Retriever:
        def retrieve(self, request, *, limit):
            requests.append(request)
            return []

    coordinator = KernelAgentCoordinator(
        lambda request: {}, retriever=Retriever(), response_language=locale
    )
    coordinator.execute(session, role=AgentRole.DIAGNOSIS, operation="diagnosis")
    assert requests[0].preferred_language() == expected
    coordinator.execute(session, role=AgentRole.DIAGNOSIS, operation="user_reply")
    coordinator.execute(
        session,
        role=AgentRole.CRITIC,
        operation="review",
        task_payload={"operation": "user_reply"},
    )
    assert len(requests) == 1


@pytest.mark.parametrize(
    "locale,source,evidence",
    [
        ("en", "系统稳定。", "系统稳定"),
        ("zh-CN", "The system is stable.", "The system is stable"),
    ],
)
def test_web_reply_language_preserves_cross_language_evidence_and_replay(
    tmp_path, monkeypatch, locale, source, evidence
):
    state = _diagnostic_state(tmp_path)
    observed = []

    def complete(request):
        observed.append(request)
        if request.role is AgentRole.DIAGNOSIS:
            return {
                "diagnostic_updates": {
                    "open_loop_stability": {
                        "status": "known",
                        "assessment": "stable",
                        "evidence": evidence,
                    }
                }
            }
        if request.role is AgentRole.MODELING:
            return {"parameter_candidates": []}
        return {"decision": "pass", "feedback": ""}

    monkeypatch.setattr(
        web_service, "_build_app_adapter", lambda *args, **kwargs: complete
    )
    prepared = web_service.prepare_kernel_reply_for_ui(
        state,
        source,
        mode="natural_language",
        base_url=None,
        model=None,
        api_key=None,
        response_language=locale,
    )
    assert prepared["source_text"] == source
    assert prepared["diagnostic_updates"]["open_loop_stability"]["evidence"] == evidence
    assert len(observed) == 3
    assert {request.response_language for request in observed} == {locale}
    assert not any(request.retrieval for request in observed)
    web_service.continue_kernel_app_run(
        state,
        action="answer",
        payload=prepared["payload"],
        request_identity={"input_mode": prepared["input_mode"], "source_text": source},
        reply_source_text=source,
        reply_input_mode=prepared["input_mode"],
        agent_records=prepared["agent_records"],
    )
    before = WorkflowService(tmp_path).read(state["kernel_session_id"]).to_dict()
    replay = web_service.prepare_kernel_reply_for_ui(
        state,
        source,
        mode="natural_language",
        base_url=None,
        model=None,
        api_key=None,
        response_language="zh-CN" if locale == "en" else "en",
    )
    assert replay["replayed"] is True
    assert len(observed) == 3
    assert (
        WorkflowService(tmp_path).read(state["kernel_session_id"]).to_dict() == before
    )


def test_concurrent_reply_preparation_is_not_shared_between_languages(
    tmp_path, monkeypatch
):
    state = _diagnostic_state(tmp_path)
    barrier = Barrier(2)

    def prepare(*args, response_language, **kwargs):
        barrier.wait(timeout=10)
        return {"prose_language": response_language}

    monkeypatch.setattr(web_service, "_prepare_kernel_reply_for_ui_uncached", prepare)

    def request(locale):
        return web_service.prepare_kernel_reply_for_ui(
            state,
            "系统稳定。",
            mode="natural_language",
            base_url=None,
            model=None,
            api_key=None,
            response_language=locale,
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(request, ("en", "zh-CN")))
    assert results == [{"prose_language": "en"}, {"prose_language": "zh-CN"}]
