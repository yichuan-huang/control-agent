from __future__ import annotations

import json
from pathlib import Path

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


def test_app_launches_same_origin_api_with_explicit_local_defaults(monkeypatch):
    import app

    calls = []
    monkeypatch.setattr(
        app.uvicorn,
        "run",
        lambda application, **kwargs: calls.append((application, kwargs)),
    )
    assert app.main([]) == 0
    assert calls[0][1] == {
        "host": "127.0.0.1",
        "port": 7860,
        "workers": 1,
        "access_log": False,
    }
    assert calls[0][0].state.rag.status().status == "error"


def test_http_shell_and_config_remain_available_while_rag_prepares_or_fails(
    tmp_path, monkeypatch
):
    from threading import Event
    from time import monotonic, sleep
    from uuid import uuid4

    from fastapi.testclient import TestClient

    from cfdc.web import runtime
    from cfdc.web.api import create_app
    from cfdc.web.drafts import case_draft

    started, release = Event(), Event()

    def prepare(*args):
        started.set()
        assert release.wait(10)
        raise runtime.BuiltinRAGStartupError("private dependency detail")

    monkeypatch.setattr(runtime, "prepare_builtin_rag_index", prepare)
    frontend = tmp_path / "frontend"
    frontend.mkdir()
    (frontend / "index.html").write_text(
        "<html><body>CFDC application shell</body></html>"
    )
    application = create_app(
        session_dir=tmp_path / "sessions",
        runtime_dir=tmp_path / "web",
        frontend_dir=frontend,
    )
    with TestClient(application, base_url="http://127.0.0.1:7860") as client:
        assert started.wait(5)
        try:
            for expected in ("preparing", "error"):
                config = client.get("/api/v1/config")
                assert config.status_code == 200
                assert config.json()["rag"]["status"] == expected
                assert "private dependency detail" not in config.text
                assert client.get("/").status_code == 200
                response = client.post(
                    "/api/v1/tasks",
                    json={
                        "request_id": str(uuid4()),
                        "draft": case_draft("dc_motor_speed_v1"),
                        "confirmed": True,
                        "use_rag": True,
                    },
                )
                assert response.status_code == 409
                assert response.json()["error"]["code"] == "rag_not_ready"
                assert not list((tmp_path / "sessions").glob("*.json"))
                release.set()
                deadline = monotonic() + 5
                while application.state.rag.status().status == "preparing":
                    assert monotonic() < deadline
                    sleep(0.01)
        finally:
            release.set()


@pytest.mark.parametrize(
    ("failure", "hint"),
    [
        (ModuleNotFoundError("private missing module"), "uv sync --locked"),
        (PermissionError("private path"), "目录权限"),
    ],
)
def test_rag_runtime_reports_safe_recovery_for_classified_failure(
    tmp_path, monkeypatch, failure, hint
):
    from time import monotonic, sleep

    from cfdc.web import rag_startup, runtime

    def prepare(*args):
        raise rag_startup._safe_startup_error(failure, phase="build")

    monkeypatch.setattr(runtime, "prepare_builtin_rag_index", prepare)
    rag = runtime.RAGRuntime(tmp_path / "index")
    rag.start()
    deadline = monotonic() + 5
    while rag.status().status == "preparing":
        assert monotonic() < deadline
        sleep(0.01)
    assert hint in rag.status().message
    assert "private" not in rag.status().message
    assert rag.options(False) == {"use_rag": False}
