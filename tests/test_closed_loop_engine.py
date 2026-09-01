"""Analytical oracles for plant execution, separate from judgment arithmetic."""

import math

import numpy as np
import pytest

from cfdc.sim.execution import LinearPlant


def test_first_order_zoh_step_matches_analytic_solution():
    plant = LinearPlant.from_transfer_matrix(
        [[([2.0], [0.5, 1.0])]], inputs=("u",), outputs=("y",)
    )
    for step in range(1, 11):
        plant.advance({"u": 1.0}, 0.1)
        assert plant.measure()["y"] == pytest.approx(
            2 * (1 - math.exp(-0.2 * step)), abs=1e-12
        )


def test_fractional_input_delay_is_executed_not_rounded_to_a_sample():
    plant = LinearPlant.from_transfer_matrix(
        [[([1.0], [1.0, 0.0])]], inputs=("u",), outputs=("y",), delays={"u": 0.15}
    )
    plant.advance({"u": 2.0}, 0.1)
    assert plant.measure()["y"] == 0
    plant.advance({"u": 2.0}, 0.1)
    assert plant.measure()["y"] == pytest.approx(0.1)
    plant.advance({"u": 2.0}, 0.1)
    assert plant.measure()["y"] == pytest.approx(0.3)


def test_mimo_inputs_use_actual_distinct_branch_dynamics():
    plant = LinearPlant.from_transfer_matrix(
        [
            [([1.0], [1.0, 1.0]), ([2.0], [2.0, 1.0])],
            [([-1.0], [3.0, 1.0]), ([4.0], [4.0, 1.0])],
        ],
        inputs=("a", "b"),
        outputs=("x", "y"),
    )
    plant.advance({"a": 0.0, "b": 1.0}, 1.0)
    assert plant.measure()["x"] == pytest.approx(2 * (1 - np.exp(-0.5)))
    assert plant.measure()["y"] == pytest.approx(4 * (1 - np.exp(-0.25)))


def test_plant_with_algebraic_feedthrough_requires_a_different_execution_contract():
    with pytest.raises(ValueError, match="feedthrough"):
        LinearPlant.from_transfer_matrix(
            [[([1, 1], [1, 2])]], inputs=("u",), outputs=("y",)
        )


def frozen_pi(kp=2.0, ki=1.0):
    from cfdc.kernel.contracts import fingerprint
    from cfdc.kernel.controllers import ControllerIR

    controller = ControllerIR(
        family="PI",
        measured_signals=("y",),
        control_inputs=("u",),
        parameters={"kp": kp, "ki": ki, "reference_filter_rate": 5.0},
        parameter_domains={
            "kp": (-20.0, 20.0),
            "ki": (-20.0, 20.0),
            "reference_filter_rate": (0.01, 20.0),
        },
        output_bounds=(-10.0, 10.0),
        integral_handling="clamped",
    )
    freeze = {
        "freeze_version": "cfdc-freeze/v2.0",
        "session_id": "physical",
        "task_fingerprint": "task",
        "controller": controller.to_dict(),
        "evidence_fingerprints": ["evidence"],
        "runtime_contract": {
            "tracked_signals": ["y"],
            "measured_signals": ["y"],
            "control_inputs": ["u"],
            "input_bounds": {"u": [-10.0, 10.0]},
            "output_bounds": {"y": [-10.0, 10.0]},
            "provider_bindings": {
                "evaluation": {"provider_id": "analytic", "provider_version": "1"}
            },
        },
        "evaluation_contract": {
            "task_type": "local_setpoint_hold",
            "references": {"y": 1.0},
            "sample_time_s": 0.02,
            "horizon_s": 20.0,
            "final_abs_error_max": 0.01,
            "overshoot_max": 0.1,
            "settling_time_max_s": 15.0,
            "hold_duration_min_s": 3.0,
            "trial_manifest": {
                "development": [{"trial_id": "d", "scenario_id": "nominal", "seed": 1}],
                "fresh_confirmation": [
                    {"trial_id": "f", "scenario_id": "nominal", "seed": 2}
                ],
            },
        },
    }
    freeze["freeze_fingerprint"] = fingerprint(freeze)
    return freeze


def test_actual_feedback_parameters_change_the_trajectory():
    from cfdc.kernel.execution_contract import execution_request
    from cfdc.sim.execution import simulate_trial

    results = []
    for kp, ki in [(2.0, 1.0), (0.0, 0.0)]:
        request = execution_request(frozen_pi(kp, ki), "development")
        plant = LinearPlant.from_transfer_matrix(
            [[([1.0], [1.0, 1.0])]], inputs=("u",), outputs=("y",)
        )
        results.append(simulate_trial(request, request["trials"][0], plant))
    assert results[0]["trajectory"]["outputs"]["y"][-1] == pytest.approx(1.0, abs=0.001)
    assert results[1]["trajectory"]["outputs"]["y"][-1] == 0.0
    assert results[0]["stop_event"] == {
        "triggered": False,
        "time_s": 20.0,
        "reason": "horizon_complete",
    }


