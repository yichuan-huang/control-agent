from __future__ import annotations

from copy import deepcopy

import numpy as np
import pytest
from pydantic import TypeAdapter, ValidationError

from cfdc.lab import (
    ComplexValue,
    ControllerRuntimeSpec,
    FilteredPDControllerSpec,
    FilteredPIDControllerSpec,
    LagControllerSpec,
    LeadControllerSpec,
    NotchControllerSpec,
    PControllerSpec,
    PIControllerSpec,
    RegisteredControllerSpec,
    SimulationEvent,
    SimulationTrace,
    StateFeedbackControllerSpec,
    StabilityDecision,
)
from cfdc.models import StateSpaceModelSpec, TransferFunctionModelSpec
from cfdc.sim.closed_loop_runtime import run_linear_closed_loop


def _continuous_tf(
    *,
    numerator: list[float] | None = None,
    denominator: list[float] | None = None,
    delay_s: float = 0.0,
) -> TransferFunctionModelSpec:
    return TransferFunctionModelSpec(
        numerator=numerator or [1.0],
        denominator=denominator or [1.0, 1.0],
        input_delay_s=delay_s,
        input_signal_id="u",
        output_signal_id="y",
    )


def _discrete_tf(
    denominator: list[float], *, delay_s: float = 0.0
) -> TransferFunctionModelSpec:
    return TransferFunctionModelSpec(
        numerator=[1.0],
        denominator=denominator,
        time_domain="discrete",
        sample_time_s=0.1,
        input_delay_s=delay_s,
        input_signal_id="u",
        output_signal_id="y",
    )


def _continuous_ss(
    a: list[list[float]],
    *,
    b: list[list[float]] | None = None,
    c: list[list[float]] | None = None,
    d: list[list[float]] | None = None,
    initial_state: list[float] | None = None,
) -> StateSpaceModelSpec:
    n = len(a)
    b_value = b or [[1.0] for _ in range(n)]
    c_value = c or [[1.0] + [0.0] * (n - 1)]
    d_value = d or [[0.0] for _ in range(len(c_value))]
    return StateSpaceModelSpec(
        a=a,
        b=b_value,
        c=c_value,
        d=d_value,
        state_names=[f"x{i + 1}" for i in range(n)],
        input_signal_ids=[f"u{i + 1}" for i in range(len(b_value[0]))],
        output_signal_ids=[f"y{i + 1}" for i in range(len(c_value))],
        initial_state=initial_state or [0.0] * n,
    )


def _discrete_ss(
    a_value: float, *, initial_state: float = 0.25
) -> StateSpaceModelSpec:
    return StateSpaceModelSpec(
        a=[[a_value]],
        b=[[1.0]],
        c=[[1.0]],
        d=[[0.0]],
        time_domain="discrete",
        sample_time_s=0.1,
        state_names=["x"],
        input_signal_ids=["u"],
        output_signal_ids=["y"],
        initial_state=[initial_state],
    )


@pytest.mark.parametrize(
    "controller",
    [
        PControllerSpec(kp=1.0),
        PIControllerSpec(kp=1.0, ki=0.2, integrator_limit=10.0),
        FilteredPDControllerSpec(
            kp=1.0,
            kd=0.1,
            derivative_source="measurement",
            filter_cutoff_rad_s=20.0,
        ),
        FilteredPIDControllerSpec(
            kp=1.0,
            ki=0.2,
            kd=0.1,
            derivative_source="measurement",
            filter_cutoff_rad_s=20.0,
            integrator_limit=10.0,
        ),
        LeadControllerSpec(gain=0.5, zero_rad_s=1.0, pole_rad_s=5.0),
        LagControllerSpec(gain=0.2, zero_rad_s=5.0, pole_rad_s=1.0),
        NotchControllerSpec(
            gain=0.2,
            center_frequency_rad_s=3.0,
            zero_damping_ratio=0.1,
            pole_damping_ratio=0.5,
        ),
        StateFeedbackControllerSpec(
            gain_matrix=[[2.0, 0.0], [0.0, 1.0]],
            reference_gain_matrix=[[1.0, 0.0], [0.0, 1.0]],
            equilibrium_state=[0.0, 0.0],
            equilibrium_input=[0.0, 0.0],
        ),
        RegisteredControllerSpec(controller_id="vtol_cascaded"),
    ],
)
def test_all_controller_contract_variants_round_trip(controller):
    payload = controller.model_dump(mode="json")
    parsed = TypeAdapter(ControllerRuntimeSpec).validate_python(payload)
    assert type(parsed) is type(controller)
    assert parsed.model_dump(mode="json") == payload


