from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
import sys
from importlib.resources import files
from pathlib import Path
from types import SimpleNamespace
from typing import ClassVar

import numpy as np
import pytest

from cfdc.knowledge import REGISTRY_VERSION, RetrievalRequest, registry_fingerprint
from cfdc.rag import SearchResult, build_index, evaluate_retrieval, load_index
from cfdc.rag.knowledge_pack import load_knowledge_pack


class KeywordEncoder:
    model_name = "intfloat/multilingual-e5-small"
    model_revision = "614241f622f53c4eeff9890bdc4f31cfecc418b3"

    def encode(self, texts, *, is_query=False):
        del is_query
        if isinstance(texts, str):
            texts = [texts]
        vocabulary = ("stability", "delay", "damping", "mimo", "qualification")
        return np.asarray(
            [[text.casefold().count(word) for word in vocabulary] for text in texts],
            dtype=float,
        )


class RecordingEncoder(KeywordEncoder):
    def __init__(self):
        self.query_texts = []

    def encode(self, texts, *, is_query=False):
        if is_query:
            self.query_texts.extend([texts] if isinstance(texts, str) else texts)
        return super().encode(texts, is_query=is_query)


def _copied_pack(tmp_path: Path) -> Path:
    source = Path(__file__).parents[1] / "cfdc" / "resources" / "knowledge_pack" / "v1"
    target = tmp_path / "pack"
    shutil.copytree(source, target)
    return target


def _rewrite_evaluation_dataset(
    pack_dir: Path,
    dataset_name: str,
    mutation,
) -> None:
    dataset_path = pack_dir / "eval" / dataset_name
    dataset = json.loads(dataset_path.read_text(encoding="utf-8"))
    mutation(dataset)
    serialized = json.dumps(dataset, ensure_ascii=False, indent=2) + "\n"
    dataset_path.write_text(serialized, encoding="utf-8")

    manifest_path = pack_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    datasets = [manifest["evaluation"], *manifest["evaluation"]["additional_datasets"]]
    metadata = next(item for item in datasets if item["dataset"].endswith(dataset_name))
    metadata["sha256"] = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")


def test_bundled_pack_keeps_twelve_auditable_english_cards():
    pack = load_knowledge_pack()

    assert pack.pack_id == "cfdc-control-foundations"
    assert pack.version == "1.3.0"
    english = [artifact for artifact in pack.artifacts if artifact.language == "en"]
    assert len(english) == 12
    assert len({artifact.artifact_group_id for artifact in english}) == 12
    assert all(artifact.authority == "advisory" for artifact in pack.artifacts)
    assert all(artifact.source_refs for artifact in pack.artifacts)
    assert all(
        source_ref in pack.sources
        for artifact in pack.artifacts
        for source_ref in artifact.source_refs
    )


def test_bundled_evaluation_preserves_independent_dataset_identities():
    pack = load_knowledge_pack()

    datasets = pack.evaluation["datasets"]
    assert [dataset["dataset_id"] for dataset in datasets] == [
        "en",
        "zh",
        "challenge_regression",
        "challenge",
    ]
    assert [len(dataset["cases"]) for dataset in datasets] == [48, 48, 48, 48]
    assert [dataset["purpose"] for dataset in datasets] == [
        "quality_gate",
        "quality_gate",
        "regression",
        "quality_gate",
    ]

    evaluation = json.loads(
        files("cfdc")
        .joinpath("resources", "knowledge_pack", "v1", "eval", "retrieval_en.json")
        .read_text(encoding="utf-8")
    )
    assert len(evaluation["cases"]) == 48
    assert sum(case["split"] == "dev" for case in evaluation["cases"]) == 24
    assert sum(case["split"] == "holdout" for case in evaluation["cases"]) == 24
    assert sum(bool(case.get("expected_empty")) for case in evaluation["cases"]) == 12


