from __future__ import annotations

import json
import math
import shutil
import sys
from pathlib import Path

import numpy as np

from cfdc.knowledge import RetrievalRequest
from cfdc.rag import SearchResult, build_index, evaluate_retrieval
from cfdc.rag.core import _fts_query, _python_lexical_score
from cfdc.rag.knowledge_pack import load_knowledge_pack


class BilingualKeywordEncoder:
    model_name = "test-bilingual"
    model_revision = "test-revision"

    def encode(self, texts, *, is_query=False):
        del is_query
        if isinstance(texts, str):
            texts = [texts]
        vocabulary = (
            "stability",
            "open-loop",
            "mimo",
            "pairing",
            "稳定",
            "开环",
            "耦合",
            "配对",
        )
        return np.asarray(
            [[text.casefold().count(word) for word in vocabulary] for text in texts],
            dtype=float,
        )


class ConstantEncoder:
    model_name = "test-constant"
    model_revision = "test-revision"

    def encode(self, texts, *, is_query=False):
        del is_query
        if isinstance(texts, str):
            texts = [texts]
        return np.ones((len(texts), 1), dtype=float)


class AsymmetricLanguageEncoder:
    model_name = "test-asymmetric-language"
    model_revision = "test-revision"

    def encode(self, texts, *, is_query=False):
        if isinstance(texts, str):
            texts = [texts]
        vectors = []
        for text in texts:
            if is_query:
                vectors.append([1.0, 0.0])
            elif "Artifact group: pulse_signed_gain" not in text:
                vectors.append([0.0, 1.0])
            elif "Knowledge card: Pulse-based" in text:
                vectors.append([1.0, 0.0])
            else:
                vectors.append([0.8, 0.6])
        return np.asarray(vectors, dtype=float)


class CorroboratedScenarioEncoder:
    model_name = "test-corroborated-scenario"
    model_revision = "test-revision"

    def encode(self, texts, *, is_query=False):
        if isinstance(texts, str):
            texts = [texts]
        vectors = []
        for text in texts:
            if is_query:
                vectors.append([1.0, 0.0])
            elif "Artifact group: open_loop_stability" in text:
                vectors.append([0.81, 0.58643])
            else:
                vectors.append([0.0, 1.0])
        return np.asarray(vectors, dtype=float)


def _copied_pack_without_mimo_zh(tmp_path: Path) -> Path:
    source = Path(__file__).parents[1] / "cfdc/resources/knowledge_pack/v1"
    target = tmp_path / "pack"
    shutil.copytree(source, target)
    manifest_path = target / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["artifacts"] = [
        item
        for item in manifest["artifacts"]
        if item["artifact_id"] != "mimo_pairing.zh"
    ]
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return target


def test_bundled_pack_has_one_english_and_chinese_card_per_group():
    pack = load_knowledge_pack()

    assert pack.version == "1.3.0"
    assert len(pack.artifacts) == 24
    assert {artifact.language for artifact in pack.artifacts} == {"en", "zh"}
    assert {
        (artifact.artifact_group_id, artifact.version)
        for artifact in pack.artifacts
        if artifact.language == "en"
    } == {
        (artifact.artifact_group_id, artifact.version)
        for artifact in pack.artifacts
        if artifact.language == "zh"
    }
    assert len(pack.evaluation["cases"]) == 192
    assert sum(case["split"] == "dev" for case in pack.evaluation["cases"]) == 96
    assert sum(case["split"] == "holdout" for case in pack.evaluation["cases"]) == 96


def test_search_result_exposes_scope_and_validity_for_quality_audit(tmp_path):
    index = build_index(
        None,
        tmp_path / "index",
        encoder=BilingualKeywordEncoder(),
        include_builtin=False,
        relevance_threshold=0.0,
    )

    result = index.retrieve(
        RetrievalRequest(
            role="diagnosis",
            operation="diagnose",
            stage="diagnosis",
            summary="open-loop stability evidence",
        )
    )[0]
    dumped = result.model_dump()

    assert dumped["roles"]
    assert dumped["stages"]
    assert dumped["valid_from"] == "2026-09-03"
    assert dumped["valid_until"] is None


