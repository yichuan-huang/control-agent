"""Evidence-conditioned numerical qualification before controller freeze."""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

import numpy as np

from cfdc.controllers.execution import ControllerRuntime
from cfdc.kernel.contracts import QUALIFICATION_VERSION, fingerprint
from cfdc.kernel.controllers import ControllerIR

OFFLINE_QUALIFIED = "offline_qualified"
DIAGNOSTIC_TRIAL_ONLY = "diagnostic_trial_only"
NOT_QUALIFIED = "not_qualified"

_MIMO_FAMILIES = {
    "decentralized_channel_PI",
    "static_decoupler_then_PI",
    "lag_dynamic_decoupler_then_PI",
}
_MODAL_FAMILIES = {
    "local_fixed_PID",
    "scheduled_damping_PID",
    "self_excitation_energy_guarded_PID",
}


def _feature_values(artifact: Mapping[str, Any]) -> dict[str, float]:
    result = {}
    for key, item in (artifact.get("features") or {}).items():
        if isinstance(item, Mapping) and isinstance(item.get("value"), (int, float)):
            result[str(key)] = float(item["value"])
    return result


def _sampled_pole_metrics(matrix: np.ndarray, sample_time_s: float) -> dict[str, Any]:
    poles = np.linalg.eigvals(matrix)
    discrete = np.exp(poles * sample_time_s)
    return {
        "continuous_poles": [
            {"real": float(value.real), "imag": float(value.imag)} for value in poles
        ],
        "max_discrete_pole_magnitude": float(np.max(np.abs(discrete))),
        "stable": bool(np.all(np.isfinite(poles)) and np.max(np.real(poles)) < -1e-9),
    }


def _parameterized_linear_backend(
    controller: ControllerIR,
    features: Mapping[str, float],
    sample_time_s: float,
) -> tuple[bool, dict[str, Any]] | None:
    if controller.family in _MIMO_FAMILIES | _MODAL_FAMILIES | {
        "cascaded_control",
        "lead_lag_series",
    }:
        return None
    gain = features.get(
        "static_gain",
        features.get(
            "input_gain",
            features.get(
                "static_map_linear_coefficient", features.get("outer_static_slope")
            ),
        ),
    )
    tau = features.get("dominant_time_constant", features.get("time_constant"))
    if gain is None or tau is None or abs(float(gain)) <= 1e-12 or tau <= 0.0:
        return None
    parameters = controller.parameters
    kp = parameters.get("kp", parameters.get("Kp_virtual"))
    if kp is None:
        return None
    effective_tau = float(tau) + float(gain) * float(parameters.get("kd", 0.0))
    if effective_tau <= 1e-12:
        return False, {
            "linear_max_discrete_pole_magnitude": float("inf"),
            "linear_continuous_poles": [],
            "linear_effective_time_constant_s": effective_tau,
        }
    ki = parameters.get("ki", parameters.get("Ki_virtual"))
    if ki is None:
        matrix = np.asarray([[-(1.0 + float(gain) * float(kp)) / effective_tau]])
    else:
        matrix = np.asarray(
            [
                [
                    -(1.0 + float(gain) * float(kp)) / effective_tau,
                    float(gain) / effective_tau,
                ],
                [-float(ki), 0.0],
            ]
        )
    pole_metrics = _sampled_pole_metrics(matrix, sample_time_s)
    delay = max(float(features.get("delay_bound", features.get("dead_time", 0.0))), 0.0)
    bandwidth = abs(
        float(
            parameters.get(
                "target_bandwidth", parameters.get("reference_filter_rate", 0.0)
            )
        )
    )
    phase_budget = bandwidth * delay
    passed = bool(pole_metrics["stable"] and phase_budget < math.pi / 2.0)
    return passed, {
        "linear_max_discrete_pole_magnitude": pole_metrics[
            "max_discrete_pole_magnitude"
        ],
        "linear_continuous_poles": pole_metrics["continuous_poles"],
        "linear_delay_phase_budget_rad": phase_budget,
        "linear_effective_time_constant_s": effective_tau,
    }


