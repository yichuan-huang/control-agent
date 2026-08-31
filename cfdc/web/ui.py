from __future__ import annotations

import html
import json
import os
from collections.abc import Mapping
from typing import Any

import gradio as gr
import plotly.graph_objects as go

from cfdc.kernel.cases import public_case_catalog, public_training_case
from cfdc.web.service import (
    KERNEL_STAGE_LABELS,
    continue_kernel_app_run,
    export_kernel_app_artifact,
    export_kernel_app_bundle,
    import_v3_app_run,
    load_kernel_app_run,
    parse_names,
    prepare_kernel_reply_for_ui,
    start_kernel_app_run,
    validate_kernel_artifact,
)

_MUTATION_OPTIONS = {
    "api_visibility": "private",
    "concurrency_id": "cfdc-web-kernel",
    "concurrency_limit": 1,
    "trigger_mode": "once",
}

_REPLY_CHOICES = [
    ("自然语言", "natural_language"),
    ("高级 JSON", "json"),
]

_SUCCESS_REQUIREMENT_CHOICES = [
    ("最大终值绝对误差", "final_abs_error_max"),
    ("最大超调", "overshoot_max"),
    ("最大调节时间", "settling_time_max_s"),
    ("最短保持时间", "hold_duration_min_s"),
    ("扰动重复成功率", "perturbed_success_rate_min"),
]

_BUDGET_FIELD_CHOICES = [
    ("不同实验次数", "distinct_experiments"),
    ("累计激励时间", "cumulative_excitation_time_s"),
]

_ACTION_ALIASES = {
    "submit_answer": "answer",
    "resolve": "answer",
    "submit_evidence": "evidence",
    "submit_features": "features",
    "submit_controller": "controller",
    "freeze_controller": "freeze",
    "record_evaluation": "evaluation",
    "replay_evaluation": "replay",
    "record_confirmation": "confirmation",
    "record_fresh_confirmation": "confirmation",
}

_TERMINAL_STATES = {"performance_met", "capability_gap", "cancelled"}
_WEB_CASE_IDS = {
    f"case-{index:02d}": case_id
    for index, case_id in enumerate(public_case_catalog(), 1)
}


def _resolve_case_id(value: Any) -> str:
    raw = str(value or "").strip()
    return _WEB_CASE_IDS.get(raw, raw)

LICENSE_NOTICE = (
    "Copyright (C) 2026 Yichuan Huang · "
    "[GNU AGPL v3.0 only](https://www.gnu.org/licenses/agpl-3.0.en.html) · "
    "[Source code](https://github.com/yichuan-huang/control-agent)"
)

CSS = """
.gradio-container { max-width: 1540px !important; }
#app-title h1 { font-size: 28px; margin-bottom: 4px; letter-spacing: 0; }
#run-status { border-left: 4px solid #1677ff; padding: 2px 0 2px 14px; }
.stage-table table { font-size: 13px; }
.stage-table td, .stage-table th { white-space: normal !important; }
.primary-run { min-height: 46px; }
.flow-strip { display: grid; grid-template-columns: repeat(9, minmax(108px, 1fr)); gap: 6px; margin: 4px 0 12px; }
.flow-step { min-height: 68px; border: 1px solid #d8dee8; border-radius: 6px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 5px; background: #f7f9fc; color: #687386; }
.flow-step span { width: 26px; height: 26px; border-radius: 50%; display: grid; place-items: center; background: #dfe5ee; font-weight: 700; }
.flow-step small { font-size: 12px; text-align: center; }
.flow-step.done { background: #eef9f2; border-color: #9cd3ae; color: #196c39; }
.flow-step.done span { background: #258a4b; color: white; }
.task-contract-grid { border-top: 1px solid #e3e8ef; padding-top: 12px; margin-top: 4px; }
.kernel-plot { min-height: 310px; }
@media (max-width: 900px) {
  .flow-strip { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}
"""


def _display_value(value: object) -> object:
    if value is None:
        return "未知"
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return value


def _mapping_rows(value: Any) -> list[list[object]]:
    if not isinstance(value, Mapping):
        return []
    return [[str(key), _display_value(item)] for key, item in value.items()]


def _protocol_figure(report: Mapping[str, Any]) -> go.Figure:
    figure = go.Figure()
    protocols = report.get("protocols") or []
    if protocols and isinstance(protocols[-1], Mapping):
        cursor = 0.0
        x = [0.0]
        y = []
        for segment in protocols[-1].get("segments", ()):
            if not isinstance(segment, Mapping):
                continue
            value = float(segment.get("input_value", 0.0))
            duration = float(segment.get("duration_s", 0.0))
            if not y:
                y.append(value)
            else:
                x.append(cursor)
                y.append(value)
            cursor += duration
            x.append(cursor)
            y.append(value)
        if x and len(x) == len(y):
            figure.add_scatter(x=x, y=y, mode="lines", line_shape="hv", name="input")
    figure.update_layout(
        height=310,
        margin={"l": 42, "r": 18, "t": 36, "b": 42},
        title="实验协议",
        xaxis_title="time (s)",
    )
    return figure


def _trace_figure(report: Mapping[str, Any]) -> go.Figure:
    figure = go.Figure()
    for evidence in report.get("evidence") or ():
        if not isinstance(evidence, Mapping) or not isinstance(evidence.get("trace"), Mapping):
            continue
        trace = evidence["trace"]
        time_s = trace.get("time_s")
        signals = trace.get("signals")
        if not isinstance(time_s, list) or not isinstance(signals, Mapping):
            continue
        for name, values in signals.items():
            if isinstance(values, list) and len(values) == len(time_s):
                figure.add_scatter(x=time_s, y=values, mode="lines", name=f"{evidence.get('trial_id')} · {name}")
    figure.update_layout(
        height=310,
        margin={"l": 42, "r": 18, "t": 36, "b": 42},
        title="公开 Trace",
        xaxis_title="time (s)",
    )
    return figure


def _evaluation_figure(report: Mapping[str, Any]) -> go.Figure:
    figure = go.Figure()
    evaluation = report.get("evaluation")
    if isinstance(evaluation, Mapping):
        rate = float(evaluation.get("success_rate") or 0.0)
        wilson = float(evaluation.get("wilson_lower_bound_95") or 0.0)
        minimum = evaluation.get("performance_gate", {}).get("success_rate_min") if isinstance(evaluation.get("performance_gate"), Mapping) else None
        labels = ["success rate", "Wilson lower 95%"]
        values = [rate, wilson]
        if minimum is not None:
            labels.append("required")
            values.append(float(minimum))
        figure.add_bar(x=labels, y=values, marker_color=["#1677ff", "#258a4b", "#b54708"][: len(values)])
    figure.update_layout(
        height=310,
        margin={"l": 42, "r": 18, "t": 36, "b": 42},
        title="重复试次置信结论",
        yaxis_range=[0, 1],
    )
    return figure