@pytest.mark.parametrize(
    ("filename", "dataset_id", "split"),
    [
        (
            "retrieval_challenge.json",
            "cfdc-control-foundations-challenge-regression-v1",
            "dev",
        ),
        (
            "retrieval_challenge_replacement.json",
            "cfdc-control-foundations-challenge-v2",
            "holdout",
        ),
    ],
)
def test_challenge_sets_are_frozen_and_balanced(filename, dataset_id, split):
    pack = load_knowledge_pack()
    challenge = json.loads(
        files("cfdc")
        .joinpath("resources", "knowledge_pack", "v1", "eval", filename)
        .read_text(encoding="utf-8")
    )
    cases = challenge["cases"]
    positive = [case for case in cases if not case.get("expected_empty")]
    negative = [case for case in cases if case.get("expected_empty")]

    assert challenge["dataset_id"] == dataset_id
    assert len(cases) == 48
    assert {case["split"] for case in cases} == {split}
    assert len(positive) == len(negative) == 24
    assert len({case["case_id"] for case in cases}) == 48
    assert "qzxv" not in json.dumps(challenge, ensure_ascii=False).casefold()
    assert {
        group: sum(group in case["relevant_artifact_group_ids"] for case in positive)
        for group in {artifact.artifact_group_id for artifact in pack.artifacts}
    } == {artifact.artifact_group_id: 2 for artifact in pack.artifacts}

    auto_en = [
        case
        for case in positive
        if "language" not in case and case["expected_language"] == "en"
    ]
    auto_zh = [
        case
        for case in positive
        if "language" not in case and case["expected_language"] == "zh"
    ]
    override_zh = [case for case in positive if case.get("language") == "zh"]
    override_en = [case for case in positive if case.get("language") == "en"]
    assert tuple(map(len, (auto_en, auto_zh, override_zh, override_en))) == (8, 8, 4, 4)
    assert {
        category: sum(case["challenge_category"] == category for case in negative)
        for category in (
            "out_of_domain",
            "control_false_friend",
            "prompt_injection",
            "underspecified_mixed",
        )
    } == {
        "out_of_domain": 8,
        "control_false_friend": 8,
        "prompt_injection": 4,
        "underspecified_mixed": 4,
    }

    assert len(pack.evaluation["cases"]) == 192
    assert sum(case["split"] == "dev" for case in pack.evaluation["cases"]) == 96
    assert sum(case["split"] == "holdout" for case in pack.evaluation["cases"]) == 96


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda case: case.update(split="training"), "split"),
        (lambda case: case.update(language="fr"), "language"),
        (
            lambda case: case.update(relevant_artifact_group_ids=[]),
            "positive case",
        ),
        (
            lambda case: case.update(
                expected_empty=True,
                relevant_artifact_group_ids=["open_loop_stability"],
            ),
            "negative case",
        ),
        (
            lambda case: case.update(
                relevant_artifact_group_ids=[
                    "open_loop_stability",
                    "open_loop_stability",
                ]
            ),
            "duplicate",
        ),
    ],
)
def test_pack_rejects_invalid_evaluation_cases(tmp_path, mutation, message):
    pack_dir = _copied_pack(tmp_path)

    def mutate_first_case(dataset):
        mutation(dataset["cases"][0])

    _rewrite_evaluation_dataset(
        pack_dir,
        "retrieval_challenge.json",
        mutate_first_case,
    )

    with pytest.raises(ValueError, match=message):
        load_knowledge_pack(pack_dir)


def test_new_index_contains_curated_pack_metadata_by_default(tmp_path):
    index = build_index(
        None,
        tmp_path / "index",
        encoder=KeywordEncoder(),
        include_builtin=False,
    )

    curated = [row for row in index.metadata() if row["source_kind"] == "curated_pack"]
    assert {row["artifact_group_id"] for row in curated} == {
        artifact.artifact_group_id for artifact in load_knowledge_pack().artifacts
    }
    assert {row["language"] for row in curated} == {"en", "zh"}
    assert {row["authority"] for row in curated} == {"advisory"}
    assert all(row["citation_refs_json"] != "[]" for row in curated)


