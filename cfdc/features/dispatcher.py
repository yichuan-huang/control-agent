from __future__ import annotations

from collections.abc import Iterable
import hashlib

import numpy as np

from cfdc.features.extractors import (
    estimate_coupling_gain,
    estimate_damping_ratio,
    estimate_dead_time,
    estimate_hover_thrust,
    estimate_inverse_response_severity,
    estimate_natural_frequency,
    estimate_pulse_input_gain,
    estimate_signal_ratio_feature,
    estimate_step_features,
)
from cfdc.models import CoreFeatureArtifact, ExperimentPrimitive, SimulationExperimentRecord, ExperimentTrace


_SIGNAL_ALIASES: dict[str, tuple[str, ...]] = {
    "free_response": (
        "free_response",
        "measured position or angle",
        "measured position",
        "measured angle",
        "position",
        "angle",
        "output",
        "measured output",
    ),
    "input": (
        "input",
        "input_signal",
        "input setting",
        "actuator",
        "command",
        "test command",
        "twist command",
    ),
    "output": (
        "output",
        "output_signal",
        "measured output",
        "measured position",
        "measured position or speed",
        "position",
        "speed",
        "level",
        "temperature",
    ),
    "acceleration": (
        "acceleration",
        "acceleration_signal",
        "measured acceleration",
    ),
    "angular_acceleration": (
        "angular_acceleration",
        "angular acceleration",
        "angle acceleration",
        "measured angular acceleration",
    ),
    "motion_rate": (
        "speed",
        "velocity",
        "measured speed",
        "measured velocity",
        "rate",
        "measured rate",
    ),
    "motion_position": (
        "position",
        "measured position",
        "measured motion",
        "measured position or speed",
    ),
    "angle_rate": (
        "angle rate",
        "angular rate",
        "roll rate",
        "measured angle rate",
    ),
    "thrust": (
        "thrust",
        "thrust_command",
        "lift setting",
        "lift_setting",
        "input setting",
        "input",
    ),
    "lift": (
        "lift",
        "lift_signal",
        "support-light signal",
        "vertical motion or support-light signal",
        "vertical motion",
    ),
    "primary_output": (
        "primary_output",
        "primary output",
        "paired_output",
        "paired output",
        "output",
        "measured output",
        "output_0",
    ),
    "coupled_output": (
        "coupled_output",
        "coupled output",
        "cross_output",
        "cross output",
        "lateral_acceleration",
        "lateral acceleration",
        "measured lateral acceleration",
        "output_1",
    ),
    "tilt": (
        "tilt",
        "tilt_angle",
        "roll_angle",
        "roll angle",
        "angle",
    ),
}


def _normalized(name: str) -> str:
    return " ".join(name.replace("_", " ").replace("-", " ").lower().split())


def _signal(trace: ExperimentTrace, canonical_name: str, required: bool = True) -> list[float] | None:
    values = _lookup_signal(trace, _SIGNAL_ALIASES[canonical_name])
    if values is not None:
        return values
    if required:
        aliases = ", ".join(_SIGNAL_ALIASES[canonical_name][:4])
        raise ValueError(f"missing signal for '{canonical_name}' (accepted aliases include: {aliases})")
    return None


def _lookup_signal(trace: ExperimentTrace, aliases: tuple[str, ...]) -> list[float] | None:
    lookup = {_normalized(name): values for name, values in trace.signals.items()}
    for alias in aliases:
        values = lookup.get(_normalized(alias))
        if values is not None:
            return values
    return None


def _signal_unit(trace: ExperimentTrace, canonical_name: str) -> str | None:
    declared = trace.metadata.get("signal_units", {})
    if not isinstance(declared, dict):
        return None
    aliases = {_normalized(item) for item in _SIGNAL_ALIASES[canonical_name]}
    for signal_name in trace.signals:
        if _normalized(signal_name) in aliases:
            unit = declared.get(signal_name)
            if isinstance(unit, str) and unit:
                return unit
    direct = declared.get(canonical_name)
    return direct if isinstance(direct, str) and direct else None