def _artifact_download(report: Mapping[str, Any]) -> Any:
    handoffs = report.get("operator_handoffs") or []
    if handoffs and isinstance(handoffs[-1], Mapping) and handoffs[-1].get("bundle_path"):
        return gr.update(value=handoffs[-1]["bundle_path"], visible=True)
    return gr.update(value=None, visible=False)


def _feature_rows(artifact: Any) -> list[list[object]]:
    if not isinstance(artifact, Mapping):
        return []
    values = artifact.get("features", artifact)
    if not isinstance(values, Mapping):
        return []
    rows: list[list[object]] = []
    for feature_id, raw in values.items():
        item = raw if isinstance(raw, Mapping) else {"value": raw}
        rows.append(
            [
                str(feature_id),
                _display_value(item.get("value")),
                str(item.get("unit") or "未知"),
                _display_value(item.get("confidence_interval")),
                _display_value(item.get("confidence")),
                str(item.get("derivation") or "未知"),
            ]
        )
    return rows


def _controller_rows(artifact: Any) -> list[list[object]]:
    if not isinstance(artifact, Mapping):
        return []
    value = artifact.get("ir") if isinstance(artifact.get("ir"), Mapping) else artifact
    rows: list[list[object]] = []
    for key in (
        "family",
        "measured_signals",
        "control_inputs",
        "output_bounds",
        "integral_handling",
        "stop_conditions",
        "ir_version",
    ):
        if key in value:
            rows.append([key, _display_value(value.get(key))])
    parameters = value.get("parameters")
    if isinstance(parameters, Mapping):
        rows.extend(
            [[str(key), _display_value(item)] for key, item in parameters.items()]
        )
    return rows


def _evidence_rows(report: Mapping[str, Any]) -> list[list[object]]:
    rows: list[list[object]] = []
    for index, item in enumerate(report.get("evidence") or (), 1):
        if not isinstance(item, Mapping):
            continue
        trace = item.get("trace") if isinstance(item.get("trace"), Mapping) else {}
        rows.append(
            [
                index,
                item.get("operation") or item.get("kind") or "公开证据",
                item.get("trial_id") or item.get("evidence_id") or "未知",
                _display_value(item.get("feature_ids")),
                trace.get("sample_count") or "未知",
                _display_value(
                    trace.get("outputs")
                    or trace.get("signals")
                    or item.get("signal_units")
                ),
            ]
        )
    return rows


def _diagnosis_rows(report: Mapping[str, Any]) -> tuple[list[list[object]], list[list[object]]]:
    diagnostic = report.get("diagnostic")
    diagnostic = diagnostic if isinstance(diagnostic, Mapping) else {}
    entries = diagnostic.get("entries")
    entries = entries if isinstance(entries, list) else []
    diagnosis = [
        [
            item.get("id", ""),
            item.get("assessment") or item.get("status", "unknown"),
            _display_value(item.get("confidence")),
            item.get("evidence", "") or "未知",
        ]
        for item in entries
        if isinstance(item, Mapping)
    ]
    checklist = [
        [
            item.get("id", ""),
            item.get("status", "unknown"),
            item.get("evidence", "") or "未知",
        ]
        for item in entries
        if isinstance(item, Mapping)
    ]
    return diagnosis, checklist


def _progress_html(report: Mapping[str, Any]) -> str:
    status = str(report.get("status") or "intake")
    diagnostic = report.get("diagnostic")
    diagnostic = diagnostic if isinstance(diagnostic, Mapping) else {}
    readiness = diagnostic.get("readiness")
    readiness = readiness if isinstance(readiness, Mapping) else {}
    done = {
        "任务": bool(report.get("session_id")),
        "诊断": readiness.get("status") == "ready",
        "取证": bool(report.get("evidence")),
        "路线／特征": bool(report.get("route") or report.get("features")),
        "控制器": bool(report.get("controller")),
        "冻结": bool(report.get("freeze")),
        "评价": bool(report.get("evaluation")),
        "调优／确认": bool(report.get("tuning")),
        "结果": status in _TERMINAL_STATES,
    }
    return "<div class='flow-strip'>" + "".join(
        f'<div class="flow-step {"done" if done.get(label, False) else ""}">'
        f"<span>{index}</span><small>{html.escape(label)}</small></div>"
        for index, label in enumerate(KERNEL_STAGE_LABELS, 1)
    ) + "</div>"


def _summary_html(report: Mapping[str, Any]) -> str:
    task = report.get("task") if isinstance(report.get("task"), Mapping) else {}
    session_id = html.escape(str(report.get("session_id") or "未知"))
    status = html.escape(str(report.get("status") or "intake"))
    task_type = html.escape(str(task.get("task_type") or "未知"))
    signals = html.escape(", ".join(str(item) for item in task.get("measured_signals", ())))
    inputs = html.escape(", ".join(str(item) for item in task.get("control_inputs", ())))
    return (
        f"<p><strong>CFDC Kernel</strong> · {session_id} · revision "
        f"{int(report.get('revision') or 0)} · {status}</p>"
        f"<p>任务：{task_type} · 观测输出：{signals or '未知'} · "
        f"控制输入：{inputs or '未知'}</p>"
    )


def _action_label(action: str) -> str:
    return {
        "confirm_task": "确认软件试验边界与预算",
        "submit_answer": "提交诊断与参数回复",
        "answer": "提交诊断与参数回复",
        "relevance": "提交不相关声明",
        "advance": "继续到下一阶段",
        "evidence": "提交公开证据",
        "phase": "提交阶段结果",
        "features": "提交核心特征",
        "controller": "提交控制器候选",
        "freeze": "冻结控制器",
        "evaluation": "提交评价结果",
        "replay": "重新计算已记录评价",
        "confirmation": "提交确认结果",
        "record_operator_report": "提交操作员报告",
        "ingest_upload": "校验并提交实验数据",
        "prepare_operator_handoff": "生成操作员交接包",
        "derive_features": "自动提取控制特征",
        "synthesize_controller": "生成控制器候选",
        "qualify_controller": "执行离线资格审查",
        "run_provider": "运行隔离取证",
        "run_evaluation": "运行独立评价",
        "run_feedback_iteration": "运行有界调优",
        "confirm_result": "执行全新确认",
        "cancel": "取消任务",
    }.get(action, "提交当前动作")


def _reply_mode_update(input_contract: Mapping[str, Any]) -> dict[str, Any]:
    allowed = [str(item) for item in input_contract.get("allowed_modes", ())]
    if allowed == ["json"]:
        return gr.update(visible=True, value="json", interactive=False)
    if "natural_language" in allowed and "json" in allowed:
        return gr.update(visible=True, value="natural_language", interactive=True)
    if allowed == ["natural_language"]:
        return gr.update(
            visible=True,
            value="natural_language",
            interactive=False,
        )
    return gr.update(visible=False, value="natural_language", interactive=False)


