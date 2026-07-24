from __future__ import annotations

import json

import pytest

from cfdc.lab import (
    ComplexValue,
    PControllerSpec,
    ProposalValidationError,
    SessionActionError,
    SessionImportError,
    SimulationEvent,
    SimulationRunConfig,
    SimulationTrace,
    StabilityDecision,
    StaleRevisionError,
    TuningParameterRule,
    TuningProfile,
    approve_llm_proposal,
    cancel_session,
    confirm_model,
    create_free_input_session,
    export_session,
    extract_tunable_parameters,
    import_session,
    append_llm_call,
    make_llm_call_record,
    make_tuning_profile,
    propose_deterministic_update,
    register_llm_proposal,
    reject_llm_proposal,
    restore_safe_controller,
    rollback_session,
    run_deterministic_auto,
    run_next_trial,
    set_initial_controller,
    set_pending_model,
)
from cfdc.models import TransferFunctionModelSpec


def model():
    return TransferFunctionModelSpec(
        numerator=[1.0],
        denominator=[1.0, 1.0],
        input_signal_id="u",
        output_signal_id="y",
        input_units="V",
        output_units="m",
    )


def config():
    return SimulationRunConfig(
        reference={"y": 1.0},
        horizon_s=1.0,
        sample_time_s=0.1,
        actuator_bounds={"u": (-10.0, 10.0)},
        output_bounds={"y": (-10.0, 10.0)},
    )


def trace(*, hard=False):
    events = (
        [
            SimulationEvent(
                kind="hard_bound_violation",
                sample_index=1,
                time_s=0.1,
                message="state crossed hard bound",
            )
        ]
        if hard
        else []
    )
    return SimulationTrace(
        time_s=[0.0, 0.1],
        reference={"y": [1.0, 1.0]},
        outputs={"y": [0.0, 0.1]},
        requested_controls={"u": [1.0, 0.9]},
        applied_controls={"u": [1.0, 0.9]},
        events=events,
    )


def decision(
    status="unstable",
    *,
    pole=0.2,
    contraction=0.0,
    saturation=0.0,
    hard=False,
):
    return StabilityDecision(
        status=status,
        analysis_domain="continuous",
        pole_analysis_method="exact_continuous_interconnection",
        poles=[ComplexValue(real=pole, imaginary=0.0)],
        trajectory_finite=not hard,
        trajectory_bounded=not hard,
        tail_error_envelope_contraction=contraction,
        saturation_fraction=saturation,
        hard_failure=hard,
        violations=["hard"] if hard else [],
        evidence=["typed fake evidence"],
    )


def runner_for(*decisions):
    values = list(decisions)

    def runner(_model, _controller):
        return [trace(hard=values[0].hard_failure)], values.pop(0)

    return runner


def ready_session(
    *,
    open_loop="stable",
    gain=1.0,
    step=0.05,
    bounds=(-10.0, 10.0),
    zero_scale=None,
):
    session = create_free_input_session(pending_model=model())
    session = confirm_model(session, expected_revision=session.revision)
    controller = PControllerSpec(kp=gain)
    profile = TuningProfile(
        profile_id="test",
        open_loop_behavior=open_loop,
        step_fraction=step,
        parameters=[
            TuningParameterRule(
                name="kp",
                binding="kp",
                lower_bound=bounds[0],
                upper_bound=bounds[1],
                stabilizing_direction=1,
                zero_step_scale=zero_scale,
            )
        ],
    )
    return set_initial_controller(
        session,
        controller,
        tuning_profile=profile,
        run_config=config(),
        expected_revision=session.revision,
    )


def test_model_confirmation_and_controller_gates_are_revisioned_copy_on_write():
    original = create_free_input_session()
    with pytest.raises(SessionActionError):
        confirm_model(original, expected_revision=0)
    reviewed = set_pending_model(
        original, model(), assumptions=["local linear model"], expected_revision=0
    )
    assert original.revision == 0
    assert original.pending_model is None
    with pytest.raises(StaleRevisionError):
        confirm_model(reviewed, expected_revision=0)
    confirmed = confirm_model(reviewed, expected_revision=1)
    assert confirmed.state == "controller_ready"
    with pytest.raises(SessionActionError):
        run_next_trial(confirmed)


