from __future__ import annotations

import json
import math
from typing import Any

from cfdc.diagnosis import (
    OpenAICompatibleDiagnosticAdapter,
    clarification_question_map,
    continue_diagnostic_session,
    start_diagnostic_session,
)
from cfdc.models import CFDCRunReport, DiagnosticSessionState, SystemDescription
from cfdc.runtime import run_cfdc_route


ROUTE_CHOICES = {
    "自然语言自动分析（主流程）": "generic",
    "开发验证 · CartPole 完整流程": "cartpole",
    "开发验证 · CartPole 安全边界": "cartpole-boundary",
    "开发验证 · VTOL 位置控制": "vtol-position",
    "开发验证 · VTOL 安全边界": "vtol-boundary",
    "开发验证 · VTOL 高度控制": "vtol-altitude",
    "开发验证 · VTOL 悬停控制": "vtol-hover",
    "开发验证 · VTOL 参数变化": "vtol-variation",
}

# Keep old labels valid for saved browser/API calls without showing them in the UI.
LEGACY_ROUTE_LABELS = {
    "自动选择": "generic",
    "CartPole 验证": "cartpole",
    "CartPole 边界": "cartpole-boundary",
    "VTOL 位置控制": "vtol-position",
    "VTOL 安全边界": "vtol-boundary",
    "VTOL 高度控制": "vtol-altitude",
    "VTOL 悬停控制": "vtol-hover",
    "VTOL 参数变化": "vtol-variation",
}

STATUS_LABELS = {
    "need_more_information": "需要补充信息",
    "feature_extraction_failed": "特征提取未通过",
    "controller_candidate_ready": "已完成诊断",
    "accepted": "已接受",
    "rejected": "已拒绝",
    "frozen": "控制器已冻结",
    "completed": "仿真流程完成",
}

DIAGNOSIS_LABELS = {
    "open_loop_stability": "开环稳定性",
    "minimum_phase": "相位特性",
    "significant_delay": "显著时延",
    "relative_degree": "相对阶次",
    "controllability_observability": "能控能观性",
    "nonlinearity_strength": "非线性强度",
    "coupling_severity": "耦合结构",
    "uncertainty_magnitude": "不确定性",
}

STAGES = [
    ("问题理解", lambda report: report.diagnosis is not None),
    ("八字段诊断", lambda report: bool(report.diagnosis and report.diagnosis.complete)),
    ("动力学归类", lambda report: report.classification is not None),
    ("安全实验", lambda report: bool(report.experiment_results)),
    ("核心特征", lambda report: bool(report.features)),
    ("初始控制器", lambda report: report.controller is not None),
    ("闭环调优", lambda report: report.algorithm1_state is not None),
    (
        "在线适应",
        lambda report: bool(
            report.feature_tracking_updates
            or report.adapted_controller_performance is not None
        ),
    ),
]


def parse_names(value: str) -> list[str]:
    return [item.strip() for item in value.replace("\n", ",").split(",") if item.strip()]


def parse_safety_bounds(value: str) -> dict[str, float]:
    bounds: dict[str, float] = {}
    for line in value.replace(",", "\n").splitlines():
        if not line.strip():
            continue
        key, separator, raw = line.partition("=")
        clean_key = key.strip()
        if not separator or not clean_key or not raw.strip():
            raise ValueError(f"安全边界格式错误：{line!r}，应使用 name=value")
        if clean_key in bounds:
            raise ValueError(f"安全边界 {clean_key!r} 重复定义")
        try:
            parsed = float(raw)
        except ValueError as exc:
            raise ValueError(f"安全边界 {clean_key!r} 必须是数字") from exc
        if not math.isfinite(parsed):
            raise ValueError(f"安全边界 {clean_key!r} 必须是有限数字")
        bounds[clean_key] = parsed
    return bounds


