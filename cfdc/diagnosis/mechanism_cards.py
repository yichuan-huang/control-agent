from __future__ import annotations

import json
from collections.abc import Iterable
from copy import deepcopy
from functools import lru_cache
from importlib import resources
from typing import Any

from cfdc.models import (
    ArchetypeClass,
    ArchetypeClassification,
    DelayAssessment,
    StructuralDiagnosis,
    SystemDescription,
)

CATALOG_RESOURCE = "control_mechanism_card_catalog.json"
EXPECTED_LAYER_IDS = (
    "dominant_dynamic_skeleton",
    "complex_control_mechanism",
    "execution_condition",
)
EXPECTED_CARD_IDS = (
    "self_regulating_process",
    "integrating_or_drifting",
    "oscillatory_modal",
    "unstable_equilibrium",
    "underactuated_energy_exchange",
    "hover_or_force_balance",
    "coupled_mimo",
    "delayed_or_transport_process",
    "nonminimum_phase_or_inverse_response",
    "operating_point_dependent_nonlinearity",
    "actuator_nonlinearity_or_hysteresis",
    "hybrid_or_mode_switching",
    "constraint_or_saturation_limited",
    "measurement_limited_or_noisy",
)


def _contains_any(text: str, terms: Iterable[str]) -> bool:
    return any(term in text for term in terms)


def _validate_catalog(catalog: dict[str, Any]) -> None:
    if catalog.get("artifact_type") != "cfdc_control_mechanism_card_catalog":
        raise ValueError("invalid mechanism-card catalog artifact_type")

    layers = catalog.get("layers")
    cards = catalog.get("cards")
    if not isinstance(layers, list) or not isinstance(cards, list):
        raise ValueError("mechanism-card catalog requires layers and cards arrays")

    layer_ids = tuple(layer.get("layer_id") for layer in layers)
    if layer_ids != EXPECTED_LAYER_IDS:
        raise ValueError(f"unexpected mechanism-card layers: {layer_ids}")

    card_ids = tuple(card.get("card_id") for card in cards)
    if card_ids != EXPECTED_CARD_IDS or len(set(card_ids)) != len(card_ids):
        raise ValueError(
            "mechanism-card catalog IDs are incomplete, duplicated, or out of order"
        )

    cards_by_id = {card["card_id"]: card for card in cards}
    layered_ids: list[str] = []
    for layer in layers:
        layer_id = layer["layer_id"]
        for card_id in layer.get("cards", []):
            if card_id not in cards_by_id:
                raise ValueError(f"layer {layer_id} references unknown card {card_id}")
            if cards_by_id[card_id].get("layer") != layer_id:
                raise ValueError(f"card {card_id} does not belong to layer {layer_id}")
            layered_ids.append(card_id)
    if set(layered_ids) != set(card_ids) or len(layered_ids) != len(card_ids):
        raise ValueError("each mechanism card must appear in exactly one catalog layer")

    allowed_roles = set(catalog.get("card_roles", []))
    for card in cards:
        required = {
            "card_id",
            "layer",
            "control_meaning",
            "when_to_consider",
            "typical_next_core_features",
            "common_non_core_items",
            "minimal_probe",
            "controller_implication",
            "default_roles",
        }
        missing = required.difference(card)
        if missing:
            raise ValueError(
                f"card {card['card_id']} is missing fields: {sorted(missing)}"
            )
        unknown_roles = set(card["default_roles"]).difference(allowed_roles)
        if unknown_roles:
            raise ValueError(
                f"card {card['card_id']} uses unknown roles: {sorted(unknown_roles)}"
            )


@lru_cache(maxsize=1)
def _cached_catalog() -> dict[str, Any]:
    catalog_text = (
        resources.files("cfdc.diagnosis")
        .joinpath(CATALOG_RESOURCE)
        .read_text(encoding="utf-8")
    )
    catalog = json.loads(catalog_text)
    _validate_catalog(catalog)
    return catalog


def load_mechanism_card_catalog() -> dict[str, Any]:
    """Return a validated copy of the optional supplemental-label catalog."""

    return deepcopy(_cached_catalog())


def list_mechanism_cards() -> list[dict[str, Any]]:
    """List the 14 mechanism cards in deterministic catalog order."""

    return deepcopy(_cached_catalog()["cards"])


