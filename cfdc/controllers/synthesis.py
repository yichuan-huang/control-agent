from __future__ import annotations

import math

import numpy as np
from scipy.optimize import linear_sum_assignment

from cfdc.models import (
    ArchetypeClass,
    ArchetypeClassification,
    ControllerCandidate,
    CoreFeatureArtifact,
)
from cfdc.validation import missing_required_features


def _feature_map(features: list[CoreFeatureArtifact]) -> dict[str, CoreFeatureArtifact]:
    return {feature.feature_id: feature for feature in features}


def _relative_uncertainty(feature: CoreFeatureArtifact) -> float:
    width = max(abs(feature.upper_bound - feature.value), abs(feature.value - feature.lower_bound))
    return width / max(abs(feature.value), 1e-9)


def _limit(name: str, safety_limits: dict[str, float], default: float) -> float:
    return float(safety_limits.get(name, default))


def synthesize_controller(
    classification: ArchetypeClassification,
    features: list[CoreFeatureArtifact],
    safety_limits: dict[str, float] | None = None,
) -> ControllerCandidate:
    safety = safety_limits or {}
    missing = missing_required_features(classification, features)
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"missing required core features for {classification.primary_class}: {joined}")
    fmap = _feature_map(features)
    archetype = str(classification.primary_class)

    if archetype == ArchetypeClass.CLASS_I_FIRST_ORDER_LAG.value:
        gain = fmap["static_gain"]
        tau = fmap["time_constant"]
        if tau.value <= 0.0 or tau.upper_bound <= 0.0:
            raise ValueError("time_constant must be positive for Class I synthesis")
        rel = _relative_uncertainty(gain)
        conservative_gain = max(abs(gain.lower_bound), abs(gain.upper_bound), 1e-9)
        kc = 0.1 / conservative_gain / (1.0 + 3.0 * rel)
        if gain.value < 0:
            kc = -kc
        ti = 5.0 * max(tau.upper_bound, 1e-6)
        source_features = ["static_gain", "time_constant"]
        constraints = [
            "stable-plant nominal gains reduced by a factor of 10",
            "integral action slowed by 5x time constant",
        ]
        architecture = "detuned_PI"
        design_parameters: dict[str, float] = {}
        if "dead_time" in fmap:
            dead_time = fmap["dead_time"]
            epsilon = 1e-9
            rho_nominal = max(dead_time.value, 0.0) / max(tau.value, epsilon)
            rho_low = max(dead_time.lower_bound, 0.0) / max(
                tau.upper_bound,
                epsilon,
            )
            rho_high = max(dead_time.upper_bound, 0.0) / max(
                tau.lower_bound,
                epsilon,
            )
            design_parameters = {
                "rho_nominal": rho_nominal,
                "rho_low": rho_low,
                "rho_high": rho_high,
            }
            source_features.append("dead_time")
            if rho_high >= 1.0:
                return ControllerCandidate(
                    architecture="large_delay_compensation_required",
                    gains={},
                    design_parameters=design_parameters,
                    tunable_gain_names=[],
                    saturation={
                        "output_min": _limit("output_min", safety, -1e12),
                        "output_max": _limit("output_max", safety, 1e12),
                    },
                    constraints=[
                        *constraints,
                        "do not release ordinary or delay-detuned PI when rho_high is at least 1",
                    ],
                    source_features=source_features,
                    status="refuse",
                    notes=[
                        "A Smith predictor, delay-robust PID, or MPC requires a separately validated implementation."
                    ],
                )
            if rho_high >= 0.1:
                architecture = "delay_detuned_PI"
                delay_detune = 1.0 + rho_nominal
                kc /= delay_detune
                ti *= delay_detune
                constraints.append(
                    "gain and integral speed are detuned by 1 + dead_time/time_constant"
                )
        return ControllerCandidate(
            architecture=architecture,
            gains={"kp": kc, "ki": kc / ti, "integral_time": ti},
            design_parameters=design_parameters,
            tunable_gain_names=["kp", "ki"],
            saturation={"output_min": _limit("output_min", safety, -1e12), "output_max": _limit("output_max", safety, 1e12)},
            constraints=constraints,
            source_features=source_features,
            status="ready_for_conservative_trial",
            notes=["No full parameter identification was used."],
        )

    if archetype == ArchetypeClass.CLASS_II_SECOND_ORDER_OSCILLATOR.value:
        if "input_gain" not in fmap:
            raise ValueError("missing required core features for Class II: input_gain")
        wn_feature = fmap["natural_frequency"]
        wn = max(wn_feature.lower_bound, 1e-9)
        zeta = fmap["damping_ratio"].lower_bound if "damping_ratio" in fmap else 0.3
        plant_gain = fmap["input_gain"]
        conservative_gain = max(
            abs(plant_gain.lower_bound),
            abs(plant_gain.upper_bound),
            1e-9,
        )
        scale = math.copysign(conservative_gain, plant_gain.value)
        kp = 0.1 * wn * wn / scale
        kd = 0.1 * (2.0 * max(zeta, 0.1) * wn) / scale
        return ControllerCandidate(
            architecture="detuned_PD",
            gains={"kp": kp, "kd": kd},
            tunable_gain_names=["kp", "kd"],
            saturation={"output_min": _limit("output_min", safety, -1e12), "output_max": _limit("output_max", safety, 1e12)},
            constraints=["stable oscillatory gains reduced by a factor of 10"],
            source_features=["natural_frequency", "damping_ratio", "input_gain"],
            status="ready_for_conservative_trial",
        )

    if archetype == ArchetypeClass.CLASS_III_DOUBLE_OR_PURE_INTEGRATOR.value:
        output_max = _limit("output_max", safety, 1.0)
        output_min = _limit("output_min", safety, -output_max)
        input_gain = fmap["input_gain"]
        conservative_gain = max(
            abs(input_gain.lower_bound),
            abs(input_gain.upper_bound),
            1e-9,
        )
        gain_scale = math.copysign(conservative_gain, input_gain.value)
        bandwidth = _limit("initial_bandwidth_rad_s", safety, 0.9)
        damping = _limit("initial_damping_ratio", safety, 1.15)
        return ControllerCandidate(
            architecture="small_saturated_PD",
            gains={
                "kp": bandwidth**2 / gain_scale,
                "kd": 2.0 * damping * bandwidth / gain_scale,
            },
            tunable_gain_names=["kp", "kd"],
            saturation={"output_min": output_min, "output_max": output_max},
            constraints=[
                "PD gains are scaled by the measured input-to-acceleration gain",
                "initial closed-loop bandwidth is bounded conservatively",
                "hard saturation is mandatory",
            ],
            source_features=["input_gain"],
            status="ready_for_conservative_trial",
        )

    if archetype == ArchetypeClass.CLASS_V_MULTIVARIABLE_SIGNIFICANT_COUPLING.value:
        if "local_gain_matrix" in fmap:
            matrix = fmap["local_gain_matrix"].value
            if not isinstance(matrix, list):
                raise ValueError("local_gain_matrix requires a matrix value")
            pairing = pair_mimo_loops(matrix)
            gains = {
                "loop_1_gain": 0.1 / max(abs(matrix[0][0]), 1e-9),
                "loop_2_gain": 0.1 / max(abs(matrix[1][1]), 1e-9),
            }
            return ControllerCandidate(
                architecture="conservative_mimo_pairing_with_half_strength_decoupling",
                gains=gains,
                design_parameters={"pairing_indicator": float(fmap["pairing_indicator"].value)},
                tunable_gain_names=list(gains),
                feedforward={f"decoupler_{r}_{c}": value for r, row in enumerate(pairing["half_strength_decoupler"]) for c, value in enumerate(row)},
                saturation={"per_input_limit": _limit("per_input_limit", safety, 1.0)},
                constraints=[
                    "use matrix-valued evidence without scalar collapse",
                    "apply half-strength static decoupling",
                ],
                source_features=["local_gain_matrix", "local_time_constant", "pairing_indicator"],
                status="ready_for_conservative_trial",
                notes=["The 2x2 normalized prototype uses global pairing and a half-strength pseudoinverse decoupler."],
            )
        return ControllerCandidate(
            architecture="conservative_mimo_pairing",
            gains={"loop_gain_scale": 0.1, "decoupler_scale": 0.5},
            tunable_gain_names=["loop_gain_scale", "decoupler_scale"],
            saturation={"per_input_limit": _limit("per_input_limit", safety, 1.0)},
            constraints=["pair loops conservatively", "multiply static decoupling by 0.5"],
            source_features=["coupling_gain"],
            status="ready_for_conservative_trial",
        )

    if "local_static_gain" in fmap or "gain_variation_ratio" in fmap:
        return ControllerCandidate(
            architecture="local_operating_region_validation_required",
            gains={},
            tunable_gain_names=[],
            saturation={},
            constraints=[
                "bind each feature packet to one declared operating region",
                "do not release a global PI controller from one local response",
            ],
            source_features=["local_static_gain", "local_time_constant", "gain_variation_ratio"],
            status="refuse",
            notes=["Gain scheduling and operating-region transition validation are not implemented."],
        )

    if "input_to_unactuated_coupling_gain" in fmap:
        return ControllerCandidate(
            architecture="underactuated_capture_route_not_implemented",
            gains={},
            tunable_gain_names=[],
            saturation={},
            constraints=[
                "validate energy exchange and capture separately for this mechanism",
                "do not reuse the cartpole controller solely because both plants are underactuated",
            ],
            source_features=["natural_frequency", "input_to_unactuated_coupling_gain"],
            status="refuse",
            notes=["Only the Cartpole-specific underactuated route currently has closed-loop validation."],
        )

    if "inverse_response_severity" in fmap and "static_gain" in fmap and "time_constant" in fmap:
        gain = fmap["static_gain"]
        tau = fmap["time_constant"]
        severity = fmap["inverse_response_severity"].value
        rel = _relative_uncertainty(gain)
        detune = 0.05 / (1.0 + severity + 3.0 * rel)
        conservative_gain = max(abs(gain.lower_bound), abs(gain.upper_bound), 1e-9)
        kp = detune / conservative_gain
        if gain.value < 0:
            kp = -kp
        ti = 8.0 * max(tau.upper_bound, 1e-6)
        return ControllerCandidate(
            architecture="detuned_PI_with_NMP_undershoot_guard",
            gains={"kp": kp, "ki": kp / ti, "integral_time": ti},
            tunable_gain_names=["kp", "ki"],
            saturation={"output_min": _limit("output_min", safety, -1e12), "output_max": _limit("output_max", safety, 1e12)},
            constraints=["outer-loop gain starts below stable PI rule", "freeze if inverse-response undershoot grows"],
            source_features=["static_gain", "time_constant", "inverse_response_severity"],
            status="ready_for_conservative_trial",
        )

    if "hover_thrust" in fmap:
        hover = fmap["hover_thrust"].value
        g = _limit("gravity", safety, 9.81)
        mass_est = hover / g
        wz = _limit("vertical_bandwidth_rad_s", safety, 2.0 * math.pi * 0.3)
        zeta = 0.7
        beta_v = 0.1
        beta_r = 0.1
        beta_l = 0.05
        angular_feature = fmap["angular_acceleration_gain"]
        angular_gain = max(
            abs(angular_feature.lower_bound),
            abs(angular_feature.upper_bound),
            1e-9,
        )
        inertia_est = 1.0 / angular_gain
        wtheta = 3.0 * wz
        wy = 0.1 * wtheta
        max_tilt = _limit("max_tilt_rad", safety, 0.26)
        max_torque = _limit("max_torque", safety, 1.0)
        max_altitude_error = _limit("max_altitude_error", safety, 0.5)

        kpz = beta_v * mass_est * wz * wz
        kdz = beta_v * 2.0 * mass_est * zeta * wz
        kpz = min(kpz, 0.05 * hover / max(max_altitude_error, 1e-9))
        kptheta = beta_r * inertia_est * wtheta * wtheta
        kdtheta = beta_r * 2.0 * inertia_est * zeta * wtheta
        kptheta = min(kptheta, 0.1 * max_torque / max(max_tilt, 1e-9))
        kpy = beta_l * wy * wy
        kdy = beta_l * 2.0 * zeta * wy
        return ControllerCandidate(
            architecture="cascaded_PD_with_hover_feedforward",
            gains={
                "kp_z": kpz,
                "kd_z": kdz,
                "kp_theta": kptheta,
                "kd_theta": kdtheta,
                "kp_y": kpy,
                "kd_y": kdy,
            },
            tunable_gain_names=["kp_z", "kd_z", "kp_theta", "kd_theta", "kp_y", "kd_y"],
            feedforward={"hover_thrust": hover},
            saturation={"max_tilt_rad": max_tilt, "max_torque": max_torque},
            constraints=["NMP outer-loop bandwidth starts far below inner-loop bandwidth", "online undershoot monitor must freeze lateral gains"],
            source_features=["hover_thrust", "angular_acceleration_gain", "lateral_coupling_gain"],
            status="ready_for_conservative_trial",
            notes=["Vertical and attitude channels use 0.1 nominal scaling; lateral outer loop uses 0.05 scaling."],
        )

    wn = fmap["natural_frequency"].value if "natural_frequency" in fmap else 1.0
    if "natural_frequency" in fmap and "input_gain" in fmap:
        input_gain = fmap["input_gain"].value
        if isinstance(wn, list) or isinstance(input_gain, list):
            raise ValueError("unstable scalar synthesis requires scalar features")
        lower = fmap["input_gain"].lower_bound
        upper = fmap["input_gain"].upper_bound
        assert lower is not None and upper is not None
        gain_scale = math.copysign(max(abs(lower), abs(upper), 1e-9), input_gain)
        return ControllerCandidate(
            architecture="unstable_mode_conservative_PD",
            gains={"kp": 1.25 * wn**2 / gain_scale, "kd": 2.2 * wn / gain_scale},
            tunable_gain_names=["kp", "kd"],
            saturation={"output_min": _limit("output_min", safety, -8.0), "output_max": _limit("output_max", safety, 8.0)},
            constraints=["stabilizing proportional gain starts above the extracted unstable pole threshold", "bounded Algorithm 1 trial is mandatory"],
            source_features=["natural_frequency", "input_gain"],
            status="requires_online_search",
        )
    if isinstance(wn, list):
        raise ValueError("natural_frequency must be scalar")
    return ControllerCandidate(
        architecture="safe_online_gain_search",
        gains={"kp": 0.0, "kd": 0.01 * wn},
        tunable_gain_names=["kp", "kd"],
        saturation={"output_min": _limit("output_min", safety, -1.0), "output_max": _limit("output_max", safety, 1.0)},
        constraints=["do not de-tune unstable plants by nominal percentage", "increase stabilizing gains only under online safety monitoring"],
        source_features=list(fmap),
        status="requires_online_search",
    )


