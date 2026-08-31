from __future__ import annotations

import json
import os
from dataclasses import replace

import gradio as gr
import pytest

from cfdc.kernel import WorkflowService
from cfdc.kernel import replies as kernel_replies
from cfdc.kernel.agents import KernelAgentCoordinator
from cfdc.kernel.replies import (
    KernelReplyMode,
    build_kernel_input_contract,
    prepare_kernel_reply,
)
from cfdc.web import service as web_service
from cfdc.web import ui as web_ui
from cfdc.web.service import (
    continue_kernel_app_run,
    prepare_kernel_reply_for_ui,
    start_kernel_app_run,
    start_kernel_case_run,
)
from cfdc.web.ui import (
    _kernel_outputs,
    _reply_mode_update,
    submit_measurement_from_ui,
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
    ui_outputs = _kernel_outputs(report, state)
    assert ui_outputs[18]["visible"] is True
    assert "确认" in ui_outputs[18]["value"]
    assert ui_outputs[19]["visible"] is True
    assert ui_outputs[17]["value"] == "natural_language"
    assert "choices" not in ui_outputs[17]


@pytest.mark.parametrize(
    ("allowed_modes", "visible", "value", "interactive"),
    [
        ([], False, "natural_language", False),
        (["natural_language"], True, "natural_language", False),
        (["json"], True, "json", False),
        (["natural_language", "json"], True, "natural_language", True),
    ],
)
def test_reply_mode_updates_keep_static_component_choices(
    allowed_modes, visible, value, interactive
):
    update = _reply_mode_update({"allowed_modes": allowed_modes})

    assert update["visible"] is visible
    assert update["value"] == value
    assert update["interactive"] is interactive
    assert "choices" not in update


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
def test_web_task_contract_rejects_missing_or_invalid_boundaries(tmp_path, update, message):
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
    report, state = _kernel_inputs(tmp_path)
    report["features"] = {
        "features": {"static_gain": {"value": 2.0, "unit": "unit/unit"}},
        "quality": {"status": "pass"},
    }
    report["controller"] = {
        "ir": {"family": "PI", "parameters": {"kp": 1.0, "ki": 0.1}},
        "validation": {"eligible": True},
    }

    ui_outputs = _kernel_outputs(report, state)

    assert any(row[0] == "static_gain" for row in ui_outputs[10])
    assert any(row[0] == "family" for row in ui_outputs[11])
    assert all(row[0] != "validation" for row in ui_outputs[10])


def test_empty_page_actions_are_reloaded_from_kernel_session(tmp_path):
    report, state = _kernel_inputs(tmp_path)
    del report
    state = {**state, "pending_actions": []}

    with pytest.raises(gr.Error, match="确认软件试验边界"):
        submit_measurement_from_ui(state, "", False, "", "", "")


def test_kernel_page_revision_and_action_id_are_stable_and_payload_cannot_override(tmp_path):
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


def test_webui_rejects_non_kernel_report():
    with pytest.raises(ValueError, match="只接受 CFDC Kernel"):
        _kernel_outputs({"workflow_version": "unknown/v9"}, {})


def test_kernel_confirmation_button_does_not_require_empty_json(tmp_path):
    _, state = _kernel_inputs(tmp_path)

    with pytest.raises(gr.Error, match="确认软件试验边界"):
        submit_measurement_from_ui(state, "", False, "", "", "")

    ui_outputs = submit_measurement_from_ui(
        state,
        "",
        True,
        "",
        "",
        "",
    )
    assert "diagnostic" in ui_outputs[1]
    assert ui_outputs[0]["pending_actions"][0]["action"] == "submit_answer"


def test_empty_kernel_reply_is_rejected_before_llm_configuration(tmp_path):
    _, state = _kernel_inputs(tmp_path)
    _, state = continue_kernel_app_run(state, action="confirm_task", payload={})

    with pytest.raises(gr.Error, match="填写回复内容"):
        submit_measurement_from_ui(state, "", False, "", "", "", "natural_language")


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
    assert prepared["diagnostic_updates"]["open_loop_stability"]["assessment"] == "stable"
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
    assert prepared["diagnostic_updates"]["open_loop_stability"]["evidence"] == "系统稳定"


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
def test_live_ollama_dc_motor_flow_reaches_performance_met(tmp_path):
    base_url = os.getenv("CFDC_OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1")
    model = os.getenv("CFDC_OLLAMA_MODEL", "gemma3:4b")
    api_key = os.getenv("CFDC_OLLAMA_API_KEY", "ollama")
    report, state = start_kernel_case_run(
        "dc_motor_speed_v1",
        session_dir=tmp_path,
        use_rag=False,
        llm_configured=True,
    )
    report, state = continue_kernel_app_run(
        state,
        action="confirm_task",
        payload={},
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
    report, _ = continue_kernel_app_run(
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

    assert report["status"] == "performance_met"
    assert report["route"]["class"] == "class_i_first_order_lag"
    assert report["route"]["profile_id"] == "first_order_lag"
    assert report["controller"]["ir"]["family"] == "PI"
    assert report["qualification"]["status"] == "offline_qualified"
    assert report["evaluation"]["wilson_lower_bound_95"] >= 0.8
    assert {record["role"] for record in report["agent_records"]} >= {
        "diagnosis",
        "modeling",
        "critic",
    }
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


def test_kernel_reply_submission_persists_diagnostics_and_parameters_atomically(tmp_path):
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


def test_kernel_reply_submission_rejects_unverified_parameter_without_mutation(tmp_path):
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


def test_kernel_webui_natural_language_reply_reaches_agents_and_kernel(tmp_path, monkeypatch):
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

    monkeypatch.setattr(web_service, "_build_app_adapter", lambda *args, **kwargs: FakeAdapter())
    outputs = submit_measurement_from_ui(
        state,
        "系统稳定，静态增益为2 degC/kW。",
        False,
        "https://provider.example/v1",
        "test-model",
        "test-key",
        "natural_language",
    )
    assert outputs[0]["kernel_revision"] == 3
    assert outputs[15]["parameter_facts"][0]["fact_id"] == "static_gain"
    assert outputs[16]["visible"] is True


def test_kernel_webui_duplicate_reply_reuses_committed_action_without_llm(tmp_path, monkeypatch):
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

    monkeypatch.setattr(web_service, "_build_app_adapter", lambda *args, **kwargs: FakeAdapter())
    text = "系统稳定。"
    first = submit_measurement_from_ui(
        state, text, False, "https://provider.example/v1", "test-model", "test-key", "natural_language"
    )
    second = submit_measurement_from_ui(
        state, text, False, "https://provider.example/v1", "test-model", "test-key", "natural_language"
    )

    assert first[0]["kernel_revision"] == second[0]["kernel_revision"] == 3
    assert calls == ["diagnosis", "modeling", "critic"]


def test_budget_exhaustion_cannot_be_reinterpreted_as_confirmation(tmp_path):
    _, state = _kernel_inputs(tmp_path)
    exhausted = {
        **state,
        "pending_actions": [{"kind": "budget", "reason": "experiment_budget_exhausted"}],
    }

    with pytest.raises(gr.Error, match="没有可用的 WebUI 入口|待处理动作"):
        submit_measurement_from_ui(exhausted, "", True, "", "", "")


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

    with pytest.raises(gr.Error, match="确认软件试验边界"):
        submit_measurement_from_ui(state, "", False, "", "", "")

    result = submit_measurement_from_ui(state, "", True, "", "", "")
    assert result[0]["pending_actions"][0]["action"] == "submit_answer"


def _fn_index(app, name, *, input_count=None):
    return next(
        index
        for index, function in app.fns.items()
        if function.name == name
        and (input_count is None or len(function.inputs) == input_count)
    )


_RUN_INPUT_NAMES = (
    "description", "task_type", "measured_signals", "control_inputs",
    "reference_enabled", "reference", "input_min", "input_max",
    "output_bounds_enabled", "output_min", "output_max", "state_stop",
    "initial_region", "goal_region", "disturbance_event",
    "recovery_start_condition", "disturbance_hold_region", "base_url", "model",
    "api_key", "rag_enabled", "rag_index_dir", "provider_case_id",
    "signal_units_json", "input_unit", "success_requirement_fields",
    "final_abs_error_max", "overshoot_max", "settling_time_max_s",
    "perturbed_success_rate_min", "hold_duration_min_s",
    "response_time_preference_enabled", "response_time_preference_s",
    "budget_fields", "distinct_experiments", "cumulative_excitation_time_s",
    "initial_output_value_enabled", "initial_output_value", "intermediate_targets",
)


def _run_inputs(**overrides):
    values = {
        "description": "保持加热器温度",
        "task_type": "local_setpoint_hold",
        "measured_signals": "temperature",
        "control_inputs": "heater",
        "reference_enabled": False,
        "reference": 0,
        "input_min": -1,
        "input_max": 1,
        "output_bounds_enabled": False,
        "output_min": 0,
        "output_max": 0,
        "state_stop": 12,
        "initial_region": "",
        "goal_region": "",
        "disturbance_event": "",
        "recovery_start_condition": "",
        "disturbance_hold_region": "",
        "base_url": "",
        "model": "",
        "api_key": "",
        "rag_enabled": False,
        "rag_index_dir": "",
        "provider_case_id": None,
        "signal_units_json": "",
        "input_unit": "",
        "success_requirement_fields": [],
        "final_abs_error_max": 0,
        "overshoot_max": 0,
        "settling_time_max_s": 0,
        "perturbed_success_rate_min": 0.8,
        "hold_duration_min_s": 0,
        "response_time_preference_enabled": False,
        "response_time_preference_s": 0,
        "budget_fields": [],
        "distinct_experiments": 0,
        "cumulative_excitation_time_s": 0,
        "initial_output_value_enabled": False,
        "initial_output_value": 0,
        "intermediate_targets": "",
    }
    values.update(overrides)
    return [values[name] for name in _RUN_INPUT_NAMES]


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
    loaded = web_ui.load_case_into_form("case-01")

    assert len(loaded) == 33
    assert loaded[4] is True
    assert loaded[5]["value"] == 20.0
    assert set(loaded[19]) == {
        "final_abs_error_max",
        "overshoot_max",
        "settling_time_max_s",
        "perturbed_success_rate_min",
    }
    assert loaded[23]["value"] == 0.8
    assert loaded[25] is True
    assert loaded[26]["value"] == 2.0
    assert loaded[27] == []
    assert loaded[28]["value"] is None
    assert loaded[29]["value"] is None


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        (
            {
                "response_time_preference_enabled": True,
                "response_time_preference_s": 0,
            },
            "响应时间偏好必须大于 0",
        ),
        (
            {
                "budget_fields": ["distinct_experiments"],
                "distinct_experiments": 1.5,
            },
            "不同实验预算必须是大于等于 1 的整数",
        ),
        (
            {
                "success_requirement_fields": ["perturbed_success_rate_min"],
                "perturbed_success_rate_min": 1.2,
            },
            "扰动重复成功率下限必须在 0 到 1 之间",
        ),
    ],
)
def test_enabled_optional_fields_have_friendly_web_validation(overrides, message):
    with pytest.raises(gr.Error, match=message):
        web_ui.run_from_ui(*_run_inputs(**overrides))


def test_kernel_webui_component_tree_contains_no_compatibility_controls():
    rendered = json.dumps(web_ui.build_app().config, ensure_ascii=False, default=str)

    for forbidden in (
        "工作流版本",
        "Agent 模式",
        "single",
        "legacy",
        "linked-tuning-panel",
        "迁移版",
        "旧版",
        "第五步",
    ):
        assert forbidden not in rendered
    assert "local_setpoint_hold" in rendered
    assert "disturbance_recovery_to_hold" in rendered
    assert "高级 JSON" in rendered


@pytest.mark.anyio
async def test_kernel_gradio_process_api_accepts_stale_json_on_confirmation(
    tmp_path, monkeypatch
):
    original_start = web_service.start_kernel_app_run

    def start_in_tmp(task, **kwargs):
        kwargs["session_dir"] = tmp_path
        return original_start(task, **kwargs)

    monkeypatch.setattr(web_ui, "start_kernel_app_run", start_in_tmp)
    app = web_ui.build_app()
    from gradio.blocks import SessionState

    session_state = SessionState(app)
    run_result = await app.process_api(
        _fn_index(app, "run_from_ui", input_count=39),
        _run_inputs(),
        state=session_state,
        session_hash="kernel-process-api",
        simple_format=True,
        explicit_call=True,
    )
    assert len(run_result["data"]) == 27
    raw_report = run_result["data"][15].root
    assert raw_report["workflow_version"].startswith("cfdc-v6-kernel")
    assert raw_report["task"]["output_min"] is None
    assert raw_report["task"]["output_max"] is None
    assert raw_report["task"]["reference"] is None
    assert raw_report["task"]["response_time_preference_s"] is None
    assert "final_abs_error_max" not in raw_report["task"]["success_requirements"]
    assert run_result["data"][17]["value"] == "natural_language"
    assert "choices" not in run_result["data"][17]

    confirm_result = await app.process_api(
        _fn_index(app, "submit_measurement_from_ui"),
        [run_result["data"][0], "", True, "", "", "", "json"],
        state=session_state,
        session_hash="kernel-process-api",
        simple_format=True,
        explicit_call=True,
    )
    assert "diagnostic" in confirm_result["data"][1]
    assert confirm_result["data"][15].root["status"] == "diagnostic"
    assert WorkflowService(tmp_path).read(raw_report["session_id"]).revision == 2


@pytest.mark.anyio
async def test_kernel_gradio_process_api_natural_language_reply_chain(tmp_path, monkeypatch):
    original_start = web_service.start_kernel_app_run

    def start_in_tmp(task, **kwargs):
        kwargs["session_dir"] = tmp_path
        return original_start(task, **kwargs)

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

    monkeypatch.setattr(web_ui, "start_kernel_app_run", start_in_tmp)
    monkeypatch.setattr(web_service, "_build_app_adapter", lambda *args, **kwargs: FakeAdapter())
    app = web_ui.build_app()
    from gradio.blocks import SessionState

    session_state = SessionState(app)
    run_result = await app.process_api(
        _fn_index(app, "run_from_ui", input_count=39),
        _run_inputs(),
        state=session_state,
        session_hash="kernel-process-api-reply",
        simple_format=True,
        explicit_call=True,
    )
    confirm_result = await app.process_api(
        _fn_index(app, "submit_measurement_from_ui"),
        [run_result["data"][0], "", True, "", "", "", "natural_language"],
        state=session_state,
        session_hash="kernel-process-api-reply",
        simple_format=True,
        explicit_call=True,
    )
    confirmed_page_state = confirm_result["data"][0]
    reply_result = await app.process_api(
        _fn_index(app, "submit_measurement_from_ui"),
        [
            confirmed_page_state,
            "系统稳定，静态增益为2 degC/kW。",
            False,
            "https://provider.example/v1",
            "test-model",
            "test-key",
            "natural_language",
        ],
        state=session_state,
        session_hash="kernel-process-api-reply",
        simple_format=True,
        explicit_call=True,
    )

    assert reply_result["data"][15].root["parameter_facts"][0]["fact_id"] == "static_gain"
    assert reply_result["data"][15].root["agent_records"]


@pytest.mark.anyio
async def test_visible_gradio_flow_reaches_kernel_result_with_ollama_shaped_replies(
    tmp_path,
    monkeypatch,
):
    original_start = web_service.start_kernel_app_run

    def start_in_tmp(task, **kwargs):
        kwargs["session_dir"] = tmp_path
        return original_start(task, **kwargs)

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

    monkeypatch.setattr(web_ui, "start_kernel_app_run", start_in_tmp)
    monkeypatch.setattr(
        web_service,
        "_build_app_adapter",
        lambda *args, **kwargs: FakeOllamaAdapter(),
    )
    app = web_ui.build_app()
    from gradio.blocks import SessionState

    session_state = SessionState(app)
    run_result = await app.process_api(
        _fn_index(app, "run_from_ui", input_count=39),
        _run_inputs(
            description=(
                "一台实验室直流电机工作在空载附近。我可以改变电枢电压并记录转轴角速度，"
                "目标是让转速达到小幅目标并保持。"
            ),
            measured_signals="转轴角速度_rad_s",
            control_inputs="电枢电压_V",
            reference_enabled=True,
            reference=20,
            input_min=-6,
            input_max=6,
            state_stop=60,
            provider_case_id="case-01",
            success_requirement_fields=[
                "final_abs_error_max",
                "overshoot_max",
                "settling_time_max_s",
                "perturbed_success_rate_min",
            ],
            final_abs_error_max=1.5,
            overshoot_max=4,
            settling_time_max_s=3,
            perturbed_success_rate_min=0.8,
            response_time_preference_enabled=True,
            response_time_preference_s=2,
        ),
        state=session_state,
        session_hash="kernel-visible-full-flow",
        simple_format=True,
        explicit_call=True,
    )
    confirm_result = await app.process_api(
        _fn_index(app, "submit_guided_action_from_ui", input_count=12),
        [
            run_result["data"][0], "", True, "", "", "", "json",
            "accepted", [], "", [], False,
        ],
        state=session_state,
        session_hash="kernel-visible-full-flow",
        simple_format=True,
        explicit_call=True,
    )
    source_text = "；".join(excerpt for excerpt, _ in evidence.values())
    result = await app.process_api(
        _fn_index(app, "submit_guided_action_from_ui", input_count=12),
        [
            confirm_result["data"][0], source_text, False,
            "http://127.0.0.1:11434/v1", "gemma3:4b", "ollama",
            "natural_language", "accepted", [], "", [], False,
        ],
        state=session_state,
        session_hash="kernel-visible-full-flow",
        simple_format=True,
        explicit_call=True,
    )

    report = result["data"][15].root
    assert report["status"] == "performance_met"
    assert report["features"]["feature_version"] == "cfdc-features/v1"
    assert report["route"]["class"] == "class_i_first_order_lag"
    assert report["route"]["profile_id"] == "first_order_lag"
    assert report["controller"]["ir"]["family"] == "PI"
    assert report["qualification"]["status"] == "offline_qualified"
    assert report["freeze"]["freeze_version"] == "cfdc-freeze/v1.0"
    assert report["evaluation"]["wilson_lower_bound_95"] >= 0.8
    assert {record["role"] for record in report["agent_records"]} >= {
        "diagnosis",
        "modeling",
        "critic",
    }
