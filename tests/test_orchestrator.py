from cfdc.models import CFDCRunReport, CoreFeatureArtifact, ExperimentPrimitive, SystemDescription
from cfdc.runtime import run_cfdc_route
from main import compact_route_report


def feature(fid, value):
    width = max(abs(value) * 0.05, 1e-6)
    return CoreFeatureArtifact(
        feature_id=fid,
        value=value,
        lower_bound=value - width,
        upper_bound=value + width,
        confidence=0.85,
        units="unit",
        method="test",
        source_experiment=ExperimentPrimitive.PULSE,
    )


def test_cartpole_route_runs_complete_cfdc_report():
    report = run_cfdc_route("cartpole", include_trajectory=False, run_id="cartpole-test")

    assert report.status == "completed"
    assert report.route_id == "cartpole"
    assert report.diagnosis is not None
    assert report.classification is not None
    assert report.experiment_plan is not None
    assert report.controller is not None
    assert report.safe_gain_search_state is not None
    assert report.cartpole_simulation is not None
    assert report.cartpole_simulation.success
    assert report.cartpole_boundary is not None
    assert report.cartpole_boundary.success
    assert report.cartpole_boundary.rollback_applied
    assert report.cartpole_boundary.rollback_verified
    assert report.cartpole_boundary.rollback_trial is not None
    assert report.cartpole_boundary.rollback_trial.accepted
    assert report.cartpole_boundary.rejected_outer_gains
    assert any(not trial.accepted for trial in report.cartpole_boundary.candidate_trials)
    assert report.baseline_comparison is not None
    assert report.baseline_comparison.cfdc_performance.success
    assert report.baseline_comparison.baseline_performance.success
    assert report.baseline_comparison.same_plant
    assert report.baseline_comparison.same_initial_state
    assert report.baseline_comparison.same_reference
    assert report.baseline_comparison.same_horizon
    assert report.baseline_comparison.same_limits
    assert report.baseline_comparison.matched_conditions["horizon_s"] == 20.0
    assert report.trial_reports
    assert all(trial.accepted for trial in report.trial_reports)
    assert {feature.feature_id for feature in report.features} == {"natural_frequency"}
    assert report.classification.required_core_features == ["natural_frequency"]
    assert report.controller.source_features == ["natural_frequency"]
    assert all(
        report.final_gains[name] == value
        for name, value in report.safe_gain_search_state.accepted_gains.items()
    )
    assert report.final_gains["kp_y"] == report.cartpole_boundary.accepted_outer_gains["kp_y"]
    assert report.final_gains["kd_y"] == report.cartpole_boundary.accepted_outer_gains["kd_y"]
    assert report.cartpole_simulation.final_gains == report.final_gains
    assert report.cartpole_simulation.events
    assert report.cartpole_simulation.metrics["upright_dwell_time_s"] >= 0.4
    assert report.go_no_go is not None
    assert report.go_no_go.decision == "go"
    assert all(
        report.cartpole_simulation.performance.channels[channel].settled
        for channel in ["cart_position", "pole_angle"]
    )


def test_cartpole_final_simulation_uses_cfdc_online_gains():
    report = run_cfdc_route("cartpole", include_trajectory=True, run_id="cartpole-controller-source-test")

    assert report.cartpole_simulation is not None
    phases = {row["phase"] for row in report.cartpole_simulation.trajectory}
    assert "balance_cfdc_pd" in phases
    assert "balance_lqr" not in phases


def test_vtol_position_route_runs_validated_gain_update_and_simulation():
    report = run_cfdc_route("vtol-position", include_trajectory=False, run_id="vtol-position-test")

    assert report.status == "completed"
    assert report.route_id == "vtol-position"
    assert report.diagnosis is not None
    assert report.classification is not None
    assert report.experiment_plan is not None
    assert report.controller is not None
    assert report.online_tuning_state is not None
    assert report.vtol_simulation is not None
    assert report.vtol_simulation.success
    assert len(report.trial_reports) == 2
    assert all(trial.accepted for trial in report.trial_reports)
    assert report.vtol_simulation.metrics["controller_source"] == "cfdc_orchestrator"
    assert report.vtol_simulation.metrics["hover_feedforward_n"] == report.final_feedforward["hover_thrust"]
    assert {feature.feature_id for feature in report.features} >= {
        "hover_thrust",
        "angular_acceleration_gain",
        "lateral_coupling_gain",
    }
    assert not report.feature_tracking_updates
    assert report.final_feedforward == report.controller.feedforward
    assert "lateral_coupling_gain" not in report.controller.gains
    assert any(
        event.get("action") == "coupled_operational_candidate"
        for event in report.online_tuning_state.history
    )
    assert report.online_tuning_state.gains == report.final_gains
    assert all(
        report.vtol_simulation.performance.channels[channel].settled
        for channel in ["lateral_position", "altitude", "attitude"]
    )
    assert not report.vtol_simulation.performance.violations
    assert report.baseline_comparison is not None
    assert report.baseline_comparison.cfdc_performance == report.vtol_simulation.performance
    assert report.baseline_comparison.baseline_performance.success
    assert report.baseline_comparison.same_plant
    assert report.baseline_comparison.same_initial_state
    assert report.baseline_comparison.same_reference
    assert report.baseline_comparison.same_horizon
    assert report.baseline_comparison.same_limits
    assert report.baseline_comparison.matched_conditions["horizon_s"] == 15.0


