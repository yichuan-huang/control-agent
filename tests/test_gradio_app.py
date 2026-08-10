import json
from pathlib import Path

import pytest

from cfdc.diagnosis import (
    DeterministicDiagnosticAdapter,
    start_diagnostic_session,
    submit_specifications_to_session,
)
from cfdc.diagnosis.engine import infer_structural_diagnosis
from cfdc.models import (
    DiagnosticSessionState,
    DiagnosticTurn,
    MeasuredFact,
    MeasurementAssessment,
    SystemDescription,
)
from cfdc.runtime import run_cfdc_route
from cfdc.web import linked_tuning_service as linked_service
from cfdc.web import linked_tuning_ui as linked_ui
from cfdc.web import service as web_service
from cfdc.web import ui as web_ui
from cfdc.web.linked_tuning_service import (
    decode_lab_state,
    link_stage5_report,
)
from cfdc.web.presentation import render_report, stage_progress_html
from cfdc.web.service import (
    ROUTE_CHOICES,
    continue_app_run,
    parse_names,
    parse_safety_bounds,
    submit_app_evidence,
    submit_app_json,
    submit_app_measurement_response,
    submit_app_specifications,
)
from cfdc.web.service import start_app_run as _start_app_run
from cfdc.web.ui import (
    NATURAL_LANGUAGE_MODE,
    build_app,
    reset_ui,
    run_from_ui,
)
from cfdc.workflow import deterministic_profile_selection

_GUIDED_FACTS = {
    "open_loop_stability": "settles or remains bounded",
    "minimum_phase": "starts in its final direction rather than moving the opposite way first",
    "significant_delay": "begins within one sample without a separate silent interval",
    "relative_degree": "one or two dominant storage or integration processes",
    "controllability_observability": "all relevant motion can be reconstructed from these synchronized records",
    "nonlinearity_strength": "small positive and negative trials are smooth, reversible, and nearly proportional",
    "coupling_severity": "one main physical route from actuation to the measured motion",
    "uncertainty_magnitude": "change the response rate and final level by a modest amount",
}

_COMPLETE_GUIDED_RESPONSE = "\n".join(
    f"{request_id}: {source_excerpt}"
    for request_id, source_excerpt in _GUIDED_FACTS.items()
)

_GUIDED_BEHAVIOR_DESCRIPTIONS = (
    (
        "这是一个由电加热器调节的恒温箱。温度传感器连续记录箱内温度，"
        "已有日志包含小幅加热功率变化前后的温度曲线；一个采样周期内温度就沿最终方向开始变化，"
        "恢复原功率后温度逐渐回到原水平，正反变化平滑且近似成比例。"
    ),
    (
        "质量块通过弹簧和阻尼器连接在支架上，由双向水平力驱动，位置传感器记录完整运动。"
        "现有小幅试验记录显示释放后会出现往复运动并多次穿过平衡位置，振幅逐次减小；"
        "一个采样周期内就开始变化，正反方向的小力变化产生近似对称的响应。"
    ),
    (
        "低摩擦小车由双向电机力驱动，位置和速度传感器连续记录同一段平移运动。"
        "已有小幅试验记录显示施力后一个采样周期内速度就沿施力方向变化；撤力后速度保持，"
        "位置继续漂移而不会自行返回，正反方向的力产生近似对称的变化。"
    ),
    (
        "带蒸汽析出的储液容器由进液阀门调节，液位传感器连续记录完整变化。"
        "已有小幅阀门试验显示一个采样周期内液位就开始变化，但开始时会先沿不利或相反方向运动，"
        "随后才转向并停在新的恒定位置；正反试验近似对称。"
    ),
    (
        "两个泵分别向连通容器供液，两个液位传感器同步记录液位。已有小幅单泵变化记录显示，"
        "改变任一执行器都会明显改变多个输出，但靠近该泵的液位变化更大；保持新泵速后两个液位"
        "最终停在新的恒定位置，正反泵速变化近似对称。"
    ),
)


def _guided_facts_for_description(description_text: str) -> dict[str, str]:
    facts_by_id = dict(_GUIDED_FACTS)
    lowered = description_text.lower()
    if "motor" in lowered and "drifting" in lowered:
        facts_by_id["open_loop_stability"] = (
            "after the input is removed, speed remains constant and position keeps drifting"
        )
    if "低摩擦小车" in description_text:
        facts_by_id["open_loop_stability"] = (
            "after the input is removed, speed retains an offset or keeps drifting"
        )
    if "往复运动" in description_text:
        facts_by_id["relative_degree"] = (
            "one or two dominant storage or integration processes with repeated peaks"
        )
    if "开始时会先沿不利或相反方向运动" in description_text:
        facts_by_id["minimum_phase"] = (
            "moves in an unfavorable or opposite direction before turning"
        )
    if "改变任一执行器都会明显改变多个输出" in description_text:
        facts_by_id["coupling_severity"] = "改变任一执行器都会明显改变多个输出"
    return facts_by_id


def _guided_response_for_description(description_text: str) -> str:
    return "\n".join(
        f"{request_id}: {source_excerpt}"
        for request_id, source_excerpt in _guided_facts_for_description(
            description_text
        ).items()
    )


class _CompleteGuidedAdapter:
    def diagnose(self, description):
        return infer_structural_diagnosis(description).model_dump(mode="json")

    def guide_description(self, description, guidance):
        del description
        return {
            "guidance": [item.model_dump(mode="json") for item in guidance],
            "observed_outputs": [],
            "actuators": [],
        }

    def phrase_measurement_plan(self, description, checklist, plan):
        del description, checklist
        return plan.model_dump(mode="json")

    def extract_measurements(
        self, description, measurement_plan, measurement_response, previous_assessment
    ):
        del measurement_response
        if previous_assessment is not None and previous_assessment.status == "ready":
            return previous_assessment.model_dump(mode="json")
        facts_by_id = _guided_facts_for_description(description.text)
        return MeasurementAssessment(
            status="ready",
            facts=[
                MeasuredFact(
                    request_id=request.request_id,
                    source_excerpt=facts_by_id[request.request_id],
                    text_value=facts_by_id[request.request_id],
                )
                for request in measurement_plan.requests
            ],
            rationale="All eight existing-record findings were verified.",
        ).model_dump(mode="json")

    def select_profile(self, description, diagnosis, classification, catalog):
        return deterministic_profile_selection(
            description, diagnosis, classification, catalog
        ).model_dump(mode="json")


class _ChecklistGuidanceAdapter:
    def __init__(self, response_by_field=None):
        self.response_by_field = response_by_field or {}

    def guide_description(self, description, guidance):
        del description
        return {
            "guidance": [
                {
                    **item.model_dump(mode="json"),
                    "response": self.response_by_field.get(
                        item.diagnostic_field_id, "unknown"
                    ),
                }
                for item in guidance
            ],
            "observed_outputs": [],
            "actuators": [],
        }

    def phrase_measurement_plan(self, description, checklist, plan):
        del description, checklist
        return plan.model_dump(mode="json")

@pytest.fixture
def guided_adapter(monkeypatch):
    adapter = _CompleteGuidedAdapter()
    monkeypatch.setattr(web_service, "build_adapter", lambda *args: adapter)
    return adapter


