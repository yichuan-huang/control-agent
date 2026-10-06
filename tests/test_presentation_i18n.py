"""Localization changes presentation without changing recorded authority."""

import copy
import json

import pytest

from cfdc.web import drafts, external_guide, presentation, readmodels


def report_fixture():
    return {
        "session_id": "localization",
        "revision": 7,
        "status": "awaiting_confirmation",
        "task": {
            "description": "用户原文 <script>alert(1)</script>",
            "measured_signals": ["温度"],
            "signal_units": {"温度": "degC"},
            "control_inputs": ["加热"],
            "input_units": "W",
            "success_requirements": {"final_abs_error_max": 0.25},
        },
        "input_contract": {"action": "confirm_result", "allowed_modes": []},
        "pending_actions": [],
        "evaluation_packets": [
            {
                "packet_fingerprint": "unchanged-packet",
                "evaluation_split": "development",
                "trials": [
                    {
                        "trial_id": "原始试次",
                        "trajectory": {
                            "time_s": [0.0, 1.0],
                            "outputs": {"温度": [2.0, 3.0]},
                            "references": {"温度": [3.0, 3.0]},
                            "control_inputs": {"加热": [0.5, 0.75]},
                        },
                    }
                ],
            }
        ],
        "evaluation": {
            "packet_fingerprint": "unchanged-packet",
            "evaluation_split": "development",
            "status": "performance_not_met",
            "trials": [
                {
                    "trial_id": "原始试次",
                    "metrics": {"channels": {"温度": {"final_abs_error": 1.0}}},
                }
            ],
        },
        "events": [{"message": "审计原文"}],
    }


def test_english_projections_preserve_raw_data_and_identity():
    report = report_fixture()
    before = copy.deepcopy(report)
    english = readmodels.summary(report, locale="en")
    chinese = readmodels.summary(report, locale="zh-CN")
    assert english.task == chinese.task == report["task"]
    assert english.revision == chinese.revision == 7
    assert english.workspace.title != chinese.workspace.title
    assert "independent confirmation" in english.workspace.title.lower()
    assert "用户原文" in english.workspace.task_summary
    assert "<script>" not in english.workspace.task_summary
    assert "Final absolute error" in english.workspace.task_summary
    assert (
        readmodels.curve_view(report, "0:0", "温度", locale="en").output[1].name
        == "Target"
    )
    assert readmodels.curve_view(report, "0:0", "温度", locale="en").output[0].y == [
        2.0,
        3.0,
    ]
    metrics = readmodels.evaluations_view(report, locale="en")
    assert metrics.options[0].fingerprint == "unchanged-packet"
    assert "Final absolute error" in json.dumps(metrics.metrics, ensure_ascii=False)
    assert "原始试次" in metrics.options[0].label
    assert readmodels.node_page(report, "events").items[0].preview
    assert report == before


def test_locale_defaults_and_untrusted_values_remain_escaped():
    report = report_fixture()
    assert presentation.project_workspace(report) == presentation.project_workspace(
        report, locale="zh-CN"
    )
    assert "Task progress" in presentation.steps_html(report, locale="en")
    report["evaluation_packets"][0]["trials"][0]["trial_id"] = (
        "<img src=x onerror=alert(1)>"
    )
    assert "<img" not in presentation.evaluation_options(report, locale="en")[0][0]


def test_external_guide_and_upload_requirements_are_localized():
    report = {
        "status": "awaiting_evidence",
        "input_contract": {"action": "ingest_upload"},
    }
    guide = external_guide.workflow_guide(report, locale="en")
    assert "upload" in guide["title"].lower()
    assert "protocol" in json.dumps(guide).lower()
    assert external_guide.workflow_guide(report) != guide
    assert report["input_contract"]["action"] == "ingest_upload"


def test_draft_validation_has_stable_message_descriptors():
    with pytest.raises(drafts.DraftValidationError) as caught:
        drafts.task_from_draft(drafts.empty_draft(), locale="en")
    error = caught.value
    assert "description" in error.field_message_refs
    assert error.field_message_refs["description"]["key"].startswith("presentation.")
    assert "Describe" in error.errors["description"]
    assert "complete" in str(error).lower()


def test_artifact_labels_localize_without_rewriting_ids():
    report = report_fixture()
    english = readmodels.artifact_catalog(report, locale="en")
    chinese = readmodels.artifact_catalog(report, locale="zh-CN")
    assert [item.id for item in english.items] == [item.id for item in chinese.items]
    assert english.items[0].label == "Report"
    assert chinese.items[0].label == "报告"


