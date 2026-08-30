"""Canonical, typed knowledge used by CFDC routing and local RAG.

The registry contains descriptions and stable identifiers only.  It never
executes expressions or replaces the deterministic validators in the business
modules.
"""

from .registry import (
    REGISTRY_VERSION,
    ClassificationRule,
    FeatureDefinition,
    KnowledgeArtifact,
    KnowledgeContext,
    ProfileDefinition,
    RetrievalRequest,
    RuleDecision,
    canonical_knowledge_documents,
    explain_profile,
    feature_definitions,
    get_classification_rules,
    get_profile_definition,
    profile_definitions,
    registry_fingerprint,
    resolve_route_decision,
    semantic_selection_for_decision,
)

__all__ = [
    "REGISTRY_VERSION",
    "ClassificationRule",
    "FeatureDefinition",
    "KnowledgeArtifact",
    "KnowledgeContext",
    "ProfileDefinition",
    "RetrievalRequest",
    "RuleDecision",
    "canonical_knowledge_documents",
    "explain_profile",
    "feature_definitions",
    "get_classification_rules",
    "get_profile_definition",
    "profile_definitions",
    "registry_fingerprint",
    "resolve_route_decision",
    "semantic_selection_for_decision",
]
