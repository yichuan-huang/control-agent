import json

from cfdc.knowledge.mechanism_cards import load_mechanism_card_catalog

EXPECTED_CARD_IDS = [
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
]


def test_catalog_contains_all_three_layers_and_fourteen_cards():
    catalog = load_mechanism_card_catalog()
    layers = {layer["layer_id"]: layer["cards"] for layer in catalog["layers"]}
    cards = {card["card_id"]: card for card in catalog["cards"]}

    assert list(layers) == [
        "dominant_dynamic_skeleton",
        "complex_control_mechanism",
        "execution_condition",
    ]
    assert list(cards) == EXPECTED_CARD_IDS
    assert {card_id for card_ids in layers.values() for card_id in card_ids} == set(
        cards
    )
    assert all(card["layer"] in layers for card in cards.values())
    assert json.loads(json.dumps(catalog)) == catalog
