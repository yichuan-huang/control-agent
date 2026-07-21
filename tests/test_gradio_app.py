import json
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
    submit_app_evidence,
    submit_app_json,
    submit_app_specifications,
)
from cfdc.web.ui import EXAMPLES, NATURAL_LANGUAGE_MODE, build_app, reset_ui, update_run_mode
from cfdc.diagnosis import DeterministicDiagnosticAdapter, submit_specifications_to_session
from cfdc.diagnosis.engine import infer_structural_diagnosis
from cfdc.models import DiagnosticSessionState, SystemDescription
from cfdc.runtime import run_cfdc_route


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

    assert report.status == "awaiting_specifications"
    assert state["session"] is not None
    assert state["api_key"] == ""
    assert len(view["diagnosis"]) == 8
    assert dict(view["route"])["方法 Profile"] == "first_order_lag"
    assert view["experiments"] == []
    assert view["features"] == []
    assert view["controller"] == []
    assert view["performance"] == []
    assert "flow-step waiting" in view["progress"]
    assert "first_order_lag" in view["summary"]
    assert "不会提取核心特征" in view["specification_guidance"]
    assert view["raw"]["evidence_boundary"] == "structural_diagnosis_only"


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

    assert completed.status == "awaiting_specifications"
    assert completed.semantic_selection.simulation_profile_id == "first_order_lag"
    assert completed.experiment_results == []
    assert next_state["session"] is not None
    assert next_state["api_key"] == ""


def test_app_renders_matrix_core_feature_without_scalar_collapse():
    report = run_cfdc_route(
        "generic",
        description=SystemDescription(
            text="A strongly coupled MIMO process has multiple inputs and multiple outputs.",
            observed_outputs=["y1", "y2"],
            actuators=["u1", "u2"],
        ),
        execution_mode="demo_fixture",
    )
    feature_by_id = {row[0]: row for row in render_report(report)["features"]}

    assert feature_by_id["local_gain_matrix"][3] == "矩阵特征"
    assert feature_by_id["local_gain_matrix"][1].startswith("[[")


