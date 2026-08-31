"""Restricted controller intermediate representation and deterministic checks."""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from .contracts import CONTROLLER_IR_VERSION, fingerprint

_FORBIDDEN_KEYS = {
    "python",
    "code",
    "source",
    "expression",
    "eval",
    "exec",
    "command",
    "shell",
}
_ALLOWED_INTEGRAL_HANDLING = {
    "none",
    "reset_on_phase_entry",
    "clamped",
    "anti_windup",
    "back_calculation",
}


def _finite(value: Any, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"controller_{label}_must_be_numeric") from exc
    if not math.isfinite(number):
        raise ValueError(f"controller_{label}_must_be_finite")
    return number


def _clean_names(values: Any, label: str) -> tuple[str, ...]:
    if isinstance(values, str):
        values = (values,)
    if values is None:
        values = ()
    result = tuple(str(item).strip() for item in values if str(item).strip())
    if len(result) != len(set(result)):
        raise ValueError(f"duplicate_controller_{label}")
    return result


def _bounds(value: Any, label: str) -> tuple[float, float]:
    if isinstance(value, (str, bytes)) or not isinstance(value, (tuple, list)) or len(value) != 2:
        raise ValueError(f"controller_{label}_bounds_invalid")
    lower = _finite(value[0], f"{label}_lower")
    upper = _finite(value[1], f"{label}_upper")
    if lower >= upper:
        raise ValueError(f"controller_{label}_bounds_invalid")
    return lower, upper


