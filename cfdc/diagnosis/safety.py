from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from cfdc.models import (
    ArchetypeClassification,
    DelayAssessment,
    DiagnosticField,
    GoNoGoDecision,
    SignificantDelayField,
    StructuralDiagnosis,
    SystemDescription,
)


DIAGNOSTIC_FIELD_NAMES = (
    "open_loop_stability",
    "minimum_phase",
    "significant_delay",
    "relative_degree",
    "controllability_observability",
    "nonlinearity_strength",
    "coupling_severity",
    "uncertainty_magnitude",
)
CONTROLLER_SYNTHESIS_FEATURES = {
    "static_gain",
    "time_constant",
    "dead_time",
    "natural_frequency",
    "damping_ratio",
    "input_gain",
    "inverse_response_severity",
    "hover_thrust",
    "angular_acceleration_gain",
    "lateral_coupling_gain",
    "coupling_gain",
}


def _contains_any(text: str, terms: Iterable[str]) -> bool:
    return any(term in text for term in terms)


def has_explicit_delay_ambiguity(description: SystemDescription) -> bool:
    text = description.text.lower()
    return _contains_any(
        text,
        [
            "first-motion timing has not been observed",
            "first motion timing has not been observed",
            "timing has not been observed",
            "delay has not been observed",
            "delay is unknown",
            "unknown delay",
            "dead time is unknown",
            "unknown dead time",
            "latency is unknown",
        ],
    )


def has_operating_point_dependence(description: SystemDescription) -> bool:
    text = description.text.lower()
    return _contains_any(
        text,
        [
            "operating point",
            "operating region",
            "safe operating points",
            "gain and time constant vary",
            "gain varies with",
            "time constant varies with",
            "vary strongly with temperature",
            "vary strongly with conversion",
            "amplitude-dependent dynamics",
            "amplitude dependent dynamics",
        ],
    )


def has_strong_mimo_interaction(description: SystemDescription) -> bool:
    text = description.text.lower()
    multiple_actuators = len(description.actuators) > 1
    return multiple_actuators and _contains_any(
        text,
        [
            "both controlled lower levels respond to both pumps",
            "both outputs respond to both inputs",
            "each input affects multiple outputs",
            "one input strongly affects several outputs",
            "interconnected tank levels",
            "strong cross-channel",
            "strongly coupled mimo",
        ],
    )


def has_underactuated_energy_exchange(description: SystemDescription) -> bool:
    text = description.text.lower()
    return _contains_any(
        text,
        [
            "acrobot",
            "underactuated energy",
            "unactuated link",
            "unactuated joint",
            "only one actuated joint",
            "natural dynamics and link coupling",
        ],
    )


def has_actuator_nonlinearity(description: SystemDescription) -> bool:
    return _contains_any(
        description.text.lower(),
        ["deadzone", "dead zone", "backlash", "hysteresis", "stiction"],
    )


def _field(
    status: str,
    value: str,
    confidence: float,
    evidence: str,
) -> DiagnosticField:
    return DiagnosticField(
        status=status,
        value=value,
        confidence=confidence,
        evidence=[evidence],
    )


def _delay_field(
    status: str,
    value: str,
    assessment: DelayAssessment,
    confidence: float,
    evidence: str,
) -> SignificantDelayField:
    return SignificantDelayField(
        status=status,
        value=value,
        assessment=assessment,
        confidence=confidence,
        evidence=[evidence],
    )


