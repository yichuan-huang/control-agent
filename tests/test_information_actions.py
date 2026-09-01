import pytest

from cfdc.kernel.acquisition import ActionBudget, InformationAction, select_action
from cfdc.kernel.cases import public_training_case
from cfdc.kernel.providers import ProviderRegistry
from cfdc.kernel.service import WorkflowService
from cfdc.sim.training import build_training_provider_registries


def actions():
    return [
        InformationAction(
            "passive",
            "observe",
            {},
            {"a": ("same",), "b": ("same",), "c": ("same",)},
            risk=0,
            cost=1,
        ),
        InformationAction(
            "risky",
            "excite",
            {"safe_excitation": True},
            {"a": ("left",), "b": ("right",), "c": ("right",)},
            risk=2,
            cost=1,
        ),
        InformationAction(
            "cheap",
            "small",
            {"bounds_known": True},
            {"a": ("one",), "b": ("two",), "c": ("three",)},
            risk=1,
            cost=1,
        ),
    ]


def test_unknown_safety_prerequisite_blocks_only_that_action_and_passive_remains():
    choice = select_action(
        ("a", "b", "c"),
        actions(),
        {"safe_excitation": None, "bounds_known": False},
        ActionBudget(4, 100, 1),
    )
    assert choice.action_id == "passive"
    assert choice.blocked_actions == {
        "risky": ["safe_excitation"],
        "cheap": ["bounds_known"],
    }


def test_maximin_elimination_then_average_then_risk_cost_ordering():
    choice = select_action(
        ("a", "b", "c"),
        actions(),
        {"safe_excitation": True, "bounds_known": True},
        ActionBudget(4, 100, 1),
    )
    assert choice.action_id == "cheap"
    assert choice.score[0] == 2  # every outcome leaves at most one of three


def test_preexecution_budget_counts_failed_attempts_and_requested_excitation():
    budget = ActionBudget(
        max_distinct_experiments=2, max_excitation_time_s=10, max_failures_per_action=1
    )
    budget = budget.reserve("cheap", protocol_fingerprint="p", excitation_time_s=4)
    budget = budget.record_failure("cheap", protocol_fingerprint="p")
    budget = budget.reserve("cheap", protocol_fingerprint="p", excitation_time_s=4)
    budget = budget.record_failure("cheap", protocol_fingerprint="p")
    try:
        budget.reserve("cheap", protocol_fingerprint="p", excitation_time_s=1)
    except ValueError as exc:
        assert "failure" in str(exc)
    else:
        raise AssertionError("third failed-action attempt was not blocked")
    assert budget.attempts == 2
    assert budget.failed_attempts == 2
    assert budget.excitation_time_s == 8
    assert budget.valid_experiments == 0


def test_valid_count_is_distinct_from_attempt_and_excitation_budget():
    budget = (
        ActionBudget(2, 5, 1)
        .reserve("cheap", protocol_fingerprint="p", excitation_time_s=5)
        .record_valid("cheap", protocol_fingerprint="p")
    )
    assert (budget.attempts, budget.valid_experiments, budget.excitation_time_s) == (
        1,
        1,
        5,
    )
    try:
        budget.reserve("risky", protocol_fingerprint="q", excitation_time_s=0.01)
    except ValueError as exc:
        assert "excitation" in str(exc)


