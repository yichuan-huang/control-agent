from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from cfdc.models import ChannelPerformanceMetrics, SimulationPerformanceSummary


def calculate_channel_performance(
    time_s: Sequence[float],
    reference: Sequence[float] | float,
    output: Sequence[float],
    *,
    settling_band_fraction: float = 0.02,
    settling_band_absolute: float = 0.0,
) -> ChannelPerformanceMetrics:
    t = np.asarray(time_s, dtype=float)
    y = np.asarray(output, dtype=float)
    if np.isscalar(reference):
        r = np.full_like(y, float(reference), dtype=float)
    else:
        r = np.asarray(reference, dtype=float)
    if not (t.ndim == y.ndim == r.ndim == 1 and t.size == y.size == r.size and t.size >= 2):
        raise ValueError("time, reference, and output must be equal-length vectors with at least two samples")

    final_reference = float(r[-1])
    final_output = float(y[-1])
    error = r - y
    final_error = float(error[-1])
    step = final_reference - float(y[0])
    scale = max(abs(step), 1e-12)
    if step > 0.0:
        overshoot = max(0.0, float(np.max(y) - final_reference) / scale)
        undershoot = max(0.0, float(y[0] - np.min(y)) / scale)
    elif step < 0.0:
        overshoot = max(0.0, float(final_reference - np.min(y)) / scale)
        undershoot = max(0.0, float(np.max(y) - y[0]) / scale)
    else:
        overshoot = 0.0
        undershoot = 0.0

    band = max(settling_band_fraction * abs(step), settling_band_absolute, 1e-12)
    settling_time_s: float | None = None
    for index in range(t.size):
        if np.all(np.abs(error[index:]) <= band):
            settling_time_s = float(t[index] - t[0])
            break

    return ChannelPerformanceMetrics(
        reference=final_reference,
        final_output=final_output,
        final_error=final_error,
        abs_final_error=abs(final_error),
        overshoot=overshoot,
        undershoot=undershoot,
        settled=settling_time_s is not None,
        settling_time_s=settling_time_s,
        integral_absolute_error=float(np.trapezoid(np.abs(error), t)),
        max_abs_output=float(np.max(np.abs(y))),
        max_abs_error=float(np.max(np.abs(error))),
    )


def build_performance_summary(
    *,
    primary_channel: str,
    channels: dict[str, ChannelPerformanceMetrics],
    actuator_saturation_fractions: dict[str, float],
    state_boundaries: dict[str, float],
    limits: dict[str, float],
    violations: list[str],
    success: bool,
    capture_success: bool | None = None,
    capture_time_s: float | None = None,
    boundary_triggered: bool | None = None,
    boundary_reason: str | None = None,
) -> SimulationPerformanceSummary:
    if primary_channel not in channels:
        raise ValueError(f"primary channel '{primary_channel}' is missing")
    primary = channels[primary_channel]
    saturation_fraction = max(actuator_saturation_fractions.values(), default=0.0)
    return SimulationPerformanceSummary(
        primary_channel=primary_channel,
        final_output=primary.final_output,
        final_error=primary.final_error,
        abs_final_error=primary.abs_final_error,
        overshoot=primary.overshoot,
        undershoot=primary.undershoot,
        settled=primary.settled,
        settling_time_s=primary.settling_time_s,
        saturation_fraction=saturation_fraction,
        success=success,
        channels=channels,
        actuator_saturation_fractions=actuator_saturation_fractions,
        state_boundaries=state_boundaries,
        limits=limits,
        violations=violations,
        capture_success=capture_success,
        capture_time_s=capture_time_s,
        boundary_triggered=boundary_triggered,
        boundary_reason=boundary_reason,
    )