def test_app_input_parsers_accept_common_multiline_forms():
    assert parse_names("temperature, pressure\nflow") == ["temperature", "pressure", "flow"]
    assert parse_names("室温、加热器状态") == ["室温", "加热器状态"]
    assert parse_names("body displacement, wheel displacement, and suspension travel") == [
        "body displacement",
        "wheel displacement",
        "suspension travel",
    ]
    assert parse_safety_bounds("max_abs_output=2\nmax_abs_control=1") == {
        "max_abs_output": 2.0,
        "max_abs_control": 1.0,
    }
    assert parse_safety_bounds(
        "max_abs_output_normalized=1.5\nmax_abs_actuator_normalized=1.0"
    ) == {
        "max_abs_output_normalized": 1.5,
        "max_abs_output": 1.5,
        "output_min": -1.5,
        "output_max": 1.5,
        "max_abs_actuator_normalized": 1.0,
        "max_abs_control": 1.0,
        "input_min": -1.0,
        "input_max": 1.0,
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


def test_app_can_submit_structured_model_evidence_after_diagnosis():
    report, state = start_app_run(
        "A measured first order heater settles after a small power change.",
        "temperature",
        "heater",
        "input_min=-1\ninput_max=1\noutput_min=-10\noutput_max=10",
        NATURAL_LANGUAGE_MODE,
        False,
        "",
        "",
        "",
        time_scale_hint_s="4",
    )
    assert report.status == "awaiting_specifications"

    with pytest.raises(ValueError, match="软件仿真"):
        submit_app_evidence(
            state,
            model_json='{"kind":"transfer_function"}',
            trace_files=None,
            trace_manifest_json="",
            validation_json="",
            demo_confirmed=False,
            simulation_bounds_confirmed=False,
        )

    resolved, next_state = submit_app_evidence(
        state,
        model_json='{"kind":"transfer_function","numerator":[1.0],"denominator":[2.0,1.0],"input_signal_id":"heater","output_signal_id":"temperature","input_units":"V","output_units":"degC"}',
        trace_files=None,
        trace_manifest_json="",
        validation_json="",
        demo_confirmed=False,
        simulation_bounds_confirmed=True,
    )

    assert resolved.status == "validation_pending"
    assert resolved.controller.release_level == "candidate_unvalidated"
    assert next_state["session"] is None


def test_standard_demo_is_exempt_from_user_simulation_boundary_confirmation():
    report, state = start_app_run(
        "A measured first order heater settles after a small power change.",
        "temperature", "heater", "", NATURAL_LANGUAGE_MODE,
        False, "", "", "",
    )
    assert report.status == "awaiting_specifications"

    resolved, next_state = submit_app_evidence(
        state,
        model_json="",
        trace_files=None,
        trace_manifest_json="",
        validation_json="",
        demo_confirmed=True,
        simulation_bounds_confirmed=False,
    )

    assert resolved.status == "demo_completed"
    assert resolved.evidence_boundary == "demo_fixture_only"
    assert next_state["session"] is None


def test_app_can_submit_dataset_json_wrapper_from_pasted_text():
    report, state = start_app_run(
        "A measured first order heater settles after a small power change.",
        "temperature",
        "heater",
        "input_min=0\ninput_max=1\noutput_min=64.5\noutput_max=65.5",
        NATURAL_LANGUAGE_MODE,
        False,
        "",
        "",
        "",
    )
    assert report.status == "awaiting_specifications"
    payload = {
        "specification_facts": [
            {"fact_id": "input_change", "value": 1, "unit": "binary_command"},
            {"fact_id": "steady_output_change", "value": 50, "unit": "degF"},
            {"fact_id": "response_time_s", "value": 20, "unit": "s"},
            {"fact_id": "input_min", "value": 0, "unit": "binary_command"},
            {"fact_id": "input_max", "value": 1, "unit": "binary_command"},
            {"fact_id": "output_min", "value": 64.5, "unit": "degF"},
            {"fact_id": "output_max", "value": 65.5, "unit": "degF"},
        ],
        "model": {
            "kind": "transfer_function",
            "numerator": [50.0],
            "denominator": [144000.0, 1.0],
            "input_signal_id": "heater",
            "output_signal_id": "temperature",
            "input_units": "binary_command",
            "output_units": "degF",
        },
        "experiment": {"sample_time_s": 60, "duration_s": 21600},
        "eight_segment_evidence": {"stability": "bounded"},
    }

    with pytest.raises(ValueError, match="软件仿真"):
        submit_app_json(
            state,
            uploaded_json=None,
            pasted_json=json.dumps(payload),
            simulation_bounds_confirmed=False,
        )

    resolved, next_state = submit_app_json(
        state,
        uploaded_json=None,
        pasted_json=json.dumps(payload),
        simulation_bounds_confirmed=True,
    )

    assert resolved.status == "candidate_unvalidated"
    assert resolved.compiled_specification_model.model.input_units == "binary_command"
    assert resolved.system_description.simulation_boundary_confirmation.confirmed is True
    assert next_state["session"] is None


def test_app_can_submit_dataset_json_wrapper_from_uploaded_file(tmp_path):
    report, state = start_app_run(
        "A measured first order heater settles after a small power change.",
        "temperature", "heater",
        "input_min=-1\ninput_max=1\noutput_min=-20\noutput_max=20",
        NATURAL_LANGUAGE_MODE,
        False, "", "", "",
    )
    payload_path = tmp_path / "thermostat.json"
    payload_path.write_text(
        json.dumps({
            "specification_facts": [
                {"fact_id": "input_change", "value": 1, "unit": "binary_command"},
                {"fact_id": "steady_output_change", "value": 50, "unit": "degF"},
                {"fact_id": "response_time_s", "value": 20, "unit": "s"},
                {"fact_id": "input_min", "value": 0, "unit": "binary_command"},
                {"fact_id": "input_max", "value": 1, "unit": "binary_command"},
                {"fact_id": "output_min", "value": 64.5, "unit": "degF"},
                {"fact_id": "output_max", "value": 65.5, "unit": "degF"},
            ]
        }),
        encoding="utf-8",
    )

    resolved, next_state = submit_app_json(
        state,
        uploaded_json=str(payload_path),
        pasted_json="",
        simulation_bounds_confirmed=True,
    )

    assert resolved.status == "candidate_unvalidated"
    assert resolved.compiled_specification_model.derived_features["static_gain"] == pytest.approx(50.0)
    assert next_state["session"] is None


def test_thermostat_natural_language_and_json_compile_equivalent_models():
    description = (
        "A binary heater command controls room temperature through fixed thermostat "
        "hysteresis. The temperature settles, starts promptly in the final direction, "
        "and has no repeated peaks."
    )
    paragraph = (
        "室外温度 50 degF、白天设定值 65 degF；等效热容 C = 20000 Btu/degF、"
        "传热系数 H = 500 Btu/(h degF)、炉子供热率 25000 Btu/h、"
        "滞环半宽 0.5 degF。"
    )
    natural_initial, natural_state = start_app_run(
        description, "room temperature, heater state", "binary heater command", "",
        NATURAL_LANGUAGE_MODE, False, "", "", "",
    )
    _, json_state = start_app_run(
        description, "room temperature, heater state", "binary heater command", "",
        NATURAL_LANGUAGE_MODE, False, "", "", "",
    )

    facts_payload = [
        {"fact_id": "input_change", "value": 1, "unit": "binary_command"},
        {"fact_id": "steady_output_change", "value": 50, "unit": "degF"},
        {"fact_id": "response_time_s", "value": 144000, "unit": "s"},
        {"fact_id": "input_min", "value": 0, "unit": "binary_command"},
        {"fact_id": "input_max", "value": 1, "unit": "binary_command"},
        {"fact_id": "output_min", "value": 64.5, "unit": "degF"},
        {"fact_id": "output_max", "value": 65.5, "unit": "degF"},
    ]
    natural_session = DiagnosticSessionState.model_validate(natural_state["session"])
    json_session = DiagnosticSessionState.model_validate(json_state["session"])
    natural_reviewed = submit_specifications_to_session(natural_session, paragraph)
    json_reviewed = submit_specifications_to_session(
        json_session,
        web_service._specification_facts_to_text(json_session, facts_payload),
    )

    natural_facts = {
        item.fact_id: (item.value, item.unit)
        for item in natural_reviewed.specification_assessment.facts
    }
    json_facts = {
        item.fact_id: (item.value, item.unit)
        for item in json_reviewed.specification_assessment.facts
    }
    assert natural_facts == json_facts
    assert (
        natural_reviewed.compiled_specification_model.model.model_dump(mode="json")
        == json_reviewed.compiled_specification_model.model.model_dump(mode="json")
    )
    assert (
        natural_reviewed.compiled_specification_model.safety_bounds
        == json_reviewed.compiled_specification_model.safety_bounds
    )
    guidance = render_report(
        natural_initial.model_copy(
            update={"specification_assessment": natural_reviewed.specification_assessment}
        )
    )["specification_guidance"]
    assert "经后端重算验证的推导规格" in guidance
    assert "3600 * heat_capacity / heat_transfer_coefficient" in guidance


def test_app_dataset_wrapper_with_empty_facts_uses_its_complete_model():
    report, state = start_app_run(
        "A measured first order heater settles after a small power change.",
        "temperature", "heater",
        "max_abs_output_normalized=20\nmax_abs_actuator_normalized=1",
        NATURAL_LANGUAGE_MODE,
        False, "", "", "", time_scale_hint_s="4",
    )
    assert report.status == "awaiting_specifications"
    payload = {
        "specification_facts": [],
        "model": {
            "kind": "transfer_function",
            "numerator": [10.0],
            "denominator": [2.0, 1.0],
            "input_signal_id": "heater",
            "output_signal_id": "temperature",
            "input_units": "normalized_input",
            "output_units": "degC",
        },
        "experiment": {"sample_time_s": 0.2, "duration_s": 20},
        "eight_segment_evidence": {"stability": "bounded"},
    }

    resolved, next_state = submit_app_json(
        state,
        uploaded_json=None,
        pasted_json=json.dumps(payload),
        simulation_bounds_confirmed=True,
    )

    assert resolved.status == "validation_pending"
    assert resolved.controller.release_level == "candidate_unvalidated"
    assert next_state["session"] is None


def test_app_json_submission_requires_exactly_one_file_or_pasted_source(tmp_path):
    with pytest.raises(ValueError, match="选择一种"):
        submit_app_json({}, uploaded_json=None, pasted_json="")

    path = tmp_path / "payload.json"
    path.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="只能选择一种"):
        submit_app_json({}, uploaded_json=str(path), pasted_json="{}")