def build_adapter(
    use_llm: bool,
    base_url: str,
    model: str,
    api_key: str,
):
    if not use_llm:
        return None
    return OpenAICompatibleDiagnosticAdapter(
        base_url=base_url.strip() or None,
        model=model.strip() or None,
        api_key=api_key.strip() or None,
    )


def _compact_report(report: CFDCRunReport) -> dict[str, Any]:
    payload = report.model_dump(mode="json")
    for result in payload.get("experiment_results", []):
        trace = result.get("trace", {})
        trace["sample_count"] = len(trace.get("time_s", []))
        trace["signal_names"] = sorted(trace.get("signals", {}))
        trace.pop("time_s", None)
        trace.pop("signals", None)
    for trial in payload.get("trial_reports", []):
        trial["sample_count"] = len(trial.pop("samples", []))
    boundary = payload.get("cartpole_boundary")
    if boundary:
        nested_trials = list(boundary.get("candidate_trials", []))
        rollback_trial = boundary.get("rollback_trial")
        if rollback_trial:
            nested_trials.append(rollback_trial)
        for trial in nested_trials:
            trial["sample_count"] = len(trial.pop("samples", []))
    search_state = payload.get("safe_gain_search_state")
    if search_state:
        history = search_state.pop("history", [])
        search_state["history_count"] = len(history)
        search_state["history_tail"] = history[-5:]
    return payload


def _run_ready_session(
    session: DiagnosticSessionState,
    adapter,
    include_trajectory: bool,
) -> CFDCRunReport:
    if session.status == "ready_for_experiments":
        if session.current_diagnosis is None or session.semantic_selection is None:
            raise RuntimeError("ready diagnostic session is missing cached routing evidence")

        class SessionReplayAdapter:
            def diagnose(self, description):
                del description
                return session.current_diagnosis.model_dump(mode="json")

            def select_profile(self, description, diagnosis, classification, catalog):
                del description, diagnosis, classification, catalog
                return session.semantic_selection.model_dump(mode="json")

        return run_cfdc_route(
            session.route_id,
            description=session.accumulated_description,
            diagnostic_adapter=SessionReplayAdapter(),
            include_trajectory=include_trajectory,
        )
    return run_cfdc_route(
        session.route_id,
        diagnostic_session_state=session,
        diagnostic_adapter=adapter,
        include_trajectory=include_trajectory,
    )


def start_app_run(
    description: str,
    observed_outputs: str,
    actuators: str,
    safety_bounds: str,
    route_label: str,
    use_llm: bool,
    base_url: str,
    model: str,
    api_key: str,
    include_trajectory: bool = False,
) -> tuple[CFDCRunReport, dict[str, Any]]:
    route_id = ROUTE_CHOICES.get(
        route_label,
        LEGACY_ROUTE_LABELS.get(route_label, route_label or "generic"),
    )
    known_route_ids = set(ROUTE_CHOICES.values())
    if route_id not in known_route_ids:
        raise ValueError(f"未知运行方式：{route_label!r}")
    if route_id != "generic":
        report = run_cfdc_route(
            route_id,
            diagnostic_adapter=None,
            include_trajectory=include_trajectory,
        )
        return report, {
            "session": None,
            "use_llm": False,
            "base_url": "",
            "model": "",
            "api_key": "",
            "include_trajectory": include_trajectory,
            "input_source": "preregistered_developer_scenario",
        }

    if not description.strip():
        raise ValueError("请描述需要控制的对象、可观察输出和可用执行器。")
    adapter = build_adapter(use_llm, base_url, model, api_key)

    system = SystemDescription(
        text=description.strip(),
        observed_outputs=parse_names(observed_outputs),
        actuators=parse_names(actuators),
        safety_bounds=parse_safety_bounds(safety_bounds),
    )
    report = run_cfdc_route(
        route_id,
        description=system,
        diagnostic_adapter=adapter,
        include_trajectory=include_trajectory,
    )
    session = None
    if report.status == "need_more_information":
        if report.diagnosis is None:
            raise RuntimeError("incomplete route report is missing its diagnosis")
        session = start_diagnostic_session(
            system,
            route_id=route_id,
            diagnostic_adapter=adapter,
            diagnosis=report.diagnosis,
        )
        report = report.model_copy(update={"diagnostic_session": session})
    awaiting_clarification = session is not None
    return report, {
        "session": session.model_dump(mode="json") if session is not None else None,
        "use_llm": use_llm if awaiting_clarification else False,
        "base_url": base_url if awaiting_clarification else "",
        "model": model if awaiting_clarification else "",
        "api_key": api_key if awaiting_clarification else "",
        "include_trajectory": include_trajectory,
        "input_source": "natural_language",
    }