def _guidance_text(report: Mapping[str, Any]) -> str:
    contract = report.get("input_contract")
    contract = contract if isinstance(contract, Mapping) else {}
    text = str(contract.get("guidance") or "")
    parameter_facts = report.get("parameter_facts") or []
    if parameter_facts:
        text += "\n\n### 已记录但尚未验证的参数"
        for item in parameter_facts:
            if isinstance(item, Mapping):
                text += (
                    f"\n- `{item.get('fact_id', '未知字段')}`："
                    f"{_display_value(item.get('value'))} {item.get('unit') or '未知单位'}"
                )
    template = contract.get("json_template")
    if template:
        text += (
            "\n\n### 高级 JSON 模板\n```json\n"
            + json.dumps(template, ensure_ascii=False, indent=2)
            + "\n```"
        )
    if contract.get("disabled_reason"):
        text += f"\n\n{contract['disabled_reason']}"
    return text


def _timeline_text(report: Mapping[str, Any]) -> str:
    lines = ["### Agent 执行与参考来源"]
    config = report.get("agent_config")
    if isinstance(config, Mapping):
        rag = (
            "启用"
            if config.get("rag_enabled")
            else "未初始化"
            if config.get("rag_requested")
            else "关闭"
        )
        lines.append(
            f"- 编排：`multi`；本地 RAG：{rag}；快照："
            f"`{report.get('rag_snapshot') or '未固定索引快照'}`"
        )
    records = report.get("agent_records") or []
    if not records:
        lines.append("- 尚未记录 Agent 调用；当前状态由确定性 Kernel 管理。")
    for record in records:
        if not isinstance(record, Mapping):
            continue
        role = record.get("role", "agent")
        stage = record.get("stage", "")
        elapsed = record.get("elapsed_ms")
        elapsed_text = (
            f"，耗时 {float(elapsed):.0f} ms"
            if isinstance(elapsed, (int, float))
            else ""
        )
        source_ids = [
            str(item.get("source_id") or "unknown")
            for item in record.get("source_refs", ()) or ()
            if isinstance(item, Mapping)
        ]
        lines.append(
            f"- `{role}` / `{stage}`{elapsed_text}；来源："
            + ("、".join(source_ids) if source_ids else "无外部片段")
        )
    pending = report.get("pending_actions") or []
    lines.append("### 当前动作")
    if pending:
        for item in pending:
            if isinstance(item, Mapping):
                lines.append(
                    f"- `{item.get('ui_action') or item.get('action') or item.get('kind')}`"
                    + (f"：{item.get('reason')}" if item.get("reason") else "")
                )
    else:
        lines.append("- 无待处理动作。")
    return "\n".join(lines)


def _kernel_outputs(report: Mapping[str, Any], state: Mapping[str, Any]) -> tuple[Any, ...]:
    if not isinstance(report, Mapping) or not str(report.get("workflow_version") or "").startswith(
        "cfdc-v6-kernel"
    ):
        raise ValueError("WebUI 只接受 CFDC Kernel 报告。")
    state = dict(state or {})
    pending = [
        dict(item)
        for item in report.get("pending_actions", ()) or ()
        if isinstance(item, Mapping)
    ]
    display_state = {
        **state,
        "kernel_session_id": report.get("session_id"),
        "kernel_revision": report.get("revision"),
        "workflow_version": report.get("workflow_version"),
        "pending_actions": pending,
    }
    contract = report.get("input_contract")
    contract = contract if isinstance(contract, Mapping) else {}
    action = str(contract.get("action") or "")
    actionable = bool(action and not contract.get("disabled_reason")) and str(
        report.get("status")
    ) not in _TERMINAL_STATES
    no_input = not contract.get("allowed_modes")
    operator_action = action == "record_operator_report"
    upload_action = action == "ingest_upload"
    reply_update = _reply_mode_update(contract)
    if operator_action or upload_action:
        reply_update = {**reply_update, "visible": False}
    handoffs = report.get("operator_handoffs") or []
    prechecks = (
        list(handoffs[-1].get("prechecks", ()))
        if handoffs and isinstance(handoffs[-1], Mapping)
        else []
    )
    diagnosis, checklist = _diagnosis_rows(report)
    return (
        display_state,
        f"### {report.get('status', 'intake')}",
        _progress_html(report),
        _summary_html(report),
        checklist,
        _guidance_text(report),
        _timeline_text(report),
        diagnosis,
        _evidence_rows(report),
        _mapping_rows(report.get("route")),
        _feature_rows(report.get("features")),
        _controller_rows(report.get("controller")),
        _mapping_rows(report.get("freeze")),
        _mapping_rows(report.get("evaluation")),
        _mapping_rows(report.get("tuning")),
        dict(report),
        gr.update(
            visible=actionable and not no_input and not operator_action and not upload_action,
            value="",
            label=str(contract.get("title") or "提交当前动作"),
            placeholder=str(contract.get("guidance") or ""),
        ),
        reply_update,
        gr.update(
            visible=actionable,
            value=_action_label(action),
            interactive=actionable,
        ),
        gr.update(
            visible=actionable and action == "confirm_task",
            value=False,
            interactive=actionable and action == "confirm_task",
        ),
        _protocol_figure(report),
        _trace_figure(report),
        _evaluation_figure(report),
        _artifact_download(report),
        gr.update(
            visible=actionable and operator_action,
        ),
        gr.update(
            choices=prechecks,
            value=[],
        ),
        gr.update(visible=actionable and upload_action),
    )


def _task_type_visibility(task_type: str) -> tuple[Any, Any]:
    return (
        gr.update(visible=task_type == "transition_then_hold"),
        gr.update(visible=task_type == "disturbance_recovery_to_hold"),
    )


def _output_bounds_visibility(enabled: bool) -> Any:
    return gr.update(visible=bool(enabled))


def _optional_number_interactivity(enabled: bool) -> Any:
    return gr.update(interactive=bool(enabled))


def _selected_number_interactivity(
    selected: list[str] | tuple[str, ...] | None,
    field_names: tuple[str, ...],
) -> tuple[Any, ...]:
    enabled = {str(item) for item in selected or ()}
    return tuple(gr.update(interactive=name in enabled) for name in field_names)


def _success_requirement_interactivity(selected: Any) -> tuple[Any, ...]:
    return _selected_number_interactivity(
        selected,
        tuple(value for _, value in _SUCCESS_REQUIREMENT_CHOICES),
    )


def _budget_field_interactivity(selected: Any) -> tuple[Any, ...]:
    return _selected_number_interactivity(
        selected,
        tuple(value for _, value in _BUDGET_FIELD_CHOICES),
    )