def _clarification_questions(
    description: SystemDescription,
    payload: dict[str, Any],
) -> list[str]:
    questions = list(payload.get("clarification_questions", []))
    text = description.text.lower()
    mechanism_questions: list[str] = []
    if _contains_any(
        text,
        [
            "deadzone",
            "dead zone",
            "backlash",
            "stiction",
            "small commands may not move",
        ],
    ):
        mechanism_questions.append(
            "What is the smallest command that reliably starts visible motion in each direction?"
        )
    if _contains_any(text, ["hysteresis", "backlash", "memory"]):
        mechanism_questions.append(
            "When the command is moved upward and then downward, how different are the recorded motion paths?"
        )
    questions = [*mechanism_questions, *questions]
    if has_explicit_delay_ambiguity(description):
        questions.insert(
            0,
            "After a small safe input change, is there a noticeable pause before the output starts moving?",
        )
    if payload["minimum_phase"]["status"] == "unknown":
        questions.append(
            "Does a small safe input change first move the output in the expected direction or the opposite direction?"
        )
    if payload["coupling_severity"]["status"] == "unknown":
        questions.append(
            "When one input changes, which measured outputs move noticeably?"
        )
    questions.extend(
        [
            "What output or motion range must not be crossed during the first test?",
            "What is the smallest reversible input change that is safe to try?",
        ]
    )
    deduplicated: list[str] = []
    for question in questions:
        if question not in deduplicated:
            deduplicated.append(question)
    return deduplicated[:4]


def enforce_shared_diagnostic_safety_rules(
    description: SystemDescription,
    diagnosis: StructuralDiagnosis,
) -> StructuralDiagnosis:
    """Apply evidence rules after either deterministic or LLM diagnosis."""

    updates: dict[str, DiagnosticField] = {}
    text = description.text.lower()

    if has_underactuated_energy_exchange(description):
        updates.update(
            {
                "open_loop_stability": _field(
                    "inferred",
                    "unstable or safety-critical equilibrium",
                    0.82,
                    "the unactuated link must swing near an upright target before stabilization",
                ),
                "minimum_phase": _field(
                    "inferred",
                    "non-minimum phase or underactuated inverse-response risk",
                    0.72,
                    "the controlled coordinate moves through an actuated coordinate and energy exchange",
                ),
                "significant_delay": _delay_field(
                    "inferred",
                    "no significant delay reported",
                    DelayAssessment.NOT_SIGNIFICANT,
                    0.58,
                    "the description presents a direct mechanical torque path and no transport delay",
                ),
                "relative_degree": _field(
                    "inferred",
                    "higher relative degree with an underactuated coordinate",
                    0.80,
                    "one actuator must move two linked coordinates through natural dynamics",
                ),
                "nonlinearity_strength": _field(
                    "inferred",
                    "strong nonlinearity from large-angle energy exchange",
                    0.82,
                    "swing-up and upright capture require large-angle motion",
                ),
                "coupling_severity": _field(
                    "inferred",
                    "moderate underactuated energy-exchange coupling",
                    0.80,
                    "the actuated joint moves an unactuated link through coupling",
                ),
                "uncertainty_magnitude": _field(
                    "known",
                    "large uncertainty in masses, inertias, and coupling strength",
                    0.86,
                    "the description states that physical masses and inertias are unknown",
                ),
            }
        )

    if has_operating_point_dependence(description):
        updates.update(
            {
                "nonlinearity_strength": _field(
                    "known",
                    "strong nonlinearity with operating-point-dependent dynamics",
                    0.90,
                    "the description states that gain or time scale changes across operating points",
                ),
                "coupling_severity": _field(
                    "inferred",
                    "moderate multivariable coupling across local operating regions",
                    0.70,
                    "multiple manipulated and measured variables are declared but strong cross-response is not established",
                ),
                "uncertainty_magnitude": _field(
                    "known",
                    "large uncertainty across operating points",
                    0.88,
                    "local dynamics vary strongly with the operating condition",
                ),
            }
        )

    if has_strong_mimo_interaction(description):
        updates.update(
            {
                "minimum_phase": _field(
                    "inferred",
                    "non-minimum phase or inverse-response risk",
                    0.78,
                    "the description reports unfavorable initial motion in a coupled process",
                ),
                "coupling_severity": _field(
                    "known",
                    "significant multivariable coupling requiring a local gain matrix and pairing",
                    0.92,
                    "each candidate input visibly affects multiple controlled outputs",
                ),
                "uncertainty_magnitude": _field(
                    "inferred",
                    "large uncertainty in multivariable interaction and pairing",
                    0.78,
                    "the local input-output pairing and cross-channel strengths are unresolved",
                ),
            }
        )

    if has_explicit_delay_ambiguity(description):
        updates["significant_delay"] = _delay_field(
            "unknown",
            "not enough information about first-motion delay",
            DelayAssessment.UNKNOWN,
            0.18,
            "the description explicitly says first-motion timing has not been observed",
        )
        if not _contains_any(text, ["payload", "wear", "operating condition", "varies"]):
            updates["uncertainty_magnitude"] = _field(
                "inferred",
                "moderate uncertainty",
                0.55,
                "delay remains unknown but no large parameter variation is described",
            )

    payload = diagnosis.model_dump()
    for field_name, field_value in updates.items():
        payload[field_name] = field_value.model_dump()
    complete = all(
        payload[field_name]["status"] != "unknown"
        for field_name in DIAGNOSTIC_FIELD_NAMES
    )
    payload["complete"] = complete
    payload["clarification_questions"] = (
        [] if complete else _clarification_questions(description, payload)
    )
    return StructuralDiagnosis.model_validate(payload)


