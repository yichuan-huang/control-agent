"""Independent immutable index for advisory operational-history summaries."""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from collections import Counter
from dataclasses import dataclass, field
from datetime import UTC, datetime
from importlib.resources import files
from pathlib import Path
from typing import Any
from uuid import uuid4

import numpy as np
from jsonschema import Draft202012Validator, FormatChecker

HISTORY_SCHEMA_VERSION = "cfdc-operational-history/v1"
SOURCE_SCHEMA_VERSION = "cfdc-operational-history-source/v1"
RECORD_SCHEMA_VERSION = "cfdc-operational-history-record/v1"
DEFAULT_HISTORY_LIMIT = 10
MAX_HISTORY_LIMIT = 50
RECORD_TYPES = frozenset(
    {
        "equipment_manual",
        "feature_artifact",
        "controller_freeze",
        "qualification_report",
        "performance_baseline",
        "adaptation_episode",
        "degradation_event",
        "rollback_report",
        "maintenance_record",
    }
)


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _hash_json(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _parse_timestamp(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"invalid operational-history timestamp: {value}") from exc
    if parsed.tzinfo is None:
        raise ValueError("operational-history timestamps must include a timezone")
    return parsed.astimezone(UTC)


def _encode(encoder: Any, texts: list[str], *, is_query: bool) -> np.ndarray:
    method = encoder.encode if hasattr(encoder, "encode") else encoder
    try:
        values = method(texts, is_query=is_query)
    except TypeError as exc:
        if "is_query" not in str(exc):
            raise
        values = method(texts)
    result = np.asarray(values, dtype=np.float32)
    if result.ndim != 2 or result.shape[0] != len(texts):
        raise ValueError("history encoder returned an invalid matrix")
    return result


def _lexical_terms(text: str) -> set[str]:
    terms: set[str] = set()
    for token in re.findall(
        r"[\u3400-\u4dbf\u4e00-\u9fff]+|[A-Za-z0-9_]+", text.casefold()
    ):
        if re.fullmatch(r"[\u3400-\u4dbf\u4e00-\u9fff]+", token):
            terms.update(token[index : index + 2] for index in range(len(token) - 1))
        else:
            terms.add(token)
    return terms


def _lexical_score(query: str, text: str) -> float:
    query_terms = _lexical_terms(query)
    if not query_terms:
        return 0.0
    return len(query_terms & _lexical_terms(text)) / len(query_terms)


@dataclass(frozen=True)
class OperationalHistoryRecord:
    record_id: str
    record_type: str
    record_version: str
    schema_version: str
    plant_id: str
    configuration: dict[str, Any] = field(repr=False)
    configuration_fingerprint: str = ""
    operating_region: dict[str, Any] = field(default_factory=dict, repr=False)
    operating_region_fingerprint: str = ""
    captured_at: str = ""
    valid_from: str = ""
    valid_until: str | None = None
    supersedes: tuple[str, ...] = ()
    source_refs: tuple[str, ...] = ()
    session_refs: tuple[str, ...] = ()
    payload: Any = field(default=None, repr=False)
    payload_sha256: str = ""
    summary: str = ""

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> OperationalHistoryRecord:
        return cls(
            record_id=str(value["record_id"]),
            record_type=str(value["record_type"]),
            record_version=str(value["record_version"]),
            schema_version=str(value["schema_version"]),
            plant_id=str(value["plant_id"]),
            configuration=dict(value["configuration"]),
            configuration_fingerprint=str(value["configuration_fingerprint"]),
            operating_region=dict(value["operating_region"]),
            operating_region_fingerprint=str(value["operating_region_fingerprint"]),
            captured_at=str(value["captured_at"]),
            valid_from=str(value["valid_from"]),
            valid_until=(
                str(value["valid_until"])
                if value.get("valid_until") is not None
                else None
            ),
            supersedes=tuple(str(item) for item in value["supersedes"]),
            source_refs=tuple(str(item) for item in value["source_refs"]),
            session_refs=tuple(str(item) for item in value["session_refs"]),
            payload=value["payload"],
            payload_sha256=str(value["payload_sha256"]),
            summary=str(value["summary"]),
        )


@dataclass(frozen=True)
class OperationalHistoryRequest:
    plant_id: str
    configuration_fingerprint: str
    operating_region_fingerprint: str
    record_types: tuple[str, ...] = ()
    as_of: str | datetime | None = None
    query_text: str = ""
    limit: int = DEFAULT_HISTORY_LIMIT

    def __post_init__(self) -> None:
        if not self.plant_id.strip():
            raise ValueError("plant_id is required")
        for name, value in (
            ("configuration_fingerprint", self.configuration_fingerprint),
            ("operating_region_fingerprint", self.operating_region_fingerprint),
        ):
            if not re.fullmatch(r"[a-f0-9]{64}", value):
                raise ValueError(f"{name} must contain 64 lowercase hex characters")
        unknown = set(self.record_types) - RECORD_TYPES
        if unknown:
            raise ValueError(
                f"unknown operational-history record types: {sorted(unknown)}"
            )
        if not 1 <= int(self.limit) <= MAX_HISTORY_LIMIT:
            raise ValueError(
                f"history query limit must be between 1 and {MAX_HISTORY_LIMIT}"
            )

    def as_of_datetime(self) -> datetime:
        if self.as_of is None:
            return datetime.now(UTC)
        if isinstance(self.as_of, datetime):
            if self.as_of.tzinfo is None:
                raise ValueError("history as_of must include a timezone")
            return self.as_of.astimezone(UTC)
        return _parse_timestamp(str(self.as_of))

    def identity(self) -> dict[str, str]:
        return {
            "plant_id": self.plant_id,
            "configuration_fingerprint": self.configuration_fingerprint,
            "operating_region_fingerprint": self.operating_region_fingerprint,
        }


@dataclass(frozen=True)
class OperationalHistoryMatch:
    record_id: str
    record_type: str
    record_version: str
    schema_version: str
    plant_id: str
    configuration_fingerprint: str
    operating_region_fingerprint: str
    captured_at: str
    valid_from: str
    valid_until: str | None
    summary: str
    source_refs: tuple[str, ...]
    session_refs: tuple[str, ...]
    payload_sha256: str
    score: float | None = None

    def model_dump(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "record_type": self.record_type,
            "record_version": self.record_version,
            "schema_version": self.schema_version,
            "identity": {
                "plant_id": self.plant_id,
                "configuration_fingerprint": self.configuration_fingerprint,
                "operating_region_fingerprint": self.operating_region_fingerprint,
            },
            "captured_at": self.captured_at,
            "valid_from": self.valid_from,
            "valid_until": self.valid_until,
            "summary": self.summary,
            "provenance": {
                "source_refs": list(self.source_refs),
                "session_refs": list(self.session_refs),
                "payload_sha256": self.payload_sha256,
            },
            "score": self.score,
        }


@dataclass(frozen=True)
class OperationalHistoryResult:
    index_snapshot: str
    request_identity: dict[str, str]
    records: tuple[OperationalHistoryMatch, ...] = ()
    empty_reason: str | None = None

    def model_dump(self) -> dict[str, Any]:
        return {
            "index_snapshot": self.index_snapshot,
            "request_identity": dict(self.request_identity),
            "empty_reason": self.empty_reason,
            "records": [record.model_dump() for record in self.records],
        }


def _validated_records(source_file: Path) -> tuple[list[OperationalHistoryRecord], str]:
    try:
        raw_text = source_file.read_text(encoding="utf-8")
        payload = json.loads(raw_text)
        schema = json.loads(
            files("cfdc.history")
            .joinpath("resources", "operational_history_schema.json")
            .read_text(encoding="utf-8")
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"unable to read operational-history source: {exc}") from exc
    try:
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(payload)
    except Exception as exc:
        raise ValueError(f"operational-history source is invalid: {exc}") from exc
    records = [
        OperationalHistoryRecord.from_mapping(item) for item in payload["records"]
    ]
    by_id = {record.record_id: record for record in records}
    if len(by_id) != len(records):
        raise ValueError("operational-history record IDs must be unique")
    for record in records:
        if _hash_json(record.configuration) != record.configuration_fingerprint:
            raise ValueError(f"configuration fingerprint mismatch: {record.record_id}")
        if _hash_json(record.operating_region) != record.operating_region_fingerprint:
            raise ValueError(
                f"operating-region fingerprint mismatch: {record.record_id}"
            )
        if _hash_json(record.payload) != record.payload_sha256:
            raise ValueError(f"payload hash mismatch: {record.record_id}")
        valid_from = _parse_timestamp(record.valid_from)
        valid_until = (
            _parse_timestamp(record.valid_until) if record.valid_until else None
        )
        _parse_timestamp(record.captured_at)
        if valid_until is not None and valid_until < valid_from:
            raise ValueError(f"invalid validity interval: {record.record_id}")
        identity = (
            record.plant_id,
            record.configuration_fingerprint,
            record.operating_region_fingerprint,
            record.record_type,
        )
        for superseded_id in record.supersedes:
            superseded = by_id.get(superseded_id)
            if superseded is None:
                raise ValueError(f"unknown superseded record: {superseded_id}")
            superseded_identity = (
                superseded.plant_id,
                superseded.configuration_fingerprint,
                superseded.operating_region_fingerprint,
                superseded.record_type,
            )
            if identity != superseded_identity:
                raise ValueError("supersedes must keep identity and record type")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(record_id: str) -> None:
        if record_id in visiting:
            raise ValueError("operational-history supersedes cycle detected")
        if record_id in visited:
            return
        visiting.add(record_id)
        for superseded_id in by_id[record_id].supersedes:
            visit(superseded_id)
        visiting.remove(record_id)
        visited.add(record_id)

    for record_id in by_id:
        visit(record_id)
    return records, hashlib.sha256(raw_text.encode("utf-8")).hexdigest()


class OperationalHistoryIndex:
    def __init__(
        self,
        snapshot: Path,
        *,
        encoder: Any | None = None,
        load_encoder: bool = True,
    ) -> None:
        self.snapshot = snapshot
        self.index_snapshot = snapshot.name
        manifest_path = snapshot / "manifest.json"
        try:
            self.manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"invalid operational-history manifest: {exc}") from exc
        if self.manifest.get("schema_version") != HISTORY_SCHEMA_VERSION:
            raise ValueError("unsupported operational-history snapshot schema")
        for filename, field_name in (
            ("metadata.sqlite3", "metadata_checksum"),
            ("vectors.npy", "vector_checksum"),
        ):
            if _hash_file(snapshot / filename) != self.manifest.get(field_name):
                raise ValueError(f"operational-history {filename} checksum mismatch")
        try:
            self._vectors = np.load(snapshot / "vectors.npy", allow_pickle=False)
        except (OSError, ValueError) as exc:
            raise ValueError(f"invalid operational-history vectors: {exc}") from exc
        database_uri = f"file:{(snapshot / 'metadata.sqlite3').resolve()}?mode=ro"
        try:
            with sqlite3.connect(database_uri, uri=True) as connection:
                connection.row_factory = sqlite3.Row
                self._rows = [
                    dict(row)
                    for row in connection.execute("SELECT * FROM records ORDER BY id")
                ]
        except sqlite3.Error as exc:
            raise ValueError(f"invalid operational-history metadata: {exc}") from exc
        if len(self._rows) != len(self._vectors):
            raise ValueError("operational-history metadata/vector count mismatch")
        if encoder is not None:
            self.encoder = encoder
        elif load_encoder:
            from cfdc.rag import SentenceTransformerEncoder

            self.encoder = SentenceTransformerEncoder(
                str(self.manifest["embedding_model"]),
                revision=str(self.manifest["embedding_revision"]),
                local_files_only=True,
            )
        else:
            self.encoder = None

    def inspect(self) -> dict[str, Any]:
        return {
            "snapshot": self.index_snapshot,
            "manifest": dict(self.manifest),
            "metadata_rows": len(self._rows),
        }

    def query(self, request: OperationalHistoryRequest) -> OperationalHistoryResult:
        if not isinstance(request, OperationalHistoryRequest):
            raise TypeError("history query expects OperationalHistoryRequest")
        identity_rows = [
            row
            for row in self._rows
            if row["plant_id"] == request.plant_id
            and row["configuration_fingerprint"] == request.configuration_fingerprint
            and row["operating_region_fingerprint"]
            == request.operating_region_fingerprint
        ]
        if not identity_rows:
            return OperationalHistoryResult(
                index_snapshot=self.index_snapshot,
                request_identity=request.identity(),
                empty_reason="identity_not_found",
            )
        as_of = request.as_of_datetime()
        superseded = {
            superseded_id
            for row in identity_rows
            if _parse_timestamp(str(row["captured_at"])) <= as_of
            and _parse_timestamp(str(row["valid_from"])) <= as_of
            for superseded_id in json.loads(str(row["supersedes_json"]))
        }
        active = [
            row
            for row in identity_rows
            if row["record_id"] not in superseded
            and _parse_timestamp(str(row["captured_at"])) <= as_of
            and _parse_timestamp(str(row["valid_from"])) <= as_of
            and (
                row["valid_until"] is None
                or _parse_timestamp(str(row["valid_until"])) >= as_of
            )
            and (not request.record_types or row["record_type"] in request.record_types)
        ]
        if not active:
            return OperationalHistoryResult(
                index_snapshot=self.index_snapshot,
                request_identity=request.identity(),
                empty_reason="no_active_records",
            )
        scores: dict[int, float] = {}
        if request.query_text.strip():
            if self.encoder is None:
                raise ValueError("history query text requires the snapshot encoder")
            query_vector = _encode(
                self.encoder, [request.query_text.strip()], is_query=True
            )[0]
            vector_norm = np.linalg.norm(query_vector)
            for row in active:
                index = int(row["id"]) - 1
                candidate = self._vectors[index]
                denominator = np.linalg.norm(candidate) * vector_norm
                dense = (
                    float(np.dot(candidate, query_vector) / denominator)
                    if denominator
                    else 0.0
                )
                lexical = _lexical_score(request.query_text, str(row["summary"]))
                scores[index] = dense + 0.1 * lexical
            active.sort(
                key=lambda row: (
                    -scores[int(row["id"]) - 1],
                    -_parse_timestamp(str(row["valid_from"])).timestamp(),
                    str(row["record_id"]),
                )
            )
        else:
            active.sort(
                key=lambda row: (
                    -_parse_timestamp(str(row["valid_from"])).timestamp(),
                    -_parse_timestamp(str(row["captured_at"])).timestamp(),
                    str(row["record_id"]),
                )
            )
        matches = tuple(
            OperationalHistoryMatch(
                record_id=str(row["record_id"]),
                record_type=str(row["record_type"]),
                record_version=str(row["record_version"]),
                schema_version=str(row["record_schema_version"]),
                plant_id=str(row["plant_id"]),
                configuration_fingerprint=str(row["configuration_fingerprint"]),
                operating_region_fingerprint=str(row["operating_region_fingerprint"]),
                captured_at=str(row["captured_at"]),
                valid_from=str(row["valid_from"]),
                valid_until=(
                    str(row["valid_until"]) if row["valid_until"] is not None else None
                ),
                summary=str(row["summary"]),
                source_refs=tuple(json.loads(str(row["source_refs_json"]))),
                session_refs=tuple(json.loads(str(row["session_refs_json"]))),
                payload_sha256=str(row["payload_sha256"]),
                score=scores.get(int(row["id"]) - 1),
            )
            for row in active[: int(request.limit)]
        )
        return OperationalHistoryResult(
            index_snapshot=self.index_snapshot,
            request_identity=request.identity(),
            records=matches,
        )