def test_v3_snapshot_freezes_retrieval_policy_v2_fingerprint(tmp_path):
    from cfdc.rag import core

    index = build_index(
        None,
        tmp_path / "index",
        encoder=KeywordEncoder(),
    )
    policy = index.manifest["retrieval_policy"]

    assert index.manifest["retrieval_policy_version"] == "cfdc-retrieval/v2"
    assert policy["semantic_query_fields"] == ["missing_fields", "summary"]
    assert policy["registry_candidate_policy"] == "summary_exact_id_only"
    assert policy["max_curated_group_results"] == 2
    assert index.manifest["retrieval_policy_fingerprint"] == (
        core.retrieval_policy_fingerprint(policy)
    )
    assert index.manifest["schema_version"] == "cfdc-rag/v3"
    assert index.manifest["retrieval_policy"]["relevance_threshold"] == 0.845
    assert index.manifest["retrieval_policy"]["threshold_calibration"] == (
        "bundled-pack-dev"
    )
    assert index.manifest["knowledge_pack"] == {
        "pack_id": "cfdc-control-foundations",
        "version": "1.3.0",
        "authority": "advisory",
        "excluded_artifact_ids": [],
        "evaluation": {
            "datasets": [
                {
                    "dataset": "eval/retrieval_en.json",
                    "sha256": "9234cb879e2d1c5d63564271643897938cc4ca6ed845fa3cac6630583b0769d4",
                },
                {
                    "dataset": "eval/retrieval_zh.json",
                    "sha256": "894a11eda54c56ab48f6de404413250b4c2137f93eaa7bf545f57b377c5f62ee",
                },
                {
                    "dataset": "eval/retrieval_challenge.json",
                    "sha256": "e2372e43bf6256b1f2bf7b2c02067bcc6873df728780327d7895eb9c0d8c304b",
                },
                {
                    "dataset": "eval/retrieval_challenge_replacement.json",
                    "sha256": "9facb332cb6bbeeabc1d71bc71a8965b02190c64ade324cd9abc455cfbeb66af",
                },
            ],
            "cases": 192,
        },
    }


def test_pack_threshold_is_not_reused_for_an_unmatched_encoder(tmp_path):
    encoder = KeywordEncoder()
    encoder.model_name = "different-encoder"
    encoder.model_revision = "different-revision"

    index = build_index(
        None,
        tmp_path / "index",
        encoder=encoder,
        include_builtin=False,
    )

    assert index.manifest["retrieval_policy"]["relevance_threshold"] == 0.2
    assert index.manifest["retrieval_policy"]["threshold_calibration"] == (
        "default; bundled pack calibration is incompatible with encoder"
    )


def test_curated_cards_obey_scope_and_return_complete_provenance(tmp_path):
    index = build_index(
        None,
        tmp_path / "index",
        encoder=KeywordEncoder(),
        include_builtin=False,
        relevance_threshold=0.0,
    )

    denied = index.retrieve(
        RetrievalRequest(
            role="diagnosis",
            operation="diagnose",
            stage="diagnosis",
            summary="controller qualification rollback",
        )
    )
    assert all(
        result.artifact_group_id != "controller_qualification_boundaries"
        for result in denied
    )

    allowed = index.retrieve(
        RetrievalRequest(
            role="controller",
            operation="explain_profile",
            stage="controller",
            profile_id="nmp_inverse_response",
            summary="minimum_phase_inverse_response.en",
        )
    )
    result = next(
        row
        for row in allowed
        if row.artifact_group_id == "minimum_phase_inverse_response"
    )
    assert result.language == "en"
    assert result.authority == "advisory"
    assert result.artifact_version == "1.0.0"
    assert result.profile_ids == ("nmp_inverse_response",)
    assert {item["source_id"] for item in result.citation_refs} >= {
        "caltech-feedback-systems-2008",
        "repo-knowledge-registry-v1",
    }


