from __future__ import annotations

import numpy as np

from cfdc.models import (
    ControllerCandidate,
    FeatureTrackingUpdate,
    OnlinePerformanceMetrics,
    OnlineTuningState,
    SafeGainSearchState,
)
from cfdc.performance import calculate_channel_performance


def compute_performance_metrics(
    time_s: list[float] | np.ndarray,
    reference: list[float] | np.ndarray,
    output: list[float] | np.ndarray,
    control: list[float] | np.ndarray,
    saturation_limit: float | None = None,
    settling_band: float = 0.02,
) -> OnlinePerformanceMetrics:
    t = np.asarray(time_s, dtype=float)
    r = np.asarray(reference, dtype=float)
    y = np.asarray(output, dtype=float)
    u = np.asarray(control, dtype=float)
    if not (
        t.ndim == r.ndim == y.ndim == u.ndim == 1
        and t.size == r.size == y.size == u.size
    ):
        raise ValueError(
            "time, reference, output, and control must be equal-length vectors"
        )
    if t.size < 3:
        raise ValueError("at least three samples are required")

    channel_metrics = calculate_channel_performance(
        t,
        r,
        y,
        settling_band_fraction=settling_band,
    )

    window = max(3, min(21, u.size // 5 * 2 + 1))
    kernel = np.ones(window) / window
    smooth = np.convolve(u, kernel, mode="same")
    high_freq = u - smooth
    hf_rms = float(np.sqrt(np.mean(high_freq * high_freq)))
    if saturation_limit is None or saturation_limit <= 0:
        sat_fraction = 0.0
    else:
        sat_fraction = float(np.mean(np.abs(u) >= 0.98 * saturation_limit))

    return OnlinePerformanceMetrics(
        overshoot=channel_metrics.overshoot,
        settling_time_s=channel_metrics.settling_time_s,
        integral_absolute_error=channel_metrics.integral_absolute_error,
        high_frequency_control_rms=hf_rms,
        actuator_saturation_fraction=sat_fraction,
        nmp_undershoot=channel_metrics.undershoot,
    )


def _violations(
    metrics: OnlinePerformanceMetrics,
    constraints: dict[str, float],
) -> list[str]:
    reasons: list[str] = []
    if metrics.overshoot > constraints.get("max_overshoot", float("inf")):
        reasons.append("overshoot")
    max_settling = constraints.get("max_settling_time_s")
    if max_settling is not None and (
        metrics.settling_time_s is None or metrics.settling_time_s > max_settling
    ):
        reasons.append("settling_time")
    if metrics.integral_absolute_error > constraints.get(
        "max_integral_absolute_error", float("inf")
    ):
        reasons.append("integral_absolute_error")
    if metrics.high_frequency_control_rms > constraints.get(
        "max_high_frequency_control_rms", float("inf")
    ):
        reasons.append("high_frequency_control_rms")
    if metrics.actuator_saturation_fraction > constraints.get(
        "max_actuator_saturation_fraction", float("inf")
    ):
        reasons.append("actuator_saturation")
    if metrics.nmp_undershoot > constraints.get("max_nmp_undershoot", float("inf")):
        reasons.append("nmp_undershoot")
    return reasons


def refine_gains_once(
    state: OnlineTuningState,
    metrics: OnlinePerformanceMetrics,
    constraints: dict[str, float],
    tunable_gain_names: list[str] | None = None,
) -> OnlineTuningState:
    """Advance one constraint-driven online gain-refinement step."""

    if state.frozen:
        return state

    reasons = _violations(metrics, constraints)
    if reasons:
        rollback = state.previous_gains or state.gains
        history = state.history + [
            {
                "action": "rollback_and_freeze",
                "reasons": reasons,
                "tested_gains": state.gains,
                "restored_gains": rollback,
            }
        ]
        return OnlineTuningState(
            gains=rollback,
            previous_gains=state.previous_gains,
            frozen=True,
            freeze_reason=",".join(reasons),
            step_fraction=state.step_fraction,
            history=history,
        )

    tunable = set(state.gains if tunable_gain_names is None else tunable_gain_names)
    unknown = tunable - set(state.gains)
    if unknown:
        raise ValueError(f"unknown tunable gains: {', '.join(sorted(unknown))}")
    next_gains = {
        name: value * (1.0 + state.step_fraction) if name in tunable else value
        for name, value in state.gains.items()
    }
    history = state.history + [
        {
            "action": "increment",
            "fraction": state.step_fraction,
            "previous_gains": state.gains,
            "next_gains": next_gains,
        }
    ]
    return OnlineTuningState(
        gains=next_gains,
        previous_gains=state.gains,
        frozen=False,
        freeze_reason=None,
        step_fraction=state.step_fraction,
        history=history,
    )


def initialize_safe_gain_search(
    controller: ControllerCandidate,
    search_direction: dict[str, float] | None = None,
    step_fraction: float = 0.05,
) -> SafeGainSearchState:
    """Create a safe-search state from an unstable-plant controller candidate."""

    if controller.status != "requires_online_search":
        raise ValueError(
            "safe gain search should start from a controller requiring online search"
        )
    direction = search_direction or {name: 1.0 for name in controller.gains}
    return SafeGainSearchState(
        accepted_gains=dict(controller.gains),
        search_direction=direction,
        step_fraction=step_fraction,
        status="ready_for_trial",
    )


def propose_unstable_gain_candidate(state: SafeGainSearchState) -> SafeGainSearchState:
    """Propose one small unstable-plant gain-search increment without accepting it."""

    if state.frozen:
        return state
    if state.status == "trial_pending":
        return state

    candidate: dict[str, float] = {}
    for name, value in state.accepted_gains.items():
        direction = float(state.search_direction.get(name, 1.0))
        if value == 0.0:
            candidate[name] = state.step_fraction * direction
        else:
            candidate[name] = value * (1.0 + state.step_fraction * direction)
    history = state.history + [
        {
            "action": "propose_unstable_trial",
            "trial_index": state.trial_index + 1,
            "accepted_gains": state.accepted_gains,
            "candidate_gains": candidate,
            "step_fraction": state.step_fraction,
        }
    ]
    return SafeGainSearchState(
        accepted_gains=state.accepted_gains,
        candidate_gains=candidate,
        search_direction=state.search_direction,
        step_fraction=state.step_fraction,
        trial_index=state.trial_index + 1,
        status="trial_pending",
        history=history,
    )


def evaluate_unstable_gain_trial(
    state: SafeGainSearchState,
    metrics: OnlinePerformanceMetrics,
    constraints: dict[str, float],
) -> SafeGainSearchState:
    """Accept a safe unstable-plant trial or rollback and freeze on violation."""

    if state.frozen:
        return state
    if state.status != "trial_pending" or state.candidate_gains is None:
        raise ValueError("a candidate trial must be proposed before evaluation")

    reasons = _violations(metrics, constraints)
    if reasons:
        history = state.history + [
            {
                "action": "rollback_and_freeze_unstable_trial",
                "trial_index": state.trial_index,
                "reasons": reasons,
                "rejected_gains": state.candidate_gains,
                "restored_gains": state.accepted_gains,
            }
        ]
        return SafeGainSearchState(
            accepted_gains=state.accepted_gains,
            candidate_gains=None,
            search_direction=state.search_direction,
            step_fraction=state.step_fraction,
            trial_index=state.trial_index,
            frozen=True,
            freeze_reason=",".join(reasons),
            status="frozen",
            history=history,
        )

    history = state.history + [
        {
            "action": "accept_unstable_trial",
            "trial_index": state.trial_index,
            "accepted_gains": state.candidate_gains,
        }
    ]
    return SafeGainSearchState(
        accepted_gains=state.candidate_gains,
        candidate_gains=None,
        search_direction=state.search_direction,
        step_fraction=state.step_fraction,
        trial_index=state.trial_index,
        status="accepted",
        history=history,
    )


def update_tracked_feature(
    feature_id: str,
    previous_value: float,
    measured_value: float,
    threshold: float = 0.05,
    smoothing_factor: float = 0.01,
) -> FeatureTrackingUpdate:
    if previous_value == 0:
        relative = 1e12 if measured_value != 0 else 0.0
    else:
        relative = abs(measured_value - previous_value) / abs(previous_value)
    required = relative > threshold
    updated = (
        (1.0 - smoothing_factor) * previous_value + smoothing_factor * measured_value
        if required
        else previous_value
    )
    return FeatureTrackingUpdate(
        feature_id=feature_id,
        previous_value=previous_value,
        measured_value=measured_value,
        updated_value=updated,
        relative_change=relative,
        controller_update_required=required,
        smoothing_factor=smoothing_factor,
    )