def test_each_bilingual_chunk_indexes_both_group_titles(tmp_path):
    index = build_index(
        None,
        tmp_path / "index",
        encoder=BilingualKeywordEncoder(),
        include_builtin=False,
        relevance_threshold=0.0,
    )
    rows = [
        row for row in index.metadata() if row["artifact_group_id"] == "mimo_pairing"
    ]

    assert all("MIMO coupling, local gain matrices" in row["text"] for row in rows)
    assert all("MIMO 耦合、局部增益矩阵" in row["text"] for row in rows)


def test_retrieval_request_language_is_backward_compatible_and_auditable():
    automatic = RetrievalRequest(role="critic", operation="check", summary="稳定性")
    explicit = RetrievalRequest(
        role="critic", operation="check", summary="stability", language="zh"
    )

    assert automatic.language == "auto"
    assert automatic.preferred_language() == "zh"
    assert automatic.model_dump()["language"] == "auto"
    assert explicit.preferred_language() == "zh"


def test_auto_and_explicit_language_preference_avoid_bilingual_duplicates(tmp_path):
    index = build_index(
        None,
        tmp_path / "index",
        encoder=BilingualKeywordEncoder(),
        include_builtin=False,
        relevance_threshold=0.0,
    )

    chinese = index.retrieve(
        RetrievalRequest(
            role="diagnosis", operation="diagnose", summary="开环稳定性证据"
        )
    )
    english = index.retrieve(
        RetrievalRequest(
            role="diagnosis",
            operation="diagnose",
            summary="open-loop stability evidence",
        )
    )
    override = index.retrieve(
        RetrievalRequest(
            role="diagnosis",
            operation="diagnose",
            summary="open-loop stability evidence",
            language="zh",
        )
    )

    assert chinese and {item.language for item in chinese} == {"zh"}
    assert english and {item.language for item in english} == {"en"}
    assert override and {item.language for item in override} == {"zh"}
    assert all(
        len({item.artifact_group_id for item in rows}) == len(rows)
        for rows in (chinese, english, override)
    )


def test_missing_preferred_group_falls_back_without_cross_identity_leakage(tmp_path):
    index = build_index(
        None,
        tmp_path / "index",
        encoder=BilingualKeywordEncoder(),
        include_builtin=False,
        knowledge_pack_dir=_copied_pack_without_mimo_zh(tmp_path),
        relevance_threshold=0.0,
    )

    results = index.retrieve(
        RetrievalRequest(
            role="modeling",
            operation="feature",
            stage="model",
            profile_id="mimo_2x2_coupled",
            summary="MIMO coupling and pairing",
            language="zh",
        )
    )
    target = next(item for item in results if item.artifact_group_id == "mimo_pairing")

    assert target.language == "en"
    assert len({item.artifact_group_id for item in results}) == len(results)


def test_qualified_fallback_group_projects_to_existing_preferred_language(tmp_path):
    index = build_index(
        None,
        tmp_path / "index",
        encoder=AsymmetricLanguageEncoder(),
        include_builtin=False,
        relevance_threshold=0.9,
    )

    results = index.retrieve(
        RetrievalRequest(
            role="critic",
            operation="check",
            stage="review",
            summary="Use a bounded pulse to determine signed input authority.",
            language="zh",
        )
    )

    target = next(
        result for result in results if result.artifact_group_id == "pulse_signed_gain"
    )
    assert target.language == "zh"


def test_dense_near_threshold_requires_strong_lexical_scenario_corroboration(tmp_path):
    index = build_index(
        None,
        tmp_path / "index",
        encoder=CorroboratedScenarioEncoder(),
        include_builtin=False,
        relevance_threshold=0.845,
    )

    results = index.retrieve(
        RetrievalRequest(
            role="critic",
            operation="check",
            stage="review",
            summary=(
                "Does the open-loop response settle, drift, or diverge near the "
                "operating point?"
            ),
        )
    )

    assert results[0].artifact_group_id == "open_loop_stability"


def test_neutral_registry_artifacts_remain_eligible_for_explicit_language(tmp_path):
    index = build_index(
        None,
        tmp_path / "index",
        encoder=BilingualKeywordEncoder(),
        relevance_threshold=0.0,
    )

    results = index.retrieve(
        RetrievalRequest(
            role="controller",
            operation="controller",
            stage="controller",
            profile_id="first_order_lag",
            summary="first_order_lag",
            language="zh",
        )
    )

    assert any(item.language == "und" for item in results)


