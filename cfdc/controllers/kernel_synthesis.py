"""Deterministic synthesis for the versioned CFDC route catalog."""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

import numpy as np

from cfdc.kernel.controllers import ControllerIR
from cfdc.kernel.route_catalog import (
    canonical_controller_family,
    controller_contract,
    controller_family_for_profile,
)


def _values(artifact: Mapping[str, Any]) -> dict[str, float]:
    raw = artifact.get("features", artifact)
    result: dict[str, float] = {}
    if isinstance(raw, Mapping):
        for key, item in raw.items():
            value = item.get("value") if isinstance(item, Mapping) else item
            try:
                number = float(value)
            except (TypeError, ValueError):
                continue
            if math.isfinite(number):
                result[str(key)] = number
    return result


def _positive(features: Mapping[str, float], *names: str, default: float) -> float:
    for name in names:
        value = features.get(name)
        if value is not None and math.isfinite(value) and abs(value) > 1e-9:
            return abs(value)
    return default


def _base_parameters(
    family: str, f: Mapping[str, float], task: Mapping[str, Any]
) -> dict[str, float]:
    gain = _positive(
        f,
        "static_gain",
        "input_gain",
        "acceleration_gain",
        "derivative_gain",
        default=1.0,
    )
    tau = _positive(f, "dominant_time_constant", "time_constant", default=1.0)
    wn = _positive(
        f,
        "natural_frequency",
        "dominant_natural_frequency",
        "modal_frequency",
        default=1.0 / tau,
    )
    zeta = float(np.clip(f.get("damping_ratio", 0.7), 0.05, 1.5))
    bandwidth = float(task.get("target_bandwidth_rad_s") or min(1.0 / tau, 0.35 * wn))
    bandwidth = max(bandwidth, 0.01)
    inverse_gain = 1.0 / gain
    pi = {
        "kp": 0.6 * inverse_gain / max(tau * bandwidth, 0.2),
        "ki": 0.25 * inverse_gain / max(tau**2 * bandwidth, 0.2),
        "reference_filter_rate": bandwidth,
    }
    if family in {"PI", "delay_aware_PI"}:
        if family == "delay_aware_PI":
            pi["kp"] *= 0.65
            pi["ki"] *= 0.5
        return pi
    if family == "notch_then_PI":
        return {
            **pi,
            "notch_center_rad_s": _positive(f, "parasitic_mode_frequency", default=wn),
            "notch_zero_damping": 0.08,
            "notch_pole_damping": 0.35,
        }
    if family == "two_dof_pid":
        return {
            "feedforward_gain": inverse_gain,
            "kp": 1.2 * zeta * wn * inverse_gain,
            "ki": 0.25 * wn**2 * inverse_gain,
            "kd": 0.12 * inverse_gain,
            "reference_filter_rate": bandwidth,
            "derivative_filter_rate": max(5.0 * bandwidth, wn),
        }
    if family == "P_integrator":
        return {
            "kp": 0.5 * bandwidth * inverse_gain,
            "reference_filter_rate": bandwidth,
        }
    if family == "PD_integrator":
        return {
            "kp": 0.5 * bandwidth**2 * inverse_gain,
            "kd": 1.2 * bandwidth * inverse_gain,
            "reference_filter_rate": bandwidth,
            "derivative_filter_rate": 5.0 * bandwidth,
        }
    if family == "lead_lag_series":
        slow = _positive(f, "slow_lag_rate", default=1.0 / tau)
        fast = max(_positive(f, "fast_lag_rate", default=4.0 / tau), 1.2 * slow)
        return {
            "gain": inverse_gain,
            "lead_zero_rate": slow,
            "lead_pole_rate": fast,
            "lag_zero_rate": max(0.1 * slow, 1e-3),
            "lag_pole_rate": slow,
        }
    if family == "two_dof_PI":
        return {"feedforward_gain": inverse_gain, **pi}
    if family in {
        "local_PI_without_inverse",
        "partial_inverse_then_PI",
        "deadzone_right_inverse_then_PI",
    }:
        base = {
            "Kp_virtual": 0.6 * bandwidth,
            "Ki_virtual": 0.2 * bandwidth**2,
            "target_bandwidth": bandwidth,
        }
        if family == "local_PI_without_inverse":
            return {**base, "reference_feedforward": 1.0, "map_linear": inverse_gain}
        if family == "partial_inverse_then_PI":
            return {
                **base,
                "map_linear": inverse_gain,
                "map_cubic": float(f.get("map_cubic", 0.0)),
            }
        return {
            **base,
            "positive_deadzone": max(f.get("positive_deadzone", 0.01), 0.0),
            "negative_deadzone": max(f.get("negative_deadzone", 0.01), 0.0),
            "outer_slope": inverse_gain,
            "virtual_noise_guard": max(f.get("virtual_noise_guard", 0.005), 1e-6),
        }
    if family in {"reduced_low_order_PI", "phase_guarded_2dof_PI"}:
        return {
            **pi,
            "target_bandwidth": min(
                bandwidth, _positive(f, "phase_guard_frequency", default=bandwidth)
            ),
        }
    if family == "local_fixed_PID":
        return {
            "kp": 1.2 * zeta * wn * inverse_gain,
            "ki": 0.1 * wn**2 * inverse_gain,
            "kd": 0.15 * inverse_gain,
            "feedforward": inverse_gain,
            "input_gain_estimate": gain,
            "target_bandwidth": bandwidth,
        }
    if family == "scheduled_damping_PID":
        return {
            "kp": 1.2 * zeta * wn * inverse_gain,
            "ki": 0.1 * wn**2 * inverse_gain,
            "kd": 0.15 * inverse_gain,
            "feedforward": inverse_gain,
            "input_gain_estimate": gain,
            "base_decay": _positive(f, "base_decay_rate", default=zeta * wn),
            "quadratic_decay": max(f.get("quadratic_decay_rate", 0.01), 1e-6),
            "desired_damping": max(0.15, zeta),
            "target_bandwidth": bandwidth,
            "antiwindup_gain": 1.0,
        }
    if family == "cascaded_control":
        unstable = _positive(f, "unstable_mode_rate", default=wn)
        input_gain = _positive(f, "angular_input_gain", "input_gain", default=gain)
        return {
            "inner_kp": 2.0 * unstable**2 / input_gain,
            "inner_kd": 2.4 * unstable / input_gain,
            "inner_target_rate": 2.0 * unstable,
            "outer_target_rate": 0.25 * unstable,
            "outer_damping": 0.9,
            "internal_reference_limit": 0.2,
            "reference_acceleration_scale": 1.0,
        }
    if family in {"decentralized_channel_PI", "static_decoupler_then_PI"}:
        matrix = np.asarray(
            [
                [f.get("local_gain_k11", 1.0), f.get("local_gain_k12", 0.0)],
                [f.get("local_gain_k21", 0.0), f.get("local_gain_k22", 1.0)],
            ],
            dtype=float,
        )
        mapping = (
            np.eye(2)
            if family == "decentralized_channel_PI"
            else np.linalg.pinv(matrix)
        )
        result = {
            "target_bandwidth": bandwidth,
            "kp_1": bandwidth,
            "kp_2": bandwidth,
            "ki_1": 0.25 * bandwidth**2,
            "ki_2": 0.25 * bandwidth**2,
        }
        result.update(
            {
                f"input_map_{row + 1}{column + 1}": float(mapping[row, column])
                for row in range(2)
                for column in range(2)
            }
        )
        return result
    if family == "lag_dynamic_decoupler_then_PI":
        result = {
            "target_bandwidth": bandwidth,
            "kp_1": bandwidth,
            "kp_2": bandwidth,
            "ki_1": 0.25 * bandwidth**2,
            "ki_2": 0.25 * bandwidth**2,
            "dynamic_filter_tau_1": 0.2 / bandwidth,
            "dynamic_filter_tau_2": 0.7 / bandwidth,
            "dynamic_filter_tau_3": 2.0 / bandwidth,
        }
        for row in range(1, 3):
            for column in range(1, 3):
                result[f"dynamic_map_base_{row}{column}"] = f.get(
                    f"dynamic_map_base_{row}{column}", float(row == column)
                )
                for basis in range(1, 4):
                    result[f"dynamic_map_lag{basis}_{row}{column}"] = f.get(
                        f"dynamic_map_lag{basis}_{row}{column}", 0.0
                    )
        return result
    if family == "self_excitation_energy_guarded_PID":
        return {
            "capture_damping_gain": max(0.1, zeta),
            "capture_target_damping_ratio": 0.4,
            "kp": wn**2 * inverse_gain,
            "ki": 0.05 * wn**2 * inverse_gain,
            "kd": 1.2 * wn * inverse_gain,
            "feedforward": inverse_gain,
            "input_gain_estimate": gain,
            "target_bandwidth": bandwidth,
            "antiwindup_gain": 1.0,
            "handoff_amplitude": 0.1,
            "handoff_hysteresis": 0.02,
            "handoff_dwell_s": max(2.0 / wn, 0.1),
            "envelope_filter_rate": wn,
        }
    raise ValueError(f"controller_synthesis_not_implemented: {family}")


