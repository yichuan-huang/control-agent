"""Public, versioned contracts for the evidence-driven CFDC workflow.

The kernel contracts deliberately contain public task and evidence metadata only.
They do not contain hidden simulator parameters or executable expressions.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from itertools import pairwise
from typing import Any, ClassVar

TASK_CONTRACT_VERSION = "cfdc-task/v1.2"
EVIDENCE_SESSION_VERSION = "cfdc-session/v2.0"
READABLE_EVIDENCE_SESSION_VERSIONS = frozenset(
    {"cfdc-session/v1.0", EVIDENCE_SESSION_VERSION}
)
DIAGNOSTIC_LEDGER_VERSION = "cfdc-diagnostics/v2.0"
FREEZE_VERSION = "cfdc-freeze/v1.0"
PACKET_VERSION = "cfdc-evaluation-packet/v1.0"
CONTROLLER_IR_VERSION = "cfdc-controller-ir/v1.0"
MULTISTAGE_VERSION = "cfdc-multistage/v1.0"
TUNING_CONTRACT_VERSION = "cfdc-tuning/v1.0"
PROTOCOL_VERSION = "cfdc-protocol/v1"
OPERATOR_HANDOFF_VERSION = "cfdc-operator-handoff/v1"
UPLOAD_AUDIT_VERSION = "cfdc-upload/v1"
FEATURE_ARTIFACT_VERSION = "cfdc-features/v1"
QUALIFICATION_VERSION = "cfdc-qualification/v1"
IMPORT_REPORT_VERSION = "cfdc-import/v1"
P1_1_TASK_SEMANTICS_VERSION = "1.1.0"

SUPPORTED_TASK_TYPES = (
    "local_setpoint_hold",
    "transition_then_hold",
    "disturbance_recovery_to_hold",
)
UNSUPPORTED_TASK_TYPES = (
    "trajectory_tracking",
    "periodic_operation",
    "constraint_optimization",
    "online_adaptation",
)

TASK_SUCCESS_METRICS: dict[str, tuple[str, ...]] = {
    "local_setpoint_hold": (
        "final_abs_error",
        "overshoot",
        "settling_time_s",
        "hold_duration_s",
        "perturbed_success_rate",
    ),
    "transition_then_hold": (
        "completed_phase_count",
        "completed_phase_ids",
        "verified_handoff_count",
        "verified_handoff_ids",
        "entered_goal_region",
        "goal_region_entry_phase_id",
        "final_hold_duration_s",
        "perturbed_success_rate",
    ),
    "disturbance_recovery_to_hold": (
        "disturbance_executed",
        "disturbance_event_fingerprint",
        "recovered_to_hold",
        "recovery_time_s",
        "post_recovery_hold_duration_s",
        "final_abs_error",
        "perturbed_success_rate",
    ),
}

DIAGNOSTIC_IDS = (
    "open_loop_stability",
    "nonminimum_phase",
    "significant_delay",
    "relative_degree",
    "sensing_actuation_adequacy",
    "nonlinearity_strength",
    "coupling_underactuation",
    "uncertainty_variation",
)

_UNSUPPORTED_TASK_MARKERS: dict[str, tuple[str, ...]] = {
    "trajectory_tracking": (
        "trajectory tracking",
        "track a trajectory",
        "轨迹跟踪",
        "跟踪轨迹",
    ),
    "periodic_operation": (
        "periodic operation",
        "periodic orbit",
        "limit cycle",
        "周期运行",
        "周期轨道",
    ),
    "constraint_optimization": (
        "constraint optimization",
        "constrained optimization",
        "economic optimum",
        "约束优化",
        "经济最优",
    ),
    "online_adaptation": (
        "online adaptation",
        "online adaptive",
        "adapt parameters online",
        "在线适应",
        "在线自适应",
    ),
}


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def fingerprint(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _clean_tuple(values: Any) -> tuple[str, ...]:
    if values is None:
        return ()
    if isinstance(values, str):
        values = (values,)
    cleaned = tuple(str(value).strip() for value in values if str(value).strip())
    if len(cleaned) != len(set(cleaned)):
        raise ValueError("duplicate values are not allowed")
    return cleaned


@dataclass(frozen=True)
class TaskContract:
    """A user-confirmed, executable task boundary."""

    task_type: str
    description: str
    objective: str
    measured_signals: tuple[str, ...]
    control_input: str
    control_inputs: tuple[str, ...] = ()
    reference: float | None = None
    input_min: float | None = None
    input_max: float | None = None
    output_min: float | None = None
    output_max: float | None = None
    state_stop: float | None = None
    operating_region: str | None = None
    success_requirements: Mapping[str, Any] = field(default_factory=dict)
    budgets: Mapping[str, Any] = field(default_factory=dict)
    initial_region: str | None = None
    initial_output_value: float | None = None
    goal_region: str | None = None
    intermediate_targets: tuple[float, ...] = ()
    disturbance_event: str | None = None
    recovery_start_condition: str | None = None
    disturbance_hold_region: str | None = None
    target_bandwidth_rad_s: float | None = None
    response_time_preference_s: float | None = None
    time_requirement_source: str | None = None
    required_phase_count_min: int | None = None
    verified_handoff_count_min: int | None = None
    final_hold_duration_min_s: float | None = None
    signal_units: Mapping[str, str] = field(default_factory=dict)
    input_units: str | None = None
    workspace: Mapping[str, Any] = field(default_factory=dict)
    # These fields preserve the public vocabulary used by the v3 contracts.
    # They are metadata and constraints supplied by the operator; they never
    # carry hidden simulator state or executable expressions.
    control_target: Mapping[str, Any] = field(default_factory=dict)
    disturbance_contract: Mapping[str, Any] = field(default_factory=dict)
    phase_schedule: Mapping[str, Any] = field(default_factory=dict)
    engineering_units: Mapping[str, Any] = field(default_factory=dict)
    task_semantics_version: str | None = None
    budget_confirmed: bool = False
    schema_version: str = TASK_CONTRACT_VERSION

    _ALIASES: ClassVar[dict[str, str]] = {
        "output_signals": "measured_signals",
        "actuator": "control_input",
        "input_lower": "input_min",
        "input_upper": "input_max",
        "task_success_requirements": "success_requirements",
    }

    @classmethod
    def from_user_input(cls, payload: Mapping[str, Any]) -> TaskContract:
        if not isinstance(payload, Mapping):
            raise TypeError("task_contract_mapping_required")
        # Archive task files wrap the contract under ``task_contract``.  Keep
        # the adapter at this boundary so all callers still share one typed
        # contract and one fingerprint implementation.
        wrapped = payload.get("task_contract")
        if not isinstance(wrapped, Mapping):
            wrapped = payload.get("task")
        raw = dict(wrapped) if isinstance(wrapped, Mapping) else dict(payload)
        supplied_fingerprint = raw.pop(
            "task_fingerprint", payload.get("task_fingerprint")
        )
        for source, target in cls._ALIASES.items():
            if (
                target not in raw
                and source in raw
                and source != "task_success_requirements"
            ):
                raw[target] = raw[source]
        declared_task_type = raw.get("task_type")
        if declared_task_type is None:
            visible = " ".join(
                str(raw.get(key) or "").casefold()
                for key in ("description", "natural_language_description", "objective")
            )
            task_type = next(
                (
                    candidate
                    for candidate, markers in _UNSUPPORTED_TASK_MARKERS.items()
                    if any(marker in visible for marker in markers)
                ),
                "local_setpoint_hold",
            )
        else:
            task_type = str(declared_task_type).strip()
        if task_type in UNSUPPORTED_TASK_TYPES:
            raise ValueError(f"unsupported_task_type: {task_type}")
        if task_type not in SUPPORTED_TASK_TYPES:
            raise ValueError(f"unsupported_task_type: {task_type}")
        semantics_version = raw.get("task_semantics_version")
        if semantics_version is not None and str(semantics_version).strip() not in {
            "",
            P1_1_TASK_SEMANTICS_VERSION,
        }:
            raise ValueError("task_semantics_version_mismatch")
        declared_schema = raw.get("schema_version")
        if declared_schema is None:
            declared_schema = raw.get(
                "contract_version", raw.get("task_contract_version")
            )
        if declared_schema is not None and str(declared_schema).strip() not in {
            "",
            TASK_CONTRACT_VERSION,
            "1.1.0",
        }:
            raise ValueError("task_contract_version_mismatch")
        description = str(
            raw.get("description") or raw.get("natural_language_description") or ""
        ).strip()
        if not description:
            raise ValueError("task_description_required")
        signals = _clean_tuple(raw.get("measured_signals"))
        if not signals:
            raise ValueError("measured_signals_required")
        declared_inputs = raw.get("control_inputs")
        if declared_inputs is None:
            declared_inputs = raw.get("actuators")
        if declared_inputs is None:
            declared_inputs = raw.get("control_input")
        control_inputs = _clean_tuple(declared_inputs)
        control_input = (
            control_inputs[0]
            if control_inputs
            else str(raw.get("control_input") or "").strip()
        )
        if not control_input:
            raise ValueError("control_input_required")
        if not control_inputs:
            control_inputs = (control_input,)
        objective = str(raw.get("objective") or "生成可审计的软件控制器").strip()
        input_min = _optional_float(raw.get("input_min"))
        input_max = _optional_float(raw.get("input_max"))
        if input_min is not None and input_max is not None and input_min >= input_max:
            raise ValueError("input_bounds_invalid")
        output_min = _optional_float(raw.get("output_min"))
        output_max = _optional_float(raw.get("output_max"))
        if (
            output_min is not None
            and output_max is not None
            and output_min >= output_max
        ):
            raise ValueError("output_bounds_invalid")
        state_stop = _optional_float(raw.get("state_stop"))
        if state_stop is not None and state_stop <= 0:
            raise ValueError("state_stop_invalid")
        initial_output_value = _optional_float(raw.get("initial_output_value"))
        declared_control_target = raw.get("control_target")
        declared_control_target = (
            declared_control_target
            if isinstance(declared_control_target, Mapping)
            else {}
        )
        target_bandwidth_value = raw.get("target_bandwidth_rad_s")
        if target_bandwidth_value is None:
            target_bandwidth_value = declared_control_target.get(
                "target_bandwidth_rad_s"
            )
        target_bandwidth = _optional_float(target_bandwidth_value)
        response_time = _optional_float(raw.get("response_time_preference_s"))
        if target_bandwidth is not None and target_bandwidth <= 0:
            raise ValueError("target_bandwidth_invalid")
        if response_time is not None and response_time <= 0:
            raise ValueError("response_time_preference_invalid")
        try:
            intermediate = tuple(
                float(value) for value in raw.get("intermediate_targets", ()) or ()
            )
        except (TypeError, ValueError) as exc:
            raise ValueError("intermediate_targets_invalid") from exc
        if len(intermediate) > 3:
            raise ValueError("intermediate_targets_limit_exceeded")
        if any(not math.isfinite(value) for value in intermediate):
            raise ValueError("intermediate_targets_invalid")
        requirements = dict(raw.get("success_requirements") or {})
        # v3 calls the same public gate ``performance_requirements``.  Merge
        # only values explicitly supplied by the operator; no example/default
        # values become object facts during migration.
        performance_requirements = raw.get("performance_requirements")
        if isinstance(performance_requirements, Mapping):
            requirements.update(dict(performance_requirements))
        task_success_requirements = raw.get("task_success_requirements")
        if isinstance(task_success_requirements, Mapping):
            requirements.update(dict(task_success_requirements))
        # Accept the current TaskDraft vocabulary without copying its defaults
        # into facts.  Only explicitly supplied values enter the new contract.
        for key in (
            "final_abs_error_max",
            "overshoot_max",
            "settling_time_max_s",
            "perturbed_success_rate_min",
            "hold_duration_s",
            "recovery_time_max_s",
        ):
            if key in raw:
                requirements[key] = raw[key]
        budgets = dict(raw.get("budgets") or {})
        for key, default in (
            ("clarification_rounds", 6),
            ("distinct_experiments", 4),
            ("same_failure_retries", 1),
            ("elapsed_time_s", 7200.0),
            ("cumulative_excitation_time_s", 1800.0),
        ):
            budgets.setdefault(key, default)
        for key, value in budgets.items():
            try:
                numeric = float(value)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"budget_invalid: {key}") from exc
            if not math.isfinite(numeric) or numeric < 0:
                raise ValueError(f"budget_invalid: {key}")
        signal_units = dict(raw.get("signal_units") or {})
        input_units = str(raw.get("input_units") or "").strip() or None
        engineering_units = raw.get("engineering_units")
        if isinstance(engineering_units, Mapping):
            unit_input = engineering_units.get("input")
            if input_units is None and isinstance(unit_input, Mapping):
                input_units = str(unit_input.get("unit") or "").strip() or None
            unit_outputs = engineering_units.get("outputs")
            if isinstance(unit_outputs, Mapping):
                for name, value in unit_outputs.items():
                    if name not in signal_units and isinstance(value, Mapping):
                        unit = str(value.get("unit") or "").strip()
                        if unit:
                            signal_units[str(name)] = unit
        simulation_limits = raw.get("simulation_limits")
        if isinstance(simulation_limits, Mapping):
            # Nested v3 limits are copied into the canonical scalar fields,
            # while the original mapping remains available in workspace.
            if input_min is None:
                input_min = _optional_float(simulation_limits.get("input_min"))
            if input_max is None:
                input_max = _optional_float(simulation_limits.get("input_max"))
            if state_stop is None:
                state_stop = _optional_float(simulation_limits.get("state_stop"))
            output_abs_max = _optional_float(simulation_limits.get("output_abs_max"))
            if output_abs_max is not None:
                if output_min is None:
                    output_min = -output_abs_max
                if output_max is None:
                    output_max = output_abs_max
        workspace = dict(raw.get("workspace") or {})
        if isinstance(simulation_limits, Mapping) and any(
            value is not None for value in simulation_limits.values()
        ):
            workspace.setdefault("simulation_limits", dict(simulation_limits))
        if isinstance(engineering_units, Mapping) and engineering_units:
            workspace.setdefault("engineering_units", dict(engineering_units))
        if (
            output_min is not None
            and output_max is not None
            and output_min >= output_max
        ):
            raise ValueError("output_bounds_invalid")
        if input_min is not None and input_max is not None and input_min >= input_max:
            raise ValueError("input_bounds_invalid")
        if state_stop is not None and state_stop <= 0:
            raise ValueError("state_stop_invalid")
        declared_phase_schedule = raw.get("phase_schedule")
        if isinstance(declared_phase_schedule, (list, tuple)):
            phase_schedule: dict[str, Any] = {
                "phases": [
                    dict(item)
                    for item in declared_phase_schedule
                    if isinstance(item, Mapping)
                ]
            }
        elif isinstance(declared_phase_schedule, Mapping):
            phase_schedule = dict(declared_phase_schedule)
        else:
            phase_schedule = {}
        if initial_output_value is None and isinstance(phase_schedule, Mapping):
            initial_output_value = _optional_float(
                phase_schedule.get("initial_output_value")
            )
        if not intermediate and isinstance(phase_schedule, Mapping):
            scheduled_targets = phase_schedule.get("intermediate_targets")
            if isinstance(scheduled_targets, (list, tuple)):
                try:
                    intermediate = tuple(float(value) for value in scheduled_targets)
                except (TypeError, ValueError) as exc:
                    raise ValueError("intermediate_targets_invalid") from exc
                if len(intermediate) > 3 or any(
                    not math.isfinite(value) for value in intermediate
                ):
                    raise ValueError("intermediate_targets_invalid")
        reference_value = raw.get("reference")
        if reference_value is None and isinstance(phase_schedule, Mapping):
            reference_value = phase_schedule.get("final_reference")
        if reference_value is None:
            reference_value = declared_control_target.get("reference")
        initial_region = (
            str(raw["initial_region"]).strip()
            if raw.get("initial_region") is not None
            else None
        )
        goal_region = (
            str(raw["goal_region"]).strip()
            if raw.get("goal_region") is not None
            else None
        )
        declared_disturbance = raw.get("disturbance_contract")
        declared_disturbance = (
            declared_disturbance if isinstance(declared_disturbance, Mapping) else {}
        )
        disturbance_event_value = raw.get(
            "disturbance_event", declared_disturbance.get("event")
        )
        recovery_start_value = raw.get(
            "recovery_start_condition",
            declared_disturbance.get("recovery_start_condition"),
        )
        disturbance_hold_value = raw.get(
            "disturbance_hold_region", declared_disturbance.get("hold_region")
        )
        disturbance_event = (
            str(disturbance_event_value).strip()
            if disturbance_event_value is not None
            else None
        )
        recovery_start_condition = (
            str(recovery_start_value).strip()
            if recovery_start_value is not None
            else None
        )
        disturbance_hold_region = (
            str(disturbance_hold_value).strip()
            if disturbance_hold_value is not None
            else None
        )
        if task_type == "transition_then_hold" and (
            not initial_region or not goal_region
        ):
            raise ValueError("transition_then_hold_requires_initial_and_goal_regions")
        if task_type == "disturbance_recovery_to_hold" and not all(
            (disturbance_event, recovery_start_condition, disturbance_hold_region)
        ):
            raise ValueError(
                "disturbance_recovery_requires_event_start_and_hold_region"
            )
        if task_type != "transition_then_hold" and intermediate:
            raise ValueError("intermediate_targets_require_transition_task")
        if intermediate:
            if initial_output_value is None or reference_value is None:
                raise ValueError(
                    "numeric_intermediate_targets_require_initial_and_reference"
                )
            points = (initial_output_value, *intermediate, float(reference_value))
            if math.isclose(points[0], points[-1], rel_tol=0.0, abs_tol=1e-12):
                raise ValueError("initial_output_and_reference_must_differ")
            direction = 1.0 if points[-1] > points[0] else -1.0
            if any(
                direction * (right - left) <= 0.0 for left, right in pairwise(points)
            ):
                raise ValueError("intermediate_targets_must_follow_execution_order")
        required_phase_count = raw.get(
            "required_phase_count_min", requirements.get("required_phase_count_min")
        )
        verified_handoff_count = raw.get(
            "verified_handoff_count_min", requirements.get("verified_handoff_count_min")
        )
        final_hold_duration = _optional_float(
            raw.get(
                "final_hold_duration_min_s",
                requirements.get("final_hold_duration_min_s"),
            )
        )
        if final_hold_duration is not None and final_hold_duration <= 0:
            raise ValueError("final_hold_duration_invalid")
        if required_phase_count is not None:
            required_phase_count = _optional_int(
                required_phase_count, "required_phase_count_invalid"
            )
            if required_phase_count < 2 or required_phase_count > 5:
                raise ValueError("required_phase_count_invalid")
        if verified_handoff_count is not None:
            verified_handoff_count = _optional_int(
                verified_handoff_count, "verified_handoff_count_invalid"
            )
            if verified_handoff_count < 1 or verified_handoff_count > 4:
                raise ValueError("verified_handoff_count_invalid")
        # Keep top-level v3 spellings and the nested success contract in one
        # canonical mapping.  Without this normalization a valid archive
        # contract that declares ``required_phase_count_min`` beside
        # ``task_success_requirements`` would fail the strict semantics check
        # even though the value was already parsed and validated above.
        for key, value in (
            ("required_phase_count_min", required_phase_count),
            ("verified_handoff_count_min", verified_handoff_count),
            ("final_hold_duration_min_s", final_hold_duration),
            (
                "goal_region_entry_required",
                raw.get(
                    "goal_region_entry_required",
                    requirements.get("goal_region_entry_required"),
                ),
            ),
            ("recovery_abs_error_max", raw.get("recovery_abs_error_max")),
            (
                "post_recovery_hold_duration_min_s",
                raw.get("post_recovery_hold_duration_min_s"),
            ),
        ):
            if value is not None:
                requirements.setdefault(key, value)
        # Validate known criteria at the contract boundary while preserving
        # forward-compatible, namespaced criteria for future routes.
        positive_criteria = {
            "final_abs_error_max",
            "settling_time_max_s",
            "hold_duration_min_s",
            "recovery_abs_error_max",
            "recovery_time_max_s",
            "post_recovery_hold_duration_min_s",
            "final_hold_duration_min_s",
            "iae_max",
            "peak_abs_input_max",
        }
        nonnegative_criteria = {"overshoot_max", "hold_duration_s"}
        rate_criteria = {"perturbed_success_rate_min", "success_rate_min"}
        for key, value in requirements.items():
            if key in {"goal_region_entry_required"}:
                if not isinstance(value, bool):
                    raise ValueError(f"task_success_requirement_invalid: {key}")
                continue
            if key in positive_criteria | nonnegative_criteria | rate_criteria:
                try:
                    number = float(value)
                except (TypeError, ValueError) as exc:
                    raise ValueError(
                        f"task_success_requirement_invalid: {key}"
                    ) from exc
                if not math.isfinite(number):
                    raise ValueError(f"task_success_requirement_invalid: {key}")
                if key in positive_criteria and number <= 0:
                    raise ValueError(f"task_success_requirement_invalid: {key}")
                if key in nonnegative_criteria and number < 0:
                    raise ValueError(f"task_success_requirement_invalid: {key}")
                if key in rate_criteria and not 0 <= number <= 1:
                    raise ValueError(f"task_success_requirement_invalid: {key}")
        if (
            semantics_version is not None
            and str(semantics_version).strip() == P1_1_TASK_SEMANTICS_VERSION
        ):
            missing_boundary = [
                name
                for name, value in (
                    ("reference", reference_value),
                    ("operating_region", raw.get("operating_region")),
                    ("input_min", input_min),
                    ("input_max", input_max),
                    ("state_stop", state_stop),
                )
                if value is None or (isinstance(value, str) and not value.strip())
            ]
            if missing_boundary:
                raise ValueError(
                    "task_contract_boundary_missing: " + ", ".join(missing_boundary)
                )
            required_by_type = {
                "local_setpoint_hold": (
                    "final_abs_error_max",
                    "overshoot_max",
                    "settling_time_max_s",
                    "perturbed_success_rate_min",
                    "hold_duration_min_s",
                ),
                "transition_then_hold": (
                    "required_phase_count_min",
                    "verified_handoff_count_min",
                    "goal_region_entry_required",
                    "final_hold_duration_min_s",
                    "perturbed_success_rate_min",
                ),
                "disturbance_recovery_to_hold": (
                    "recovery_abs_error_max",
                    "recovery_time_max_s",
                    "post_recovery_hold_duration_min_s",
                    "perturbed_success_rate_min",
                ),
            }
            missing = [
                key for key in required_by_type[task_type] if key not in requirements
            ]
            if missing:
                raise ValueError(
                    "task_success_requirements_missing: " + ", ".join(missing)
                )
        budget_confirmed_value = raw.get("budget_confirmed", False)
        if not isinstance(budget_confirmed_value, bool):
            raise ValueError("budget_confirmed_must_be_boolean")  # noqa: TRY004 - stable API error
        budget_confirmed = budget_confirmed_value
        disturbance_contract = dict(raw.get("disturbance_contract") or {})
        if task_type == "disturbance_recovery_to_hold":
            disturbance_contract.setdefault("event", disturbance_event)
            disturbance_contract.setdefault(
                "recovery_start_condition", recovery_start_condition
            )
            disturbance_contract.setdefault("hold_region", disturbance_hold_region)
        if final_hold_duration is not None:
            requirements.setdefault("final_hold_duration_min_s", final_hold_duration)
        contract = cls(
            task_type=task_type,
            description=description,
            objective=objective,
            measured_signals=signals,
            control_input=control_input,
            control_inputs=control_inputs,
            reference=_optional_float(reference_value),
            input_min=input_min,
            input_max=input_max,
            output_min=output_min,
            output_max=output_max,
            state_stop=state_stop,
            operating_region=(
                str(raw["operating_region"]).strip()
                if raw.get("operating_region") is not None
                else None
            ),
            success_requirements=requirements,
            budgets=budgets,
            initial_region=initial_region,
            initial_output_value=initial_output_value,
            goal_region=goal_region,
            intermediate_targets=intermediate,
            disturbance_event=disturbance_event,
            recovery_start_condition=recovery_start_condition,
            disturbance_hold_region=disturbance_hold_region,
            target_bandwidth_rad_s=target_bandwidth,
            response_time_preference_s=response_time,
            time_requirement_source=(
                str(raw["time_requirement_source"]).strip()
                if raw.get("time_requirement_source") is not None
                else None
            ),
            required_phase_count_min=required_phase_count,
            verified_handoff_count_min=verified_handoff_count,
            final_hold_duration_min_s=final_hold_duration,
            signal_units=signal_units,
            input_units=input_units,
            workspace=workspace,
            control_target=dict(declared_control_target),
            disturbance_contract=disturbance_contract,
            phase_schedule=phase_schedule,
            engineering_units=dict(engineering_units or {})
            if isinstance(engineering_units, Mapping)
            else {},
            task_semantics_version=(
                str(semantics_version).strip()
                if semantics_version is not None
                else None
            ),
            budget_confirmed=budget_confirmed,
        )
        if (
            supplied_fingerprint is not None
            and str(supplied_fingerprint) != contract.fingerprint
        ):
            raise ValueError("task_contract_fingerprint_mismatch")
        return contract

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> TaskContract:
        """Compatibility alias for callers that receive a decoded contract."""

        return cls.from_user_input(payload)

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> TaskContract:
        """Deserialize a previously exported public task contract."""

        return cls.from_user_input(payload)

    @property
    def contract_version(self) -> str:
        """Stable alias used by archive consumers and export tooling."""

        return self.schema_version

    @property
    def task_contract_version(self) -> str:
        return self.schema_version

    @property
    def output_signals(self) -> tuple[str, ...]:
        return self.measured_signals

    @property
    def actuator(self) -> str:
        return self.control_input

    @property
    def actuators(self) -> tuple[str, ...]:
        return self.control_inputs or (self.control_input,)

    @property
    def performance_requirements(self) -> Mapping[str, Any]:
        return self.success_requirements

    @property
    def task_success_requirements(self) -> Mapping[str, Any]:
        return self.success_requirements

    @property
    def simulation_limits(self) -> dict[str, Any]:
        value: dict[str, Any] = {
            "input_min": self.input_min,
            "input_max": self.input_max,
            "state_stop": self.state_stop,
        }
        original = self.workspace.get("simulation_limits")
        if isinstance(original, Mapping):
            value.update(dict(original))
        return value

    @property
    def fingerprint(self) -> str:
        value = self.to_dict(include_fingerprint=False)
        # Compatibility aliases are useful at the API boundary but should not
        # make a task fingerprint depend on serialization spelling.  A nested
        # ``simulation_limits`` block that merely repeats canonical scalar
        # bounds is likewise representation metadata, not a new task fact.
        for key in (
            "output_signals",
            "actuator",
            "actuators",
            "task_success_requirements",
            "performance_requirements",
            "simulation_limits",
            "contract_version",
            "task_contract_version",
        ):
            value.pop(key, None)
        workspace = dict(value.get("workspace") or {})
        limits = workspace.get("simulation_limits")
        if isinstance(limits, Mapping):
            canonical_limits = {
                "input_min": self.input_min,
                "input_max": self.input_max,
                "state_stop": self.state_stop,
            }
            if all(
                limits.get(key) == item for key, item in canonical_limits.items()
            ) and set(limits) <= set(canonical_limits):
                workspace.pop("simulation_limits", None)
        value["workspace"] = workspace
        return fingerprint(value)

    def to_dict(self, *, include_fingerprint: bool = True) -> dict[str, Any]:
        result = asdict(self)
        result["measured_signals"] = list(self.measured_signals)
        result["control_inputs"] = list(self.control_inputs or (self.control_input,))
        result["output_signals"] = list(self.measured_signals)
        result["actuator"] = self.control_input
        result["actuators"] = list(self.control_inputs or (self.control_input,))
        result["intermediate_targets"] = list(self.intermediate_targets)
        result["success_requirements"] = dict(self.success_requirements)
        result["budgets"] = dict(self.budgets)
        result["signal_units"] = dict(self.signal_units)
        result["workspace"] = dict(self.workspace)
        result["control_target"] = dict(self.control_target)
        result["disturbance_contract"] = dict(self.disturbance_contract)
        result["phase_schedule"] = dict(self.phase_schedule)
        result["engineering_units"] = dict(self.engineering_units)
        result["task_success_requirements"] = dict(self.success_requirements)
        result["performance_requirements"] = dict(self.success_requirements)
        result["simulation_limits"] = self.simulation_limits
        result["contract_version"] = self.schema_version
        result["task_contract_version"] = self.schema_version
        if include_fingerprint:
            result["task_fingerprint"] = self.fingerprint
        return result


def _optional_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("non_finite_number")
    return number


def _optional_int(value: Any, error: str) -> int:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(error) from exc
    if not math.isfinite(number) or not number.is_integer():
        raise ValueError(error)
    return int(number)


@dataclass(frozen=True)
class ControllerFreeze:
    session_id: str
    task_fingerprint: str
    controller: Mapping[str, Any]
    evidence_fingerprints: tuple[str, ...]
    runtime_contract: Mapping[str, Any]
    evaluation_contract: Mapping[str, Any]
    source_version: str
    freeze_version: str = FREEZE_VERSION
    freeze_fingerprint: str | None = None

    def __post_init__(self) -> None:
        if self.freeze_version != FREEZE_VERSION:
            raise ValueError("controller_freeze_version_mismatch")
        if not self.session_id.strip() or not self.task_fingerprint.strip():
            raise ValueError("controller_freeze_binding_required")
        if (
            not self.controller
            or not self.runtime_contract
            or not self.evaluation_contract
        ):
            raise ValueError("controller_freeze_contract_incomplete")

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> ControllerFreeze:
        raw = dict(value)
        supplied = raw.get("freeze_fingerprint")
        raw.pop("freeze_fingerprint", None)
        freeze = cls(
            session_id=str(raw.get("session_id") or ""),
            task_fingerprint=str(raw.get("task_fingerprint") or ""),
            controller=dict(raw.get("controller") or {}),
            evidence_fingerprints=tuple(
                str(item) for item in raw.get("evidence_fingerprints", ()) or ()
            ),
            runtime_contract=dict(raw.get("runtime_contract") or {}),
            evaluation_contract=dict(raw.get("evaluation_contract") or {}),
            source_version=str(raw.get("source_version") or ""),
            freeze_version=str(raw.get("freeze_version") or FREEZE_VERSION),
        )
        if (
            supplied is not None
            and str(supplied) != freeze.to_dict()["freeze_fingerprint"]
        ):
            raise ValueError("controller_freeze_fingerprint_mismatch")
        return freeze

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> ControllerFreeze:
        return cls.from_mapping(value)

    def to_dict(self, *, include_fingerprint: bool = True) -> dict[str, Any]:
        value = asdict(self)
        value["evidence_fingerprints"] = list(self.evidence_fingerprints)
        value.pop("freeze_fingerprint", None)
        if include_fingerprint:
            value["freeze_fingerprint"] = fingerprint(value)
        return value


@dataclass(frozen=True)
class EvaluationPacket:
    session_id: str
    freeze_fingerprint: str
    task_fingerprint: str
    provider_id: str
    provider_version: str
    trials: tuple[Mapping[str, Any], ...]
    private_truth_returned: bool = False
    evaluation_split: str = "development"
    evidence_fingerprints: tuple[str, ...] = ()
    provider_contract: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    packet_version: str = PACKET_VERSION
    packet_fingerprint: str | None = None

    def __post_init__(self) -> None:
        if self.packet_version != PACKET_VERSION:
            raise ValueError("evaluation_packet_version_mismatch")
        if (
            not self.session_id.strip()
            or not self.freeze_fingerprint.strip()
            or not self.task_fingerprint.strip()
        ):
            raise ValueError("evaluation_packet_binding_required")
        if not self.provider_id.strip() or not self.provider_version.strip():
            raise ValueError("evaluation_packet_provider_required")
        if not self.trials or not all(
            isinstance(item, Mapping) for item in self.trials
        ):
            raise ValueError("evaluation_packet_trials_required")
        if self.evaluation_split not in {"development", "fresh_confirmation", "replay"}:
            raise ValueError("evaluation_packet_split_invalid")
        if len(set(self.evidence_fingerprints)) != len(self.evidence_fingerprints):
            raise ValueError("evaluation_packet_duplicate_evidence")

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> EvaluationPacket:
        raw = dict(value)
        supplied = raw.get("packet_fingerprint")
        raw.pop("packet_fingerprint", None)
        private_truth_value = raw.get("private_truth_returned", False)
        if not isinstance(private_truth_value, bool):
            raise ValueError("private_truth_returned_must_be_boolean")  # noqa: TRY004 - stable API error
        provider = (
            raw.get("provider_contract")
            if isinstance(raw.get("provider_contract"), Mapping)
            else {}
        )
        provider_id = raw.get("provider_id") or provider.get("provider_id")
        provider_version = raw.get("provider_version") or provider.get(
            "provider_version"
        )
        raw_evidence = raw.get("evidence_fingerprints")
        if raw_evidence is None and raw.get("evidence_fingerprint"):
            raw_evidence = (raw.get("evidence_fingerprint"),)
        elif isinstance(raw_evidence, str):
            raw_evidence = (raw_evidence,)
        elif not isinstance(raw_evidence, (list, tuple, set, frozenset)):
            raw_evidence = ()
        packet = cls(
            session_id=str(raw.get("session_id") or raw.get("run_id") or ""),
            freeze_fingerprint=str(
                raw.get("freeze_fingerprint")
                or raw.get("controller_freeze_fingerprint")
                or raw.get("evaluation_freeze_fingerprint")
                or ""
            ),
            task_fingerprint=str(
                raw.get("task_fingerprint")
                or raw.get("task_contract_fingerprint")
                or ""
            ),
            provider_id=str(provider_id or ""),
            provider_version=str(provider_version or ""),
            trials=tuple(dict(item) for item in raw.get("trials", ()) or ()),
            private_truth_returned=private_truth_value,
            evaluation_split=str(raw.get("evaluation_split") or "development"),
            evidence_fingerprints=tuple(str(item) for item in raw_evidence),
            provider_contract=dict(provider) if provider else {},
            metadata=dict(raw.get("metadata") or {}),
            packet_version=str(raw.get("packet_version") or PACKET_VERSION),
        )
        if (
            supplied is not None
            and str(supplied) != packet.to_dict()["packet_fingerprint"]
        ):
            raise ValueError("evaluation_packet_fingerprint_mismatch")
        return packet

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> EvaluationPacket:
        return cls.from_mapping(value)

    def to_dict(self, *, include_fingerprint: bool = True) -> dict[str, Any]:
        value = asdict(self)
        value["trials"] = [dict(item) for item in self.trials]
        value["evidence_fingerprints"] = list(self.evidence_fingerprints)
        value["provider_contract"] = dict(self.provider_contract)
        value["metadata"] = dict(self.metadata)
        value.pop("packet_fingerprint", None)
        if include_fingerprint:
            value["packet_fingerprint"] = fingerprint(value)
        return value
