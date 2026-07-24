import pytest

from cfdc.diagnosis.engine import DiagnosticEngine, classify_archetype
from cfdc.models import FeatureQualityDecision, FeatureQualityIssue, SystemDescription
from cfdc.runtime import run_cfdc_route
from cfdc.sim import run_profile_experiments


@pytest.mark.parametrize(
    ("description", "profile_id", "expected_class"),
    [
        (
            SystemDescription(
                text="A measured first order heater settles after a small power change.",
                observed_outputs=["temperature"],
                actuators=["heater"],
            ),
            "first_order_lag",
            "class_i_first_order_lag",
        ),
        (
            SystemDescription(
                text="A measured spring vibrates and its free motion decays after release.",
                observed_outputs=["position"],
                actuators=["force"],
            ),
            "second_order_oscillator",
            "class_ii_second_order_oscillator",
        ),
        (
            SystemDescription(
                text="A low-friction cart keeps drifting after a small motor nudge.",
                observed_outputs=["position", "speed"],
                actuators=["force"],
            ),
            "double_integrator",
            "class_iii_double_or_pure_integrator",
        ),
        (
            SystemDescription(
                text="A stable process settles but first moves in the opposite direction after a valve change.",
                observed_outputs=["output"],
                actuators=["valve"],
            ),
            "nmp_inverse_response",
            "class_iv_higher_order_unstable_nonlinear_or_nmp",
        ),
        (
            SystemDescription(
                text="A strongly coupled MIMO process has multiple inputs and multiple outputs.",
                observed_outputs=["y1", "y2"],
                actuators=["u1", "u2"],
            ),
            "mimo_2x2_coupled",
            "class_v_multivariable_significant_coupling",
        ),
    ],
)
def test_class_i_to_v_natural_language_routes_stop_before_numeric_work(
    description, profile_id, expected_class
):
    report = run_cfdc_route("generic", description=description)
    assert report.diagnosis.complete
    assert report.classification.primary_class == expected_class
    assert report.semantic_selection.simulation_profile_id == profile_id
    assert report.status == "awaiting_specifications"
    assert report.experiment_results == []
    assert report.features == []
    assert report.controller is None
    assert report.algorithm1_state is None


@pytest.mark.parametrize(
    ("route_id", "profile_id"),
    [("cartpole", "underactuated_cartpole"), ("vtol-position", "vtol_cascaded")],
)
def test_class_iv_specialized_profiles_share_the_automatic_front_half(
    route_id, profile_id
):
    report = run_cfdc_route(route_id, include_trajectory=False)
    assert report.semantic_selection.simulation_profile_id == profile_id
    assert {record.repeat_index for record in report.experiment_results} == {1, 2, 3}
    assert report.feature_quality_decision.decision == "accept"
    assert report.status == "demo_completed"


def test_classification_ignores_explanatory_value_text():
    description = SystemDescription(
        text="A first order heater settles after a small power change.",
        observed_outputs=["temperature"],
        actuators=["heater"],
    )
    diagnosis = DiagnosticEngine().diagnose(description)
    baseline = classify_archetype(diagnosis)
    poisoned = diagnosis.model_copy(
        update={
            "open_loop_stability": diagnosis.open_loop_stability.model_copy(
                update={"value": "unstable cartpole vtol severe mimo"}
            ),
            "coupling_severity": diagnosis.coupling_severity.model_copy(
                update={"value": "severe mimo underactuated"}
            ),
        }
    )
    assert classify_archetype(poisoned) == baseline


def test_changed_scalar_demo_profile_reports_stale_and_adapted_performance():
    report = run_cfdc_route(
        "generic",
        description=SystemDescription(
            text="A measured first order heater settles after a small power change.",
            observed_outputs=["temperature"],
            actuators=["heater"],
        ),
        execution_mode="demo_fixture",
    )
    assert report.stale_controller_performance is not None
    assert report.adapted_controller_performance is not None
    assert report.adapted_controller_performance.success
    assert report.feature_tracking_updates
    assert any(
        update.relative_change > 0.05 for update in report.feature_tracking_updates
    )


def test_class_v_demo_uses_matrix_feature_and_adapts_after_coupling_drift():
    report = run_cfdc_route(
        "generic",
        description=SystemDescription(
            text="A strongly coupled MIMO process has multiple inputs and multiple outputs.",
            observed_outputs=["y1", "y2"],
            actuators=["u1", "u2"],
        ),
        execution_mode="demo_fixture",
    )
    matrix = next(
        feature
        for feature in report.features
        if feature.feature_id == "local_gain_matrix"
    )
    assert isinstance(matrix.value, list)
    assert report.stale_controller_performance is not None
    assert report.adapted_controller_performance is not None
    assert report.adapted_controller_performance.success
    assert (
        report.adapted_controller_performance.abs_final_error
        <= report.stale_controller_performance.abs_final_error
    )
    assert any(
        update.feature_id == "local_gain_matrix" and update.relative_change > 0.05
        for update in report.feature_tracking_updates
    )


