from __future__ import annotations

import pytest

from cfdc.web.presentation import (
    evaluation_figures,
    evaluation_options,
    project_workspace,
    protocol_summary,
    result_rows,
    signal_options,
    steps_html,
    task_summary,
    trace_preview,
    upload_feedback,
)
from cfdc.web.service import (
    continue_kernel_app_run,
    start_kernel_app_run,
    start_kernel_case_run,
)


def _task() -> dict:
    return {
        "description": "保持 <温度> **稳定**",
        "measured_signals": ["temperature"],
        "control_inputs": ["heater"],
        "reference": 42.0,
        "input_min": 0.0,
        "input_max": 100.0,
        "output_min": None,
        "output_max": 80.0,
        "signal_units": {"temperature": "°C"},
        "input_units": "%",
        "success_requirements": {
            "final_abs_error_max": 0.5,
            "settling_time_max_s": 20.0,
        },
        "api_key": "never-render-this",
    }


def _trial(trial_id: str, offset: float = 0.0) -> dict:
    return {
        "trial_id": trial_id,
        "trajectory": {
            "time_s": [0.0, 1.0, 2.0],
            "outputs": {
                "temperature": [20.0 + offset, 35.0 + offset, 42.0 + offset],
                "secondary": [0.0, 0.5, 1.0],
            },
            "references": {
                "temperature": [42.0, 42.0, 42.0],
                "secondary": [1.0, 1.0, 1.0],
            },
            "control_inputs": {"heater": [100.0, 45.0, 10.0]},
        },
    }


def _packets() -> list[dict]:
    return [
        {
            "packet_fingerprint": "development-old",
            "evaluation_split": "development",
            "trials": [_trial("dev-old")],
        },
        {
            "packet_fingerprint": "development-current",
            "evaluation_split": "development",
            "trials": [_trial("dev-current", 1.0)],
        },
        {
            "packet_fingerprint": "confirmation-current",
            "evaluation_split": "fresh_confirmation",
            "trials": [_trial("confirm-1", 2.0), _trial("confirm-2", 3.0)],
        },
    ]


def test_task_summary_whitelists_task_fields_and_marks_unknown_bounds() -> None:
    summary = task_summary(_task())

    assert "保持 &lt;温度&gt; \\*\\*稳定\\*\\*" in summary
    assert "temperature（°C）" in summary
    assert "heater（%）" in summary
    assert "0–100 %" in summary
    assert "输出下界未提供" in summary
    assert "终值绝对误差不超过 0.5" in summary
    assert "never-render-this" not in summary
    assert summary.count("\n\n") == 6


def test_task_summary_suppresses_unknown_and_nested_requirement_credentials() -> None:
    task = _task()
    task["success_requirements"] = {
        "final_abs_error_max": {
            "temperature": 0.5,
            "api_key": "nested-secret-token",
        },
        "peak_abs_input_max": {
            "heater": 95.0,
            "vendor.password": "nested-password",
        },
        "api_key": "secret-token",
        "vendor.password": {"value": "password"},
    }

    summary = task_summary(task)

    assert "temperature 0.5 °C" in summary
    assert "heater 95 %" in summary
    for secret in (
        "api_key",
        "vendor.password",
        "nested-secret-token",
        "nested-password",
        "secret-token",
        "password",
    ):
        assert secret not in summary


