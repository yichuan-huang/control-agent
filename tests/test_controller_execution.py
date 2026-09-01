"""Numerical execution checks independent of plant truth or task thresholds."""

import math

import pytest

from cfdc.kernel.controllers import ControllerIR

PI = {"kp": 2.0, "ki": 3.0, "reference_filter_rate": 1.0}
MODAL = {
    "kp": 2.0,
    "ki": 1.0,
    "kd": 3.0,
    "feedforward": 0.5,
    "input_gain_estimate": 2.0,
    "target_bandwidth": 1.0,
    "antiwindup_gain": 2.0,
}
CASCADE = {
    "inner_kp": 3.0,
    "inner_kd": 2.0,
    "inner_target_rate": 2.0,
    "outer_target_rate": 1.0,
    "outer_damping": 0.5,
    "internal_reference_limit": 0.2,
    "reference_acceleration_scale": 2.0,
}
CHANNEL = {
    "target_bandwidth": 1.0,
    "kp_1": 2.0,
    "kp_2": -3.0,
    "ki_1": 1.0,
    "ki_2": -2.0,
    "input_map_11": 1.0,
    "input_map_12": 0.0,
    "input_map_21": 0.0,
    "input_map_22": 1.0,
}


def ir(family="PI", parameters=None, signals=("y",), inputs=("u",), **kwargs):
    parameters = dict(PI if parameters is None else parameters)
    return ControllerIR(
        family=family,
        measured_signals=signals,
        control_inputs=inputs,
        parameters=parameters,
        parameter_domains={key: (-1e6, 1e6) for key in parameters},
        output_bounds=kwargs.pop("output_bounds", (-100.0, 100.0)),
        integral_handling=kwargs.pop("integral_handling", "anti_windup"),
        **kwargs,
    )


def runtime(*args, **kwargs):
    try:
        from cfdc.controllers.execution import ControllerRuntime
    except ModuleNotFoundError:
        pytest.fail("typed per-sample controller execution is not implemented")
    return ControllerRuntime(*args, **kwargs)


def test_pi_uses_exact_reference_filter_and_pre_update_integral():
    controller = runtime(ir())
    first = controller.step({"y": 0.0}, 1.0, math.log(2))
    assert first.raw_control == pytest.approx({"u": 1.0})
    assert first.state["integral_control"] == pytest.approx(1.5 * math.log(2))
    second = controller.step({"y": 0.0}, 1.0, math.log(2))
    assert second.raw_control["u"] == pytest.approx(1.5 + 1.5 * math.log(2))
    controller.reset()
    assert controller.step({"y": 0.0}, 1.0, math.log(2)).to_dict() == first.to_dict()


def test_negative_ki_cannot_integrate_further_into_negative_saturation():
    controller = runtime(
        ir(parameters={**PI, "kp": -2.0, "ki": -3.0}, output_bounds=(-0.5, 0.5))
    )
    sample = controller.step({"y": -1.0}, 0.0, 0.1)
    assert sample.raw_control == {"u": -2.0}
    assert sample.control == {"u": -0.5}
    assert sample.saturated == {"u": True}
    assert sample.state["integral_control"] == 0.0
    assert any(event["kind"] == "saturation" for event in sample.events)


def test_negative_ki_can_unwind_positive_saturation():
    controller = runtime(ir(parameters={**PI, "ki": -3.0}, output_bounds=(-0.5, 0.5)))
    sample = controller.step({"y": -1.0}, 0.0, 0.1)
    assert sample.raw_control == {"u": 2.0}
    assert sample.state["integral_control"] == pytest.approx(-0.3)


def test_back_calculation_corrects_integral_in_output_units():
    controller = runtime(
        ir(
            parameters={**PI, "kp": -2.0, "ki": -3.0, "antiwindup_gain": 2.0},
            output_bounds=(-0.5, 0.5),
            integral_handling="back_calculation",
        )
    )
    sample = controller.step({"y": -1.0}, 0.0, 0.1)
    assert sample.state["integral_control"] == pytest.approx(0.0)