def run_from_ui(
    description,
    task_type,
    measured_signals,
    control_inputs,
    reference_enabled,
    reference,
    input_min,
    input_max,
    output_bounds_enabled,
    output_min,
    output_max,
    state_stop,
    initial_region,
    goal_region,
    disturbance_event,
    recovery_start_condition,
    disturbance_hold_region,
    base_url,
    model,
    api_key,
    rag_enabled,
    rag_index_dir,
    provider_case_id=None,
    signal_units_json="",
    input_unit="",
    success_requirement_fields=None,
    final_abs_error_max=None,
    overshoot_max=None,
    settling_time_max_s=None,
    perturbed_success_rate_min=None,
    hold_duration_min_s=None,
    response_time_preference_enabled=False,
    response_time_preference_s=None,
    budget_fields=None,
    distinct_experiments=None,
    cumulative_excitation_time_s=None,
    initial_output_value_enabled=False,
    initial_output_value=None,
    intermediate_targets="",
):
    try:
        task: dict[str, Any] = {
            "description": str(description or ""),
            "task_type": str(task_type or ""),
            "measured_signals": parse_names(measured_signals),
            "control_inputs": parse_names(control_inputs),
            "input_min": input_min,
            "input_max": input_max,
            "output_min": output_min if output_bounds_enabled else None,
            "output_max": output_max if output_bounds_enabled else None,
            "state_stop": state_stop,
            "input_units": str(input_unit or "").strip() or None,
        }
        if reference_enabled:
            task["reference"] = reference
        if response_time_preference_enabled:
            task["response_time_preference_s"] = response_time_preference_s
        if str(signal_units_json or "").strip():
            units = json.loads(str(signal_units_json))
            if not isinstance(units, Mapping):
                raise ValueError("信号单位必须是 JSON 对象。")
            task["signal_units"] = dict(units)
        enabled_requirements = {
            str(item) for item in success_requirement_fields or ()
        }
        requirements = {
            key: value
            for key, value in {
                "final_abs_error_max": final_abs_error_max,
                "overshoot_max": overshoot_max,
                "settling_time_max_s": settling_time_max_s,
                "perturbed_success_rate_min": perturbed_success_rate_min,
                "hold_duration_min_s": hold_duration_min_s,
            }.items()
            if key in enabled_requirements
        }
        if requirements:
            task["success_requirements"] = requirements
        enabled_budgets = {str(item) for item in budget_fields or ()}
        budgets = {
            key: value
            for key, value in {
                "distinct_experiments": distinct_experiments,
                "cumulative_excitation_time_s": cumulative_excitation_time_s,
            }.items()
            if key in enabled_budgets
        }
        if budgets:
            task["budgets"] = budgets
        if task_type == "transition_then_hold":
            intermediate = [
                float(item.strip())
                for item in str(intermediate_targets or "").replace("、", ",").split(",")
                if item.strip()
            ]
            task.update(
                initial_region=str(initial_region or "").strip(),
                goal_region=str(goal_region or "").strip(),
                intermediate_targets=intermediate,
            )
            if initial_output_value_enabled:
                task["initial_output_value"] = initial_output_value
        elif task_type == "disturbance_recovery_to_hold":
            task.update(
                disturbance_event=str(disturbance_event or "").strip(),
                recovery_start_condition=str(recovery_start_condition or "").strip(),
                disturbance_hold_region=str(disturbance_hold_region or "").strip(),
            )
        report, state = start_kernel_app_run(
            task,
            rag_index_dir=str(rag_index_dir or "").strip() or None,
            use_rag=bool(rag_enabled),
            llm_configured=bool(base_url and model and api_key),
            provider_case_id=_resolve_case_id(provider_case_id) or None,
        )
        return _kernel_outputs(report, state)
    except Exception as exc:
        raise gr.Error(str(exc)) from exc


def submit_measurement_from_ui(
    state,
    response,
    simulation_bounds_confirmed,
    base_url,
    model,
    api_key,
    reply_mode="natural_language",
):
    try:
        if not isinstance(state, Mapping) or not str(
            state.get("workflow_version") or ""
        ).startswith("cfdc-v6-kernel"):
            raise TypeError("当前页面没有可继续的 CFDC Kernel 会话。")
        prepared = prepare_kernel_reply_for_ui(
            state,
            "" if response is None else str(response),
            mode=reply_mode,
            base_url=base_url,
            model=model,
            api_key=api_key,
        )
        action = _ACTION_ALIASES.get(str(prepared.get("action") or ""), prepared.get("action"))
        if action == "confirm_task" and simulation_bounds_confirmed is not True:
            raise ValueError("请先确认软件试验边界与预算。")
        if not isinstance(action, str) or not action:
            raise ValueError("当前待处理动作没有可用的 WebUI 入口。")
        payload = prepared.get("payload")
        payload = dict(payload) if isinstance(payload, Mapping) else {}
        report, next_state = continue_kernel_app_run(
            state,
            action=action,
            payload=payload,
            request_identity=(
                {
                    "input_mode": prepared.get("input_mode"),
                    "source_text": prepared.get("source_text", ""),
                }
                if prepared.get("input_mode")
                else None
            ),
            reply_source_text=prepared.get("source_text") or None,
            reply_input_mode=prepared.get("input_mode"),
            agent_records=prepared.get("agent_records", ()),
        )
        return _kernel_outputs(report, next_state)
    except Exception as exc:
        raise gr.Error(str(exc)) from exc


def submit_guided_action_from_ui(
    state,
    response,
    simulation_bounds_confirmed,
    base_url,
    model,
    api_key,
    reply_mode,
    operator_decision,
    operator_prechecks,
    operator_note,
    upload_files,
    stopped_on_limit,
):
    try:
        if not isinstance(state, Mapping):
            raise TypeError("当前页面没有可继续的 CFDC Kernel 会话。")
        pending = state.get("pending_actions")
        current = pending[0] if isinstance(pending, list) and pending else {}
        action = _ACTION_ALIASES.get(
            str(current.get("ui_action") or current.get("action") or ""),
            str(current.get("ui_action") or current.get("action") or ""),
        )
        if action == "record_operator_report":
            payload = {
                "decision": str(operator_decision or "").strip(),
                "prechecks_completed": list(operator_prechecks or ()),
                "note": str(operator_note or "").strip(),
            }
        elif action == "ingest_upload":
            files = upload_files if isinstance(upload_files, list) else [upload_files]
            paths = [_file_path(item) for item in files if item is not None]
            if not paths or any(not path for path in paths):
                raise ValueError("请选择协议绑定的 CSV 或 JSON 实验数据。")
            payload = {
                "paths": paths,
                "stopped_on_limit": bool(stopped_on_limit),
            }
        else:
            return submit_measurement_from_ui(
                state,
                response,
                simulation_bounds_confirmed,
                base_url,
                model,
                api_key,
                reply_mode,
            )
        report, next_state = continue_kernel_app_run(
            state,
            action=action,
            payload=payload,
        )
        return _kernel_outputs(report, next_state)
    except Exception as exc:
        raise gr.Error(str(exc)) from exc


