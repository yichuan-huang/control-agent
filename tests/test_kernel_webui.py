from __future__ import annotations

import json
import os
from dataclasses import replace
from types import SimpleNamespace
from uuid import uuid4

import numpy as np
import pytest
from web_api_helpers import action, api_client, create, finish

from cfdc.kernel import WorkflowService
from cfdc.kernel import replies as kernel_replies
from cfdc.kernel.agents import KernelAgentCoordinator
from cfdc.kernel.replies import (
    KernelReplyMode,
    build_kernel_input_contract,
    prepare_kernel_reply,
)
from cfdc.web import readmodels
from cfdc.web import service as web_service
from cfdc.web.drafts import (
    TASK_TYPES,
    DraftValidationError,
    case_draft,
    empty_draft,
    task_from_draft,
)
from cfdc.web.presentation import project_workspace
from cfdc.web.service import (
    continue_kernel_app_run,
    prepare_kernel_reply_for_ui,
    start_kernel_app_run,
    start_kernel_case_run,
)


class _WebRAGEncoder:
    model_name = "intfloat/multilingual-e5-small"
    model_revision = "614241f622f53c4eeff9890bdc4f31cfecc418b3"

    def encode(self, texts, *, is_query=False):
        del is_query
        if isinstance(texts, str):
            texts = [texts]
        vocabulary = ("stability", "delay", "damping", "mimo", "qualification")
        return np.asarray(
            [[text.casefold().count(word) for word in vocabulary] for text in texts],
            dtype=float,
        )


def test_webui_shows_real_evaluation_curve_and_readiness_budget() -> None:
    report = {
        "evaluation_packets": [
            {
                "evaluation_split": "development",
                "trials": [
                    {
                        "trajectory": {
                            "time_s": [0.0, 1.0],
                            "outputs": {"y": [0.0, 1.0]},
                            "references": {"y": [1.0, 1.0]},
                            "control_inputs": {"u": [1.0, 0.0]},
                        }
                    }
                ],
            }
        ],
        "readiness_gates": {
            "evidence_acquisition": {"ready": True, "blockers": []},
            "route_selection": {
                "ready": False,
                "blockers": ["candidate_set_not_resolved"],
            },
            "controller_synthesis": {
                "ready": False,
                "blockers": ["public_feature_artifact_required"],
            },
        },
        "information_budget": {
            "distinct_protocols_remaining": 2,
            "distinct_protocols_limit": 4,
            "excitation_time_remaining_s": 120.0,
            "failed_attempts": 1,
        },
        "input_contract": {"guidance": "继续取证。"},
        "route": {"selection_reason": "maximin public evidence"},
    }
    curve = readmodels.curve_view(report, "0:0", "y")
    assert [line.name for line in curve.output] == ["y", "目标值"]
    assert curve.control[0].name == "u"
    assert curve.output[0].y == [0.0, 1.0]
    assert curve.control[0].y == [1.0, 0.0]
    gates = readmodels.node_page(report, "readiness_gates")
    assert {item.key for item in gates.items} == {
        "evidence_acquisition",
        "route_selection",
        "controller_synthesis",
    }
    assert (
        readmodels.node_page(
            report, "readiness_gates", "/route_selection/blockers/0"
        ).text
        == "candidate_set_not_resolved"
    )
    assert (
        readmodels.node_page(
            report, "information_budget", "/distinct_protocols_remaining"
        ).value
        == 2
    )
    assert (
        readmodels.node_page(
            report, "information_budget", "/distinct_protocols_limit"
        ).value
        == 4
    )
    assert (
        readmodels.node_page(report, "route", "/selection_reason").text
        == "maximin public evidence"
    )


def test_webui_explains_tuning_exhaustion_as_a_terminal_capability_gap() -> None:
    report = {
        "status": "capability_gap",
        "session_id": "session-gap",
        "revision": 18,
        "task": {
            "task_type": "local_setpoint_hold",
            "measured_signals": ["y"],
            "control_inputs": ["u"],
        },
        "tuning": {"reason": "no_strict_development_improvement"},
        "input_contract": {"disabled_reason": "会话已终止：capability_gap"},
    }

    workspace = project_workspace(report)
    assert workspace["actionable"] is False
    assert workspace["result_visible"] is True
    assert "未" in workspace["explanation"]
    assert (
        readmodels.node_page(report, "tuning", "/reason").text
        == "no_strict_development_improvement"
    )


def _kernel_inputs(tmp_path):
    return start_kernel_app_run(
        {
            "description": "保持加热器温度在设定值附近",
            "task_type": "local_setpoint_hold",
            "measured_signals": ["temperature"],
            "control_inputs": ["heater"],
            "input_min": -1,
            "input_max": 1,
            "output_min": -10,
            "output_max": 10,
            "state_stop": 12,
        },
        session_dir=tmp_path,
        use_rag=False,
    )


def test_kernel_start_exposes_explicit_budget_confirmation(tmp_path):
    report, state = _kernel_inputs(tmp_path)

    assert report["status"] == "intake"
    assert state["pending_actions"]
    assert state["pending_actions"][0]["action"] == "confirm_task"
    view = readmodels.summary(report)
    assert view.workspace.action == "confirm_task"
    assert view.workspace.actionable
    assert "确认" in view.workspace.action_title


@pytest.mark.parametrize(
    "allowed_modes", [[], ["natural_language"], ["json"], ["natural_language", "json"]]
)
def test_reply_modes_are_explicit_in_semantic_contract(allowed_modes):
    view = readmodels.summary({"input_contract": {"allowed_modes": allowed_modes}})
    assert view.input_contract["allowed_modes"] == allowed_modes


