import pytest

from cfdc.sim import run_feature_ablation_suite


@pytest.fixture(scope="module")
def ablation_result():
    return run_feature_ablation_suite()


@pytest.mark.parametrize(
    ("case_id", "variant", "expected_success"),
    [
        ("first_order_self_regulating_process", "minimal_core_feature", True),
        ("first_order_self_regulating_process", "wrong_or_noisy_feature", False),
        ("first_order_self_regulating_process", "full_model_reference", True),
        ("double_integrator_low_friction_cart", "minimal_core_feature", True),
        ("double_integrator_low_friction_cart", "wrong_or_noisy_feature", True),
        ("double_integrator_low_friction_cart", "full_model_reference", True),
    ],
)
def test_feature_ablation_trial(case_id, variant, expected_success, ablation_result):
    trial = next(
        trial
        for trial in ablation_result.trials
        if trial.case_id == case_id and trial.variant == variant
    )

    assert trial.success is expected_success
    assert trial.performance.success is expected_success
    assert trial.feature_values
    assert trial.controller.source_features


@pytest.mark.parametrize(
    "case_id",
    [
        "first_order_self_regulating_process",
        "double_integrator_low_friction_cart",
    ],
)
def test_noisy_feature_packet_degrades_against_minimal_packet(case_id, ablation_result):
    rows = {
        trial.variant: trial
        for trial in ablation_result.trials
        if trial.case_id == case_id
    }
    minimal = rows["minimal_core_feature"].performance
    noisy = rows["wrong_or_noisy_feature"].performance

    assert (
        not noisy.success
        or noisy.abs_final_error > minimal.abs_final_error
        or noisy.saturation_fraction > minimal.saturation_fraction
    )
