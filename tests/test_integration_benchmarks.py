from cfdc.diagnosis import DiagnosticEngine
from cfdc.experiments import plan_safe_experiments
from cfdc.sim import (
    CartpoleSwingupConfig,
    VtolConfig,
    VtolParams,
    list_benchmark_cases,
    run_benchmark_suite,
    run_vtol_simulation,
    simulate_cartpole_energy_swingup,
)


def test_seven_case_cfdc_feature_chain_benchmark_passes():
    summary = run_benchmark_suite()
    assert summary["case_count"] == 7
    assert summary["success_count"] == 7
    assert summary["validation_scope"] == "feature_chain_smoke"
    assert summary["closed_loop_executed"] is False
    assert all(row["features_cover_required"] for row in summary["results"])
    assert all(row["closed_loop_executed"] is False for row in summary["results"])


def test_benchmark_experiment_plans_cover_stage_one_required_features():
    engine = DiagnosticEngine()
    for case in list_benchmark_cases():
        diagnosis = engine.diagnose(case.description)
        classification = engine.classify(diagnosis)
        plan = plan_safe_experiments(diagnosis, classification)
        estimates = {feature for instruction in plan.instructions for feature in instruction.estimates}
        assert set(classification.required_core_features).issubset(estimates), case.case_id


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
    last_safe_trial = next(
        event
        for event in reversed(boundary.events[:-1])
        if event["event"] == "candidate_trial" and event["accepted"] is True
    )
    assert boundary.metrics["nmp_undershoot"] == last_safe_trial["nmp_undershoot"]
    assert boundary.metrics["tested_candidate_count"] >= 2


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
