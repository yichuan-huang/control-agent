"""Bounded, registered per-sample execution of Kernel ControllerIR families.

Sample order is measurement validation, reference/derivative preprocessing,
output from the *previous* integral and transfer-section states, actuator
clipping, then state update. Reference/derivative low-pass preprocessing uses
exact held-input exponential updates. Continuous lead/lag/notch sections use
exact zero-order-hold state-space discretization and pre-update outputs; the
lead/lag cascade is discretized as one continuous transfer function. Dynamic
matrix lag states also update after output, preserving the declared DC map.

Integrals are stored in virtual-control units (``integral_control``), not
error-seconds. Conditional integration tests the signed actuator displacement
of each proposed integral update. Back-calculation uses the actuator residual
mapped back to virtual-control units. No controller gains are made positive.

This module knows neither plant truth nor task performance/safety thresholds.
Internal capture/hold events are controller modes, never Kernel phase changes
or hardware authorization. Providers remain responsible for measured-state
limits, stop conditions, timing, and immutable trajectory evidence.
"""

from __future__ import annotations

import copy
import math
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

import numpy as np
from scipy import optimize, signal

from cfdc.kernel.controllers import ControllerIR

_VERSION = "1.0.0"
_PI = ("kp", "ki", "reference_filter_rate")
_MODAL = (
    "kp",
    "ki",
    "kd",
    "feedforward",
    "input_gain_estimate",
    "target_bandwidth",
    "antiwindup_gain",
)
_CHANNEL = ("target_bandwidth", "kp_1", "kp_2", "ki_1", "ki_2")
_STATIC_MAP = tuple(f"input_map_{i}{j}" for i in (1, 2) for j in (1, 2))
_DYNAMIC_MAP = tuple(
    f"dynamic_map_{section}_{i}{j}"
    for section in ("base", "lag1", "lag2", "lag3")
    for i in (1, 2)
    for j in (1, 2)
)
_REQUIRED = {
    "PI": _PI,
    "delay_aware_PI": _PI,
    "notch_then_PI": _PI
    + (
        "notch_center_rad_s",
        "notch_zero_damping",
        "notch_pole_damping",
    ),
    "two_dof_pid": _PI + ("feedforward_gain", "kd", "derivative_filter_rate"),
    "P_integrator": ("kp", "reference_filter_rate"),
    "PD_integrator": ("kp", "kd", "reference_filter_rate", "derivative_filter_rate"),
    "lead_lag_series": (
        "gain",
        "lead_zero_rate",
        "lead_pole_rate",
        "lag_zero_rate",
        "lag_pole_rate",
    ),
    "two_dof_PI": _PI + ("feedforward_gain",),
    "local_PI_without_inverse": (
        "Kp_virtual",
        "Ki_virtual",
        "reference_feedforward",
        "map_linear",
        "target_bandwidth",
    ),
    "partial_inverse_then_PI": (
        "Kp_virtual",
        "Ki_virtual",
        "map_linear",
        "map_cubic",
        "target_bandwidth",
        "inverse_input_lower",
        "inverse_input_upper",
    ),
    "deadzone_right_inverse_then_PI": (
        "Kp_virtual",
        "Ki_virtual",
        "positive_deadzone",
        "negative_deadzone",
        "outer_slope",
        "virtual_noise_guard",
        "target_bandwidth",
    ),
    "reduced_low_order_PI": _PI + ("target_bandwidth",),
    "phase_guarded_2dof_PI": _PI + ("target_bandwidth", "feedforward_gain"),
    "cascaded_control": (
        "inner_kp",
        "inner_kd",
        "inner_target_rate",
        "outer_target_rate",
        "outer_damping",
        "internal_reference_limit",
        "reference_acceleration_scale",
    ),
    "local_fixed_PID": _MODAL,
    "scheduled_damping_PID": _MODAL
    + ("base_decay", "quadratic_decay", "desired_damping"),
    "self_excitation_energy_guarded_PID": _MODAL
    + (
        "capture_damping_gain",
        "capture_target_damping_ratio",
        "handoff_amplitude",
        "handoff_hysteresis",
        "handoff_dwell_s",
        "envelope_filter_rate",
    ),
    "decentralized_channel_PI": _CHANNEL + _STATIC_MAP,
    "static_decoupler_then_PI": _CHANNEL + _STATIC_MAP,
    "lag_dynamic_decoupler_then_PI": _CHANNEL
    + _DYNAMIC_MAP
    + (
        "dynamic_filter_tau_1",
        "dynamic_filter_tau_2",
        "dynamic_filter_tau_3",
    ),
}
_MIMO = frozenset(
    {
        "decentralized_channel_PI",
        "static_decoupler_then_PI",
        "lag_dynamic_decoupler_then_PI",
    }
)
_MODAL_FAMILIES = frozenset(
    {
        "local_fixed_PID",
        "scheduled_damping_PID",
        "self_excitation_energy_guarded_PID",
    }
)
_INVERSE_FAMILIES = frozenset(
    {
        "local_PI_without_inverse",
        "partial_inverse_then_PI",
        "deadzone_right_inverse_then_PI",
    }
)
_MODAL_INTERFACES = (
    ("position", "velocity"),
    ("position_m", "velocity_m_s"),
    ("x", "x_dot"),
)
_CASCADE_INTERFACES = (
    ("position", "velocity", "internal", "internal_rate"),
    ("position_m", "velocity_m_s", "angle_rad", "angular_rate_rad_s"),
    ("x", "x_dot", "theta", "theta_dot"),
)
_VTOL_INTERFACE = (
    "x_m",
    "z_m",
    "pitch_rad",
    "x_velocity_m_s",
    "z_velocity_m_s",
    "pitch_rate_rad_s",
)
_VTOL_PARAMETERS = ("altitude_kp", "altitude_kd", "hover_thrust")


