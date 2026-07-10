import json
import sys

from cfdc.diagnosis import DiagnosticEngine, load_mechanism_card_catalog
from cfdc.models import ArchetypeClassification, CoreFeatureArtifact, SystemDescription
from cfdc.pipeline import run_cfdc_pipeline
from cfdc.runtime import run_cfdc_route
from main import parse_args


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


def feature(feature_id: str, value: float) -> CoreFeatureArtifact:
    width = max(abs(value) * 0.05, 1e-6)
    return CoreFeatureArtifact(
        feature_id=feature_id,
        value=value,
        lower_bound=value - width,
        upper_bound=value + width,
        confidence=0.9,
        units="unit",
        method="mechanism-card-test",
        source_experiment="ramp_step",
    )


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
    assert {card_id for card_ids in layers.values() for card_id in card_ids} == set(cards)
    assert all(card["layer"] in layers for card in cards.values())
    assert json.loads(json.dumps(catalog)) == catalog


def test_mechanism_cards_are_disabled_by_default_in_engine_pipeline_and_route():
    description = SystemDescription(
        text="A first order temperature process settles after a small heater change.",
        observed_outputs=["temperature"],
        actuators=["heater"],
    )
    engine = DiagnosticEngine()
    diagnosis, classification = engine.run(description)
    assert diagnosis.complete
    assert classification is not None
    assert classification.supplemental_mechanism_cards == []

    features = [feature("static_gain", 2.0), feature("time_constant", 5.0)]
    pipeline = run_cfdc_pipeline(description, features=features)
    route = run_cfdc_route("generic", description=description, features=features)
    assert pipeline["classification"]["supplemental_mechanism_cards"] == []
    assert route.classification is not None
    assert route.classification.supplemental_mechanism_cards == []


def test_cartpole_and_vtol_receive_expected_supplemental_cards_when_enabled():
    cartpole = SystemDescription(
        text=(
            "A rod hinged on a cart falls over when upright. The cart motor pushes left "
            "and right. Cart position and rod angle are measured. Travel and force are limited."
        ),
        observed_outputs=["cart position", "rod angle"],
        actuators=["cart motor"],
        safety_bounds={"max_abs_position": 2.4, "max_abs_control": 10.0},
    )
    vtol = SystemDescription(
        text=(
            "A VTOL aircraft with two rotors can hover and move sideways by tilting. "
            "Payload can change. Altitude, position, and attitude are measured."
        ),
        observed_outputs=["altitude", "lateral position", "attitude"],
        actuators=["total thrust", "roll torque"],
        safety_bounds={"max_tilt_rad": 0.7},
    )
    engine = DiagnosticEngine(use_mechanism_cards=True)

    _, cartpole_classification = engine.run(cartpole)
    _, vtol_classification = engine.run(vtol)
    assert cartpole_classification is not None
    assert vtol_classification is not None
    assert {
        "unstable_equilibrium",
        "underactuated_energy_exchange",
        "nonminimum_phase_or_inverse_response",
        "constraint_or_saturation_limited",
    }.issubset(cartpole_classification.supplemental_mechanism_cards)
    assert {
        "unstable_equilibrium",
        "hover_or_force_balance",
        "nonminimum_phase_or_inverse_response",
        "operating_point_dependent_nonlinearity",
        "constraint_or_saturation_limited",
    }.issubset(vtol_classification.supplemental_mechanism_cards)


def test_delay_and_hysteresis_cards_are_selected_from_diagnosis_and_description():
    delayed = SystemDescription(
        text="A first order heater settles after a valve step, with a noticeable dead time.",
        observed_outputs=["temperature"],
        actuators=["valve"],
    )
    hysteretic = SystemDescription(
        text=(
            "A first order positioning actuator settles after a command and has no delay, "
            "but deadzone, backlash, hysteresis, and current saturation are known."
        ),
        observed_outputs=["position"],
        actuators=["motor command"],
    )
    engine = DiagnosticEngine(use_mechanism_cards=True)

    _, delayed_classification = engine.run(delayed)
    _, hysteretic_classification = engine.run(hysteretic)
    assert delayed_classification is not None
    assert delayed_classification.supplemental_mechanism_cards == [
        "self_regulating_process",
        "delayed_or_transport_process",
    ]
    assert hysteretic_classification is not None
    assert "actuator_nonlinearity_or_hysteresis" in hysteretic_classification.supplemental_mechanism_cards
    assert "constraint_or_saturation_limited" in hysteretic_classification.supplemental_mechanism_cards


def test_no_reported_delay_does_not_select_delay_card():
    description = SystemDescription(
        text="A self-regulating first order process settles after a small input change.",
        observed_outputs=["output"],
        actuators=["input"],
    )
    _, classification = DiagnosticEngine(use_mechanism_cards=True).run(description)

    assert classification is not None
    assert classification.supplemental_mechanism_cards == ["self_regulating_process"]


def test_enabling_cards_does_not_change_canonical_route_or_controller():
    description = SystemDescription(
        text="A first order heater settles after a valve step, with a noticeable dead time.",
        observed_outputs=["temperature"],
        actuators=["valve"],
        safety_bounds={"output_min": -2.0, "output_max": 2.0},
    )
    features = [
        feature("static_gain", 2.0),
        feature("time_constant", 5.0),
        feature("dead_time", 1.0),
    ]
    without_cards = run_cfdc_pipeline(description, features=features)
    with_cards = run_cfdc_pipeline(
        description,
        features=features,
        use_mechanism_cards=True,
    )

    base_classification = without_cards["classification"]
    enhanced_classification = with_cards["classification"]
    for field_name in [
        "primary_class",
        "control_architecture",
        "required_core_features",
        "safety_constraints",
        "rationale",
    ]:
        assert enhanced_classification[field_name] == base_classification[field_name]
    assert base_classification["supplemental_mechanism_cards"] == []
    assert enhanced_classification["supplemental_mechanism_cards"] == [
        "self_regulating_process",
        "delayed_or_transport_process",
        "constraint_or_saturation_limited",
    ]
    assert with_cards["controller"] == without_cards["controller"]

    restored = ArchetypeClassification.model_validate_json(
        json.dumps(enhanced_classification)
    )
    assert restored.model_dump() == enhanced_classification


def test_cli_exposes_explicit_mechanism_card_opt_in(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["main.py", "--run-route", "generic", "--use-mechanism-cards"],
    )
    assert parse_args().use_mechanism_cards is True
