from __future__ import annotations

import asyncio
import json
from tempfile import SpooledTemporaryFile
from time import monotonic, sleep
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from cfdc.kernel import WorkflowService
from cfdc.kernel.contracts import TaskContract
from cfdc.web.api import create_app
from cfdc.web.drafts import empty_draft
from cfdc.web.errors import APIError


def task_draft():
    return {
        **empty_draft(),
        "description": "保持温度",
        "outputs": [["temperature", "degC"]],
        "inputs": [["heater"]],
        "input_unit": "kW",
        "input_min": 0,
        "input_max": 2,
        "state_stop": 50,
    }


@pytest.fixture
def client(tmp_path):
    app = create_app(
        session_dir=tmp_path / "sessions",
        runtime_dir=tmp_path / "web",
        frontend_dir=tmp_path / "frontend",
        prepare_rag=False,
    )
    with TestClient(app, base_url="http://127.0.0.1:7860") as client:
        yield client


def finish(client, operation, timeout=10):
    deadline = monotonic() + timeout
    while operation["status"] in {"queued", "running"}:
        assert monotonic() < deadline, operation
        sleep(0.01)
        response = client.get(f"/api/v1/operations/{operation['operation_id']}")
        assert response.status_code == 200
        operation = response.json()
    return operation


def create_task(client):
    response = client.post(
        "/api/v1/tasks",
        json={
            "request_id": str(uuid4()),
            "draft": task_draft(),
            "confirmed": True,
            "use_rag": False,
        },
    )
    assert response.status_code == 202, response.text
    operation = finish(client, response.json())
    assert operation["status"] == "completed", operation
    return operation["session_id"]