def _start_verified_app_run(*args, **kwargs):
    """Advance an explicitly LLM-enabled test setup through the v4 record gate."""

    use_llm = args[5] if len(args) > 5 else kwargs.get("use_llm")
    if use_llm is not True:
        raise AssertionError("verified test setup must explicitly enable the LLM")
    report, state = _start_app_run(*args, **kwargs)
    assert report.status == "awaiting_measurements"
    assert report.classification is None
    assert report.semantic_selection is None
    report, state = submit_app_measurement_response(
        state,
        _guided_response_for_description(str(args[0])),
    )
    return report, state


def _as_awaiting_evidence(state):
    session = DiagnosticSessionState.model_validate(state["session"]).model_copy(
        update={"status": "awaiting_evidence"}
    )
    return {**state, "session": session.model_dump(mode="json")}


def test_root_app_is_a_thin_launcher_and_legacy_package_app_is_removed():
    assert not Path("cfdc/app.py").exists()
    launcher = Path("app.py").read_text(encoding="utf-8")
    assert "from cfdc.web.ui import CSS, build_app" in launcher
    assert "def build_app" not in launcher


def test_gradio_exposes_agpl_notice_and_source_link():
    app = build_app()
    notices = [
        component["props"]
        for component in app.config["components"]
        if component["type"] == "markdown"
        and component["props"].get("elem_id") == "license-notice"
    ]

    assert len(notices) == 1
    assert notices[0]["value"] == (
        "Copyright (C) 2026 Yichuan Huang · "
        "[GNU AGPL v3.0 only](https://www.gnu.org/licenses/agpl-3.0.en.html) · "
        "[Source code](https://github.com/yichuan-huang/control-agent)"
    )


def test_app_runs_clear_description_and_renders_stage_tables():
    report = _guided_description_report()
    view = render_report(report)

    assert report.diagnostic_session is not None
    assert len(view["checklist"]) == 8
    assert view["diagnosis"] == []
    assert view["route"] == []
    assert view["experiments"] == []
    assert view["features"] == []
    assert view["controller"] == []
    assert view["performance"] == []
    assert "flow-step pending" in view["progress"]
    assert "待确认" in view["summary"]


def test_thermostat_checklist_renders_eight_hollow_missing_items():
    description = SystemDescription(
        text="这是一个由恒温器监测房间温度并控制电加热器通断的住宅供暖系统"
    )
    session = start_diagnostic_session(
        description,
        diagnostic_adapter=_ChecklistGuidanceAdapter(),
    )
    report = run_cfdc_route("demo").model_copy(
        update={"diagnostic_session": session}
    )

    view = render_report(report)

    assert session.status == "awaiting_measurements"
    assert len(view["checklist"]) == 8
    assert [row[1] for row in view["checklist"]] == ["○ 缺少描述"] * 8
    assert len(view["clarifications"]) == 8


def test_grounded_description_checks_only_answered_checklist_item():
    excerpt = "已有记录显示恢复原输入后房间温度会逐渐稳定"
    description = SystemDescription(
        text=(
            "这是一个住宅供暖系统。"
            f"{excerpt}，但没有记录其他动态现象。"
        )
    )
    session = start_diagnostic_session(
        description,
        diagnostic_adapter=_ChecklistGuidanceAdapter(
            {"open_loop_stability": excerpt}
        ),
    )
    report = run_cfdc_route("demo").model_copy(
        update={"diagnostic_session": session}
    )

    view = render_report(report)

    assert view["checklist"][0][1] == "✓ 已有线索"
    assert [row[1] for row in view["checklist"][1:]] == ["○ 缺少描述"] * 7
    assert len(view["clarifications"]) == 7
    assert all(excerpt not in prompt for _, prompt in view["clarifications"])


def test_complete_eight_item_description_switches_to_measurement_instruction():
    description_text = (
        "这是一个由恒温器监测房间温度并控制电加热器通断的住宅供暖系统。"
        "控制输入是二值加热命令，输出是由传感器或同步记录器连续获取的室温、加热器状态。"
        "在多次小幅且可逆的试验中，室温开始时就沿最终方向变化，不会先向相反方向运动；"
        "二值加热命令改变后，室温在一个采样周期内就开始变化，不会出现独立静默区间，"
        "而且从执行作用到可见响应只涉及一到两个主导储能或积分过程。"
        "把二值加热命令恢复到基准值后，室温最终会收敛或保持有界，不会出现自行增长的运动。"
        "改变二值加热命令的方向和幅值时，可以观察到固定滞环和继电切换，"
        "但非比例现象只存在于这条固定输入输出规律中，不会增加新的动态状态。"
        "二值加热命令与室温、加热器状态采用同一时钟记录，"
        "因此这些同步记录足以重建所有相关运动；"
        "装置只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动进入。"
        "在安全范围内改变负载、元件或运行条件并重复试验时，"
        "这些变化会使响应速度和最终水平发生适度变化，"
        "但不会改变主要运动方向和通道结构。"
    )
    response_by_field = {
        "open_loop_stability": (
            "把二值加热命令恢复到基准值后，室温最终会收敛或保持有界，"
            "不会出现自行增长的运动"
        ),
        "minimum_phase": "室温开始时就沿最终方向变化，不会先向相反方向运动",
        "significant_delay": (
            "二值加热命令改变后，室温在一个采样周期内就开始变化，"
            "不会出现独立静默区间"
        ),
        "relative_degree": "从执行作用到可见响应只涉及一到两个主导储能或积分过程",
        "controllability_observability": (
            "二值加热命令与室温、加热器状态采用同一时钟记录，"
            "因此这些同步记录足以重建所有相关运动"
        ),
        "nonlinearity_strength": (
            "可以观察到固定滞环和继电切换，但非比例现象只存在于这条固定输入输出规律中，"
            "不会增加新的动态状态"
        ),
        "coupling_severity": (
            "装置只有一条从执行作用到被测运动的主要物理通道，"
            "其他给定量只作为扰动进入"
        ),
        "uncertainty_magnitude": (
            "这些变化会使响应速度和最终水平发生适度变化，"
            "但不会改变主要运动方向和通道结构"
        ),
    }
    session = start_diagnostic_session(
        SystemDescription(text=description_text),
        diagnostic_adapter=_ChecklistGuidanceAdapter(response_by_field),
    )
    report = run_cfdc_route("demo").model_copy(
        update={"diagnostic_session": session}
    )

    view = render_report(report)
    outputs = web_ui._outputs(report, {"session": session.model_dump(mode="json")})

    assert [row[1] for row in view["checklist"]] == ["✓ 已有线索"] * 8
    assert view["clarifications"] == []
    assert outputs[16]["visible"] is True
    assert outputs[17]["visible"] is True
    assert outputs[18]["visible"] is True
    assert "八项问题描述已完成" in view["measurement_guidance"]
    assert "请把相应的值和原文摘录反馈给 AI" in view[
        "measurement_guidance"
    ]


@pytest.fixture(scope="module")
def candidate_report_with_first_four_stages_complete():
    report = _guided_verified_report()
    assert report.diagnosis is not None
    assert report.classification is not None
    return report.model_copy(update={"status": "candidate_unvalidated"})