@dataclass(frozen=True)
class RuntimeRegistration:
    runtime_id: str
    version: str
    required_parameters: tuple[str, ...]


RUNTIME_REGISTRY = MappingProxyType(
    {
        family: RuntimeRegistration(f"cfdc.controller.{family}", _VERSION, parameters)
        for family, parameters in _REQUIRED.items()
    }
)


def runtime_contract(family: str) -> dict[str, Any]:
    """Return an independent, executable contract; names are case-sensitive.

    Scalar and MIMO output names come from the IR's declared measurement order.
    Measured-state controllers use only the listed explicit interfaces, matched
    by names (not incoming dictionary order). Extra declared sensors must still
    be supplied and finite at every step.
    """
    if family not in RUNTIME_REGISTRY:
        raise ValueError(f"controller_runtime_family_not_registered: {family}")
    entry = RUNTIME_REGISTRY[family]
    if family == "cascaded_control":
        interfaces = [list(names) for names in (*_CASCADE_INTERFACES, _VTOL_INTERFACE)]
        roles = ["position", "velocity", "internal", "internal_rate"]
    elif family in _MODAL_FAMILIES:
        interfaces = [list(names) for names in _MODAL_INTERFACES]
        roles = ["position", "velocity"]
    else:
        interfaces = []
        roles = (
            ["measured_output_1", "measured_output_2"]
            if family in _MIMO
            else ["measured_output"]
        )
    return {
        "family": family,
        "runtime_id": entry.runtime_id,
        "version": entry.version,
        "required_parameters": list(entry.required_parameters),
        "required_signal_roles": roles,
        "signal_interfaces": interfaces,
        "measurement_binding": "explicit_named_interface"
        if interfaces
        else "IR.measured_signals order",
        "optional_parameters": (
            {"reference_weight": 1.0}
            if family
            not in _MODAL_FAMILIES | _MIMO | {"cascaded_control", "lead_lag_series"}
            else {}
        ),
        "integral_policy": (
            "frozen_back_calculation"
            if family in _MODAL_FAMILIES
            else "IR.integral_handling"
        ),
        "conditional_required_parameters": {
            "integral_handling=back_calculation": ["antiwindup_gain"],
            **(
                {"VTOL measured interface": list(_VTOL_PARAMETERS)}
                if family == "cascaded_control"
                else {}
            ),
        },
        "update_order": [
            "measurements",
            "reference_and_derivative_filters",
            "pre_update_output",
            "clip",
            "state_update",
        ],
        "discretization": "exact_zero_order_hold",
        "integral_state_units": "virtual_control",
        "command_bounds": "finite per-input bounds required; legacy output_bounds may supply shared bounds",
    }


@dataclass(frozen=True)
class RuntimeSample:
    raw_control: dict[str, float]
    control: dict[str, float]
    state: dict[str, Any]
    saturated: dict[str, bool]
    events: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return copy.deepcopy(
            {
                "raw_control": self.raw_control,
                "control": self.control,
                "state": self.state,
                "saturated": self.saturated,
                "events": self.events,
            }
        )