def _reject_executable_values(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if str(key).casefold() in _FORBIDDEN_KEYS:
                raise ValueError("controller_ir_executable_content_not_allowed")
            _reject_executable_values(item)
    elif isinstance(value, (tuple, list)):
        for item in value:
            _reject_executable_values(item)
    elif callable(value):
        raise TypeError("controller_ir_callable_not_allowed")


@dataclass(frozen=True)
class ControllerIR:
    """Declarative controller description accepted by the runtime.

    A Controller Agent may fill this structure, but the numeric backend only
    accepts registered ``family`` values and bounded parameters.
    """

    family: str
    measured_signals: tuple[str, ...]
    control_inputs: tuple[str, ...]
    parameters: Mapping[str, float]
    parameter_domains: Mapping[str, tuple[float, float]]
    output_bounds: tuple[float, float] | None = None
    state_limits: Mapping[str, tuple[float, float]] = field(default_factory=dict)
    stop_conditions: tuple[str, ...] = ()
    integral_handling: str = "none"
    phase_id: str | None = None
    ir_version: str = CONTROLLER_IR_VERSION

    def __post_init__(self) -> None:
        if not self.family.strip():
            raise ValueError("controller_family_required")
        if not self.measured_signals or not self.control_inputs:
            raise ValueError("controller_interface_required")
        if self.ir_version != CONTROLLER_IR_VERSION:
            raise ValueError("controller_ir_version_mismatch")
        if self.integral_handling not in _ALLOWED_INTEGRAL_HANDLING:
            raise ValueError("controller_integral_handling_invalid")
        _reject_executable_values(self.to_dict(include_fingerprint=False))
        names = set(self.parameters)
        domains = set(self.parameter_domains)
        if any(not str(name).strip() for name in names | domains):
            raise ValueError("controller_parameter_name_required")
        if not names <= domains:
            raise ValueError("controller_parameter_domain_missing")
        for name, value in self.parameters.items():
            number = _finite(value, f"parameter_{name}")
            lower, upper = self.parameter_domains[name]
            lower = _finite(lower, f"domain_{name}_lower")
            upper = _finite(upper, f"domain_{name}_upper")
            if lower >= upper or not lower <= number <= upper:
                raise ValueError(f"controller_parameter_out_of_domain: {name}")
        for name, bounds in self.state_limits.items():
            if not str(name).strip() or not isinstance(bounds, (tuple, list)) or len(bounds) != 2:
                raise ValueError("controller_state_limit_invalid")
            lower = _finite(bounds[0], f"state_{name}_lower")
            upper = _finite(bounds[1], f"state_{name}_upper")
            if lower >= upper:
                raise ValueError(f"controller_state_limit_invalid: {name}")
        if self.output_bounds is not None:
            lower, upper = self.output_bounds
            if _finite(lower, "output_lower") >= _finite(upper, "output_upper"):
                raise ValueError("controller_output_bounds_invalid")

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> ControllerIR:
        raw = dict(value)
        _reject_executable_values(raw)
        supplied_fingerprint = raw.pop("controller_fingerprint", raw.pop("fingerprint", None))
        params_raw = raw.get("parameters") or {}
        domains_raw = raw.get("parameter_domains") or {}
        states_raw = raw.get("state_limits") or {}
        if not isinstance(params_raw, Mapping) or not isinstance(domains_raw, Mapping) or not isinstance(states_raw, Mapping):
            raise TypeError("controller_parameter_mappings_required")
        params = {str(key): _finite(item, f"parameter_{key}") for key, item in params_raw.items()}
        domains = {
            str(key): _bounds(item, f"domain_{key}")
            for key, item in domains_raw.items()
        }
        state_limits = {
            str(key): _bounds(item, f"state_{key}")
            for key, item in states_raw.items()
        }
        output_bounds = raw.get("output_bounds")
        if output_bounds is not None:
            output_bounds = _bounds(output_bounds, "output")
        controller = cls(
            family=str(raw.get("family") or raw.get("controller_family") or "").strip(),
            measured_signals=_clean_names(raw.get("measured_signals") or raw.get("sensed_signals"), "signals"),
            control_inputs=_clean_names(raw.get("control_inputs") or raw.get("control_input") or raw.get("actuators"), "inputs"),
            parameters=params,
            parameter_domains=domains,
            output_bounds=output_bounds,
            state_limits=state_limits,
            stop_conditions=_clean_names(raw.get("stop_conditions"), "stop_conditions"),
            integral_handling=str(raw.get("integral_handling") or "none"),
            phase_id=str(raw["phase_id"]) if raw.get("phase_id") is not None else None,
            ir_version=str(raw.get("ir_version") or CONTROLLER_IR_VERSION),
        )
        if supplied_fingerprint is not None and str(supplied_fingerprint) != controller.fingerprint:
            raise ValueError("controller_ir_fingerprint_mismatch")
        return controller

    @property
    def fingerprint(self) -> str:
        return fingerprint(self.to_dict(include_fingerprint=False))

    def to_dict(self, *, include_fingerprint: bool = True) -> dict[str, Any]:
        value = {
            "ir_version": self.ir_version,
            "family": self.family,
            "measured_signals": list(self.measured_signals),
            "control_inputs": list(self.control_inputs),
            "parameters": dict(self.parameters),
            "parameter_domains": {key: list(bounds) for key, bounds in self.parameter_domains.items()},
            "output_bounds": list(self.output_bounds) if self.output_bounds is not None else None,
            "state_limits": {key: list(bounds) for key, bounds in self.state_limits.items()},
            "stop_conditions": list(self.stop_conditions),
            "integral_handling": self.integral_handling,
            "phase_id": self.phase_id,
        }
        if include_fingerprint:
            value["controller_fingerprint"] = self.fingerprint
        return value


def validate_controller_for_route(controller: ControllerIR, route: Mapping[str, Any]) -> dict[str, Any]:
    """Check family and required features before an IR can be frozen."""

    validate_controller_family_for_route(controller.family, route)
    allowed = {str(item) for item in route.get("tunable_gain_names", ()) or ()}
    if route.get("controller_contract_id"):
        from .route_catalog import controller_contract

        contract = controller_contract(controller.family)
        if contract is None:
            raise ValueError(f"controller_contract_not_registered: {controller.family}")
        compatibility_family = str(route.get("controller_template_id") or "")
        if controller.family.casefold() != compatibility_family.casefold():
            required = {str(item) for item in contract.get("required_parameters", ())}
            missing = sorted(required - set(controller.parameters))
            if missing:
                raise ValueError("controller_required_parameters_missing: " + ", ".join(missing))
        allowed = set(controller.parameters)
    if allowed:
        extra = sorted(set(controller.parameters) - allowed)
        if extra:
            raise ValueError(
                "controller_parameter_not_allowed: " + ", ".join(extra)
            )
    return {
        "status": "validated",
        "route_id": route.get("route_id"),
        "controller_fingerprint": controller.fingerprint,
        "family": controller.family,
        "parameter_names": sorted(controller.parameters),
    }


def validate_controller_family_for_route(family: str, route: Mapping[str, Any]) -> None:
    """Validate only the registered controller family for compatibility paths."""

    expected = str(route.get("controller_contract_id") or route.get("controller_template_id") or "")
    if route.get("controller_contract_id"):
        from .route_catalog import canonical_controller_family

        if canonical_controller_family(family).casefold() != canonical_controller_family(expected).casefold():
            raise ValueError(f"controller_family_incompatible: expected {expected}")
        return
    aliases = {
        "detuned_pi": {"detuned_pi", "pi", "pid"},
        "damping_pd": {"damping_pd", "pd", "pid"},
        "saturated_pd": {"saturated_pd", "pd", "pid"},
        "nmp_outer_loop": {"nmp_outer_loop", "pi", "pid"},
        "cartpole_cascaded": {"cartpole_cascaded", "cascade"},
        "vtol_cascaded": {"vtol_cascaded", "cascade"},
        "mimo_decoupling_matrix": {"mimo_decoupling_matrix", "mimo"},
        "class_iv_conservative": {"class_iv_conservative", "pd", "pi", "pid"},
    }
    allowed = aliases.get(expected, {expected} if expected else set())
    normalized = str(family).strip().casefold()
    if normalized not in {str(item).casefold() for item in allowed}:
        raise ValueError(f"controller_family_incompatible: expected {expected}")


__all__ = ["ControllerIR", "validate_controller_family_for_route", "validate_controller_for_route"]
