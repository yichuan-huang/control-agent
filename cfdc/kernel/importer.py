"""Read-only importer for current CFDC result bundles.

The importer parses data files only.  It never imports or executes Python from
the source bundle, and ZIP members are consumed in memory after path and size
checks.
"""

from __future__ import annotations

import hashlib
import json
import stat
import zipfile
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from .contracts import (
    IMPORT_REPORT_VERSION,
    TASK_CONTRACT_VERSION,
    TaskContract,
    fingerprint,
    utc_now,
)
from .diagnostics import DiagnosticLedger

MAX_IMPORT_FILES = 2_000
MAX_IMPORT_FILE_BYTES = 32 * 1024 * 1024
MAX_IMPORT_TOTAL_BYTES = 256 * 1024 * 1024

_PRIVATE_KEYS = {
    "private_truth",
    "hidden_truth",
    "hidden_parameters",
    "raw_llm_response",
    "provider_private_state",
    "answer_key",
}


@dataclass(frozen=True)
class ImportInspection:
    source_path: str
    source_kind: str
    source_digest: str
    file_receipts: tuple[Mapping[str, Any], ...]
    task_payload: Mapping[str, Any]
    diagnostic_updates: Mapping[str, Any]
    checks: tuple[Mapping[str, Any], ...]
    discarded: tuple[Mapping[str, Any], ...]

    def public_summary(self) -> dict[str, Any]:
        return {
            "import_version": IMPORT_REPORT_VERSION,
            "source_path": self.source_path,
            "source_kind": self.source_kind,
            "source_digest": self.source_digest,
            "file_count": len(self.file_receipts),
            "file_receipts": [dict(item) for item in self.file_receipts],
            "checks": [dict(item) for item in self.checks],
            "discarded": [dict(item) for item in self.discarded],
        }


def _safe_member(name: str) -> str:
    normalized = name.replace("\\", "/")
    path = PurePosixPath(normalized)
    if (
        not normalized
        or path.is_absolute()
        or any(part in {"", ".", ".."} for part in path.parts)
    ):
        raise ValueError(f"result_import_unsafe_path: {name}")
    if ":" in path.parts[0]:
        raise ValueError(f"result_import_unsafe_path: {name}")
    return path.as_posix()


def _contains_private(value: Any) -> bool:
    if isinstance(value, Mapping):
        return any(
            str(key).casefold() in _PRIVATE_KEYS or _contains_private(item)
            for key, item in value.items()
        )
    if isinstance(value, (list, tuple)):
        return any(_contains_private(item) for item in value)
    return False


def _diagnostics(ledger: DiagnosticLedger) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for item in ledger.entries:
        # Policy decisions must be recomputed for the newly confirmed task.
        status = "unknown" if item.status == "not_relevant" else item.status
        result[item.id] = {
            "status": status,
            "assessment": item.assessment,
            "value": item.value,
            "evidence": item.evidence,
            "confidence": item.confidence,
            "blocking_for_current_route": status != "known",
            "next_resolving_action": item.next_resolving_action
            if status != "known"
            else None,
            "valid_region": item.valid_region,
        }
    return result


