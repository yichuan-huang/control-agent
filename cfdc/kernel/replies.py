"""Safe WebUI reply contracts for the evidence-driven kernel workflow.

The kernel has two deliberately separate input paths: a natural-language path
that is interpreted by the configured role agents, and an advanced JSON path
for public evidence and other typed artifacts.  Neither path is allowed to
change task boundaries, route selection, or tool permissions.
"""

from __future__ import annotations

import json
import math
import re
from collections.abc import Mapping
from enum import StrEnum
from typing import Any

from cfdc.knowledge import feature_definitions
from cfdc.specifications.templates import default_specification_template_catalog

from .agents import AgentRole, KernelAgentCoordinator
from .contracts import DIAGNOSTIC_IDS
from .session import TERMINAL_STATES, EvidenceSession


class KernelReplyMode(StrEnum):
    NATURAL_LANGUAGE = "natural_language"
    JSON = "json"


_ACTION_ALIASES = {
    "answer": "submit_answer",
    "resolve": "submit_answer",
    "submit_answer": "submit_answer",
    "submit_evidence": "evidence",
    "submit_features": "features",
    "submit_controller": "controller",
    "freeze_controller": "freeze",
    "record_evaluation": "evaluation",
    "replay_evaluation": "replay",
    "record_confirmation": "confirmation",
    "record_fresh_confirmation": "confirmation",
    "set_provider": "set_provider",
    "compile_protocol": "compile_protocol",
    "prepare_operator_handoff": "prepare_operator_handoff",
    "record_operator_report": "record_operator_report",
    "ingest_upload": "ingest_upload",
    "derive_features": "derive_features",
    "synthesize_controller": "synthesize_controller",
    "qualify_controller": "qualify_controller",
    "run_provider": "run_provider",
    "run_evaluation": "run_evaluation",
    "run_tuning": "run_feedback_iteration",
    "run_feedback_iteration": "run_feedback_iteration",
    "confirm_result": "confirm_result",
}

_NO_INPUT_ACTIONS = frozenset(
    {
        "advance",
        "cancel",
        "replay",
        "prepare_operator_handoff",
        "derive_features",
        "synthesize_controller",
        "qualify_controller",
        "run_provider",
        "run_evaluation",
        "run_feedback_iteration",
        "confirm_result",
    }
)

_MODE_ALIASES = {
    "自然语言": KernelReplyMode.NATURAL_LANGUAGE,
    "自然语言自动分析（主流程）": KernelReplyMode.NATURAL_LANGUAGE,
    "高级 JSON": KernelReplyMode.JSON,
    "json": KernelReplyMode.JSON,
}

_DIAGNOSTIC_ALIASES = {
    "minimum_phase": "nonminimum_phase",
    "controllability_observability": "sensing_actuation_adequacy",
    "coupling_severity": "coupling_underactuation",
    "uncertainty_magnitude": "uncertainty_variation",
}

_SPECIFICATION_FACT_IDS = frozenset(
    field.fact_id
    for template in default_specification_template_catalog().templates
    for field in template.fields
)
_PARAMETER_FACT_IDS = _SPECIFICATION_FACT_IDS | frozenset(
    item.feature_id for item in feature_definitions()
)
_ALLOWED_REPLY_SOURCE_TYPES = frozenset({"user_reply"})


def _canonical_action(value: Any) -> str:
    raw = str(value or "").strip()
    return _ACTION_ALIASES.get(raw, raw)


def _pending_action(session: EvidenceSession) -> dict[str, Any]:
    if session.pending_actions:
        return dict(session.pending_actions[0])
    if (
        session.status == "intake"
        and not session.task.budget_confirmed
        and not session.read_only
    ):
        return {
            "kind": "budget",
            "action": "confirm_task",
            "reason": "task_boundary_confirmation_required",
        }
    if session.status in TERMINAL_STATES:
        return {"kind": "terminal", "reason": session.status}
    return {}


