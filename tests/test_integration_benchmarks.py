from cfdc.diagnosis import DiagnosticEngine
from cfdc.experiments import plan_safe_experiments
from cfdc.sim import (
    CartpoleParams,
    CartpoleSwingupConfig,
    VtolConfig,
    VtolParams,
    list_benchmark_cases,
    run_benchmark_suite,
    run_cartpole_nmp_boundary_scan,
    run_vtol_lqr_baseline,
    run_vtol_simulation,
    run_vtol_variation,
    run_feature_ablation_suite,
    search_cartpole_pd_gains,
    simulate_cartpole_energy_swingup,
)


def test_seven_case_cfdc_closed_loop_benchmark_passes():
    summary = run_benchmark_suite()
    assert summary["case_count"] == 7
    assert summary["success_count"] == 7
    assert summary["execution_count"] == 7
    assert summary["validation_scope"] == "closed_loop_benchmark"
    assert summary["closed_loop_executed"] is True
    assert all(row["features_cover_required"] for row in summary["results"])
    assert all(row["closed_loop_executed"] is True for row in summary["results"])
    assert all(row["performance"]["success"] for row in summary["results"])
    assert {row["execution_backend"] for row in summary["results"]} == {
        "cfdc.sim.generic",
        "cfdc.sim.cartpole",
        "cfdc.sim.vtol",
    }
    by_id = {row["case_id"]: row for row in summary["results"]}
    assert by_id["cartpole_underactuated_sim"]["controller"]["status"] == "ready_for_conservative_trial"
    assert by_id["cartpole_underactuated_sim"]["controller"]["gains"]["kp"] > 0.0
    assert by_id["planar_vtol_hover_lateral_sim"]["controller"]["gains"]["kp_y"] == 0.34


def test_benchmark_experiment_plans_cover_stage_one_required_features():
    engine = DiagnosticEngine()
    for case in list_benchmark_cases():
        diagnosis = engine.diagnose(case.description)
        classification = engine.classify(diagnosis)
        plan = plan_safe_experiments(diagnosis, classification)
        estimates = {feature for instruction in plan.instructions for feature in instruction.estimates}
        assert set(classification.required_core_features).issubset(estimates), case.case_id


def test_feature_ablation_suite_compares_minimal_noisy_and_full_model_packets():
    result = run_feature_ablation_suite()

    assert result.success
    assert result.case_count == 2
    assert result.trial_count == 6
    assert {trial.variant for trial in result.trials} == {
        "minimal_core_feature",
        "wrong_or_noisy_feature",
        "full_model_reference",
    }
    for case_id in {trial.case_id for trial in result.trials}:
        rows = {trial.variant: trial for trial in result.trials if trial.case_id == case_id}
        assert rows["minimal_core_feature"].success
        assert rows["full_model_reference"].success
        assert (
            not rows["wrong_or_noisy_feature"].success
            or rows["wrong_or_noisy_feature"].performance.abs_final_error
            > rows["minimal_core_feature"].performance.abs_final_error
            or rows["wrong_or_noisy_feature"].performance.saturation_fraction
            > rows["minimal_core_feature"].performance.saturation_fraction
        )


def test_cartpole_energy_swingup_reaches_safe_handoff_window():
    result = simulate_cartpole_energy_swingup(include_trajectory=False)
    assert result.success
    assert result.stop_reason == "upright_handoff_window_reached"
    assert result.handoff_time_s is not None
    assert result.max_abs_cart_position_m < 2.4
    assert result.max_abs_force_n <= 10.0
    assert abs(result.final_state.pole_angle_rad) < 0.18
    assert abs(result.final_state.pole_angular_velocity_rad_s) < 1.0
    assert result.performance.capture_success is True
    assert result.performance.actuator_saturation_fractions["force"] == result.metrics["force_saturation_fraction"]
    assert result.metrics["final_error"] == result.performance.final_error
    assert result.metrics["final_output"] == result.performance.final_output


def test_cartpole_force_saturation_participates_in_acceptance():
    result = simulate_cartpole_energy_swingup(
        config=CartpoleSwingupConfig(max_force_saturation_fraction=0.0),
        include_trajectory=False,
    )

    assert result.performance.saturation_fraction > 0.0
    assert not result.success
    assert "force_saturation_fraction" in result.performance.violations