@pytest.mark.parametrize("dt", [0.0, -1.0, math.nan, math.inf])
def test_invalid_dt_rejected_without_mutating_controller(dt):
    controller = runtime(ir())
    with pytest.raises(ValueError, match="dt"):
        controller.step({"y": 0.0}, 1.0, dt)
    assert controller.step({"y": 0.0}, 1.0, math.log(2)).raw_control[
        "u"
    ] == pytest.approx(1.0)


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_nonfinite_measurement_or_reference_is_rejected(value):
    controller = runtime(ir())
    with pytest.raises(ValueError, match="finite"):
        controller.step({"y": value}, 1.0, 0.1)
    with pytest.raises(ValueError, match="finite"):
        controller.step({"y": 0.0}, {"y": value}, 0.1)


def test_missing_measurement_or_reference_is_rejected():
    controller = runtime(ir())
    with pytest.raises(ValueError, match="measurement.*missing"):
        controller.step({}, 1.0, 0.1)
    with pytest.raises(ValueError, match="reference.*missing"):
        controller.step({"y": 0.0}, {}, 0.1)


def test_missing_command_bounds_are_rejected():
    with pytest.raises(ValueError, match="bounds.*required"):
        runtime(ir(output_bounds=None))


def test_explicit_bounds_must_cover_every_input():
    with pytest.raises(ValueError, match="bounds.*missing"):
        runtime(
            ir("static_decoupler_then_PI", CHANNEL, ("y1", "y2"), ("u1", "u2")),
            input_bounds={"u1": (-1, 1)},
        )


@pytest.mark.parametrize("bounds", [(1, -1), (-math.inf, 1), (0, math.nan)])
def test_invalid_input_bounds_are_rejected(bounds):
    with pytest.raises(ValueError, match="bounds"):
        runtime(ir(), input_bounds={"u": bounds})


def test_missing_required_coefficients_are_rejected():
    with pytest.raises(ValueError, match="ki"):
        runtime(ir(parameters={"kp": 1.0, "reference_filter_rate": 1.0}))
    with pytest.raises(ValueError, match="antiwindup_gain"):
        runtime(ir(integral_handling="back_calculation"))


@pytest.mark.parametrize("family", ["PI", "delay_aware_PI", "reduced_low_order_PI"])
def test_pi_families_execute_signed_integral_control(family):
    controller = runtime(ir(family, {**PI, "target_bandwidth": 0.5}))
    assert controller.step({"y": -1.0}, 0.0, 0.1).raw_control["u"] == 2.0
    assert controller.step({"y": -1.0}, 0.0, 0.1).raw_control["u"] == pytest.approx(2.3)


@pytest.mark.parametrize("family", ["two_dof_PI", "phase_guarded_2dof_PI"])
def test_two_dof_pi_executes_reference_feedforward(family):
    controller = runtime(
        ir(family, {**PI, "feedforward_gain": -4.0, "target_bandwidth": 1.0})
    )
    assert controller.step({"y": 0.0}, 1.0, math.log(2)).raw_control[
        "u"
    ] == pytest.approx(-1.0)


def test_p_integrator_has_no_controller_integral():
    controller = runtime(ir("P_integrator", {"kp": -2.0, "reference_filter_rate": 1.0}))
    assert controller.step({"y": 1.0}, 0.0, 0.1).raw_control == {"u": 2.0}
    assert controller.step({"y": 1.0}, 0.0, 0.1).raw_control == {"u": 2.0}


@pytest.mark.parametrize("family", ["PD_integrator", "two_dof_pid"])
def test_pid_derivative_is_filtered_measurement_without_reference_kick(family):
    controller = runtime(
        ir(
            family,
            {
                **PI,
                "kp": 0.0,
                "ki": 0.0,
                "kd": 2.0,
                "feedforward_gain": 0.0,
                "derivative_filter_rate": math.log(2),
            },
        )
    )
    assert controller.step({"y": 0.0}, 1.0, 1.0).raw_control == {"u": 0.0}
    assert controller.step({"y": 1.0}, 1.0, 1.0).raw_control["u"] == pytest.approx(-1.0)
    assert controller.step({"y": 1.0}, 2.0, 1.0).raw_control["u"] == pytest.approx(-0.5)


def test_reference_weight_changes_p_but_not_integral_error():
    controller = runtime(
        ir("two_dof_PI", {**PI, "feedforward_gain": 0.0, "reference_weight": 0.0})
    )
    sample = controller.step({"y": 0.0}, 1.0, math.log(2))
    assert sample.raw_control == {"u": 0.0}
    assert sample.state["integral_control"] == pytest.approx(1.5 * math.log(2))