def test_controller_contracts_reject_unknown_fields_and_nonfinite_gains():
    with pytest.raises(ValidationError, match="extra_forbidden"):
        PControllerSpec(kp=1.0, python_code="import os")  # type: ignore[call-arg]
    with pytest.raises(ValidationError):
        PControllerSpec(kp=np.inf)


def test_derivative_controller_requires_measurement_source_and_positive_filter():
    with pytest.raises(ValidationError, match="derivative_source"):
        FilteredPDControllerSpec(  # type: ignore[call-arg]
            kp=1.0, kd=0.1, filter_cutoff_rad_s=10.0
        )
    with pytest.raises(ValidationError, match="greater than 0"):
        FilteredPIDControllerSpec(
            kp=1.0,
            ki=0.1,
            kd=0.1,
            derivative_source="measurement",
            filter_cutoff_rad_s=0.0,
        )


@pytest.mark.parametrize(
    "factory",
    [
        lambda: LeadControllerSpec(gain=1.0, zero_rad_s=4.0, pole_rad_s=2.0),
        lambda: LagControllerSpec(gain=1.0, zero_rad_s=1.0, pole_rad_s=2.0),
        lambda: NotchControllerSpec(
            gain=1.0,
            center_frequency_rad_s=2.0,
            zero_damping_ratio=0.8,
            pole_damping_ratio=0.2,
        ),
    ],
)
def test_compensator_contracts_reject_invalid_architecture(factory):
    with pytest.raises(ValidationError, match="architecture"):
        factory()


def test_state_feedback_contract_rejects_incomplete_dimensions():
    with pytest.raises(ValidationError, match="gain_matrix"):
        StateFeedbackControllerSpec(
            gain_matrix=[[1.0, 2.0], [3.0]],
            reference_gain_matrix=[[1.0], [1.0]],
            equilibrium_state=[0.0, 0.0],
            equilibrium_input=[0.0, 0.0],
        )
    with pytest.raises(ValidationError, match="equilibrium"):
        StateFeedbackControllerSpec(
            gain_matrix=[[1.0, 2.0]],
            reference_gain_matrix=[[1.0]],
            equilibrium_state=[0.0],
            equilibrium_input=[0.0],
        )


def test_trace_contract_validates_lengths_finiteness_and_sample_cap():
    base = {
        "time_s": [0.0, 0.1],
        "reference": {"y": [1.0, 1.0]},
        "states": {"x": [0.0, 0.1]},
        "outputs": {"y": [0.0, 0.1]},
        "requested_controls": {"u": [1.0, 0.9]},
        "applied_controls": {"u": [0.5, 0.5]},
        "events": [],
    }
    assert len(SimulationTrace(**base).time_s) == 2

    bad_length = deepcopy(base)
    bad_length["outputs"]["y"] = [0.0]
    with pytest.raises(ValidationError, match="channel lengths"):
        SimulationTrace(**bad_length)

    nonfinite = deepcopy(base)
    nonfinite["states"]["x"][1] = np.nan
    with pytest.raises(ValidationError):
        SimulationTrace(**nonfinite)

    too_long = deepcopy(base)
    size = 20_001
    too_long["time_s"] = [float(i) for i in range(size)]
    for group in (
        "reference",
        "states",
        "outputs",
        "requested_controls",
        "applied_controls",
    ):
        too_long[group] = {
            name: [0.0] * size for name in too_long[group]
        }
    with pytest.raises(ValidationError, match="20,000"):
        SimulationTrace(**too_long)


