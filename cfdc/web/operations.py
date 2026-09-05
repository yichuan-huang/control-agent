"""Single-worker operations, with durable metadata and no persisted inputs.

This is a transport queue. The Kernel remains the sole authority for task state.
Only IDs, a non-credential request digest, timestamps and public outcomes persist.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ValidationError

from cfdc.web.errors import APIError, PublicError

OperationStatus = Literal["queued", "running", "completed", "failed", "interrupted"]
_ACTIVE = {"queued", "running"}


def _now() -> str:
    return datetime.now(UTC).isoformat()


class OperationResult(BaseModel):
    session_id: str | None = None
    revision: int | None = None


class Operation(BaseModel):
    operation_id: str
    request_id: str
    session_id: str | None = None
    status: OperationStatus
    created_at: str
    updated_at: str
    result: OperationResult | None = None
    error: PublicError | None = None


class OperationList(BaseModel):
    items: list[Operation]


class OperationContext:
    def __init__(self, manager: OperationManager, operation_id: str) -> None:
        self._manager = manager
        self._operation_id = operation_id

    def created_task(self, session_id: str) -> None:
        """Persist a recoverable task ID before attempting boundary confirmation."""
        self._manager._created_task(self._operation_id, session_id)


class OperationManager:
    def __init__(self, root: Path, *, max_pending: int = 64) -> None:
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()
        self._operations: dict[str, Operation] = {}
        self._requests: dict[str, str] = {}
        self._signatures: dict[str, str] = {}
        self._max_pending = max_pending
        self._closed = False
        self._restore()
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="cfdc-op")

    def _restore(self) -> None:
        for path in self.root.glob("*.json"):
            try:
                record = json.loads(path.read_text(encoding="utf-8"))
                operation = Operation.model_validate(record["operation"])
                if str(UUID(operation.operation_id)) != path.stem:
                    continue
                signature = str(record["signature"])
            except (OSError, KeyError, ValueError, TypeError, ValidationError):
                continue
            self._operations[operation.operation_id] = operation
            self._requests[operation.request_id] = operation.operation_id
            self._signatures[operation.operation_id] = signature
            if operation.status in _ACTIVE:
                operation.status = "interrupted"
                operation.updated_at = _now()
                operation.error = PublicError(
                    code="operation_interrupted",
                    message="服务重启中断了此次操作。请刷新任务，核对已记录内容后重新操作。",
                    session_id=operation.session_id,
                )
                self._save(operation)

    def _save(self, operation: Operation) -> None:
        path = self.root / f"{operation.operation_id}.json"
        temporary = path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(
                {
                    "operation": operation.model_dump(mode="json"),
                    "signature": self._signatures[operation.operation_id],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        temporary.replace(path)

    def find(self, request_id: str, signature: str) -> Operation | None:
        with self._lock:
            operation_id = self._requests.get(request_id)
            if operation_id is None:
                return None
            if self._signatures[operation_id] != signature:
                raise APIError(
                    "request_id_conflict", "请求标识已用于其他输入，请重新操作。", 409
                )
            return self._operations[operation_id].model_copy(deep=True)

    def get(self, operation_id: str) -> Operation:
        with self._lock:
            operation = self._operations.get(operation_id)
            if operation is None:
                raise APIError("operation_not_found", "未找到此次操作。", 404)
            return operation.model_copy(deep=True)

    def for_task(self, session_id: str) -> list[Operation]:
        with self._lock:
            matching = sorted(
                (
                    item
                    for item in self._operations.values()
                    if item.session_id == session_id
                ),
                key=lambda item: item.created_at,
                reverse=True,
            )
            return [item.model_copy(deep=True) for item in matching[:20]]

    def submit(
        self,
        request_id: str,
        session_id: str | None,
        signature: str,
        work: Callable[[OperationContext], dict],
    ) -> Operation:
        with self._lock:
            existing = self.find(request_id, signature)
            if existing is not None:
                return existing
            if self._closed:
                raise APIError(
                    "service_stopping", "服务正在停止，请稍后重新打开。", 503
                )
            active = [
                item for item in self._operations.values() if item.status in _ACTIVE
            ]
            if session_id and any(item.session_id == session_id for item in active):
                raise APIError("task_busy", "此任务已有操作正在执行，请等待完成。", 409)
            if len(active) >= self._max_pending:
                raise APIError("queue_full", "等待操作较多，请稍后重试。", 429)
            operation = Operation(
                operation_id=str(uuid4()),
                request_id=request_id,
                session_id=session_id,
                status="queued",
                created_at=_now(),
                updated_at=_now(),
            )
            self._operations[operation.operation_id] = operation
            self._requests[request_id] = operation.operation_id
            self._signatures[operation.operation_id] = signature
            try:
                self._save(operation)
            except OSError:
                del self._operations[operation.operation_id]
                del self._requests[request_id]
                del self._signatures[operation.operation_id]
                raise APIError(
                    "operation_storage_unavailable", "操作记录暂时无法保存。", 503
                ) from None
            self._executor.submit(self._run, operation.operation_id, work)
            return operation.model_copy(deep=True)

    def _created_task(self, operation_id: str, session_id: str) -> None:
        with self._lock:
            operation = self._operations[operation_id]
            operation.session_id = session_id
            operation.updated_at = _now()
            self._save(operation)

    def _run(self, operation_id: str, work: Callable[[OperationContext], dict]) -> None:
        with self._lock:
            operation = self._operations[operation_id]
        try:
            with self._lock:
                operation.status = "running"
                operation.updated_at = _now()
                self._save(operation)
            result = OperationResult.model_validate(
                work(OperationContext(self, operation_id))
            )
        except Exception as exc:  # noqa: BLE001 -- worker must publish failures without logging secret-bearing exceptions.
            error = (
                exc.public
                if isinstance(exc, APIError)
                else PublicError(
                    code="operation_failed",
                    message="此次操作未完成。请刷新任务，核对状态后重新操作；输入仍保留在页面中。",
                )
            )
            with self._lock:
                operation.status = "failed"
                operation.error = error.model_copy(deep=True)
                if operation.error.session_id is None:
                    operation.error.session_id = operation.session_id
        else:
            with self._lock:
                operation.status = "completed"
                operation.result = result
                operation.session_id = result.session_id or operation.session_id
        finally:
            with self._lock:
                operation.updated_at = _now()
                try:
                    self._save(operation)
                except OSError:
                    operation.status = "failed"
                    operation.error = PublicError(
                        code="operation_storage_unavailable",
                        message="操作记录无法保存。请核对任务中已记录的状态后再操作。",
                        session_id=operation.session_id,
                        latest_revision=operation.result.revision
                        if operation.result
                        else None,
                    )

    def close(self) -> None:
        with self._lock:
            self._closed = True
        self._executor.shutdown(wait=True)
