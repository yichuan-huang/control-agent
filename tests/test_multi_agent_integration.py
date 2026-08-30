from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pytest

from cfdc.agents import AgentRole, CompositeAgentAdapter
from cfdc.lab.llm import (
    GainProposalContext,
    MinimalStabilityEvidence,
    build_gain_proposal_messages,
)
from cfdc.web.service import build_adapter
from main import parse_args


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

    def propose_gain_update(self, context):
        return {
            "new_parameters": {
                name: value * 0.95 for name, value in context.current_parameters.items()
            },
            "rationale": "stability-only adjustment",
        }


def _gain_context() -> GainProposalContext:
    return GainProposalContext(
        session_id="session-1",
        revision=1,
        base_trial_iteration=1,
        controller_kind="pi",
        architecture_sha256="0" * 64,
        current_parameters={"kp": 1.0},
        tunable_whitelist=["kp"],
        parameter_bounds={"kp": (0.0, 2.0)},
        last_stability_evidence=MinimalStabilityEvidence(
            status="stable",
            analysis_domain="continuous",
            normalized_margin=0.2,
            tail_error_envelope_contraction=0.8,
            saturation_fraction=0.0,
            hard_failure=False,
        ),
    )


def test_multi_factory_wraps_existing_adapter_and_single_is_explicit(monkeypatch):
    monkeypatch.setattr("cfdc.web.service.OpenAICompatibleDiagnosticAdapter", _Adapter)

    single = build_adapter(
        True,
        "https://provider.example/v1",
        "test-model",
        "secret",
        agent_mode="single",
        use_rag=False,
    )
    multi = build_adapter(
        True,
        "https://provider.example/v1",
        "test-model",
        "secret",
        agent_mode="multi",
        use_rag=False,
    )

    assert isinstance(single, _Adapter)
    assert isinstance(multi, CompositeAgentAdapter)
    assert isinstance(multi.adapter, _Adapter)


def test_gain_retrieval_is_added_to_the_exact_provider_message(monkeypatch):
    adapter = _Adapter()
    wrapped = CompositeAgentAdapter(
        adapter,
        # The critic response is used by the candidate review gate.
        runtime=__import__("cfdc.agents", fromlist=["AgentRuntime"]).AgentRuntime(
            adapter.complete_agent
        ),
        retriever=_Retriever(),
    )
    context = wrapped.prepare_gain_context(_gain_context())
    messages = build_gain_proposal_messages(context)
    serialized = "\n".join(message["content"] for message in messages)

    assert "manual:p3" in serialized
    assert "The method is valid near the stated operating point." in serialized
    assert context.agent_retrieved_references[0]["source_id"] == "manual:p3"


def test_cli_exposes_agent_and_rag_switches(tmp_path):
    args = parse_args(
        [
            "--agent-mode",
            "single",
            "--rag-index",
            str(tmp_path / "rag-index"),
            "--no-rag",
        ]
    )

    assert args.agent_mode == "single"
    assert args.rag_index == tmp_path / "rag-index"
    assert args.no_rag is True


def test_invalid_agent_mode_is_rejected():
    with pytest.raises(SystemExit):
        parse_args(["--agent-mode", "supervisor"])


def test_factory_loads_a_snapshot_only_when_rag_is_enabled(tmp_path, monkeypatch):
    from cfdc.rag import build_index

    source = tmp_path / "sources"
    source.mkdir()
    (source / "manual.md").write_text("# Method\n\nA heater method.", encoding="utf-8")
    index_dir = tmp_path / "rag"
    build_index(source, index_dir, encoder=_IndexEncoder(), include_builtin=False)
    monkeypatch.setattr("cfdc.rag.core.SentenceTransformerEncoder", _IndexEncoder)
    monkeypatch.setattr("cfdc.web.service.OpenAICompatibleDiagnosticAdapter", _Adapter)

    enabled = build_adapter(
        True,
        "https://provider.example/v1",
        "test-model",
        "secret",
        agent_mode="multi",
        rag_index_dir=index_dir,
        use_rag=True,
    )
    disabled = build_adapter(
        True,
        "https://provider.example/v1",
        "test-model",
        "secret",
        agent_mode="multi",
        rag_index_dir=index_dir,
        use_rag=False,
    )

    assert enabled.rag_enabled is True
    assert enabled.retriever.index_snapshot.startswith("snapshot-")
    assert disabled.rag_enabled is False
    assert disabled.retriever is None
