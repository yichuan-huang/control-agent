"""Terminal guard for trajectories that leave a local model's valid region."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import TypeAlias

from cfdc.lab.contracts import (
    SimulationEvent,
    SimulationTrace,
    StabilityDecision,
)
from cfdc.lab.model_contracts import ValidityRegion


SimulationResultGuard: TypeAlias = Callable[
    [list[SimulationTrace], StabilityDecision],
    tuple[list[SimulationTrace], StabilityDecision],
]


def _first_violation(
    trace: SimulationTrace,
    region: ValidityRegion,
) -> tuple[int, str, float, tuple[float, float]] | None:
    channel_groups: Sequence[
        tuple[
            Mapping[str, list[float]],
            Mapping[str, tuple[float, float]],
        ]
    ] = (
        (trace.applied_controls, region.input_ranges),
        (trace.states, region.state_ranges),
        (trace.outputs, region.output_ranges),
    )
    first: tuple[int, str, float, tuple[float, float]] | None = None
    for channels, ranges in channel_groups:
        for signal_name, allowed in ranges.items():
            values = channels.get(signal_name)
            if values is None:
                continue
            lower, upper = allowed
            for sample_index, value in enumerate(values):
                if value < lower or value > upper:
                    candidate = (
                        sample_index,
                        signal_name,
                        value,
                        allowed,
                    )
                    if first is None or candidate[0] < first[0]:
                        first = candidate
                    break
    return first


def _truncate_channels(
    channels: Mapping[str, list[float]],
    stop: int,
) -> dict[str, list[float]]:
    return {name: values[:stop] for name, values in channels.items()}


def _guard_trace(
    trace: SimulationTrace,
    region: ValidityRegion,
) -> tuple[SimulationTrace, bool]:
    violation = _first_violation(trace, region)
    if violation is None:
        return trace, False
    sample_index, signal_name, value, allowed = violation
    stop = sample_index + 1
    event = SimulationEvent(
        kind="model_validity_boundary_violation",
        sample_index=sample_index,
        time_s=trace.time_s[sample_index],
        message=(
            f"{signal_name} left the confirmed local model validity range; "
            "the controller cannot be judged from later samples"
        ),
        channel=signal_name,
        value=value,
        allowed_range=allowed,
    )
    return (
        SimulationTrace(
            time_s=trace.time_s[:stop],
            reference=_truncate_channels(trace.reference, stop),
            states=_truncate_channels(trace.states, stop),
            outputs=_truncate_channels(trace.outputs, stop),
            requested_controls=_truncate_channels(
                trace.requested_controls,
                stop,
            ),
            applied_controls=_truncate_channels(
                trace.applied_controls,
                stop,
            ),
            events=[
                *[
                    existing
                    for existing in trace.events
                    if existing.sample_index <= sample_index
                ],
                event,
            ],
        ),
        True,
    )


def apply_model_validity_guard(
    traces: list[SimulationTrace],
    decision: StabilityDecision,
    region: ValidityRegion,
) -> tuple[list[SimulationTrace], StabilityDecision]:
    """Stop at the first out-of-region sample without blaming the controller."""

    guarded: list[SimulationTrace] = []
    violated = False
    for trace in traces:
        guarded_trace, trace_violated = _guard_trace(trace, region)
        guarded.append(guarded_trace)
        violated = violated or trace_violated
    if not violated:
        return guarded, decision
    reason = (
        "model_validity_boundary_violation: trajectory left the confirmed "
        "local model range"
    )
    guarded_decision = decision.model_copy(
        update={
            "status": "inconclusive",
            "hard_failure": False,
            "violations": [
                *decision.violations,
                reason,
            ],
            "evidence": [
                *decision.evidence,
                (
                    "The local model, rather than the controller, became "
                    "invalid at the recorded boundary sample."
                ),
            ],
        }
    )
    return guarded, StabilityDecision.model_validate(
        guarded_decision.model_dump(mode="python")
    )


def local_validity_guard(
    region: ValidityRegion,
) -> SimulationResultGuard:
    typed_region = (
        region
        if isinstance(region, ValidityRegion)
        else ValidityRegion.model_validate(region)
    )

    def guard(
        traces: list[SimulationTrace],
        decision: StabilityDecision,
    ) -> tuple[list[SimulationTrace], StabilityDecision]:
        return apply_model_validity_guard(
            traces,
            decision,
            typed_region,
        )

    return guard


__all__ = [
    "SimulationResultGuard",
    "apply_model_validity_guard",
    "local_validity_guard",
]
