from pathlib import Path

import pytest

from cfdc.web.presentation import render_report
from cfdc.web import service as web_service
from cfdc.web.service import (
    ROUTE_CHOICES,
    continue_app_run,
    parse_names,
    parse_safety_bounds,
    start_app_run,
)
from cfdc.web.ui import EXAMPLES, NATURAL_LANGUAGE_MODE, build_app, reset_ui, update_run_mode
from cfdc.diagnosis import DeterministicDiagnosticAdapter
from cfdc.diagnosis.engine import infer_structural_diagnosis
from cfdc.models import SystemDescription


def test_root_app_is_a_thin_launcher_and_legacy_package_app_is_removed():
    assert not Path("cfdc/app.py").exists()
    launcher = Path("app.py").read_text(encoding="utf-8")
    assert "from cfdc.web.ui import CSS, build_app" in launcher
    assert "def build_app" not in launcher


def test_app_runs_clear_description_and_renders_stage_tables():
    report, state = start_app_run(
        "A measured first order heater settles after a small power change.",
        "temperature",
        "heater",
        "max_abs_control=1.0",
        "自动选择",
        False,
        "",
        "",
        "",
    )
    view = render_report(report)

    assert report.status == "completed"
    assert state["session"] is None
    assert state["api_key"] == ""
    assert len(view["diagnosis"]) == 8
    assert dict(view["route"])["仿真 Profile"] == "first_order_lag"
    assert view["experiments"]
    assert view["features"]
    assert view["controller"]
    assert view["performance"]
    assert "flow-step done" in view["progress"]
    assert "first_order_lag" in view["summary"]
    assert "原控制器" in view["performance_visual"]
    assert "适应控制器" in view["performance_visual"]
    assert view["raw"]["evidence_boundary"] == "software_simulation_only"


def test_app_clarification_state_can_continue_into_full_simulation():
    report, state = start_app_run(
        "I have a machine.",
        "",
        "",
        "",
        "自动选择",
        False,
        "",
        "",
        "",
    )
    questions = render_report(report)["clarifications"]

    assert report.status == "need_more_information"
    assert "flow-step waiting" in render_report(report)["progress"]
    assert state["session"] is not None
    assert 2 <= len(questions) <= 4

    completed, next_state = continue_app_run(
        state,
        ["Temperature can be recorded.", "A heater changes it.", "It immediately moves in the expected direction.", "The response starts promptly."],
        "It is a measured first-order thermal process that settles after a heater change.",
    )

    assert completed.status == "completed"
    assert completed.semantic_selection.simulation_profile_id == "first_order_lag"
    assert completed.experiment_results
    assert next_state["session"] is None
    assert next_state["api_key"] == ""


def test_app_renders_matrix_core_feature_without_scalar_collapse():
    report, _ = start_app_run(
        "A strongly coupled MIMO process has multiple inputs and multiple outputs.",
        "y1, y2",
        "u1, u2",
        "",
        "自动选择",
        False,
        "",
        "",
        "",
    )
    feature_by_id = {row[0]: row for row in render_report(report)["features"]}

    assert feature_by_id["local_gain_matrix"][3] == "矩阵特征"
    assert feature_by_id["local_gain_matrix"][1].startswith("[[")


def test_app_input_parsers_accept_common_multiline_forms():
    assert parse_names("temperature, pressure\nflow") == ["temperature", "pressure", "flow"]
    assert parse_safety_bounds("max_abs_output=2\nmax_abs_control=1") == {
        "max_abs_output": 2.0,
        "max_abs_control": 1.0,
    }
    assert {
        "cartpole",
        "cartpole-boundary",
        "vtol-position",
        "vtol-boundary",
        "vtol-altitude",
        "vtol-hover",
        "vtol-variation",
    }.issubset(set(ROUTE_CHOICES.values()))


def test_time_scale_hint_parser_accepts_blank_and_positive_finite_values():
    assert web_service.parse_time_scale_hint(None) is None
    assert web_service.parse_time_scale_hint("") is None
    assert web_service.parse_time_scale_hint(" 2.5 ") == 2.5
    assert web_service.parse_time_scale_hint(0.05) == 0.05


def test_forbidden_actions_parser_preserves_commas_inside_one_action_per_line():
    assert web_service.parse_forbidden_actions(
        "free release\ncontinue after angle, rate, torque, or duration limits are reached"
    ) == [
        "free release",
        "continue after angle, rate, torque, or duration limits are reached",
    ]


@pytest.mark.parametrize("value", ["0", "-1", "nan", "inf", "fast"])
def test_time_scale_hint_parser_rejects_nonpositive_or_nonfinite_values(value):
    with pytest.raises(ValueError, match="主导时间尺度"):
        web_service.parse_time_scale_hint(value)


