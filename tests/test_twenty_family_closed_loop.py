from __future__ import annotations

import pytest

from cfdc.controllers.execution import ControllerRuntime, runtime_contract
from cfdc.controllers.kernel_synthesis import synthesize_controller
from cfdc.controllers.qualification import OFFLINE_QUALIFIED, qualify_controller
from cfdc.kernel.contracts import ControllerFreeze, fingerprint
from cfdc.kernel.controllers import ControllerIR
from cfdc.kernel.execution_contract import execution_request
from cfdc.kernel.judging import judge_packet
from cfdc.kernel.route_catalog import (
    controller_contract,
    implemented_controller_families,
)
from cfdc.sim.execution import (
    CartPoleLocalPlant,
    LinearPlant,
    OscillatorPlant,
    StaticMapPlant,
    VTOLLocalPlant,
    simulate_trial,
)

MIMO = {
    "decentralized_channel_PI",
    "static_decoupler_then_PI",
    "lag_dynamic_decoupler_then_PI",
}
MODAL = {
    "local_fixed_PID",
    "scheduled_damping_PID",
    "self_excitation_energy_guarded_PID",
}
INVERSE = {
    "local_PI_without_inverse",
    "partial_inverse_then_PI",
    "deadzone_right_inverse_then_PI",
}


def family_context(family: str):
    contract = controller_contract(family)
    assert contract is not None
    required_features = set(contract.get("controller_features", ())) | set(
        contract.get("route_guard_features", ())
    )
    values = dict.fromkeys(required_features, 1.0)
    values.update(
        static_gain=1.0,
        dominant_time_constant=1.0,
        time_constant=1.0,
        input_gain=1.0,
        signed_input_gain=1.0,
        acceleration_gain=1.0,
        derivative_gain=1.0,
        velocity_gain=1.0,
        drag_rate=1.0,
        natural_frequency=1.0,
        dominant_natural_frequency=1.0,
        modal_frequency=1.0,
        damping_ratio=0.7,
        base_decay_rate=0.2,
        quadratic_decay_rate=0.1,
        small_amplitude_decay_rate=-0.1,
        zero_decay_crossing_amplitude=0.5,
        capture_damping=0.2,
        unstable_mode_rate=1.0,
        angular_input_gain=1.0,
        control_authority=2.0,
        sensing_actuation_adequacy=1.0,
        static_map_linear_coefficient=1.0,
        static_map_cubic_coefficient=0.1,
        local_invertibility_margin=0.5,
        inverse_input_lower=-1.0,
        inverse_input_upper=1.0,
        positive_deadzone_bound=0.1,
        negative_deadzone_bound=0.1,
        outer_static_slope=1.0,
        virtual_noise_guard=0.001,
        phase_guard_frequency=2.0,
        low_order_residual_index=0.05,
        amplitude_dependence_index=0.05,
        minimum_decay_rate=0.1,
        damping_change_fraction=0.05,
        release_model_fit_r2=0.99,
        pairing_bootstrap_probability=0.99,
        gain_matrix_condition=1.2,
        static_inverse_amplification=1.2,
        inband_static_decoupler_residual=0.05,
        dynamic_decoupler_fit_residual=0.05,
        dynamic_inverse_peak_amplification=1.2,
        task_band_magnitude_at_crossover=1.0,
        parasitic_mode_frequency=4.0,
        slow_lag_rate=1.0,
        fast_lag_rate=4.0,
        local_gain_k11=1.0,
        local_gain_k12=0.1,
        local_gain_k21=0.1,
        local_gain_k22=1.0,
        paired_time_constant_1=1.0,
        paired_time_constant_2=1.0,
    )
    for row in (1, 2):
        for column in (1, 2):
            values[f"dynamic_map_base_{row}{column}"] = float(row == column)
            for basis in (1, 2, 3):
                values[f"dynamic_map_lag{basis}_{row}{column}"] = 0.0
    if family in MIMO:
        measured, controls = ["y1", "y2"], ["u1", "u2"]
    elif family in MODAL:
        measured, controls = ["position", "velocity"], ["u"]
    elif family == "cascaded_control":
        measured, controls = ["x", "x_dot", "theta", "theta_dot"], ["u"]
    else:
        measured, controls = ["y"], ["u"]
    task = {
        "measured_signals": measured,
        "control_inputs": controls,
        "control_input": controls[0],
        "input_min": -10.0,
        "input_max": 10.0,
        "output_min": -5.0,
        "output_max": 5.0,
        "state_stop": 10.0,
        "target_bandwidth_rad_s": 0.25,
    }
    artifact = {
        "features": {
            key: {
                "value": value,
                "uncertainty": {
                    "lower_bound": value - max(abs(value) * 1e-4, 1e-8),
                    "upper_bound": value + max(abs(value) * 1e-4, 1e-8),
                },
            }
            for key, value in values.items()
        },
        "missing_feature_ids": [],
        "quality": {"passed": True},
        "artifact_fingerprint": f"public-features-{family}",
    }
    route = {
        "route_id": f"verified:{family}",
        "profile_id": "mimo_2x2_coupled" if family in MIMO else "first_order_lag",
        "controller_contract_id": family,
        "feature_ids": sorted(required_features),
        "capability_gap": None,
    }
    return task, artifact, route


