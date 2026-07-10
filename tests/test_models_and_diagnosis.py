import pytest

from cfdc.diagnosis import DiagnosticEngine, validate_agent_payload
from cfdc.diagnosis.engine import infer_structural_diagnosis
from cfdc.diagnosis.llm import (
    OpenAICompatibleDiagnosticAdapter,
    build_diagnostic_prompt,
    parse_json_content,
)
from cfdc.models import (
    ArchetypeClass,
    CoreFeatureArtifact,
    DelayAssessment,
    ExperimentPrimitive,
    ExperimentResult,
    ExperimentTrace,
    SignificantDelayField,
    SystemDescription,
)


def test_public_model_json_roundtrip():
    feature = CoreFeatureArtifact(
        feature_id="natural_frequency",
        value=3.0,
        lower_bound=2.9,
        upper_bound=3.1,
        confidence=0.9,
        units="rad/s",
        method="frequency_locked_matched_filter",
        source_experiment=ExperimentPrimitive.FREE_DECAY,
    )
    payload = feature.model_dump_json()
    restored = CoreFeatureArtifact.model_validate_json(payload)
    assert restored == feature


def test_experiment_result_json_roundtrip():
    result = ExperimentResult(
        primitive=ExperimentPrimitive.RAMP_STEP,
        estimates=["static_gain", "time_constant"],
        trace=ExperimentTrace(
            time_s=[0.0, 1.0, 2.0],
            signals={"input setting": [0.0, 0.5, 0.5], "measured output": [0.0, 0.4, 0.8]},
        ),
    )
    payload = result.model_dump_json()
    restored = ExperimentResult.model_validate_json(payload)
    assert restored == result


def test_significant_delay_field_roundtrip_and_consistency():
    field = SignificantDelayField(
        status="known",
        value="noticeable pause before first motion",
        assessment=DelayAssessment.SIGNIFICANT,
        confidence=0.9,
        evidence=["operator observed a pause"],
    )

    assert SignificantDelayField.model_validate_json(field.model_dump_json()) == field
    with pytest.raises(ValueError, match="unknown"):
        SignificantDelayField(
            status="unknown",
            value="delay unknown",
            assessment=DelayAssessment.SIGNIFICANT,
            confidence=0.2,
        )


@pytest.mark.parametrize(
    ("phrase", "status", "expected"),
    [
        ("significant delay likely", "known", "significant"),
        ("significant delay present", "inferred", "significant"),
        ("noticeable dead time", "known", "significant"),
        ("no significant delay reported", "known", "not_significant"),
        ("negligible delay", "inferred", "not_significant"),
        ("delay unknown", "unknown", "unknown"),
        ("not enough information about first-motion delay", "unknown", "unknown"),
    ],
)
def test_legacy_delay_synonyms_are_normalized_at_adapter_boundary(
    phrase,
    status,
    expected,
):
    description = SystemDescription(
        text="A first order process settles after a small pump change with dead time.",
        observed_outputs=["level"],
        actuators=["pump"],
    )
    payload = infer_structural_diagnosis(description).model_dump()
    payload["significant_delay"].pop("assessment")
    payload["significant_delay"].update(status=status, value=phrase)
    payload["complete"] = status != "unknown"
    payload["clarification_questions"] = (
        []
        if payload["complete"]
        else ["Is there a pause before motion?", "What is a safe test input?"]
    )

    diagnosis = validate_agent_payload(payload)

    assert diagnosis.significant_delay.assessment == expected


def test_contradictory_legacy_delay_phrase_is_rejected():
    description = SystemDescription(
        text="A first order process settles after a small pump change with dead time.",
        observed_outputs=["level"],
        actuators=["pump"],
    )
    payload = infer_structural_diagnosis(description).model_dump()
    payload["significant_delay"].pop("assessment")
    payload["significant_delay"]["value"] = (
        "no significant delay reported but significant delay present"
    )

    with pytest.raises(ValueError, match="contradictory"):
        validate_agent_payload(payload)


def test_agent_output_rejects_free_text():
    try:
        validate_agent_payload("the plant is probably stable")
    except ValueError:
        return
    raise AssertionError("free-text agent output was accepted")


def test_incomplete_description_gets_two_to_four_questions():
    engine = DiagnosticEngine()
    diagnosis = engine.diagnose(SystemDescription(text="I have a machine and want it to behave better."))
    assert not diagnosis.complete
    assert 2 <= len(diagnosis.clarification_questions) <= 4


def test_complete_cartpole_description_classifies_as_class_iv():
    engine = DiagnosticEngine()
    diagnosis = engine.diagnose(
        SystemDescription(
            text="A rod hinged on a cart falls over when upright. The cart motor pushes left and right. Cart position and rod angle are measured.",
            observed_outputs=["cart position", "rod angle"],
            actuators=["cart motor"],
        )
    )
    classification = engine.classify(diagnosis)
    assert diagnosis.complete
    assert classification.primary_class == ArchetypeClass.CLASS_IV_HIGHER_ORDER_UNSTABLE_NONLINEAR_OR_NMP.value
    assert "natural_frequency" in classification.required_core_features


