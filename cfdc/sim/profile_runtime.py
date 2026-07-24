from __future__ import annotations

import numpy as np

from cfdc.controllers import synthesize_controller
from cfdc.models import (
    BenchmarkRouteIR,
    ControllerCandidate,
    CoreFeatureArtifact,
    SimulationPerformanceSummary,
    SimulationProfile,
)
from cfdc.performance import build_performance_summary, calculate_channel_performance
from cfdc.sim.generic import run_scalar_closed_loop


def _family(profile_id: str) -> str:
    return {
        "first_order_lag": "first_order_lag",
        "first_order_lag_with_delay": "first_order_plus_dead_time",
        "second_order_oscillator": "second_order_oscillator",
        "double_integrator": "double_integrator",
        "nmp_inverse_response": "inverse_response",
        "generic_unstable_higher_order": "unstable_second_order",
    }[profile_id]


def _feature_params(features: list[CoreFeatureArtifact]) -> dict[str, float]:
    values = {
        feature.feature_id: feature.value
        for feature in features
        if isinstance(feature.value, float)
    }
    if "inverse_response_severity" in values:
        values["inverse_time_constant"] = 0.8
    if "natural_frequency" in values and "damping_ratio" not in values:
        values["damping_ratio"] = 0.12
    return values


def _route(
    profile: SimulationProfile, params: dict[str, float], *, changed: bool = False
) -> BenchmarkRouteIR:
    family = _family(profile.profile_id)
    if family == "double_integrator":
        return BenchmarkRouteIR(
            case_id=f"{profile.profile_id}-{'changed' if changed else 'nominal'}",
            plant_family=family,
            reference={"output": 1.0},
            horizon_s=16.0,
            dt_s=0.01,
            plant_params=params,
            actuator_limits={"input_min": -1.0, "input_max": 1.0},
            state_limits={"max_abs_output": 1.6, "max_abs_velocity": 1.4},
            performance_limits={
                "max_abs_final_error": 0.12,
                "max_overshoot": 0.25,
                "max_settling_time_s": 14.0,
                "max_saturation_fraction": 0.6,
                "settling_band_absolute": 0.03,
            },
        )
    if family in {"second_order_oscillator", "unstable_second_order"}:
        return BenchmarkRouteIR(
            case_id=f"{profile.profile_id}-{'changed' if changed else 'nominal'}",
            plant_family=family,
            reference={"output": 0.0},
            horizon_s=14.0,
            dt_s=0.005,
            plant_params=params,
            initial_state={"output": 1.0, "velocity": 0.0},
            actuator_limits={"input_min": -8.0, "input_max": 8.0},
            state_limits={"max_abs_output": 1.5},
            performance_limits={
                "max_abs_final_error": 0.12,
                "max_settling_time_s": 12.0,
                "max_saturation_fraction": 0.6,
                "settling_band_absolute": 0.03,
            },
        )
    return BenchmarkRouteIR(
        case_id=f"{profile.profile_id}-{'changed' if changed else 'nominal'}",
        plant_family=family,
        reference={"output": 0.7},
        horizon_s=2500.0,
        dt_s=0.2,
        plant_params=params,
        actuator_limits={"input_min": 0.0, "input_max": 1.0},
        state_limits={"max_abs_output": 1.5},
        performance_limits={
            "max_abs_final_error": 0.12,
            "max_overshoot": 0.3,
            "max_settling_time_s": 2400.0,
            "max_saturation_fraction": 0.7,
            "settling_band_absolute": 0.03,
        },
    )


def changed_features(features: list[CoreFeatureArtifact]) -> list[CoreFeatureArtifact]:
    factors = {
        "static_gain": 0.8,
        "time_constant": 1.25,
        "natural_frequency": 0.82,
        "input_gain": 0.75,
        "damping_ratio": 0.9,
        "inverse_response_severity": 1.2,
    }
    changed: list[CoreFeatureArtifact] = []
    for feature in features:
        factor = factors.get(feature.feature_id, 1.0)
        value = feature.value * factor
        width = max(abs(value) * 0.05, 1e-6)
        changed.append(
            feature.model_copy(
                update={
                    "object_id": None,
                    "value": value,
                    "lower_bound": value - width,
                    "upper_bound": value + width,
                    "method": f"{feature.method}+online_tracking",
                }
            )
        )
    return changed


def run_scalar_profile_adaptation(
    profile: SimulationProfile,
    classification,
    features: list[CoreFeatureArtifact],
    controller: ControllerCandidate,
) -> tuple[
    SimulationPerformanceSummary,
    SimulationPerformanceSummary,
    ControllerCandidate,
    list[tuple[str, float, float]],
]:
    updated_features = changed_features(features)
    changed_params = _feature_params(updated_features)
    stale = run_scalar_closed_loop(
        _route(profile, changed_params, changed=True), controller
    )
    adapted_controller = synthesize_controller(classification, updated_features)
    adapted = run_scalar_closed_loop(
        _route(profile, changed_params, changed=True), adapted_controller
    )
    updates = [
        (before.feature_id, before.value, after.value)
        for before, after in zip(features, updated_features)
        if before.value != after.value
    ]
    return stale, adapted, adapted_controller, updates