def test_manual_fresh_confirmation_keeps_json_input_contract(tmp_path):
    service = WorkflowService(tmp_path)
    session = service.start(
        {
            "description": "Hold a measured output near its reference.",
            "task_type": "local_setpoint_hold",
            "measured_signals": ["output"],
            "control_input": "input",
            "input_min": -1,
            "input_max": 1,
            "state_stop": 2,
        }
    )
    staged = replace(
        session,
        status="awaiting_confirmation",
        tuning={"accepted": True},
        pending_actions=(
            {"kind": "confirmation", "action": "record_fresh_confirmation"},
        ),
    )

    pending = web_service._kernel_pending_actions(staged)
    contract = build_kernel_input_contract(staged, pending_actions=pending)

    assert pending == ({"kind": "confirmation", "action": "record_fresh_confirmation"},)
    assert contract["action"] == "confirmation"
    assert contract["allowed_modes"] == ["json"]
    assert readmodels.summary({"input_contract": contract}).input_contract[
        "allowed_modes"
    ] == ["json"]


def test_registered_single_heater_fresh_confirmation_uses_provider_button(tmp_path):
    report, state = start_kernel_case_run(
        "tclab_single_heater_v1",
        session_dir=tmp_path,
        use_rag=False,
    )
    report, state = continue_kernel_app_run(
        state,
        action="confirm_task",
        payload={},
    )
    assert report["status"] == "tuning_eligible"

    report, state = continue_kernel_app_run(
        state,
        action="run_feedback_iteration",
        payload={},
    )

    assert report["status"] == "awaiting_confirmation"
    assert report["tuning"]["status"] == "selected"
    assert report["tuning"]["accepted"] is True
    assert report["pending_actions"] == [
        {
            "kind": "confirmation",
            "action": "record_fresh_confirmation",
            "ui_action": "confirm_result",
        }
    ]
    assert report["input_contract"]["action"] == "confirm_result"
    assert report["input_contract"]["allowed_modes"] == []
    view = readmodels.summary(report)
    assert view.input_contract["allowed_modes"] == []
    assert view.workspace.action == "confirm_result"
    assert view.workspace.actionable

    persisted = WorkflowService(tmp_path).read(state["kernel_session_id"])
    assert persisted.pending_actions == (
        {"kind": "confirmation", "action": "record_fresh_confirmation"},
    )

    report, _ = continue_kernel_app_run(
        state,
        action="confirm_result",
        payload={},
    )

    assert report["status"] == "performance_met"
    assert report["pending_actions"] == []
    assert report["confirmation"]["status"] == "performance_met"
    assert report["evaluation_packets"][-1]["evaluation_split"] == (
        "fresh_confirmation"
    )
    assert report["evaluation_replays"][-1]["matches_previous"] is True


@pytest.mark.parametrize(
    ("task_type", "extra"),
    [
        ("local_setpoint_hold", {}),
        (
            "transition_then_hold",
            {"initial_region": "低温区域", "goal_region": "目标温度区域"},
        ),
        (
            "disturbance_recovery_to_hold",
            {
                "disturbance_event": "负载阶跃增加",
                "recovery_start_condition": "扰动施加完成",
                "disturbance_hold_region": "目标温度带",
            },
        ),
    ],
)
def test_web_task_contract_supports_all_kernel_task_types(tmp_path, task_type, extra):
    report, _ = start_kernel_app_run(
        {
            "description": "验证完整 Kernel 任务合同",
            "task_type": task_type,
            "measured_signals": ["temperature"],
            "control_inputs": ["heater"],
            "input_min": -1,
            "input_max": 1,
            "state_stop": 12,
            **extra,
        },
        session_dir=tmp_path / task_type,
        use_rag=False,
    )

    assert report["task"]["task_type"] == task_type
    assert report["agent_config"]["mode"] == "multi"


@pytest.mark.parametrize(
    ("update", "message"),
    [
        ({"measured_signals": []}, "观测输出"),
        ({"control_inputs": []}, "控制输入"),
        ({"input_min": 1, "input_max": 1}, "下界必须小于上界"),
        ({"state_stop": 0}, "停止阈值必须大于"),
        ({"output_min": -1, "output_max": None}, "必须同时填写"),
    ],
)
def test_web_task_contract_rejects_missing_or_invalid_boundaries(
    tmp_path, update, message
):
    task = {
        "description": "保持温度",
        "task_type": "local_setpoint_hold",
        "measured_signals": ["temperature"],
        "control_inputs": ["heater"],
        "input_min": -1,
        "input_max": 1,
        "state_stop": 12,
    }
    task.update(update)

    with pytest.raises(ValueError, match=message):
        start_kernel_app_run(task, session_dir=tmp_path, use_rag=False)


def test_kernel_feature_and_controller_columns_use_their_own_artifacts(tmp_path):
    report, _ = _kernel_inputs(tmp_path)
    report["features"] = {
        "features": {"static_gain": {"value": 2.0, "unit": "unit/unit"}},
        "quality": {"status": "pass"},
    }
    report["controller"] = {
        "ir": {"family": "PI", "parameters": {"kp": 1.0, "ki": 0.1}},
        "validation": {"eligible": True},
    }

    features = readmodels.node_page(report, "features", "/features")
    controller = readmodels.node_page(report, "controller", "/ir")
    assert "static_gain" in {item.key for item in features.items}
    assert "family" in {item.key for item in controller.items}
    assert "validation" not in {item.key for item in features.items}


def test_empty_page_actions_are_reloaded_from_kernel_session(tmp_path):
    _, state = _kernel_inputs(tmp_path)
    with api_client(tmp_path) as client:
        refreshed = client.get(f"/api/v1/tasks/{state['kernel_session_id']}").json()
    assert refreshed["revision"] == state["kernel_revision"]
    assert refreshed["pending_actions"][0]["action"] == "confirm_task"


def test_kernel_page_revision_and_action_id_are_stable_and_payload_cannot_override(
    tmp_path,
):
    _, state = _kernel_inputs(tmp_path)
    page_state = dict(state)

    report, confirmed_state = continue_kernel_app_run(
        page_state,
        action="confirm_task",
        payload={},
    )
    first_events = report["events"]
    assert first_events[-1]["action_id"] != "web-action"

    repeated_report, _ = continue_kernel_app_run(
        page_state,
        action="confirm_task",
        payload={},
    )
    assert len(repeated_report["events"]) == len(first_events)

    with pytest.raises(ValueError, match="stale_revision"):
        continue_kernel_app_run(
            page_state,
            action="confirm_task",
            payload={"budget": {"clarification_rounds": 3}},
        )

    assert confirmed_state["kernel_revision"] == report["revision"]


