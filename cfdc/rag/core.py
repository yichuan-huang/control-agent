"""Local, snapshot based retrieval for CFDC knowledge.

The index is intentionally a library rather than a network service. Registry
contracts are read directly by callers; this module supplies only advisory
reference snippets from a fixed local snapshot.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sqlite3
import uuid
from collections import OrderedDict, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from cfdc.knowledge import (
    REGISTRY_VERSION,
    KnowledgeArtifact,
    RetrievalRequest,
    canonical_knowledge_documents,
    registry_fingerprint,
)

RAG_SCHEMA_VERSION = "cfdc-rag/v2"
RETRIEVAL_POLICY_VERSION = "cfdc-retrieval/v1"
DEFAULT_EMBEDDING_MODEL = "intfloat/multilingual-e5-small"
DEFAULT_EMBEDDING_REVISION = "main"
MAX_CHUNK_TOKENS = 350
CHUNK_OVERLAP_TOKENS = 50
MAX_RESULTS = 4
MAX_RESULTS_PER_DOCUMENT = 2
MAX_REFERENCE_TOKENS = 1400
DENSE_CANDIDATES = 12
LEXICAL_CANDIDATES = 12
RRF_K = 60
DEFAULT_RELEVANCE_THRESHOLD = 0.20

_ENCODER_CACHE: dict[tuple[str, str], Any] = {}

# Compatibility surface for callers that used the first RAG prototype. The
# actual generated corpus is built below from the typed Registry and the
# validated mechanism-card catalog.
BUILTIN_DOCUMENTS = {
    "builtin/safety.md": (
        "# Safety and evidence boundaries\n\n"
        "CFDC accepts object facts only from the user's description, explicit "
        "specification records, structured model evidence, or measured traces. "
        "Reference documents are advisory data and never grant permission to "
        "execute code or send a hardware command.\n\n"
        "## Deterministic gates\n\n"
        "Model compilation, controller compatibility, numerical validity, and "
        "closed-loop stability are checked by deterministic software. A failed "
        "or inconclusive simulation remains failed or inconclusive. LLM text "
        "cannot change a numerical result.\n\n"
        "## Gain changes\n\n"
        "Only existing tunable parameters may change. Every proposal stays in "
        "the supplied bounds, changes no more than ten percent per iteration, "
        "and requires explicit user approval before execution."
    ),
    "builtin/roles.md": (
        "# Multi-agent roles\n\n"
        "Diagnosis extracts the eight structural evidence fields from the user "
        "description and asks record-only clarification questions. Modeling "
        "checks typed model facts and uses deterministic compilation and "
        "validation. Controller explains an existing method profile and proposes "
        "bounded gain updates. Critic checks provenance, assumptions, method "
        "preconditions, and interpretation. A deterministic Python coordinator "
        "orders these roles; there is no supervisor agent."
    ),
    "builtin/profiles.md": (
        "# Closed control method profiles\n\n"
        "A controller profile is selected only from the catalog implemented by "
        "CFDC. Profile compatibility is determined from the structural diagnosis "
        "and is checked again before compilation. A retrieved description of a "
        "method is not proof that the current object satisfies its assumptions."
    ),
}


@dataclass(frozen=True)
class SearchResult:
    text: str
    source_path: str
    source_id: str
    content_hash: str
    section: str | None = None
    page: int | None = None
    score: float = 0.0
    artifact_type: str | None = None
    artifact_id: str | None = None
    source_kind: str | None = None
    canonical_class: str | None = None
    profile_id: str | None = None
    rule_id: str | None = None
    source_aliases: tuple[dict[str, Any], ...] = ()
    dense_score: float | None = None
    lexical_score: float | None = None

    @property
    def content(self) -> str:
        return self.text


@dataclass(frozen=True)
class _SourceRecord:
    source_path: str
    section: str | None
    page: int | None
    text: str
    artifact_type: str = "external_document"
    artifact_id: str | None = None
    source_kind: str = "external"
    role: tuple[str, ...] = ()
    stage: tuple[str, ...] = ()
    canonical_class: str | None = None
    profile_id: str | None = None
    rule_id: str | None = None
    char_start: int | None = None
    char_end: int | None = None


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _hash_bytes(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _fallback_token_spans(text: str) -> list[tuple[int, int]]:
    return [
        (match.start(), match.end())
        for match in re.finditer(
            r"[\u4e00-\u9fff]|[A-Za-z0-9_]+|[^\w\s]", text, re.UNICODE
        )
    ]


def _tokenizer_for_encoder(encoder: Any | None) -> Any | None:
    if encoder is None:
        return None
    tokenizer = getattr(encoder, "tokenizer", None)
    if tokenizer is not None:
        return tokenizer
    model = getattr(encoder, "model", None)
    return getattr(model, "tokenizer", None)


def _model_token_spans(text: str, tokenizer: Any | None) -> list[tuple[int, int]]:
    if tokenizer is None:
        return []
    try:
        encoded = tokenizer(
            text,
            add_special_tokens=False,
            return_offsets_mapping=True,
            truncation=False,
        )
        offsets = encoded.get("offset_mapping") if hasattr(encoded, "get") else None
        if offsets is None:
            return []
        if hasattr(offsets, "tolist"):
            offsets = offsets.tolist()
        if (
            offsets
            and isinstance(offsets[0], list)
            and offsets[0]
            and isinstance(offsets[0][0], list)
        ):
            offsets = offsets[0]
        return [
            (int(start), int(end)) for start, end in offsets if int(end) > int(start)
        ]
    except (AttributeError, IndexError, KeyError, TypeError, ValueError):
        return []


def _text_chunks_with_offsets(
    text: str,
    *,
    tokenizer: Any | None = None,
) -> list[tuple[str, int, int]]:
    if not text or not text.strip():
        return []
    spans = _model_token_spans(text, tokenizer) or _fallback_token_spans(text)
    if not spans:
        return []
    chunks: list[tuple[str, int, int]] = []
    start = 0
    while start < len(spans):
        end = min(start + MAX_CHUNK_TOKENS, len(spans))
        char_start, char_end = spans[start][0], spans[end - 1][1]
        value = text[char_start:char_end]
        if value.strip():
            chunks.append((value, char_start, char_end))
        if end >= len(spans):
            break
        start = max(start + 1, end - CHUNK_OVERLAP_TOKENS)
    return chunks


def _bounded_chunks(text: str, tokenizer: Any | None = None) -> list[str]:
    """Return chunks bounded by the model tokenizer when one is available."""

    return [
        chunk
        for chunk, _start, _end in _text_chunks_with_offsets(text, tokenizer=tokenizer)
    ]


def _markdown_segments(text: str) -> Iterable[tuple[str | None, int, int]]:
    heading_stack: list[tuple[int, str]] = []
    paragraph_start: int | None = None
    paragraph_end: int | None = None
    offset = 0

    def flush() -> tuple[str | None, int, int] | None:
        nonlocal paragraph_start, paragraph_end
        if paragraph_start is None or paragraph_end is None:
            return None
        result = (
            " > ".join(item[1] for item in heading_stack) or None,
            paragraph_start,
            paragraph_end,
        )
        paragraph_start = None
        paragraph_end = None
        return result

    for line in text.splitlines(keepends=True):
        without_newline = line.rstrip("\r\n")
        match = re.match(r"^(#{1,6})\s+(.*?)\s*$", without_newline)
        if match:
            previous = flush()
            if previous is not None:
                yield previous
            level = len(match.group(1))
            title = match.group(2).strip()
            while heading_stack and heading_stack[-1][0] >= level:
                heading_stack.pop()
            if title:
                heading_stack.append((level, title))
        elif without_newline.strip():
            if paragraph_start is None:
                paragraph_start = offset
            paragraph_end = offset + len(line)
        else:
            previous = flush()
            if previous is not None:
                yield previous
        offset += len(line)
    previous = flush()
    if previous is not None:
        yield previous


def _markdown_chunks(path: str, text: str, tokenizer: Any | None = None):
    """Yield ``(heading path, chunk)`` pairs while preserving source text."""

    del path
    for section, start, end in _markdown_segments(text):
        for chunk, _local_start, _local_end in _text_chunks_with_offsets(
            text[start:end], tokenizer=tokenizer
        ):
            yield section, chunk


def _builtin_artifacts() -> tuple[KnowledgeArtifact, ...]:
    documents = [
        KnowledgeArtifact(
            artifact_id=path.removeprefix("builtin/").removesuffix(".md"),
            artifact_type="policy",
            title=path,
            text=text,
            role=("diagnosis", "modeling", "controller", "critic"),
            stage=("all",),
        )
        for path, text in BUILTIN_DOCUMENTS.items()
    ]
    documents.extend(canonical_knowledge_documents())

    from cfdc.diagnosis.mechanism_cards import load_mechanism_card_catalog

    catalog = load_mechanism_card_catalog()
    cards = catalog.get("cards")
    if not isinstance(cards, list) or len(cards) != 14:
        raise ValueError("mechanism-card catalog must contain all 14 cards")
    role_map = {
        "feature_source": {"diagnosis", "modeling"},
        "interaction_structure": {"diagnosis", "modeling"},
        "controller_structure": {"controller"},
        "route_warning": {"controller", "critic"},
        "operating_region_warning": {"modeling", "controller", "critic"},
        "constraint_boundary": {"controller", "critic"},
        "measurement_warning": {"diagnosis", "modeling", "critic"},
    }
    for card in cards:
        card_id = card.get("card_id")
        if not isinstance(card_id, str) or not card_id:
            raise ValueError("mechanism-card catalog contains an invalid card ID")
        text = (
            f"Mechanism card ID: {card_id}\n"
            f"Layer: {card.get('layer')}\n"
            f"Control meaning: {card.get('control_meaning')}\n"
            "When to consider: "
            f"{'; '.join(str(item) for item in card.get('when_to_consider', []))}\n"
            f"Typical next core features: {', '.join(card.get('typical_next_core_features', []))}\n"
            f"Common non-core items: {', '.join(card.get('common_non_core_items', []))}\n"
            f"Minimal probe: {card.get('minimal_probe')}\n"
            f"Controller implication: {card.get('controller_implication')}\n"
            "This card is an advisory mechanism label. It does not add a simulator, controller, or tool capability."
        )
        documents.append(
            KnowledgeArtifact(
                artifact_id=card_id,
                artifact_type="mechanism_card",
                title=card_id,
                text=text,
                role=tuple(
                    sorted(
                        {
                            agent_role
                            for card_role in card.get("default_roles", ())
                            for agent_role in role_map.get(card_role, ())
                        }
                    )
                ),
                stage=("diagnosis", "model", "controller", "review"),
            )
        )

    from cfdc.workflow import default_capability_catalog

    documents.append(
        KnowledgeArtifact(
            artifact_id="capability_catalog",
            artifact_type="capability",
            title="Registered deterministic capabilities",
            text=(
                "Capability catalog is generated from the installed implementation. "
                "Only listed primitives, extractors, controller templates, and tracking "
                "implementations may be executed.\n"
                + default_capability_catalog().model_dump_json(indent=2)
            ),
            role=("modeling", "controller", "critic"),
            stage=("model", "controller", "review"),
        )
    )
    return tuple(documents)


def _builtin_documents_with_catalogs() -> dict[str, str]:
    """Return independent generated builtin documents for compatibility/debugging."""

    return {
        f"builtin/{artifact.artifact_type}/{artifact.artifact_id}.md": artifact.text
        for artifact in _builtin_artifacts()
    }


def _read_sources(
    source_dir: Path | None,
    include_builtin: bool,
    *,
    tokenizer: Any | None = None,
) -> list[_SourceRecord]:
    records: list[_SourceRecord] = []
    if include_builtin:
        for artifact in _builtin_artifacts():
            for section, start, end in _markdown_segments(artifact.text):
                for chunk, local_start, local_end in _text_chunks_with_offsets(
                    artifact.text[start:end], tokenizer=tokenizer
                ):
                    records.append(
                        _SourceRecord(
                            source_path=f"builtin/{artifact.artifact_type}/{artifact.artifact_id}.md",
                            section=section or artifact.title,
                            page=None,
                            text=chunk,
                            artifact_type=artifact.artifact_type,
                            artifact_id=artifact.artifact_id,
                            source_kind=artifact.source_kind,
                            role=artifact.role,
                            stage=artifact.stage,
                            canonical_class=artifact.canonical_class,
                            profile_id=artifact.profile_id,
                            rule_id=artifact.rule_id,
                            char_start=start + local_start,
                            char_end=start + local_end,
                        )
                    )

    if source_dir is None:
        return records
    root = source_dir.resolve()
    for path in sorted(source_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {
            ".md",
            ".markdown",
            ".pdf",
        }:
            continue
        resolved = path.resolve()
        if not resolved.is_relative_to(root):
            raise ValueError(f"source path escapes source directory: {path}")
        relative = path.relative_to(source_dir).as_posix()
        if path.suffix.lower() in {".md", ".markdown"}:
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as exc:
                raise ValueError(
                    f"unable to read Markdown source {relative}: {exc}"
                ) from exc
            for section, start, end in _markdown_segments(text):
                for chunk, local_start, local_end in _text_chunks_with_offsets(
                    text[start:end], tokenizer=tokenizer
                ):
                    records.append(
                        _SourceRecord(
                            source_path=relative,
                            section=section,
                            page=None,
                            text=chunk,
                            char_start=start + local_start,
                            char_end=start + local_end,
                        )
                    )
            continue
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise ValueError(
                "PDF indexing requires the optional 'rag' dependency (pypdf)"
            ) from exc
        try:
            reader = PdfReader(str(path), strict=False)
            if reader.is_encrypted:
                raise ValueError("PDF is encrypted")
            page_records: list[_SourceRecord] = []
            for page_number, page in enumerate(reader.pages, 1):
                page_text = page.extract_text() or ""
                page_records.extend(
                    _SourceRecord(
                        source_path=relative,
                        section=None,
                        page=page_number,
                        text=chunk,
                        char_start=start,
                        char_end=end,
                    )
                    for chunk, start, end in _text_chunks_with_offsets(
                        page_text, tokenizer=tokenizer
                    )
                )
            if not page_records:
                raise ValueError("PDF has no extractable text layer")
            records.extend(page_records)
        except ValueError:
            raise
        except Exception as exc:
            raise ValueError(f"unable to parse PDF source {relative}: {exc}") from exc
    return records


def _encode(encoder: Any, texts: Iterable[str], *, is_query: bool):
    method = encoder.encode if hasattr(encoder, "encode") else encoder
    try:
        return method(texts, is_query=is_query)
    except TypeError as exc:
        if "is_query" not in str(exc):
            raise
        return method(texts)


class SentenceTransformerEncoder:
    """Lazy local CPU encoder using E5 query/passage prefixes."""

    def __init__(
        self,
        model_name: str = DEFAULT_EMBEDDING_MODEL,
        *,
        revision: str | None = None,
        local_files_only: bool = False,
    ):
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise ValueError(
                "local RAG indexing/search requires the optional 'rag' dependencies; "
                "run `uv sync --extra rag`"
            ) from exc
        self.model_name = model_name
        self.model_revision = revision or DEFAULT_EMBEDDING_REVISION
        kwargs: dict[str, Any] = {
            "device": "cpu",
            "trust_remote_code": False,
            "revision": self.model_revision,
        }
        if local_files_only:
            kwargs["local_files_only"] = True
        # Runtime loading is intentionally local-only.  A missing cached model
        # is an explicit infrastructure error instead of an implicit download.
        self.model = SentenceTransformer(model_name, **kwargs)
        self.tokenizer = getattr(self.model, "tokenizer", None)

    def encode(self, texts, *, is_query: bool = False):
        values = [texts] if isinstance(texts, str) else list(texts)
        prefix = "query: " if is_query else "passage: "
        return self.model.encode(
            [prefix + value for value in values],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )


def _cached_encoder(model_name: str, revision: str) -> Any:
    key = (model_name, revision)
    cached = _ENCODER_CACHE.get(key)
    if cached is None:
        cached = SentenceTransformerEncoder(
            model_name,
            revision=revision,
            local_files_only=True,
        )
        _ENCODER_CACHE[key] = cached
        while len(_ENCODER_CACHE) > 4:
            _ENCODER_CACHE.pop(next(iter(_ENCODER_CACHE)))
    return cached


def _encoder_name(encoder: Any) -> str:
    return str(getattr(encoder, "model_name", DEFAULT_EMBEDDING_MODEL))


def _encoder_version(encoder: Any) -> str:
    return str(
        getattr(
            encoder,
            "model_revision",
            getattr(encoder, "revision", DEFAULT_EMBEDDING_REVISION),
        )
    )


def _tokenizer_version(encoder: Any) -> str:
    explicit = getattr(encoder, "tokenizer_revision", None)
    if explicit:
        return str(explicit)
    tokenizer = _tokenizer_for_encoder(encoder)
    revision = getattr(tokenizer, "revision", None) if tokenizer is not None else None
    return str(revision or _encoder_version(encoder))


def _row_roles(row: dict[str, Any], key: str) -> tuple[str, ...]:
    value = row.get(key)
    if isinstance(value, str):
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError:
            decoded = []
        return tuple(str(item) for item in decoded) if isinstance(decoded, list) else ()
    return (
        tuple(str(item) for item in value) if isinstance(value, (list, tuple)) else ()
    )


def _fts_query(query: str) -> str:
    terms = re.findall(r"[\u4e00-\u9fff]|[A-Za-z0-9_]+", query.casefold())
    return " OR ".join(f'"{term.replace(chr(34), "")}"' for term in terms[:64])


def _python_lexical_score(query: str, text: str) -> float:
    query_terms = set(re.findall(r"[\u4e00-\u9fff]|[A-Za-z0-9_]+", query.casefold()))
    text_terms = set(re.findall(r"[\u4e00-\u9fff]|[A-Za-z0-9_]+", text.casefold()))
    if not query_terms:
        return 0.0
    return len(query_terms & text_terms) / len(query_terms)


class RAGIndex:
    def __init__(self, snapshot: Path, encoder=None, *, load_encoder: bool = True):
        self.snapshot = snapshot
        self.index_snapshot = snapshot.name
        self._db = snapshot / "metadata.sqlite3"
        self._manifest_path = snapshot / "manifest.json"
        if not self._manifest_path.is_file():
            raise ValueError(
                f"corrupt RAG index snapshot (manifest missing): {snapshot}"
            )
        try:
            self.manifest = json.loads(self._manifest_path.read_text(encoding="utf-8"))
            if self.manifest.get("schema_version") != RAG_SCHEMA_VERSION:
                raise ValueError(
                    "unsupported RAG index schema version; rebuild explicitly"
                )
            if self.manifest.get("registry_version") != REGISTRY_VERSION:
                raise ValueError(
                    "RAG index Registry version is incompatible; rebuild explicitly"
                )
            if self.manifest.get("registry_fingerprint") != registry_fingerprint():
                raise ValueError(
                    "RAG index Registry fingerprint is incompatible; rebuild explicitly"
                )
            expected_vectors_checksum = self.manifest.get("vector_checksum")
            expected_metadata_checksum = self.manifest.get("metadata_checksum")
            if (
                not isinstance(expected_vectors_checksum, str)
                or not expected_vectors_checksum
            ):
                raise ValueError("RAG vector checksum is missing from the manifest")
            if (
                not isinstance(expected_metadata_checksum, str)
                or not expected_metadata_checksum
            ):
                raise ValueError("RAG metadata checksum is missing from the manifest")
            if _hash_bytes(self.snapshot / "vectors.npy") != expected_vectors_checksum:
                raise ValueError("RAG vector checksum does not match its manifest")
            if (
                _hash_bytes(self.snapshot / "metadata.sqlite3")
                != expected_metadata_checksum
            ):
                raise ValueError("RAG metadata checksum does not match its manifest")
            self._vectors = np.load(snapshot / "vectors.npy", allow_pickle=False)
        except (
            OSError,
            EOFError,
            UnicodeError,
            ValueError,
            TypeError,
            json.JSONDecodeError,
        ) as exc:
            if isinstance(exc, ValueError) and "incompatible" in str(exc):
                raise
            raise ValueError(f"corrupt RAG index snapshot: {snapshot}") from exc
        if self._vectors.ndim != 2 or not np.isfinite(self._vectors).all():
            raise ValueError("RAG vectors must be a finite two-dimensional array")
        try:
            expected_dimension = int(self.manifest.get("embedding_dimension", -1))
        except (TypeError, ValueError) as exc:
            raise ValueError("corrupt RAG index embedding dimension") from exc
        if expected_dimension != self._vectors.shape[1]:
            raise ValueError("RAG vector dimension does not match its manifest")
        self.encoder = encoder
        if self.encoder is None and load_encoder:
            self.encoder = _cached_encoder(
                str(self.manifest.get("embedding_model", DEFAULT_EMBEDDING_MODEL)),
                str(
                    self.manifest.get(
                        "embedding_model_revision", DEFAULT_EMBEDDING_REVISION
                    )
                ),
            )
        self._rows = self._load_metadata()
        if len(self._rows) != len(self._vectors):
            raise ValueError("RAG metadata/vector row count mismatch")
        self._query_cache: OrderedDict[str, tuple[SearchResult, ...]] = OrderedDict()

    def _load_metadata(self) -> list[dict[str, Any]]:
        try:
            with sqlite3.connect(self._db) as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute("SELECT * FROM chunks ORDER BY id").fetchall()
                columns = {
                    str(item[1])
                    for item in conn.execute("PRAGMA table_info(chunks)").fetchall()
                }
                fts = conn.execute(
                    "SELECT 1 FROM sqlite_master WHERE type='table' AND name='chunks_fts'"
                ).fetchone()
        except sqlite3.Error as exc:
            raise ValueError(f"corrupt RAG metadata database: {self._db}") from exc
        if fts is None:
            raise ValueError("RAG index is missing its FTS5 table; rebuild explicitly")
        required_columns = {
            "id",
            "text",
            "source_path",
            "source_id",
            "content_hash",
            "artifact_type",
            "source_kind",
            "roles_json",
            "stages_json",
        }
        if not required_columns.issubset(columns):
            raise ValueError("RAG metadata database is missing required columns")
        return [dict(row) for row in rows]

    def metadata(self):
        return [dict(row) for row in self._rows]

    def _allowed_rows(self, request: RetrievalRequest) -> list[int]:
        role = str(request.role).casefold()
        # The legacy ``search(query)`` surface historically searched the whole
        # corpus.  Keep that compatibility behavior while structured callers
        # receive role/stage filtering below.
        unrestricted_role = role in {"", "all"}
        if unrestricted_role:
            role = ""
        stage = str(request.stage).casefold() if request.stage else None
        allowed: list[int] = []
        for index, row in enumerate(self._rows):
            if row.get("source_kind") == "external":
                allowed.append(index)
                continue
            roles = {item.casefold() for item in _row_roles(row, "roles_json")}
            stages = {item.casefold() for item in _row_roles(row, "stages_json")}
            if roles and role and role not in roles:
                continue
            if stage and stages and stage not in stages and "all" not in stages:
                continue
            if request.canonical_class and row.get("canonical_class") not in {
                None,
                request.canonical_class,
            }:
                continue
            if request.profile_id and row.get("profile_id") not in {
                None,
                request.profile_id,
            }:
                continue
            allowed.append(index)
        return allowed

    def _lexical_candidates(
        self, query: str, allowed: set[int]
    ) -> list[tuple[int, float]]:
        fts_query = _fts_query(query)
        candidates: list[tuple[int, float]] = []
        if fts_query:
            try:
                with sqlite3.connect(self._db) as conn:
                    rows = conn.execute(
                        "SELECT rowid, bm25(chunks_fts) FROM chunks_fts "
                        "WHERE chunks_fts MATCH ? ORDER BY bm25(chunks_fts) LIMIT ?",
                        # Fetch all matching row IDs before applying the
                        # structured allow-list so disallowed builtin entries
                        # cannot consume the twelve lexical candidate slots.
                        (fts_query, max(LEXICAL_CANDIDATES, len(self._rows))),
                    ).fetchall()
                for row_id, _bm25_score in rows:
                    index = int(row_id) - 1
                    if index in allowed:
                        # SQLite's BM25 values are only meaningful for ranking
                        # within one query.  Store a bounded rank score so the
                        # independent relevance threshold is meaningful.
                        candidates.append((index, 1.0 / (len(candidates) + 1)))
                        if len(candidates) >= LEXICAL_CANDIDATES:
                            break
            except sqlite3.Error as exc:
                raise ValueError("RAG FTS5 query failed") from exc
        if candidates:
            return candidates
        fallback = [
            (index, _python_lexical_score(query, self._rows[index]["text"]))
            for index in allowed
        ]
        return sorted(
            ((index, score) for index, score in fallback if score > 0.0),
            key=lambda item: (-item[1], self._rows[item[0]]["source_id"]),
        )[:LEXICAL_CANDIDATES]

    def _result(
        self,
        index: int,
        *,
        score: float,
        dense_score: float | None,
        lexical_score: float | None,
    ) -> SearchResult:
        row = self._rows[index]
        aliases: tuple[dict[str, Any], ...] = ()
        raw_aliases = row.get("source_aliases")
        if isinstance(raw_aliases, str):
            try:
                decoded = json.loads(raw_aliases)
                if isinstance(decoded, list):
                    aliases = tuple(item for item in decoded if isinstance(item, dict))
            except json.JSONDecodeError:
                aliases = ()
        return SearchResult(
            text=str(row["text"]),
            source_path=str(row["source_path"]),
            source_id=str(row["source_id"]),
            content_hash=str(row["content_hash"]),
            section=row.get("section"),
            page=row.get("page"),
            score=float(score),
            artifact_type=row.get("artifact_type"),
            artifact_id=row.get("artifact_id"),
            source_kind=row.get("source_kind"),
            canonical_class=row.get("canonical_class"),
            profile_id=row.get("profile_id"),
            rule_id=row.get("rule_id"),
            source_aliases=aliases,
            dense_score=dense_score,
            lexical_score=lexical_score,
        )

    def retrieve(
        self, request: RetrievalRequest, limit: int = MAX_RESULTS
    ) -> list[SearchResult]:
        if not isinstance(request, RetrievalRequest):
            raise TypeError("RAG retrieve expects a RetrievalRequest")
        limit = min(max(int(limit), 0), MAX_RESULTS)
        if not limit:
            return []
        query = request.query_text().strip()
        if not query:
            return []
        cache_key = _hash(
            json.dumps(
                {
                    "snapshot": self.index_snapshot,
                    "role": request.role,
                    "operation": request.operation,
                    "class": request.canonical_class,
                    "profile": request.profile_id,
                    "stage": request.stage,
                    "missing": request.missing_fields,
                    "summary": request.summary,
                    "limit": limit,
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        cached = self._query_cache.get(cache_key)
        if cached is not None:
            self._query_cache.move_to_end(cache_key)
            return list(cached)
        allowed = set(self._allowed_rows(request))
        if not allowed:
            return []
        if self.encoder is None:
            raise ValueError(
                "RAG encoder is not loaded; use load_index(..., load_encoder=True)"
            )
        vector = np.asarray(
            _encode(self.encoder, [query], is_query=True)[0], dtype=float
        )
        if vector.ndim != 1 or vector.shape[0] != self._vectors.shape[1]:
            raise ValueError("query embedding dimension does not match RAG index")
        norms = np.linalg.norm(self._vectors, axis=1) * np.linalg.norm(vector)
        scores = np.divide(
            self._vectors @ vector,
            norms,
            out=np.zeros(len(norms), dtype=float),
            where=norms != 0,
        )
        dense_order = sorted(
            ((index, float(scores[index])) for index in allowed),
            key=lambda item: (-item[1], self._rows[item[0]]["source_id"]),
        )[:DENSE_CANDIDATES]
        dense_rank = {
            index: rank for rank, (index, _score) in enumerate(dense_order, 1)
        }
        dense_scores = {index: score for index, score in dense_order}
        lexical_order = self._lexical_candidates(query, allowed)
        lexical_rank = {
            index: rank for rank, (index, _score) in enumerate(lexical_order, 1)
        }
        lexical_scores = {index: score for index, score in lexical_order}
        exact_ids = {
            token for token in re.findall(r"[A-Za-z0-9_.-]+", query.casefold()) if token
        }
        candidates: list[tuple[int, float]] = []
        threshold = float(
            self.manifest.get("retrieval_policy", {}).get(
                "relevance_threshold", DEFAULT_RELEVANCE_THRESHOLD
            )
        )
        for index in set(dense_rank) | set(lexical_rank):
            row = self._rows[index]
            exact = any(
                token in exact_ids
                for token in (
                    str(row.get("artifact_id") or "").casefold(),
                    str(row.get("profile_id") or "").casefold(),
                    str(row.get("rule_id") or "").casefold(),
                )
                if token
            )
            relevance = max(
                dense_scores.get(index, -1.0),
                lexical_scores.get(index, 0.0),
            )
            if not exact and relevance < threshold:
                continue
            rrf = 0.0
            if index in dense_rank:
                rrf += 1.0 / (RRF_K + dense_rank[index])
            if index in lexical_rank:
                rrf += 1.0 / (RRF_K + lexical_rank[index])
            candidates.append((index, rrf))
        candidates.sort(key=lambda item: (-item[1], self._rows[item[0]]["source_id"]))
        selected: list[SearchResult] = []
        per_document: defaultdict[str, int] = defaultdict(int)
        token_budget = MAX_REFERENCE_TOKENS
        max_per_document = (
            MAX_RESULTS if request.operation == "search" else MAX_RESULTS_PER_DOCUMENT
        )
        for index, rrf in candidates:
            row = self._rows[index]
            document_key = str(row.get("source_path") or row["source_id"])
            if per_document[document_key] >= max_per_document:
                continue
            token_count = len(_fallback_token_spans(str(row["text"])))
            if token_count > token_budget:
                continue
            selected.append(
                self._result(
                    index,
                    score=rrf,
                    dense_score=dense_scores.get(index),
                    lexical_score=lexical_scores.get(index),
                )
            )
            per_document[document_key] += 1
            token_budget -= token_count
            if len(selected) >= limit:
                break
        self._query_cache[cache_key] = tuple(selected)
        self._query_cache.move_to_end(cache_key)
        while len(self._query_cache) > 128:
            self._query_cache.popitem(last=False)
        return selected

    def search(self, query: str, limit: int = MAX_RESULTS):
        """Compatibility wrapper around structured retrieval."""

        return self.retrieve(
            RetrievalRequest(role="legacy", operation="search", summary=str(query)),
            limit=limit,
        )

    def inspect(self) -> dict[str, Any]:
        artifact_types = sorted({str(row.get("artifact_type")) for row in self._rows})
        return {
            "snapshot": self.index_snapshot,
            "manifest": dict(self.manifest),
            "metadata_rows": len(self._rows),
            "artifact_types": {
                key: sum(1 for row in self._rows if row.get("artifact_type") == key)
                for key in artifact_types
            },
        }


def calibrate_relevance_threshold(
    scores: Iterable[float],
    relevant: Iterable[bool],
    *,
    max_false_positive_rate: float = 0.05,
) -> float:
    """Choose the strictest threshold with maximum recall under the FP limit."""

    values = [float(value) for value in scores]
    labels = [bool(value) for value in relevant]
    if len(values) != len(labels) or not values:
        return DEFAULT_RELEVANCE_THRESHOLD
    positive_count = sum(labels)
    negative_count = len(labels) - positive_count
    if not positive_count or not negative_count:
        return DEFAULT_RELEVANCE_THRESHOLD
    best_recall = -1.0
    best_threshold = DEFAULT_RELEVANCE_THRESHOLD
    for threshold in np.linspace(0.0, 1.0, 101):
        predicted = [value >= threshold for value in values]
        true_positive = sum(item and label for item, label in zip(predicted, labels))
        false_positive = sum(
            item and not label for item, label in zip(predicted, labels)
        )
        recall = true_positive / positive_count
        false_rate = false_positive / negative_count
        if false_rate <= max_false_positive_rate and (
            recall > best_recall
            or (recall == best_recall and threshold > best_threshold)
        ):
            best_recall = recall
            best_threshold = float(threshold)
    return best_threshold


def evaluate_retrieval(
    index: RAGIndex,
    cases: Iterable[dict[str, Any]],
    *,
    split: str | None = None,
) -> dict[str, Any]:
    """Evaluate a fixed retrieval snapshot against a labeled JSON case set.

    A case contains the fields accepted by :class:`RetrievalRequest` and a
    ``relevant_source_ids`` array. This helper performs no LLM calls and never
    mutates the index or its threshold. A ``split`` filter reports a
    development set separately from a holdout set.
    """

    rows = list(cases)
    if split is not None:
        rows = [item for item in rows if str(item.get("split", "")) == split]
    evaluated = 0
    recall_hits = 0
    reciprocal_rank = 0.0
    returned = 0
    irrelevant = 0
    duplicate = 0
    details: list[dict[str, Any]] = []
    request_fields = {
        "role",
        "operation",
        "canonical_class",
        "profile_id",
        "missing_fields",
        "summary",
        "stage",
    }
    for case in rows:
        relevant = {
            str(value)
            for value in case.get("relevant_source_ids", case.get("relevant_ids", []))
            if value
        }
        if not relevant:
            continue
        request = RetrievalRequest(
            **{
                key: case[key]
                for key in request_fields
                if key in case and case[key] is not None
            }
        )
        results = index.retrieve(request, limit=MAX_RESULTS)
        source_ids = [result.source_id for result in results]
        evaluated += 1
        returned += len(source_ids)
        irrelevant += sum(source_id not in relevant for source_id in source_ids)
        duplicate += len(source_ids) - len(set(source_ids))
        ranks = [
            rank
            for rank, source_id in enumerate(source_ids, 1)
            if source_id in relevant
        ]
        if ranks:
            recall_hits += 1
            reciprocal_rank += 1.0 / ranks[0]
        details.append(
            {
                "query": request.query_text(),
                "relevant_source_ids": sorted(relevant),
                "returned_source_ids": source_ids,
                "reciprocal_rank": 1.0 / ranks[0] if ranks else 0.0,
            }
        )
    return {
        "snapshot": index.index_snapshot,
        "split": split,
        "cases": evaluated,
        "recall_at_4": recall_hits / evaluated if evaluated else 0.0,
        "mrr": reciprocal_rank / evaluated if evaluated else 0.0,
        "irrelevant_result_rate": irrelevant / returned if returned else 0.0,
        "duplicate_rate": duplicate / returned if returned else 0.0,
        "details": details,
    }


def _record_key(record: _SourceRecord) -> tuple[str, str]:
    content_hash = _hash(record.text)
    # Identical fragments share one vector row regardless of their location;
    # every source position is retained in ``source_aliases``. This covers
    # copied manuals, repeated paragraphs, and duplicate builtin entries while
    # keeping the primary source ID independent of full-corpus ordering.
    artifact_identity = record.artifact_id or ""
    return record.artifact_type, f"{artifact_identity}|{content_hash}"


def build_index(
    source_dir: str | Path | None,
    index_dir: str | Path,
    *,
    encoder=None,
    include_builtin: bool = True,
):
    source = Path(source_dir) if source_dir is not None else None
    index_root = Path(index_dir)
    if source is not None and not source.is_dir():
        raise FileNotFoundError(f"source directory not found: {source}")
    index_root.mkdir(parents=True, exist_ok=True)
    if encoder is None:
        encoder = SentenceTransformerEncoder()
    records = _read_sources(
        source,
        include_builtin,
        tokenizer=_tokenizer_for_encoder(encoder),
    )
    if not records:
        raise ValueError("no indexable Markdown/PDF or builtin sources found")

    unique: list[_SourceRecord] = []
    aliases: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    seen: dict[tuple[str, str], int] = {}
    for record in records:
        key = _record_key(record)
        alias = {
            "source_path": record.source_path,
            "section": record.section,
            "page": record.page,
            "char_start": record.char_start,
            "char_end": record.char_end,
        }
        aliases[key].append(alias)
        if key not in seen:
            seen[key] = len(unique)
            unique.append(record)
    texts = [item.text for item in unique]
    vectors = np.asarray(_encode(encoder, texts, is_query=False), dtype=np.float32)
    if vectors.ndim != 2 or vectors.shape[0] != len(texts) or vectors.shape[1] <= 0:
        raise ValueError("embedding encoder returned an invalid matrix")
    if not np.isfinite(vectors).all():
        raise ValueError("embedding encoder returned non-finite values")

    snapshot_name = f"snapshot-{uuid.uuid4().hex}"
    snapshot = index_root / snapshot_name
    snapshot.mkdir()
    try:
        np.save(snapshot / "vectors.npy", vectors)
        with sqlite3.connect(snapshot / "metadata.sqlite3") as conn:
            try:
                conn.execute(
                    "CREATE VIRTUAL TABLE chunks_fts USING fts5(source_id UNINDEXED, text)"
                )
            except sqlite3.OperationalError as exc:
                raise ValueError(
                    "SQLite FTS5 is required for the local RAG index"
                ) from exc
            conn.execute(
                "CREATE TABLE chunks ("
                "id INTEGER PRIMARY KEY, text TEXT NOT NULL, source_path TEXT NOT NULL, "
                "source_id TEXT NOT NULL UNIQUE, content_hash TEXT NOT NULL, section TEXT, page INTEGER, "
                "artifact_type TEXT NOT NULL, artifact_id TEXT, source_kind TEXT NOT NULL, "
                "roles_json TEXT NOT NULL, stages_json TEXT NOT NULL, canonical_class TEXT, "
                "profile_id TEXT, rule_id TEXT, char_start INTEGER, char_end INTEGER, source_aliases TEXT NOT NULL)"
            )
            for index, record in enumerate(unique):
                content_hash = _hash(record.text)
                source_id = _hash(
                    "|".join(
                        str(value or "")
                        for value in (
                            record.artifact_type,
                            record.artifact_id,
                            content_hash,
                        )
                    )
                )
                source_aliases = json.dumps(
                    aliases[_record_key(record)],
                    ensure_ascii=False,
                    sort_keys=True,
                )
                conn.execute(
                    "INSERT INTO chunks(id,text,source_path,source_id,content_hash,section,page,"
                    "artifact_type,artifact_id,source_kind,roles_json,stages_json,canonical_class,"
                    "profile_id,rule_id,char_start,char_end,source_aliases) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (
                        index,
                        record.text,
                        record.source_path,
                        source_id,
                        content_hash,
                        record.section,
                        record.page,
                        record.artifact_type,
                        record.artifact_id,
                        record.source_kind,
                        json.dumps(record.role, ensure_ascii=False),
                        json.dumps(record.stage, ensure_ascii=False),
                        record.canonical_class,
                        record.profile_id,
                        record.rule_id,
                        record.char_start,
                        record.char_end,
                        source_aliases,
                    ),
                )
                conn.execute(
                    "INSERT INTO chunks_fts(rowid,source_id,text) VALUES(?,?,?)",
                    (index + 1, source_id, record.text),
                )
            conn.commit()

        metadata_checksum = _hash_bytes(snapshot / "metadata.sqlite3")
        vector_checksum = _hash_bytes(snapshot / "vectors.npy")
        source_version = _hash(
            json.dumps(
                [
                    {
                        "path": record.source_path,
                        "section": record.section,
                        "page": record.page,
                        "hash": _hash(record.text),
                        "artifact_type": record.artifact_type,
                        "artifact_id": record.artifact_id,
                    }
                    for record in sorted(
                        records,
                        key=lambda item: (
                            item.source_path,
                            item.page or 0,
                            item.char_start or 0,
                            item.artifact_type,
                        ),
                    )
                ],
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        source_files: list[dict[str, str]] = []
        if source is not None:
            for path in sorted(source.rglob("*")):
                if path.is_file() and path.suffix.lower() in {
                    ".md",
                    ".markdown",
                    ".pdf",
                }:
                    source_files.append(
                        {
                            "path": path.relative_to(source).as_posix(),
                            "sha256": _hash_bytes(path),
                            "kind": "external",
                        }
                    )
        builtin_paths = sorted(
            {
                record.source_path
                for record in records
                if record.source_kind != "external"
            }
        )
        source_files.extend(
            {
                "path": path,
                "sha256": _hash(
                    "|".join(
                        sorted(
                            record.text
                            for record in records
                            if record.source_path == path
                        )
                    )
                ),
                "kind": "builtin",
            }
            for path in builtin_paths
        )
        manifest = {
            "schema_version": RAG_SCHEMA_VERSION,
            "retrieval_policy_version": RETRIEVAL_POLICY_VERSION,
            "embedding_model": _encoder_name(encoder),
            "embedding_model_revision": _encoder_version(encoder),
            "tokenizer_revision": _tokenizer_version(encoder),
            "embedding_dimension": int(vectors.shape[1]),
            "chunking": {
                "max_tokens": MAX_CHUNK_TOKENS,
                "overlap_tokens": CHUNK_OVERLAP_TOKENS,
                "pdf_page_boundary": True,
                "tokenizer_offsets": _tokenizer_for_encoder(encoder) is not None,
            },
            "retrieval_policy": {
                "dense_candidates": DENSE_CANDIDATES,
                "lexical_candidates": LEXICAL_CANDIDATES,
                "rrf_k": RRF_K,
                "max_results": MAX_RESULTS,
                "max_results_per_document": MAX_RESULTS_PER_DOCUMENT,
                "max_reference_tokens": MAX_REFERENCE_TOKENS,
                "relevance_threshold": DEFAULT_RELEVANCE_THRESHOLD,
                "threshold_calibration": "default; run rag eval to replace",
            },
            "registry_version": REGISTRY_VERSION,
            "registry_fingerprint": registry_fingerprint(),
            "source_count": len({item.source_path for item in records}),
            "source_files": source_files,
            "chunk_count": len(unique),
            "source_version": source_version,
            "metadata_checksum": metadata_checksum,
            "vector_checksum": vector_checksum,
        }
        (snapshot / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2),
            encoding="utf-8",
        )
        current_tmp = index_root / f".CURRENT.{os.getpid()}.{uuid.uuid4().hex}"
        current_tmp.write_text(snapshot_name, encoding="utf-8")
        os.replace(current_tmp, index_root / "CURRENT")
    except Exception:
        shutil.rmtree(snapshot, ignore_errors=True)
        raise
    return RAGIndex(snapshot, encoder=encoder)


def load_index(
    index_dir,
    *,
    encoder=None,
    snapshot_name: str | None = None,
    load_encoder: bool = True,
):
    index_dir = Path(index_dir)
    if snapshot_name is None:
        current = index_dir / "CURRENT"
        if not current.is_file():
            raise FileNotFoundError(f"RAG index missing CURRENT: {index_dir}")
        try:
            snapshot_name = current.read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise ValueError(f"corrupt RAG CURRENT pointer: {current}") from exc
        if not snapshot_name or Path(snapshot_name).name != snapshot_name:
            raise ValueError(f"corrupt RAG CURRENT pointer: {current}")
    elif not snapshot_name or Path(snapshot_name).name != snapshot_name:
        raise ValueError("invalid RAG snapshot name")
    snapshot = index_dir / snapshot_name
    if not snapshot.is_dir() or not all(
        (snapshot / name).is_file()
        for name in ("metadata.sqlite3", "vectors.npy", "manifest.json")
    ):
        raise ValueError(f"corrupt RAG index snapshot: {snapshot}")
    return RAGIndex(snapshot, encoder=encoder, load_encoder=load_encoder)
