from __future__ import annotations

import numpy as np

from cfdc.models import ExperimentPrimitive, ExperimentTrace, SimulationExperimentRecord, SimulationProfile
from cfdc.sim.cartpole import CartpoleParams
from cfdc.sim.traces import bounded_scan_trace, hover_trace, modal_trace, pulse_trace, step_trace, vtol_pulse_trace
from cfdc.sim.vtol import VtolParams


_PROFILE_PARAMS: dict[str, dict[str, float]] = {
    "first_order_lag": {"static_gain": 2.0, "time_constant": 5.0},
    "first_order_lag_with_delay": {"static_gain": 1.5, "time_constant": 8.0, "dead_time": 2.0},
    "second_order_oscillator": {"natural_frequency": 3.0, "damping_ratio": 0.18, "input_gain": 1.0},
    "double_integrator": {"input_gain": 0.8},
    "nmp_inverse_response": {"static_gain": 1.0, "time_constant": 6.0, "inverse_response_severity": 0.25},
    "generic_unstable_higher_order": {"natural_frequency": 2.4, "input_gain": 0.7},
    "mimo_2x2_coupled": {"coupling_gain": 0.45},
}


def profile_nominal_parameters(profile: SimulationProfile) -> dict[str, float]:
    if profile.profile_id == "underactuated_cartpole":
        params = CartpoleParams()
        return {"natural_frequency": params.free_cart_natural_frequency_down_rad_s}
    if profile.profile_id == "vtol_cascaded":
        params = VtolParams()
        return {"hover_thrust": params.hover_thrust_n, "angular_acceleration_gain": 1.0 / params.pitch_inertia_kg_m2, "lateral_coupling_gain": 9.81}
    return dict(_PROFILE_PARAMS[profile.profile_id])


def _noise(signal: np.ndarray, repeat_index: int, scale: float) -> np.ndarray:
    rng = np.random.default_rng(1200 + repeat_index)
    return signal + rng.normal(0.0, scale, size=signal.shape)


def run_profile_experiments(profile: SimulationProfile, repeat_index: int) -> list[SimulationExperimentRecord]:
    params = profile_nominal_parameters(profile)
    records: list[SimulationExperimentRecord] = []
    features = set(profile.required_feature_ids)
    if {"static_gain", "time_constant", "dead_time", "inverse_response_severity"} & features:
        t, u, y = step_trace(params["static_gain"], params["time_constant"], params.get("dead_time", 0.0), params.get("inverse_response_severity", 0.0))
        estimates = [feature for feature in ["static_gain", "time_constant", "dead_time", "inverse_response_severity"] if feature in features]
        records.append(SimulationExperimentRecord(primitive=ExperimentPrimitive.RAMP_STEP, estimates=estimates, repeat_index=repeat_index, trace=ExperimentTrace(time_s=t.tolist(), signals={"input": u.tolist(), "output": _noise(y, repeat_index, 0.001).tolist()}), instruction_title="Automatic normalized step simulation"))
    modal = [feature for feature in ["natural_frequency", "damping_ratio"] if feature in features]
    if modal:
        duration_s = 14.0 if profile.profile_id == "second_order_oscillator" else 8.0
        t, y = modal_trace(params["natural_frequency"], params.get("damping_ratio", 0.08), duration_s=duration_s, sample_count=int(duration_s * 200))
        records.append(SimulationExperimentRecord(primitive=ExperimentPrimitive.FREE_DECAY, estimates=modal, repeat_index=repeat_index, trace=ExperimentTrace(time_s=t.tolist(), signals={"free_response": _noise(y, repeat_index, 0.0005).tolist()}), instruction_title="Automatic normalized free-decay simulation"))
    if "input_gain" in features:
        t, u, a = pulse_trace(params["input_gain"])
        records.append(SimulationExperimentRecord(primitive=ExperimentPrimitive.PULSE, estimates=["input_gain"], repeat_index=repeat_index, trace=ExperimentTrace(time_s=t.tolist(), signals={"input": u.tolist(), "acceleration": _noise(a, repeat_index, 0.0005).tolist()}), instruction_title="Automatic normalized pulse simulation"))
    if "hover_thrust" in features:
        t, thrust, lift = hover_trace(params["hover_thrust"])
        records.append(SimulationExperimentRecord(primitive=ExperimentPrimitive.HOVER_THRUST, estimates=["hover_thrust"], repeat_index=repeat_index, trace=ExperimentTrace(time_s=t.tolist(), signals={"thrust": thrust.tolist(), "lift": lift.tolist()}), instruction_title="Automatic ground-contact thrust ramp"))
    if {"angular_acceleration_gain", "lateral_coupling_gain"} & features:
        t, u, angular, tilt, lateral = vtol_pulse_trace(params["angular_acceleration_gain"], params["lateral_coupling_gain"])
        records.append(SimulationExperimentRecord(primitive=ExperimentPrimitive.PULSE, estimates=[feature for feature in ["angular_acceleration_gain", "lateral_coupling_gain"] if feature in features], repeat_index=repeat_index, trace=ExperimentTrace(time_s=t.tolist(), signals={"input": u.tolist(), "angular_acceleration": angular.tolist(), "tilt": tilt.tolist(), "coupled_output": lateral.tolist()}), instruction_title="Automatic grounded VTOL pulse simulation"))
    if "local_gain_matrix" in features:
        gain_matrix = [[2.0, 0.7], [0.5, 1.6]]
        time_s = np.linspace(0.0, 12.0, 1200)
        u1 = np.zeros_like(time_s); u2 = np.zeros_like(time_s)
        u1[(time_s >= 1.0) & (time_s < 4.0)] = 0.4
        u2[(time_s >= 6.0) & (time_s < 9.0)] = 0.4
        y1 = gain_matrix[0][0] * u1 + gain_matrix[0][1] * u2
        y2 = gain_matrix[1][0] * u1 + gain_matrix[1][1] * u2
        records.append(SimulationExperimentRecord(primitive=ExperimentPrimitive.BOUNDED_SCAN, estimates=["local_gain_matrix", "local_time_constant", "pairing_indicator"], repeat_index=repeat_index, trace=ExperimentTrace(time_s=time_s.tolist(), signals={"input_1": u1.tolist(), "input_2": u2.tolist(), "output_1": y1.tolist(), "output_2": y2.tolist()}), instruction_title="Automatic 2x2 one-at-a-time scan"))
    return records