def test_scope_control_fields_do_not_pollute_the_semantic_query(tmp_path):
    encoder = RecordingEncoder()
    index = build_index(
        None,
        tmp_path / "index",
        encoder=encoder,
        include_builtin=False,
        relevance_threshold=0.0,
    )

    index.retrieve(
        RetrievalRequest(
            role="critic",
            operation="check",
            stage="review",
            canonical_class="class_i_first_order_lag",
            profile_id="first_order_lag",
            missing_fields=("settling_time",),
            summary="stability evidence near the operating point",
        )
    )

    assert encoder.query_texts[-1] == (
        "settling_time stability evidence near the operating point"
    )


def test_curated_chunks_retain_card_and_section_context(tmp_path):
    index = build_index(
        None,
        tmp_path / "index",
        encoder=KeywordEncoder(),
        include_builtin=False,
        relevance_threshold=0.0,
    )

    row = next(
        item
        for item in index.metadata()
        if item["artifact_group_id"] == "mimo_pairing"
        and item["section"].endswith("Critic checks")
    )

    assert row["text"].startswith(
        "Knowledge card: MIMO coupling, local gain matrices, pairing, and "
        "decoupling\nArtifact group: mimo_pairing\nSection:"
    )


def test_pack_rejects_supersedes_across_concept_groups(tmp_path):
    pack_dir = _copied_pack(tmp_path)
    manifest_path = pack_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["artifacts"][0]["supersedes"] = ["minimum_phase_inverse_response.en"]
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(ValueError, match="same group and language"):
        load_knowledge_pack(pack_dir)


def test_pack_rejects_modified_evaluation_dataset(tmp_path):
    pack_dir = _copied_pack(tmp_path)
    evaluation_path = pack_dir / "eval" / "retrieval_en.json"
    evaluation_path.write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError, match="evaluation dataset.*sha256"):
        load_knowledge_pack(pack_dir)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda manifest: manifest["artifacts"][0].update(sha256="0" * 64), "sha256"),
        (
            lambda manifest: manifest["artifacts"][0].update(
                source_refs=["missing-source"]
            ),
            "unknown sources",
        ),
        (
            lambda manifest: manifest["artifacts"][0].update(
                valid_from="2026-09-04", valid_until="2026-09-03"
            ),
            "invalid validity range",
        ),
        (
            lambda manifest: manifest["artifacts"][1].update(
                artifact_id=manifest["artifacts"][0]["artifact_id"]
            ),
            "artifact IDs must be unique",
        ),
        (
            lambda manifest: manifest["artifacts"][0].update(path="/tmp/outside.md"),
            "manifest is invalid",
        ),
    ],
)
def test_pack_rejects_invalid_audit_metadata(tmp_path, mutation, message):
    pack_dir = _copied_pack(tmp_path)
    manifest_path = pack_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    mutation(manifest)
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        load_knowledge_pack(pack_dir)


def test_retrieval_evaluation_uses_stable_groups_and_negative_cases(tmp_path):
    index = build_index(
        None,
        tmp_path / "index",
        encoder=KeywordEncoder(),
        include_builtin=False,
    )
    report = evaluate_retrieval(
        index,
        [
            {
                "split": "holdout",
                "role": "controller",
                "operation": "explain_profile",
                "stage": "controller",
                "profile_id": "nmp_inverse_response",
                "summary": "minimum_phase_inverse_response.en",
                "relevant_artifact_group_ids": ["minimum_phase_inverse_response"],
            },
            {
                "split": "holdout",
                "role": "",
                "operation": "",
                "stage": None,
                "summary": "xyzzy qzxv",
                "expected_empty": True,
                "relevant_artifact_group_ids": [],
            },
        ],
        split="holdout",
    )

    assert report["cases"] == 2
    assert report["positive_cases"] == 1
    assert report["negative_cases"] == 1
    assert report["artifact_group_recall_at_4"] == 1.0
    assert report["artifact_group_mrr"] == 1.0
    assert report["negative_query_false_positive_rate"] == 0.0
    assert report["artifact_group_duplicate_rate"] == 0.0
    assert report["provenance_resolution_rate"] == 1.0