def test_start_app_run_passes_forbidden_actions_and_time_scale_to_system_description(monkeypatch):
    captured = {}
    real_system_description = SystemDescription

    def capture_system_description(**kwargs):
        captured.update(kwargs)
        return real_system_description(**kwargs)

    monkeypatch.setattr(web_service, "SystemDescription", capture_system_description)

    report, _ = start_app_run(
        "A measured first order heater settles after a small power change.",
        "temperature",
        "heater",
        "max_abs_control=1.0",
        NATURAL_LANGUAGE_MODE,
        False,
        "",
        "",
        "",
        forbidden_actions="free release\nphysical deployment",
        time_scale_hint_s="2.5",
    )

    assert report.status == "completed"
    assert captured["forbidden_actions"] == ["free release", "physical deployment"]
    assert captured["time_scale_hint_s"] == 2.5
    assert report.system_description.forbidden_actions == ["free release", "physical deployment"]
    assert report.system_description.time_scale_hint_s == 2.5
    assert report.experiment_plan.instructions[0].duration_s == 20.0


def test_app_input_parsers_treat_uninitialized_textboxes_as_empty():
    assert parse_names(None) == []
    assert parse_safety_bounds(None) == {}


def test_gradio_textboxes_start_with_string_values():
    app = build_app()
    provider_labels = {"Base URL", "Model"}
    textbox_values = [
        component["props"].get("value")
        for component in app.config["components"]
        if component["type"] == "textbox"
        and component["props"].get("label") not in provider_labels
    ]

    assert textbox_values
    assert all(value == "" for value in textbox_values)


def test_gradio_exposes_all_six_domain_inputs_with_blank_optional_defaults():
    app = build_app()
    textboxes = {
        component["props"].get("label"): component["props"]
        for component in app.config["components"]
        if component["type"] == "textbox"
    }

    assert {
        "控制问题",
        "可观察输出",
        "执行器",
        "安全边界",
        "禁止实验动作",
        "主导时间尺度（秒）",
    }.issubset(textboxes)
    assert textboxes["禁止实验动作"]["value"] == ""
    assert textboxes["主导时间尺度（秒）"]["value"] == ""


def test_first_example_accepts_uninitialized_optional_textboxes():
    description, outputs, actuators = EXAMPLES[0]

    report, state = start_app_run(
        description,
        outputs,
        actuators,
        None,
        NATURAL_LANGUAGE_MODE,
        False,
        None,
        None,
        None,
    )

    assert report.status in {"completed", "frozen"}
    assert state["session"] is None


def test_uninitialized_required_description_uses_validation_error():
    with pytest.raises(ValueError, match="请描述需要控制的对象"):
        start_app_run(
            None,
            None,
            None,
            None,
            NATURAL_LANGUAGE_MODE,
            False,
            None,
            None,
            None,
        )


def test_uninitialized_llm_fields_use_configuration_error(monkeypatch):
    description, outputs, actuators = EXAMPLES[0]
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

    with pytest.raises(ValueError, match="Missing OpenAI-compatible LLM configuration"):
        start_app_run(
            description,
            outputs,
            actuators,
            None,
            NATURAL_LANGUAGE_MODE,
            True,
            None,
            None,
            None,
        )


def test_uninitialized_answer_textboxes_use_validation_error():
    report, state = start_app_run(
        "I have a machine.",
        "",
        "",
        "",
        NATURAL_LANGUAGE_MODE,
        False,
        "",
        "",
        "",
    )
    assert report.status == "need_more_information"

    with pytest.raises(
        ValueError,
        match="provide at least one clarification answer or supplemental description",
    ):
        continue_app_run(
            state,
            [None, None, None, None],
            None,
        )


def test_app_rejects_nonfinite_duplicate_bounds_and_unknown_routes():
    with pytest.raises(ValueError, match="有限数字"):
        parse_safety_bounds("max_abs_output=nan")
    with pytest.raises(ValueError, match="重复定义"):
        parse_safety_bounds("max_abs_output=1\nmax_abs_output=2")
    with pytest.raises(ValueError, match="未知运行方式"):
        start_app_run("description", "output", "input", "", "unknown-route", False, "", "", "")


def test_app_does_not_repeat_diagnosis_for_clear_description(monkeypatch):
    calls = {"diagnose": 0, "select": 0}
    delegate = DeterministicDiagnosticAdapter()

    class CountingAdapter:
        def diagnose(self, description):
            calls["diagnose"] += 1
            return delegate.diagnose(description)

        def select_profile(self, description, diagnosis, classification, catalog):
            calls["select"] += 1
            return delegate.select_profile(description, diagnosis, classification, catalog)

    monkeypatch.setattr("cfdc.web.service.build_adapter", lambda *args: CountingAdapter())
    report, _ = start_app_run(
        "A measured first order heater settles after a small power change.",
        "temperature",
        "heater",
        "",
        "自动选择",
        True,
        "https://provider.example/v1",
        "provider-model",
        "test-key",
    )

    assert report.status == "completed"
    assert calls == {"diagnose": 1, "select": 1}


