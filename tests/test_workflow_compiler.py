import pytest

from cfdc.diagnosis import DiagnosticEngine
from cfdc.experiments import plan_safe_experiments
from cfdc.models import (
    ArchetypeClass,
    ArchetypeClassification,
    BenchmarkRouteIR,
    CandidateRouteIR,
    DataProvenance,
    SystemDescription,
    WorkflowMode,
)
from cfdc.runtime import run_cfdc_route
from cfdc.workflow import (
    build_candidate_route,
    compile_candidate_route,
    default_capability_catalog,
)


def _cartpole_route(workflow_mode=WorkflowMode.SIMULATION):
    description = SystemDescription(
        text=(
            "A rod hinged on a cart falls over when upright. The cart motor can push "
            "left and right, and cart position and rod angle are measured."
        ),
        observed_outputs=["cart position", "rod angle"],
        actuators=["cart motor force"],
        safety_bounds={"max_abs_position": 2.4, "max_abs_control": 10.0},
    )
    engine = DiagnosticEngine()
    diagnosis = engine.diagnose(description)
    classification = engine.classify(diagnosis, description)
    plan = plan_safe_experiments(diagnosis, classification)
    return build_candidate_route(
        "cartpole",
        diagnosis,
        classification,
        description,
        plan,
        workflow_mode,
    )


def _gap_codes(route):
    compiled = compile_candidate_route(route, default_capability_catalog())
    return compiled, {gap.code for gap in compiled.gaps}


def test_candidate_route_ir_round_trips_without_hidden_plant_parameters():
    route = _cartpole_route()

    restored = CandidateRouteIR.model_validate_json(route.model_dump_json())
    payload = route.model_dump_json()

    assert restored == route
    assert route.schema_version == "1.0"
    assert route.required_core_feature_ids == ["natural_frequency"]
    assert "plant_params" not in payload
    assert "mass_kg" not in payload
    assert "inertia" not in payload
    assert "gravity_m_s2" not in payload


def test_supported_candidate_route_compiles_without_gaps():
    compiled, codes = _gap_codes(_cartpole_route())

    assert compiled.executable
    assert codes == set()


def test_compiler_reports_unknown_primitive_and_missing_signals():
    route = _cartpole_route()
    request = route.experiment_requests[0]

    unknown = route.model_copy(
        update={
            "experiment_requests": [
                request.model_copy(update={"primitive": "teleport_probe"})
            ]
        }
    )
    _, unknown_codes = _gap_codes(unknown)
    assert "unknown_experiment_primitive" in unknown_codes

    missing_signal = route.model_copy(
        update={
            "experiment_requests": [
                request.model_copy(update={"output_signal_ids": []})
            ]
        }
    )
    _, signal_codes = _gap_codes(missing_signal)
    assert "missing_experiment_signal" in signal_codes


def test_compiler_reports_controller_class_and_tracker_gaps():
    route = _cartpole_route()

    wrong_controller = route.model_copy(
        update={"controller_template_id": "detuned_pi"}
    )
    _, controller_codes = _gap_codes(wrong_controller)
    assert "controller_class_mismatch" in controller_codes

    missing_tracker = route.model_copy(
        update={"feature_tracking_requests": ["unimplemented_tracker"]}
    )
    _, tracker_codes = _gap_codes(missing_tracker)
    assert "missing_tracking_implementation" in tracker_codes


def test_compiler_reports_unimplemented_mimo_matrix_route():
    description = SystemDescription(
        text="A coupled MIMO process has multiple measured outputs and multiple inputs.",
        observed_outputs=["output_1", "output_2"],
        actuators=["input_1", "input_2"],
        safety_bounds={"max_abs_control": 1.0, "max_abs_output": 1.0},
    )
    engine = DiagnosticEngine()
    diagnosis = engine.diagnose(description)
    classification = ArchetypeClassification(
        primary_class=ArchetypeClass.CLASS_V_MULTIVARIABLE_SIGNIFICANT_COUPLING,
        control_architecture="local gain matrix pairing and decoupling",
        required_core_features=[
            "local_gain_matrix",
            "local_time_constant",
            "pairing_indicator",
        ],
        safety_constraints=["one input at a time"],
        rationale="Significant multivariable coupling requires matrix handling.",
    )
    plan = plan_safe_experiments(diagnosis, classification)
    route = build_candidate_route(
        "generic",
        diagnosis,
        classification,
        description,
        plan,
        WorkflowMode.REAL,
    )

    compiled, codes = _gap_codes(route)

    assert not compiled.executable
    assert "unimplemented_mimo_matrix_route" in codes
    assert "unsupported_feature_extractor" in codes


def test_compiler_refuses_benchmark_route_ir_with_hidden_plant_parameters():
    benchmark = BenchmarkRouteIR(
        case_id="hidden-plant",
        plant_family="cartpole",
        reference={"position": 0.0},
        horizon_s=10.0,
        dt_s=0.01,
        plant_params={"mass_kg": 2.0},
        actuator_limits={"force_n": 10.0},
    )

    with pytest.raises(TypeError, match="CandidateRouteIR"):
        compile_candidate_route(benchmark, default_capability_catalog())


def test_compiler_rejects_synthetic_provenance_requirement_in_real_mode():
    route = _cartpole_route(WorkflowMode.REAL)
    synthetic_request = route.experiment_requests[0].model_copy(
        update={"provenance_requirement": DataProvenance.SYNTHETIC_FIXTURE}
    )
    route = route.model_copy(update={"experiment_requests": [synthetic_request]})

    compiled, codes = _gap_codes(route)

    assert not compiled.executable
    assert "synthetic_provenance_forbidden" in codes


def test_orchestrator_reports_candidate_and_compiled_routes():
    report = run_cfdc_route("cartpole", include_trajectory=False)

    assert report.candidate_route is not None
    assert report.compiled_route is not None
    assert report.compiled_route.executable
    assert report.compiled_route.gaps == []