def pair_mimo_loops(gain_matrix: list[list[float]] | np.ndarray) -> dict[str, object]:
    matrix = np.asarray(gain_matrix, dtype=float)
    if matrix.ndim != 2 or matrix.shape[0] == 0 or matrix.shape[1] == 0:
        raise ValueError("gain_matrix must be a non-empty 2D matrix")
    if not np.all(np.isfinite(matrix)):
        raise ValueError("gain_matrix must contain only finite values")
    rows, cols = matrix.shape
    output_indices, input_indices = linear_sum_assignment(np.abs(matrix), maximize=True)
    pairing: list[dict[str, int | float]] = []
    for row, col in sorted(zip(output_indices.tolist(), input_indices.tolist())):
        strength = abs(float(matrix[row, col]))
        row_sum = float(np.sum(np.abs(matrix[row, :])))
        dominance = float(strength / max(row_sum, 1e-12))
        pairing.append({"output_index": row, "input_index": col, "dominance": dominance})

    decoupler = 0.5 * np.linalg.pinv(matrix)
    diagonal_dominance = min(item["dominance"] for item in pairing)
    paired_outputs = set(output_indices.tolist())
    paired_inputs = set(input_indices.tolist())
    unpaired_outputs = sorted(set(range(rows)) - paired_outputs)
    unpaired_inputs = sorted(set(range(cols)) - paired_inputs)
    return {
        "pairing": pairing,
        "unpaired_output_indices": unpaired_outputs,
        "unpaired_input_indices": unpaired_inputs,
        "half_strength_decoupler": decoupler.tolist(),
        "diagonal_dominance": diagonal_dominance,
        "requires_centralized_review": bool(
            diagonal_dominance < 0.8 or unpaired_outputs or unpaired_inputs
        ),
    }