def test_cartpole_reports_safe_frequency_adaptation_after_mass_change():
    report = run_cfdc_route("cartpole", include_trajectory=False)
    assert report.stale_controller_performance is not None
    assert report.adapted_controller_performance is not None
    assert report.adapted_controller_performance.success
    assert (
        report.adapted_controller_performance.abs_final_error
        < report.stale_controller_performance.abs_final_error
    )
    assert any(
        update.feature_id == "natural_frequency" and update.relative_change > 0.05
        for update in report.feature_tracking_updates
    )


def test_low_quality_after_three_repeats_triggers_fourth_experiment(monkeypatch):
    from cfdc.runtime import orchestrator

    decisions = iter(["repeat_experiment", "accept"])

    def quality_gate(classification, features):
        decision = next(decisions)
        return FeatureQualityDecision(
            decision=decision,
            issues=(
                [
                    FeatureQualityIssue(
                        code="low_snr",
                        feature_id="static_gain",
                        severity="repeat_experiment",
                        explanation="Repeat normalized simulation.",
                    )
                ]
                if decision == "repeat_experiment"
                else []
            ),
            accepted_feature_ids=[feature.feature_id for feature in features]
            if decision == "accept"
            else [],
        )

    monkeypatch.setattr(orchestrator, "evaluate_feature_quality", quality_gate)
    report = run_cfdc_route(
        "generic",
        description=SystemDescription(
            text="A measured first order heater settles after a small power change.",
            observed_outputs=["temperature"],
            actuators=["heater"],
        ),
        execution_mode="demo_fixture",
    )
    assert {record.repeat_index for record in report.experiment_results} == {1, 2, 3, 4}
    assert report.feature_quality_decision.decision == "accept"
    assert report.controller is not None


def test_five_low_quality_repeats_fail_without_controller(monkeypatch):
    from cfdc.runtime import orchestrator

    def quality_gate(classification, features):
        del classification, features
        return FeatureQualityDecision(
            decision="repeat_experiment",
            issues=[
                FeatureQualityIssue(
                    code="low_snr",
                    feature_id="static_gain",
                    severity="repeat_experiment",
                    explanation="Repeat normalized simulation.",
                )
            ],
        )

    monkeypatch.setattr(orchestrator, "evaluate_feature_quality", quality_gate)
    report = run_cfdc_route(
        "generic",
        description=SystemDescription(
            text="A measured first order heater settles after a small power change.",
            observed_outputs=["temperature"],
            actuators=["heater"],
        ),
        experiment_runner=run_profile_experiments,
        execution_mode="demo_fixture",
    )
    assert report.status == "feature_extraction_failed"
    assert {record.repeat_index for record in report.experiment_results} == {
        1,
        2,
        3,
        4,
        5,
    }
    assert report.controller is None


def test_numeric_experiment_conflict_blocks_controller_and_requests_route_recompile():
    def conflicting_nmp_experiment(profile, repeat_index):
        records = run_profile_experiments(profile, repeat_index)
        for record in records:
            if "inverse_response_severity" in record.estimates:
                output = record.trace.signals["output"]
                input_signal = record.trace.signals["input"]
                onset = next(
                    index for index, value in enumerate(input_signal) if value > 0.0
                )
                monotone_output = [0.0] * onset + [
                    1.0 - 0.999 ** (index - onset)
                    for index in range(onset, len(output))
                ]
                record = record.model_copy(
                    update={
                        "trace": record.trace.model_copy(
                            update={
                                "signals": {
                                    **record.trace.signals,
                                    "output": monotone_output,
                                }
                            }
                        )
                    }
                )
            yield record

    report = run_cfdc_route(
        "generic",
        description=SystemDescription(
            text="A stable process settles but first moves in the opposite direction after a valve change.",
            observed_outputs=["output"],
            actuators=["valve"],
        ),
        experiment_runner=lambda profile, repeat_index: list(
            conflicting_nmp_experiment(profile, repeat_index)
        ),
        execution_mode="demo_fixture",
    )
    assert report.status == "rejected"
    assert report.controller is None
    assert any("recompile" in reason for reason in report.go_no_go.reasons)
