"""Pure, read-only presentation helpers for the guided Kernel WebUI."""

from __future__ import annotations

import html
import math
import re
from collections.abc import Mapping
from typing import Any

import plotly.graph_objects as go

from cfdc.evidence import GATE_DEFINITIONS

_TERMINAL_STATES = frozenset({"performance_met", "capability_gap", "cancelled"})
_ACTION_ALIASES = {"submit_answer": "answer"}
_KNOWN_ACTIONS = frozenset(
    {
        "confirm_task",
        "answer",
        "relevance",
        "advance",
        "evidence",
        "phase",
        "features",
        "controller",
        "freeze",
        "evaluation",
        "cancel",
        "replay",
        "confirmation",
        "revise_diagnostic",
        "compile_protocol",
        "prepare_operator_handoff",
        "prepare_training_exercise_bundle",
        "record_operator_report",
        "ingest_upload",
        "derive_features",
        "synthesize_controller",
        "qualify_controller",
        "run_provider",
        "run_evaluation",
        "run_feedback_iteration",
        "confirm_result",
    }
)
_ACTION_COPY = {
    "confirm_task": ("确认任务边界", "确认目标、软件试验边界和预算后开始。"),
    "answer": (
        "补充已知现象",
        "说明已经观察到的对象特征；没有把握的项目可以明确填写不知道。",
    ),
    "relevance": ("说明不相关项", "说明某项诊断为何不适用于当前任务。"),
    "advance": ("继续下一步", "使用已记录信息进入下一阶段。"),
    "evidence": (
        "需要补充可验证的证据",
        "准备与本任务和路线要求一致的公开实验记录；打开专业提交查看所需字段。",
    ),
    "phase": ("确认阶段方案", "检查分阶段目标后继续。"),
    "features": ("记录特征", "提交由公开证据支持的特征。"),
    "derive_features": ("提取特征", "从已接受的公开证据提取特征。"),
    "controller": ("提交控制器", "提交满足当前类型合同的控制器描述。"),
    "synthesize_controller": ("生成控制器", "根据已确认的特征生成候选控制器。"),
    "freeze": ("冻结候选方案", "冻结控制器及其评价条件，供独立评价使用。"),
    "qualify_controller": ("检查控制器资格", "运行冻结前的确定性资格审查。"),
    "evaluation": ("记录评价", "提交与冻结方案绑定的评价数据。"),
    "run_evaluation": ("运行开发评价", "按冻结的评价合同运行软件开发评价。"),
    "replay": ("复核评价记录", "重新读取已记录数据并核对评价结论。"),
    "confirmation": ("提交独立确认", "提交与已冻结候选绑定的全新确认数据。"),
    "confirm_result": ("执行独立确认", "使用预留试次对冻结候选做一次独立确认。"),
    "run_feedback_iteration": ("运行有界调优", "在预先限定的范围内评估候选。"),
    "compile_protocol": ("生成实验协议", "生成当前取证步骤所需的受限协议。"),
    "prepare_operator_handoff": ("下载操作包", "下载当前协议和操作说明。"),
    "prepare_training_exercise_bundle": (
        "生成练习包",
        "生成当前教学练习所需的数据包。",
    ),
    "record_operator_report": ("确认操作检查", "记录操作前检查结果。"),
    "ingest_upload": ("检查上传数据", "按当前协议检查上传文件。"),
    "run_provider": ("运行当前步骤", "运行当前配置的确定性提供器。"),
    "revise_diagnostic": ("修订诊断", "根据已记录证据修订诊断。"),
    "cancel": ("取消任务", "结束当前任务。"),
}
_STAGE_BY_STATUS = {
    "intake": 0,
    "diagnostic": 0,
    "awaiting_evidence": 1,
    "protocol_ready": 1,
    "awaiting_operator_report": 1,
    "awaiting_provider": 1,
    "route_ready": 2,
    "controller_pending": 2,
    "controller_candidate_ready": 2,
    "controller_qualified": 2,
    "controller_ready": 2,
    "evaluation_recorded_pending_replay": 3,
    "tuning_eligible": 3,
    "awaiting_confirmation": 3,
    "performance_met": 3,
    "capability_gap": 3,
    "cancelled": 3,
}
_REQUIREMENT_LABELS = {
    "final_abs_error_max": "终值绝对误差不超过",
    "overshoot_max": "超调不超过",
    "settling_time_max_s": "调节时间不超过",
    "hold_duration_min_s": "保持时间不少于",
    "hold_duration_s": "保持时间不少于",
    "recovery_time_max_s": "恢复时间不超过",
    "perturbed_success_rate_min": "扰动试次成功率不少于",
    "success_rate_min": "试次成功率不少于",
    "worst_trial_violation_max": "最差试次偏差不超过",
    "required_phase_count_min": "完成阶段数不少于",
    "verified_handoff_count_min": "已验证阶段切换数不少于",
    "goal_region_entry_required": "必须进入目标区域",
    "final_hold_duration_min_s": "最终保持时间不少于",
    "recovery_abs_error_max": "恢复绝对误差不超过",
    "post_recovery_hold_duration_min_s": "恢复后保持时间不少于",
    "iae_max": "绝对误差积分不超过",
    "peak_abs_input_max": "输入峰值不超过",
    "peak_abs_output_max": "输出峰值不超过",
    "saturation_duration_max_s": "饱和持续时间不超过",
    "saturation_ratio_max": "饱和时间占比不超过",
}
_METRIC_LABELS = {
    "final_abs_error": "终值绝对误差",
    "overshoot": "超调",
    "settling_time_s": "调节时间",
    "hold_duration_s": "保持时间",
    "iae": "绝对误差积分",
    "peak_abs_output": "输出绝对峰值",
    "peak_abs_input": "输入绝对峰值",
    "raw_peak_abs_input": "限幅前输入绝对峰值",
    "saturation_duration_s": "饱和持续时间",
    "saturation_fraction": "饱和时间占比",
    "completed_phase_count": "已完成阶段数",
    "verified_handoff_count": "已验证阶段切换数",
    "final_hold_duration_s": "最终保持时间",
    "entered_goal_region": "已进入目标区域",
    "recovered_to_hold": "已恢复并保持",
    "recovery_time_s": "恢复时间",
    "post_recovery_hold_duration_s": "恢复后保持时间",
    "disturbance_event_verified": "扰动事件已验证",
}
_METRIC_REQUIREMENTS = {
    "final_abs_error": ("final_abs_error_max", "recovery_abs_error_max"),
    "overshoot": ("overshoot_max",),
    "settling_time_s": ("settling_time_max_s",),
    "hold_duration_s": ("hold_duration_min_s",),
    "iae": ("iae_max",),
    "peak_abs_output": ("peak_abs_output_max",),
    "peak_abs_input": ("peak_abs_input_max",),
    "saturation_duration_s": ("saturation_duration_max_s",),
    "saturation_fraction": ("saturation_ratio_max",),
    "completed_phase_count": ("required_phase_count_min",),
    "verified_handoff_count": ("verified_handoff_count_min",),
    "final_hold_duration_s": ("final_hold_duration_min_s",),
    "entered_goal_region": ("goal_region_entry_required",),
    "recovery_time_s": ("recovery_time_max_s",),
    "post_recovery_hold_duration_s": ("post_recovery_hold_duration_min_s",),
}
_TOP_LEVEL_METRICS = (
    "completed_phase_count",
    "verified_handoff_count",
    "final_hold_duration_s",
    "entered_goal_region",
    "recovered_to_hold",
    "recovery_time_s",
    "post_recovery_hold_duration_s",
    "disturbance_event_verified",
)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _items(value: Any) -> list[Any]:
    if isinstance(value, list | tuple):
        return list(value)
    return []


