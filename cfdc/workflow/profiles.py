from __future__ import annotations

from cfdc.models import (
    ArchetypeClass,
    ArchetypeClassification,
    SemanticRouteSelection,
    SimulationProfile,
    SimulationProfileCatalog,
    StructuralDiagnosis,
    SystemDescription,
)


def default_simulation_profile_catalog() -> SimulationProfileCatalog:
    from cfdc.knowledge import profile_definitions

    return SimulationProfileCatalog(
        profiles=[
            SimulationProfile(
                profile_id=item.profile_id,
                compatible_class=ArchetypeClass(item.compatible_class),
                semantic_description=item.semantic_description,
                feature_bundle_id=item.feature_bundle_id,
                required_feature_ids=list(item.required_feature_ids),
                controller_template_id=item.controller_template_id,
                simulator_backend=item.simulator_backend,
                experiment_primitives=list(item.experiment_primitives),
                tunable_gain_names=list(item.tunable_gain_names),
                tracking_ids=list(item.tracking_ids),
                change_scenario_id=item.change_scenario_id,
            )
            for item in profile_definitions()
        ]
    )


def profile_by_id(
    catalog: SimulationProfileCatalog, profile_id: str
) -> SimulationProfile:
    for profile in catalog.profiles:
        if profile.profile_id == profile_id:
            return profile
    raise ValueError(f"unknown simulation profile '{profile_id}'")


def deterministic_profile_selection(
    description: SystemDescription,
    diagnosis: StructuralDiagnosis,
    classification: ArchetypeClassification,
    catalog: SimulationProfileCatalog,
) -> SemanticRouteSelection:
    """Select a unique profile through the canonical Registry resolver."""

    from cfdc.knowledge import resolve_route_decision, semantic_selection_for_decision

    decision = resolve_route_decision(description, diagnosis, classification)
    selection = semantic_selection_for_decision(decision)
    # Preserve the caller's catalog as the compatibility validation surface.
    profile_by_id(catalog, selection.simulation_profile_id)
    return selection


def validate_semantic_selection(
    selection: SemanticRouteSelection,
    classification: ArchetypeClassification,
    catalog: SimulationProfileCatalog,
) -> SimulationProfile:
    profile = profile_by_id(catalog, selection.simulation_profile_id)
    if str(profile.compatible_class) != str(classification.primary_class):
        raise ValueError(
            "selected simulation profile is incompatible with the canonical class"
        )
    if selection.feature_bundle_id != profile.feature_bundle_id:
        raise ValueError(
            "selected feature bundle does not belong to the simulation profile"
        )
    if selection.selected_feature_ids != profile.required_feature_ids:
        raise ValueError(
            "selected features must exactly match the catalog's minimal feature bundle"
        )
    if selection.confidence < 0.5:
        raise ValueError("semantic route selection confidence must be at least 0.5")
    return profile


def apply_profile_to_classification(
    classification: ArchetypeClassification,
    profile: SimulationProfile,
) -> ArchetypeClassification:
    return classification.model_copy(
        update={
            "required_core_features": profile.required_feature_ids,
            "control_architecture": profile.controller_template_id,
            "rationale": f"{classification.rationale} Simulation profile: {profile.profile_id}.",
        }
    )
