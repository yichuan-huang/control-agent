"""Natural-language presentation for the generated plant-model workflow."""

from __future__ import annotations

from typing import Any

from cfdc.lab import (
    ModelDiscoverySession,
    load_model_question_examples,
)
from cfdc.models import (
    RegisteredNonlinearModelSpec,
    StateSpaceModelSpec,
    TransferFunctionModelSpec,
)


def _example_map():
    return {
        item.example_id: item
        for item in load_model_question_examples().examples
    }


def _question_slots(
    session: ModelDiscoverySession,
) -> list[dict[str, Any]]:
    examples = _example_map()
    answers = {
        item.question_id: item
        for item in session.answers
    }
    slots: list[dict[str, Any]] = []
    for question in session.current_questions:
        example = examples[question.example_id]
        answer = answers.get(question.question_id)
        slots.append(
            {
                "question_id": question.question_id,
                "fact_id": question.fact_id,
                "prompt": question.prompt,
                "why_needed": question.why_needed,
                "answer_kind": question.answer_kind,
                "example_id": example.example_id,
                "example_text": example.answer_text,
                "answer_text": answer.answer_text if answer else "",
                "answer_source": answer.source if answer else None,
                "adopt_label": "采用此示例值",
            }
        )
    return slots


def _signal_rows(model) -> list[tuple[str, str, str]]:
    if isinstance(model, TransferFunctionModelSpec):
        return [
            ("输入", model.input_signal_id, model.input_units),
            ("输出", model.output_signal_id, model.output_units),
        ]
    if isinstance(model, StateSpaceModelSpec):
        groups = (
            ("状态", model.state_names),
            ("输入", model.input_signal_ids),
            ("输出", model.output_signal_ids),
        )
    else:
        assert isinstance(model, RegisteredNonlinearModelSpec)
        groups = (
            ("状态", list(model.initial_state)),
            ("输入", model.input_signal_ids),
            ("输出", model.output_signal_ids),
        )
    return [
        (group, name, model.signal_units[name])
        for group, names in groups
        for name in names
    ]


def _markdown_table(
    headers: tuple[str, ...],
    rows: list[tuple[Any, ...]],
) -> str:
    if not rows:
        return "（无）"
    header = "| " + " | ".join(headers) + " |"
    rule = "| " + " | ".join("---" for _ in headers) + " |"
    body = [
        "| "
        + " | ".join(str(value).replace("|", "\\|") for value in row)
        + " |"
        for row in rows
    ]
    return "\n".join([header, rule, *body])


def _region_markdown(envelope) -> str:
    sections: list[str] = []
    if envelope.operating_point is not None:
        point = envelope.operating_point
        rows = [
            (group, name, value, point.signal_units[name])
            for group, values in (
                ("状态", point.states),
                ("输入", point.inputs),
                ("输出", point.outputs),
            )
            for name, value in values.items()
        ]
        sections.extend(
            [
                "#### 工作点",
                point.description,
                _markdown_table(
                    ("类别", "变量", "数值", "单位"),
                    rows,
                ),
            ]
        )
    if envelope.validity_region is not None:
        region = envelope.validity_region
        rows = [
            (
                group,
                name,
                f"{bounds[0]} ～ {bounds[1]}",
                region.signal_units[name],
            )
            for group, values in (
                ("输入", region.input_ranges),
                ("输出", region.output_ranges),
                ("状态", region.state_ranges),
            )
            for name, bounds in values.items()
        ]
        sections.extend(
            [
                "#### 只在以下范围内有效",
                region.description,
                _markdown_table(
                    ("类别", "变量", "范围", "单位"),
                    rows,
                ),
                "保持不变：" + "；".join(region.constant_conditions),
                f"越界后：{region.out_of_range_effect}",
            ]
        )
    return "\n\n".join(sections)


