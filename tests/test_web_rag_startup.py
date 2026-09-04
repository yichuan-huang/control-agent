from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest


class RecordingEncoder:
    model_name = "intfloat/multilingual-e5-small"
    model_revision = "614241f622f53c4eeff9890bdc4f31cfecc418b3"

    def __init__(self) -> None:
        self.query_texts: list[str] = []

    def encode(self, texts, *, is_query=False):
        if isinstance(texts, str):
            texts = [texts]
        if is_query:
            self.query_texts.extend(texts)
        vocabulary = ("stability", "delay", "damping", "mimo", "qualification")
        return np.asarray(
            [[text.casefold().count(word) for word in vocabulary] for text in texts],
            dtype=float,
        )


def test_preflight_builds_only_builtin_knowledge_and_warms_encoder(tmp_path: Path):
    from cfdc.web.rag_startup import prepare_builtin_rag_index

    encoder = RecordingEncoder()
    prepared = prepare_builtin_rag_index(tmp_path / "index", encoder=encoder)

    manifest = json.loads(
        (prepared.index_dir / prepared.snapshot / "manifest.json").read_text(
            encoding="utf-8"
        )
    )
    assert manifest["schema_version"] == "cfdc-rag/v3"
    assert manifest["retrieval_policy_version"] == "cfdc-retrieval/v2"
    assert manifest["retrieval_policy_fingerprint"]
    assert manifest["knowledge_pack"]["pack_id"] == "cfdc-control-foundations"
    assert {item["kind"] for item in manifest["source_files"]} == {
        "builtin_registry",
        "curated_pack",
    }
    assert encoder.query_texts == ["control-system knowledge readiness"]


def test_preflight_reuses_matching_snapshot_and_rewarms_encoder(tmp_path: Path):
    from cfdc.web.rag_startup import prepare_builtin_rag_index

    first = prepare_builtin_rag_index(tmp_path / "index", encoder=RecordingEncoder())
    second_encoder = RecordingEncoder()

    second = prepare_builtin_rag_index(tmp_path / "index", encoder=second_encoder)

    assert second.snapshot == first.snapshot
    assert sorted(
        path.name
        for path in (tmp_path / "index").iterdir()
        if path.is_dir() and path.name.startswith("snapshot-")
    ) == [first.snapshot]
    assert second_encoder.query_texts == ["control-system knowledge readiness"]


def test_preflight_rebuilds_v2_snapshot_without_rewriting_it(tmp_path: Path):
    from cfdc.web.rag_startup import prepare_builtin_rag_index

    first = prepare_builtin_rag_index(tmp_path / "index", encoder=RecordingEncoder())
    old_manifest_path = first.index_dir / first.snapshot / "manifest.json"
    old_manifest = json.loads(old_manifest_path.read_text(encoding="utf-8"))
    old_manifest["schema_version"] = "cfdc-rag/v2"
    old_manifest_path.write_text(
        json.dumps(old_manifest, ensure_ascii=False, sort_keys=True, indent=2),
        encoding="utf-8",
    )

    second = prepare_builtin_rag_index(tmp_path / "index", encoder=RecordingEncoder())

    assert second.snapshot != first.snapshot
    assert (
        json.loads(old_manifest_path.read_text(encoding="utf-8"))["schema_version"]
        == "cfdc-rag/v2"
    )
    assert (
        json.loads(
            (second.index_dir / second.snapshot / "manifest.json").read_text(
                encoding="utf-8"
            )
        )["schema_version"]
        == "cfdc-rag/v3"
    )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("embedding_model", "different-encoder"),
        ("knowledge_pack.pack_id", "different-pack"),
        ("retrieval_policy.relevance_threshold", 0.99),
        ("retrieval_policy_version", "cfdc-retrieval/v1"),
        ("retrieval_policy_fingerprint", "0" * 64),
        ("retrieval_policy.semantic_query_fields", ["summary"]),
        ("retrieval_policy.registry_candidate_policy", "dense"),
        ("retrieval_policy.max_curated_group_results", 4),
    ],
)
def test_preflight_rebuilds_configuration_mismatches(tmp_path: Path, field: str, value):
    from cfdc.web.rag_startup import prepare_builtin_rag_index

    first = prepare_builtin_rag_index(tmp_path / "index", encoder=RecordingEncoder())
    old_manifest_path = first.index_dir / first.snapshot / "manifest.json"
    old_manifest = json.loads(old_manifest_path.read_text(encoding="utf-8"))
    target = old_manifest
    parts = field.split(".")
    for part in parts[:-1]:
        target = target[part]
    target[parts[-1]] = value
    old_manifest_path.write_text(
        json.dumps(old_manifest, ensure_ascii=False, sort_keys=True, indent=2),
        encoding="utf-8",
    )

    second = prepare_builtin_rag_index(tmp_path / "index", encoder=RecordingEncoder())

    assert second.snapshot != first.snapshot
    assert old_manifest_path.is_file()


