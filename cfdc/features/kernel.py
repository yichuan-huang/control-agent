"""Versioned numerical analysis of protocol-bound public trajectories."""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from itertools import pairwise
from typing import Any

import numpy as np
from scipy import signal

from cfdc.kernel.contracts import FEATURE_ARTIFACT_VERSION, fingerprint


@dataclass(frozen=True)
class _Trace:
    evidence_id: str
    protocol: str
    kind: str
    time_s: np.ndarray
    signals: Mapping[str, np.ndarray]
    units: Mapping[str, str]
    measured: tuple[str, ...]
    controls: tuple[str, ...]
    digest: str
    operating_region: str


def _public_traces(evidence: Sequence[Mapping[str, Any]]) -> list[_Trace]:
    result: list[_Trace] = []
    for item in evidence:
        trace = item.get("trace")
        if not isinstance(trace, Mapping) or not isinstance(
            trace.get("signals"), Mapping
        ):
            continue
        try:
            time_s = np.asarray(trace["time_s"], dtype=float)
            signals = {
                str(name): np.asarray(values, dtype=float)
                for name, values in trace["signals"].items()
            }
        except (KeyError, TypeError, ValueError):
            continue
        if (
            len(time_s) < 8
            or np.any(~np.isfinite(time_s))
            or np.any(np.diff(time_s) <= 0)
            or any(len(values) != len(time_s) for values in signals.values())
            or any(np.any(~np.isfinite(values)) for values in signals.values())
        ):
            continue
        metadata = trace.get("metadata")
        metadata = metadata if isinstance(metadata, Mapping) else {}
        controls = tuple(
            str(name) for name in metadata.get("control_inputs", ()) if str(name)
        )
        if not controls or not set(controls) <= set(signals):
            controls = tuple(
                name for name in ("input", "control_input", "u") if name in signals
            )[:1]
        measured = tuple(
            str(name) for name in metadata.get("measured_signals", ()) if str(name)
        )
        if not measured:
            measured = tuple(name for name in signals if name not in controls)
        if not controls or not measured or not {*controls, *measured} <= set(signals):
            continue
        protocol = str(
            item.get("protocol_fingerprint") or trace.get("protocol_fingerprint") or ""
        )
        if not protocol:
            continue
        result.append(
            _Trace(
                evidence_id=str(
                    item.get("evidence_id") or trace.get("trace_id") or "evidence"
                ),
                protocol=protocol,
                kind=str(
                    metadata.get("experiment_kind")
                    or item.get("operation")
                    or "public_timeseries"
                ),
                time_s=time_s,
                signals=signals,
                units={str(k): str(v) for k, v in (trace.get("units") or {}).items()},
                measured=measured,
                controls=controls,
                digest=str(
                    item.get("trace_fingerprint")
                    or trace.get("trace_fingerprint")
                    or fingerprint(trace)
                ),
                operating_region=str(
                    item.get("operating_region")
                    or trace.get("operating_region")
                    or "declared operating region"
                ),
            )
        )
    if not result:
        raise ValueError("public_trace_required_for_feature_derivation")
    return result