def test_input_contract_copy_localizes_known_system_text_only():
    report = report_fixture()
    report["status"] = "diagnostic"
    report["input_contract"] = {
        "action": "submit_answer",
        "title": "补充结构诊断与核心参数",
        "guidance": "原始系统提示",
        "allowed_modes": ["natural_language", "json"],
        "json_template": {
            "open_loop_stability": {
                "status": "known|unknown",
                "assessment": "可选字符串",
                "evidence": "用户原文摘录",
                "confidence": "0 到 1（可选）",
            },
        },
    }
    report["pending_actions"] = [{"action": "submit_answer", "user_text": "保持原文"}]
    before = copy.deepcopy(report)
    projected = readmodels.summary(report, locale="en")
    assert "natural language" in projected.input_contract["guidance"]
    assert (
        projected.input_contract["json_template"]["open_loop_stability"]["evidence"]
        == "Excerpt from the user's original text"
    )
    assert projected.pending_actions[0]["user_text"] == "保持原文"
    assert report == before


def test_upload_gate_display_localizes_without_changing_audit():
    report = {
        "upload_attempts": [
            {
                "audit": {
                    "status": "rejected",
                    "failed_gate": "timebase",
                    "gates": [
                        {
                            "id": "timebase",
                            "status": "failed",
                            "details": "原始拒绝信息",
                        }
                    ],
                }
            }
        ]
    }
    before = copy.deepcopy(report)
    feedback = presentation.upload_feedback(report, locale="en")
    assert "Time axis and sampling" in feedback
    assert "原始拒绝信息" in feedback
    assert report == before


@pytest.mark.parametrize(
    "status",
    [
        "intake",
        "diagnostic",
        "awaiting_evidence",
        "awaiting_provider",
        "route_ready",
        "evaluation_recorded_pending_replay",
        "awaiting_confirmation",
        "performance_met",
        "capability_gap",
        "cancelled",
        "unknown",
    ],
)
def test_system_workspace_states_have_english_text(status):
    report = {"status": status, "input_contract": {"action": "advance"}}
    view = presentation.project_workspace(report, locale="en")
    assert not any(
        "\u4e00" <= char <= "\u9fff" for char in view["title"] + view["explanation"]
    )


@pytest.mark.parametrize(
    "action",
    [
        "submit_answer",
        "select_external_source",
        "compile_protocol",
        "freeze",
        "start_external_tuning",
        "prepare_external_run",
        "submit_external_results",
        "advance",
    ],
)
def test_external_guides_cover_each_action_in_both_languages(action):
    report = {"status": "diagnostic", "input_contract": {"action": action}}
    before = copy.deepcopy(report)
    for locale in ("en", "zh-CN"):
        guide = external_guide.workflow_guide(report, locale=locale)
        assert guide["steps"]
        if locale == "en":
            assert not any(
                "\u4e00" <= char <= "\u9fff"
                for char in json.dumps(guide, ensure_ascii=False)
            )
    assert report == before


def test_protocol_preview_and_execution_requirements_are_display_only():
    report = {
        "session_id": "protocol-locale",
        "revision": 8,
        "active_protocol_fingerprint": "protocol-fixed",
        "protocols": [
            {
                "protocol_fingerprint": "protocol-fixed",
                "requested_signals": ["y"],
                "control_inputs": ["u"],
                "units": {"outputs": {"y": "K"}, "input": "V"},
                "repeats": 2,
                "sample_period_s": 0.5,
                "data_kind": "raw-kind",
            }
        ],
        "evidence": [
            {
                "protocol_fingerprint": "protocol-fixed",
                "status": "accepted",
                "trace": {"time_s": [0.0, 0.5], "signals": {"y": [1.0, 2.0]}},
            }
        ],
        "external_workflow": {
            "active_request": {
                "stage": "fresh_confirmation",
                "execution_request": {
                    "tracked_signals": ["y"],
                    "control_inputs": ["u"],
                },
                "manifest": {"trials": [{"file": "recorded-file.json"}]},
            }
        },
    }
    before = copy.deepcopy(report)
    english = readmodels.protocol_view(report, locale="en")
    chinese = readmodels.protocol_view(report, locale="zh-CN")
    assert (
        english.protocol_fingerprint == chinese.protocol_fingerprint == "protocol-fixed"
    )
    assert english.preview.columns[0] == "Time (s)"
    assert english.preview.rows[0][-1] == chinese.preview.rows[0][-1] == 1.0
    assert "raw\\-kind" in english.summary
    assert "Sample interval" in english.summary
    requirements = external_guide.upload_requirements(report, locale="en")
    assert "evaluation result ZIP" in requirements["expected_format"]
    assert requirements["files"][1]["filename"] == "recorded-file.json"
    assert report == before


def test_draft_locale_changes_errors_only_not_valid_task_values():
    form = {
        **drafts.empty_draft(),
        "description": "用户任务原文",
        "outputs": [["温度", "K"]],
        "inputs": [["加热"]],
        "input_min": 0,
        "input_max": 10,
        "state_stop": 80,
    }
    assert drafts.task_from_draft(form, locale="en") == drafts.task_from_draft(
        form, locale="zh-CN"
    )