def _domain(value: float) -> tuple[float, float]:
    width = max(abs(value) * 0.75, 0.1)
    lower, upper = value - width, value + width
    if value >= 0:
        lower = max(0.0, lower)
        if lower == upper:
            upper += max(0.1, abs(value))
    return float(lower), float(upper)


def synthesize_controller(
    task: Mapping[str, Any],
    route: Mapping[str, Any],
    feature_artifact: Mapping[str, Any],
) -> tuple[ControllerIR, dict[str, Any]]:
    if feature_artifact.get("missing_feature_ids") or not bool(
        (feature_artifact.get("quality") or {}).get("passed", False)
    ):
        raise ValueError("feature_quality_required_for_controller_synthesis")
    family = str(
        route.get("controller_contract_id")
        or controller_family_for_profile(str(route.get("profile_id")))
        or route.get("controller_template_id")
        or ""
    )
    family = canonical_controller_family(family)
    contract = controller_contract(family)
    if contract is None:
        raise ValueError(f"controller_contract_not_registered: {family}")
    parameters = _base_parameters(family, _values(feature_artifact), task)
    required = {str(item) for item in contract.get("required_parameters", ())}
    missing = sorted(required - set(parameters))
    if missing:
        raise ValueError(
            "controller_required_parameters_missing: " + ", ".join(missing)
        )
    domains = {key: _domain(value) for key, value in parameters.items()}
    input_min, input_max = task.get("input_min"), task.get("input_max")
    if input_min is None or input_max is None:
        raise ValueError("controller_input_bounds_required")
    measured = tuple(str(item) for item in task.get("measured_signals", ()))
    inputs = tuple(
        str(item) for item in task.get("control_inputs") or (task.get("control_input"),)
    )
    state_limits = {}
    if task.get("output_min") is not None and task.get("output_max") is not None:
        state_limits = {
            name: (float(task["output_min"]), float(task["output_max"]))
            for name in measured
        }
    ir = ControllerIR(
        family=family,
        measured_signals=measured,
        control_inputs=inputs,
        parameters=parameters,
        parameter_domains=domains,
        output_bounds=(float(input_min), float(input_max)),
        state_limits=state_limits,
        stop_conditions=(
            f"stop when state magnitude reaches {task.get('state_stop')}",
        ),
        integral_handling="anti_windup"
        if any("ki" in name.casefold() for name in parameters)
        else "none",
    )
    audit = {
        "status": "consistent",
        "family": family,
        "contract_label": contract.get("label_cn"),
        "required_parameters": sorted(required),
        "active_terms": sorted(parameters),
        "synthesis_features": list(contract.get("controller_features", ())),
        "route_guard_features": list(contract.get("route_guard_features", ())),
        "runtime_contract": contract.get("runtime_contract", {}),
    }
    return ir, audit


__all__ = ["synthesize_controller"]