def test_event_and_stability_contracts_are_strict_and_serializable():
    event = SimulationEvent(
        kind="saturation",
        sample_index=3,
        time_s=0.3,
        message="u reached its upper limit",
        channel="u",
        value=1.5,
        limit=1.0,
    )
    decision = StabilityDecision(
        status="stable",
        analysis_domain="continuous",
        pole_analysis_method="exact_continuous_interconnection",
        poles=[ComplexValue(real=-1.0, imaginary=2.0)],
        spectral_radius=None,
        trajectory_finite=True,
        trajectory_bounded=True,
        tail_error_envelope_contraction=0.2,
        saturation_fraction=0.0,
        violations=[],
        evidence=["all poles lie in the open left half plane"],
    )
    assert event.model_dump(mode="json")["kind"] == "saturation"
    assert decision.model_dump_json()
    with pytest.raises(ValidationError):
        ComplexValue(real=np.nan, imaginary=0.0)


@pytest.mark.parametrize(
    "change,match",
    [
        ({"trajectory_finite": False}, "stable decision"),
        ({"trajectory_bounded": False}, "stable decision"),
        ({"saturation_fraction": 0.11}, "stable decision"),
        ({"violations": ["contradictory"]}, "stable decision"),
        (
            {"pole_analysis_method": "exact_discrete_interconnection"},
            "analysis domain",
        ),
        (
            {"poles": [ComplexValue(real=0.0, imaginary=0.0)]},
            "continuous stable decision",
        ),
    ],
)
def test_stability_decision_rejects_semantically_contradictory_stable_payloads(
    change, match
):
    payload = {
        "status": "stable",
        "analysis_domain": "continuous",
        "pole_analysis_method": "exact_continuous_interconnection",
        "poles": [ComplexValue(real=-1.0, imaginary=0.0)],
        "spectral_radius": None,
        "trajectory_finite": True,
        "trajectory_bounded": True,
        "tail_error_envelope_contraction": 0.0,
        "saturation_fraction": 0.0,
        "violations": [],
        "evidence": ["coherent stable evidence"],
    }
    payload.update(change)
    with pytest.raises(ValidationError, match=match):
        StabilityDecision(**payload)


def test_discrete_stability_decision_requires_spectral_radius_to_match_poles():
    with pytest.raises(ValidationError, match="spectral_radius must match"):
        StabilityDecision(
            status="stable",
            analysis_domain="discrete",
            pole_analysis_method="exact_discrete_interconnection",
            poles=[ComplexValue(real=0.5, imaginary=0.0)],
            spectral_radius=0.4,
            trajectory_finite=True,
            trajectory_bounded=True,
            tail_error_envelope_contraction=0.0,
            saturation_fraction=0.0,
            violations=[],
            evidence=["deliberately contradictory spectral evidence"],
        )


def test_continuous_tf_stable_unstable_and_marginal_decisions():
    stable = run_linear_closed_loop(
        _continuous_tf(),
        PControllerSpec(kp=1.0),
        reference=1.0,
        horizon_s=5.0,
        sample_time_s=0.01,
    )
    unstable = run_linear_closed_loop(
        _continuous_tf(denominator=[1.0, -1.0]),
        PControllerSpec(kp=0.5),
        reference=0.0,
        horizon_s=2.0,
        sample_time_s=0.01,
    )
    marginal = run_linear_closed_loop(
        _continuous_tf(denominator=[1.0, 0.0]),
        PControllerSpec(kp=0.0),
        reference=0.0,
        horizon_s=1.0,
        sample_time_s=0.01,
    )

    assert stable.stability.status == "stable"
    assert stable.stability.analysis_domain == "continuous"
    assert unstable.stability.status == "unstable"
    assert max(p.real for p in unstable.stability.poles) > 0.0
    assert marginal.stability.status == "inconclusive"


