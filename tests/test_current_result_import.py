"""Large execution records are archived evidence, not new task authority."""

import json
import zipfile
from pathlib import Path

import pytest

from cfdc.kernel import WorkflowService
from cfdc.kernel.contracts import fingerprint
from cfdc.kernel.importer import MAX_IMPORT_FILE_BYTES, MAX_IMPORT_TOTAL_BYTES


def bundle(tmp_path, *, large=False, corruption=None):
    service = WorkflowService(tmp_path / "source")
    session = service.start(
        {
            "description": "Import task boundaries",
            "measured_signals": ["y"],
            "control_input": "u",
        }
    )
    original = service.export_result_bundle(session.session_id)
    with zipfile.ZipFile(original) as archive:
        values = {name: archive.read(name) for name in archive.namelist()}
    if corruption == "manifest":
        value = json.loads(values["manifest.json"])
        value["session_id"] = "tampered"
        values["manifest.json"] = json.dumps(value).encode()
    if corruption == "task":
        value = json.loads(values["task.json"])
        value["description"] = "tampered"
        values["task.json"] = json.dumps(value).encode()
    if corruption == "events":
        value = json.loads(values["event_chain.json"])
        value[0]["revision_before"] = 50
        values["event_chain.json"] = json.dumps(value).encode()
        manifest = json.loads(values["manifest.json"])
        manifest["artifacts"]["event_chain.json"] = fingerprint(value)
        manifest.pop("bundle_fingerprint")
        manifest["bundle_fingerprint"] = fingerprint(manifest)
        values["manifest.json"] = json.dumps(manifest).encode()
    path = tmp_path / "input.zip"
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, value in values.items():
            if name != "session.json":
                archive.writestr(name, value)
        if large or corruption == "total":
            size = (
                MAX_IMPORT_TOTAL_BYTES + 1
                if corruption == "total"
                else MAX_IMPORT_FILE_BYTES + 1
            )
            with archive.open("session.json", "w") as stream:
                chunk = b" " * (1024 * 1024)
                for _ in range(size // len(chunk)):
                    stream.write(chunk)
                stream.write(chunk[: size % len(chunk)])
        else:
            archive.writestr("session.json", values["session.json"])
        if corruption == "duplicate":
            with pytest.warns(UserWarning):
                archive.writestr("task.json", values["task.json"])
    return path


def test_large_own_result_bundle_imports_only_new_task_authority(tmp_path):
    source = bundle(tmp_path, large=True)
    child = WorkflowService(tmp_path / "target").import_result_bundle(source)
    assert child.task.description == "Import task boundaries"
    assert not child.task.budget_confirmed
    assert not child.evidence and not child.evaluation_packets
    assert child.controller_freeze is None and child.external_workflow is None
    assert any(
        row.get("source") == "session.json"
        and row.get("reason") == "execution_artifact_not_imported"
        for row in child.import_report["discarded"]
    )
    receipt = next(
        row
        for row in child.import_report["file_receipts"]
        if row["path"] == "session.json"
    )
    assert receipt["size_bytes"] > MAX_IMPORT_FILE_BYTES
    assert len(receipt["sha256"]) == 64


@pytest.mark.parametrize(
    "corruption,error",
    [
        ("manifest", "result_import_manifest_fingerprint_mismatch"),
        ("task", "result_import_artifact_fingerprint_mismatch"),
        ("events", "session_event_fingerprint_mismatch"),
        ("total", "result_import_bundle_limit_exceeded"),
        ("duplicate", "result_import_duplicate_member"),
    ],
)
def test_current_result_import_rejects_corruption_before_creating_task(
    tmp_path, corruption, error
):
    source = bundle(tmp_path, corruption=corruption)
    target = WorkflowService(tmp_path / "target")
    with pytest.raises(ValueError, match=error):
        target.import_result_bundle(source)
    assert not list(Path(tmp_path / "target").glob("*.json"))


def test_corrupt_result_import_has_public_chinese_http_error(tmp_path):
    from uuid import uuid4

    from fastapi.testclient import TestClient
    from test_web_api import finish

    from cfdc.web.api import create_app

    source = bundle(tmp_path, corruption="task")
    app = create_app(
        session_dir=tmp_path / "http-sessions",
        runtime_dir=tmp_path / "http",
        frontend_dir=tmp_path / "frontend",
        prepare_rag=False,
    )
    with TestClient(app, base_url="http://127.0.0.1:7860") as client:
        uploaded = client.post(
            "/api/v1/uploads",
            files={"file": ("history.zip", source.read_bytes(), "application/zip")},
        )
        assert uploaded.status_code == 200
        response = client.post(
            "/api/v1/imports",
            json={"request_id": str(uuid4()), "file_id": uploaded.json()["file_id"]},
        )
        assert response.status_code == 202
        result = finish(client, response.json())
        assert result["status"] == "failed"
        assert result["error"]["code"] == "result_import_artifact_fingerprint_mismatch"
        assert (
            result["error"]["message"]
            == "导入包中的任务或诊断文档已改变，请重新导出后再导入。"
        )


def test_result_import_is_idempotent_and_preserves_source(tmp_path):
    source = bundle(tmp_path)
    original = source.read_bytes()
    service = WorkflowService(tmp_path / "target")
    first = service.import_result_bundle(source)
    second = service.import_result_bundle(source)
    assert second.to_dict() == first.to_dict()
    assert source.read_bytes() == original


@pytest.mark.parametrize("kind", ["directory", "old_zip", "unsafe_zip"])
def test_old_or_unsafe_result_sources_are_rejected_without_writes(tmp_path, kind):
    source = tmp_path / "old"
    if kind == "directory":
        source.mkdir()
        (source / "task.json").write_text("{}")
        error = "result_import_current_bundle_required"
    elif kind == "old_zip":
        source = source.with_suffix(".zip")
        with zipfile.ZipFile(source, "w") as archive:
            archive.writestr("task.json", "{}")
        error = "result_import_current_bundle_required"
    else:
        source = bundle(tmp_path)
        with zipfile.ZipFile(source, "a") as archive:
            archive.writestr("../outside.json", "{}")
        error = "result_import_unsafe_path"
    service = WorkflowService(tmp_path / "target")
    with pytest.raises(ValueError, match=error):
        service.import_result_bundle(source)
    assert not list(service.root.glob("*.json"))


@pytest.mark.parametrize(
    "document,field,version,error",
    [
        ("task.json", "schema_version", "1.1.0", "task_contract_version_mismatch"),
        ("task.json", "schema_version", None, "task_contract_version_mismatch"),
        ("task.json", "contract_version", "1.1.0", "task_contract_version_mismatch"),
        (
            "diagnostic_ledger.json",
            "ledger_version",
            "cfdc-diagnostics/v1.0",
            "diagnostic_ledger_version_mismatch",
        ),
        (
            "diagnostic_ledger.json",
            "ledger_version",
            None,
            "diagnostic_ledger_version_mismatch",
        ),
    ],
)
def test_result_import_rejects_obsolete_typed_documents(
    tmp_path, document, field, version, error
):
    source = bundle(tmp_path)
    with zipfile.ZipFile(source) as archive:
        values = {name: archive.read(name) for name in archive.namelist()}
    payload = json.loads(values[document])
    if version is None:
        payload.pop(field)
    else:
        payload[field] = version
    values[document] = json.dumps(payload).encode()
    manifest = json.loads(values["manifest.json"])
    manifest["artifacts"][document] = fingerprint(payload)
    manifest.pop("bundle_fingerprint")
    manifest["bundle_fingerprint"] = fingerprint(manifest)
    values["manifest.json"] = json.dumps(manifest).encode()
    with zipfile.ZipFile(source, "w") as archive:
        for name, value in values.items():
            archive.writestr(name, value)
    original = source.read_bytes()
    service = WorkflowService(tmp_path / "target")
    with pytest.raises(ValueError, match=error):
        service.import_result_bundle(source)
    assert not list(service.root.glob("*.json"))
    assert source.read_bytes() == original