def select_supplemental_mechanism_cards(
    description: SystemDescription | None,
    diagnosis: StructuralDiagnosis,
    classification: ArchetypeClassification,
) -> list[str]:
    """Select audit labels without changing the canonical five-class route."""

    description_text = description.text.lower() if description else ""
    diagnostic_text = " ".join(
        getattr(diagnosis, field_name).value.lower()
        + " "
        + " ".join(getattr(diagnosis, field_name).evidence).lower()
        for field_name in (
            "open_loop_stability",
            "minimum_phase",
            "relative_degree",
            "controllability_observability",
            "nonlinearity_strength",
            "coupling_severity",
            "uncertainty_magnitude",
        )
    )
    text = f"{description_text} {diagnostic_text}"
    selected: set[str] = set()

    stability = diagnosis.open_loop_stability.assessment
    coupling = diagnosis.coupling_severity.assessment
    phase = diagnosis.minimum_phase.assessment
    primary_class = str(classification.primary_class)

    if stability == "unstable":
        selected.add("unstable_equilibrium")
    elif stability == "marginal":
        selected.add("integrating_or_drifting")
    elif _contains_any(text, ["oscillat", "vibrat", "resonan", "natural frequency"]):
        selected.add("oscillatory_modal")
    elif (
        "stable" in stability
        or primary_class == ArchetypeClass.CLASS_I_FIRST_ORDER_LAG.value
    ):
        selected.add("self_regulating_process")
    elif primary_class == ArchetypeClass.CLASS_II_SECOND_ORDER_OSCILLATOR.value:
        selected.add("oscillatory_modal")
    elif primary_class == ArchetypeClass.CLASS_III_DOUBLE_OR_PURE_INTEGRATOR.value:
        selected.add("integrating_or_drifting")

    if diagnosis.coupling_severity.assessment == "underactuated" or _contains_any(
        description_text,
        [
            "underactuated",
            "cartpole",
            "cart-pole",
            "hinged on a cart",
            "swing-up",
            "swing up",
            "unactuated coordinate",
            "fewer independent actuators",
        ],
    ):
        selected.add("underactuated_energy_exchange")

    if _contains_any(
        text,
        [
            "hover",
            "vtol",
            "vertical take-off",
            "vertical takeoff",
            "balance gravity",
            "balance weight",
            "sustained thrust",
            "force balance",
        ],
    ):
        selected.add("hover_or_force_balance")

    if coupling == "severe_mimo" or _contains_any(
        description_text,
        ["coupled mimo", "coupled multi-input", "both outputs respond to both inputs"],
    ):
        selected.add("coupled_mimo")

    if diagnosis.significant_delay.assessment == DelayAssessment.SIGNIFICANT.value:
        selected.add("delayed_or_transport_process")
    if phase == "nonminimum_phase":
        selected.add("nonminimum_phase_or_inverse_response")

    if _contains_any(
        description_text,
        [
            "operating point",
            "payload",
            "mass variation",
            "inertia variation",
            "load change",
            "load varies",
            "gain changes",
            "amplitude dependent",
            "amplitude-dependent",
            "changes with level",
            "changes with speed",
        ],
    ):
        selected.add("operating_point_dependent_nonlinearity")

    if _contains_any(
        description_text,
        [
            "deadzone",
            "dead zone",
            "backlash",
            "hysteresis",
            "stiction",
            "up-sweep",
            "down-sweep",
        ],
    ):
        selected.add("actuator_nonlinearity_or_hysteresis")

    if _contains_any(
        description_text,
        [
            "mode switch",
            "mode-switch",
            "switching mode",
            "contact/no-contact",
            "contact state",
            "relay",
            "guard condition",
            "discontinuous logic",
        ],
    ):
        selected.add("hybrid_or_mode_switching")

    has_declared_constraints = bool(
        description and (description.safety_bounds or description.forbidden_actions)
    )
    if has_declared_constraints or _contains_any(
        description_text,
        [
            "saturation",
            "limited travel",
            "bounded force",
            "hard limit",
            "end stop",
            "safety boundary",
            "must be avoided",
            "must not",
        ],
    ):
        selected.add("constraint_or_saturation_limited")

    if _contains_any(
        description_text,
        [
            "sensor noise",
            "noisy measurement",
            "measurement noise",
            "sensor bias",
            "sample rate",
            "sampling is too slow",
            "state is not measured",
            "missing sensor",
        ],
    ):
        selected.add("measurement_limited_or_noisy")

    return [card_id for card_id in EXPECTED_CARD_IDS if card_id in selected]


def supplement_with_mechanism_cards(
    description: SystemDescription | None,
    diagnosis: StructuralDiagnosis,
    classification: ArchetypeClassification,
) -> ArchetypeClassification:
    selected = select_supplemental_mechanism_cards(
        description,
        diagnosis,
        classification,
    )
    return classification.model_copy(
        update={"supplemental_mechanism_cards": selected},
    )