def test_preflight_rebuilds_a_corrupt_snapshot_without_deleting_it(tmp_path: Path):
    from cfdc.web.rag_startup import prepare_builtin_rag_index

    first = prepare_builtin_rag_index(tmp_path / "index", encoder=RecordingEncoder())
    old_vectors = first.index_dir / first.snapshot / "vectors.npy"
    old_vectors.write_bytes(b"corrupt")

    second = prepare_builtin_rag_index(tmp_path / "index", encoder=RecordingEncoder())

    assert second.snapshot != first.snapshot
    assert old_vectors.read_bytes() == b"corrupt"


def test_preflight_sanitizes_pack_validation_failure(tmp_path: Path, monkeypatch):
    from cfdc.web import rag_startup

    def invalid_pack():
        raise ValueError("private-local-path")

    monkeypatch.setattr(rag_startup, "load_knowledge_pack", invalid_pack)

    with pytest.raises(
        rag_startup.BuiltinRAGStartupError,
        match="内置 RAG 知识包校验失败",
    ) as caught:
        rag_startup.prepare_builtin_rag_index(
            tmp_path / "index", encoder=RecordingEncoder()
        )

    assert "private-local-path" not in str(caught.value)


def test_app_prepares_rag_before_building_and_launching_webui(monkeypatch):
    import app

    events: list[str] = []
    prepared = SimpleNamespace(index_dir=Path("output/rag-index"), snapshot="snap")

    class FakeDemo:
        def queue(self, *, default_concurrency_limit):
            assert default_concurrency_limit == 2
            events.append("queue")
            return self

        def launch(self, **kwargs):
            assert kwargs["server_name"] == "127.0.0.1"
            assert kwargs["server_port"] == 7860
            events.append("launch")

    def prepare():
        events.append("prepare")
        return prepared

    def build(*, prepared_rag):
        assert prepared_rag is prepared
        events.append("build")
        return FakeDemo()

    monkeypatch.setattr(app, "prepare_builtin_rag_index", prepare)
    monkeypatch.setattr(app, "build_app", build)

    assert app.main([]) == 0
    assert events == ["prepare", "build", "queue", "launch"]


def test_app_does_not_create_or_launch_webui_when_rag_preflight_fails(
    monkeypatch, capsys
):
    import app
    from cfdc.web.rag_startup import BuiltinRAGStartupError

    built = False

    def fail_prepare():
        raise BuiltinRAGStartupError(
            "内置 RAG 依赖未安装；请执行 uv sync --locked --extra rag。"
        )

    def build(*, prepared_rag):
        nonlocal built
        built = True
        return prepared_rag

    monkeypatch.setattr(app, "prepare_builtin_rag_index", fail_prepare)
    monkeypatch.setattr(app, "build_app", build)

    assert app.main([]) == 1
    assert built is False
    assert "uv sync --locked --extra rag" in capsys.readouterr().err