@pytest.mark.parametrize(
    ("linked_state", "expected_state", "expected_icon"),
    [
        ("trial_pending", "waiting", "6"),
        ("needs_adjustment", "waiting", "6"),
        ("rolled_back", "waiting", "6"),
        ("stable", "done", "✓"),
        ("inconclusive", "blocked", "6"),
        ("budget_exhausted", "blocked", "6"),
    ],
)
def test_effect_validation_progress_uses_linked_state(
    candidate_report_with_first_four_stages_complete,
    linked_state,
    expected_state,
    expected_icon,
):
    html = stage_progress_html(
        candidate_report_with_first_four_stages_complete,
        linked_simulation_state=linked_state,
    )
    fifth = html.split('<div class="flow-step ')[-1]

    assert fifth.startswith(f'{expected_state}">')
    assert f"<span>{expected_icon}</span><small>效果验证与调优</small>" in fifth


@pytest.mark.parametrize(
    "status",
    ["validated_in_simulation", "demo_completed"],
)
def test_existing_validated_reports_keep_effect_validation_green(
    status, completed_cartpole_report
):
    report = completed_cartpole_report.model_copy(update={"status": status})

    html = stage_progress_html(report)
    fifth = html.split('<div class="flow-step ')[-1]

    assert fifth.startswith('done">')
    assert "<span>✓</span><small>效果验证与调优</small>" in fifth


