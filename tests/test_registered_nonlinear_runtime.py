from __future__ import annotations

import json

import numpy as np
import pytest
from pydantic import ValidationError

from cfdc.lab import RegisteredControllerSpec, StabilityDecision
from cfdc.models import RegisteredNonlinearModelSpec
from cfdc.sim.registered_runtime import (
    NONLINEAR_SOFTWARE_MODEL_BOUNDARY,
    RegisteredNonlinearValidationResult,
    evaluate_tail_contraction,
    linearize_registered_closed_loop,
    list_registered_controllers,
    list_registered_templates,
    run_registered_scenario,
    run_registered_validation,
    validate_registered_equilibrium,
)

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


def cartpole_model(**changes: float) -> RegisteredNonlinearModelSpec:
    parameters = CARTPOLE_PARAMETERS | changes
    return RegisteredNonlinearModelSpec(
        template_id="underactuated_cartpole",
        parameters=parameters,
        initial_state={
            "position_m": 0.0,
            "velocity_m_s": 0.0,
            "angle_rad": 0.0,
            "angular_rate_rad_s": 0.0,
        },
        input_signal_ids=["force_n"],
        output_signal_ids=["position_m", "angle_rad"],
    )


def vtol_model(**changes: float) -> RegisteredNonlinearModelSpec:
    parameters = VTOL_PARAMETERS | changes
    return RegisteredNonlinearModelSpec(
        template_id="vtol_cascaded",
        parameters=parameters,
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
    )


def cartpole_controller(
    kp: float = 18.15, kd: float = 8.47
) -> RegisteredControllerSpec:
    return RegisteredControllerSpec(
        controller_id="cartpole_cascaded",
        parameters={"kp": kp, "kd": kd, "kp_y": 0.02, "kd_y": 0.05},
        reference={"position_m": 0.0},
        feedforward={"position_reference_prefilter": 1.0},
        configuration={"theta_reference_limit_rad": 0.08},
    )


def vtol_controller(**changes: float) -> RegisteredControllerSpec:
    parameters = {
        "kp_z": 1.44,
        "kd_z": 2.16,
        "kp_theta": 0.3698,
        "kd_theta": 0.1548,
        "kp_y": 0.34,
        "kd_y": 0.70,
    } | changes
    return RegisteredControllerSpec(
        controller_id="vtol_cascaded",
        parameters=parameters,
        reference={"x_m": 0.0, "z_m": 0.0},
        feedforward={
            "hover_thrust_n": (
                VTOL_PARAMETERS["mass_kg"] * VTOL_PARAMETERS["gravity_m_s2"]
            )
        },
        configuration={"tilt_reference_limit_rad": 0.48},
    )


def test_closed_registry_lists_only_audited_templates_and_controllers():
    assert list_registered_templates() == [
        "underactuated_cartpole",
        "vtol_cascaded",
    ]
    assert list_registered_controllers() == {
        "underactuated_cartpole": ["cartpole_cascaded"],
        "vtol_cascaded": ["vtol_cascaded"],
    }


def test_registered_inputs_reject_code_unknown_keys_and_wrong_pairing():
    with pytest.raises(ValidationError, match="extra_forbidden"):
        RegisteredControllerSpec(
            controller_id="cartpole_cascaded",
            parameters={"kp": 1.0},
            python_code="import os",
        )
    with pytest.raises(ValueError, match="must use exact keys"):
        validate_registered_equilibrium(
            cartpole_model(),
            RegisteredControllerSpec(
                controller_id="cartpole_cascaded",
                parameters={
                    "kp": 18.15,
                    "kd": 8.47,
                    "kp_y": 0.02,
                    "kd_y": 0.05,
                    "unknown_gain": 1.0,
                },
            ),
        )
    with pytest.raises(ValueError, match="not registered for template"):
        validate_registered_equilibrium(cartpole_model(), vtol_controller())
    with pytest.raises(ValueError, match="equilibrium_state"):
        validate_registered_equilibrium(
            cartpole_model(),
            cartpole_controller(),
            equilibrium_state=[0.0, 0.0],
        )