def test_lead_lag_transient_and_dc_gain_are_real():
    controller = runtime(
        ir(
            "lead_lag_series",
            {
                "gain": -2.0,
                "lead_zero_rate": 1.0,
                "lead_pole_rate": 4.0,
                "lag_zero_rate": 2.0,
                "lag_pole_rate": 1.0,
            },
        )
    )
    first = controller.step({"y": 0.0}, 1.0, 0.1)
    second = controller.step({"y": 0.0}, 1.0, 0.1)
    assert first.raw_control["u"] == -2.0
    assert -2.0 < second.raw_control["u"] < -1.0
    for _ in range(400):
        sample = controller.step({"y": 0.0}, 1.0, 0.1)
    assert sample.raw_control["u"] == pytest.approx(-1.0, abs=1e-8)


def test_notch_attenuates_its_declared_frequency():
    plain = runtime(ir(parameters={**PI, "kp": 1.0, "ki": 0.0}))
    notch = runtime(
        ir(
            "notch_then_PI",
            {
                **PI,
                "kp": 1.0,
                "ki": 0.0,
                "notch_center_rad_s": 5.0,
                "notch_zero_damping": 0.05,
                "notch_pole_damping": 0.5,
            },
        )
    )
    plain_energy = notch_energy = 0.0
    for i in range(5000):
        y = math.sin(5 * i * 0.01)
        a = plain.step({"y": y}, 0.0, 0.01)
        b = notch.step({"y": y}, 0.0, 0.01)
        if i > 3000:
            plain_energy += a.control["u"] ** 2
            notch_energy += b.control["u"] ** 2
    assert notch_energy < 0.02 * plain_energy


def test_local_pi_divides_virtual_command_by_signed_local_slope():
    controller = runtime(
        ir(
            "local_PI_without_inverse",
            {
                "Kp_virtual": 2.0,
                "Ki_virtual": 1.0,
                "reference_feedforward": 1.0,
                "map_linear": -2.0,
                "target_bandwidth": 1.0,
            },
        )
    )
    sample = controller.step({"y": -1.0}, 0.0, 0.1)
    assert sample.raw_control == {"u": -1.0}
    assert sample.state["integral_control"] == pytest.approx(0.1)


def test_cubic_inverse_stays_in_declared_monotonic_interval():
    parameters = {
        "Kp_virtual": 2.0,
        "Ki_virtual": 0.0,
        "map_linear": 1.0,
        "map_cubic": 1.0,
        "target_bandwidth": 1.0,
        "inverse_input_lower": -2.0,
        "inverse_input_upper": 2.0,
    }
    controller = runtime(ir("partial_inverse_then_PI", parameters))
    assert controller.step({"y": -1.0}, 0.0, 0.1).raw_control["u"] == pytest.approx(1.0)
    sample = controller.step({"y": -100.0}, 0.0, 0.1)
    assert sample.raw_control["u"] == 2.0
    assert any(event["kind"] == "inverse_domain_clipped" for event in sample.events)


def test_nonmonotonic_or_undeclared_cubic_interval_rejected():
    parameters = {
        "Kp_virtual": 2.0,
        "Ki_virtual": 0.0,
        "map_linear": -1.0,
        "map_cubic": 1.0,
        "target_bandwidth": 1.0,
    }
    with pytest.raises(ValueError, match="inverse_input"):
        runtime(ir("partial_inverse_then_PI", parameters))
    with pytest.raises(ValueError, match="monotonic"):
        runtime(
            ir(
                "partial_inverse_then_PI",
                {**parameters, "inverse_input_lower": -2.0, "inverse_input_upper": 2.0},
            )
        )


@pytest.mark.parametrize("y,expected", [(-2.0, 1.3), (2.0, -1.7), (0.01, 0.0)])
def test_deadzone_right_inverse_has_asymmetric_offsets_and_correct_slope(y, expected):
    controller = runtime(
        ir(
            "deadzone_right_inverse_then_PI",
            {
                "Kp_virtual": 1.0,
                "Ki_virtual": 0.0,
                "positive_deadzone": 0.3,
                "negative_deadzone": 0.7,
                "outer_slope": 2.0,
                "virtual_noise_guard": 0.02,
                "target_bandwidth": 1.0,
            },
        )
    )
    assert controller.step({"y": y}, 0.0, 0.1).raw_control["u"] == pytest.approx(
        expected
    )


