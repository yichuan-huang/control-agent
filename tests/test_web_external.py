from uuid import uuid4

import pytest

from cfdc.web import actions, readmodels, service
from cfdc.web.schemas import ActionRequest


def test_json_payload_uses_parser_and_preserves_original_text(monkeypatch):
    seen = {}

    def prepare(state, text, **kwargs):
        seen["text"] = text
        return {
            "action": "answer",
            "payload": {"x": 1},
            "source_text": text,
            "input_mode": "json",
        }

    def apply(state, **kwargs):
        seen.update(kwargs)
        return {}, {}

    monkeypatch.setattr(service, "prepare_kernel_reply_for_ui", prepare)
    monkeypatch.setattr(service, "continue_kernel_app_run", apply)
    request = ActionRequest(
        request_id=uuid4(),
        expected_revision=1,
        action="answer",
        input={"mode": "json", "text": '{ "x": 1 }', "payload": {"x": 1}},
    )
    actions.execute_action({}, request, None)
    assert seen.get("text") == '{ "x": 1 }'
    assert seen["reply_source_text"] == '{ "x": 1 }'


def test_external_result_upload_requires_scoped_files():
    request = ActionRequest(
        request_id=uuid4(), expected_revision=1, action="submit_external_results"
    )
    with pytest.raises(actions.APIError) as exc:
        actions.execute_action({}, request, None)
    assert exc.value.public.code == "upload_files_required"


def test_custom_source_action_is_actionable():
    report = {
        "session_id": "test",
        "revision": 1,
        "status": "awaiting_provider",
        "task": {},
        "input_contract": {"action": "select_external_source", "allowed_modes": []},
        "external_workflow": {
            "source": {},
            "active_request": {
                "stage": "development",
                "package_path": "/private/secret",
            },
        },
    }
    summary = readmodels.summary(report).model_dump()
    assert summary["workspace"]["actionable"]
    assert summary["external_workflow"]["stage"] == "development"
    assert "/private/secret" not in str(summary)


def test_source_selection_generates_guided_handoff(tmp_path):
    from test_external_evidence_guards import resolved

    from cfdc.kernel import WorkflowService

    session = resolved(WorkflowService(tmp_path))
    report, state = service.load_kernel_app_run(
        session.session_id, session_dir=tmp_path
    )
    assert report["input_contract"]["action"] == "select_external_source"
    report, state = service.continue_kernel_app_run(
        state, action="select_external_source", payload={"source_kind": "software"}
    )
    assert report["protocols"]
    assert report["operator_handoffs"]
    assert report["input_contract"]["action"] == "record_operator_report"


def test_source_required_summary_has_guided_external_state(tmp_path):
    from test_external_evidence_guards import resolved

    from cfdc.kernel import WorkflowService

    session = resolved(WorkflowService(tmp_path))
    report, _ = service.load_kernel_app_run(session.session_id, session_dir=tmp_path)
    assert readmodels.summary(report).external_workflow is not None


def test_external_errors_are_stable_and_never_include_raw_details():
    error = actions.public_action_error(
        ValueError("external_results_binding_mismatch: secret-token"), {}
    )
    assert error.public.code == "external_results_binding_mismatch"
    assert "secret-token" not in error.public.message


@pytest.mark.parametrize(
    "status,read_only",
    [
        ("controller_pending", False),
        ("capability_gap", False),
        ("legacy_read_only", True),
    ],
)
def test_custom_history_without_protocol_keeps_recovery_available(status, read_only):
    report = {
        "session_id": "old",
        "revision": 2,
        "status": status,
        "read_only": read_only,
        "task": {},
        "input_contract": {"action": "features", "allowed_modes": ["json"]},
        "protocols": [],
        "registered_case_binding": None,
    }
    result = readmodels.summary(report)
    assert result.external_workflow is not None
    assert result.external_workflow["recovery_available"] is True
    assert result.external_workflow["recovery_required"] is True
    assert result.workspace.actionable is False


def test_registered_task_does_not_gain_external_recovery():
    report = {
        "session_id": "case",
        "revision": 2,
        "status": "controller_pending",
        "task": {},
        "input_contract": {"action": "features"},
        "registered_case_binding": {"case_id": "builtin"},
    }
    assert readmodels.summary(report).external_workflow is None


def test_external_candidate_summary_shows_completed_evaluation():
    report = {
        "task": {},
        "external_workflow": {
            "tuning": {
                "candidates": [
                    {
                        "candidate_id": "probe-1",
                        "qualification": {"status": "offline_qualified"},
                        "result": {
                            "hard_failure": True,
                            "stable": False,
                            "performance_pass": False,
                            "score": 1e12,
                        },
                    }
                ]
            }
        },
    }
    candidate = readmodels.external_summary(report)["candidates"][0]
    assert candidate["status"] == "hard_failure"
    assert candidate["reason"] == "候选试次未通过稳定性或硬约束检查。"
    assert candidate["score"] == 1e12


def test_external_tuning_budget_is_visible_before_user_starts_tuning():
    from cfdc.web.readmodels import external_summary

    value = external_summary(
        {"task": {"budgets": {"evaluation_repeats": 20}}, "status": "tuning_eligible"}
    )
    assert value["tuning"]["max_attempts"] == 6
    assert value["tuning"]["minimum_relative_improvement"] == 0.02
    assert value["tuning"]["repeats"] == 20
