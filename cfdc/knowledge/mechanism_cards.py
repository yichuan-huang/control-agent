from __future__ import annotations

import json
from copy import deepcopy
from functools import lru_cache
from importlib import resources
from typing import Any

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


def _validate_catalog(catalog: dict[str, Any]) -> None:
    if catalog.get("artifact_type") != "cfdc_control_mechanism_card_catalog":
        raise ValueError("invalid mechanism-card catalog artifact_type")

    layers = catalog.get("layers")
    cards = catalog.get("cards")
    if not isinstance(layers, list) or not isinstance(cards, list):
        raise TypeError("mechanism-card catalog requires layers and cards arrays")

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
        resources.files("cfdc.knowledge")
        .joinpath("resources")
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
