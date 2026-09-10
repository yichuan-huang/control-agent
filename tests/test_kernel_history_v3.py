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


@pytest.mark.parametrize(
    "version", ["cfdc-session/v1.0", "cfdc-session/v2.0", "cfdc-session/v3.0"]
)
def test_previous_session_is_rejected_without_modifying_source(tmp_path, version):
    service = WorkflowService(tmp_path)
    identity, path = old_session(service)
    raw = json.loads(path.read_text())
    raw["session_version"] = version
    path.write_text(json.dumps(raw))
    original = path.read_bytes()
    with pytest.raises(ValueError, match="evidence_session_version_mismatch"):
        service.read(identity)
    with pytest.raises(ValueError, match="evidence_session_version_mismatch"):
        service.fork_session(identity)
    assert path.read_bytes() == original


def test_current_read_only_fork_starts_new_authority(tmp_path):
    service = WorkflowService(tmp_path)
    from test_service_evaluation_replay import prepared_service, successful_packet

    service, current, _ = prepared_service(tmp_path, successful_packet)
    identity = current.session_id
    path = service.root / f"{identity}.json"
    raw = current.to_dict()
    raw["read_only"] = True
    path.write_text(json.dumps(raw))
    original = path.read_bytes()
    parent = service.read(identity)
    assert parent.read_only
    with pytest.raises(ValueError, match="read_only"):
        service.cancel(identity, action_id="cancel", revision=parent.revision)
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
    assert path.read_bytes() == original


def test_single_agent_mode_cannot_start_or_restore_current_session(tmp_path):
    from cfdc.kernel import EvidenceSession

    service = WorkflowService(tmp_path)
    task = {
        "description": "Hold output",
        "measured_signals": ["y"],
        "control_input": "u",
    }
    with pytest.raises(ValueError, match="agent_mode_must_be_multi"):
        service.start(task, agent_config={"mode": "single"})
    assert not list(tmp_path.glob("*.json"))
    current = service.start(task, agent_config={"mode": "multi"})
    raw = current.to_dict()
    raw["agent_config"] = {"mode": "single"}
    with pytest.raises(ValueError, match="agent_mode_must_be_multi"):
        EvidenceSession.from_dict(raw)


@pytest.mark.parametrize(
    "field,version_key,old_version",
    [
        ("feature_artifact", "feature_version", "cfdc-features/v1"),
        ("controller_qualification", "qualification_version", "cfdc-qualification/v1"),
        ("evaluation", "judge_version", "legacy"),
        ("evaluation_packets", "packet_version", "cfdc-evaluation-packet/v1.0"),
        ("protocols", "protocol_version", "cfdc-protocol/v1"),
        ("controller_candidate", "ir_version", "cfdc-controller-ir/v1.0"),
        ("tuning", "contract_version", "cfdc-tuning/v1.0"),
    ],
)
def test_current_session_rejects_explicit_old_artifact_versions(
    tmp_path, field, version_key, old_version
):
    from cfdc.kernel import EvidenceSession

    service = WorkflowService(tmp_path)
    session = service.start(
        {"description": "Hold output", "measured_signals": ["y"], "control_input": "u"}
    )
    raw = session.to_dict()
    artifact = {version_key: old_version}
    raw[field] = (
        [artifact] if field in {"evaluation_packets", "protocols"} else artifact
    )
    with pytest.raises(ValueError, match="version_mismatch"):
        EvidenceSession.from_dict(raw)