def test_run_next_records_evaluating_and_stops_at_first_stable():
    session = ready_session()
    complete = run_next_trial(
        session,
        expected_revision=session.revision,
        runner=runner_for(
            decision("stable", pole=-0.5, contraction=0.2)
        ),
    )
    assert complete.state == "stable"
    assert complete.revision == session.revision + 2
    assert [item.to_state for item in complete.transition_history[-2:]] == [
        "evaluating",
        "stable",
    ]
    assert len(complete.trials) == 1
    with pytest.raises(SessionActionError):
        run_next_trial(complete)


def test_stable_plant_reduces_and_unstable_plant_increases_exact_step():
    stable = run_next_trial(
        ready_session(open_loop="stable", gain=2.0, step=0.05),
        runner=runner_for(decision()),
    )
    stable = propose_deterministic_update(stable)
    assert extract_tunable_parameters(
        stable.trial_controller, stable.tuning_profile
    ) == {"kp": 1.9}

    unstable = run_next_trial(
        ready_session(open_loop="unstable", gain=2.0, step=0.10),
        runner=runner_for(decision()),
    )
    unstable = propose_deterministic_update(unstable)
    assert extract_tunable_parameters(
        unstable.trial_controller, unstable.tuning_profile
    ) == {"kp": 2.2}


def test_zero_gain_and_bounds_fail_closed_instead_of_looping():
    zero = run_next_trial(
        ready_session(open_loop="unstable", gain=0.0),
        runner=runner_for(decision()),
    )
    assert propose_deterministic_update(zero).state == "inconclusive"
    movable = run_next_trial(
        ready_session(
            open_loop="unstable", gain=0.0, zero_scale=2.0, bounds=(-1, 1)
        ),
        runner=runner_for(decision()),
    )
    moved = propose_deterministic_update(movable)
    assert moved.pending_proposal.new_parameters["kp"] == pytest.approx(0.1)


def test_llm_proposal_requires_exact_whitelist_ten_percent_and_approval():
    session = run_next_trial(
        ready_session(open_loop="unstable", gain=2.0),
        runner=runner_for(decision()),
    )
    with pytest.raises(ProposalValidationError):
        register_llm_proposal(
            session, new_parameters={"unknown": 2.1}, rationale="bad"
        )
    with pytest.raises(ProposalValidationError, match="more than 10"):
        register_llm_proposal(
            session, new_parameters={"kp": 2.21}, rationale="too large"
        )
    pending = register_llm_proposal(
        session,
        new_parameters={"kp": 2.2},
        rationale="stability-only change",
    )
    assert pending.state == "needs_adjustment"
    assert pending.trial_controller.kp == 2.0
    approved = approve_llm_proposal(
        pending, expected_revision=pending.revision
    )
    assert approved.state == "trial_pending"
    assert approved.trial_controller.kp == 2.2
    with pytest.raises(SessionActionError):
        approve_llm_proposal(approved)


def test_llm_reject_does_not_change_controller():
    session = run_next_trial(
        ready_session(open_loop="unstable"), runner=runner_for(decision())
    )
    pending = register_llm_proposal(
        session, new_parameters={"kp": 1.05}, rationale="proposal"
    )
    rejected = reject_llm_proposal(pending)
    assert rejected.pending_proposal.approval_state == "rejected"
    assert rejected.trial_controller.kp == 1.0


def test_hard_violation_rolls_back_and_soft_worsening_freezes():
    session = ready_session()
    hard = run_next_trial(
        session,
        runner=runner_for(decision(hard=True)),
    )
    assert hard.state == "rolled_back"
    assert hard.trials[-1].rolled_back
    assert hard.trial_controller == session.current_safe_controller

    soft = ready_session(open_loop="unstable")
    fake = runner_for(
        decision(pole=0.1),
        decision(pole=0.2),
        decision(pole=0.3),
    )
    for expected_state in ("needs_adjustment", "needs_adjustment", "frozen"):
        soft = run_next_trial(soft, runner=fake)
        assert soft.state == expected_state
        if soft.state == "needs_adjustment":
            soft = propose_deterministic_update(soft)


def test_auto_mode_never_accepts_or_calls_an_llm_and_stops_stable():
    session = ready_session(open_loop="unstable")
    calls = {"runner": 0}

    def fake_runner(_model, _controller):
        calls["runner"] += 1
        result = (
            decision()
            if calls["runner"] == 1
            else decision("stable", pole=-0.2, contraction=0.2)
        )
        return [trace()], result

    complete = run_deterministic_auto(session, runner=fake_runner)
    assert complete.state == "stable"
    assert calls == {"runner": 2}


