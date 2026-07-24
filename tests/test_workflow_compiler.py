import pytest

from cfdc.models import (
    ArchetypeClass,
    ArchetypeClassification,
    BenchmarkRouteIR,
    SemanticRouteSelection,
    SystemDescription,
)
from cfdc.runtime import run_cfdc_route
from cfdc.workflow import (
    compile_candidate_route,
    default_capability_catalog,
    default_simulation_profile_catalog,
    validate_semantic_selection,
)


def test_candidate_route_round_trip_and_no_hidden_parameters():
    report = run_cfdc_route("cartpole", include_trajectory=False)
    payload = report.candidate_route.model_dump_json()
    assert report.compiled_route.executable
    assert "plant_params" not in payload and "mass_kg" not in payload


def test_semantic_selection_rejects_unknown_extra_and_wrong_class():
    catalog = default_simulation_profile_catalog()
    classification = ArchetypeClassification(
        primary_class=ArchetypeClass.CLASS_I_FIRST_ORDER_LAG,
        control_architecture="pi",
        required_core_features=["static_gain", "time_constant"],
        rationale="test",
    )
    with pytest.raises(ValueError, match="exactly match"):
        validate_semantic_selection(
            SemanticRouteSelection(
                simulation_profile_id="first_order_lag",
                feature_bundle_id="class_i_minimal",
                selected_feature_ids=[
                    "static_gain",
                    "time_constant",
                    "invented_feature",
                ],
                confidence=0.9,
                evidence=["x"],
                rationale="x",
            ),
            classification,
            catalog,
        )
    with pytest.raises(ValueError, match="incompatible"):
        validate_semantic_selection(
            SemanticRouteSelection(
                simulation_profile_id="double_integrator",
                feature_bundle_id="class_iii_minimal",
                selected_feature_ids=["input_gain"],
                confidence=0.9,
                evidence=["x"],
                rationale="x",
            ),
            classification,
            catalog,
        )


def test_class_v_matrix_route_is_executable():
    description = SystemDescription(
        text="A strongly coupled MIMO process with multiple inputs and outputs.",
        observed_outputs=["y1", "y2"],
        actuators=["u1", "u2"],
    )
    report = run_cfdc_route(
        "generic", description=description, execution_mode="demo_fixture"
    )
    assert report.semantic_selection.simulation_profile_id == "mimo_2x2_coupled"
    assert report.compiled_route.executable
    matrix = next(
        feature
        for feature in report.features
        if feature.feature_id == "local_gain_matrix"
    )
    assert isinstance(matrix.value, list)
    assert len(matrix.value) == 2
    assert (
        report.controller.architecture
        == "conservative_mimo_pairing_with_half_strength_decoupling"
    )


def test_compiler_refuses_benchmark_ir():
    benchmark = BenchmarkRouteIR(
        case_id="hidden",
        plant_family="cartpole",
        reference={"position": 0},
        horizon_s=10,
        dt_s=0.01,
        plant_params={"mass_kg": 2},
        actuator_limits={"force": 10},
    )
    with pytest.raises(TypeError, match="CandidateRouteIR"):
        compile_candidate_route(benchmark, default_capability_catalog())