def build_history_index(
    source_file: str | Path,
    index_dir: str | Path,
    *,
    encoder: Any | None = None,
) -> OperationalHistoryIndex:
    """Validate source records and create a new immutable history snapshot."""

    source = Path(source_file)
    records, source_hash = _validated_records(source)
    if encoder is None:
        from cfdc.rag import SentenceTransformerEncoder

        encoder = SentenceTransformerEncoder(local_files_only=True)
    vectors = _encode(encoder, [record.summary for record in records], is_query=False)
    root = Path(index_dir)
    root.mkdir(parents=True, exist_ok=True)
    snapshot_name = f"snapshot-{uuid4().hex}"
    snapshot = root / snapshot_name
    snapshot.mkdir()
    np.save(snapshot / "vectors.npy", vectors)
    with sqlite3.connect(snapshot / "metadata.sqlite3") as connection:
        connection.execute(
            "CREATE TABLE records ("
            "id INTEGER PRIMARY KEY, record_id TEXT NOT NULL UNIQUE, "
            "record_type TEXT NOT NULL, record_version TEXT NOT NULL, "
            "record_schema_version TEXT NOT NULL, plant_id TEXT NOT NULL, "
            "configuration_fingerprint TEXT NOT NULL, "
            "operating_region_fingerprint TEXT NOT NULL, captured_at TEXT NOT NULL, "
            "valid_from TEXT NOT NULL, valid_until TEXT, supersedes_json TEXT NOT NULL, "
            "source_refs_json TEXT NOT NULL, session_refs_json TEXT NOT NULL, "
            "payload_sha256 TEXT NOT NULL, summary TEXT NOT NULL)"
        )
        connection.execute(
            "CREATE VIRTUAL TABLE records_fts USING fts5(record_id UNINDEXED, summary)"
        )
        for index, record in enumerate(records, 1):
            connection.execute(
                "INSERT INTO records VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    index,
                    record.record_id,
                    record.record_type,
                    record.record_version,
                    record.schema_version,
                    record.plant_id,
                    record.configuration_fingerprint,
                    record.operating_region_fingerprint,
                    record.captured_at,
                    record.valid_from,
                    record.valid_until,
                    json.dumps(record.supersedes),
                    json.dumps(record.source_refs),
                    json.dumps(record.session_refs),
                    record.payload_sha256,
                    record.summary,
                ),
            )
            connection.execute(
                "INSERT INTO records_fts(rowid,record_id,summary) VALUES(?,?,?)",
                (index, record.record_id, record.summary),
            )
        connection.commit()
    manifest = {
        "schema_version": HISTORY_SCHEMA_VERSION,
        "source_schema_version": SOURCE_SCHEMA_VERSION,
        "record_schema_version": RECORD_SCHEMA_VERSION,
        "record_count": len(records),
        "record_types": dict(
            sorted(Counter(record.record_type for record in records).items())
        ),
        "identity_fields": [
            "plant_id",
            "configuration_fingerprint",
            "operating_region_fingerprint",
        ],
        "embedding_model": str(getattr(encoder, "model_name", type(encoder).__name__)),
        "embedding_revision": str(
            getattr(encoder, "model_revision", getattr(encoder, "revision", "unknown"))
        ),
        "embedding_dimension": int(vectors.shape[1]),
        "payload_stored": False,
        "source_sha256": source_hash,
        "metadata_checksum": _hash_file(snapshot / "metadata.sqlite3"),
        "vector_checksum": _hash_file(snapshot / "vectors.npy"),
    }
    (snapshot / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2),
        encoding="utf-8",
    )
    current = root / "CURRENT"
    temporary_current = root / f".CURRENT-{uuid4().hex}"
    temporary_current.write_text(snapshot_name, encoding="utf-8")
    temporary_current.replace(current)
    return OperationalHistoryIndex(snapshot, encoder=encoder)


def load_history_index(
    index_dir: str | Path,
    *,
    snapshot_name: str | None = None,
    encoder: Any | None = None,
    load_encoder: bool = True,
) -> OperationalHistoryIndex:
    root = Path(index_dir)
    if snapshot_name is None:
        try:
            snapshot_name = (root / "CURRENT").read_text(encoding="utf-8").strip()
        except (OSError, UnicodeError) as exc:
            raise ValueError(
                f"unable to resolve history CURRENT snapshot: {exc}"
            ) from exc
    if not re.fullmatch(r"snapshot-[a-f0-9]{32}", snapshot_name or ""):
        raise ValueError("invalid operational-history snapshot name")
    snapshot = root / str(snapshot_name)
    if not snapshot.is_dir():
        raise ValueError("operational-history snapshot does not exist")
    return OperationalHistoryIndex(
        snapshot,
        encoder=encoder,
        load_encoder=load_encoder,
    )
