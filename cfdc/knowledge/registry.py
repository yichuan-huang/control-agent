"""Single source of truth for CFDC routing knowledge.

Only stable metadata and fixed evaluator keys live here.  Numeric algorithms,
fact validation, and safety gates remain in their existing deterministic
modules.  The module is deliberately dependency-light so it can also be used
while building a RAG index.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from typing import Any

REGISTRY_VERSION = "cfdc-knowledge/v1"


@dataclass(frozen=True)
class ClassificationRule:
    rule_id: str
    priority: int
    evaluator_key: str
    required_evidence_fields: tuple[str, ...]
    result_class: str
    explanation: str
    disqualifiers: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ()


@dataclass(frozen=True)
class FeatureDefinition:
    feature_id: str
    meaning: str
    canonical_unit: str | None = None
    aliases: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProfileDefinition:
    profile_id: str
    compatible_class: str
    semantic_description: str
    feature_bundle_id: str
    required_feature_ids: tuple[str, ...]
    controller_template_id: str
    experiment_primitives: tuple[str, ...]
    tunable_gain_names: tuple[str, ...]
    tracking_ids: tuple[str, ...]
    simulator_backend: str
    change_scenario_id: str
    preconditions: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ()


@dataclass(frozen=True)
class RuleDecision:
    primary_class: str
    simulation_profile_id: str
    feature_bundle_id: str
    selected_feature_ids: tuple[str, ...]
    matched_rule_ids: tuple[str, ...]
    registry_version: str
    rationale: str
    confidence: float = 1.0

    def model_dump(self) -> dict[str, Any]:
        return {
            "primary_class": self.primary_class,
            "simulation_profile_id": self.simulation_profile_id,
            "feature_bundle_id": self.feature_bundle_id,
            "selected_feature_ids": list(self.selected_feature_ids),
            "matched_rule_ids": list(self.matched_rule_ids),
            "registry_version": self.registry_version,
            "rationale": self.rationale,
            "confidence": self.confidence,
        }


@dataclass(frozen=True)
class RetrievalRequest:
    """Deterministic retrieval inputs for one role/operation."""

    role: str
    operation: str
    canonical_class: str | None = None
    profile_id: str | None = None
    missing_fields: tuple[str, ...] = ()
    summary: str = ""
    stage: str | None = None
    language: str = "auto"

    def __post_init__(self) -> None:
        if self.language not in {"auto", "en", "zh"}:
            raise ValueError("retrieval language must be auto, en, or zh")

    def preferred_language(self) -> str:
        """Resolve the requested language from the user-supplied summary only."""

        if self.language != "auto":
            return self.language
        return self.inferred_language()

    def inferred_language(self) -> str:
        """Detect Han text without consulting role, route, or retrieved content."""

        return (
            "zh" if re.search(r"[\u3400-\u4dbf\u4e00-\u9fff]", self.summary) else "en"
        )

    def query_text(self) -> str:
        parts = [self.role, self.operation]
        for value in (
            self.canonical_class,
            self.profile_id,
            self.stage,
            *self.missing_fields,
            self.summary,
        ):
            if value:
                parts.append(str(value))
        return " ".join(parts)

    def model_dump(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "operation": self.operation,
            "canonical_class": self.canonical_class,
            "profile_id": self.profile_id,
            "missing_fields": list(self.missing_fields),
            "summary": self.summary,
            "stage": self.stage,
            "language": self.language,
        }


@dataclass(frozen=True)
class KnowledgeArtifact:
    artifact_id: str
    artifact_type: str
    title: str
    text: str
    role: tuple[str, ...] = ()
    stage: tuple[str, ...] = ()
    canonical_class: str | None = None
    profile_id: str | None = None
    rule_id: str | None = None
    source_kind: str = "builtin_registry"
    registry_version: str = REGISTRY_VERSION

    def model_dump(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class KnowledgeContext:
    """Trusted contracts plus untrusted reference snippets for one call."""

    required_rules: tuple[KnowledgeArtifact, ...] = ()
    references: tuple[Any, ...] = ()
    registry_version: str = REGISTRY_VERSION
    index_snapshot: str | None = None

    def model_dump(self) -> dict[str, Any]:
        return {
            "required_rules": [item.model_dump() for item in self.required_rules],
            "references": [
                item.model_dump() if hasattr(item, "model_dump") else item
                for item in self.references
            ],
            "registry_version": self.registry_version,
            "index_snapshot": self.index_snapshot,
        }


# The tuple is intentionally explicit and reviewed with the runtime catalogs.
# ``profiles.py`` and ``method_profiles.py`` generate their Pydantic views from
# this definition, so IDs and capability metadata cannot silently drift.
_PROFILES: tuple[ProfileDefinition, ...] = (
    ProfileDefinition(
        "first_order_lag",
        "class_i_first_order_lag",
        "Stable self-regulating scalar process, optionally with transport delay.",
        "class_i_minimal",
        ("static_gain", "time_constant"),
        "detuned_pi",
        ("ramp_step",),
        ("kp", "ki"),
        ("scalar_rls",),
        "scalar_first_order",
        "gain_and_time_constant_drift",
        ("stable self-regulating scalar response",),
        ("does not model higher-order, unstable, or materially coupled dynamics",),
        ("first order", "lag", "一阶惯性", "稳定自衡"),
    ),
    ProfileDefinition(
        "first_order_lag_with_delay",
        "class_i_first_order_lag",
        "Stable self-regulating scalar process with significant dead time.",
        "class_i_delay_minimal",
        ("static_gain", "time_constant", "dead_time"),
        "detuned_pi",
        ("ramp_step",),
        ("kp", "ki"),
        ("scalar_rls",),
        "scalar_first_order_delay",
        "gain_and_time_constant_drift",
        ("stable response with explicitly significant delay",),
        ("delay must be evidenced; silence is not zero delay",),
        ("dead time", "transport delay", "时延", "延迟"),
    ),
    ProfileDefinition(
        "second_order_oscillator",
        "class_ii_second_order_oscillator",
        "Stable damped oscillatory scalar mode with a restoring force.",
        "class_ii_minimal",
        ("natural_frequency", "damping_ratio", "input_gain"),
        "damping_pd",
        ("free_decay", "pulse"),
        ("kp", "kd"),
        ("frequency_locked_loop", "scalar_rls"),
        "scalar_second_order",
        "frequency_and_gain_drift",
        ("positive ringing or free-vibration evidence",),
        ("an order bound or thermostat hysteresis alone is insufficient",),
        ("oscillator", "ringing", "振荡", "二阶"),
    ),
    ProfileDefinition(
        "double_integrator",
        "class_iii_double_or_pure_integrator",
        "Marginal non-restoring scalar motion such as position driven through acceleration.",
        "class_iii_minimal",
        ("input_gain",),
        "saturated_pd",
        ("pulse",),
        ("kp", "kd"),
        ("scalar_rls",),
        "scalar_double_integrator",
        "input_gain_drift",
        ("marginal non-restoring dynamics",),
        ("requires hard saturation and bounded excitation",),
        ("integrator", "drifting", "积分", "漂移"),
    ),
    ProfileDefinition(
        "nmp_inverse_response",
        "class_iv_higher_order_unstable_nonlinear_or_nmp",
        "Stable scalar process whose measured output initially moves opposite to its final direction.",
        "class_iv_nmp_minimal",
        ("static_gain", "time_constant", "inverse_response_severity"),
        "nmp_outer_loop",
        ("ramp_step",),
        ("kp", "ki"),
        ("scalar_rls",),
        "scalar_inverse_response",
        "gain_and_inverse_response_drift",
        ("explicit inverse-response evidence",),
        ("cannot be selected from generic delay or transient overshoot alone",),
        ("inverse response", "nonminimum phase", "反向响应", "非最小相位"),
    ),
    ProfileDefinition(
        "generic_unstable_higher_order",
        "class_iv_higher_order_unstable_nonlinear_or_nmp",
        "Generic unstable or higher-order scalar prototype without a more specific mechanism profile.",
        "class_iv_unstable_minimal",
        ("natural_frequency", "input_gain"),
        "class_iv_conservative",
        ("free_decay", "pulse"),
        ("kp", "kd"),
        ("frequency_locked_loop", "scalar_rls"),
        "generic_unstable",
        "unstable_mode_drift",
        ("Class IV condition without a more specific registered profile",),
        (
            "generic profile has no registered specification compiler for arbitrary plants",
        ),
        ("higher order", "unstable", "高阶", "不稳定"),
    ),
    ProfileDefinition(
        "underactuated_cartpole",
        "class_iv_higher_order_unstable_nonlinear_or_nmp",
        "One actuator exchanges energy between a translating base and an unactuated falling or balancing link.",
        "cartpole_minimal",
        ("natural_frequency",),
        "cartpole_cascaded",
        ("free_decay",),
        ("kp", "kd", "kp_y", "kd_y"),
        ("frequency_locked_loop",),
        "cartpole",
        "pole_frequency_drift",
        ("underactuation and an unactuated coordinate are explicit",),
        ("requires cart-pole-compatible signals; not a generic Class IV fallback",),
        ("cartpole", "underactuated", "欠驱动"),
    ),
    ProfileDefinition(
        "vtol_cascaded",
        "class_iv_higher_order_unstable_nonlinear_or_nmp",
        "Hovering vehicle where lateral motion is mediated through attitude and thrust.",
        "vtol_minimal",
        ("hover_thrust", "angular_acceleration_gain", "lateral_coupling_gain"),
        "vtol_cascaded",
        ("hover_thrust", "pulse"),
        ("kp_z", "kd_z", "kp_theta", "kd_theta", "kp_y", "kd_y"),
        ("hover_average", "scalar_rls"),
        "vtol",
        "payload_and_inertia_drift",
        ("cascaded hover and lateral coupling are explicit",),
        ("does not establish real vehicle safety or flight authority",),
        ("VTOL", "hover", "悬停", "垂直起降"),
    ),
    ProfileDefinition(
        "mimo_2x2_coupled",
        "class_v_multivariable_significant_coupling",
        "Generic two-input two-output process with material cross-channel interaction.",
        "class_v_matrix_minimal",
        ("local_gain_matrix", "local_time_constant", "pairing_indicator"),
        "mimo_decoupling_matrix",
        ("bounded_scan",),
        ("loop_1_gain", "loop_2_gain"),
        ("matrix_rls",),
        "mimo_2x2",
        "coupling_matrix_drift",
        ("two inputs and two outputs with severe coupling evidence",),
        ("only the registered 2x2 route is implemented",),
        ("MIMO", "coupled", "多变量", "耦合"),
    ),
)


_FEATURES: tuple[FeatureDefinition, ...] = (
    FeatureDefinition(
        "static_gain",
        "steady output change per input change",
        "output/input",
        ("gain", "静态增益"),
    ),
    FeatureDefinition(
        "time_constant",
        "time for a first-order response to reach about 63 percent",
        "s",
        ("response time", "时间常数"),
    ),
    FeatureDefinition(
        "dead_time",
        "transport delay before a measured response begins",
        "s",
        ("delay", "dead time", "时延"),
    ),
    FeatureDefinition(
        "natural_frequency",
        "frequency of a restoring oscillatory mode",
        "rad/s",
        ("resonant frequency", "自然频率"),
    ),
    FeatureDefinition(
        "damping_ratio",
        "dimensionless damping of an oscillatory mode",
        None,
        ("阻尼比",),
    ),
    FeatureDefinition(
        "input_gain",
        "input to acceleration or direct motion gain",
        "context dependent",
        ("输入增益",),
    ),
    FeatureDefinition(
        "inverse_response_severity",
        "initial motion opposite to final response",
        "dimensionless",
        ("nonminimum phase", "反向响应"),
    ),
    FeatureDefinition(
        "hover_thrust",
        "thrust needed to balance weight near hover",
        "force",
        ("悬停推力",),
    ),
    FeatureDefinition(
        "angular_acceleration_gain",
        "control input to angular acceleration gain",
        "context dependent",
        ("角加速度增益",),
    ),
    FeatureDefinition(
        "lateral_coupling_gain",
        "attitude/thrust to lateral motion coupling",
        "context dependent",
        ("横向耦合增益",),
    ),
    FeatureDefinition(
        "local_gain_matrix",
        "local 2x2 input-output gain matrix",
        "matrix",
        ("增益矩阵",),
    ),
    FeatureDefinition(
        "local_time_constant",
        "local response time for each coupled channel",
        "s",
        ("局部时间常数",),
    ),
    FeatureDefinition(
        "pairing_indicator",
        "registered input-output pairing indicator",
        "dimensionless",
        ("配对指标",),
    ),
)


_CLASS_RULES: tuple[ClassificationRule, ...] = (
    ClassificationRule(
        "class.v.severe_mimo",
        500,
        "coupling_severity=severe_mimo",
        ("coupling_severity",),
        "class_v_multivariable_significant_coupling",
        "Severe multivariable coupling has highest classification priority.",
        aliases=("severe MIMO", "强耦合多变量"),
    ),
    ClassificationRule(
        "class.iv.escalating_dynamics",
        400,
        "unstable|nonminimum_phase|high_relative_degree|strong_dynamic|underactuated|cascaded",
        (
            "open_loop_stability",
            "minimum_phase",
            "relative_degree",
            "nonlinearity_strength",
            "coupling_severity",
        ),
        "class_iv_higher_order_unstable_nonlinear_or_nmp",
        "Any registered Class IV condition routes to the conservative higher-order family.",
        aliases=("higher order", "不稳定", "非最小相位", "欠驱动"),
    ),
    ClassificationRule(
        "class.iii.marginal",
        300,
        "open_loop_stability=marginal",
        ("open_loop_stability",),
        "class_iii_double_or_pure_integrator",
        "Marginal non-restoring dynamics require a bounded saturated route.",
        aliases=("integrator", "边界稳定", "积分"),
    ),
    ClassificationRule(
        "class.ii.explicit_oscillation",
        200,
        "relative_degree=order2_and_explicit_oscillation",
        ("relative_degree",),
        "class_ii_second_order_oscillator",
        "A second-order oscillator is selected only with positive oscillation evidence.",
        aliases=("ringing", "振荡", "二阶振荡"),
    ),
    ClassificationRule(
        "class.i.stable_remaining",
        100,
        "stable_remaining_signature",
        ("open_loop_stability", "significant_delay"),
        "class_i_first_order_lag",
        "The remaining stable scalar signature uses the first-order lag family.",
        aliases=("first order", "一阶惯性"),
    ),
)


def profile_definitions() -> tuple[ProfileDefinition, ...]:
    return _PROFILES


def get_profile_definition(profile_id: str) -> ProfileDefinition:
    for profile in _PROFILES:
        if profile.profile_id == profile_id or profile_id in profile.aliases:
            return profile
    raise ValueError(f"unknown canonical profile '{profile_id}'")


def feature_definitions() -> tuple[FeatureDefinition, ...]:
    return _FEATURES


def get_classification_rules() -> tuple[ClassificationRule, ...]:
    return _CLASS_RULES


def registry_fingerprint() -> str:
    payload = {
        "version": REGISTRY_VERSION,
        "profiles": [asdict(item) for item in _PROFILES],
        "features": [asdict(item) for item in _FEATURES],
        "rules": [asdict(item) for item in _CLASS_RULES],
    }
    return hashlib.sha256(
        json.dumps(
            payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode()
    ).hexdigest()


def _profile_for_diagnosis(
    diagnosis: Any, classification: Any
) -> tuple[ProfileDefinition, str]:
    archetype = str(classification.primary_class)
    if archetype == "class_i_first_order_lag":
        profile_id = (
            "first_order_lag_with_delay"
            if str(diagnosis.significant_delay.assessment) == "significant"
            else "first_order_lag"
        )
    elif archetype == "class_ii_second_order_oscillator":
        profile_id = "second_order_oscillator"
    elif archetype == "class_iii_double_or_pure_integrator":
        profile_id = "double_integrator"
    elif archetype == "class_v_multivariable_significant_coupling":
        profile_id = "mimo_2x2_coupled"
    elif str(diagnosis.coupling_severity.assessment) == "underactuated":
        profile_id = "underactuated_cartpole"
    elif str(diagnosis.coupling_severity.assessment) == "cascaded":
        profile_id = "vtol_cascaded"
    elif (
        str(diagnosis.minimum_phase.assessment) == "nonminimum_phase"
        and str(diagnosis.open_loop_stability.assessment) == "stable"
    ):
        profile_id = "nmp_inverse_response"
    else:
        profile_id = "generic_unstable_higher_order"
    return get_profile_definition(profile_id), profile_id


def _matched_rule_ids(
    diagnosis: Any, classification: Any, description: Any | None
) -> tuple[str, ...]:
    del description
    class_name = str(classification.primary_class)
    if class_name == "class_v_multivariable_significant_coupling":
        return ("class.v.severe_mimo",)
    if class_name == "class_iv_higher_order_unstable_nonlinear_or_nmp":
        return ("class.iv.escalating_dynamics",)
    if class_name == "class_iii_double_or_pure_integrator":
        return ("class.iii.marginal",)
    if class_name == "class_ii_second_order_oscillator":
        return ("class.ii.explicit_oscillation",)
    return ("class.i.stable_remaining",)


def resolve_route_decision(
    description: Any,
    diagnosis: Any,
    classification: Any | None = None,
) -> RuleDecision:
    """Resolve class/profile from existing deterministic diagnosis rules.

    The description is passed to the canonical classifier when needed; no LLM
    or retrieved text is consulted.  Incomplete diagnosis is a hard stop.
    """

    if not getattr(diagnosis, "complete", False):
        raise ValueError("cannot resolve a profile from an incomplete diagnosis")
    if classification is None:
        from cfdc.diagnosis.engine import classify_archetype

        classification = classify_archetype(diagnosis, description)
    profile, _ = _profile_for_diagnosis(diagnosis, classification)
    return RuleDecision(
        primary_class=str(classification.primary_class),
        simulation_profile_id=profile.profile_id,
        feature_bundle_id=profile.feature_bundle_id,
        selected_feature_ids=profile.required_feature_ids,
        matched_rule_ids=_matched_rule_ids(diagnosis, classification, description),
        registry_version=REGISTRY_VERSION,
        rationale=(
            f"{get_classification_rules()[0].explanation if str(classification.primary_class) == get_classification_rules()[0].result_class else classification.rationale} "
            f"Canonical profile '{profile.profile_id}' is selected from the closed registry."
        ),
    )


def semantic_selection_for_decision(decision: RuleDecision) -> Any:
    """Create the legacy Pydantic selection payload from a RuleDecision."""

    from cfdc.models import SemanticRouteSelection

    return SemanticRouteSelection(
        simulation_profile_id=decision.simulation_profile_id,
        feature_bundle_id=decision.feature_bundle_id,
        selected_feature_ids=list(decision.selected_feature_ids),
        confidence=decision.confidence,
        evidence=list(decision.matched_rule_ids),
        rationale=decision.rationale,
    )


def explain_profile(decision: RuleDecision) -> dict[str, Any]:
    profile = get_profile_definition(decision.simulation_profile_id)
    rules = {rule.rule_id: rule for rule in _CLASS_RULES}
    return {
        "profile_id": profile.profile_id,
        "class": decision.primary_class,
        "matched_rule_ids": list(decision.matched_rule_ids),
        "explanation": " ".join(
            [rules[r].explanation for r in decision.matched_rule_ids if r in rules]
        )
        or decision.rationale,
        "preconditions": list(profile.preconditions),
        "limitations": list(profile.limitations),
        "registry_version": REGISTRY_VERSION,
        "source_ids": [f"builtin/rule/{r}" for r in decision.matched_rule_ids]
        + [f"builtin/profile/{profile.profile_id}"],
    }


def canonical_knowledge_documents() -> tuple[KnowledgeArtifact, ...]:
    """Render registry records into independent, searchable artifacts."""

    documents: list[KnowledgeArtifact] = []
    for rule in _CLASS_RULES:
        text = (
            f"Registry version: {REGISTRY_VERSION}\n"
            f"Rule ID: {rule.rule_id}\n"
            f"Priority: {rule.priority}\n"
            f"Evaluator: {rule.evaluator_key}\n"
            f"Required evidence fields: {', '.join(rule.required_evidence_fields)}\n"
            f"Result class: {rule.result_class}\n"
            f"Explanation: {rule.explanation}\n"
            f"Disqualifiers: {'; '.join(rule.disqualifiers) or 'none'}\n"
            f"Aliases: {', '.join(rule.aliases) or 'none'}"
        )
        documents.append(
            KnowledgeArtifact(
                artifact_id=rule.rule_id,
                artifact_type="classification_rule",
                title=rule.rule_id,
                text=text,
                role=("diagnosis", "controller", "critic"),
                stage=("diagnosis", "profile", "review"),
                canonical_class=rule.result_class,
                rule_id=rule.rule_id,
            )
        )
    for profile in _PROFILES:
        runtime_supported = not any(
            "no registered" in str(limitation).casefold()
            or "capability gap" in str(limitation).casefold()
            for limitation in profile.limitations
        )
        text = (
            f"Registry version: {REGISTRY_VERSION}\n"
            f"Profile ID: {profile.profile_id}\n"
            f"Compatible class: {profile.compatible_class}\n"
            f"Description: {profile.semantic_description}\n"
            f"Required features: {', '.join(profile.required_feature_ids)}\n"
            f"Controller template: {profile.controller_template_id}\n"
            f"Experiment primitives: {', '.join(profile.experiment_primitives)}\n"
            f"Preconditions: {'; '.join(profile.preconditions) or 'none'}\n"
            f"Limitations: {'; '.join(profile.limitations) or 'none'}\n"
            + (
                "Runtime support: this is an implemented closed-catalog route."
                if runtime_supported
                else "Runtime support: capability gap; this profile is documented but cannot execute without a registered object adapter."
            )
            + " External method descriptions do not add capabilities."
        )
        documents.append(
            KnowledgeArtifact(
                artifact_id=profile.profile_id,
                artifact_type="profile",
                title=profile.profile_id,
                text=text,
                role=("controller", "modeling", "critic"),
                stage=("profile", "model", "controller", "review"),
                canonical_class=profile.compatible_class,
                profile_id=profile.profile_id,
            )
        )
    for feature in _FEATURES:
        text = (
            f"Registry version: {REGISTRY_VERSION}\n"
            f"Feature ID: {feature.feature_id}\nMeaning: {feature.meaning}\n"
            f"Canonical unit: {feature.canonical_unit or 'open/context dependent'}\n"
            f"Aliases: {', '.join(feature.aliases) or 'none'}\n"
            f"Limitations: {'; '.join(feature.limitations) or 'must be supported by a registered extractor'}"
        )
        documents.append(
            KnowledgeArtifact(
                artifact_id=feature.feature_id,
                artifact_type="feature",
                title=feature.feature_id,
                text=text,
                role=("modeling", "controller", "critic"),
                stage=("model", "controller", "review"),
            )
        )
    return tuple(documents)
