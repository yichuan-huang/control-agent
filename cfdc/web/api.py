"""Local, same-origin API for the guided Kernel workspace."""

from __future__ import annotations

import hashlib
import json
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated
from urllib.parse import urlsplit

from fastapi import FastAPI, File, Form, Query, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from openai import OpenAI, OpenAIError
from starlette.concurrency import run_in_threadpool
from starlette.datastructures import MutableHeaders
from starlette.exceptions import HTTPException

from cfdc.doctor import run_doctor
from cfdc.kernel.cases import (
    case_learning_material,
    public_case_catalog,
    public_training_case,
)
from cfdc.kernel.contracts import TaskContract
from cfdc.web import readmodels, service
from cfdc.web.actions import check_mutation, execute_action, public_action_error
from cfdc.web.drafts import (
    DraftValidationError,
    case_draft,
    empty_draft,
    task_from_draft,
)
from cfdc.web.errors import APIError, ErrorResponse, PublicError
from cfdc.web.files import MAX_UPLOAD_BYTES, FileStore
from cfdc.web.operations import Operation, OperationList, OperationManager
from cfdc.web.presentation import task_summary
from cfdc.web.runtime import RAGRuntime
from cfdc.web.schemas import (
    ActionRequest,
    ArtifactValidationRequest,
    ArtifactValidationResponse,
    CaseCard,
    CaseDetail,
    CaseList,
    ConfigResponse,
    CreateRequest,
    DoctorCheck,
    DoctorRequest,
    DoctorResponse,
    DraftRequest,
    DraftResponse,
    DraftValidationResponse,
    ImportRequest,
    ProbeRequest,
    ProbeResponse,
    UploadResponse,
)

UPLOAD_ENVELOPE_BYTES = 64 * 1024


class _UploadBodyTooLarge(Exception):
    pass


class _UploadBodyLimitMiddleware:
    def __init__(self, app, *, max_bytes: int) -> None:
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] != "http" or scope.get("path") != "/api/v1/uploads":
            await self.app(scope, receive, send)
            return
        request = Request(scope)
        if not _is_local_request(request):
            await self.app(scope, receive, send)
            return

        declared_size = None
        for name, value in scope.get("headers", ()):
            if name.lower() == b"content-length":
                try:
                    declared_size = int(value)
                except ValueError:
                    pass
                break
        if declared_size is not None and declared_size > self.max_bytes:
            await self._reject(scope, receive, send)
            return

        received = 0
        exceeded = False
        pending_messages = []

        async def bounded_receive():
            nonlocal exceeded, received
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > self.max_bytes:
                    exceeded = True
                    raise _UploadBodyTooLarge
            return message

        async def pending_send(message):
            pending_messages.append(message)

        try:
            await self.app(scope, bounded_receive, pending_send)
        except _UploadBodyTooLarge:
            exceeded = True
        if exceeded:
            await self._reject(scope, receive, send)
            return
        for message in pending_messages:
            await send(message)

    @staticmethod
    async def _reject(scope, receive, send) -> None:
        response = JSONResponse(
            status_code=413,
            content={
                "error": PublicError(
                    code="file_too_large", message="文件超过 128 MiB 上传上限。"
                ).model_dump()
            },
        )
        await response(scope, receive, send)


def _is_local_request(request: Request) -> bool:
    origin = request.headers.get("origin")
    host = request.headers.get("host", "")
    local_host = urlsplit(str(request.url)).hostname in {
        "127.0.0.1",
        "localhost",
        "::1",
    }
    allowed = {f"{request.url.scheme}://{host}"}
    if local_host:
        allowed.update({"http://127.0.0.1:5173", "http://localhost:5173"})
    return bool(
        local_host
        and request.headers.get("sec-fetch-site") != "cross-site"
        and (not origin or origin in allowed)
    )


class _LocalOriginMiddleware:
    def __init__(self, app) -> None:
        self.app = app

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] != "http" or not scope.get("path", "").startswith("/api/"):
            await self.app(scope, receive, send)
            return
        if not _is_local_request(Request(scope)):
            response = JSONResponse(
                status_code=403,
                content={
                    "error": PublicError(
                        code="origin_rejected", message="请求来源与本地应用不一致。"
                    ).model_dump()
                },
            )
            await response(scope, receive, send)
            return

        async def send_with_security_headers(message):
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers["Cache-Control"] = "no-store"
                headers["X-Content-Type-Options"] = "nosniff"
            await send(message)

        await self.app(scope, receive, send_with_security_headers)


