from __future__ import annotations

import json
from copy import deepcopy

import pytest

from cfdc.lab import (
    ComplexValue,
    SimulationTrace,
    StabilityDecision,
    extract_tunable_parameters,
    make_llm_call_record,
    register_llm_proposal,
)
from cfdc.lab import (
    run_next_trial as run_simulation_trial,
)
from cfdc.models import CompiledSpecificationModel, TransferFunctionModelSpec
from cfdc.web import linked_tuning_service as service
from cfdc.web.linked_tuning_service import (
    approve_and_run_linked_gain,
    decode_lab_state,
    link_stage5_report,
    run_linked_trial,
)


def first_order_model() -> TransferFunctionModelSpec:
    return TransferFunctionModelSpec(
        numerator=[10.0],
        denominator=[5.0, 1.0],
        input_signal_id="throttle angle",
        output_signal_id="vehicle speed",
        input_units="deg",
        output_units="mph",
    )


def problem2_report() -> dict:
    return {
        "run_id": "run-problem-2",
        "status": "candidate_unvalidated",
        "system_description": {
            "text": "Automobile cruise control around a local operating point.",
            "observed_outputs": ["vehicle speed"],
            "actuators": ["throttle angle"],
            "safety_bounds": {
                "max_abs_reference_normalized": 0.5,
                "max_abs_output_normalized": 2.0,
                "max_abs_actuator_normalized": 1.5,
                "max_test_duration_s": 100.0,
            },
            "forbidden_actions": ["issue commands to physical hardware"],
            "time_scale_hint_s": 10.0,
        },
        "compiled_specification_model": {
            "plant_id": "plant-070ff358c61c92d1",
            "template_id": "first_order_stable",
            "model": first_order_model().model_dump(mode="json"),
            "derived_features": {
                "static_gain": 10.0,
                "time_constant": 5.0,
            },
            "parameter_sources": {
                "static_gain": ["input_change", "steady_output_change"],
                "time_constant": ["response_time_s"],
            },
            "safety_bounds": {
                "input_min": -3.0,
                "input_max": 3.0,
                "output_min": 45.0,
                "output_max": 80.0,
                "input_range": 6.0,
                "state_range": 35.0,
            },
            "time_scale_hint_s": 5.0,
            "assumptions": ["local deviation-coordinate model"],
            "evidence_boundary": "declared_specification_model_only",
        },
        "controller": {
            "plant_id": "plant-070ff358c61c92d1",
            "method_profile_id": "class-i-profile",
            "architecture": "detuned_PI",
            "gains": {
                "kp": 0.000144541,
                "ki": 5.15298e-06,
                "integral_time": 28.05,
            },
            "tunable_gain_names": ["kp", "ki"],
            "saturation": {"input_min": -3.0, "input_max": 3.0},
            "release_level": "candidate_unvalidated",
            "status": "ready_for_conservative_trial",
        },
        "final_gains": {
            "kp": 0.000144541,
            "ki": 5.15298e-06,
            "integral_time": 28.05,
        },
        "evidence_boundary": "software_simulation_only",
    }


def test_complete_stage5_report_uses_compiled_model_without_model_discovery(
    monkeypatch,
):
    def forbidden_adapter(*args, **kwargs):
        del args, kwargs
        raise AssertionError("model discovery must not be called")

    monkeypatch.setattr(
        service,
        "OpenAICompatibleDiagnosticAdapter",
        forbidden_adapter,
    )

    state, view = link_stage5_report(
        problem2_report(),
        base_url="https://provider.example/v1",
        model="unused-model",
        api_key="unused-key",
    )
    session = decode_lab_state(state)

    assert session.origin == "stage5_candidate_model"
    assert session.state == "trial_pending"
    assert session.confirmed_model == first_order_model()
    assert session.trial_controller.kind == "pi"
    assert session.trial_controller.kp == pytest.approx(0.000144541)
    assert session.trial_controller.ki == pytest.approx(5.15298e-06)
    assert view["controls"]["run_trial"] is True
    assert "discovery" not in state


def test_stage5_report_without_compiled_model_is_locked():
    report = problem2_report()
    report["compiled_specification_model"] = None

    state, view = link_stage5_report(report)

    assert state == {}
    assert view["available"] is False
    assert "缺少已编译对象模型" in view["status"]


def test_same_report_keeps_existing_trial_history():
    state, view = link_stage5_report(problem2_report())
    state, _ = run_linked_trial(
        state,
        view["parameter_rows"],
        expected_revision=state["revision"],
    )

    repeated, _ = link_stage5_report(problem2_report(), state)

    assert repeated == state
    assert len(repeated["trials"]) == 1


