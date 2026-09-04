from __future__ import annotations

import hashlib
import json
import zipfile
from copy import deepcopy
from pathlib import Path

import pytest

from cfdc.kernel import EvidenceSession, evidence_from_trace
from cfdc.kernel.contracts import fingerprint
from cfdc.kernel.service import WorkflowService
from cfdc.kernel.session import TRAINING_EXERCISE_LOCAL_FIELDS
from cfdc.sim.training import build_training_provider_registries
from cfdc.web import ui as web_ui


def _diagnostics() -> dict[str, dict[str, object]]:
    values = {
        "open_loop_stability": "stable",
        "nonminimum_phase": "minimum_phase",
        "significant_delay": "not_significant",
        "relative_degree": "low",
        "sensing_actuation_adequacy": "adequate",
        "nonlinearity_strength": "weak",
        "coupling_underactuation": "siso",
        "uncertainty_variation": "small",
    }
    return {
        key: {
            "status": "known",
            "assessment": value,
            "evidence": "公开操作员观察",
            "confidence": 0.95,
        }
        for key, value in values.items()
    }


def _ready_exercise_session(tmp_path: Path):
    service = WorkflowService(tmp_path)
    session = service.start_registered_case(
        "dc_motor_speed_v1", evidence_mode="exercise_bundle"
    )
    session = service.confirm_task(
        session.session_id, action_id="confirm", revision=session.revision
    )
    session = service.submit_answer(
        session.session_id,
        action_id="diagnostics",
        revision=session.revision,
        answer=_diagnostics(),
    )
    session = service.advance(
        session.session_id, action_id="route", revision=session.revision
    )
    session = service.compile_protocol(
        session.session_id, action_id="protocol", revision=session.revision
    )
    assert session.pending_actions[0]["action"] == "prepare_training_exercise_bundle"
    return service, session


def test_training_exercise_bundle_is_generated_without_evidence(tmp_path: Path) -> None:
    service, session = _ready_exercise_session(tmp_path)
    identification, identification_id, _, _ = build_training_provider_registries(
        "dc_motor_speed_v1"
    )

    generated = service.prepare_training_exercise_bundle(
        session.session_id,
        action_id="exercise",
        revision=session.revision,
        provider_registry=identification,
        provider_id=identification_id,
        output_dir=tmp_path / "bundle",
    )

    assert not generated.evidence
    assert generated.status == "awaiting_evidence"
    record = generated.training_exercise_bundles[-1]
    bundle = Path(record["bundle_path"])
    assert bundle.is_file()
    with zipfile.ZipFile(bundle) as archive:
        names = set(archive.namelist())
        assert {"manifest.json", "instructions.md"} <= names
        manifest = json.loads(archive.read("manifest.json"))
        assert manifest["bundle_version"] == "cfdc-training-exercise/v1"
        assert manifest["session_id"] == generated.session_id
        assert "private" not in json.dumps(manifest).casefold()


def test_registered_exercise_case_rejects_direct_public_evidence(
    tmp_path: Path,
) -> None:
    service, session = _ready_exercise_session(tmp_path)
    identification, identification_id, _, _ = build_training_provider_registries(
        "dc_motor_speed_v1"
    )
    provider = identification.get(identification_id)
    result = provider.execute(session.protocols[-1], task=session.task.to_dict())
    trace = result[0] if isinstance(result, tuple) else result
    evidence = evidence_from_trace(trace)

    with pytest.raises(
        ValueError, match="registered_case_evidence_requires_bound_provider_or_upload"
    ):
        service.submit_evidence(
            session.session_id,
            action_id="forged-direct-evidence",
            revision=session.revision,
            evidence=evidence,
        )

    persisted = service.read(session.session_id)
    assert persisted.revision == session.revision
    assert persisted.evidence == ()


def test_training_exercise_zip_upload_runs_normal_audit_and_consumes_no_extra_budget(
    tmp_path: Path,
) -> None:
    service, session = _ready_exercise_session(tmp_path)
    identification, identification_id, _, _ = build_training_provider_registries(
        "dc_motor_speed_v1"
    )
    generated = service.prepare_training_exercise_bundle(
        session.session_id,
        action_id="exercise",
        revision=session.revision,
        provider_registry=identification,
        provider_id=identification_id,
        output_dir=tmp_path / "bundle",
    )
    before = generated.revision
    uploaded = service.ingest_upload(
        generated.session_id,
        action_id="upload",
        revision=before,
        paths=[Path(generated.training_exercise_bundles[-1]["bundle_path"])],
    )

    assert uploaded.status == "route_ready"
    assert len(uploaded.evidence) == int(uploaded.protocols[-1]["repeats"])
    assert uploaded.upload_attempts[-1]["evidence_mode"] == "exercise_bundle"
    assert uploaded.revision > before


