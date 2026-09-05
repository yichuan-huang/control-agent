"""HTTP action adaptation without any UI framework or client filesystem paths."""

from __future__ import annotations

from typing import Any

from openai import OpenAIError

from cfdc.kernel.replies import _NO_INPUT_ACTIONS
from cfdc.web import service
from cfdc.web.errors import APIError
from cfdc.web.files import FileStore
from cfdc.web.schemas import ActionRequest


def check_mutation(report: dict, revision: int, action: str) -> str:
    details = {
        "latest_revision": report["revision"],
        "session_id": report["session_id"],
    }
    if report["revision"] != revision:
        raise APIError(
            "stale_revision",
            "任务状态已更新，请核对最新状态后重新操作。",
            409,
            **details,
        )
    if report.get("read_only"):
        raise APIError("task_read_only", "这是只读任务，不能提交修改。", 409, **details)
    if report.get("status") in {"performance_met", "capability_gap", "cancelled"}:
        raise APIError(
            "task_terminal", "此任务已结束；可查看结果或创建新任务。", 409, **details
        )
    normalized = service._normalise_kernel_action(action)
    current = service._normalise_kernel_action(
        str(report.get("input_contract", {}).get("action") or "")
    )
    if normalized not in {current, "cancel"} and not (
        normalized == "revise_diagnostic" and current == "answer"
    ):
        raise APIError(
            "action_conflict",
            "当前步骤不接受此操作，请刷新任务后重试。",
            409,
            **details,
        )
    return normalized


def public_action_error(exc: Exception, state: dict[str, Any]) -> APIError:
    if isinstance(exc, APIError):
        return exc
    error = service.kernel_action_error_payload(exc, state)
    code = str(error.get("code") or "action_failed")
    message = str(error.get("message_cn") or "操作未完成，请检查当前任务状态。")
    if isinstance(exc, OpenAIError):
        code = "model_request_failed"
        message = (
            "模型请求失败。请检查设置中的连接与模型名称；输入已保留，可由你重新提交。"
        )
    elif str(exc) in {
        "Diagnosis 提取的 evidence 不在用户原文中。",
        "Critic 修正后的 Diagnosis evidence 不在用户原文中。",
    }:
        code = "model_evidence_unverified"
        message = "模型提取的证据无法与原始输入对应，本次未写入事实。请改写观察到的现象，不知道的内容可继续写“不知道”。"
    elif str(exc).startswith("unable to load RAG index"):
        code = "rag_index_unavailable"
        message = "此任务固定的知识库暂时无法加载。请运行环境自检并修复知识库后重试。"
    elif not hasattr(exc, "to_dict") and code not in {
        "stale_revision",
        "confirmation_failed",
        "upload_files_required",
        "registered_case_task_contract_mismatch",
        "model_evidence_unverified",
    }:
        # An arbitrary provider exception may itself contain a credential.
        code = "action_failed"
    return APIError(
        code,
        message,
        409 if code == "stale_revision" else 422,
        latest_revision=error.get("revision"),
        session_id=state.get("kernel_session_id"),
        receipt_saved=bool(error.get("receipt_saved")),
    )


def execute_action(
    state: dict, request: ActionRequest, files: FileStore
) -> tuple[dict, dict]:
    action = service._normalise_kernel_action(request.action)
    data = request.input
    if action == "confirm_task":
        if data.confirmed is not True:
            raise APIError(
                "confirmation_required",
                "请先核对并确认软件试验边界。",
                422,
                fields={"confirmed": "需要确认软件试验边界。"},
            )
        if data.payload:
            raise APIError(
                "boundary_immutable", "已创建任务的边界修改需要创建新任务。", 422
            )
        payload = {}
    elif action == "ingest_upload":
        if not data.file_ids:
            raise APIError("upload_files_required", "请选择当前协议要求的文件。", 422)
        payload = {
            "paths": [
                str(files.resolve(str(item), session_id=state["kernel_session_id"]))
                for item in data.file_ids
            ],
            "stopped_on_limit": data.stopped_on_limit,
        }
    elif data.payload is not None:
        payload = data.payload
    elif action in _NO_INPUT_ACTIONS:
        payload = {}
    else:
        credentials = request.credentials
        if data.mode == "natural_language" and not (
            credentials.base_url.strip()
            and credentials.model.strip()
            and credentials.api_key.strip()
        ):
            raise APIError(
                "model_not_configured",
                "此步骤需要模型，请先在设置中填写地址、模型名称和密钥。",
                422,
            )
        prepared = service.prepare_kernel_reply_for_ui(
            state,
            data.text,
            mode=data.mode,
            base_url=credentials.base_url,
            model=credentials.model,
            api_key=credentials.api_key,
        )
        prepared_action = service._normalise_kernel_action(
            str(prepared.get("action") or "")
        )
        if prepared_action != action:
            raise APIError("action_conflict", "任务步骤已变化，请刷新后重新操作。", 409)
        return service.continue_kernel_app_run(
            state,
            action=prepared_action,
            payload=dict(prepared.get("payload") or {}),
            request_identity={
                "input_mode": prepared.get("input_mode"),
                "source_text": prepared.get("source_text", ""),
            }
            if prepared.get("input_mode")
            else None,
            reply_source_text=prepared.get("source_text") or None,
            reply_input_mode=prepared.get("input_mode"),
            agent_records=prepared.get("agent_records", ()),
        )
    if action != "ingest_upload" and any(
        key in payload
        for key in ("paths", "files", "session_dir", "kernel_session_dir")
    ):
        raise APIError("client_path_forbidden", "请通过文件上传控件提交文件。", 422)
    return service.continue_kernel_app_run(state, action=action, payload=payload)