def test_registered_controller_snapshot_is_complete_and_deeply_immutable():
    controller = cartpole_controller()
    with pytest.raises(TypeError, match="immutable"):
        controller.parameters["kp"] = 20.0
    with pytest.raises(TypeError, match="immutable"):
        controller.configuration.update({"theta_reference_limit_rad": 0.1})

    payload = controller.model_dump()
    payload["reference"] = {}
    with pytest.raises(ValidationError, match="reference must use exact keys"):
        RegisteredControllerSpec.model_validate(payload)
    payload = controller.model_dump()
    payload["feedforward"] = {"unknown_prefilter": 1.0}
    with pytest.raises(ValidationError, match="feedforward must match"):
        RegisteredControllerSpec.model_validate(payload)
    payload = controller.model_dump()
    payload["configuration"] = {}
    with pytest.raises(ValidationError, match="configuration must use exact keys"):
        RegisteredControllerSpec.model_validate(payload)


def test_registered_signal_units_reject_unknown_or_conflicting_declarations():
    model = cartpole_model().model_copy(
        update={
            "signal_units": {
                "position_m": "ampere",
                "velocity_m_s": "m/s",
                "angle_rad": "rad",
                "angular_rate_rad_s": "rad/s",
                "force_n": "degC",
                "bogus": "byte",
            }
        }
    )
    with pytest.raises(ValueError, match="signal_units conflict"):
        validate_registered_equilibrium(model, cartpole_controller())


def test_missing_parameters_and_unknown_template_fail_closed():
    payload = cartpole_model().model_dump()
    payload["parameters"].pop("gravity_m_s2")
    with pytest.raises(ValidationError, match="complete parameter set"):
        RegisteredNonlinearModelSpec(**payload)
    payload = cartpole_model().model_dump()
    payload["template_id"] = "arbitrary_ode"
    payload["equation"] = "dx = eval(user_input)"
    with pytest.raises(ValidationError):
        RegisteredNonlinearModelSpec(**payload)


def test_cartpole_position_reference_prefilter_is_optional_and_defaults_to_one():
    controller = cartpole_controller().model_copy(update={"feedforward": {}})
    result = validate_registered_equilibrium(cartpole_model(), controller)
    assert result.status == "stable"


@pytest.mark.parametrize(
    ("model", "controller", "state_count"),
    [
        (cartpole_model(), cartpole_controller(), 4),
        (vtol_model(), vtol_controller(), 6),
    ],
)
def test_equilibrium_linearization_is_finite_stable_and_has_expected_shape(
    model, controller, state_count
):
    result = validate_registered_equilibrium(model, controller)
    assert np.asarray(result.jacobian).shape == (state_count, state_count)
    assert len(result.poles) == state_count
    assert max(pole.real for pole in result.poles) < -1e-6
    assert result.status == "stable"
    assert NONLINEAR_SOFTWARE_MODEL_BOUNDARY in result.evidence


def test_central_jacobian_agrees_with_independent_directional_difference():
    model = cartpole_model()
    controller = cartpole_controller()
    jacobian = np.asarray(
        linearize_registered_closed_loop(model, controller), dtype=float
    )
    equilibrium = np.zeros(4)
    epsilon = 3e-6
    direction = np.array([0.3, -0.2, 0.4, -0.1])
    plus = linearize_registered_closed_loop(
        model,
        controller,
        equilibrium_state=(equilibrium + epsilon * direction).tolist(),
        return_derivative_only=True,
    )
    minus = linearize_registered_closed_loop(
        model,
        controller,
        equilibrium_state=(equilibrium - epsilon * direction).tolist(),
        return_derivative_only=True,
    )
    directional = (np.asarray(plus) - np.asarray(minus)) / (2.0 * epsilon)
    assert directional == pytest.approx(jacobian @ direction, rel=3e-4, abs=3e-6)


def test_vtol_central_jacobian_agrees_with_independent_directional_difference():
    model = vtol_model()
    controller = vtol_controller()
    jacobian = np.asarray(
        linearize_registered_closed_loop(model, controller), dtype=float
    )
    equilibrium = np.zeros(6)
    epsilon = 3e-6
    direction = np.array([0.2, -0.1, 0.3, -0.2, 0.1, -0.25])
    plus = linearize_registered_closed_loop(
        model,
        controller,
        equilibrium_state=(equilibrium + epsilon * direction).tolist(),
        return_derivative_only=True,
    )
    minus = linearize_registered_closed_loop(
        model,
        controller,
        equilibrium_state=(equilibrium - epsilon * direction).tolist(),
        return_derivative_only=True,
    )
    directional = (np.asarray(plus) - np.asarray(minus)) / (2.0 * epsilon)
    assert directional == pytest.approx(jacobian @ direction, rel=3e-4, abs=3e-6)


