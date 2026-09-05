from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Mapping
from copy import deepcopy
from pathlib import Path
from threading import Event, RLock
from typing import Any

from cfdc.agents import wrap_agent_adapter
from cfdc.diagnosis import OpenAICompatibleDiagnosticAdapter
from cfdc.kernel import KernelActionError, WorkflowService
from cfdc.kernel.agents import KernelAgentCoordinator
from cfdc.kernel.cases import case_learning_material, public_training_case
from cfdc.kernel.replies import (
    KernelReplyMode,
    build_kernel_input_contract,
    prepare_kernel_reply,
)
from cfdc.kernel.session import registered_task_scope_fingerprint


class _ReplyPreparation:
    def __init__(self) -> None:
        self.done = Event()
        self.result: dict[str, Any] | None = None
        self.error: Exception | None = None


_KERNEL_REPLY_PREPARATIONS: dict[str, _ReplyPreparation] = {}
_KERNEL_REPLY_PREPARATIONS_LOCK = RLock()

KERNEL_STAGE_LABELS = (
    "任务",
    "诊断",
    "取证",
    "路线／特征",
    "控制器",
    "冻结",
    "评价",
    "调优／确认",
    "结果",
)

_SAFE_WEB_ERROR_MESSAGES = frozenset(
    {
        "响应时间偏好必须大于 0。",
        "不同实验预算必须是大于等于 1 的整数。",
        "扰动重复成功率下限必须在 0 到 1 之间。",
        "请先确认软件试验边界与预算。",
        "请填写回复内容，明确说明已知信息或“不知道”。",
        "当前没有待处理动作，请刷新页面。",
        "内置 RAG 尚未在 WebUI 启动前准备完成。",
    }
)


