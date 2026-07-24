from __future__ import annotations

import pytest

from cfdc.lab import (
    ComplexValue,
    PIControllerSpec,
    SessionActionError,
    SimulationRunConfig,
    SimulationTrace,
    StabilityDecision,
    TuningParameterRule,
    TuningProfile,
    approve_llm_proposal,
    build_gain_proposal_context,
    create_stage5_session,
    edit_initial_controller_parameters,
    register_llm_proposal,
    restore_initial_controller,
    run_next_trial,
    export_session,
)
from cfdc.models import TransferFunctionModelSpec
from cfdc.web.linked_tuning_presentation import (
    empty_linked_tuning_view,
    render_linked_tuning,
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


def run_config() -> SimulationRunConfig:
    return SimulationRunConfig(
        reference={"vehicle speed": 0.5},
        horizon_s=30.0,
        sample_time_s=0.05,
        actuator_bounds={"throttle angle": (-3.0, 3.0)},
        output_bounds={"vehicle speed": (-2.0, 2.0)},
    )


def pi_profile() -> TuningProfile:
    return TuningProfile(
        profile_id="stage5-test",
        open_loop_behavior="stable",
        step_fraction=0.05,
        parameters=[
            TuningParameterRule(
                name="kp",
                binding="kp",
                lower_bound=-1.0,
                upper_bound=1.0,
            ),
            TuningParameterRule(
                name="ki",
                binding="ki",
                lower_bound=-1.0,
                upper_bound=1.0,
            ),
        ],
    )


def stage5_session():
    return create_stage5_session(
        source_run_id="run-problem-2",
        source_plant_id="plant-problem-2",
        source_controller_architecture="detuned_PI",
        source_link_sha256="0" * 64,
        model=first_order_model(),
        controller=PIControllerSpec(kp=0.1, ki=0.02),
        tuning_profile=pi_profile(),
        run_config=run_config(),
        model_assumptions=["local deviation-coordinate model"],
    )


def unstable_runner(_model, _controller):
    trace = SimulationTrace(
        time_s=[0.0, 0.1],
        reference={"vehicle speed": [0.5, 0.5]},
        outputs={"vehicle speed": [0.0, 0.1]},
        requested_controls={"throttle angle": [0.05, 0.04]},
        applied_controls={"throttle angle": [0.05, 0.04]},
    )
    decision = StabilityDecision(
        status="unstable",
        analysis_domain="continuous",
        pole_analysis_method="exact_continuous_interconnection",
        poles=[ComplexValue(real=0.2, imaginary=0.0)],
        trajectory_finite=True,
        trajectory_bounded=True,
        tail_error_envelope_contraction=0.0,
        saturation_fraction=0.0,
        evidence=["typed test evidence"],
    )
    return [trace], decision


def inconclusive_runner(_model, _controller):
    traces, _ = unstable_runner(_model, _controller)
    decision = StabilityDecision(
        status="inconclusive",
        analysis_domain="continuous",
        pole_analysis_method="exact_continuous_interconnection",
        poles=[ComplexValue(real=0.0, imaginary=0.0)],
        trajectory_finite=True,
        trajectory_bounded=True,
        tail_error_envelope_contraction=0.0,
        saturation_fraction=0.0,
        evidence=["the trial was finite but did not resolve the stability margin"],
    )
    return traces, decision


def hard_unstable_runner(_model, _controller):
    traces, decision = unstable_runner(_model, _controller)
    return traces, decision.model_copy(
        update={
            "trajectory_bounded": False,
            "hard_failure": True,
            "violations": ["declared state boundary exceeded"],
        }
    )


def test_stage5_session_is_immediately_ready_for_first_trial():
    session = stage5_session()

    assert session.origin == "stage5_candidate_model"
    assert session.evidence_boundary == "stage5_candidate_model"
    assert session.source_run_id == "run-problem-2"
    assert session.source_plant_id == "plant-problem-2"
    assert session.source_controller_architecture == "detuned_PI"
    assert session.model_confirmed is True
    assert session.confirmed_model == first_order_model()
    assert session.state == "trial_pending"


def test_initial_parameter_edit_preserves_stage5_source_snapshot():
    session = stage5_session()

    edited = edit_initial_controller_parameters(
        session,
        {"kp": 0.11, "ki": 0.021},
        expected_revision=session.revision,
    )

    assert edited.initial_controller.kp == pytest.approx(0.1)
    assert edited.initial_controller.ki == pytest.approx(0.02)
    assert edited.current_safe_controller == edited.initial_controller
    assert edited.trial_controller.kp == pytest.approx(0.11)
    assert edited.trial_controller.ki == pytest.approx(0.021)
    assert edited.trial_controller != edited.initial_controller
    assert session.initial_controller.kp == pytest.approx(0.1)


def test_initial_parameter_edit_is_rejected_after_first_trial():
    completed = run_next_trial(
        stage5_session(),
        expected_revision=stage5_session().revision,
        runner=unstable_runner,
    )

    with pytest.raises(SessionActionError, match="before the first trial"):
        edit_initial_controller_parameters(
            completed,
            {"kp": 0.11, "ki": 0.021},
            expected_revision=completed.revision,
        )


def test_restore_initial_controller_discards_later_safe_parameters():
    first = run_next_trial(
        stage5_session(),
        expected_revision=stage5_session().revision,
        runner=unstable_runner,
    )
    proposed = register_llm_proposal(
        first,
        new_parameters={"kp": 0.105, "ki": 0.021},
        rationale="bounded test adjustment",
        expected_revision=first.revision,
    )
    approved = approve_llm_proposal(
        proposed,
        expected_revision=proposed.revision,
    )
    adjusted = run_next_trial(
        approved,
        expected_revision=approved.revision,
        runner=unstable_runner,
    )

    restored = restore_initial_controller(
        adjusted,
        expected_revision=adjusted.revision,
    )

    assert restored.state == "trial_pending"
    assert restored.trial_controller == restored.initial_controller
    assert restored.current_safe_controller == restored.initial_controller
    assert restored.initial_controller.kp == pytest.approx(0.1)
    assert restored.pending_proposal is None


def test_restore_initial_controller_discards_first_round_manual_edit():
    session = stage5_session()
    edited = edit_initial_controller_parameters(
        session,
        {"kp": 0.11, "ki": 0.021},
        expected_revision=session.revision,
    )
    completed = run_next_trial(
        edited,
        expected_revision=edited.revision,
        runner=unstable_runner,
    )

    restored = restore_initial_controller(
        completed,
        expected_revision=completed.revision,
    )

    assert restored.trial_controller == session.initial_controller
    assert restored.current_safe_controller == session.initial_controller
    assert restored.trial_controller.kp == pytest.approx(0.1)
    assert restored.trial_controller.ki == pytest.approx(0.02)


def test_linked_view_exposes_only_the_simple_flow_controls():
    view = render_linked_tuning(stage5_session())

    assert view["architecture"] == "detuned_PI"
    assert view["parameter_rows"] == [["kp", 0.1], ["ki", 0.02]]
    assert "integral_time = 5" in view["derived_parameters"]
    assert view["controls"] == {
        "run_trial": True,
        "request_gain": False,
        "approve_and_run": False,
        "reject_gain": False,
        "restore_initial": False,
    }


def test_stable_view_stops_and_scopes_the_conclusion():
    stable = run_next_trial(
        stage5_session(),
        expected_revision=stage5_session().revision,
    )

    view = render_linked_tuning(stable)

    assert all(not enabled for enabled in view["controls"].values())
    assert "当前软件模型" in view["status"]
    assert view["stability_rows"][0] == ["判定", "stable"]


def test_finite_inconclusive_trial_remains_available_for_llm_adjustment():
    session = stage5_session()
    evaluated = run_next_trial(
        session,
        expected_revision=session.revision,
        runner=inconclusive_runner,
    )

    assert evaluated.state == "needs_adjustment"
    view = render_linked_tuning(evaluated)
    assert view["stability_rows"][0] == ["判定", "inconclusive"]
    assert view["controls"]["request_gain"] is True


def test_simulation_infrastructure_failure_stays_terminal_inconclusive():
    session = stage5_session()

    def failed_runner(_model, _controller):
        raise RuntimeError("simulator unavailable")

    evaluated = run_next_trial(
        session,
        expected_revision=session.revision,
        runner=failed_runner,
    )

    assert evaluated.state == "inconclusive"
    assert render_linked_tuning(evaluated)["controls"]["request_gain"] is False


def test_hard_unstable_trial_rolls_back_then_accepts_bounded_llm_proposal():
    session = stage5_session()
    rolled_back = run_next_trial(
        session,
        expected_revision=session.revision,
        runner=hard_unstable_runner,
    )

    assert rolled_back.state == "rolled_back"
    assert build_gain_proposal_context(
        rolled_back
    ).current_parameters == {"kp": 0.1, "ki": 0.02}
    assert render_linked_tuning(rolled_back)["controls"]["request_gain"] is True

    proposed = register_llm_proposal(
        rolled_back,
        new_parameters={"kp": 0.095, "ki": 0.019},
        rationale="reduce only the whitelisted gains after the rollback",
        expected_revision=rolled_back.revision,
    )

    assert proposed.state == "needs_adjustment"
    assert proposed.pending_proposal.approval_state == "pending"


def test_hard_first_round_manual_edit_rolls_back_to_exportable_stage5_base():
    session = stage5_session()
    edited = edit_initial_controller_parameters(
        session,
        {"kp": 0.11, "ki": 0.021},
        expected_revision=session.revision,
    )
    rolled_back = run_next_trial(
        edited,
        expected_revision=edited.revision,
        runner=hard_unstable_runner,
    )

    assert rolled_back.trial_controller == session.initial_controller
    assert rolled_back.current_safe_controller == session.initial_controller
    proposed = register_llm_proposal(
        rolled_back,
        new_parameters={"kp": 0.095, "ki": 0.019},
        rationale="bounded update from the restored Stage-5 safe base",
        expected_revision=rolled_back.revision,
    )
    approved = approve_llm_proposal(
        proposed,
        expected_revision=proposed.revision,
    )
    completed = run_next_trial(
        approved,
        expected_revision=approved.revision,
        runner=unstable_runner,
    )

    exported = export_session(completed)
    assert '"creation_source": "llm"' in exported


def test_empty_linked_view_has_no_actions_or_session_details():
    view = empty_linked_tuning_view("第五步尚未生成候选。")

    assert view["available"] is False
    assert view["parameter_rows"] == []
    assert view["controls"]["run_trial"] is False
    assert "session_json" not in view
    assert "events" not in view