def test_continuous_state_space_stable_and_unstable_cases():
    stable = run_linear_closed_loop(
        _continuous_ss([[-1.0]]),
        PControllerSpec(kp=0.2),
        reference=1.0,
        horizon_s=2.0,
        sample_time_s=0.01,
    )
    unstable = run_linear_closed_loop(
        _continuous_ss([[1.0]], initial_state=[0.1]),
        PControllerSpec(kp=0.2),
        reference=0.0,
        horizon_s=2.0,
        sample_time_s=0.01,
    )
    assert stable.stability.status == "stable"
    assert unstable.stability.status == "unstable"


def test_coarse_continuous_rollout_cannot_be_declared_stable_when_sampled_map_diverges():
    plant = _continuous_ss([[-1.0]], initial_state=[1.0])
    p_result = run_linear_closed_loop(
        plant,
        PControllerSpec(kp=2.0),
        reference=0.0,
        horizon_s=40.0,
        sample_time_s=2.0,
    )
    state_feedback_result = run_linear_closed_loop(
        plant,
        StateFeedbackControllerSpec(
            gain_matrix=[[2.0]],
            reference_gain_matrix=[[0.0]],
            equilibrium_state=[0.0],
            equilibrium_input=[0.0],
        ),
        reference=0.0,
        horizon_s=40.0,
        sample_time_s=2.0,
    )
    for result in (p_result, state_feedback_result):
        assert max(p.real for p in result.stability.poles) < -1e-6
        assert result.stability.status == "unstable"
        assert not result.stability.trajectory_bounded
        assert "sampled_rollout_dynamics_unstable" in result.stability.violations


def test_discrete_tf_and_state_space_stable_unstable_boundary_cases():
    stable_tf = run_linear_closed_loop(
        _discrete_tf([1.0, -0.5]),
        PControllerSpec(kp=0.1),
        reference=1.0,
        horizon_s=2.0,
        sample_time_s=0.1,
    )
    unstable_tf = run_linear_closed_loop(
        _discrete_tf([1.0, -1.2]),
        PControllerSpec(kp=0.0),
        reference=0.0,
        horizon_s=1.0,
        sample_time_s=0.1,
    )
    stable_ss = run_linear_closed_loop(
        _discrete_ss(0.8),
        PControllerSpec(kp=0.1),
        reference=0.0,
        horizon_s=1.0,
        sample_time_s=0.1,
    )
    boundary_ss = run_linear_closed_loop(
        _discrete_ss(1.0),
        PControllerSpec(kp=0.0),
        reference=0.0,
        horizon_s=1.0,
        sample_time_s=0.1,
    )
    assert stable_tf.stability.status == "stable"
    assert stable_tf.stability.spectral_radius is not None
    assert unstable_tf.stability.status == "unstable"
    assert stable_ss.stability.status == "stable"
    assert boundary_ss.stability.status == "inconclusive"


def test_discrete_sample_time_mismatch_and_fractional_delay_are_rejected():
    with pytest.raises(ValueError, match="sample time"):
        run_linear_closed_loop(
            _discrete_tf([1.0, -0.5]),
            PControllerSpec(kp=0.1),
            reference=1.0,
            horizon_s=1.0,
            sample_time_s=0.05,
        )
    with pytest.raises(ValueError, match="integral number of samples"):
        run_linear_closed_loop(
            _discrete_tf([1.0, -0.5], delay_s=0.15),
            PControllerSpec(kp=0.1),
            reference=1.0,
            horizon_s=1.0,
            sample_time_s=0.1,
        )