@pytest.mark.parametrize(
    ("report", "title_fragment", "stage", "visible"),
    [
        ({"status": "awaiting_evidence"}, "证据不足", 1, False),
        (
            {
                "status": "capability_gap",
                "qualification": {"status": "rejected"},
            },
            "资格审查未通过",
            3,
            True,
        ),
        (
            {
                "status": "tuning_eligible",
                "evaluation": {
                    "status": "performance_not_met",
                    "evaluation_split": "development",
                    "stability_gate": {"passed": True},
                    "evidence_gate": {"passed": True},
                },
            },
            "稳定，但性能尚未达标",
            3,
            True,
        ),
        (
            {
                "status": "performance_met",
                "evaluation": {
                    "status": "performance_met",
                    "evaluation_split": "development",
                },
            },
            "开发评价达到要求",
            3,
            True,
        ),
        (
            {
                "status": "performance_met",
                "evaluation": {
                    "status": "performance_met",
                    "evaluation_split": "fresh_confirmation",
                },
                "confirmation": {
                    "status": "performance_met",
                    "packet_fingerprint": "fresh",
                },
                "evaluation_packets": [
                    {
                        "packet_fingerprint": "fresh",
                        "evaluation_split": "fresh_confirmation",
                        "trials": [{}],
                    }
                ],
                "evaluation_replays": [
                    {
                        "packet_fingerprint": "fresh",
                        "evaluation_split": "fresh_confirmation",
                        "matches_previous": True,
                    }
                ],
            },
            "独立确认已通过",
            3,
            True,
        ),
        (
            {
                "status": "capability_gap",
                "confirmation": {"status": "performance_not_met"},
                "evaluation": {
                    "status": "performance_not_met",
                    "evaluation_split": "fresh_confirmation",
                },
            },
            "独立确认未通过",
            3,
            True,
        ),
        ({"status": "capability_gap"}, "能力范围不足", 3, True),
        ({"status": "cancelled"}, "任务已取消", 3, True),
    ],
)
def test_workspace_distinguishes_authoritative_result_classes(
    report: dict, title_fragment: str, stage: int, visible: bool
) -> None:
    projected = project_workspace({"task": _task(), **report})

    assert title_fragment in projected["title"]
    assert projected["stage"] == stage
    assert projected["result_visible"] is visible


def test_workspace_actions_fail_closed_for_readonly_terminal_and_unknown() -> None:
    actionable = project_workspace(
        {
            "status": "diagnostic",
            "task": _task(),
            "input_contract": {
                "action": "answer",
                "allowed_modes": ["json"],
            },
        }
    )
    readonly = project_workspace(
        {
            "status": "diagnostic",
            "read_only": True,
            "input_contract": {"action": "answer", "allowed_modes": ["json"]},
        }
    )
    terminal = project_workspace(
        {
            "status": "cancelled",
            "input_contract": {"action": "answer", "allowed_modes": ["json"]},
        }
    )
    unsupported = project_workspace(
        {
            "status": "unexpected_new_state",
            "input_contract": {"action": "future_action"},
        }
    )

    assert actionable["actionable"] is True
    assert actionable["advanced"] is True
    assert readonly["actionable"] is False
    assert readonly["title"].startswith("只读 · ")
    assert "只读记录" in readonly["explanation"]
    assert terminal["actionable"] is False
    assert unsupported["actionable"] is False
    assert unsupported["action"] == "future_action"


def test_real_diagnostic_report_normalizes_submit_answer_for_novices(tmp_path) -> None:
    report, state = start_kernel_app_run(
        {
            "description": "保持输出稳定",
            "measured_signals": ["y"],
            "control_inputs": ["u"],
            "input_min": -1,
            "input_max": 1,
            "output_min": -2,
            "output_max": 2,
            "state_stop": 3,
        },
        session_dir=tmp_path,
        use_rag=False,
    )
    report, _ = continue_kernel_app_run(state, action="confirm_task", payload={})

    assert report["input_contract"]["action"] == "submit_answer"
    projected = project_workspace(report)
    assert projected["action"] == "answer"
    assert projected["actionable"] is True
    assert projected["action_title"] == "补充已知现象"
    assert projected["title"] == "补充对象的已知现象"
    assert "不知道" in projected["explanation"]
    assert "补全任务目标" not in projected["explanation"]


def test_real_tuning_and_confirmation_states_override_stale_development_result(
    tmp_path,
) -> None:
    report, state = start_kernel_case_run(
        "tclab_single_heater_v1", session_dir=tmp_path, use_rag=False
    )
    report, state = continue_kernel_app_run(state, action="confirm_task", payload={})
    assert report["evaluation"]["status"] == "performance_not_met"

    report, state = continue_kernel_app_run(
        state, action="run_feedback_iteration", payload={}
    )
    assert report["status"] == "awaiting_confirmation"
    assert "等待独立确认" in project_workspace(report)["title"]

    report, _ = continue_kernel_app_run(state, action="confirm_result", payload={})
    assert report["confirmation"]["status"] == "performance_met"
    assert report["evaluation_replays"][-1]["matches_previous"] is True
    assert project_workspace(report)["title"] == "独立确认已通过"