def test_kernel_unconfirmed_advance_is_rejected(tmp_path):
    _, state = _kernel_inputs(tmp_path)

    with pytest.raises(ValueError, match="当前待处理动作"):
        continue_kernel_app_run(state, action="advance", payload={})


def test_kernel_tuning_action_maps_to_the_public_web_entry(tmp_path) -> None:
    assert web_service._normalise_kernel_action("run_tuning") == (
        "run_feedback_iteration"
    )
    service = WorkflowService(tmp_path)
    session = service.read(_kernel_inputs(tmp_path)[1]["kernel_session_id"])
    session = replace(
        session,
        status="tuning_eligible",
        pending_actions=({"kind": "tuning", "action": "run_tuning"},),
    )
    contract = build_kernel_input_contract(session)
    assert contract["action"] == "run_feedback_iteration"
    assert contract["disabled_reason"] is None
    assert contract["allowed_modes"] == []


def test_webui_rejects_non_kernel_report(tmp_path):
    with api_client(tmp_path) as client:
        response = client.post(
            "/api/v1/artifacts/validate",
            json={"payload": {"workflow_version": "unknown/v9"}},
        )
        assert response.status_code == 422


def test_kernel_confirmation_button_does_not_require_empty_json(tmp_path):
    _, state = _kernel_inputs(tmp_path)
    with api_client(tmp_path) as client:
        rejected = finish(
            client, action(client, state, "confirm_task", confirmed=False)
        )
        assert rejected["status"] == "failed"
        assert (
            WorkflowService(tmp_path).read(state["kernel_session_id"]).revision
            == state["kernel_revision"]
        )
        accepted = finish(
            client,
            action(
                client,
                state,
                "confirm_task",
                confirmed=True,
                mode="json",
                text="stale editor text",
            ),
        )
        assert accepted["status"] == "completed"
        view = client.get(f"/api/v1/tasks/{state['kernel_session_id']}").json()
    assert view["status"] == "diagnostic"
    assert view["pending_actions"][0]["action"] == "submit_answer"


def test_empty_kernel_reply_does_not_mutate_without_llm_configuration(tmp_path):
    _, state = _kernel_inputs(tmp_path)
    _, state = continue_kernel_app_run(state, action="confirm_task", payload={})
    with api_client(tmp_path) as client:
        rejected = finish(client, action(client, state, "answer", text=""))
    assert rejected["status"] == "failed"
    assert (
        WorkflowService(tmp_path).read(state["kernel_session_id"]).revision
        == state["kernel_revision"]
    )


def test_kernel_reply_contract_allows_natural_language_diagnosis(tmp_path):
    _, state = _kernel_inputs(tmp_path)
    report, state = continue_kernel_app_run(state, action="confirm_task", payload={})
    del report

    contract = build_kernel_input_contract(
        WorkflowService(tmp_path).read(state["kernel_session_id"])
    )
    assert contract["action"] == "submit_answer"
    assert "natural_language" in contract["allowed_modes"]
    assert "json" in contract["allowed_modes"]

    class FakeCompletion:
        def __call__(self, request):
            if request.role.value == "critic":
                return {"decision": "pass", "feedback": ""}
            if request.role.value == "diagnosis":
                return {
                    "diagnostic_updates": {
                        "open_loop_stability": {
                            "status": "known",
                            "assessment": "stable",
                            "evidence": "系统稳定",
                            "confidence": 0.9,
                        }
                    }
                }
            return {
                "parameter_candidates": [
                    {
                        "fact_id": "static_gain",
                        "value": 2.0,
                        "unit": "degC/kW",
                        "source_text": "静态增益为2 degC/kW",
                    }
                ]
            }

    coordinator = KernelAgentCoordinator(FakeCompletion(), agent_mode="multi")
    prepared = prepare_kernel_reply(
        WorkflowService(tmp_path).read(state["kernel_session_id"]),
        "系统稳定，静态增益为2 degC/kW。",
        mode=KernelReplyMode.NATURAL_LANGUAGE,
        coordinator=coordinator,
    )
    assert (
        prepared["diagnostic_updates"]["open_loop_stability"]["assessment"] == "stable"
    )
    assert prepared["parameter_candidates"][0]["fact_id"] == "static_gain"
    assert prepared["source_text"] == "系统稳定，静态增益为2 degC/kW。"


def test_kernel_single_reply_uses_one_typed_agent_call(tmp_path):
    _, state = _kernel_inputs(tmp_path)
    _, state = continue_kernel_app_run(state, action="confirm_task", payload={})
    session = WorkflowService(tmp_path).read(state["kernel_session_id"])
    calls = []

    class FakeCompletion:
        def __call__(self, request):
            calls.append(request.role.value)
            return {
                "diagnostic_updates": {
                    "open_loop_stability": {
                        "status": "known",
                        "evidence": "系统稳定",
                    }
                },
                "parameter_candidates": [
                    {
                        "fact_id": "static_gain",
                        "value": 2,
                        "unit": "degC/kW",
                        "source_text": "静态增益为2 degC/kW",
                    }
                ],
            }

    prepared = prepare_kernel_reply(
        session,
        "系统稳定，静态增益为2 degC/kW。",
        mode=KernelReplyMode.NATURAL_LANGUAGE,
        coordinator=KernelAgentCoordinator(FakeCompletion(), agent_mode="single"),
    )

    assert calls == ["diagnosis"]
    assert prepared["parameter_candidates"][0]["fact_id"] == "static_gain"


def test_kernel_reply_json_code_fence_is_parsed_without_llm(tmp_path):
    _, state = _kernel_inputs(tmp_path)
    report, state = continue_kernel_app_run(state, action="confirm_task", payload={})
    del report
    session = WorkflowService(tmp_path).read(state["kernel_session_id"])

    prepared = prepare_kernel_reply(
        session,
        '```json\n{"open_loop_stability": {"status": "unknown", "evidence": "不知道"}}\n```',
        mode=KernelReplyMode.JSON,
    )
    assert prepared["diagnostic_updates"]["open_loop_stability"]["status"] == "unknown"
    assert prepared["parameter_candidates"] == []