def test_cartpole_nmp_boundary_triggers_and_verifies_rollback():
    natural_frequency = CartpoleParams().free_cart_natural_frequency_down_rad_s
    search, _, _ = search_cartpole_pd_gains(natural_frequency)
    result = run_cartpole_nmp_boundary_scan(
        natural_frequency,
        search.accepted_gains,
        include_trajectory=False,
    )

    assert result.success
    assert result.performance.boundary_triggered is True
    assert result.rejected_outer_gains["kp_y"] > result.accepted_outer_gains["kp_y"]
    assert result.rollback_applied
    assert result.rollback_verified
    assert result.rollback_trial is not None
    assert result.rollback_trial.accepted
    assert any(not trial.accepted for trial in result.candidate_trials)
    assert all(
        result.performance.channels[channel].settled
        for channel in ["cart_position", "pole_angle"]
    )


def test_vtol_position_and_boundary_simulations_run():
    position = run_vtol_simulation(mode="position", include_trajectory=False)
    assert position.success
    assert abs(position.metrics["final_x_error_m"]) < 0.18
    assert position.performance.primary_channel == "lateral_position"
    assert position.metrics["settled"] == position.performance.channels["lateral_position"].settled
    assert position.metrics["settling_time_s"] == position.performance.channels["lateral_position"].settling_time_s
    assert set(position.performance.actuator_saturation_fractions) == {"thrust", "torque"}
    assert position.metrics["torque_saturation_fraction"] == position.performance.actuator_saturation_fractions["torque"]
    assert {feature.feature_id for feature in position.features} >= {
        "hover_thrust",
        "vertical_input_gain",
        "angular_acceleration_gain",
        "lateral_coupling_gain",
    }

    boundary = run_vtol_simulation(mode="boundary", include_trajectory=False)
    assert boundary.success
    assert boundary.metrics["boundary_triggered"] is True
    assert boundary.metrics["boundary_reason"] == "nmp_undershoot"
    assert boundary.metrics["boundary_nmp_undershoot"] >= 0.15
    assert boundary.metrics["nmp_undershoot"] < 0.15
    assert boundary.performance.undershoot == boundary.metrics["nmp_undershoot"]
    assert boundary.events[-1]["event"] == "rollback_validation"
    assert boundary.events[-1]["accepted"] is True
    assert boundary.metrics["nmp_undershoot"] == boundary.events[-1]["nmp_undershoot"]
    assert any(
        event["event"] == "rollback_validation" and event["accepted"] is False
        for event in boundary.events[:-1]
    )
    assert boundary.metrics["tested_candidate_count"] >= 2


def test_vtol_variation_and_full_state_lqr_are_strictly_validated():
    variation = run_vtol_variation(include_trajectory=False)
    baseline = run_vtol_lqr_baseline(include_trajectory=False)

    assert variation.success
    assert len(variation.scenarios) == 6
    assert all(scenario.expectation_met for scenario in variation.scenarios)
    assert baseline.success
    assert all(
        baseline.performance.channels[channel].settled
        for channel in ["lateral_position", "altitude", "attitude"]
    )
    assert baseline.metrics["controller_source"] == "full_model_lqr"


def test_strict_gate_rejects_unsettled_vtol_response():
    result = run_vtol_simulation(
        mode="position",
        config=VtolConfig(duration_s=1.0),
        include_trajectory=False,
    )

    assert not result.success
    assert not result.performance.success
    assert "lateral_position_not_settled" in result.performance.violations


def test_vtol_core_feature_uses_signed_lateral_convention():
    from cfdc.sim import extract_vtol_core_features

    features = {feature.feature_id: feature.value for feature in extract_vtol_core_features()}
    assert features["lateral_coupling_gain"] < 0.0


def test_vtol_altitude_mode_reports_altitude_settling():
    result = run_vtol_simulation(mode="altitude", include_trajectory=False)

    assert result.performance.primary_channel == "altitude"
    assert result.metrics["settled"] == result.performance.channels["altitude"].settled
    assert result.metrics["settling_time_s"] == result.performance.channels["altitude"].settling_time_s


def test_vtol_torque_saturation_and_lateral_boundary_participate_in_acceptance():
    torque_limited = run_vtol_simulation(
        mode="position",
        params=VtolParams(torque_limit_n_m=0.0001),
        include_trajectory=False,
    )
    assert not torque_limited.success
    assert torque_limited.metrics["torque_saturation_fraction"] > 0.10
    assert "torque_saturation_limit" in torque_limited.performance.violations

    position_limited = run_vtol_simulation(
        mode="position",
        config=VtolConfig(max_abs_lateral_position_m=0.5),
        include_trajectory=False,
    )
    assert not position_limited.success
    assert position_limited.metrics["max_abs_lateral_position_m"] > 0.5
    assert "lateral_position_limit" in position_limited.performance.violations
