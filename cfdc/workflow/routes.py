from __future__ import annotations

import re

from cfdc.models import (
    ArchetypeClass,
    ArchetypeClassification,
    CandidateExperimentRequest,
    CandidateRouteIR,
    DataProvenance,
    ExperimentPlan,
    ExperimentPrimitive,
    StructuralDiagnosis,
    SystemDescription,
    WorkflowMode,
)


def _architecture_id(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return normalized or "unspecified_control_architecture"


def _controller_route(
    classification: ArchetypeClassification,
) -> tuple[str, list[str], str]:
    archetype = str(classification.primary_class)
    features = set(classification.required_core_features)
    if archetype == ArchetypeClass.CLASS_I_FIRST_ORDER_LAG.value:
        return "detuned_pi", ["kp", "ki"], "bounded_gain_refinement"
    if archetype == ArchetypeClass.CLASS_II_SECOND_ORDER_OSCILLATOR.value:
        return "damping_pd", ["kp", "kd"], "bounded_gain_refinement"
    if archetype == ArchetypeClass.CLASS_III_DOUBLE_OR_PURE_INTEGRATOR.value:
        return "saturated_pd", ["kp", "kd"], "bounded_gain_refinement"
    if archetype == ArchetypeClass.CLASS_V_MULTIVARIABLE_SIGNIFICANT_COUPLING.value:
        return "mimo_decoupling_matrix", [], "bounded_gain_refinement"
    if "hover_thrust" in features:
        return (
            "vtol_cascaded",
            ["kp_z", "kd_z", "kp_theta", "kd_theta", "kp_y", "kd_y"],
            "bounded_gain_refinement",
        )
    if "natural_frequency" in features:
        return (
            "cartpole_cascaded",
            ["kp_theta", "kd_theta", "kp_y", "kd_y"],
            "bounded_gain_refinement",
        )
    if "local_static_gain" in features:
        return "gain_scheduled_pi", ["kp", "ki"], "bounded_gain_refinement"
    if "inverse_response_severity" in features:
        return "nmp_outer_loop", ["kp", "ki"], "bounded_gain_refinement"
    return "class_iv_conservative", [], "bounded_gain_refinement"


def _signals_for_request(
    primitive: str,
    feature_ids: list[str],
) -> tuple[list[str], list[str]]:
    if primitive == ExperimentPrimitive.FREE_DECAY.value:
        return [], ["free_response"]
    if primitive == ExperimentPrimitive.RAMP_STEP.value:
        return ["input"], ["output"]
    if primitive == ExperimentPrimitive.HOVER_THRUST.value:
        return ["thrust"], ["lift"]
    if primitive == ExperimentPrimitive.BOUNDED_SCAN.value:
        return ["input"], ["primary_output", "coupled_output"]
    outputs: list[str] = []
    if "input_gain" in feature_ids:
        outputs.append("acceleration")
    if "angular_acceleration_gain" in feature_ids:
        outputs.append("angular_acceleration")
    if "lateral_coupling_gain" in feature_ids:
        outputs.extend(["tilt", "coupled_output"])
    if "input_to_unactuated_coupling_gain" in feature_ids:
        outputs.extend(["actuated_motion", "unactuated_motion"])
    return ["input"], outputs or ["response"]


def _tracking_requests(feature_ids: list[str]) -> list[str]:
    requests: list[str] = []
    if "natural_frequency" in feature_ids:
        requests.append("frequency_locked_loop")
    if set(feature_ids) & {
        "static_gain",
        "input_gain",
        "angular_acceleration_gain",
        "lateral_coupling_gain",
        "coupling_gain",
    }:
        requests.append("scalar_rls")
    if "hover_thrust" in feature_ids:
        requests.append("hover_average")
    return requests


def build_candidate_route(
    route_id: str,
    diagnosis: StructuralDiagnosis,
    classification: ArchetypeClassification,
    description: SystemDescription,
    experiment_plan: ExperimentPlan,
    workflow_mode: WorkflowMode | str,
) -> CandidateRouteIR:
    """Build an executable-intent IR only from declared diagnostic evidence."""

    del diagnosis  # Its resolved evidence is represented by the classification.
    mode = WorkflowMode(workflow_mode)
    provenance = (
        DataProvenance.REAL_EXPERIMENT
        if mode == WorkflowMode.REAL
        else DataProvenance.SYNTHETIC_FIXTURE
    )
    requests: list[CandidateExperimentRequest] = []
    for index, instruction in enumerate(experiment_plan.instructions, start=1):
        primitive = str(instruction.primitive)
        inputs, outputs = _signals_for_request(primitive, instruction.estimates)
        requests.append(
            CandidateExperimentRequest(
                request_id=f"experiment-{index}-{primitive}",
                primitive=primitive,
                input_signal_ids=inputs,
                output_signal_ids=outputs,
                feature_ids=instruction.estimates,
                stop_conditions=instruction.stop_conditions,
                provenance_requirement=provenance,
            )
        )

    template_id, gain_names, refinement_id = _controller_route(classification)
    safety_constraints = list(classification.safety_constraints)
    safety_constraints.extend(
        f"declared_bound:{name}" for name in sorted(description.safety_bounds)
    )
    safety_constraints.extend(
        f"forbidden_action:{action}" for action in description.forbidden_actions
    )
    if not safety_constraints:
        safety_constraints.append("operator_declared_safe_region_required")

    return CandidateRouteIR(
        route_id=route_id,
        workflow_mode=mode,
        canonical_class=classification.primary_class,
        supplemental_mechanism_cards=classification.supplemental_mechanism_cards,
        control_architecture_id=_architecture_id(classification.control_architecture),
        experiment_requests=requests,
        required_core_feature_ids=classification.required_core_features,
        controller_template_id=template_id,
        tunable_gain_names=gain_names,
        online_refinement_policy_id=refinement_id,
        feature_tracking_requests=_tracking_requests(
            classification.required_core_features
        ),
        validation_metrics=[
            "overshoot",
            "settling_time_s",
            "integral_absolute_error",
            "high_frequency_control_rms",
            "actuator_saturation_fraction",
            "nmp_undershoot",
        ],
        safety_constraints=safety_constraints,
    )