def plant_for(family: str):
    if family in MIMO:
        return LinearPlant.from_transfer_matrix(
            [
                [([1.0], [1.0, 1.0]), ([0.1], [1.0, 1.0])],
                [([0.1], [1.0, 1.0]), ([1.0], [1.0, 1.0])],
            ],
            inputs=("u1", "u2"),
            outputs=("y1", "y2"),
        )
    if family in MODAL:
        return OscillatorPlant(1.0, 0.2, 0.1, 1.0)
    if family == "cascaded_control":
        return CartPoleLocalPlant()
    if family in INVERSE:
        return StaticMapPlant(1.0, 1.0, cubic=0.1)
    return LinearPlant.from_transfer_matrix(
        [[([1.0], [1.0, 1.0])]], inputs=("u",), outputs=("y",)
    )


def frozen_trial(family: str, controller: ControllerIR, task: dict):
    measured = list(task["measured_signals"])
    controls = list(task["control_inputs"])
    binding = {"provider_id": "matrix", "provider_version": "1"}
    freeze = ControllerFreeze(
        session_id=f"family-{family}",
        task_fingerprint=f"task-{family}",
        controller=controller.to_dict(),
        evidence_fingerprints=(f"evidence-{family}",),
        runtime_contract={
            **runtime_contract(family),
            "tracked_signals": (
                ["y1", "y2"]
                if family in MIMO
                else ["position"]
                if family in MODAL
                else ["x"]
                if family == "cascaded_control"
                else ["y"]
            ),
            "measured_signals": measured,
            "control_inputs": controls,
            "input_bounds": {name: [-10.0, 10.0] for name in controls},
            "output_bounds": {name: [-5.0, 5.0] for name in measured},
            "state_bounds": {name: [-5.0, 5.0] for name in measured},
            "controller_state_bounds": {},
            "provider_bindings": {"evaluation": binding},
        },
        evaluation_contract={
            "task_type": "local_setpoint_hold",
            "references": {
                name: 0.1
                for name in (
                    ["y1", "y2"]
                    if family in MIMO
                    else ["position"]
                    if family in MODAL
                    else ["x"]
                    if family == "cascaded_control"
                    else ["y"]
                )
            },
            "sample_time_s": 0.02,
            "horizon_s": 20.0,
            "final_abs_error_max": 0.1,
            "overshoot_max": 1.0,
            "settling_time_max_s": 20.0,
            "hold_duration_min_s": 0.1,
            "trial_manifest": {
                "development": [
                    {"trial_id": "d0", "scenario_id": "nominal", "seed": 1}
                ],
                "fresh_confirmation": [
                    {"trial_id": "f0", "scenario_id": "nominal", "seed": 2}
                ],
            },
        },
        source_version="twenty-family-matrix/v1",
    ).to_dict()
    request = execution_request(freeze, "development")
    trial = simulate_trial(request, request["trials"][0], plant_for(family))
    packet = {
        "packet_version": "cfdc-evaluation-packet/v2.0",
        "session_id": freeze["session_id"],
        "task_fingerprint": freeze["task_fingerprint"],
        "freeze_fingerprint": freeze["freeze_fingerprint"],
        "evidence_fingerprints": freeze["evidence_fingerprints"],
        "provider_id": "matrix",
        "provider_version": "1",
        "evaluation_split": "development",
        "trials": [trial],
    }
    packet["packet_fingerprint"] = fingerprint(packet)
    result = judge_packet(freeze, packet)
    assert any(
        abs(value) > 1e-10
        for values in trial["trajectory"]["control_inputs"].values()
        for value in values
    )
    return result


@pytest.mark.parametrize("family", implemented_controller_families())
def test_each_registered_family_synthesizes_qualifies_executes_and_is_judged(family):
    task, artifact, route = family_context(family)
    controller, audit = synthesize_controller(task, route, artifact)
    qualification = qualify_controller(
        controller,
        task=task,
        route=route,
        feature_artifact=artifact,
        protocol={"protocol_fingerprint": f"protocol-{family}"},
    )

    assert audit["status"] == "consistent"
    assert qualification["status"] == OFFLINE_QUALIFIED
    assert qualification["checks"]["actual_runtime_trajectories"] == "pass"
    assert frozen_trial(family, controller, task)["status"] == "performance_met"