def test_kernel_reply_json_can_contain_diagnostics_and_parameters_together(tmp_path):
    _, state = _kernel_inputs(tmp_path)
    _, state = continue_kernel_app_run(state, action="confirm_task", payload={})
    session = WorkflowService(tmp_path).read(state["kernel_session_id"])

    prepared = prepare_kernel_reply(
        session,
        '{"open_loop_stability": {"status": "known", "evidence": "系统稳定"}, '
        '"parameter_candidates": [{"fact_id": "static_gain", "value": 2, '
        '"unit": "degC/kW", "source_text": "静态增益为2 degC/kW"}]}',
        mode=KernelReplyMode.JSON,
    )

    assert prepared["diagnostic_updates"]["open_loop_stability"]["status"] == "known"
    assert prepared["parameter_candidates"][0]["fact_id"] == "static_gain"


def test_kernel_reply_accepts_multiple_verbatim_diagnostic_excerpts(tmp_path):
    _, state = _kernel_inputs(tmp_path)
    _, state = continue_kernel_app_run(state, action="confirm_task", payload={})
    session = WorkflowService(tmp_path).read(state["kernel_session_id"])

    prepared = prepare_kernel_reply(
        session,
        '{"open_loop_stability": {"status": "known", "evidence": ["系统稳定", "没有自行增长"]}}',
        mode=KernelReplyMode.JSON,
    )
    assert (
        prepared["diagnostic_updates"]["open_loop_stability"]["evidence"] == "系统稳定"
    )


def test_kernel_reply_uses_critic_correction_before_submission(tmp_path):
    _, state = _kernel_inputs(tmp_path)
    _, state = continue_kernel_app_run(state, action="confirm_task", payload={})
    session = WorkflowService(tmp_path).read(state["kernel_session_id"])
    critic_calls = 0
    modeling_calls = 0
    observed_requests = []

    class FakeCompletion:
        def __call__(self, request):
            nonlocal critic_calls, modeling_calls
            observed_requests.append(request)
            if request.role.value == "critic":
                critic_calls += 1
                if critic_calls == 1:
                    return {"decision": "revise", "feedback": "请修正候选格式"}
                return {"decision": "pass", "feedback": ""}
            if request.role.value == "diagnosis":
                return {
                    "diagnostic_updates": {
                        "open_loop_stability": {
                            "status": "known",
                            "evidence": "系统稳定",
                        }
                    }
                }
            modeling_calls += 1
            source = "静态增益为2 degC/kW"
            value = 1.5 if modeling_calls == 1 else 2.0
            return {
                "parameter_candidates": [
                    {
                        "fact_id": "static_gain",
                        "value": value,
                        "unit": "degC/kW",
                        "source_text": source,
                    }
                ]
            }

    prepared = prepare_kernel_reply(
        session,
        "系统稳定，静态增益为2 degC/kW。",
        mode=KernelReplyMode.NATURAL_LANGUAGE,
        coordinator=KernelAgentCoordinator(FakeCompletion(), agent_mode="multi"),
    )

    assert prepared["parameter_candidates"][0]["value"] == 2.0
    assert modeling_calls == 2
    assert critic_calls == 2
    review_or_revision = [
        request
        for request in observed_requests
        if request.role.value == "critic" or request.revision == 1
    ]
    assert review_or_revision
    for request in review_or_revision:
        rendered = json.dumps(request.request, ensure_ascii=False)
        assert "input_min" not in rendered
        assert "output_max" not in rendered
        assert "state_stop" not in rendered
    critic_system = next(
        request.messages[0]["content"]
        for request in observed_requests
        if request.role.value == "critic"
    )
    assert "A partial candidate" in critic_system


def test_kernel_diagnosis_prompt_distinguishes_asserted_and_unknown_facts(tmp_path):
    _, state = _kernel_inputs(tmp_path)
    _, state = continue_kernel_app_run(state, action="confirm_task", payload={})
    session = WorkflowService(tmp_path).read(state["kernel_session_id"])
    diagnosis_requests = []

    class FakeCompletion:
        def __call__(self, request):
            if request.role.value == "diagnosis":
                diagnosis_requests.append(request)
                return {
                    "diagnostic_updates": {
                        "open_loop_stability": {
                            "status": "known",
                            "assessment": "stable",
                            "evidence": "系统稳定",
                        }
                    }
                }
            if request.role.value == "modeling":
                return {"parameter_candidates": []}
            return {"decision": "pass", "feedback": ""}

    prepare_kernel_reply(
        session,
        "系统稳定。",
        mode=KernelReplyMode.NATURAL_LANGUAGE,
        coordinator=KernelAgentCoordinator(FakeCompletion(), agent_mode="multi"),
    )

    assert len(diagnosis_requests) == 1
    system = diagnosis_requests[0].messages[0]["content"]
    prompt = diagnosis_requests[0].messages[1]["content"]
    assert "Use status=known for an explicit assertion" in system
    assert "Use status=unknown only when the user explicitly says" in system
    assert "canonical_assessments" in prompt
    assert "Omit confidence" in prompt
    payload = diagnosis_requests[0].request["task_payload"]
    assert set(payload["canonical_assessments"]) == set(
        payload["allowed_diagnostic_ids"]
    )