def test_group_duplicate_metric_ignores_legacy_rows_without_group_ids():
    class LegacyIndex:
        index_snapshot = "snapshot-legacy"

        def retrieve(self, request, limit=4):
            del request, limit
            return [
                SearchResult(
                    text="first chunk",
                    source_path="legacy.md",
                    source_id="a" * 64,
                    content_hash="c" * 64,
                    artifact_id="legacy-card",
                ),
                SearchResult(
                    text="second chunk",
                    source_path="legacy.md",
                    source_id="b" * 64,
                    content_hash="d" * 64,
                    artifact_id="legacy-card",
                ),
            ]

    report = evaluate_retrieval(
        LegacyIndex(),
        [
            {
                "role": "",
                "operation": "",
                "summary": "legacy",
                "relevant_source_ids": ["a" * 64, "b" * 64],
            }
        ],
    )

    assert report["artifact_group_duplicate_rate"] == 0.0


def test_group_evaluation_distinguishes_acceptable_secondary_results():
    class Index:
        index_snapshot = "snapshot-test"

        def retrieve(self, request, limit=4):
            del request, limit
            return [
                SearchResult(
                    text=group,
                    source_path=f"{group}.md",
                    source_id=source * 64,
                    content_hash=content * 64,
                    artifact_group_id=group,
                )
                for group, source, content in (
                    ("required", "a", "d"),
                    ("supporting", "b", "e"),
                    ("unrelated", "c", "f"),
                )
            ]

    report = evaluate_retrieval(
        Index(),
        [
            {
                "role": "",
                "operation": "",
                "summary": "required",
                "relevant_artifact_group_ids": ["required"],
                "acceptable_artifact_group_ids": ["supporting"],
            }
        ],
    )

    assert report["artifact_group_recall_at_4"] == 1.0
    assert report["irrelevant_result_rate"] == pytest.approx(1 / 3)


def test_rag_index_cli_passes_curated_pack_and_threshold(monkeypatch, tmp_path, capsys):
    from cfdc.rag import __main__ as rag_cli

    captured = {}

    class BuiltIndex:
        index_snapshot = "snapshot-test"
        manifest: ClassVar = {"chunk_count": 3, "embedding_model": "fake"}

    def fake_build(source_dir, index_dir, **kwargs):
        captured.update({"source_dir": source_dir, "index_dir": index_dir, **kwargs})
        return BuiltIndex()

    monkeypatch.setattr(rag_cli, "build_index", fake_build)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "python -m cfdc.rag",
            "index",
            "--index-dir",
            str(tmp_path / "index"),
            "--knowledge-pack",
            str(tmp_path / "pack"),
            "--relevance-threshold",
            "0.37",
        ],
    )

    rag_cli.main()

    assert captured["include_curated"] is True
    assert captured["knowledge_pack_dir"] == str(tmp_path / "pack")
    assert captured["relevance_threshold"] == 0.37
    assert json.loads(capsys.readouterr().out)["snapshot"] == "snapshot-test"


