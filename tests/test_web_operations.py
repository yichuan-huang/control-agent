from __future__ import annotations

import json
from threading import Event

import pytest

from cfdc.web.errors import APIError
from cfdc.web.operations import OperationManager


def test_duplicate_requests_reuse_operation_and_busy_task_is_rejected(tmp_path):
    entered, release = Event(), Event()
    calls = []
    manager = OperationManager(tmp_path)

    def work(context):
        calls.append("run")
        entered.set()
        assert release.wait(5)
        return {"session_id": "task-a", "revision": 3}

    try:
        operation = manager.submit("request-a", "task-a", "signature", work)
        assert entered.wait(5)
        duplicate = manager.submit("request-a", "task-a", "signature", work)
        assert duplicate.operation_id == operation.operation_id
        with pytest.raises(APIError, match="task_busy"):
            manager.submit("request-b", "task-a", "signature", work)
        with pytest.raises(APIError, match="request_id_conflict"):
            manager.submit("request-a", "task-a", "different", work)
    finally:
        release.set()
        manager.close()
    finished = manager.get(operation.operation_id)
    assert finished.status == "completed"
    assert finished.result.revision == 3
    assert calls == ["run"]


def test_creation_records_task_before_failed_confirmation_without_secrets(tmp_path):
    manager = OperationManager(tmp_path)
    secret = "transient-api-key-must-not-be-persisted"

    def work(context):
        assert secret
        context.created_task("created-task")
        raise APIError("confirmation_failed", "边界确认失败，任务已保留。", 409)

    operation = manager.submit("create-a", None, "non-secret-hash", work)
    manager.close()
    stored = manager.get(operation.operation_id)
    assert stored.status == "failed"
    assert stored.session_id == "created-task"
    assert stored.error.code == "confirmation_failed"
    assert "边界确认失败" in stored.error.message
    assert secret not in "".join(p.read_text() for p in tmp_path.glob("*.json"))


def test_restart_marks_pending_operations_interrupted_and_never_replays(tmp_path):
    manager = OperationManager(tmp_path)
    operation = manager.submit("request-a", "task-a", "signature", lambda _: {})
    manager.close()
    path = tmp_path / f"{operation.operation_id}.json"
    record = json.loads(path.read_text())
    record["operation"]["status"] = "running"
    path.write_text(json.dumps(record))
    restarted = OperationManager(tmp_path)
    try:
        restored = restarted.get(operation.operation_id)
        assert restored.status == "interrupted"
        assert restored.error.code == "operation_interrupted"
        assert (
            restarted.find("request-a", "signature").operation_id
            == operation.operation_id
        )
    finally:
        restarted.close()


def test_unexpected_worker_error_does_not_expose_exception_or_secret(tmp_path):
    manager = OperationManager(tmp_path)

    def work(_):
        raise RuntimeError("provider response contained secret-123")

    operation = manager.submit("request-a", "task-a", "signature", work)
    manager.close()
    result = manager.get(operation.operation_id)
    assert result.status == "failed"
    assert result.error.code == "operation_failed"
    assert "secret-123" not in result.model_dump_json()
    assert "secret-123" not in "".join(p.read_text() for p in tmp_path.glob("*.json"))


def test_failed_status_write_releases_task_and_exposes_recoverable_failure(
    tmp_path, monkeypatch
):
    manager = OperationManager(tmp_path)
    original = manager._save

    def fail_running(operation):
        if operation.status == "running":
            raise OSError("disk unavailable")
        return original(operation)

    monkeypatch.setattr(manager, "_save", fail_running)
    operation = manager.submit("request-a", "task-a", "signature", lambda _: {})
    manager.close()
    assert manager.get(operation.operation_id).status == "failed"
