from __future__ import annotations

import math

import numpy as np
from scipy.signal import find_peaks, lfilter, periodogram

from cfdc.models import CoreFeatureArtifact, ExperimentPrimitive


def _as_array(values: np.ndarray | list[float]) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    if arr.ndim != 1 or arr.size < 3:
        raise ValueError("Expected a one-dimensional array with at least three samples")
    if not np.all(np.isfinite(arr)):
        raise ValueError("Input contains non-finite values")
    return arr


def _bounds(value: float, half_width: float) -> tuple[float, float]:
    low = value - abs(half_width)
    high = value + abs(half_width)
    return (min(low, high), max(low, high))


def _integrate(values: np.ndarray, time_s: np.ndarray) -> float:
    return float(np.trapezoid(values, time_s))


def low_pass_filter(
    values: np.ndarray | list[float], dt_s: float, cutoff_hz: float
) -> np.ndarray:
    data = _as_array(values)
    if dt_s <= 0 or cutoff_hz <= 0:
        raise ValueError("dt_s and cutoff_hz must be positive")
    rc = 1.0 / (2.0 * math.pi * cutoff_hz)
    alpha = dt_s / (rc + dt_s)
    filtered, _ = lfilter(
        [alpha],
        [1.0, -(1.0 - alpha)],
        data,
        zi=[(1.0 - alpha) * data[0]],
    )
    return filtered


def steady_state_detected(
    values: np.ndarray | list[float],
    window: int = 20,
    slope_tolerance: float = 1e-3,
) -> bool:
    data = _as_array(values)
    if data.size < max(4, window):
        return False
    tail = data[-window:]
    x = np.arange(tail.size, dtype=float)
    slope = np.polyfit(x, tail, 1)[0]
    span = max(float(np.ptp(data)), 1e-9)
    return abs(slope) / span <= slope_tolerance


def estimate_natural_frequency(
    time_s: np.ndarray | list[float],
    signal: np.ndarray | list[float],
    bandwidth_hz: float = 0.1,
) -> CoreFeatureArtifact:
    """Estimate natural frequency with a narrow matched-filter frequency scan."""

    t = _as_array(time_s)
    y = _as_array(signal)
    if t.size != y.size:
        raise ValueError("time and signal arrays must have equal length")
    dt = float(np.median(np.diff(t)))
    if dt <= 0:
        raise ValueError("time must be strictly increasing")

    centered = y - np.mean(y)
    freqs, power = periodogram(
        centered,
        fs=1.0 / dt,
        window="hann",
        detrend=False,
        scaling="spectrum",
    )
    if freqs.size < 3:
        raise ValueError("not enough samples for frequency extraction")
    power[0] = 0.0
    peak_idx = int(np.argmax(power))
    peak_hz = float(freqs[peak_idx])
    if peak_hz <= 0:
        raise ValueError("no oscillatory component detected")

    search_half_width = max(3.0 * bandwidth_hz, 0.25 * peak_hz)
    low_hz = max(1e-6, peak_hz - search_half_width)
    high_hz = peak_hz + search_half_width
    grid = np.linspace(low_hz, high_hz, 500)
    centered_norm = centered / max(float(np.std(centered)), 1e-12)
    scores = np.array(
        [abs(np.sum(centered_norm * np.exp(-2j * math.pi * freq * t))) for freq in grid]
    )
    best_idx = int(np.argmax(scores))
    best_hz = float(grid[best_idx])
    omega = 2.0 * math.pi * best_hz

    sorted_scores = np.sort(scores)
    peak_ratio = float(sorted_scores[-1] / max(sorted_scores[-2], 1e-12))
    width_rad = 2.0 * math.pi * max(bandwidth_hz, 0.02 * best_hz)
    lower, upper = _bounds(omega, width_rad)
    confidence = min(0.98, 0.55 + 0.15 * peak_ratio)
    flags = [] if confidence > 0.7 else ["weak_frequency_lock"]

    return CoreFeatureArtifact(
        feature_id="natural_frequency",
        value=omega,
        lower_bound=max(0.0, lower),
        upper_bound=upper,
        confidence=confidence,
        units="rad/s",
        method="frequency_locked_matched_filter",
        source_experiment=ExperimentPrimitive.FREE_DECAY,
        data_quality_flags=flags,
    )


