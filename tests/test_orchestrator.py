from cfdc.models import CFDCRunReport, CoreFeatureArtifact, ExperimentPrimitive, SystemDescription
from cfdc.runtime import run_cfdc_route


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
    assert report.trial_reports
    assert all(trial.accepted for trial in report.trial_reports)
    assert {feature.feature_id for feature in report.features} == {"natural_frequency"}
    assert report.classification.required_core_features == ["natural_frequency"]
    assert report.controller.source_features == ["natural_frequency"]
    assert report.final_gains == report.safe_gain_search_state.accepted_gains
    assert report.cartpole_simulation.final_gains == report.final_gains
    assert report.cartpole_simulation.events
    assert report.cartpole_simulation.metrics["upright_dwell_time_s"] >= 0.4
    assert report.go_no_go is not None
    assert report.go_no_go.decision == "go"


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
    assert report.final_gains["kp_z"] == report.trial_reports[-1].accepted_gains["kp_z"]
    assert report.final_gains["kd_z"] == report.trial_reports[-1].accepted_gains["kd_z"]
    for name in ["kp_theta", "kd_theta", "kp_y", "kd_y"]:
        assert report.final_gains[name] == report.controller.gains[name]


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
    assert report.final_gains["kp_y"] == report.vtol_simulation.metrics["accepted_lateral_kp"]
    assert report.final_gains["kd_y"] == report.vtol_simulation.metrics["accepted_lateral_kd"]
    assert report.vtol_simulation.metrics["controller_source"] == "cfdc_orchestrator"


def test_cfdc_run_report_json_round_trip():
    report = run_cfdc_route("cartpole", include_trajectory=False, run_id="round-trip-test")
    restored = CFDCRunReport.model_validate_json(report.model_dump_json())
    assert restored == report


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
        features=[feature("static_gain", 2.0), feature("time_constant", 5.0)],
        run_id="route-mismatch-test",
    )

    assert report.status == "rejected"
    assert report.go_no_go is not None
    assert report.go_no_go.decision == "no_go"
    assert report.go_no_go.route_compatible is False
    assert report.controller is None
    assert report.cartpole_simulation is None


def test_route_missing_required_features_returns_structured_no_go():
    report = run_cfdc_route(
        "generic",
        description=SystemDescription(
            text="A first order temperature process settles after a small heater change.",
            observed_outputs=["temperature"],
            actuators=["heater"],
        ),
        features=[feature("static_gain", 2.0)],
        run_id="missing-feature-test",
    )

    assert report.status == "experiments_required"
    assert report.go_no_go is not None
    assert report.go_no_go.decision == "no_go"
    assert report.go_no_go.missing_features == ["time_constant"]
    assert report.controller is None
