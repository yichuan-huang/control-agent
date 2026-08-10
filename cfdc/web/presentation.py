from __future__ import annotations

import json
from typing import Any

from cfdc.diagnosis import clarification_question_map
from cfdc.models import CFDCRunReport

STATUS_LABELS = {
    "collecting_description": "补充问题描述",
    "awaiting_measurements": "等待现有记录",
    "measurement_needs_more": "仍需补充现有记录",
    "measurement_conflict": "测量记录存在冲突",
    "measurement_verified": "测量证据已核验",
    "awaiting_profile_measurements": "等待对象参数记录",
    "specification_model_ready": "规格模型已就绪",
    "need_more_information": "需要补充信息",
    "awaiting_specifications": "等待设备规格",
    "need_more_specifications": "仍需补充设备规格",
    "specification_conflict": "设备规格存在冲突",
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

CHECKLIST_LABELS = {
    "open_loop_stability": "恢复输入后会怎样",
    "minimum_phase": "输出最初往哪边变化",
    "significant_delay": "多久开始变化",
    "relative_degree": "有几个明显快慢阶段",
    "controllability_observability": "关键运动能否被带动和记录",
    "nonlinearity_strength": "小幅正反变化是否近似一致",
    "coupling_severity": "一个作用会影响哪些读数",
    "uncertainty_magnitude": "换负载或工况后变化多大",
}

CHECKLIST_STATUS_LABELS = {
    "missing": "缺少描述",
    "described": "已有线索",
    "verified": "测量已验证",
}

STAGES = [
    (
        "问题描述",
        lambda report: bool(
            report.system_description and report.system_description.text.strip()
        ),
    ),
    (
        "AI 测量计划",
        lambda report: _measurement_plan_released(report),
    ),
    (
        "测量回填",
        lambda report: _measurement_evidence_released(report),
    ),
    (
        "系统分类",
        lambda report: _classification_released(report),
    ),
    (
        "初始控制器",
        lambda report: _controller_released(report),
    ),
    (
        "效果验证与调优",
        lambda report: _validation_released(report),
    ),
]

LINKED_VALIDATION_BLOCKED_STATES = {
    "frozen",
    "inconclusive",
    "budget_exhausted",
    "cancelled",
}

_PRE_MEASUREMENT_STATUSES = {
    "collecting_description",
    "awaiting_measurements",
    "measurement_needs_more",
    "measurement_conflict",
    "need_more_information",
}

_PRE_MODEL_STATUSES = {
    *_PRE_MEASUREMENT_STATUSES,
    "measurement_verified",
    "awaiting_profile_measurements",
    "awaiting_specifications",
    "need_more_specifications",
    "specification_conflict",
    "awaiting_evidence",
    "evidence_rejected",
}


def _effective_status(report: CFDCRunReport) -> str:
    session = report.diagnostic_session
    return session.status if session is not None else report.status


def _measurement_plan_released(report: CFDCRunReport) -> bool:
    session = report.diagnostic_session
    if session is None:
        return _effective_status(report) not in {
            "need_more_information",
            "collecting_description",
        }
    return session.measurement_plan is not None and session.status != "collecting_description"


def _measurement_evidence_released(report: CFDCRunReport) -> bool:
    if _effective_status(report) in _PRE_MEASUREMENT_STATUSES:
        return False
    session = report.diagnostic_session
    return session is None or session.evidence_level == "measurement_verified"


def _classification_released(report: CFDCRunReport) -> bool:
    return bool(
        _measurement_evidence_released(report)
        and report.classification
        and report.semantic_selection
    )


def _model_released(report: CFDCRunReport) -> bool:
    return bool(
        _classification_released(report)
        and _effective_status(report) not in _PRE_MODEL_STATUSES
        and (
            report.compiled_specification_model
            or report.experiment_results
            or report.controller
        )
    )


def _features_released(report: CFDCRunReport) -> bool:
    return bool(_model_released(report) and report.features)


def _controller_released(report: CFDCRunReport) -> bool:
    return bool(_model_released(report) and report.controller)


def _validation_released(report: CFDCRunReport) -> bool:
    return bool(
        _controller_released(report)
        and _effective_status(report)
        in {"validated_in_simulation", "demo_completed", "completed"}
    )


def technical_visibility(report: CFDCRunReport) -> dict[str, bool]:
    measurement_released = _measurement_evidence_released(report)
    route_released = _classification_released(report)
    model_released = _model_released(report)
    features_released = _features_released(report)
    controller_released = _controller_released(report)
    return {
        "diagnosis": measurement_released,
        "route": route_released,
        "model": model_released,
        "features": features_released,
        "controller": controller_released,
        "tuning": controller_released,
    }


def checklist_rows(report: CFDCRunReport) -> list[list[str]]:
    session = report.diagnostic_session
    if session is None:
        return []
    request_field_by_id = {
        request.request_id: request.diagnostic_field_id
        for request in (session.measurement_plan.requests if session.measurement_plan else [])
    }
    fact_by_field = {}
    assessment = session.measurement_assessment
    if assessment is not None:
        for fact in assessment.facts:
            field_id = request_field_by_id.get(fact.request_id)
            if field_id is not None:
                fact_by_field[field_id] = fact
    rows = []
    for item in session.checklist:
        fact = fact_by_field.get(item.diagnostic_field_id)
        if fact is not None:
            state = "verified"
            evidence = fact.source_excerpt
        elif item.status == "unknown":
            state = "missing"
            evidence = "；".join(item.evidence)
        else:
            state = "described"
            evidence = "；".join(item.evidence)
        rows.append(
            [
                CHECKLIST_LABELS[item.diagnostic_field_id],
                CHECKLIST_STATUS_LABELS[state],
                evidence or "—",
            ]
        )
    return rows


def measurement_guidance_markdown(report: CFDCRunReport) -> str:
    session = report.diagnostic_session
    if session is None or session.measurement_plan is None:
        return ""
    requests = session.measurement_plan.requests
    lines = [
        "### 从现有记录中补充证据",
        "请只查找已有记录、日志或手册，不要为回答这些问题操作真实硬件。",
    ]
    for index, request in enumerate(requests, start=1):
        unit = f"；数值单位提示：{request.unit_hint}" if request.unit_hint else ""
        lines.append(
            f"{index}. **{CHECKLIST_LABELS[request.diagnostic_field_id]}** "
            f"(`{request.request_id}`){unit}  \n"
            f"   来源：{request.source_hint}  \n"
            f"   回填：{request.report_template}  \n"
            f"   范围：`{request.safety_scope}`"
        )
    assessment = session.measurement_assessment
    if assessment is not None:
        lines.append(f"\n**上轮核验：** {assessment.rationale}")
        if assessment.conflicts:
            lines.extend(f"- ⚠️ {item}" for item in assessment.conflicts)
    return "\n\n".join(lines)


def guided_timeline_markdown(report: CFDCRunReport) -> str:
    session = report.diagnostic_session
    if session is None:
        return ""
    lines = ["### 引导记录时间线"]
    if not session.turns and not session.measurement_history:
        lines.append("尚无补充轮次。")
    for turn in session.turns:
        lines.append(f"#### 描述补充 · 第 {turn.turn_index} 轮")
        for question_id, answer in turn.answers.items():
            lines.append(f"- `{question_id}`：{answer}")
        for evidence in turn.evidence:
            lines.append(f"- 记录：{evidence}")
    for round_index, assessment in enumerate(session.measurement_history, start=1):
        lines.append(f"#### 测量回填 · 第 {round_index} 轮")
        for fact in assessment.facts:
            rendered = fact.text_value or f"{fact.numeric_value} {fact.unit}"
            lines.append(
                f"- `{fact.request_id}`：{fact.source_excerpt}（{rendered}）"
            )
        if assessment.gaps:
            lines.append("- 缺口：" + "、".join(assessment.gaps))
        for request_id, conflict in zip(
            assessment.conflict_request_ids,
            assessment.conflicts,
            strict=True,
        ):
            lines.append(f"- 冲突 `{request_id}`：{conflict}")
        lines.append(f"- 结论：{assessment.rationale}")
    return "\n\n".join(lines)


def _redacted_report_payload(report: CFDCRunReport) -> dict[str, Any]:
    payload = report.model_dump(mode="json")
    measurement_released = _measurement_evidence_released(report)
    classification_released = _classification_released(report)
    model_released = _model_released(report)
    features_released = _features_released(report)
    controller_released = _controller_released(report)
    validation_released = _validation_released(report)

    session = payload.get("diagnostic_session")
    if session is not None and not measurement_released:
        session["current_diagnosis"] = None
    if session is not None and not classification_released:
        for name, empty in {
            "classification": None,
            "semantic_selection": None,
            "experiment_plan": None,
            "evidence_requirement_plan": None,
            "evidence_readiness": None,
            "specification_templates": [],
            "specification_assessment": None,
            "specification_answer_history": [],
            "candidate_route": None,
            "compiled_route": None,
        }.items():
            session[name] = empty
    if session is not None and not model_released:
        session["compiled_specification_model"] = None

    if not measurement_released:
        payload["diagnosis"] = None
    if not classification_released:
        for name, empty in {
            "classification": None,
            "semantic_selection": None,
            "experiment_plan": None,
            "evidence_requirement_plan": None,
            "evidence_readiness": None,
            "specification_templates": [],
            "specification_assessment": None,
            "candidate_route": None,
            "compiled_route": None,
        }.items():
            payload[name] = empty
    if not model_released:
        payload["compiled_specification_model"] = None
        payload["experiment_results"] = []
    if not features_released:
        payload["features"] = []
        payload["feature_quality_decision"] = None
    if not controller_released:
        for name, empty in {
            "controller": None,
            "controller_validation": None,
            "trial_reports": [],
            "online_tuning_state": None,
            "algorithm1_state": None,
            "safe_gain_search_state": None,
            "feature_tracking_updates": [],
            "tracking_state": None,
            "cartpole_simulation": None,
            "cartpole_boundary": None,
            "vtol_simulation": None,
            "vtol_variation": None,
            "baseline_comparison": None,
            "final_gains": {},
            "final_feedforward": {},
            "go_no_go": None,
        }.items():
            payload[name] = empty
    if not validation_released:
        payload["stale_controller_performance"] = None
        payload["adapted_controller_performance"] = None
    if not controller_released:
        payload["notes"] = []
    return payload


def _compact_report(report: CFDCRunReport) -> dict[str, Any]:
    payload = _redacted_report_payload(report)
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
    if report.diagnosis is None or not _measurement_evidence_released(report):
        return []
    payload = report.diagnosis.model_dump(mode="json")
    rows = []
    for field_id, label in DIAGNOSIS_LABELS.items():
        field = payload[field_id]
        estimate = field.get("estimated_order")
        assessment = field["assessment"]
        if estimate is not None:
            assessment = f"{assessment}（估计 {estimate} 阶）"
        rows.append(
            [
                label,
                assessment,
                f"{100 * field['confidence']:.0f}%",
                "；".join(field.get("evidence", [])),
            ]
        )
    return rows


def route_rows(report: CFDCRunReport) -> list[list[str]]:
    if not _classification_released(report):
        return []
    rows: list[list[str]] = []
    if report.classification:
        rows.extend(
            [
                ["动力学原型", str(report.classification.primary_class)],
                ["控制架构", report.classification.control_architecture],
            ]
        )
    if report.semantic_selection:
        rows.extend(
            [
                ["方法 Profile", report.semantic_selection.simulation_profile_id],
                ["特征 Bundle", report.semantic_selection.feature_bundle_id],
                ["核心特征", ", ".join(report.semantic_selection.selected_feature_ids)],
            ]
        )
    if report.compiled_route:
        rows.append(
            [
                "Route 编译",
                "可执行" if report.compiled_route.executable else "存在能力缺口",
            ]
        )
    return rows


def experiment_rows(report: CFDCRunReport) -> list[list[Any]]:
    if not _model_released(report):
        return []
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
    if not _features_released(report):
        return []
    rows = []
    for feature in report.features:
        value = feature.value
        rendered = (
            json.dumps(value, ensure_ascii=False)
            if isinstance(value, list)
            else f"{value:.6g}"
        )
        interval = (
            "矩阵特征"
            if feature.lower_bound is None
            else f"[{feature.lower_bound:.6g}, {feature.upper_bound:.6g}]"
        )
        rows.append(
            [
                feature.feature_id,
                rendered,
                feature.units,
                interval,
                f"{100 * feature.confidence:.0f}%",
                feature.method,
            ]
        )
    return rows


def controller_rows(report: CFDCRunReport) -> list[list[str]]:
    if report.controller is None or not _controller_released(report):
        return []
    rows = [["架构", report.controller.architecture]]
    rows.extend(
        [f"增益 · {name}", f"{value:.6g}"] for name, value in report.final_gains.items()
    )
    rows.extend(
        [f"前馈 · {name}", f"{value:.6g}"]
        for name, value in report.final_feedforward.items()
    )
    rows.append(["候选状态", report.controller.status])
    rows.append(["发布等级", report.controller.release_level])
    if report.controller.plant_id:
        rows.append(["对象 ID", report.controller.plant_id])
    return rows


def tuning_rows(report: CFDCRunReport) -> list[list[Any]]:
    if not _controller_released(report):
        return []
    rows: list[list[Any]] = []
    if report.algorithm1_state:
        rows.append(
            [
                "Algorithm 1",
                report.algorithm1_state.status,
                report.algorithm1_state.iteration_count,
                report.algorithm1_state.completion_reason or "-",
            ]
        )
    for update in report.feature_tracking_updates:
        rows.append(
            [
                update.feature_id,
                "已更新" if update.controller_update_required else "仅跟踪",
                f"{100 * update.relative_change:.2f}%",
                f"{update.previous_value:.6g} → {update.updated_value:.6g}",
            ]
        )
    return rows


def performance_rows(report: CFDCRunReport) -> list[list[Any]]:
    if not _validation_released(report):
        return []
    rows = []
    for label, performance in (
        ("变化后 · 原控制器", report.stale_controller_performance),
        ("变化后 · 适应控制器", report.adapted_controller_performance),
    ):
        if performance is None:
            continue
        rows.append(
            [
                label,
                "通过" if performance.success else "未通过",
                f"{performance.abs_final_error:.6g}",
                "-"
                if performance.settling_time_s is None
                else f"{performance.settling_time_s:.3f}",
                f"{100 * performance.saturation_fraction:.2f}%",
                ", ".join(performance.violations) or "无",
            ]
        )
    return rows


def stage_progress_html(
    report: CFDCRunReport,
    linked_simulation_state: str | None = None,
) -> str:
    effective_status = _effective_status(report)
    blocked = effective_status in {
        "feature_extraction_failed",
        "evidence_rejected",
        "rejected",
        "frozen",
    }
    waiting = effective_status in {
        "collecting_description",
        "awaiting_measurements",
        "measurement_needs_more",
        "measurement_conflict",
        "awaiting_profile_measurements",
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
        if label == "效果验证与调优" and linked_simulation_state is not None:
            complete = linked_simulation_state == "stable"
            linked_state = (
                "blocked"
                if linked_simulation_state in LINKED_VALIDATION_BLOCKED_STATES
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
    classification_released = _classification_released(report)
    features_released = _features_released(report)
    model_released = _model_released(report)
    archetype = (
        str(report.classification.primary_class)
        .replace("class_", "Class ")
        .replace("_", " ")
        if classification_released and report.classification
        else "待确认"
    )
    profile = (
        report.semantic_selection.simulation_profile_id
        if classification_released and report.semantic_selection
        else "待选择"
    )
    quality = (
        report.feature_quality_decision.decision
        if features_released and report.feature_quality_decision
        else "未执行"
    )
    repeats = (
        max((record.repeat_index for record in report.experiment_results), default=0)
        if model_released
        else 0
    )
    cards = [
        ("动力学原型", archetype),
        ("方法 Profile", profile),
        ("核心特征", str(len(report.features)) if features_released else "-"),
        ("模型/数据运行", str(repeats) if repeats else "-"),
        ("质量门", quality),
    ]
    return (
        '<div class="metric-grid">'
        + "".join(
            f'<div class="metric"><small>{label}</small><strong>{value}</strong></div>'
            for label, value in cards
        )
        + "</div>"
    )


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
        item
        for item in assessment.facts
        if item.source_type != "derived_from_declared_physics"
    ]
    derived_facts = [
        item
        for item in assessment.facts
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
    progress_note = f"\n\n{assessment.rationale}" if assessment.no_progress else ""
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
    if not _validation_released(report):
        return '<div class="empty-result">当前流程尚未生成系统变化后的性能对照。</div>'
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
        settling = (
            "未稳定"
            if item.settling_time_s is None
            else f"{item.settling_time_s:.2f} s"
        )
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
    effective_status = _effective_status(report)
    label = STATUS_LABELS.get(effective_status, effective_status)
    profile = (
        report.semantic_selection.simulation_profile_id
        if _classification_released(report) and report.semantic_selection
        else "等待诊断"
    )
    quality = (
        report.feature_quality_decision.decision
        if _features_released(report) and report.feature_quality_decision
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
        "checklist": checklist_rows(report),
        "measurement_guidance": measurement_guidance_markdown(report),
        "timeline": guided_timeline_markdown(report),
        "technical_visibility": technical_visibility(report),
        "clarifications": clarification_items(report),
        "specification_guidance": (
            specification_guidance_markdown(report)
            if _classification_released(report)
            else ""
        ),
    }