def test_evaluator_request_does_not_expose_performance_thresholds():
    from cfdc.kernel.contracts import fingerprint
    from cfdc.kernel.execution_contract import execution_request
    from cfdc.sim.execution import simulate_trial

    freeze = frozen_pi()
    request = execution_request(freeze, "development")
    assert "evaluation_contract" not in request
    assert "final_abs_error_max" not in str(request)
    baseline = simulate_trial(
        request,
        request["trials"][0],
        LinearPlant.from_transfer_matrix(
            [[([1.0], [1.0, 1.0])]], inputs=("u",), outputs=("y",)
        ),
    )
    freeze["evaluation_contract"]["final_abs_error_max"] = 900.0
    freeze.pop("freeze_fingerprint")
    freeze["freeze_fingerprint"] = fingerprint(freeze)
    changed = execution_request(freeze, "development")
    trial = simulate_trial(
        changed,
        changed["trials"][0],
        LinearPlant.from_transfer_matrix(
            [[([1.0], [1.0, 1.0])]], inputs=("u",), outputs=("y",)
        ),
    )
    assert trial == baseline


def test_disturbance_is_actually_applied_on_the_declared_input():
    from cfdc.kernel.contracts import fingerprint
    from cfdc.kernel.execution_contract import execution_request
    from cfdc.sim.execution import simulate_trial

    freeze = frozen_pi(0.0, 0.0)
    freeze["evaluation_contract"]["trial_manifest"]["development"][0]["disturbance"] = {
        "time_s": 1.0,
        "duration_s": 0.5,
        "channel": "u",
        "amplitude": 2.0,
    }
    freeze.pop("freeze_fingerprint")
    freeze["freeze_fingerprint"] = fingerprint(freeze)
    request = execution_request(freeze, "development")
    trial = simulate_trial(
        request,
        request["trials"][0],
        LinearPlant.from_transfer_matrix(
            [[([1.0], [1.0, 0.0])]], inputs=("u",), outputs=("y",)
        ),
    )
    assert trial["trajectory"]["outputs"]["y"][-1] == pytest.approx(1.0)
    assert len(trial["events"]) == 1
    assert trial["events"][0]["kind"] == "disturbance"


def evaluate_packet(freeze, trial):
    from cfdc.kernel.contracts import fingerprint
    from cfdc.kernel.judging import judge_packet

    packet = {
        "packet_version": "cfdc-evaluation-packet/v2.0",
        "session_id": freeze["session_id"],
        "task_fingerprint": freeze["task_fingerprint"],
        "freeze_fingerprint": freeze["freeze_fingerprint"],
        "evidence_fingerprints": freeze["evidence_fingerprints"],
        "provider_id": "analytic",
        "provider_version": "1",
        "evaluation_split": "development",
        "trials": [trial],
    }
    packet["packet_fingerprint"] = fingerprint(packet)
    return judge_packet(freeze, packet)


def test_actual_multistage_handoff_is_reconstructed_by_independent_judge():
    from cfdc.kernel.contracts import fingerprint
    from cfdc.kernel.execution_contract import execution_request
    from cfdc.sim.execution import simulate_trial

    freeze = frozen_pi()
    freeze["evaluation_contract"].update(
        task_type="transition_then_hold",
        phases=[
            {
                "phase_id": "approach",
                "references": {"y": 0.5},
                "exit_predicate": {
                    "kind": "within_band",
                    "signal": "y",
                    "target": 0.5,
                    "tolerance": 0.02,
                },
                "dwell_s": 0.5,
                "timeout_s": 15.0,
                "hysteresis": 0.005,
                "state_policy": "inherit",
                "stable_region": {"y": [-0.1, 1.1]},
            },
            {
                "phase_id": "hold",
                "references": {"y": 1.0},
                "exit_predicate": {
                    "kind": "within_band",
                    "signal": "y",
                    "target": 1.0,
                    "tolerance": 0.02,
                },
                "dwell_s": 0.5,
                "timeout_s": 15.0,
                "hysteresis": 0.005,
                "state_policy": "inherit",
                "stable_region": {"y": [-0.1, 1.1]},
            },
        ],
        final_hold_duration_min_s=0.5,
        required_phase_count_min=2,
        verified_handoff_count_min=1,
        goal_region_entry_required=True,
    )
    freeze.pop("freeze_fingerprint")
    freeze["freeze_fingerprint"] = fingerprint(freeze)
    request = execution_request(freeze, "development")
    trial = simulate_trial(
        request,
        request["trials"][0],
        LinearPlant.from_transfer_matrix(
            [[([1.0], [1.0, 1.0])]], inputs=("u",), outputs=("y",)
        ),
    )
    result = evaluate_packet(freeze, trial)
    assert result["status"] == "performance_met", result
    assert result["trials"][0]["metrics"]["verified_handoff_count"] == 1
    assert [event["kind"] for event in trial["events"]] == ["handoff"]