def test_cascade_uses_outer_position_and_inner_measured_states():
    controller = runtime(
        ir(
            "cascaded_control",
            CASCADE,
            ("position", "velocity", "internal", "internal_rate"),
        )
    )
    sample = controller.step(
        {"position": 0.0, "velocity": 0.0, "internal": 0.1, "internal_rate": 0.2},
        1.0,
        0.1,
    )
    assert sample.state["internal_reference"] == -0.2
    assert sample.raw_control["u"] == pytest.approx(-1.3)


def test_cascade_recognizes_declared_cartpole_signal_names():
    signals = ("position_m", "velocity_m_s", "angle_rad", "angular_rate_rad_s")
    controller = runtime(ir("cascaded_control", CASCADE, signals, ("force_n",)))
    sample = controller.step(
        dict(zip(signals, (0.0, 0.0, 0.1, 0.2))), {"position_m": 1.0}, 0.1
    )
    assert sample.raw_control["force_n"] == pytest.approx(-1.3)


def test_vtol_cascade_requires_and_executes_altitude_loop():
    signals = (
        "x_m",
        "z_m",
        "pitch_rad",
        "x_velocity_m_s",
        "z_velocity_m_s",
        "pitch_rate_rad_s",
    )
    with pytest.raises(ValueError, match="altitude_kp"):
        runtime(ir("cascaded_control", CASCADE, signals, ("thrust_n", "torque_n_m")))
    params = {**CASCADE, "altitude_kp": 4.0, "altitude_kd": 2.0, "hover_thrust": 10.0}
    controller = runtime(
        ir("cascaded_control", params, signals, ("thrust_n", "torque_n_m"))
    )
    sample = controller.step(
        dict(zip(signals, (0.0, 0.5, 0.0, 0.0, 0.2, 0.0))),
        {"x_m": 1.0, "z_m": 1.0},
        0.1,
    )
    assert sample.raw_control == pytest.approx({"thrust_n": 11.6, "torque_n_m": -0.6})


def test_local_pid_uses_measured_velocity_and_back_calculation():
    controller = runtime(
        ir("local_fixed_PID", MODAL, ("position", "velocity"), output_bounds=(-1, 1))
    )
    sample = controller.step({"position": 0.0, "velocity": 1.0}, 1.0, 0.1)
    assert sample.raw_control["u"] == -0.5
    assert sample.state["integral_control"] == pytest.approx(0.1)
    sample = controller.step({"position": -3.0, "velocity": 0.0}, 1.0, 0.1)
    assert sample.raw_control["u"] == pytest.approx(8.6)
    assert sample.state["integral_control"] == pytest.approx(-1.02)


@pytest.mark.parametrize("gain,expected", [(2.0, -0.75), (-2.0, 0.75)])
def test_damping_schedule_uses_amplitude_and_preserves_input_sign(gain, expected):
    params = {
        **MODAL,
        "kp": 0.0,
        "ki": 0.0,
        "feedforward": 0.0,
        "input_gain_estimate": gain,
        "base_decay": 0.0,
        "quadratic_decay": 1.0,
        "desired_damping": 1.0,
    }
    controller = runtime(ir("scheduled_damping_PID", params, ("position", "velocity")))
    assert controller.step({"position": 0.5, "velocity": 1.0}, 0.0, 0.1).raw_control[
        "u"
    ] == pytest.approx(expected)
    assert (
        controller.step({"position": 2.0, "velocity": 1.0}, 0.0, 0.1).raw_control["u"]
        == 0.0
    )


def capture_parameters():
    return {
        **MODAL,
        "capture_damping_gain": -2.0,
        "capture_target_damping_ratio": 0.4,
        "handoff_amplitude": 0.1,
        "handoff_hysteresis": 0.05,
        "handoff_dwell_s": 0.3,
        "envelope_filter_rate": 10.0,
    }


def test_self_excitation_capture_dwell_hold_and_recovery_events():
    controller = runtime(
        ir(
            "self_excitation_energy_guarded_PID",
            capture_parameters(),
            ("position", "velocity"),
        )
    )
    first = controller.step({"position": 0.0, "velocity": 0.2}, 1.0, 0.1)
    assert first.raw_control["u"] == pytest.approx(0.4)
    assert first.state["mode"] == "capture"
    events = []
    for _ in range(10):
        sample = controller.step({"position": 0.0, "velocity": 0.0}, 1.0, 0.1)
        events.extend(sample.events)
    assert sample.state["mode"] == "hold"
    assert sample.raw_control["u"] > 0.0
    assert any(
        event["kind"] == "mode_transition" and event["to"] == "hold" for event in events
    )
    recovered = controller.step({"position": 1.0, "velocity": 0.0}, 1.0, 0.1)
    assert recovered.state["mode"] == "capture"
    assert recovered.raw_control["u"] == 0.0
    assert recovered.state["integral_control"] == 0.0