@pytest.mark.parametrize(
    "controller",
    [
        PControllerSpec(kp=0.4),
        PIControllerSpec(kp=0.4, ki=0.1, integrator_limit=10.0),
        FilteredPDControllerSpec(
            kp=0.4,
            kd=0.05,
            derivative_source="measurement",
            filter_cutoff_rad_s=10.0,
        ),
        FilteredPIDControllerSpec(
            kp=0.4,
            ki=0.1,
            kd=0.05,
            derivative_source="measurement",
            filter_cutoff_rad_s=10.0,
            integrator_limit=10.0,
        ),
        LeadControllerSpec(gain=0.2, zero_rad_s=1.0, pole_rad_s=4.0),
        LagControllerSpec(gain=0.2, zero_rad_s=4.0, pole_rad_s=1.0),
        NotchControllerSpec(
            gain=0.2,
            center_frequency_rad_s=3.0,
            zero_damping_ratio=0.1,
            pole_damping_ratio=0.5,
        ),
    ],
)
def test_each_siso_controller_executes_with_named_trace_channels(controller):
    result = run_linear_closed_loop(
        _continuous_tf(),
        controller,
        reference={"y": 1.0},
        actuator_bounds={"u": (-5.0, 5.0)},
        horizon_s=2.0,
        sample_time_s=0.01,
    )
    assert result.trace.reference.keys() == {"y"}
    assert result.trace.outputs.keys() == {"y"}
    assert result.trace.requested_controls.keys() == {"u"}
    assert result.trace.applied_controls.keys() == {"u"}
    assert len(result.trace.time_s) == 201
    assert result.stability.status == "stable"


def test_filtered_derivative_does_not_kick_on_reference_step():
    result = run_linear_closed_loop(
        _continuous_tf(),
        FilteredPDControllerSpec(
            kp=1.0,
            kd=10.0,
            derivative_source="measurement",
            filter_cutoff_rad_s=100.0,
        ),
        reference=1.0,
        horizon_s=0.1,
        sample_time_s=0.01,
    )
    assert result.trace.requested_controls["u"][0] == pytest.approx(1.0)


def test_mimo_state_feedback_executes_and_validates_plant_dimensions():
    plant = _continuous_ss(
        [[1.0, 0.0], [0.0, 0.5]],
        b=[[1.0, 0.0], [0.0, 1.0]],
        c=[[1.0, 0.0], [0.0, 1.0]],
        d=[[0.0, 0.0], [0.0, 0.0]],
        initial_state=[0.1, -0.1],
    )
    controller = StateFeedbackControllerSpec(
        gain_matrix=[[2.0, 0.0], [0.0, 1.0]],
        reference_gain_matrix=[[1.0, 0.0], [0.0, 1.0]],
        equilibrium_state=[0.0, 0.0],
        equilibrium_input=[0.0, 0.0],
    )
    result = run_linear_closed_loop(
        plant,
        controller,
        reference=[0.0, 0.0],
        horizon_s=2.0,
        sample_time_s=0.01,
    )
    assert result.stability.status == "stable"
    assert result.trace.states.keys() == {"x1", "x2"}
    assert result.trace.applied_controls.keys() == {"u1", "u2"}

    with pytest.raises(ValueError, match="state-feedback gain"):
        run_linear_closed_loop(
            plant,
            StateFeedbackControllerSpec(
                gain_matrix=[[1.0]],
                reference_gain_matrix=[[1.0]],
                equilibrium_state=[0.0],
                equilibrium_input=[0.0],
            ),
            reference=[0.0, 0.0],
            horizon_s=1.0,
            sample_time_s=0.01,
        )


def test_continuous_delay_uses_buffer_and_reports_third_order_pade_evidence():
    result = run_linear_closed_loop(
        _continuous_tf(delay_s=0.2),
        PControllerSpec(kp=0.2),
        reference=1.0,
        horizon_s=1.0,
        sample_time_s=0.05,
    )
    early = [
        value
        for time, value in zip(result.trace.time_s, result.trace.outputs["y"])
        if time <= 0.2
    ]
    assert early == pytest.approx([0.0] * len(early), abs=1e-12)
    assert result.stability.pole_analysis_method == "third_order_pade_auxiliary"
    assert any("Padé" in item and "time-domain delay buffer" in item
               for item in result.stability.evidence)