def _safe(value: Any) -> str:
    """Escape untrusted text for Markdown, including embedded HTML."""

    text = html.escape(str(value), quote=True)
    return re.sub(r"([\\`*_{}\[\]()#+.!|>\-])", r"\\\1", text)


def _plain(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _number(value: Any) -> str:
    if isinstance(value, bool):
        return _safe(value)
    if isinstance(value, int | float) and math.isfinite(float(value)):
        return f"{float(value):g}"
    return _safe(value)


def _unit_suffix(unit: Any) -> str:
    text = str(unit or "").strip()
    return f" {_safe(text)}" if text and text != "unspecified" else ""


def _named_signals(names: Any, units: Mapping[str, Any]) -> str:
    values = []
    for name in _items(names):
        clean_name = str(name).strip()
        if not clean_name:
            continue
        unit = str(units.get(clean_name) or "").strip()
        rendered = _safe(clean_name)
        if unit and unit != "unspecified":
            rendered += f"（{_safe(unit)}）"
        values.append(rendered)
    return "、".join(values) if values else "未提供"


def _criterion_unit(
    task: Mapping[str, Any], key: str, signal: str | None = None
) -> str:
    if key.endswith("_s"):
        return "s"
    if "rate" in key or "ratio" in key:
        return "%"
    if key == "iae_max":
        base = _mapping(task.get("signal_units")).get(signal or "")
        return f"{base}·s" if base else ""
    if "input" in key:
        return str(task.get("input_units") or "")
    if any(marker in key for marker in ("error", "overshoot", "output")):
        signal_units = _mapping(task.get("signal_units"))
        if signal:
            return str(signal_units.get(signal) or "")
        units = {str(value) for value in signal_units.values() if value}
        return units.pop() if len(units) == 1 else ""
    return ""


def _criterion_value(
    task: Mapping[str, Any], key: str, value: Any, signal: str | None = None
) -> str:
    if isinstance(value, bool):
        return "是" if value else "否"
    if ("rate" in key or "ratio" in key) and isinstance(value, int | float):
        return _percent(value)
    return f"{_number(value)}{_unit_suffix(_criterion_unit(task, key, signal))}"


def _finite_numeric(value: Any) -> bool:
    return (
        isinstance(value, int | float)
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def _requirement_signals(task: Mapping[str, Any], key: str) -> set[str]:
    if "input" in key or "saturation" in key:
        names = _items(task.get("control_inputs"))
        if not names and task.get("control_input"):
            names = [task["control_input"]]
    else:
        names = _items(task.get("measured_signals"))
    return {str(name) for name in names if str(name).strip()}


def _requirement_text(requirements: Mapping[str, Any], task: Mapping[str, Any]) -> str:
    rendered = []
    for raw_key, value in requirements.items():
        key = str(raw_key)
        label = _REQUIREMENT_LABELS.get(key)
        if label is None or value is None:
            continue
        if isinstance(value, Mapping):
            allowed_signals = _requirement_signals(task, key)
            safe_values = [
                (str(signal), item)
                for signal, item in value.items()
                if str(signal) in allowed_signals and _finite_numeric(item)
            ]
            if not safe_values:
                continue
            shown = "、".join(
                f"{_safe(signal)} {_criterion_value(task, key, item, signal)}"
                for signal, item in safe_values
            )
        elif key == "goal_region_entry_required":
            if not isinstance(value, bool):
                continue
            shown = _criterion_value(task, key, value)
        else:
            if not _finite_numeric(value):
                continue
            shown = _criterion_value(task, key, value)
        if key == "goal_region_entry_required" and value is True:
            rendered.append(label)
        else:
            rendered.append(f"{label} {shown}")
    return "；".join(rendered) if rendered else "未提供"


def task_summary(task: Mapping[str, Any]) -> str:
    """Summarize only whitelisted, user-facing task fields."""

    task = _mapping(task)
    if not task:
        return "尚未提供任务说明。"
    signal_units = _mapping(task.get("signal_units"))
    measured = _named_signals(task.get("measured_signals"), signal_units)
    control_names = task.get("control_inputs")
    if not _items(control_names) and task.get("control_input"):
        control_names = [task["control_input"]]
    input_unit = task.get("input_units")
    control_units = {
        str(name): input_unit for name in _items(control_names) if input_unit
    }
    controls = _named_signals(control_names, control_units)

    input_low = task.get("input_min")
    input_high = task.get("input_max")
    if input_low is None or input_high is None:
        missing = []
        if input_low is None:
            missing.append("输入下界未提供")
        if input_high is None:
            missing.append("输入上界未提供")
        input_bounds = "；".join(missing)
    else:
        input_bounds = (
            f"{_number(input_low)}–{_number(input_high)}{_unit_suffix(input_unit)}"
        )

    output_low = task.get("output_min")
    output_high = task.get("output_max")
    output_unit = None
    measured_names = _items(task.get("measured_signals"))
    if len(measured_names) == 1:
        output_unit = signal_units.get(str(measured_names[0]))
    output_parts = []
    output_parts.append(
        "输出下界未提供"
        if output_low is None
        else f"下界 {_number(output_low)}{_unit_suffix(output_unit)}"
    )
    output_parts.append(
        "输出上界未提供"
        if output_high is None
        else f"上界 {_number(output_high)}{_unit_suffix(output_unit)}"
    )

    reference = task.get("reference")
    goal_region = task.get("goal_region")
    control_target = _mapping(task.get("control_target"))
    if reference is not None:
        target = f"{_number(reference)}{_unit_suffix(output_unit)}"
    elif goal_region:
        target = _safe(goal_region)
    elif control_target:
        target = _safe(
            ", ".join(f"{key}={value}" for key, value in control_target.items())
        )
    else:
        target = "未提供"

    description = task.get("description") or task.get("objective") or "未提供"
    requirements = _mapping(task.get("success_requirements"))
    return "\n\n".join(
        (
            f"**目标：** {_safe(description)}",
            f"**观测量：** {measured}",
            f"**控制输入：** {controls}",
            f"**输入范围：** {input_bounds}",
            f"**输出范围：** {'；'.join(output_parts)}",
            f"**声明目标：** {target}",
            f"**验收要求：** {_requirement_text(requirements, task)}",
        )
    )


def _confirmed_success(report: Mapping[str, Any]) -> bool:
    confirmation = _mapping(report.get("confirmation"))
    evaluation = _mapping(report.get("evaluation"))
    packet_fingerprint = str(confirmation.get("packet_fingerprint") or "")
    if not (
        report.get("status") == "performance_met"
        and confirmation.get("status") == "performance_met"
        and evaluation.get("status") == "performance_met"
        and evaluation.get("evaluation_split") == "fresh_confirmation"
        and packet_fingerprint
    ):
        return False
    packet_bound = any(
        isinstance(packet, Mapping)
        and packet.get("packet_fingerprint") == packet_fingerprint
        and packet.get("evaluation_split") == "fresh_confirmation"
        for packet in _items(report.get("evaluation_packets"))
    )
    replay_bound = any(
        isinstance(replay, Mapping)
        and replay.get("packet_fingerprint") == packet_fingerprint
        and replay.get("evaluation_split") == "fresh_confirmation"
        and replay.get("matches_previous") is True
        for replay in _items(report.get("evaluation_replays"))
    )
    return packet_bound and replay_bound


def _workspace_copy(report: Mapping[str, Any]) -> tuple[str, str]:
    status = str(report.get("status") or "")
    evaluation = _mapping(report.get("evaluation"))
    qualification = _mapping(report.get("qualification"))
    confirmation = _mapping(report.get("confirmation"))

    if status == "cancelled":
        return "任务已取消", "本次工作已结束；如需继续，请创建新的任务。"
    if status == "evaluation_recorded_pending_replay":
        return "评价已记录，等待复核", "复核完成前，已计算的结果不能作为最终结论。"
    if status == "awaiting_confirmation":
        return "开发评价完成，等待独立确认", "请用预留的全新试次确认冻结候选。"
    if status == "awaiting_provider":
        return (
            "需要重新选择数据来源",
            "当前协议已被拒绝，需在受支持入口选择新的数据来源。",
        )
    if _confirmed_success(report):
        return "独立确认已通过", "冻结方案已通过全新试次的独立确认。"
    if confirmation.get("status") == "performance_not_met":
        return "独立确认未通过", "全新确认试次未达到已声明的要求。"
    if confirmation.get("status") == "replay_mismatch":
        return "独立确认记录不一致", "评价复核与原记录不一致，不能发布结果。"
    if confirmation.get("status") == "pending_replay":
        return "独立确认待复核", "确认数据已记录，复核完成前不能发布结果。"
    if status == "capability_gap":
        tuning = _mapping(report.get("tuning"))
        if tuning.get("reason") == "no_strict_development_improvement":
            return "有界调优未找到可确认方案", "候选均未达到预先声明的改善门槛。"
        if qualification and qualification.get("status") != "offline_qualified":
            return "控制器资格审查未通过", "候选未通过已记录的离线资格审查。"
        return "当前能力范围不足", "现有证据或方法不足以安全完成此任务。"
    if evaluation.get("status") == "performance_not_met":
        stable = _mapping(evaluation.get("stability_gate")).get("passed") is True
        evidence = _mapping(evaluation.get("evidence_gate")).get("passed", True) is True
        if stable and evidence:
            return "稳定，但性能尚未达标", "方案保持稳定，但已记录性能未达到目标。"
        return "评价未通过", "稳定性或证据门未通过，当前方案不能进入结果确认。"
    if (
        evaluation.get("status") == "performance_met"
        and evaluation.get("evaluation_split") == "development"
    ):
        return "开发评价达到要求", "这是软件开发评价；尚不等同于全新独立确认。"
    if evaluation.get("status") == "performance_met":
        return "确认结果尚不能发布", "确认记录尚未完成严格绑定与复核。"
    if qualification and qualification.get("status") != "offline_qualified":
        return "控制器资格审查未通过", "候选未通过已记录的离线资格审查。"
    if status in {"awaiting_evidence", "protocol_ready", "awaiting_operator_report"}:
        return "证据不足，需继续准备数据", "请按当前协议准备并提交可审计数据。"
    if status == "intake":
        return "先说明目标和边界", "补全任务目标、信号和安全边界后再继续。"
    if status == "diagnostic":
        return (
            "补充对象的已知现象",
            "请说明稳定性、时延、耦合等已观察现象；不知道的项目可以明确标注。",
        )
    if status in _STAGE_BY_STATUS:
        return "正在生成并验证方案", "按当前提示完成下一项验证动作。"
    return "当前状态无法安全识别", "请刷新报告；在状态明确前不会启用操作。"


def project_workspace(report: Mapping[str, Any]) -> dict[str, Any]:
    """Project an authoritative Kernel report into the novice workspace model."""

    report = _mapping(report)
    contract = _mapping(report.get("input_contract"))
    status = str(report.get("status") or "")
    raw_action = str(contract.get("action") or "")
    action = _ACTION_ALIASES.get(raw_action, raw_action)
    disabled = bool(contract.get("disabled_reason"))
    actionable = bool(
        action
        and action in _KNOWN_ACTIONS
        and status in _STAGE_BY_STATUS
        and status not in _TERMINAL_STATES
        and not report.get("read_only")
        and not disabled
    )
    modes = [str(item) for item in _items(contract.get("allowed_modes"))]
    title, explanation = _workspace_copy(report)
    if report.get("read_only"):
        title = f"只读 · {title}"
        explanation = f"{explanation} 此任务是只读记录，因此不能提交动作或取消任务。"
    action_title, action_help = _ACTION_COPY.get(
        action, ("当前动作不可用", "请刷新报告后重试。")
    )
    result_visible = bool(
        isinstance(report.get("evaluation"), Mapping)
        or isinstance(report.get("qualification"), Mapping)
        or isinstance(report.get("confirmation"), Mapping)
        or status in _TERMINAL_STATES
    )
    return {
        "stage": _STAGE_BY_STATUS.get(status, 0),
        "title": title,
        "explanation": explanation,
        "action": action,
        "action_title": action_title,
        "action_help": action_help,
        "actionable": actionable,
        "advanced": actionable
        and modes == ["json"]
        and action not in {"record_operator_report", "ingest_upload"},
        "result_visible": result_visible,
        "task_summary": task_summary(_mapping(report.get("task"))),
    }


def steps_html(report: Mapping[str, Any]) -> str:
    """Render a semantic, noninteractive four-step progress indicator."""

    report = _mapping(report)
    task = _mapping(report.get("task"))
    task_done = bool(
        task.get("budget_confirmed")
        or report.get("protocols")
        or report.get("evidence")
        or report.get("route")
        or report.get("features")
        or report.get("controller")
        or report.get("qualification")
        or report.get("evaluation")
    )
    data_done = bool(
        report.get("route")
        or report.get("features")
        or report.get("controller")
        or report.get("qualification")
        or report.get("evaluation")
    )
    synthesis_done = isinstance(report.get("evaluation"), Mapping)
    if not task_done:
        current = 0
    elif not data_done:
        current = 1
    elif not synthesis_done:
        current = 2
    else:
        current = 3
    labels = ("说明目标", "准备数据", "生成并验证方案", "查看结果")
    rows = []
    for index, label in enumerate(labels):
        state = (
            "complete"
            if index < current
            else "current"
            if index == current
            else "pending"
        )
        current_attr = ' aria-current="step"' if index == current else ""
        rows.append(
            f'<li class="guided-step {state}"{current_attr}>'
            f'<span aria-hidden="true">{index + 1}</span><span>{label}</span></li>'
        )
    return '<ol class="guided-steps" aria-label="任务进度">' + "".join(rows) + "</ol>"


def _status_label(status: Any) -> str:
    return {
        "performance_met": "已通过",
        "performance_not_met": "未通过",
        "pending_replay": "待复核",
        "replay_mismatch": "复核不一致",
    }.get(str(status or ""), "未记录")


def _percent(value: Any) -> str:
    if isinstance(value, int | float) and not isinstance(value, bool):
        return f"{100 * float(value):g}%"
    return "未记录"


def _metric_target(
    report: Mapping[str, Any], metric: str, signal: str | None = None
) -> str:
    requirement_names = _METRIC_REQUIREMENTS.get(metric, ())
    if not requirement_names:
        if metric in {
            "recovered_to_hold",
            "disturbance_event_verified",
        }:
            return "必须为 是"
        return "未声明"
    task = _mapping(report.get("task"))
    requirements = _mapping(task.get("success_requirements"))
    requirement = next(
        (name for name in requirement_names if requirements.get(name) is not None),
        None,
    )
    if requirement is None:
        return "未声明"
    value = requirements[requirement]
    if isinstance(value, Mapping):
        value = value.get(signal) if signal is not None else None
    if value is None:
        return "未声明"
    if requirement == "goal_region_entry_required":
        return "必须为 是" if value is True else "未声明"
    relation = "不少于" if requirement.endswith(("_min", "_min_s")) else "不超过"
    return f"{relation} {_criterion_value(task, requirement, value, signal)}"


def _metric_value(
    report: Mapping[str, Any], metric: str, value: Any, signal: str | None = None
) -> str:
    if isinstance(value, bool):
        return "是" if value else "否"
    task = _mapping(report.get("task"))
    if metric in {"saturation_fraction"} and isinstance(value, int | float):
        return _percent(value)
    if metric in {
        "settling_time_s",
        "hold_duration_s",
        "saturation_duration_s",
        "final_hold_duration_s",
        "recovery_time_s",
        "post_recovery_hold_duration_s",
    }:
        unit = "s"
    elif metric == "iae":
        base = _mapping(task.get("signal_units")).get(signal or "")
        unit = f"{base}·s" if base else ""
    elif metric in {"peak_abs_input", "raw_peak_abs_input"}:
        unit = str(task.get("input_units") or "")
    elif metric in {"final_abs_error", "overshoot", "peak_abs_output"}:
        unit = str(_mapping(task.get("signal_units")).get(signal or "") or "")
    else:
        unit = ""
    return f"{_number(value)}{_unit_suffix(unit)}"


def _recorded_metric_rows(
    report: Mapping[str, Any], evaluation: Mapping[str, Any]
) -> list[list[Any]]:
    rows: list[list[Any]] = []
    for trial_index, trial in enumerate(_items(evaluation.get("trials")), 1):
        if not isinstance(trial, Mapping):
            continue
        trial_id = _plain(trial.get("trial_id") or f"第 {trial_index} 次")
        metrics = _mapping(trial.get("metrics"))
        for group_name, group in (
            ("输出", _mapping(metrics.get("channels"))),
            ("输入", _mapping(metrics.get("inputs"))),
        ):
            for signal, values in group.items():
                if not isinstance(values, Mapping):
                    continue
                for metric, value in values.items():
                    if metric not in _METRIC_LABELS or value is None:
                        continue
                    rows.append(
                        [
                            f"{_plain(signal)} · {_METRIC_LABELS[metric]}",
                            _metric_target(report, metric, str(signal)),
                            _metric_value(report, metric, value, str(signal)),
                            f"{trial_id} 的已记录{group_name}指标",
                        ]
                    )
        for metric in _TOP_LEVEL_METRICS:
            if metrics.get(metric) is not None:
                rows.append(
                    [
                        _METRIC_LABELS[metric],
                        _metric_target(report, metric),
                        _metric_value(report, metric, metrics[metric]),
                        f"{trial_id} 的已记录指标",
                    ]
                )
    return rows


def result_rows(
    report: Mapping[str, Any], selection: str | None = None
) -> list[list[Any]]:
    """Return recorded result rows without deriving metrics from trajectories."""

    report = _mapping(report)
    evaluation = _mapping(report.get("evaluation"))
    confirmation = _mapping(report.get("confirmation"))
    if not evaluation and not confirmation:
        return []
    split = str(evaluation.get("evaluation_split") or "")
    phase = "独立确认" if split == "fresh_confirmation" or confirmation else "开发评价"
    if report.get("status") == "evaluation_recorded_pending_replay":
        status = "pending_replay"
    else:
        status = (
            confirmation.get("status") if confirmation else evaluation.get("status")
        )
    rows: list[list[Any]] = [
        [
            "结论",
            "通过已记录的稳定性、证据与性能门",
            _status_label(status),
            f"{phase}的已记录判断",
        ]
    ]
    performance = _mapping(evaluation.get("performance_gate"))
    if evaluation.get("success_rate") is not None:
        minimum = performance.get("success_rate_min")
        rows.append(
            [
                "试次成功率",
                _percent(minimum) if minimum is not None else "未声明",
                _percent(evaluation.get("success_rate")),
                f"{phase}的已记录汇总",
            ]
        )
    if evaluation.get("wilson_lower_bound_95") is not None:
        rows.append(
            [
                "成功率 95% Wilson 下界",
                _percent(performance.get("success_rate_min"))
                if performance.get("success_rate_min") is not None
                else "未声明",
                _percent(evaluation.get("wilson_lower_bound_95")),
                "已记录的保守成功率下界",
            ]
        )
    metric_evaluation = evaluation
    if selection is not None:
        _, selected_trial = _selected_trial(report, selection)
        if selected_trial:
            trial_id = str(selected_trial.get("trial_id") or "")
            metric_trial = selected_trial
            if not _mapping(selected_trial.get("metrics")) and trial_id:
                metric_trial = next(
                    (
                        trial
                        for trial in _items(evaluation.get("trials"))
                        if isinstance(trial, Mapping)
                        and str(trial.get("trial_id") or "") == trial_id
                    ),
                    selected_trial,
                )
            metric_evaluation = {**evaluation, "trials": [metric_trial]}
    metric_rows = _recorded_metric_rows(report, metric_evaluation)
    rows.extend(metric_rows)
    if evaluation and not metric_rows:
        rows.append(
            [
                "试次指标",
                "按冻结的评价合同",
                "未记录",
                "当前评价没有提供逐试次指标；未从轨迹重新计算。",
            ]
        )
    return rows


def _packet_order(report: Mapping[str, Any]) -> list[int]:
    packets = _items(report.get("evaluation_packets"))
    linked = str(_mapping(report.get("confirmation")).get("packet_fingerprint") or "")
    preferred: list[int] = []
    if linked:
        preferred.extend(
            index
            for index, packet in enumerate(packets)
            if isinstance(packet, Mapping)
            and packet.get("packet_fingerprint") == linked
            and packet.get("evaluation_split") == "fresh_confirmation"
        )
    evaluation = _mapping(report.get("evaluation"))
    current = str(evaluation.get("packet_fingerprint") or "")
    if current and evaluation.get("evaluation_split") == "development":
        preferred.extend(
            index
            for index, packet in enumerate(packets)
            if isinstance(packet, Mapping)
            and packet.get("packet_fingerprint") == current
            and packet.get("evaluation_split") == "development"
        )
    preferred.extend(
        index
        for index in reversed(range(len(packets)))
        if isinstance(packets[index], Mapping)
        and packets[index].get("evaluation_split") == "development"
    )
    preferred.extend(reversed(range(len(packets))))
    return list(dict.fromkeys(preferred))


def evaluation_options(report: Mapping[str, Any]) -> list[tuple[str, str]]:
    """List stable packet/trial selections with their true evaluation phase."""

    report = _mapping(report)
    packets = _items(report.get("evaluation_packets"))
    labels = {
        "development": "开发评价",
        "fresh_confirmation": "独立确认",
        "replay": "重放检查",
    }
    options: list[tuple[str, str]] = []
    for packet_index in _packet_order(report):
        packet = packets[packet_index]
        split = str(packet.get("evaluation_split") or "")
        phase = labels.get(split, "未识别评价")
        for trial_index, trial in enumerate(_items(packet.get("trials"))):
            if not isinstance(trial, Mapping):
                continue
            trial_id = _plain(trial.get("trial_id") or f"第 {trial_index + 1} 次")
            options.append(
                (
                    f"{phase} · 第 {trial_index + 1} 次（{trial_id}）",
                    f"{packet_index}:{trial_index}",
                )
            )
    return options


def _selected_trial(
    report: Mapping[str, Any], selection: str | None
) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    packets = _items(report.get("evaluation_packets"))
    allowed = {value for _, value in evaluation_options(report)}
    chosen = str(selection or "")
    if chosen not in allowed:
        options = evaluation_options(report)
        chosen = options[0][1] if options else ""
    try:
        packet_index, trial_index = (int(item) for item in chosen.split(":"))
        packet = packets[packet_index]
        trial = _items(packet.get("trials"))[trial_index]
    except (AttributeError, IndexError, TypeError, ValueError):
        return {}, {}
    if not isinstance(packet, Mapping) or not isinstance(trial, Mapping):
        return {}, {}
    return packet, trial


def signal_options(report: Mapping[str, Any], selection: str | None) -> list[str]:
    """List output signals present in the selected recorded trial."""

    _, trial = _selected_trial(_mapping(report), selection)
    outputs = _mapping(_mapping(trial.get("trajectory")).get("outputs"))
    return [str(name) for name, values in outputs.items() if isinstance(values, list)]


def _signal_unit(
    report: Mapping[str, Any], trial: Mapping[str, Any], signal: str, *, control: bool
) -> str:
    task = _mapping(report.get("task"))
    if control:
        unit = task.get("input_units")
    else:
        unit = _mapping(task.get("signal_units")).get(signal)
    for container in (trial, _mapping(trial.get("trajectory"))):
        units = _mapping(container.get("units"))
        if control:
            unit = units.get("input", unit)
        else:
            outputs = _mapping(units.get("outputs"))
            unit = outputs.get(signal, units.get(signal, unit))
    text = str(unit or "").strip()
    return "" if text == "unspecified" else _plain(text)


def _base_figure(title: str) -> go.Figure:
    figure = go.Figure()
    figure.update_layout(
        height=320,
        margin={"l": 48, "r": 18, "t": 48, "b": 42},
        title=title,
        xaxis_title="时间 (s)",
    )
    return figure


def evaluation_figures(
    report: Mapping[str, Any],
    selection: str | None = None,
    signal: str | None = None,
) -> tuple[go.Figure, go.Figure]:
    """Plot one recorded output/reference and its recorded control inputs."""

    report = _mapping(report)
    output_figure = _base_figure("输出与目标")
    control_figure = _base_figure("控制输入")
    _, trial = _selected_trial(report, selection)
    trajectory = _mapping(trial.get("trajectory"))
    time_s = trajectory.get("time_s")
    if not isinstance(time_s, list):
        return output_figure, control_figure
    outputs = _mapping(trajectory.get("outputs"))
    available = [
        str(name) for name, values in outputs.items() if isinstance(values, list)
    ]
    selected = str(signal or "")
    if selected not in available:
        selected = available[0] if available else ""
    values = outputs.get(selected)
    if isinstance(values, list) and len(values) == len(time_s):
        output_figure.add_scatter(
            x=time_s, y=values, mode="lines", name=_plain(selected)
        )
        references = _mapping(trajectory.get("references"))
        reference = references.get(selected)
        if isinstance(reference, list) and len(reference) == len(time_s):
            output_figure.add_scatter(
                x=time_s,
                y=reference,
                mode="lines",
                line={"dash": "dash"},
                name="目标值",
            )
        output_unit = _signal_unit(report, trial, selected, control=False)
        output_figure.update_yaxes(
            title=f"{_plain(selected)} ({output_unit})"
            if output_unit
            else _plain(selected)
        )
    controls = _mapping(trajectory.get("control_inputs"))
    control_units = []
    for name, control_values in controls.items():
        if not isinstance(control_values, list) or len(control_values) != len(time_s):
            continue
        clean_name = str(name)
        control_figure.add_scatter(
            x=time_s, y=control_values, mode="lines", name=_plain(clean_name)
        )
        unit = _signal_unit(report, trial, clean_name, control=True)
        if unit and unit not in control_units:
            control_units.append(unit)
    control_figure.update_yaxes(
        title=f"控制输入 ({' / '.join(control_units)})" if control_units else "控制输入"
    )
    return output_figure, control_figure


def upload_feedback(report: Mapping[str, Any]) -> str:
    """Explain the latest authoritative upload audit and its next repair."""

    attempts = _items(_mapping(report).get("upload_attempts"))
    if not attempts or not isinstance(attempts[-1], Mapping):
        return "还没有上传检查记录。"
    audit = _mapping(attempts[-1].get("audit")) or attempts[-1]
    gates = [gate for gate in _items(audit.get("gates")) if isinstance(gate, Mapping)]
    passed = sum(gate.get("status") == "passed" for gate in gates)
    unreached = sum(gate.get("status") == "not_reached" for gate in gates)
    status = str(audit.get("status") or "")
    if status == "accepted":
        return f"上传已接受：已通过 {passed} 项检查，没有把被拒数据计入证据。"
    failed_id = str(audit.get("failed_gate") or "")
    definition = GATE_DEFINITIONS.get(failed_id)
    failed_gate = next((gate for gate in gates if gate.get("id") == failed_id), {})
    label = definition[0] if definition else failed_gate.get("label") or "未知检查项"
    redo = (
        definition[1]
        if definition
        else failed_gate.get("redo") or "请按当前协议重新准备数据。"
    )
    binding = _mapping(report.get("registered_case_binding"))
    if failed_id == "file_format" and binding.get("evidence_mode") == "exercise_bundle":
        redo = "请下载并上传当前协议生成的完整教学练习 ZIP 包，保留包内文件。"
    details = str(failed_gate.get("details") or audit.get("message") or "").strip()
    parts = [
        f"本次上传未接受：在“{_safe(label)}”处未通过。",
        f"建议：{_safe(redo)}",
        f"检查进度：已通过 {passed} 项，尚未检查 {unreached} 项。",
    ]
    if details:
        parts.append(f"技术信息：{_safe(details)}")
    return "\n\n".join(parts)


def trace_preview(report: Mapping[str, Any]) -> tuple[list[str], list[list[Any]]]:
    """Preview at most twenty samples from the latest accepted public trace."""

    for evidence in reversed(_items(_mapping(report).get("evidence"))):
        if not isinstance(evidence, Mapping):
            continue
        if "status" in evidence and evidence.get("status") not in {
            "accepted",
            "passed",
            "valid",
        }:
            continue
        trace = _mapping(evidence.get("trace"))
        time_s = trace.get("time_s")
        signals = _mapping(trace.get("signals"))
        if not isinstance(time_s, list) or not time_s or not signals:
            continue
        valid_signals = [
            str(name)
            for name, values in signals.items()
            if isinstance(values, list) and len(values) == len(time_s)
        ]
        if not valid_signals:
            continue
        trial = _plain(
            evidence.get("trial_id") or trace.get("trial_id") or "未标注试次"
        )
        headers = ["时间 (s)", "试次", *[_plain(name) for name in valid_signals]]
        rows = [
            [time_s[index], trial, *[signals[name][index] for name in valid_signals]]
            for index in range(min(20, len(time_s)))
        ]
        return headers, rows
    return ["时间 (s)"], []


def protocol_summary(report: Mapping[str, Any], *, request_upload: bool = True) -> str:
    """Summarize the active protocol without exposing a hardware command."""

    report = _mapping(report)
    protocols = _items(report.get("protocols"))
    active_fingerprint = str(report.get("active_protocol_fingerprint") or "")
    protocol = next(
        (
            item
            for item in protocols
            if isinstance(item, Mapping)
            and active_fingerprint
            and item.get("protocol_fingerprint") == active_fingerprint
        ),
        None,
    )
    if protocol is None:
        return "当前还没有可执行的实验协议。"
    units = _mapping(protocol.get("units"))
    output_units = _mapping(units.get("outputs"))
    requested = _named_signals(protocol.get("requested_signals"), output_units)
    control_names = protocol.get("control_inputs")
    control_units = {str(name): units.get("input") for name in _items(control_names)}
    controls = _named_signals(control_names, control_units)
    repeats = protocol.get("repeats")
    sample_period = protocol.get("sample_period_s")
    exercise = (
        _mapping(report.get("registered_case_binding")).get("evidence_mode")
        == "exercise_bundle"
    )
    file_type = "教学练习 ZIP" if exercise else "CSV 或 JSON"
    lines = [
        f"**观测信号：** {requested}",
        f"**控制输入记录：** {controls}",
        f"**独立重复：** {_number(repeats) if repeats is not None else '未提供'} 次",
        f"**采样间隔：** {_number(sample_period) if sample_period is not None else '未提供'} s",
        f"**数据类型：** {_safe(protocol.get('data_kind') or '未提供')}；上传文件为 {file_type}",
    ]
    if request_upload:
        lines.append("请下载当前操作包，按其中的协议采集或准备数据后再上传。")
    return "\n".join(lines)


__all__ = [
    "evaluation_figures",
    "evaluation_options",
    "project_workspace",
    "protocol_summary",
    "result_rows",
    "signal_options",
    "steps_html",
    "task_summary",
    "trace_preview",
    "upload_feedback",
]