@pytest.mark.parametrize("family", implemented_controller_families())
def test_each_registered_family_has_a_family_relevant_rejection(family):
    task, artifact, route = family_context(family)
    controller, _ = synthesize_controller(task, route, artifact)
    raw = controller.to_dict()
    raw.pop("controller_fingerprint")
    parameters = raw["parameters"]
    structurally_invalid = family in MIMO | {
        "lead_lag_series",
        "partial_inverse_then_PI",
        "self_excitation_energy_guarded_PID",
        "cascaded_control",
        "notch_then_PI",
    }
    if family in MIMO:
        prefix = (
            "dynamic_map_base"
            if family == "lag_dynamic_decoupler_then_PI"
            else "input_map"
        )
        for name in list(parameters):
            if name.startswith(prefix):
                parameters[name] = 1.0
    elif family == "lead_lag_series":
        parameters["lead_pole_rate"] = parameters["lead_zero_rate"]
    elif family == "partial_inverse_then_PI":
        parameters["inverse_input_upper"] = parameters["inverse_input_lower"]
    elif family == "self_excitation_energy_guarded_PID":
        parameters["capture_damping_gain"] = 0.0
    elif family == "cascaded_control":
        parameters["inner_target_rate"] = -1.0
    elif family == "notch_then_PI":
        parameters["notch_center_rad_s"] = 0.0
    elif "kp" in parameters:
        parameters["kp"] *= -1.0
    elif "Kp_virtual" in parameters:
        parameters["Kp_virtual"] *= -1.0
    else:
        parameters["gain"] *= -1.0
    if structurally_invalid:
        with pytest.raises(ValueError):
            rejected = ControllerIR.from_mapping(raw)
            ControllerRuntime(rejected)
        return

    gain_name = (
        "kp"
        if "kp" in parameters
        else "Kp_virtual"
        if "Kp_virtual" in parameters
        else "gain"
    )
    magnitude = max(abs(float(parameters[gain_name])), 1.0)
    raw["parameter_domains"][gain_name] = [-2.0 * magnitude, 2.0 * magnitude]
    rejected = ControllerIR.from_mapping(raw)
    qualification = qualify_controller(
        rejected,
        task=task,
        route=route,
        feature_artifact=artifact,
        protocol={"protocol_fingerprint": f"protocol-{family}"},
    )
    assert qualification["status"] != OFFLINE_QUALIFIED
    assert qualification["checks"]["signed_feedback"] == "fail"


def test_cascaded_control_synthesizes_and_executes_declared_vtol_local_chart():
    task, artifact, route = family_context("cascaded_control")
    task.update(
        measured_signals=[
            "x_m",
            "z_m",
            "pitch_rad",
            "x_velocity_m_s",
            "z_velocity_m_s",
            "pitch_rate_rad_s",
        ],
        control_inputs=["thrust_n", "torque_n_m"],
        control_input="thrust_n",
        input_min=-20.0,
        input_max=20.0,
        workspace={
            "local_equilibrium": {
                "hover_thrust_n": 9.81,
                "vertical_input_gain": 1.0,
            }
        },
    )
    controller, _ = synthesize_controller(task, route, artifact)
    assert controller.parameters["hover_thrust"] == pytest.approx(9.81)
    qualification = qualify_controller(
        controller,
        task=task,
        route=route,
        feature_artifact=artifact,
        protocol={"protocol_fingerprint": "protocol-vtol"},
    )
    assert qualification["status"] == OFFLINE_QUALIFIED

    binding = {"provider_id": "matrix", "provider_version": "1"}
    freeze = ControllerFreeze(
        session_id="family-cascaded-vtol",
        task_fingerprint="task-cascaded-vtol",
        controller=controller.to_dict(),
        evidence_fingerprints=("evidence-cascaded-vtol",),
        runtime_contract={
            **runtime_contract("cascaded_control"),
            "tracked_signals": ["x_m", "z_m"],
            "measured_signals": list(controller.measured_signals),
            "control_inputs": list(controller.control_inputs),
            "input_bounds": {
                "thrust_n": [0.0, 20.0],
                "torque_n_m": [-10.0, 10.0],
            },
            "output_bounds": {"x_m": [-1.0, 1.0], "z_m": [-1.0, 1.0]},
            "state_bounds": {name: [-1.0, 1.0] for name in controller.measured_signals},
            "controller_state_bounds": {},
            "provider_bindings": {"evaluation": binding},
        },
        evaluation_contract={
            "task_type": "local_setpoint_hold",
            "references": {"x_m": 0.0, "z_m": 0.0},
            "sample_time_s": 0.01,
            "horizon_s": 0.5,
            "final_abs_error_max": 0.01,
            "overshoot_max": 0.01,
            "settling_time_max_s": 0.1,
            "hold_duration_min_s": 0.25,
            "trial_manifest": {
                "development": [
                    {"trial_id": "d0", "scenario_id": "near_hover", "seed": 1}
                ],
                "fresh_confirmation": [
                    {"trial_id": "f0", "scenario_id": "near_hover", "seed": 2}
                ],
            },
        },
        source_version="twenty-family-matrix/v1",
    ).to_dict()
    request = execution_request(freeze, "development")
    trial = simulate_trial(request, request["trials"][0], VTOLLocalPlant())
    packet = {
        "packet_version": "cfdc-evaluation-packet/v2.0",
        "session_id": freeze["session_id"],
        "task_fingerprint": freeze["task_fingerprint"],
        "freeze_fingerprint": freeze["freeze_fingerprint"],
        "evidence_fingerprints": freeze["evidence_fingerprints"],
        "provider_id": "matrix",
        "provider_version": "1",
        "evaluation_split": "development",
        "trials": [trial],
    }
    packet["packet_fingerprint"] = fingerprint(packet)
    assert judge_packet(freeze, packet)["status"] == "performance_met"
