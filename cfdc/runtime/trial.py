from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

import numpy as np

from cfdc.models import (
    OnlinePerformanceMetrics,
    SafetyViolation,
    TrialReport,
    TrialSample,
)
from cfdc.online import compute_performance_metrics
from cfdc.runtime.safety import check_sample_safety


StateDict = dict[str, float]
ControlDict = dict[str, float]
ReferenceDict = dict[str, float]
ControllerFn = Callable[[StateDict, ReferenceDict, dict[str, float], float], ControlDict]
PlantStepFn = Callable[[StateDict, ControlDict, float], StateDict]
ReferenceFn = Callable[[float], ReferenceDict]


@dataclass(frozen=True)
class SafeTrialConfig:
    trial_id: str
    dt_s: float
    duration_s: float
    constraints: dict[str, float] = field(default_factory=dict)
    output_key: str = "output"
    reference_key: str = "output"
    control_key: str = "input"
    stop_on_first_violation: bool = True
    max_samples: int = 20000


def _metric_violations(
    metrics: OnlinePerformanceMetrics,
    constraints: dict[str, float],
    time_s: float,
) -> list[SafetyViolation]:
    checks = [
        ("max_overshoot", metrics.overshoot, "overshoot"),
        ("max_integral_absolute_error", metrics.integral_absolute_error, "integral absolute error"),
        ("max_high_frequency_control_rms", metrics.high_frequency_control_rms, "high-frequency control RMS"),
        ("max_actuator_saturation_fraction", metrics.actuator_saturation_fraction, "actuator saturation fraction"),
        ("max_nmp_undershoot", metrics.nmp_undershoot, "NMP undershoot"),
    ]
    violations: list[SafetyViolation] = []
    for key, observed, label in checks:
        limit = constraints.get(key)
        if limit is not None and observed > limit:
            violations.append(
                SafetyViolation(
                    constraint=key,
                    observed_value=observed,
                    limit=limit,
                    time_s=time_s,
                    message=f"{label} exceeded {limit}",
                )
            )

    max_settling = constraints.get("max_settling_time_s")
    if max_settling is not None and (
        metrics.settling_time_s is None or metrics.settling_time_s > max_settling
    ):
        violations.append(
            SafetyViolation(
                constraint="max_settling_time_s",
                observed_value=(
                    metrics.settling_time_s
                    if metrics.settling_time_s is not None
                    else time_s
                ),
                limit=max_settling,
                time_s=time_s,
                message=(
                    f"output did not settle within {max_settling}"
                    if metrics.settling_time_s is None
                    else f"settling time exceeded {max_settling}"
                ),
            )
        )
    return violations


class SafeTrialRunner:
    """Deterministic bounded-trial executor with structured safety reporting."""

    def __init__(self, config: SafeTrialConfig):
        if config.dt_s <= 0 or config.duration_s <= 0:
            raise ValueError("dt_s and duration_s must be positive")
        self.config = config

    def run(
        self,
        initial_state: StateDict,
        controller: ControllerFn,
        plant_step: PlantStepFn,
        gains: dict[str, float],
        reference: ReferenceDict | ReferenceFn | None = None,
    ) -> TrialReport:
        state = dict(initial_state)
        samples: list[TrialSample] = []
        safety_violations: list[SafetyViolation] = []
        steps = min(int(np.ceil(self.config.duration_s / self.config.dt_s)) + 1, self.config.max_samples)
        stop_reason = "duration_elapsed"

        for step in range(steps):
            time_s = step * self.config.dt_s
            ref = self._reference_at(reference, time_s)
            control = controller(dict(state), dict(ref), dict(gains), time_s)
            sample = TrialSample(
                time_s=time_s,
                state=dict(state),
                control=dict(control),
                reference=dict(ref),
                metadata={
                    "saturated": self._is_saturated(control),
                },
            )
            samples.append(sample)
            violations = check_sample_safety(sample, self.config.constraints)
            safety_violations.extend(violations)
            if violations and self.config.stop_on_first_violation:
                stop_reason = violations[0].constraint
                break
            if step < steps - 1:
                state = plant_step(dict(state), dict(control), self.config.dt_s)

        metrics = self._metrics(samples)
        if metrics is not None:
            aggregate_violations = _metric_violations(metrics, self.config.constraints, samples[-1].time_s)
            safety_violations.extend(aggregate_violations)
            if aggregate_violations and stop_reason == "duration_elapsed":
                stop_reason = aggregate_violations[0].constraint

        accepted = not safety_violations
        return TrialReport(
            trial_id=self.config.trial_id,
            accepted=accepted,
            stop_reason="accepted" if accepted else stop_reason,
            duration_s=samples[-1].time_s if samples else 0.0,
            samples=samples,
            metrics=metrics,
            safety_violations=safety_violations,
            tested_gains=dict(gains),
            accepted_gains=dict(gains) if accepted else {},
        )

    def _reference_at(
        self,
        reference: ReferenceDict | ReferenceFn | None,
        time_s: float,
    ) -> ReferenceDict:
        if reference is None:
            return {self.config.reference_key: 0.0}
        if callable(reference):
            return reference(time_s)
        return dict(reference)

    def _is_saturated(self, control: ControlDict) -> bool:
        limit = self.config.constraints.get("max_abs_control")
        if limit is None:
            return False
        value = control.get(self.config.control_key)
        return value is not None and abs(value) >= 0.98 * limit

    def _metrics(self, samples: list[TrialSample]) -> OnlinePerformanceMetrics | None:
        if len(samples) < 3:
            return None
        if not all(self.config.output_key in sample.state for sample in samples):
            return None
        if not all(self.config.control_key in sample.control for sample in samples):
            return None
        time_s = [sample.time_s for sample in samples]
        output = [sample.state[self.config.output_key] for sample in samples]
        reference = [
            sample.reference.get(self.config.reference_key, sample.reference.get(self.config.output_key, 0.0))
            for sample in samples
        ]
        control = [sample.control[self.config.control_key] for sample in samples]
        return compute_performance_metrics(
            time_s,
            reference,
            output,
            control,
            saturation_limit=self.config.constraints.get("max_abs_control"),
        )