def _finite(value: Any, label: str) -> float:
    if isinstance(value, (bool, str, bytes)):
        raise TypeError(f"{label}_must_be_finite_numeric")
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{label}_must_be_finite_numeric") from exc
    if not math.isfinite(number):
        raise ValueError(f"{label}_must_be_finite")
    return number


def _require(parameters: Mapping[str, float], names: tuple[str, ...]) -> None:
    missing = sorted(set(names) - set(parameters))
    if missing:
        raise ValueError("controller_runtime_parameters_missing: " + ", ".join(missing))


def _alpha(rate: float, dt: float) -> float:
    return -math.expm1(-rate * dt)


def _filter(
    state: dict[str, Any], name: str, value: float, rate: float, dt: float
) -> float:
    previous = state.get(name, 0.0)
    state[name] = previous + _alpha(rate, dt) * (value - previous)
    return state[name]


class ControllerRuntime:
    """Execute one immutable controller description without any plant access.

    ``reference`` mappings use the controlled measurement names. A scalar is
    broadcast for SISO and paired PI channels; VTOL requires both x/z references.
    Unknown families, incomplete coefficients/interfaces and unbounded commands
    fail closed. A rejected sample does not commit any controller state.
    """

    def __init__(
        self,
        controller: ControllerIR | Mapping[str, Any],
        *,
        input_bounds: Mapping[str, tuple[float, float]] | None = None,
    ):
        if isinstance(controller, ControllerIR):
            # Preserve typed artifact identity, including numeric representation.
            # Frozen dataclasses still contain mutable mappings: validate a copy.
            self.controller = copy.deepcopy(controller)
            self.controller.__post_init__()
        else:
            self.controller = ControllerIR.from_mapping(controller)
        self.family = self.controller.family
        self.contract = runtime_contract(self.family)
        self.parameters = {
            name: float(value) for name, value in self.controller.parameters.items()
        }
        self.measured_signals = self.controller.measured_signals
        self.control_inputs = self.controller.control_inputs
        if len(set(self.measured_signals)) != len(self.measured_signals) or len(
            set(self.control_inputs)
        ) != len(self.control_inputs):
            raise ValueError("controller_runtime_duplicate_interface_name")
        _require(self.parameters, RUNTIME_REGISTRY[self.family].required_parameters)
        self._interface = self._bind_interface()
        self.reference_names = self._reference_names()
        self._validate_parameters()
        if input_bounds is None:
            if self.controller.output_bounds is None:
                raise ValueError("controller_input_bounds_required")
            input_bounds = dict.fromkeys(
                self.control_inputs, self.controller.output_bounds
            )
        if set(self.control_inputs) - set(input_bounds):
            raise ValueError(
                "controller_input_bounds_missing: "
                + ", ".join(sorted(set(self.control_inputs) - set(input_bounds)))
            )
        if set(input_bounds) - set(self.control_inputs):
            raise ValueError("controller_input_bounds_unknown_channel")
        self.input_bounds = {}
        for name in self.control_inputs:
            bounds = input_bounds[name]
            if not isinstance(bounds, (tuple, list)) or len(bounds) != 2:
                raise ValueError(f"controller_input_bounds_invalid: {name}")
            lower, upper = (_finite(value, f"input_bounds_{name}") for value in bounds)
            if lower >= upper:
                raise ValueError(f"controller_input_bounds_invalid: {name}")
            self.input_bounds[name] = (lower, upper)
        if self.family == "partial_inverse_then_PI":
            lower, upper = self.input_bounds[self.control_inputs[0]]
            if (
                lower > self.parameters["inverse_input_upper"]
                or upper < self.parameters["inverse_input_lower"]
            ):
                raise ValueError("controller_inverse_and_actuator_bounds_disjoint")
        self._section = self._continuous_section()
        self._discrete_cache: dict[float, tuple[np.ndarray, ...]] = {}
        self.reset()

    def reset(self) -> None:
        """Reset all memory, including filters and internal capture/hold mode."""
        self._state: dict[str, Any] = {}

    def _bind_interface(self) -> tuple[str, ...]:
        names = set(self.measured_signals)
        if self.family == "cascaded_control":
            if set(_VTOL_INTERFACE) <= names:
                if set(self.control_inputs) != {"thrust_n", "torque_n_m"}:
                    raise ValueError("controller_vtol_control_inputs_invalid")
                _require(self.parameters, _VTOL_PARAMETERS)
                return _VTOL_INTERFACE
            for interface in _CASCADE_INTERFACES:
                if set(interface) <= names and len(self.control_inputs) == 1:
                    return interface
            raise ValueError("controller_cascade_measurement_interface_missing")
        if self.family in _MODAL_FAMILIES:
            for interface in _MODAL_INTERFACES:
                if set(interface) <= names and len(self.control_inputs) == 1:
                    return interface
            raise ValueError("controller_modal_measurement_interface_missing")
        count = 2 if self.family in _MIMO else 1
        if len(self.measured_signals) != count or len(self.control_inputs) != count:
            raise ValueError("controller_measurement_or_control_interface_invalid")
        return self.measured_signals

    def _reference_names(self) -> tuple[str, ...]:
        if self._interface == _VTOL_INTERFACE:
            return ("x_m", "z_m")
        if self.family in _MODAL_FAMILIES or self.family == "cascaded_control":
            return (self._interface[0],)
        return self._interface

    def _matrix(self, prefix: str) -> np.ndarray:
        return np.asarray(
            [[self.parameters[f"{prefix}_{i}{j}"] for j in (1, 2)] for i in (1, 2)]
        )

    def _validate_parameters(self) -> None:
        p = self.parameters
        positive = {
            "reference_filter_rate",
            "derivative_filter_rate",
            "notch_center_rad_s",
            "notch_pole_damping",
            "lead_zero_rate",
            "lead_pole_rate",
            "lag_zero_rate",
            "lag_pole_rate",
            "target_bandwidth",
            "inner_target_rate",
            "outer_target_rate",
            "outer_damping",
            "internal_reference_limit",
            "desired_damping",
            "capture_target_damping_ratio",
            "handoff_amplitude",
            "handoff_dwell_s",
            "envelope_filter_rate",
            "dynamic_filter_tau_1",
            "dynamic_filter_tau_2",
            "dynamic_filter_tau_3",
        }
        nonnegative = {
            "notch_zero_damping",
            "positive_deadzone",
            "negative_deadzone",
            "virtual_noise_guard",
            "handoff_hysteresis",
            "antiwindup_gain",
        }
        for name in positive & p.keys():
            if p[name] <= 0.0:
                raise ValueError(f"controller_parameter_must_be_positive: {name}")
        for name in nonnegative & p.keys():
            if p[name] < 0.0:
                raise ValueError(f"controller_parameter_must_be_nonnegative: {name}")
        if self.controller.integral_handling == "back_calculation":
            _require(p, ("antiwindup_gain",))
        if "reference_weight" in p and not 0.0 <= p["reference_weight"] <= 1.0:
            raise ValueError("controller_reference_weight_out_of_range")
        nonzero = {"input_gain_estimate", "reference_acceleration_scale", "outer_slope"}
        if self.family == "local_PI_without_inverse":
            nonzero.add("map_linear")
        if self.family == "self_excitation_energy_guarded_PID":
            nonzero.add("capture_damping_gain")
        for name in nonzero & p.keys():
            if p[name] == 0.0:
                raise ValueError(f"controller_parameter_must_be_nonzero: {name}")
        if self.family == "lead_lag_series" and not (
            p["lead_zero_rate"] < p["lead_pole_rate"]
            and p["lag_pole_rate"] <= p["lag_zero_rate"]
        ):
            raise ValueError("controller_lead_lag_rate_ordering_invalid")
        if self.family == "partial_inverse_then_PI":
            lo, hi = p["inverse_input_lower"], p["inverse_input_upper"]
            if lo >= hi:
                raise ValueError("controller_inverse_input_interval_invalid")
            points = [lo, hi] + ([0.0] if lo <= 0.0 <= hi else [])
            derivatives = [
                p["map_linear"] + 3.0 * p["map_cubic"] * x * x for x in points
            ]
            if not (
                (min(derivatives) >= 0.0 and max(derivatives) > 0.0)
                or (max(derivatives) <= 0.0 and min(derivatives) < 0.0)
            ):
                raise ValueError("controller_inverse_interval_not_monotonic")
        if self.family in {"decentralized_channel_PI", "static_decoupler_then_PI"}:
            matrix = self._matrix("input_map")
            if np.linalg.matrix_rank(matrix) != 2:
                raise ValueError("controller_input_map_singular")
            if self.family == "decentralized_channel_PI" and not (
                np.all(np.count_nonzero(matrix, axis=0) == 1)
                and np.all(np.count_nonzero(matrix, axis=1) == 1)
            ):
                raise ValueError("controller_decentralized_input_map_must_be_pairing")
        if self.family == "lag_dynamic_decoupler_then_PI":
            if np.linalg.matrix_rank(self._matrix("dynamic_map_base")) != 2:
                raise ValueError("controller_dynamic_dc_map_singular")
            direct = self._matrix("dynamic_map_base") - sum(
                self._matrix(f"dynamic_map_lag{k}") for k in (1, 2, 3)
            )
            if (
                self.controller.integral_handling == "back_calculation"
                and np.linalg.matrix_rank(direct) != 2
            ):
                raise ValueError(
                    "controller_back_calculation_requires_invertible_direct_map"
                )

    def _continuous_section(self) -> tuple[np.ndarray, ...] | None:
        p = self.parameters
        if self.family == "notch_then_PI":
            w = p["notch_center_rad_s"]
            return signal.tf2ss(
                [1.0, 2.0 * p["notch_zero_damping"] * w, w * w],
                [1.0, 2.0 * p["notch_pole_damping"] * w, w * w],
            )
        if self.family == "lead_lag_series":
            return signal.tf2ss(
                np.polymul([1.0, p["lead_zero_rate"]], [1.0, p["lag_zero_rate"]]),
                np.polymul([1.0, p["lead_pole_rate"]], [1.0, p["lag_pole_rate"]]),
            )
        return None

    def _section_output(self, value: float, dt: float, state: dict[str, Any]) -> float:
        if dt not in self._discrete_cache:
            # Bound cache growth when providers record variable sample periods.
            if len(self._discrete_cache) >= 16:
                self._discrete_cache.clear()
            self._discrete_cache[dt] = signal.cont2discrete(
                self._section, dt, method="zoh"
            )[:4]
        a, b, c, d = self._discrete_cache[dt]
        old = np.asarray(state.get("transfer_state", [0.0] * a.shape[0]))
        output = float((c @ old + d[:, 0] * value)[0])
        state["transfer_state"] = (a @ old + b[:, 0] * value).tolist()
        return output

    def _references(self, reference: float | Mapping[str, float]) -> dict[str, float]:
        if isinstance(reference, Mapping):
            missing = set(self.reference_names) - set(reference)
            if missing:
                raise ValueError(
                    "controller_reference_missing: " + ", ".join(sorted(missing))
                )
            return {
                name: _finite(value, f"reference_{name}")
                for name, value in reference.items()
            }
        if self._interface == _VTOL_INTERFACE:
            raise ValueError("controller_vtol_reference_mapping_required")
        return dict.fromkeys(self.reference_names, _finite(reference, "reference"))

    def _inverse(self, virtual: float) -> tuple[float, bool]:
        p = self.parameters
        if self.family == "local_PI_without_inverse":
            return virtual / p["map_linear"], False
        if self.family == "deadzone_right_inverse_then_PI":
            if abs(virtual) <= p["virtual_noise_guard"]:
                return 0.0, False
            linear = virtual / p["outer_slope"]
            return linear + (
                p["positive_deadzone"] if linear > 0.0 else -p["negative_deadzone"]
            ), False
        lo, hi = p["inverse_input_lower"], p["inverse_input_upper"]
        f_lo, f_hi = self._forward(lo), self._forward(hi)
        target = float(np.clip(virtual, min(f_lo, f_hi), max(f_lo, f_hi)))
        if target == f_lo:
            return lo, target != virtual
        if target == f_hi:
            return hi, target != virtual
        return float(
            optimize.brentq(lambda x: self._forward(x) - target, lo, hi)
        ), target != virtual

    def _forward(self, control: float) -> float:
        p = self.parameters
        if self.family == "partial_inverse_then_PI":
            return p["map_linear"] * control + p["map_cubic"] * control**3
        if self.family == "local_PI_without_inverse":
            return p["map_linear"] * control
        if control > p["positive_deadzone"]:
            return p["outer_slope"] * (control - p["positive_deadzone"])
        if control < -p["negative_deadzone"]:
            return p["outer_slope"] * (control + p["negative_deadzone"])
        return 0.0

    def _scalar(
        self,
        measured: dict[str, float],
        references: dict[str, float],
        dt: float,
        state: dict[str, Any],
        events: list[dict[str, Any]],
    ) -> tuple[
        np.ndarray, np.ndarray, np.ndarray, tuple[str, ...], np.ndarray, np.ndarray
    ]:
        p, family = self.parameters, self.family
        y, reference = measured[self._interface[0]], references[self.reference_names[0]]
        if family == "lead_lag_series":
            value = p["gain"] * self._section_output(reference - y, dt, state)
            return (
                np.array([value]),
                np.array([value]),
                np.eye(1),
                (),
                np.zeros(0),
                np.zeros(0),
            )
        rate = (
            p["target_bandwidth"]
            if family in _INVERSE_FAMILIES
            else p["reference_filter_rate"]
        )
        rf = _filter(state, "reference_filter_state", reference, rate, dt)
        error = rf - y
        integral_key = "integral_control"
        has_integral = family not in {"P_integrator", "PD_integrator"}
        kp = p["Kp_virtual"] if family in _INVERSE_FAMILIES else p["kp"]
        ki = p["Ki_virtual"] if family in _INVERSE_FAMILIES else p.get("ki", 0.0)
        virtual = kp * (p.get("reference_weight", 1.0) * rf - y) + (
            state.get(integral_key, 0.0) if has_integral else 0.0
        )
        if family in {"two_dof_PI", "two_dof_pid", "phase_guarded_2dof_PI"}:
            virtual += p["feedforward_gain"] * rf
        elif family in _INVERSE_FAMILIES:
            virtual += (
                p["reference_feedforward"]
                if family == "local_PI_without_inverse"
                else 1.0
            ) * rf
        if family in {"PD_integrator", "two_dof_pid"}:
            previous = state.get("previous_measured_output", y)
            derivative = _filter(
                state,
                "filtered_output_derivative",
                (y - previous) / dt,
                p["derivative_filter_rate"],
                dt,
            )
            virtual -= p["kd"] * derivative
            state["previous_measured_output"] = y
        if family in _INVERSE_FAMILIES:
            raw, clipped = self._inverse(virtual)
            if clipped:
                events.append(
                    {
                        "kind": "inverse_domain_clipped",
                        "requested_virtual_control": virtual,
                    }
                )
        elif family == "notch_then_PI":
            raw = self._section_output(virtual, dt, state)
        else:
            raw = virtual
        return (
            np.array([raw]),
            np.array([virtual]),
            np.eye(1),
            (integral_key,) if has_integral else (),
            np.array([error]) if has_integral else np.zeros(0),
            np.array([ki]) if has_integral else np.zeros(0),
        )

    def _modal(
        self,
        measured: dict[str, float],
        references: dict[str, float],
        dt: float,
        state: dict[str, Any],
        events: list[dict[str, Any]],
    ) -> tuple[
        np.ndarray, np.ndarray, np.ndarray, tuple[str, ...], np.ndarray, np.ndarray
    ]:
        p = self.parameters
        position, velocity = (measured[name] for name in self._interface)
        reference = references[self.reference_names[0]]
        if self.family == "self_excitation_energy_guarded_PID":
            amplitude = math.hypot(position, velocity / p["target_bandwidth"])
            state.setdefault("oscillation_envelope", amplitude)
            envelope = _filter(
                state, "oscillation_envelope", amplitude, p["envelope_filter_rate"], dt
            )
            mode = state.get("mode", "capture")
            if (
                mode == "hold"
                and envelope > p["handoff_amplitude"] + p["handoff_hysteresis"]
            ):
                mode = "capture"
                state["integral_control"] = 0.0
                state["handoff_dwell_elapsed_s"] = 0.0
                state["handoff_guard_active"] = False
                events.append(
                    {"kind": "mode_transition", "from": "hold", "to": "capture"}
                )
            if mode == "capture":
                guard_active = envelope <= p["handoff_amplitude"]
                # The first observation starts the dwell; it cannot establish
                # that the guard already held during the preceding interval.
                dwell = (
                    state.get("handoff_dwell_elapsed_s", 0.0) + dt
                    if guard_active and state.get("handoff_guard_active", False)
                    else 0.0
                )
                state["handoff_guard_active"] = guard_active
                state["handoff_dwell_elapsed_s"] = dwell
                if dwell >= p["handoff_dwell_s"]:
                    mode = "hold"
                    state["integral_control"] = 0.0
                    events.append(
                        {"kind": "mode_transition", "from": "capture", "to": "hold"}
                    )
            state["mode"] = mode
            if mode == "capture":
                state["integral_control"] = 0.0
                raw = np.array([-p["capture_damping_gain"] * velocity])
                return raw, raw.copy(), np.eye(1), (), np.zeros(0), np.zeros(0)
        kd = p["kd"]
        if self.family == "scheduled_damping_PID":
            decay = p["base_decay"] + p["quadratic_decay"] * position * position
            kd = (
                max(
                    2.0 * p["desired_damping"] * p["target_bandwidth"] - 2.0 * decay,
                    0.0,
                )
                / p["input_gain_estimate"]
            )
            state["scheduled_derivative_gain"] = kd
        error = reference - position
        raw = np.array(
            [
                p["feedforward"] * reference
                + p["kp"] * error
                + state.get("integral_control", 0.0)
                - kd * velocity
            ]
        )
        return (
            raw,
            raw.copy(),
            np.eye(1),
            ("integral_control",),
            np.array([error]),
            np.array([p["ki"]]),
        )

    def _cascade(
        self,
        measured: dict[str, float],
        references: dict[str, float],
        state: dict[str, Any],
    ) -> np.ndarray:
        p = self.parameters
        if self._interface == _VTOL_INTERFACE:
            position, altitude, internal, velocity, vertical_velocity, internal_rate = (
                measured[name] for name in _VTOL_INTERFACE
            )
            reference = references["x_m"]
        else:
            position, velocity, internal, internal_rate = (
                measured[name] for name in self._interface
            )
            reference = references[self.reference_names[0]]
        acceleration = (
            p["outer_target_rate"] ** 2 * (reference - position)
            - 2.0 * p["outer_damping"] * p["outer_target_rate"] * velocity
        )
        internal_reference = float(
            np.clip(
                -acceleration / p["reference_acceleration_scale"],
                -p["internal_reference_limit"],
                p["internal_reference_limit"],
            )
        )
        state["internal_reference"] = internal_reference
        inner = (
            -p["inner_kp"] * (internal - internal_reference)
            - p["inner_kd"] * internal_rate
        )
        if self._interface != _VTOL_INTERFACE:
            return np.array([inner])
        cosine = math.cos(internal)
        if cosine <= 0.0:
            raise ValueError("controller_vtol_tilt_outside_hover_chart")
        controls = {
            "torque_n_m": inner,
            "thrust_n": p["hover_thrust"] / cosine
            + p["altitude_kp"] * (references["z_m"] - altitude)
            - p["altitude_kd"] * vertical_velocity,
        }
        return np.array([controls[name] for name in self.control_inputs])

    def _channels(
        self,
        measured: dict[str, float],
        references: dict[str, float],
        dt: float,
        state: dict[str, Any],
    ) -> tuple[
        np.ndarray, np.ndarray, np.ndarray, tuple[str, ...], np.ndarray, np.ndarray
    ]:
        p = self.parameters
        error = np.array(
            [references[name] - measured[name] for name in self._interface]
        )
        keys = ("integral_control_1", "integral_control_2")
        virtual = np.array(
            [p[f"kp_{i}"] * error[i - 1] + state.get(keys[i - 1], 0.0) for i in (1, 2)]
        )
        ki = np.array([p["ki_1"], p["ki_2"]])
        if self.family != "lag_dynamic_decoupler_then_PI":
            matrix = self._matrix("input_map")
            return matrix @ virtual, virtual, matrix, keys, error, ki
        matrix = self._matrix("dynamic_map_base")
        raw = matrix @ virtual
        for k in (1, 2, 3):
            lag = self._matrix(f"dynamic_map_lag{k}")
            old = np.array(state.get(f"dynamic_lag_{k}", [0.0, 0.0]))
            raw += lag @ (old - virtual)
            matrix -= lag
            state[f"dynamic_lag_{k}"] = (
                old + _alpha(1.0 / p[f"dynamic_filter_tau_{k}"], dt) * (virtual - old)
            ).tolist()
        return raw, virtual, matrix, keys, error, ki

    def _integrate(
        self,
        state: dict[str, Any],
        raw: np.ndarray,
        applied: np.ndarray,
        virtual: np.ndarray,
        matrix: np.ndarray,
        keys: tuple[str, ...],
        error: np.ndarray,
        ki: np.ndarray,
        dt: float,
        *,
        inverse_domain_clipped: bool,
    ) -> None:
        if not keys:
            return
        delta = ki * error * dt
        backcalc = (
            self.family in _MODAL_FAMILIES
            or self.controller.integral_handling == "back_calculation"
        )
        if self.family in _INVERSE_FAMILIES:
            # A root solver's roundoff and the intentional deadzone noise guard
            # are not actuator saturation. Only real clipping can block an
            # integral increment or create a back-calculation residual.
            residual = (
                np.array([virtual[0] - self._forward(float(applied[0]))])
                if inverse_domain_clipped or np.any(raw != applied)
                else np.zeros(1)
            )
        else:
            residual = raw - applied
        if backcalc:
            correction = (
                -residual
                if self.family in _INVERSE_FAMILIES
                else np.linalg.solve(matrix, -residual)
            )
            delta += dt * self.parameters["antiwindup_gain"] * correction
        elif self.controller.integral_handling != "none":
            for i in range(len(keys)):
                displacement = (
                    np.array([delta[i]])
                    if self.family in _INVERSE_FAMILIES
                    else matrix[:, i] * delta[i]
                )
                if np.any(residual * displacement > 0.0):
                    delta[i] = 0.0
        for i, key in enumerate(keys):
            state[key] = state.get(key, 0.0) + float(delta[i])

    def step(
        self,
        measurements: Mapping[str, float],
        reference: float | Mapping[str, float],
        dt: float,
    ) -> RuntimeSample:
        dt = _finite(dt, "dt")
        if dt <= 0.0:
            raise ValueError("dt_must_be_positive")
        if not isinstance(measurements, Mapping):
            raise TypeError("controller_measurement_mapping_required")
        missing = set(self.measured_signals) - set(measurements)
        if missing:
            raise ValueError(
                "controller_measurement_missing: " + ", ".join(sorted(missing))
            )
        measured = {
            name: _finite(value, f"measurement_{name}")
            for name, value in measurements.items()
        }
        references = self._references(reference)
        state = copy.deepcopy(self._state)
        events: list[dict[str, Any]] = []
        with np.errstate(over="ignore", invalid="ignore"):
            if self.family == "cascaded_control":
                raw = self._cascade(measured, references, state)
                virtual, matrix, keys, error, ki = (
                    raw.copy(),
                    np.eye(len(raw)),
                    (),
                    np.zeros(0),
                    np.zeros(0),
                )
            elif self.family in _MIMO:
                raw, virtual, matrix, keys, error, ki = self._channels(
                    measured, references, dt, state
                )
            elif self.family in _MODAL_FAMILIES:
                raw, virtual, matrix, keys, error, ki = self._modal(
                    measured, references, dt, state, events
                )
            else:
                raw, virtual, matrix, keys, error, ki = self._scalar(
                    measured, references, dt, state, events
                )
            if not np.all(np.isfinite(raw)) or not np.all(np.isfinite(virtual)):
                raise ValueError("controller_raw_control_must_be_finite")
            lower = np.array(
                [self.input_bounds[name][0] for name in self.control_inputs]
            )
            upper = np.array(
                [self.input_bounds[name][1] for name in self.control_inputs]
            )
            applied = np.clip(raw, lower, upper)
            self._integrate(
                state,
                raw,
                applied,
                virtual,
                matrix,
                keys,
                error,
                ki,
                dt,
                inverse_domain_clipped=any(
                    event["kind"] == "inverse_domain_clipped" for event in events
                ),
            )
        for name, value in state.items():
            if isinstance(value, str):
                continue
            if not np.all(np.isfinite(np.asarray(value, dtype=float))):
                raise ValueError(f"controller_state_must_be_finite: {name}")
        saturated = {
            name: bool(raw[i] != applied[i])
            for i, name in enumerate(self.control_inputs)
        }
        for i, name in enumerate(self.control_inputs):
            if saturated[name]:
                events.append(
                    {
                        "kind": "saturation",
                        "channel": name,
                        "raw_control": float(raw[i]),
                        "control": float(applied[i]),
                    }
                )
        self._state = state
        return RuntimeSample(
            raw_control={
                name: float(raw[i]) for i, name in enumerate(self.control_inputs)
            },
            control={
                name: float(applied[i]) for i, name in enumerate(self.control_inputs)
            },
            state=copy.deepcopy(state),
            saturated=saturated,
            events=events,
        )


__all__ = [
    "RUNTIME_REGISTRY",
    "ControllerRuntime",
    "RuntimeRegistration",
    "RuntimeSample",
    "runtime_contract",
]