def test_first_order_delay_keeps_dead_time_feature():
    engine = DiagnosticEngine()
    diagnosis = engine.diagnose(
        SystemDescription(
            text="A first order process settles after a pump change, with a noticeable dead time.",
            observed_outputs=["level"],
            actuators=["pump"],
        )
    )
    classification = engine.classify(diagnosis)
    assert classification.primary_class == ArchetypeClass.CLASS_I_FIRST_ORDER_LAG.value
    assert classification.required_core_features == ["static_gain", "time_constant", "dead_time"]


def test_first_order_without_reported_delay_does_not_request_dead_time():
    engine = DiagnosticEngine()
    diagnosis = engine.diagnose(
        SystemDescription(
            text="A first order temperature process settles after a small heater change.",
            observed_outputs=["temperature"],
            actuators=["heater"],
        )
    )
    classification = engine.classify(diagnosis)
    assert classification.required_core_features == ["static_gain", "time_constant"]


def test_parse_json_content():
    assert parse_json_content("{\"complete\": true}") == {"complete": True}


def test_openai_compatible_adapter_uses_sdk(monkeypatch):
    calls = {}

    class FakeCompletions:
        def create(self, **kwargs):
            calls["completion"] = kwargs
            message = type("Message", (), {"content": "{\"complete\": true}"})()
            choice = type("Choice", (), {"message": message})()
            return type("Response", (), {"choices": [choice]})()

    class FakeOpenAI:
        def __init__(self, **kwargs):
            calls["client"] = kwargs
            completions = FakeCompletions()
            self.chat = type("Chat", (), {"completions": completions})()

    monkeypatch.setattr("cfdc.diagnosis.llm.OpenAI", FakeOpenAI)
    adapter = OpenAICompatibleDiagnosticAdapter(
        base_url="https://example.test/v1/chat/completions",
        model="test-model",
        api_key="test-key",
        timeout_s=12.0,
        max_tokens=321,
    )

    result = adapter.diagnose(SystemDescription(text="A simple heater process settles."))

    assert result == {"complete": True}
    assert calls["client"] == {
        "api_key": "test-key",
        "base_url": "https://example.test/v1",
        "timeout": 12.0,
    }
    assert calls["completion"]["model"] == "test-model"
    assert calls["completion"]["temperature"] == 0.0
    assert calls["completion"]["max_tokens"] == 321
    assert calls["completion"]["response_format"] == {"type": "json_object"}
    assert "extra_body" not in calls["completion"]
    assert calls["completion"]["messages"][1]["role"] == "user"
    assert "open_loop_stability" in calls["completion"]["messages"][1]["content"]


def test_deepseek_adapter_disables_thinking_for_strict_json(monkeypatch):
    calls = {}

    class FakeCompletions:
        def create(self, **kwargs):
            calls["completion"] = kwargs
            message = type("Message", (), {"content": "{\"complete\": true}"})()
            choice = type("Choice", (), {"message": message, "finish_reason": "stop"})()
            return type("Response", (), {"choices": [choice]})()

    class FakeOpenAI:
        def __init__(self, **kwargs):
            completions = FakeCompletions()
            self.chat = type("Chat", (), {"completions": completions})()

    monkeypatch.setattr("cfdc.diagnosis.llm.OpenAI", FakeOpenAI)
    adapter = OpenAICompatibleDiagnosticAdapter(
        base_url="https://api.deepseek.com",
        model="deepseek-v4-flash",
        api_key="test-key",
    )

    result = adapter.diagnose(SystemDescription(text="A simple heater process settles."))

    assert result == {"complete": True}
    assert calls["completion"]["extra_body"] == {
        "thinking": {"type": "disabled"}
    }


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

    monkeypatch.setattr("cfdc.diagnosis.llm.OpenAI", FakeOpenAI)
    adapter = OpenAICompatibleDiagnosticAdapter(
        base_url="https://example.test/v1",
        model="test-model",
        api_key="test-key",
    )

    with pytest.raises(ValueError, match="finish_reason='length'"):
        adapter.diagnose(SystemDescription(text="A simple heater process settles."))


def test_diagnostic_prompt_contains_required_fields():
    prompt = build_diagnostic_prompt(SystemDescription(text="A simple heater process settles."))
    for field in [
        "open_loop_stability",
        "minimum_phase",
        "significant_delay",
        "relative_degree",
        "controllability_observability",
        "nonlinearity_strength",
        "coupling_severity",
        "uncertainty_magnitude",
    ]:
        assert field in prompt
    assert '"assessment": "significant|not_significant|unknown"' in prompt
    assert "Return ONLY one JSON object" in prompt
