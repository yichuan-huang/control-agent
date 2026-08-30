from __future__ import annotations

import sqlite3

import numpy as np
import pytest

from cfdc.diagnosis.engine import classify_archetype, infer_structural_diagnosis
from cfdc.knowledge import (
    REGISTRY_VERSION,
    RetrievalRequest,
    resolve_route_decision,
)
from cfdc.models import SystemDescription
from cfdc.rag import build_index


class KeywordEncoder:
    model_name = "test-keyword"
    model_revision = "test-revision"

    def encode(self, texts, *, is_query=False):
        del is_query
        if isinstance(texts, str):
            texts = [texts]
        vocabulary = ("heater", "motor", "delay", "限幅", "稳定", "profile")
        return np.asarray(
            [[text.casefold().count(word) for word in vocabulary] for text in texts],
            dtype=float,
        )


def test_builtin_registry_index_contains_all_mechanism_cards(tmp_path):
    source = tmp_path / "sources"
    source.mkdir()
    index = build_index(source, tmp_path / "index", encoder=KeywordEncoder())

    rows = index.metadata()
    mechanism_rows = [
        row for row in rows if row.get("artifact_type") == "mechanism_card"
    ]
    assert len({row["artifact_id"] for row in mechanism_rows}) == 14
    assert index.manifest["registry_version"] == REGISTRY_VERSION


def test_registry_resolver_is_deterministic_and_does_not_need_llm():
    description = SystemDescription(
        text="A stable heater has a voltage input and temperature output."
    )
    diagnosis = infer_structural_diagnosis(description).model_copy(
        update={"complete": True, "clarification_questions": []}
    )
    classification = classify_archetype(diagnosis, description)

    decision = resolve_route_decision(description, diagnosis, classification)

    assert decision.registry_version == REGISTRY_VERSION
    assert decision.primary_class == str(classification.primary_class)
    assert decision.simulation_profile_id == "first_order_lag"
    assert decision.matched_rule_ids


def test_structured_retrieval_filters_by_profile_and_returns_empty_for_irrelevant_query(
    tmp_path,
):
    source = tmp_path / "sources"
    source.mkdir()
    (source / "profiles.md").write_text(
        "# Heater\n\nThe first_order_lag profile is for stable heater systems.\n\n"
        "# Motor\n\nA motor profile has delay limits.\n",
        encoding="utf-8",
    )
    index = build_index(
        source, tmp_path / "index", encoder=KeywordEncoder(), include_builtin=False
    )

    request = RetrievalRequest(
        role="controller",
        operation="explain_profile",
        profile_id="first_order_lag",
        summary="heater profile preconditions",
    )
    results = index.retrieve(request)

    assert results
    assert any("first_order_lag" in result.text for result in results)
    assert (
        index.retrieve(
            RetrievalRequest(
                role="critic", operation="check", summary="unrelated xyzzy"
            )
        )
        == []
    )


def test_index_uses_stable_source_ids_and_builds_fts5(tmp_path):
    source = tmp_path / "sources"
    source.mkdir()
    document = source / "manual.md"
    document.write_text("# Safety\n\nKeep heater stable.", encoding="utf-8")
    first = build_index(
        source, tmp_path / "index", encoder=KeywordEncoder(), include_builtin=False
    )
    first_id = first.metadata()[0]["source_id"]

    (source / "other.md").write_text("# Other\n\nExtra motor notes.", encoding="utf-8")
    second = build_index(
        source, tmp_path / "index", encoder=KeywordEncoder(), include_builtin=False
    )
    second_rows = {row["source_path"]: row for row in second.metadata()}
    assert second_rows["manual.md"]["source_id"] == first_id
    with sqlite3.connect(second.snapshot / "metadata.sqlite3") as connection:
        assert connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='chunks_fts'"
        ).fetchone()


def test_corrupt_registry_payload_is_not_silently_omitted(monkeypatch, tmp_path):
    from cfdc.rag import core

    monkeypatch.setattr(
        core,
        "_builtin_artifacts",
        lambda: (_ for _ in ()).throw(ValueError("broken registry")),
    )
    source = tmp_path / "sources"
    source.mkdir()
    with pytest.raises(ValueError, match="broken registry"):
        build_index(source, tmp_path / "index", encoder=KeywordEncoder())