def _inspect_current_result(path: Path) -> ImportInspection | None:
    """Import bounded task documents, streaming audit records only for receipts."""
    if not path.is_file() or not zipfile.is_zipfile(path):
        return None
    parsed_names = {
        "manifest.json",
        "task.json",
        "diagnostic_ledger.json",
        "event_chain.json",
    }
    with zipfile.ZipFile(path) as archive:
        try:
            manifest_info = archive.getinfo("manifest.json")
        except KeyError:
            return None
        if manifest_info.file_size > MAX_IMPORT_FILE_BYTES:
            raise ValueError("result_import_file_too_large: manifest.json")
        manifest = json.loads(archive.read(manifest_info))
        if (
            not isinstance(manifest, Mapping)
            or manifest.get("bundle_version") != "cfdc-result-bundle/v1"
        ):
            return None
        infos = archive.infolist()
        if (
            len(infos) > MAX_IMPORT_FILES
            or sum(item.file_size for item in infos) > MAX_IMPORT_TOTAL_BYTES
        ):
            raise ValueError("result_import_bundle_limit_exceeded")
        names = set()
        for info in infos:
            name = _safe_member(info.filename)
            if name in names:
                raise ValueError("result_import_duplicate_member")
            names.add(name)
            if stat.S_ISLNK(info.external_attr >> 16):
                raise ValueError(f"result_import_symlink_not_allowed: {name}")
            if name in parsed_names and info.file_size > MAX_IMPORT_FILE_BYTES:
                raise ValueError(f"result_import_file_too_large: {name}")
        if not parsed_names <= names:
            raise ValueError("result_import_required_document_missing")
        unsigned = dict(manifest)
        supplied = unsigned.pop("bundle_fingerprint", None)
        if supplied != fingerprint(unsigned):
            raise ValueError("result_import_manifest_fingerprint_mismatch")
        documents = {}
        receipts = []
        for info in infos:
            if info.is_dir():
                continue
            digest = hashlib.sha256()
            size = 0
            chunks = []
            with archive.open(info) as stream:
                while chunk := stream.read(1024 * 1024):
                    size += len(chunk)
                    if size > info.file_size:
                        raise ValueError("result_import_size_mismatch")
                    digest.update(chunk)
                    if info.filename in parsed_names:
                        chunks.append(chunk)
            if size != info.file_size:
                raise ValueError("result_import_size_mismatch")
            receipts.append(
                {
                    "path": info.filename,
                    "sha256": digest.hexdigest(),
                    "size_bytes": size,
                }
            )
            if info.filename in parsed_names:
                documents[info.filename] = json.loads(b"".join(chunks))
        declared = manifest.get("artifacts")
        if not isinstance(declared, Mapping):
            raise TypeError("result_import_artifact_manifest_required")
        for name in parsed_names - {"manifest.json"}:
            if declared.get(name) != fingerprint(documents[name]):
                raise ValueError("result_import_artifact_fingerprint_mismatch")
        from .session import SessionEvent, _validate_event_chain

        events = documents["event_chain.json"]
        if not isinstance(events, list):
            raise TypeError("session_event_chain_invalid")
        _validate_event_chain(tuple(SessionEvent.from_dict(event) for event in events))
        task = documents["task.json"]
        ledger = documents["diagnostic_ledger.json"]
        if not isinstance(task, Mapping) or not isinstance(ledger, Mapping):
            raise TypeError("result_import_task_documents_invalid")
        if _contains_private(task) or _contains_private(ledger):
            raise ValueError("result_import_public_artifact_not_found")
        if task.get("schema_version") != TASK_CONTRACT_VERSION:
            raise ValueError("task_contract_version_mismatch")
        for version_field in ("contract_version", "task_contract_version"):
            if version_field in task and task[version_field] != TASK_CONTRACT_VERSION:
                raise ValueError("task_contract_version_mismatch")
        validated_task = TaskContract.from_user_input(task)
        validated_ledger = DiagnosticLedger.from_dict(ledger)
        hashes = {
            row["path"]: row["sha256"]
            for row in sorted(receipts, key=lambda row: row["path"])
        }
        source_digest = hashlib.sha256(
            json.dumps(hashes, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        return ImportInspection(
            source_path=str(path),
            source_kind="zip",
            source_digest=source_digest,
            file_receipts=tuple(sorted(receipts, key=lambda row: row["path"])),
            task_payload=validated_task.to_dict(),
            diagnostic_updates=_diagnostics(validated_ledger),
            checks=tuple(
                {"check": check, "status": "passed"}
                for check in (
                    "path_safety",
                    "streamed_source_hashes",
                    "imported_document_fingerprints",
                    "current_typed_task_and_ledger",
                    "event_chain",
                    "imported_document_public_filter",
                )
            ),
            discarded=tuple(
                {"source": row["path"], "reason": "execution_artifact_not_imported"}
                for row in receipts
                if row["path"] not in parsed_names
            ),
        )


def inspect_result_bundle(source: str | Path) -> ImportInspection:
    path = Path(source).expanduser().resolve()
    result = _inspect_current_result(path)
    if result is None:
        raise ValueError("result_import_current_bundle_required")
    return result


def build_import_report(
    inspection: ImportInspection,
    *,
    session_id: str,
    accepted: Iterable[Mapping[str, Any]],
    discarded: Iterable[Mapping[str, Any]],
    resumed_stage: str,
) -> dict[str, Any]:
    value = {
        **inspection.public_summary(),
        "session_id": session_id,
        "recorded_at": utc_now(),
        "accepted": [dict(item) for item in accepted],
        "discarded": [
            *inspection.public_summary()["discarded"],
            *(dict(item) for item in discarded),
        ],
        "resumed_stage": resumed_stage,
        "source_modified": False,
        "old_execution_authority_imported": False,
        "private_truth_imported": False,
    }
    value["import_fingerprint"] = fingerprint(value)
    return value


__all__ = ["ImportInspection", "build_import_report", "inspect_result_bundle"]