def continue_app_run(
    app_state: dict[str, Any],
    answers: list[str],
    supplemental_description: str,
) -> tuple[CFDCRunReport, dict[str, Any]]:
    if not app_state or not app_state.get("session"):
        raise ValueError("当前没有等待回答的诊断会话。")
    session = DiagnosticSessionState.model_validate(app_state["session"])
    adapter = build_adapter(
        bool(app_state.get("use_llm")),
        str(app_state.get("base_url", "")),
        str(app_state.get("model", "")),
        str(app_state.get("api_key", "")),
    )
    question_ids = list(clarification_question_map(session))
    question_map = clarification_question_map(session)
    keyed_answers = {
        question_id: answer.strip()
        for question_id, answer in zip(question_ids, answers)
        if answer.strip()
    }
    observed_outputs = list(session.accumulated_description.observed_outputs)
    actuators = list(session.accumulated_description.actuators)
    for question_id, answer in keyed_answers.items():
        question = question_map[question_id].lower()
        if "watch or record" in question and answer not in observed_outputs:
            observed_outputs.append(answer)
        if "physical action or device" in question and answer not in actuators:
            actuators.append(answer)
    if observed_outputs != session.accumulated_description.observed_outputs or actuators != session.accumulated_description.actuators:
        session = session.model_copy(
            update={
                "accumulated_description": session.accumulated_description.model_copy(
                    update={
                        "observed_outputs": observed_outputs,
                        "actuators": actuators,
                    }
                )
            }
        )
    updated = continue_diagnostic_session(
        session,
        keyed_answers,
        supplemental_description=supplemental_description.strip() or None,
        diagnostic_adapter=adapter,
    )
    report = _run_ready_session(
        updated,
        adapter,
        bool(app_state.get("include_trajectory")),
    )
    if updated.status == "collecting_information":
        report = report.model_copy(update={"diagnostic_session": updated})
    next_state = dict(app_state)
    next_state["session"] = (
        updated.model_dump(mode="json")
        if updated.status == "collecting_information"
        else None
    )
    if next_state["session"] is None:
        next_state.update(
            {
                "use_llm": False,
                "base_url": "",
                "model": "",
                "api_key": "",
            }
        )
    return report, next_state


def diagnosis_rows(report: CFDCRunReport) -> list[list[Any]]:
    if report.diagnosis is None:
        return []
    payload = report.diagnosis.model_dump(mode="json")
    rows = []
    for field_id, label in DIAGNOSIS_LABELS.items():
        field = payload[field_id]
        estimate = field.get("estimated_order")
        assessment = field["assessment"]
        if estimate is not None:
            assessment = f"{assessment}（估计 {estimate} 阶）"
        rows.append([
            label,
            assessment,
            f"{100 * field['confidence']:.0f}%",
            "；".join(field.get("evidence", [])),
        ])
    return rows