def test_malformed_provider_result_consumes_attempt_and_retry_budget(tmp_path):
    class MalformedProvider:
        provider_id = "malformed"
        provider_version = "1"
        capabilities = frozenset({"bounded_input_sequence"})

        @staticmethod
        def execute(operation, *, task):
            del operation, task
            return ()

    service = WorkflowService(tmp_path)
    session = service.start(
        {
            "description": "Identify a bounded stable scalar process.",
            "task_type": "local_setpoint_hold",
            "measured_signals": ["y"],
            "control_input": "u",
            "input_min": -1,
            "input_max": 1,
            "state_stop": 5,
            "reference": 0.5,
            "budget_confirmed": True,
            "budgets": {
                "distinct_experiments": 4,
                "cumulative_excitation_time_s": 200,
                "same_failure_retries": 1,
            },
        }
    )
    assessments = {
        "open_loop_stability": "stable",
        "nonminimum_phase": "minimum_phase",
        "significant_delay": "not_significant",
        "relative_degree": "low",
        "sensing_actuation_adequacy": "adequate",
        "nonlinearity_strength": "weak",
        "coupling_underactuation": "siso",
        "uncertainty_variation": "small",
    }
    session = service.submit_answer(
        session.session_id,
        action_id="diagnosis",
        revision=session.revision,
        answer={
            key: {
                "status": "known",
                "assessment": value,
                "evidence": f"declared {key}",
                "confidence": 0.9,
            }
            for key, value in assessments.items()
        },
    )
    session = service.advance(
        session.session_id, action_id="route", revision=session.revision
    )
    session = service.set_provider(
        session.session_id,
        action_id="bind",
        revision=session.revision,
        provider={
            "provider_id": "malformed",
            "provider_version": "1",
            "capabilities": ["bounded_input_sequence"],
            "execution_kind": "software",
        },
    )
    session = service.compile_protocol(
        session.session_id,
        action_id="protocol",
        revision=session.revision,
        request={
            "operation": "bounded_input_sequence",
            "segments": [
                {"duration_s": 1, "input_value": 0},
                {"duration_s": 1, "input_value": 0.1},
                {"duration_s": 1, "input_value": 0},
            ],
            "repeats": 1,
            "sample_period_s": 0.1,
        },
    )
    registry = ProviderRegistry()
    registry.register(MalformedProvider())

    for action_id in ("attempt-1", "attempt-2"):
        with pytest.raises(ValueError, match="public_trace"):
            service.run_provider(
                session.session_id,
                action_id=action_id,
                revision=session.revision,
                provider_registry=registry,
            )
        session = service.read(session.session_id)

    blocked = service.run_provider(
        session.session_id,
        action_id="attempt-3",
        revision=session.revision,
        provider_registry=registry,
    )
    assert blocked.status == "capability_gap"
    assert len(blocked.experiment_failures) == 2
    assert (
        sum(
            event.event_type == "experiment_attempt_reserved"
            for event in blocked.events
        )
        == 2
    )


def test_unknown_ledger_runs_legal_experiment_then_revises_route(tmp_path):
    service = WorkflowService(tmp_path)
    session = service.start(public_training_case("dc_motor_speed_v1")["task"])
    session = service.confirm_task(
        session.session_id, action_id="confirm", revision=session.revision
    )
    identification, identification_id, evaluation, evaluation_id = (
        build_training_provider_registries("dc_motor_speed_v1")
    )
    result = service.run_until_blocked(
        session.session_id,
        provider_registry=identification,
        identification_provider_id=identification_id,
        evaluation_provider_registry=evaluation,
        evaluation_provider_id=evaluation_id,
    )

    assert result.status == "tuning_eligible"
    assert result.route["controller_contract_id"] == "PI"
    assert result.route_history[0]["provisional"] is True
    assert result.route_history[-1]["selection_basis"].startswith("versioned public")
    assert result.ledger.entry("open_loop_stability").assessment == "stable"
    assert any(
        event.event_type == "information_action_selected" for event in result.events
    )


def test_unknown_safety_limit_allows_only_passive_action(tmp_path):
    service = WorkflowService(tmp_path)
    session = service.start(
        {
            "description": "Observe a bounded process before excitation is authorized.",
            "measured_signals": ["y"],
            "control_input": "u",
            "input_min": -1,
            "input_max": 1,
            "budget_confirmed": True,
        }
    )
    selected = service.advance(
        session.session_id, action_id="select", revision=session.revision
    )
    assert selected.route["provisional"] is True
    assert all(
        segment["input_value"] == 0
        for segment in selected.route["experiment_request"]["segments"]
    )
    assert (
        "safe_excitation" in selected.route["blocked_actions"]["bounded_input_sequence"]
    )


def test_projection_exposes_three_independent_readiness_gates(tmp_path):
    service = WorkflowService(tmp_path)
    initial = service.start(public_training_case("dc_motor_speed_v1")["task"])
    gates = service.project(initial)["readiness_gates"]
    assert gates["evidence_acquisition"]["ready"] is False
    assert gates["route_selection"]["ready"] is False
    assert gates["controller_synthesis"]["ready"] is False
    assert "budget_confirmation_required" in gates["evidence_acquisition"]["blockers"]

    confirmed = service.confirm_task(
        initial.session_id, action_id="confirm", revision=initial.revision
    )
    selected = service.advance(
        confirmed.session_id, action_id="select", revision=confirmed.revision
    )
    gates = service.project(selected)["readiness_gates"]
    assert gates["evidence_acquisition"]["ready"] is True
    assert gates["route_selection"]["ready"] is False
    assert gates["controller_synthesis"]["ready"] is False

    identification, identification_id, evaluation, evaluation_id = (
        build_training_provider_registries("dc_motor_speed_v1")
    )
    completed = service.run_until_blocked(
        selected.session_id,
        provider_registry=identification,
        identification_provider_id=identification_id,
        evaluation_provider_registry=evaluation,
        evaluation_provider_id=evaluation_id,
    )
    gates = service.project(completed)["readiness_gates"]
    assert gates["route_selection"]["ready"] is True
    assert gates["controller_synthesis"]["ready"] is True