def test_app_clarification_state_can_continue_into_full_simulation():
    description = SystemDescription(text="I have a machine.")
    session = start_diagnostic_session(
        description,
        diagnosis=infer_structural_diagnosis(description),
    ).model_copy(update={"status": "collecting_description"})
    state = {
        "session": session.model_dump(mode="json"),
        "use_llm": False,
        "include_trajectory": False,
    }

    completed, next_state = continue_app_run(
        state,
        [None, None, None, None],
        "It is a measured first-order thermal process that settles after a heater change.",
    )

    assert completed.status == "awaiting_measurements"
    assert completed.semantic_selection is None
    assert completed.experiment_results == []
    assert next_state["session"] is not None
    assert "api_key" not in next_state
    assert "base_url" not in next_state
    assert "model" not in next_state


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
    assert parse_names("temperature, pressure\nflow") == [
        "temperature",
        "pressure",
        "flow",
    ]
    assert parse_names("室温、加热器状态") == ["室温", "加热器状态"]
    assert parse_names(
        "body displacement, wheel displacement, and suspension travel"
    ) == [
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
    assert ROUTE_CHOICES == {"自然语言自动分析（主流程）": "generic"}


def test_app_can_submit_structured_model_evidence_after_diagnosis(guided_adapter):
    report, state = _start_verified_app_run(
        "A measured first order heater settles after a small power change.",
        "temperature",
        "heater",
        "input_min=-1\ninput_max=1\noutput_min=-10\noutput_max=10",
        NATURAL_LANGUAGE_MODE,
        True,
        "",
        "",
        "",
        time_scale_hint_s="4",
    )
    assert report.status == "awaiting_profile_measurements"
    state = _as_awaiting_evidence(state)

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


def test_standard_demo_is_exempt_from_user_simulation_boundary_confirmation(
    guided_adapter,
):
    report, state = _start_verified_app_run(
        "A measured first order heater settles after a small power change.",
        "temperature",
        "heater",
        "",
        NATURAL_LANGUAGE_MODE,
        True,
        "",
        "",
        "",
    )
    assert report.status == "awaiting_profile_measurements"
    state = _as_awaiting_evidence(state)

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


def test_app_can_submit_dataset_json_wrapper_from_pasted_text(guided_adapter):
    report, state = _start_verified_app_run(
        "A measured first order heater settles after a small power change.",
        "temperature",
        "heater",
        "input_min=0\ninput_max=1\noutput_min=64.5\noutput_max=65.5",
        NATURAL_LANGUAGE_MODE,
        True,
        "",
        "",
        "",
    )
    assert report.status == "awaiting_profile_measurements"
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
    assert (
        resolved.system_description.simulation_boundary_confirmation.confirmed is True
    )
    assert next_state["session"] is None


def test_app_can_submit_dataset_json_wrapper_from_uploaded_file(
    tmp_path, guided_adapter
):
    _report, state = _start_verified_app_run(
        "A measured first order heater settles after a small power change.",
        "temperature",
        "heater",
        "input_min=-1\ninput_max=1\noutput_min=-20\noutput_max=20",
        NATURAL_LANGUAGE_MODE,
        True,
        "",
        "",
        "",
    )
    payload_path = tmp_path / "thermostat.json"
    payload_path.write_text(
        json.dumps(
            {
                "specification_facts": [
                    {"fact_id": "input_change", "value": 1, "unit": "binary_command"},
                    {"fact_id": "steady_output_change", "value": 50, "unit": "degF"},
                    {"fact_id": "response_time_s", "value": 20, "unit": "s"},
                    {"fact_id": "input_min", "value": 0, "unit": "binary_command"},
                    {"fact_id": "input_max", "value": 1, "unit": "binary_command"},
                    {"fact_id": "output_min", "value": 64.5, "unit": "degF"},
                    {"fact_id": "output_max", "value": 65.5, "unit": "degF"},
                ]
            }
        ),
        encoding="utf-8",
    )

    resolved, next_state = submit_app_json(
        state,
        uploaded_json=str(payload_path),
        pasted_json="",
        simulation_bounds_confirmed=True,
    )

    assert resolved.status == "candidate_unvalidated"
    assert resolved.compiled_specification_model.derived_features[
        "static_gain"
    ] == pytest.approx(50.0)
    assert next_state["session"] is None


def test_thermostat_natural_language_and_json_compile_equivalent_models(
    guided_adapter,
):
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
    natural_initial, natural_state = _start_verified_app_run(
        description,
        "room temperature, heater state",
        "binary heater command",
        "",
        NATURAL_LANGUAGE_MODE,
        True,
        "",
        "",
        "",
    )
    _, json_state = _start_verified_app_run(
        description,
        "room temperature, heater state",
        "binary heater command",
        "",
        NATURAL_LANGUAGE_MODE,
        True,
        "",
        "",
        "",
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
    natural_reviewed = submit_specifications_to_session(
        natural_session,
        paragraph,
        simulation_bounds_confirmed=True,
    )
    json_reviewed = submit_specifications_to_session(
        json_session,
        web_service._specification_facts_to_text(json_session, facts_payload),
        simulation_bounds_confirmed=True,
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
    assert natural_reviewed.compiled_specification_model.model.model_dump(
        mode="json"
    ) == json_reviewed.compiled_specification_model.model.model_dump(mode="json")
    assert (
        natural_reviewed.compiled_specification_model.safety_bounds
        == json_reviewed.compiled_specification_model.safety_bounds
    )
    guidance = render_report(
        natural_initial.model_copy(
            update={
                "specification_assessment": natural_reviewed.specification_assessment
            }
        )
    )["specification_guidance"]
    assert "经后端重算验证的推导规格" in guidance
    assert "3600 * heat_capacity / heat_transfer_coefficient" in guidance


def test_thermostat_prompt_goes_directly_to_effect_validation_without_ai(
    monkeypatch,
    guided_adapter,
):
    problem = (
        "这是一个由恒温器监测房间温度并控制电加热器通断的住宅供暖系统。"
        "控制输入是二值加热命令，输出是由传感器或同步记录器连续获取的室温、"
        "加热器状态。在多次小幅且可逆的试验中，室温开始时就沿最终方向变化，"
        "不会先向相反方向运动；二值加热命令改变后，室温在一个采样周期内就"
        "开始变化，不会出现独立静默区间，而且从执行作用到可见响应只涉及一到"
        "两个主导储能或积分过程。把二值加热命令恢复到基准值后，室温最终会"
        "收敛或保持有界，不会出现自行增长的运动。改变二值加热命令的方向和"
        "幅值时，可以观察到固定滞环和继电切换，但非比例现象只存在于这条固定"
        "输入输出规律中，不会增加新的动态状态。二值加热命令与室温、加热器"
        "状态采用同一时钟记录，因此这些同步记录足以重建所有相关运动；装置"
        "只有一条从执行作用到被测运动的主要物理通道，其他给定量只作为扰动"
        "进入。在安全范围内改变负载、元件或运行条件并重复试验时，这些变化"
        "会使响应速度和最终水平发生适度变化，但不会改变主要运动方向和通道"
        "结构。"
    )
    prompt = (
        "采用室外温度 50 degF、设定值 65 degF、等效热容 "
        "20000 Btu/degF、传热系数 500 Btu/(h*degF)、炉子供热率 "
        "25000 Btu/h 和滞环半宽 0.5 degF。初温取 64.5 degF 且炉子"
        "开启，以 60 s 采样仿真 6 h。\n\n"
        "input_change=1 binary_command; "
        "steady_output_change=50 degF; "
        "response_time_s=144000 s; "
        "input_min=0 binary_command; "
        "input_max=1 binary_command; "
        "output_min=64.5 degF; "
        "output_max=65.5 degF;"
    )
    initial, app_state = _start_verified_app_run(
        problem,
        "室温、加热器状态",
        "二值加热命令",
        (
            "max_abs_reference_normalized=0.25\n"
            "max_abs_output_normalized=1.5\n"
            "max_abs_actuator_normalized=1.0\n"
            "max_test_duration_s=80.0"
        ),
        NATURAL_LANGUAGE_MODE,
        True,
        "",
        "",
        "",
        forbidden_actions=(
            "向真实物理硬件下发命令\n"
            "关闭仿真饱和或自动停止检查\n"
            "输出或执行器越界后继续运行\n"
            "安全验证时把题目声明的非线性替换为无限制线性环节"
        ),
        time_scale_hint_s="10.0",
    )
    assert initial.status == "awaiting_profile_measurements"
    resolved, _ = submit_app_specifications(
        app_state,
        prompt,
        simulation_bounds_confirmed=True,
    )

    def forbidden_adapter(*args, **kwargs):
        del args, kwargs
        raise AssertionError("model discovery must not be called")

    monkeypatch.setattr(
        linked_service,
        "OpenAICompatibleDiagnosticAdapter",
        forbidden_adapter,
    )
    state, view = link_stage5_report(
        resolved.model_dump(mode="json"),
        base_url="https://unused.example/v1",
        model="must-not-be-called",
        api_key="must-not-be-used",
    )
    session = decode_lab_state(state)

    assert resolved.status == "candidate_unvalidated"
    assert resolved.compiled_specification_model is not None
    assert resolved.compiled_specification_model.derived_features[
        "static_gain"
    ] == pytest.approx(50.0)
    assert resolved.compiled_specification_model.derived_features[
        "time_constant"
    ] == pytest.approx(144000.0)
    assert session.origin == "stage5_candidate_model"
    assert session.confirmed_model.numerator == pytest.approx([50.0])
    assert session.confirmed_model.denominator == pytest.approx([144000.0, 1.0])
    assert session.state == "trial_pending"
    assert view["controls"]["run_trial"] is True
    assert "discovery" not in state

    compact_report = render_report(resolved)["raw"]
    compact_trace = compact_report["experiment_results"][0]["trace"]
    assert compact_trace["sample_count"] > 0
    assert "time_s" not in compact_trace
    ui_outputs = linked_ui._sync_callback(compact_report, {})
    assert ui_outputs[0]["state"] == "trial_pending"
    assert "flow-step waiting" in ui_outputs[-1]

    trial_state, trial_view = linked_service.run_linked_trial(
        state,
        view["parameter_rows"],
        expected_revision=state["revision"],
    )
    stored_trace = trial_state["trials"][-1]["traces"][0]
    assert len(stored_trace["time_s"]) >= 3
    assert trial_view["output_frame"]["time_s"].nunique() >= 3
    assert trial_view["control_frame"]["time_s"].nunique() >= 3


def test_app_dataset_wrapper_with_empty_facts_uses_its_complete_model(
    guided_adapter,
):
    report, state = _start_verified_app_run(
        "A measured first order heater settles after a small power change.",
        "temperature",
        "heater",
        "max_abs_output_normalized=20\nmax_abs_actuator_normalized=1",
        NATURAL_LANGUAGE_MODE,
        True,
        "",
        "",
        "",
        time_scale_hint_s="4",
    )
    assert report.status == "awaiting_profile_measurements"
    state = _as_awaiting_evidence(state)
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


def test_app_trace_manifest_cannot_read_an_unuploaded_server_path(
    tmp_path, guided_adapter
):
    report, state = _start_verified_app_run(
        "A measured first order heater settles after a small power change.",
        "temperature",
        "heater",
        "input_min=-1\ninput_max=1\noutput_min=-10\noutput_max=10",
        NATURAL_LANGUAGE_MODE,
        True,
        "",
        "",
        "",
        time_scale_hint_s="4",
    )
    assert report.status == "awaiting_profile_measurements"
    state = _as_awaiting_evidence(state)
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


def test_app_can_submit_plain_language_specifications_as_default_path(guided_adapter):
    report, state = _start_verified_app_run(
        "A measured first order heater settles after a small power change.",
        "temperature",
        "heater power",
        "",
        NATURAL_LANGUAGE_MODE,
        True,
        "",
        "",
        "",
    )
    assert report.status == "awaiting_profile_measurements"

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
    assert (
        resolved.system_description.simulation_boundary_confirmation.confirmed is True
    )
    assert (
        resolved.system_description.simulation_boundary_confirmation.scope
        == "software_simulation_only"
    )
    assert next_state["session"] is None


def test_gradio_specification_submission_accepts_motor_voltage_and_unicode_acceleration_units(
    monkeypatch,
    guided_adapter,
):
    report, state = _start_verified_app_run(
        (
            "A low-friction motor positioning axis accelerates under applied voltage "
            "and keeps drifting after voltage is removed. Position and speed are measured."
        ),
        "motor position, motor speed",
        "motor voltage",
        "",
        NATURAL_LANGUAGE_MODE,
        True,
        "",
        "",
        "",
    )
    assert report.status == "awaiting_profile_measurements"
    assert report.semantic_selection.simulation_profile_id == "double_integrator"
    paragraph = (
        "The held motor voltage has a baseline of 0.0 V and an allowed operating "
        "range of −5.0 V to +5.0 V. The voltage is changed by +0.5 V. "
        "This produces an angular-acceleration change of approximately +1.0 rad/s². "
        "A typical target change takes approximately 2.0 s. "
        "The permitted position range is −2.5 rad to +2.5 rad."
    )

    class MotorSpecificationAdapter(_CompleteGuidedAdapter):
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
                        "output_min",
                        -2.5,
                        "rad",
                        "position range is −2.5 rad to +2.5 rad",
                    ),
                    fact(
                        "output_max",
                        2.5,
                        "rad",
                        "position range is −2.5 rad to +2.5 rad",
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


def test_gradio_missing_unit_returns_to_specification_questions_instead_of_error(
    monkeypatch,
    guided_adapter,
):
    report, state = _start_verified_app_run(
        "A measured first order heater settles after a small power change.",
        "temperature",
        "heater power",
        "",
        NATURAL_LANGUAGE_MODE,
        True,
        "",
        "",
        "",
    )
    assert report.status == "awaiting_profile_measurements"

    class MissingUnitAdapter(_CompleteGuidedAdapter):
        def assess_specifications(self, *args):
            template = args[4][0]
            return {
                "status": "need_more",
                "template_id": template.template_id,
                "facts": [
                    {
                        "fact_id": "input_change",
                        "value": 1.0,
                        "unit": "",
                        "source_type": "user_known_behavior",
                        "source_text": "input change is 1",
                    }
                ],
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

    assert unresolved.status == "awaiting_profile_measurements"
    assert "input_change" in unresolved.specification_assessment.missing_fact_ids
    assert next_state["session"] is not None


def test_repeated_specification_gap_is_rendered_as_no_progress_not_full_question_loop(
    guided_adapter,
):
    _report, state = _start_verified_app_run(
        "A measured first order heater settles after a small power change.",
        "temperature",
        "heater power",
        "",
        NATURAL_LANGUAGE_MODE,
        True,
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


def test_specification_form_accepts_answers_in_visible_question_order(
    guided_adapter,
):
    report, state = _start_verified_app_run(
        "A measured first order heater settles after a small power change.",
        "temperature",
        "heater power",
        "",
        NATURAL_LANGUAGE_MODE,
        True,
        "",
        "",
        "",
    )
    assert report.status == "awaiting_profile_measurements"

    partial, state = submit_app_specifications(
        state,
        "1 normalized_input\n10 degC\n20 s\n-2 normalized_input",
        simulation_bounds_confirmed=True,
    )

    assert partial.status == "awaiting_profile_measurements"
    facts = partial.specification_assessment.facts
    assert {item.fact_id for item in facts} == {
        "input_change",
        "steady_output_change",
        "response_time_s",
        "input_min",
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


def test_start_app_run_passes_forbidden_actions_and_time_scale_to_system_description(
    monkeypatch,
    guided_adapter,
):
    captured = {}
    real_system_description = SystemDescription

    def capture_system_description(**kwargs):
        captured.update(kwargs)
        return real_system_description(**kwargs)

    monkeypatch.setattr(web_service, "SystemDescription", capture_system_description)

    report, _ = _start_verified_app_run(
        "A measured first order heater settles after a small power change.",
        "temperature",
        "heater",
        "max_abs_control=1.0",
        NATURAL_LANGUAGE_MODE,
        True,
        "",
        "",
        "",
        forbidden_actions="free release\nphysical deployment",
        time_scale_hint_s="2.5",
    )

    assert report.status == "awaiting_profile_measurements"
    assert captured["forbidden_actions"] == ["free release", "physical deployment"]
    assert captured["time_scale_hint_s"] == 2.5
    assert report.system_description.forbidden_actions == [
        "free release",
        "physical deployment",
    ]
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


def test_gradio_exposes_only_the_single_domain_description_input():
    app = build_app()
    textboxes = {
        component["props"].get("label"): component["props"]
        for component in app.config["components"]
        if component["type"] == "textbox"
    }

    assert "控制问题描述" in textboxes
    assert {
        "可观察输出",
        "执行器",
        "安全边界",
        "禁止实验动作",
        "主导时间尺度（秒）",
    }.isdisjoint(textboxes)


def test_gradio_exposes_guided_measurement_and_tuning_flow():
    app = build_app()
    labels = {component["props"].get("label") for component in app.config["components"]}
    buttons = {
        component["props"].get("value")
        for component in app.config["components"]
        if component["type"] == "button"
    }

    assert {
        "现有记录与测量回复",
        "诊断检查清单",
        "我确认所提交的输入/输出范围仅作为本次软件仿真的停止边界",
        "已编译对象模型",
        "已载入控制器",
    }.issubset(labels)
    assert "数学模型 JSON" not in labels
    assert "JSON 数据文件（.json）" not in labels
    assert "确认仅运行标准对象演示" not in labels
    assert "请用自然语言回答" not in labels
    assert {
        "检查描述并继续",
        "提交测量回复",
        "运行初始控制器效果验证",
        "请求 AI 下一轮参数",
        "批准并运行下一轮",
    }.issubset(buttons)
    assert {"开始引导诊断", "提交描述补充"}.isdisjoint(buttons)
    assert {
        "采用此示例值",
        "请求 AI 判断还缺什么",
        "提交回答并继续",
        "确认该模型并继续",
    }.isdisjoint(buttons)

    progress = render_report(_guided_description_report())["progress"]
    assert progress.count('class="flow-step') == 6
    assert "AI 测量计划" in progress


def _ancestor_ids(layout, target_id, ancestors=()):
    if layout["id"] == target_id:
        return ancestors
    for child in layout.get("children", []):
        found = _ancestor_ids(
            child,
            target_id,
            (*ancestors, layout["id"]),
        )
        if found is not None:
            return found
    return None


def test_linked_tuning_panel_is_inside_tuning_tab():
    app = build_app()
    components = {component["id"]: component for component in app.config["components"]}
    panel_id = next(
        component["id"]
        for component in app.config["components"]
        if component["props"].get("elem_id") == "linked-tuning-panel"
    )
    ancestors = _ancestor_ids(app.config["layout"], panel_id)
    assert ancestors is not None
    ancestor_labels = {
        components[component_id]["props"].get("label")
        for component_id in ancestors
        if component_id in components
    }

    assert "调优与适应" in ancestor_labels
    assert "控制器" not in ancestor_labels


def test_linked_tuning_mutations_refresh_main_stage_progress():
    app = build_app()
    components = {component["id"]: component for component in app.config["components"]}
    run_trial_id = next(
        component_id
        for component_id, component in components.items()
        if component["props"].get("elem_id") == "linked-run-trial"
    )
    progress_id = next(
        component_id
        for component_id, component in components.items()
        if component["props"].get("elem_id") == "stage-progress"
    )
    report_id = next(
        component_id
        for component_id, component in components.items()
        if component["props"].get("label") == "完整阶段记录"
    )
    dependency = next(
        item
        for item in app.config["dependencies"]
        if (run_trial_id, "click") in item["targets"]
    )

    assert report_id in dependency["inputs"]
    assert progress_id in dependency["outputs"]


def test_main_ui_exposes_no_examples_component():
    app = build_app()

    assert all(
        component["type"] != "examples"
        for component in app.config["components"]
    )
    assert all(
        component["props"].get("label") != "控制问题描述示例"
        for component in app.config["components"]
    )


def test_uninitialized_required_description_uses_validation_error():
    with pytest.raises(ValueError, match="请描述需要控制的对象"):
        _start_app_run(
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


def test_generic_web_flow_rejects_disabled_llm(monkeypatch):
    description = _GUIDED_BEHAVIOR_DESCRIPTIONS[0]
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

    with pytest.raises(ValueError, match="需要启用 LLM"):
        _start_app_run(
            description,
            "",
            "",
            None,
            NATURAL_LANGUAGE_MODE,
            False,
            None,
            None,
            None,
        )


def test_generic_web_flow_requires_complete_provider_configuration(monkeypatch):
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

    with pytest.raises(
        ValueError,
        match="Missing OpenAI-compatible LLM configuration.*base URL, model, API key",
    ):
        _start_app_run(
            _GUIDED_BEHAVIOR_DESCRIPTIONS[0],
            "",
            "",
            "",
            NATURAL_LANGUAGE_MODE,
            True,
            "",
            "",
            "",
        )


def test_uninitialized_answer_textboxes_use_validation_error():
    description = SystemDescription(text="I have a machine.")
    session = start_diagnostic_session(
        description,
        diagnosis=infer_structural_diagnosis(description),
    ).model_copy(update={"status": "collecting_description"})
    state = {
        "session": session.model_dump(mode="json"),
        "use_llm": False,
        "include_trajectory": False,
    }

    with pytest.raises(
        ValueError,
        match="provide a supplemental description",
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
        _start_app_run(
            "description", "output", "input", "", "unknown-route", False, "", "", ""
        )


def test_app_does_not_repeat_diagnosis_for_clear_description(monkeypatch):
    calls = {"diagnose": 0, "select": 0}
    delegate = DeterministicDiagnosticAdapter()

    class CountingAdapter(_CompleteGuidedAdapter):
        def diagnose(self, description):
            calls["diagnose"] += 1
            return delegate.diagnose(description)

        def select_profile(self, description, diagnosis, classification, catalog):
            calls["select"] += 1
            return delegate.select_profile(
                description, diagnosis, classification, catalog
            )

    adapter = CountingAdapter()
    monkeypatch.setattr("cfdc.web.service.build_adapter", lambda *args: adapter)
    report, state = _start_app_run(
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

    assert report.status == "awaiting_measurements"
    assert report.classification is None
    assert report.semantic_selection is None
    assert calls == {"diagnose": 0, "select": 0}

    report, _ = submit_app_measurement_response(
        state,
        _COMPLETE_GUIDED_RESPONSE,
        base_url="https://provider.example/v1",
        model="provider-model",
        api_key="test-key",
    )

    assert report.status == "awaiting_profile_measurements"
    assert report.classification is not None
    assert report.semantic_selection is not None
    assert calls == {"diagnose": 0, "select": 1}


@pytest.mark.parametrize(
    ("description", "expected_class", "expected_profile"),
    [
        (_GUIDED_BEHAVIOR_DESCRIPTIONS[0], "class_i_first_order_lag", "first_order_lag"),
        (_GUIDED_BEHAVIOR_DESCRIPTIONS[1], "class_ii_second_order_oscillator", "second_order_oscillator"),
        (_GUIDED_BEHAVIOR_DESCRIPTIONS[2], "class_iii_double_or_pure_integrator", "double_integrator"),
        (_GUIDED_BEHAVIOR_DESCRIPTIONS[3], "class_iv_higher_order_unstable_nonlinear_or_nmp", "nmp_inverse_response"),
        (_GUIDED_BEHAVIOR_DESCRIPTIONS[4], "class_v_multivariable_significant_coupling", "mimo_2x2_coupled"),
    ],
)
def test_type_i_to_v_behavior_descriptions_wait_for_measurements_before_releasing_route(
    description,
    expected_class,
    expected_profile,
    guided_adapter,
):
    initial, state = _start_app_run(
        description,
        "",
        "",
        "",
        NATURAL_LANGUAGE_MODE,
        True,
        "https://provider.example/v1",
        "provider-model",
        "test-key",
    )

    assert initial.status == "awaiting_measurements"
    assert initial.classification is None
    assert initial.semantic_selection is None
    assert initial.experiment_results == []
    assert initial.features == []
    assert initial.controller is None
    assert state["session"] is not None

    released, _ = submit_app_measurement_response(
        state,
        _guided_response_for_description(description),
        base_url="https://provider.example/v1",
        model="provider-model",
        api_key="test-key",
    )

    assert released.status == "awaiting_profile_measurements"
    assert str(released.classification.primary_class) == expected_class
    assert released.semantic_selection.simulation_profile_id == expected_profile
    assert released.experiment_results == []
    assert released.features == []
    assert released.controller is None


def test_main_ui_has_no_case_or_developer_route_selector():
    app = build_app()
    dropdown_labels = {
        component["props"].get("label")
        for component in app.config["components"]
        if component["type"] == "dropdown"
    }
    source = Path("cfdc/web/ui.py").read_text(encoding="utf-8")

    assert "运行方式" not in dropdown_labels
    assert "开发验证 ·" not in source
    assert "运行标准对象演示" not in source


def test_description_and_measurement_rounds_release_profile_only_after_verification(
    monkeypatch,
):
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

    class SequencedAdapter(_CompleteGuidedAdapter):
        def diagnose(self, description):
            calls["diagnose"] += 1
            return (incomplete if calls["diagnose"] == 1 else complete).model_dump(
                mode="json"
            )

        def select_profile(self, description, diagnosis, classification, catalog):
            calls["select"] += 1
            return delegate.select_profile(
                description, diagnosis, classification, catalog
            )

    adapter = SequencedAdapter()
    monkeypatch.setattr("cfdc.web.service.build_adapter", lambda *args: adapter)
    initial, state = _start_app_run(
        "I have a machine.",
        "",
        "",
        "",
        NATURAL_LANGUAGE_MODE,
        True,
        "https://provider.example/v1",
        "provider-model",
        "test-key",
    )
    assert "test-key" not in json.dumps(state)
    assert "api_key" not in state
    assert "base_url" not in state
    assert "model" not in state
    assert initial.status == "awaiting_measurements"
    assert initial.classification is None
    assert initial.semantic_selection is None

    continued, state = continue_app_run(
        state,
        [
            "Temperature is measured.",
            "A heater changes it.",
            "It moves in the expected direction.",
            "It starts promptly.",
        ],
        "It is a first order measured thermal process that settles.",
        base_url="https://provider.example/v1",
        model="provider-model",
        api_key="test-key",
    )

    assert continued.status == "awaiting_measurements"
    assert continued.classification is None
    assert continued.semantic_selection is None
    assert state["session"]["description_turn_count"] == 1
    assert state["session"]["measurement_round_count"] == 0
    assert calls == {"diagnose": 0, "select": 0}

    completed, _ = submit_app_measurement_response(
        state,
        _COMPLETE_GUIDED_RESPONSE,
        base_url="https://provider.example/v1",
        model="provider-model",
        api_key="test-key",
    )

    assert completed.status == "awaiting_profile_measurements"
    assert completed.classification is not None
    assert completed.semantic_selection is not None
    assert completed.diagnostic_session.measurement_round_count == 1
    assert calls == {"diagnose": 0, "select": 1}


def test_clear_resets_mode_credentials_session_and_report(monkeypatch):
    monkeypatch.setenv("CFDC_LLM_BASE_URL", "https://provider.example/v1")
    monkeypatch.setenv("CFDC_LLM_MODEL", "provider-model")
    reset = reset_ui()

    assert len(reset) == 29
    assert reset[:4] == (
        "",
        "https://provider.example/v1",
        "provider-model",
        "",
    )
    assert reset[4] == {}
    assert all(update.get("visible") is False for update in reset[-9:])


def _guided_description_report():
    description = SystemDescription(
        text="A heater changes a recorded temperature and the temperature settles.",
        observed_outputs=["temperature"],
        actuators=["heater"],
    )
    session = start_diagnostic_session(
        description,
        diagnosis=infer_structural_diagnosis(description),
    )
    return run_cfdc_route("demo").model_copy(
        update={"diagnostic_session": session}
    )


def _guided_verified_report():
    report = run_cfdc_route(
        "generic",
        description=SystemDescription(
            text="A strongly coupled process has two recorded outputs and two inputs.",
            observed_outputs=["y1", "y2"],
            actuators=["u1", "u2"],
        ),
        execution_mode="demo_fixture",
    )
    session = start_diagnostic_session(
        report.system_description,
        diagnosis=report.diagnosis,
    )
    facts = [
        MeasuredFact(
            request_id=request.request_id,
            source_excerpt=f"record for {request.request_id}",
            text_value="recorded observation",
        )
        for request in session.measurement_plan.requests
    ]
    assessment = MeasurementAssessment(
        status="ready",
        facts=facts,
        rationale="All current records were verified.",
    )
    session = session.model_copy(
        update={
            "status": "measurement_verified",
            "evidence_level": "measurement_verified",
            "classification": report.classification,
            "semantic_selection": report.semantic_selection,
            "measurement_assessment": assessment,
            "measurement_history": [assessment],
            "measurement_round_count": 1,
        }
    )
    return report.model_copy(update={"diagnostic_session": session})


def test_guided_gradio_has_one_domain_input_and_no_optional_legacy_controls():
    app = build_app()
    labels = {
        component["props"].get("label") for component in app.config["components"]
    }

    assert "控制问题描述" in labels
    assert "现有记录与测量回复" in labels
    assert "诊断检查清单" in labels
    assert {
        "控制问题",
        "可观察输出",
        "执行器",
        "安全边界",
        "禁止实验动作",
        "主导时间尺度（秒）",
        "启用 LLM 诊断、语义路由与规格整理",
        "保留完整轨迹",
    }.isdisjoint(labels)


def test_guided_progress_and_pre_measurement_technical_gates():
    view = render_report(_guided_description_report())

    assert view["progress"].count('class="flow-step') == 6
    for label in (
        "问题描述",
        "AI 测量计划",
        "测量回填",
        "系统分类",
        "初始控制器",
        "效果验证与调优",
    ):
        assert f"<small>{label}</small>" in view["progress"]
    assert len(view["checklist"]) == 8
    assert view["diagnosis"] == []
    assert view["route"] == []
    assert view["controller"] == []
    assert not any(view["technical_visibility"].values())


def test_guided_checklist_uses_status_icons_and_current_assessment_only():
    report = _guided_verified_report()
    session = report.diagnostic_session
    previous = session.measurement_assessment
    current = MeasurementAssessment(
        status="need_more",
        facts=previous.facts[1:],
        gaps=["open_loop_stability"],
        rationale="the stability record is no longer available",
    )
    session = session.model_copy(
        update={
            "status": "measurement_needs_more",
            "evidence_level": "description_only",
            "classification": None,
            "semantic_selection": None,
            "measurement_history": [previous, current],
            "measurement_assessment": current,
            "measurement_round_count": 2,
        }
    )
    rows = render_report(
        report.model_copy(update={"diagnostic_session": session})
    )["checklist"]

    assert [row[0] for row in rows] == [
        "恢复输入后会怎样",
        "输出最初往哪边变化",
        "多久开始变化",
        "有几个明显快慢阶段",
        "关键运动能否被带动和记录",
        "小幅正反变化是否近似一致",
        "一个作用会影响哪些读数",
        "换负载或工况后变化多大",
    ]
    assert rows[0][1] != "✓ 测量已验证"
    assert all(row[1] == "✓ 测量已验证" for row in rows[1:])


def test_guided_measurement_plan_and_timeline_are_auditable():
    report = _guided_verified_report()
    session = report.diagnostic_session
    turn = DiagnosticTurn(
        turn_index=1,
        questions=["supplemental_description"],
        answers={"supplemental_description": "heater and temperature are logged"},
        evidence=["Supplemental description: heater and temperature are logged"],
        diagnosis=session.current_diagnosis,
    )
    session = session.model_copy(
        update={"turns": [turn], "description_turn_count": 1}
    )
    view = render_report(report.model_copy(update={"diagnostic_session": session}))

    assert "existing_records_only" in view["measurement_guidance"]
    assert "open_loop_stability" in view["measurement_guidance"]
    assert "来源：Review an existing record." in view["measurement_guidance"]
    assert "回填：Report the source excerpt and recorded observation." in view[
        "measurement_guidance"
    ]
    assert "描述补充 · 第 1 轮" in view["timeline"]
    assert "heater and temperature are logged" in view["timeline"]
    assert "测量回填 · 第 1 轮" in view["timeline"]
    assert "record for open_loop_stability" in view["timeline"]


def test_profile_stage_replaces_diagnostic_plan_with_profile_questions(
    guided_adapter,
):
    report, _state = _start_verified_app_run(
        "A measured first order heater settles after a small power change.",
        "temperature",
        "heater power",
        "",
        NATURAL_LANGUAGE_MODE,
        True,
        "https://provider.example/v1",
        "provider-model",
        "test-key",
    )

    view = render_report(report)

    assert "补充当前设备的已知规格" in view["measurement_guidance"]
    assert "为什么需要" in view["measurement_guidance"]
    assert "可以从哪里找" in view["measurement_guidance"]
    assert "单位提示" in view["measurement_guidance"]
    assert "existing_records_only" not in view["measurement_guidance"]
    assert "open_loop_stability" not in view["measurement_guidance"]


def test_incomplete_description_uses_original_input_and_hides_measurement_controls(
    monkeypatch,
):
    class CountingAdapter(_CompleteGuidedAdapter):
        def __init__(self):
            self.phrase_calls = 0

        def phrase_measurement_plan(self, description, checklist, plan):
            self.phrase_calls += 1
            return super().phrase_measurement_plan(description, checklist, plan)

    adapter = CountingAdapter()
    monkeypatch.setattr(web_service, "build_adapter", lambda *args: adapter)
    app = build_app()
    component_props = [component["props"] for component in app.config["components"]]
    assert not any(props.get("label") == "补充描述" for props in component_props)
    assert not any(props.get("value") == "提交描述补充" for props in component_props)
    assert any(props.get("value") == "检查描述并继续" for props in component_props)

    report, state = _start_app_run(
        "A heater and temperature record are available.",
        "",
        "",
        "",
        NATURAL_LANGUAGE_MODE,
        True,
        "https://provider.example/v1",
        "provider-model",
        "test-key",
    )
    view = render_report(report)
    outputs = web_ui._outputs(report, state)
    assert report.status == "awaiting_measurements"
    assert "请直接在左侧“控制问题描述”栏继续补充" in view[
        "measurement_guidance"
    ]
    assert "open_loop_stability" not in view["measurement_guidance"]
    assert "Review an existing record" not in view["measurement_guidance"]
    assert view["status"].startswith("### 补充问题描述")
    assert (
        '<div class="flow-step waiting"><span>2</span><small>AI 测量计划</small>'
        in view["progress"]
    )
    assert outputs[16]["visible"] is False
    assert outputs[17]["visible"] is False
    assert outputs[18]["visible"] is False
    assert adapter.phrase_calls == 1


def test_guided_run_callback_forces_llm_and_blank_internal_domain_fields(monkeypatch):
    captured = {}
    report = _guided_description_report()

    def fake_start(*args):
        captured["args"] = args
        return report, {"session": report.diagnostic_session.model_dump(mode="json")}

    monkeypatch.setattr("cfdc.web.ui.start_app_run", fake_start)

    run_from_ui(
        "one natural-language description",
        "https://provider.example/v1",
        "provider-model",
        "secret",
    )

    assert captured["args"][:6] == (
        "one natural-language description",
        "",
        "",
        "",
        NATURAL_LANGUAGE_MODE,
        True,
    )


def test_description_continuation_preserves_session_for_measurement_reply():
    description = SystemDescription(text="I have a machine.")
    session = start_diagnostic_session(
        description,
        diagnosis=infer_structural_diagnosis(description),
    ).model_copy(update={"status": "collecting_description"})

    report, next_state = continue_app_run(
        {
            "session": session.model_dump(mode="json"),
            "use_llm": False,
            "include_trajectory": False,
        },
        [None, None, None, None],
        (
            "A heater changes a recorded temperature. Existing logs show that the "
            "temperature settles after the heater returns to its baseline."
        ),
    )

    assert report.status == "awaiting_measurements"
    assert next_state["session"]["status"] == "awaiting_measurements"


@pytest.fixture(scope="module")
def completed_cartpole_report():
    report = run_cfdc_route("cartpole")
    assert report.status == "demo_completed"
    return report


def test_pre_measurement_render_redacts_all_stale_technical_artifacts(
    completed_cartpole_report,
):
    session = start_diagnostic_session(
        completed_cartpole_report.system_description,
        diagnosis=completed_cartpole_report.diagnosis,
    )
    report = completed_cartpole_report.model_copy(
        update={
            "diagnostic_session": session,
        }
    )

    view = render_report(report)

    assert "underactuated_cartpole" not in view["summary"]
    assert "accept" not in view["summary"]
    assert "<strong>1</strong>" not in view["summary"]
    assert "<strong>3</strong>" not in view["summary"]
    assert "underactuated_cartpole" not in view["status"]
    assert "accept" not in view["status"]
    assert "标准对象演示完成" not in view["status"]
    assert "cartpole" not in view["status"]
    assert "demo_fixture_only" not in view["status"]
    assert "最终误差" not in view["performance_visual"]
    for key in (
        "diagnosis",
        "route",
        "experiments",
        "features",
        "controller",
        "tuning",
        "performance",
    ):
        assert view[key] == []
    assert not any(view["technical_visibility"].values())
    assert 'flow-step done"><span>✓</span><small>系统分类</small>' not in view[
        "progress"
    ]
    assert 'flow-step done"><span>✓</span><small>初始控制器</small>' not in view[
        "progress"
    ]
    assert (
        'flow-step done"><span>✓</span><small>效果验证与调优</small>'
        not in view["progress"]
    )
    assert view["raw"]["diagnosis"] is None
    assert view["raw"]["route_id"] == "generic"
    assert view["raw"]["status"] == "awaiting_measurements"
    assert (
        view["raw"]["evidence_boundary"]
        == "software_simulation_diagnostic_session"
    )
    assert view["raw"]["classification"] is None
    assert view["raw"]["semantic_selection"] is None
    assert view["raw"]["experiment_results"] == []
    assert view["raw"]["features"] == []
    assert view["raw"]["controller"] is None
    assert view["raw"]["adapted_controller_performance"] is None
    assert view["raw"]["diagnostic_session"]["current_diagnosis"] is None


def test_profile_measurement_stage_redacts_stale_model_and_controller_artifacts(
    completed_cartpole_report,
):
    session = start_diagnostic_session(
        completed_cartpole_report.system_description,
        diagnosis=completed_cartpole_report.diagnosis,
    ).model_copy(
        update={
            "status": "awaiting_profile_measurements",
            "evidence_level": "measurement_verified",
            "classification": completed_cartpole_report.classification,
            "semantic_selection": completed_cartpole_report.semantic_selection,
        }
    )
    report = completed_cartpole_report.model_copy(
        update={
            "diagnostic_session": session,
        }
    )

    view = render_report(report)

    assert view["diagnosis"]
    assert view["route"]
    assert view["experiments"] == []
    assert view["features"] == []
    assert view["controller"] == []
    assert view["tuning"] == []
    assert view["performance"] == []
    assert view["technical_visibility"] == {
        "diagnosis": True,
        "route": True,
        "model": False,
        "features": False,
        "controller": False,
        "tuning": False,
    }
    assert 'flow-step done"><span>✓</span><small>系统分类</small>' in view[
        "progress"
    ]
    assert 'flow-step done"><span>✓</span><small>初始控制器</small>' not in view[
        "progress"
    ]
    assert view["raw"]["classification"] is not None
    assert view["raw"]["semantic_selection"] is not None
    assert view["raw"]["experiment_results"] == []
    assert view["raw"]["features"] == []
    assert view["raw"]["controller"] is None
    assert view["raw"]["adapted_controller_performance"] is None


def test_every_gradio_event_declares_unique_outputs():
    app = build_app()

    duplicated = [
        dependency
        for dependency in app.config["dependencies"]
        if len(dependency["outputs"]) != len(set(dependency["outputs"]))
    ]

    assert duplicated == []


def test_frozen_validation_keeps_failure_evidence_visible_and_stage_blocked(
    completed_cartpole_report,
):
    report = completed_cartpole_report.model_copy(update={"status": "frozen"})

    view = render_report(report)
    final_stage = view["progress"].split('<div class="flow-step ')[-1]

    assert len(view["performance"]) == 2
    assert "最终误差" in view["performance_visual"]
    assert view["raw"]["stale_controller_performance"] is not None
    assert view["raw"]["adapted_controller_performance"] is not None
    assert final_stage.startswith('blocked">')
    assert "效果验证与调优" in final_stage


@pytest.fixture
def specification_candidate_report(guided_adapter):
    _, state = _start_verified_app_run(
        "A measured first order heater settles after a small power change.",
        "temperature",
        "heater power",
        "",
        NATURAL_LANGUAGE_MODE,
        True,
        "https://provider.example/v1",
        "provider-model",
        "test-key",
    )
    report, _ = submit_app_specifications(
        state,
        (
            "input_change=1 normalized_input; steady_output_change=10 degC; "
            "response_time_s=20 s; input_min=-2 normalized_input; "
            "input_max=2 normalized_input; output_min=-30 degC; output_max=80 degC."
        ),
        simulation_bounds_confirmed=True,
    )
    assert report.status == "candidate_unvalidated"
    assert report.diagnostic_session.status == "specification_model_ready"
    return report


def test_outer_terminal_rejection_overrides_model_ready_session_status(
    specification_candidate_report,
):
    report = specification_candidate_report.model_copy(
        update={
            "status": "rejected",
            "evidence_boundary": "user_object_model_validation_failed",
        }
    )

    view = render_report(report)

    assert "### 已拒绝" in view["status"]
    assert "规格模型已就绪" not in view["status"]
    assert view["raw"]["status"] == "rejected"
    assert (
        view["raw"]["evidence_boundary"]
        == "user_object_model_validation_failed"
    )