@pytest.mark.parametrize(
    "family", ["decentralized_channel_PI", "static_decoupler_then_PI"]
)
def test_channel_pi_pairing_uses_each_error_and_per_channel_bounds(family):
    params = {
        **CHANNEL,
        "input_map_11": 0.0,
        "input_map_12": 1.0,
        "input_map_21": -2.0,
        "input_map_22": 0.0,
    }
    controller = runtime(
        ir(family, params, ("y1", "y2"), ("u1", "u2")),
        input_bounds={"u1": (-2.0, 0.0), "u2": (-10.0, 10.0)},
    )
    sample = controller.step({"y1": -1.0, "y2": -2.0}, {"y1": 0.0, "y2": 0.0}, 0.1)
    assert sample.raw_control == {"u1": -6.0, "u2": -4.0}
    assert sample.control == {"u1": -2.0, "u2": -4.0}
    assert sample.state["integral_control_1"] == pytest.approx(0.1)
    assert sample.state["integral_control_2"] == 0.0


def test_static_decoupler_applies_full_matrix():
    params = {**CHANNEL, "input_map_12": 0.5, "input_map_21": -0.5}
    controller = runtime(
        ir("static_decoupler_then_PI", params, ("y1", "y2"), ("u1", "u2"))
    )
    sample = controller.step({"y1": -1.0, "y2": -2.0}, 0.0, 0.1)
    assert sample.raw_control == {"u1": -1.0, "u2": -7.0}


def test_missing_matrix_entry_and_singular_decoupler_rejected():
    params = dict(CHANNEL)
    del params["input_map_12"]
    with pytest.raises(ValueError, match="input_map_12"):
        runtime(ir("static_decoupler_then_PI", params, ("y1", "y2"), ("u1", "u2")))
    with pytest.raises(ValueError, match="singular"):
        runtime(
            ir(
                "static_decoupler_then_PI",
                {**CHANNEL, "input_map_22": 0.0},
                ("y1", "y2"),
                ("u1", "u2"),
            )
        )


def dynamic_parameters():
    params = {
        key: value for key, value in CHANNEL.items() if not key.startswith("input_map_")
    }
    params.update({"ki_1": 0.0, "ki_2": 0.0})
    for i in (1, 2):
        for j in (1, 2):
            params[f"dynamic_map_base_{i}{j}"] = float(i == j)
            for k in (1, 2, 3):
                params[f"dynamic_map_lag{k}_{i}{j}"] = 0.0
    params.update(
        {
            "dynamic_filter_tau_1": 1.0,
            "dynamic_filter_tau_2": 2.0,
            "dynamic_filter_tau_3": 3.0,
            "dynamic_map_lag1_12": 0.5,
        }
    )
    return params


def test_dynamic_decoupler_has_stable_lag_response_and_preserves_dc():
    controller = runtime(
        ir(
            "lag_dynamic_decoupler_then_PI",
            dynamic_parameters(),
            ("y1", "y2"),
            ("u1", "u2"),
        )
    )
    sample = controller.step({"y1": -1.0, "y2": -2.0}, 0.0, math.log(2))
    assert sample.raw_control == {"u1": 5.0, "u2": -6.0}
    sample = controller.step({"y1": -1.0, "y2": -2.0}, 0.0, math.log(2))
    assert sample.raw_control == pytest.approx({"u1": 3.5, "u2": -6.0})
    for _ in range(80):
        sample = controller.step({"y1": -1.0, "y2": -2.0}, 0.0, 5.0)
    assert sample.raw_control == pytest.approx({"u1": 2.0, "u2": -6.0})