@pytest.mark.skipif(
    os.getenv("CFDC_RUN_OLLAMA_SMOKE") != "1",
    reason="set CFDC_RUN_OLLAMA_SMOKE=1 to run the local Ollama acceptance test",
)
def test_live_ollama_dc_motor_flow_fails_closed_after_bounded_tuning(tmp_path):
    base_url = os.getenv("CFDC_OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1")
    model = os.getenv("CFDC_OLLAMA_MODEL", "gemma4:e4b")
    api_key = os.getenv("CFDC_OLLAMA_API_KEY", "ollama")
    report, state = start_kernel_case_run(
        "dc_motor_speed_v1",
        session_dir=tmp_path,
        use_rag=False,
        llm_configured=True,
    )
    # Registered cases now retain their Provider authority in the persisted
    # Kernel binding; do not use stale browser state to disable it.  Confirm
    # the software boundary directly so this smoke can exercise the LLM
    # diagnosis step before the configured automatic Provider path runs.
    service = WorkflowService(tmp_path)
    service.confirm_task(
        report["session_id"],
        action_id="live-confirm",
        revision=report["revision"],
    )
    report, state = web_service.load_kernel_app_run(
        report["session_id"], session_dir=tmp_path
    )
    assert report["status"] == "diagnostic"
    source_text = (
        "开环稳定；没有反向响应；纯延迟不显著；相对阶数较低；"
        "传感器和执行器足够；工作区内非线性较弱；对象是单输入单输出；"
        "实验间变化较小"
    )
    prepared = prepare_kernel_reply_for_ui(
        state,
        source_text,
        mode="natural_language",
        base_url=base_url,
        model=model,
        api_key=api_key,
    )
    report, state = continue_kernel_app_run(
        state,
        action="answer",
        payload=prepared["payload"],
        request_identity={
            "input_mode": prepared["input_mode"],
            "source_text": prepared["source_text"],
        },
        reply_source_text=prepared["source_text"],
        reply_input_mode=prepared["input_mode"],
        agent_records=prepared["agent_records"],
    )

    assert report["status"] == "tuning_eligible"
    assert report["route"]["profile_id"] == "first_order_lag"
    assert report["route"]["controller_contract_id"] == "PI"
    assert report["controller"]["ir"]["family"] == "PI"
    assert report["qualification"]["status"] == "offline_qualified"
    assert {record["role"] for record in report["agent_records"]} >= {
        "diagnosis",
        "modeling",
        "critic",
    }

    report, state = continue_kernel_app_run(
        state,
        action="run_feedback_iteration",
        payload={},
    )
    assert report["status"] == "capability_gap"
    assert report["tuning"]["status"] == "exhausted"
    assert report["tuning"]["reason"] == "no_strict_development_improvement"
    assert report["pending_actions"] == []
    serialized = json.dumps(report, ensure_ascii=False)
    assert api_key not in serialized


def test_kernel_reply_reports_agent_conflicts_without_submitting(tmp_path):
    _, state = _kernel_inputs(tmp_path)
    _, state = continue_kernel_app_run(state, action="confirm_task", payload={})
    session = WorkflowService(tmp_path).read(state["kernel_session_id"])

    class FakeCompletion:
        def __call__(self, request):
            if request.role.value == "diagnosis":
                return {
                    "diagnostic_updates": {},
                    "conflicts": ["用户对稳定性给出了相反描述"],
                }
            return {"parameter_candidates": []}

    with pytest.raises(ValueError, match="冲突|澄清"):
        prepare_kernel_reply(
            session,
            "系统稳定，但另一段记录写着系统不稳定。",
            mode=KernelReplyMode.NATURAL_LANGUAGE,
            coordinator=KernelAgentCoordinator(FakeCompletion()),
        )


def test_kernel_reply_rejects_parameter_with_non_verbatim_source(tmp_path):
    _, state = _kernel_inputs(tmp_path)
    report, state = continue_kernel_app_run(state, action="confirm_task", payload={})
    del report
    session = WorkflowService(tmp_path).read(state["kernel_session_id"])

    class FakeCompletion:
        def __call__(self, request):
            if request.role.value == "diagnosis":
                return {"diagnostic_updates": {}}
            return {
                "parameter_candidates": [
                    {
                        "fact_id": "static_gain",
                        "value": 2.0,
                        "unit": "degC/kW",
                        "source_text": "模型猜测的增益为2",
                    }
                ]
            }

    with pytest.raises(ValueError, match="原文|来源|verbatim"):
        prepare_kernel_reply(
            session,
            "没有提供任何增益数值。",
            mode=KernelReplyMode.NATURAL_LANGUAGE,
            coordinator=KernelAgentCoordinator(FakeCompletion()),
        )


def test_kernel_reply_submission_persists_diagnostics_and_parameters_atomically(
    tmp_path,
):
    _, state = _kernel_inputs(tmp_path)
    _, state = continue_kernel_app_run(state, action="confirm_task", payload={})
    service = WorkflowService(tmp_path)
    session = service.read(state["kernel_session_id"])
    reply = {
        "diagnostic_updates": {
            "open_loop_stability": {
                "status": "known",
                "assessment": "stable",
                "evidence": "系统稳定",
                "confidence": 0.9,
            }
        },
        "parameter_candidates": [
            {
                "fact_id": "static_gain",
                "value": 2.0,
                "unit": "degC/kW",
                "source_text": "静态增益为2 degC/kW",
            }
        ],
    }
    updated = service.submit_reply(
        session.session_id,
        action_id="reply-1",
        revision=session.revision,
        diagnostic_updates=reply["diagnostic_updates"],
        parameter_facts=reply["parameter_candidates"],
        source_text="系统稳定，静态增益为2 degC/kW。",
        input_mode="natural_language",
    )
    assert updated.revision == session.revision + 1
    assert updated.ledger.entry("open_loop_stability").status == "known"
    assert updated.parameter_facts[0]["fact_id"] == "static_gain"
    assert updated.events[-1].event_type == "user_reply_recorded"

    repeated = service.submit_reply(
        session.session_id,
        action_id="reply-1",
        revision=session.revision,
        diagnostic_updates=reply["diagnostic_updates"],
        parameter_facts=reply["parameter_candidates"],
        source_text="系统稳定，静态增益为2 degC/kW。",
        input_mode="natural_language",
    )
    assert len(repeated.events) == len(updated.events)


