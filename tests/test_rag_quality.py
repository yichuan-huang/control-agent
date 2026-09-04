from __future__ import annotations

import os

import pytest

from cfdc.rag import (
    SentenceTransformerEncoder,
    build_index,
    evaluate_retrieval,
    load_knowledge_pack,
)

pytestmark = pytest.mark.skipif(
    os.environ.get("CFDC_RUN_RAG_QUALITY") != "1",
    reason="set CFDC_RUN_RAG_QUALITY=1 to run the real multilingual E5 gate",
)


@pytest.fixture(scope="module")
def real_e5_bundle(tmp_path_factory):
    pack = load_knowledge_pack()
    metadata = pack.evaluation_metadata
    encoder = SentenceTransformerEncoder(
        str(metadata["embedding_model"]),
        revision=str(metadata["embedding_revision"]),
        local_files_only=True,
    )
    index = build_index(
        None,
        tmp_path_factory.mktemp("rag-quality") / "index",
        encoder=encoder,
        relevance_threshold=float(metadata["relevance_threshold"]),
    )
    return pack, index


def _assert_acceptance(report):
    assert report["artifact_group_recall_at_4"] >= 0.90
    assert report["artifact_group_mrr"] >= 0.80
    assert report["irrelevant_result_rate"] <= 0.25
    assert report["negative_query_false_positive_rate"] <= 0.05
    assert report["preferred_language_hit_rate"] >= 0.90
    assert report["override_error_rate"] == 0.0
    assert report["duplicate_rate"] == 0.0
    assert report["artifact_group_duplicate_rate"] == 0.0
    assert report["bilingual_group_duplicate_rate"] == 0.0
    assert report["provenance_resolution_rate"] == 1.0
    assert report["scope_leakage_rate"] == 0.0
    assert report["stale_result_rate"] == 0.0


def _dataset(pack, dataset_id):
    return next(
        dataset["cases"]
        for dataset in pack.evaluation["datasets"]
        if dataset["dataset_id"] == dataset_id
    )


def test_bundled_real_e5_dev_reproduces_calibrated_baseline(real_e5_bundle):
    pack, index = real_e5_bundle
    calibration_cases = [
        case for dataset_id in ("en", "zh") for case in _dataset(pack, dataset_id)
    ]

    report = evaluate_retrieval(index, calibration_cases, split="dev")

    assert report["cases"] == 48
    assert report["positive_cases"] == 36
    assert report["negative_cases"] == 12
    assert report["artifact_group_recall_at_4"] == pytest.approx(1.0)
    assert report["artifact_group_mrr"] == pytest.approx(0.9722, abs=1e-4)
    assert report["irrelevant_result_rate"] == pytest.approx(0.1273, abs=1e-4)
    assert report["negative_query_false_positive_rate"] == 0.0
    assert report["preferred_language_hit_rate"] == 1.0
    assert report["override_error_rate"] == 0.0
    assert report["artifact_group_duplicate_rate"] == 0.0
    assert report["bilingual_group_duplicate_rate"] == 0.0
    assert report["provenance_resolution_rate"] == 1.0
    assert report["scope_leakage_rate"] == 0.0
    assert report["stale_result_rate"] == 0.0


def test_bundled_real_e5_exposed_challenge_is_a_passing_regression_set(
    real_e5_bundle,
):
    pack, index = real_e5_bundle

    report = evaluate_retrieval(
        index,
        _dataset(pack, "challenge_regression"),
        split="dev",
    )

    assert report["cases"] == 48
    _assert_acceptance(report)


@pytest.mark.parametrize(
    ("dataset_id", "expected_cases"),
    [("en", 24), ("zh", 24), ("challenge", 48)],
)
def test_bundled_real_e5_holdout_suite_meets_acceptance(
    real_e5_bundle,
    dataset_id,
    expected_cases,
):
    pack, index = real_e5_bundle

    report = evaluate_retrieval(
        index,
        _dataset(pack, dataset_id),
        split="holdout",
    )

    assert report["cases"] == expected_cases
    _assert_acceptance(report)


def test_bundled_real_e5_combined_holdout_meets_acceptance(real_e5_bundle):
    pack, index = real_e5_bundle

    report = evaluate_retrieval(index, pack.evaluation["cases"], split="holdout")

    assert report["cases"] == 96
    _assert_acceptance(report)
