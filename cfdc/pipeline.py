from __future__ import annotations

from typing import Any

from cfdc.controllers import synthesize_controller
from cfdc.diagnosis import DiagnosticEngine
from cfdc.diagnosis.llm import DiagnosticAdapter
from cfdc.experiments import plan_safe_experiments
from cfdc.features import extract_features_from_results
from cfdc.models import CoreFeatureArtifact, ExperimentResult, SystemDescription
from cfdc.validation import validate_required_features


def run_cfdc_pipeline(
    description: SystemDescription,
    features: list[CoreFeatureArtifact] | None = None,
    experiment_results: list[ExperimentResult] | None = None,
    safety_limits: dict[str, float] | None = None,
    diagnostic_adapter: DiagnosticAdapter | None = None,
) -> dict[str, Any]:
    """Run CFDC stages with optional raw experiment data or pre-extracted features."""

    engine = DiagnosticEngine(adapter=diagnostic_adapter)
    diagnosis = engine.diagnose(description)
    result: dict[str, Any] = {
        "system_description": description.model_dump(),
        "diagnosis": diagnosis.model_dump(),
        "evidence_boundary": "software_pipeline_output_not_physical_validation",
    }
    if not diagnosis.complete:
        result["status"] = "need_more_information"
        return result

    classification = engine.classify(diagnosis)
    experiment_plan = plan_safe_experiments(diagnosis, classification)
    result["classification"] = classification.model_dump()
    result["experiment_plan"] = experiment_plan.model_dump()

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
        result["status"] = "controller_candidate_ready"
        controller = synthesize_controller(classification, resolved_features, safety_limits or description.safety_bounds)
        result["controller"] = controller.model_dump()
    else:
        feature_gate = validate_required_features(classification, [])
        result["status"] = "experiments_required"
        result["go_no_go"] = feature_gate.model_dump()
    return result