def build_kernel_input_contract(
    session: EvidenceSession,
    *,
    pending_actions: Any | None = None,
) -> dict[str, Any]:
    """Build the action-specific input contract rendered by WebUI."""

    pending_values = (
        pending_actions if pending_actions is not None else session.pending_actions
    )
    pending = (
        dict(pending_values[0])
        if isinstance(pending_values, (list, tuple)) and pending_values
        else _pending_action(session)
    )
    reason = str(pending.get("reason") or "")
    raw_action = pending.get("ui_action") or pending.get("action")
    if not raw_action:
        raw_action = {
            "budget": (
                "confirm_task"
                if reason == "task_boundary_confirmation_required"
                else None
            ),
            "diagnostic": "submit_answer",
            "route": "advance",
            "evidence": "evidence",
            "phase": "phase",
            "feature": "features",
            "features": "features",
            "controller": "controller",
            "freeze": "freeze",
            "evaluation": "evaluation",
            "confirmation": "confirmation",
            "replay": "replay",
            "provider": "set_provider",
            "provider_run": "run_provider",
            "operator_handoff": "prepare_operator_handoff",
            "operator_report": "record_operator_report",
            "upload": "ingest_upload",
            "qualification": "qualify_controller",
            "tuning": "run_feedback_iteration",
        }.get(str(pending.get("kind") or ""))
    action = _canonical_action(raw_action)
    result: dict[str, Any] = {
        "action": action or None,
        "kind": str(pending.get("kind") or "") or None,
        "reason": reason or None,
        "allowed_modes": [],
        "title": "",
        "guidance": "",
        "json_template": None,
        "required_fields": [],
        "disabled_reason": None,
    }
    if not action:
        result["disabled_reason"] = (
            f"会话已终止：{session.status}"
            if session.status in TERMINAL_STATES
            else "当前没有待处理动作，请刷新页面。"
        )
        return result
    if action == "confirm_task":
        result.update(
            title="确认软件试验边界与预算",
            guidance="请先确认边界和预算；此动作不需要在输入框填写内容。",
        )
        return result
    if action in _NO_INPUT_ACTIONS:
        result.update(
            title=(
                "继续到下一阶段"
                if action == "advance"
                else "重新计算已记录评价"
                if action == "replay"
                else "执行当前确定性阶段"
            ),
            guidance="此动作使用专用按钮，不需要在输入框填写内容。",
        )
        return result
    if action == "relevance":
        result.update(
            allowed_modes=[KernelReplyMode.JSON.value],
            title="声明与当前任务无关的诊断项",
            guidance="只能提交确定性任务规则允许的不相关声明；不能用它绕过必需证据。",
            json_template={"coupling_underactuation": "不相关的确定性说明"},
            required_fields=["coupling_underactuation"],
        )
        return result
    if action == "submit_answer":
        diagnostic_template = {
            dimension_id: {
                "status": "known|unknown",
                "assessment": "可选字符串",
                "evidence": "用户原文摘录",
                "confidence": "0 到 1（可选）",
            }
            for dimension_id in DIAGNOSTIC_IDS
        }
        result.update(
            allowed_modes=[item.value for item in KernelReplyMode],
            title="补充结构诊断与核心参数",
            guidance=(
                "可直接用自然语言描述已知现象、单位和来源；也可切换高级 JSON，"
                "只提交八项诊断字段。没有把握的项目请明确写“不知道”。"
            ),
            json_template={
                **diagnostic_template,
                "parameter_candidates": [
                    {
                        "fact_id": "static_gain",
                        "value": "用户原文中的数值",
                        "unit": "用户原文中的单位",
                        "source_text": "原文摘录",
                    }
                ],
            },
            required_fields=list(DIAGNOSTIC_IDS),
        )
        return result
    if action in {
        "evidence",
        "features",
        "controller",
        "freeze",
        "evaluation",
        "replay",
        "phase",
        "confirmation",
        "set_provider",
        "compile_protocol",
        "record_operator_report",
        "ingest_upload",
    }:
        result.update(
            allowed_modes=[KernelReplyMode.JSON.value],
            title="提交结构化公开产物",
            guidance="此动作只能提交经过合同校验的 JSON 对象；参考资料和示例数值不会被接受。",
            json_template={},
        )
        return result
    result["disabled_reason"] = (
        "当前 WebUI 尚未提供该实验动作的执行适配。"
        if action in {"run_experiment", "retry"}
        else f"未知待处理动作：{action}"
    )
    return result


def _json_error(exc: json.JSONDecodeError) -> ValueError:
    return ValueError(
        f"JSON 格式错误：第 {exc.lineno} 行、第 {exc.colno} 列；"
        "请切换为自然语言，或提交一个完整的 JSON 对象。"
    )