def test_detailed_type_i_to_iii_examples_complete_the_full_pipeline():
    expected = [
        ("class_i_first_order_lag", "first_order_lag"),
        ("class_ii_second_order_oscillator", "second_order_oscillator"),
        ("class_iii_double_or_pure_integrator", "double_integrator"),
    ]

    for example, (archetype, profile) in zip(EXAMPLES[:3], expected):
        description, outputs, actuators = example
        report, state = start_app_run(
            description,
            outputs,
            actuators,
            "",
            NATURAL_LANGUAGE_MODE,
            False,
            "",
            "",
            "",
        )

        assert report.status == "completed"
        assert str(report.classification.primary_class) == archetype
        assert report.semantic_selection.simulation_profile_id == profile
        assert report.experiment_results
        assert report.features
        assert report.controller is not None
        assert report.algorithm1_state is not None
        assert report.adapted_controller_performance is not None
        assert state["session"] is None


def test_detailed_type_iv_and_v_examples_complete_the_full_pipeline():
    expected = [
        ("class_iv_higher_order_unstable_nonlinear_or_nmp", "nmp_inverse_response"),
        ("class_v_multivariable_significant_coupling", "mimo_2x2_coupled"),
    ]

    for example, (archetype, profile) in zip(EXAMPLES[3:5], expected):
        description, outputs, actuators = example
        report, state = start_app_run(
            description,
            outputs,
            actuators,
            "",
            NATURAL_LANGUAGE_MODE,
            False,
            "",
            "",
            "",
        )

        assert report.status in {"completed", "frozen"}
        assert str(report.classification.primary_class) == archetype
        assert report.semantic_selection.simulation_profile_id == profile
        assert report.experiment_results
        assert report.features
        assert report.controller is not None
        assert report.algorithm1_state is not None
        assert report.adapted_controller_performance is not None
        assert state["session"] is None


def test_last_two_examples_are_preserved_for_clarification_flow():
    expected_incomplete_examples = [
        [
            "一个稳定过程对阀门阶跃先反向运动，随后才向最终方向稳定。",
            "output",
            "valve",
        ],
        [
            "强耦合双输入双输出过程，每个输入都会明显影响两个输出。",
            "y1, y2",
            "u1, u2",
        ],
    ]

    assert len(EXAMPLES) == 7
    assert EXAMPLES[-2:] == expected_incomplete_examples

    for description, outputs, actuators in EXAMPLES[-2:]:
        report, state = start_app_run(
            description,
            outputs,
            actuators,
            "",
            NATURAL_LANGUAGE_MODE,
            False,
            "",
            "",
            "",
        )
        questions = render_report(report)["clarifications"]

        assert report.status == "need_more_information"
        assert state["session"] is not None
        assert 2 <= len(questions) <= 4


def test_first_five_examples_use_observations_without_diagnostic_answer_leakage():
    forbidden_terms = [
        "first-order",
        "first order",
        "self-regulating",
        "oscillator",
        "double integrator",
        "integrator",
        "non-restoring",
        "relative degree",
        "estimated_order",
        "open_loop_stability",
        "minimum_phase",
        "significant_delay",
        "controllability_observability",
        "nonlinearity_strength",
        "coupling_severity",
        "uncertainty_magnitude",
        "clarification_questions",
        "complete=true",
        "stage 0",
        "type i",
        "type ii",
        "type iii",
        "type iv",
        "type v",
        "class_i",
        "class_ii",
        "class_iii",
        "class_iv",
        "class_v",
        "higher-order",
        "higher order",
        "inverse response",
        "nmp",
        "mimo",
        "multivariable",
        "一阶系统",
        "二阶系统",
        "高阶系统",
        "不稳定系统",
        "双积分",
        "相对阶",
        "最小相位",
        "非最小相位",
        "逆响应",
        "多变量系统",
        "强耦合",
        "双输入双输出",
        "开环稳定",
        "边界稳定",
        "单输入单输出",
    ]

    for description, _, _ in EXAMPLES[:5]:
        normalized = description.lower()
        leaked = [term for term in forbidden_terms if term in normalized]

        assert not leaked
        assert "=" not in description
        assert "一个采样周期内" in description
        assert "初始" in description
        assert "传感器" in description
        assert "小幅" in description
        assert "输入" in description
        assert "输出" in description

    ui_source = Path("cfdc/web/ui.py").read_text(encoding="utf-8")
    assert "Type I / II / III" not in ui_source


