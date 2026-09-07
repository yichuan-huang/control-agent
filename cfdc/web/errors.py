"""Small, explicitly public HTTP errors; exception internals stay server-side."""

from __future__ import annotations

from pydantic import BaseModel, Field


class PublicError(BaseModel):
    code: str
    message: str
    fields: dict[str, str] = Field(default_factory=dict)
    latest_revision: int | None = None
    session_id: str | None = None
    receipt_saved: bool = False


class ErrorResponse(BaseModel):
    error: PublicError


class APIError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        **details,
    ) -> None:
        super().__init__(code)
        self.status_code = status_code
        self.public = PublicError(code=code, message=message, **details)


EXTERNAL_ERROR_MESSAGES = {
    "protocol_segment_outside_task_envelope": "当前采集协议的输入序列超出已确认边界，未开始实验。请查看协议要求与真实输入范围；如任务填写有误，请新建任务纠正，若边界确实不能满足则当前协议不适用，不要反复重试或放宽真实边界。",
    "protocol_excitation_budget_exceeded": "采集协议所需时长超过已确认的激励预算，未开始实验。请核对协议和预算；如需改变预算，应重新建立并确认任务。",
    "protocol_sample_count_out_of_bounds": "协议采样点数超出支持范围，未开始实验。请核对任务的采样周期与时长，重新建立任务或选择适用的采集方案。",
    "protocol_control_input_binding_mismatch": "协议控制通道与任务输入不匹配，未开始实验。请核对任务定义及采集协议。",
    "protocol_signal_not_declared_by_task": "协议要求的测量信号未在任务中声明，未开始实验。请核对测量通道后重新建立任务。",
    "automatic_execution_removed": "自动仿真入口已移除；请按页面指导下载、在外部执行并上传记录。",
    "external_reacquisition_required": "此任务保留了旧的自动实验记录，请派生新任务重新确认并采集。",
    "system_prechecks_server_only": "人工检查不能冒充系统检查，请按实际完成情况提交检查表。",
    "external_source_required": "请先选择外部数据来源。",
    "external_source_kind_invalid": "请选择软件仿真或外部测量数据。",
    "external_source_already_in_use": "数据来源已锁定；如需更改，请重新采集证据。",
    "external_request_already_pending": "请先提交当前请求的结果。",
    "external_request_required": "请先生成当前阶段的执行包。",
    "external_results_zip_required": "请上传一个结果 ZIP 文件。",
    "external_results_archive_invalid": "结果包格式无效，请核对下载包中的说明。",
    "external_results_binding_mismatch": "结果包与当前任务、请求或冻结版本不一致。",
    "external_results_files_mismatch": "结果包缺少必需试次或包含额外文件。",
    "external_trial_binding_mismatch": "试次与当前执行请求不一致。",
    "external_active_freeze_mismatch": "结果不属于当前冻结方案。",
    "external_tuning_required": "请先开始有界调优。",
    "external_tuning_no_pending_candidates": "当前没有待执行的调优候选。",
    "external_tuning_already_started": "本轮有界调优已经开始。",
    "external_development_already_consumed": "开发评价已经完成，请继续当前阶段。",
    "controller_freeze_required": "请先冻结控制器方案。",
    "tuning_requires_verified_evaluation_replay": "请先复核开发评价。",
    "tuning_budget_not_confirmed": "请先确认调优预算。",
    "compiled_protocol_required": "请先选择来源并生成实验协议。",
    "fresh_confirmation_requires_accepted_tuning": "独立确认需要已接受的调优候选。",
}

IMPORT_ERROR_MESSAGES = {
    "result_import_manifest_fingerprint_mismatch": "导入包清单校验失败，请重新导出后再导入。",
    "result_import_artifact_fingerprint_mismatch": "导入包中的任务或诊断文档已改变，请重新导出后再导入。",
    "result_import_duplicate_member": "导入包包含重复文件，无法确定唯一记录。",
    "result_import_required_document_missing": "导入包缺少任务、诊断或审计文档。",
    "result_import_artifact_manifest_required": "导入包缺少有效的产物清单。",
    "result_import_task_documents_invalid": "导入包中的任务或诊断文档格式无效。",
    "v3_import_file_too_large": "需要解析的导入文档超过 32 MiB 限制。",
    "v3_import_bundle_limit_exceeded": "导入包超过文件数量或 256 MiB 解压总量限制。",
    "session_event_chain_invalid": "导入记录的审计事件顺序不完整，请重新导出。",
    "session_event_fingerprint_mismatch": "导入记录的审计事件校验失败，请重新导出。",
    "session_event_revision_invalid": "导入记录的审计版本不连续，请重新导出。",
}