def route_rows(report: CFDCRunReport) -> list[list[str]]:
    rows: list[list[str]] = []
    if report.classification:
        rows.extend([
            ["动力学原型", str(report.classification.primary_class)],
            ["控制架构", report.classification.control_architecture],
        ])
    if report.semantic_selection:
        rows.extend([
            ["仿真 Profile", report.semantic_selection.simulation_profile_id],
            ["特征 Bundle", report.semantic_selection.feature_bundle_id],
            ["核心特征", ", ".join(report.semantic_selection.selected_feature_ids)],
        ])
    if report.compiled_route:
        rows.append(["Route 编译", "可执行" if report.compiled_route.executable else "存在能力缺口"])
    return rows


def experiment_rows(report: CFDCRunReport) -> list[list[Any]]:
    return [
        [
            index + 1,
            str(record.primitive),
            record.repeat_index,
            ", ".join(record.estimates),
            len(record.trace.time_s),
            ", ".join(sorted(record.trace.signals)),
        ]
        for index, record in enumerate(report.experiment_results)
    ]


def feature_rows(report: CFDCRunReport) -> list[list[Any]]:
    rows = []
    for feature in report.features:
        value = feature.value
        rendered = json.dumps(value, ensure_ascii=False) if isinstance(value, list) else f"{value:.6g}"
        interval = (
            "矩阵特征"
            if feature.lower_bound is None
            else f"[{feature.lower_bound:.6g}, {feature.upper_bound:.6g}]"
        )
        rows.append([
            feature.feature_id,
            rendered,
            feature.units,
            interval,
            f"{100 * feature.confidence:.0f}%",
            feature.method,
        ])
    return rows


def controller_rows(report: CFDCRunReport) -> list[list[str]]:
    if report.controller is None:
        return []
    rows = [["架构", report.controller.architecture]]
    rows.extend([f"增益 · {name}", f"{value:.6g}"] for name, value in report.final_gains.items())
    rows.extend([f"前馈 · {name}", f"{value:.6g}"] for name, value in report.final_feedforward.items())
    rows.append(["发布状态", report.controller.status])
    return rows


def tuning_rows(report: CFDCRunReport) -> list[list[Any]]:
    rows: list[list[Any]] = []
    if report.algorithm1_state:
        rows.append([
            "Algorithm 1",
            report.algorithm1_state.status,
            report.algorithm1_state.iteration_count,
            report.algorithm1_state.completion_reason or "-",
        ])
    for update in report.feature_tracking_updates:
        rows.append([
            update.feature_id,
            "已更新" if update.controller_update_required else "仅跟踪",
            f"{100 * update.relative_change:.2f}%",
            f"{update.previous_value:.6g} → {update.updated_value:.6g}",
        ])
    return rows


def performance_rows(report: CFDCRunReport) -> list[list[Any]]:
    rows = []
    for label, performance in (
        ("变化后 · 原控制器", report.stale_controller_performance),
        ("变化后 · 适应控制器", report.adapted_controller_performance),
    ):
        if performance is None:
            continue
        rows.append([
            label,
            "通过" if performance.success else "未通过",
            f"{performance.abs_final_error:.6g}",
            "-" if performance.settling_time_s is None else f"{performance.settling_time_s:.3f}",
            f"{100 * performance.saturation_fraction:.2f}%",
            ", ".join(performance.violations) or "无",
        ])
    return rows


def stage_progress_html(report: CFDCRunReport) -> str:
    blocked = report.status in {"feature_extraction_failed", "rejected", "frozen"}
    waiting = report.status == "need_more_information"
    items = []
    first_pending_seen = False
    for index, (label, predicate) in enumerate(STAGES, start=1):
        complete = bool(predicate(report))
        state = "done" if complete else "pending"
        if not complete and not first_pending_seen:
            first_pending_seen = True
            if waiting:
                state = "waiting"
            elif blocked:
                state = "blocked"
        icon = "✓" if complete else str(index)
        items.append(
            f'<div class="flow-step {state}"><span>{icon}</span><small>{label}</small></div>'
        )
    return f'<div class="flow-strip">{"".join(items)}</div>'