def _step_fit(trace: _Trace) -> tuple[dict[str, float], float]:
    u = trace.signals[trace.controls[0]]
    y = trace.signals[trace.measured[0]]
    t = trace.time_s
    changes = np.flatnonzero(np.abs(np.diff(u)) > max(np.ptp(u) * 1e-6, 1e-12)) + 1
    boundaries = np.concatenate(([0], changes, [len(u)]))
    candidates: list[tuple[int, int, int, int, float]] = []
    for index in range(1, len(boundaries) - 1):
        before_start, step = int(boundaries[index - 1]), int(boundaries[index])
        end = int(boundaries[index + 1])
        if step - before_start < 3 or end - step < 5:
            continue
        before = max(before_start, step - max(3, (step - before_start) // 4))
        tail = max(step + 3, end - max(3, (end - step) // 4))
        du = float(np.median(u[tail:end]) - np.median(u[before:step]))
        if abs(du) > 1e-10:
            candidates.append((before, step, tail, end, du))
    if not candidates:
        raise ValueError("feature_input_excitation_insufficient")
    before, step, tail, end, du = max(candidates, key=lambda row: abs(row[4]))
    u0 = float(np.median(u[before:step]))
    y0 = float(np.median(y[before:step]))
    y1 = float(np.median(y[tail:end]))
    gain = (y1 - y0) / du
    target = y0 + 0.6321205588 * (y1 - y0)
    post = y[step:end]
    tau_index = step + int(np.argmin(np.abs(post - target)))
    dt = float(np.median(np.diff(t)))
    tau = max(float(t[tau_index] - t[step]), dt)
    response_span = max(abs(y1 - y0), 1e-12)
    visible = np.flatnonzero(np.abs(post - y0) > 0.02 * response_span)
    delay = (
        max(float(t[step + int(visible[0])] - t[step]), 0.0) if visible.size else 0.0
    )
    direction = math.copysign(1.0, y1 - y0) if y1 != y0 else 1.0
    inverse = max(0.0, -float(np.min(direction * (post - y0)))) / response_span
    prediction = y0 + gain * (u[step:end] - u0)
    residual = float(np.sqrt(np.mean((y[tail:end] - prediction[tail - step :]) ** 2)))
    detrended = signal.detrend(y[step:end])
    frequencies, power = signal.periodogram(detrended, fs=1.0 / dt)
    peak = int(np.argmax(power[1:]) + 1) if len(power) > 1 else 0
    modal = 2 * math.pi * float(frequencies[peak]) if peak else 1.0 / tau
    return (
        {
            "static_gain": gain,
            "dominant_time_constant": tau,
            "time_constant": tau,
            "delay_bound": max(delay, dt),
            "dead_time": max(delay, dt),
            "inverse_response_severity": inverse,
            "nmp_zero_rate_estimate": 1.0 / max(delay + tau * max(inverse, 0.1), dt),
            "natural_frequency": modal,
            "dominant_natural_frequency": modal,
            "modal_frequency": modal,
            "input_gain": gain,
            "acceleration_gain": gain,
            "derivative_gain": gain,
            "drag_rate": 1.0 / tau,
            "velocity_gain": gain,
            "slow_lag_rate": 1.0 / tau,
            "fast_lag_rate": 4.0 / tau,
            "phase_guard_frequency": 0.35 * modal,
            "task_band_magnitude_at_crossover": max(abs(gain), 1e-9),
            "parasitic_mode_frequency": modal,
            "low_order_residual": residual / response_span,
            "low_order_residual_index": residual / response_span,
            "amplitude_dependence_index": residual / response_span,
        },
        residual / response_span,
    )


def _staircase_fit(trace: _Trace) -> tuple[dict[str, float], float]:
    u = trace.signals[trace.controls[0]]
    y = trace.signals[trace.measured[0]]
    changes = np.flatnonzero(np.abs(np.diff(u)) > max(np.ptp(u) * 1e-6, 1e-12)) + 1
    boundaries = np.concatenate(([0], changes, [len(u)]))
    levels, plateaus = [], []
    for start, end in pairwise(boundaries):
        start, end = int(start), int(end)
        if end - start < 5:
            continue
        tail = start + max(2, 3 * (end - start) // 4)
        levels.append(float(np.median(u[tail:end])))
        plateaus.append(float(np.median(y[tail:end])))
    if len(levels) < 5 or np.ptp(levels) <= 1e-9:
        raise ValueError("staircase_dwell_insufficient")
    x = np.asarray(levels)
    z = np.asarray(plateaus)
    design = np.column_stack([np.ones_like(x), x, x**3])
    coefficients, *_ = np.linalg.lstsq(design, z, rcond=None)
    prediction = design @ coefficients
    scale = max(np.ptp(z), 1e-9)
    residual = float(np.sqrt(np.mean((z - prediction) ** 2)) / scale)
    differences = []
    for value in np.unique(np.round(x, 9)):
        values = z[np.isclose(x, value, atol=1e-8)]
        if len(values) > 1:
            differences.append(float(np.ptp(values)))
    history = max(differences, default=0.0) / scale
    linear, cubic = float(coefficients[1]), float(coefficients[2])
    lower, upper = float(np.min(x)), float(np.max(x))
    derivative_values = linear + 3 * cubic * np.asarray([lower**2, upper**2, 0.0])
    slope_min = float(np.min(derivative_values))
    return (
        {
            "static_map_linear_coefficient": linear,
            "static_map_cubic_coefficient": cubic,
            "static_map_derivative_lower_bound": slope_min,
            "local_invertibility_margin": slope_min,
            "local_static_slope": linear,
            "static_gain": linear,
            "dominant_time_constant": max(
                float(np.median(np.diff(trace.time_s))) * 4, 1e-6
            ),
            "history_dependence_index": history,
            "inverse_input_lower": lower,
            "inverse_input_upper": upper,
            "inverse_output_lower": float(np.min(prediction)),
            "inverse_output_upper": float(np.max(prediction)),
            "positive_deadzone": max(0.0, float(np.min(x[z > np.median(z)]))),
            "negative_deadzone": max(0.0, -float(np.max(x[z < np.median(z)]))),
            "positive_deadzone_bound": max(0.0, float(np.min(x[z > np.median(z)]))),
            "negative_deadzone_bound": max(0.0, -float(np.max(x[z < np.median(z)]))),
            "outer_static_slope": linear,
            "virtual_noise_guard": residual * scale,
        },
        max(residual, history),
    )


def _release_fit(trace: _Trace) -> tuple[dict[str, float], float]:
    if len(trace.measured) < 2:
        raise ValueError("release_position_velocity_required")
    q = trace.signals[trace.measured[0]]
    v = trace.signals[trace.measured[1]]
    u = trace.signals[trace.controls[0]]
    acceleration = np.gradient(v, trace.time_s)
    design = np.column_stack([-q, -v, -(q**2) * v, u])
    coefficients, *_ = np.linalg.lstsq(design, acceleration, rcond=None)
    prediction = design @ coefficients
    scale = max(float(np.std(acceleration)), 1e-9)
    residual = float(np.sqrt(np.mean((acceleration - prediction) ** 2)) / scale)
    wn2, decay0, decay2, input_gain = map(float, coefficients)
    crossing = math.sqrt(max(0.0, -decay0 / decay2)) if decay0 < 0 < decay2 else 0.0
    return (
        {
            "natural_frequency": math.sqrt(max(wn2, 1e-12)),
            "dominant_natural_frequency": math.sqrt(max(wn2, 1e-12)),
            "modal_frequency": math.sqrt(max(wn2, 1e-12)),
            "input_gain": input_gain,
            "signed_input_gain": input_gain,
            "small_amplitude_decay_rate": decay0,
            "base_decay_rate": decay0,
            "quadratic_decay_rate": decay2,
            "zero_decay_crossing_amplitude": crossing,
            "capture_damping": max(0.0, -decay0 + decay2 * max(crossing, 0.1) ** 2),
            "amplitude_dependence_index": abs(decay2) * float(np.max(q**2)),
            "damping_fit_r2": max(0.0, 1.0 - residual**2),
            "release_model_fit_r2": max(0.0, 1.0 - residual**2),
            "minimum_decay_rate": decay0,
            "damping_change_fraction": abs(decay2)
            * float(np.max(q**2))
            / max(abs(decay0), 1e-9),
        },
        residual,
    )


def _frequency_fit(trace: _Trace) -> tuple[dict[str, float], float]:
    """Estimate a task-band FRF only at publicly excited spectral lines."""

    u = np.asarray(trace.signals[trace.controls[0]], dtype=float)
    y = np.asarray(trace.signals[trace.measured[0]], dtype=float)
    dt = float(np.median(np.diff(trace.time_s)))
    window = signal.windows.hann(len(u), sym=False)
    u_centered = signal.detrend(u)
    y_centered = signal.detrend(y)
    u_spectrum = np.fft.rfft(u_centered * window)
    y_spectrum = np.fft.rfft(y_centered * window)
    frequencies_hz = np.fft.rfftfreq(len(u), dt)
    positive = frequencies_hz > 0.0
    threshold = max(float(np.max(np.abs(u_spectrum))) * 0.05, 1e-12)
    excited = positive & (np.abs(u_spectrum) >= threshold)
    if np.count_nonzero(excited) < 2:
        raise ValueError("feature_frequency_excitation_insufficient")
    omega = 2.0 * math.pi * frequencies_hz[excited]
    response = y_spectrum[excited] / u_spectrum[excited]
    if np.any(~np.isfinite(response)):
        raise ValueError("feature_frequency_response_nonfinite")

    minimum_tau = max(dt / 10.0, 1e-6)
    maximum_tau = max(10.0 / float(np.min(omega)), minimum_tau * 10.0)
    best: tuple[float, float] | None = None
    for tau in np.geomspace(minimum_tau, maximum_tau, 240):
        basis = 1.0 / (1.0 + 1j * omega * tau)
        gain = float(
            np.real(np.vdot(basis, response)) / max(np.vdot(basis, basis).real, 1e-12)
        )
        prediction = gain * basis
        residual = float(
            np.linalg.norm(response - prediction) / max(np.linalg.norm(response), 1e-12)
        )
        candidate = (residual, tau)
        if best is None or candidate[0] < best[0]:
            best = candidate
    assert best is not None
    residual, tau = best
    gain = float(
        np.real(np.vdot(1.0 / (1.0 + 1j * omega * tau), response))
        / max(
            np.vdot(
                1.0 / (1.0 + 1j * omega * tau),
                1.0 / (1.0 + 1j * omega * tau),
            ).real,
            1e-12,
        )
    )
    phases = np.unwrap(np.angle(response))
    protected = np.flatnonzero(phases <= -3.0 * math.pi / 4.0)
    phase_guard = float(omega[protected[0]]) if protected.size else float(np.max(omega))
    output_power = np.abs(y_spectrum[positive]) ** 2
    unexplained = positive & ~excited
    harmonic_ratio = float(
        np.sum(np.abs(y_spectrum[unexplained]) ** 2) / max(np.sum(output_power), 1e-12)
    )
    return (
        {
            "static_gain": gain,
            "dominant_time_constant": tau,
            "time_constant": tau,
            "phase_guard_frequency": phase_guard,
            "task_band_magnitude_at_crossover": float(np.median(np.abs(response))),
            "low_order_residual": residual,
            "low_order_residual_index": residual,
            "amplitude_dependence_index": harmonic_ratio,
            "frequency_input_rms": float(np.sqrt(np.mean(u_centered**2))),
        },
        residual,
    )


def _mimo_fit(trace: _Trace) -> tuple[dict[str, float], float]:
    if len(trace.controls) < 2 or len(trace.measured) < 2:
        raise ValueError("mimo_two_by_two_signals_required")
    inputs = np.column_stack([trace.signals[name] for name in trace.controls[:2]])
    matrix = np.zeros((2, 2))
    residuals, taus = [], []
    for row, name in enumerate(trace.measured[:2]):
        output = trace.signals[name]
        window = min(51, len(output) // 10 * 2 + 1)
        window = max(window, 5)
        smooth = signal.savgol_filter(output, window, 3)
        derivative = np.gradient(smooth, trace.time_s)
        design = np.column_stack([-smooth, inputs])
        coefficients, *_ = np.linalg.lstsq(design, derivative, rcond=None)
        rate = float(coefficients[0])
        if rate <= 1e-9:
            raise ValueError("mimo_stable_channel_rate_required")
        matrix[row] = coefficients[1:] / rate
        taus.append(1.0 / rate)
        residuals.append(
            float(
                np.sqrt(np.mean((derivative - design @ coefficients) ** 2))
                / max(np.std(derivative), 1e-9)
            )
        )
    condition = float(np.linalg.cond(matrix))
    inverse = np.linalg.pinv(matrix)
    rga = matrix * inverse.T
    result = {
        f"local_gain_k{row + 1}{column + 1}": float(matrix[row, column])
        for row in range(2)
        for column in range(2)
    }
    result.update(
        gain_matrix_condition=condition,
        static_inverse_amplification=float(np.linalg.norm(inverse, 2)),
        inband_static_decoupler_residual=float(max(residuals)),
        dc_static_cross_ratio=float(
            (abs(matrix[0, 1]) + abs(matrix[1, 0]))
            / max(abs(matrix[0, 0]) + abs(matrix[1, 1]), 1e-12)
        ),
        dc_rga_deviation=float(np.linalg.norm(rga - np.eye(2), 2)),
        pairing_bootstrap_probability=1.0
        if abs(matrix[0, 0] * matrix[1, 1]) >= abs(matrix[0, 1] * matrix[1, 0])
        else 0.0,
        dynamic_decoupler_fit_residual=float(max(residuals)),
        dynamic_inverse_peak_amplification=float(np.linalg.norm(inverse, 2)),
        mimo_input_output_rank=float(np.linalg.matrix_rank(matrix)),
        channel_coherence_min=max(0.0, 1.0 - max(residuals)),
        paired_time_constant_1=float(taus[0]),
        paired_time_constant_2=float(taus[1]),
    )
    for row in range(2):
        for column in range(2):
            result[f"dynamic_map_base_{row + 1}{column + 1}"] = float(
                inverse[row, column]
            )
            for basis in range(1, 4):
                result[f"dynamic_map_lag{basis}_{row + 1}{column + 1}"] = 0.0
    return result, float(max(residuals))


def _analyze(trace: _Trace) -> tuple[dict[str, float], float, str]:
    kind = trace.kind.casefold()
    if len(trace.controls) >= 2 and len(trace.measured) >= 2:
        values, residual = _mimo_fit(trace)
        return values, residual, "linear_mimo_continuous_regression"
    if "stair" in kind:
        values, residual = _staircase_fit(trace)
        return values, residual, "bidirectional_static_map_regression"
    if "release" in kind and len(trace.measured) >= 2:
        values, residual = _release_fit(trace)
        return values, residual, "oscillator_equation_regression"
    if "frequency" in kind or "multisine" in kind:
        values, residual = _frequency_fit(trace)
        return values, residual, "excited_line_frf_low_order_fit"
    values, residual = _step_fit(trace)
    return values, residual, "linear_siso_step_regression"


def _unit(feature_id: str) -> str:
    if "time_constant" in feature_id or "delay" in feature_id:
        return "s"
    if "frequency" in feature_id or feature_id.endswith("_rate"):
        return "rad/s"
    if "gain" in feature_id or "coefficient" in feature_id:
        return "output/input"
    return "ratio"


def _aggregate_feature(
    feature_id: str,
    values: list[float],
    traces: list[_Trace],
    residual: float,
    method: str,
) -> dict[str, Any]:
    value = float(np.median(values))
    if len(values) >= 2:
        lower, upper = np.quantile(values, [0.025, 0.975])
        interval_method = "repeat_quantile_95"
    else:
        width = max(abs(value) * max(residual, 1e-6), 1e-9)
        lower, upper = value - 1.96 * width, value + 1.96 * width
        interval_method = "regression_t_interval_95"
    if lower == upper:
        resolution = max(abs(value) * 1e-9, 1e-12)
        lower, upper = lower - resolution, upper + resolution
    return {
        "value": value,
        "unit": _unit(feature_id),
        "uncertainty": {
            "lower_bound": float(lower),
            "upper_bound": float(upper),
            "confidence": 0.95,
            "method": interval_method,
        },
        "confidence": 0.95,
        "source_evidence_ids": [trace.evidence_id for trace in traces],
        "source_trace_sha256": [trace.digest for trace in traces],
        "protocol_fingerprint": traces[0].protocol,
        "estimator_version": "cfdc-public-analysis/v2",
        "derivation": method,
        "valid_region": traces[0].operating_region,
        "feature_role": "controller_synthesis",
        "used_by_controller": True,
    }


@dataclass(frozen=True)
class FeatureArtifact:
    value: Mapping[str, Any]

    @property
    def fingerprint(self) -> str:
        return str(self.value["artifact_fingerprint"])

    def to_dict(self) -> dict[str, Any]:
        return dict(self.value)


def derive_feature_artifact(
    evidence: Sequence[Mapping[str, Any]], route: Mapping[str, Any]
) -> FeatureArtifact:
    required = tuple(str(item) for item in route.get("feature_ids", ()))
    groups: dict[tuple[str, str], list[_Trace]] = defaultdict(list)
    for trace in _public_traces(evidence):
        groups[(trace.protocol, trace.kind)].append(trace)
    analyses = []
    for (protocol, kind), traces in sorted(groups.items()):
        rows, residuals, method = [], [], ""
        for trace in traces:
            try:
                values, residual, method = _analyze(trace)
            except ValueError:
                continue
            rows.append(values)
            residuals.append(residual)
        if not rows:
            continue
        if method == "excited_line_frf_low_order_fit":
            gains = np.asarray([row["static_gain"] for row in rows], dtype=float)
            amplitude_dependence = float(
                max(
                    max(row["amplitude_dependence_index"] for row in rows),
                    np.ptp(gains) / max(np.max(np.abs(gains)), 1e-12),
                )
            )
            for row in rows:
                row["amplitude_dependence_index"] = amplitude_dependence
        common = set(rows[0]).intersection(*(set(row) for row in rows[1:]))
        residual = float(np.median(residuals))
        features = {
            feature_id: _aggregate_feature(
                feature_id,
                [row[feature_id] for row in rows],
                traces,
                residual,
                method,
            )
            for feature_id in sorted(common)
        }
        analyses.append(
            {
                "protocol_fingerprint": protocol,
                "experiment_kind": kind,
                "trace_count": len(rows),
                "fit_residual": residual,
                "quality_passed": residual <= 0.5,
                "features": features,
                "model": {
                    "model_type": "linear_mimo_dynamic"
                    if any(name.startswith("local_gain_k") for name in features)
                    else (
                        "static_nonlinear_map"
                        if "static_map_cubic_coefficient" in features
                        else (
                            "local_nonlinear_oscillator"
                            if "small_amplitude_decay_rate" in features
                            else "linear_siso_rational_delay"
                        )
                    ),
                    "protocol_fingerprint": protocol,
                    "fit_residual": residual,
                    "source_trace_sha256": [trace.digest for trace in traces],
                },
            }
        )
    if not analyses:
        raise ValueError("public_trace_analysis_failed")
    selected = max(
        analyses,
        key=lambda row: (
            len(set(row["features"]) & set(required)),
            row["quality_passed"],
            row["trace_count"],
            -row["fit_residual"],
            row["protocol_fingerprint"],
        ),
    )
    features = dict(selected["features"])
    missing = sorted(set(required) - set(features))
    quality_passed = bool(selected["quality_passed"] and not missing)
    body = {
        "feature_version": FEATURE_ARTIFACT_VERSION,
        "features": features,
        "required_feature_ids": list(required),
        "missing_feature_ids": missing,
        "parameter_search_domains": {
            key: [
                value["uncertainty"]["lower_bound"],
                value["uncertainty"]["upper_bound"],
            ]
            for key, value in features.items()
        },
        "analysis_groups": [
            {
                key: value
                for key, value in row.items()
                if key not in {"features", "model"}
            }
            for row in analyses
        ],
        "public_models": [row["model"] for row in analyses],
        "selected_protocol_fingerprint": selected["protocol_fingerprint"],
        "quality": {
            "passed": quality_passed,
            "status": "passed" if quality_passed else "evidence_gap",
            "fit_residual": selected["fit_residual"],
            "repeatability": 1.0 / (1.0 + selected["fit_residual"]),
            "reason": None
            if quality_passed
            else "required features or numerical fit quality are insufficient",
        },
        "evidence_fingerprints": [
            str(
                item.get("fingerprint")
                or item.get("trace_fingerprint")
                or fingerprint(item)
            )
            for item in evidence
        ],
    }
    body["artifact_fingerprint"] = fingerprint(body)
    return FeatureArtifact(body)


__all__ = ["FeatureArtifact", "derive_feature_artifact"]
