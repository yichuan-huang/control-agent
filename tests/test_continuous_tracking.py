import math

import numpy as np

from cfdc.models import (
    ControllerCandidate,
    FLLTrackerState,
    HoverAverageTrackerState,
    ScalarRLSTrackerState,
    TrackingObservation,
    TrackingSchedulerState,
    TrackingStateBundle,
)
from cfdc.online import (
    adapt_controller_from_tracked_feature,
    tracking_scheduler_eligible,
    update_fll_window,
    update_hover_average,
    update_scalar_rls,
)
from cfdc.runtime import run_cfdc_route
from cfdc.sim import run_vtol_variation


def test_tracking_scheduler_pauses_and_resumes_after_duty_interval():
    state = TrackingSchedulerState(duty_interval_s=2.0, tracking_error_threshold=0.1)
    paused, eligible = tracking_scheduler_eligible(
        state,
        TrackingObservation(time_s=0.0, steady_operating_mode=False),
    )
    assert not eligible
    assert paused.pause_reason == "not_steady_operating_mode"

    unsafe, eligible = tracking_scheduler_eligible(
        paused,
        TrackingObservation(
            time_s=1.0,
            steady_operating_mode=True,
            tracking_error=0.01,
            hard_safety_active=True,
        ),
    )
    assert not eligible
    assert unsafe.pause_reason == "hard_safety_active"

    resumed, eligible = tracking_scheduler_eligible(
        unsafe,
        TrackingObservation(
            time_s=2.0,
            steady_operating_mode=True,
            tracking_error=0.01,
        ),
    )
    assert eligible
    assert resumed.last_eligible_time_s == 2.0

    duty_paused, eligible = tracking_scheduler_eligible(
        resumed,
        TrackingObservation(
            time_s=3.0,
            steady_operating_mode=True,
            tracking_error=0.01,
        ),
    )
    assert not eligible
    assert duty_paused.pause_reason == "duty_interval_not_elapsed"


def test_fll_tracks_drifting_sinusoid_and_rejects_weak_lock():
    state = FLLTrackerState(
        angular_frequency_rad_s=4.5,
        bandwidth_rad_s=2.0,
        smoothing_gain=0.5,
        minimum_lock_quality=0.5,
    )
    for index, omega in enumerate(np.linspace(5.0, 5.6, 7)):
        time_s = np.linspace(index * 8.0, (index + 1) * 8.0, 800)
        signal = np.sin(omega * time_s)
        state = update_fll_window(state, time_s.tolist(), signal.tolist())

    assert state.last_update_accepted
    assert abs(state.angular_frequency_rad_s - 5.6) < 0.25
    accepted_frequency = state.angular_frequency_rad_s

    weak = update_fll_window(
        state,
        np.linspace(60.0, 68.0, 800).tolist(),
        np.zeros(800).tolist(),
    )
    assert not weak.last_update_accepted
    assert weak.angular_frequency_rad_s == accepted_frequency


def test_scalar_rls_converges_and_ignores_degenerate_regressor():
    state = ScalarRLSTrackerState(parameter_estimate=0.0, covariance=100.0)
    for regressor in np.linspace(-2.0, 2.0, 100):
        state = update_scalar_rls(state, float(regressor), 3.0 * float(regressor))

    assert abs(state.parameter_estimate - 3.0) < 1e-3
    before = state
    ignored = update_scalar_rls(state, 0.0, 100.0)
    assert ignored.parameter_estimate == before.parameter_estimate
    assert ignored.ignored_sample_count == before.ignored_sample_count + 1


def test_hover_average_uses_ten_second_time_constant():
    state = HoverAverageTrackerState(average_control_effort=10.0)
    for _ in range(30):
        state = update_hover_average(state, measured_control_effort=12.0, dt_s=1.0)

    expected = 12.0 + (10.0 - 12.0) * math.exp(-3.0)
    assert state.time_constant_s == 10.0
    assert math.isclose(state.average_control_effort, expected, rel_tol=1e-6)


def test_controller_updates_above_five_percent_and_requests_nmp_retune_above_ten():
    controller = ControllerCandidate(
        architecture="test",
        gains={"kp_z": 1.0},
        tunable_gain_names=["kp_z"],
        feedforward={"hover_thrust": 10.0},
        status="ready_for_conservative_trial",
    )

    no_change, update, retune = adapt_controller_from_tracked_feature(
        controller,
        "hover_thrust",
        10.0,
        10.4,
    )
    assert not update.controller_update_required
    assert no_change == controller
    assert not retune

    changed, update, retune = adapt_controller_from_tracked_feature(
        controller,
        "hover_thrust",
        10.0,
        11.2,
        smoothing_factor=1.0,
    )
    assert update.controller_update_required
    assert changed.feedforward["hover_thrust"] == 11.2
    assert retune


def test_tracking_state_bundle_json_round_trip():
    bundle = TrackingStateBundle(
        scheduler=TrackingSchedulerState(),
        fll=FLLTrackerState(angular_frequency_rad_s=5.0),
        rls=ScalarRLSTrackerState(parameter_estimate=2.0),
        hover=HoverAverageTrackerState(average_control_effort=10.0),
    )

    assert TrackingStateBundle.model_validate_json(bundle.model_dump_json()) == bundle


def test_orchestrator_accepts_and_returns_persistent_tracking_state():
    state = TrackingStateBundle(
        scheduler=TrackingSchedulerState(duty_interval_s=1.0),
        hover=HoverAverageTrackerState(average_control_effort=10.0),
    )
    observation = TrackingObservation(
        time_s=2.0,
        steady_operating_mode=True,
        tracking_error=0.01,
        feature_id="hover_thrust",
        control_effort=12.0,
        dt_s=10.0,
    )

    report = run_cfdc_route(
        "vtol-hover",
        tracking_state=state,
        tracking_observations=[observation],
        include_trajectory=False,
    )

    assert report.tracking_state is not None
    assert report.tracking_state.hover.update_count == 1
    assert report.tracking_state.nmp_retune_requested
    assert len(report.feature_tracking_updates) == 1
    assert report.feature_tracking_updates[0].controller_update_required


def test_vtol_variation_updated_scenarios_use_hover_and_rls_trackers():
    variation = run_vtol_variation(include_trajectory=False)

    assert variation.success
    for scenario in variation.scenarios:
        if scenario.feature_source == "updated":
            methods = {feature.method for feature in scenario.features}
            assert any("continuous_hover_ema" in method for method in methods)
            assert any("continuous_scalar_rls" in method for method in methods)