def estimate_damping_ratio(
    time_s: np.ndarray | list[float],
    signal: np.ndarray | list[float],
) -> CoreFeatureArtifact:
    """Estimate damping ratio from peak decay in a free response trace."""

    t = _as_array(time_s)
    y = _as_array(signal)
    if t.size != y.size:
        raise ValueError("time and signal arrays must have equal length")
    dt = float(np.median(np.diff(t)))
    if dt <= 0:
        raise ValueError("time must be strictly increasing")
    centered = y - float(np.median(y[-max(3, y.size // 10) :]))
    amplitudes = np.abs(centered)
    max_amplitude = float(np.max(amplitudes))
    amplitude_floor = max(1e-9, 0.05 * max_amplitude)
    freqs, power = periodogram(
        centered,
        fs=1.0 / dt,
        window="hann",
        detrend=False,
        scaling="spectrum",
    )
    power[0] = 0.0
    dominant_hz = float(freqs[int(np.argmax(power))])
    minimum_peak_distance = max(1, int(0.35 / max(dominant_hz * dt, 1e-12)))
    peak_indices, properties = find_peaks(
        amplitudes,
        height=amplitude_floor,
        prominence=max(1e-9, 0.02 * max_amplitude),
        distance=minimum_peak_distance,
    )
    peaks = list(zip(t[peak_indices].tolist(), properties["peak_heights"].tolist()))
    if len(peaks) < 3:
        raise ValueError("not enough decaying peaks for damping-ratio extraction")

    reliable_floor = max(amplitude_floor, 0.20 * max_amplitude)
    reliable_peaks = [(time, amp) for time, amp in peaks if amp >= reliable_floor]
    if len(reliable_peaks) >= 3:
        peaks = reliable_peaks
    peak_times = np.asarray([time for time, _ in peaks], dtype=float)
    peak_amplitudes = np.asarray([amp for _, amp in peaks], dtype=float)
    decay_slope = float(np.polyfit(peak_times, np.log(peak_amplitudes), 1)[0])
    if decay_slope >= 0.0:
        raise ValueError("free response does not show measurable decay")
    half_period_s = float(np.median(np.diff(peak_times)))
    damped_omega = math.pi / max(half_period_s, 1e-12)
    decay_rate = -decay_slope
    zeta = decay_rate / math.sqrt(damped_omega**2 + decay_rate**2)
    ratios = np.log(peak_amplitudes[:-1] / peak_amplitudes[1:])
    spread = float(np.std(ratios, ddof=1)) if len(ratios) > 1 else 0.0
    half_width = max(0.03, 2.0 * spread / max(2.0 * math.pi, 1e-9))
    lower, upper = _bounds(zeta, half_width)
    confidence = 0.84 if len(ratios) >= 4 else 0.72
    flags = [] if len(ratios) >= 4 else ["few_decay_peaks"]

    return CoreFeatureArtifact(
        feature_id="damping_ratio",
        value=max(0.0, zeta),
        lower_bound=max(0.0, lower),
        upper_bound=min(1.0, max(upper, zeta)),
        confidence=confidence,
        units="ratio",
        method="log_decrement_from_free_decay",
        source_experiment=ExperimentPrimitive.FREE_DECAY,
        data_quality_flags=flags,
    )


def estimate_step_features(
    time_s: np.ndarray | list[float],
    input_signal: np.ndarray | list[float],
    output_signal: np.ndarray | list[float],
    cutoff_hz: float | None = None,
) -> list[CoreFeatureArtifact]:
    """Extract static gain and time constant from a bounded step/ramp test."""

    t = _as_array(time_s)
    u = _as_array(input_signal)
    y_raw = _as_array(output_signal)
    if not (t.size == u.size == y_raw.size):
        raise ValueError("time, input, and output arrays must have equal length")
    dt = float(np.median(np.diff(t)))
    if dt <= 0:
        raise ValueError("time must be strictly increasing")
    cutoff = cutoff_hz or max(2.0, 1.0 / max(t[-1] - t[0], dt))
    y = low_pass_filter(y_raw, dt, cutoff)

    n = t.size
    u_span = float(np.ptp(u))
    if u_span < 1e-12:
        raise ValueError("step response has insufficient input change")
    changed_all = np.where(np.abs(u - u[0]) >= 0.1 * u_span)[0]
    detected_step_idx = int(changed_all[0]) if changed_all.size else max(3, n // 10)
    head = max(3, min(detected_step_idx, n // 10))
    tail = max(3, n // 5)
    u0 = float(np.median(u[:head]))
    u1 = float(np.median(u[-tail:]))
    y0 = float(np.median(y[:head]))
    y1 = float(np.median(y[-tail:]))
    du = u1 - u0
    dy = y1 - y0
    if abs(du) < 1e-12 or abs(dy) < 1e-12:
        raise ValueError("step response has insufficient input or output change")

    input_threshold = u0 + 0.1 * du
    if du >= 0:
        changed = np.where(u >= input_threshold)[0]
    else:
        changed = np.where(u <= input_threshold)[0]
    step_idx = int(changed[0]) if changed.size else detected_step_idx
    step_time = float(t[step_idx])

    target = y0 + 0.6321205588 * dy
    if dy >= 0:
        crossed = np.where(y[step_idx:] >= target)[0]
    else:
        crossed = np.where(y[step_idx:] <= target)[0]
    tau = (
        float(t[step_idx + int(crossed[0])] - step_time)
        if crossed.size
        else float(t[-1] - step_time)
    )
    gain = dy / du

    steady = steady_state_detected(y, window=min(40, max(5, n // 8)))
    gain_width = max(0.05 * abs(gain), 1e-6)
    tau_width = max(0.10 * abs(tau), dt)
    gain_bounds = _bounds(gain, gain_width)
    tau_bounds = _bounds(tau, tau_width)
    confidence = 0.86 if steady else 0.68
    flags = [] if steady else ["steady_state_not_fully_confirmed"]

    return [
        CoreFeatureArtifact(
            feature_id="static_gain",
            value=gain,
            lower_bound=gain_bounds[0],
            upper_bound=gain_bounds[1],
            confidence=confidence,
            units="output/input",
            method="low_pass_steady_state_detector",
            source_experiment=ExperimentPrimitive.RAMP_STEP,
            data_quality_flags=flags,
        ),
        CoreFeatureArtifact(
            feature_id="time_constant",
            value=max(0.0, tau),
            lower_bound=max(0.0, tau_bounds[0]),
            upper_bound=tau_bounds[1],
            confidence=confidence,
            units="s",
            method="low_pass_steady_state_detector",
            source_experiment=ExperimentPrimitive.RAMP_STEP,
            data_quality_flags=flags,
        ),
    ]


def estimate_dead_time(
    time_s: np.ndarray | list[float],
    input_signal: np.ndarray | list[float],
    output_signal: np.ndarray | list[float],
) -> CoreFeatureArtifact:
    t = _as_array(time_s)
    u = _as_array(input_signal)
    y = _as_array(output_signal)
    if not (t.size == u.size == y.size):
        raise ValueError("time, input, and output arrays must have equal length")
    n = t.size
    u_span = float(np.ptp(u))
    if u_span < 1e-12:
        raise ValueError("insufficient input change for dead-time extraction")
    changed_all = np.where(np.abs(u - u[0]) >= 0.1 * u_span)[0]
    detected_step_idx = int(changed_all[0]) if changed_all.size else max(3, n // 10)
    head = max(3, min(detected_step_idx, n // 10))
    tail = max(3, n // 5)
    u0 = float(np.median(u[:head]))
    u1 = float(np.median(u[-tail:]))
    y0 = float(np.median(y[:head]))
    y1 = float(np.median(y[-tail:]))
    du = u1 - u0
    dy = y1 - y0
    if abs(du) < 1e-12 or abs(dy) < 1e-12:
        raise ValueError("insufficient change for dead-time extraction")
    input_threshold = u0 + 0.1 * du
    output_threshold = y0 + 0.05 * dy
    input_idx = (
        np.where(u >= input_threshold)[0]
        if du >= 0
        else np.where(u <= input_threshold)[0]
    )
    output_idx = (
        np.where(y >= output_threshold)[0]
        if dy >= 0
        else np.where(y <= output_threshold)[0]
    )
    start = int(input_idx[0]) if input_idx.size else head
    response = int(output_idx[0]) if output_idx.size else start
    dead_time = max(0.0, float(t[response] - t[start]))
    dt = float(np.median(np.diff(t)))
    lower, upper = _bounds(dead_time, max(2.0 * dt, 0.1 * dead_time))
    return CoreFeatureArtifact(
        feature_id="dead_time",
        value=dead_time,
        lower_bound=max(0.0, lower),
        upper_bound=upper,
        confidence=0.74,
        units="s",
        method="threshold_delay_detector",
        source_experiment=ExperimentPrimitive.RAMP_STEP,
        data_quality_flags=[],
    )


def estimate_inverse_response_severity(
    time_s: np.ndarray | list[float],
    output_signal: np.ndarray | list[float],
) -> CoreFeatureArtifact:
    t = _as_array(time_s)
    y = _as_array(output_signal)
    if t.size != y.size:
        raise ValueError("time and output arrays must have equal length")
    head = max(3, t.size // 10)
    tail = max(3, t.size // 5)
    y0 = float(np.median(y[:head]))
    y1 = float(np.median(y[-tail:]))
    dy = y1 - y0
    if abs(dy) < 1e-12:
        raise ValueError("output change too small for inverse-response severity")
    if dy >= 0:
        reverse = max(0.0, y0 - float(np.min(y)))
    else:
        reverse = max(0.0, float(np.max(y)) - y0)
    severity = reverse / abs(dy)
    lower, upper = _bounds(severity, max(0.05 * severity, 0.01))
    return CoreFeatureArtifact(
        feature_id="inverse_response_severity",
        value=severity,
        lower_bound=max(0.0, lower),
        upper_bound=upper,
        confidence=0.78,
        units="fraction",
        method="initial_reverse_motion_ratio",
        source_experiment=ExperimentPrimitive.RAMP_STEP,
        data_quality_flags=[],
    )


def _pulse_segments(input_signal: np.ndarray) -> list[np.ndarray]:
    threshold = 0.2 * float(np.max(np.abs(input_signal)))
    if threshold <= 0:
        raise ValueError("pulse input is zero")
    active = np.abs(input_signal) >= threshold
    indices = np.where(active)[0]
    if indices.size == 0:
        raise ValueError("no pulse segment found")
    breaks = np.where(np.diff(indices) > 1)[0]
    starts = np.r_[0, breaks + 1]
    ends = np.r_[breaks, indices.size - 1]
    return [indices[start : end + 1] for start, end in zip(starts, ends)]


def estimate_pulse_input_gain(
    time_s: np.ndarray | list[float],
    input_signal: np.ndarray | list[float],
    acceleration_signal: np.ndarray | list[float],
    feature_id: str = "input_gain",
    units: str = "acceleration/input",
) -> CoreFeatureArtifact:
    """Estimate input or torque gain by integrating pulse response."""

    t = _as_array(time_s)
    u = _as_array(input_signal)
    a_raw = _as_array(acceleration_signal)
    if not (t.size == u.size == a_raw.size):
        raise ValueError("time, input, and acceleration arrays must have equal length")
    baseline = float(np.median(a_raw[: max(3, t.size // 10)]))
    a = a_raw - baseline
    segments = _pulse_segments(u)
    ratios: list[float] = []
    for segment in segments:
        if segment.size < 2:
            continue
        impulse = _integrate(u[segment], t[segment])
        response = _integrate(a[segment], t[segment])
        if abs(impulse) > 1e-12:
            ratios.append(response / impulse)
    if not ratios:
        raise ValueError("pulse integral is too small")
    gain = float(np.mean(ratios))
    spread = (
        float(np.std(ratios, ddof=1))
        if len(ratios) > 1
        else max(0.05 * abs(gain), 1e-6)
    )
    half_width = max(2.0 * spread, 0.05 * abs(gain), 1e-6)
    lower, upper = _bounds(gain, half_width)
    confidence = 0.9 if len(ratios) > 1 else 0.76
    flags = [] if len(ratios) > 1 else ["single_pulse_only"]

    return CoreFeatureArtifact(
        feature_id=feature_id,
        value=gain,
        lower_bound=lower,
        upper_bound=upper,
        confidence=confidence,
        units=units,
        method="pulse_integration",
        source_experiment=ExperimentPrimitive.PULSE,
        data_quality_flags=flags,
    )


def estimate_hover_thrust(
    time_s: np.ndarray | list[float],
    thrust_command: np.ndarray | list[float],
    lift_signal: np.ndarray | list[float] | None = None,
    cutoff_hz: float = 2.0,
) -> CoreFeatureArtifact:
    """Extract hover thrust from a slow lift-threshold ramp."""

    t = _as_array(time_s)
    thrust = _as_array(thrust_command)
    if t.size != thrust.size:
        raise ValueError("time and thrust arrays must have equal length")
    dt = float(np.median(np.diff(t)))
    smooth = low_pass_filter(thrust, dt, cutoff_hz)
    if lift_signal is not None:
        lift = _as_array(lift_signal)
        if lift.size != t.size:
            raise ValueError("lift signal must match time array")
        threshold = float(
            np.median(lift[: max(3, lift.size // 10)])
            + 0.5 * (np.max(lift) - np.min(lift))
        )
        crossing = np.where(lift >= threshold)[0]
        idx = int(crossing[0]) if crossing.size else int(0.8 * t.size)
        hover = float(thrust[idx])
        flags = [] if crossing.size else ["lift_threshold_not_detected"]
    else:
        hover = float(np.median(smooth[-max(3, t.size // 5) :]))
        flags = ["no_lift_signal_used"]

    half_width = max(0.05 * abs(hover), 1e-6)
    lower, upper = _bounds(hover, half_width)
    return CoreFeatureArtifact(
        feature_id="hover_thrust",
        value=hover,
        lower_bound=lower,
        upper_bound=upper,
        confidence=0.86 if not flags else 0.72,
        units="input_units",
        method="liftoff_threshold_command",
        source_experiment=ExperimentPrimitive.HOVER_THRUST,
        data_quality_flags=flags,
    )


def estimate_coupling_gain(
    time_s: np.ndarray | list[float],
    input_signal: np.ndarray | list[float],
    primary_output_signal: np.ndarray | list[float],
    coupled_output_signal: np.ndarray | list[float] | None = None,
    feature_id: str = "coupling_gain",
    units: str = "fraction",
    source_experiment: ExperimentPrimitive = ExperimentPrimitive.BOUNDED_SCAN,
) -> CoreFeatureArtifact:
    """Estimate a conservative scalar coupling indicator from a bounded scan."""

    t = _as_array(time_s)
    u = _as_array(input_signal)
    primary = _as_array(primary_output_signal)
    if not (t.size == u.size == primary.size):
        raise ValueError(
            "time, input, and primary output arrays must have equal length"
        )
    if float(np.ptp(u)) < 1e-12 or float(np.ptp(primary)) < 1e-12:
        raise ValueError("bounded scan has insufficient input or primary-output motion")

    if coupled_output_signal is None:
        value = float(np.ptp(primary) / max(abs(float(np.ptp(u))), 1e-12))
        width = max(0.1 * abs(value), 1e-6)
        method = "bounded_scan_primary_response"
        confidence = 0.64
        flags = ["no_separate_coupled_output"]
    else:
        coupled = _as_array(coupled_output_signal)
        if coupled.size != t.size:
            raise ValueError("coupled output array must match time array")
        value = float(np.ptp(coupled) / max(float(np.ptp(primary)), 1e-12))
        width = max(0.1 * abs(value), 1e-6)
        method = "bounded_scan_cross_response_ratio"
        confidence = 0.78
        flags = []

    lower, upper = _bounds(value, width)
    return CoreFeatureArtifact(
        feature_id=feature_id,
        value=value,
        lower_bound=lower,
        upper_bound=upper,
        confidence=confidence,
        units=units,
        method=method,
        source_experiment=source_experiment,
        data_quality_flags=flags,
    )


def estimate_signal_ratio_feature(
    time_s: np.ndarray | list[float],
    numerator_signal: np.ndarray | list[float],
    denominator_signal: np.ndarray | list[float],
    feature_id: str,
    units: str,
    method: str,
    source_experiment: ExperimentPrimitive,
) -> CoreFeatureArtifact:
    """Estimate a scalar feature as a robust ratio between two recorded signals."""

    t = _as_array(time_s)
    numerator = _as_array(numerator_signal)
    denominator = _as_array(denominator_signal)
    if not (t.size == numerator.size == denominator.size):
        raise ValueError(
            "time, numerator, and denominator arrays must have equal length"
        )

    head = max(3, t.size // 10)
    num = numerator - float(np.median(numerator[:head]))
    den = denominator - float(np.median(denominator[:head]))
    den_span = float(np.ptp(den))
    if den_span < 1e-12:
        raise ValueError("denominator signal has insufficient motion")
    active = np.abs(den) >= 0.1 * den_span
    if int(np.sum(active)) < 3:
        active = np.ones_like(den, dtype=bool)
    denom_power = float(np.dot(den[active], den[active]))
    if denom_power < 1e-12:
        raise ValueError("denominator signal is too small for ratio extraction")

    value = float(np.dot(den[active], num[active]) / denom_power)
    residual = num[active] - value * den[active]
    residual_scale = float(np.sqrt(np.mean(residual**2))) if residual.size else 0.0
    denominator_scale = max(float(np.sqrt(np.mean(den[active] ** 2))), 1e-12)
    half_width = max(0.05 * abs(value), residual_scale / denominator_scale, 1e-6)
    lower, upper = _bounds(value, half_width)
    relative_residual = residual_scale / max(
        float(np.sqrt(np.mean(num[active] ** 2))), 1e-12
    )
    confidence = max(0.5, min(0.9, 0.9 - 0.25 * relative_residual))
    flags = [] if relative_residual < 0.25 else ["large_ratio_residual"]

    return CoreFeatureArtifact(
        feature_id=feature_id,
        value=value,
        lower_bound=lower,
        upper_bound=upper,
        confidence=confidence,
        units=units,
        method=method,
        source_experiment=source_experiment,
        data_quality_flags=flags,
    )