def test_v2_snapshot_remains_readable_without_v3_metadata(tmp_path):
    index_dir = tmp_path / "index"
    snapshot = index_dir / "snapshot-legacy"
    snapshot.mkdir(parents=True)
    vectors = np.asarray([[1.0, 0.0, 0.0, 0.0, 0.0]], dtype=np.float32)
    np.save(snapshot / "vectors.npy", vectors)
    content = "stability guidance"
    content_hash = hashlib.sha256(content.encode()).hexdigest()
    with sqlite3.connect(snapshot / "metadata.sqlite3") as connection:
        connection.execute(
            "CREATE VIRTUAL TABLE chunks_fts USING fts5(source_id UNINDEXED, text)"
        )
        connection.execute(
            "CREATE TABLE chunks ("
            "id INTEGER PRIMARY KEY, text TEXT NOT NULL, source_path TEXT NOT NULL, "
            "source_id TEXT NOT NULL UNIQUE, content_hash TEXT NOT NULL, section TEXT, "
            "page INTEGER, artifact_type TEXT NOT NULL, artifact_id TEXT, "
            "source_kind TEXT NOT NULL, roles_json TEXT NOT NULL, stages_json TEXT NOT NULL, "
            "canonical_class TEXT, profile_id TEXT, rule_id TEXT, char_start INTEGER, "
            "char_end INTEGER, source_aliases TEXT NOT NULL)"
        )
        connection.execute(
            "INSERT INTO chunks VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                0,
                content,
                "legacy.md",
                "a" * 64,
                content_hash,
                "Legacy",
                None,
                "external_document",
                "legacy-card",
                "external",
                "[]",
                "[]",
                None,
                None,
                None,
                0,
                len(content),
                "[]",
            ),
        )
        connection.execute(
            "INSERT INTO chunks_fts(rowid,source_id,text) VALUES(1,?,?)",
            ("a" * 64, content),
        )
        connection.commit()

    def checksum(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    (snapshot / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": "cfdc-rag/v2",
                "embedding_model": "test-keyword",
                "embedding_model_revision": "test-revision",
                "embedding_dimension": 5,
                "registry_version": REGISTRY_VERSION,
                "registry_fingerprint": registry_fingerprint(),
                "vector_checksum": checksum(snapshot / "vectors.npy"),
                "metadata_checksum": checksum(snapshot / "metadata.sqlite3"),
                "retrieval_policy": {"relevance_threshold": 0.2},
            }
        ),
        encoding="utf-8",
    )
    (index_dir / "CURRENT").write_text("snapshot-legacy", encoding="utf-8")

    index = load_index(index_dir, encoder=KeywordEncoder())
    result = index.search("stability")[0]

    assert result.artifact_id == "legacy-card"
    assert result.language == "und"
    assert result.artifact_group_id is None


def test_prior_v3_snapshot_without_policy_fingerprint_remains_readable(tmp_path):
    index_dir = tmp_path / "index"
    built = build_index(
        None,
        index_dir,
        encoder=KeywordEncoder(),
        include_curated=False,
    )
    manifest_path = built.snapshot / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["retrieval_policy_version"] = "cfdc-retrieval/v1"
    manifest.pop("retrieval_policy_fingerprint")
    manifest["retrieval_policy"].pop("semantic_query_fields")
    manifest["retrieval_policy"].pop("registry_candidate_policy")
    manifest["retrieval_policy"].pop("max_curated_group_results")
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    loaded = load_index(index_dir, encoder=KeywordEncoder())

    assert loaded.index_snapshot == built.index_snapshot
    assert loaded.manifest["retrieval_policy_version"] == "cfdc-retrieval/v1"


def test_rag_query_cli_reports_curated_provenance(monkeypatch, capsys):
    from cfdc.rag import __main__ as rag_cli

    result = SimpleNamespace(
        source_id="source-1",
        source_path="curated/cards/en/example.md",
        section="Definition",
        page=None,
        artifact_type="knowledge_card",
        artifact_id="example.en",
        artifact_group_id="example",
        source_kind="curated_pack",
        language="en",
        authority="advisory",
        artifact_version="1.0.0",
        canonical_classes=("class_i_first_order_lag",),
        profile_ids=("first_order_lag",),
        citation_refs=({"source_id": "source-meta"},),
        score=1.0,
        dense_score=1.0,
        lexical_score=1.0,
        text="Reference text.",
    )

    class Index:
        def retrieve(self, request):
            del request
            return [result]

    monkeypatch.setattr(rag_cli, "load_index", lambda *args, **kwargs: Index())
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "python -m cfdc.rag",
            "query",
            "--index-dir",
            "/tmp/index",
            "--query",
            "example",
        ],
    )

    rag_cli.main()

    payload = json.loads(capsys.readouterr().out)[0]
    assert payload["artifact_group_id"] == "example"
    assert payload["language"] == "en"
    assert payload["authority"] == "advisory"
    assert payload["artifact_version"] == "1.0.0"
    assert payload["citation_refs"] == [{"source_id": "source-meta"}]


