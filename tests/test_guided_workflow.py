"""Generic external guidance and preservation of removed automatic sessions."""

import csv
import io
import json
import zipfile
from dataclasses import replace
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from test_service_evaluation_replay import prepared_service, successful_packet
from test_web_api import client, create_task, finish, task_draft  # noqa: F401

from cfdc.kernel import WorkflowService
from cfdc.web.api import create_app


def _action(browser, session_id, action, payload=None):
    summary = browser.get(f"/api/v1/tasks/{session_id}").json()
    response = browser.post(
        f"/api/v1/tasks/{session_id}/actions",
        json={
            "request_id": str(uuid4()),
            "expected_revision": summary["revision"],
            "action": action,
            "input": {
                "payload": payload or {},
                "confirmed": True,
                **(
                    {"mode": "json", "text": json.dumps(payload)}
                    if payload is not None
                    else {}
                ),
            },
        },
    )
    assert response.status_code == 202, response.text
    operation = finish(browser, response.json())
    assert operation["status"] == "completed", json.dumps(operation, ensure_ascii=False)
    return operation


def _assert_guide(summary):
    guide = summary["workflow_guide"]
    for key in ("title", "purpose", "actor", "next_step"):
        assert isinstance(guide[key], str) and guide[key].strip(), guide
    assert isinstance(guide["steps"], list) and guide["steps"], guide
    return guide


def test_removed_simulation_registry_returns_not_found(client):  # noqa: F811
    response = client.get("/api/v1/simulation-runners")
    assert response.status_code == 404, response.text


@pytest.mark.parametrize("endpoint", ["/api/v1/drafts/validate", "/api/v1/tasks"])
def test_removed_managed_draft_is_rejected_without_creating_session(
    client,  # noqa: F811
    tmp_path,
    endpoint,
):
    request = {
        "draft": {
            **task_draft(),
            "execution_mode": "managed",
            "runner_id": "local_python",
            "model_id": "optical",
        }
    }
    if endpoint == "/api/v1/tasks":
        request.update(request_id=str(uuid4()), confirmed=True, use_rag=False)
    response = client.post(endpoint, json=request)
    assert response.status_code == 422, response.text
    assert not list((tmp_path / "sessions").glob("*.json"))


def test_generic_creation_has_guide_without_managed_authority(client, tmp_path):  # noqa: F811
    session_id = create_task(client)
    summary = client.get(f"/api/v1/tasks/{session_id}").json()
    assert not summary.get("managed_execution")
    assert summary["workspace"]["action"] == "answer"
    _assert_guide(summary)
    session = WorkflowService(tmp_path / "sessions").read(session_id)
    assert session.managed_execution is None
    assert "managed_execution" not in session.to_dict()
    assert session.external_workflow is None


def _historical_managed_session(tmp_path, state):
    service, session, _ = prepared_service(tmp_path / "sessions", successful_packet)
    # Construct historical stored evidence only; production APIs must never create
    # this removed execution capability or grant authority from these records.
    session = replace(
        session,
        managed_execution={
            "workflow_version": "cfdc-managed-execution/v1",
            "authorized": True,
            "state": state,
            "runner_id": "local_python",
            "model_id": "optical",
            "task_fingerprint": session.task.fingerprint,
            "artifacts": [],
        },
        external_workflow={
            "workflow_version": "cfdc-external-workflow/v1",
            "source": {"source_kind": "software", "provider_id": "historical"},
            "active_request": None,
            "receipts": [{"accepted": True, "request_id": "old-request"}],
        },
        evidence=({"evidence_id": "historical-measurement", "kind": "experiment"},),
        feature_artifact={"feature_fingerprint": "historical-features"},
        controller_candidate={
            "family": "PI",
            "controller_fingerprint": "old-controller",
        },
    )
    session.save(service._path(session.session_id))
    return service, session