def test_dynamic_decoupler_requires_all_lag_entries_and_positive_time_constants():
    params = dynamic_parameters()
    del params["dynamic_map_lag3_21"]
    with pytest.raises(ValueError, match="dynamic_map_lag3_21"):
        runtime(ir("lag_dynamic_decoupler_then_PI", params, ("y1", "y2"), ("u1", "u2")))
    with pytest.raises(ValueError, match="dynamic_filter_tau_1"):
        runtime(
            ir(
                "lag_dynamic_decoupler_then_PI",
                {**dynamic_parameters(), "dynamic_filter_tau_1": 0.0},
                ("y1", "y2"),
                ("u1", "u2"),
            )
        )


def test_typed_controller_snapshot_preserves_fingerprint_and_revalidates_mutation():
    source = ir(output_bounds=(-1, 1))
    controller = runtime(source)
    assert controller.controller.fingerprint == source.fingerprint
    source.parameters["ki"] = 2e6
    with pytest.raises(ValueError, match="out_of_domain"):
        runtime(source)
    assert controller.step({"y": 0.0}, 1.0, math.log(2)).state[
        "integral_control"
    ] == pytest.approx(1.5 * math.log(2))


def test_mapping_fingerprint_mismatch_is_never_ignored():
    source = ir().to_dict()
    source["parameters"]["kp"] = 3.0
    with pytest.raises(ValueError, match="fingerprint_mismatch"):
        runtime(source)


def test_cubic_inverse_roundoff_does_not_freeze_unsaturated_integral():
    parameters = {
        "Kp_virtual": 1.0,
        "Ki_virtual": 1.0,
        "map_linear": 0.3,
        "map_cubic": 0.7,
        "target_bandwidth": 1.0,
        "inverse_input_lower": -2.0,
        "inverse_input_upper": 2.0,
    }
    sample = runtime(ir("partial_inverse_then_PI", parameters)).step(
        {"y": -0.1}, 0.0, 0.1
    )
    assert not sample.saturated["u"]
    assert sample.state["integral_control"] == pytest.approx(0.01)


def test_cubic_inverse_domain_clipping_prevents_integral_windup():
    parameters = {
        "Kp_virtual": 1.0,
        "Ki_virtual": 1.0,
        "map_linear": -1.0,
        "map_cubic": -1.0,
        "target_bandwidth": 1.0,
        "inverse_input_lower": -1.0,
        "inverse_input_upper": 1.0,
    }
    sample = runtime(ir("partial_inverse_then_PI", parameters)).step(
        {"y": -4.0}, 0.0, 0.1
    )
    assert sample.control["u"] == -1.0
    assert sample.state["integral_control"] == 0.0
    assert any(event["kind"] == "inverse_domain_clipped" for event in sample.events)


def test_deadzone_guard_allows_integral_to_build_control_authority():
    parameters = {
        "Kp_virtual": 0.0,
        "Ki_virtual": 1.0,
        "positive_deadzone": 0.3,
        "negative_deadzone": 0.7,
        "outer_slope": -2.0,
        "virtual_noise_guard": 0.02,
        "target_bandwidth": 1.0,
    }
    controller = runtime(ir("deadzone_right_inverse_then_PI", parameters))
    assert controller.step({"y": -0.1}, 0.0, 0.1).control["u"] == 0.0
    for _ in range(5):
        sample = controller.step({"y": -0.1}, 0.0, 0.1)
    assert sample.control["u"] < -0.7


def test_runtime_rejects_unknown_family_and_incomplete_state_interface():
    with pytest.raises(ValueError, match="family_not_registered"):
        runtime(ir("pi"))
    with pytest.raises(ValueError, match="interface_missing"):
        runtime(ir("local_fixed_PID", MODAL, ("position",)))
    with pytest.raises(ValueError, match="interface_missing"):
        runtime(ir("cascaded_control", CASCADE, ("y", "dy", "z", "dz")))


@pytest.mark.parametrize("field", ["kp", "reference_filter_rate"])
def test_invalid_mutated_typed_parameters_cannot_bypass_ir_validation(field):
    source = ir()
    source.parameters[field] = math.nan
    with pytest.raises(ValueError, match="finite"):
        runtime(source)


@pytest.mark.parametrize(
    "measurements,reference,dt",
    [
        ({"y": True}, 1.0, 0.1),
        ({"y": 0.0}, "1", 0.1),
        ({"y": 0.0}, 1.0, True),
        ([], 1.0, 0.1),
    ],
)
def test_invalid_signal_payload_types_are_rejected(measurements, reference, dt):
    with pytest.raises(TypeError):
        runtime(ir()).step(measurements, reference, dt)