def test_app_trace_manifest_cannot_read_an_unuploaded_server_path(tmp_path):
    report, state = start_app_run(
        "A measured first order heater settles after a small power change.",
        "temperature",
        "heater",
        "input_min=-1\ninput_max=1\noutput_min=-10\noutput_max=10",
        NATURAL_LANGUAGE_MODE,
        False,
        "",
        "",
        "",
        time_scale_hint_s="4",
    )
    assert report.status == "awaiting_specifications"
    server_file = tmp_path / "server-local.csv"
    server_file.write_text("time,input,output\n0,0,0\n1,1,1\n2,1,1\n", encoding="utf-8")
    manifest = {
        "csv_path": str(server_file),
        "primitive": "ramp_step",
        "repeat_index": 1,
        "time_column": "time",
        "signal_columns": {"input": "input", "output": "output"},
        "signal_units": {"time": "s", "input": "V", "output": "degC"},
        "estimates": ["static_gain", "time_constant"],
        "operating_region": "nominal",
        "trial_id": "server-file",
        "data_source": "claimed upload",
    }

    with pytest.raises(ValueError, match="上传的 CSV"):
        submit_app_evidence(
            state,
            model_json="",
            trace_files=None,
            trace_manifest_json=json.dumps([manifest]),
            validation_json="",
            demo_confirmed=False,
            simulation_bounds_confirmed=True,
        )


