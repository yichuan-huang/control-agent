"""Read-only importer for public CFDC v3 session bundles.

The importer parses data files only.  It never imports or executes Python from
the source bundle, and ZIP members are consumed in memory after path and size
checks.
"""

from __future__ import annotations

import hashlib
import json
import os
import stat
import zipfile
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from .contracts import DIAGNOSTIC_IDS, IMPORT_REPORT_VERSION, fingerprint, utc_now

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
_IGNORED_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache"}


@dataclass(frozen=True)
class ImportInspection:
    source_path: str
    source_kind: str
    source_digest: str
    file_receipts: tuple[Mapping[str, Any], ...]
    task_payload: Mapping[str, Any]
    diagnostic_updates: Mapping[str, Any]
    candidates: Mapping[str, tuple[Mapping[str, Any], ...]]
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
            "candidate_counts": {
                key: len(values) for key, values in self.candidates.items()
            },
        }


def _safe_member(name: str) -> str:
    normalized = name.replace("\\", "/")
    path = PurePosixPath(normalized)
    if (
        not normalized
        or path.is_absolute()
        or any(part in {"", ".", ".."} for part in path.parts)
    ):
        raise ValueError(f"v3_import_unsafe_path: {name}")
    if ":" in path.parts[0]:
        raise ValueError(f"v3_import_unsafe_path: {name}")
    return path.as_posix()


def _directory_files(root: Path) -> dict[str, bytes]:
    values: dict[str, bytes] = {}
    total = 0
    for current, dir_names, file_names in os.walk(root, followlinks=False):
        current_path = Path(current)
        kept_dirs: list[str] = []
        for name in dir_names:
            item = current_path / name
            if item.is_symlink():
                raise ValueError(
                    f"v3_import_symlink_not_allowed: {item.relative_to(root)}"
                )
            if name not in _IGNORED_DIRS:
                kept_dirs.append(name)
        dir_names[:] = kept_dirs
        for name in file_names:
            path = current_path / name
            if path.is_symlink():
                raise ValueError(
                    f"v3_import_symlink_not_allowed: {path.relative_to(root)}"
                )
            if not path.is_file():
                continue
            relative = _safe_member(path.relative_to(root).as_posix())
            size = path.stat().st_size
            if size > MAX_IMPORT_FILE_BYTES:
                raise ValueError(f"v3_import_file_too_large: {relative}")
            total += size
            if total > MAX_IMPORT_TOTAL_BYTES or len(values) >= MAX_IMPORT_FILES:
                raise ValueError("v3_import_bundle_limit_exceeded")
            values[relative] = path.read_bytes()
    return values


def _zip_files(path: Path) -> dict[str, bytes]:
    values: dict[str, bytes] = {}
    total = 0
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        if len(infos) > MAX_IMPORT_FILES:
            raise ValueError("v3_import_bundle_limit_exceeded")
        for info in infos:
            relative = _safe_member(info.filename)
            mode = info.external_attr >> 16
            if stat.S_ISLNK(mode):
                raise ValueError(f"v3_import_symlink_not_allowed: {relative}")
            if info.is_dir():
                continue
            if info.file_size > MAX_IMPORT_FILE_BYTES:
                raise ValueError(f"v3_import_file_too_large: {relative}")
            total += info.file_size
            if total > MAX_IMPORT_TOTAL_BYTES:
                raise ValueError("v3_import_bundle_limit_exceeded")
            payload = archive.read(info)
            if len(payload) != info.file_size:
                raise ValueError(f"v3_import_size_mismatch: {relative}")
            values[relative] = payload
    return values


def _bundle_files(source: Path) -> tuple[str, dict[str, bytes]]:
    if source.is_dir():
        if source.is_symlink():
            raise ValueError("v3_import_symlink_not_allowed")
        return "directory", _directory_files(source)
    if source.is_file() and zipfile.is_zipfile(source):
        return "zip", _zip_files(source)
    raise ValueError("v3_import_source_must_be_directory_or_zip")


def _contains_private(value: Any) -> bool:
    if isinstance(value, Mapping):
        return any(
            str(key).casefold() in _PRIVATE_KEYS or _contains_private(item)
            for key, item in value.items()
        )
    if isinstance(value, (list, tuple)):
        return any(_contains_private(item) for item in value)
    return False


def _walk(value: Any) -> Iterable[Mapping[str, Any]]:
    if isinstance(value, Mapping):
        yield value
        for item in value.values():
            yield from _walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk(item)