def test_real_exhausted_motor_tuning_overrides_stale_development_evaluation(
    tmp_path,
) -> None:
    report, state = start_kernel_case_run(
        "dc_motor_speed_v1", session_dir=tmp_path, use_rag=False
    )
    report, state = continue_kernel_app_run(state, action="confirm_task", payload={})
    assert report["status"] == "tuning_eligible"

    report, _ = continue_kernel_app_run(
        state, action="run_feedback_iteration", payload={}
    )
    projected = project_workspace(report)

    assert report["status"] == "capability_gap"
    assert report["tuning"]["reason"] == "no_strict_development_improvement"
    assert projected["title"] == "有界调优未找到可确认方案"
    assert projected["actionable"] is False


def test_pending_replay_state_withholds_calculated_pass() -> None:
    report = {
        "status": "evaluation_recorded_pending_replay",
        "task": _task(),
        "evaluation": {
            "status": "performance_met",
            "evaluation_split": "development",
        },
        "input_contract": {"action": "replay", "allowed_modes": []},
    }

    projected = project_workspace(report)
    flat = " ".join(str(cell) for row in result_rows(report) for cell in row)

    assert "等待复核" in projected["title"]
    assert "待复核" in flat
    assert "已通过" not in flat


def test_awaiting_provider_is_a_known_data_stage_but_action_stays_disabled() -> None:
    projected = project_workspace(
        {
            "status": "awaiting_provider",
            "task": {**_task(), "budget_confirmed": True},
            "input_contract": {
                "action": "set_provider",
                "disabled_reason": "当前动作不向 WebUI 开放。",
            },
        }
    )

    assert projected["stage"] == 1
    assert "数据来源" in projected["title"]
    assert projected["actionable"] is False


def test_route_ready_evidence_action_does_not_claim_a_protocol_exists() -> None:
    projected = project_workspace(
        {
            "status": "route_ready",
            "task": _task(),
            "input_contract": {"action": "evidence", "allowed_modes": ["json"]},
        }
    )

    assert projected["action_title"] == "需要补充可验证的证据"
    assert "与本任务和路线要求一致" in projected["action_help"]
    assert "打开专业提交" in projected["action_help"]
    assert "当前协议" not in projected["action_help"]


def test_result_rows_use_recorded_judgments_and_metrics_without_trace_math() -> None:
    report = {
        "evaluation": {
            "status": "performance_not_met",
            "evaluation_split": "development",
            "success_rate": 0.5,
            "wilson_lower_bound_95": 0.2,
            "performance_gate": {"success_rate_min": 0.8},
            "trials": [
                {
                    "trial_id": "dev-1",
                    "metrics": {
                        "channels": {
                            "temperature": {
                                "final_abs_error": 0.75,
                                "settling_time_s": 21.0,
                            }
                        }
                    },
                }
            ],
        },
        "evaluation_packets": [
            {
                "evaluation_split": "development",
                "trials": [
                    {
                        "trajectory": {
                            "time_s": [0.0, 1.0],
                            "outputs": {"temperature": [0.0, 999.0]},
                        }
                    }
                ],
            }
        ],
    }

    rows = result_rows(report)
    flat = " ".join(str(cell) for row in rows for cell in row)

    assert "开发评价" in flat
    assert "50%" in flat
    assert "80%" in flat
    assert "0.75" in flat
    assert "21" in flat
    assert "999" not in flat


def test_result_rows_limit_trial_metrics_to_selected_recorded_trial() -> None:
    first = {
        "trial_id": "trial-first",
        "metrics": {"channels": {"temperature": {"final_abs_error": 0.25}}},
    }
    second = {
        "trial_id": "trial-second",
        "metrics": {"channels": {"temperature": {"final_abs_error": 0.75}}},
    }
    report = {
        "task": _task(),
        "evaluation": {
            "status": "performance_not_met",
            "evaluation_split": "development",
            "packet_fingerprint": "development-current",
            "trials": [first, second],
        },
        "evaluation_packets": [
            {
                "packet_fingerprint": "development-current",
                "evaluation_split": "development",
                "trials": [first, second],
            }
        ],
    }

    flat = " ".join(str(cell) for row in result_rows(report, "0:1") for cell in row)

    assert "trial-second" in flat
    assert "0.75" in flat
    assert "trial-first" not in flat
    assert "0.25" not in flat


def test_rejected_confirmation_is_labeled_as_confirmation_without_success() -> None:
    rows = result_rows(
        {
            "confirmation": {"status": "performance_not_met"},
            "evaluation": {
                "status": "performance_not_met",
                "evaluation_split": "fresh_confirmation",
            },
        }
    )
    flat = " ".join(str(cell) for row in rows for cell in row)

    assert "独立确认" in flat
    assert "未通过" in flat
    assert "已通过" not in flat