def diagnostic_required_feature_plan(
    description: SystemDescription,
    diagnosis: StructuralDiagnosis,
    classification: ArchetypeClassification | None,
) -> list[str]:
    """Return classified or provisional next features for diagnostic auditing."""

    del diagnosis
    if classification is not None:
        return list(classification.required_core_features)
    text = description.text.lower()
    if has_explicit_delay_ambiguity(description) and _contains_any(
        text,
        ["heater", "temperature", "first order", "first-order", "settles"],
    ):
        return ["static_gain", "time_constant", "dead_time"]
    if has_actuator_nonlinearity(description):
        features: list[str] = []
        if _contains_any(text, ["deadzone", "dead zone", "backlash"]):
            features.append("deadzone_width")
        if _contains_any(text, ["hysteresis", "backlash", "memory"]):
            features.append("hysteresis_width")
        features.append("effective_gain_after_deadzone")
        return features
    return []


def validate_diagnostic_controller_release(
    description: SystemDescription,
    diagnosis: StructuralDiagnosis,
    classification: ArchetypeClassification | None,
) -> GoNoGoDecision:
    """Shared deterministic safety gate for every diagnostic adapter."""

    reasons: list[str] = []
    if not diagnosis.complete or classification is None:
        reasons.append("Stage 0 diagnosis is incomplete; clarification is required before controller release.")
    if has_explicit_delay_ambiguity(description):
        reasons.append("First-motion delay is explicitly unresolved; measure or clarify dead time before PI release.")
    if has_operating_point_dependence(description):
        reasons.append("Operating-point-dependent dynamics require local feature validation and an operating-region boundary.")
    if has_strong_mimo_interaction(description):
        reasons.append("Strong MIMO interaction requires a local gain matrix and pairing evidence before controller release.")
    unsupported: list[str] = []
    missing_features: list[str] = []
    if classification is not None:
        unsupported = [
            feature_id
            for feature_id in classification.required_core_features
            if feature_id not in CONTROLLER_SYNTHESIS_FEATURES
        ]
        if unsupported:
            reasons.append(
                "Current deterministic synthesis does not support the required diagnostic features: "
                + ", ".join(unsupported)
                + "."
            )
        if (
            diagnosis.significant_delay.assessment
            == DelayAssessment.SIGNIFICANT.value
            and "dead_time" not in classification.required_core_features
        ):
            reasons.append(
                "A significant-delay diagnosis requires dead_time before controller release."
            )
            missing_features.append("dead_time")
    missing_features.extend(
        feature for feature in unsupported if feature not in missing_features
    )
    if reasons:
        return GoNoGoDecision(
            decision="no_go",
            reasons=reasons,
            missing_features=missing_features,
            feature_complete=not missing_features,
        )
    return GoNoGoDecision(decision="go")
