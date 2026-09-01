"""Trajectory-only performance judgment, independent of providers and runtimes.

All numbers below are reconstructed from public samples.  This module does not
import a simulator, controller implementation, feature estimator or LLM.  The
finite-horizon safety gate is not a proof of asymptotic stability: that authority
belongs to the separately bound initial qualification.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from copy import deepcopy
from itertools import pairwise
from typing import Any

from .contracts import fingerprint

JUDGE_VERSION = "cfdc-independent-judge/v2.0"
STRICT_FREEZE_VERSION = "cfdc-freeze/v2.0"
STRICT_PACKET_VERSION = "cfdc-evaluation-packet/v2.0"
HARD_FAILURE_SCORE = 1e12


def _number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{label}_finite_number_required")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{label}_finite_number_required")
    return result


def _array(value: Any, size: int | None, label: str) -> list[float]:
    if not isinstance(value, (list, tuple)) or (
        size is not None and len(value) != size
    ):
        raise ValueError(f"trajectory_{label}_length_mismatch")
    return [_number(item, f"trajectory_{label}") for item in value]


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if value is None:
        raise ValueError(f"{label}_required")
    if not isinstance(value, Mapping):
        raise TypeError(f"{label}_object_required")
    return value


def _signed(value: Mapping[str, Any], key: str) -> None:
    supplied = value.get(key)
    raw = dict(value)
    raw.pop(key, None)
    if not supplied or fingerprint(raw) != supplied:
        raise ValueError(f"{key}_mismatch")


def _public(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if any(
                word in str(key).lower()
                for word in ("private", "truth", "hidden", "secret", "oracle")
            ):
                if key == "private_truth_returned" and item is False:
                    continue
                raise ValueError("private_truth_not_allowed")
            _public(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _public(item)
    elif isinstance(value, float) and not math.isfinite(value):
        raise ValueError("nonfinite_public_value")


def _bound_pair(value: Any, label: str) -> tuple[float, float]:
    pair = _array(value, 2, label)
    if pair[0] >= pair[1]:
        raise ValueError(f"{label}_invalid_bounds")
    return pair[0], pair[1]


def _criterion(
    criteria: Mapping[str, Any], name: str, channel: str | None = None
) -> float | None:
    local = criteria.get("per_channel", {}).get(channel, {}) if channel else {}
    value = local.get(name, criteria.get(name))
    if value is None:
        return None
    number = _number(value, f"criterion_{name}")
    if number < 0:
        raise ValueError(f"criterion_{name}_negative")
    return number


def wilson_lower_bound(successes: int, total: int) -> float:
    """Two-sided 95% Wilson interval's lower endpoint, fixed preregistered n."""
    if total <= 0 or not 0 <= successes <= total:
        raise ValueError("invalid_binomial_counts")
    z = 1.959963984540054
    p = successes / total
    z2 = z * z
    return (
        p
        + z2 / (2 * total)
        - z * math.sqrt(p * (1 - p) / total + z2 / (4 * total * total))
    ) / (1 + z2 / total)


def _violation(actual: float | None, limit: float, *, minimum: bool = False) -> float:
    if actual is None:
        return HARD_FAILURE_SCORE
    scale = max(abs(limit), 1e-12)
    return max(0.0, (limit - actual if minimum else actual - limit) / scale)


def _hold(
    times: Sequence[float], errors: Sequence[float], tolerance: float
) -> tuple[float | None, float]:
    last_outside = -1
    for index, error in enumerate(errors):
        if abs(error) > tolerance:
            last_outside = index
    start = last_outside + 1
    if start == len(times):
        return None, 0.0
    return times[start], times[-1] - times[start]


