import pytest

from cfdc.models import Algorithm1Observation, OnlineRefinementPolicy
from cfdc.online import (
    evaluate_algorithm1_probe,
    initialize_algorithm1,
    propose_algorithm1_candidate,
)
from cfdc.runtime import run_cfdc_route


def _state(**policy_updates):
    policy = OnlineRefinementPolicy(**policy_updates)
    return initialize_algorithm1(
        {"kp": 2.0, "kd": 3.0, "feedforward": 4.0},
        ["kp", "kd"],
        policy,
    )


def _observation(**updates):
    return Algorithm1Observation(dwell_time_s=1.0, **updates)


def test_policy_restricts_multiplier_to_five_through_ten_percent():
    with pytest.raises(ValueError):
        OnlineRefinementPolicy(step_multiplier=1.049)
    with pytest.raises(ValueError):
        OnlineRefinementPolicy(step_multiplier=1.101)


def test_proposal_multiplies_only_declared_tunable_gains():
    state = propose_algorithm1_candidate(_state())

    assert state.candidate_gains == pytest.approx({
        "kp": 2.1,
        "kd": 3.15,
        "feedforward": 4.0,
    })
    assert state.accepted_gains["feedforward"] == 4.0


def test_dwell_prevents_early_probe_evaluation():
    state = propose_algorithm1_candidate(_state(minimum_dwell_s=2.0))

    waiting = evaluate_algorithm1_probe(
        state,
        Algorithm1Observation(dwell_time_s=1.0),
    )

    assert waiting.status == "probing"
    assert waiting.accepted_gains == state.accepted_gains
    assert waiting.candidate_gains == state.candidate_gains
    assert waiting.history[-1]["action"] == "dwell_wait"


def test_safe_probe_accepts_candidate_and_preserves_previous_safe_gains():
    initial = _state()
    proposed = propose_algorithm1_candidate(initial)

    accepted = evaluate_algorithm1_probe(proposed, _observation())

    assert accepted.status == "ready"
    assert accepted.accepted_gains == proposed.candidate_gains
    assert accepted.previous_safe_gains == initial.accepted_gains
    assert accepted.iteration_count == 1


def test_first_soft_or_nmp_violation_waits_for_confirmation():
    proposed = propose_algorithm1_candidate(_state())

    first = evaluate_algorithm1_probe(
        proposed,
        _observation(soft_performance_violation=True),
    )

    assert first.status == "probing"
    assert first.consecutive_soft_violations == 1
    assert not first.frozen


def test_second_soft_violation_rolls_back_and_freezes():
    proposed = propose_algorithm1_candidate(_state())
    first = evaluate_algorithm1_probe(
        proposed,
        _observation(nmp_violation=True),
    )

    frozen = evaluate_algorithm1_probe(
        first,
        _observation(nmp_violation=True),
    )

    assert frozen.status == "frozen"
    assert frozen.frozen
    assert frozen.accepted_gains == proposed.accepted_gains
    assert frozen.candidate_gains == proposed.accepted_gains
    assert frozen.history[-1]["restored_gains"] == proposed.accepted_gains


def test_hard_safety_violation_rolls_back_immediately():
    proposed = propose_algorithm1_candidate(_state())

    frozen = evaluate_algorithm1_probe(
        proposed,
        _observation(
            hard_safety_violation=True,
            violation_reasons=["state_boundary"],
        ),
    )

    assert frozen.frozen
    assert frozen.freeze_reason == "state_boundary"
    assert frozen.accepted_gains == proposed.accepted_gains


def test_iteration_limit_and_target_completion_stop_new_candidates():
    state = _state(max_iterations=1)
    accepted = evaluate_algorithm1_probe(
        propose_algorithm1_candidate(state),
        _observation(),
    )
    limited = propose_algorithm1_candidate(accepted)
    assert limited.status == "completed"
    assert limited.completion_reason == "iteration_limit"

    target = evaluate_algorithm1_probe(
        propose_algorithm1_candidate(_state()),
        _observation(performance_target_met=True),
    )
    assert target.status == "completed"
    assert target.completion_reason == "performance_target_met"


@pytest.mark.parametrize("route_id", ["cartpole", "vtol-hover"])
def test_route_executors_report_shared_algorithm1_state(route_id):
    report = run_cfdc_route(route_id, include_trajectory=False)

    assert report.algorithm1_state is not None
    proposals = [
        entry
        for entry in report.algorithm1_state.history
        if entry.get("action") == "propose_candidate"
    ]
    assert proposals
    for proposal in proposals:
        for gain_name in report.algorithm1_state.tunable_gain_names:
            assert proposal["candidate_gains"][gain_name] == pytest.approx(
                1.05 * proposal["accepted_gains"][gain_name]
            )


def test_nmp_boundary_candidates_use_multiplicative_algorithm1_steps():
    cartpole = run_cfdc_route("cartpole", include_trajectory=False)
    cartpole_candidates = [
        event["candidate_outer_gains"]["kp_y"]
        for event in cartpole.cartpole_boundary.events
        if event.get("event") == "candidate_trial"
    ]
    assert all(
        current == pytest.approx(1.10 * previous)
        for previous, current in zip(cartpole_candidates, cartpole_candidates[1:])
    )

    vtol = run_cfdc_route("vtol-boundary", include_trajectory=False)
    vtol_candidates = [
        event["candidate_lateral_kp"]
        for event in vtol.vtol_simulation.events
        if event.get("event") == "candidate_trial"
    ]
    assert all(
        current == pytest.approx(1.10 * previous)
        for previous, current in zip(vtol_candidates, vtol_candidates[1:])
    )