def test_create_confirms_separately_and_summary_excludes_full_report(client, tmp_path):
    task_id = create_task(client)
    response = client.get(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["revision"] == 2
    assert body["read_only"] is False
    assert body["workspace"]["action"] == "answer"
    assert not {"evaluation_packets", "events", "tuning", "agent_records"} & body.keys()
    session = WorkflowService(tmp_path / "sessions").read(task_id)
    assert len(session.events) == 2
    assert session.task.budget_confirmed


def test_expert_task_can_be_created_unconfirmed_then_confirmed_immutably(
    client, tmp_path
):
    task = TaskContract.from_user_input(
        {
            "description": "保持温度",
            "task_type": "local_setpoint_hold",
            "measured_signals": ["temperature"],
            "control_input": "heater",
            "input_min": 0,
            "input_max": 2,
            "state_stop": 50,
        }
    ).to_dict(include_fingerprint=False)
    created = client.post(
        "/api/v1/tasks",
        json={
            "request_id": str(uuid4()),
            "task": task,
            "confirmed": False,
            "use_rag": False,
        },
    )
    assert created.status_code == 202, created.text
    operation = finish(client, created.json())
    assert operation["status"] == "completed"
    assert operation["result"]["revision"] == 1
    task_id = operation["session_id"]

    rejected = client.post(
        f"/api/v1/tasks/{task_id}/actions",
        json={
            "request_id": str(uuid4()),
            "expected_revision": 1,
            "action": "confirm_task",
            "input": {"confirmed": True, "payload": {"description": "changed"}},
        },
    )
    assert rejected.status_code == 202
    rejected_operation = finish(client, rejected.json())
    assert rejected_operation["status"] == "failed"
    assert rejected_operation["error"]["code"] == "boundary_immutable"
    assert client.get(f"/api/v1/tasks/{task_id}").json()["revision"] == 1

    confirmed = client.post(
        f"/api/v1/tasks/{task_id}/actions",
        json={
            "request_id": str(uuid4()),
            "expected_revision": 1,
            "action": "confirm_task",
            "input": {"confirmed": True},
        },
    )
    completed = finish(client, confirmed.json())
    assert completed["status"] == "completed"
    assert completed["result"]["revision"] == 2
    session = WorkflowService(tmp_path / "sessions").read(task_id)
    assert len(session.events) == 2
    assert session.task.budget_confirmed


def test_guided_draft_still_requires_confirmation(client):
    response = client.post(
        "/api/v1/tasks",
        json={
            "request_id": str(uuid4()),
            "draft": task_draft(),
            "confirmed": False,
            "use_rag": False,
        },
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "confirmation_required"


def test_displayed_task_budgets_match_kernel_defaults_and_persisted_task(
    client, tmp_path
):
    validated = client.post("/api/v1/drafts/validate", json={"draft": task_draft()})
    assert validated.status_code == 200
    displayed_budgets = validated.json()["task"]["budgets"]
    assert displayed_budgets == {
        "clarification_rounds": 6,
        "distinct_experiments": 4,
        "same_failure_retries": 1,
        "elapsed_time_s": 7200.0,
        "cumulative_excitation_time_s": 1800.0,
    }
    case = client.get("/api/v1/cases/dc_motor_speed_v1")
    assert case.status_code == 200
    assert set(case.json()["task"]["budgets"]) == set(displayed_budgets)

    task_id = create_task(client)
    persisted = WorkflowService(tmp_path / "sessions").read(task_id)
    assert dict(persisted.task.budgets) == displayed_budgets


def test_draft_boundary_errors_are_field_specific_and_do_not_create(client, tmp_path):
    draft = task_draft()
    draft["state_stop"] = None
    response = client.post("/api/v1/drafts/validate", json={"draft": draft})
    assert response.status_code == 422
    assert "state_stop" in response.json()["error"]["fields"]
    assert not list((tmp_path / "sessions").glob("*.json"))


def test_requests_are_idempotent_and_stale_revision_does_not_execute(client):
    task_id = create_task(client)
    body = {
        "request_id": str(uuid4()),
        "expected_revision": 2,
        "action": "cancel",
        "input": {},
    }
    path = f"/api/v1/tasks/{task_id}/actions"
    first = client.post(path, json=body)
    assert first.status_code == 202, first.text
    completed = finish(client, first.json())
    second = client.post(path, json=body)
    assert second.status_code == 202
    assert second.json()["operation_id"] == completed["operation_id"]
    stale = client.post(path, json={**body, "request_id": str(uuid4())})
    assert stale.status_code == 409
    assert stale.json()["error"]["latest_revision"] == 3
    assert client.get(f"/api/v1/tasks/{task_id}").json()["revision"] == 3


def test_confirmation_failure_keeps_created_task_recoverable(
    client, tmp_path, monkeypatch
):
    from cfdc.web import service

    original = service.continue_kernel_app_run

    def fail_confirmation(state, *, action, **kwargs):
        if action == "confirm_task":
            raise ValueError("confirmation_failed")
        return original(state, action=action, **kwargs)

    monkeypatch.setattr(service, "continue_kernel_app_run", fail_confirmation)
    response = client.post(
        "/api/v1/tasks",
        json={
            "request_id": str(uuid4()),
            "draft": task_draft(),
            "confirmed": True,
            "use_rag": False,
        },
    )
    operation = finish(client, response.json())
    assert operation["status"] == "failed"
    assert operation["session_id"]
    task = client.get(f"/api/v1/tasks/{operation['session_id']}").json()
    assert task["revision"] == 1
    assert task["workspace"]["action"] == "confirm_task"


def test_origins_credentials_and_upload_task_isolation(client, tmp_path):
    denied = client.post(
        "/api/v1/config/probe", headers={"Origin": "https://attacker.test"}, json={}
    )
    assert denied.status_code == 403
    task_a, task_b = create_task(client), create_task(client)
    upload = client.post(
        "/api/v1/uploads",
        data={"session_id": task_a},
        files={"file": ("trace.csv", b"t,y\n0,1\n", "text/csv")},
    )
    assert upload.status_code == 200, upload.text
    file_id = upload.json()["file_id"]
    assert "path" not in upload.json()
    with pytest.raises(APIError, match="file_task_mismatch"):
        client.app.state.files.resolve(file_id, session_id=task_b)


def test_upload_rejects_oversized_content_length_before_reading_body(
    tmp_path, monkeypatch
):
    from cfdc.web import api

    monkeypatch.setattr(api, "MAX_UPLOAD_BYTES", 1024)
    monkeypatch.setattr(api, "UPLOAD_ENVELOPE_BYTES", 256)
    app = create_app(
        session_dir=tmp_path / "sessions",
        runtime_dir=tmp_path / "web",
        frontend_dir=tmp_path / "frontend",
        prepare_rag=False,
    )
    with TestClient(app, base_url="http://127.0.0.1:7860") as bounded_client:
        response = bounded_client.post(
            "/api/v1/uploads",
            headers={"Content-Length": "1281", "Content-Type": "multipart/form-data"},
            content=b"body must not be parsed",
        )

    assert response.status_code == 413
    assert response.json()["error"]["code"] == "file_too_large"
    assert not list((tmp_path / "web" / "uploads").iterdir())


def test_upload_accepts_file_at_limit_with_multipart_envelope(tmp_path, monkeypatch):
    from cfdc.web import api, files

    monkeypatch.setattr(api, "MAX_UPLOAD_BYTES", 1024)
    monkeypatch.setattr(api, "UPLOAD_ENVELOPE_BYTES", 512)
    monkeypatch.setattr(files, "MAX_UPLOAD_BYTES", 1024)
    app = create_app(
        session_dir=tmp_path / "sessions",
        runtime_dir=tmp_path / "web",
        frontend_dir=tmp_path / "frontend",
        prepare_rag=False,
    )
    with TestClient(app, base_url="http://127.0.0.1:7860") as bounded_client:
        response = bounded_client.post(
            "/api/v1/uploads",
            files={"file": ("trace.csv", b"x" * 1024, "text/csv")},
        )

    assert response.status_code == 200, response.text
    assert response.json()["size"] == 1024


def test_streamed_upload_stops_early_and_closes_partial_spool(tmp_path, monkeypatch):
    from starlette import formparsers

    from cfdc.web import api

    monkeypatch.setattr(api, "MAX_UPLOAD_BYTES", 1024)
    monkeypatch.setattr(api, "UPLOAD_ENVELOPE_BYTES", 256)
    spools = []

    def tracked_spool(*args, **kwargs):
        spool = SpooledTemporaryFile(*args, **kwargs)  # noqa: SIM115
        spools.append(spool)
        return spool

    monkeypatch.setattr(formparsers, "SpooledTemporaryFile", tracked_spool)
    app = create_app(
        session_dir=tmp_path / "sessions",
        runtime_dir=tmp_path / "web",
        frontend_dir=tmp_path / "frontend",
        prepare_rag=False,
    )
    boundary = b"upload-boundary"
    prefix = (
        b"--" + boundary + b'\r\nContent-Disposition: form-data; name="file"; '
        b'filename="trace.csv"\r\nContent-Type: text/csv\r\n\r\n'
    )
    chunks = [prefix + (b"x" * 1000), b"y" * 512, b"z" * 512]
    consumed = 0

    async def receive():
        nonlocal consumed
        chunk = chunks[consumed]
        consumed += 1
        return {
            "type": "http.request",
            "body": chunk,
            "more_body": consumed < len(chunks),
        }

    sent = []

    async def send(message):
        sent.append(message)

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/api/v1/uploads",
        "raw_path": b"/api/v1/uploads",
        "query_string": b"",
        "root_path": "",
        "server": ("127.0.0.1", 7860),
        "client": ("127.0.0.1", 12345),
        "headers": [
            (b"host", b"127.0.0.1:7860"),
            (b"content-type", b"multipart/form-data; boundary=" + boundary),
        ],
    }
    asyncio.run(app(scope, receive, send))

    start = next(
        message for message in sent if message["type"] == "http.response.start"
    )
    body = b"".join(
        message.get("body", b"")
        for message in sent
        if message["type"] == "http.response.body"
    )
    assert start["status"] == 413, (body, consumed, spools)
    assert json.loads(body)["error"]["code"] == "file_too_large"
    assert consumed == 2
    assert spools and all(spool.closed for spool in spools)
    assert not list((tmp_path / "web" / "uploads").iterdir())


def test_invalid_requests_never_echo_credential_values(client):
    secret = "not-a-real-key-secret-value"
    result = client.post("/api/v1/tasks", json={"credentials": {"api_key": secret}})
    assert result.status_code == 422
    assert secret not in result.text
    config = client.get("/api/v1/config").json()
    assert "api_key" not in json.dumps(config)
    assert config["rag"]["status"] == "error"


def test_terminal_and_read_only_tasks_reject_mutation(client, tmp_path):
    task_id = create_task(client)
    path = tmp_path / "sessions" / f"{task_id}.json"
    stored = json.loads(path.read_text())
    stored["read_only"] = True
    path.write_text(json.dumps(stored))
    response = client.post(
        f"/api/v1/tasks/{task_id}/actions",
        json={
            "request_id": str(uuid4()),
            "expected_revision": 2,
            "action": "cancel",
        },
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "task_read_only"


def test_static_spa_shell_has_safe_api_404(client):
    response = client.get("/api/v1/does-not-exist")
    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/json")
    assert client.get("/").status_code == 503  # explicit frontend build instructions


def test_untrusted_host_cannot_make_its_origin_look_like_local_app(client):
    response = client.get(
        "/api/v1/config",
        headers={
            "Host": "attacker.example:7860",
            "Origin": "http://attacker.example:7860",
        },
    )
    assert response.status_code == 403


def test_evidence_curves_only_expose_current_protocol_accepted_trials(client):
    case_id = "dc_motor_speed_v1"
    case = client.get(f"/api/v1/cases/{case_id}").json()
    operation = finish(
        client,
        client.post(
            "/api/v1/tasks",
            json={
                "request_id": str(uuid4()),
                "draft": case["draft"],
                "case_id": case_id,
                "confirmed": True,
                "use_rag": False,
            },
        ).json(),
    )
    assert operation["status"] == "completed", operation
    task_id = operation["session_id"]
    protocol = client.get(f"/api/v1/tasks/{task_id}/protocol").json()
    option = protocol["evidence_options"][0]
    response = client.get(
        f"/api/v1/tasks/{task_id}/evidence/curves",
        params={"selection": option["value"], "signal": option["signals"][0]},
    )
    assert response.status_code == 200, response.text
    curve = response.json()
    assert curve["stage"] == "evidence"
    assert curve["protocol_fingerprint"] == protocol["protocol_fingerprint"]
    assert curve["revision"] == protocol["revision"]
    assert curve["fingerprint"] == option["fingerprint"]
    assert 0 < curve["display_points"] <= 2000
    assert len(response.content) <= 256 * 1024
    invalid = client.get(
        f"/api/v1/tasks/{task_id}/evidence/curves",
        params={"selection": option["value"], "signal": "unknown"},
    )
    assert invalid.status_code == 422
    assert invalid.json()["error"]["code"] == "evidence_curve_unavailable"
