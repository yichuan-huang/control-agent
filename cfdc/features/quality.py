from __future__ import annotations

import math
import re

from cfdc.models import (
    ArchetypeClassification,
    CoreFeatureArtifact,
    FeatureQualityDecision,
    FeatureQualityIssue,
    FeatureQualityPolicy,
)


_STRICTLY_POSITIVE = {
    "natural_frequency",
    "time_constant",
    "hover_thrust",
    "angular_acceleration_gain",
    "local_time_constant",
}
_NONNEGATIVE = {
    "damping_ratio",
    "dead_time",
    "inverse_response_severity",
}
_CRITICAL_NONZERO = {
    "static_gain",
    "input_gain",
    "angular_acceleration_gain",
}
_REPEATABLE_FLAGS = {
    "few_decay_peaks",
    "high_noise",
    "insufficient_cycles",
    "insufficient_samples",
    "low_snr",
    "poor_fit",
    "steady_state_not_fully_confirmed",
    "weak_frequency_lock",
    "weak_lock",
}
_REFUSAL_FLAGS = {
    "forbidden_provenance",
    "invalid_physical_domain",
    "non_finite_data",
    "unsafe_experiment",
    "zero_critical_denominator",
}
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _issue(
    code: str,
    feature_id: str,
    severity: str,
    explanation: str,
) -> FeatureQualityIssue:
    return FeatureQualityIssue(
        code=code,
        feature_id=feature_id,
        severity=severity,
        explanation=explanation,
    )


