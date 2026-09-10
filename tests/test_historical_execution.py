"""Removed managed execution payloads cannot enter current sessions."""

import pytest

from cfdc.kernel import EvidenceSession, WorkflowService


@pytest.mark.parametrize(
    "managed",
    [None, {}, {"workflow_version": "cfdc-managed-execution/v1", "authorized": True}],
)
def test_managed_execution_rejected(tmp_path, managed):
    service = WorkflowService(tmp_path)
    session = service.start(
        {"description": "Hold output", "measured_signals": ["y"], "control_input": "u"}
    )
    assert "managed_execution" not in session.to_dict()
    assert (
        EvidenceSession.from_json(session.to_json()).fingerprint == session.fingerprint
    )
    with pytest.raises(ValueError, match="managed_execution_removed"):
        EvidenceSession.from_dict({**session.to_dict(), "managed_execution": managed})


@pytest.mark.parametrize(
    "field,version,digest_field",
    [
        ("feature_version", "cfdc-features/v1", "artifact_fingerprint"),
        ("qualification_version", "cfdc-qualification/v1", "qualification_fingerprint"),
        ("judge_version", "cfdc-independent-judge/v1", "judge_fingerprint"),
        ("schema_version", "1.1.0", "task_fingerprint"),
    ],
)
def test_obsolete_artifact_versions_are_rejected(field, version, digest_field):
    from cfdc.kernel.contracts import fingerprint
    from cfdc.web.service import validate_kernel_artifact

    value = {
        field: version,
        "description": "Hold output",
        "measured_signals": ["y"],
        "control_input": "u",
    }
    value[digest_field] = fingerprint(value)
    with pytest.raises(ValueError):
        validate_kernel_artifact(value)
