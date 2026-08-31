"""Deterministic, provider-bound experiment protocol compiler."""

from __future__ import annotations

import math
from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from jsonschema import Draft202012Validator

from cfdc.kernel.contracts import PROTOCOL_VERSION, TaskContract, fingerprint

PROTOCOL_REQUEST_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["operation", "segments", "repeats", "sample_period_s"],
    "properties": {
        "operation": {"type": "string", "minLength": 1},
        "data_kind": {"type": "string", "minLength": 1},
        "segments": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["duration_s", "input_value"],
                "properties": {
                    "duration_s": {"type": "number", "exclusiveMinimum": 0},
                    "input_value": {"type": "number"},
                },
                "additionalProperties": False,
            },
        },
        "repeats": {"type": "integer", "minimum": 1},
        "sample_period_s": {"type": "number", "exclusiveMinimum": 0},
        "requested_signals": {"type": "array", "items": {"type": "string"}},
        "control_inputs": {"type": "array", "items": {"type": "string"}},
        "initial_condition_id": {"type": "string"},
    },
    "additionalProperties": True,
}

_DATA_KIND_BY_OPERATION = {
    "bounded_bidirectional_staircase": "step_b_repeated_staircase",
    "step_b_repeated_staircase": "step_b_repeated_staircase",
    "bounded_two_level_multisine": "class_iv_frequency_repeats",
    "class_iv_frequency_repeats": "class_iv_frequency_repeats",
    "class_iv_amplitude_release_repeats": "class_iv_amplitude_release_repeats",
    "class_iv_release_repeats": "class_iv_release_repeats",
    "unstable_local_balance_repeats": "unstable_local_balance_repeats",
    "bounded_mimo_dc_then_hadamard_multisine": "class_v_mimo_summary",
    "class_v_mimo_summary": "class_v_mimo_summary",
}


def _finite(value: Any, label: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label}_must_be_finite") from exc
    if not math.isfinite(result):
        raise ValueError(f"{label}_must_be_finite")
    return result


def _default_request(task: TaskContract, route: Mapping[str, Any]) -> dict[str, Any]:
    operation = str(next(iter(route.get("experiment_primitives", ())), "bounded_input_sequence"))
    profile_id = str(route.get("profile_id") or "")
    if profile_id == "mimo_2x2_coupled":
        operation = "bounded_mimo_dc_then_hadamard_multisine"
    elif profile_id in {"nmp_inverse_response", "generic_unstable_higher_order"}:
        operation = "class_iv_frequency_repeats"
    elif profile_id == "underactuated_cartpole":
        operation = "unstable_local_balance_repeats"
    elif profile_id == "vtol_cascaded":
        operation = "bounded_mimo_dc_then_hadamard_multisine"
    elif profile_id == "second_order_oscillator":
        operation = "bounded_two_level_multisine"
    if operation in {"ramp_step", "pulse", "free_decay"}:
        operation = "bounded_input_sequence"
    lower = float(task.input_min if task.input_min is not None else -1.0)
    upper = float(task.input_max if task.input_max is not None else 1.0)
    amplitude = 0.1 * min(abs(lower), abs(upper))
    if amplitude <= 0:
        amplitude = 0.05 * (upper - lower)
    amplitude = max(min(amplitude, upper), lower)
    duration = float(task.response_time_preference_s or 10.0)
    duration = min(max(duration, 1.0), float(task.budgets.get("cumulative_excitation_time_s", 1800.0)) / 3.0)
    return {
        "operation": operation,
        "data_kind": _DATA_KIND_BY_OPERATION.get(operation, "siso_repeated_timeseries"),
        "initial_condition_id": "declared_operating_region",
        "segments": [
            {"duration_s": duration / 4.0, "input_value": 0.0},
            {"duration_s": duration / 4.0, "input_value": amplitude},
            {"duration_s": duration / 4.0, "input_value": -amplitude},
            {"duration_s": duration / 4.0, "input_value": 0.0},
        ],
        "repeats": 3,
        "sample_period_s": max(min(duration / 200.0, 0.1), 0.001),
        "requested_signals": list(task.measured_signals),
        "control_inputs": list(task.control_inputs or (task.control_input,)),
    }


@dataclass(frozen=True)
class ExperimentProtocol:
    value: Mapping[str, Any]

    @property
    def fingerprint(self) -> str:
        return str(self.value["protocol_fingerprint"])

    def to_dict(self) -> dict[str, Any]:
        return deepcopy(dict(self.value))

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> ExperimentProtocol:
        raw = deepcopy(dict(value))
        supplied = raw.pop("protocol_fingerprint", None)
        if raw.get("protocol_version") != PROTOCOL_VERSION:
            raise ValueError("protocol_version_mismatch")
        expected = fingerprint(raw)
        if supplied != expected:
            raise ValueError("protocol_fingerprint_mismatch")
        raw["protocol_fingerprint"] = expected
        return cls(raw)


