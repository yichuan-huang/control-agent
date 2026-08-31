"""Deterministic route and profile resolution for the migrated workflow.

The resolver consumes only the public diagnostic ledger.  It deliberately does
not inspect retrieved text, call an LLM, or infer a route from an object name.
The current :mod:`cfdc.knowledge.registry` remains the canonical source for
profile metadata; this module only adapts that registry to the new ledger.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from typing import Any

from cfdc.knowledge import (
    REGISTRY_VERSION,
    get_profile_definition,
    registry_fingerprint,
)

from .contracts import DIAGNOSTIC_IDS
from .diagnostics import DiagnosticEntry, DiagnosticLedger
from .route_catalog import controller_contract, controller_family_for_profile


@dataclass(frozen=True)
class RouteCapability:
    """Public capability declaration for one route.

    ``implemented`` means that a registered adapter and deterministic compiler
    exist.  It never means that an arbitrary physical object can be controlled.
    """

    route_id: str
    class_id: str
    profile_id: str
    implemented: bool
    required_feature_ids: tuple[str, ...]
    controller_template_id: str
    experiment_primitives: tuple[str, ...]
    limitations: tuple[str, ...]
    capability_gap: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


_CLASS_ORDER = {
    "class_v_multivariable_significant_coupling": 500,
    "class_iv_higher_order_unstable_nonlinear_or_nmp": 400,
    "class_iii_double_or_pure_integrator": 300,
    "class_ii_second_order_oscillator": 200,
    "class_i_first_order_lag": 100,
}


def _text(entry: DiagnosticEntry) -> str:
    # A normalized assessment is the authoritative semantic value.  Do not
    # reclassify it from a supporting phrase such as "没有反向响应", whose
    # negated keyword would otherwise look like positive inverse response.
    assessment = str(entry.assessment or "").strip()
    value = str(entry.value or "").strip()
    if assessment:
        return f"{assessment} {value}".casefold()

    # Older and direct expert payloads may omit assessment.  Only those
    # entries fall back to tolerant evidence matching.
    evidence = str(entry.evidence or "").casefold()
    # User evidence often repeats the field label (for example
    # ``confirmed nonminimum_phase``).  Labels are schema metadata, not
    # evidence, so remove them before applying the semantic token rules.
    for label in (*DIAGNOSTIC_IDS, "minimum_phase", "controllability_observability", "coupling_severity", "uncertainty_magnitude"):
        evidence = re.sub(rf"\b{re.escape(label.casefold())}\b", " ", evidence)
    return f"{evidence} {value}".casefold()


def _has(entry: DiagnosticEntry, *tokens: str) -> bool:
    value = _text(entry)
    stemmed = {"oscillat"}
    for token in tokens:
        normalized = token.casefold()
        if not normalized:
            continue
        # English assessment labels need word boundaries: ``stable`` must not
        # match ``unstable`` and ``low`` must not match ``below``.  Chinese
        # labels and deliberately stemmed tokens (for example ``oscillat``)
        # remain substring matches so the public evidence vocabulary stays
        # tolerant of ordinary prose.
        if normalized in stemmed:
            if normalized in value:
                return True
        elif re.fullmatch(r"[a-z0-9_]+(?: [a-z0-9_]+)*", normalized):
            if re.search(rf"(?<![a-z0-9_]){re.escape(normalized)}(?![a-z0-9_])", value):
                return True
        elif normalized in value:
            return True
    return False


def _assessment(entry: DiagnosticEntry) -> str:
    return str(entry.assessment or entry.value or entry.evidence).casefold().strip()


def _class_for_ledger(ledger: DiagnosticLedger) -> tuple[str, str]:
    """Apply the reviewed five-class priority table."""

    coupling = ledger.entry("coupling_underactuation")
    if _has(coupling, "severe_mimo", "severe mimo", "强耦合", "多变量", "mimo"):
        return "class_v_multivariable_significant_coupling", "class.v.severe_mimo"

    stability = ledger.entry("open_loop_stability")
    phase = ledger.entry("nonminimum_phase")
    degree = ledger.entry("relative_degree")
    nonlinear = ledger.entry("nonlinearity_strength")
    if (
        _has(stability, "unstable", "不稳定")
        or _has(phase, "nonminimum_phase", "nonminimum phase", "反向", "非最小相位")
        or _has(degree, "high", "higher", "高阶", "order3", "order 3")
        or _has(nonlinear, "strong_dynamic", "strong dynamic", "强动态", "强非线性")
        or _has(coupling, "underactuated", "欠驱动", "cascaded", "级联")
    ):
        return "class_iv_higher_order_unstable_nonlinear_or_nmp", "class.iv.escalating_dynamics"

    if _has(stability, "marginal", "integrator", "积分", "drift", "漂移"):
        return "class_iii_double_or_pure_integrator", "class.iii.marginal"

    if _has(degree, "order2", "order 2", "oscillat", "ringing", "振荡", "二阶"):
        return "class_ii_second_order_oscillator", "class.ii.explicit_oscillation"

    return "class_i_first_order_lag", "class.i.stable_remaining"


def _profile_for_class(class_id: str, ledger: DiagnosticLedger) -> str:
    if class_id == "class_i_first_order_lag":
        return (
            "first_order_lag_with_delay"
            if _has(ledger.entry("significant_delay"), "significant", "显著", "delay", "时延")
            and not _has(ledger.entry("significant_delay"), "not_significant", "not significant", "无")
            else "first_order_lag"
        )
    if class_id == "class_ii_second_order_oscillator":
        return "second_order_oscillator"
    if class_id == "class_iii_double_or_pure_integrator":
        return "double_integrator"
    if class_id == "class_v_multivariable_significant_coupling":
        return "mimo_2x2_coupled"
    coupling = _assessment(ledger.entry("coupling_underactuation"))
    if "underactuated" in coupling or "欠驱动" in coupling or _has(ledger.entry("coupling_underactuation"), "cartpole", "摆"):
        return "underactuated_cartpole"
    if "cascaded" in coupling or "级联" in coupling or _has(ledger.entry("coupling_underactuation"), "vtol", "hover", "悬停"):
        return "vtol_cascaded"
    if _has(ledger.entry("nonminimum_phase"), "nonminimum_phase", "nonminimum phase", "反向", "非最小相位") and _has(ledger.entry("open_loop_stability"), "stable", "稳定"):
        return "nmp_inverse_response"
    return "generic_unstable_higher_order"


def resolve_route(ledger: DiagnosticLedger) -> dict[str, Any]:
    """Resolve one route after deterministic diagnostic readiness checks."""

    readiness = ledger.readiness()
    if readiness.status != "ready":
        raise ValueError("cannot_resolve_route_before_diagnostic_readiness")
    class_id, rule_id = _class_for_ledger(ledger)
    profile_id = _profile_for_class(class_id, ledger)
    profile = get_profile_definition(profile_id)
    controller_family = controller_family_for_profile(profile.profile_id)
    contract = controller_contract(controller_family) if controller_family else None
    route_id = f"{class_id}:{profile_id}"
    # The implementation catalog currently contains deterministic adapters for
    # the scalar profiles, the explicit CartPole/VTOL fixtures, and the 2x2
    # registered route.  Generic Class IV remains an explicit capability gap.
    implemented = profile_id != "generic_unstable_higher_order"
    capability_gap = None if implemented else "generic_class_iv_route_requires_registered_object_adapter"
    return {
        "route_id": route_id,
        "class": class_id,
        "profile_id": profile.profile_id,
        "feature_ids": list(contract.get("controller_features", profile.required_feature_ids)) if contract else list(profile.required_feature_ids),
        "controller_template_id": profile.controller_template_id,
        "controller_contract_id": controller_family,
        "matched_rule_ids": [rule_id],
        "registry_version": REGISTRY_VERSION,
        "registry_fingerprint": registry_fingerprint(),
        "preconditions": list(profile.preconditions),
        "limitations": list(profile.limitations),
        "experiment_primitives": list(profile.experiment_primitives),
        "tunable_gain_names": list(contract.get("required_parameters", profile.tunable_gain_names)) if contract else list(profile.tunable_gain_names),
        "implemented": implemented,
        "capability_gap": capability_gap,
        "diagnostic_ids": list(DIAGNOSTIC_IDS),
    }


def route_capability(route: Mapping[str, Any]) -> RouteCapability:
    """Validate and normalize a route payload for downstream callers."""

    profile = get_profile_definition(str(route.get("profile_id")))
    return RouteCapability(
        route_id=str(route.get("route_id") or ""),
        class_id=str(route.get("class") or profile.compatible_class),
        profile_id=profile.profile_id,
        implemented=bool(route.get("implemented", False)),
        required_feature_ids=tuple(str(item) for item in route.get("feature_ids", profile.required_feature_ids)),
        controller_template_id=str(route.get("controller_template_id") or profile.controller_template_id),
        experiment_primitives=tuple(str(item) for item in route.get("experiment_primitives", profile.experiment_primitives)),
        limitations=tuple(str(item) for item in route.get("limitations", profile.limitations)),
        capability_gap=(str(route["capability_gap"]) if route.get("capability_gap") else None),
    )


__all__ = ["RouteCapability", "resolve_route", "route_capability"]
