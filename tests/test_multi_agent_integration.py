from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from cfdc.agents import AgentRole, AgentRuntime, RetrievalSnippet
from cfdc.web.service import build_adapter


@dataclass
class _Row:
    source_id: str
    text: str
    score: float = 0.9


class _Retriever:
    index_snapshot = "snapshot-test"

    def search(self, query, limit=4):
        assert query
        assert limit == 4
        return [
            _Row("manual:p3", "The method is valid near the stated operating point.")
        ]


class _IndexEncoder:
    model_name = "test-encoder"

    def __init__(self, *args, **kwargs):
        del args, kwargs

    def encode(self, texts, **kwargs):
        del kwargs
        if isinstance(texts, str):
            texts = [texts]
        return np.asarray(
            [
                [text.lower().count("method"), text.lower().count("heater")]
                for text in texts
            ],
            dtype=float,
        )


class _Adapter:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.base_url = "https://provider.example/v1"
        self.model = "test-model"
        self.api_key = "secret"

    def complete_agent(self, request):
        assert request.role is AgentRole.CRITIC
        return {"decision": "pass", "feedback": ""}


def test_web_factory_constructs_current_transport_directly(monkeypatch):
    monkeypatch.setattr("cfdc.web.service.OpenAICompatibleAdapter", _Adapter)

    multi = build_adapter(
        True,
        "https://provider.example/v1",
        "test-model",
        "secret",
        use_rag=False,
    )

    assert isinstance(multi, _Adapter)
    assert multi.retriever is None


def test_retrieval_is_added_to_the_exact_provider_message():
    captured = []
    runtime = AgentRuntime(
        lambda request: captured.append(request) or {"decision": "pass"}
    )
    record = runtime.execute(
        AgentRole.CRITIC,
        stage="review",
        request={"candidate": "bounded gain"},
        retrieval=[
            RetrievalSnippet(
                source_id="manual:p3",
                content="The method is valid near the stated operating point.",
            )
        ],
    )
    serialized = "\n".join(message["content"] for message in captured[0].messages)
    assert "manual:p3" in serialized
    assert "The method is valid near the stated operating point." in serialized
    assert record.messages == captured[0].messages


def test_factory_loads_a_snapshot_only_when_rag_is_enabled(tmp_path, monkeypatch):
    from cfdc.rag import build_index

    source = tmp_path / "sources"
    source.mkdir()
    (source / "manual.md").write_text("# Method\n\nA heater method.", encoding="utf-8")
    index_dir = tmp_path / "rag"
    build_index(source, index_dir, encoder=_IndexEncoder(), include_builtin=False)
    monkeypatch.setattr("cfdc.rag.core.SentenceTransformerEncoder", _IndexEncoder)
    monkeypatch.setattr("cfdc.web.service.OpenAICompatibleAdapter", _Adapter)

    enabled = build_adapter(
        True,
        "https://provider.example/v1",
        "test-model",
        "secret",
        rag_index_dir=index_dir,
        use_rag=True,
    )
    disabled = build_adapter(
        True,
        "https://provider.example/v1",
        "test-model",
        "secret",
        rag_index_dir=index_dir,
        use_rag=False,
    )

    assert enabled.rag_enabled is True
    assert enabled.retriever.index_snapshot.startswith("snapshot-")
    assert disabled.rag_enabled is False
    assert disabled.retriever is None
