"""RAG preparation is visible independently from the HTTP application's startup."""

from __future__ import annotations

from pathlib import Path
from threading import Lock, Thread

from cfdc.web.errors import APIError
from cfdc.web.rag_startup import (
    BuiltinRAGStartupError,
    PreparedRAGIndex,
    prepare_builtin_rag_index,
)
from cfdc.web.schemas import RAGStatus


class RAGRuntime:
    def __init__(self, index_dir: Path) -> None:
        self.index_dir = index_dir
        self.prepared: PreparedRAGIndex | None = None
        self._lock = Lock()
        self._thread: Thread | None = None
        self._status = RAGStatus(status="error", message="内置知识库尚未准备。")

    def start(self) -> None:
        with self._lock:
            if self._thread is not None:
                return
            self._status = RAGStatus(
                status="preparing",
                message="正在准备内置知识库，可先填写草稿或查看任务。",
            )
            self._thread = Thread(target=self._prepare, name="cfdc-rag", daemon=True)
            self._thread.start()

    def _prepare(self) -> None:
        try:
            prepared = prepare_builtin_rag_index(self.index_dir)
        except BuiltinRAGStartupError as exc:
            status = RAGStatus(
                status="error",
                message=exc.public_message,
            )
            with self._lock:
                self._status = status
        else:
            with self._lock:
                self.prepared = prepared
                self._status = RAGStatus(
                    status="ready",
                    message="内置知识库已就绪。",
                    snapshot=prepared.snapshot,
                )

    def status(self) -> RAGStatus:
        with self._lock:
            return self._status.model_copy(deep=True)

    def options(self, use_rag: bool) -> dict:
        with self._lock:
            if not use_rag:
                return {"use_rag": False}
            if self._status.status != "ready" or self.prepared is None:
                raise APIError("rag_not_ready", self._status.message, 409)
            return {
                "use_rag": True,
                "rag_index_dir": str(self.prepared.index_dir),
                "rag_snapshot": self.prepared.snapshot,
            }