def test_vtol_boundary_route_records_boundary_result():
    report = run_cfdc_route("vtol-boundary", include_trajectory=False, run_id="vtol-boundary-test")

    assert report.status == "completed"
    assert report.vtol_simulation is not None
    assert report.vtol_simulation.stop_reason == "boundary_triggered"
    assert report.vtol_simulation.metrics["boundary_triggered"] is True
    assert report.vtol_simulation.metrics["boundary_reason"] == "nmp_undershoot"
    assert report.vtol_simulation.metrics["boundary_nmp_undershoot"] >= 0.15
    assert report.vtol_simulation.metrics["nmp_undershoot"] < 0.15
    assert report.vtol_simulation.metrics["rollback_applied"] is True
    assert report.vtol_simulation.performance.success
    assert report.vtol_simulation.performance.boundary_reason == "nmp_undershoot"
    assert all(
        report.vtol_simulation.performance.channels[channel].settled
        for channel in ["lateral_position", "altitude", "attitude"]
    )
    assert not report.vtol_simulation.performance.violations
    assert report.final_gains["kp_y"] == report.vtol_simulation.metrics["accepted_lateral_kp"]
    assert report.final_gains["kd_y"] == report.vtol_simulation.metrics["accepted_lateral_kd"]
    assert report.vtol_simulation.metrics["controller_source"] == "cfdc_orchestrator"
    assert any(
        event.get("action") == "boundary_rollback_validated"
        for event in report.online_tuning_state.history
    )


def test_vtol_variation_route_records_six_stale_updated_scenarios():
    report = run_cfdc_route("vtol-variation", include_trajectory=False, run_id="vtol-variation-test")

    assert report.status == "completed"
    assert report.vtol_variation is not None
    assert report.vtol_variation.success
    assert len(report.vtol_variation.scenarios) == 6
    assert report.vtol_variation.updated_scenario_count == 4
    assert report.vtol_variation.stale_scenario_count == 2
    assert all(scenario.expectation_met for scenario in report.vtol_variation.scenarios)
    scenarios = {scenario.scenario_id: scenario for scenario in report.vtol_variation.scenarios}
    assert not scenarios["mass_plus_25_percent_stale_features"].simulation.success
    assert report.stale_controller_performance == scenarios["mass_plus_25_percent_stale_features"].simulation.performance
    assert report.adapted_controller_performance == scenarios["mass_plus_25_percent_updated_features"].simulation.performance
    assert not report.stale_controller_performance.success
    assert report.adapted_controller_performance.success
    for scenario in report.vtol_variation.scenarios:
        if scenario.feature_source == "updated":
            assert scenario.simulation.success
            assert all(
                scenario.simulation.performance.channels[channel].settled
                for channel in ["lateral_position", "altitude", "attitude"]
            )


def test_cfdc_run_report_json_round_trip():
    report = run_cfdc_route("cartpole", include_trajectory=False, run_id="round-trip-test")
    restored = CFDCRunReport.model_validate_json(report.model_dump_json())
    assert restored == report
    assert restored.cartpole_boundary is not None
    assert restored.baseline_comparison is not None


def test_compact_report_removes_nested_cartpole_trial_samples():
    report = run_cfdc_route("cartpole", include_trajectory=False, run_id="compact-report-test")
    payload = compact_route_report(report)
    boundary = payload["cartpole_boundary"]

    assert boundary is not None
    nested_trials = [*boundary["candidate_trials"], boundary["rollback_trial"]]
    assert all("samples" not in trial for trial in nested_trials)
    assert all(trial["sample_count"] > 0 for trial in nested_trials)
    assert "history" not in payload["safe_gain_search_state"]
    assert payload["safe_gain_search_state"]["history_count"] > 0
    assert "events" not in payload["cartpole_simulation"]
    assert payload["cartpole_simulation"]["event_count"] > 0


def test_orchestrator_stops_for_incomplete_description():
    report = run_cfdc_route(
        "generic",
        description=SystemDescription(text="I have a machine and want it to behave better."),
        run_id="clarify-test",
    )
    assert report.status == "need_more_information"
    assert report.diagnosis is not None
    assert 2 <= len(report.diagnosis.clarification_questions) <= 4
    assert report.classification is None


def test_route_class_mismatch_returns_structured_no_go():
    report = run_cfdc_route(
        "cartpole",
        description=SystemDescription(
            text="A first order temperature process settles after a small heater change.",
            observed_outputs=["temperature"],
            actuators=["heater"],
        ),
        run_id="route-mismatch-test",
    )

    assert report.status == "rejected"
    assert report.go_no_go is not None
    assert report.go_no_go.decision == "no_go"
    assert report.go_no_go.route_compatible is False
    assert report.controller is None
    assert report.cartpole_simulation is None


def test_generic_route_automatically_extracts_required_features():
    report = run_cfdc_route(
        "generic",
        description=SystemDescription(
            text="A first order temperature process settles after a small heater change.",
            observed_outputs=["temperature"],
            actuators=["heater"],
        ),
        run_id="missing-feature-test",
    )

    assert report.status == "completed"
    assert report.go_no_go is not None
    assert report.go_no_go.decision == "go"
    assert {feature.feature_id for feature in report.features} == {"static_gain", "time_constant"}
    assert report.controller is not None


def test_route_api_does_not_accept_user_feature_packets():
    import pytest
    with pytest.raises(TypeError, match="features"):
        run_cfdc_route("generic", features=[feature("static_gain", 2.0)])