def load_case_into_form(case_id: str) -> tuple[Any, ...]:
    if not str(case_id or "").strip():
        return (
            "", "local_setpoint_hold", "", "", False,
            gr.update(value=None, interactive=False),
            None, None, False, None, None, None, "", "", "", "", "", "", "",
            [],
            gr.update(value=None, interactive=False),
            gr.update(value=None, interactive=False),
            gr.update(value=None, interactive=False),
            gr.update(value=0.8, interactive=False),
            gr.update(value=None, interactive=False),
            False,
            gr.update(value=None, interactive=False),
            [],
            gr.update(value=None, interactive=False),
            gr.update(value=None, interactive=False),
            False,
            gr.update(value=None, interactive=False),
            "",
        )
    task = public_training_case(_resolve_case_id(case_id))["task"]
    units = task.get("engineering_units") if isinstance(task.get("engineering_units"), Mapping) else {}
    input_unit_value = ""
    signal_units: dict[str, str] = {}
    if isinstance(units, Mapping):
        input_spec = units.get("input")
        if isinstance(input_spec, Mapping):
            input_unit_value = str(input_spec.get("unit") or "")
        outputs = units.get("outputs")
        if isinstance(outputs, Mapping):
            signal_units = {
                str(name): str(spec.get("unit") or "")
                for name, spec in outputs.items()
                if isinstance(spec, Mapping)
            }
    requirements = (
        task.get("success_requirements")
        if isinstance(task.get("success_requirements"), Mapping)
        else task
    )
    budgets = task.get("budgets") if isinstance(task.get("budgets"), Mapping) else {}
    selected_requirements = [
        field_id
        for _, field_id in _SUCCESS_REQUIREMENT_CHOICES
        if requirements.get(field_id) is not None
    ]
    selected_budgets = [
        field_id
        for _, field_id in _BUDGET_FIELD_CHOICES
        if budgets.get(field_id) is not None
    ]
    reference_enabled = task.get("reference") is not None
    response_time_enabled = task.get("response_time_preference_s") is not None
    initial_output_enabled = task.get("initial_output_value") is not None

    def optional_update(value: Any, enabled: bool) -> Any:
        return gr.update(value=value, interactive=enabled)

    return (
        task.get("description", ""),
        task.get("task_type", "local_setpoint_hold"),
        ", ".join(task.get("measured_signals", ())),
        ", ".join(task.get("control_inputs") or [task.get("control_input", "")]),
        reference_enabled,
        optional_update(task.get("reference"), reference_enabled),
        task.get("input_min"),
        task.get("input_max"),
        bool(task.get("output_min") is not None),
        task.get("output_min"),
        task.get("output_max"),
        task.get("state_stop"),
        task.get("initial_region", ""),
        task.get("goal_region", ""),
        task.get("disturbance_event", ""),
        task.get("recovery_start_condition", ""),
        task.get("disturbance_hold_region", ""),
        json.dumps(signal_units, ensure_ascii=False) if signal_units else "",
        input_unit_value,
        selected_requirements,
        optional_update(
            requirements.get("final_abs_error_max"),
            "final_abs_error_max" in selected_requirements,
        ),
        optional_update(
            requirements.get("overshoot_max"),
            "overshoot_max" in selected_requirements,
        ),
        optional_update(
            requirements.get("settling_time_max_s"),
            "settling_time_max_s" in selected_requirements,
        ),
        optional_update(
            requirements.get("perturbed_success_rate_min", 0.8),
            "perturbed_success_rate_min" in selected_requirements,
        ),
        optional_update(
            requirements.get("hold_duration_min_s"),
            "hold_duration_min_s" in selected_requirements,
        ),
        response_time_enabled,
        optional_update(task.get("response_time_preference_s"), response_time_enabled),
        selected_budgets,
        optional_update(
            budgets.get("distinct_experiments"),
            "distinct_experiments" in selected_budgets,
        ),
        optional_update(
            budgets.get("cumulative_excitation_time_s"),
            "cumulative_excitation_time_s" in selected_budgets,
        ),
        initial_output_enabled,
        optional_update(task.get("initial_output_value"), initial_output_enabled),
        ", ".join(str(item) for item in task.get("intermediate_targets", ()) or ()),
    )


def _file_path(value: Any) -> str:
    if isinstance(value, list):
        if len(value) != 1:
            raise ValueError("请选择一个 v3 ZIP。")
        return _file_path(value[0])
    if isinstance(value, str):
        return value
    if isinstance(value, Mapping):
        return str(value.get("path") or value.get("name") or "")
    name = getattr(value, "name", None)
    return str(name or "")


def expert_start_from_json(task_json: str, session_dir: str) -> tuple[Any, ...]:
    try:
        payload = json.loads(str(task_json or ""))
        if not isinstance(payload, Mapping):
            raise TypeError("TaskContract JSON 必须是对象。")
        report, state = start_kernel_app_run(
            payload,
            session_dir=str(session_dir or "").strip() or None,
            use_rag=False,
        )
        return _kernel_outputs(report, state)
    except Exception as exc:
        raise gr.Error(str(exc)) from exc


def expert_load_session(session_id: str, session_dir: str) -> tuple[Any, ...]:
    try:
        report, state = load_kernel_app_run(
            str(session_id or "").strip(),
            session_dir=str(session_dir or "").strip() or None,
        )
        return _kernel_outputs(report, state)
    except Exception as exc:
        raise gr.Error(str(exc)) from exc


def expert_import_v3(source: Any, session_dir: str) -> tuple[Any, ...]:
    try:
        path = _file_path(source)
        if not path:
            raise ValueError("请选择 v3 目录 ZIP。")
        report, state = import_v3_app_run(
            path,
            session_dir=str(session_dir or "").strip() or None,
        )
        return _kernel_outputs(report, state)
    except Exception as exc:
        raise gr.Error(str(exc)) from exc


def expert_submit_action(state: Any, action: str, payload_json: str) -> tuple[Any, ...]:
    try:
        payload = json.loads(str(payload_json or "{}").strip() or "{}")
        if not isinstance(payload, Mapping):
            raise TypeError("Typed action payload 必须是 JSON 对象。")
        report, next_state = continue_kernel_app_run(
            state,
            action=str(action or "").strip(),
            payload=payload,
        )
        return _kernel_outputs(report, next_state)
    except Exception as exc:
        raise gr.Error(str(exc)) from exc


def expert_validate_artifact(payload_json: str) -> dict[str, Any]:
    try:
        payload = json.loads(str(payload_json or ""))
        if not isinstance(payload, Mapping):
            raise TypeError("Artifact JSON 必须是对象。")
        return validate_kernel_artifact(payload)
    except Exception as exc:
        raise gr.Error(str(exc)) from exc


def expert_export_bundle(state: Any) -> str:
    try:
        return export_kernel_app_bundle(state)
    except Exception as exc:
        raise gr.Error(str(exc)) from exc


def export_artifact_from_ui(state: Any, artifact_kind: str) -> str:
    try:
        return export_kernel_app_artifact(state, artifact_kind)
    except Exception as exc:
        raise gr.Error(str(exc)) from exc


