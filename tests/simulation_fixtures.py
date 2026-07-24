from __future__ import annotations

from cfdc.lab import (
    PControllerSpec,
    RegisteredControllerSpec,
    SimulationRunConfig,
    confirm_model,
    create_free_input_session,
    make_tuning_profile,
    set_initial_controller,
    set_pending_model,
)
from cfdc.models import (
    RegisteredNonlinearModelSpec,
    TransferFunctionModelSpec,
)
from cfdc.sim import registered_run_envelope


CARTPOLE_PARAMETERS = {
    "cart_mass_kg": 0.5,
    "pole_mass_kg": 0.2,
    "com_length_m": 0.3,
    "pole_inertia_kg_m2": 0.006,
    "cart_friction_n_s_m": 0.1,
    "gravity_m_s2": 9.8,
    "force_limit_n": 10.0,
    "cart_position_limit_m": 2.4,
}
VTOL_PARAMETERS = {
    "mass_kg": 1.2,
    "pitch_inertia_kg_m2": 0.035,
    "gravity_m_s2": 9.81,
    "linear_drag_n_s_m": 0.08,
    "pitch_damping_n_m_s": 0.015,
    "thrust_min_n": 0.0,
    "thrust_max_n": 18.0,
    "torque_limit_n_m": 0.9,
}


def cartpole_model() -> RegisteredNonlinearModelSpec:
    return RegisteredNonlinearModelSpec(
        template_id="underactuated_cartpole",
        parameters=CARTPOLE_PARAMETERS,
        initial_state={
            "position_m": 0.0,
            "velocity_m_s": 0.0,
            "angle_rad": 0.05,
            "angular_rate_rad_s": 0.0,
        },
        input_signal_ids=["force_n"],
        output_signal_ids=["position_m", "angle_rad"],
        signal_units={
            "position_m": "m",
            "velocity_m_s": "m/s",
            "angle_rad": "rad",
            "angular_rate_rad_s": "rad/s",
            "force_n": "N",
        },
        parameter_uncertainty={
            "cart_mass_kg": 0.1,
            "pole_mass_kg": 0.1,
            "com_length_m": 0.1,
        },
    )


def cartpole_controller(
    *,
    kp: float = 15.0,
    kd: float = 7.0,
) -> RegisteredControllerSpec:
    return RegisteredControllerSpec(
        controller_id="cartpole_cascaded",
        parameters={
            "kp": kp,
            "kd": kd,
            "kp_y": 0.02,
            "kd_y": 0.05,
        },
        reference={"position_m": 0.0},
        feedforward={"position_reference_prefilter": 1.0},
        configuration={"theta_reference_limit_rad": 0.08},
    )


def vtol_model() -> RegisteredNonlinearModelSpec:
    return RegisteredNonlinearModelSpec(
        template_id="vtol_cascaded",
        parameters=VTOL_PARAMETERS,
        initial_state={
            "x_m": 0.0,
            "z_m": 0.0,
            "pitch_rad": 0.0,
            "x_velocity_m_s": 0.0,
            "z_velocity_m_s": 0.0,
            "pitch_rate_rad_s": 0.0,
        },
        input_signal_ids=["thrust_n", "torque_n_m"],
        output_signal_ids=["x_m", "z_m", "pitch_rad"],
        signal_units={
            "x_m": "m",
            "z_m": "m",
            "pitch_rad": "rad",
            "x_velocity_m_s": "m/s",
            "z_velocity_m_s": "m/s",
            "pitch_rate_rad_s": "rad/s",
            "thrust_n": "N",
            "torque_n_m": "N*m",
        },
    )


def continuous_siso_session():
    model = TransferFunctionModelSpec(
        numerator=[1.0],
        denominator=[5.0, 1.0],
        input_signal_id="u",
        output_signal_id="y",
        input_units="V",
        output_units="m",
    )
    controller = PControllerSpec(kp=0.05)
    session = create_free_input_session()
    session = set_pending_model(session, model, expected_revision=0)
    session = confirm_model(session, expected_revision=1)
    return set_initial_controller(
        session,
        controller,
        tuning_profile=make_tuning_profile(
            controller,
            tunable_parameters=["kp"],
            parameter_bindings={"kp": "kp"},
            open_loop_behavior="stable",
            profile_id="test-continuous-siso-v1",
        ),
        run_config=SimulationRunConfig(
            reference={"y": 0.1},
            horizon_s=30.0,
            sample_time_s=0.05,
            actuator_bounds={"u": (-2.0, 2.0)},
            output_bounds={"y": (-1.0, 1.0)},
        ),
        expected_revision=2,
    )


def cartpole_session():
    model = cartpole_model()
    controller = cartpole_controller()
    session = create_free_input_session()
    session = set_pending_model(session, model, expected_revision=0)
    session = confirm_model(session, expected_revision=1)
    return set_initial_controller(
        session,
        controller,
        tuning_profile=make_tuning_profile(
            controller,
            tunable_parameters=["kp", "kd", "kp_y", "kd_y"],
            parameter_bindings={
                "kp": "parameters.kp",
                "kd": "parameters.kd",
                "kp_y": "parameters.kp_y",
                "kd_y": "parameters.kd_y",
            },
            open_loop_behavior="unstable",
            profile_id="test-cartpole-v1",
        ),
        run_config=SimulationRunConfig.model_validate(
            registered_run_envelope(model)
        ),
        expected_revision=2,
    )
