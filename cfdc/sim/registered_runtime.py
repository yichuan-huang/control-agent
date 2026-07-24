"""Closed nonlinear runtime for the sixth-stage CFDC stability laboratory.

Only two audited software-model templates are executable here.  No equation,
expression, Python source, or dynamically imported callable crosses this
boundary.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal

import numpy as np
from pydantic import Field, model_validator

from cfdc.lab import (
    ComplexValue,
    NonlinearScenarioEvidence,
    RegisteredControllerSpec,
    SimulationEvent,
    SimulationTrace,
    StabilityDecision,
)
from cfdc.models import RegisteredNonlinearModelSpec
from cfdc.models.schemas import CFDCModel
from cfdc.sim.cartpole import (
    CartpoleParams,
)
from cfdc.sim.cartpole import (
    _dynamics as _cartpole_dynamics,
)
from cfdc.sim.cartpole import (
    _rk4_step as _cartpole_rk4_step,
)
from cfdc.sim.integrators import rk4_step
from cfdc.sim.vtol import VtolParams
from cfdc.sim.vtol import _dynamics as _vtol_dynamics

NONLINEAR_SOFTWARE_MODEL_BOUNDARY = (
    "Local stability evidence applies only to the registered software model "
    "near the declared equilibrium; it is neither global stability nor "
    "real-plant or hardware validation."
)

_POLE_TOLERANCE = 1e-6
_EQUILIBRIUM_RESIDUAL_TOLERANCE = 1e-8
_CONTRACTION_THRESHOLD = 0.10
_SATURATION_LIMIT = 0.10
_TINY_ENVELOPE = 1e-12
_MAX_SAMPLES = 20_000


class RegisteredEquilibriumValidation(CFDCModel):
    template_id: Literal["underactuated_cartpole", "vtol_cascaded"]
    controller_id: Literal["cartpole_cascaded", "vtol_cascaded"]
    equilibrium_state: list[float]
    equilibrium_derivative: list[float]
    residual_norm: float = Field(ge=0.0)
    jacobian: list[list[float]]
    poles: list[ComplexValue]
    status: Literal["stable", "unstable", "inconclusive"]
    evidence: list[str] = Field(min_length=1)


class RegisteredScenarioResult(CFDCModel):
    trace: SimulationTrace
    evidence: NonlinearScenarioEvidence


class RegisteredNonlinearValidationResult(CFDCModel):
    equilibrium: RegisteredEquilibriumValidation
    traces: dict[str, SimulationTrace] = Field(min_length=5, max_length=5)
    stability: StabilityDecision

    @model_validator(mode="after")
    def validate_aggregate_identity(
        self,
    ) -> RegisteredNonlinearValidationResult:
        evidence_ids = {item.scenario_id for item in self.stability.scenario_evidence}
        if set(self.traces) != evidence_ids:
            raise ValueError(
                "registered trace keys must match nonlinear scenario evidence"
            )
        if self.stability.registered_template_id != self.equilibrium.template_id:
            raise ValueError(
                "equilibrium and aggregate stability template IDs must match"
            )
        if self.stability.poles != self.equilibrium.poles:
            raise ValueError("aggregate local poles must match equilibrium validation")
        return self


@dataclass(frozen=True)
class _Scenario:
    scenario_id: str
    perturbation: tuple[float, ...]


@dataclass(frozen=True)
class _RegistryEntry:
    template_id: str
    controller_id: str
    state_names: tuple[str, ...]
    state_units: tuple[str, ...]
    input_names: tuple[str, ...]
    input_units: tuple[str, ...]
    output_names: tuple[str, ...]
    output_units: tuple[str, ...]
    parameter_names: frozenset[str]
    reference_names: frozenset[str]
    feedforward_names: frozenset[str]
    configuration_names: frozenset[str]
    controller_parameter_names: frozenset[str]
    state_error_scales: tuple[float, ...]
    fixed_state_bounds: tuple[tuple[float, float], ...]
    sample_time_s: float
    horizon_s: float
    scenarios: tuple[_Scenario, ...]


_CARTPOLE_ENTRY = _RegistryEntry(
    template_id="underactuated_cartpole",
    controller_id="cartpole_cascaded",
    state_names=(
        "position_m",
        "velocity_m_s",
        "angle_rad",
        "angular_rate_rad_s",
    ),
    state_units=("m", "m/s", "rad", "rad/s"),
    input_names=("force_n",),
    input_units=("N",),
    output_names=("position_m", "angle_rad"),
    output_units=("m", "rad"),
    parameter_names=frozenset(
        {
            "cart_mass_kg",
            "pole_mass_kg",
            "com_length_m",
            "pole_inertia_kg_m2",
            "cart_friction_n_s_m",
            "gravity_m_s2",
            "force_limit_n",
            "cart_position_limit_m",
        }
    ),
    reference_names=frozenset({"position_m"}),
    feedforward_names=frozenset({"position_reference_prefilter"}),
    configuration_names=frozenset({"theta_reference_limit_rad"}),
    controller_parameter_names=frozenset({"kp", "kd", "kp_y", "kd_y"}),
    state_error_scales=(0.1, 0.1, 0.05, 0.1),
    fixed_state_bounds=((-math.inf, math.inf), (-5.0, 5.0), (-0.70, 0.70), (-8.0, 8.0)),
    sample_time_s=0.01,
    horizon_s=5.8,
    scenarios=(
        _Scenario("angle_positive", (0.0, 0.0, 0.05, 0.0)),
        _Scenario("angle_negative", (0.0, 0.0, -0.05, 0.0)),
        _Scenario("position_and_angle_positive", (0.1, 0.0, 0.03, 0.0)),
        _Scenario("position_and_angle_negative", (-0.1, 0.0, -0.03, 0.0)),
        _Scenario("mixed_velocity", (0.0, 0.1, 0.02, -0.1)),
    ),
)

_VTOL_ENTRY = _RegistryEntry(
    template_id="vtol_cascaded",
    controller_id="vtol_cascaded",
    state_names=(
        "x_m",
        "z_m",
        "pitch_rad",
        "x_velocity_m_s",
        "z_velocity_m_s",
        "pitch_rate_rad_s",
    ),
    state_units=("m", "m", "rad", "m/s", "m/s", "rad/s"),
    input_names=("thrust_n", "torque_n_m"),
    input_units=("N", "N*m"),
    output_names=("x_m", "z_m", "pitch_rad"),
    output_units=("m", "m", "rad"),
    parameter_names=frozenset(
        {
            "mass_kg",
            "pitch_inertia_kg_m2",
            "gravity_m_s2",
            "linear_drag_n_s_m",
            "pitch_damping_n_m_s",
            "thrust_min_n",
            "thrust_max_n",
            "torque_limit_n_m",
        }
    ),
    reference_names=frozenset({"x_m", "z_m"}),
    feedforward_names=frozenset({"hover_thrust_n"}),
    configuration_names=frozenset({"tilt_reference_limit_rad"}),
    controller_parameter_names=frozenset(
        {"kp_z", "kd_z", "kp_theta", "kd_theta", "kp_y", "kd_y"}
    ),
    state_error_scales=(0.1, 0.1, 0.05, 0.05, 0.05, 0.03),
    fixed_state_bounds=(
        (-3.0, 3.0),
        (-2.0, 2.0),
        (-0.70, 0.70),
        (-5.0, 5.0),
        (-5.0, 5.0),
        (-8.0, 8.0),
    ),
    sample_time_s=0.005,
    horizon_s=5.8,
    scenarios=(
        _Scenario("lateral_position", (0.1, 0.0, 0.0, 0.0, 0.0, 0.0)),
        _Scenario("altitude", (0.0, 0.1, 0.0, 0.0, 0.0, 0.0)),
        _Scenario("pitch", (0.0, 0.0, 0.05, 0.0, 0.0, 0.0)),
        _Scenario("combined_positive", (0.05, 0.05, 0.03, 0.05, -0.05, 0.0)),
        _Scenario("combined_negative", (-0.05, -0.05, -0.03, -0.05, 0.05, 0.03)),
    ),
)

_REGISTRY: dict[str, _RegistryEntry] = {
    _CARTPOLE_ENTRY.template_id: _CARTPOLE_ENTRY,
    _VTOL_ENTRY.template_id: _VTOL_ENTRY,
}


def list_registered_templates() -> list[str]:
    """Return the deterministic public order of executable templates."""

    return list(_REGISTRY)


def list_registered_controllers(
    template_id: str | None = None,
) -> dict[str, list[str]] | list[str]:
    """List controllers without accepting or importing dynamic registrations."""

    if template_id is not None:
        entry = _entry_for_template(template_id)
        return [entry.controller_id]
    return {name: [entry.controller_id] for name, entry in _REGISTRY.items()}


def _entry_for_template(template_id: str) -> _RegistryEntry:
    try:
        return _REGISTRY[template_id]
    except KeyError as exc:
        raise ValueError(f"unknown registered template: {template_id}") from exc


def _require_exact_keys(actual: set[str], expected: frozenset[str], label: str) -> None:
    if actual != expected:
        raise ValueError(
            f"{label} must use the exact parameter keys; "
            f"missing={sorted(expected - actual)}, "
            f"unknown={sorted(actual - expected)}"
        )


def _resolve(
    model: RegisteredNonlinearModelSpec,
    controller: RegisteredControllerSpec,
) -> _RegistryEntry:
    entry = _entry_for_template(model.template_id)
    if controller.controller_id != entry.controller_id:
        raise ValueError(
            f"controller {controller.controller_id!r} is not registered for "
            f"template {entry.template_id!r}"
        )
    _require_exact_keys(
        set(model.parameters), entry.parameter_names, "model parameters"
    )
    _require_exact_keys(
        set(controller.parameters),
        entry.controller_parameter_names,
        "controller parameters",
    )
    _require_exact_keys(
        set(controller.reference), entry.reference_names, "controller reference"
    )
    if entry.template_id == "underactuated_cartpole":
        if set(controller.feedforward) not in (
            set(),
            set(entry.feedforward_names),
        ):
            raise ValueError(
                "controller feedforward contains unknown keys: "
                f"{sorted(set(controller.feedforward) - entry.feedforward_names)}"
            )
    else:
        _require_exact_keys(
            set(controller.feedforward),
            entry.feedforward_names,
            "controller feedforward",
        )
    _require_exact_keys(
        set(controller.configuration),
        entry.configuration_names,
        "controller configuration",
    )
    if any(value <= 0.0 for value in controller.configuration.values()):
        raise ValueError("controller configuration limits must be positive")
    if tuple(model.input_signal_ids) != entry.input_names:
        raise ValueError(f"input_signal_ids must be exactly {list(entry.input_names)}")
    if tuple(model.output_signal_ids) != entry.output_names:
        raise ValueError(
            f"output_signal_ids must be exactly {list(entry.output_names)}"
        )
    expected_units = {
        **dict(zip(entry.state_names, entry.state_units)),
        **dict(zip(entry.input_names, entry.input_units)),
        **dict(zip(entry.output_names, entry.output_units)),
    }
    if model.signal_units and model.signal_units != expected_units:
        missing = sorted(set(expected_units) - set(model.signal_units))
        unknown = sorted(set(model.signal_units) - set(expected_units))
        conflicting = sorted(
            name
            for name in set(model.signal_units) & set(expected_units)
            if model.signal_units[name] != expected_units[name]
        )
        raise ValueError(
            "registered signal_units conflict with the audited registry; "
            f"missing={missing}, unknown={unknown}, conflicting={conflicting}"
        )
    return entry


def _cartpole_params(model: RegisteredNonlinearModelSpec) -> CartpoleParams:
    return CartpoleParams(**model.parameters)


def _vtol_params(model: RegisteredNonlinearModelSpec) -> VtolParams:
    return VtolParams(**model.parameters)


def _equilibrium_state(
    entry: _RegistryEntry,
    controller: RegisteredControllerSpec,
) -> np.ndarray:
    if entry.template_id == "underactuated_cartpole":
        position = (
            controller.feedforward.get("position_reference_prefilter", 1.0)
            * controller.reference["position_m"]
        )
        return np.asarray([position, 0.0, 0.0, 0.0], dtype=float)
    return np.asarray(
        [
            controller.reference["x_m"],
            controller.reference["z_m"],
            0.0,
            0.0,
            0.0,
            0.0,
        ],
        dtype=float,
    )


def _validate_state_vector(
    state: list[float] | np.ndarray,
    entry: _RegistryEntry,
    label: str,
) -> np.ndarray:
    vector = np.asarray(state, dtype=float)
    if vector.shape != (len(entry.state_names),):
        raise ValueError(f"{label} must have dimension {len(entry.state_names)}")
    if not np.all(np.isfinite(vector)):
        raise ValueError(f"{label} must contain only finite values")
    return vector


def _controller_command(
    entry: _RegistryEntry,
    model: RegisteredNonlinearModelSpec,
    controller: RegisteredControllerSpec,
    state: np.ndarray,
) -> tuple[dict[str, float], dict[str, float]]:
    gains = controller.parameters
    if entry.template_id == "underactuated_cartpole":
        params = _cartpole_params(model)
        x, x_dot, theta, theta_dot = [float(value) for value in state]
        filtered_reference = (
            controller.feedforward.get("position_reference_prefilter", 1.0)
            * controller.reference["position_m"]
        )
        theta_reference = (
            gains["kp_y"] * (filtered_reference - x) - gains["kd_y"] * x_dot
        )
        theta_reference = float(
            np.clip(
                theta_reference,
                -controller.configuration["theta_reference_limit_rad"],
                controller.configuration["theta_reference_limit_rad"],
            )
        )
        requested_force = (
            gains["kp"] * (theta - theta_reference) + gains["kd"] * theta_dot
        )
        applied_force = float(
            np.clip(requested_force, -params.force_limit_n, params.force_limit_n)
        )
        return (
            {"force_n": float(requested_force)},
            {"force_n": applied_force},
        )

    params = _vtol_params(model)
    x, z, theta, x_dot, z_dot, theta_dot = [float(value) for value in state]
    desired_lateral_acceleration = (
        gains["kp_y"] * (controller.reference["x_m"] - x) - gains["kd_y"] * x_dot
    )
    lateral_tilt_gain = -params.gravity_m_s2
    theta_reference = float(
        np.clip(
            desired_lateral_acceleration / lateral_tilt_gain,
            -controller.configuration["tilt_reference_limit_rad"],
            controller.configuration["tilt_reference_limit_rad"],
        )
    )
    requested_thrust = (
        controller.feedforward["hover_thrust_n"] / max(0.20, math.cos(theta))
        + gains["kp_z"] * (controller.reference["z_m"] - z)
        - gains["kd_z"] * z_dot
    )
    requested_torque = (
        gains["kp_theta"] * (theta_reference - theta) - gains["kd_theta"] * theta_dot
    )
    applied_thrust = float(
        np.clip(
            requested_thrust,
            params.thrust_min_n,
            params.thrust_max_n,
        )
    )
    applied_torque = float(
        np.clip(
            requested_torque,
            -params.torque_limit_n_m,
            params.torque_limit_n_m,
        )
    )
    return (
        {
            "thrust_n": float(requested_thrust),
            "torque_n_m": float(requested_torque),
        },
        {"thrust_n": applied_thrust, "torque_n_m": applied_torque},
    )


def _closed_loop_derivative(
    entry: _RegistryEntry,
    model: RegisteredNonlinearModelSpec,
    controller: RegisteredControllerSpec,
    state: np.ndarray,
) -> np.ndarray:
    requested, applied = _controller_command(entry, model, controller, state)
    if not all(math.isfinite(value) for value in requested.values()):
        raise ValueError("registered controller produced a non-finite derivative input")
    if entry.template_id == "underactuated_cartpole":
        derivative = _cartpole_dynamics(
            state, applied["force_n"], _cartpole_params(model)
        )
    else:
        derivative = _vtol_dynamics(
            state,
            applied["thrust_n"],
            applied["torque_n_m"],
            _vtol_params(model),
        )
    if not np.all(np.isfinite(derivative)):
        raise ValueError("registered closed-loop derivative is non-finite")
    return np.asarray(derivative, dtype=float)


def linearize_registered_closed_loop(
    model: RegisteredNonlinearModelSpec,
    controller: RegisteredControllerSpec,
    *,
    equilibrium_state: list[float] | None = None,
    return_derivative_only: bool = False,
) -> list[list[float]] | list[float]:
    """Central finite-difference Jacobian of the actual saturated policy."""

    entry = _resolve(model, controller)
    state = _validate_state_vector(
        equilibrium_state
        if equilibrium_state is not None
        else _equilibrium_state(entry, controller),
        entry,
        "equilibrium_state",
    )
    if return_derivative_only:
        return _closed_loop_derivative(entry, model, controller, state).tolist()
    state_count = len(state)
    jacobian = np.zeros((state_count, state_count), dtype=float)
    for column in range(state_count):
        step = 1e-6 * max(1.0, abs(float(state[column])))
        delta = np.zeros(state_count, dtype=float)
        delta[column] = step
        plus = _closed_loop_derivative(entry, model, controller, state + delta)
        minus = _closed_loop_derivative(entry, model, controller, state - delta)
        jacobian[:, column] = (plus - minus) / (2.0 * step)
    if not np.all(np.isfinite(jacobian)):
        raise ValueError("registered closed-loop Jacobian is non-finite")
    return jacobian.tolist()


def validate_registered_equilibrium(
    model: RegisteredNonlinearModelSpec,
    controller: RegisteredControllerSpec,
    *,
    equilibrium_state: list[float] | None = None,
) -> RegisteredEquilibriumValidation:
    """Validate one declared equilibrium and its local continuous poles."""

    entry = _resolve(model, controller)
    state = _validate_state_vector(
        equilibrium_state
        if equilibrium_state is not None
        else _equilibrium_state(entry, controller),
        entry,
        "equilibrium_state",
    )
    derivative = _closed_loop_derivative(entry, model, controller, state)
    if not np.all(np.isfinite(derivative)):
        raise ValueError("registered equilibrium derivative is non-finite")
    residual = float(np.linalg.norm(derivative, ord=np.inf))
    if not math.isfinite(residual):
        raise ValueError("registered equilibrium residual is non-finite")
    if residual > _EQUILIBRIUM_RESIDUAL_TOLERANCE:
        raise ValueError(
            "equilibrium residual exceeds "
            f"{_EQUILIBRIUM_RESIDUAL_TOLERANCE:g}: {residual:g}"
        )
    jacobian = np.asarray(
        linearize_registered_closed_loop(
            model,
            controller,
            equilibrium_state=state.tolist(),
        ),
        dtype=float,
    )
    if not np.all(np.isfinite(jacobian)):
        raise ValueError("registered equilibrium Jacobian is non-finite")
    eigenvalues = np.linalg.eigvals(jacobian)
    largest_real_part = max(float(value.real) for value in eigenvalues)
    if largest_real_part < -_POLE_TOLERANCE:
        status: Literal["stable", "unstable", "inconclusive"] = "stable"
    elif largest_real_part > _POLE_TOLERANCE:
        status = "unstable"
    else:
        status = "inconclusive"
    return RegisteredEquilibriumValidation(
        template_id=entry.template_id,
        controller_id=entry.controller_id,
        equilibrium_state=state.tolist(),
        equilibrium_derivative=derivative.tolist(),
        residual_norm=residual,
        jacobian=jacobian.tolist(),
        poles=[
            ComplexValue(real=float(value.real), imaginary=float(value.imag))
            for value in eigenvalues
        ],
        status=status,
        evidence=[
            NONLINEAR_SOFTWARE_MODEL_BOUNDARY,
            (
                "The Jacobian uses central finite differences with "
                "h=1e-6*max(1,abs(component))."
            ),
            "Every local continuous-time pole must have real part below -1e-6.",
        ],
    )


def evaluate_tail_contraction(early_envelope: float, tail_envelope: float) -> float:
    """Return fractional envelope reduction without tiny-denominator artifacts."""

    early = abs(float(early_envelope))
    tail = abs(float(tail_envelope))
    if early == 0.0:
        return 1.0 if tail == 0.0 else 0.0
    if early <= _TINY_ENVELOPE:
        return 1.0 if tail == 0.0 else max(0.0, 1.0 - tail / early)
    return 1.0 - tail / early


def _state_bounds(
    entry: _RegistryEntry,
    model: RegisteredNonlinearModelSpec,
    supplied: Mapping[str, tuple[float, float]] | None = None,
) -> tuple[tuple[float, float], ...]:
    if supplied is not None:
        if set(supplied) != set(entry.state_names):
            raise ValueError(
                "registered state bounds must use every exact state name; "
                f"missing={sorted(set(entry.state_names) - set(supplied))}, "
                f"unknown={sorted(set(supplied) - set(entry.state_names))}"
            )
        normalized: list[tuple[float, float]] = []
        for name in entry.state_names:
            pair = supplied[name]
            if len(pair) != 2:
                raise ValueError(
                    f"registered state bound for {name} must be (lower, upper)"
                )
            lower, upper = float(pair[0]), float(pair[1])
            if not math.isfinite(lower) or not math.isfinite(upper):
                raise ValueError("registered state bounds must be finite")
            if lower >= upper:
                raise ValueError(
                    "registered state bound lower value must be below upper"
                )
            normalized.append((lower, upper))
        return tuple(normalized)
    if entry.template_id != "underactuated_cartpole":
        return entry.fixed_state_bounds
    cart_limit = model.parameters["cart_position_limit_m"]
    return ((-cart_limit, cart_limit), *entry.fixed_state_bounds[1:])


def registered_run_envelope(
    model: RegisteredNonlinearModelSpec,
    *,
    declared_bounds: Mapping[str, float] | None = None,
) -> dict[str, object]:
    """Return the fixed, allowlisted runtime envelope for one registered model."""

    entry = _entry_for_template(model.template_id)
    if tuple(model.input_signal_ids) != entry.input_names:
        raise ValueError(f"input_signal_ids must be exactly {list(entry.input_names)}")
    if tuple(model.output_signal_ids) != entry.output_names:
        raise ValueError(
            f"output_signal_ids must be exactly {list(entry.output_names)}"
        )
    state_bounds = dict(zip(entry.state_names, _state_bounds(entry, model)))
    supplied = dict(declared_bounds or {})
    if entry.template_id == "vtol_cascaded":
        for name, declared_name in (
            ("z_m", "max_altitude_error"),
            ("pitch_rad", "max_tilt_rad"),
        ):
            if declared_name not in supplied:
                continue
            limit = float(supplied[declared_name])
            if not math.isfinite(limit) or limit <= 0.0:
                raise ValueError(
                    f"declared {declared_name} must be a positive finite value"
                )
            lower, upper = state_bounds[name]
            state_bounds[name] = (max(lower, -limit), min(upper, limit))
        actuator_bounds = {
            "thrust_n": (
                model.parameters["thrust_min_n"],
                model.parameters["thrust_max_n"],
            ),
            "torque_n_m": (
                -model.parameters["torque_limit_n_m"],
                model.parameters["torque_limit_n_m"],
            ),
        }
    else:
        force_limit = model.parameters["force_limit_n"]
        actuator_bounds = {"force_n": (-force_limit, force_limit)}
    output_bounds = {name: state_bounds[name] for name in entry.output_names}
    return {
        "reference": {
            name: 0.0 for name in entry.output_names if name in entry.reference_names
        },
        "horizon_s": entry.horizon_s,
        "sample_time_s": entry.sample_time_s,
        "actuator_bounds": actuator_bounds,
        "state_bounds": state_bounds,
        "output_bounds": output_bounds,
    }


def _append_nonfinite_event(
    events: list[SimulationEvent],
    sample_index: int,
    time_s: float,
    message: str,
) -> None:
    events.append(
        SimulationEvent(
            kind="non_finite",
            sample_index=sample_index,
            time_s=max(0.0, time_s),
            message=message,
        )
    )


def run_registered_scenario(
    model: RegisteredNonlinearModelSpec,
    controller: RegisteredControllerSpec,
    scenario_id: str,
    *,
    state_bounds: Mapping[str, tuple[float, float]] | None = None,
) -> RegisteredScenarioResult:
    """Run one named scenario from the closed deterministic scenario set."""

    entry = _resolve(model, controller)
    equilibrium = validate_registered_equilibrium(model, controller)
    scenario = next(
        (item for item in entry.scenarios if item.scenario_id == scenario_id),
        None,
    )
    if scenario is None:
        raise ValueError(
            f"unknown scenario {scenario_id!r} for template {entry.template_id!r}"
        )
    equilibrium_state = np.asarray(equilibrium.equilibrium_state, dtype=float)
    state = equilibrium_state + np.asarray(scenario.perturbation, dtype=float)
    step_count = round(entry.horizon_s / entry.sample_time_s)
    if step_count + 1 > _MAX_SAMPLES:
        raise ValueError("registered scenario would exceed 20,000 samples")

    time_values: list[float] = []
    references = {name: [] for name in sorted(entry.reference_names)}
    states = {name: [] for name in entry.state_names}
    outputs = {name: [] for name in entry.output_names}
    requested_controls = {name: [] for name in entry.input_names}
    applied_controls = {name: [] for name in entry.input_names}
    events: list[SimulationEvent] = []
    error_norms: list[float] = []
    saturated_samples = 0
    saturation_event_channels: set[str] = set()
    hard_failure = False
    finite = True
    bounded = True
    bounds = _state_bounds(entry, model, state_bounds)
    scales = np.asarray(entry.state_error_scales, dtype=float)

    for sample_index in range(step_count + 1):
        time_s = sample_index * entry.sample_time_s
        if not np.all(np.isfinite(state)):
            finite = False
            hard_failure = True
            _append_nonfinite_event(
                events,
                len(time_values),
                time_s,
                "non-finite state terminated the registered rollout",
            )
            break
        bound_violation = next(
            (
                (index, float(state[index]), lower, upper)
                for index, (lower, upper) in enumerate(bounds)
                if float(state[index]) < lower or float(state[index]) > upper
            ),
            None,
        )
        if bound_violation is not None:
            index, value, lower, upper = bound_violation
            bounded = False
            hard_failure = True
            limit = lower if value < lower else upper
            events.append(
                SimulationEvent(
                    kind="hard_bound_violation",
                    sample_index=len(time_values),
                    time_s=time_s,
                    message=(
                        f"{entry.state_names[index]} left the registered "
                        "software-model validation boundary"
                    ),
                    channel=entry.state_names[index],
                    value=value,
                    limit=float(limit),
                )
            )
            break
        try:
            requested, applied = _controller_command(entry, model, controller, state)
        except (OverflowError, ValueError, FloatingPointError) as exc:
            finite = False
            hard_failure = True
            _append_nonfinite_event(
                events,
                len(time_values),
                time_s,
                f"controller arithmetic terminated the rollout: {exc}",
            )
            break
        if not all(math.isfinite(value) for value in requested.values()):
            finite = False
            hard_failure = True
            _append_nonfinite_event(
                events,
                len(time_values),
                time_s,
                "non-finite requested control terminated the rollout",
            )
            break

        time_values.append(float(time_s))
        for name, values in references.items():
            values.append(float(controller.reference[name]))
        for index, name in enumerate(entry.state_names):
            states[name].append(float(state[index]))
        for name in entry.output_names:
            outputs[name].append(float(state[entry.state_names.index(name)]))
        sample_saturated = False
        for name in entry.input_names:
            requested_value = float(requested[name])
            applied_value = float(applied[name])
            requested_controls[name].append(requested_value)
            applied_controls[name].append(applied_value)
            if not math.isclose(
                requested_value,
                applied_value,
                rel_tol=0.0,
                abs_tol=1e-12,
            ):
                sample_saturated = True
                if name not in saturation_event_channels:
                    saturation_event_channels.add(name)
                    events.append(
                        SimulationEvent(
                            kind="saturation",
                            sample_index=sample_index,
                            time_s=time_s,
                            message=(
                                f"requested {name} was clipped by the "
                                "registered actuator boundary"
                            ),
                            channel=name,
                            value=requested_value,
                            limit=applied_value,
                        )
                    )
        saturated_samples += int(sample_saturated)
        error_norms.append(float(np.linalg.norm((state - equilibrium_state) / scales)))

        if sample_index == step_count:
            break

        try:
            if entry.template_id == "underactuated_cartpole":
                next_state = _cartpole_rk4_step(
                    state,
                    applied["force_n"],
                    entry.sample_time_s,
                    _cartpole_params(model),
                )
            else:
                next_state = rk4_step(
                    _vtol_dynamics,
                    state,
                    entry.sample_time_s,
                    applied["thrust_n"],
                    applied["torque_n_m"],
                    _vtol_params(model),
                )
        except (
            FloatingPointError,
            OverflowError,
            ValueError,
            np.linalg.LinAlgError,
        ) as exc:
            finite = False
            hard_failure = True
            _append_nonfinite_event(
                events,
                len(time_values),
                time_s + entry.sample_time_s,
                f"non-finite integration terminated the rollout: {exc}",
            )
            break
        if not np.all(np.isfinite(next_state)):
            finite = False
            hard_failure = True
            _append_nonfinite_event(
                events,
                len(time_values),
                time_s + entry.sample_time_s,
                "non-finite integration result terminated the rollout",
            )
            break
        state = np.asarray(next_state, dtype=float)

    sample_count = len(time_values)
    window = max(2, int(0.05 * sample_count)) if sample_count else 0
    if error_norms:
        early_envelope = max(error_norms[:window])
        tail_envelope = max(error_norms[-window:])
        contraction = evaluate_tail_contraction(early_envelope, tail_envelope)
    else:
        contraction = 0.0
    saturation_fraction = saturated_samples / sample_count if sample_count else 0.0
    violations: list[str] = []
    if not finite:
        violations.append("non_finite_trajectory")
    if not bounded:
        violations.append("hard_state_boundary_violation")
    if saturation_fraction > _SATURATION_LIMIT:
        violations.append("sustained_actuator_saturation")
    if contraction < _CONTRACTION_THRESHOLD - 1e-12:
        violations.append("tail_contraction_below_10_percent")
    passed = (
        finite
        and bounded
        and saturation_fraction <= _SATURATION_LIMIT
        and contraction >= _CONTRACTION_THRESHOLD - 1e-12
    )
    trace = SimulationTrace(
        time_s=time_values,
        reference=references,
        states=states,
        outputs=outputs,
        requested_controls=requested_controls,
        applied_controls=applied_controls,
        events=events,
    )
    evidence = NonlinearScenarioEvidence(
        scenario_id=scenario.scenario_id,
        passed=passed,
        trajectory_finite=finite,
        trajectory_bounded=bounded,
        tail_error_envelope_contraction=float(contraction),
        saturation_fraction=float(saturation_fraction),
        hard_failure=hard_failure,
        sample_count=sample_count,
        violations=violations,
        evidence=[
            NONLINEAR_SOFTWARE_MODEL_BOUNDARY,
            (
                "The final 5% error envelope must be at least 10% smaller "
                "than the early 5% envelope."
            ),
        ],
    )
    return RegisteredScenarioResult(trace=trace, evidence=evidence)


def run_registered_validation(
    model: RegisteredNonlinearModelSpec,
    controller: RegisteredControllerSpec,
    *,
    state_bounds: Mapping[str, tuple[float, float]] | None = None,
) -> RegisteredNonlinearValidationResult:
    """Run local pole analysis followed by all five registered scenarios."""

    entry = _resolve(model, controller)
    equilibrium = validate_registered_equilibrium(model, controller)
    scenario_results = [
        run_registered_scenario(
            model,
            controller,
            scenario.scenario_id,
            state_bounds=state_bounds,
        )
        for scenario in entry.scenarios
    ]
    evidence = [result.evidence for result in scenario_results]
    hard_failure = any(item.hard_failure for item in evidence)
    any_failed = any(not item.passed for item in evidence)
    if hard_failure or equilibrium.status == "unstable" or any_failed:
        status: Literal["stable", "unstable", "inconclusive"] = "unstable"
    elif equilibrium.status == "inconclusive":
        status = "inconclusive"
    else:
        status = "stable"
    violations = sorted(
        {violation for item in evidence for violation in item.violations}
    )
    if equilibrium.status == "unstable":
        violations.append("local_closed_loop_pole_unstable")
    decision = StabilityDecision(
        status=status,
        analysis_domain="continuous",
        pole_analysis_method="registered_nonlinear_local_linearization",
        registered_template_id=entry.template_id,
        poles=equilibrium.poles,
        spectral_radius=None,
        trajectory_finite=all(item.trajectory_finite for item in evidence),
        trajectory_bounded=all(item.trajectory_bounded for item in evidence),
        tail_error_envelope_contraction=min(
            item.tail_error_envelope_contraction for item in evidence
        ),
        saturation_fraction=max(item.saturation_fraction for item in evidence),
        hard_failure=hard_failure,
        violations=violations,
        evidence=[
            NONLINEAR_SOFTWARE_MODEL_BOUNDARY,
            (
                "Aggregate stability requires passing local poles and all five "
                "registered deterministic perturbation rollouts."
            ),
        ],
        scenario_evidence=evidence,
    )
    return RegisteredNonlinearValidationResult(
        equilibrium=equilibrium,
        traces={
            result.evidence.scenario_id: result.trace for result in scenario_results
        },
        stability=decision,
    )


__all__ = [
    "NONLINEAR_SOFTWARE_MODEL_BOUNDARY",
    "RegisteredEquilibriumValidation",
    "RegisteredNonlinearValidationResult",
    "RegisteredScenarioResult",
    "evaluate_tail_contraction",
    "linearize_registered_closed_loop",
    "list_registered_controllers",
    "list_registered_templates",
    "registered_run_envelope",
    "run_registered_scenario",
    "run_registered_validation",
    "validate_registered_equilibrium",
]
