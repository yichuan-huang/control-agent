"""Versioned CFDC v3 route and controller contract catalog."""

from __future__ import annotations

import json
from copy import deepcopy
from functools import lru_cache
from importlib.resources import files
from typing import Any

ROUTE_CATALOG_VERSION = "cfdc-route/v2.7.1"

_ALIASES = {
    "detuned_pi": "PI",
    "damping_pd": "two_dof_pid",
    "saturated_pd": "PD_integrator",
    "nmp_outer_loop": "two_dof_PI",
    "cartpole_cascaded": "cascaded_control",
    "vtol_cascaded": "cascaded_control",
    "mimo_decoupling_matrix": "decentralized_channel_PI",
    "two_degree_of_freedom_PI": "two_dof_PI",
    "low_bandwidth_PI": "two_dof_PI",
}

_PROFILE_FAMILIES = {
    "first_order_lag": "PI",
    "first_order_lag_with_delay": "delay_aware_PI",
    "second_order_oscillator": "two_dof_pid",
    "double_integrator": "PD_integrator",
    "nmp_inverse_response": "two_dof_PI",
    "underactuated_cartpole": "cascaded_control",
    "vtol_cascaded": "cascaded_control",
    "mimo_2x2_coupled": "decentralized_channel_PI",
}


def _resource(name: str) -> dict[str, Any]:
    path = files("cfdc.kernel").joinpath("resources", name)
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def route_catalog() -> dict[str, Any]:
    base = _resource("control_route_registry.v2.7.1.json")
    extension = _resource("control_route_extensions.v1.json")
    contracts = {**base["controller_contracts"], **extension["controller_contracts"]}
    subtypes = deepcopy(base["class_subtypes"])
    for class_id, values in extension.get("class_subtypes", {}).items():
        subtypes.setdefault(class_id, {}).update(deepcopy(values))
    route_to_subtype = {
        **base.get("route_to_subtype", {}),
        **extension.get("route_to_subtype", {}),
    }
    return {
        "catalog_version": ROUTE_CATALOG_VERSION,
        "source_registry_version": base["registry_version"],
        "controller_contracts": contracts,
        "class_subtypes": subtypes,
        "route_to_subtype": route_to_subtype,
        "provider_capabilities": _resource("provider_capabilities.v1.json"),
    }


def canonical_controller_family(family: str) -> str:
    value = str(family).strip()
    return _ALIASES.get(value, value)


def controller_contract(family: str) -> dict[str, Any] | None:
    canonical = canonical_controller_family(family)
    value = route_catalog()["controller_contracts"].get(canonical)
    return deepcopy(value) if isinstance(value, dict) else None


def controller_family_for_profile(profile_id: str) -> str | None:
    return _PROFILE_FAMILIES.get(str(profile_id))


def implemented_controller_families() -> tuple[str, ...]:
    return tuple(sorted(route_catalog()["controller_contracts"]))


def capability_gap_routes() -> tuple[str, ...]:
    routes: set[str] = set()
    for classes in route_catalog()["class_subtypes"].values():
        for subtype in classes.values():
            for route in subtype.get("routes", ()):
                if str(route).endswith("capability_gap") or "capability_gap" in str(
                    route
                ):
                    routes.add(str(route))
    return tuple(sorted(routes))


def known_feature_ids() -> frozenset[str]:
    ids: set[str] = set()
    for classes in route_catalog()["class_subtypes"].values():
        for subtype in classes.values():
            ids.update(str(item) for item in subtype.get("controller_features", ()))
    for contract in route_catalog()["controller_contracts"].values():
        ids.update(str(item) for item in contract.get("controller_features", ()))
        ids.update(str(item) for item in contract.get("route_guard_features", ()))
    ids.update(
        {
            "time_constant",
            "dead_time",
            "input_gain",
            "drag_rate",
            "inverse_response_severity",
            "static_gain",
            "natural_frequency",
            "damping_ratio",
            "acceleration_gain",
            "delay_bound",
        }
    )
    return frozenset(ids)


