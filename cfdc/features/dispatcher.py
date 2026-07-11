from __future__ import annotations

from collections.abc import Iterable

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
from cfdc.models import CoreFeatureArtifact, ExperimentPrimitive, ExperimentResult, ExperimentTrace


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


def extract_features_from_result(result: ExperimentResult) -> list[CoreFeatureArtifact]:
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
            features.append(estimate_pulse_input_gain(trace.time_s, input_signal, acceleration))
        if "angular_acceleration_gain" in requested:
            angular_acceleration = _acceleration_response(trace, "angular_acceleration", "angle_rate", "tilt")
            features.append(
                estimate_pulse_input_gain(
                    trace.time_s,
                    input_signal,
                    angular_acceleration,
                    feature_id="angular_acceleration_gain",
                    units="rad/s^2/input",
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
    return [
        feature.model_copy(update={"provenance": result.provenance})
        for feature in features
    ]


def extract_features_from_results(results: list[ExperimentResult]) -> list[CoreFeatureArtifact]:
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
