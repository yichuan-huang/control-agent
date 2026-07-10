import pytest

from cfdc.diagnosis import (
    DiagnosticEngine,
    diagnostic_case_catalog_sha256,
    list_diagnostic_evaluation_cases,
    load_saved_llm_diagnostic_responses,
    load_saved_diagnostic_responses,
    run_diagnostic_evaluation,
    run_live_llm_diagnostic_comparison,
    score_diagnostic_response_snapshot,
    snapshot_current_diagnostic_responses,
)
from cfdc.diagnosis.evaluation import build_diagnostic_response_snapshot
from cfdc.diagnosis.engine import infer_structural_diagnosis
from cfdc.models import SystemDescription
from cfdc.pipeline import run_cfdc_pipeline


FROZEN_CATALOG_SHA256 = "e33a1cc79d50c4f24f309ad81d290616ce193b0e8b2c421bc3c27aaaf96ce6b9"


def test_diagnostic_case_catalog_contains_prompt_8_and_complex_4():
    cases = list_diagnostic_evaluation_cases()

    assert len(cases) == 12
    assert sum(case.suite == "prompt_8" for case in cases) == 8
    assert sum(case.suite == "complex_4" for case in cases) == 4
    assert all(len(case.expected_fields) == 8 for case in cases)
    assert all(case.constraints_not_core_features for case in cases)
    assert all(case.dangerous_core_features for case in cases)
    assert diagnostic_case_catalog_sha256() == FROZEN_CATALOG_SHA256


def test_saved_diagnostic_responses_match_current_deterministic_snapshot():
    saved = load_saved_diagnostic_responses()
    current = snapshot_current_diagnostic_responses()

    assert saved == current
    assert len(saved) == 12


@pytest.mark.parametrize("use_saved", [True, False])
def test_offline_diagnostic_scorer_reports_each_decision_dimension(use_saved):
    result = run_diagnostic_evaluation(use_saved_responses=use_saved)

    assert result.case_count == 12
    assert result.prompt_case_count == 8
    assert result.complex_case_count == 4
    assert result.case_catalog_sha256 == FROZEN_CATALOG_SHA256
    assert result.mean_eight_field_accuracy == pytest.approx(89.0 / 96.0)
    assert result.mean_required_feature_recall == 1.0
    assert result.mean_required_feature_precision == 1.0
    assert result.core_feature_minimality_accuracy == 1.0
    assert result.constraint_isolation_accuracy == 1.0
    assert result.dangerous_false_positive_control_accuracy == 1.0
    assert result.evidence_discipline_accuracy == 1.0
    assert result.mean_missing_information_quality == 1.0
    assert result.experiment_executability_accuracy == 1.0
    assert result.controller_testability_accuracy == 1.0
    assert result.clarification_accuracy == 1.0
    assert result.archetype_accuracy == 1.0
    assert result.controller_gate_accuracy == 1.0
    assert result.premature_controller_release_count == 0
    assert result.dangerous_false_positive_control_count == 0
    assert result.passed_count == 12
    assert all(len(row.field_matches) == 8 for row in result.cases)


def test_diagnostic_scorer_identifies_premature_controller_release_cases():
    result = run_diagnostic_evaluation()
    premature = {
        row.case_id
        for row in result.cases
        if row.premature_controller_release
    }

    assert premature == set()


def test_archive_audit_dimensions_reject_extra_constraint_and_overclaim():
    responses = snapshot_current_diagnostic_responses()
    target_index = next(
        index
        for index, response in enumerate(responses)
        if response.case_id == "cartpole_underactuated"
    )
    target = responses[target_index]
    evidence = {name: list(items) for name, items in target.field_evidence.items()}
    evidence["open_loop_stability"].append("The controller is physically validated and proven safe.")
    responses[target_index] = target.model_copy(
        update={
            "required_core_features": [
                *target.required_core_features,
                "force_limit",
                "max_force_n",
                "mass",
            ],
            "field_evidence": evidence,
            "experiment_plan_executable": False,
            "experiment_plan_issues": ["instruction_0_missing_stop_conditions"],
            "controller_testable": False,
        }
    )
    snapshot = build_diagnostic_response_snapshot(
        responses,
        response_source="live_llm",
        generator="negative-audit-fixture",
        model="negative-audit-fixture",
    )

    result = score_diagnostic_response_snapshot(snapshot)
    row = next(case for case in result.cases if case.case_id == target.case_id)

    assert row.required_feature_recall == 1.0
    assert row.required_feature_precision < 1.0
    assert not row.core_feature_minimality_correct
    assert row.extra_core_features == ["force_limit", "mass", "max_force_n"]
    assert not row.constraint_isolation_correct
    assert row.constraint_feature_leaks == ["force_limit", "max_force_n"]
    assert not row.dangerous_false_positive_control_correct
    assert row.dangerous_false_positive_features == ["mass"]
    assert not row.evidence_discipline_correct
    assert not row.experiment_executability_correct
    assert not row.controller_testability_correct
    assert not row.passed