def _model_card(session: ModelDiscoverySession) -> str:
    envelope = session.pending_envelope or session.confirmed_envelope
    if envelope is None:
        return ""
    evidence_rows = [
        (
            item.parameter_path,
            item.value,
            item.unit,
            item.source,
            "、".join(item.source_fact_ids),
        )
        for item in envelope.parameter_evidence
    ]
    experiment = envelope.experiment_proposal
    deviation_coordinates = any(
        item.derivation_rule_id
        in {
            "output_step_delta_reference/v1",
            "center_actuator_bounds_at_input_before/v1",
            "center_output_bounds_at_output_before/v1",
        }
        for item in envelope.parameter_evidence
    )
    experiment_rows = [
        ("仿真时长", experiment.horizon_s, "s"),
        ("采样间隔", experiment.sample_time_s, "s"),
        *[
            (
                (
                    f"相对起始值的目标变化 {name}"
                    if deviation_coordinates
                    else f"目标 {name}"
                ),
                value,
                experiment.signal_units[name],
            )
            for name, value in experiment.reference.items()
        ],
        *[
            (
                f"初始状态 {name}",
                value,
                experiment.signal_units[name],
            )
            for name, value in experiment.initial_state.items()
        ],
        *[
            (
                f"执行器范围 {name}",
                f"{bounds[0]} ～ {bounds[1]}",
                experiment.signal_units[name],
            )
            for name, bounds in experiment.actuator_bounds.items()
        ],
        *[
            (
                f"状态范围 {name}",
                f"{bounds[0]} ～ {bounds[1]}",
                experiment.signal_units[name],
            )
            for name, bounds in experiment.state_bounds.items()
        ],
        *[
            (
                f"输出范围 {name}",
                f"{bounds[0]} ～ {bounds[1]}",
                experiment.signal_units[name],
            )
            for name, bounds in experiment.output_bounds.items()
        ],
    ]
    equations = "\n\n".join(
        f"$$\n{equation}\n$$"
        for equation in envelope.equation_latex
    )
    role_note = {
        "user_evidence_model": "参数来自用户或问题中明确给出的事实。",
        "example_hypothesis": (
            "本模型包含用户明确采用的固定示例值，仅用于可重复演示。"
        ),
        "local_linear_hypothesis": (
            "这是工作点附近的局部线性近似，越界后立即停止判定。"
        ),
        "registered_nonlinear_model": (
            "这是 CartPole/VTOL 的闭合注册非线性模板。"
        ),
    }[envelope.model_role]
    sections = [
        "### AI 对系统的理解",
        envelope.plain_language_summary,
        role_note,
        "#### 数学方程",
        equations,
        "#### 变量与单位",
        _markdown_table(
            ("类别", "变量", "单位"),
            _signal_rows(envelope.model),
        ),
        "#### 参数与来源",
        _markdown_table(
            ("模型字段", "数值", "单位", "来源", "事实 ID"),
            evidence_rows,
        ),
        _region_markdown(envelope),
        "#### 软件仿真条件",
        (
            "本模型使用**偏差坐标**：0 表示采用事实中的起始工作点；"
            "目标和边界显示的是相对起始值的变化量。"
            if deviation_coordinates
            else ""
        ),
        _markdown_table(
            ("项目", "数值", "单位"),
            experiment_rows,
        ),
        "#### 假设",
        "\n".join(f"- {item}" for item in envelope.assumptions),
        "#### 限制",
        "\n".join(f"- {item}" for item in envelope.limitations),
        (
            "**这里只能说明当前确认的软件模型是否稳定，不能代表真实对象"
            "或硬件安全。**"
        ),
    ]
    return "\n\n".join(section for section in sections if section)


def _compatibility_markdown(session: ModelDiscoverySession) -> str:
    result = session.compatibility_result
    if result is None:
        return ""
    title = (
        "### 初始控制器可以直接使用"
        if result.status == "compatible"
        else "### 初始控制器与模型不兼容"
    )
    details = "\n".join(f"- {item}" for item in result.reasons)
    recommendation = ""
    if result.recommended_controller is not None:
        recommendation = (
            "\n\n后端已生成类型化替代控制器 "
            f"`{result.recommended_controller.kind}`。确认后才会进入仿真。"
        )
    return f"{title}\n\n{details}{recommendation}"


def _status_markdown(session: ModelDiscoverySession) -> str:
    labels = {
        "collecting_model_information": "正在收集建立数学模型所需的信息",
        "model_proposed": "AI 已提出一个数学模型",
        "model_review": "请检查并确认 AI 生成的数学模型",
        "controller_compatibility_check": "模型已确认，等待控制器兼容性检查",
        "controller_replacement_review": "请确认替代控制器",
        "simulation_ready": "模型和控制器均已确认，可以运行仿真",
    }
    requests = "\n".join(
        f"- {item}" for item in session.material_requests
    )
    return (
        f"### {labels[session.state]}\n\n"
        f"{requests}\n\n"
        "**不会使用题号或 Profile 中的固定对象模型。**"
    )


def render_model_discovery(
    session: ModelDiscoverySession,
) -> dict[str, Any]:
    envelope = session.pending_envelope or session.confirmed_envelope
    candidate = session.stage5.initial_controller_candidate
    return {
        "status": _status_markdown(session),
        "state": session.state,
        "initial_controller_architecture": candidate.architecture,
        "initial_controller_rows": [
            [name, value]
            for name, value in candidate.gains.items()
        ],
        "questions": _question_slots(session),
        "model_card_markdown": _model_card(session),
        "technical_json": (
            envelope.model_dump(mode="json")
            if envelope is not None
            else {}
        ),
        "show_technical_json": envelope is not None,
        "technical_json_open": False,
        "compatibility_markdown": _compatibility_markdown(session),
        "replacement_json": (
            session.recommended_controller.model_dump(mode="json")
            if session.recommended_controller is not None
            else {}
        ),
        "llm_audit": [
            item.model_dump(mode="json")
            for item in session.llm_calls
        ],
        "controls": {
            "request_model": (
                session.state == "collecting_model_information"
            ),
            "submit_answers": (
                session.state == "collecting_model_information"
                and bool(session.current_questions)
            ),
            "confirm_model": session.state == "model_review",
            "return_to_answers": session.state != (
                "collecting_model_information"
            ),
            "confirm_replacement": (
                session.state == "controller_replacement_review"
                and session.recommended_controller is not None
            ),
        },
    }


__all__ = ["render_model_discovery"]
