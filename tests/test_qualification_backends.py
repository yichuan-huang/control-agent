from __future__ import annotations

from cfdc.controllers.qualification import NOT_QUALIFIED, qualify_controller
from cfdc.kernel.controllers import ControllerIR


def artifact(**values):
    return {
        "features": {
            name: {
                "value": value,
                "uncertainty": {
                    "lower_bound": value - 1e-5,
                    "upper_bound": value + 1e-5,
                },
            }
            for name, value in values.items()
        },
        "missing_feature_ids": [],
        "quality": {"passed": True},
        "artifact_fingerprint": "public",
    }


def task(measured, controls):
    return {
        "measured_signals": list(measured),
        "control_inputs": list(controls),
        "input_min": -10.0,
        "input_max": 10.0,
        "output_min": -5.0,
        "output_max": 5.0,
        "state_stop": 10.0,
        "sample_time_s": 0.02,
    }


def controller(family, measured, controls, parameters):
    return ControllerIR(
        family=family,
        measured_signals=tuple(measured),
        control_inputs=tuple(controls),
        parameters=parameters,
        parameter_domains={name: (-100.0, 100.0) for name in parameters},
        output_bounds=(-10.0, 10.0),
        integral_handling="anti_windup",
    )


def qualify(ir, public):
    return qualify_controller(
        ir,
        task=task(ir.measured_signals, ir.control_inputs),
        route={"route_id": "backend", "feature_ids": list(public["features"])},
        feature_artifact=public,
        protocol={"protocol_fingerprint": "protocol"},
    )


def test_parameterized_linear_backend_rejects_unstable_integral_pole():
    ir = controller(
        "PI",
        ("y",),
        ("u",),
        {"kp": 1.0, "ki": -1.0, "reference_filter_rate": 2.0},
    )
    result = qualify(ir, artifact(static_gain=1.0, dominant_time_constant=1.0))
    assert result["status"] == NOT_QUALIFIED
    assert result["checks"]["parameterized_linear_stability"] == "fail"
    assert result["metrics"]["linear_max_discrete_pole_magnitude"] > 1.0


def test_frequency_mimo_backend_rejects_positive_feedback_integrators():
    parameters = {
        "target_bandwidth": 0.5,
        "kp_1": 0.5,
        "kp_2": 0.5,
        "ki_1": -0.2,
        "ki_2": -0.2,
        "input_map_11": 1.0,
        "input_map_12": 0.0,
        "input_map_21": 0.0,
        "input_map_22": 1.0,
    }
    ir = controller("static_decoupler_then_PI", ("y1", "y2"), ("u1", "u2"), parameters)
    public = artifact(
        local_gain_k11=1.0,
        local_gain_k12=0.1,
        local_gain_k21=0.1,
        local_gain_k22=1.0,
        paired_time_constant_1=1.0,
        paired_time_constant_2=1.2,
        gain_matrix_condition=1.3,
        static_inverse_amplification=1.2,
        inband_static_decoupler_residual=0.05,
    )
    result = qualify(ir, public)
    assert result["status"] == NOT_QUALIFIED
    assert result["checks"]["frequency_mimo_stability"] == "fail"
    assert result["metrics"]["mimo_max_discrete_pole_magnitude"] > 1.0


def test_local_nonlinear_backend_rejects_unstable_pid_integral_mode():
    ir = controller(
        "local_fixed_PID",
        ("position", "velocity"),
        ("u",),
        {
            "kp": 1.0,
            "ki": -0.5,
            "kd": 0.2,
            "feedforward": 1.0,
            "input_gain_estimate": 1.0,
            "target_bandwidth": 0.5,
            "antiwindup_gain": 1.0,
        },
    )
    public = artifact(
        modal_frequency=1.0,
        input_gain=1.0,
        base_decay_rate=0.2,
    )
    result = qualify(ir, public)
    assert result["status"] == NOT_QUALIFIED
    assert result["checks"]["local_nonlinear_stability"] == "fail"
    assert result["metrics"]["local_max_discrete_pole_magnitude"] > 1.0