def test_kernel_reply_submission_rejects_unverified_parameter_without_mutation(
    tmp_path,
):
    _, state = _kernel_inputs(tmp_path)
    _, state = continue_kernel_app_run(state, action="confirm_task", payload={})
    service = WorkflowService(tmp_path)
    session = service.read(state["kernel_session_id"])
    with pytest.raises(ValueError, match="原文|source"):
        service.submit_reply(
            session.session_id,
            action_id="reply-invalid",
            revision=session.revision,
            diagnostic_updates={},
            parameter_facts=[
                {
                    "fact_id": "static_gain",
                    "value": 2,
                    "unit": "degC/kW",
                    "source_text": "模型猜测的增益为2",
                }
            ],
            source_text="没有提供增益。",
            input_mode="natural_language",
        )
    assert service.read(session.session_id).revision == session.revision


def test_kernel_reply_conflicting_diagnostic_requires_clarification(tmp_path):
    _, state = _kernel_inputs(tmp_path)
    _, state = continue_kernel_app_run(state, action="confirm_task", payload={})
    service = WorkflowService(tmp_path)
    session = service.read(state["kernel_session_id"])
    known = service.submit_reply(
        session.session_id,
        action_id="reply-known",
        revision=session.revision,
        diagnostic_updates={
            "open_loop_stability": {
                "status": "known",
                "assessment": "stable",
                "evidence": "系统稳定",
            }
        },
        source_text="系统稳定。",
        input_mode="natural_language",
    )

    with pytest.raises(ValueError, match="冲突|conflict|澄清"):
        service.submit_reply(
            known.session_id,
            action_id="reply-conflict",
            revision=known.revision,
            diagnostic_updates={
                "open_loop_stability": {
                    "status": "known",
                    "assessment": "unstable",
                    "evidence": "系统不稳定",
                }
            },
            source_text="系统不稳定。",
            input_mode="natural_language",
        )

    assert service.read(known.session_id).revision == known.revision


def test_kernel_webui_natural_language_reply_reaches_agents_and_kernel(
    tmp_path, monkeypatch
):
    _, state = _kernel_inputs(tmp_path)
    _, state = continue_kernel_app_run(state, action="confirm_task", payload={})

    class FakeAdapter:
        agent_mode = "multi"
        retriever = None

        def complete_agent(self, request):
            if request.role.value == "critic":
                return {"decision": "pass", "feedback": ""}
            if request.role.value == "diagnosis":
                return {
                    "diagnostic_updates": {
                        "open_loop_stability": {
                            "status": "known",
                            "assessment": "stable",
                            "evidence": "系统稳定",
                        }
                    }
                }
            return {
                "parameter_candidates": [
                    {
                        "fact_id": "static_gain",
                        "value": 2,
                        "unit": "degC/kW",
                        "source_text": "静态增益为2 degC/kW",
                    }
                ]
            }

    monkeypatch.setattr(
        web_service, "_build_app_adapter", lambda *args, **kwargs: FakeAdapter()
    )
    with api_client(tmp_path) as client:
        body = {
            "request_id": str(uuid4()),
            "expected_revision": state["kernel_revision"],
            "action": "answer",
            "input": {
                "text": "系统稳定，静态增益为2 degC/kW。",
                "mode": "natural_language",
            },
            "credentials": {
                "base_url": "https://provider.example/v1",
                "model": "test-model",
                "api_key": "test-key",
            },
        }
        operation = finish(
            client,
            client.post(
                f"/api/v1/tasks/{state['kernel_session_id']}/actions", json=body
            ),
        )
        assert operation["status"] == "completed", operation
        view = client.get(f"/api/v1/tasks/{state['kernel_session_id']}").json()
        report, _ = client.app.state.cache.get(state["kernel_session_id"])
    assert view["revision"] == 3
    assert report["parameter_facts"][0]["fact_id"] == "static_gain"
    assert view["input_contract"]["allowed_modes"]


def test_kernel_webui_duplicate_reply_reuses_committed_action_without_llm(
    tmp_path, monkeypatch
):
    _, state = _kernel_inputs(tmp_path)
    _, state = continue_kernel_app_run(state, action="confirm_task", payload={})
    calls = []

    class FakeAdapter:
        agent_mode = "multi"
        retriever = None

        def complete_agent(self, request):
            calls.append(request.role.value)
            if request.role.value == "critic":
                return {"decision": "pass", "feedback": ""}
            if request.role.value == "modeling":
                return {"parameter_candidates": []}
            return {
                "diagnostic_updates": {
                    "open_loop_stability": {
                        "status": "known",
                        "evidence": "系统稳定",
                    }
                },
                "parameter_candidates": [],
            }

    monkeypatch.setattr(
        web_service, "_build_app_adapter", lambda *args, **kwargs: FakeAdapter()
    )
    with api_client(tmp_path) as client:
        body = {
            "request_id": str(uuid4()),
            "expected_revision": state["kernel_revision"],
            "action": "answer",
            "input": {"text": "系统稳定。", "mode": "natural_language"},
            "credentials": {
                "base_url": "https://provider.example/v1",
                "model": "test-model",
                "api_key": "test-key",
            },
        }
        path = f"/api/v1/tasks/{state['kernel_session_id']}/actions"
        first = finish(client, client.post(path, json=body))
        second = finish(client, client.post(path, json=body))
        assert first["status"] == second["status"] == "completed"
        assert first["operation_id"] == second["operation_id"]
        assert (
            client.get(f"/api/v1/tasks/{state['kernel_session_id']}").json()["revision"]
            == 3
        )
    assert calls == ["diagnosis", "modeling", "critic"]


def test_budget_exhaustion_cannot_be_reinterpreted_as_confirmation(tmp_path):
    _, state = _kernel_inputs(tmp_path)
    service = WorkflowService(tmp_path)
    session = service.read(state["kernel_session_id"])
    exhausted = replace(
        session,
        status="capability_gap",
        pending_actions=({"kind": "budget", "reason": "experiment_budget_exhausted"},),
    )
    exhausted.save(tmp_path / f"{session.session_id}.json")
    with api_client(tmp_path) as client:
        rejected = action(client, state, "confirm_task", confirmed=True)
        assert rejected.status_code == 409
    assert service.read(session.session_id).revision == session.revision