def summary_html(report: CFDCRunReport) -> str:
    archetype = (
        str(report.classification.primary_class).replace("class_", "Class ").replace("_", " ")
        if report.classification
        else "待确认"
    )
    profile = (
        report.semantic_selection.simulation_profile_id
        if report.semantic_selection
        else "待选择"
    )
    quality = (
        report.feature_quality_decision.decision
        if report.feature_quality_decision
        else "未执行"
    )
    repeats = max(
        (record.repeat_index for record in report.experiment_results),
        default=0,
    )
    cards = [
        ("动力学原型", archetype),
        ("仿真 Profile", profile),
        ("核心特征", str(len(report.features))),
        ("实验重复", str(repeats) if repeats else "-"),
        ("质量门", quality),
    ]
    return '<div class="metric-grid">' + "".join(
        f'<div class="metric"><small>{label}</small><strong>{value}</strong></div>'
        for label, value in cards
    ) + "</div>"


def performance_html(report: CFDCRunReport) -> str:
    comparisons = [
        ("原控制器", report.stale_controller_performance),
        ("适应控制器", report.adapted_controller_performance),
    ]
    available = [(label, item) for label, item in comparisons if item is not None]
    if not available:
        return '<div class="empty-result">当前流程尚未生成系统变化后的性能对照。</div>'
    max_error = max(item.abs_final_error for _, item in available) or 1.0
    rows = []
    for label, item in available:
        width = max(3.0, 100.0 * item.abs_final_error / max_error)
        outcome = "安全通过" if item.success else "未通过"
        outcome_class = "safe" if item.success else "unsafe"
        settling = "未稳定" if item.settling_time_s is None else f"{item.settling_time_s:.2f} s"
        rows.append(
            '<div class="comparison-row">'
            f'<div class="comparison-label"><strong>{label}</strong><span class="{outcome_class}">{outcome}</span></div>'
            f'<div class="bar-track"><div class="bar {outcome_class}" style="width:{width:.1f}%"></div></div>'
            f'<div class="comparison-values"><span>最终误差 {item.abs_final_error:.5g}</span><span>稳定时间 {settling}</span><span>饱和率 {100 * item.saturation_fraction:.2f}%</span></div>'
            "</div>"
        )
    improvement = ""
    stale = report.stale_controller_performance
    adapted = report.adapted_controller_performance
    if stale is not None and adapted is not None:
        delta = stale.abs_final_error - adapted.abs_final_error
        direction = "降低" if delta >= 0 else "增加"
        improvement = f'<div class="comparison-note">适应后最终误差{direction} {abs(delta):.5g}</div>'
    return f'<div class="comparison-panel">{"".join(rows)}{improvement}</div>'


def status_markdown(report: CFDCRunReport) -> str:
    label = STATUS_LABELS.get(report.status, report.status)
    profile = (
        report.semantic_selection.simulation_profile_id
        if report.semantic_selection
        else "等待诊断"
    )
    quality = (
        report.feature_quality_decision.decision
        if report.feature_quality_decision
        else "未执行"
    )
    return (
        f"### {label}\n"
        f"`{report.run_id}` · `{profile}` · 特征质量门 `{quality}` · "
        f"证据边界 `{report.evidence_boundary}`"
    )


def clarification_items(report: CFDCRunReport) -> list[tuple[str, str]]:
    session = report.diagnostic_session
    if session is None:
        return []
    return list(clarification_question_map(session).items())


def render_report(report: CFDCRunReport) -> dict[str, Any]:
    return {
        "status": status_markdown(report),
        "progress": stage_progress_html(report),
        "summary": summary_html(report),
        "performance_visual": performance_html(report),
        "diagnosis": diagnosis_rows(report),
        "route": route_rows(report),
        "experiments": experiment_rows(report),
        "features": feature_rows(report),
        "controller": controller_rows(report),
        "tuning": tuning_rows(report),
        "performance": performance_rows(report),
        "raw": _compact_report(report),
        "clarifications": clarification_items(report),
    }
