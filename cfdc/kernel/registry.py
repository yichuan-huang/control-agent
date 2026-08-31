"""Kernel-facing view of the shared CFDC knowledge registry."""

from cfdc.knowledge import (
    REGISTRY_VERSION,
    ClassificationRule,
    FeatureDefinition,
    ProfileDefinition,
    feature_definitions,
    get_classification_rules,
    get_profile_definition,
    profile_definitions,
    registry_fingerprint,
)

from .routes import RouteCapability, resolve_route, route_capability

__all__ = [
    "REGISTRY_VERSION",
    "ClassificationRule",
    "FeatureDefinition",
    "ProfileDefinition",
    "RouteCapability",
    "feature_definitions",
    "get_classification_rules",
    "get_profile_definition",
    "profile_definitions",
    "registry_fingerprint",
    "resolve_route",
    "route_capability",
]