def test_projection_adds_confirmation_for_stored_intake_without_mutating_file(tmp_path):
    service = WorkflowService(tmp_path)
    session = service.start(
        {
            "description": "保持输出稳定",
            "measured_signals": ["output"],
            "control_input": "input",
        }
    )
    old_intake = replace(session, pending_actions=())
    old_intake.save(tmp_path / f"{session.session_id}.json")

    restored = service.read(session.session_id)
    assert restored.pending_actions == ()
    projected = service.project(restored)
    assert projected["pending_actions"][0]["action"] == "confirm_task"
    assert service.read(session.session_id).pending_actions == ()


def test_old_intake_confirmation_can_use_the_projected_web_action(tmp_path):
    service = WorkflowService(tmp_path)
    session = service.start(
        {
            "description": "保持输出稳定",
            "measured_signals": ["output"],
            "control_input": "input",
        }
    )
    old_intake = replace(session, pending_actions=())
    old_intake.save(tmp_path / f"{session.session_id}.json")
    state = {
        "kernel_session_id": session.session_id,
        "kernel_session_dir": str(tmp_path),
        "kernel_revision": session.revision,
        "workflow_version": session.workflow_version,
        "pending_actions": [
            {
                "kind": "budget",
                "action": "confirm_task",
                "reason": "task_boundary_confirmation_required",
            }
        ],
    }

    with api_client(tmp_path) as client:
        rejected = finish(
            client, action(client, state, "confirm_task", confirmed=False)
        )
        assert rejected["status"] == "failed"
        assert service.read(session.session_id).revision == session.revision
        accepted = finish(client, action(client, state, "confirm_task", confirmed=True))
        assert accepted["status"] == "completed"
        result = client.get(f"/api/v1/tasks/{session.session_id}").json()
    assert result["pending_actions"][0]["action"] == "submit_answer"


def test_optional_agent_envelopes_are_bounded_and_canonicalized():
    nested = {
        "diagnosis": {
            "diagnostic_updates": {
                "open_loop_stability": {
                    "status": "known",
                    "evidence": "系统稳定",
                }
            }
        }
    }
    assert set(kernel_replies._diagnostic_updates(nested)) == {"open_loop_stability"}
    repeated = {
        "diagnostic_updates": {
            "diagnostic_updates": {
                "open_loop_stability": {
                    "status": "known",
                    "evidence": "系统稳定",
                }
            }
        }
    }
    assert set(kernel_replies._diagnostic_updates(repeated)) == {"open_loop_stability"}
    modeling = {
        "modeling": {
            "parameter_candidates": [
                {
                    "fact_id": "static_gain",
                    "value": 2,
                    "unit": "degC/kW",
                    "source_text": "静态增益为2 degC/kW",
                }
            ]
        }
    }
    parameters = kernel_replies._parameter_candidates(
        modeling,
        "静态增益为2 degC/kW",
    )
    assert parameters[0]["fact_id"] == "static_gain"

    too_deep = {"diagnosis": {"diagnosis": nested}}
    with pytest.raises(ValueError, match="层级超过 2 层"):
        kernel_replies._diagnostic_updates(too_deep)
    mixed = {
        **nested,
        "open_loop_stability": {"status": "known", "evidence": "系统稳定"},
    }
    with pytest.raises(ValueError, match="混合了包裹字段"):
        kernel_replies._diagnostic_updates(mixed)


def test_builtin_case_enables_only_explicit_optional_fields():
    loaded = case_draft("dc_motor_speed_v1")
    assert loaded["reference_enabled"] is True
    assert loaded["reference"] == 20.0
    assert set(loaded["success_requirement_fields"]) == {
        "final_abs_error_max",
        "overshoot_max",
        "settling_time_max_s",
        "perturbed_success_rate_min",
    }
    assert loaded["perturbed_success_rate_min"] == 0.8
    assert loaded["response_time_preference_enabled"] is True
    assert loaded["response_time_preference_s"] == 2.0
    assert loaded["budget_fields"] == []
    assert loaded["distinct_experiments"] is None
    assert loaded["cumulative_excitation_time_s"] is None


@pytest.mark.parametrize(
    ("overrides", "field"),
    [
        (
            {"response_time_preference_enabled": True, "response_time_preference_s": 0},
            "response_time_preference_s",
        ),
        (
            {"budget_fields": ["distinct_experiments"], "distinct_experiments": 1.5},
            "distinct_experiments",
        ),
        (
            {
                "success_requirement_fields": ["perturbed_success_rate_min"],
                "perturbed_success_rate_min": 1.2,
            },
            "perturbed_success_rate_min",
        ),
    ],
)
def test_enabled_optional_fields_have_friendly_web_validation(overrides, field):
    with pytest.raises(DraftValidationError) as error:
        task_from_draft({**_draft(), **overrides})
    assert field in error.value.errors
    assert error.value.errors[field]


def _draft():
    return {
        **empty_draft(),
        "description": "保持加热器温度",
        "outputs": [["temperature", "degC"]],
        "inputs": [["heater"]],
        "input_unit": "kW",
        "input_min": -1,
        "input_max": 1,
        "state_stop": 12,
    }


def test_kernel_api_contains_no_compatibility_controls(tmp_path):
    with api_client(tmp_path) as client:
        response = client.post(
            "/api/v1/tasks",
            json={
                "request_id": str(uuid4()),
                "draft": _draft(),
                "confirmed": True,
                "use_rag": False,
                "agent_mode": "single",
            },
        )
        assert response.status_code == 422
        schema = client.get("/openapi.json").json()
        assert (
            "agent_mode"
            not in schema["components"]["schemas"]["CreateRequest"]["properties"]
        )
        assert set(dict(TASK_TYPES).values()) == {
            "local_setpoint_hold",
            "transition_then_hold",
            "disturbance_recovery_to_hold",
        }


def test_kernel_api_defaults_to_builtin_rag_without_exposing_an_index_path(tmp_path):
    from cfdc.web.schemas import CreateRequest

    request = CreateRequest(request_id=uuid4(), draft=_draft())
    assert request.use_rag is True
    with api_client(tmp_path) as client:
        config = client.get("/api/v1/config").json()
        assert "index_dir" not in json.dumps(config)
        response = client.post(
            "/api/v1/tasks",
            json={"request_id": str(uuid4()), "draft": _draft(), "confirmed": True},
        )
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "rag_not_ready"


