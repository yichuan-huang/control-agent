from __future__ import annotations

import hashlib

import numpy as np
from scipy import signal

from cfdc.models import (
    ControllerCandidate,
    ControllerValidationResult,
    PlantEvidencePackage,
    TransferFunctionModelSpec,
)
from cfdc.performance import build_performance_summary, calculate_channel_performance


def _limit(limits: dict[str, float], name: str) -> float:
    if name not in limits:
        raise ValueError(f"closed-loop validation requires '{name}'")
    return float(limits[name])


def validate_controller_on_model(
    package: PlantEvidencePackage,
    controller: ControllerCandidate,
) -> ControllerValidationResult:
    """Run an auditable unity-feedback PI validation on a supplied SISO model."""

    spec = package.validation_spec
    model = package.model
    if spec is None:
        raise ValueError("closed-loop validation requirements are missing")
    if not isinstance(model, TransferFunctionModelSpec) or model.time_domain != "continuous":
        return ControllerValidationResult(
            status="not_supported",
            violations=[
                "The first object-evidence release validates continuous SISO transfer-function controllers only."
            ],
        )
    if len(spec.reference) != 1:
        return ControllerValidationResult(
            status="not_supported",
            violations=[
                "Continuous SISO validation requires exactly one reference channel."
            ],
        )
    reference_name = next(iter(spec.reference))
    if reference_name != model.output_signal_id:
        return ControllerValidationResult(
            status="not_supported",
            violations=[
                "The validation reference channel does not match the model output signal."
            ],
        )
    if spec.initial_state:
        return ControllerValidationResult(
            status="not_supported",
            violations=[
                "Transfer-function validation cannot execute the declared initial_state without named state coordinates."
            ],
        )
    if not {"kp", "ki"}.issubset(controller.gains):
        return ControllerValidationResult(
            status="not_supported",
            violations=["The supplied controller is not a supported PI candidate."],
        )

    reference = float(spec.reference[reference_name])
    kp = float(controller.gains["kp"])
    ki = float(controller.gains["ki"])
    plant_num = np.asarray(model.numerator, dtype=float)
    plant_den = np.asarray(model.denominator, dtype=float)
    open_num = np.polymul([kp, ki], plant_num)
    open_den = np.polymul([1.0, 0.0], plant_den)
    closed_den = np.polyadd(open_den, open_num)
    output_num = open_num
    control_num = np.polymul([kp, ki], plant_den)

    sample_count = max(3, int(spec.horizon_s / spec.sample_time_s) + 1)
    time_s = np.linspace(0.0, spec.horizon_s, sample_count)
    reference_signal = np.full(sample_count, reference, dtype=float)
    try:
        _, output, _ = signal.lsim(
            signal.TransferFunction(output_num, closed_den),
            U=reference_signal,
            T=time_s,
        )
        _, control, _ = signal.lsim(
            signal.TransferFunction(control_num, closed_den),
            U=reference_signal,
            T=time_s,
        )
    except (ValueError, FloatingPointError) as exc:
        return ControllerValidationResult(
            status="failed",
            violations=[f"closed-loop numerical simulation failed: {exc}"],
        )
    output = np.asarray(output, dtype=float)
    control = np.asarray(control, dtype=float)
    if not np.all(np.isfinite(output)) or not np.all(np.isfinite(control)):
        return ControllerValidationResult(
            status="failed",
            violations=["closed-loop simulation produced non-finite values"],
        )

    channel = calculate_channel_performance(time_s, reference, output)
    input_min = _limit(spec.actuator_limits, "input_min")
    input_max = _limit(spec.actuator_limits, "input_max")
    output_min = _limit(spec.state_limits, "output_min")
    output_max = _limit(spec.state_limits, "output_max")
    saturation_fraction = float(np.mean((control < input_min) | (control > input_max)))
    violations: list[str] = []
    if float(np.min(control)) < input_min or float(np.max(control)) > input_max:
        violations.append("actuator_limit")
    if float(np.min(output)) < output_min or float(np.max(output)) > output_max:
        violations.append("output_state_limit")
    if channel.abs_final_error > _limit(spec.performance_limits, "max_abs_final_error"):
        violations.append("final_error")
    if channel.overshoot > _limit(spec.performance_limits, "max_overshoot"):
        violations.append("overshoot")
    max_settling = _limit(spec.performance_limits, "max_settling_time_s")
    if channel.settling_time_s is None or channel.settling_time_s > max_settling:
        violations.append("settling_time")
    if saturation_fraction > _limit(
        spec.performance_limits,
        "max_saturation_fraction",
    ):
        violations.append("saturation_fraction")

    performance = build_performance_summary(
        primary_channel=reference_name,
        channels={reference_name: channel},
        actuator_saturation_fractions={"input": saturation_fraction},
        state_boundaries={
            "min_output": float(np.min(output)),
            "max_output": float(np.max(output)),
            "min_input": float(np.min(control)),
            "max_input": float(np.max(control)),
        },
        limits={
            **spec.actuator_limits,
            **spec.state_limits,
            **spec.performance_limits,
        },
        violations=violations,
        success=not violations,
    )
    digest_payload = np.column_stack((time_s, reference_signal, output, control)).tobytes()
    return ControllerValidationResult(
        status="passed" if not violations else "failed",
        performance=performance,
        violations=violations,
        trace_sha256=hashlib.sha256(digest_payload).hexdigest(),
    )
