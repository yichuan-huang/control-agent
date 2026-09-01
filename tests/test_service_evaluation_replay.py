from dataclasses import replace

import pytest

from cfdc.kernel.contracts import ControllerFreeze
from cfdc.kernel.providers import CallableEvaluationProvider, EvaluationProviderRegistry
from cfdc.kernel.service import WorkflowService


def prepared_service(tmp_path, callback):
    service = WorkflowService(tmp_path)
    session = service.start(
        {
            "description": "Hold a scalar output at one.",
            "task_type": "local_setpoint_hold",
            "measured_signals": ["y"],
            "control_input": "u",
            "input_min": -2,
            "input_max": 2,
            "state_stop": 5,
            "reference": 1,
            "budget_confirmed": True,
        }
    )
    binding = {
        "provider_id": "isolated",
        "provider_version": "1",
        "capabilities": ["software_evaluation"],
        "binding_role": "evaluation",
        "execution_kind": "software",
    }
    freeze = ControllerFreeze(
        session_id=session.session_id,
        task_fingerprint=session.task.fingerprint,
        controller={"family": "PI"},
        evidence_fingerprints=("evidence",),
        runtime_contract={
            "tracked_signals": ["y"],
            "measured_signals": ["y"],
            "control_inputs": ["u"],
            "input_bounds": {"u": [-2, 2]},
            "output_bounds": {"y": [-5, 5]},
            "provider_bindings": {"evaluation": binding},
        },
        evaluation_contract={
            "task_type": "local_setpoint_hold",
            "references": {"y": 1.0},
            "sample_time_s": 1.0,
            "horizon_s": 3.0,
            "final_abs_error_max": 0.1,
            "overshoot_max": 0.1,
            "settling_time_max_s": 2.0,
            "hold_duration_min_s": 1.0,
            "trial_manifest": {
                "development": [
                    {"trial_id": "d0", "scenario_id": "nominal", "seed": 1}
                ],
                "fresh_confirmation": [
                    {"trial_id": "f0", "scenario_id": "nominal", "seed": 2}
                ],
            },
        },
        source_version="test",
    ).to_dict()
    session = service._save(
        service._append(
            replace(
                session,
                status="controller_ready",
                controller_freeze=freeze,
                provider_bindings={"evaluation": binding},
            ),
            "test_controller_prepared",
            "prepare",
            {},
        )
    )
    registry = EvaluationProviderRegistry()
    registry.register(CallableEvaluationProvider("isolated", "1", callback))
    return service, session, registry


def successful_packet(request):
    assert "evaluation_contract" not in request
    assert "final_abs_error_max" not in str(request)
    scenario = request["trials"][0]
    return {
        "evaluation_split": request["evaluation_split"],
        "trials": [
            {
                **scenario,
                "trajectory": {
                    "time_s": [0, 1, 2, 3],
                    "outputs": {"y": [0, 0.5, 1, 1]},
                    "measurements": {"y": [0, 0.5, 1, 1]},
                    "references": {"y": [1, 1, 1, 1]},
                    "control_inputs": {"u": [2, 1, 0, 0]},
                    "raw_control_inputs": {"u": [3, 1, 0, 0]},
                    "controller_states": [{"integral": 0}] * 4,
                    "phase_ids": ["hold"] * 4,
                },
                "stop_event": {
                    "triggered": False,
                    "time_s": 3.0,
                    "reason": "horizon_complete",
                },
                "events": [],
            }
        ],
        "private_truth_returned": False,
    }


def test_service_only_publishes_result_after_exact_packet_replay(tmp_path):
    service, session, registry = prepared_service(tmp_path, successful_packet)
    recorded = service.run_evaluation(
        session.session_id,
        action_id="evaluate",
        revision=session.revision,
        provider_registry=registry,
        repeats=1,
    )
    assert recorded.status == "evaluation_recorded_pending_replay"
    assert recorded.evaluation["status"] == "performance_met"
    assert recorded.pending_actions[0]["action"] == "replay_evaluation"

    replayed = service.replay_evaluation(
        session.session_id,
        action_id="replay",
        revision=recorded.revision,
    )
    assert replayed.status == "performance_met"
    assert replayed.evaluation_replays[-1]["matches_previous"] is True


def test_summary_only_provider_cannot_change_service_state(tmp_path):
    def summary_only(request):
        scenario = request["trials"][0]
        return {
            "evaluation_split": request["evaluation_split"],
            "trials": [{**scenario, "stable": True, "performance_pass": True}],
            "private_truth_returned": False,
        }

    service, session, registry = prepared_service(tmp_path, summary_only)
    with pytest.raises(ValueError, match="trajectory"):
        service.run_evaluation(
            session.session_id,
            action_id="evaluate",
            revision=session.revision,
            provider_registry=registry,
            repeats=1,
        )
    assert service.read(session.session_id).status == "controller_ready"
