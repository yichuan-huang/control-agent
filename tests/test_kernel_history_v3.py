"""Old claims may be viewed, never reused as new workflow authority."""

import json

import pytest

from cfdc.kernel import WorkflowService
from cfdc.kernel.contracts import EVIDENCE_SESSION_VERSION


def old_session(service):
    current = service.start(
        {
            "description": "Local speed control",
            "measured_signals": ["y"],
            "control_input": "u",
        }
    )
    path = service.root / f"{current.session_id}.json"
    raw = json.loads(path.read_text())
    raw["session_version"] = "cfdc-session/v2.0"
    raw["status"] = "performance_met"
    raw["evaluation"] = {"status": "performance_met", "judge_version": "legacy"}
    raw["controller_qualification"] = {"status": "offline_qualified"}
    raw["feature_artifact"] = {"features": {"static_gain": {"value": 1.0}}}
    path.write_text(json.dumps(raw))
    return current.session_id, path


def test_previous_session_is_read_only_and_original_file_is_unchanged(tmp_path):
    service = WorkflowService(tmp_path)
    identity, path = old_session(service)
    original = path.read_bytes()
    historical = service.read(identity)
    assert historical.read_only
    assert historical.evaluation["status"] == "performance_met"
    with pytest.raises(ValueError, match="read_only"):
        service.cancel(identity, action_id="cancel-old", revision=historical.revision)
    assert path.read_bytes() == original


def test_fork_starts_new_authority_without_prior_qualification_or_evidence(tmp_path):
    service = WorkflowService(tmp_path)
    identity, _ = old_session(service)
    child = service.fork_session(identity)
    assert child.session_id != identity
    assert child.session_version == EVIDENCE_SESSION_VERSION
    assert not child.read_only
    assert child.status == "intake"
    assert child.evidence == ()
    assert child.feature_artifact is None
    assert child.controller_qualification is None
    assert child.controller_candidate is None
    assert child.controller_freeze is None
    assert child.evaluation is None
    assert child.legacy_lineage["source_session_id"] == identity