def reset_ui() -> tuple[Any, ...]:
    return (
        {},
        "### 等待 CFDC Kernel 任务",
        "",
        "",
        [],
        "",
        "",
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        {},
        gr.update(visible=False, value=""),
        gr.update(visible=False, value="natural_language", interactive=False),
        gr.update(visible=False, interactive=False),
        gr.update(visible=False, value=False, interactive=False),
        _protocol_figure({}),
        _trace_figure({}),
        _evaluation_figure({}),
        gr.update(value=None, visible=False),
        gr.update(visible=False),
        gr.update(choices=[], value=[]),
        gr.update(visible=False),
    )


def reset_task_form() -> tuple[Any, ...]:
    return (
        "",
        "local_setpoint_hold",
        "",
        "",
        False,
        gr.update(value=None, interactive=False),
        None,
        None,
        False,
        None,
        None,
        None,
        "",
        "",
        "",
        "",
        "",
        os.getenv("CFDC_LLM_BASE_URL", ""),
        os.getenv("CFDC_LLM_MODEL", ""),
        "",
        True,
        "",
        "",
        "",
        "",
        [],
        gr.update(value=None, interactive=False),
        gr.update(value=None, interactive=False),
        gr.update(value=None, interactive=False),
        gr.update(value=0.8, interactive=False),
        gr.update(value=None, interactive=False),
        False,
        gr.update(value=None, interactive=False),
        [],
        gr.update(value=None, interactive=False),
        gr.update(value=None, interactive=False),
        False,
        gr.update(value=None, interactive=False),
        "",
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
    )


