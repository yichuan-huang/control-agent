from __future__ import annotations

import json
from pathlib import Path

from cfdc.doctor import DoctorStatus, run_doctor


def test_doctor_reports_required_checks_and_never_echoes_api_key(
    tmp_path: Path,
) -> None:
    report = run_doctor(
        session_dir=tmp_path / "sessions",
        ollama_base_url="http://127.0.0.1:9/v1",
        ollama_model="gemma4:e4b",
        api_key="super-secret-key",
        probe_ollama=False,
    )

    payload = report.to_dict()
    assert report.status in {DoctorStatus.PASS, DoctorStatus.WARN}
    assert payload["doctor_version"] == "cfdc-doctor/v1"
    assert {item["id"] for item in payload["checks"]} >= {
        "python",
        "resources",
        "session_dir",
        "case_registry",
        "rag",
        "ollama",
    }
    assert "super-secret-key" not in json.dumps(payload, ensure_ascii=False)
    assert not payload["required_failures"]


def test_doctor_does_not_probe_non_loopback_ollama(tmp_path: Path) -> None:
    report = run_doctor(
        session_dir=tmp_path / "sessions",
        ollama_base_url="https://remote.example/v1",
        ollama_model="gemma4:e4b",
        probe_ollama=True,
    )

    ollama = next(item for item in report.checks if item.check_id == "ollama")
    assert ollama.status == DoctorStatus.WARN
    assert ollama.details["probed"] is False
    assert "remote.example" not in json.dumps(ollama.to_dict(), ensure_ascii=False)


def test_doctor_marks_invalid_rag_as_optional_warning(tmp_path: Path) -> None:
    report = run_doctor(
        session_dir=tmp_path / "sessions",
        rag_index_dir=tmp_path / "not-an-index",
        probe_ollama=False,
    )

    rag = next(item for item in report.checks if item.check_id == "rag")
    assert rag.status == DoctorStatus.WARN
    assert rag.required is False
    assert report.status == DoctorStatus.WARN
    assert report.ok is True