@pytest.mark.parametrize("state", ["running", "paused", "blocked"])
def test_historical_managed_startup_read_and_restart_preserve_parent_bytes(
    tmp_path, state
):
    service, parent = _historical_managed_session(tmp_path, state)
    parent_path = service._path(parent.session_id)
    before = parent_path.read_bytes()
    app = create_app(
        session_dir=tmp_path / "sessions",
        runtime_dir=tmp_path / "web",
        frontend_dir=tmp_path / "frontend",
        prepare_rag=False,
    )
    with TestClient(app, base_url="http://127.0.0.1:7860") as browser:
        assert parent_path.read_bytes() == before
        for _ in range(2):
            response = browser.get(f"/api/v1/tasks/{parent.session_id}")
            assert response.status_code == 200, response.text
            summary = response.json()
            assert summary["external_workflow"]["recovery_required"] is True
            assert summary["external_workflow"]["recovery_reason"]
            assert summary["workspace"]["actionable"] is False
            assert parent_path.read_bytes() == before
        operation = _action(browser, parent.session_id, "restart_external_acquisition")
        child_id = operation["result"]["session_id"]
        assert child_id != parent.session_id
        child = service.read(child_id)
        assert child.legacy_lineage["source_session_id"] == parent.session_id
        assert child.task.description == parent.task.description
        assert child.task.budget_confirmed is False
        assert child.managed_execution is None
        assert child.external_workflow is None
        assert child.evidence == ()
        assert child.protocols == ()
        assert child.active_protocol_fingerprint is None
        assert child.feature_artifact is None
        assert child.controller_candidate is None
        assert child.controller_qualification is None
        assert child.controller_freeze is None
        assert child.provider_bindings == {}
        assert child.evaluation is None
        assert child.evaluation_packets == ()
        assert child.confirmation is None
        child_summary = browser.get(f"/api/v1/tasks/{child_id}").json()
        assert child_summary["workspace"]["action"] == "confirm_task"
        _assert_guide(child_summary)
        assert parent_path.read_bytes() == before
    assert parent_path.read_bytes() == before


def test_identification_guide_matches_download_and_download_does_not_advance(
    client,  # noqa: F811
    tmp_path,
):
    created = client.post(
        "/api/v1/tasks",
        json={
            "request_id": str(uuid4()),
            "draft": {**task_draft(), "input_min": -2},
            "confirmed": True,
            "use_rag": False,
        },
    )
    assert created.status_code == 202, created.text
    operation = finish(client, created.json())
    assert operation["status"] == "completed", operation
    session_id = operation["session_id"]
    assessments = {
        "open_loop_stability": "stable",
        "nonminimum_phase": "minimum_phase",
        "significant_delay": "not_significant",
        "relative_degree": "low",
        "sensing_actuation_adequacy": "adequate",
        "nonlinearity_strength": "weak",
        "coupling_underactuation": "siso",
        "uncertainty_variation": "small",
    }
    _action(
        client,
        session_id,
        "answer",
        {
            key: {
                "status": "known",
                "assessment": value,
                "evidence": "Independent test design statement: " + value,
                "confidence": 1,
            }
            for key, value in assessments.items()
        },
    )
    _action(client, session_id, "advance")
    _action(client, session_id, "select_external_source", {"source_kind": "software"})
    summary = client.get(f"/api/v1/tasks/{session_id}").json()
    _assert_guide(summary)
    assert summary["workspace"]["action"] == "record_operator_report"
    requirements = summary["upload_requirements"]
    assert requirements["stage"] == "identification"
    assert requirements["expected_format"]
    service = WorkflowService(tmp_path / "sessions")
    session_path = service._path(session_id)
    before = session_path.read_bytes()
    for _ in range(2):
        response = client.get(f"/api/v1/tasks/{session_id}/downloads/operator")
        assert response.status_code == 200, response.text
        with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
            card = json.loads(archive.read("operator_card.json"))
            templates = {
                Path(name).name: next(
                    csv.reader(io.StringIO(archive.read(name).decode("utf-8-sig")))
                )
                for name in archive.namelist()
                if name.endswith(".csv")
            }
        assert requirements["file_count"] == len(templates) == card["repeats"]
        assert requirements["repeats"] == card["repeats"]
        assert {row["filename"] for row in requirements["files"]} == templates.keys()
        for row in requirements["files"]:
            assert {column["name"] for column in row["columns"]} == set(
                templates[row["filename"]]
            )
        assert session_path.read_bytes() == before
        assert client.get(f"/api/v1/tasks/{session_id}").json() == summary
    assert service.read(session_id).evidence == ()


@pytest.mark.parametrize(
    ("pending", "expected"),
    [
        ({"action": "prepare_external_run", "stage": "tuning_probe"}, "候选调优"),
        ({"action": "record_fresh_confirmation"}, "全新确认"),
    ],
)
def test_guide_uses_pending_stage_before_request_exists(pending, expected):
    from cfdc.web.external_guide import workflow_guide

    guide = workflow_guide(
        {
            "input_contract": {"action": "prepare_external_run"},
            "external_workflow": {"active_request": None},
            "pending_actions": [pending],
        }
    )
    assert expected in guide["title"]


def test_protocol_boundary_failure_has_actionable_public_reason():
    from cfdc.web.actions import public_action_error

    error = public_action_error(
        ValueError("protocol_segment_outside_task_envelope"), {}
    ).public
    assert error.code == "protocol_segment_outside_task_envelope"
    assert "未开始实验" in error.message
    assert "边界" in error.message
    assert "新建任务" in error.message