def test_fractional_continuous_delay_is_causal_and_integrated_piecewise():
    static_result = run_linear_closed_loop(
        _continuous_tf(
            numerator=[1.0],
            denominator=[1.0],
            delay_s=0.15,
        ),
        PControllerSpec(kp=0.5),
        reference=1.0,
        horizon_s=0.3,
        sample_time_s=0.1,
    )
    assert static_result.trace.outputs["y"][:2] == pytest.approx([0.0, 0.0])
    assert static_result.trace.outputs["y"][2] == pytest.approx(0.5)

    dynamic_result = run_linear_closed_loop(
        _continuous_tf(delay_s=0.15),
        PControllerSpec(kp=0.5),
        reference=1.0,
        horizon_s=0.3,
        sample_time_s=0.1,
    )
    # u(0)=0.5 reaches the plant at t=.15. Exact ZOH propagation through
    # xdot=-x+u for the remaining .05 seconds gives this state at t=.2.
    expected_state_at_point_two = 0.5 * (1.0 - np.exp(-0.05))
    assert dynamic_result.trace.states["x1"][2] == pytest.approx(
        expected_state_at_point_two, rel=1e-10, abs=1e-12
    )


def test_fractional_delay_sampled_map_cannot_hide_numerically_unbounded_rollout():
    result = run_linear_closed_loop(
        _continuous_tf(delay_s=0.1),
        PControllerSpec(kp=10.0),
        reference=1.0,
        horizon_s=40.0,
        sample_time_s=0.5,
    )
    assert max(abs(value) for value in result.trace.outputs["y"]) > 1e20
    assert result.stability.status == "unstable"
    assert not result.stability.trajectory_bounded
    assert "sampled_rollout_dynamics_unstable" in result.stability.violations
    assert any(
        "sampled rollout-map spectral radius" in item
        and "independent of reference-tracking performance" in item
        for item in result.stability.evidence
    )


def test_multi_sample_fractional_delay_analysis_matches_rollout_queue_order():
    sample_time = 0.2
    gain = 5.0
    result = run_linear_closed_loop(
        _continuous_tf(delay_s=2.5 * sample_time),
        PControllerSpec(kp=gain),
        reference=0.0,
        horizon_s=4.0,
        sample_time_s=sample_time,
    )

    first_a = np.exp(-0.5 * sample_time)
    first_b = 1.0 - first_a
    second_a = np.exp(-0.5 * sample_time)
    second_b = 1.0 - second_a
    augmented_a = np.zeros((4, 4))
    augmented_a[0] = [
        second_a * first_a,
        second_a * first_b,
        second_b,
        0.0,
    ]
    augmented_a[1, 2] = 1.0
    augmented_a[2, 3] = 1.0
    augmented_b = np.asarray([[0.0], [0.0], [0.0], [1.0]])
    augmented_c = np.asarray([[1.0, 0.0, 0.0, 0.0]])
    expected_radius = max(
        abs(
            np.linalg.eigvals(
                augmented_a - augmented_b @ (gain * augmented_c)
            )
        )
    )
    radius_evidence = next(
        item
        for item in result.stability.evidence
        if "actual sampled rollout-map spectral radius" in item
    )
    recorded_radius = float(
        radius_evidence.split("=", maxsplit=1)[1].split(";", maxsplit=1)[0]
    )
    assert recorded_radius == pytest.approx(expected_radius, rel=1e-8)
    assert expected_radius > 1.0
    assert "sampled_rollout_dynamics_unstable" in result.stability.violations


def test_tiny_positive_continuous_delay_uses_zero_prehistory_at_time_zero():
    result = run_linear_closed_loop(
        _continuous_tf(
            numerator=[1.0],
            denominator=[1.0],
            delay_s=1e-14,
        ),
        PControllerSpec(kp=0.5),
        reference=1.0,
        horizon_s=0.02,
        sample_time_s=0.01,
    )
    assert result.trace.outputs["y"][0] == pytest.approx(0.0)
    assert result.trace.outputs["y"][1] == pytest.approx(0.5)


