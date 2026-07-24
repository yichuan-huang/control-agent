import math

import pytest

from cfdc.models import TrialSample
from cfdc.runtime import SafeTrialConfig, SafeTrialRunner


def test_safe_trial_runner_accepts_bounded_first_order_trial():
    def controller(state, reference, gains, time_s):
        del time_s
        return {"input": gains["kp"] * (reference["output"] - state["output"])}

    def plant_step(state, control, dt_s):
        return {
            "output": state["output"] + dt_s * (-state["output"] + control["input"])
        }

    runner = SafeTrialRunner(
        SafeTrialConfig(
            trial_id="first_order_safe_trial",
            dt_s=0.02,
            duration_s=2.0,
            constraints={
                "max_abs_output": 1.5,
                "max_abs_control": 2.0,
                "max_overshoot": 0.4,
            },
        )
    )
    report = runner.run(
        initial_state={"output": 0.0},
        controller=controller,
        plant_step=plant_step,
        gains={"kp": 0.8},
        reference={"output": 1.0},
    )
    assert report.accepted
    assert report.metrics is not None
    assert report.accepted_gains == {"kp": 0.8}


def test_safe_trial_runner_reports_immediate_safety_violation():
    def controller(state, reference, gains, time_s):
        del state, reference, time_s
        return {"input": gains["kp"]}

    def plant_step(state, control, dt_s):
        return {"output": state["output"] + dt_s * control["input"]}

    runner = SafeTrialRunner(
        SafeTrialConfig(
            trial_id="unsafe_control_trial",
            dt_s=0.1,
            duration_s=1.0,
            constraints={"max_abs_control": 1.0},
        )
    )
    report = runner.run(
        initial_state={"output": 0.0},
        controller=controller,
        plant_step=plant_step,
        gains={"kp": 2.0},
        reference={"output": 0.0},
    )
    assert not report.accepted
    assert report.safety_violations[0].constraint == "max_abs_control"


def test_safe_trial_runner_rejects_a_response_that_never_settles():
    def controller(state, reference, gains, time_s):
        del state, reference, gains, time_s
        return {"input": 0.0}

    def plant_step(state, control, dt_s):
        del control, dt_s
        return state

    runner = SafeTrialRunner(
        SafeTrialConfig(
            trial_id="unsettled_trial",
            dt_s=0.1,
            duration_s=0.5,
            constraints={"max_settling_time_s": 0.4},
        )
    )
    report = runner.run(
        initial_state={"output": 0.0},
        controller=controller,
        plant_step=plant_step,
        gains={},
        reference={"output": 1.0},
    )

    assert not report.accepted
    assert report.stop_reason == "max_settling_time_s"
    assert report.metrics is not None
    assert report.metrics.settling_time_s is None


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_runtime_models_reject_non_finite_safety_values(value):
    with pytest.raises(ValueError):
        TrialSample(
            time_s=0.0,
            state={"output": value},
            control={"input": 0.0},
        )