def parse_kernel_json(text: str) -> dict[str, Any]:
    """Parse one object or one complete JSON code fence, never mixed prose."""

    value = str(text or "").strip()
    if not value:
        raise ValueError("高级 JSON 输入不能为空。")
    if value.startswith("```"):
        lines = value.splitlines()
        if len(lines) < 3 or lines[-1].strip() != "```":
            raise ValueError("JSON 代码围栏未闭合；请提交完整的 ```json ... ```。")
        language = lines[0].strip().casefold()
        if language not in {"```", "```json"}:
            raise ValueError("只支持 json 代码围栏，不支持其他代码或指令。")
        value = "\n".join(lines[1:-1]).strip()
    elif "```" in value:
        raise ValueError("JSON 输入不能混合普通文字和代码围栏。")
    try:
        payload = json.loads(value)
    except json.JSONDecodeError as exc:
        raise _json_error(exc) from None
    if not isinstance(payload, dict):
        raise TypeError("JSON 输入必须是对象，不能是数组、数字或字符串。")
    return payload


def _contains_verbatim(text: str, excerpt: Any) -> bool:
    candidate = str(excerpt or "").strip()
    if not candidate:
        return False
    if candidate in text:
        return True
    compact_text = re.sub(r"\s+", " ", text).casefold()
    compact_candidate = re.sub(r"\s+", " ", candidate).casefold()
    return compact_candidate in compact_text


def _evidence_excerpts(value: Mapping[str, Any]) -> list[str]:
    raw = value.get("evidence")
    if isinstance(raw, (list, tuple)):
        return [str(item).strip() for item in raw if str(item).strip()]
    excerpt = str(raw or "").strip()
    return [excerpt] if excerpt else []


def _evidence_in_source(source: str, value: Mapping[str, Any]) -> bool:
    excerpts = _evidence_excerpts(value)
    return bool(excerpts) and all(_contains_verbatim(source, item) for item in excerpts)


def _unwrap_known_agent_mapping(
    payload: Mapping[str, Any],
    *,
    role: str,
    wrappers: tuple[str, ...],
    allowed_siblings: frozenset[str],
) -> Mapping[str, Any]:
    current = payload
    for _ in range(2):
        present = [key for key in wrappers if key in current]
        if not present:
            return current
        if len(present) != 1:
            raise ValueError(f"{role} Agent 输出同时包含多个互斥包裹。")
        wrapper = present[0]
        unexpected = set(current) - {wrapper} - allowed_siblings
        if unexpected:
            raise ValueError(f"{role} Agent 输出混合了包裹字段和未知字段。")
        nested = current[wrapper]
        if not isinstance(nested, Mapping):
            raise TypeError(f"{role} Agent 的 {wrapper} 必须是 JSON 对象。")
        current = nested
    if any(key in current for key in wrappers):
        raise ValueError(f"{role} Agent 输出包裹层级超过 2 层。")
    return current


