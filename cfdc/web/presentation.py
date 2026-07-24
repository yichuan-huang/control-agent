from __future__ import annotations

import json
from typing import Any

from cfdc.diagnosis import clarification_question_map
from cfdc.models import CFDCRunReport


STATUS_LABELS = {
    "need_more_information": "需要补充信息",
    "awaiting_specifications": "等待设备规格",
    "need_more_specifications": "仍需补充设备规格",
    "specification_conflict": "设备规格存在冲突",
    "specification_model_ready": "规格模型已就绪",
    "awaiting_evidence": "等待对象证据",
    "evidence_rejected": "对象证据未通过",
    "candidate_unvalidated": "参数候选尚未验证",
    "validation_pending": "等待验证条件",
    "validated_in_simulation": "已在用户对象模型中验证",
    "demo_completed": "标准对象演示完成",
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
    ("结构诊断", lambda report: bool(report.diagnosis and report.diagnosis.complete and report.classification)),
    (
        "规格模型",
        lambda report: bool(
            report.compiled_specification_model
            or
            (report.evidence_readiness and report.evidence_readiness.decision == "ready")
            or report.status == "demo_completed"
        ),
    ),
    ("核心特征", lambda report: bool(report.features)),
    ("参数候选", lambda report: report.controller is not None),
    (
        "效果验证",
        lambda report: report.status in {"validated_in_simulation", "demo_completed"},
    ),
]

LINKED_VALIDATION_BLOCKED_STATES = {
    "frozen",
    "inconclusive",
    "budget_exhausted",
    "cancelled",
}


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
            ["方法 Profile", report.semantic_selection.simulation_profile_id],
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
    rows.append(["候选状态", report.controller.status])
    rows.append(["发布等级", report.controller.release_level])
    if report.controller.plant_id:
        rows.append(["对象 ID", report.controller.plant_id])
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


def stage_progress_html(
    report: CFDCRunReport,
    linked_simulation_state: str | None = None,
) -> str:
    blocked = report.status in {
        "feature_extraction_failed",
        "evidence_rejected",
        "rejected",
        "frozen",
    }
    waiting = report.status in {
        "need_more_information",
        "awaiting_specifications",
        "need_more_specifications",
        "specification_conflict",
        "awaiting_evidence",
        "validation_pending",
        "candidate_unvalidated",
    }
    items = []
    first_pending_seen = False
    for index, (label, predicate) in enumerate(STAGES, start=1):
        complete = bool(predicate(report))
        linked_state: str | None = None
        if (
            label == "效果验证"
            and linked_simulation_state is not None
        ):
            complete = linked_simulation_state == "stable"
            linked_state = (
                "blocked"
                if linked_simulation_state
                in LINKED_VALIDATION_BLOCKED_STATES
                else "waiting"
            )
        state = "done" if complete else "pending"
        if not complete and not first_pending_seen:
            first_pending_seen = True
            if linked_state is not None:
                state = linked_state
            elif waiting:
                state = "waiting"
            elif blocked:
                state = "blocked"
        elif not complete and linked_state is not None:
            state = linked_state
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
        ("方法 Profile", profile),
        ("核心特征", str(len(report.features))),
        ("模型/数据运行", str(repeats) if repeats else "-"),
        ("质量门", quality),
    ]
    return '<div class="metric-grid">' + "".join(
        f'<div class="metric"><small>{label}</small><strong>{value}</strong></div>'
        for label, value in cards
    ) + "</div>"


def specification_guidance_markdown(report: CFDCRunReport) -> str:
    assessment = report.specification_assessment
    if assessment is None:
        return ""
    templates = {item.template_id: item for item in report.specification_templates}
    template = templates.get(assessment.template_id)
    summary = template.user_summary if template is not None else assessment.rationale
    field_labels = {
        item.fact_id: item.label
        for item in (template.fields if template is not None else [])
    }
    direct_facts = [
        item for item in assessment.facts
        if item.source_type != "derived_from_declared_physics"
    ]
    derived_facts = [
        item for item in assessment.facts
        if item.source_type == "derived_from_declared_physics"
    ]
    fact_sections: list[str] = []
    if direct_facts:
        fact_sections.append("\n\n**直接识别的规格**")
        fact_sections.extend(
            f"\n- {field_labels.get(item.fact_id, item.fact_id)}：{item.value} {item.unit}"
            for item in direct_facts
        )
    if derived_facts:
        fact_sections.append("\n\n**经后端重算验证的推导规格**")
        for item in derived_facts:
            assert item.derivation is not None
            fact_sections.append(
                f"\n- {field_labels.get(item.fact_id, item.fact_id)}：{item.value} {item.unit}；"
                f"公式：`{item.derivation.expression}`"
            )
    rejected = ""
    if assessment.rejected_facts:
        rejected = "\n\n**本次未采纳的内容**" + "".join(
            f"\n- ⚠️ {item}" for item in assessment.rejected_facts
        )
    missing = ""
    if assessment.missing_fact_ids:
        missing_labels = [
            field_labels.get(item, item) for item in assessment.missing_fact_ids
        ]
        missing = "\n\n**仍缺少：** " + "、".join(missing_labels)
    progress_note = (
        f"\n\n{assessment.rationale}" if assessment.no_progress else ""
    )
    conflicts = "".join(f"\n- ⚠️ {item}" for item in assessment.conflicts)
    questions = []
    visible_questions = [] if assessment.no_progress else assessment.questions
    for index, question in enumerate(visible_questions, start=1):
        options = " / ".join(question.answer_options)
        questions.append(
            f"\n\n**{index}. {question.prompt}**\n\n"
            f"为什么需要：{question.why_needed}\n\n"
            f"可以从哪里找：{question.where_to_find}\n\n"
            f"单位提示：{question.unit_hint}\n\n"
            f"回答示例：{question.example}\n\n"
            f"可选方式：{options}"
        )
    if assessment.status == "ready":
        ready_note = "\n\n规格已经能够编译近似模型；该模型仍不代表真实对象验证。"
    else:
        ready_note = (
            "\n\n在这些明确数值齐全前，系统不会编译规格模型、不会提取核心特征，"
            "也不会生成控制器参数。回答“暂时不知道”会保留当前缺口，不会补造数值。"
        )
    return (
        "### 补充当前设备的已知规格\n\n"
        f"{summary}{''.join(fact_sections)}{rejected}{missing}{progress_note}"
        f"{conflicts}{''.join(questions)}{ready_note}"
    )


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
        "specification_guidance": specification_guidance_markdown(report),
    }
