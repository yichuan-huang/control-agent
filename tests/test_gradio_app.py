from pathlib import Path

from cfdc.web.presentation import render_report
from cfdc.web.service import (
    ROUTE_CHOICES,
    continue_app_run,
    parse_names,
    parse_safety_bounds,
    start_app_run,
)
from cfdc.web.ui import EXAMPLES, NATURAL_LANGUAGE_MODE, reset_ui, update_run_mode
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


def test_app_rejects_nonfinite_duplicate_bounds_and_unknown_routes():
    import pytest

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
    assert validation_updates[1]["interactive"] is False
    assert "value" not in validation_updates[1]
    assert validation_updates[5]["interactive"] is False
    assert validation_updates[5]["value"] is False
    assert natural_updates[1]["interactive"] is True
    assert natural_updates[6]["interactive"] is True


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

    assert len(reset) == 30
    assert reset[0] == NATURAL_LANGUAGE_MODE
    assert reset[6] is False
    assert reset[7] is False
    assert reset[8] == "https://provider.example/v1"
    assert reset[9] == "provider-model"
    assert reset[10] == ""
    assert reset[12] == {}
