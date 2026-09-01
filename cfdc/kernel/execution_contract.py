"""Frozen execution requests intentionally exclude performance acceptance rules."""

from __future__ import annotations

import math
from collections.abc import Mapping
from copy import deepcopy
from typing import Any

from .contracts import fingerprint

EXECUTION_VERSION = "cfdc-execution/v1"


def _positive(value: Any, label: str) -> float:
    if isinstance(value, bool):
        raise TypeError(f"execution_{label}_invalid")
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise ValueError(f"execution_{label}_invalid")
    return number


def execution_request(freeze: Mapping[str, Any], split: str) -> dict[str, Any]:
    """Compile the execution-only subset; never hand the provider a judge API.

    The complete freeze stays with the Kernel. This request includes reference
    and phase-exit predicates because they drive commands; error/overshoot/IAE
    acceptance thresholds and qualification models are deliberately absent.
    """
    raw = deepcopy(dict(freeze))
    digest = raw.pop("freeze_fingerprint", None)
    if not digest or fingerprint(raw) != digest:
        raise ValueError("execution_freeze_fingerprint_mismatch")
    if freeze.get("freeze_version") != "cfdc-freeze/v2.0":
        raise ValueError("historical_execution_not_allowed")
    if split not in {"development", "fresh_confirmation"}:
        raise ValueError("execution_split_invalid")
    runtime = dict(freeze["runtime_contract"])
    evaluation = dict(freeze["evaluation_contract"])
    trials = deepcopy(evaluation.get("trial_manifest", {}).get(split))
    if not isinstance(trials, list) or not trials:
        raise ValueError("execution_frozen_trials_required")
    dt = _positive(evaluation.get("sample_time_s"), "sample_time")
    horizon = _positive(evaluation.get("horizon_s"), "horizon")
    if horizon <= dt or math.ceil(horizon / dt) > 1_000_000:
        raise ValueError("execution_sample_budget_invalid")
    measured = list(
        runtime.get("measured_signals") or freeze["controller"]["measured_signals"]
    )
    tracked = list(runtime["tracked_signals"])
    inputs = list(runtime["control_inputs"])
    bounds = deepcopy(runtime["input_bounds"])
    references = deepcopy(evaluation["references"])
    if (
        not tracked
        or not set(tracked) <= set(measured)
        or set(bounds) != set(inputs)
        or set(references) != set(tracked)
    ):
        raise ValueError("execution_signal_map_mismatch")
    for name, pair in bounds.items():
        if (
            len(pair) != 2
            or not all(math.isfinite(float(value)) for value in pair)
            or float(pair[0]) >= float(pair[1])
        ):
            raise ValueError(f"execution_input_bounds_invalid:{name}")
    for scenario in trials:
        disturbance = scenario.get("disturbance", evaluation.get("disturbance"))
        if disturbance:
            start = float(disturbance["time_s"])
            duration = _positive(disturbance["duration_s"], "disturbance_duration")
            if (
                disturbance["channel"] not in inputs
                or not 0 <= start < start + duration < horizon
                or not math.isfinite(float(disturbance["amplitude"]))
            ):
                raise ValueError("execution_disturbance_invalid")
    return {
        "request_version": EXECUTION_VERSION,
        "session_id": freeze["session_id"],
        "task_fingerprint": freeze["task_fingerprint"],
        "freeze_fingerprint": digest,
        "controller": deepcopy(freeze["controller"]),
        "sample_time_s": dt,
        "horizon_s": horizon,
        "measured_signals": measured,
        "tracked_signals": tracked,
        "control_inputs": inputs,
        "input_bounds": bounds,
        "output_bounds": deepcopy(runtime.get("output_bounds", {})),
        "state_bounds": deepcopy(runtime.get("state_bounds", {})),
        "controller_state_bounds": deepcopy(runtime.get("controller_state_bounds", {})),
        "state_stop": runtime.get("state_stop"),
        "references": references,
        "trials": trials,
        "phases": deepcopy(evaluation.get("phases", [])),
        "disturbance": deepcopy(evaluation.get("disturbance")),
        "evaluation_split": split,
    }


def freeze_trial_manifest(
    repeats: int, *, seed: int = 7301, scenarios: list[Mapping[str, Any]] | None = None
) -> dict[str, list[dict[str, Any]]]:
    """Preregister independent realizations without consulting any outcome."""
    if (
        isinstance(repeats, bool)
        or not isinstance(repeats, int)
        or not 1 <= repeats <= 10_000
    ):
        raise ValueError("evaluation_repeat_count_invalid")
    scenarios = scenarios or [{"scenario_id": "bounded_perturbation"}]
    if any(not scenario.get("scenario_id") for scenario in scenarios):
        raise ValueError("evaluation_scenario_id_required")
    manifest = {}
    for split, offset in (("development", 0), ("fresh_confirmation", 1_000_000)):
        manifest[split] = [
            {
                **deepcopy(dict(scenarios[index % len(scenarios)])),
                "trial_id": f"{split}-{index + 1:04d}",
                "seed": seed + offset + index,
            }
            for index in range(repeats)
        ]
    return manifest