def test_app_can_submit_plain_language_specifications_as_default_path():
    report, state = start_app_run(
        "A measured first order heater settles after a small power change.",
        "temperature", "heater power", "", NATURAL_LANGUAGE_MODE,
        False, "", "", "",
    )
    assert report.status == "awaiting_specifications"

    with pytest.raises(ValueError, match="软件仿真"):
        submit_app_specifications(
            state,
            "input_change=1 normalized_input;",
            simulation_bounds_confirmed=False,
        )

    resolved, next_state = submit_app_specifications(
        state,
        (
            "From the manual: input_change=1 normalized_input; "
            "steady_output_change=10 degC; response_time_s=20 s; "
            "input_min=-2 normalized_input; input_max=2 normalized_input; "
            "output_min=-30 degC; output_max=80 degC."
        ),
        simulation_bounds_confirmed=True,
    )

    assert resolved.status == "candidate_unvalidated"
    assert resolved.evidence_boundary == "declared_specification_model_only"
    assert resolved.controller.release_level == "candidate_unvalidated"
    assert resolved.system_description.simulation_boundary_confirmation.confirmed is True
    assert (
        resolved.system_description.simulation_boundary_confirmation.scope
        == "software_simulation_only"
    )
    assert next_state["session"] is None


def test_gradio_specification_submission_accepts_motor_voltage_and_unicode_acceleration_units(monkeypatch):
    report, state = start_app_run(
        (
            "A low-friction motor positioning axis accelerates under applied voltage "
            "and keeps drifting after voltage is removed. Position and speed are measured."
        ),
        "motor position, motor speed",
        "motor voltage",
        "",
        NATURAL_LANGUAGE_MODE,
        False,
        "",
        "",
        "",
    )
    assert report.status == "awaiting_specifications"
    assert report.semantic_selection.simulation_profile_id == "double_integrator"
    paragraph = (
        "The held motor voltage has a baseline of 0.0 V and an allowed operating "
        "range of −5.0 V to +5.0 V. The voltage is changed by +0.5 V. "
        "This produces an angular-acceleration change of approximately +1.0 rad/s². "
        "A typical target change takes approximately 2.0 s. "
        "The permitted position range is −2.5 rad to +2.5 rad."
    )

    class MotorSpecificationAdapter:
        def assess_specifications(self, *args):
            template = args[4][0]
            def fact(fact_id, value, unit, source_text):
                return {
                    "fact_id": fact_id,
                    "value": value,
                    "unit": unit,
                    "source_type": "user_known_behavior",
                    "source_text": source_text,
                }

            return {
                "status": "ready",
                "template_id": template.template_id,
                "facts": [
                    fact("input_change", 0.5, "V", "voltage is changed by +0.5 V"),
                    fact(
                        "acceleration_change",
                        1.0,
                        "rad/s²",
                        "angular-acceleration change of approximately +1.0 rad/s²",
                    ),
                    fact("motion_time_scale_s", 2.0, "s", "takes approximately 2.0 s"),
                    fact("input_min", -5.0, "V", "range of −5.0 V to +5.0 V"),
                    fact("input_max", 5.0, "V", "range of −5.0 V to +5.0 V"),
                    fact(
                        "output_min", -2.5, "rad", "position range is −2.5 rad to +2.5 rad"
                    ),
                    fact(
                        "output_max", 2.5, "rad", "position range is −2.5 rad to +2.5 rad"
                    ),
                ],
                "missing_fact_ids": [],
                "conflicts": [],
                "questions": [],
                "rationale": "All required facts were explicitly stated.",
            }

    state["use_llm"] = True
    monkeypatch.setattr(
        "cfdc.web.service.build_adapter",
        lambda *args: MotorSpecificationAdapter(),
    )

    resolved, next_state = submit_app_specifications(
        state,
        paragraph,
        simulation_bounds_confirmed=True,
    )

    assert resolved.status == "candidate_unvalidated"
    assert resolved.compiled_specification_model.model.input_units == "V"
    assert resolved.compiled_specification_model.model.output_units == "rad"
    input_gain = {item.feature_id: item for item in resolved.features}["input_gain"]
    assert input_gain.value == pytest.approx(2.0)
    assert input_gain.units == "rad/s^2/V"
    assert resolved.controller.saturation == {
        "input_min": -5.0,
        "input_max": 5.0,
    }
    assert next_state["session"] is None