def _input_gain_units(
    trace: ExperimentTrace,
    acceleration_name: str,
    rate_name: str,
    position_name: str,
    fallback: str = "acceleration/input",
) -> str:
    acceleration_unit = _signal_unit(trace, acceleration_name)
    if acceleration_unit is None and _signal(trace, rate_name, required=False) is not None:
        rate_unit = _signal_unit(trace, rate_name)
        acceleration_unit = f"{rate_unit}/s" if rate_unit else None
    if (
        acceleration_unit is None
        and _signal(trace, position_name, required=False) is not None
    ):
        position_unit = _signal_unit(trace, position_name)
        acceleration_unit = f"{position_unit}/s^2" if position_unit else None
    input_unit = _signal_unit(trace, "input")
    if acceleration_unit and input_unit:
        return f"{acceleration_unit}/{input_unit}"
    return fallback


def _differentiate(trace: ExperimentTrace, values: list[float]) -> list[float]:
    time = np.asarray(trace.time_s, dtype=float)
    signal = np.asarray(values, dtype=float)
    return np.gradient(signal, time).tolist()


def _acceleration_response(
    trace: ExperimentTrace,
    acceleration_name: str,
    rate_name: str,
    position_name: str,
) -> list[float]:
    direct = _signal(trace, acceleration_name, required=False)
    if direct is not None:
        return direct
    rate = _signal(trace, rate_name, required=False)
    if rate is not None:
        return _differentiate(trace, rate)
    position = _signal(trace, position_name, required=False)
    if position is not None:
        return _differentiate(trace, _differentiate(trace, position))
    raise ValueError(f"missing acceleration-like signal for '{acceleration_name}'")


def _filter_requested(
    artifacts: Iterable[CoreFeatureArtifact],
    requested: set[str],
) -> list[CoreFeatureArtifact]:
    return [artifact for artifact in artifacts if artifact.feature_id in requested]