def test_developer_route_ignores_user_inputs_and_never_builds_llm(monkeypatch):
    def forbidden_adapter(*args, **kwargs):
        raise AssertionError("developer validation route must not build an LLM adapter")

    monkeypatch.setattr("cfdc.web.service.build_adapter", forbidden_adapter)
    report, state = start_app_run(
        "This user description must be ignored.",
        "wrong output",
        "wrong actuator",
        "this is deliberately not a valid safety bound",
        "开发验证 · CartPole 完整流程",
        True,
        "not-a-url",
        "wrong-model",
        "wrong-key",
    )

    assert report.status == "completed"
    assert report.semantic_selection.simulation_profile_id == "underactuated_cartpole"
    assert "rod hinged on a cart" in report.system_description.text
    assert "This user description" not in report.system_description.text
    assert state["use_llm"] is False
    assert state["input_source"] == "preregistered_developer_scenario"


def test_run_mode_disables_inputs_without_clearing_their_values():
    validation_updates = update_run_mode("开发验证 · VTOL 位置控制")
    natural_updates = update_run_mode(NATURAL_LANGUAGE_MODE)

    assert "不会调用 LLM" in validation_updates[0]
    assert "六项" in natural_updates[0]
    for update in validation_updates[1:7]:
        assert update["interactive"] is False
        assert "value" not in update
    assert validation_updates[7]["interactive"] is False
    assert validation_updates[7]["value"] is False
    assert all(update["interactive"] is True for update in natural_updates[1:7])
    assert natural_updates[8]["interactive"] is True


def test_clarification_reuses_completed_diagnosis_and_profile_without_extra_llm_calls(monkeypatch):
    calls = {"diagnose": 0, "select": 0}
    incomplete = infer_structural_diagnosis(SystemDescription(text="I have a machine."))
    complete = infer_structural_diagnosis(
        SystemDescription(
            text="A first order temperature process settles after a heater change.",
            observed_outputs=["temperature"],
            actuators=["heater"],
        )
    )
    delegate = DeterministicDiagnosticAdapter()

    class SequencedAdapter:
        def diagnose(self, description):
            calls["diagnose"] += 1
            return (incomplete if calls["diagnose"] == 1 else complete).model_dump(mode="json")

        def select_profile(self, description, diagnosis, classification, catalog):
            calls["select"] += 1
            return delegate.select_profile(description, diagnosis, classification, catalog)

    adapter = SequencedAdapter()
    monkeypatch.setattr("cfdc.web.service.build_adapter", lambda *args: adapter)
    _, state = start_app_run(
        "I have a machine.", "", "", "", NATURAL_LANGUAGE_MODE,
        True, "https://provider.example/v1", "provider-model", "test-key",
    )
    completed, _ = continue_app_run(
        state,
        ["Temperature is measured.", "A heater changes it.", "It moves in the expected direction.", "It starts promptly."],
        "It is a first order measured thermal process that settles.",
    )

    assert completed.status == "completed"
    assert completed.semantic_selection.simulation_profile_id == "first_order_lag"
    assert calls == {"diagnose": 2, "select": 1}


def test_include_trajectory_exposes_route_trajectory_in_audit_json():
    report, _ = start_app_run(
        "ignored", "ignored", "ignored", "",
        "开发验证 · VTOL 位置控制",
        False, "", "", "", True,
    )
    compact = render_report(report)["raw"]

    assert compact["vtol_simulation"]["trajectory"]


def test_cartpole_audit_json_compacts_nested_trial_samples():
    import json

    report, _ = start_app_run(
        "ignored", "ignored", "ignored", "",
        "开发验证 · CartPole 完整流程",
        False, "", "", "", False,
    )
    compact = render_report(report)["raw"]
    boundary = compact["cartpole_boundary"]
    trials = [*boundary["candidate_trials"], boundary["rollback_trial"]]

    assert all("samples" not in trial for trial in trials)
    assert all(trial["sample_count"] > 0 for trial in trials)
    assert len(json.dumps(compact, ensure_ascii=False)) < 500_000


def test_clear_resets_mode_credentials_session_and_report(monkeypatch):
    monkeypatch.setenv("CFDC_LLM_BASE_URL", "https://provider.example/v1")
    monkeypatch.setenv("CFDC_LLM_MODEL", "provider-model")
    reset = reset_ui()

    assert len(reset) == 32
    assert reset[0] == NATURAL_LANGUAGE_MODE
    assert "六项" in reset[1]
    assert reset[2:8] == ("", "", "", "", "", "")
    assert reset[8] is False
    assert reset[9] is False
    assert reset[10] == "https://provider.example/v1"
    assert reset[11] == "provider-model"
    assert reset[12] == ""
    assert reset[14] == {}