@pytest.mark.parametrize(
    ("task", "metrics", "expected_summary", "expected_rows"),
    [
        (
            {
                **_task(),
                "task_type": "local_setpoint_hold",
                "success_requirements": {
                    "final_abs_error_max": 0.5,
                    "overshoot_max": 1.0,
                    "settling_time_max_s": 20.0,
                    "hold_duration_min_s": 5.0,
                    "perturbed_success_rate_min": 0.8,
                    "iae_max": 12.0,
                    "peak_abs_input_max": 95.0,
                },
            },
            {
                "channels": {
                    "temperature": {
                        "final_abs_error": 0.2,
                        "overshoot": 0.4,
                        "settling_time_s": 18.0,
                        "hold_duration_s": 6.0,
                        "iae": 9.0,
                        "peak_abs_output": 44.0,
                    }
                },
                "inputs": {
                    "heater": {
                        "peak_abs_input": 90.0,
                        "raw_peak_abs_input": 110.0,
                        "saturation_duration_s": 1.5,
                        "saturation_fraction": 0.1,
                    }
                },
            },
            ("保持时间不少于", "输入峰值不超过"),
            ("输出绝对峰值", "44 °C", "输入绝对峰值", "90 %"),
        ),
        (
            {
                **_task(),
                "task_type": "transition_then_hold",
                "success_requirements": {
                    "required_phase_count_min": 2,
                    "verified_handoff_count_min": 1,
                    "goal_region_entry_required": True,
                    "final_hold_duration_min_s": 4.0,
                    "perturbed_success_rate_min": 0.8,
                },
            },
            {
                "completed_phase_count": 2,
                "verified_handoff_count": 1,
                "final_hold_duration_s": 4.5,
                "entered_goal_region": True,
            },
            ("完成阶段数不少于", "必须进入目标区域", "最终保持时间不少于"),
            ("已完成阶段数", "已验证阶段切换数", "最终保持时间", "已进入目标区域"),
        ),
        (
            {
                **_task(),
                "task_type": "disturbance_recovery_to_hold",
                "success_requirements": {
                    "recovery_abs_error_max": 0.8,
                    "recovery_time_max_s": 30.0,
                    "post_recovery_hold_duration_min_s": 8.0,
                    "perturbed_success_rate_min": 0.8,
                },
            },
            {
                "recovered_to_hold": True,
                "recovery_time_s": 24.0,
                "post_recovery_hold_duration_s": 9.0,
            },
            ("恢复绝对误差不超过", "恢复后保持时间不少于"),
            ("已恢复并保持", "恢复时间", "24 s", "恢复后保持时间", "9 s"),
        ),
    ],
)
def test_current_task_criteria_and_judged_metrics_are_all_present(
    task: dict,
    metrics: dict,
    expected_summary: tuple[str, ...],
    expected_rows: tuple[str, ...],
) -> None:
    report = {
        "task": task,
        "evaluation": {
            "status": "performance_met",
            "evaluation_split": "development",
            "trials": [{"trial_id": "trial-1", "metrics": metrics}],
        },
    }

    summary = task_summary(task)
    flat = " ".join(str(cell) for row in result_rows(report) for cell in row)

    assert all(expected in summary for expected in expected_summary)
    assert all(expected in flat for expected in expected_rows)


def test_confirmation_packet_is_prioritized_and_figures_separate_curves() -> None:
    report = {
        "task": _task(),
        "evaluation_packets": _packets(),
        "confirmation": {
            "status": "performance_not_met",
            "packet_fingerprint": "confirmation-current",
        },
    }

    options = evaluation_options(report)
    assert options[0][1] == "2:0"
    assert "独立确认" in options[0][0]
    assert "confirm-1" in options[0][0]
    assert signal_options(report, "2:1") == ["temperature", "secondary"]

    output, control = evaluation_figures(report, "2:1", "temperature")
    assert [trace.name for trace in output.data] == ["temperature", "目标值"]
    assert [trace.name for trace in control.data] == ["heater"]
    assert list(output.data[0].y) == [23.0, 38.0, 45.0]
    assert "°C" in output.layout.yaxis.title.text
    assert "%" in control.layout.yaxis.title.text

    fallback_output, _ = evaluation_figures(report, "99:99", "missing")
    assert list(fallback_output.data[0].y) == [22.0, 37.0, 44.0]