def _estimate_mimo_local_time_constant(
    time_s: np.ndarray,
    inputs: list[np.ndarray],
    outputs: list[np.ndarray],
) -> CoreFeatureArtifact:
    transitions = sorted(
        {
            int(index + 1)
            for input_signal in inputs
            for index in np.where(
                np.diff(input_signal)
                > max(1e-12, 0.10 * float(np.ptp(input_signal)))
            )[0]
        }
    )
    all_changes = sorted(
        {
            int(index + 1)
            for input_signal in inputs
            for index in np.where(
                np.abs(np.diff(input_signal))
                > max(1e-12, 0.10 * float(np.ptp(input_signal)))
            )[0]
        }
    )
    estimates: list[float] = []
    sample_dt = float(np.median(np.diff(time_s)))
    for start in transitions:
        later = [index for index in all_changes if index > start]
        stop = later[0] if later else len(time_s)
        if stop - start < 10:
            continue
        baseline_start = max(0, start - max(5, (stop - start) // 10))
        tail_count = max(5, (stop - start) // 10)
        for output in outputs:
            baseline = float(np.median(output[baseline_start:start]))
            settled = float(np.median(output[stop - tail_count : stop]))
            change = settled - baseline
            if abs(change) < max(1e-12, 0.02 * float(np.ptp(output))):
                continue
            target = baseline + 0.6321205588 * change
            segment = output[start:stop]
            crossed = (
                np.where(segment >= target)[0]
                if change > 0.0
                else np.where(segment <= target)[0]
            )
            if crossed.size:
                estimate = float(time_s[start + int(crossed[0])] - time_s[start])
                if estimate >= sample_dt:
                    estimates.append(estimate)
    if not estimates:
        raise ValueError("MIMO scan does not contain a resolvable 63-percent transition")
    value = float(np.median(estimates))
    spread = float(np.std(estimates, ddof=1)) if len(estimates) > 1 else 0.0
    half_width = max(2.0 * sample_dt, 0.10 * value, spread)
    return CoreFeatureArtifact(
        feature_id="local_time_constant",
        value=value,
        lower_bound=max(sample_dt, value - half_width),
        upper_bound=value + half_width,
        confidence=0.90 if len(estimates) >= 2 else 0.78,
        units="s",
        method="mimo_step_63_percent_transition",
        source_experiment=ExperimentPrimitive.BOUNDED_SCAN,
    )


def _estimate_mimo_gain_matrix(
    time_s: np.ndarray,
    inputs: list[np.ndarray],
    outputs: list[np.ndarray],
    time_constant_s: float,
) -> np.ndarray:
    """Estimate one-at-a-time steady gains without treating transients as static data."""

    if time_constant_s <= 0.0:
        raise ValueError("MIMO steady-gain estimation requires a positive time constant")
    input_stack = np.column_stack(inputs)
    inactive = np.all(
        np.abs(input_stack) <= max(1e-9, 0.01 * float(np.max(np.abs(input_stack)))),
        axis=1,
    )
    first_active = int(np.flatnonzero(~inactive)[0])
    baseline_slice = slice(0, max(first_active, 1))
    baseline_outputs = np.asarray(
        [float(np.median(output[baseline_slice])) for output in outputs]
    )
    columns: list[np.ndarray] = []
    for input_signal in inputs:
        threshold = max(1e-9, 0.05 * float(np.max(np.abs(input_signal))))
        active_indices = np.flatnonzero(np.abs(input_signal) > threshold)
        if active_indices.size < 3:
            raise ValueError("each MIMO scan input requires a bounded non-zero interval")
        splits = np.split(active_indices, np.where(np.diff(active_indices) > 1)[0] + 1)
        segment = max(splits, key=len)
        start = int(segment[0])
        stop = int(segment[-1])
        amplitude = float(np.median(input_signal[segment]))
        if abs(amplitude) <= 1e-12:
            raise ValueError("MIMO scan input amplitude must be non-zero")
        tail_count = max(3, len(segment) // 20)
        tail = segment[-tail_count:]
        elapsed = max(float(np.mean(time_s[tail]) - time_s[start]), 1e-9)
        decay = float(np.exp(-elapsed / time_constant_s))
        if 1.0 - decay <= 1e-6:
            raise ValueError("MIMO scan interval is too short to estimate steady gain")
        start_outputs = np.asarray(
            [float(output[max(0, start - 1)]) for output in outputs]
        )
        tail_outputs = np.asarray(
            [float(np.median(output[tail])) for output in outputs]
        )
        steady_target = (tail_outputs - decay * start_outputs) / (1.0 - decay)
        columns.append((steady_target - baseline_outputs) / amplitude)
    return np.column_stack(columns)


def extract_features_from_result(result: SimulationExperimentRecord) -> list[CoreFeatureArtifact]:
    """Dispatch one structured experiment result to deterministic CFDC extractors."""

    requested = set(result.estimates)
    trace = result.trace
    primitive = str(result.primitive)
    features: list[CoreFeatureArtifact] = []

    if primitive == ExperimentPrimitive.FREE_DECAY.value:
        response = _signal(trace, "free_response")
        if "natural_frequency" in requested:
            features.append(estimate_natural_frequency(trace.time_s, response))
        if "damping_ratio" in requested:
            features.append(estimate_damping_ratio(trace.time_s, response))

    elif primitive == ExperimentPrimitive.RAMP_STEP.value:
        input_signal = _signal(trace, "input")
        output_signal = _signal(trace, "output")
        if {"static_gain", "time_constant"} & requested:
            features.extend(_filter_requested(estimate_step_features(trace.time_s, input_signal, output_signal), requested))
        if "dead_time" in requested:
            features.append(estimate_dead_time(trace.time_s, input_signal, output_signal))
        if "inverse_response_severity" in requested:
            features.append(estimate_inverse_response_severity(trace.time_s, output_signal))

    elif primitive == ExperimentPrimitive.PULSE.value:
        input_signal = _signal(trace, "input")
        if "input_gain" in requested:
            acceleration = _acceleration_response(trace, "acceleration", "motion_rate", "motion_position")
            features.append(
                estimate_pulse_input_gain(
                    trace.time_s,
                    input_signal,
                    acceleration,
                    units=_input_gain_units(
                        trace,
                        "acceleration",
                        "motion_rate",
                        "motion_position",
                    ),
                )
            )
        if "angular_acceleration_gain" in requested:
            angular_acceleration = _acceleration_response(trace, "angular_acceleration", "angle_rate", "tilt")
            features.append(
                estimate_pulse_input_gain(
                    trace.time_s,
                    input_signal,
                    angular_acceleration,
                    feature_id="angular_acceleration_gain",
                    units=_input_gain_units(
                        trace,
                        "angular_acceleration",
                        "angle_rate",
                        "tilt",
                        fallback="rad/s^2/input",
                    ),
                )
            )
        if "lateral_coupling_gain" in requested:
            lateral = _signal(trace, "coupled_output")
            tilt = _signal(trace, "tilt", required=False)
            denominator = tilt if tilt is not None else input_signal
            units = "m/s^2/rad" if tilt is not None else "m/s^2/input"
            features.append(
                estimate_signal_ratio_feature(
                    trace.time_s,
                    lateral,
                    denominator,
                    feature_id="lateral_coupling_gain",
                    units=units,
                    method="small_pulse_coupling_ratio",
                    source_experiment=ExperimentPrimitive.PULSE,
                )
            )

    elif primitive == ExperimentPrimitive.HOVER_THRUST.value:
        if "hover_thrust" in requested:
            thrust = _signal(trace, "thrust")
            lift = _signal(trace, "lift", required=False)
            features.append(estimate_hover_thrust(trace.time_s, thrust, lift))

    elif primitive == ExperimentPrimitive.BOUNDED_SCAN.value:
        if "local_gain_matrix" in requested:
            lookup = {_normalized(name): values for name, values in trace.signals.items()}
            u1 = np.asarray(lookup["input 1"], dtype=float)
            u2 = np.asarray(lookup["input 2"], dtype=float)
            y1 = np.asarray(lookup["output 1"], dtype=float)
            y2 = np.asarray(lookup["output 2"], dtype=float)
            time_s = np.asarray(trace.time_s, dtype=float)
            time_constant = _estimate_mimo_local_time_constant(
                time_s, [u1, u2], [y1, y2]
            )
            matrix = _estimate_mimo_gain_matrix(
                time_s,
                [u1, u2],
                [y1, y2],
                float(time_constant.value),
            )
            diagonal = min(abs(matrix[0, 0]), abs(matrix[1, 1]))
            off_diagonal = max(abs(matrix[0, 1]), abs(matrix[1, 0]))
            pairing = diagonal / max(diagonal + off_diagonal, 1e-9)
            features.extend([
                CoreFeatureArtifact(feature_id="local_gain_matrix", value=matrix.tolist(), confidence=0.92, units="output/input", method="2x2_one_at_a_time_steady_state_extrapolation", source_experiment=ExperimentPrimitive.BOUNDED_SCAN),
                time_constant,
                CoreFeatureArtifact(feature_id="pairing_indicator", value=float(pairing), lower_bound=max(0.0, float(pairing)-0.03), upper_bound=min(1.0, float(pairing)+0.03), confidence=0.9, units="ratio", method="matrix_diagonal_dominance", source_experiment=ExperimentPrimitive.BOUNDED_SCAN),
            ])
        if "coupling_gain" in requested:
            input_signal = _signal(trace, "input")
            primary = _signal(trace, "primary_output")
            coupled = _signal(trace, "coupled_output", required=False)
            features.append(estimate_coupling_gain(trace.time_s, input_signal, primary, coupled))

    else:
        raise ValueError(f"unsupported experiment primitive: {result.primitive}")

    produced = {feature.feature_id for feature in features}
    missing = requested - produced
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"no extractor available for requested feature(s): {missing_list}")
    trace_sha256 = hashlib.sha256(result.trace.model_dump_json().encode()).hexdigest()
    propagated: list[CoreFeatureArtifact] = []
    for feature in features:
        payload = feature.model_dump()
        payload.update(
            {
                "object_id": None,
                "plant_id": result.plant_id,
                "evidence_package_id": result.evidence_package_id,
                "model_sha256": result.model_sha256,
                "evidence_source": (
                    "demo_fixture"
                    if result.evidence_source == "demo_fixture"
                    else result.evidence_source
                    if result.evidence_source in {"model_simulation", "measured_trace"}
                    else "legacy"
                ),
                "trace_sha256": trace_sha256,
                "experiment_protocol_version": result.experiment_protocol_version,
                "operating_region": result.operating_region,
            }
        )
        propagated.append(CoreFeatureArtifact.model_validate(payload))
    return propagated


def extract_features_from_results(results: list[SimulationExperimentRecord]) -> list[CoreFeatureArtifact]:
    """Dispatch complementary results without silently discarding duplicate estimates."""

    features: list[CoreFeatureArtifact] = []
    seen: set[str] = set()
    for result in results:
        duplicates = seen.intersection(result.estimates)
        if duplicates:
            duplicate = sorted(duplicates)[0]
            raise ValueError(f"duplicate experiment estimate '{duplicate}'")
        for feature in extract_features_from_result(result):
            features.append(feature)
            seen.add(feature.feature_id)
    return features


def extract_features_from_repeated_results(
    results: list[SimulationExperimentRecord],
) -> list[CoreFeatureArtifact]:
    """Aggregate repeated simulation experiments without treating repeats as conflicts."""

    regions_by_feature: dict[str, set[str]] = {}
    plants_by_feature: dict[str, set[str]] = {}
    packages_by_feature: dict[str, set[str]] = {}
    for result in results:
        for feature_id in result.estimates:
            regions_by_feature.setdefault(feature_id, set()).add(
                result.operating_region
            )
            if result.plant_id is not None:
                plants_by_feature.setdefault(feature_id, set()).add(result.plant_id)
            if result.evidence_package_id is not None:
                packages_by_feature.setdefault(feature_id, set()).add(
                    result.evidence_package_id
                )
    for feature_id, regions in regions_by_feature.items():
        if len(regions) > 1:
            raise ValueError(
                f"repeated feature '{feature_id}' spans more than one operating region"
            )
        if len(plants_by_feature.get(feature_id, set())) > 1:
            raise ValueError(
                f"repeated feature '{feature_id}' belongs to more than one plant"
            )
        if len(packages_by_feature.get(feature_id, set())) > 1:
            raise ValueError(
                f"repeated feature '{feature_id}' belongs to more than one evidence package"
            )

    grouped: dict[str, list[CoreFeatureArtifact]] = {}
    for result in results:
        for feature in extract_features_from_result(result):
            grouped.setdefault(feature.feature_id, []).append(feature)
    aggregated: list[CoreFeatureArtifact] = []
    for feature_id, samples in grouped.items():
        if feature_id == "local_gain_matrix":
            matrices = np.asarray([sample.value for sample in samples], dtype=float)
            mean_matrix = np.mean(matrices, axis=0)
            reference_norm = max(
                float(np.linalg.norm(mean_matrix)),
                float(np.median([np.linalg.norm(matrix) for matrix in matrices])),
                1e-12,
            )
            maximum_relative_deviation = max(
                float(np.linalg.norm(matrix - mean_matrix)) / reference_norm
                for matrix in matrices
            )
            if maximum_relative_deviation > 0.35:
                raise ValueError(
                    "inconsistent local gain matrices across measured repeats; "
                    "review trial identity, operating region, and excitation quality"
                )
            exemplar = samples[0]
            digest = hashlib.sha256("".join(sample.trace_sha256 or "" for sample in samples).encode()).hexdigest()
            payload = exemplar.model_dump()
            payload.update({
                "object_id": None,
                "value": mean_matrix.tolist(),
                "confidence": min(0.99, max(sample.confidence for sample in samples) + 0.03 * (len(samples) - 1)),
                "method": f"{exemplar.method}+repeat_matrix_mean_n{len(samples)}",
                "trace_sha256": digest,
            })
            aggregated.append(CoreFeatureArtifact.model_validate(payload))
            continue
        values = np.asarray([sample.value for sample in samples], dtype=float)
        mean = float(np.mean(values))
        between = float(np.std(values, ddof=1)) if len(values) > 1 else 0.0
        estimator_half_width = max(
            max(abs(sample.upper_bound - sample.value), abs(sample.value - sample.lower_bound))
            for sample in samples
        )
        half_width = max(estimator_half_width / max(len(samples) ** 0.5, 1.0), 1.96 * between / max(len(samples) ** 0.5, 1.0), 1e-9)
        exemplar = samples[0]
        digest = hashlib.sha256("".join(sample.trace_sha256 or "" for sample in samples).encode()).hexdigest()
        payload = exemplar.model_dump()
        payload.update({
            "object_id": None,
            "value": mean,
            "lower_bound": mean - half_width,
            "upper_bound": mean + half_width,
            "confidence": min(0.99, max(sample.confidence for sample in samples) + 0.03 * (len(samples) - 1)),
            "method": f"{exemplar.method}+repeat_mean_n{len(samples)}",
            "trace_sha256": digest,
        })
        aggregated.append(CoreFeatureArtifact.model_validate(payload))
    return aggregated