def test_integral_discrete_delay_is_in_rollout_and_pole_analysis():
    result = run_linear_closed_loop(
        _discrete_tf([1.0, -0.5], delay_s=0.2),
        PControllerSpec(kp=0.1),
        reference=1.0,
        horizon_s=2.0,
        sample_time_s=0.1,
    )
    assert result.trace.outputs["y"][:3] == pytest.approx([0.0, 0.0, 0.0])
    assert result.stability.pole_analysis_method == "exact_discrete_delay_augmentation"
    assert len(result.stability.poles) >= 3


def test_saturation_records_requested_applied_and_prevents_stable_when_sustained():
    result = run_linear_closed_loop(
        _continuous_tf(),
        PControllerSpec(kp=10.0),
        reference=10.0,
        actuator_bounds={"u": (-0.1, 0.1)},
        horizon_s=2.0,
        sample_time_s=0.01,
    )
    requested = result.trace.requested_controls["u"]
    applied = result.trace.applied_controls["u"]
    assert requested[0] > applied[0]
    assert max(applied) <= 0.1
    assert sum(event.kind == "saturation" for event in result.trace.events) == 1
    assert result.stability.saturation_fraction > 0.1
    assert result.stability.status == "unstable"
    assert "sustained_actuator_saturation" in result.stability.violations


def test_saturated_direct_feedthrough_keeps_controller_law_self_consistent():
    plant = _continuous_ss(
        [[-1.0]],
        b=[[1.0]],
        c=[[1.0]],
        d=[[1.0]],
    )
    result = run_linear_closed_loop(
        plant,
        PControllerSpec(kp=10.0),
        reference=1.0,
        actuator_bounds={"u1": (-0.1, 0.1)},
        horizon_s=0.1,
        sample_time_s=0.01,
    )
    requested = result.trace.requested_controls["u1"][0]
    applied = result.trace.applied_controls["u1"][0]
    output = result.trace.outputs["y1"][0]
    assert applied == pytest.approx(0.1)
    assert output == pytest.approx(0.1)
    assert requested == pytest.approx(10.0 * (1.0 - output))
    assert requested == pytest.approx(9.0)


def test_ambiguous_saturated_direct_feedthrough_loop_is_rejected():
    plant = _continuous_ss(
        [[-1.0]],
        b=[[1.0]],
        c=[[1.0]],
        d=[[-0.2]],
    )
    with pytest.raises(ValueError, match="multiple self-consistent solution"):
        run_linear_closed_loop(
            plant,
            PControllerSpec(kp=10.0),
            reference=0.0,
            actuator_bounds={"u1": (-0.1, 0.1)},
            horizon_s=0.1,
            sample_time_s=0.01,
        )


def test_conditional_integration_prevents_windup_during_saturation():
    result = run_linear_closed_loop(
        _continuous_tf(),
        PIControllerSpec(kp=1.0, ki=100.0, integrator_limit=1000.0),
        reference=10.0,
        actuator_bounds={"u": (-0.1, 0.1)},
        horizon_s=1.0,
        sample_time_s=0.01,
    )
    # The proportional request falls slightly as y rises. A winding
    # integrator would instead drive this request hundreds of units upward.
    assert max(result.trace.requested_controls["u"]) <= 10.0 + 1e-9


def test_zero_integral_gain_does_not_add_an_irrelevant_marginal_pole():
    result = run_linear_closed_loop(
        _continuous_tf(),
        PIControllerSpec(kp=0.2, ki=0.0),
        reference=1.0,
        horizon_s=1.0,
        sample_time_s=0.01,
    )
    assert result.stability.status == "stable"
    assert all(abs(p.real) > 1e-6 for p in result.stability.poles)


def test_static_transfer_function_has_no_spurious_dynamic_pole():
    result = run_linear_closed_loop(
        _continuous_tf(numerator=[1.0], denominator=[2.0]),
        PControllerSpec(kp=1.0),
        reference=1.0,
        horizon_s=0.1,
        sample_time_s=0.01,
    )
    assert result.stability.status == "stable"
    assert result.stability.poles == []
    assert result.trace.states == {}
    assert result.trace.outputs["y"][0] == pytest.approx(1.0 / 3.0)