def test_training_exercise_zip_tampering_is_rejected_without_evidence(
    tmp_path: Path,
) -> None:
    service, session = _ready_exercise_session(tmp_path)
    identification, identification_id, _, _ = build_training_provider_registries(
        "dc_motor_speed_v1"
    )
    generated = service.prepare_training_exercise_bundle(
        session.session_id,
        action_id="exercise",
        revision=session.revision,
        provider_registry=identification,
        provider_id=identification_id,
        output_dir=tmp_path / "bundle",
    )
    source = Path(generated.training_exercise_bundles[-1]["bundle_path"])
    tampered = tmp_path / "tampered.zip"
    with (
        zipfile.ZipFile(source) as original,
        zipfile.ZipFile(tampered, "w", compression=zipfile.ZIP_DEFLATED) as archive,
    ):
        for name in original.namelist():
            value = original.read(name)
            if name == "manifest.json":
                manifest = json.loads(value)
                manifest["protocol_fingerprint"] = "tampered"
                value = (json.dumps(manifest) + "\n").encode()
            archive.writestr(name, value)

    rejected = service.ingest_upload(
        generated.session_id,
        action_id="upload-tampered",
        revision=generated.revision,
        paths=[tampered],
    )
    assert rejected.evidence == ()
    assert rejected.upload_attempts[-1]["status"] == "rejected"
    assert rejected.upload_attempts[-1]["failed_gate"] == "session_binding"