def evaluate_feature_quality(
    classification: ArchetypeClassification,
    features: list[CoreFeatureArtifact],
    policy: FeatureQualityPolicy | None = None,
) -> FeatureQualityDecision:
    """Fail closed before any controller consumes released core features."""

    resolved_policy = policy or FeatureQualityPolicy()
    issues: list[FeatureQualityIssue] = []
    feature_by_id: dict[str, CoreFeatureArtifact] = {}

    for feature in features:
        if feature.feature_id in feature_by_id:
            issues.append(
                _issue(
                    "duplicate_feature_id",
                    feature.feature_id,
                    "refuse",
                    "A release packet cannot contain duplicate feature identifiers.",
                )
            )
        feature_by_id[feature.feature_id] = feature

    for feature_id in classification.required_core_features:
        if feature_id not in feature_by_id:
            issues.append(
                _issue(
                    "missing_required_feature",
                    feature_id,
                    "repeat_experiment",
                    "The canonical class requires this feature before controller synthesis.",
                )
            )

    for feature in features:
        feature_id = feature.feature_id
        if not feature.object_id or not feature.object_id.strip():
            issues.append(
                _issue(
                    "missing_object_id",
                    feature_id,
                    "refuse",
                    "Feature artifacts require a stable object identifier.",
                )
            )
        if any(
            not value.strip()
            for value in (
                feature.experiment_protocol_version,
                feature.estimator_version,
                feature.operating_region,
            )
        ):
            issues.append(
                _issue(
                    "invalid_provenance_metadata",
                    feature_id,
                    "refuse",
                    "Protocol, estimator, and operating-region provenance fields must be non-empty.",
                )
            )
        if isinstance(feature.value, list):
            matrix_values = [value for row in feature.value for value in row]
            if not matrix_values or not all(math.isfinite(value) for value in matrix_values):
                issues.append(
                    _issue(
                        "non_finite_feature_value",
                        feature_id,
                        "refuse",
                        "Matrix feature elements must be finite.",
                    )
                )
            if feature_id != "local_gain_matrix":
                issues.append(
                    _issue(
                        "invalid_matrix_feature",
                        feature_id,
                        "refuse",
                        "Only the registered local gain matrix may use a matrix value.",
                    )
                )
            if feature.confidence < resolved_policy.minimum_confidence:
                issues.append(
                    _issue(
                        "confidence_below_release_threshold",
                        feature_id,
                        "repeat_experiment",
                        f"Confidence {feature.confidence:g} is below {resolved_policy.minimum_confidence:g}.",
                    )
                )
            continue
        assert feature.lower_bound is not None and feature.upper_bound is not None
        values = (feature.value, feature.lower_bound, feature.upper_bound)
        if not all(math.isfinite(value) for value in values):
            issues.append(
                _issue(
                    "non_finite_feature_value",
                    feature_id,
                    "refuse",
                    "Feature values and bounds must be finite.",
                )
            )
            continue
        if feature_id in _STRICTLY_POSITIVE and (
            feature.value <= 0.0 or feature.lower_bound <= 0.0
        ):
            issues.append(
                _issue(
                    "invalid_physical_domain",
                    feature_id,
                    "refuse",
                    "This feature and its released lower bound must be strictly positive.",
                )
            )
        if feature_id in _NONNEGATIVE and (
            feature.value < 0.0 or feature.lower_bound < 0.0
        ):
            issues.append(
                _issue(
                    "invalid_physical_domain",
                    feature_id,
                    "refuse",
                    "This feature and its released lower bound must be nonnegative.",
                )
            )
        if feature_id == "damping_ratio" and feature.upper_bound > 1.0:
            issues.append(
                _issue(
                    "invalid_physical_domain",
                    feature_id,
                    "refuse",
                    "The damping-ratio confidence interval must remain within [0, 1].",
                )
            )
        if feature_id in _CRITICAL_NONZERO and (
            feature.value == 0.0
            or feature.lower_bound <= 0.0 <= feature.upper_bound
        ):
            issues.append(
                _issue(
                    "zero_critical_denominator",
                    feature_id,
                    "refuse",
                    "A feature inverted during synthesis cannot be zero or cross zero.",
                )
            )
        if feature.confidence < resolved_policy.minimum_confidence:
            issues.append(
                _issue(
                    "confidence_below_release_threshold",
                    feature_id,
                    "repeat_experiment",
                    f"Confidence {feature.confidence:g} is below {resolved_policy.minimum_confidence:g}.",
                )
            )
        if feature.value != 0.0:
            relative_half_width = max(
                abs(feature.upper_bound - feature.value),
                abs(feature.value - feature.lower_bound),
            ) / abs(feature.value)
            if relative_half_width > resolved_policy.maximum_relative_half_width:
                issues.append(
                    _issue(
                        "confidence_interval_too_wide",
                        feature_id,
                        "repeat_experiment",
                        f"Relative confidence half-width {relative_half_width:g} exceeds {resolved_policy.maximum_relative_half_width:g}.",
                    )
                )
        for flag in feature.data_quality_flags:
            normalized = flag.strip().lower()
            if normalized in _REFUSAL_FLAGS:
                issues.append(
                    _issue(
                        "refusal_data_quality_flag",
                        feature_id,
                        "refuse",
                        f"Data-quality flag '{flag}' forbids feature release.",
                    )
                )
            elif normalized in _REPEATABLE_FLAGS:
                issues.append(
                    _issue(
                        "repeatable_data_quality_flag",
                        feature_id,
                        "repeat_experiment",
                        f"Data-quality flag '{flag}' requires another experiment.",
                    )
                )

        if feature.trace_sha256 is not None and _SHA256.fullmatch(feature.trace_sha256) is None:
            issues.append(
                _issue(
                    "invalid_trace_sha256",
                    feature_id,
                    "refuse",
                    "Simulation-derived features require a valid trace SHA-256 digest.",
                )
            )

    if any(issue.severity == "refuse" for issue in issues):
        decision = "refuse"
    elif issues:
        decision = "repeat_experiment"
    else:
        decision = "accept"
    return FeatureQualityDecision(
        decision=decision,
        issues=issues,
        accepted_feature_ids=(
            [feature.feature_id for feature in features]
            if decision == "accept"
            else []
        ),
        policy=resolved_policy,
    )