def test_invalid_equilibrium_residual_is_rejected():
    with pytest.raises(ValueError, match="equilibrium residual"):
        validate_registered_equilibrium(
            cartpole_model(),
            cartpole_controller(),
            equilibrium_state=[0.0, 0.0, 0.05, 0.0],
        )


def test_nonfinite_equilibrium_derivative_is_rejected(monkeypatch):
    import cfdc.sim.registered_runtime as runtime

    monkeypatch.setattr(
        runtime,
        "_closed_loop_derivative",
        lambda *args, **kwargs: np.full(4, np.nan),
    )
    with pytest.raises(ValueError, match="derivative is non-finite"):
        validate_registered_equilibrium(cartpole_model(), cartpole_controller())


def test_nonfinite_equilibrium_jacobian_is_rejected(monkeypatch):
    import cfdc.sim.registered_runtime as runtime

    monkeypatch.setattr(
        runtime,
        "linearize_registered_closed_loop",
        lambda *args, **kwargs: np.full((4, 4), np.nan).tolist(),
    )
    with pytest.raises(ValueError, match="Jacobian is non-finite"):
        validate_registered_equilibrium(cartpole_model(), cartpole_controller())


def test_exact_local_pole_boundary_is_inconclusive(monkeypatch):
    import cfdc.sim.registered_runtime as runtime

    monkeypatch.setattr(
        runtime,
        "linearize_registered_closed_loop",
        lambda *args, **kwargs: np.diag([-1e-6, -2.0, -3.0, -4.0]).tolist(),
    )
    result = validate_registered_equilibrium(cartpole_model(), cartpole_controller())
    assert result.status == "inconclusive"


@pytest.mark.parametrize(
    ("model", "controller"),
    [
        (cartpole_model(), cartpole_controller()),
        (vtol_model(), vtol_controller()),
    ],
)
def test_full_validation_runs_exactly_five_repeatable_scenarios(model, controller):
    first = run_registered_validation(model, controller)
    second = run_registered_validation(model, controller)
    assert first.stability.status == "stable"
    assert len(first.stability.scenario_evidence) == 5
    assert len(first.traces) == 5
    assert all(item.passed for item in first.stability.scenario_evidence)
    assert first.model_dump_json() == second.model_dump_json()


def test_registered_stability_contract_requires_all_poles_and_unique_scenarios():
    result = run_registered_validation(cartpole_model(), cartpole_controller())
    payload = result.stability.model_dump()
    payload["poles"] = []
    with pytest.raises(ValidationError, match="report every local"):
        StabilityDecision.model_validate(payload)

    payload = result.stability.model_dump()
    payload["scenario_evidence"][-1]["scenario_id"] = payload["scenario_evidence"][0][
        "scenario_id"
    ]
    with pytest.raises(ValidationError, match="exact unique"):
        StabilityDecision.model_validate(payload)


def test_registered_aggregate_rejects_mismatched_trace_and_equilibrium_identity():
    result = run_registered_validation(cartpole_model(), cartpole_controller())

    payload = result.model_dump()
    first_key = next(iter(payload["traces"]))
    payload["traces"]["unexpected_scenario"] = payload["traces"].pop(first_key)
    with pytest.raises(ValidationError, match="trace keys must match"):
        RegisteredNonlinearValidationResult.model_validate(payload)

    payload = result.model_dump()
    payload["equilibrium"]["template_id"] = "vtol_cascaded"
    with pytest.raises(ValidationError, match="template IDs must match"):
        RegisteredNonlinearValidationResult.model_validate(payload)

    payload = result.model_dump()
    payload["equilibrium"]["poles"][0]["real"] += 0.1
    with pytest.raises(ValidationError, match="local poles must match"):
        RegisteredNonlinearValidationResult.model_validate(payload)


def test_cartpole_audited_gain_sequence_first_passes_at_third_seed():
    first = run_registered_validation(cartpole_model(), cartpole_controller(15.0, 7.0))
    second = run_registered_validation(cartpole_model(), cartpole_controller(16.5, 7.7))
    third = run_registered_validation(
        cartpole_model(), cartpole_controller(18.15, 8.47)
    )
    assert first.stability.status != "stable"
    assert second.stability.status != "stable"
    assert third.stability.status == "stable"
    assert first.stability.trajectory_finite
    assert first.stability.trajectory_bounded