def test_rollback_restore_cancel_and_illegal_terminal_actions():
    cancelled_review = cancel_session(create_free_input_session())
    assert cancelled_review.state == "cancelled"
    session = run_next_trial(ready_session(), runner=runner_for(decision()))
    rolled = rollback_session(session)
    assert rolled.state == "rolled_back"
    restored = restore_safe_controller(rolled)
    assert restored.state == "trial_pending"
    cancelled = cancel_session(restored)
    assert cancelled.state == "cancelled"
    with pytest.raises(SessionActionError):
        cancel_session(cancelled)


def test_exact_twenty_trial_budget_and_trial_20_stable_wins():
    session = ready_session(open_loop="unstable")
    for index in range(20):
        status = "stable" if index == 19 else "unstable"
        session = run_next_trial(
            session,
            runner=runner_for(
                decision(status, pole=-0.2 if status == "stable" else 0.2)
            ),
        )
        if session.state == "needs_adjustment":
            session = propose_deterministic_update(session)
    assert session.state == "stable"
    assert len(session.trials) == 20

    budget = ready_session(open_loop="unstable")
    for _ in range(20):
        budget = run_next_trial(
            budget, runner=runner_for(decision(pole=0.2))
        )
        if budget.state == "needs_adjustment":
            budget = propose_deterministic_update(budget)
    assert budget.state == "budget_exhausted"
    assert len(budget.trials) == 20


def test_json_roundtrip_is_deep_and_tamper_secret_nonfinite_fail_closed():
    session = run_next_trial(
        ready_session(),
        runner=runner_for(decision("stable", pole=-0.2)),
    )
    exported = export_session(session)
    restored = import_session(exported)
    assert restored == session
    restored.model_assumptions.append("caller mutation")
    assert session.model_assumptions == []

    payload = json.loads(exported)
    payload["termination_reason"] = "tampered"
    with pytest.raises(SessionImportError, match="checksum"):
        import_session(json.dumps(payload))
    with pytest.raises(SessionImportError, match="sensitive"):
        import_session(exported[:-1] + ', "API-Key": "secret"}')
    with pytest.raises(SessionImportError, match="non-finite"):
        import_session(exported.replace('"revision": 4', '"revision": NaN'))


def test_duplicate_json_keys_and_extra_fields_are_rejected():
    exported = export_session(ready_session())
    with pytest.raises(SessionImportError, match="duplicate"):
        import_session(exported[:-1] + ', "state": "trial_pending"}')
    payload = json.loads(exported)
    payload["extra"] = "no"
    payload["content_sha256"] = "0" * 64
    with pytest.raises(SessionImportError):
        import_session(json.dumps(payload))


def test_imported_evaluating_session_never_auto_resumes():
    import cfdc.lab.session as session_module

    pending = ready_session()
    evaluating = session_module._transition(
        pending, to_state="evaluating", action="begin_trial"
    )
    recovered = import_session(export_session(evaluating))
    assert recovered.state == "trial_pending"
    assert recovered.revision == evaluating.revision + 1
    assert recovered.trials == []
    assert recovered.transition_history[-1].action == "recover_inflight_import"


def test_nonfinite_raw_runner_result_rolls_back_without_crashing():
    session = ready_session()
    raw_trace = trace().model_dump(mode="python")
    raw_trace["outputs"]["y"][1] = float("nan")

    def bad_runner(_model, _controller):
        return [raw_trace], decision().model_dump(mode="python")

    result = run_next_trial(session, runner=bad_runner)
    assert result.state == "rolled_back"
    assert result.trials[-1].hard_violation
    assert result.trials[-1].rolled_back


def test_unrelated_audit_revision_marks_pending_llm_proposal_stale():
    session = run_next_trial(
        ready_session(open_loop="unstable"), runner=runner_for(decision())
    )
    pending = register_llm_proposal(
        session, new_parameters={"kp": 1.05}, rationale="pending"
    )
    record = make_llm_call_record(
        operation="gain_proposal",
        provider="test",
        model="test",
        messages=[
            {"role": "system", "content": "sanitized"},
            {"role": "user", "content": "sanitized"},
        ],
        structured_response={"status": "audit-only"},
        validation_status="accepted",
    )
    revised = append_llm_call(
        pending, record, expected_revision=pending.revision
    )
    stale = approve_llm_proposal(
        revised, expected_revision=revised.revision
    )
    assert stale.state == "needs_adjustment"
    assert stale.pending_proposal.approval_state == "stale"
    assert stale.trial_controller.kp == 1.0
