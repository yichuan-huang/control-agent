from __future__ import annotations

from cfdc.models import (
    ArchetypeClass,
    ArchetypeClassification,
    CoreFeatureArtifact,
    GoNoGoDecision,
)


def available_feature_ids(features: list[CoreFeatureArtifact]) -> set[str]:
    return {feature.feature_id for feature in features}


def missing_required_features(
    classification: ArchetypeClassification,
    features: list[CoreFeatureArtifact],
) -> list[str]:
    present = available_feature_ids(features)
    return [feature_id for feature_id in classification.required_core_features if feature_id not in present]


def validate_required_features(
    classification: ArchetypeClassification,
    features: list[CoreFeatureArtifact],
) -> GoNoGoDecision:
    missing = missing_required_features(classification, features)
    if missing:
        return GoNoGoDecision(
            decision="no_go",
            reasons=[
                "Stage 3 feature set is incomplete for the Stage 1 canonical class.",
            ],
            missing_features=missing,
            feature_complete=False,
        )
    return GoNoGoDecision(decision="go")


def route_compatibility_reasons(route_id: str, classification: ArchetypeClassification) -> list[str]:
    if route_id == "generic":
        return []

    primary = str(classification.primary_class)
    required = set(classification.required_core_features)

    if route_id == "cartpole":
        if primary != ArchetypeClass.CLASS_IV_HIGHER_ORDER_UNSTABLE_NONLINEAR_OR_NMP.value:
            return [
                "cartpole route requires Class IV unstable/nonlinear handling, "
                f"but Stage 1 classified the system as {primary}.",
            ]
        if "natural_frequency" not in required:
            return [
                "cartpole route requires the Class IV natural_frequency feature, "
                f"but Stage 1 requested {sorted(required)}.",
            ]
        return []

    if route_id.startswith("vtol"):
        vtol_features = {"hover_thrust", "angular_acceleration_gain", "lateral_coupling_gain"}
        if primary != ArchetypeClass.CLASS_IV_HIGHER_ORDER_UNSTABLE_NONLINEAR_OR_NMP.value:
            return [
                "VTOL route requires Class IV cascaded/NMP handling, "
                f"but Stage 1 classified the system as {primary}.",
            ]
        if not vtol_features.issubset(required):
            return [
                "VTOL route requires hover_thrust, angular_acceleration_gain, and lateral_coupling_gain, "
                f"but Stage 1 requested {sorted(required)}.",
            ]
        return []

    return [f"Unknown CFDC route_id '{route_id}'."]


def validate_route_compatibility(
    route_id: str,
    classification: ArchetypeClassification,
) -> GoNoGoDecision:
    reasons = route_compatibility_reasons(route_id, classification)
    if reasons:
        return GoNoGoDecision(
            decision="no_go",
            reasons=reasons,
            route_compatible=False,
        )
    return GoNoGoDecision(decision="go")


def merge_go_no_go(*decisions: GoNoGoDecision) -> GoNoGoDecision:
    reasons: list[str] = []
    missing_features: list[str] = []
    route_compatible = True
    feature_complete = True
    for decision in decisions:
        reasons.extend(decision.reasons)
        missing_features.extend(feature for feature in decision.missing_features if feature not in missing_features)
        route_compatible = route_compatible and decision.route_compatible
        feature_complete = feature_complete and decision.feature_complete
    if reasons or missing_features or not route_compatible or not feature_complete:
        return GoNoGoDecision(
            decision="no_go",
            reasons=reasons,
            missing_features=missing_features,
            route_compatible=route_compatible,
            feature_complete=feature_complete,
        )
    return GoNoGoDecision(decision="go")
