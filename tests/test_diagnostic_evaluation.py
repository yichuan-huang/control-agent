import pytest

from cfdc.diagnosis import (
    list_diagnostic_evaluation_cases,
    load_saved_diagnostic_responses,
    run_diagnostic_evaluation,
    snapshot_current_diagnostic_responses,
)


def test_diagnostic_case_catalog_contains_prompt_8_and_complex_4():
    cases = list_diagnostic_evaluation_cases()

    assert len(cases) == 12
    assert sum(case.suite == "prompt_8" for case in cases) == 8
    assert sum(case.suite == "complex_4" for case in cases) == 4
    assert all(len(case.expected_fields) == 8 for case in cases)


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
    assert result.mean_eight_field_accuracy == 0.75
    assert result.mean_required_feature_recall == pytest.approx(5.0 / 9.0)
    assert result.clarification_accuracy == pytest.approx(10.0 / 12.0)
    assert result.controller_gate_accuracy == pytest.approx(9.0 / 12.0)
    assert result.premature_controller_release_count == 3
    assert result.passed_count == 6
    assert all(len(row.field_matches) == 8 for row in result.cases)


def test_diagnostic_scorer_identifies_premature_controller_release_cases():
    result = run_diagnostic_evaluation()
    premature = {
        row.case_id
        for row in result.cases
        if row.premature_controller_release
    }

    assert premature == {
        "first_order_thermal",
        "cstr_operating_point_nonlinearity_diagnosis",
        "quadruple_tank_mimo_nmp_diagnosis",
    }
