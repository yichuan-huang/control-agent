import math

from cfdc.diagnosis import DiagnosticEngine
from cfdc.experiments import plan_safe_experiments
from cfdc.models import ExperimentPrimitive, SystemDescription
from cfdc.runtime import run_cfdc_route


def _diagnosis_and_classification(description):
    engine = DiagnosticEngine()
    diagnosis = engine.diagnose(description)
    return diagnosis, engine.classify(diagnosis, description)


def test_step_parameters_scale_with_declared_bounds_and_time_scale():
    description = SystemDescription(text="A first order temperature process settles after a heater change.", observed_outputs=["temperature"], actuators=["heater"], safety_bounds={"max_abs_control": 20.0}, time_scale_hint_s=2.0)
    diagnosis, classification = _diagnosis_and_classification(description)
    instruction = plan_safe_experiments(diagnosis, classification, description).instructions[0]
    assert math.isclose(instruction.input_amplitude, 2.0)
    assert math.isclose(instruction.duration_s, 16.0)
    assert math.isclose(instruction.sample_rate_hz, 25.0)


def test_missing_bounds_block_user_object_experiment_parameterization():
    description = SystemDescription(text="A first order temperature process settles after a heater change.", observed_outputs=["temperature"], actuators=["heater"])
    diagnosis, classification = _diagnosis_and_classification(description)
    plan = plan_safe_experiments(diagnosis, classification, description)
    assert plan.parameterization_status == "blocked"
    assert plan.instructions[0].input_amplitude is None
    assert plan.planning_gaps[0].code == "missing_numeric_safety_bound"


def test_forbidden_actions_block_automatic_experiment_plan():
    description = SystemDescription(text="A measured spring oscillator returns with a decaying vibration.", observed_outputs=["position"], actuators=["force"], forbidden_actions=["free release", "pulse"])
    diagnosis, classification = _diagnosis_and_classification(description)
    plan = plan_safe_experiments(diagnosis, classification, description)
    assert plan.parameterization_status == "blocked"
    assert {gap.code for gap in plan.planning_gaps} == {"forbidden_experiment_action"}


def test_route_parameters_propagate_to_candidate_requests():
    report = run_cfdc_route("cartpole", include_trajectory=False)
    planned = report.experiment_plan.instructions[0]
    requested = report.candidate_route.experiment_requests[0]
    assert planned.primitive == ExperimentPrimitive.FREE_DECAY
    assert requested.input_amplitude == planned.input_amplitude
    assert requested.duration_s == planned.duration_s
    assert requested.sample_rate_hz == planned.sample_rate_hz