def validate_kernel_artifact(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Validate one typed public artifact without mutating a session."""

    if not isinstance(payload, Mapping):
        raise TypeError("Artifact 必须是 JSON 对象。")
    from cfdc.experiments.protocols import ExperimentProtocol
    from cfdc.kernel.contracts import (
        FEATURE_ARTIFACT_VERSION,
        QUALIFICATION_VERSION,
        ControllerFreeze,
        EvaluationPacket,
        TaskContract,
        fingerprint,
    )
    from cfdc.kernel.controllers import ControllerIR
    from cfdc.kernel.judging import JUDGE_VERSION
    from cfdc.kernel.session import EvidenceSession
    from cfdc.kernel.tuning import TuningContract

    value = dict(payload)
    if value.get("session_version"):
        artifact = EvidenceSession.from_dict(value)
        kind = "session"
        artifact_fingerprint = artifact.fingerprint
    elif value.get("protocol_version"):
        artifact = ExperimentProtocol.from_mapping(value)
        kind = "protocol"
        artifact_fingerprint = artifact.fingerprint
    elif value.get("ir_version"):
        artifact = ControllerIR.from_mapping(value)
        kind = "controller_ir"
        artifact_fingerprint = artifact.fingerprint
    elif value.get("freeze_version"):
        artifact = ControllerFreeze.from_mapping(value)
        kind = "freeze"
        artifact_fingerprint = artifact.to_dict()["freeze_fingerprint"]
    elif value.get("packet_version"):
        artifact = EvaluationPacket.from_mapping(value)
        kind = "evaluation_packet"
        artifact_fingerprint = artifact.to_dict()["packet_fingerprint"]
    elif value.get("contract_version") == "cfdc-tuning/v1.0":
        artifact = TuningContract.from_mapping(value)
        kind = "tuning_contract"
        artifact_fingerprint = artifact.fingerprint
    elif value.get("schema_version") or value.get("task_type"):
        artifact = TaskContract.from_user_input(value)
        kind = "task"
        artifact_fingerprint = artifact.fingerprint
    else:
        typed_fingerprints = {
            ("feature_version", "cfdc-features/v1"): (
                "artifact_fingerprint",
                "features",
            ),
            ("feature_version", FEATURE_ARTIFACT_VERSION): (
                "artifact_fingerprint",
                "features",
            ),
            ("qualification_version", "cfdc-qualification/v1"): (
                "qualification_fingerprint",
                "qualification",
            ),
            ("qualification_version", QUALIFICATION_VERSION): (
                "qualification_fingerprint",
                "qualification",
            ),
            ("upload_version", "cfdc-upload/v1"): (
                "upload_fingerprint",
                "upload_receipt",
            ),
            ("import_version", "cfdc-import/v1"): (
                "import_fingerprint",
                "import_report",
            ),
            ("judge_version", "cfdc-independent-judge/v1"): (
                "judge_fingerprint",
                "evaluation",
            ),
            ("judge_version", JUDGE_VERSION): (
                "judge_fingerprint",
                "evaluation",
            ),
            ("feedback_version", "cfdc-feedback/v1"): (
                "feedback_fingerprint",
                "feedback",
            ),
            ("confirmation_version", "cfdc-confirmation/v1"): (
                "confirmation_fingerprint",
                "confirmation",
            ),
            ("result_version", "cfdc-result/v1"): (
                "result_fingerprint",
                "result",
            ),
        }
        matches = [
            fingerprint_contract
            for (
                version_field,
                version,
            ), fingerprint_contract in typed_fingerprints.items()
            if value.get(version_field) == version
        ]
        if len(matches) != 1:
            raise ValueError("无法识别版本化 CFDC Artifact 类型。")
        fingerprint_field, kind = matches[0]
        if not value.get(fingerprint_field):
            raise ValueError(f"{fingerprint_field}_required")
        supplied = str(value.pop(fingerprint_field))
        expected = fingerprint(value)
        if supplied != expected:
            raise ValueError(f"{fingerprint_field}_mismatch")
        artifact_fingerprint = expected
    return {
        "status": "valid",
        "artifact_kind": kind,
        "artifact_fingerprint": artifact_fingerprint,
    }


_KERNEL_PUBLIC_ACTIONS = frozenset(
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

_KERNEL_ACTION_ALIASES = {
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
    "run_tuning": "run_feedback_iteration",
}


def parse_names(value: str | None) -> list[str]:
    text = "" if value is None else str(value)
    names: list[str] = []
    for item in text.replace("、", ",").replace("\n", ",").split(","):
        name = re.sub(r"^(?:and|与|和)\s+", "", item.strip(), flags=re.IGNORECASE)
        if name:
            names.append(name)
    return names


def _required_finite_number(payload: Mapping[str, Any], key: str, label: str) -> float:
    value = payload.get(key)
    if isinstance(value, bool) or value is None:
        raise ValueError(f"请填写{label}。")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label}必须是有限数字。") from exc
    if not math.isfinite(number):
        raise ValueError(f"{label}必须是有限数字。")
    return number


def _optional_finite_number(
    payload: Mapping[str, Any], key: str, label: str
) -> float | None:
    value = payload.get(key)
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    if isinstance(value, bool):
        raise ValueError(f"{label}必须是有限数字。")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label}必须是有限数字。") from exc
    if not math.isfinite(number):
        raise ValueError(f"{label}必须是有限数字。")
    return number


def _validated_web_optional_fields(payload: dict[str, Any]) -> None:
    for key, label in (
        ("reference", "目标参考值"),
        ("initial_output_value", "初始输出数值"),
    ):
        if key in payload:
            payload[key] = _optional_finite_number(payload, key, label)

    if "response_time_preference_s" in payload:
        response_time = _optional_finite_number(
            payload,
            "response_time_preference_s",
            "响应时间偏好",
        )
        if response_time is not None and response_time <= 0:
            raise ValueError("响应时间偏好必须大于 0。")
        payload["response_time_preference_s"] = response_time

    raw_requirements = payload.get("success_requirements")
    if raw_requirements is not None and not isinstance(raw_requirements, Mapping):
        raise ValueError("性能要求必须是 JSON 对象。")
    requirements = dict(raw_requirements or {})
    requirement_rules = {
        "final_abs_error_max": ("最大终值绝对误差", "positive"),
        "overshoot_max": ("最大超调", "nonnegative"),
        "settling_time_max_s": ("最大调节时间", "positive"),
        "hold_duration_min_s": ("最短保持时间", "positive"),
        "perturbed_success_rate_min": ("扰动重复成功率下限", "rate"),
    }
    for key, (label, rule) in requirement_rules.items():
        source = payload if key in payload else requirements
        if key not in source:
            continue
        number = _optional_finite_number(source, key, label)
        if number is None:
            raise ValueError(f"已启用{label}，请填写数值。")
        if rule == "positive" and number <= 0:
            raise ValueError(f"{label}必须大于 0。")
        if rule == "nonnegative" and number < 0:
            raise ValueError(f"{label}不能小于 0。")
        if rule == "rate" and not 0 <= number <= 1:
            raise ValueError(f"{label}必须在 0 到 1 之间。")
        source[key] = number
    if raw_requirements is not None:
        payload["success_requirements"] = requirements

    raw_budgets = payload.get("budgets")
    if raw_budgets is not None and not isinstance(raw_budgets, Mapping):
        raise ValueError("实验预算必须是 JSON 对象。")
    budgets = dict(raw_budgets or {})
    if "distinct_experiments" in budgets:
        distinct = _optional_finite_number(
            budgets,
            "distinct_experiments",
            "不同实验预算",
        )
        if distinct is None or distinct < 1 or not distinct.is_integer():
            raise ValueError("不同实验预算必须是大于等于 1 的整数。")
        budgets["distinct_experiments"] = int(distinct)
    if "cumulative_excitation_time_s" in budgets:
        cumulative = _optional_finite_number(
            budgets,
            "cumulative_excitation_time_s",
            "累计激励预算",
        )
        if cumulative is None or cumulative <= 0:
            raise ValueError("累计激励预算必须大于 0。")
        budgets["cumulative_excitation_time_s"] = cumulative
    if raw_budgets is not None:
        payload["budgets"] = budgets


def _validated_web_task(task: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(task, Mapping):
        raise TypeError("Web 任务合同必须是 JSON 对象。")
    payload = dict(task)
    description = str(payload.get("description") or "").strip()
    if not description:
        raise ValueError("请描述需要控制的对象和目标。")
    measured_signals = payload.get("measured_signals")
    control_inputs = payload.get("control_inputs")
    if control_inputs is None:
        control_inputs = payload.get("control_input")
    if isinstance(measured_signals, str):
        measured_signals = parse_names(measured_signals)
    if isinstance(control_inputs, str):
        control_inputs = parse_names(control_inputs)
    if not isinstance(measured_signals, (list, tuple)) or not measured_signals:
        raise ValueError("请至少填写一个观测输出。")
    if not isinstance(control_inputs, (list, tuple)) or not control_inputs:
        raise ValueError("请至少填写一个控制输入。")

    input_min = _required_finite_number(payload, "input_min", "控制输入下界")
    input_max = _required_finite_number(payload, "input_max", "控制输入上界")
    state_stop = _required_finite_number(payload, "state_stop", "状态停止阈值")
    if input_min >= input_max:
        raise ValueError("控制输入下界必须小于上界。")
    if state_stop <= 0:
        raise ValueError("状态停止阈值必须大于 0。")

    output_min = _optional_finite_number(payload, "output_min", "观测输出下界")
    output_max = _optional_finite_number(payload, "output_max", "观测输出上界")
    if (output_min is None) != (output_max is None):
        raise ValueError("观测输出下界和上界必须同时填写或同时留空。")
    if output_min is not None and output_max is not None and output_min >= output_max:
        raise ValueError("观测输出下界必须小于上界。")

    _validated_web_optional_fields(payload)

    payload.update(
        description=description,
        measured_signals=[str(item).strip() for item in measured_signals],
        control_inputs=[str(item).strip() for item in control_inputs],
        control_input=str(control_inputs[0]).strip(),
        input_min=input_min,
        input_max=input_max,
        output_min=output_min,
        output_max=output_max,
        state_stop=state_stop,
        workspace={**dict(payload.get("workspace") or {}), "source": "web"},
    )
    return payload


def _kernel_pending_actions(session) -> tuple[dict[str, Any], ...]:
    normalized: list[dict[str, Any]] = []
    evaluation_provider = session.provider_bindings.get("evaluation")
    registered_software_confirmation = (
        isinstance(session.registered_case_binding, Mapping)
        and isinstance(evaluation_provider, Mapping)
        and str(evaluation_provider.get("execution_kind") or "") == "software"
    )
    for item in session.pending_actions or ():
        value = dict(item)
        action = str(value.get("action") or "")
        if action in {"run_experiment", "retry"}:
            value.setdefault("ui_action", "evidence")
        elif action == "record_fresh_confirmation" and (
            registered_software_confirmation
        ):
            value["ui_action"] = "confirm_result"
        normalized.append(value)
    if normalized:
        return tuple(normalized)
    if (
        session.status == "intake"
        and not session.task.budget_confirmed
        and not session.read_only
    ):
        return (
            {
                "kind": "budget",
                "action": "confirm_task",
                "reason": "task_boundary_confirmation_required",
            },
        )
    return ()


def _kernel_action_id(
    session_id: str,
    revision: int,
    action: str,
    payload: Mapping[str, Any],
) -> str:
    try:
        canonical = json.dumps(
            dict(payload),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ValueError("kernel_payload_not_json") from exc
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:24]
    return f"web:{session_id}:{revision}:{action}:{digest}"


def _kernel_action_already_recorded(session, action_id: str) -> bool:
    return any(event.action_id == action_id for event in session.events)


def kernel_action_error_payload(
    exc: Exception, app_state: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    """Describe a failed Web action without exposing internals or stale state."""

    session_revision: int | None = None
    if isinstance(app_state, Mapping):
        session_id = str(app_state.get("kernel_session_id") or "")
        session_dir = app_state.get("kernel_session_dir")
        if session_id and session_dir:
            try:
                session_revision = (
                    WorkflowService(session_dir).read(session_id).revision
                )
            except (OSError, ValueError):
                session_revision = None
    if isinstance(exc, KernelActionError):
        result = exc.to_dict()
        result["revision"] = (
            session_revision if session_revision is not None else result["revision"]
        )
        return result
    raw_code = str(exc).split(":", 1)[0].strip()
    code = (
        raw_code if re.fullmatch(r"[a-z][a-z0-9_]{0,63}", raw_code) else "action_failed"
    )
    raw_message = str(exc).strip()
    message_cn = (
        raw_message
        if raw_message in _SAFE_WEB_ERROR_MESSAGES
        else "操作未完成；请根据当前会话状态检查输入后重试。"
    )
    return {
        "code": code,
        "message_cn": message_cn,
        "receipt_saved": False,
        "revision": session_revision,
        "next_step": "refresh_and_retry",
        "trace_id": hashlib.sha256(code.encode("utf-8")).hexdigest()[:16],
    }


def _normalise_kernel_action(action: str) -> str:
    return _KERNEL_ACTION_ALIASES.get(action, action)


def start_kernel_app_run(
    task: Mapping[str, Any],
    *,
    session_dir: str | Path | None = None,
    rag_index_dir: str | Path | None = None,
    rag_snapshot: str | None = None,
    use_rag: bool = True,
    llm_configured: bool = False,
    provider_case_id: str | None = None,
    evidence_mode: str = "automatic",
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Create a Kernel Web task from one explicit public task contract."""

    service = WorkflowService(session_dir or Path("output") / "kernel-sessions")
    resolved_snapshot = rag_snapshot
    if use_rag and rag_snapshot and not rag_index_dir:
        raise ValueError("rag_snapshot_requires_index_dir")
    if use_rag and rag_index_dir:
        from cfdc.rag import load_index

        index = load_index(
            rag_index_dir, snapshot_name=rag_snapshot, load_encoder=False
        )
        resolved_snapshot = index.index_snapshot
    rag_active = bool(use_rag and resolved_snapshot)
    agent_config = {
        "mode": "multi",
        "rag_requested": bool(use_rag),
        "rag_enabled": rag_active,
        "rag_status": (
            "active" if rag_active else "not_initialized" if use_rag else "disabled"
        ),
        "rag_index_dir": str(rag_index_dir) if rag_index_dir else None,
        "llm_configured": bool(llm_configured),
    }
    case_id = str(provider_case_id or "").strip()
    if case_id:
        from cfdc.kernel.contracts import TaskContract

        registered_task = TaskContract.from_user_input(
            public_training_case(case_id)["task"]
        )
        submitted_task = TaskContract.from_user_input(task)
        if registered_task_scope_fingerprint(
            submitted_task
        ) != registered_task_scope_fingerprint(registered_task):
            raise ValueError("registered_case_task_contract_mismatch")
        session = service.start_registered_case(
            case_id,
            agent_config=agent_config,
            rag_snapshot=resolved_snapshot,
            evidence_mode=evidence_mode,
        )
    else:
        payload = _validated_web_task(task)
        session = service.start(
            payload,
            agent_config=agent_config,
            rag_snapshot=resolved_snapshot,
        )
    report = _kernel_report(session)
    return report, {
        "kernel_session_id": session.session_id,
        "kernel_session_dir": str(service.root),
        "kernel_revision": session.revision,
        "workflow_version": session.workflow_version,
        "pending_actions": list(report["pending_actions"]),
        "rag_index_dir": str(rag_index_dir) if rag_index_dir else None,
        "rag_snapshot": resolved_snapshot,
        "use_rag": bool(use_rag),
    }


def _training_registries(case_id: str):
    from cfdc.sim.training import build_training_provider_registries

    return build_training_provider_registries(case_id)


def _run_configured_automatic(
    service: WorkflowService,
    session,
):
    binding = session.registered_case_binding
    if not isinstance(binding, Mapping):
        return session
    case_id = str(binding.get("case_id") or "").strip()
    if not case_id:
        return session
    identification_registry, _, evaluation_registry, _ = _training_registries(case_id)
    return service.run_until_blocked(
        session.session_id,
        provider_registry=identification_registry,
        identification_provider_id=str(
            binding["provider_references"]["identification"]["provider_id"]
        ),
        evaluation_provider_registry=evaluation_registry,
        evaluation_provider_id=str(
            binding["provider_references"]["evaluation"]["provider_id"]
        ),
    )


def continue_kernel_app_run(
    app_state: Mapping[str, Any],
    *,
    action: str,
    payload: Mapping[str, Any] | None = None,
    request_identity: Mapping[str, Any] | None = None,
    reply_source_text: str | None = None,
    reply_input_mode: str | None = None,
    agent_records: Any = (),
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Apply one revisioned Kernel action and return its public projection."""

    session_id = str(app_state.get("kernel_session_id") or "")
    if not session_id:
        raise ValueError("当前没有 CFDC Kernel 任务会话。")
    state_workflow = str(app_state.get("workflow_version") or "")
    if not state_workflow.startswith("cfdc-v6-kernel"):
        raise ValueError("当前页面状态不属于 CFDC Kernel，不能提交动作。")
    service = WorkflowService(
        app_state.get("kernel_session_dir") or Path("output") / "kernel-sessions"
    )
    session = service.read(session_id)
    if not str(session.workflow_version).startswith("cfdc-v6-kernel"):
        raise ValueError("当前会话不属于 CFDC Kernel，不能提交动作。")
    if not isinstance(action, str) or action not in _KERNEL_PUBLIC_ACTIONS:
        raise ValueError(f"未知 Kernel 动作：{action}")
    if not isinstance(payload, Mapping):
        if payload is not None:
            raise ValueError("Kernel 动作 payload 必须是 JSON 对象。")
        raw: dict[str, Any] = {}
    else:
        raw = dict(payload)
    if "action_id" in raw or "revision" in raw:
        raise ValueError("Kernel payload 不能覆盖 action_id 或 revision。")
    page_revision = app_state.get("kernel_revision")
    if isinstance(page_revision, bool) or not isinstance(page_revision, int):
        raise ValueError("页面 Kernel revision 无效，请刷新后重试。")
    identity = dict(request_identity) if isinstance(request_identity, Mapping) else {}
    if reply_input_mode is not None:
        identity.setdefault("input_mode", str(reply_input_mode))
    if reply_source_text is not None:
        identity.setdefault("source_text", str(reply_source_text))
    action_for_identity = (
        identity
        if reply_source_text is not None or reply_input_mode is not None
        else {**identity, "payload": raw}
        if identity
        else raw
    )
    action_id = _kernel_action_id(
        session_id, page_revision, action, action_for_identity
    )
    if _kernel_action_already_recorded(session, action_id):
        report = _kernel_report(session)
        return report, {
            **dict(app_state),
            "kernel_revision": session.revision,
            "workflow_version": session.workflow_version,
            "pending_actions": list(report["pending_actions"]),
        }
    if page_revision != session.revision:
        raise ValueError("stale_revision: 页面状态已更新，请刷新后重试。")

    pending = _kernel_pending_actions(session)
    if action != "cancel" and pending:
        expected = pending[0]
        expected_action = str(
            expected.get("ui_action")
            or _normalise_kernel_action(str(expected.get("action") or ""))
        )
        if not expected_action:
            raise ValueError("当前待处理动作没有可执行入口。")
        diagnostic_revision_allowed = (
            action == "revise_diagnostic" and expected_action == "answer"
        )
        if action != expected_action and not diagnostic_revision_allowed:
            raise ValueError(f"当前待处理动作是 {expected_action}，不能执行 {action}。")
    elif action != "cancel":
        if session.status in {"performance_met", "capability_gap", "cancelled"}:
            raise ValueError(f"当前会话已终止：{session.status}")
        raise ValueError("当前没有待处理动作，请刷新页面读取最新状态。")

    if action == "confirm_task":
        session = service.confirm_task(
            session_id,
            action_id=action_id,
            revision=page_revision,
            budgets=raw or None,
        )
    elif action == "answer":
        diagnostic_payload = raw.get("diagnostic_updates")
        if diagnostic_payload is None:
            diagnostic_payload = raw.get("diagnosis")
        if diagnostic_payload is None:
            diagnostic_payload = {
                key: value
                for key, value in raw.items()
                if key
                not in {
                    "parameter_candidates",
                    "parameters",
                    "source_text",
                    "input_mode",
                }
            }
        parameter_payload = raw.get("parameter_candidates")
        if parameter_payload is None:
            parameter_payload = raw.get("parameters", ())
        session = service.submit_reply(
            session_id,
            action_id=action_id,
            revision=page_revision,
            diagnostic_updates=diagnostic_payload,
            parameter_facts=parameter_payload,
            source_text=reply_source_text or str(raw.get("source_text") or ""),
            input_mode=reply_input_mode or str(raw.get("input_mode") or "json"),
            agent_records=agent_records,
        )
    elif action == "revise_diagnostic":
        session = service.revise_diagnostic(
            session_id,
            action_id=action_id,
            revision=page_revision,
            diagnostic_updates=raw.get("diagnostic_updates", raw),
            source_text=reply_source_text or str(raw.get("source_text") or ""),
            confirmation=bool(raw.get("confirmation", False)),
        )
    elif action == "relevance":
        session = service.apply_task_relevance(
            session_id,
            action_id=action_id,
            revision=page_revision,
            declarations=raw,
        )
    elif action == "advance":
        session = service.advance(
            session_id, action_id=action_id, revision=page_revision
        )
    elif action == "evidence":
        session = service.submit_evidence(
            session_id,
            action_id=action_id,
            revision=page_revision,
            evidence=raw,
        )
    elif action == "phase":
        session = service.record_phase_result(
            session_id,
            action_id=action_id,
            revision=page_revision,
            result=raw,
        )
    elif action == "features":
        quality = raw.pop("quality", None)
        session = service.submit_features(
            session_id,
            action_id=action_id,
            revision=page_revision,
            features=raw.get("features", raw),
            quality=quality,
        )
    elif action == "controller":
        session = service.submit_controller(
            session_id,
            action_id=action_id,
            revision=page_revision,
            controller=raw.get("controller", raw),
            phases=raw.get("phases"),
        )
    elif action == "freeze":
        session = service.freeze_controller(
            session_id,
            action_id=action_id,
            revision=page_revision,
            controller=raw["controller"],
            runtime_contract=raw["runtime_contract"],
            evaluation_contract=raw["evaluation_contract"],
        )
    elif action == "evaluation":
        session = service.record_evaluation(
            session_id,
            action_id=action_id,
            revision=page_revision,
            packet=raw,
        )
    elif action == "cancel":
        session = service.cancel(
            session_id,
            action_id=action_id,
            revision=page_revision,
            reason=str(raw.get("reason", "operator_cancelled")),
        )
    elif action == "replay":
        session = service.replay_evaluation(
            session_id,
            action_id=action_id,
            revision=page_revision,
        )
    elif action == "confirmation":
        session = service.record_confirmation(
            session_id,
            action_id=action_id,
            revision=page_revision,
            packet=raw,
        )
    elif action == "compile_protocol":
        session = service.compile_protocol(
            session_id,
            action_id=action_id,
            revision=page_revision,
            request=raw or None,
        )
    elif action == "prepare_operator_handoff":
        session = service.prepare_operator_handoff(
            session_id,
            action_id=action_id,
            revision=page_revision,
        )
    elif action == "prepare_training_exercise_bundle":
        binding = session.registered_case_binding
        if not isinstance(binding, Mapping):
            raise ValueError("当前会话没有注册可执行的软件案例 Provider。")
        case_id = str(binding.get("case_id") or "")
        identification_registry, identification_id, _, _ = _training_registries(case_id)
        session = service.prepare_training_exercise_bundle(
            session_id,
            action_id=action_id,
            revision=page_revision,
            provider_registry=identification_registry,
            provider_id=identification_id,
        )
    elif action == "record_operator_report":
        session = service.record_operator_report(
            session_id,
            action_id=action_id,
            revision=page_revision,
            report=raw,
        )
    elif action == "ingest_upload":
        paths = raw.get("paths") or raw.get("files") or ()
        if isinstance(paths, str):
            paths = [paths]
        session = service.ingest_upload(
            session_id,
            action_id=action_id,
            revision=page_revision,
            paths=[Path(item) for item in paths],
            stopped_on_limit=bool(raw.get("stopped_on_limit", False)),
        )
    elif action == "derive_features":
        session = service.derive_features(
            session_id,
            action_id=action_id,
            revision=page_revision,
        )
    elif action == "synthesize_controller":
        session = service.synthesize_controller(
            session_id,
            action_id=action_id,
            revision=page_revision,
        )
    elif action == "qualify_controller":
        session = service.qualify_controller(
            session_id,
            action_id=action_id,
            revision=page_revision,
        )
    elif action in {
        "run_provider",
        "run_evaluation",
        "run_feedback_iteration",
        "confirm_result",
    }:
        binding = session.registered_case_binding
        if not isinstance(binding, Mapping):
            raise ValueError("当前会话没有注册可执行的软件案例 Provider。")
        case_id = str(binding.get("case_id") or "")
        (
            identification_registry,
            identification_id,
            evaluation_registry,
            evaluation_id,
        ) = _training_registries(case_id)
        if action == "run_provider":
            session = service.run_provider(
                session_id,
                action_id=action_id,
                revision=page_revision,
                provider_registry=identification_registry,
                provider_id=identification_id,
            )
        elif action == "run_evaluation":
            session = service.run_evaluation(
                session_id,
                action_id=action_id,
                revision=page_revision,
                provider_registry=evaluation_registry,
                provider_id=evaluation_id,
            )
        elif action == "run_feedback_iteration":
            session = service.run_feedback_iteration(
                session_id,
                action_id=action_id,
                revision=page_revision,
                provider_registry=evaluation_registry,
                provider_id=evaluation_id,
                contract=raw or None,
            )
        else:
            session = service.confirm_result(
                session_id,
                action_id=action_id,
                revision=page_revision,
                provider_registry=evaluation_registry,
                provider_id=evaluation_id,
            )
    session = _run_configured_automatic(service, session)
    report = _kernel_report(session)
    return report, {
        **dict(app_state),
        "kernel_revision": session.revision,
        "workflow_version": session.workflow_version,
        "pending_actions": list(report["pending_actions"]),
    }


def _kernel_report(session) -> dict[str, Any]:
    readiness = session.ledger.readiness()
    pending_actions = _kernel_pending_actions(session)
    projection = WorkflowService.project(session)
    binding = session.registered_case_binding
    case_id = str(binding.get("case_id") or "") if isinstance(binding, Mapping) else ""
    education = case_learning_material(case_id or None)
    return {
        "workflow_version": session.workflow_version,
        "session_id": session.session_id,
        "status": session.status,
        "revision": session.revision,
        "read_only": session.read_only,
        "active_protocol_fingerprint": session.active_protocol_fingerprint,
        "task": session.task.to_dict(),
        "parameter_facts": [dict(item) for item in session.parameter_facts],
        "diagnostic": {
            "readiness": readiness.to_dict(),
            "entries": [item.to_dict() for item in session.ledger.entries],
        },
        "readiness_gates": projection["readiness_gates"],
        "information_budget": projection["information_budget"],
        "route": dict(session.route) if session.route else None,
        "features": dict(session.feature_artifact)
        if session.feature_artifact
        else None,
        "controller": (
            dict(session.controller_candidate) if session.controller_candidate else None
        ),
        "phase_plan": dict(session.phase_plan) if session.phase_plan else None,
        "phase_results": [dict(item) for item in session.phase_results],
        "freeze": dict(session.controller_freeze)
        if session.controller_freeze
        else None,
        "evaluation": dict(session.evaluation) if session.evaluation else None,
        "tuning": dict(session.tuning) if session.tuning else None,
        "confirmation": dict(session.confirmation) if session.confirmation else None,
        "protocols": [dict(item) for item in session.protocols],
        "operator_handoffs": [dict(item) for item in session.operator_handoffs],
        "operator_reports": [dict(item) for item in session.operator_reports],
        "training_exercise_bundles": [
            dict(item) for item in session.training_exercise_bundles
        ],
        "education": education,
        "teaching_steps": [
            {
                "id": "task_boundary",
                "title": "1. 任务与边界",
                "status": "done" if session.task.budget_confirmed else "current",
            },
            {
                "id": "evidence_controller",
                "title": "2. 证据与控制器",
                "status": "done"
                if session.controller_candidate or session.feature_artifact
                else "current",
            },
            {
                "id": "evaluation_confirmation",
                "title": "3. 评价与确认",
                "status": "done"
                if session.evaluation or session.confirmation
                else "current",
            },
        ],
        "upload_attempts": [dict(item) for item in session.upload_attempts],
        "qualification": dict(session.controller_qualification)
        if session.controller_qualification
        else None,
        "provider_bindings": dict(session.provider_bindings),
        "registered_case_binding": (
            dict(session.registered_case_binding)
            if session.registered_case_binding is not None
            else None
        ),
        "import_report": dict(session.import_report) if session.import_report else None,
        "evidence": [dict(item) for item in session.evidence],
        "evaluation_packets": [dict(item) for item in session.evaluation_packets],
        "evaluation_replays": [dict(item) for item in session.evaluation_replays],
        "agent_config": dict(session.agent_config) if session.agent_config else None,
        "agent_records": [dict(item) for item in session.agent_records],
        "rag_snapshot": session.rag_snapshot,
        "events": [event.to_dict() for event in session.events],
        "pending_actions": [dict(item) for item in pending_actions],
        "input_contract": build_kernel_input_contract(
            session,
            pending_actions=pending_actions,
        ),
        "stages": list(KERNEL_STAGE_LABELS),
    }


def start_kernel_case_run(
    case_id: str,
    **kwargs: Any,
) -> tuple[dict[str, Any], dict[str, Any]]:
    case = public_training_case(case_id)
    return start_kernel_app_run(case["task"], provider_case_id=case_id, **kwargs)


def load_kernel_app_run(
    session_id: str,
    *,
    session_dir: str | Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    service = WorkflowService(session_dir or Path("output") / "kernel-sessions")
    session = service.read(str(session_id))
    if not str(session.workflow_version).startswith("cfdc-v6-kernel"):
        raise ValueError("WebUI 只接受 CFDC Kernel 会话。")
    report = _kernel_report(session)
    return report, {
        "kernel_session_id": session.session_id,
        "kernel_session_dir": str(service.root),
        "kernel_revision": session.revision,
        "workflow_version": session.workflow_version,
        "pending_actions": list(report["pending_actions"]),
    }


def import_v3_app_run(
    source: str | Path,
    *,
    session_dir: str | Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    service = WorkflowService(session_dir or Path("output") / "kernel-sessions")
    session = service.import_v3(source)
    report = _kernel_report(session)
    return report, {
        "kernel_session_id": session.session_id,
        "kernel_session_dir": str(service.root),
        "kernel_revision": session.revision,
        "workflow_version": session.workflow_version,
        "pending_actions": list(report["pending_actions"]),
    }


def export_kernel_app_bundle(app_state: Mapping[str, Any]) -> str:
    session_id = str(app_state.get("kernel_session_id") or "")
    if not session_id:
        raise ValueError("当前没有 CFDC Kernel 会话。")
    service = WorkflowService(
        app_state.get("kernel_session_dir") or Path("output") / "kernel-sessions"
    )
    return str(service.export_result_bundle(session_id))


def export_kernel_app_artifact(
    app_state: Mapping[str, Any],
    artifact_kind: str,
) -> str:
    session_id = str(app_state.get("kernel_session_id") or "")
    if not session_id:
        raise ValueError("当前没有 CFDC Kernel 会话。")
    service = WorkflowService(
        app_state.get("kernel_session_dir") or Path("output") / "kernel-sessions"
    )
    return str(service.export_artifact(session_id, artifact_kind))


def build_adapter(
    use_llm: bool,
    base_url: str | None,
    model: str | None,
    api_key: str | None,
    *,
    rag_index_dir: str | Path | None = None,
    rag_snapshot: str | None = None,
    use_rag: bool = True,
    timeout_s: float = 60.0,
    max_tokens: int = 2200,
):
    if not use_llm:
        return None
    adapter = OpenAICompatibleDiagnosticAdapter(
        base_url=str(base_url or "").strip() or None,
        model=str(model or "").strip() or None,
        api_key=str(api_key or "").strip() or None,
        timeout_s=timeout_s,
        max_tokens=max_tokens,
    )
    return wrap_agent_adapter(
        adapter,
        agent_mode="multi",
        rag_index_dir=str(rag_index_dir) if rag_index_dir is not None else None,
        rag_snapshot=rag_snapshot,
        use_rag=use_rag,
    )


def _build_app_adapter(
    base_url: str | None,
    model: str | None,
    api_key: str | None,
    *,
    rag_index_dir: str | Path | None,
    rag_snapshot: str | None,
    use_rag: bool,
):
    return build_adapter(
        True,
        base_url,
        model,
        api_key,
        rag_index_dir=rag_index_dir,
        rag_snapshot=rag_snapshot,
        use_rag=use_rag,
    )


def _selected_reply_mode(
    mode: KernelReplyMode | str,
    contract: Mapping[str, Any],
) -> KernelReplyMode:
    allowed = [str(item) for item in contract.get("allowed_modes", ())]
    if not allowed:
        return KernelReplyMode.NATURAL_LANGUAGE
    if len(allowed) == 1:
        return KernelReplyMode(allowed[0])
    if isinstance(mode, KernelReplyMode):
        selected = mode
    elif str(mode) in {"自然语言", "natural_language"}:
        selected = KernelReplyMode.NATURAL_LANGUAGE
    elif str(mode) in {"高级 JSON", "json"}:
        selected = KernelReplyMode.JSON
    else:
        raise ValueError("未知输入模式：请选择自然语言或高级 JSON。")
    if selected.value not in allowed:
        raise ValueError("当前动作不允许使用该输入模式。")
    return selected


def prepare_kernel_reply_for_ui(
    app_state: Mapping[str, Any],
    text: str,
    *,
    mode: KernelReplyMode | str,
    base_url: str | None,
    model: str | None,
    api_key: str | None,
) -> dict[str, Any]:
    """Prepare one Web reply through the fixed multi-agent Kernel boundary."""

    session_id = str(app_state.get("kernel_session_id") or "")
    if not session_id:
        raise ValueError("当前没有 CFDC Kernel 任务会话。")
    if not str(app_state.get("workflow_version") or "").startswith("cfdc-v6-kernel"):
        raise ValueError("当前页面状态不属于 CFDC Kernel。")
    service = WorkflowService(
        app_state.get("kernel_session_dir") or Path("output") / "kernel-sessions"
    )
    session = service.read(session_id)
    projected_pending = app_state.get("pending_actions") or _kernel_pending_actions(
        session
    )
    contract = build_kernel_input_contract(session, pending_actions=projected_pending)
    selected_mode = _selected_reply_mode(mode, contract)
    contract_action = str(contract.get("action") or "")
    public_action = _normalise_kernel_action(contract_action)
    raw_text = str(text or "")

    if not contract_action or contract.get("disabled_reason"):
        return prepare_kernel_reply(
            session,
            raw_text,
            mode=selected_mode,
            pending_actions=projected_pending,
        )

    if raw_text.strip() and public_action in _KERNEL_PUBLIC_ACTIONS:
        identity_revision = app_state.get("kernel_revision", session.revision)
        if isinstance(identity_revision, bool) or not isinstance(
            identity_revision, int
        ):
            identity_revision = session.revision
        replay_action_id = _kernel_action_id(
            session.session_id,
            identity_revision,
            public_action,
            {"input_mode": selected_mode.value, "source_text": raw_text},
        )
        if _kernel_action_already_recorded(session, replay_action_id):
            return {
                "action": contract_action,
                "input_mode": selected_mode.value,
                "source_text": raw_text,
                "diagnostic_updates": {},
                "parameter_candidates": [],
                "payload": {},
                "agent_records": [],
                "replayed": True,
            }
    if not raw_text.strip() and contract_action in {
        "confirm_task",
        "advance",
        "cancel",
        "replay",
        "prepare_operator_handoff",
        "prepare_training_exercise_bundle",
        "derive_features",
        "synthesize_controller",
        "qualify_controller",
        "run_provider",
        "run_evaluation",
        "run_feedback_iteration",
        "confirm_result",
        "submit_answer",
    }:
        prepared = prepare_kernel_reply(
            session,
            raw_text,
            mode=selected_mode,
            pending_actions=projected_pending,
        )
        prepared["agent_records"] = []
        return prepared

    cache_entry: _ReplyPreparation | None = None
    cache_key: str | None = None
    owner = True
    if raw_text.strip() and public_action in _KERNEL_PUBLIC_ACTIONS:
        identity_revision = app_state.get("kernel_revision", session.revision)
        if isinstance(identity_revision, bool) or not isinstance(
            identity_revision, int
        ):
            identity_revision = session.revision
        cache_key = _kernel_action_id(
            session.session_id,
            identity_revision,
            public_action,
            {"input_mode": selected_mode.value, "source_text": raw_text},
        )
        with _KERNEL_REPLY_PREPARATIONS_LOCK:
            cache_entry = _KERNEL_REPLY_PREPARATIONS.get(cache_key)
            owner = cache_entry is None
            if owner:
                cache_entry = _ReplyPreparation()
                _KERNEL_REPLY_PREPARATIONS[cache_key] = cache_entry
        if not owner:
            cache_entry.done.wait()
            if cache_entry.error is not None:
                raise cache_entry.error
            if cache_entry.result is None:
                raise RuntimeError("kernel_reply_preparation_missing_result")
            return deepcopy(cache_entry.result)

    try:
        prepared = _prepare_kernel_reply_for_ui_uncached(
            app_state,
            session,
            raw_text,
            selected_mode=selected_mode,
            projected_pending=projected_pending,
            base_url=base_url,
            model=model,
            api_key=api_key,
        )
    except Exception as exc:
        if cache_key is not None and cache_entry is not None:
            with _KERNEL_REPLY_PREPARATIONS_LOCK:
                cache_entry.error = exc
                cache_entry.done.set()
                _KERNEL_REPLY_PREPARATIONS.pop(cache_key, None)
        raise
    if cache_key is not None and cache_entry is not None:
        with _KERNEL_REPLY_PREPARATIONS_LOCK:
            cache_entry.result = deepcopy(prepared)
            cache_entry.done.set()
            _KERNEL_REPLY_PREPARATIONS.pop(cache_key, None)
    return prepared


def _prepare_kernel_reply_for_ui_uncached(
    app_state: Mapping[str, Any],
    session,
    text: str,
    *,
    selected_mode: KernelReplyMode,
    projected_pending: Any,
    base_url: str | None,
    model: str | None,
    api_key: str | None,
) -> dict[str, Any]:
    coordinator = None
    if selected_mode is KernelReplyMode.NATURAL_LANGUAGE:
        index_dir = app_state.get("rag_index_dir") or (session.agent_config or {}).get(
            "rag_index_dir"
        )
        use_rag = bool(
            app_state.get(
                "use_rag",
                (session.agent_config or {}).get("rag_requested", True),
            )
        )
        adapter = _build_app_adapter(
            base_url,
            model,
            api_key,
            rag_index_dir=index_dir,
            rag_snapshot=app_state.get("rag_snapshot") or session.rag_snapshot,
            use_rag=use_rag,
        )
        if str(getattr(adapter, "agent_mode", "")).strip().casefold() != "multi":
            raise ValueError("WebUI 需要支持 multi-agent 边界的 Provider adapter。")
        coordinator = KernelAgentCoordinator(
            adapter,
            retriever=getattr(adapter, "retriever", None),
            agent_mode="multi",
        )
    prepared = prepare_kernel_reply(
        session,
        text,
        mode=selected_mode,
        coordinator=coordinator,
        pending_actions=projected_pending,
    )
    prepared["agent_records"] = (
        list(coordinator.audit_log) if coordinator is not None else []
    )
    return prepared


__all__ = [
    "KERNEL_STAGE_LABELS",
    "build_adapter",
    "continue_kernel_app_run",
    "export_kernel_app_artifact",
    "export_kernel_app_bundle",
    "import_v3_app_run",
    "load_kernel_app_run",
    "parse_names",
    "prepare_kernel_reply_for_ui",
    "start_kernel_app_run",
    "start_kernel_case_run",
    "validate_kernel_artifact",
]
