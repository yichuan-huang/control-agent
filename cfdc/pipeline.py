from __future__ import annotations

from typing import Any

from cfdc.controllers import synthesize_controller
from cfdc.diagnosis import DiagnosticEngine
from cfdc.diagnosis.safety import (
    diagnostic_required_feature_plan,
    validate_diagnostic_controller_release,
)
from cfdc.diagnosis.llm import DiagnosticAdapter
from cfdc.experiments import plan_safe_experiments
from cfdc.features import extract_features_from_results
from cfdc.models import (
    CoreFeatureArtifact,
    ExperimentResult,
    GoNoGoDecision,
    SystemDescription,
)
from cfdc.validation import validate_required_features


def run_cfdc_pipeline(
    description: SystemDescription,
    features: list[CoreFeatureArtifact] | None = None,
    experiment_results: list[ExperimentResult] | None = None,
    safety_limits: dict[str, float] | None = None,
    diagnostic_adapter: DiagnosticAdapter | None = None,
    use_mechanism_cards: bool = False,
) -> dict[str, Any]:
    """Run CFDC stages with optional raw experiment data or pre-extracted features."""

    engine = DiagnosticEngine(
        adapter=diagnostic_adapter,
        use_mechanism_cards=use_mechanism_cards,
    )
    diagnosis = engine.diagnose(description)
    result: dict[str, Any] = {
        "system_description": description.model_dump(),
        "diagnosis": diagnosis.model_dump(),
        "evidence_boundary": "software_pipeline_output_not_physical_validation",
    }
    if not diagnosis.complete:
        diagnostic_gate = validate_diagnostic_controller_release(
            description,
            diagnosis,
            None,
        )
        result["status"] = "need_more_information"
        result["go_no_go"] = diagnostic_gate.model_dump()
        result["provisional_required_features"] = diagnostic_required_feature_plan(
            description,
            diagnosis,
            None,
        )
        return result

    classification = engine.classify(diagnosis, description)
    experiment_plan = plan_safe_experiments(diagnosis, classification)
    result["classification"] = classification.model_dump()
    result["experiment_plan"] = experiment_plan.model_dump()
    diagnostic_gate = validate_diagnostic_controller_release(
        description,
        diagnosis,
        classification,
    )
    result["diagnostic_release_gate"] = diagnostic_gate.model_dump()
    if diagnostic_gate.decision == "no_go":
        result["status"] = "experiments_required"
        result["go_no_go"] = diagnostic_gate.model_dump()
        result["notes"] = [
            "The shared diagnostic safety gate blocked controller release before Stage 3/4.",
        ]
        return result

    resolved_features = features
    if resolved_features is None and experiment_results:
        resolved_features = extract_features_from_results(experiment_results)
        result["experiment_results"] = [experiment_result.model_dump() for experiment_result in experiment_results]

    if resolved_features:
        result["features"] = [feature.model_dump() for feature in resolved_features]
        feature_gate = validate_required_features(classification, resolved_features)
        result["go_no_go"] = feature_gate.model_dump()
        if feature_gate.decision == "no_go":
            result["status"] = "experiments_required"
            result["notes"] = [
                "Stage 3 feature set is incomplete; run the Stage 2 experiments for the missing features before Stage 4.",
            ]
            return result
        controller = synthesize_controller(classification, resolved_features, safety_limits or description.safety_bounds)
        result["controller"] = controller.model_dump()
        if controller.status == "refuse":
            result["status"] = "rejected"
            result["go_no_go"] = GoNoGoDecision(
                decision="no_go",
                reasons=[
                    f"Controller synthesis refused release for architecture '{controller.architecture}'.",
                    *controller.notes,
                ],
            ).model_dump()
            result["notes"] = [
                "Stage 4 returned a refusal candidate and failed closed before controller release."
            ]
            return result
        result["status"] = "controller_candidate_ready"
    else:
        feature_gate = validate_required_features(classification, [])
        result["status"] = "experiments_required"
        result["go_no_go"] = feature_gate.model_dump()
    return result
