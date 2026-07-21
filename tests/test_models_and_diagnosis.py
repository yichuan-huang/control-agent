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
    SimulationExperimentRecord,
    ExperimentTrace,
    SignificantDelayField,
    SystemDescription,
)
from cfdc.workflow import (
    default_simulation_profile_catalog,
    deterministic_profile_selection,
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
    result = SimulationExperimentRecord(
        primitive=ExperimentPrimitive.RAMP_STEP,
        estimates=["static_gain", "time_constant"],
        trace=ExperimentTrace(
            time_s=[0.0, 1.0, 2.0],
            signals={"input setting": [0.0, 0.5, 0.5], "measured output": [0.0, 0.4, 0.8]},
        ),
    )
    payload = result.model_dump_json()
    restored = SimulationExperimentRecord.model_validate_json(payload)
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


def test_missing_assessment_is_rejected_at_adapter_boundary():
    description = SystemDescription(
        text="A first order process settles after a small pump change with dead time.",
        observed_outputs=["level"],
        actuators=["pump"],
    )
    payload = infer_structural_diagnosis(description).model_dump()
    payload["significant_delay"].pop("assessment")
    with pytest.raises(ValueError, match="assessment"):
        validate_agent_payload(payload)


def test_invalid_assessment_enum_is_rejected():
    description = SystemDescription(
        text="A first order process settles after a small pump change with dead time.",
        observed_outputs=["level"],
        actuators=["pump"],
    )
    payload = infer_structural_diagnosis(description).model_dump()
    payload["significant_delay"]["assessment"] = "maybe_delay"

    with pytest.raises(ValueError, match="assessment"):
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


def test_thermostat_negations_are_not_misread_as_inverse_response_or_dead_time():
    description = SystemDescription(
        text=(
            "以二值加热命令作为控制并连续记录室温和加热器状态；室温会收敛或保持有界。"
            "输出的首次有效变化与最终方向一致，不会先向相反方向运动。"
            "动态过程中存在滞后，但在有效输出运动前没有独立的输运、测量或计算停顿，"
            "首次记录变化会及时开始，不会出现独立静默区间。"
            "执行作用至多经过两个主导储能或积分环节即可到达测量输出。"
            "每个相关运动模态至少出现在一项记录中，并随某个可用输入变化。"
            "恒温器通过固定滞环带切换加热状态，偏离比例关系只存在于固定输入输出规律中。"
            "试验由一条主要动作到记录量的通道承担。"
            "合理参数变化只会适度改变响应速度和最终水平。"
        ),
        observed_outputs=["室温", "加热器状态"],
        actuators=["二值加热命令"],
    )

    diagnosis, classification = DiagnosticEngine().run(description)

    assert diagnosis.complete
    assert diagnosis.minimum_phase.assessment == "minimum_phase"
    assert diagnosis.significant_delay.assessment == "not_significant"
    assert diagnosis.relative_degree.estimated_order == 1
    assert classification.primary_class == ArchetypeClass.CLASS_I_FIRST_ORDER_LAG.value


def test_order_upper_bound_alone_does_not_turn_a_thermal_process_into_an_oscillator():
    description = SystemDescription(
        text=(
            "A thermal process settles after a binary heater change, starts promptly, "
            "and never rings or produces repeated peaks. At most two storage stages may "
            "contribute to the measured temperature."
        ),
        observed_outputs=["temperature"],
        actuators=["binary heater command"],
    )
    diagnosis = DiagnosticEngine().diagnose(description)
    order_two_upper_bound = diagnosis.model_copy(
        update={
            "relative_degree": diagnosis.relative_degree.model_copy(
                update={"estimated_order": 2}
            )
        }
    )

    classification = DiagnosticEngine().classify(order_two_upper_bound, description)

    assert classification.primary_class == ArchetypeClass.CLASS_I_FIRST_ORDER_LAG.value
    assert classification.required_core_features == ["static_gain", "time_constant"]


def test_diagnostic_prompt_distinguishes_order_bounds_static_hysteresis_and_oscillation():
    prompt = build_diagnostic_prompt(
        SystemDescription(
            text="A thermostat has a fixed hysteresis band.",
            observed_outputs=["temperature"],
            actuators=["heater"],
        )
    )

    assert "at most two" in prompt
    assert "not an exact second-order" in prompt
    assert "fixed thermostat hysteresis" in prompt
    assert "repeated peaks" in prompt


def test_engine_reconciles_llm_misreadings_against_explicit_thermostat_negations():
    description = SystemDescription(
        text=(
            "A room-temperature process settles after a binary heater command. "
            "Its first effective change follows the final direction and never moves "
            "opposite first. There is dynamic lag, but no independent transport delay, "
            "pause, or silent interval. At most two storage stages contribute. The "
            "thermostat uses a fixed hysteresis band rather than a dynamic nonlinear state."
        ),
        observed_outputs=["room temperature", "heater state"],
        actuators=["binary heater command"],
    )
    baseline = infer_structural_diagnosis(description)
    poisoned = baseline.model_copy(
        update={
            "minimum_phase": baseline.minimum_phase.model_copy(
                update={"assessment": "nonminimum_phase"}
            ),
            "significant_delay": baseline.significant_delay.model_copy(
                update={"assessment": "significant"}
            ),
            "relative_degree": baseline.relative_degree.model_copy(
                update={"estimated_order": 2}
            ),
            "nonlinearity_strength": baseline.nonlinearity_strength.model_copy(
                update={"assessment": "strong_dynamic"}
            ),
        }
    )

    class MisreadingAdapter:
        def diagnose(self, supplied_description):
            assert supplied_description == description
            return poisoned.model_dump(mode="json")

    diagnosis, classification = DiagnosticEngine(adapter=MisreadingAdapter()).run(description)

    assert diagnosis.minimum_phase.assessment == "minimum_phase"
    assert diagnosis.significant_delay.assessment == "not_significant"
    assert diagnosis.relative_degree.estimated_order == 1
    assert diagnosis.nonlinearity_strength.assessment == "static_compensable"
    assert classification.primary_class == ArchetypeClass.CLASS_I_FIRST_ORDER_LAG.value


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


def test_profile_selection_prompt_declares_exact_json_field_types(monkeypatch):
    calls = {}
    description = SystemDescription(
        text="A measured first order heater settles after a small power change.",
        observed_outputs=["temperature"],
        actuators=["heater"],
    )
    diagnosis, classification = DiagnosticEngine().run(description)
    catalog = default_simulation_profile_catalog()
    expected = deterministic_profile_selection(
        description,
        diagnosis,
        classification,
        catalog,
    )

    class FakeCompletions:
        def create(self, **kwargs):
            calls["completion"] = kwargs
            message = type("Message", (), {"content": expected.model_dump_json()})()
            choice = type("Choice", (), {"message": message})()
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

    result = adapter.select_profile(description, diagnosis, classification, catalog)

    assert result == expected.model_dump()
    system_prompt = calls["completion"]["messages"][0]["content"]
    user_prompt = calls["completion"]["messages"][1]["content"]
    assert "exact JSON schema" in system_prompt
    assert '"selected_feature_ids": ["string"]' in user_prompt
    assert '"evidence": ["string"]' in user_prompt
    assert "evidence must be a non-empty JSON array of strings" in user_prompt
    assert "even when there is only one evidence item" in user_prompt
    assert "Do not add any other keys" in user_prompt


def test_openai_compatible_adapter_requires_explicit_provider_configuration(monkeypatch):
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
        OpenAICompatibleDiagnosticAdapter()


def test_openai_compatible_adapter_reads_non_openai_provider_environment(monkeypatch):
    calls = {}

    class FakeOpenAI:
        def __init__(self, **kwargs):
            calls.update(kwargs)

    monkeypatch.setattr("cfdc.diagnosis.llm.OpenAI", FakeOpenAI)
    monkeypatch.setenv("CFDC_LLM_BASE_URL", "http://localhost:11434/v1")
    monkeypatch.setenv("CFDC_LLM_MODEL", "qwen2.5:14b")
    monkeypatch.setenv("CFDC_LLM_API_KEY", "ollama")

    adapter = OpenAICompatibleDiagnosticAdapter()

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
