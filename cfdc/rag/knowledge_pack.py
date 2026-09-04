"""Validated, packaged advisory knowledge cards for local RAG."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, date, datetime
from importlib.resources import files
from pathlib import Path, PurePosixPath
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


@dataclass(frozen=True)
class KnowledgePackArtifact:
    artifact_id: str
    artifact_group_id: str
    title: str
    text: str
    relative_path: str
    language: str
    authority: str
    version: str
    roles: tuple[str, ...]
    stages: tuple[str, ...]
    canonical_classes: tuple[str, ...]
    profile_ids: tuple[str, ...]
    sha256: str
    source_refs: tuple[str, ...]
    valid_from: str
    valid_until: str | None
    supersedes: tuple[str, ...]


@dataclass(frozen=True)
class KnowledgePack:
    pack_id: str
    version: str
    authority: str
    artifacts: tuple[KnowledgePackArtifact, ...]
    sources: dict[str, dict[str, Any]]
    evaluation: dict[str, Any]
    evaluation_metadata: dict[str, Any]
    excluded_artifact_ids: tuple[str, ...] = ()


def _safe_relative_path(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or ".." in path.parts:
        raise ValueError(f"knowledge-pack path must stay inside the pack: {value}")
    return path


def _read_text(root: Any, relative: str) -> str:
    safe = _safe_relative_path(relative)
    target = root.joinpath(*safe.parts)
    if isinstance(root, Path):
        resolved_root = root.resolve()
        resolved_target = target.resolve()
        if not resolved_target.is_relative_to(resolved_root):
            raise ValueError(f"knowledge-pack path escapes its root: {relative}")
        target = resolved_target
    try:
        return target.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ValueError(
            f"unable to read knowledge-pack file {relative}: {exc}"
        ) from exc


def _validate_evaluation_case(case: Any) -> None:
    if not isinstance(case, dict):
        raise TypeError("knowledge-pack evaluation case must be an object")
    case_id = case.get("case_id")
    if not isinstance(case_id, str) or not case_id:
        raise ValueError("knowledge-pack evaluation case ID is invalid")
    if case.get("split") not in {"dev", "holdout"}:
        raise ValueError(f"knowledge-pack evaluation case {case_id} has invalid split")
    for field in ("role", "operation", "summary"):
        if not isinstance(case.get(field), str):
            raise TypeError(
                f"knowledge-pack evaluation case {case_id} has invalid {field}"
            )
    for field in ("stage", "canonical_class", "profile_id"):
        if (
            field in case
            and case[field] is not None
            and not isinstance(case[field], str)
        ):
            raise ValueError(
                f"knowledge-pack evaluation case {case_id} has invalid {field}"
            )
    if case.get("language", "auto") not in {"auto", "en", "zh"}:
        raise ValueError(
            f"knowledge-pack evaluation case {case_id} has invalid language"
        )
    if "expected_language" in case and case["expected_language"] not in {"en", "zh"}:
        raise ValueError(
            f"knowledge-pack evaluation case {case_id} has invalid expected language"
        )
    if (
        case.get("language") in {"en", "zh"}
        and case.get("expected_language") is not None
        and case["language"] != case["expected_language"]
    ):
        raise ValueError(
            f"knowledge-pack evaluation case {case_id} has inconsistent language override"
        )
    missing_fields = case.get("missing_fields", [])
    if not isinstance(missing_fields, list) or not all(
        isinstance(item, str) and item for item in missing_fields
    ):
        raise ValueError(
            f"knowledge-pack evaluation case {case_id} has invalid missing_fields"
        )
    if "allow_cross_language_fallback" in case and not isinstance(
        case["allow_cross_language_fallback"], bool
    ):
        raise ValueError(
            f"knowledge-pack evaluation case {case_id} has invalid fallback policy"
        )
    if "expected_empty" in case and not isinstance(case["expected_empty"], bool):
        raise ValueError(
            f"knowledge-pack evaluation case {case_id} has invalid expected_empty"
        )

    def group_ids(field: str) -> list[str]:
        values = case.get(field, [])
        if not isinstance(values, list) or not all(
            isinstance(item, str) and item for item in values
        ):
            raise ValueError(
                f"knowledge-pack evaluation case {case_id} has invalid {field}"
            )
        if len(values) != len(set(values)):
            raise ValueError(
                f"knowledge-pack evaluation case {case_id} has duplicate {field}"
            )
        return values

    relevant = group_ids("relevant_artifact_group_ids")
    acceptable = group_ids("acceptable_artifact_group_ids")
    if case.get("expected_empty"):
        if relevant or acceptable:
            raise ValueError(
                f"knowledge-pack negative case {case_id} cannot label relevant groups"
            )
    elif not relevant:
        raise ValueError(
            f"knowledge-pack positive case {case_id} requires a relevant group"
        )
    category = case.get("challenge_category")
    if category is not None and category not in {
        "out_of_domain",
        "control_false_friend",
        "prompt_injection",
        "underspecified_mixed",
    }:
        raise ValueError(
            f"knowledge-pack evaluation case {case_id} has invalid challenge category"
        )


def load_knowledge_pack(
    pack_dir: str | Path | None = None,
    *,
    as_of: date | None = None,
) -> KnowledgePack:
    """Load and fully validate one advisory Markdown knowledge pack."""

    root: Any = (
        Path(pack_dir)
        if pack_dir is not None
        else files("cfdc").joinpath("resources", "knowledge_pack", "v1")
    )
    try:
        schema = json.loads(_read_text(root, "schema.json"))
        manifest = json.loads(_read_text(root, "manifest.json"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"knowledge-pack JSON is invalid: {exc}") from exc
    try:
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(manifest)
    except Exception as exc:
        raise ValueError(f"knowledge-pack manifest is invalid: {exc}") from exc

    evaluation_meta = dict(manifest["evaluation"])

    def load_evaluation_dataset(metadata: dict[str, Any]) -> dict[str, Any]:
        evaluation_text = _read_text(root, str(metadata["dataset"]))
        evaluation_hash = hashlib.sha256(evaluation_text.encode("utf-8")).hexdigest()
        if evaluation_hash != metadata["sha256"]:
            raise ValueError(
                "knowledge-pack evaluation dataset does not match its sha256"
            )
        try:
            dataset = json.loads(evaluation_text)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"knowledge-pack evaluation dataset is invalid: {exc}"
            ) from exc
        cases = dataset.get("cases") if isinstance(dataset, dict) else None
        if not isinstance(cases, list) or len(cases) != metadata["cases"]:
            raise ValueError("knowledge-pack evaluation dataset case count is invalid")
        if dataset.get("schema_version") != "cfdc-retrieval-eval/v1":
            raise ValueError("knowledge-pack evaluation dataset schema is invalid")
        if "dataset_id" in dataset and (
            not isinstance(dataset["dataset_id"], str) or not dataset["dataset_id"]
        ):
            raise ValueError("knowledge-pack evaluation dataset ID is invalid")
        for case in cases:
            _validate_evaluation_case(case)
        if sum(case.get("split") == "dev" for case in cases) != metadata["dev_cases"]:
            raise ValueError("knowledge-pack evaluation dataset dev count is invalid")
        if (
            sum(case.get("split") == "holdout" for case in cases)
            != metadata["holdout_cases"]
        ):
            raise ValueError(
                "knowledge-pack evaluation dataset holdout count is invalid"
            )
        if metadata.get("purpose") == "regression" and metadata["holdout_cases"] != 0:
            raise ValueError(
                "knowledge-pack regression evaluation datasets must contain only dev cases"
            )
        return dataset

    loaded_evaluations = [(evaluation_meta, load_evaluation_dataset(evaluation_meta))]
    for additional in evaluation_meta.get("additional_datasets", []):
        metadata = dict(additional)
        loaded_evaluations.append((metadata, load_evaluation_dataset(metadata)))
    combined_cases = [
        case for _metadata, dataset in loaded_evaluations for case in dataset["cases"]
    ]
    case_ids = [str(case.get("case_id") or "") for case in combined_cases]
    if not all(case_ids) or len(case_ids) != len(set(case_ids)):
        raise ValueError("knowledge-pack evaluation case IDs must be unique")
    evaluation = {
        "schema_version": loaded_evaluations[0][1].get("schema_version"),
        "dataset_id": f"{manifest['pack_id']}-{manifest['version']}",
        "cases": combined_cases,
        "datasets": [
            {
                "dataset_id": str(
                    metadata.get("dataset_id")
                    or Path(str(metadata["dataset"])).stem.removeprefix("retrieval_")
                ),
                "purpose": str(metadata.get("purpose") or "quality_gate"),
                "path": str(metadata["dataset"]),
                "sha256": str(metadata["sha256"]),
                "cases": list(dataset["cases"]),
            }
            for metadata, dataset in loaded_evaluations
        ],
    }

    source_rows = manifest["sources"]
    sources = {str(item["source_id"]): dict(item) for item in source_rows}
    if len(sources) != len(source_rows):
        raise ValueError("knowledge-pack source IDs must be unique")

    artifact_rows = manifest["artifacts"]
    artifact_ids = [str(item["artifact_id"]) for item in artifact_rows]
    if len(set(artifact_ids)) != len(artifact_ids):
        raise ValueError("knowledge-pack artifact IDs must be unique")
    language_groups = [
        (str(item["artifact_group_id"]), str(item["language"]))
        for item in artifact_rows
    ]
    if len(set(language_groups)) != len(language_groups):
        raise ValueError("knowledge-pack group/language pairs must be unique")

    known_artifacts = set(artifact_ids)
    identity_by_artifact = {
        str(item["artifact_id"]): (
            str(item["artifact_group_id"]),
            str(item["language"]),
        )
        for item in artifact_rows
    }
    today = as_of or datetime.now(UTC).date()
    parsed: list[KnowledgePackArtifact] = []
    excluded: list[str] = []
    for raw in artifact_rows:
        artifact_id = str(raw["artifact_id"])
        missing_sources = set(raw["source_refs"]) - sources.keys()
        if missing_sources:
            raise ValueError(
                f"knowledge-pack artifact {artifact_id} has unknown sources: "
                f"{sorted(missing_sources)}"
            )
        unknown_supersedes = set(raw["supersedes"]) - known_artifacts
        if unknown_supersedes:
            raise ValueError(
                f"knowledge-pack artifact {artifact_id} supersedes unknown artifacts: "
                f"{sorted(unknown_supersedes)}"
            )
        identity = identity_by_artifact[artifact_id]
        if any(
            identity_by_artifact[superseded_id] != identity
            for superseded_id in raw["supersedes"]
        ):
            raise ValueError(
                "knowledge-pack supersedes must stay in the same group and language"
            )
        valid_from = date.fromisoformat(str(raw["valid_from"]))
        valid_until = (
            date.fromisoformat(str(raw["valid_until"]))
            if raw["valid_until"] is not None
            else None
        )
        if valid_until is not None and valid_until < valid_from:
            raise ValueError(
                f"knowledge-pack artifact {artifact_id} has an invalid validity range"
            )
        text = _read_text(root, str(raw["path"]))
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if digest != raw["sha256"]:
            raise ValueError(
                f"knowledge-pack artifact {artifact_id} does not match its sha256"
            )
        if (
            raw["status"] != "active"
            or valid_from > today
            or (valid_until is not None and valid_until < today)
        ):
            excluded.append(artifact_id)
            continue
        parsed.append(
            KnowledgePackArtifact(
                artifact_id=artifact_id,
                artifact_group_id=str(raw["artifact_group_id"]),
                title=str(raw["title"]),
                text=text,
                relative_path=str(raw["path"]),
                language=str(raw["language"]),
                authority=str(raw["authority"]),
                version=str(raw["version"]),
                roles=tuple(str(item) for item in raw["roles"]),
                stages=tuple(str(item) for item in raw["stages"]),
                canonical_classes=tuple(str(item) for item in raw["canonical_classes"]),
                profile_ids=tuple(str(item) for item in raw["profile_ids"]),
                sha256=str(raw["sha256"]),
                source_refs=tuple(str(item) for item in raw["source_refs"]),
                valid_from=str(raw["valid_from"]),
                valid_until=(
                    str(raw["valid_until"]) if raw["valid_until"] is not None else None
                ),
                supersedes=tuple(str(item) for item in raw["supersedes"]),
            )
        )

    superseded = {
        superseded_id for artifact in parsed for superseded_id in artifact.supersedes
    }
    active = tuple(item for item in parsed if item.artifact_id not in superseded)
    excluded.extend(sorted(superseded))
    return KnowledgePack(
        pack_id=str(manifest["pack_id"]),
        version=str(manifest["version"]),
        authority=str(manifest["authority"]),
        artifacts=active,
        sources=sources,
        evaluation=evaluation,
        evaluation_metadata=evaluation_meta,
        excluded_artifact_ids=tuple(sorted(set(excluded))),
    )