def select_route_from_features(
    artifact: dict[str, Any],
    task: dict[str, Any],
    prior_route: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Select an executable family from released public numerical features."""

    features = artifact.get("features") or {}

    def value(name: str, default: float | None = None) -> float | None:
        item = features.get(name)
        if isinstance(item, dict) and isinstance(item.get("value"), (int, float)):
            return float(item["value"])
        return default

    family: str | None = None
    gap: str | None = None
    measured = tuple(str(item) for item in task.get("measured_signals", ()))
    controls = tuple(
        str(item) for item in task.get("control_inputs") or (task.get("control_input"),)
    )
    if (
        len(measured) >= 2
        and len(controls) >= 2
        and value("gain_matrix_condition") is not None
    ):
        condition = float(value("gain_matrix_condition", float("inf")))
        inverse = float(value("static_inverse_amplification", float("inf")))
        cross = float(value("dc_static_cross_ratio", float("inf")))
        residual = float(value("dynamic_decoupler_fit_residual", float("inf")))
        if condition > 50.0 or inverse > 20.0:
            gap = "static_decoupling_capability_gap"
        elif cross <= 0.2:
            family = "decentralized_channel_PI"
        elif (
            inverse <= 8.0
            and float(value("inband_static_decoupler_residual", 1.0)) <= 0.35
        ):
            family = "static_decoupler_then_PI"
        elif (
            residual <= 0.35
            and float(value("dynamic_inverse_peak_amplification", float("inf"))) <= 12.0
        ):
            family = "lag_dynamic_decoupler_then_PI"
        else:
            gap = "dynamic_decoupling_capability_gap"
    elif value("history_dependence_index") is not None:
        if float(value("history_dependence_index", 1.0)) > 0.03:
            gap = "history_dependent_static_inverse_gap"
        elif float(value("static_map_derivative_lower_bound", -1.0)) <= 0.0:
            gap = "noninvertible_static_map_gap"
        elif abs(float(value("static_map_cubic_coefficient", 0.0))) > 0.05:
            family = "partial_inverse_then_PI"
        elif (
            max(
                float(value("positive_deadzone", 0.0)),
                float(value("negative_deadzone", 0.0)),
            )
            > 0.1
        ):
            family = "deadzone_right_inverse_then_PI"
        else:
            family = "local_PI_without_inverse"
    elif value("small_amplitude_decay_rate") is not None:
        small = float(value("small_amplitude_decay_rate", 0.0))
        quadratic = float(value("quadratic_decay_rate", 0.0))
        crossing = float(value("zero_decay_crossing_amplitude", 0.0))
        if small < 0 < quadratic and crossing > 0:
            family = "self_excitation_energy_guarded_PID"
        elif float(value("amplitude_dependence_index", 0.0)) > 0.1:
            family = "scheduled_damping_PID"
        elif small > 0:
            family = "local_fixed_PID"
        else:
            gap = "nonlinear_decay_qualification_gap"
    elif value("static_gain") is not None:
        delay = float(value("delay_bound", 0.0))
        tau = max(float(value("dominant_time_constant", 1.0)), 1e-12)
        inverse = float(value("inverse_response_severity", 0.0))
        residual = float(value("low_order_residual", 0.0))
        if inverse > 0.05:
            family = "two_dof_PI"
        elif residual > 0.25:
            guard = value("phase_guard_frequency")
            family = "phase_guarded_2dof_PI" if guard else None
            gap = None if family else "high_order_phase_evidence_gap"
        elif delay / tau > 0.15:
            family = "delay_aware_PI"
        else:
            family = "PI"
    elif prior_route:
        return dict(prior_route)
    else:
        gap = "public_features_do_not_resolve_controller_route"

    profile_by_family = {
        "PI": "first_order_lag",
        "delay_aware_PI": "first_order_lag_with_delay",
        "notch_then_PI": "second_order_oscillator",
        "two_dof_pid": "second_order_oscillator",
        "P_integrator": "double_integrator",
        "PD_integrator": "double_integrator",
        "lead_lag_series": "double_integrator",
        "two_dof_PI": "nmp_inverse_response",
        "cascaded_control": "underactuated_cartpole",
        "local_PI_without_inverse": "first_order_lag",
        "partial_inverse_then_PI": "first_order_lag",
        "deadzone_right_inverse_then_PI": "first_order_lag",
        "reduced_low_order_PI": "first_order_lag",
        "phase_guarded_2dof_PI": "generic_unstable_higher_order",
        "local_fixed_PID": "generic_unstable_higher_order",
        "scheduled_damping_PID": "generic_unstable_higher_order",
        "self_excitation_energy_guarded_PID": "generic_unstable_higher_order",
        "decentralized_channel_PI": "mimo_2x2_coupled",
        "static_decoupler_then_PI": "mimo_2x2_coupled",
        "lag_dynamic_decoupler_then_PI": "mimo_2x2_coupled",
    }
    contract = controller_contract(family) if family else None
    required = (
        list(
            dict.fromkeys(
                [
                    *contract.get("controller_features", ()),
                    *contract.get("route_guard_features", ()),
                ]
            )
        )
        if contract
        else []
    )
    profile = profile_by_family.get(family or "", "capability_gap")
    return {
        "route_id": f"public-analysis:{family or 'capability_gap'}",
        "profile_id": profile,
        "controller_family": family,
        "controller_contract_id": family,
        "controller_template_id": family,
        "feature_ids": required,
        "implemented": family is not None,
        "capability_gap": gap,
        "selection_basis": "versioned public numerical features",
        "source_feature_artifact_fingerprint": artifact.get("artifact_fingerprint"),
    }


__all__ = [
    "ROUTE_CATALOG_VERSION",
    "canonical_controller_family",
    "capability_gap_routes",
    "controller_contract",
    "controller_family_for_profile",
    "implemented_controller_families",
    "known_feature_ids",
    "route_catalog",
    "select_route_from_features",
]
