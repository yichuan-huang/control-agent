"""Load and adopt fixed examples for plain-language model questions."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from cfdc.lab.model_contracts import (
    DiscoveryQuestion,
    ModelFactAnswer,
    ModelQuestionExample,
    ModelQuestionExampleCatalog,
)


_CATALOG_PATH = (
    Path(__file__).resolve().parent / "resources" / "model_question_examples.v1.json"
)


def _canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def load_model_question_examples() -> ModelQuestionExampleCatalog:
    """Load a validated, independent copy of the package-data catalog."""

    try:
        payload = json.loads(_CATALOG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("model question example catalog could not be loaded") from exc
    try:
        return ModelQuestionExampleCatalog.model_validate(payload)
    except ValueError as exc:
        raise ValueError(f"invalid model question example catalog: {exc}") from exc


def _find_example(
    example_id: str,
    catalog: ModelQuestionExampleCatalog,
) -> ModelQuestionExample:
    for example in catalog.examples:
        if example.example_id == example_id:
            return example
    raise ValueError(f"unknown example ID: {example_id}")


def adopt_example_answer(
    question: DiscoveryQuestion,
    catalog: ModelQuestionExampleCatalog,
    *,
    adopted_at: str,
) -> ModelFactAnswer:
    """Create an answer only after an explicit example-adoption action."""

    if catalog.catalog_version != "v1":
        raise ValueError("model question example catalog version mismatch")
    example = _find_example(question.example_id, catalog)
    if (
        example.fact_type != question.fact_type
        or example.unit_family != question.unit_family
    ):
        raise ValueError("question fact type or unit family does not match its example")
    return ModelFactAnswer(
        fact_id=question.fact_id,
        fact_type=question.fact_type,
        answer_text=example.answer_text,
        value_payload=example.value_payload,
        unit_family=question.unit_family,
        source="user_adopted_example",
        example_id=example.example_id,
        example_catalog_version=catalog.catalog_version,
        example_content_sha256=_canonical_sha256(example.model_dump(mode="json")),
        adopted_at=adopted_at,
    )


__all__ = ["adopt_example_answer", "load_model_question_examples"]
