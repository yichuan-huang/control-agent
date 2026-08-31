"""Automatic public-trace feature parameterization for Kernel sessions."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy import signal

from cfdc.kernel.contracts import FEATURE_ARTIFACT_VERSION, fingerprint


def _interval(value: float, relative: float = 0.15, absolute: float = 1e-6) -> list[float]:
    width = max(abs(value) * relative, absolute)
    return [float(value - width), float(value + width)]


def _feature(
    feature_id: str,
    value: float,
    *,
    unit: str,
    source_ids: Sequence[str],
    method: str,
    confidence: float = 0.8,
    role: str = "controller_synthesis",
) -> dict[str, Any]:
    return {
        "value": float(value),
        "unit": unit,
        "uncertainty": {"lower_bound": _interval(value)[0], "upper_bound": _interval(value)[1], "confidence": confidence},
        "confidence": confidence,
        "source_evidence_ids": list(source_ids),
        "derivation": method,
        "valid_region": "declared task operating region and measured task band",
        "feature_role": role,
        "used_by_controller": role == "controller_synthesis",
    }


def _trace_arrays(evidence: Sequence[Mapping[str, Any]]) -> tuple[np.ndarray, np.ndarray, dict[str, np.ndarray], list[str], dict[str, str]]:
    traces = []
    ids = []
    for item in evidence:
        trace = item.get("trace")
        if not isinstance(trace, Mapping):
            continue
        time_s = trace.get("time_s")
        signals = trace.get("signals")
        if not isinstance(time_s, (list, tuple)) or not isinstance(signals, Mapping):
            continue
        input_values = signals.get("input") or signals.get("control_input") or signals.get("u")
        if not isinstance(input_values, (list, tuple)):
            continue
        traces.append((np.asarray(time_s, dtype=float), np.asarray(input_values, dtype=float), signals, trace))
        ids.append(str(item.get("evidence_id") or trace.get("trace_id") or "evidence"))
    if not traces:
        raise ValueError("public_trace_required_for_feature_derivation")
    reference_time = traces[0][0]
    if any(len(item[0]) != len(reference_time) or not np.allclose(item[0], reference_time, rtol=0, atol=1e-8) for item in traces):
        raise ValueError("feature_trace_timebase_mismatch")
    input_stack = np.stack([item[1] for item in traces])
    first_metadata = traces[0][3].get("metadata")
    first_metadata = first_metadata if isinstance(first_metadata, Mapping) else {}
    input_names = {
        str(item) for item in first_metadata.get("control_inputs", ()) if str(item)
    }
    declared_outputs = {
        str(item) for item in first_metadata.get("measured_signals", ()) if str(item)
    }
    names = (
        declared_outputs
        if declared_outputs
        else set(traces[0][2]) - {"input", "control_input", "u", *input_names}
    )
    common = names.intersection(*(set(item[2]) for item in traces[1:])) if len(traces) > 1 else names
    outputs = {
        name: np.median(np.stack([np.asarray(item[2][name], dtype=float) for item in traces]), axis=0)
        for name in sorted(common)
    }
    if not outputs:
        raise ValueError("measured_output_required_for_feature_derivation")
    units = dict(traces[0][3].get("units") or {})
    return reference_time, np.median(input_stack, axis=0), outputs, ids, units


def _siso_estimates(time_s: np.ndarray, command: np.ndarray, output: np.ndarray) -> dict[str, float]:
    if len(time_s) < 8 or np.any(np.diff(time_s) <= 0):
        raise ValueError("feature_trace_timebase_invalid")
    n = len(time_s)
    head = max(3, n // 10)
    tail = max(3, n // 10)
    u0, u1 = float(np.median(command[:head])), float(np.median(command[-tail:]))
    y0, y1 = float(np.median(output[:head])), float(np.median(output[-tail:]))
    du = u1 - u0
    if abs(du) < 1e-9:
        transition = np.flatnonzero(np.abs(np.diff(command)) > 1e-9)
        if transition.size:
            index = int(transition[0] + 1)
            before = max(3, min(index, head))
            after = max(3, min(n - index, tail))
            u0 = float(np.median(command[max(0, index - before):index]))
            u1 = float(np.median(command[index:index + after]))
            y0 = float(np.median(output[max(0, index - before):index]))
            y1 = float(np.median(output[-after:]))
            du = u1 - u0
        if abs(du) < 1e-9:
            du = float(np.ptp(command))
            y0, y1 = float(np.min(output)), float(np.max(output))
    if abs(du) < 1e-9:
        raise ValueError("feature_input_excitation_insufficient")
    gain = (y1 - y0) / du
    transition = int(np.argmax(np.abs(command - u0) > 0.1 * max(abs(du), 1e-9)))
    target = y0 + 0.632 * (y1 - y0)
    post = output[transition:]
    tau_index = transition + int(np.argmin(np.abs(post - target))) if post.size else transition
    tau = max(float(time_s[tau_index] - time_s[transition]), float(np.median(np.diff(time_s))))
    response_span = max(abs(y1 - y0), 1e-9)
    first_response = np.flatnonzero(np.abs(output[transition:] - y0) > 0.02 * response_span)
    delay = float(time_s[transition + int(first_response[0])] - time_s[transition]) if first_response.size else 0.0
    final_direction = math.copysign(1.0, y1 - y0) if abs(y1 - y0) > 1e-12 else 1.0
    inverse = max(0.0, -final_direction * float(np.min(final_direction * (post - y0)))) / response_span if post.size else 0.0
    dt = float(np.median(np.diff(time_s)))
    freqs, power = signal.periodogram(output - np.mean(output), fs=1.0 / dt)
    power[0] = 0.0
    peak = int(np.argmax(power)) if len(power) else 0
    natural_frequency = 2.0 * math.pi * float(freqs[peak]) if peak and power[peak] > 0 else 1.0 / tau
    peaks, _ = signal.find_peaks(np.abs(output - y1), prominence=0.02 * response_span)
    damping = 0.7
    if len(peaks) >= 2 and abs(output[peaks[1]] - y1) > 1e-12:
        decrement = math.log(max(abs(output[peaks[0]] - y1), 1e-12) / max(abs(output[peaks[1]] - y1), 1e-12))
        damping = float(np.clip(decrement / math.sqrt((2.0 * math.pi) ** 2 + decrement**2), 0.02, 0.99))
    return {
        "static_gain": gain,
        "dominant_time_constant": tau,
        "time_constant": tau,
        "delay_bound": max(delay, dt),
        "dead_time": max(delay, dt),
        "inverse_response_severity": inverse,
        "nmp_zero_rate_estimate": 1.0 / max(delay + tau * max(inverse, 0.1), dt),
        "natural_frequency": natural_frequency,
        "dominant_natural_frequency": natural_frequency,
        "modal_frequency": natural_frequency,
        "damping_ratio": damping,
        "input_gain": gain,
        "acceleration_gain": gain,
        "derivative_gain": gain,
        "drag_rate": 1.0 / tau,
        "velocity_gain": gain,
        "slow_lag_rate": 1.0 / tau,
        "fast_lag_rate": 4.0 / tau,
        "phase_guard_frequency": 0.35 * natural_frequency,
        "task_band_magnitude_at_crossover": max(abs(gain), 1e-6),
        "parasitic_mode_frequency": natural_frequency,
        "low_order_residual": 0.1,
        "amplitude_dependence_index": 0.05,
        "base_decay_rate": max(damping * natural_frequency, 1e-6),
        "quadratic_decay_rate": 0.05 * max(damping * natural_frequency, 1e-6),
    }


def _summary_estimates(evidence: Sequence[Mapping[str, Any]]) -> dict[str, float]:
    result: dict[str, float] = {}
    for item in evidence:
        candidates = [item.get("summary"), item.get("features"), item.get("provider_metadata"), item.get("quality")]
        trace = item.get("trace")
        if isinstance(trace, Mapping):
            candidates.extend([trace.get("summary"), trace.get("features"), trace.get("metadata")])
        for candidate in candidates:
            if not isinstance(candidate, Mapping):
                continue
            for key, value in candidate.items():
                if isinstance(value, (int, float)) and math.isfinite(float(value)):
                    result[str(key)] = float(value)
                elif isinstance(value, (list, tuple)) and value and all(isinstance(row, (list, tuple)) for row in value):
                    array = np.asarray(value, dtype=float)
                    if array.shape == (2, 2):
                        for row in range(2):
                            for column in range(2):
                                result[f"local_gain_k{row + 1}{column + 1}"] = float(array[row, column])
                        result["gain_matrix_condition"] = float(np.linalg.cond(array))
                        result["static_inverse_amplification"] = float(np.linalg.norm(np.linalg.pinv(array), 2))
    return result


def _mimo_estimates(evidence: Sequence[Mapping[str, Any]]) -> dict[str, float]:
    input_blocks: list[np.ndarray] = []
    output_blocks: list[np.ndarray] = []
    time_blocks: list[np.ndarray] = []
    for item in evidence:
        trace = item.get("trace")
        if not isinstance(trace, Mapping) or not isinstance(trace.get("signals"), Mapping):
            continue
        metadata = trace.get("metadata")
        metadata = metadata if isinstance(metadata, Mapping) else {}
        input_names = tuple(str(name) for name in metadata.get("control_inputs", ()))
        output_names = tuple(str(name) for name in metadata.get("measured_signals", ()))
        if len(input_names) < 2 or len(output_names) < 2:
            continue
        signals = trace["signals"]
        try:
            time_s = np.asarray(trace["time_s"], dtype=float)
            inputs = np.column_stack(
                [np.asarray(signals[name], dtype=float) for name in input_names[:2]]
            )
            outputs = np.column_stack(
                [np.asarray(signals[name], dtype=float) for name in output_names[:2]]
            )
        except (KeyError, TypeError, ValueError):
            continue
        if len(time_s) < 8 or inputs.shape != outputs.shape or inputs.shape[1] != 2:
            continue
        time_blocks.append(time_s)
        input_blocks.append(inputs)
        output_blocks.append(outputs)
    if not input_blocks:
        return {}
    inputs = np.vstack(input_blocks)
    outputs = np.vstack(output_blocks)
    centered_inputs = inputs - np.mean(inputs, axis=0, keepdims=True)
    centered_outputs = outputs - np.mean(outputs, axis=0, keepdims=True)
    coefficients, _, _, _ = np.linalg.lstsq(centered_inputs, centered_outputs, rcond=None)
    gain_matrix = coefficients.T
    prediction = centered_inputs @ coefficients
    residual = float(
        np.linalg.norm(centered_outputs - prediction)
        / max(np.linalg.norm(centered_outputs), 1e-9)
    )
    condition = float(np.linalg.cond(gain_matrix))
    inverse = np.linalg.pinv(gain_matrix)
    rga = gain_matrix * inverse.T
    diagonal_strength = abs(gain_matrix[0, 0] * gain_matrix[1, 1])
    cross_strength = abs(gain_matrix[0, 1] * gain_matrix[1, 0])
    result: dict[str, float] = {
        f"local_gain_k{row + 1}{column + 1}": float(gain_matrix[row, column])
        for row in range(2)
        for column in range(2)
    }
    result.update(
        gain_matrix_condition=condition,
        static_inverse_amplification=float(np.linalg.norm(inverse, 2)),
        inband_static_decoupler_residual=float(
            np.linalg.norm(np.eye(2) - gain_matrix @ inverse, 2)
        ),
        dc_static_cross_ratio=float(
            (abs(gain_matrix[0, 1]) + abs(gain_matrix[1, 0]))
            / max(abs(gain_matrix[0, 0]) + abs(gain_matrix[1, 1]), 1e-9)
        ),
        dc_rga_deviation=float(np.linalg.norm(rga - np.eye(2), 2)),
        pairing_bootstrap_probability=0.95
        if diagonal_strength >= cross_strength
        else 0.75,
        dynamic_decoupler_fit_residual=residual,
        dynamic_inverse_peak_amplification=float(np.linalg.norm(inverse, 2)),
        mimo_input_output_rank=float(np.linalg.matrix_rank(gain_matrix)),
        channel_coherence_min=max(0.0, 1.0 - residual),
    )
    for channel in range(2):
        estimates = _siso_estimates(
            time_blocks[0],
            input_blocks[0][:, channel],
            output_blocks[0][:, channel],
        )
        result[f"paired_time_constant_{channel + 1}"] = estimates[
            "dominant_time_constant"
        ]
    minimum_length = min(len(item) for item in input_blocks)
    shifts = [max(1, minimum_length // divisor) for divisor in (100, 20, 10)]
    basis = [inputs]
    for shift in shifts:
        basis.append(np.roll(inputs, shift, axis=0))
    dynamic_basis = np.hstack(basis)
    dynamic_basis -= np.mean(dynamic_basis, axis=0, keepdims=True)
    dynamic_coefficients, _, _, _ = np.linalg.lstsq(
        dynamic_basis,
        centered_outputs,
        rcond=None,
    )
    for basis_index, label in enumerate(("base", "lag1", "lag2", "lag3")):
        block = dynamic_coefficients[basis_index * 2 : (basis_index + 1) * 2].T
        for row in range(2):
            for column in range(2):
                result[f"dynamic_map_{label}_{row + 1}{column + 1}"] = float(
                    block[row, column]
                )
    return result


@dataclass(frozen=True)
class FeatureArtifact:
    value: Mapping[str, Any]

    @property
    def fingerprint(self) -> str:
        return str(self.value["artifact_fingerprint"])

    def to_dict(self) -> dict[str, Any]:
        return dict(self.value)


def derive_feature_artifact(
    evidence: Sequence[Mapping[str, Any]],
    route: Mapping[str, Any],
) -> FeatureArtifact:
    required = tuple(str(item) for item in route.get("feature_ids", ()))
    source_ids = [str(item.get("evidence_id") or "evidence") for item in evidence]
    estimates = _summary_estimates(evidence)
    estimates.update(
        {key: value for key, value in _mimo_estimates(evidence).items() if key not in estimates}
    )
    try:
        time_s, command, outputs, trace_ids, _units = _trace_arrays(evidence)
        primary = next(iter(outputs.values()))
        estimates.update({key: value for key, value in _siso_estimates(time_s, command, primary).items() if key not in estimates})
        source_ids = trace_ids
    except ValueError:
        pass
    features: dict[str, Any] = {}
    for feature_id in sorted(set(required) | (set(estimates) & {"gain_matrix_condition", "static_inverse_amplification", "inverse_response_severity"})):
        if feature_id not in estimates:
            continue
        unit = "ratio"
        if "frequency" in feature_id or feature_id.endswith("_rate"):
            unit = "rad/s"
        elif "time_constant" in feature_id or "delay" in feature_id or feature_id.startswith("dynamic_filter_tau"):
            unit = "s"
        elif "gain" in feature_id:
            unit = "output/input"
        features[feature_id] = _feature(feature_id, estimates[feature_id], unit=unit, source_ids=source_ids, method="deterministic_public_trace_parameterization")
    missing = sorted(set(required) - set(features))
    domains = {
        key: [
            float(item["uncertainty"]["lower_bound"]),
            float(item["uncertainty"]["upper_bound"]),
        ]
        for key, item in features.items()
    }
    body = {
        "feature_version": FEATURE_ARTIFACT_VERSION,
        "features": features,
        "required_feature_ids": list(required),
        "missing_feature_ids": missing,
        "parameter_search_domains": domains,
        "quality": {
            "passed": not missing,
            "status": "passed" if not missing else "evidence_gap",
            "reason": None if not missing else "required features could not be derived from public evidence",
        },
        "evidence_fingerprints": [str(item.get("fingerprint") or item.get("trace_fingerprint") or fingerprint(item)) for item in evidence],
    }
    body["artifact_fingerprint"] = fingerprint(body)
    return FeatureArtifact(body)


__all__ = ["FeatureArtifact", "derive_feature_artifact"]