def test_kernel_api_pins_the_server_prepared_rag_snapshot(tmp_path):
    from cfdc.rag import build_index
    from cfdc.web.schemas import RAGStatus

    index = build_index(None, tmp_path / "rag", encoder=_WebRAGEncoder())
    prepared = SimpleNamespace(
        index_dir=index.snapshot.parent, snapshot=index.index_snapshot
    )
    with api_client(tmp_path / "sessions") as client:
        runtime = client.app.state.rag
        runtime.prepared = prepared
        runtime._status = RAGStatus(
            status="ready", message="ready", snapshot=prepared.snapshot
        )
        task_id = create(client, draft=_draft(), use_rag=True)
        report, _ = client.app.state.cache.get(task_id)
        assert report["agent_config"]["rag_enabled"] is True
        assert report["rag_snapshot"] == prepared.snapshot
        assert (
            WorkflowService(tmp_path / "sessions").read(task_id).rag_snapshot
            == prepared.snapshot
        )
        assert report["agent_config"]["rag_index_dir"] == str(prepared.index_dir)
        disabled = create(client, draft=_draft(), use_rag=False)
        report, _ = client.app.state.cache.get(disabled)
        assert report["agent_config"]["rag_enabled"] is False
        assert report["rag_snapshot"] is None
        assert (
            WorkflowService(tmp_path / "sessions").read(disabled).rag_snapshot is None
        )
        assert report["agent_config"].get("rag_index_dir") is None


def test_kernel_api_creation_keeps_disabled_optional_fields_absent(tmp_path):
    with api_client(tmp_path) as client:
        task_id = create(client, draft=_draft())
        report, _ = client.app.state.cache.get(task_id)
        assert report["workflow_version"].startswith("cfdc-v6-kernel")
        for field in (
            "output_min",
            "output_max",
            "reference",
            "response_time_preference_s",
        ):
            assert report["task"][field] is None
        assert "final_abs_error_max" not in report["task"]["success_requirements"]
        assert report["status"] == "diagnostic"
        assert report["revision"] == 2


def test_kernel_api_natural_language_reply_chain(tmp_path, monkeypatch):
    class FakeAdapter:
        agent_mode = "multi"
        retriever = None

        def complete_agent(self, request):
            if request.role.value == "critic":
                return {"decision": "pass", "feedback": ""}
            if request.role.value == "diagnosis":
                return {
                    "diagnosis": {
                        "diagnostic_updates": {
                            "open_loop_stability": {
                                "status": "known",
                                "evidence": "系统稳定",
                            }
                        }
                    }
                }
            return {
                "modeling": {
                    "parameter_candidates": [
                        {
                            "fact_id": "static_gain",
                            "value": 2,
                            "unit": "degC/kW",
                            "source_text": "静态增益为2 degC/kW",
                        }
                    ]
                }
            }

    monkeypatch.setattr(
        web_service, "_build_app_adapter", lambda *args, **kwargs: FakeAdapter()
    )
    with api_client(tmp_path) as client:
        task_id = create(client, draft=_draft())
        response = client.post(
            f"/api/v1/tasks/{task_id}/actions",
            json={
                "request_id": str(uuid4()),
                "expected_revision": 2,
                "action": "answer",
                "input": {"text": "系统稳定，静态增益为2 degC/kW。"},
                "credentials": {
                    "base_url": "https://provider.example/v1",
                    "model": "test-model",
                    "api_key": "test-key",
                },
            },
        )
        operation = finish(client, response)
        assert operation["status"] == "completed", operation
        report, _ = client.app.state.cache.get(task_id)
        assert report["parameter_facts"][0]["fact_id"] == "static_gain"
        assert report["agent_records"]


def test_kernel_api_flow_reaches_result_with_ollama_shaped_replies(
    tmp_path, monkeypatch
):
    evidence = {
        "open_loop_stability": ("开环稳定", "stable"),
        "nonminimum_phase": ("没有反向响应", "minimum_phase"),
        "significant_delay": ("纯延迟不显著", "not_significant"),
        "relative_degree": ("相对阶数较低", "low"),
        "sensing_actuation_adequacy": ("传感器和执行器足够", "adequate"),
        "nonlinearity_strength": ("工作区内非线性较弱", "weak"),
        "coupling_underactuation": ("对象是单输入单输出", "siso"),
        "uncertainty_variation": ("实验间变化较小", "small"),
    }

    class FakeOllamaAdapter:
        agent_mode = "multi"
        retriever = None

        def complete_agent(self, request):
            if request.role.value == "critic":
                return {"decision": "pass", "feedback": ""}
            if request.role.value == "diagnosis":
                return {
                    "diagnosis": {
                        "diagnostic_updates": {
                            key: {
                                "status": "known",
                                "assessment": assessment,
                                "evidence": excerpt,
                                "confidence": 0.95,
                            }
                            for key, (excerpt, assessment) in evidence.items()
                        }
                    }
                }
            return {"modeling": {"parameter_candidates": []}}

    monkeypatch.setattr(
        web_service, "_build_app_adapter", lambda *args, **kwargs: FakeOllamaAdapter()
    )
    with api_client(tmp_path) as client:
        task_id = create(
            client, draft=case_draft("dc_motor_speed_v1"), case_id="dc_motor_speed_v1"
        )
        report, _ = client.app.state.cache.get(task_id)
    assert report["status"] == "tuning_eligible"
    assert report["features"]["feature_version"] == "cfdc-features/v2"
    assert report["route"]["profile_id"] == "first_order_lag"
    assert report["route"]["controller_contract_id"] == "PI"
    assert report["controller"]["ir"]["family"] == "PI"
    assert report["qualification"]["status"] == "offline_qualified"
    assert report["freeze"]["freeze_version"] == "cfdc-freeze/v2.0"
    assert report["evaluation"]["status"] == "performance_not_met"
    assert report["evaluation"]["wilson_lower_bound_95"] == 0.0