def _request_signature(kind: str, model, task_id: str = "") -> str:
    value = model.model_dump(mode="json", exclude={"credentials", "request_id"})
    encoded = json.dumps(
        [kind, task_id, value], sort_keys=True, ensure_ascii=False, allow_nan=False
    )
    return hashlib.sha256(encoded.encode()).hexdigest()


def _case_card(case_id: str) -> CaseCard:
    try:
        value = public_training_case(case_id)
    except ValueError:
        raise APIError("case_not_found", "未找到此内置案例。", 404) from None
    learning = case_learning_material(case_id)
    return CaseCard(
        id=case_id,
        title=value["label_cn"],
        category="audit" if value.get("case_kind") == "audit" else "engineering",
        description=str(learning["learning_goal"]),
        data_source=str(learning["evidence_boundary"]),
        scope="用于公开软件案例验证；不代表真实设备测量或硬件安全认证。",
    )


def _display_task(task: dict) -> dict:
    return TaskContract.from_user_input(task).to_dict(include_fingerprint=False)


def create_app(
    *,
    session_dir: str | Path | None = None,
    runtime_dir: str | Path | None = None,
    frontend_dir: str | Path | None = None,
    prepare_rag: bool = True,
) -> FastAPI:
    session_root = Path(
        session_dir or os.getenv("CFDC_KERNEL_SESSION_DIR") or "output/kernel-sessions"
    ).resolve()
    runtime_root = Path(runtime_dir or "output/web").resolve()
    static_root = Path(
        frontend_dir or Path(__file__).resolve().parent / "frontend/dist"
    ).resolve()
    cache = readmodels.ReportCache(session_root)
    files = FileStore(runtime_root / "uploads")
    rag = RAGRuntime(
        Path(os.getenv("CFDC_RAG_INDEX_DIR") or "output/rag-index").resolve()
    )
    operations = OperationManager(runtime_root / "operations")

    @asynccontextmanager
    async def lifespan(app):
        if prepare_rag:
            rag.start()
        yield
        operations.close()

    app = FastAPI(
        title="CFDC Kernel Web API",
        version="0.3.4",
        lifespan=lifespan,
        responses={
            400: {"model": ErrorResponse},
            409: {"model": ErrorResponse},
            422: {"model": ErrorResponse},
        },
    )
    app.state.cache, app.state.files, app.state.rag, app.state.operations = (
        cache,
        files,
        rag,
        operations,
    )
    app.add_middleware(
        _UploadBodyLimitMiddleware,
        max_bytes=MAX_UPLOAD_BYTES + UPLOAD_ENVELOPE_BYTES,
    )
    app.add_middleware(_LocalOriginMiddleware)

    @app.exception_handler(APIError)
    async def api_error(request, exc: APIError):
        return JSONResponse(
            status_code=exc.status_code, content={"error": exc.public.model_dump()}
        )

    @app.exception_handler(DraftValidationError)
    async def draft_error(request, exc: DraftValidationError):
        error = PublicError(
            code="draft_invalid", message="请完成标出的项目后继续。", fields=exc.errors
        )
        return JSONResponse(status_code=422, content={"error": error.model_dump()})

    @app.exception_handler(RequestValidationError)
    async def request_error(request, exc: RequestValidationError):
        fields = {
            ".".join(
                str(part) for part in item["loc"] if part not in {"body", "query"}
            ): "此项缺失或格式不正确。"
            for item in exc.errors()
        }
        return JSONResponse(
            status_code=422,
            content={
                "error": PublicError(
                    code="invalid_request", message="请检查标出的输入。", fields=fields
                ).model_dump()
            },
        )

    @app.exception_handler(HTTPException)
    async def http_error(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": PublicError(
                    code="not_found" if exc.status_code == 404 else "http_error",
                    message="未找到此资源。"
                    if exc.status_code == 404
                    else "请求未完成。",
                ).model_dump()
            },
        )

    @app.exception_handler(Exception)
    async def unexpected_error(request, exc):
        return JSONResponse(
            status_code=500,
            content={
                "error": PublicError(
                    code="internal_error",
                    message="服务暂时无法完成请求，请刷新后检查任务状态。",
                ).model_dump()
            },
        )

    def load(task_id: str):
        try:
            return cache.get(task_id)
        except APIError:
            raise
        except (OSError, ValueError, TypeError, KeyError):
            raise APIError(
                "task_unavailable",
                "未找到有效任务，请检查任务编号和本地会话文件。",
                404,
            ) from None

    def fresh_error(exc: Exception, task_id: str | None) -> APIError:
        state = {}
        if task_id:
            cache.invalidate(task_id)
            try:
                _, state = load(task_id)
            except APIError:
                state = {
                    "kernel_session_id": task_id,
                    "kernel_session_dir": str(session_root),
                }
        return public_action_error(exc, state)

    @app.get("/api/v1/config", response_model=ConfigResponse)
    def configuration():
        return ConfigResponse(
            base_url=os.getenv("CFDC_LLM_BASE_URL", ""),
            model=os.getenv("CFDC_LLM_MODEL", ""),
            rag=rag.status(),
        )

    @app.post("/api/v1/config/probe", response_model=ProbeResponse)
    def probe(body: ProbeRequest):
        credentials = body.credentials
        if not all(
            (
                credentials.base_url.strip(),
                credentials.model.strip(),
                credentials.api_key.strip(),
            )
        ):
            return ProbeResponse(
                connected=False, message="请填写模型地址、名称和密钥。"
            )
        try:
            with OpenAI(
                base_url=credentials.base_url,
                api_key=credentials.api_key,
                timeout=15,
                max_retries=0,
            ) as client:
                available = {item.id for item in client.models.list()}
            if credentials.model not in available:
                return ProbeResponse(
                    connected=False,
                    message="服务可连接，但未找到所选模型，请核对模型名称。",
                )
        except (OpenAIError, OSError, ValueError):
            return ProbeResponse(
                connected=False,
                message="连接探测失败，请检查服务地址、密钥及服务是否启动。",
            )
        return ProbeResponse(connected=True, message="已连接服务并找到所选模型。")

    @app.post("/api/v1/config/doctor", response_model=DoctorResponse)
    def doctor(body: DoctorRequest):
        report = run_doctor(
            session_dir=session_root,
            rag_index_dir=rag.index_dir if body.use_rag else None,
            ollama_base_url=body.credentials.base_url,
            ollama_model=body.credentials.model,
            api_key=body.credentials.api_key,
        )
        return DoctorResponse(
            checks=[
                DoctorCheck(
                    name=item.check_id,
                    status=item.status.value,
                    message=item.message_cn,
                )
                for item in report.checks
            ]
        )

    @app.get("/api/v1/cases", response_model=CaseList)
    def cases():
        items = [_case_card(case_id) for case_id in public_case_catalog()]
        return CaseList(items=items)

    @app.get("/api/v1/cases/{case_id}", response_model=CaseDetail)
    def case(case_id: str):
        card = _case_card(case_id)
        return CaseDetail(
            **card.model_dump(),
            draft=case_draft(case_id),
            task=_display_task(public_training_case(case_id)["task"]),
            learning=case_learning_material(case_id),
        )

    @app.get("/api/v1/drafts/default", response_model=DraftResponse)
    def default_draft():
        return DraftResponse(draft=empty_draft())

    @app.post("/api/v1/drafts/validate", response_model=DraftValidationResponse)
    def validate_draft(body: DraftRequest):
        task = _display_task(task_from_draft(body.draft, case_id=body.case_id))
        return DraftValidationResponse(task=task, summary=task_summary(task))

    @app.post("/api/v1/tasks", response_model=Operation, status_code=202)
    def create_task(body: CreateRequest):
        signature = _request_signature("create", body)
        existing = operations.find(str(body.request_id), signature)
        if existing:
            return existing
        if body.draft is not None and not body.confirmed:
            raise APIError(
                "confirmation_required",
                "请核对并确认软件试验边界和预算。",
                422,
                fields={"confirmed": "开始前需要确认。"},
            )
        task = (
            task_from_draft(body.draft, case_id=body.case_id)
            if body.draft is not None
            else body.task
        )
        options = rag.options(body.use_rag)

        def work(context):
            task_id = None
            try:
                report, state = service.start_kernel_app_run(
                    task,
                    session_dir=session_root,
                    provider_case_id=body.case_id or None,
                    evidence_mode=body.evidence_mode if body.case_id else "automatic",
                    llm_configured=bool(
                        body.credentials.model.strip()
                        and body.credentials.api_key.strip()
                    ),
                    **options,
                )
                task_id = state["kernel_session_id"]
                context.created_task(task_id)
                if body.confirmed:
                    report, state = service.continue_kernel_app_run(
                        state, action="confirm_task", payload={}
                    )
                cache.invalidate(task_id)
                return {"session_id": task_id, "revision": report["revision"]}
            except Exception as exc:
                raise fresh_error(exc, task_id) from exc

        return operations.submit(str(body.request_id), None, signature, work)

    @app.post("/api/v1/imports", response_model=Operation, status_code=202)
    def import_history(body: ImportRequest):
        signature = _request_signature("import", body)
        existing = operations.find(str(body.request_id), signature)
        if existing:
            return existing
        path = files.resolve(str(body.file_id), session_id=None)
        if path.suffix != ".zip":
            raise APIError("import_zip_required", "历史记录导入需要 ZIP 文件。", 422)

        def work(context):
            try:
                report, state = service.import_v3_app_run(
                    path, session_dir=session_root
                )
                context.created_task(state["kernel_session_id"])
                return {
                    "session_id": state["kernel_session_id"],
                    "revision": report["revision"],
                }
            except Exception as exc:
                raise fresh_error(exc, None) from exc

        return operations.submit(str(body.request_id), None, signature, work)

    @app.get("/api/v1/tasks/{task_id}", response_model=readmodels.TaskSummary)
    def task(task_id: str):
        report, _ = load(task_id)
        return readmodels.summary(report)

    @app.post(
        "/api/v1/tasks/{task_id}/actions", response_model=Operation, status_code=202
    )
    def action(task_id: str, body: ActionRequest):
        signature = _request_signature("action", body, task_id)
        existing = operations.find(str(body.request_id), signature)
        if existing:
            return existing
        report, _ = load(task_id)
        check_mutation(report, body.expected_revision, body.action)

        def work(context):
            try:
                cache.invalidate(task_id)
                current, state = load(task_id)
                check_mutation(current, body.expected_revision, body.action)
                report, _ = execute_action(state, body, files)
                cache.invalidate(task_id)
                return {"session_id": task_id, "revision": report["revision"]}
            except Exception as exc:
                raise fresh_error(exc, task_id) from exc

        return operations.submit(str(body.request_id), task_id, signature, work)

    @app.get("/api/v1/operations/{operation_id}", response_model=Operation)
    def operation(operation_id: str):
        return operations.get(operation_id)

    @app.get("/api/v1/tasks/{task_id}/operations", response_model=OperationList)
    def task_operations(task_id: str):
        return OperationList(items=operations.for_task(task_id))

    @app.post("/api/v1/uploads", response_model=UploadResponse)
    async def upload(
        file: Annotated[UploadFile, File()],
        session_id: Annotated[str | None, Form()] = None,
    ):
        if session_id:
            report, _ = await run_in_threadpool(load, session_id)
            check_mutation(report, report["revision"], "cancel")
        return await files.save(file, session_id=session_id)

    @app.post("/api/v1/artifacts/validate", response_model=ArtifactValidationResponse)
    def validate_artifact(body: ArtifactValidationRequest):
        try:
            return ArtifactValidationResponse(
                artifact=service.validate_kernel_artifact(body.payload)
            )
        except Exception as exc:
            raise public_action_error(exc, {}) from exc

    @app.get(
        "/api/v1/tasks/{task_id}/artifacts", response_model=readmodels.ArtifactCatalog
    )
    def artifacts(task_id: str):
        return readmodels.artifact_catalog(load(task_id)[0])

    @app.get(
        "/api/v1/tasks/{task_id}/artifacts/{artifact_id}/node",
        response_model=readmodels.NodePage,
    )
    def node(
        task_id: str,
        artifact_id: str,
        pointer: str = Query(default="", max_length=8192),
        offset: int = Query(default=0, ge=0),
        limit: int = Query(default=50, ge=1, le=100),
    ):
        try:
            return readmodels.node_page(
                load(task_id)[0],
                artifact_id,
                pointer=pointer,
                offset=offset,
                limit=limit,
            )
        except (ValueError, KeyError, IndexError):
            raise APIError(
                "node_unavailable", "此节点不可用，请刷新产物目录。", 404
            ) from None

    @app.get(
        "/api/v1/tasks/{task_id}/sections/{section}",
        response_model=readmodels.SectionPage,
    )
    def section_page(
        task_id: str,
        section: str,
        offset: int = Query(default=0, ge=0),
        limit: int = Query(default=50, ge=1, le=100),
    ):
        try:
            return readmodels.section_page(
                load(task_id)[0], section, offset=offset, limit=limit
            )
        except (ValueError, KeyError, TypeError):
            raise APIError("section_unavailable", "此专业记录暂不可用。", 404) from None

    @app.get("/api/v1/tasks/{task_id}/protocol", response_model=readmodels.ProtocolView)
    def protocol(task_id: str):
        return readmodels.protocol_view(load(task_id)[0])

    @app.get(
        "/api/v1/tasks/{task_id}/evaluations", response_model=readmodels.EvaluationsView
    )
    def evaluations(task_id: str, selection: str | None = None):
        try:
            return readmodels.evaluations_view(load(task_id)[0], selection=selection)
        except (ValueError, KeyError, IndexError):
            raise APIError(
                "evaluation_unavailable", "未找到所选评价，请刷新结果。", 404
            ) from None

    @app.get("/api/v1/tasks/{task_id}/curves", response_model=readmodels.CurveView)
    def curves(
        task_id: str,
        selection: str,
        signal: str,
        start: float | None = Query(default=None, allow_inf_nan=False),
        end: float | None = Query(default=None, allow_inf_nan=False),
        control: str | None = None,
    ):
        try:
            return readmodels.curve_view(
                load(task_id)[0],
                selection,
                signal,
                start=start,
                end=end,
                control=control,
            )
        except (ValueError, KeyError, IndexError):
            raise APIError(
                "curve_unavailable", "所选试次、信号或时间范围没有可用曲线。", 422
            ) from None

    @app.get(
        "/api/v1/tasks/{task_id}/evidence/curves",
        response_model=readmodels.EvidenceCurveView,
    )
    def evidence_curves(
        task_id: str,
        selection: str,
        signal: str,
        start: float | None = Query(default=None, allow_inf_nan=False),
        end: float | None = Query(default=None, allow_inf_nan=False),
    ):
        try:
            return readmodels.evidence_curve_view(
                load(task_id)[0], selection, signal, start=start, end=end
            )
        except (ValueError, KeyError, IndexError):
            raise APIError(
                "evidence_curve_unavailable",
                "当前协议没有此试次、信号或时间范围的已通过数据。",
                422,
            ) from None

    @app.get("/api/v1/tasks/{task_id}/downloads/{kind}")
    def download(task_id: str, kind: str, artifact_id: str | None = None):
        report, state = load(task_id)
        try:
            if kind in {"artifact", "report"}:
                selected = "report" if kind == "report" else artifact_id
                available = {
                    item.id for item in readmodels.artifact_catalog(report).items
                }
                if selected not in available:
                    raise ValueError("artifact unavailable")
                value = report if selected == "report" else report[selected]
                directory = (
                    runtime_root / "downloads" / task_id / str(report["revision"])
                )
                directory.mkdir(parents=True, exist_ok=True)
                path = directory / f"{selected}.json"
                path.write_text(
                    json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)
                    + "\n",
                    encoding="utf-8",
                )
            elif kind == "bundle":
                path = Path(service.export_kernel_app_bundle(state)).resolve()
                if path != session_root / f"{task_id}.result.zip":
                    raise ValueError("invalid bundle location")
            else:
                mapping = {
                    "exercise": "training_exercise_bundle",
                    "operator": "operator_bundle",
                    "controller": "controller_ir",
                    "protocol": "protocol",
                    "features": "features",
                    "qualification": "qualification",
                    "freeze": "freeze",
                    "evaluation": "evaluation",
                    "confirmation": "confirmation",
                    "feedback": "feedback",
                    "result": "result",
                    "audit": "audit",
                    "upload_receipt": "upload_receipt",
                }
                if kind not in mapping:
                    raise ValueError("unknown download")
                path = Path(
                    service.export_kernel_app_artifact(state, mapping[kind])
                ).resolve()
                expected_root = (
                    session_root / f"{task_id}.artifacts"
                    if kind in {"exercise", "operator"}
                    else session_root / f"{task_id}.downloads"
                )
                if not path.is_relative_to(expected_root):
                    raise ValueError("download belongs to another task")
            return FileResponse(
                path,
                filename=path.name,
                media_type="application/zip"
                if path.suffix == ".zip"
                else "application/json",
            )
        except (OSError, ValueError, KeyError):
            raise APIError(
                "download_unavailable", "当前任务尚无此文件，或文件已不可用。", 404
            ) from None

    @app.get("/{path:path}", include_in_schema=False)
    def frontend(path: str):
        if path == "api" or path.startswith("api/"):
            raise APIError("not_found", "未找到此接口。", 404)
        candidate = (static_root / path).resolve()
        if candidate.is_relative_to(static_root) and candidate.is_file():
            return FileResponse(candidate)
        index = static_root / "index.html"
        if not index.is_file():
            return HTMLResponse(
                "<html lang='zh'><meta charset='utf-8'><title>CFDC</title><h1>前端尚未构建</h1><p>请进入 cfdc/web/frontend 执行 npm ci 和 npm run build，然后刷新页面。</p></html>",
                status_code=503,
            )
        return FileResponse(index)

    return app