def _unwrap_diagnosis_payload(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    return _unwrap_known_agent_mapping(
        payload,
        role="Diagnosis",
        wrappers=("diagnosis", "diagnostic_updates"),
        allowed_siblings=frozenset(
            {
                "parameter_candidates",
                "parameters",
                "modeling",
                "rationale",
                "gaps",
                "conflicts",
            }
        ),
    )


def _unwrap_modeling_payload(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    return _unwrap_known_agent_mapping(
        payload,
        role="Modeling",
        wrappers=("modeling",),
        allowed_siblings=frozenset(
            {
                "diagnosis",
                "diagnostic_updates",
                "rationale",
                "gaps",
                "conflicts",
            }
        ),
    )


def _diagnostic_updates(payload: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    raw = _unwrap_diagnosis_payload(payload)
    result: dict[str, dict[str, Any]] = {}
    for raw_key, raw_value in raw.items():
        key = _DIAGNOSTIC_ALIASES.get(str(raw_key).strip(), str(raw_key).strip())
        if key not in DIAGNOSTIC_IDS:
            if str(raw_key) in {"rationale", "gaps", "conflicts"}:
                continue
            raise ValueError(f"未知诊断字段：{raw_key}")
        if not isinstance(raw_value, Mapping):
            raw_value = {"status": "known", "evidence": str(raw_value)}
        value = dict(raw_value)
        status = str(value.get("status", "known")).strip()
        if status not in {"known", "unknown", "not_relevant"}:
            raise ValueError(f"诊断字段 {key} 的 status 无效。")
        excerpts = _evidence_excerpts(value)
        if not excerpts:
            raise ValueError(f"诊断字段 {key} 缺少原文 evidence。")
        evidence = excerpts[0]
        value["status"] = status
        value["evidence"] = evidence
        if len(excerpts) > 1:
            value["evidence_excerpts"] = excerpts
        if "confidence" in value:
            try:
                confidence = float(value["confidence"])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"诊断字段 {key} 的 confidence 无效。") from exc
            if not math.isfinite(confidence) or not 0.0 <= confidence <= 1.0:
                raise ValueError(f"诊断字段 {key} 的 confidence 必须在 0 到 1 之间。")
            value["confidence"] = confidence
        result[key] = value
    return result


def _parameter_candidates(
    payload: Mapping[str, Any], source_text: str
) -> list[dict[str, Any]]:
    normalized = _unwrap_modeling_payload(payload)
    raw = normalized.get("parameter_candidates", normalized.get("parameters", []))
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise TypeError("Modeling 输出的 parameter_candidates 必须是数组。")
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in raw:
        if not isinstance(item, Mapping):
            raise TypeError("每个参数候选必须是 JSON 对象。")
        value = dict(item)
        fact_id = str(value.get("fact_id") or value.get("parameter_id") or "").strip()
        if fact_id not in _PARAMETER_FACT_IDS:
            raise ValueError(f"未知或不允许的参数字段：{fact_id or '空字段'}")
        source_excerpt = str(
            value.get("source_text") or value.get("source_excerpt") or ""
        ).strip()
        if not _contains_verbatim(source_text, source_excerpt):
            raise ValueError(f"参数 {fact_id} 的 source_text 不在用户原文中。")
        if "value" not in value:
            raise ValueError(f"参数 {fact_id} 缺少 value。")
        raw_numeric = value["value"]
        if isinstance(raw_numeric, bool):
            raise TypeError(f"参数 {fact_id} 的 value 不能是布尔值。")
        if isinstance(raw_numeric, (int, float)):
            numeric = float(raw_numeric)
            if not math.isfinite(numeric):
                raise ValueError(f"参数 {fact_id} 的 value 必须是有限数值。")
            value["value"] = numeric
            if not str(value.get("unit") or "").strip():
                raise ValueError(f"参数 {fact_id} 的数值必须包含 unit。")
        elif not isinstance(raw_numeric, (str, list, dict)):
            raise TypeError(f"参数 {fact_id} 的 value 类型不受支持。")
        if fact_id in seen:
            raise ValueError(f"参数 {fact_id} 在一次回复中重复提交。")
        source_type = str(value.get("source_type") or "user_reply").strip()
        if source_type not in _ALLOWED_REPLY_SOURCE_TYPES:
            raise ValueError(f"参数 {fact_id} 的 source_type 必须是 user_reply。")
        seen.add(fact_id)
        result.append(
            {
                "fact_id": fact_id,
                "value": value["value"],
                "unit": str(value.get("unit") or ""),
                "source_text": source_excerpt,
                "source_type": source_type,
            }
        )
    return result


def _candidate_parts(
    payload: Mapping[str, Any],
    source_text: str,
    *,
    fallback_updates: Mapping[str, Any] | None = None,
    fallback_parameters: list[dict[str, Any]] | None = None,
) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    """Parse a complete candidate while accepting role-specific corrections.

    A Modeling correction commonly returns only ``parameter_candidates`` while
    retaining the already validated Diagnosis result.  Conversely a Diagnosis
    correction may return only diagnostic fields.  The fallback values make
    that one correction composable without allowing an omitted section to
    erase a previously checked section.
    """

    parameter_keys = {"parameter_candidates", "parameters"}
    has_diagnostics = bool(
        {str(key) for key in payload}
        & (
            {
                *DIAGNOSTIC_IDS,
                *_DIAGNOSTIC_ALIASES.keys(),
                "diagnostic_updates",
                "diagnosis",
            }
        )
    )
    if has_diagnostics:
        diagnostic_payload: Mapping[str, Any] = payload
        if "diagnostic_updates" not in payload and "diagnosis" not in payload:
            diagnostic_payload = {
                key: value
                for key, value in payload.items()
                if key not in parameter_keys
            }
        updates = _diagnostic_updates(diagnostic_payload)
    else:
        updates = {
            str(key): dict(value) if isinstance(value, Mapping) else value
            for key, value in (fallback_updates or {}).items()
        }
    if any(key in payload for key in {*parameter_keys, "modeling"}):
        parameters = _parameter_candidates(payload, source_text)
    else:
        parameters = list(fallback_parameters or [])
    return updates, parameters


def _normalize_agent_payload(record: Any, role: AgentRole) -> Mapping[str, Any]:
    payload = getattr(record, "payload", record)
    if not isinstance(payload, Mapping):
        raise TypeError(f"{role.value} Agent 输出必须是 JSON 对象。")
    return payload


def _conflict_messages(payload: Mapping[str, Any]) -> list[str]:
    raw = payload.get("conflicts")
    if raw is None:
        return []
    if isinstance(raw, str):
        return [raw.strip()] if raw.strip() else []
    if isinstance(raw, (list, tuple)):
        return [str(item).strip() for item in raw if str(item).strip()]
    raise TypeError("Agent conflicts 必须是字符串或数组。")


def prepare_kernel_reply(
    session: EvidenceSession,
    text: str,
    *,
    mode: KernelReplyMode | str,
    coordinator: KernelAgentCoordinator | None = None,
    pending_actions: Any | None = None,
) -> dict[str, Any]:
    """Validate or interpret one user reply without mutating the session."""

    contract = build_kernel_input_contract(session, pending_actions=pending_actions)
    action = contract.get("action")
    if not action:
        raise ValueError(
            str(contract.get("disabled_reason") or "当前没有可提交的动作。")
        )
    if action == "confirm_task":
        if str(text or "").strip():
            raise ValueError("确认动作不需要输入内容，请直接确认软件试验边界与预算。")
        return {
            "action": action,
            "input_mode": None,
            "source_text": "",
            "diagnostic_updates": {},
            "parameter_candidates": [],
            "payload": {},
        }
    if action in _NO_INPUT_ACTIONS:
        if str(text or "").strip():
            raise ValueError("当前动作使用专用按钮，不需要填写回复内容。")
        return {
            "action": action,
            "input_mode": None,
            "source_text": "",
            "diagnostic_updates": {},
            "parameter_candidates": [],
            "payload": {},
        }
    try:
        if isinstance(mode, KernelReplyMode):
            selected_mode = mode
        elif str(mode) in _MODE_ALIASES:
            selected_mode = _MODE_ALIASES[str(mode)]
        else:
            selected_mode = KernelReplyMode(str(mode))
    except ValueError as exc:
        raise ValueError("未知输入模式：请选择自然语言或高级 JSON。") from exc
    if selected_mode.value not in contract.get("allowed_modes", []):
        raise ValueError("当前动作不允许使用该输入模式。")
    source_text = str(text or "")
    if not source_text.strip():
        raise ValueError("请填写回复内容，明确说明已知信息或“不知道”。")
    if selected_mode is KernelReplyMode.JSON:
        payload = parse_kernel_json(source_text)
        if action == "submit_answer":
            updates, parameters = _candidate_parts(payload, source_text)
            # A JSON source excerpt is valid only when it is literally present
            # in the submitted object; this path is intended for advanced users
            # and does not grant a shortcut around the evidence boundary.
            for value in updates.values():
                if not _evidence_in_source(source_text, value):
                    raise ValueError("诊断 evidence 必须出现在提交的 JSON 原文中。")
            if not updates and not parameters:
                raise ValueError("没有提交可验证的诊断或参数事实，请填写允许的字段。")
            return {
                "action": action,
                "input_mode": selected_mode.value,
                "source_text": source_text,
                "diagnostic_updates": updates,
                "parameter_candidates": parameters,
                "payload": payload,
            }
        return {
            "action": action,
            "input_mode": selected_mode.value,
            "source_text": source_text,
            "diagnostic_updates": {},
            "parameter_candidates": [],
            "payload": payload,
        }
    if coordinator is None:
        raise ValueError("自然语言回复需要配置 LLM；也可以切换到高级 JSON。")
    diagnosis_task_payload = {
        "user_response": source_text,
        "canonical_assessments": {
            "open_loop_stability": "stable|unstable|marginal",
            "nonminimum_phase": "minimum_phase|nonminimum_phase",
            "significant_delay": "not_significant|significant",
            "relative_degree": "low|moderate|high",
            "sensing_actuation_adequacy": "adequate|inadequate",
            "nonlinearity_strength": "weak|moderate|strong",
            "coupling_underactuation": "siso|coupled|underactuated",
            "uncertainty_variation": "small|moderate|large",
        },
        "required_output_schema": {
            "diagnostic_updates": {
                "<diagnostic_id>": {
                    "status": "known|unknown|not_relevant",
                    "evidence": "verbatim substring of user_response",
                    "assessment": "optional concise interpretation",
                    "confidence": "optional number from 0 to 1",
                }
            }
        },
        "allowed_diagnostic_ids": list(DIAGNOSTIC_IDS),
        "output_rules": [
            "Return exactly one JSON object with diagnostic_updates at the top level.",
            "Include only facts supported by a verbatim evidence substring.",
            "Use status=known whenever user_response explicitly asserts the fact, including an explicit absence such as no significant delay.",
            "Use status=unknown only when user_response explicitly states that the fact is unknown; otherwise omit that diagnostic field.",
            "Choose assessment from canonical_assessments when status=known.",
            "Omit confidence unless user_response itself provides a confidence value.",
            "Keep assessment concise and do not repeat task or registry context.",
        ],
    }
    modeling_task_payload = {
        "user_response": source_text,
        "allowed_parameter_fact_ids": sorted(_PARAMETER_FACT_IDS),
        "required_output_schema": {
            "parameter_candidates": [
                {
                    "fact_id": "one allowed parameter fact id",
                    "value": "value stated by the user",
                    "unit": "unit stated by the user",
                    "source_text": "verbatim substring of user_response",
                    "source_type": "user_reply",
                }
            ]
        },
        "output_rules": [
            "Return exactly one JSON object with parameter_candidates at the top level.",
            "Return an empty list when the user supplied no allowed numeric parameter fact.",
            "Do not copy example placeholders into the response.",
        ],
    }
    diagnosis_record = coordinator.execute(
        session,
        role=AgentRole.DIAGNOSIS,
        operation="user_reply",
        task_payload=diagnosis_task_payload,
        revision=session.revision,
    )
    # The single-agent baseline deliberately makes one provider call and lets
    # the same typed response carry both sections.  Multi-agent mode isolates
    # Diagnosis and Modeling into separate role calls before the Critic gate.
    modeling_record = (
        coordinator.execute(
            session,
            role=AgentRole.MODELING,
            operation="user_reply",
            task_payload=modeling_task_payload,
            revision=session.revision,
        )
        if coordinator.agent_mode == "multi"
        else diagnosis_record
    )
    diagnosis_payload = _normalize_agent_payload(diagnosis_record, AgentRole.DIAGNOSIS)
    modeling_payload = _normalize_agent_payload(modeling_record, AgentRole.MODELING)
    conflicts = _conflict_messages(diagnosis_payload) + _conflict_messages(
        modeling_payload
    )
    if conflicts:
        raise ValueError("检测到矛盾信息，请先澄清：" + "；".join(conflicts[:4]))
    if coordinator.agent_mode == "single":
        updates, parameters = _candidate_parts(diagnosis_payload, source_text)
    else:
        updates = _diagnostic_updates(diagnosis_payload)
        parameters = _parameter_candidates(modeling_payload, source_text)
    for value in updates.values():
        if not _evidence_in_source(source_text, value):
            raise ValueError("Diagnosis 提取的 evidence 不在用户原文中。")
    candidate = {"diagnostic_updates": updates, "parameter_candidates": parameters}
    if coordinator.agent_mode == "multi":
        reviewed_candidate = coordinator.review_and_correct(
            session,
            owner_role=AgentRole.MODELING,
            operation="user_reply",
            candidate=candidate,
            task_payload={"user_response": source_text},
        )
        if not isinstance(reviewed_candidate, Mapping):
            raise TypeError("Critic 修正结果必须是 JSON 对象。")
        updates, parameters = _candidate_parts(
            reviewed_candidate,
            source_text,
            fallback_updates=updates,
            fallback_parameters=parameters,
        )
        for value in updates.values():
            if not _evidence_in_source(source_text, value):
                raise ValueError("Critic 修正后的 Diagnosis evidence 不在用户原文中。")
        candidate = {
            "diagnostic_updates": updates,
            "parameter_candidates": parameters,
        }
    if not updates and not parameters:
        raise ValueError("没有从回复中提取到可验证的诊断或参数事实，请补充原文证据。")
    return {
        "action": action,
        "input_mode": selected_mode.value,
        "source_text": source_text,
        "diagnostic_updates": updates,
        "parameter_candidates": parameters,
        "payload": candidate,
    }


__all__ = [
    "KernelReplyMode",
    "build_kernel_input_contract",
    "parse_kernel_json",
    "prepare_kernel_reply",
]
