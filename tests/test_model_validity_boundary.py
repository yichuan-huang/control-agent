from __future__ import annotations

import pytest

from cfdc.lab import (
    ComplexValue,
    ProposalValidationError,
    SimulationTrace,
    StabilityDecision,
    ValidityRegion,
    build_gain_proposal_context,
    local_validity_guard,
    run_next_trial,
)
from tests.simulation_fixtures import continuous_siso_session


def local_region() -> ValidityRegion:
    return ValidityRegion(
        description="The local heater model is valid near zero deviation.",
        output_ranges={"y": (-0.2, 0.2)},
        signal_units={"y": "m"},
        constant_conditions=["The operating configuration remains unchanged."],
        out_of_range_effect=(
            "Outside this range the local linear model is no longer evidence "
            "about the controller."
        ),
    )


def trace_that_leaves_validity_region(model, controller):
    del model, controller
    return (
        SimulationTrace(
            time_s=[0.0, 1.0, 2.0, 3.0],
            reference={"y": [0.1, 0.1, 0.1, 0.1]},
            states={"x1": [0.0, 0.05, 0.1, 0.3]},
            outputs={"y": [0.0, 0.1, 0.25, 0.3]},
            requested_controls={"u": [0.0, 0.1, 0.2, 0.3]},
            applied_controls={"u": [0.0, 0.1, 0.2, 0.3]},
        ),
        StabilityDecision(
            status="unstable",
            analysis_domain="continuous",
            pole_analysis_method="exact_continuous_interconnection",
            poles=[ComplexValue(real=0.2, imaginary=0.0)],
            trajectory_finite=True,
            trajectory_bounded=True,
            tail_error_envelope_contraction=-0.1,
            saturation_fraction=0.0,
            violations=["positive closed-loop pole"],
            evidence=["test trace"],
        ),
    )


def test_local_validity_violation_is_terminal_and_not_tunable():
    session = continuous_siso_session()

    guarded = run_next_trial(
        session,
        runner=trace_that_leaves_validity_region,
        result_guard=local_validity_guard(local_region()),
    )

    trace = guarded.trials[-1].traces[0]
    event = trace.events[-1]
    assert event.kind == "model_validity_boundary_violation"
    assert event.allowed_range == pytest.approx((-0.2, 0.2))
    assert event.channel == "y"
    assert event.value == pytest.approx(0.25)
    assert len(trace.time_s) == 3
    assert guarded.state == "inconclusive"
    assert "模型有效范围" in guarded.termination_reason
    with pytest.raises(ProposalValidationError, match="terminal"):
        build_gain_proposal_context(guarded)
