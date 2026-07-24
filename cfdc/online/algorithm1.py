from __future__ import annotations

from cfdc.models import (
    Algorithm1Observation,
    Algorithm1State,
    OnlineRefinementPolicy,
)


def initialize_algorithm1(
    initial_safe_gains: dict[str, float],
    tunable_gain_names: list[str],
    policy: OnlineRefinementPolicy | None = None,
) -> Algorithm1State:
    if not initial_safe_gains:
        raise ValueError("Algorithm 1 requires at least one initial safe gain")
    return Algorithm1State(
        accepted_gains=dict(initial_safe_gains),
        previous_safe_gains=dict(initial_safe_gains),
        tunable_gain_names=list(tunable_gain_names),
        policy=policy or OnlineRefinementPolicy(),
        history=[
            {
                "action": "initialize",
                "accepted_gains": dict(initial_safe_gains),
                "tunable_gain_names": list(tunable_gain_names),
            }
        ],
    )


def propose_algorithm1_candidate(state: Algorithm1State) -> Algorithm1State:
    if state.frozen or state.status in {"frozen", "completed", "probing"}:
        return state
    if state.iteration_count >= state.policy.max_iterations:
        return state.model_copy(
            update={
                "status": "completed",
                "completion_reason": "iteration_limit",
                "history": [
                    *state.history,
                    {
                        "action": "complete",
                        "reason": "iteration_limit",
                        "accepted_gains": state.accepted_gains,
                    },
                ],
            }
        )

    tunable = set(state.tunable_gain_names)
    candidate = {
        name: (value * state.policy.step_multiplier if name in tunable else value)
        for name, value in state.accepted_gains.items()
    }
    return state.model_copy(
        update={
            "previous_safe_gains": dict(state.accepted_gains),
            "candidate_gains": candidate,
            "status": "probing",
            "consecutive_soft_violations": 0,
            "history": [
                *state.history,
                {
                    "action": "propose_candidate",
                    "iteration": state.iteration_count + 1,
                    "step_multiplier": state.policy.step_multiplier,
                    "accepted_gains": state.accepted_gains,
                    "candidate_gains": candidate,
                },
            ],
        }
    )


def _rollback_and_freeze(
    state: Algorithm1State,
    reasons: list[str],
    action: str,
) -> Algorithm1State:
    restored = dict(state.accepted_gains)
    return state.model_copy(
        update={
            "candidate_gains": restored,
            "status": "frozen",
            "frozen": True,
            "freeze_reason": ",".join(reasons),
            "history": [
                *state.history,
                {
                    "action": action,
                    "reasons": reasons,
                    "rejected_gains": state.candidate_gains,
                    "restored_gains": restored,
                },
            ],
        }
    )


def evaluate_algorithm1_probe(
    state: Algorithm1State,
    observation: Algorithm1Observation,
) -> Algorithm1State:
    if state.frozen:
        return state
    if state.status != "probing" or state.candidate_gains is None:
        raise ValueError("Algorithm 1 requires a proposed candidate before evaluation")
    if observation.dwell_time_s < state.policy.minimum_dwell_s:
        return state.model_copy(
            update={
                "history": [
                    *state.history,
                    {
                        "action": "dwell_wait",
                        "observed_dwell_s": observation.dwell_time_s,
                        "required_dwell_s": state.policy.minimum_dwell_s,
                    },
                ]
            }
        )

    reasons = list(observation.violation_reasons)
    if observation.hard_safety_violation:
        return _rollback_and_freeze(
            state,
            reasons or ["hard_safety_violation"],
            "hard_violation_rollback_and_freeze",
        )

    soft_violation = observation.soft_performance_violation or observation.nmp_violation
    if soft_violation:
        count = state.consecutive_soft_violations + 1
        soft_reasons = reasons or [
            "nmp_violation"
            if observation.nmp_violation
            else "soft_performance_violation"
        ]
        if count >= state.policy.soft_violation_confirmations:
            return _rollback_and_freeze(
                state.model_copy(update={"consecutive_soft_violations": count}),
                soft_reasons,
                "confirmed_soft_violation_rollback_and_freeze",
            )
        return state.model_copy(
            update={
                "consecutive_soft_violations": count,
                "history": [
                    *state.history,
                    {
                        "action": "soft_violation_confirmation_pending",
                        "count": count,
                        "required": state.policy.soft_violation_confirmations,
                        "reasons": soft_reasons,
                    },
                ],
            }
        )

    accepted = dict(state.candidate_gains)
    completed = observation.performance_target_met
    return state.model_copy(
        update={
            "previous_safe_gains": dict(state.accepted_gains),
            "accepted_gains": accepted,
            "candidate_gains": None,
            "iteration_count": state.iteration_count + 1,
            "consecutive_soft_violations": 0,
            "status": "completed" if completed else "ready",
            "completion_reason": ("performance_target_met" if completed else None),
            "history": [
                *state.history,
                {
                    "action": "accept_candidate",
                    "accepted_gains": accepted,
                    "metrics": observation.metrics,
                    "performance_target_met": completed,
                },
            ],
        }
    )
