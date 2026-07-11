from __future__ import annotations

import math

import numpy as np

from cfdc.models import (
    ControllerCandidate,
    FLLTrackerState,
    FeatureTrackingUpdate,
    HoverAverageTrackerState,
    ScalarRLSTrackerState,
    TrackingObservation,
    TrackingSchedulerState,
)
from cfdc.online.refinement import update_tracked_feature


def tracking_scheduler_eligible(
    state: TrackingSchedulerState,
    observation: TrackingObservation,
) -> tuple[TrackingSchedulerState, bool]:
    reason: str | None = None
    if not observation.steady_operating_mode:
        reason = "not_steady_operating_mode"
    elif observation.tracking_error > state.tracking_error_threshold:
        reason = "tracking_error_too_large"
    elif observation.hard_safety_active:
        reason = "hard_safety_active"
    elif observation.aggressive_maneuver:
        reason = "aggressive_maneuver_active"
    elif (
        state.last_eligible_time_s is not None
        and observation.time_s - state.last_eligible_time_s < state.duty_interval_s
    ):
        reason = "duty_interval_not_elapsed"

    if reason is not None:
        return state.model_copy(update={"pause_reason": reason}), False
    return (
        state.model_copy(
            update={
                "last_eligible_time_s": observation.time_s,
                "pause_reason": None,
                "eligible_update_count": state.eligible_update_count + 1,
            }
        ),
        True,
    )


def update_fll_window(
    state: FLLTrackerState,
    time_s: list[float],
    signal: list[float],
) -> FLLTrackerState:
    time = np.asarray(time_s, dtype=float)
    values = np.asarray(signal, dtype=float)
    if time.ndim != 1 or values.ndim != 1 or len(time) != len(values) or len(time) < 8:
        raise ValueError("FLL window requires equal one-dimensional arrays with at least 8 samples")
    if not np.all(np.isfinite(time)) or not np.all(np.isfinite(values)):
        raise ValueError("FLL window values must be finite")
    if np.any(np.diff(time) <= 0.0):
        raise ValueError("FLL time values must be strictly increasing")

    centered = values - float(np.mean(values))
    energy = float(np.dot(centered, centered))
    if energy <= 1e-12:
        return state.model_copy(
            update={
                "last_lock_quality": 0.0,
                "last_update_accepted": False,
                "rejected_update_count": state.rejected_update_count + 1,
                "window_time_s": time.tolist(),
                "window_signal": values.tolist(),
            }
        )
    low = max(1e-6, state.angular_frequency_rad_s - state.bandwidth_rad_s)
    high = state.angular_frequency_rad_s + state.bandwidth_rad_s
    grid = np.linspace(low, high, 161)
    scores = np.asarray(
        [
            abs(np.sum(centered * np.exp(-1j * omega * time)))
            / math.sqrt(energy * len(time))
            for omega in grid
        ]
    )
    best_index = int(np.argmax(scores))
    best_frequency = float(grid[best_index])
    lock_quality = min(1.0, float(scores[best_index]))
    accepted = lock_quality >= state.minimum_lock_quality
    updated_frequency = (
        (1.0 - state.smoothing_gain) * state.angular_frequency_rad_s
        + state.smoothing_gain * best_frequency
        if accepted
        else state.angular_frequency_rad_s
    )
    return state.model_copy(
        update={
            "angular_frequency_rad_s": updated_frequency,
            "last_lock_quality": lock_quality,
            "last_update_accepted": accepted,
            "accepted_update_count": state.accepted_update_count + int(accepted),
            "rejected_update_count": state.rejected_update_count + int(not accepted),
            "window_time_s": time.tolist(),
            "window_signal": values.tolist(),
        }
    )


def update_scalar_rls(
    state: ScalarRLSTrackerState,
    regressor: float,
    response: float,
) -> ScalarRLSTrackerState:
    if not math.isfinite(regressor) or not math.isfinite(response):
        raise ValueError("RLS samples must be finite")
    if abs(regressor) <= 1e-12:
        return state.model_copy(
            update={"ignored_sample_count": state.ignored_sample_count + 1}
        )
    denominator = state.forgetting_factor + state.covariance * regressor**2
    gain = state.covariance * regressor / denominator
    estimate = state.parameter_estimate + gain * (
        response - regressor * state.parameter_estimate
    )
    covariance = (
        state.covariance - gain * regressor * state.covariance
    ) / state.forgetting_factor
    return state.model_copy(
        update={
            "parameter_estimate": estimate,
            "covariance": max(covariance, 1e-12),
            "update_count": state.update_count + 1,
        }
    )


def update_hover_average(
    state: HoverAverageTrackerState,
    measured_control_effort: float,
    dt_s: float,
) -> HoverAverageTrackerState:
    if not math.isfinite(measured_control_effort) or dt_s <= 0.0:
        raise ValueError("hover average requires finite effort and positive dt_s")
    alpha = 1.0 - math.exp(-dt_s / state.time_constant_s)
    average = (
        (1.0 - alpha) * state.average_control_effort
        + alpha * measured_control_effort
    )
    return state.model_copy(
        update={
            "average_control_effort": average,
            "update_count": state.update_count + 1,
        }
    )


def adapt_controller_from_tracked_feature(
    controller: ControllerCandidate,
    feature_id: str,
    previous_value: float,
    measured_value: float,
    *,
    threshold: float = 0.05,
    smoothing_factor: float = 0.1,
) -> tuple[ControllerCandidate, FeatureTrackingUpdate, bool]:
    update = update_tracked_feature(
        feature_id,
        previous_value,
        measured_value,
        threshold=threshold,
        smoothing_factor=smoothing_factor,
    )
    if not update.controller_update_required:
        return controller, update, False

    gains = dict(controller.gains)
    feedforward = dict(controller.feedforward)
    if feature_id == "hover_thrust":
        feedforward["hover_thrust"] = update.updated_value
    elif feature_id == "natural_frequency" and previous_value != 0.0:
        ratio = update.updated_value / previous_value
        gains = {
            name: value * ratio
            for name, value in gains.items()
        }
    elif feature_id in {"input_gain", "angular_acceleration_gain"} and update.updated_value != 0.0:
        inverse_ratio = previous_value / update.updated_value
        gains = {
            name: value * inverse_ratio
            for name, value in gains.items()
        }
    relative_change = update.relative_change
    nmp_retune_requested = (
        feature_id == "hover_thrust" and relative_change > 0.10
    )
    return (
        controller.model_copy(update={"gains": gains, "feedforward": feedforward}),
        update,
        nmp_retune_requested,
    )
