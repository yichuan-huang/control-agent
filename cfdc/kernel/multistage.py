"""Small declarative multi-stage runtime contract.

The runtime consumes this plan; it never evaluates expressions supplied by an
LLM.  Conditions are named predicates implemented by the numerical backend or
reported as public observations by a provider.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from itertools import pairwise
from typing import Any

from .contracts import MULTISTAGE_VERSION, TaskContract, fingerprint

_ALLOWED_HANDOFF_POLICIES = {"forward_only", "forward_with_safe_recovery"}


@dataclass(frozen=True)
class PhaseContract:
    phase_id: str
    objective: str
    entry_condition: str
    exit_condition: str
    valid_region: str
    timeout_s: float
    handoff_policy: str = "forward_only"
    controller: Mapping[str, Any] | None = None
    required_feature_ids: tuple[str, ...] = ()
    phase_version: str = MULTISTAGE_VERSION

    def __post_init__(self) -> None:
        if not self.phase_id.strip() or not self.objective.strip():
            raise ValueError("phase_identity_required")
        if not self.entry_condition.strip() or not self.exit_condition.strip():
            raise ValueError("phase_conditions_required")
        if not self.valid_region.strip():
            raise ValueError("phase_valid_region_required")
        if not math.isfinite(float(self.timeout_s)) or float(self.timeout_s) <= 0:
            raise ValueError("phase_timeout_invalid")
        if self.handoff_policy not in _ALLOWED_HANDOFF_POLICIES:
            raise ValueError("phase_handoff_policy_invalid")
        if self.phase_version != MULTISTAGE_VERSION:
            raise ValueError("phase_contract_version_mismatch")
        if len(set(self.required_feature_ids)) != len(self.required_feature_ids):
            raise ValueError("duplicate_phase_feature_ids")

    def to_dict(self) -> dict[str, Any]:
        return {
            "phase_version": self.phase_version,
            "phase_id": self.phase_id,
            "objective": self.objective,
            "entry_condition": self.entry_condition,
            "exit_condition": self.exit_condition,
            "valid_region": self.valid_region,
            "timeout_s": float(self.timeout_s),
            "handoff_policy": self.handoff_policy,
            "controller": dict(self.controller)
            if self.controller is not None
            else None,
            "required_feature_ids": list(self.required_feature_ids),
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> PhaseContract:
        raw = dict(value)
        return cls(
            phase_id=str(raw.get("phase_id") or raw.get("id") or "").strip(),
            objective=str(raw.get("objective") or raw.get("goal") or "").strip(),
            entry_condition=str(
                raw.get("entry_condition") or raw.get("entry") or ""
            ).strip(),
            exit_condition=str(
                raw.get("exit_condition") or raw.get("exit") or ""
            ).strip(),
            valid_region=str(
                raw.get("valid_region") or raw.get("validity") or ""
            ).strip(),
            timeout_s=float(raw.get("timeout_s", raw.get("max_duration_s", 0))),
            handoff_policy=str(raw.get("handoff_policy") or "forward_only"),
            controller=dict(raw["controller"])
            if raw.get("controller") is not None
            else None,
            required_feature_ids=tuple(
                str(item) for item in raw.get("required_feature_ids", ()) or ()
            ),
            phase_version=str(raw.get("phase_version") or MULTISTAGE_VERSION),
        )

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> PhaseContract:
        return cls.from_mapping(value)

    @property
    def id(self) -> str:
        return self.phase_id

    @property
    def goal(self) -> str:
        return self.objective

    @property
    def entry(self) -> str:
        return self.entry_condition

    @property
    def exit(self) -> str:
        return self.exit_condition

    @property
    def validity(self) -> str:
        return self.valid_region

    @property
    def max_duration_s(self) -> float:
        return self.timeout_s


@dataclass(frozen=True)
class MultiStagePlan:
    task_fingerprint: str
    route_id: str
    phases: tuple[PhaseContract, ...]
    plan_version: str = MULTISTAGE_VERSION
    plan_fingerprint: str | None = None

    def __post_init__(self) -> None:
        if self.plan_version != MULTISTAGE_VERSION:
            raise ValueError("multistage_plan_version_mismatch")
        if not self.phases or len(self.phases) > 5:
            raise ValueError("multistage_plan_requires_one_to_five_phases")
        ids = [phase.phase_id for phase in self.phases]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate_phase_id")
        if not self.task_fingerprint or not self.route_id:
            raise ValueError("multistage_binding_required")

    @property
    def fingerprint(self) -> str:
        return fingerprint(self.to_dict(include_fingerprint=False))

    def to_dict(self, *, include_fingerprint: bool = True) -> dict[str, Any]:
        value = {
            "plan_version": self.plan_version,
            "task_fingerprint": self.task_fingerprint,
            "route_id": self.route_id,
            "phases": [phase.to_dict() for phase in self.phases],
        }
        if include_fingerprint:
            value["plan_fingerprint"] = self.fingerprint
        return value

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> MultiStagePlan:
        raw = dict(value)
        supplied = raw.pop("plan_fingerprint", None)
        plan = cls(
            task_fingerprint=str(raw.get("task_fingerprint") or ""),
            route_id=str(raw.get("route_id") or raw.get("route") or ""),
            phases=tuple(
                PhaseContract.from_mapping(item) for item in raw.get("phases", ()) or ()
            ),
            plan_version=str(raw.get("plan_version") or MULTISTAGE_VERSION),
        )
        if supplied is not None and str(supplied) != plan.fingerprint:
            raise ValueError("multistage_plan_fingerprint_mismatch")
        return plan

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> MultiStagePlan:
        return cls.from_mapping(value)

    @property
    def route(self) -> str:
        return self.route_id

    @property
    def phase_order(self) -> tuple[str, ...]:
        return tuple(item.phase_id for item in self.phases)

    @property
    def handoff_ids(self) -> tuple[str, ...]:
        return tuple(
            f"{source}__to__{target}" for source, target in pairwise(self.phase_order)
        )


def compile_phase_plan(
    task: TaskContract,
    route: Mapping[str, Any],
    *,
    controller: Mapping[str, Any] | None = None,
    phases: Sequence[Mapping[str, Any]] | None = None,
) -> MultiStagePlan:
    """Compile a task into one or two named phases.

    Explicit phase plans are accepted only as declarative condition names.  If
    the caller omits them, transition and disturbance tasks receive the
    registered ``transition`` → ``hold`` topology; local hold receives one
    phase.
    """

    if phases is None and task.phase_schedule:
        declared = (
            task.phase_schedule.get("phases")
            if isinstance(task.phase_schedule, Mapping)
            else None
        )
        if isinstance(declared, Sequence) and not isinstance(declared, (str, bytes)):
            phases = tuple(dict(item) for item in declared if isinstance(item, Mapping))
        elif isinstance(task.phase_schedule, Mapping) and any(
            key in task.phase_schedule
            for key in (
                "phase_id",
                "id",
                "objective",
                "goal",
                "entry_condition",
                "entry",
            )
        ):
            phases = (dict(task.phase_schedule),)

    if phases is None:
        if task.task_type == "local_setpoint_hold":
            phase_values = [
                {
                    "phase_id": "hold",
                    "objective": "hold the requested reference",
                    "entry_condition": "task_start",
                    "exit_condition": "success_hold",
                    "valid_region": task.goal_region
                    or task.operating_region
                    or "declared_operating_region",
                    "timeout_s": float(task.budgets.get("elapsed_time_s", 7200.0)),
                }
            ]
        elif task.task_type == "disturbance_recovery_to_hold":
            phase_values = [
                {
                    "phase_id": "recovery",
                    "objective": "recover after the declared disturbance",
                    "entry_condition": "disturbance_event_detected",
                    "exit_condition": "recovery_target_reached",
                    "valid_region": task.disturbance_hold_region
                    or task.goal_region
                    or task.operating_region
                    or "declared_operating_region",
                    "timeout_s": float(task.budgets.get("elapsed_time_s", 7200.0))
                    / 2.0,
                    "handoff_policy": "forward_with_safe_recovery",
                },
                {
                    "phase_id": "hold",
                    "objective": "hold after disturbance recovery",
                    "entry_condition": "recovery_target_reached",
                    "exit_condition": "success_hold",
                    "valid_region": task.disturbance_hold_region
                    or task.goal_region
                    or task.operating_region
                    or "declared_operating_region",
                    "timeout_s": float(task.budgets.get("elapsed_time_s", 7200.0))
                    / 2.0,
                },
            ]
        else:
            transition_targets = list(task.intermediate_targets)
            if task.reference is not None:
                transition_targets.append(float(task.reference))
            # A numeric public schedule creates one transition phase per
            # checkpoint, followed by exactly one final hold phase.  Without
            # numeric targets the compact two-phase topology is retained.
            if not transition_targets:
                transition_targets = [None]
            phase_values = []
            for index, target in enumerate(transition_targets, 1):
                final_transition = index == len(transition_targets)
                phase_values.append(
                    {
                        "phase_id": (
                            "transition"
                            if len(transition_targets) == 1
                            else (
                                "transition_to_goal"
                                if final_transition
                                else f"transition_checkpoint_{index:02d}"
                            )
                        ),
                        "objective": (
                            "move from the declared initial region"
                            if target is None
                            else f"move to public checkpoint {target:g}"
                        ),
                        "entry_condition": "task_start"
                        if index == 1
                        else f"transition_checkpoint_{index - 1:02d}_reached",
                        "exit_condition": (
                            "transition_target_reached"
                            if len(transition_targets) == 1 or final_transition
                            else f"transition_checkpoint_{index:02d}_reached"
                        ),
                        "valid_region": task.initial_region
                        or task.operating_region
                        or "declared_operating_region",
                        "timeout_s": float(task.budgets.get("elapsed_time_s", 7200.0))
                        / (len(transition_targets) + 1),
                        "handoff_policy": "forward_with_safe_recovery",
                    }
                )
            phase_values.append(
                {
                    "phase_id": "hold" if len(transition_targets) == 1 else "hold_goal",
                    "objective": "hold the requested goal region",
                    "entry_condition": "transition_target_reached",
                    "exit_condition": "success_hold",
                    "valid_region": task.goal_region
                    or task.operating_region
                    or "declared_operating_region",
                    "timeout_s": float(task.budgets.get("elapsed_time_s", 7200.0))
                    / (len(transition_targets) + 1),
                }
            )
    else:
        phase_values = [dict(item) for item in phases]
        if task.task_type == "local_setpoint_hold" and len(phase_values) != 1:
            raise ValueError("local_setpoint_hold_requires_single_phase")
        if not 2 <= len(phase_values) <= 5 and task.task_type != "local_setpoint_hold":
            raise ValueError("multistage_tasks_require_two_to_five_phases")
        if not phase_values:
            raise ValueError("phase_plan_empty")

    result = []
    for item in phase_values:
        result.append(
            PhaseContract.from_mapping(
                {
                    **item,
                    "controller": (
                        item.get("controller")
                        if item.get("controller") is not None
                        else (dict(controller) if controller is not None else None)
                    ),
                }
            )
        )
    for previous, current in pairwise(result):
        if current.entry_condition != previous.exit_condition:
            raise ValueError("phase_handoff_condition_mismatch")
    if (
        task.required_phase_count_min is not None
        and len(result) != task.required_phase_count_min
    ):
        raise ValueError("phase_count_does_not_match_task_contract")
    if (
        task.verified_handoff_count_min is not None
        and len(result) - 1 != task.verified_handoff_count_min
    ):
        raise ValueError("handoff_count_does_not_match_task_contract")
    elapsed_budget = float(task.budgets.get("elapsed_time_s", 7200.0))
    if sum(phase.timeout_s for phase in result) > elapsed_budget + 1e-9:
        raise ValueError("phase_time_budget_exceeded")
    return MultiStagePlan(
        task_fingerprint=task.fingerprint,
        route_id=str(route.get("route_id") or ""),
        phases=tuple(result),
    )


def validate_handoff(
    plan: MultiStagePlan, observations: Mapping[str, Any]
) -> dict[str, Any]:
    """Validate public phase observations without executing arbitrary code."""

    reached: list[str] = []
    failures: list[str] = []
    for phase in plan.phases:
        observation = observations.get(phase.phase_id)
        if not isinstance(observation, Mapping):
            failures.append(f"missing_observation:{phase.phase_id}")
            continue
        if (
            observation.get("safety_failure") is True
            or observation.get("stopped_on_limit") is True
            or observation.get("hard_failure") is True
            or observation.get("safety_violation") is True
            or observation.get("constraint_violation") is True
        ):
            failures.append(f"safety_failure:{phase.phase_id}")
            continue
        entry_passed = observation.get(
            "entry_condition_met", observation.get("entry_passed")
        )
        exit_passed = observation.get(
            "exit_condition_met", observation.get("exit_passed")
        )
        success = observation.get("success")
        # The archived progression contract used ``entry_passed`` and
        # ``exit_passed`` as the complete public handoff observation and did
        # not emit a separate ``success`` flag.  Preserve that wire format at
        # this compatibility boundary while keeping the canonical format
        # strict: a canonical observation must explicitly provide ``success``
        # and an observation with no gate fields is still blocked.
        if (
            success is None
            and "entry_condition_met" not in observation
            and "exit_condition_met" not in observation
            and "entry_passed" in observation
            and "exit_passed" in observation
        ):
            success = True
        if any(value is None for value in (entry_passed, exit_passed, success)):
            failures.append(f"missing_gate:{phase.phase_id}")
            continue
        if any(
            not isinstance(value, bool)
            for value in (entry_passed, exit_passed, success)
        ):
            failures.append(f"invalid_gate:{phase.phase_id}")
            continue
        if entry_passed is False or exit_passed is False or success is False:
            failures.append(f"condition_failed:{phase.phase_id}")
            continue
        reached.append(phase.phase_id)
    return {
        "status": "passed"
        if not failures and len(reached) == len(plan.phases)
        else "blocked",
        "phase_ids_reached": reached,
        "failures": failures,
        "plan_fingerprint": plan.fingerprint,
    }


__all__ = ["MultiStagePlan", "PhaseContract", "compile_phase_plan", "validate_handoff"]