def _channel_metrics(
    times: list[float], output: list[float], reference: list[float], tolerance: float
) -> dict[str, Any]:
    errors = [y - r for y, r in zip(output, reference, strict=True)]
    settling, hold = _hold(times, errors, tolerance)
    # Overshoot is in engineering units. Direction is measured from the initial
    # output, not from reference[0] (which is already the step's target).
    direction = 1 if reference[-1] >= output[0] else -1
    overshoot = max(0.0, max(direction * error for error in errors))
    iae = sum(
        (abs(errors[i]) + abs(errors[i + 1])) * (times[i + 1] - times[i]) / 2
        for i in range(len(times) - 1)
    )
    return {
        "final_abs_error": abs(errors[-1]),
        "overshoot": overshoot,
        "settling_time_s": settling,
        "iae": iae,
        "peak_abs_output": max(map(abs, output)),
        "peak_abs_error": max(map(abs, errors)),
        "hold_duration_s": hold,
    }


def _task_metrics(
    trial: Mapping[str, Any],
    trace: Mapping[str, Any],
    times: list[float],
    criteria: Mapping[str, Any],
    channels: Mapping[str, Any],
    scenario: Mapping[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    task_type = criteria.get("task_type")
    metrics: dict[str, Any] = {}
    failures: list[str] = []
    events = trial.get("events")
    if events is None:
        raise ValueError("trial_events_required")
    if not isinstance(events, list):
        raise TypeError("trial_events_list_required")
    if task_type == "local_setpoint_hold":
        return metrics, failures
    if task_type == "disturbance_recovery_to_hold":
        expected = scenario.get("disturbance", criteria.get("disturbance"))
        expected = _mapping(expected, "frozen_disturbance")
        disturbance_start = _number(expected.get("time_s"), "disturbance_time")
        duration = _number(expected.get("duration_s"), "disturbance_duration")
        amplitude = _number(expected.get("amplitude"), "disturbance_amplitude")
        end = disturbance_start + duration
        if (
            duration <= 0
            or amplitude == 0
            or not 0
            <= disturbance_start
            < end
            < _number(criteria.get("horizon_s"), "horizon")
            or expected.get("channel") not in trace["control_inputs"]
        ):
            raise ValueError("frozen_disturbance_invalid")
        matching = [
            event
            for event in events
            if isinstance(event, Mapping) and event.get("kind") == "disturbance"
        ]
        if len(matching) != 1:
            return metrics, ["disturbance_event_missing_or_duplicate"]
        event = matching[0]
        for key in ("time_s", "channel", "amplitude", "duration_s"):
            if key not in expected or event.get(key) != expected[key]:
                return metrics, ["disturbance_event_contract_mismatch"]
        sample_index = event.get("sample_index")
        if (
            isinstance(sample_index, bool)
            or not isinstance(sample_index, int)
            or not 0 <= sample_index < len(times) - 1
            or not times[sample_index] <= disturbance_start < times[sample_index + 1]
        ):
            return metrics, ["disturbance_event_sample_mismatch"]
        if end >= times[-1]:
            return metrics, ["disturbance_outside_trial"]
        start = next(i for i, time in enumerate(times) if time >= end)
        recoveries, holds = [], []
        for name in channels:
            tolerance = _criterion(criteria, "recovery_abs_error_max", name)
            if tolerance is None:
                raise ValueError("recovery_error_criterion_required")
            errors = [
                y - r
                for y, r in zip(
                    trace["outputs"][name][start:],
                    trace["references"][name][start:],
                    strict=True,
                )
            ]
            recovered, hold = _hold(times[start:], errors, tolerance)
            recoveries.append(None if recovered is None else recovered - end)
            holds.append(hold)
        recovery = None if any(item is None for item in recoveries) else max(recoveries)
        metrics.update(
            # An event proves packet provenance, not physical execution. The
            # provider's actual perturbation needs independent engine tests.
            disturbance_event_verified=True,
            recovered_to_hold=recovery is not None,
            recovery_time_s=recovery,
            post_recovery_hold_duration_s=min(holds),
            disturbance_event_fingerprint=fingerprint(dict(event)),
        )
        return metrics, failures
    if task_type == "transition_then_hold":
        return _phase_metrics(trace, times, criteria, channels, events)
    raise ValueError("evaluation_task_type_unsupported")


def _phase_metrics(
    trace: Mapping[str, Any],
    times: list[float],
    criteria: Mapping[str, Any],
    channels: Mapping[str, Any],
    events: list[Any],
) -> tuple[dict[str, Any], list[str]]:
    """Bind registered phase predicates and handoffs to public sampled evidence.

    ``stable_region`` is an optional destination-phase map from measured signal
    to [lower, upper]. State snapshots straddle the public sample boundary;
    ``state_on_entry`` records memory before the destination's first update.
    """
    phases = criteria.get("phases")
    if not isinstance(phases, list) or not phases:
        raise ValueError("frozen_phase_contract_required")
    phase_map = {}
    signals = {**trace["outputs"], **trace.get("measurements", {})}
    for raw_phase in phases:
        phase = _mapping(raw_phase, "phase")
        phase_id = phase.get("phase_id")
        if not isinstance(phase_id, str) or not phase_id or phase_id in phase_map:
            raise ValueError("frozen_phase_identity_invalid")
        predicate = _mapping(phase.get("exit_predicate"), "phase_exit_predicate")
        if predicate.get("kind") != "within_band":
            raise ValueError("unregistered_phase_predicate")
        if predicate.get("signal") not in signals:
            raise ValueError("phase_predicate_signal_missing")
        _number(predicate.get("target"), "phase_target")
        if (
            _number(predicate.get("tolerance"), "phase_tolerance") <= 0
            or _number(phase.get("dwell_s"), "phase_dwell") <= 0
            or _number(phase.get("timeout_s"), "phase_timeout") <= 0
            or _number(phase.get("hysteresis", 0.0), "phase_hysteresis") < 0
        ):
            raise ValueError("phase_numeric_contract_invalid")
        if phase.get("state_policy") not in {"reset", "inherit"}:
            raise ValueError("unregistered_phase_state_policy")
        references = _mapping(phase.get("references"), "frozen_phase_references")
        if set(references) != set(channels):
            raise ValueError("frozen_phase_reference_map_mismatch")
        for value in references.values():
            _number(value, "phase_reference")
        region = _mapping(phase.get("stable_region", {}), "phase_stable_region")
        for signal, bounds in region.items():
            if signal not in trace.get("measurements", {}):
                raise ValueError("phase_stable_region_measurement_missing")
            _bound_pair(bounds, "phase_stable_region")
        phase_map[phase_id] = phase

    phase_ids = trace["phase_ids"]
    boundaries = [i for i in range(1, len(times)) if phase_ids[i] != phase_ids[i - 1]]
    observed = [phase_ids[0], *[phase_ids[i] for i in boundaries]]
    expected_ids = list(phase_map)
    failures = []
    if observed != expected_ids:
        failures.append("phase_sequence_incomplete")
    handoffs = [
        event
        for event in events
        if isinstance(event, Mapping) and event.get("kind") == "handoff"
    ]
    if len(handoffs) != len(phases) - 1 or len(handoffs) != len(boundaries):
        failures.append("handoff_evidence_incomplete")

    for index, phase_id in enumerate(phase_ids):
        phase = phase_map.get(phase_id)
        if phase is None:
            continue
        if any(
            trace["references"][name][index] != value
            for name, value in phase["references"].items()
        ):
            raise ValueError("trajectory_phase_reference_mismatch")

    # Boundary samples were measured under the previous controller, before the
    # runner labels the first new-phase sample. Include them in the old dwell.
    for start, end in zip([0, *boundaries], [*boundaries, len(times) - 1], strict=True):
        phase = phase_map.get(phase_ids[start])
        if phase is None:
            continue
        predicate = phase["exit_predicate"]
        entered = None
        # A boundary closes the prior phase. The destination FSM first checks
        # its predicate on the following sample, so do not count it twice.
        predicate_start = start if start == 0 else start + 1
        for index in range(predicate_start, end + 1):
            error = abs(signals[predicate["signal"]][index] - predicate["target"])
            if entered is not None and error > predicate["tolerance"] + phase.get(
                "hysteresis", 0.0
            ):
                entered = None
            if entered is None and error <= predicate["tolerance"]:
                entered = times[index]
        held = 0.0 if entered is None else times[end] - entered
        if held + 1e-9 < phase["dwell_s"]:
            failures.append(f"phase_dwell_not_verified:{phase['phase_id']}")
        if times[end] - times[start] > phase["timeout_s"] + 1e-9:
            failures.append(f"phase_timeout:{phase['phase_id']}")

    for number, (event, boundary) in enumerate(zip(handoffs, boundaries)):
        if number >= len(phases) - 1:
            break
        if (
            event.get("from_phase") != expected_ids[number]
            or event.get("to_phase") != expected_ids[number + 1]
            or event.get("from_phase") != phase_ids[boundary - 1]
            or event.get("to_phase") != phase_ids[boundary]
        ):
            failures.append("handoff_order_mismatch")
        if (
            isinstance(event.get("sample_index"), bool)
            or not isinstance(event.get("sample_index"), int)
            or event["sample_index"] != boundary
            or isinstance(event.get("time_s"), bool)
            or event.get("time_s") != times[boundary]
        ):
            failures.append("handoff_sample_mismatch")
        expected_snapshots = {
            "state_before": trace["controller_states"][boundary - 1],
            "state_after": trace["controller_states"][boundary],
            "command_before": {
                name: values[boundary - 1]
                for name, values in trace["control_inputs"].items()
            },
            "command_after": {
                name: values[boundary]
                for name, values in trace["control_inputs"].items()
            },
        }
        if any(
            not isinstance(event.get(field), Mapping) or event[field] != snapshot
            for field, snapshot in expected_snapshots.items()
        ):
            failures.append("handoff_snapshot_mismatch")
        destination = phases[number + 1]
        policy = destination["state_policy"]
        entry = {} if policy == "reset" else expected_snapshots["state_before"]
        if event.get("state_policy") != policy or event.get("state_on_entry") != entry:
            failures.append("handoff_state_policy_mismatch")
        for signal, bounds in destination.get("stable_region", {}).items():
            value = trace["measurements"][signal][boundary]
            if not bounds[0] <= value <= bounds[1]:
                failures.append(f"handoff_outside_stable_region:{signal}")

    return {
        "completed_phase_ids": observed,
        "completed_phase_count": len(observed),
        "verified_handoff_count": len(handoffs) if not failures else 0,
        "final_hold_duration_s": min(
            value["hold_duration_s"] for value in channels.values()
        ),
        "entered_goal_region": not failures,
    }, failures


def _judge_trial(
    trial: Mapping[str, Any], freeze: Mapping[str, Any], scenario: Mapping[str, Any]
) -> dict[str, Any]:
    criteria = _mapping(freeze.get("evaluation_contract"), "evaluation_contract")
    runtime = _mapping(freeze.get("runtime_contract"), "runtime_contract")
    trace = _mapping(trial.get("trajectory"), "trajectory")
    stop = _mapping(trial.get("stop_event"), "stop_event")
    if (
        not isinstance(stop.get("triggered"), bool)
        or not isinstance(stop.get("reason"), str)
        or not stop["reason"]
    ):
        raise ValueError("stop_event_incomplete")
    times = _array(trace.get("time_s"), None, "time_s")
    if len(times) < 2 or times[0] != 0:
        raise ValueError("trajectory_sampling_invalid")
    horizon = _number(criteria.get("horizon_s"), "horizon")
    dt = _number(criteria.get("sample_time_s"), "sample_time")
    if (
        horizon <= 0
        or dt <= 0
        or any(b <= a or b - a > dt * (1 + 1e-6) for a, b in pairwise(times))
    ):
        raise ValueError("trajectory_sampling_invalid")
    if times[-1] > horizon + 1e-8 or (
        not stop["triggered"] and abs(times[-1] - horizon) > 1e-8
    ):
        raise ValueError("trajectory_horizon_incomplete")
    if abs(_number(stop.get("time_s"), "stop_event_time") - times[-1]) > 1e-8:
        raise ValueError("stop_event_time_mismatch")
    if not stop["triggered"] and stop["reason"] != "horizon_complete":
        raise ValueError("stop_event_completion_reason_invalid")
    size = len(times)
    states = trace.get("controller_states")
    phases = trace.get("phase_ids")
    if (
        not isinstance(states, list)
        or len(states) != size
        or not all(isinstance(state, Mapping) for state in states)
    ):
        raise ValueError("trajectory_controller_states_required")
    if (
        not isinstance(phases, list)
        or len(phases) != size
        or not all(isinstance(phase, str) and phase for phase in phases)
    ):
        raise ValueError("trajectory_phase_ids_required")
    tracked = runtime.get("tracked_signals")
    inputs = runtime.get("control_inputs")
    if (
        not tracked
        or not inputs
        or len(set(tracked)) != len(tracked)
        or len(set(inputs)) != len(inputs)
    ):
        raise ValueError("runtime_signal_map_required")
    outputs = _mapping(trace.get("outputs"), "trajectory_outputs")
    refs = _mapping(trace.get("references"), "trajectory_references")
    commands = _mapping(trace.get("control_inputs"), "trajectory_control_inputs")
    raws = _mapping(trace.get("raw_control_inputs"), "trajectory_raw_control_inputs")
    if (
        set(outputs) != set(tracked)
        or set(refs) != set(tracked)
        or set(commands) != set(inputs)
        or set(raws) != set(inputs)
    ):
        raise ValueError("trajectory_signal_map_mismatch")
    hard_failures = [str(stop["reason"])] if stop["triggered"] else []
    # Physical state safety is defined only over public measured channels.
    # Controller memory is a separate per-sample mapping and has its own bounds.
    declared_measurements = runtime.get("measured_signals")
    state_bounds = _mapping(runtime.get("state_bounds", {}), "state_bounds")
    measurements = _mapping(trace.get("measurements", {}), "trajectory_measurements")
    if declared_measurements is not None and (
        not isinstance(declared_measurements, list)
        or not declared_measurements
        or not all(isinstance(name, str) and name for name in declared_measurements)
        or len(set(declared_measurements)) != len(declared_measurements)
        or set(measurements) != set(declared_measurements)
        or not set(tracked) <= set(declared_measurements)
    ):
        raise ValueError("trajectory_measurement_map_mismatch")
    if not set(state_bounds) <= set(measurements):
        raise ValueError("trajectory_bounded_state_measurement_missing")
    measured_values = {
        name: _array(values, size, f"measurement_{name}")
        for name, values in measurements.items()
    }
    for name, values in measured_values.items():
        if name in outputs and values != _array(outputs[name], size, name):
            raise ValueError("trajectory_output_measurement_mismatch")
        if name in state_bounds:
            lower, upper = _bound_pair(state_bounds[name], f"state_{name}")
            if min(values) < lower or max(values) > upper:
                hard_failures.append(f"state_limit:{name}")
    if runtime.get("state_stop") is not None:
        state_stop = _number(runtime["state_stop"], "state_stop")
        if state_stop <= 0:
            raise ValueError("state_stop_positive_required")
        # Older minimal fixtures lack a measured-signal declaration. In that
        # case tracked outputs are the only declared physical measurements.
        safety_values = measured_values or {
            name: _array(outputs[name], size, name) for name in tracked
        }
        if any(
            abs(value) > state_stop
            for values in safety_values.values()
            for value in values
        ):
            hard_failures.append("state_stop_limit")
    for name, bounds in _mapping(
        runtime.get("controller_state_bounds", {}), "controller_state_bounds"
    ).items():
        if any(name not in state for state in states):
            raise ValueError("trajectory_bounded_controller_state_missing")
        values = [_number(state[name], f"controller_state_{name}") for state in states]
        lower, upper = _bound_pair(bounds, f"controller_state_{name}")
        if min(values) < lower or max(values) > upper:
            hard_failures.append(f"controller_state_limit:{name}")
    violations: list[float] = []
    channels: dict[str, Any] = {}
    input_metrics: dict[str, Any] = {}
    for name in tracked:
        output = _array(outputs[name], size, name)
        reference = _array(refs[name], size, f"reference_{name}")
        frozen_references = criteria.get("references")
        if criteria.get("task_type") != "transition_then_hold":
            frozen_references = _mapping(frozen_references, "frozen_references")
            expected_reference = _number(
                frozen_references.get(name), "frozen_reference"
            )
            if any(abs(value - expected_reference) > 1e-10 for value in reference):
                raise ValueError("trajectory_reference_mismatch")
        tolerance = _criterion(criteria, "final_abs_error_max", name)
        if tolerance is None:
            tolerance = _criterion(criteria, "recovery_abs_error_max", name)
        if tolerance is None:
            raise ValueError("error_criterion_required")
        metrics = _channel_metrics(times, output, reference, tolerance)
        channels[name] = metrics
        bounds = runtime.get("output_bounds", {}).get(name)
        if bounds is not None:
            lower, upper = _bound_pair(bounds, name)
            if min(output) < lower or max(output) > upper:
                hard_failures.append(f"output_limit:{name}")
        for metric, key in (
            ("final_abs_error", "final_abs_error_max"),
            ("overshoot", "overshoot_max"),
            ("settling_time_s", "settling_time_max_s"),
            ("iae", "iae_max"),
            ("peak_abs_output", "peak_abs_output_max"),
        ):
            limit = _criterion(criteria, key, name)
            if limit is not None:
                violations.append(_violation(metrics[metric], limit))
        minimum = _criterion(criteria, "hold_duration_min_s", name)
        if minimum is not None:
            violations.append(
                _violation(metrics["hold_duration_s"], minimum, minimum=True)
            )
    for name in inputs:
        command = _array(commands[name], size, name)
        raw = _array(raws[name], size, f"raw_{name}")
        lower, upper = _bound_pair(
            runtime.get("input_bounds", {}).get(name), f"input_{name}"
        )
        if min(command) < lower - 1e-10 or max(command) > upper + 1e-10:
            hard_failures.append(f"input_limit:{name}")
        if any(
            abs(value - min(max(before, lower), upper)) > 1e-8
            for value, before in zip(command, raw, strict=True)
        ):
            hard_failures.append(f"input_clipping_mismatch:{name}")
        saturated = [abs(a - b) > 1e-10 for a, b in zip(command, raw, strict=True)]
        duration = sum(times[i + 1] - times[i] for i in range(size - 1) if saturated[i])
        metrics = {
            "peak_abs_input": max(map(abs, command)),
            "raw_peak_abs_input": max(map(abs, raw)),
            "saturation_duration_s": duration,
            "saturation_fraction": duration / times[-1],
        }
        input_metrics[name] = metrics
        for metric, key in (
            ("peak_abs_input", "peak_abs_input_max"),
            ("saturation_duration_s", "saturation_duration_max_s"),
            ("saturation_fraction", "saturation_ratio_max"),
        ):
            limit = _criterion(criteria, key, name)
            if limit is not None:
                violations.append(_violation(metrics[metric], limit))
    task_metrics, task_failures = _task_metrics(
        trial, trace, times, criteria, channels, scenario
    )
    for metric, key, minimum in (
        ("recovery_time_s", "recovery_time_max_s", False),
        ("post_recovery_hold_duration_s", "post_recovery_hold_duration_min_s", True),
        ("final_hold_duration_s", "final_hold_duration_min_s", True),
    ):
        limit = _criterion(criteria, key)
        if limit is not None:
            violations.append(
                _violation(task_metrics.get(metric), limit, minimum=minimum)
            )
    score = max(violations, default=0.0)
    if hard_failures or task_failures:
        score = HARD_FAILURE_SCORE
    metrics = {
        "channels": channels,
        "inputs": input_metrics,
        "sample_count": size,
        "duration_s": times[-1],
        **task_metrics,
    }
    # Scalar compatibility aliases are always worst-channel derived values.
    for key in ("final_abs_error", "overshoot", "iae", "peak_abs_output"):
        metrics[key] = max(item[key] for item in channels.values())
    metrics["hold_duration_s"] = min(
        item["hold_duration_s"] for item in channels.values()
    )
    settling = [item["settling_time_s"] for item in channels.values()]
    metrics["settling_time_s"] = None if None in settling else max(settling)
    return {
        "trial_id": trial["trial_id"],
        "scenario_id": trial["scenario_id"],
        "seed": trial["seed"],
        "stable": not hard_failures,
        "evidence_valid": not task_failures,
        "stopped_on_limit": bool(stop["triggered"]),
        "stop_reason": stop["reason"],
        "performance_pass": score == 0,
        "score": score,
        "metrics": metrics,
        "failure_reasons": hard_failures
        + task_failures
        + (
            ["performance_threshold_not_met"]
            if score > 0 and not hard_failures and not task_failures
            else []
        ),
    }


def judge_packet(
    freeze: Mapping[str, Any], packet: Mapping[str, Any]
) -> dict[str, Any]:
    """Validate identities and recompute all trial results from a complete packet."""
    freeze = deepcopy(dict(_mapping(freeze, "freeze")))
    packet = deepcopy(dict(_mapping(packet, "packet")))
    if (
        freeze.get("freeze_version") != STRICT_FREEZE_VERSION
        or packet.get("packet_version") != STRICT_PACKET_VERSION
    ):
        raise ValueError("historical_evaluation_read_only")
    _signed(freeze, "freeze_fingerprint")
    _signed(packet, "packet_fingerprint")
    _public(packet)
    for key in ("session_id", "task_fingerprint", "freeze_fingerprint"):
        if not freeze.get(key) or packet.get(key) != freeze[key]:
            raise ValueError(f"evaluation_{key}_mismatch")
    if packet.get("evidence_fingerprints") != freeze.get("evidence_fingerprints"):
        raise ValueError("evaluation_evidence_binding_mismatch")
    runtime = _mapping(freeze.get("runtime_contract"), "runtime_contract")
    binding = _mapping(
        runtime.get("provider_bindings", {}).get("evaluation"),
        "evaluation_provider_binding",
    )
    for key in ("provider_id", "provider_version"):
        if not binding.get(key) or packet.get(key) != binding[key]:
            raise ValueError("evaluation_provider_mismatch")
    criteria = _mapping(freeze.get("evaluation_contract"), "evaluation_contract")
    split = packet.get("evaluation_split")
    if split not in {"development", "fresh_confirmation"}:
        raise ValueError("evaluation_split_invalid")
    partitions = _mapping(criteria.get("trial_manifest"), "trial_manifest")
    for partition in ("development", "fresh_confirmation"):
        if (
            not isinstance(partitions.get(partition), list)
            or not 1 <= len(partitions[partition]) <= 10_000
        ):
            raise ValueError("trial_partition_missing")
        if not all(isinstance(row, Mapping) for row in partitions[partition]):
            raise ValueError("trial_partition_invalid")
        rows = partitions[partition]
        if any(
            not isinstance(row.get("trial_id"), str)
            or not row["trial_id"]
            or not isinstance(row.get("scenario_id"), str)
            or not row["scenario_id"]
            or isinstance(row.get("seed"), bool)
            or not isinstance(row.get("seed"), int)
            for row in rows
        ):
            raise ValueError("frozen_trial_manifest_invalid")
        if len({row["trial_id"] for row in rows}) != len(rows) or len(
            {(row["scenario_id"], row["seed"]) for row in rows}
        ) != len(rows):
            raise ValueError("trial_partition_duplicate")
    development = {
        (row.get("scenario_id"), row.get("seed")) for row in partitions["development"]
    }
    confirmation = {
        (row.get("scenario_id"), row.get("seed"))
        for row in partitions["fresh_confirmation"]
    }
    if development & confirmation:
        raise ValueError("trial_partition_overlap")
    manifest = partitions.get(split)
    trials = packet.get("trials")
    if (
        not isinstance(manifest, list)
        or not manifest
        or not isinstance(trials, list)
        or len(trials) != len(manifest)
    ):
        raise ValueError("evaluation_trial_count_mismatch")
    identities = [
        (row.get("trial_id"), row.get("scenario_id"), row.get("seed"))
        for row in manifest
    ]
    if len({row[0] for row in identities}) != len(identities) or any(
        not row[0]
        or not row[1]
        or isinstance(row[2], bool)
        or not isinstance(row[2], int)
        for row in identities
    ):
        raise ValueError("frozen_trial_manifest_invalid")
    if (
        not all(isinstance(row, Mapping) for row in trials)
        or [
            (row.get("trial_id"), row.get("scenario_id"), row.get("seed"))
            for row in trials
        ]
        != identities
    ):
        raise ValueError("evaluation_trial_identity_mismatch")
    judged = [
        _judge_trial(trial, freeze, scenario)
        for trial, scenario in zip(trials, manifest, strict=True)
    ]
    failures = [trial["trial_id"] for trial in judged if not trial["stable"]]
    invalid_evidence = [
        trial["trial_id"] for trial in judged if not trial["evidence_valid"]
    ]
    success_count = sum(trial["performance_pass"] for trial in judged)
    lower = wilson_lower_bound(success_count, len(manifest))
    minimum_rate = _criterion(criteria, "perturbed_success_rate_min")
    if minimum_rate is not None and minimum_rate > 1:
        raise ValueError("success_rate_criterion_invalid")
    rate_passed = minimum_rate is None or lower >= minimum_rate
    worst_score = max(trial["score"] for trial in judged)
    worst_limit = _criterion(criteria, "worst_trial_violation_max")
    worst_passed = worst_limit is None or worst_score <= worst_limit
    performance_passed = (
        success_count == len(manifest) if minimum_rate is None else rate_passed
    )
    passed = (
        not failures and not invalid_evidence and performance_passed and worst_passed
    )
    score = max(
        worst_score,
        _violation(lower, minimum_rate, minimum=True)
        if minimum_rate is not None
        else 0.0,
        _violation(worst_score, worst_limit) if worst_limit is not None else 0.0,
    )
    result = {
        "status": "performance_met" if passed else "performance_not_met",
        "evaluation_split": split,
        "stability_gate": {
            "passed": not failures,
            "failed_trials": failures,
            "basis": "public_finite_horizon_safety_not_asymptotic_proof",
        },
        "evidence_gate": {
            "passed": not invalid_evidence,
            "failed_trials": invalid_evidence,
            "basis": "event_and_phase_evidence_bound_to_public_samples",
        },
        "performance_gate": {
            "evaluated_after_stability": not failures and not invalid_evidence,
            "passed": passed,
            "success_count": success_count,
            "success_rate": success_count / len(manifest),
            "success_rate_min": minimum_rate,
            "success_rate_passed": rate_passed,
            "success_rate_basis": "wilson_lower_bound_95",
            "aggregation_rule": "all_trials"
            if minimum_rate is None
            else "wilson_lower_bound_95",
            "worst_trial_violation_max": worst_limit,
            "worst_trial_passed": worst_passed,
        },
        "trial_count": len(manifest),
        "success_count": success_count,
        "success_rate": success_count / len(manifest),
        "wilson_lower_bound_95": lower,
        "score": score,
        "objective_direction": "minimize",
        "worst_trial_id": max(judged, key=lambda trial: trial["score"])["trial_id"],
        "trials": judged,
        "failure_reasons": sorted(
            {reason for trial in judged for reason in trial["failure_reasons"]}
            | ({"success_rate_below_frozen_requirement"} if not rate_passed else set())
            | (
                {"worst_trial_violation_above_frozen_requirement"}
                if not worst_passed
                else set()
            )
        ),
        "packet_fingerprint": packet["packet_fingerprint"],
        "freeze_fingerprint": freeze["freeze_fingerprint"],
        "provider_id": packet["provider_id"],
        "provider_version": packet["provider_version"],
        "judge_version": JUDGE_VERSION,
        "private_truth_used": False,
    }
    result["judge_fingerprint"] = fingerprint(result)
    return result