def test_gradio_missing_unit_returns_to_specification_questions_instead_of_error(monkeypatch):
    report, state = start_app_run(
        "A measured first order heater settles after a small power change.",
        "temperature",
        "heater power",
        "",
        NATURAL_LANGUAGE_MODE,
        False,
        "",
        "",
        "",
    )
    assert report.status == "awaiting_specifications"

    class MissingUnitAdapter:
        def assess_specifications(self, *args):
            template = args[4][0]
            return {
                "status": "need_more",
                "template_id": template.template_id,
                "facts": [{
                    "fact_id": "input_change",
                    "value": 1.0,
                    "unit": "",
                    "source_type": "user_known_behavior",
                    "source_text": "input change is 1",
                }],
                "missing_fact_ids": ["input_change"],
                "conflicts": [],
                "questions": [],
                "rationale": "The value is explicit but its unit is missing.",
            }

    state["use_llm"] = True
    monkeypatch.setattr(
        "cfdc.web.service.build_adapter",
        lambda *args: MissingUnitAdapter(),
    )

    unresolved, next_state = submit_app_specifications(
        state,
        "The input change is 1, but I do not know the unit yet.",
        simulation_bounds_confirmed=True,
    )

    assert unresolved.status == "need_more_specifications"
    assert "input_change" in unresolved.specification_assessment.missing_fact_ids
    assert next_state["session"] is not None


def test_repeated_specification_gap_is_rendered_as_no_progress_not_full_question_loop():
    report, state = start_app_run(
        "A measured first order heater settles after a small power change.",
        "temperature",
        "heater power",
        "",
        NATURAL_LANGUAGE_MODE,
        False,
        "",
        "",
        "",
    )

    unresolved, _ = submit_app_specifications(
        state,
        "The heater is fast and strong, but I do not know numeric values.",
        simulation_bounds_confirmed=True,
    )
    guidance = render_report(unresolved)["specification_guidance"]

    assert unresolved.specification_assessment.no_progress is True
    assert "本次提交未增加可验证规格" in guidance
    assert "仍缺少" in guidance
    assert "为什么需要" not in guidance


