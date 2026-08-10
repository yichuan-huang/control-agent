from __future__ import annotations

import gradio as gr
import pytest

from cfdc.lab import (
    ComplexValue,
    PIControllerSpec,
    SessionActionError,
    SimulationRunConfig,
    SimulationSession,
    SimulationTrace,
    StabilityDecision,
    TuningParameterRule,
    TuningProfile,
    approve_llm_proposal,
    build_gain_proposal_context,
    create_stage5_session,
    edit_initial_controller_parameters,
    export_session,
    register_llm_proposal,
    restore_initial_controller,
    run_next_trial,
)
from cfdc.models import TransferFunctionModelSpec
from cfdc.web.linked_tuning_presentation import (
    empty_linked_tuning_view,
    output_plot_frame,
    render_linked_tuning,
)
from cfdc.web.linked_tuning_ui import (
    _approve_callback,
    _render_outputs,
    _run_callback,
    build_linked_tuning_panel,
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


def stage5_session(run_configuration: SimulationRunConfig | None = None):
    return create_stage5_session(
        source_run_id="run-problem-2",
        source_plant_id="plant-problem-2",
        source_controller_architecture="detuned_PI",
        source_link_sha256="0" * 64,
        model=first_order_model(),
        controller=PIControllerSpec(kp=0.1, ki=0.02),
        tuning_profile=pi_profile(),
        run_config=run_configuration or run_config(),
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


def stable_runner(_model, _controller):
    traces, decision = unstable_runner(_model, _controller)
    return traces, decision.model_copy(
        update={
            "status": "stable",
            "poles": [ComplexValue(real=-0.2, imaginary=0.0)],
            "tail_error_envelope_contraction": 0.75,
        }
    )


def mimo_runner(_model, _controller):
    trace = SimulationTrace(
        time_s=[0.0, 0.1],
        reference={
            "vehicle speed": [0.5, 0.5],
            "yaw rate": [0.2, 0.2],
        },
        outputs={
            "vehicle speed": [0.0, 0.1],
            "yaw rate": [0.0, 0.05],
        },
        requested_controls={"throttle angle": [0.05, 0.04]},
        applied_controls={"throttle angle": [0.05, 0.04]},
    )
    _, decision = unstable_runner(_model, _controller)
    return [trace], decision


def _series_values(frame, series: str) -> list[float]:
    return frame.loc[frame["series"] == series, "value"].tolist()


def _series_times(frame, series: str) -> list[float]:
    return frame.loc[frame["series"] == series, "time_s"].tolist()


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
        runner=stable_runner,
    )

    view = render_linked_tuning(stable)

    assert all(not enabled for enabled in view["controls"].values())
    assert "当前软件模型" in view["status"]
    assert view["stability_rows"][0] == ["判定", "稳定"]


def test_finite_inconclusive_trial_remains_available_for_llm_adjustment():
    session = stage5_session()
    evaluated = run_next_trial(
        session,
        expected_revision=session.revision,
        runner=inconclusive_runner,
    )

    assert evaluated.state == "needs_adjustment"
    view = render_linked_tuning(evaluated)
    assert view["stability_rows"][0] == ["判定", "证据不足"]
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
    assert build_gain_proposal_context(rolled_back).current_parameters == {
        "kp": 0.1,
        "ki": 0.02,
    }
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


def test_output_plot_overlays_stored_initial_and_latest_siso_trials_with_bounds():
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
    approved = approve_llm_proposal(proposed, expected_revision=proposed.revision)

    def latest_runner(_model, _controller):
        traces, decision = unstable_runner(_model, _controller)
        traces[0] = traces[0].model_copy(
            update={"outputs": {"vehicle speed": [0.0, 0.2]}}
        )
        return traces, decision

    latest = run_next_trial(
        approved,
        expected_revision=approved.revision,
        runner=latest_runner,
    )

    frame = output_plot_frame(latest)

    assert _series_values(
        frame, "scenario-1 · 参考 · vehicle speed"
    ) == [0.5, 0.5]
    assert _series_values(
        frame, "scenario-1 · 初始控制器输出 · vehicle speed"
    ) == [0.0, 0.1]
    assert _series_values(
        frame, "scenario-1 · 最新执行输出 · vehicle speed"
    ) == [0.0, 0.2]
    assert _series_values(
        frame, "scenario-1 · 输出下界 · vehicle speed"
    ) == [-2.0, -2.0]
    assert _series_values(
        frame, "scenario-1 · 输出上界 · vehicle speed"
    ) == [2.0, 2.0]


def test_output_plot_expands_bounds_for_each_mimo_output_channel():
    configuration = SimulationRunConfig(
        reference={"vehicle speed": 0.5, "yaw rate": 0.2},
        horizon_s=30.0,
        sample_time_s=0.05,
        actuator_bounds={"throttle angle": (-3.0, 3.0)},
        output_bounds={
            "vehicle speed": (-2.0, 2.0),
            "yaw rate": (-0.4, 0.6),
        },
    )
    session = stage5_session(configuration)
    evaluated = run_next_trial(
        session,
        expected_revision=session.revision,
        runner=mimo_runner,
    )

    frame = output_plot_frame(evaluated)

    assert _series_values(
        frame, "scenario-1 · 初始控制器输出 · yaw rate"
    ) == [0.0, 0.05]
    assert _series_values(
        frame, "scenario-1 · 输出下界 · yaw rate"
    ) == [-0.4, -0.4]
    assert _series_values(
        frame, "scenario-1 · 输出上界 · yaw rate"
    ) == [0.6, 0.6]
    assert not any("最新执行输出" in series for series in frame["series"])


def test_rolled_back_latest_output_is_explicitly_unaccepted():
    session = stage5_session()
    evaluated = run_next_trial(
        session,
        expected_revision=session.revision,
        runner=hard_unstable_runner,
    )

    view = render_linked_tuning(evaluated)
    series = set(view["output_frame"]["series"])

    assert "scenario-1 · 最新执行输出（未采纳） · vehicle speed" in series
    assert "未采纳" in view["status"]
    assert all("当前安全" not in label for label in series)
    assert dict(view["stability_rows"])["硬边界违规"] == (
        "declared state boundary exceeded"
    )


@pytest.mark.parametrize(
    ("runner", "expected_label"),
    [
        (stable_runner, "稳定"),
        (unstable_runner, "不稳定"),
        (inconclusive_runner, "证据不足"),
    ],
)
def test_stability_presentation_uses_deterministic_chinese_tri_state(
    runner,
    expected_label,
):
    session = stage5_session()
    evaluated = run_next_trial(
        session,
        expected_revision=session.revision,
        runner=runner,
    )

    evidence = dict(render_linked_tuning(evaluated)["stability_rows"])

    assert evidence["判定"] == expected_label
    assert "极点" in evidence
    assert "末段误差收缩" in evidence
    assert "饱和率" in evidence
    assert "硬边界违规" in evidence


def test_stability_evidence_is_placed_above_output_curves():
    with gr.Blocks() as demo:
        build_linked_tuning_panel()

    component_order = {
        component.get("props", {}).get("elem_id"): index
        for index, component in enumerate(demo.get_config_file()["components"])
    }

    assert component_order["linked-stability-summary"] < component_order[
        "linked-output-plot"
    ]


def test_trial_entry_rejects_missing_output_bounds_with_measurement_action():
    partial_configuration = SimulationRunConfig(
        reference={"vehicle speed": 0.5, "yaw rate": 0.2},
        horizon_s=30.0,
        sample_time_s=0.05,
        actuator_bounds={"throttle angle": (-3.0, 3.0)},
        output_bounds={"vehicle speed": (-2.0, 2.0)},
    )
    state = stage5_session(partial_configuration).model_dump(mode="json")

    with pytest.raises(
        gr.Error,
        match=(
            "yaw rate.*请返回测量阶段补充每个输出通道的数值上下限"
        ),
    ):
        _run_callback(
            state,
            [["kp", 0.1], ["ki", 0.02]],
            {},
        )


def test_historical_output_bound_gap_disables_approve_and_run():
    configuration = SimulationRunConfig(
        reference={"vehicle speed": 0.5},
        horizon_s=30.0,
        sample_time_s=0.05,
        actuator_bounds={"throttle angle": (-3.0, 3.0)},
        output_bounds={"vehicle speed": (-2.0, 2.0)},
    )

    def unexpected_channel_runner(_model, _controller):
        trace = SimulationTrace(
            time_s=[0.0, 0.1],
            reference={"vehicle speed": [0.5, 0.5]},
            outputs={
                "vehicle speed": [0.0, 0.1],
                "yaw rate": [0.0, 0.05],
            },
            requested_controls={"throttle angle": [0.05, 0.04]},
            applied_controls={"throttle angle": [0.05, 0.04]},
        )
        _, decision = unstable_runner(_model, _controller)
        return [trace], decision

    session = stage5_session(configuration)
    first = run_next_trial(
        session,
        expected_revision=session.revision,
        runner=unexpected_channel_runner,
    )
    proposed = register_llm_proposal(
        first,
        new_parameters={"kp": 0.105, "ki": 0.021},
        rationale="bounded test adjustment",
        expected_revision=first.revision,
    )
    approved = approve_llm_proposal(proposed, expected_revision=proposed.revision)
    latest = run_next_trial(
        approved,
        expected_revision=approved.revision,
        runner=unstable_runner,
    )
    pending = register_llm_proposal(
        latest,
        new_parameters={"kp": 0.11, "ki": 0.022},
        rationale="another bounded test adjustment",
        expected_revision=latest.revision,
    )

    view = render_linked_tuning(pending)

    assert "yaw rate" in view["status"]
    assert view["controls"]["approve_and_run"] is False
    assert view["controls"]["reject_gain"] is True
    assert _render_outputs(pending.model_dump(mode="json"), view)[16]["visible"] is True


def test_output_bounds_cover_union_of_displayed_first_and_latest_time_axes():
    configuration = SimulationRunConfig(
        reference={"vehicle speed": 0.5},
        horizon_s=30.0,
        sample_time_s=0.05,
        actuator_bounds={"throttle angle": (-3.0, 3.0)},
        output_bounds={
            "vehicle speed": (-2.0, 2.0),
            "yaw rate": (-0.4, 0.6),
        },
    )

    def first_runner(_model, _controller):
        trace = SimulationTrace(
            time_s=[0.0, 0.2],
            reference={"vehicle speed": [0.5, 0.5]},
            outputs={
                "vehicle speed": [0.0, 0.1],
                "yaw rate": [0.0, 0.05],
            },
            requested_controls={"throttle angle": [0.05, 0.04]},
            applied_controls={"throttle angle": [0.05, 0.04]},
        )
        _, decision = unstable_runner(_model, _controller)
        return [trace], decision

    session = stage5_session(configuration)
    first = run_next_trial(
        session,
        expected_revision=session.revision,
        runner=first_runner,
    )
    proposed = register_llm_proposal(
        first,
        new_parameters={"kp": 0.105, "ki": 0.021},
        rationale="bounded test adjustment",
        expected_revision=first.revision,
    )
    approved = approve_llm_proposal(proposed, expected_revision=proposed.revision)
    latest = run_next_trial(
        approved,
        expected_revision=approved.revision,
        runner=unstable_runner,
    )

    frame = output_plot_frame(latest)

    assert _series_times(
        frame, "scenario-1 · 输出下界 · yaw rate"
    ) == [0.0, 0.2]
    assert _series_values(
        frame, "scenario-1 · 输出下界 · yaw rate"
    ) == [-0.4, -0.4]
    assert _series_times(
        frame, "scenario-1 · 输出下界 · vehicle speed"
    ) == [0.0, 0.1, 0.2]
    assert _series_values(
        frame, "scenario-1 · 输出下界 · vehicle speed"
    ) == [-2.0, -2.0, -2.0]


def test_historical_reference_only_bound_gap_blocks_valid_run_and_approval():
    configuration = SimulationRunConfig(
        reference={"vehicle speed": 0.5},
        horizon_s=30.0,
        sample_time_s=0.05,
        actuator_bounds={"throttle angle": (-3.0, 3.0)},
        output_bounds={"vehicle speed": (-2.0, 2.0)},
    )

    def historical_reference_runner(_model, _controller):
        trace = SimulationTrace(
            time_s=[0.0, 0.2],
            reference={
                "vehicle speed": [0.5, 0.5],
                "operator target": [0.1, 0.1],
            },
            outputs={"vehicle speed": [0.0, 0.1]},
            requested_controls={"throttle angle": [0.05, 0.04]},
            applied_controls={"throttle angle": [0.05, 0.04]},
        )
        _, decision = unstable_runner(_model, _controller)
        return [trace], decision

    session = stage5_session(configuration)
    first = run_next_trial(
        session,
        expected_revision=session.revision,
        runner=historical_reference_runner,
    )
    proposed = register_llm_proposal(
        first,
        new_parameters={"kp": 0.105, "ki": 0.021},
        rationale="bounded test adjustment",
        expected_revision=first.revision,
    )
    approved = approve_llm_proposal(proposed, expected_revision=proposed.revision)
    latest = run_next_trial(
        approved,
        expected_revision=approved.revision,
        runner=unstable_runner,
    )
    restored = restore_initial_controller(latest, expected_revision=latest.revision)
    pending = register_llm_proposal(
        latest,
        new_parameters={"kp": 0.11, "ki": 0.022},
        rationale="another bounded test adjustment",
        expected_revision=latest.revision,
    )

    restored = SimulationSession.model_validate(restored.model_dump(mode="json"))
    pending = SimulationSession.model_validate(pending.model_dump(mode="json"))
    restored_view = render_linked_tuning(restored)
    pending_view = render_linked_tuning(pending)

    assert "operator target" in restored_view["status"]
    assert restored_view["controls"]["run_trial"] is False
    assert "operator target" in pending_view["status"]
    assert pending_view["controls"]["approve_and_run"] is False
    with pytest.raises(gr.Error, match="operator target.*请返回测量阶段"):
        _run_callback(
            restored.model_dump(mode="json"),
            [["kp", 0.1], ["ki", 0.02]],
            {},
        )
    with pytest.raises(gr.Error, match="operator target.*请返回测量阶段"):
        _approve_callback(pending.model_dump(mode="json"), {})