def _task_score(value: Mapping[str, Any]) -> int:
    wrapped = value.get("task_contract") or value.get("task")
    candidate = wrapped if isinstance(wrapped, Mapping) else value
    score = 0
    if candidate.get("description") or candidate.get("natural_language_description"):
        score += 3
    if candidate.get("measured_signals") or candidate.get("observed_outputs"):
        score += 3
    if (
        candidate.get("control_input")
        or candidate.get("control_inputs")
        or candidate.get("actuator")
    ):
        score += 3
    if candidate.get("task_type"):
        score += 1
    return score


def _task_payload(documents: Iterable[Mapping[str, Any]]) -> Mapping[str, Any]:
    candidates = sorted(
        (item for document in documents for item in _walk(document)),
        key=_task_score,
        reverse=True,
    )
    if not candidates or _task_score(candidates[0]) < 9:
        raise ValueError("v3_import_public_task_not_found")
    value = candidates[0]
    wrapped = value.get("task_contract") or value.get("task")
    return dict(wrapped) if isinstance(wrapped, Mapping) else dict(value)


def _diagnostics(documents: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    snapshots: list[list[Mapping[str, Any]]] = []
    for document in documents:
        for item in _walk(document):
            raw = (
                item.get("entries")
                if isinstance(item.get("entries"), list)
                else item.get("diagnostic_ledger")
            )
            if isinstance(raw, Mapping):
                raw = raw.get("entries")
            if isinstance(raw, list) and {
                str(entry.get("id")) for entry in raw if isinstance(entry, Mapping)
            } == set(DIAGNOSTIC_IDS):
                snapshots.append([entry for entry in raw if isinstance(entry, Mapping)])
    if not snapshots:
        return {}
    result: dict[str, Any] = {}
    for item in snapshots[-1]:
        status = str(item.get("status") or "unknown")
        if status == "not_relevant":
            # The old policy authorization cannot be carried across kernels.
            status = "unknown"
        evidence = str(item.get("evidence") or "").strip()
        if status == "known" and not evidence:
            status = "unknown"
        result[str(item["id"])] = {
            "status": status,
            "assessment": item.get("assessment") or item.get("value"),
            "evidence": evidence,
            "confidence": float(item.get("confidence") or 0.0),
            "blocking_for_current_route": status != "known",
            "next_resolving_action": item.get("next_resolving_action")
            if status != "known"
            else None,
            "valid_region": item.get("valid_region"),
        }
    return result


def _classify_candidates(
    documents: Iterable[Mapping[str, Any]],
) -> dict[str, tuple[Mapping[str, Any], ...]]:
    buckets: dict[str, list[Mapping[str, Any]]] = {
        "protocol": [],
        "evidence": [],
        "features": [],
        "route": [],
        "controller": [],
        "freeze": [],
        "evaluation_packet": [],
    }
    seen: set[tuple[str, str]] = set()
    for document in documents:
        for value in _walk(document):
            kinds: list[str] = []
            keys = set(value)
            if (
                "protocol_fingerprint" in keys
                and {"segments", "sample_period_s"} <= keys
            ):
                kinds.append("protocol")
            if "trace_fingerprint" in keys or (
                "evidence_id" in keys
                and ("trace" in keys or "protocol_fingerprint" in keys)
            ):
                kinds.append("evidence")
            if (
                "feature_artifact_fingerprint" in keys
                or "artifact_fingerprint" in keys
                and "features" in keys
                or "feature_ledger" in keys
            ):
                kinds.append("features")
            if "route_id" in keys and (
                "profile_id" in keys or "controller_contract_id" in keys
            ):
                kinds.append("route")
            if "ir_version" in keys and "family" in keys or "controller_ir" in keys:
                kinds.append("controller")
            if "freeze_fingerprint" in keys or "joint_freeze_fingerprint" in keys:
                kinds.append("freeze")
            if "packet_fingerprint" in keys and "trials" in keys:
                kinds.append("evaluation_packet")
            for kind in kinds:
                marker = (kind, fingerprint(value))
                if marker not in seen and not _contains_private(value):
                    buckets[kind].append(dict(value))
                    seen.add(marker)
    return {key: tuple(values) for key, values in buckets.items()}


def _verify_declared_file_hashes(
    documents: Iterable[Mapping[str, Any]], receipts: Mapping[str, str]
) -> None:
    for document in documents:
        for value in _walk(document):
            declared = value.get("files") or value.get("artifacts")
            if not isinstance(declared, list):
                continue
            for item in declared:
                if not isinstance(item, Mapping):
                    continue
                path = item.get("path") or item.get("file")
                digest = item.get("sha256") or item.get("file_hash")
                if path is None or digest is None:
                    continue
                relative = _safe_member(str(path))
                if relative not in receipts or receipts[relative] != str(digest):
                    raise ValueError(
                        f"v3_import_declared_file_hash_mismatch: {relative}"
                    )


def _verify_v3_event_chain(documents: Iterable[Mapping[str, Any]]) -> bool:
    found = False
    for document in documents:
        for value in _walk(document):
            events = value.get("event_log")
            if not isinstance(events, list) or not events:
                continue
            found = True
            previous_fingerprint = None
            previous_state = None
            seen_ids: set[str] = set()
            for event in events:
                if not isinstance(event, Mapping) or event.get("event_id") in seen_ids:
                    raise ValueError("v3_import_event_chain_invalid")
                seen_ids.add(str(event.get("event_id")))
                if (
                    event.get("from_state") != previous_state
                    or event.get("previous_event_fingerprint") != previous_fingerprint
                ):
                    raise ValueError("v3_import_event_chain_invalid")
                payload = event.get("sanitized_payload")
                if event.get("payload_fingerprint") != fingerprint(payload):
                    raise ValueError("v3_import_event_payload_fingerprint_mismatch")
                core_keys = (
                    "event_id",
                    "event_type",
                    "source",
                    "occurred_at",
                    "recorded_at",
                    "from_state",
                    "to_state",
                    "payload_fingerprint",
                    "previous_event_fingerprint",
                    "sanitized_payload",
                )
                if any(key not in event for key in core_keys):
                    raise ValueError("v3_import_event_chain_invalid")
                core = {key: event[key] for key in core_keys}
                if event.get("event_fingerprint") != fingerprint(core):
                    raise ValueError("v3_import_event_fingerprint_mismatch")
                previous_fingerprint = str(event["event_fingerprint"])
                previous_state = event.get("to_state")
            if (
                value.get("workflow_state") is not None
                and value.get("workflow_state") != previous_state
            ):
                raise ValueError("v3_import_event_chain_head_mismatch")
    return found


def inspect_v3_source(source: str | Path) -> ImportInspection:
    path = Path(source).expanduser().resolve()
    source_kind, files = _bundle_files(path)
    receipts = {
        name: hashlib.sha256(payload).hexdigest()
        for name, payload in sorted(files.items())
    }
    source_digest = hashlib.sha256(
        json.dumps(receipts, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    documents: list[Mapping[str, Any]] = []
    discarded: list[Mapping[str, Any]] = []
    for name, payload in sorted(files.items()):
        if not name.casefold().endswith(".json"):
            continue
        try:
            value = json.loads(payload)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"v3_import_invalid_json: {name}") from exc
        if isinstance(value, Mapping):
            documents.append(value)
            if _contains_private(value):
                discarded.append(
                    {"source": name, "reason": "private_or_hidden_fields_not_imported"}
                )
    if not documents:
        raise ValueError("v3_import_json_artifact_not_found")
    _verify_declared_file_hashes(documents, receipts)
    event_chain_found = _verify_v3_event_chain(documents)
    public_documents = [value for value in documents if not _contains_private(value)]
    if not public_documents:
        raise ValueError("v3_import_public_artifact_not_found")
    task = _task_payload(public_documents)
    candidates = _classify_candidates(public_documents)
    checks = (
        {"check": "path_safety", "status": "passed"},
        {"check": "source_hashes", "status": "passed"},
        {"check": "json_parse", "status": "passed"},
        {
            "check": "event_chain",
            "status": "passed" if event_chain_found else "not_present",
        },
        {"check": "private_truth_filter", "status": "passed"},
    )
    file_receipts = tuple(
        {"path": name, "sha256": digest, "size_bytes": len(files[name])}
        for name, digest in receipts.items()
    )
    return ImportInspection(
        source_path=str(path),
        source_kind=source_kind,
        source_digest=source_digest,
        file_receipts=file_receipts,
        task_payload=task,
        diagnostic_updates=_diagnostics(public_documents),
        candidates=candidates,
        checks=checks,
        discarded=tuple(discarded),
    )


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


__all__ = ["ImportInspection", "build_import_report", "inspect_v3_source"]
