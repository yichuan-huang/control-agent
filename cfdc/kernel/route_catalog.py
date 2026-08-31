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


__all__ = [
    "ROUTE_CATALOG_VERSION",
    "canonical_controller_family",
    "capability_gap_routes",
    "controller_contract",
    "controller_family_for_profile",
    "implemented_controller_families",
    "known_feature_ids",
    "route_catalog",
]
