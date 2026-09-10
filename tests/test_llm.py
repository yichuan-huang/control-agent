from __future__ import annotations

from types import SimpleNamespace

import pytest

from cfdc.llm import OpenAICompatibleAdapter, parse_json_content


def _request():
    return SimpleNamespace(
        prompt="Extract open_loop_stability", role=SimpleNamespace(value="diagnosis")
    )


def test_parse_json_content():
    assert parse_json_content('{"complete": true}') == {"complete": True}


def test_openai_compatible_adapter_uses_sdk(monkeypatch):
    calls = {}

    class FakeCompletions:
        def create(self, **kwargs):
            calls["completion"] = kwargs
            message = type("Message", (), {"content": '{"complete": true}'})()
            choice = type("Choice", (), {"message": message})()
            return type("Response", (), {"choices": [choice]})()

    class FakeOpenAI:
        def __init__(self, **kwargs):
            calls["client"] = kwargs
            completions = FakeCompletions()
            self.chat = type("Chat", (), {"completions": completions})()

    monkeypatch.setattr("cfdc.llm.OpenAI", FakeOpenAI)
    adapter = OpenAICompatibleAdapter(
        base_url="https://example.test/v1/chat/completions",
        model="test-model",
        api_key="test-key",
        timeout_s=12.0,
        max_tokens=321,
    )

    result = adapter.complete_agent(_request())

    assert result == {"complete": True}
    assert calls["client"] == {
        "api_key": "test-key",
        "base_url": "https://example.test/v1",
        "timeout": 12.0,
    }
    assert calls["completion"]["model"] == "test-model"
    assert calls["completion"]["temperature"] == 0.0
    assert calls["completion"]["max_tokens"] == 900
    assert calls["completion"]["response_format"] == {"type": "json_object"}
    assert "extra_body" not in calls["completion"]
    assert calls["completion"]["messages"][1]["role"] == "user"
    assert "open_loop_stability" in calls["completion"]["messages"][1]["content"]


def test_openai_compatible_adapter_requires_explicit_provider_configuration(
    monkeypatch,
):
    for name in [
        "CFDC_LLM_BASE_URL",
        "CONTROL_PROJECT_LLM_BASE_URL",
        "OPENAI_BASE_URL",
        "CFDC_LLM_MODEL",
        "CONTROL_PROJECT_LLM_MODEL",
        "OPENAI_MODEL",
        "CFDC_LLM_API_KEY",
        "CONTROL_PROJECT_LLM_API_KEY",
        "OPENAI_API_KEY",
    ]:
        monkeypatch.delenv(name, raising=False)

    with pytest.raises(ValueError, match="base URL, model, API key"):
        OpenAICompatibleAdapter()


def test_openai_compatible_adapter_reads_non_openai_provider_environment(monkeypatch):
    calls = {}

    class FakeOpenAI:
        def __init__(self, **kwargs):
            calls.update(kwargs)

    monkeypatch.setattr("cfdc.llm.OpenAI", FakeOpenAI)
    monkeypatch.setenv("CFDC_LLM_BASE_URL", "http://localhost:11434/v1")
    monkeypatch.setenv("CFDC_LLM_MODEL", "qwen2.5:14b")
    monkeypatch.setenv("CFDC_LLM_API_KEY", "ollama")

    adapter = OpenAICompatibleAdapter()

    assert adapter.base_url == "http://localhost:11434/v1"
    assert adapter.model == "qwen2.5:14b"
    assert calls == {
        "api_key": "ollama",
        "base_url": "http://localhost:11434/v1",
        "timeout": 60.0,
    }


def test_deepseek_adapter_disables_thinking_for_strict_json(monkeypatch):
    calls = {}

    class FakeCompletions:
        def create(self, **kwargs):
            calls["completion"] = kwargs
            message = type("Message", (), {"content": '{"complete": true}'})()
            choice = type("Choice", (), {"message": message, "finish_reason": "stop"})()
            return type("Response", (), {"choices": [choice]})()

    class FakeOpenAI:
        def __init__(self, **kwargs):
            completions = FakeCompletions()
            self.chat = type("Chat", (), {"completions": completions})()

    monkeypatch.setattr("cfdc.llm.OpenAI", FakeOpenAI)
    adapter = OpenAICompatibleAdapter(
        base_url="https://api.deepseek.com",
        model="deepseek-v4-flash",
        api_key="test-key",
    )

    result = adapter.complete_agent(_request())

    assert result == {"complete": True}
    assert calls["completion"]["extra_body"] == {"thinking": {"type": "disabled"}}


def test_openai_compatible_adapter_explains_empty_content(monkeypatch):
    class FakeCompletions:
        def create(self, **kwargs):
            message = type(
                "Message",
                (),
                {"content": "", "reasoning_content": "unfinished reasoning"},
            )()
            choice = type(
                "Choice",
                (),
                {"message": message, "finish_reason": "length"},
            )()
            return type("Response", (), {"choices": [choice]})()

    class FakeOpenAI:
        def __init__(self, **kwargs):
            completions = FakeCompletions()
            self.chat = type("Chat", (), {"completions": completions})()

    monkeypatch.setattr("cfdc.llm.OpenAI", FakeOpenAI)
    adapter = OpenAICompatibleAdapter(
        base_url="https://example.test/v1",
        model="test-model",
        api_key="test-key",
    )

    with pytest.raises(ValueError, match="finish_reason='length'"):
        adapter.complete_agent(_request())


def test_agent_transport_preserves_exact_messages_and_telemetry(monkeypatch):
    from cfdc.agents import AgentRole, AgentRuntime

    captured = []

    def complete(**kwargs):
        captured.append(kwargs)
        return SimpleNamespace(
            id="call-1",
            usage=SimpleNamespace(
                prompt_tokens=12, completion_tokens=4, total_tokens=16
            ),
            choices=[
                SimpleNamespace(message=SimpleNamespace(content='{"decision":"pass"}'))
            ],
        )

    monkeypatch.setattr(
        "cfdc.llm.OpenAI",
        lambda **kwargs: SimpleNamespace(
            chat=SimpleNamespace(completions=SimpleNamespace(create=complete))
        ),
    )
    adapter = OpenAICompatibleAdapter(
        base_url="http://localhost:11434/v1", model="gemma4:e4b", api_key="ollama"
    )
    record = AgentRuntime(adapter.complete_agent).execute(
        AgentRole.CRITIC, stage="review", request={"candidate": "safe"}
    )
    assert record.messages == tuple(captured[0]["messages"])
    assert record.token_usage == {
        "prompt_tokens": 12,
        "completion_tokens": 4,
        "total_tokens": 16,
    }
    assert record.provider_call_id == "call-1"
    assert adapter.last_call_elapsed_ms >= 0


@pytest.mark.parametrize("text", ["[]", "null", '"text"'])
def test_json_transport_rejects_non_objects(text):
    with pytest.raises(TypeError, match="JSON object"):
        parse_json_content(text)