def _mimo_frequency_backend(
    controller: ControllerIR,
    features: Mapping[str, float],
    sample_time_s: float,
) -> tuple[bool, dict[str, Any]] | None:
    if controller.family not in _MIMO_FAMILIES:
        return None
    plant = np.asarray(
        [
            [features.get("local_gain_k11", 0.0), features.get("local_gain_k12", 0.0)],
            [features.get("local_gain_k21", 0.0), features.get("local_gain_k22", 0.0)],
        ],
        dtype=float,
    )
    parameters = controller.parameters
    prefix = (
        "dynamic_map_base"
        if controller.family == "lag_dynamic_decoupler_then_PI"
        else "input_map"
    )
    mapping = np.asarray(
        [
            [parameters[f"{prefix}_11"], parameters[f"{prefix}_12"]],
            [parameters[f"{prefix}_21"], parameters[f"{prefix}_22"]],
        ],
        dtype=float,
    )
    time_constants = np.asarray(
        [
            features.get("paired_time_constant_1", 1.0),
            features.get("paired_time_constant_2", 1.0),
        ],
        dtype=float,
    )
    if np.any(time_constants <= 0.0):
        return False, {"mimo_max_discrete_pole_magnitude": float("inf")}
    rates = np.diag(1.0 / time_constants)
    kp = np.diag([parameters["kp_1"], parameters["kp_2"]])
    ki = np.diag([parameters["ki_1"], parameters["ki_2"]])
    loop_map = plant @ mapping
    matrix = np.block(
        [
            [-rates - rates @ loop_map @ kp, rates @ loop_map],
            [-ki, np.zeros((2, 2))],
        ]
    )
    pole_metrics = _sampled_pole_metrics(matrix, sample_time_s)
    return_difference = np.eye(2) + loop_map @ kp
    minimum_return_difference = float(
        np.min(np.linalg.svd(return_difference, compute_uv=False))
    )
    sensitivity_peak = float(np.linalg.norm(np.linalg.inv(return_difference), 2))
    inverse_amplification = float(
        features.get(
            "dynamic_inverse_peak_amplification",
            features.get("static_inverse_amplification", np.linalg.norm(mapping, 2)),
        )
    )
    residual = float(
        features.get(
            "dynamic_decoupler_fit_residual",
            features.get("inband_static_decoupler_residual", 0.0),
        )
    )
    passed = bool(
        pole_metrics["stable"]
        and minimum_return_difference > 1e-6
        and math.isfinite(sensitivity_peak)
        and sensitivity_peak <= 50.0
        and inverse_amplification <= 50.0
        and residual <= 1.0
    )
    return passed, {
        "mimo_max_discrete_pole_magnitude": pole_metrics["max_discrete_pole_magnitude"],
        "mimo_continuous_poles": pole_metrics["continuous_poles"],
        "minimum_return_difference": minimum_return_difference,
        "sensitivity_peak_bound": sensitivity_peak,
        "decoupler_inverse_amplification": inverse_amplification,
        "decoupler_fit_residual": residual,
    }


def _local_nonlinear_backend(
    controller: ControllerIR,
    features: Mapping[str, float],
    sample_time_s: float,
) -> tuple[bool, dict[str, Any]] | None:
    parameters = controller.parameters
    if controller.family in _MODAL_FAMILIES:
        frequency = float(
            features.get("modal_frequency", features.get("natural_frequency", 0.0))
        )
        input_gain = float(
            features.get("input_gain", features.get("signed_input_gain", 0.0))
        )
        if frequency <= 0.0 or abs(input_gain) <= 1e-12:
            return False, {"local_max_discrete_pole_magnitude": float("inf")}
        decay = float(
            features.get(
                "base_decay_rate", features.get("small_amplitude_decay_rate", 0.0)
            )
        )
        derivative_gain = float(parameters["kd"])
        if controller.family == "self_excitation_energy_guarded_PID":
            derivative_gain += abs(float(parameters["capture_damping_gain"]))
        matrix = np.asarray(
            [
                [0.0, 1.0, 0.0],
                [
                    -(frequency**2) - input_gain * float(parameters["kp"]),
                    -decay - input_gain * derivative_gain,
                    input_gain,
                ],
                [-float(parameters["ki"]), 0.0, 0.0],
            ]
        )
    elif controller.family == "cascaded_control":
        if "x_m" in controller.measured_signals:
            valid = all(
                math.isfinite(float(parameters.get(name, float("nan"))))
                and float(parameters[name]) > 0.0
                for name in ("hover_thrust", "altitude_kp", "altitude_kd")
            )
            return valid, {
                "local_chart": "planar_vtol_near_hover",
                "local_max_discrete_pole_magnitude": 0.0 if valid else float("inf"),
            }
        unstable = float(features.get("unstable_mode_rate", 0.0))
        input_gain = float(features.get("angular_input_gain", 0.0))
        if unstable <= 0.0 or abs(input_gain) <= 1e-12:
            return False, {"local_max_discrete_pole_magnitude": float("inf")}
        inner_kp = float(parameters["inner_kp"])
        inner_kd = float(parameters["inner_kd"])
        outer_rate = float(parameters["outer_target_rate"])
        outer_damping = float(parameters["outer_damping"])
        scale = float(parameters["reference_acceleration_scale"])
        position_gain = inner_kp * outer_rate**2 / scale
        velocity_gain = inner_kp * 2.0 * outer_damping * outer_rate / scale
        matrix = np.asarray(
            [
                [0.0, 1.0, 0.0, 0.0],
                [position_gain, velocity_gain - 0.15, -inner_kp, -inner_kd],
                [0.0, 0.0, 0.0, 1.0],
                [
                    input_gain * position_gain,
                    input_gain * velocity_gain,
                    unstable**2 - input_gain * inner_kp,
                    -0.1 - input_gain * inner_kd,
                ],
            ]
        )
    else:
        return None
    pole_metrics = _sampled_pole_metrics(matrix, sample_time_s)
    return bool(pole_metrics["stable"]), {
        "local_max_discrete_pole_magnitude": pole_metrics[
            "max_discrete_pole_magnitude"
        ],
        "local_continuous_poles": pole_metrics["continuous_poles"],
        "local_chart": "bounded_equilibrium_linearization",
    }


