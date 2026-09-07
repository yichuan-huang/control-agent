"""HTTP boundary regressions; setup seeds a freeze, mutations use real routes."""

import json
import zipfile
from dataclasses import replace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from test_kernel_external import external_prepared, result_zip
from test_web_api import finish

from cfdc.kernel import WorkflowService
from cfdc.web.api import create_app


def seeded(tmp_path):
    service, session = external_prepared(tmp_path / "sessions")
    session = service._save(
        service._append(
            replace(
                session,
                pending_actions=({"action": "run_evaluation", "kind": "evaluation"},),
            ),
            "http_fixture_ready",
            "http-fixture",
            {},
        )
    )
    return service, session


def make_app(tmp_path):
    return create_app(
        session_dir=tmp_path / "sessions",
        runtime_dir=tmp_path / "web",
        frontend_dir=tmp_path / "frontend",
        prepare_rag=False,
    )


def request(client, task, action, input=None, *, request_id=None, revision=None):
    current = client.get(f"/api/v1/tasks/{task}").json()
    return client.post(
        f"/api/v1/tasks/{task}/actions",
        json={
            "request_id": request_id or str(uuid4()),
            "expected_revision": current["revision"] if revision is None else revision,
            "action": action,
            "input": input or {},
        },
    )


def completed(client, response):
    assert response.status_code == 202, response.text
    operation = finish(client, response.json())
    assert operation["status"] == "completed", operation
    return operation


def upload(client, task, path):
    response = client.post(
        "/api/v1/uploads",
        data={"session_id": task},
        files={"file": (path.name, path.read_bytes(), "application/zip")},
    )
    assert response.status_code == 200, response.text
    return response.json()["file_id"]


@pytest.fixture
def prepared(tmp_path):
    service, session = seeded(tmp_path)
    with TestClient(make_app(tmp_path), base_url="http://127.0.0.1:7860") as client:
        completed(client, request(client, session.session_id, "prepare_external_run"))
        yield client, service, service.read(session.session_id), tmp_path


def test_external_stale_revision_and_duplicate_http_requests(prepared):
    client, service, session, tmp_path = prepared
    path = result_zip(tmp_path, session.external_workflow["active_request"])
    file_id = upload(client, session.session_id, path)
    input = {"file_ids": [file_id]}
    stale = request(
        client,
        session.session_id,
        "submit_external_results",
        input,
        revision=session.revision - 1,
    )
    assert stale.status_code == 409
    assert stale.json()["error"]["code"] == "stale_revision"
    request_id = str(uuid4())
    result = completed(
        client,
        request(
            client,
            session.session_id,
            "submit_external_results",
            input,
            request_id=request_id,
            revision=session.revision,
        ),
    )
    stored = service.read(session.session_id)
    duplicate = completed(
        client,
        request(
            client,
            session.session_id,
            "submit_external_results",
            input,
            request_id=request_id,
            revision=session.revision,
        ),
    )
    assert duplicate["operation_id"] == result["operation_id"]
    assert service.read(session.session_id).to_dict() == stored.to_dict()
    assert len(stored.external_workflow["receipts"]) == 1


def test_external_upload_rejects_cross_task_file_id(prepared):
    client, service, session, tmp_path = prepared
    other = service.start(
        {
            "description": "Other task",
            "measured_signals": ["other"],
            "control_input": "actuator",
        }
    )
    path = result_zip(tmp_path, session.external_workflow["active_request"])
    file_id = upload(client, other.session_id, path)
    response = request(
        client, session.session_id, "submit_external_results", {"file_ids": [file_id]}
    )
    assert response.status_code == 202
    operation = finish(client, response.json())
    assert operation["status"] == "failed"
    assert operation["error"]["code"] == "file_task_mismatch"
    assert service.read(session.session_id).to_dict() == session.to_dict()


@pytest.mark.parametrize(
    "corruption", ["candidate", "trial", "duplicate_trial", "fresh_split"]
)
def test_external_rejected_zip_keeps_request_and_budget(prepared, corruption):
    client, service, session, tmp_path = prepared
    active = session.external_workflow["active_request"]
    path = result_zip(tmp_path, active)
    with zipfile.ZipFile(path) as archive:
        contents = {name: json.loads(archive.read(name)) for name in archive.namelist()}
    if corruption == "candidate":
        contents["manifest.json"]["candidate_id"] = "other-candidate"
    elif corruption == "duplicate_trial":
        contents["manifest.json"]["trials"].append(
            contents["manifest.json"]["trials"][0]
        )
    elif corruption == "fresh_split":
        contents["manifest.json"]["stage"] = "fresh_confirmation"
    else:
        rows = contents["manifest.json"]["trials"]
        contents[rows[-1]["file"]]["trial_id"] = (
            rows[0]["trial_id"] if corruption == "duplicate_trial" else "unknown-trial"
        )
    with zipfile.ZipFile(path, "w") as archive:
        for name, value in contents.items():
            archive.writestr(name, json.dumps(value))
    file_id = upload(client, session.session_id, path)
    completed(
        client,
        request(
            client,
            session.session_id,
            "submit_external_results",
            {"file_ids": [file_id]},
        ),
    )
    updated = service.read(session.session_id)
    assert updated.external_workflow["receipts"][-1]["accepted"] is False
    assert updated.external_workflow["active_request"] == active
    assert updated.task.budgets == session.task.budgets
    assert updated.external_workflow["tuning"] == session.external_workflow["tuning"]
    assert updated.evaluation_packets == session.evaluation_packets
    assert updated.revision == session.revision + 1