def test_first_trial_accepts_edited_numeric_strings_from_gradio():
    state, _ = link_stage5_report(problem2_report())

    updated, _ = run_linked_trial(
        state,
        [["kp", "0.00015"], ["ki", "0.000006"]],
        expected_revision=state["revision"],
    )

    controller = updated["trials"][0]["controller"]
    assert controller["kp"] == pytest.approx(0.00015)
    assert controller["ki"] == pytest.approx(0.000006)


@pytest.mark.parametrize("value", ["", "not-a-number", "nan", "inf", "-inf"])
def test_first_trial_rejects_invalid_numeric_strings_from_gradio(value):
    state, view = link_stage5_report(problem2_report())
    rows = deepcopy(view["parameter_rows"])
    rows[0][1] = value

    with pytest.raises(ValueError, match="控制器参数 kp 必须是"):
        run_linked_trial(
            state,
            rows,
            expected_revision=state["revision"],
        )


def test_changed_compiled_model_creates_a_new_linked_session():
    report = problem2_report()
    state, _ = link_stage5_report(report)
    changed = deepcopy(report)
    changed["compiled_specification_model"]["model"]["numerator"] = [12.0]
    changed["compiled_specification_model"]["model_sha256"] = (
        CompiledSpecificationModel.model_validate(
            report["compiled_specification_model"]
        ).model_sha256
    )

    relinked, _ = link_stage5_report(changed, state)

    assert relinked["session_id"] != state["session_id"]
    assert relinked["confirmed_model"]["numerator"] == [12.0]


def _unstable_runner(model, controller):
    del model, controller
    return (
        SimulationTrace(
            time_s=[0.0, 0.1, 0.2],
            reference={"vehicle speed": [0.5, 0.5, 0.5]},
            outputs={"vehicle speed": [0.0, 0.1, 0.2]},
            requested_controls={"throttle angle": [0.1, 0.1, 0.1]},
            applied_controls={"throttle angle": [0.1, 0.1, 0.1]},
        ),
        StabilityDecision(
            status="unstable",
            analysis_domain="continuous",
            pole_analysis_method="exact_continuous_interconnection",
            poles=[ComplexValue(real=0.1, imaginary=0.0)],
            trajectory_finite=True,
            trajectory_bounded=True,
            tail_error_envelope_contraction=0.0,
            saturation_fraction=0.0,
            violations=["positive pole"],
            evidence=["deterministic test runner"],
        ),
    )


def test_unstable_direct_trial_requests_approved_gain_then_runs_next_round(
    monkeypatch,
):
    state, view = link_stage5_report(problem2_report())

    def run_unstable(session, *, expected_revision, result_guard=None):
        del result_guard
        return run_simulation_trial(
            session,
            expected_revision=expected_revision,
            runner=_unstable_runner,
        )

    monkeypatch.setattr(service, "run_next_trial", run_unstable)
    state, view = run_linked_trial(
        state,
        view["parameter_rows"],
        expected_revision=state["revision"],
    )
    assert state["state"] == "needs_adjustment"

    def fake_gain_request(session, adapter, **kwargs):
        assert adapter.base_url == "https://provider.example/v1"
        assert adapter.model == "gain-model"
        assert adapter.api_key == "gain-secret"
        current = extract_tunable_parameters(
            session.trial_controller,
            session.tuning_profile,
        )
        proposed = {name: value * 0.95 for name, value in current.items()}
        record = make_llm_call_record(
            operation="gain_proposal",
            provider="test-provider",
            model="gain-model",
            messages=[{"role": "user", "content": "sanitized"}],
            structured_response={
                "new_parameters": proposed,
                "rationale": "bounded five-percent update",
            },
            validation_status="accepted",
        )
        return (
            register_llm_proposal(
                session,
                new_parameters=proposed,
                rationale="bounded five-percent update",
                llm_call_record=record,
                expected_revision=session.revision,
            ),
            object(),
        )

    monkeypatch.setattr(
        service,
        "request_gain_for_session",
        fake_gain_request,
    )
    proposed, view = service.request_linked_gain(
        state,
        expected_revision=state["revision"],
        base_url="https://provider.example/v1",
        model="gain-model",
        api_key="gain-secret",
    )

    assert proposed["pending_proposal"]["approval_state"] == "pending"
    assert view["controls"]["approve_and_run"] is True
    assert "gain-secret" not in json.dumps(proposed)

    completed, _ = approve_and_run_linked_gain(
        proposed,
        expected_revision=proposed["revision"],
    )
    assert len(completed["trials"]) == 2
    assert completed["trials"][-1]["creation_source"] == "llm"
