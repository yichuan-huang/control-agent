"""Task-type compatibility helpers migrated from the v3 workbench.

The service uses :class:`~cfdc.kernel.contracts.TaskContract` as its single
typed boundary.  These small helpers keep the archive's public validation and
outcome vocabulary available to callers without importing anything from the
archive at runtime.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from itertools import pairwise
from typing import Any

from .contracts import (
    P1_1_TASK_SEMANTICS_VERSION,
    SUPPORTED_TASK_TYPES,
    TASK_SUCCESS_METRICS,
    UNSUPPORTED_TASK_TYPES,
    TaskContract,
)


class TaskTypeContractError(ValueError):
    """Structured deterministic task-contract failure."""

    def __init__(
        self,
        *,
        code: str,
        task_type: str,
        missing_fields: list[str] | None = None,
        conflict_fields: list[str] | None = None,
    ) -> None:
        self.audit = {
            "status": "task_contract_gap",
            "error_code": code,
            "task_type": task_type,
            "missing_fields": list(missing_fields or []),
            "conflict_fields": list(conflict_fields or []),
            "experiment_compiled": False,
            "authorization": "none",
        }
        super().__init__(
            f"{code}: task_type={task_type}; "
            f"missing={self.audit['missing_fields']}; conflicts={self.audit['conflict_fields']}"
        )


def infer_task_type(task: Mapping[str, Any]) -> tuple[str, str]:
    """Infer a supported task type only from explicit public text."""

    if not isinstance(task, Mapping):
        raise TypeError("task_contract_mapping_required")
    declared = task.get("task_type")
    if declared is not None:
        return str(declared), "explicit_task_contract"
    visible = " ".join(
        str(task.get(key) or "").casefold()
        for key in ("description", "natural_language_description", "objective")
    )
    markers = {
        "trajectory_tracking": ("trajectory tracking", "track a trajectory", "轨迹跟踪", "跟踪轨迹"),
        "periodic_operation": ("periodic operation", "periodic orbit", "limit cycle", "周期运行", "周期轨道"),
        "constraint_optimization": ("constraint optimization", "constrained optimization", "economic optimum", "约束优化", "经济最优"),
        "online_adaptation": ("online adaptation", "online adaptive", "adapt parameters online", "在线适应", "在线自适应"),
    }
    for task_type, candidates in markers.items():
        if any(marker in visible for marker in candidates):
            return task_type, "conservative_public_text_detection"
    return "local_setpoint_hold", "legacy_single_stage_migration"


def validate_task_type_contract(task: Mapping[str, Any]) -> dict[str, Any]:
    """Validate task semantics and return an auditable metric declaration."""

    task_type, source = infer_task_type(task)
    try:
        contract = TaskContract.from_user_input(task)
    except ValueError as exc:
        code = str(exc).split(":", 1)[0]
        if task_type in UNSUPPORTED_TASK_TYPES:
            code = "unsupported_task_type"
        raise TaskTypeContractError(code=code, task_type=task_type) from exc
    requirements = contract.success_requirements
    if source == "legacy_single_stage_migration" and not requirements:
        return {
            "task_type": contract.task_type,
            "source": source,
            "success_metric_ids": [
                "final_abs_error", "overshoot", "settling_time_s", "perturbed_success_rate",
            ],
            "criteria_status": "not_pre_registered",
        }
    if contract.task_semantics_version == P1_1_TASK_SEMANTICS_VERSION:
        criteria_status = "p1_1_explicit_task_success_requirements"
        metric_ids = list(TASK_SUCCESS_METRICS[contract.task_type])
    elif source == "explicit_task_contract" and requirements:
        criteria_status = "p1_explicit_compatibility"
        metric_ids = [
            "final_abs_error", "overshoot", "settling_time_s", "perturbed_success_rate",
        ]
    elif requirements:
        criteria_status = "legacy_performance_requirements"
        metric_ids = [
            "final_abs_error", "overshoot", "settling_time_s", "perturbed_success_rate",
        ]
    else:
        criteria_status = "not_pre_registered"
        metric_ids = list(TASK_SUCCESS_METRICS[contract.task_type])
    return {
        "task_type": contract.task_type,
        "source": source,
        "success_metric_ids": metric_ids,
        "criteria_status": criteria_status,
    }


def task_success_requirements(task: Mapping[str, Any]) -> Mapping[str, Any] | None:
    contract = TaskContract.from_user_input(task)
    return contract.success_requirements or None


def disturbance_event_fingerprint(task: Mapping[str, Any]) -> str:
    contract = TaskContract.from_user_input(task)
    if contract.task_type != "disturbance_recovery_to_hold":
        raise TaskTypeContractError(
            code="disturbance_fingerprint_requested_for_other_task",
            task_type=contract.task_type,
        )
    return hashlib.sha256(
        json.dumps(contract.disturbance_contract, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def transition_outcome_binding(task_coverage: Mapping[str, Any]) -> dict[str, Any]:
    phases = task_coverage.get("phases", ())
    phase_ids = [str(item.get("id", item.get("phase_id", ""))) for item in phases if isinstance(item, Mapping)]
    if len(phase_ids) < 2 or len(phase_ids) != len(set(phase_ids)) or any(not item for item in phase_ids):
        raise ValueError("transition outcome binding requires at least two unique phase ids")
    handoffs = task_coverage.get("handoffs")
    if handoffs is None:
        handoffs = [
            {"id": f"{source}__to__{target}", "source_phase_id": source, "target_phase_id": target}
            for source, target in pairwise(phase_ids)
        ]
    pairs = [(str(item.get("source_phase_id")), str(item.get("target_phase_id"))) for item in handoffs]
    if pairs != list(pairwise(phase_ids)):
        raise ValueError("transition handoff identities do not match adjacent compiled phases")
    handoff_ids = [str(item.get("id", "")) for item in handoffs]
    if any(not item for item in handoff_ids) or len(handoff_ids) != len(set(handoff_ids)):
        raise ValueError("transition handoff ids must be unique")
    return {"required_phase_ids": phase_ids, "required_handoff_ids": handoff_ids, "goal_phase_id": phase_ids[-1]}


def evaluate_nominal_task_outcome(
    task: Mapping[str, Any],
    outcome: Mapping[str, Any],
    *,
    transition_binding: Mapping[str, Any] | None = None,
) -> bool:
    """Apply task-specific public criteria; never inspect hidden simulator state."""

    contract = TaskContract.from_user_input(task)
    criteria = contract.success_requirements
    if not criteria:
        raise TaskTypeContractError(code="missing_task_success_requirements", task_type=contract.task_type)
    if outcome.get("stopped_on_limit"):
        return False
    if contract.task_type == "local_setpoint_hold":
        required_hold = criteria.get("hold_duration_min_s")
        return bool(
            float(outcome.get("final_abs_error", float("inf"))) <= float(criteria.get("final_abs_error_max", float("inf")))
            and float(outcome.get("overshoot", float("inf"))) <= float(criteria.get("overshoot_max", float("inf")))
            and outcome.get("settling_time_s") is not None
            and float(outcome["settling_time_s"]) <= float(criteria.get("settling_time_max_s", float("inf")))
            and (required_hold is None or float(outcome.get("hold_duration_s", -1)) >= float(required_hold))
        )
    if contract.task_type == "transition_then_hold":
        if transition_binding is None:
            raise TaskTypeContractError(code="transition_identity_binding_missing", task_type=contract.task_type)
        required_phases = set(transition_binding["required_phase_ids"])
        required_handoffs = set(transition_binding["required_handoff_ids"])
        phase_ids = outcome.get("completed_phase_ids")
        handoff_ids = outcome.get("verified_handoff_ids")
        if not isinstance(phase_ids, list) or not isinstance(handoff_ids, list):
            raise TaskTypeContractError(code="transition_outcome_identity_missing", task_type=contract.task_type)
        identities = (
            len(phase_ids) == len(set(phase_ids))
            and len(handoff_ids) == len(set(handoff_ids))
            and set(phase_ids) == required_phases
            and set(handoff_ids) == required_handoffs
            and int(outcome.get("completed_phase_count", -1)) == len(phase_ids)
            and int(outcome.get("verified_handoff_count", -1)) == len(handoff_ids)
        )
        return bool(
            identities
            and (outcome.get("entered_goal_region") is True or not criteria.get("goal_region_entry_required", True))
            and int(outcome.get("completed_phase_count", 0)) >= int(criteria.get("required_phase_count_min", 0))
            and int(outcome.get("verified_handoff_count", 0)) >= int(criteria.get("verified_handoff_count_min", 0))
            and float(outcome.get("final_hold_duration_s", -1)) >= float(criteria.get("final_hold_duration_min_s", float("inf")))
        )
    expected = disturbance_event_fingerprint(task)
    return bool(
        outcome.get("disturbance_executed") is True
        and outcome.get("disturbance_event_fingerprint") == expected
        and outcome.get("recovered_to_hold") is True
        and outcome.get("recovery_time_s") is not None
        and float(outcome["recovery_time_s"]) <= float(criteria.get("recovery_time_max_s", float("inf")))
        and float(outcome.get("post_recovery_hold_duration_s", -1)) >= float(criteria.get("post_recovery_hold_duration_min_s", float("inf")))
        and float(outcome.get("final_abs_error", float("inf"))) <= float(criteria.get("recovery_abs_error_max", float("inf")))
    )


__all__ = [
    "P1_1_TASK_SEMANTICS_VERSION",
    "SUPPORTED_TASK_TYPES",
    "TASK_SUCCESS_METRICS",
    "UNSUPPORTED_TASK_TYPES",
    "TaskContract",
    "TaskTypeContractError",
    "disturbance_event_fingerprint",
    "evaluate_nominal_task_outcome",
    "infer_task_type",
    "task_success_requirements",
    "transition_outcome_binding",
    "validate_task_type_contract",
]