def test_pending_external_request_survives_web_service_restart(tmp_path):
    service, session = seeded(tmp_path)
    with TestClient(make_app(tmp_path), base_url="http://127.0.0.1:7860") as client:
        completed(client, request(client, session.session_id, "prepare_external_run"))
        before = client.get(f"/api/v1/tasks/{session.session_id}").json()
        package = client.get(
            f"/api/v1/tasks/{session.session_id}/downloads/external_run"
        ).content
    active = service.read(session.session_id).external_workflow["active_request"]
    path = result_zip(tmp_path, active)
    with TestClient(make_app(tmp_path), base_url="http://127.0.0.1:7860") as client:
        assert client.get(f"/api/v1/tasks/{session.session_id}").json() == before
        assert (
            client.get(
                f"/api/v1/tasks/{session.session_id}/downloads/external_run"
            ).content
            == package
        )
        file_id = upload(client, session.session_id, path)
        completed(
            client,
            request(
                client,
                session.session_id,
                "submit_external_results",
                {"file_ids": [file_id]},
            ),
        )
    assert service.read(session.session_id).status == "performance_met"


def test_recovery_refuses_registered_case_without_mutation(tmp_path):
    from cfdc.kernel.cases import public_case_catalog

    service = WorkflowService(tmp_path / "sessions")
    session = service.start_registered_case(next(iter(public_case_catalog())))
    with TestClient(make_app(tmp_path), base_url="http://127.0.0.1:7860") as client:
        response = request(client, session.session_id, "restart_external_acquisition")
        assert response.status_code == 409
    assert service.read(session.session_id).to_dict() == session.to_dict()


def test_terminal_custom_recovery_forks_unconfirmed_without_changing_evidence(prepared):
    client, service, session, tmp_path = prepared
    path = result_zip(tmp_path, session.external_workflow["active_request"])
    file_id = upload(client, session.session_id, path)
    completed(
        client,
        request(
            client,
            session.session_id,
            "submit_external_results",
            {"file_ids": [file_id]},
        ),
    )
    parent = service.read(session.session_id)
    assert parent.status == "performance_met"
    operation = completed(
        client, request(client, session.session_id, "restart_external_acquisition")
    )
    child = service.read(operation["result"]["session_id"])
    assert child.session_id != parent.session_id
    assert child.task.budget_confirmed is False
    assert child.evidence == ()
    assert child.external_workflow is None
    assert child.controller_freeze is None
    assert service.read(parent.session_id).to_dict() == parent.to_dict()


def test_http_can_finish_saved_replay_after_interruption_without_new_upload(
    prepared, monkeypatch
):
    client, service, session, tmp_path = prepared
    path = result_zip(tmp_path, session.external_workflow["active_request"])
    file_id = upload(client, session.session_id, path)
    original = WorkflowService.replay_evaluation

    def crash_after_replay(self, *args, **kwargs):
        original(self, *args, **kwargs)
        raise RuntimeError("simulated interruption after durable replay")

    monkeypatch.setattr(WorkflowService, "replay_evaluation", crash_after_replay)
    response = request(
        client, session.session_id, "submit_external_results", {"file_ids": [file_id]}
    )
    failed = finish(client, response.json())
    assert failed["status"] == "failed"
    monkeypatch.setattr(WorkflowService, "replay_evaluation", original)
    stored = service.read(session.session_id)
    assert stored.status == "performance_met", failed
    current = client.get(f"/api/v1/tasks/{session.session_id}").json()
    assert current["workspace"]["action"] == "submit_external_results"
    completed(client, request(client, session.session_id, "submit_external_results"))
    restored = service.read(session.session_id)
    assert restored.external_workflow["active_request"] is None
    assert len(restored.evaluation_packets) == len(stored.evaluation_packets)
    assert len(restored.evaluation_replays) == len(stored.evaluation_replays)
