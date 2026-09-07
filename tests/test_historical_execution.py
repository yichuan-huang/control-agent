"""Historical execution records remain inert and public exports stay sanitized."""

from dataclasses import replace

import pytest

from cfdc.kernel import WorkflowService
from cfdc.kernel.session import EvidenceSession


def test_old_session_omits_managed_execution_and_roundtrips(tmp_path):
    session = WorkflowService(tmp_path).start(
        {"description": "old", "measured_signals": ["y"], "control_input": "u"}
    )
    assert "managed_execution" not in session.to_dict()
    assert session.managed_execution is None
    assert EvidenceSession.from_dict(session.to_dict()).to_dict() == session.to_dict()
    with pytest.raises(ValueError, match="managed_execution_version_mismatch"):
        EvidenceSession.from_dict(
            {**session.to_dict(), "managed_execution": {"workflow_version": "unknown"}}
        )


def test_public_managed_export_never_exposes_server_artifact_paths(tmp_path):
    service = WorkflowService(tmp_path)
    session = service.start(
        {"description": "public", "measured_signals": ["y"], "control_input": "u"}
    )
    session = replace(
        session,
        managed_execution={
            "workflow_version": "cfdc-managed-execution/v1",
            "artifacts": [
                {"artifact_id": "a", "path": "/private/internal/results.zip"}
            ],
        },
    )
    # Fixture only; production writes remain revisioned.
    session.save(service._path(session.session_id))
    import json
    import zipfile

    with zipfile.ZipFile(service.export_result_bundle(session.session_id)) as bundle:
        value = json.loads(bundle.read("session.json"))
        assert value["managed_execution"]["artifacts"] == [{"artifact_id": "a"}]
        assert b"/private/internal" not in bundle.read("managed_execution.json")


def test_generic_artifact_projection_hides_managed_storage_paths():
    from cfdc.web.readmodels import _artifact

    report = {
        "session_id": "task",
        "managed_execution": {
            "artifacts": [
                {
                    "artifact_id": "a",
                    "path": "/private/server/data.json",
                    "sha256": "hash",
                }
            ]
        },
    }
    for selected in ("report", "managed_execution"):
        value = _artifact(report, selected)
        assert "/private/server" not in str(value)
        assert "hash" in str(value)
    assert (
        report["managed_execution"]["artifacts"][0]["path"]
        == "/private/server/data.json"
    )