def test_latest_development_packet_is_default_without_linked_confirmation() -> None:
    report = {"evaluation_packets": _packets()[:2]}

    assert evaluation_options(report)[0][1] == "1:0"
    assert signal_options(report, None) == ["temperature", "secondary"]


def test_empty_or_malformed_evaluation_data_produces_no_fake_plots() -> None:
    assert evaluation_options({"evaluation_packets": [{"trials": []}]}) == []
    assert signal_options({}, None) == []
    output, control = evaluation_figures({}, None, None)
    assert not output.data
    assert not control.data


def test_upload_feedback_names_failed_and_unreached_gates_with_redo() -> None:
    feedback = upload_feedback(
        {
            "upload_attempts": [
                {
                    "status": "rejected",
                    "failed_gate": "timebase",
                    "gates": [
                        {"id": "file_format", "status": "passed"},
                        {
                            "id": "timebase",
                            "status": "failed",
                            "details": "time must start at zero",
                        },
                        {"id": "signal_quality", "status": "not_reached"},
                    ],
                }
            ]
        }
    )

    assert "时间轴与采样" in feedback
    assert "从 0 秒开始" in feedback
    assert "已通过 1 项" in feedback
    assert "尚未检查 1 项" in feedback
    assert "上传已接受" not in feedback


def test_trace_preview_uses_latest_accepted_public_trace_and_caps_rows() -> None:
    rejected = {
        "status": "rejected",
        "trial_id": "bad",
        "trace": {"time_s": [0.0], "signals": {"y": [999.0]}},
    }
    accepted = {
        "source": "user_upload",
        "trial_id": "repeat-03",
        "trace": {
            "time_s": [float(index) for index in range(25)],
            "signals": {
                "input": [float(index) for index in range(25)],
                "temperature": [20.0 + index for index in range(25)],
            },
        },
    }
    headers, rows = trace_preview({"evidence": [rejected, accepted]})

    assert headers == ["时间 (s)", "试次", "input", "temperature"]
    assert len(rows) == 20
    assert rows[0] == [0.0, "repeat-03", 0.0, 20.0]
    assert rows[-1] == [19.0, "repeat-03", 19.0, 39.0]
    assert trace_preview({"evidence": [rejected]}) == (["时间 (s)"], [])


def test_steps_and_protocol_are_safe_guidance_not_hardware_commands() -> None:
    report = {
        "status": "capability_gap",
        "task": {**_task(), "budget_confirmed": True},
        "qualification": {"status": "rejected"},
        "protocols": [
            {
                "protocol_fingerprint": "active-protocol",
                "requested_signals": ["temperature"],
                "control_inputs": ["heater"],
                "repeats": 3,
                "sample_period_s": 0.2,
                "data_kind": "siso_repeated_timeseries",
                "units": {
                    "time": "s",
                    "input": "%",
                    "outputs": {"temperature": "°C"},
                },
            }
        ],
        "active_protocol_fingerprint": "active-protocol",
        "registered_case_binding": {"evidence_mode": "exercise_bundle"},
    }

    html = steps_html(report)
    summary = protocol_summary(report)

    assert html.count('aria-current="step"') == 1
    assert "生成并验证方案" in html
    assert "查看结果" in html
    assert "ZIP" in summary
    assert "temperature（°C）" in summary
    assert "3 次" in summary
    assert "0.2 s" in summary
    assert "下载当前" in summary
    assert "启动硬件" not in summary


def test_protocol_summary_requires_exact_active_protocol_match() -> None:
    old = {
        "protocol_fingerprint": "old",
        "requested_signals": ["old-output"],
        "control_inputs": ["old-input"],
        "repeats": 1,
        "sample_period_s": 1.0,
        "data_kind": "old-data",
        "units": {"outputs": {}},
    }
    active = {
        "protocol_fingerprint": "active",
        "requested_signals": ["current-output"],
        "control_inputs": ["current-input"],
        "repeats": 2,
        "sample_period_s": 0.5,
        "data_kind": "current-data",
        "units": {"outputs": {}},
    }

    assert "当前还没有" in protocol_summary(
        {"protocols": [old, active], "active_protocol_fingerprint": None}
    )
    summary = protocol_summary(
        {"protocols": [active, old], "active_protocol_fingerprint": "active"}
    )
    assert "current\\-output" in summary
    assert "old\\-output" not in summary