def test_missing_information_quality_rejects_jargon_and_incomplete_questions():
    responses = snapshot_current_diagnostic_responses()
    target_index = next(
        index
        for index, response in enumerate(responses)
        if response.case_id == "first_order_thermal"
    )
    target = responses[target_index]
    responses[target_index] = target.model_copy(
        update={
            "clarification_questions": [
                "What is the transfer function relative degree?",
            ],
        }
    )
    snapshot = build_diagnostic_response_snapshot(
        responses,
        response_source="live_llm",
        generator="bad-question-fixture",
        model="bad-question-fixture",
    )

    result = score_diagnostic_response_snapshot(snapshot)
    row = next(case for case in result.cases if case.case_id == target.case_id)

    assert row.missing_information_quality < 0.75
    assert not row.passed


def test_shared_safety_rules_override_unsafe_adapter_delay_release():
    class UnsafeAdapter:
        def diagnose(self, description):
            payload = infer_structural_diagnosis(description).model_dump()
            payload["significant_delay"] = {
                "status": "inferred",
                "value": "no significant delay reported",
                "confidence": 0.8,
                "evidence": ["unsafe adapter assumption"],
            }
            payload["complete"] = True
            payload["clarification_questions"] = []
            return payload

    description = SystemDescription(
        text=(
            "A heater settles after power changes, but the first-motion timing "
            "has not been observed."
        ),
        observed_outputs=["temperature"],
        actuators=["heater power"],
    )
    diagnosis, classification = DiagnosticEngine(adapter=UnsafeAdapter()).run(
        description
    )

    assert not diagnosis.complete
    assert diagnosis.significant_delay.status == "unknown"
    assert classification is None
    assert any("noticeable pause" in question for question in diagnosis.clarification_questions)


@pytest.mark.parametrize(
    ("description", "expected_class", "expected_features"),
    [
        (
            SystemDescription(
                text=(
                    "A stirred reactor is locally self-regulating, but process gain and "
                    "time constant vary strongly with temperature and conversion. Only "
                    "local tests at safe operating points are allowed."
                ),
                observed_outputs=["temperature", "conversion"],
                actuators=["cooling input", "feed input"],
            ),
            "class_iv_higher_order_unstable_nonlinear_or_nmp",
            ["local_static_gain", "local_time_constant", "gain_variation_ratio"],
        ),
        (
            SystemDescription(
                text=(
                    "A process has two pumps and four interconnected tank levels. Both "
                    "controlled lower levels respond to both pumps, and valve distribution "
                    "can cause initial unfavorable motion."
                ),
                observed_outputs=["four tank levels"],
                actuators=["pump 1", "pump 2"],
            ),
            "class_v_multivariable_significant_coupling",
            ["local_gain_matrix", "local_time_constant", "pairing_indicator"],
        ),
    ],
)
def test_pipeline_common_gate_blocks_unsupported_complex_release(
    description,
    expected_class,
    expected_features,
):
    result = run_cfdc_pipeline(description)

    assert result["status"] == "experiments_required"
    assert result["classification"]["primary_class"] == expected_class
    assert result["classification"]["required_core_features"] == expected_features
    assert result["diagnostic_release_gate"]["decision"] == "no_go"
    assert "controller" not in result


def test_live_llm_snapshot_is_saved_and_compared_on_frozen_spec(tmp_path):
    class DeterministicLikeLlmAdapter:
        model = "fake-structured-model"

        def diagnose(self, description):
            return infer_structural_diagnosis(description).model_dump()

    output = tmp_path / "llm-responses.json"
    comparison = run_live_llm_diagnostic_comparison(
        DeterministicLikeLlmAdapter(),
        output_path=output,
    )
    saved = load_saved_llm_diagnostic_responses(output)

    assert output.exists()
    assert saved.response_source == "saved_llm"
    assert saved.model == "fake-structured-model"
    assert saved.case_catalog_sha256 == FROZEN_CATALOG_SHA256
    assert len(saved.responses) == 12
    assert comparison.llm.response_source == "live_llm"
    assert comparison.llm.premature_controller_release_count == 0
    assert "archetype_accuracy" in comparison.metric_deltas_llm_minus_deterministic
    assert all(
        value == pytest.approx(0.0)
        for value in comparison.metric_deltas_llm_minus_deterministic.values()
    )