def _matrix_feature(features: list[CoreFeatureArtifact]) -> np.ndarray:
    value = next(
        feature.value
        for feature in features
        if feature.feature_id == "local_gain_matrix"
    )
    if not isinstance(value, list):
        raise ValueError("local_gain_matrix must be matrix-valued")
    return np.asarray(value, dtype=float)


def changed_mimo_features(
    features: list[CoreFeatureArtifact],
) -> list[CoreFeatureArtifact]:
    changed: list[CoreFeatureArtifact] = []
    for feature in features:
        if feature.feature_id == "local_gain_matrix":
            matrix = _matrix_feature([feature])
            drifted = matrix * np.asarray([[0.82, 1.55], [1.50, 0.86]])
            changed.append(
                feature.model_copy(
                    update={
                        "object_id": None,
                        "value": drifted.tolist(),
                        "method": f"{feature.method}+matrix_rls_tracking",
                    }
                )
            )
        elif feature.feature_id == "pairing_indicator":
            assert isinstance(feature.value, float)
            value = max(0.0, feature.value * 0.78)
            changed.append(
                feature.model_copy(
                    update={
                        "object_id": None,
                        "value": value,
                        "lower_bound": max(0.0, value - 0.03),
                        "upper_bound": min(1.0, value + 0.03),
                        "method": f"{feature.method}+matrix_rls_tracking",
                    }
                )
            )
        else:
            changed.append(feature)
    return changed


def run_mimo_closed_loop(
    plant_matrix: np.ndarray,
    controller: ControllerCandidate,
    *,
    horizon_s: float = 180.0,
    dt_s: float = 0.02,
) -> SimulationPerformanceSummary:
    references = np.asarray([0.65, -0.45], dtype=float)
    output = np.zeros(2, dtype=float)
    integral = np.zeros(2, dtype=float)
    gains = np.asarray(
        [controller.gains["loop_1_gain"], controller.gains["loop_2_gain"]]
    )
    decoupler = np.asarray(
        [
            [controller.feedforward[f"decoupler_{row}_{column}"] for column in range(2)]
            for row in range(2)
        ],
        dtype=float,
    )
    transform = 0.5 * np.eye(2) + decoupler
    times: list[float] = []
    outputs = [[], []]
    saturated = np.zeros(2, dtype=int)
    steps = round(horizon_s / dt_s)
    for step in range(steps + 1):
        error = references - output
        integral += error * dt_s
        virtual_input = gains * (error + 0.35 * integral)
        raw_input = transform @ virtual_input
        control = np.clip(raw_input, -1.0, 1.0)
        saturated += np.abs(raw_input - control) > 1e-12
        times.append(step * dt_s)
        for index in range(2):
            outputs[index].append(float(output[index]))
        if step < steps:
            output += dt_s * (-output + plant_matrix @ control)
    channels = {
        f"output_{index + 1}": calculate_channel_performance(
            times,
            float(references[index]),
            outputs[index],
            settling_band_absolute=0.035,
        )
        for index in range(2)
    }
    saturation_fractions = {
        f"input_{index + 1}": float(saturated[index] / max(1, steps + 1))
        for index in range(2)
    }
    violations: list[str] = []
    for name, channel in channels.items():
        if channel.abs_final_error > 0.08:
            violations.append(f"{name}_final_error_limit")
        if not channel.settled:
            violations.append(f"{name}_not_settled")
    if max(saturation_fractions.values()) > 0.25:
        violations.append("saturation_fraction_limit")
    return build_performance_summary(
        primary_channel="output_1",
        channels=channels,
        actuator_saturation_fractions=saturation_fractions,
        state_boundaries={
            "max_abs_output": max(
                max(abs(value) for value in channel) for channel in outputs
            )
        },
        limits={"max_abs_final_error": 0.08, "max_saturation_fraction": 0.25},
        violations=violations,
        success=not violations,
    )


def run_mimo_profile_adaptation(
    profile: SimulationProfile,
    classification,
    features: list[CoreFeatureArtifact],
    controller: ControllerCandidate,
) -> tuple[
    SimulationPerformanceSummary,
    SimulationPerformanceSummary,
    ControllerCandidate,
    list[tuple[str, float, float]],
]:
    del profile
    updated_features = changed_mimo_features(features)
    changed_matrix = _matrix_feature(updated_features)
    stale = run_mimo_closed_loop(changed_matrix, controller)
    adapted_controller = synthesize_controller(classification, updated_features)
    adapted = run_mimo_closed_loop(changed_matrix, adapted_controller)
    old_matrix = _matrix_feature(features)
    relative_change = float(
        np.linalg.norm(changed_matrix - old_matrix) / np.linalg.norm(old_matrix)
    )
    return (
        stale,
        adapted,
        adapted_controller,
        [("local_gain_matrix", 1.0, 1.0 + relative_change)],
    )
