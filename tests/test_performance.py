from cfdc.models import OnlineTuningState
from cfdc.online import compute_performance_metrics, refine_gains_once
from cfdc.performance import calculate_channel_performance


def test_channel_performance_reports_archive_style_fields_and_settling():
    metrics = calculate_channel_performance(
        [0.0, 1.0, 2.0, 3.0],
        1.0,
        [0.0, 0.8, 0.99, 1.0],
    )

    assert metrics.final_error == 0.0
    assert metrics.abs_final_error == 0.0
    assert metrics.final_output == 1.0
    assert metrics.overshoot == 0.0
    assert metrics.settled
    assert metrics.settling_time_s == 2.0


def test_channel_performance_uses_null_when_response_never_settles():
    metrics = calculate_channel_performance(
        [0.0, 1.0, 2.0],
        0.1,
        [0.0, 0.08, 0.085],
    )

    assert not metrics.settled
    assert metrics.settling_time_s is None


def test_online_settling_band_uses_actual_step_and_unsettled_is_a_violation():
    metrics = compute_performance_metrics(
        [0.0, 1.0, 2.0],
        [0.1, 0.1, 0.1],
        [0.0, 0.08, 0.085],
        [0.0, 0.0, 0.0],
    )
    assert metrics.settling_time_s is None

    state = OnlineTuningState(gains={"kp": 1.0}, previous_gains={"kp": 0.9})
    updated = refine_gains_once(state, metrics, {"max_settling_time_s": 2.0})
    assert updated.frozen
    assert updated.freeze_reason == "settling_time"