def qualify_controller(
    controller: ControllerIR,
    *,
    task: Mapping[str, Any],
    route: Mapping[str, Any],
    feature_artifact: Mapping[str, Any],
    protocol: Mapping[str, Any],
) -> dict[str, Any]:
    reasons: list[str] = []
    checks: dict[str, str] = {}
    features = _feature_values(feature_artifact)
    if feature_artifact.get("missing_feature_ids") or not bool(
        (feature_artifact.get("quality") or {}).get("passed", False)
    ):
        reasons.append("required public features are missing or failed quality checks")
    lower, upper = controller.output_bounds or (float("nan"), float("nan"))
    bounds_ok = math.isfinite(lower) and math.isfinite(upper) and lower < upper
    if task.get("input_min") is not None:
        bounds_ok &= lower >= float(task["input_min"]) - 1e-12
    if task.get("input_max") is not None:
        bounds_ok &= upper <= float(task["input_max"]) + 1e-12
    checks["constraints"] = "pass" if bounds_ok else "fail"
    if not bounds_ok:
        reasons.append("controller output bounds exceed the declared task envelope")
    domains_ok = all(
        bounds[0] <= controller.parameters[name] <= bounds[1]
        for name, bounds in controller.parameter_domains.items()
    )
    checks["parameter_domains"] = "pass" if domains_ok else "fail"
    if not domains_ok:
        reasons.append(
            "one or more controller parameters are outside their frozen domains"
        )
    uncertainty_ok = True
    worst_relative = 0.0
    consumed_features = set(route.get("feature_ids", ())) or set(features)
    for feature_name, item in (feature_artifact.get("features") or {}).items():
        if feature_name not in consumed_features:
            continue
        if not isinstance(item, Mapping):
            continue
        signed_value = float(item.get("value", 0.0))
        value = abs(signed_value)
        interval = item.get("uncertainty") or {}
        width = max(
            abs(float(interval.get("upper_bound", signed_value)) - signed_value),
            abs(signed_value - float(interval.get("lower_bound", signed_value))),
        )
        relative = width / max(value, 1e-6)
        worst_relative = max(worst_relative, relative)
        uncertainty_ok &= relative <= 1.0
    checks["evidence_uncertainty"] = "pass" if uncertainty_ok else "fail"
    if not uncertainty_ok:
        reasons.append("feature uncertainty is too wide for a bounded first trial")
    family = controller.family
    stability_ok = True
    recoverability = "pass"
    metrics: dict[str, Any] = {"worst_relative_feature_uncertainty": worst_relative}
    signed_gain = features.get(
        "static_gain",
        features.get("input_gain", features.get("acceleration_gain")),
    )
    signed_controller_gain = controller.parameters.get(
        "kp",
        controller.parameters.get("Kp_virtual", controller.parameters.get("gain")),
    )
    signed_feedback_ok = (
        signed_gain is None
        or signed_controller_gain is None
        or float(signed_gain) * float(signed_controller_gain) > 0.0
    )
    if signed_gain is not None:
        gain_item = (feature_artifact.get("features") or {}).get("static_gain") or (
            feature_artifact.get("features") or {}
        ).get("input_gain")
        interval = (
            gain_item.get("uncertainty", {}) if isinstance(gain_item, Mapping) else {}
        )
        if interval:
            signed_feedback_ok &= not (
                float(interval.get("lower_bound", signed_gain))
                <= 0.0
                <= float(interval.get("upper_bound", signed_gain))
            )
    checks["signed_feedback"] = "pass" if signed_feedback_ok else "fail"
    if not signed_feedback_ok:
        reasons.append(
            "controller action sign disagrees with the measured input action"
        )
    if family in {
        "decentralized_channel_PI",
        "static_decoupler_then_PI",
        "lag_dynamic_decoupler_then_PI",
    }:
        matrix = np.asarray(
            [
                [
                    features.get("local_gain_k11", 1.0),
                    features.get("local_gain_k12", 0.0),
                ],
                [
                    features.get("local_gain_k21", 0.0),
                    features.get("local_gain_k22", 1.0),
                ],
            ]
        )
        condition = float(features.get("gain_matrix_condition", np.linalg.cond(matrix)))
        metrics["gain_matrix_condition"] = condition
        stability_ok = (
            math.isfinite(condition)
            and condition <= 50.0
            and abs(float(np.linalg.det(matrix))) > 1e-8
        )
        if not stability_ok:
            reasons.append(
                "the measured 2x2 gain map is singular or too ill-conditioned"
            )
    elif family == "cascaded_control":
        required = {"unstable_mode_rate", "angular_input_gain"}
        stability_ok = required <= set(features)
        recoverability = "conditional"
        if not stability_ok:
            reasons.append(
                "unstable balance route lacks internal-mode rate or input-gain evidence"
            )
    elif family == "self_excitation_energy_guarded_PID":
        stability_ok = (
            features.get("base_decay_rate", 0.0) > 0.0
            or features.get("capture_damping", 0.0) > 0.0
        )
        recoverability = "conditional"
        if not stability_ok:
            reasons.append(
                "no positive capture or decay evidence supports the guarded handoff"
            )
    else:
        gain = float(
            features.get(
                "static_gain",
                features.get("input_gain", features.get("acceleration_gain", 1.0)),
            )
        )
        bandwidth = abs(
            controller.parameters.get(
                "target_bandwidth",
                controller.parameters.get("reference_filter_rate", 0.5),
            )
        )
        loop_scale = gain * float(
            controller.parameters.get(
                "kp",
                controller.parameters.get(
                    "Kp_virtual", controller.parameters.get("gain", 1.0)
                ),
            )
        )
        metrics.update(loop_scale=loop_scale, target_bandwidth_rad_s=bandwidth)
        stability_ok = (
            math.isfinite(loop_scale)
            and math.isfinite(bandwidth)
            and 0.0 < loop_scale < 100.0
            and bandwidth > 0.0
        )
        if family in {"two_dof_PI", "phase_guarded_2dof_PI"}:
            guard = features.get(
                "phase_guard_frequency", features.get("nmp_zero_rate_estimate")
            )
            if guard is not None:
                stability_ok &= bandwidth <= max(float(guard), 1e-6)
        if not stability_ok:
            reasons.append("conservative task-band loop screen failed")
    sample_time_s = float(task.get("sample_time_s", 0.01))
    if not math.isfinite(sample_time_s) or sample_time_s <= 0.0:
        sample_time_s = 0.01
    backend_specs = (
        (
            "parameterized_linear_stability",
            _parameterized_linear_backend(controller, features, sample_time_s),
            "parameterized public-model pole or delay envelope failed",
        ),
        (
            "frequency_mimo_stability",
            _mimo_frequency_backend(controller, features, sample_time_s),
            "MIMO return-difference, decoupling, or sampled-pole guard failed",
        ),
        (
            "local_nonlinear_stability",
            _local_nonlinear_backend(controller, features, sample_time_s),
            "local equilibrium or bounded-region pole guard failed",
        ),
    )
    active_backends = []
    for check_name, backend, failure_reason in backend_specs:
        if backend is None:
            checks[check_name] = "not_applicable"
            continue
        backend_passed, backend_metrics = backend
        active_backends.append(check_name)
        checks[check_name] = "pass" if backend_passed else "fail"
        metrics.update(backend_metrics)
        stability_ok &= backend_passed
        if not backend_passed:
            reasons.append(failure_reason)
    metrics["qualification_backends"] = active_backends
    checks["stability"] = "pass" if stability_ok else "fail"
    checks["recoverability"] = recoverability
    validated_region: dict[str, list[float]] = {}
    output_min, output_max = task.get("output_min"), task.get("output_max")
    state_stop = task.get("state_stop")
    for name in controller.measured_signals:
        if output_min is not None and output_max is not None:
            lower_region, upper_region = float(output_min), float(output_max)
        elif state_stop is not None and math.isfinite(float(state_stop)):
            lower_region, upper_region = -abs(float(state_stop)), abs(float(state_stop))
        else:
            continue
        if lower_region < upper_region:
            validated_region[name] = [lower_region, upper_region]
    region_ok = len(validated_region) == len(controller.measured_signals)
    checks["validated_region"] = "pass" if region_ok else "fail"
    if not region_ok:
        reasons.append(
            "no finite nonempty measured-signal validation region is declared"
        )

    runtime_ok = False
    try:
        runtime = ControllerRuntime(controller)
        measured = dict.fromkeys(controller.measured_signals, 0.0)
        reference: float | dict[str, float]
        if set(runtime.reference_names) == {"x_m", "z_m"}:
            reference = {"x_m": 0.05, "z_m": 0.05}
        elif len(runtime.reference_names) > 1:
            reference = dict.fromkeys(runtime.reference_names, 0.05)
        else:
            reference = 0.05
        sample = runtime.step(measured, reference, 0.01)
        runtime_ok = all(
            math.isfinite(float(value)) for value in sample.control.values()
        )
        if (
            runtime_ok
            and family in {"PI", "delay_aware_PI"}
            and signed_gain is not None
        ):
            tau = max(float(features.get("dominant_time_constant", 1.0)), 1e-6)
            dt = min(0.01, tau / 50.0)
            y = 0.0
            runtime.reset()
            for _ in range(max(50, int(5.0 * tau / dt))):
                sample = runtime.step({controller.measured_signals[0]: y}, 0.05, dt)
                u = sample.control[controller.control_inputs[0]]
                y += dt * (-y + float(signed_gain) * u) / tau
                if not math.isfinite(y) or abs(y) > max(abs(state_stop or 1e6), 1e6):
                    runtime_ok = False
                    break
    except (TypeError, ValueError, OverflowError):
        runtime_ok = False
    checks["actual_runtime_trajectories"] = "pass" if runtime_ok else "fail"
    if not runtime_ok:
        reasons.append("typed runtime could not execute a bounded public-model probe")
    hard_pass = (
        not reasons
        and bounds_ok
        and domains_ok
        and uncertainty_ok
        and stability_ok
        and signed_feedback_ok
        and region_ok
        and runtime_ok
    )
    if hard_pass:
        status = OFFLINE_QUALIFIED
        scope = [
            "isolated_software_evaluation",
            "bounded_first_trial_after_physical_preflight",
        ]
        next_action = "freeze the qualified candidate and run an isolated evaluation"
    elif (
        stability_ok
        and bounds_ok
        and domains_ok
        and not feature_artifact.get("missing_feature_ids")
    ):
        status = DIAGNOSTIC_TRIAL_ONLY
        scope = ["isolated_software_diagnostic_evaluation"]
        next_action = (
            "run software-only diagnostics or collect the named missing evidence"
        )
    else:
        status = NOT_QUALIFIED
        scope = []
        next_action = "do not freeze; reduce bandwidth or collect the named evidence"
    result = {
        "qualification_version": QUALIFICATION_VERSION,
        "status": status,
        "limited_trial_authorized": status == OFFLINE_QUALIFIED,
        "authorization_scope": scope,
        "checks": checks,
        "metrics": metrics,
        "reasons": reasons,
        "next_action": next_action,
        "controller_fingerprint": controller.fingerprint,
        "feature_artifact_fingerprint": feature_artifact.get("artifact_fingerprint"),
        "protocol_fingerprint": protocol.get("protocol_fingerprint"),
        "route_id": route.get("route_id"),
        "validated_region": validated_region,
        "claims_forbidden": [
            "physical safety certification",
            "global stability",
            "performance optimality",
        ],
    }
    result["qualification_fingerprint"] = fingerprint(result)
    return result


__all__ = [
    "DIAGNOSTIC_TRIAL_ONLY",
    "NOT_QUALIFIED",
    "OFFLINE_QUALIFIED",
    "qualify_controller",
]
