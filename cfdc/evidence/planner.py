from __future__ import annotations

import hashlib

from cfdc.models import (
    ArchetypeClassification,
    EvidenceExperimentRequirement,
    EvidenceRequirementPlan,
    SemanticRouteSelection,
    StructuralDiagnosis,
    SystemDescription,
)


_EXPERIMENT_SPECS = (
    (
        "ramp_step",
        {"static_gain", "time_constant", "dead_time", "inverse_response_severity"},
        ["time", "input", "output"],
    ),
    (
        "free_decay",
        {"natural_frequency", "damping_ratio"},
        ["time", "free_response"],
    ),
    (
        "pulse",
        {
            "input_gain",
            "angular_acceleration_gain",
            "lateral_coupling_gain",
            "input_to_unactuated_coupling_gain",
        },
        ["time", "input", "position_or_rate_or_acceleration"],
    ),
    (
        "hover_thrust",
        {"hover_thrust"},
        ["time", "thrust", "lift_or_vertical_motion"],
    ),
    (
        "bounded_scan",
        {
            "local_gain_matrix",
            "local_time_constant",
            "pairing_indicator",
            "coupling_gain",
        },
        ["time", "all_inputs", "all_outputs"],
    ),
)


def plant_id_for_description(description: SystemDescription) -> str:
    identity = "|".join(
        (
            description.text.strip(),
            ",".join(description.observed_outputs),
            ",".join(description.actuators),
        )
    )
    return f"plant-{hashlib.sha256(identity.encode()).hexdigest()[:16]}"


def build_evidence_requirement_plan(
    description: SystemDescription,
    diagnosis: StructuralDiagnosis,
    classification: ArchetypeClassification,
    semantic_selection: SemanticRouteSelection | None = None,
) -> EvidenceRequirementPlan:
    """Describe the object-specific evidence required after structural diagnosis."""

    if not diagnosis.complete:
        raise ValueError(
            "evidence requirements require a complete structural diagnosis"
        )
    required = list(classification.required_core_features)
    required_set = set(required)
    requirements: list[EvidenceExperimentRequirement] = []
    covered: set[str] = set()
    for primitive, supported_features, signals in _EXPERIMENT_SPECS:
        selected = [
            feature_id for feature_id in required if feature_id in supported_features
        ]
        if not selected:
            continue
        requirements.append(
            EvidenceExperimentRequirement(
                primitive=primitive,
                feature_ids=selected,
                required_signal_ids=signals,
            )
        )
        covered.update(selected)
    unsupported = required_set - covered
    if unsupported:
        names = ", ".join(sorted(unsupported))
        raise ValueError(
            f"no evidence protocol is registered for required features: {names}"
        )

    missing_items: list[str] = []
    questions: list[str] = []
    if not description.observed_outputs:
        missing_items.append("observed_outputs")
    if not description.actuators:
        missing_items.append("actuators")
    if not description.safety_bounds:
        missing_items.append("safety_bounds")
    if description.time_scale_hint_s is None:
        missing_items.append("time_scale_hint_s")

    method_profile_id = (
        semantic_selection.simulation_profile_id
        if semantic_selection is not None
        else str(classification.primary_class)
    )
    return EvidenceRequirementPlan(
        plant_id=plant_id_for_description(description),
        method_profile_id=method_profile_id,
        required_feature_ids=required,
        accepted_sources=[
            "declared_specification",
            "structured_mathematical_model",
            "measured_traces_reserved_for_later",
        ],
        experiment_requirements=requirements,
        missing_items=missing_items,
        supplemental_questions=questions,
    )