def test_bilingual_evaluator_reports_preference_and_override_errors():
    class Index:
        index_snapshot = "snapshot-bilingual"

        def retrieve(self, request, limit=4):
            del limit
            language = "zh" if request.summary != "wrong override" else "en"
            return [
                SearchResult(
                    text="reference",
                    source_path=f"cards/{language}/stability.md",
                    source_id=language * 32,
                    content_hash="c" * 64,
                    artifact_group_id="open_loop_stability",
                    language=language,
                )
            ]

    report = evaluate_retrieval(
        Index(),
        [
            {
                "role": "critic",
                "operation": "check",
                "summary": "稳定性",
                "relevant_artifact_group_ids": ["open_loop_stability"],
                "expected_language": "zh",
            },
            {
                "role": "critic",
                "operation": "check",
                "summary": "stability",
                "language": "zh",
                "relevant_artifact_group_ids": ["open_loop_stability"],
                "expected_language": "zh",
            },
            {
                "role": "critic",
                "operation": "check",
                "summary": "wrong override",
                "language": "zh",
                "relevant_artifact_group_ids": ["open_loop_stability"],
                "expected_language": "zh",
            },
        ],
    )

    assert report["preferred_language_hit_rate"] == 2 / 3
    assert report["bilingual_group_duplicate_rate"] == 0.0
    assert report["override_error_rate"] == 0.5


def test_query_cli_accepts_and_preserves_language_override(monkeypatch, capsys):
    from cfdc.rag import __main__ as rag_cli

    captured = {}

    class Index:
        def retrieve(self, request):
            captured["request"] = request
            return []

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
            "stability",
            "--language",
            "zh",
        ],
    )

    rag_cli.main()

    assert captured["request"].language == "zh"
    assert json.loads(capsys.readouterr().out) == []


def test_chinese_lexical_matching_does_not_promote_shared_single_characters():
    query = "唐诗格律与押韵 qzxv"

    assert '"与"' not in _fts_query(query)
    assert '"唐诗格律与押韵"' in _fts_query(query)
    assert _python_lexical_score(query, "控制器资格审查、有界增益变化与权限") == 0
    assert _python_lexical_score("开环稳定证据", "检查开环稳定响应证据") > 0


def test_one_lexical_word_cannot_bypass_a_strict_relevance_threshold(tmp_path):
    source = tmp_path / "sources"
    source.mkdir()
    (source / "notes.md").write_text(
        "# Notes\n\nThe delta symbol is used in a damping equation.",
        encoding="utf-8",
    )
    index = build_index(
        source,
        tmp_path / "index",
        encoder=BilingualKeywordEncoder(),
        include_builtin=False,
        include_curated=False,
        relevance_threshold=0.9,
    )

    assert index.search("river delta cartography qzxv") == []


def test_same_language_curated_dense_hits_require_lexical_corroboration(tmp_path):
    index = build_index(
        None,
        tmp_path / "index",
        encoder=ConstantEncoder(),
        include_builtin=False,
        relevance_threshold=0.9,
    )

    assert (
        index.retrieve(
            RetrievalRequest(
                role="critic",
                operation="check",
                stage="review",
                summary="甲乙丙丁戊己庚辛壬癸 qzxv",
            )
        )
        == []
    )
    explicit_cross_language = index.retrieve(
        RetrievalRequest(
            role="critic",
            operation="check",
            stage="review",
            summary="检查开环稳定证据",
            language="en",
        )
    )
    assert explicit_cross_language
    assert {item.language for item in explicit_cross_language} == {"en"}


def test_dense_relevance_can_be_corroborated_by_partial_lexical_coverage(tmp_path):
    class CorroboratingEncoder:
        model_name = "test-corroborating"
        model_revision = "test-revision"

        def encode(self, texts, *, is_query=False):
            del is_query
            if isinstance(texts, str):
                texts = [texts]
            return np.asarray(
                [
                    [0.835, math.sqrt(1 - 0.835**2)]
                    if "gamma delta" in text
                    else [1.0, 0.0]
                    for text in texts
                ],
                dtype=float,
            )

    source = tmp_path / "sources"
    source.mkdir()
    (source / "notes.md").write_text("# Notes\n\nalpha beta", encoding="utf-8")
    index = build_index(
        source,
        tmp_path / "index",
        encoder=CorroboratingEncoder(),
        include_builtin=False,
        include_curated=False,
        relevance_threshold=0.84,
    )

    assert index.search("alpha beta gamma delta")