def test_training_exercise_zip_rehashed_output_tampering_is_rejected(
    tmp_path: Path,
) -> None:
    service, session = _ready_exercise_session(tmp_path)
    identification, identification_id, _, _ = build_training_provider_registries(
        "dc_motor_speed_v1"
    )
    generated = service.prepare_training_exercise_bundle(
        session.session_id,
        action_id="exercise",
        revision=session.revision,
        provider_registry=identification,
        provider_id=identification_id,
        output_dir=tmp_path / "bundle",
    )
    source = Path(generated.training_exercise_bundles[-1]["bundle_path"])
    tampered = tmp_path / "rehashed-tampered.zip"
    with zipfile.ZipFile(source) as original:
        members = {name: original.read(name) for name in original.namelist()}
    manifest = json.loads(members["manifest.json"])
    data_name = str(manifest["files"][0]["path"])
    rows = members[data_name].decode("utf-8-sig").splitlines()
    cells = rows[-1].split(",")
    cells[-1] = f"{float(cells[-1]) + 1e-6:.12g}"
    members[data_name] = (
        "\ufeff" + "\n".join([*rows[:-1], ",".join(cells)]) + "\n"
    ).encode("utf-8")
    manifest["files"][0]["sha256"] = hashlib.sha256(members[data_name]).hexdigest()
    manifest.pop("manifest_fingerprint")
    manifest["manifest_fingerprint"] = fingerprint(manifest)
    members["manifest.json"] = (
        json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    ).encode()
    with zipfile.ZipFile(tampered, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, value in members.items():
            archive.writestr(name, value)

    rejected = service.ingest_upload(
        generated.session_id,
        action_id="upload-rehashed-tampered",
        revision=generated.revision,
        paths=[tampered],
    )

    assert rejected.evidence == ()
    assert rejected.upload_attempts[-1]["status"] == "rejected"
    assert rejected.upload_attempts[-1]["failed_gate"] == "session_binding"


def test_persisted_exercise_manifest_must_match_preparation_event(
    tmp_path: Path,
) -> None:
    service, session = _ready_exercise_session(tmp_path)
    identification, identification_id, _, _ = build_training_provider_registries(
        "dc_motor_speed_v1"
    )
    generated = service.prepare_training_exercise_bundle(
        session.session_id,
        action_id="exercise",
        revision=session.revision,
        provider_registry=identification,
        provider_id=identification_id,
        output_dir=tmp_path / "bundle",
    )
    payload = generated.to_dict()
    record = payload["training_exercise_bundles"][-1]
    record["provider_id"] = "forged-provider"
    manifest = {
        key: value
        for key, value in record.items()
        if key not in {*TRAINING_EXERCISE_LOCAL_FIELDS, "manifest_fingerprint"}
    }
    record["manifest_fingerprint"] = fingerprint(manifest)
    record_raw = dict(record)
    record_raw.pop("record_fingerprint")
    record["record_fingerprint"] = fingerprint(record_raw)

    with pytest.raises(ValueError, match="training_exercise_bundle_event_mismatch"):
        EvidenceSession.from_dict(payload)


def test_persisted_exercise_records_and_events_must_be_bijective(
    tmp_path: Path,
) -> None:
    service, session = _ready_exercise_session(tmp_path)
    identification, identification_id, _, _ = build_training_provider_registries(
        "dc_motor_speed_v1"
    )
    first = service.prepare_training_exercise_bundle(
        session.session_id,
        action_id="exercise-one",
        revision=session.revision,
        provider_registry=identification,
        provider_id=identification_id,
        output_dir=tmp_path / "bundle-one",
    )
    revised = service.revise_diagnostic(
        first.session_id,
        action_id="revise",
        revision=first.revision,
        confirmation=True,
        source_text="新的公开试验记录表明时延显著。",
        diagnostic_updates={
            "significant_delay": {
                "status": "known",
                "assessment": "significant",
                "evidence": "时延显著",
            }
        },
    )
    rerouted = service.advance(
        revised.session_id, action_id="reroute", revision=revised.revision
    )
    recompiled = service.compile_protocol(
        rerouted.session_id, action_id="recompile", revision=rerouted.revision
    )
    second = service.prepare_training_exercise_bundle(
        recompiled.session_id,
        action_id="exercise-two",
        revision=recompiled.revision,
        provider_registry=identification,
        provider_id=identification_id,
        output_dir=tmp_path / "bundle-two",
    )
    assert len(second.training_exercise_bundles) == 2
    payload = second.to_dict()
    payload["training_exercise_bundles"][1] = deepcopy(
        payload["training_exercise_bundles"][0]
    )

    with pytest.raises(ValueError, match="training_exercise_bundle_event_mismatch"):
        EvidenceSession.from_dict(payload)


def test_exercise_mode_cannot_use_operator_handoff(tmp_path: Path) -> None:
    service, session = _ready_exercise_session(tmp_path)
    with pytest.raises(ValueError, match="exercise_bundle_requires_training_action"):
        service.prepare_operator_handoff(
            session.session_id,
            action_id="operator",
            revision=session.revision,
        )


def test_exercise_mode_auto_stops_after_bundle_generation(tmp_path: Path) -> None:
    service = WorkflowService(tmp_path)
    session = service.start_registered_case(
        "dc_motor_speed_v1", evidence_mode="exercise_bundle"
    )
    session = service.confirm_task(
        session.session_id, action_id="confirm", revision=session.revision
    )
    session = service.submit_answer(
        session.session_id,
        action_id="diagnostics",
        revision=session.revision,
        answer=_diagnostics(),
    )
    identification, identification_id, evaluation, evaluation_id = (
        build_training_provider_registries("dc_motor_speed_v1")
    )
    stopped = service.run_until_blocked(
        session.session_id,
        provider_registry=identification,
        identification_provider_id=identification_id,
        evaluation_provider_registry=evaluation,
        evaluation_provider_id=evaluation_id,
    )
    assert stopped.status == "awaiting_evidence"
    assert not stopped.evidence
    assert stopped.training_exercise_bundles


def test_web_can_start_explicit_exercise_case_without_editable_contract(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(
        web_ui,
        "start_kernel_app_run",
        lambda *args, **kwargs: (
            {
                "workflow_version": "cfdc-v6-kernel/v1",
                "status": "intake",
                "revision": 0,
                "session_id": "x",
                "task": {},
                "diagnostic": {"entries": [], "readiness": {}},
                "pending_actions": [],
                "input_contract": {},
                "stages": [],
                "education": {},
                "teaching_steps": [],
            },
            {"kernel_session_id": "x", "kernel_revision": 0},
        ),
    )
    monkeypatch.setattr(
        web_ui, "_kernel_outputs", lambda report, state: (report, state)
    )

    report, state = web_ui.start_training_exercise_from_ui("case-01", "", "", "", False)
    assert report["status"] == "intake"
    assert state["kernel_session_id"] == "x"