def test_no_llm_specification_form_accepts_answers_in_visible_question_order():
    report, state = start_app_run(
        "A measured first order heater settles after a small power change.",
        "temperature", "heater power", "", NATURAL_LANGUAGE_MODE,
        False, "", "", "",
    )
    assert report.status == "awaiting_specifications"

    partial, state = submit_app_specifications(
        state,
        "1 normalized_input\n10 degC\n20 s\n-2 normalized_input",
        simulation_bounds_confirmed=True,
    )

    assert partial.status == "need_more_specifications"
    facts = partial.specification_assessment.facts
    assert {item.fact_id for item in facts} == {
        "input_change", "steady_output_change", "response_time_s", "input_min"
    }

    resolved, state = submit_app_specifications(
        state,
        "2 normalized_input\n-30 degC\n80 degC",
        simulation_bounds_confirmed=True,
    )

    assert resolved.status == "candidate_unvalidated"
    assert state["session"] is None


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

    assert report.status == "awaiting_specifications"
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


def test_gradio_exposes_object_evidence_inputs_and_five_stage_progress():
    app = build_app()
    labels = {
        component["props"].get("label")
        for component in app.config["components"]
    }
    buttons = {
        component["props"].get("value")
        for component in app.config["components"]
        if component["type"] == "button"
    }

    assert {
        "用自然语言补充设备规格",
        "数学模型 JSON",
        "闭环验证条件 JSON（可选）",
        "JSON 数据文件（.json）",
        "粘贴 JSON 数据（可选）",
        "我确认所提交的输入/输出范围仅作为本次软件仿真的停止边界",
        "确认仅运行标准对象演示",
    }.issubset(labels)
    assert "实测 CSV（可多选）" not in labels
    assert "实测数据 Manifest JSON" not in labels
    assert {
        "开始诊断",
        "提交规格信息",
        "提交 JSON 数据",
        "提交高级模型 / 运行演示",
    }.issubset(buttons)

    report, _ = start_app_run(
        "A measured first order heater settles after a small power change.",
        "temperature", "heater", "", NATURAL_LANGUAGE_MODE,
        False, "", "", "",
    )
    progress = render_report(report)["progress"]
    assert progress.count('class="flow-step') == 5
    assert "规格模型" in progress


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

    assert report.status == "awaiting_specifications"
    assert state["session"] is not None


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

    assert report.status == "awaiting_specifications"
    assert calls == {"diagnose": 1, "select": 1}


def test_detailed_type_i_to_iii_examples_stop_at_object_evidence_gate():
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

        assert report.status == "awaiting_specifications"
        assert str(report.classification.primary_class) == archetype
        assert report.semantic_selection.simulation_profile_id == profile
        assert report.experiment_results == []
        assert report.features == []
        assert report.controller is None
        assert report.algorithm1_state is None
        assert report.adapted_controller_performance is None
        assert state["session"] is not None


def test_detailed_type_iv_and_v_examples_stop_at_object_evidence_gate():
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

        assert report.status == "awaiting_specifications"
        assert str(report.classification.primary_class) == archetype
        assert report.semantic_selection.simulation_profile_id == profile
        assert report.experiment_results == []
        assert report.features == []
        assert report.controller is None
        assert report.algorithm1_state is None
        assert report.adapted_controller_performance is None
        assert state["session"] is not None


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

    assert report.status == "demo_completed"
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

    assert completed.status == "awaiting_specifications"
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

    assert len(reset) == 41
    assert reset[0] == NATURAL_LANGUAGE_MODE
    assert "六项" in reset[1]
    assert reset[2:8] == ("", "", "", "", "", "")
    assert reset[8] is False
    assert reset[9] is False
    assert reset[10] == "https://provider.example/v1"
    assert reset[11] == "provider-model"
    assert reset[12] == ""
    assert reset[14:21] == ("", None, "", "", "", False, False)
    assert reset[21] == {}