def test_rag_eval_cli_reports_bundled_suite_and_asserts_acceptance(monkeypatch, capsys):
    from cfdc.rag import __main__ as rag_cli

    positive = {
        "case_id": "positive",
        "split": "holdout",
        "role": "critic",
        "operation": "check",
        "summary": "stability",
        "relevant_artifact_group_ids": ["open_loop_stability"],
        "expected_language": "en",
    }
    negative = {
        "case_id": "negative",
        "split": "holdout",
        "role": "critic",
        "operation": "check",
        "summary": "weather",
        "expected_empty": True,
    }
    pack = SimpleNamespace(
        evaluation={
            "cases": [positive, negative],
            "datasets": [
                {"dataset_id": "en", "cases": [positive]},
                {"dataset_id": "challenge", "cases": [positive, negative]},
            ],
        },
        evaluation_metadata={
            "acceptance": {
                "artifact_group_recall_at_4_min": 0.9,
                "artifact_group_mrr_min": 0.8,
                "irrelevant_result_rate_max": 0.25,
                "negative_query_false_positive_rate_max": 0.05,
                "artifact_group_duplicate_rate_max": 0.0,
                "provenance_resolution_rate_min": 1.0,
                "preferred_language_hit_rate_min": 0.9,
                "bilingual_group_duplicate_rate_max": 0.0,
                "override_error_rate_max": 0.0,
            }
        },
    )

    class Index:
        index_snapshot = "snapshot-quality"

        def retrieve(self, request, limit=4):
            del limit
            if request.summary == "weather":
                return []
            return [
                SearchResult(
                    text="reference",
                    source_path="card.md",
                    source_id="a" * 64,
                    content_hash="b" * 64,
                    artifact_group_id="open_loop_stability",
                    source_kind="curated_pack",
                    language="en",
                    citation_refs=(
                        {
                            "source_id": "source",
                            "url": "https://example.test/source",
                            "license": "metadata-only",
                        },
                    ),
                )
            ]

    monkeypatch.setattr(rag_cli, "load_index", lambda *args, **kwargs: Index())
    monkeypatch.setattr(rag_cli, "load_knowledge_pack", lambda: pack, raising=False)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "python -m cfdc.rag",
            "eval",
            "--index-dir",
            "/tmp/index",
            "--bundled",
            "--suite",
            "challenge",
            "--split",
            "holdout",
            "--assert-acceptance",
        ],
    )

    rag_cli.main()

    payload = json.loads(capsys.readouterr().out)
    assert payload["snapshot"] == "snapshot-quality"
    assert set(payload["reports"]) == {"challenge"}
    assert payload["combined"]["cases"] == 2
    assert payload["passed"] is True


def test_rag_eval_cli_assert_acceptance_exits_nonzero(monkeypatch, capsys):
    from cfdc.rag import __main__ as rag_cli

    case = {
        "case_id": "miss",
        "split": "holdout",
        "role": "critic",
        "operation": "check",
        "summary": "stability",
        "relevant_artifact_group_ids": ["open_loop_stability"],
    }
    pack = SimpleNamespace(
        evaluation={
            "cases": [case],
            "datasets": [{"dataset_id": "en", "cases": [case]}],
        },
        evaluation_metadata={
            "acceptance": {
                "artifact_group_recall_at_4_min": 0.9,
                "artifact_group_mrr_min": 0.8,
            }
        },
    )

    class Index:
        index_snapshot = "snapshot-quality"

        def retrieve(self, request, limit=4):
            del request, limit
            return []

    monkeypatch.setattr(rag_cli, "load_index", lambda *args, **kwargs: Index())
    monkeypatch.setattr(rag_cli, "load_knowledge_pack", lambda: pack, raising=False)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "python -m cfdc.rag",
            "eval",
            "--index-dir",
            "/tmp/index",
            "--bundled",
            "--assert-acceptance",
        ],
    )

    with pytest.raises(SystemExit) as caught:
        rag_cli.main()

    assert caught.value.code == 1
    assert json.loads(capsys.readouterr().out)["passed"] is False