def test_zero_and_sign_flipped_gains_are_not_declared_stable():
    zero = run_registered_validation(cartpole_model(), cartpole_controller(0.0, 0.0))
    flipped = run_registered_validation(
        cartpole_model(), cartpole_controller(-18.15, -8.47)
    )
    assert zero.stability.status in {"unstable", "inconclusive"}
    assert flipped.stability.status == "unstable"


def test_overlarge_vtol_gains_report_sustained_saturation():
    result = run_registered_validation(
        vtol_model(),
        vtol_controller(
            kp_z=1e8,
            kd_z=1e8,
            kp_theta=1e8,
            kd_theta=1e8,
            kp_y=1e8,
            kd_y=1e8,
        ),
    )
    assert result.stability.status == "unstable"
    assert result.stability.saturation_fraction > 0.10
    assert "sustained_actuator_saturation" in result.stability.violations


def test_hard_bound_failure_stops_early_and_retains_finite_samples():
    result = run_registered_scenario(
        cartpole_model(cart_position_limit_m=0.05),
        cartpole_controller(),
        "position_and_angle_positive",
    )
    assert not result.evidence.passed
    assert result.evidence.hard_failure
    assert result.evidence.trajectory_finite
    assert len(result.trace.time_s) < 20_000
    assert any(event.kind == "hard_bound_violation" for event in result.trace.events)
    assert all(
        np.isfinite(value)
        for values in result.trace.states.values()
        for value in values
    )


def test_initial_hard_bound_is_checked_before_controller_execution(monkeypatch):
    import cfdc.sim.registered_runtime as runtime

    real_command = runtime._controller_command
    calls = 0

    def fail_if_scenario_state(entry, model, controller, state):
        nonlocal calls
        if np.linalg.norm(state) > 0.01:
            calls += 1
            raise AssertionError("controller must not run outside hard bounds")
        return real_command(entry, model, controller, state)

    monkeypatch.setattr(runtime, "_controller_command", fail_if_scenario_state)
    result = run_registered_scenario(
        cartpole_model(cart_position_limit_m=0.05),
        cartpole_controller(),
        "position_and_angle_positive",
    )
    assert calls == 0
    assert result.trace.time_s == []
    assert result.evidence.hard_failure
    assert not result.evidence.trajectory_bounded
    assert result.trace.events[0].kind == "hard_bound_violation"


def test_controller_overflow_terminates_with_a_finite_empty_prefix(monkeypatch):
    import cfdc.sim.registered_runtime as runtime

    real_command = runtime._controller_command

    def overflow_away_from_equilibrium(entry, model, controller, state):
        if np.linalg.norm(state) > 0.01:
            raise OverflowError("forced finite-arithmetic overflow")
        return real_command(entry, model, controller, state)

    monkeypatch.setattr(runtime, "_controller_command", overflow_away_from_equilibrium)
    result = run_registered_scenario(
        cartpole_model(), cartpole_controller(), "angle_positive"
    )
    assert result.evidence.hard_failure
    assert not result.evidence.trajectory_finite
    assert result.trace.time_s == []
    assert result.trace.events[0].kind == "non_finite"


def test_tail_contraction_threshold_is_inclusive_without_division_artifacts():
    assert evaluate_tail_contraction(1.0, 0.9) == pytest.approx(0.1)
    assert evaluate_tail_contraction(1.0, 0.9000001) < 0.1
    assert evaluate_tail_contraction(1.0, 0.8999999) > 0.1
    assert evaluate_tail_contraction(0.0, 0.0) == 1.0
    assert evaluate_tail_contraction(0.0, 1e-14) == 0.0


def test_scenario_trace_records_requested_and_applied_actuators_and_boundary():
    result = run_registered_scenario(
        vtol_model(), vtol_controller(), "combined_positive"
    )
    assert set(result.trace.requested_controls) == {"thrust_n", "torque_n_m"}
    assert set(result.trace.applied_controls) == {"thrust_n", "torque_n_m"}
    assert result.evidence.tail_error_envelope_contraction >= 0.1
    assert NONLINEAR_SOFTWARE_MODEL_BOUNDARY in result.evidence.evidence
    json.loads(result.model_dump_json())