def compile_protocol(
    task: TaskContract,
    route: Mapping[str, Any],
    *,
    provider: Mapping[str, Any],
    request: Mapping[str, Any] | None = None,
    phase: Mapping[str, Any] | None = None,
) -> ExperimentProtocol:
    raw = deepcopy(dict(request)) if request is not None else _default_request(task, route)
    errors = sorted(Draft202012Validator(PROTOCOL_REQUEST_SCHEMA).iter_errors(raw), key=lambda item: list(item.path))
    if errors:
        raise ValueError("protocol_request_invalid: " + " | ".join(item.message for item in errors))
    capabilities = {str(item) for item in provider.get("capabilities", ())}
    operation = str(raw["operation"])
    if capabilities and operation not in capabilities and raw.get("data_kind") not in capabilities:
        raise ValueError(f"provider_operation_not_supported: {operation}")
    task_lower = _finite(task.input_min, "task_input_min")
    task_upper = _finite(task.input_max, "task_input_max")
    if task_lower >= task_upper:
        raise ValueError("task_input_bounds_invalid")
    segments: list[dict[str, float]] = []
    total = 0.0
    exposure = 0.0
    maximum_step = 0.0
    previous = 0.0
    for index, item in enumerate(raw["segments"]):
        duration = _finite(item["duration_s"], f"segment_{index}_duration")
        command = _finite(item["input_value"], f"segment_{index}_input")
        if duration <= 0 or not task_lower <= command <= task_upper:
            raise ValueError("protocol_segment_outside_task_envelope")
        total += duration
        exposure += abs(command) * duration
        maximum_step = max(maximum_step, abs(command - previous))
        previous = command
        segments.append({"duration_s": duration, "input_value": command})
    maximum_step = max(maximum_step, abs(previous))
    duration_budget = float(task.budgets.get("cumulative_excitation_time_s", 1800.0))
    if total * int(raw["repeats"]) > duration_budget + 1e-12:
        raise ValueError("protocol_excitation_budget_exceeded")
    sample_period = _finite(raw["sample_period_s"], "sample_period")
    sample_count = round(total / sample_period) + 1
    if sample_count < 8 or sample_count > 2_000_000:
        raise ValueError("protocol_sample_count_out_of_bounds")
    requested = tuple(str(item) for item in raw.get("requested_signals") or task.measured_signals)
    if not set(requested) <= set(task.measured_signals):
        raise ValueError("protocol_signal_not_declared_by_task")
    requested_inputs = tuple(
        str(item)
        for item in raw.get("control_inputs")
        or task.control_inputs
        or (task.control_input,)
    )
    if set(requested_inputs) != set(task.control_inputs or (task.control_input,)):
        raise ValueError("protocol_control_input_binding_mismatch")
    body = {
        "protocol_version": PROTOCOL_VERSION,
        "task_fingerprint": task.fingerprint,
        "route_id": route.get("route_id"),
        "provider_id": provider.get("provider_id"),
        "provider_version": provider.get("provider_version"),
        "provider_capabilities_fingerprint": fingerprint(sorted(capabilities)),
        "phase_id": phase.get("phase_id") if phase else None,
        "operation": operation,
        "data_kind": str(raw.get("data_kind") or _DATA_KIND_BY_OPERATION.get(operation, "siso_repeated_timeseries")),
        "initial_condition_id": str(raw.get("initial_condition_id") or "declared_operating_region"),
        "segments": segments,
        "repeats": int(raw["repeats"]),
        "sample_period_s": sample_period,
        "duration_s": total,
        "expected_sample_count": sample_count,
        "requested_signals": list(requested),
        "control_inputs": list(requested_inputs),
        "input_bounds": [task_lower, task_upper],
        "state_stop": task.state_stop,
        "units": {
            "time": "s",
            "input": task.input_units or "unspecified",
            "outputs": {name: task.signal_units.get(name, "unspecified") for name in requested},
        },
        "derived_limits": {
            "integrated_absolute_input": exposure,
            "maximum_input_step": maximum_step,
            "cumulative_excitation_time_s": total * int(raw["repeats"]),
        },
        "stop_condition": {
            "input_bounds": [task_lower, task_upper],
            "output_bounds": ([task.output_min, task.output_max] if task.output_min is not None else None),
            "state_stop": task.state_stop,
        },
    }
    body["protocol_fingerprint"] = fingerprint(body)
    return ExperimentProtocol(body)


def verify_protocol(
    value: Mapping[str, Any],
    *,
    task: TaskContract,
    route: Mapping[str, Any],
    provider: Mapping[str, Any],
) -> ExperimentProtocol:
    protocol = ExperimentProtocol.from_mapping(value)
    request = {
        "operation": protocol.value["operation"],
        "data_kind": protocol.value["data_kind"],
        "initial_condition_id": protocol.value["initial_condition_id"],
        "segments": protocol.value["segments"],
        "repeats": protocol.value["repeats"],
        "sample_period_s": protocol.value["sample_period_s"],
        "requested_signals": protocol.value["requested_signals"],
        "control_inputs": protocol.value.get("control_inputs"),
    }
    expected = compile_protocol(task, route, provider=provider, request=request)
    if expected.fingerprint != protocol.fingerprint:
        raise ValueError("protocol_binding_mismatch")
    return protocol


__all__ = ["PROTOCOL_REQUEST_SCHEMA", "ExperimentProtocol", "compile_protocol", "verify_protocol"]