def build_app() -> gr.Blocks:
    with gr.Blocks(title="CFDC Control Studio") as demo:
        app_state = gr.State({})
        gr.Markdown("# CFDC Control Studio", elem_id="app-title")

        with gr.Row(equal_height=False):
            with gr.Column(scale=5, min_width=360):
                case_catalog = public_case_catalog()
                provider_case_id = gr.Dropdown(
                    label="内置审计／工程案例",
                    choices=[("自定义任务", "")] + [
                        (str(case_catalog[case_id]["label"]), web_case_id)
                        for web_case_id, case_id in _WEB_CASE_IDS.items()
                    ],
                    value="",
                )
                task_type = gr.Radio(
                    label="任务类型",
                    choices=[
                        ("局部设定值保持", "local_setpoint_hold"),
                        ("转换后保持", "transition_then_hold"),
                        ("扰动恢复后保持", "disturbance_recovery_to_hold"),
                    ],
                    value="local_setpoint_hold",
                )
                description = gr.Textbox(
                    label="控制任务描述",
                    lines=6,
                    placeholder="描述控制对象、目标、已知现象和事实来源。",
                )
                with gr.Group(elem_classes="task-contract-grid"):
                    measured_signals = gr.Textbox(
                        label="观测输出",
                        placeholder="temperature, pressure",
                    )
                    control_inputs = gr.Textbox(
                        label="控制输入",
                        placeholder="heater_voltage",
                    )
                    with gr.Row():
                        reference_enabled = gr.Checkbox(
                            label="提供目标参考值",
                            value=False,
                        )
                        reference = gr.Number(
                            label="目标参考值",
                            value=None,
                            interactive=False,
                        )
                    with gr.Row():
                        input_min = gr.Number(label="控制输入下界", value=None)
                        input_max = gr.Number(label="控制输入上界", value=None)
                    output_bounds_enabled = gr.Checkbox(
                        label="提供观测输出边界",
                        value=False,
                    )
                    with gr.Row(visible=False) as output_bounds_fields:
                        output_min = gr.Number(label="观测输出下界（可选）", value=None)
                        output_max = gr.Number(label="观测输出上界（可选）", value=None)
                    state_stop = gr.Number(label="状态停止阈值", value=None)

                with gr.Accordion("单位、性能与预算", open=False):
                    signal_units_json = gr.Textbox(
                        label="输出信号单位 JSON",
                        placeholder='{"temperature": "degC"}',
                    )
                    input_unit = gr.Textbox(label="控制输入单位")
                    success_requirement_fields = gr.CheckboxGroup(
                        label="启用的性能要求",
                        choices=_SUCCESS_REQUIREMENT_CHOICES,
                        value=[],
                    )
                    with gr.Row():
                        final_abs_error_max = gr.Number(
                            label="最大终值绝对误差",
                            value=None,
                            interactive=False,
                        )
                        overshoot_max = gr.Number(
                            label="最大超调",
                            value=None,
                            interactive=False,
                        )
                    with gr.Row():
                        settling_time_max_s = gr.Number(
                            label="最大调节时间 (s)",
                            value=None,
                            interactive=False,
                        )
                        hold_duration_min_s = gr.Number(
                            label="最短保持时间 (s)",
                            value=None,
                            interactive=False,
                        )
                    perturbed_success_rate_min = gr.Slider(
                        label="扰动重复成功率下限",
                        minimum=0,
                        maximum=1,
                        step=0.05,
                        value=0.8,
                        interactive=False,
                    )
                    with gr.Row():
                        response_time_preference_enabled = gr.Checkbox(
                            label="提供响应时间偏好",
                            value=False,
                        )
                        response_time_preference_s = gr.Number(
                            label="响应时间偏好 (s)",
                            value=None,
                            interactive=False,
                        )
                    budget_fields = gr.CheckboxGroup(
                        label="启用的实验预算",
                        choices=_BUDGET_FIELD_CHOICES,
                        value=[],
                    )
                    with gr.Row():
                        distinct_experiments = gr.Number(
                            label="不同实验预算",
                            value=None,
                            precision=0,
                            interactive=False,
                        )
                        cumulative_excitation_time_s = gr.Number(
                            label="累计激励预算 (s)",
                            value=None,
                            interactive=False,
                        )

                with gr.Group(visible=False) as transition_fields:
                    initial_region = gr.Textbox(label="初始区域")
                    with gr.Row():
                        initial_output_value_enabled = gr.Checkbox(
                            label="提供初始输出数值",
                            value=False,
                        )
                        initial_output_value = gr.Number(
                            label="初始输出数值",
                            value=None,
                            interactive=False,
                        )
                    intermediate_targets = gr.Textbox(label="中间目标", placeholder="3, 6")
                    goal_region = gr.Textbox(label="目标区域")
                with gr.Group(visible=False) as disturbance_fields:
                    disturbance_event = gr.Textbox(label="扰动事件")
                    recovery_start_condition = gr.Textbox(label="恢复起点条件")
                    disturbance_hold_region = gr.Textbox(label="恢复后保持区域")

                with gr.Accordion("Provider 与 RAG", open=False):
                    base_url = gr.Textbox(
                        label="Base URL",
                        value=os.getenv("CFDC_LLM_BASE_URL", ""),
                        placeholder="https://provider.example/v1",
                    )
                    model = gr.Textbox(
                        label="Model",
                        value=os.getenv("CFDC_LLM_MODEL", ""),
                        placeholder="provider-model",
                    )
                    api_key = gr.Textbox(label="API Key", value="", type="password")
                    rag_enabled = gr.Checkbox(label="启用本地 RAG", value=True)
                    rag_index_dir = gr.Textbox(
                        label="本地 RAG 索引目录（可选）",
                        placeholder="例如 ./rag-index",
                    )
                with gr.Row():
                    base_run_button = gr.Button("创建基础任务", visible=False)
                    run_button = gr.Button(
                        "创建 Kernel 任务",
                        variant="primary",
                        elem_classes="primary-run",
                        scale=4,
                    )
                    clear_button = gr.Button("清空", scale=1)

            with gr.Column(scale=8, min_width=560):
                status = gr.Markdown("### 等待 CFDC Kernel 任务", elem_id="run-status")
                progress = gr.HTML(elem_id="stage-progress")
                summary = gr.HTML()
                checklist = gr.Dataframe(
                    headers=["诊断维度", "状态", "证据摘录"],
                    datatype=["str", "str", "str"],
                    interactive=False,
                    label="八项动态诊断账本",
                    elem_classes="stage-table",
                )
                guidance = gr.Markdown()
                timeline = gr.Markdown()

                response = gr.Textbox(
                    label="提交当前动作",
                    value="",
                    lines=8,
                    visible=False,
                )
                reply_mode = gr.Radio(
                    label="回复方式",
                    choices=_REPLY_CHOICES,
                    value="natural_language",
                    visible=False,
                )
                simulation_bounds_confirmed = gr.Checkbox(
                    label="我确认这些边界只用于软件试验和停止条件",
                    value=False,
                    visible=False,
                )
                with gr.Group(visible=False) as operator_action_fields:
                    operator_decision = gr.Dropdown(
                        label="操作员决定",
                        choices=[
                            ("接受并按协议执行", "accepted"),
                            ("需要澄清", "needs_clarification"),
                            ("拒绝执行", "refused"),
                        ],
                        value="accepted",
                    )
                    operator_prechecks = gr.CheckboxGroup(
                        label="已完成预检查",
                        choices=[],
                    )
                    operator_note = gr.Textbox(label="操作员备注", lines=3)
                with gr.Group(visible=False) as upload_action_fields:
                    upload_files = gr.File(
                        label="协议绑定实验数据",
                        file_types=[".csv", ".json"],
                        file_count="multiple",
                    )
                    stopped_on_limit = gr.Checkbox(
                        label="实验触发停止边界并已停止",
                        value=False,
                    )
                base_action_button = gr.Button("提交基础动作", visible=False)
                action_button = gr.Button(
                    "提交当前动作",
                    variant="primary",
                    visible=False,
                )

                with gr.Tabs():
                    with gr.Tab("引导工作台"):
                        diagnosis = gr.Dataframe(
                            headers=["字段", "Assessment", "置信度", "证据"],
                            datatype=["str", "str", "str", "str"],
                            interactive=False,
                            elem_classes="stage-table",
                        )
                    with gr.Tab("公开证据"):
                        protocol_plot = gr.Plot(elem_classes="kernel-plot")
                        trace_plot = gr.Plot(elem_classes="kernel-plot")
                        evidence = gr.Dataframe(
                            headers=["#", "操作", "证据 ID", "特征", "采样数", "信号"],
                            datatype=["number", "str", "str", "str", "str", "str"],
                            interactive=False,
                            elem_classes="stage-table",
                        )
                    with gr.Tab("路线与特征"):
                        route = gr.Dataframe(
                            headers=["路线字段", "值"],
                            datatype=["str", "str"],
                            interactive=False,
                            elem_classes="stage-table",
                        )
                        features = gr.Dataframe(
                            headers=["特征", "值", "单位", "置信区间", "置信度", "方法"],
                            datatype=["str", "str", "str", "str", "str", "str"],
                            interactive=False,
                            elem_classes="stage-table",
                        )
                    with gr.Tab("控制器与冻结"):
                        controller = gr.Dataframe(
                            headers=["控制器字段", "值"],
                            datatype=["str", "str"],
                            interactive=False,
                            elem_classes="stage-table",
                        )
                        freeze = gr.Dataframe(
                            headers=["冻结字段", "值"],
                            datatype=["str", "str"],
                            interactive=False,
                            elem_classes="stage-table",
                        )
                    with gr.Tab("评价与调优"):
                        evaluation_plot = gr.Plot(elem_classes="kernel-plot")
                        evaluation = gr.Dataframe(
                            headers=["评价字段", "值"],
                            datatype=["str", "str"],
                            interactive=False,
                            elem_classes="stage-table",
                        )
                        tuning = gr.Dataframe(
                            headers=["调优字段", "值"],
                            datatype=["str", "str"],
                            interactive=False,
                            elem_classes="stage-table",
                        )
                    with gr.Tab("审计 JSON"):
                        raw_json = gr.JSON(label="完整 Kernel 记录")
                        artifact_download = gr.DownloadButton(
                            label="下载当前 Artifact",
                            visible=False,
                        )
                        artifact_kind = gr.Dropdown(
                            label="公开 Artifact",
                            choices=[
                                ("实验协议", "protocol"),
                                ("操作员交接包", "operator_bundle"),
                                ("上传回执", "upload_receipt"),
                                ("自动特征", "features"),
                                ("Controller IR", "controller_ir"),
                                ("资格审查", "qualification"),
                                ("控制器冻结", "freeze"),
                                ("独立评价", "evaluation"),
                                ("有界反馈", "feedback"),
                                ("全新确认", "confirmation"),
                                ("最终结果", "result"),
                                ("完整会话审计", "audit"),
                            ],
                            value="result",
                        )
                        selected_artifact_download = gr.DownloadButton(
                            label="下载所选 Artifact"
                        )
                        artifact_export_button = gr.Button("生成所选 Artifact")
                        export_button = gr.Button("导出完整审计包")
                    with gr.Tab("专家合同"):
                        expert_session_dir = gr.Textbox(
                            label="Kernel session 目录",
                            value="output/kernel-sessions",
                        )
                        with gr.Row():
                            expert_session_id = gr.Textbox(label="Session ID")
                            expert_load_button = gr.Button("加载")
                        expert_task_json = gr.Code(
                            label="TaskContract JSON",
                            language="json",
                            value="{}",
                        )
                        expert_start_button = gr.Button("创建专家任务")
                        with gr.Row():
                            expert_action = gr.Dropdown(
                                label="Typed action",
                                choices=sorted(
                                    {
                                        "confirm_task", "answer", "advance", "set_provider",
                                        "compile_protocol", "prepare_operator_handoff",
                                        "record_operator_report", "ingest_upload", "derive_features",
                                        "synthesize_controller", "qualify_controller", "freeze",
                                        "run_provider", "run_evaluation", "run_feedback_iteration",
                                        "confirm_result", "replay", "cancel",
                                    }
                                ),
                            )
                            expert_action_button = gr.Button("执行")
                        expert_payload = gr.Code(label="Action payload JSON", language="json", value="{}")
                        expert_artifact_json = gr.Code(
                            label="Artifact JSON",
                            language="json",
                            value="{}",
                        )
                        expert_validate_button = gr.Button("校验 Artifact")
                        expert_validation = gr.JSON(label="校验结果")
                        expert_v3_zip = gr.File(
                            label="v3 目录 ZIP",
                            file_types=[".zip"],
                            file_count="multiple",
                        )
                        expert_import_button = gr.Button("只读导入 v3")
                        expert_bundle = gr.DownloadButton(label="下载完整审计 ZIP")

        gr.Markdown(LICENSE_NOTICE, elem_id="license-notice")

        output_components = [
            app_state,
            status,
            progress,
            summary,
            checklist,
            guidance,
            timeline,
            diagnosis,
            evidence,
            route,
            features,
            controller,
            freeze,
            evaluation,
            tuning,
            raw_json,
            response,
            reply_mode,
            action_button,
            simulation_bounds_confirmed,
            protocol_plot,
            trace_plot,
            evaluation_plot,
            artifact_download,
            operator_action_fields,
            operator_prechecks,
            upload_action_fields,
        ]
        base_form_components = [
            description,
            task_type,
            measured_signals,
            control_inputs,
            reference_enabled,
            reference,
            input_min,
            input_max,
            output_bounds_enabled,
            output_min,
            output_max,
            state_stop,
            initial_region,
            goal_region,
            disturbance_event,
            recovery_start_condition,
            disturbance_hold_region,
            base_url,
            model,
            api_key,
            rag_enabled,
            rag_index_dir,
        ]
        extended_form_components = [
            provider_case_id,
            signal_units_json,
            input_unit,
            success_requirement_fields,
            final_abs_error_max,
            overshoot_max,
            settling_time_max_s,
            perturbed_success_rate_min,
            hold_duration_min_s,
            response_time_preference_enabled,
            response_time_preference_s,
            budget_fields,
            distinct_experiments,
            cumulative_excitation_time_s,
            initial_output_value_enabled,
            initial_output_value,
            intermediate_targets,
        ]
        form_components = [*base_form_components, *extended_form_components]
        provider_case_id.change(
            load_case_into_form,
            inputs=[provider_case_id],
            outputs=[
                description, task_type, measured_signals, control_inputs,
                reference_enabled, reference,
                input_min, input_max, output_bounds_enabled, output_min, output_max,
                state_stop, initial_region, goal_region, disturbance_event,
                recovery_start_condition, disturbance_hold_region, signal_units_json,
                input_unit, success_requirement_fields, final_abs_error_max,
                overshoot_max, settling_time_max_s, perturbed_success_rate_min,
                hold_duration_min_s, response_time_preference_enabled,
                response_time_preference_s, budget_fields, distinct_experiments,
                cumulative_excitation_time_s, initial_output_value_enabled,
                initial_output_value, intermediate_targets,
            ],
            api_visibility="private",
        )
        reference_enabled.change(
            _optional_number_interactivity,
            inputs=[reference_enabled],
            outputs=[reference],
            api_visibility="private",
        )
        success_requirement_fields.change(
            _success_requirement_interactivity,
            inputs=[success_requirement_fields],
            outputs=[
                final_abs_error_max,
                overshoot_max,
                settling_time_max_s,
                hold_duration_min_s,
                perturbed_success_rate_min,
            ],
            api_visibility="private",
        )
        response_time_preference_enabled.change(
            _optional_number_interactivity,
            inputs=[response_time_preference_enabled],
            outputs=[response_time_preference_s],
            api_visibility="private",
        )
        budget_fields.change(
            _budget_field_interactivity,
            inputs=[budget_fields],
            outputs=[distinct_experiments, cumulative_excitation_time_s],
            api_visibility="private",
        )
        initial_output_value_enabled.change(
            _optional_number_interactivity,
            inputs=[initial_output_value_enabled],
            outputs=[initial_output_value],
            api_visibility="private",
        )
        task_type.change(
            _task_type_visibility,
            inputs=[task_type],
            outputs=[transition_fields, disturbance_fields],
            api_visibility="private",
        )
        output_bounds_enabled.change(
            _output_bounds_visibility,
            inputs=[output_bounds_enabled],
            outputs=[output_bounds_fields],
            api_visibility="private",
        )
        base_run_button.click(
            run_from_ui,
            inputs=base_form_components,
            outputs=output_components,
            **_MUTATION_OPTIONS,
        )
        run_button.click(
            run_from_ui,
            inputs=form_components,
            outputs=output_components,
            **_MUTATION_OPTIONS,
        )
        base_action_button.click(
            submit_measurement_from_ui,
            inputs=[
                app_state,
                response,
                simulation_bounds_confirmed,
                base_url,
                model,
                api_key,
                reply_mode,
            ],
            outputs=output_components,
            **_MUTATION_OPTIONS,
        )
        action_button.click(
            submit_guided_action_from_ui,
            inputs=[
                app_state,
                response,
                simulation_bounds_confirmed,
                base_url,
                model,
                api_key,
                reply_mode,
                operator_decision,
                operator_prechecks,
                operator_note,
                upload_files,
                stopped_on_limit,
            ],
            outputs=output_components,
            **_MUTATION_OPTIONS,
        )
        clear_button.click(
            reset_ui,
            outputs=output_components,
            **_MUTATION_OPTIONS,
        )
        expert_start_button.click(
            expert_start_from_json,
            inputs=[expert_task_json, expert_session_dir],
            outputs=output_components,
            **_MUTATION_OPTIONS,
        )
        expert_load_button.click(
            expert_load_session,
            inputs=[expert_session_id, expert_session_dir],
            outputs=output_components,
            **_MUTATION_OPTIONS,
        )
        expert_action_button.click(
            expert_submit_action,
            inputs=[app_state, expert_action, expert_payload],
            outputs=output_components,
            **_MUTATION_OPTIONS,
        )
        expert_validate_button.click(
            expert_validate_artifact,
            inputs=[expert_artifact_json],
            outputs=[expert_validation],
            api_visibility="private",
        )
        expert_import_button.click(
            expert_import_v3,
            inputs=[expert_v3_zip, expert_session_dir],
            outputs=output_components,
            **_MUTATION_OPTIONS,
        )
        export_button.click(
            expert_export_bundle,
            inputs=[app_state],
            outputs=[expert_bundle],
            **_MUTATION_OPTIONS,
        )
        artifact_export_button.click(
            export_artifact_from_ui,
            inputs=[app_state, artifact_kind],
            outputs=[selected_artifact_download],
            **_MUTATION_OPTIONS,
        )
        clear_button.click(
            reset_task_form,
            outputs=[
                *form_components,
                output_bounds_fields,
                transition_fields,
                disturbance_fields,
            ],
            **_MUTATION_OPTIONS,
        )
    return demo


__all__ = [
    "CSS",
    "build_app",
    "expert_validate_artifact",
    "export_artifact_from_ui",
    "reset_task_form",
    "reset_ui",
    "run_from_ui",
    "submit_guided_action_from_ui",
    "submit_measurement_from_ui",
]