def test_nonfinite_generated_command_rejects_sample_without_committing_filters():
    controller = runtime(ir())
    with pytest.raises(ValueError, match="finite"):
        controller.step({"y": 1e308}, 1.0, 0.1)
    assert controller.step({"y": 0.0}, 1.0, math.log(2)).raw_control[
        "u"
    ] == pytest.approx(1.0)


@pytest.mark.parametrize("basis", [1, 2, 3])
def test_every_dynamic_lag_basis_affects_the_actual_transient(basis):
    params = dynamic_parameters()
    params["dynamic_map_lag1_12"] = 0.0
    params[f"dynamic_map_lag{basis}_12"] = 0.5
    controller = runtime(
        ir("lag_dynamic_decoupler_then_PI", params, ("y1", "y2"), ("u1", "u2"))
    )
    dt = basis * math.log(2)
    assert controller.step({"y1": -1.0, "y2": -2.0}, 0.0, dt).raw_control["u1"] == 5.0
    assert controller.step({"y1": -1.0, "y2": -2.0}, 0.0, dt).raw_control[
        "u1"
    ] == pytest.approx(3.5)


def test_matrix_back_calculation_transforms_residual_to_virtual_channel_units():
    params = {
        **CHANNEL,
        "input_map_11": -2.0,
        "input_map_22": 3.0,
        "antiwindup_gain": 2.0,
    }
    controller = runtime(
        ir(
            "static_decoupler_then_PI",
            params,
            ("y1", "y2"),
            ("u1", "u2"),
            integral_handling="back_calculation",
        ),
        input_bounds={"u1": (-1.0, 1.0), "u2": (-2.0, 2.0)},
    )
    sample = controller.step({"y1": -1.0, "y2": -1.0}, 0.0, 0.1)
    assert sample.raw_control == {"u1": -4.0, "u2": -9.0}
    assert sample.state["integral_control_1"] == pytest.approx(-0.2)
    assert sample.state["integral_control_2"] == pytest.approx(4.0 / 15.0)


def test_returned_samples_cannot_mutate_internal_state():
    controller = runtime(ir())
    sample = controller.step({"y": -1.0}, 0.0, 0.1)
    sample.state["integral_control"] = 123.0
    exported = sample.to_dict()
    exported["control"]["u"] = -100.0
    assert sample.control["u"] == 2.0
    assert controller.step({"y": -1.0}, 0.0, 0.1).raw_control["u"] == pytest.approx(2.3)


def test_inverse_chart_and_actuator_bounds_must_intersect():
    parameters = {
        "Kp_virtual": 1.0,
        "Ki_virtual": 1.0,
        "map_linear": 1.0,
        "map_cubic": 1.0,
        "target_bandwidth": 1.0,
        "inverse_input_lower": -2.0,
        "inverse_input_upper": 2.0,
    }
    with pytest.raises(ValueError, match="inverse.*bounds"):
        runtime(
            ir("partial_inverse_then_PI", parameters), input_bounds={"u": (3.0, 5.0)}
        )


def test_duplicate_typed_interface_names_are_rejected():
    with pytest.raises(ValueError, match="duplicate"):
        runtime(ir("static_decoupler_then_PI", CHANNEL, ("y1", "y2"), ("u", "u")))


def test_capture_dwell_counts_observed_intervals_not_first_observation():
    controller = runtime(
        ir(
            "self_excitation_energy_guarded_PID",
            capture_parameters(),
            ("position", "velocity"),
        )
    )
    first = controller.step({"position": 0.0, "velocity": 0.0}, 1.0, 0.1)
    assert first.state["handoff_dwell_elapsed_s"] == 0.0
    assert first.state["mode"] == "capture"
    for _ in range(2):
        sample = controller.step({"position": 0.0, "velocity": 0.0}, 1.0, 0.1)
        assert sample.state["mode"] == "capture"
    sample = controller.step({"position": 0.0, "velocity": 0.0}, 1.0, 0.1)
    assert sample.state["mode"] == "hold"


def test_self_excitation_rejects_zero_capture_damping_authority():
    parameters = {**capture_parameters(), "capture_damping_gain": 0.0}
    with pytest.raises(ValueError, match="capture_damping_gain"):
        runtime(
            ir(
                "self_excitation_energy_guarded_PID",
                parameters,
                ("position", "velocity"),
            )
        )