def test_state_bound_aborts_early_and_retains_only_finite_samples():
    result = run_linear_closed_loop(
        _continuous_ss([[2.0]], initial_state=[0.5]),
        PControllerSpec(kp=0.0),
        reference=0.0,
        state_bounds={"x1": (-1.0, 1.0)},
        horizon_s=10.0,
        sample_time_s=0.01,
    )
    assert len(result.trace.time_s) < 1001
    assert all(np.isfinite(result.trace.states["x1"]))
    assert result.trace.events[-1].kind == "hard_bound_violation"
    assert result.stability.status == "unstable"
    assert not result.stability.trajectory_bounded


def test_nonfinite_divergence_aborts_without_serializing_nonfinite_values():
    result = run_linear_closed_loop(
        _discrete_ss(1e308, initial_state=2.0),
        PControllerSpec(kp=0.0),
        reference=0.0,
        horizon_s=1.0,
        sample_time_s=0.1,
    )
    assert len(result.trace.time_s) == 1
    assert result.trace.events[-1].kind == "non_finite"
    assert result.trace.events[-1].sample_index == 1
    assert result.trace.events[-1].time_s == pytest.approx(0.1)
    assert result.stability.status == "unstable"
    assert not result.stability.trajectory_finite
    assert np.isfinite(result.trace.states["x"][0])


@pytest.mark.parametrize("duplicate_group", ["state", "input", "output"])
def test_runtime_rejects_duplicate_signal_names_before_trace_dict_creation(
    duplicate_group,
):
    state_names = ["duplicate", "duplicate"] if duplicate_group == "state" else ["x1", "x2"]
    input_names = ["duplicate", "duplicate"] if duplicate_group == "input" else ["u1", "u2"]
    output_names = ["duplicate", "duplicate"] if duplicate_group == "output" else ["y1", "y2"]
    plant = StateSpaceModelSpec(
        a=[[-1.0, 0.0], [0.0, -2.0]],
        b=[[1.0, 0.0], [0.0, 1.0]],
        c=[[1.0, 0.0], [0.0, 1.0]],
        d=[[0.0, 0.0], [0.0, 0.0]],
        state_names=state_names,
        input_signal_ids=input_names,
        output_signal_ids=output_names,
        initial_state=[0.0, 0.0],
    )
    controller = StateFeedbackControllerSpec(
        gain_matrix=[[1.0, 0.0], [0.0, 1.0]],
        reference_gain_matrix=[[1.0, 0.0], [0.0, 1.0]],
        equilibrium_state=[0.0, 0.0],
        equilibrium_input=[0.0, 0.0],
    )
    with pytest.raises(ValueError, match=f"duplicate {duplicate_group}"):
        run_linear_closed_loop(
            plant,
            controller,
            reference=[0.0, 0.0],
            horizon_s=1.0,
            sample_time_s=0.01,
        )


def test_sample_cap_rejects_more_than_20000_requested_samples():
    with pytest.raises(ValueError, match="20,000"):
        run_linear_closed_loop(
            _continuous_tf(),
            PControllerSpec(kp=0.1),
            reference=0.0,
            horizon_s=200.0,
            sample_time_s=0.01,
        )


def test_performance_characteristics_do_not_gate_stability_only_decision():
    result = run_linear_closed_loop(
        _continuous_tf(numerator=[0.01], denominator=[10.0, 1.0]),
        PControllerSpec(kp=0.01),
        reference=100.0,
        horizon_s=0.2,
        sample_time_s=0.01,
    )
    # The response has enormous final error and would fail ordinary tracking
    # performance limits, but this stage intentionally evaluates stability only.
    assert abs(result.trace.reference["y"][-1] - result.trace.outputs["y"][-1]) > 90.0
    assert result.stability.status == "stable"
    assert not any(
        token in " ".join(result.stability.violations).lower()
        for token in ("overshoot", "settling", "iae", "final_error")
    )
