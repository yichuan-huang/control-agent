"""Explicit, credential-free form drafts for the guided task wizard."""

from __future__ import annotations

import math
from collections.abc import Mapping
from copy import deepcopy
from typing import Any

from cfdc.i18n import Locale, message_ref, t
from cfdc.kernel.cases import public_training_case
from cfdc.kernel.contracts import TaskContract
from cfdc.kernel.session import registered_task_scope_fingerprint

TASK_TYPES = [
    ("保持在目标附近", "local_setpoint_hold"),
    ("变化到新目标后保持", "transition_then_hold"),
    ("受到扰动后恢复并保持", "disturbance_recovery_to_hold"),
]
REQUIREMENTS = {
    "final_abs_error_max": "稳定后允许偏离目标多少",
    "overshoot_max": "允许超过目标多少",
    "settling_time_max_s": "希望多少秒内稳定",
    "hold_duration_min_s": "至少保持多少秒",
    "perturbed_success_rate_min": "重复试验成功率下限",
}
BUDGETS = {
    "distinct_experiments": "最多尝试几种实验",
    "cumulative_excitation_time_s": "累计激励时间上限 (s)",
}


class DraftValidationError(ValueError):
    def __init__(
        self,
        errors: Mapping[str, str | Mapping[str, Any]],
        *,
        locale: Locale = "zh-CN",
        field_message_refs: Mapping[str, Mapping[str, Any]] | None = None,
    ):
        self.field_message_refs = {
            field: dict(value)
            for field, value in errors.items()
            if isinstance(value, Mapping) and "key" in value
        }
        self.field_message_refs.update(dict(field_message_refs or {}))
        self.errors = {
            field: t(
                str(self.field_message_refs[field]["key"]),
                locale,
                **dict(self.field_message_refs[field].get("params") or {}),
            )
            if field in self.field_message_refs
            else str(value)
            for field, value in errors.items()
        }
        self.message_ref = message_ref("presentation.draft.complete_fields")
        super().__init__(t(self.message_ref["key"], locale))


def empty_draft() -> dict[str, Any]:
    return {
        "description": "",
        "task_type": "local_setpoint_hold",
        "outputs": [["", ""]],
        "inputs": [[""]],
        "input_unit": "",
        "reference_enabled": False,
        "reference": None,
        "input_min": None,
        "input_max": None,
        "state_stop": None,
        "output_bounds_enabled": False,
        "output_min": None,
        "output_max": None,
        "initial_region": "",
        "goal_region": "",
        "initial_output_value_enabled": False,
        "initial_output_value": None,
        "intermediate_targets": "",
        "disturbance_event": "",
        "recovery_start_condition": "",
        "disturbance_hold_region": "",
        "success_requirement_fields": [],
        **dict.fromkeys(REQUIREMENTS),
        "response_time_preference_enabled": False,
        "response_time_preference_s": None,
        "budget_fields": [],
        **dict.fromkeys(BUDGETS),
    }


EXTERNAL_DRAFT_DEFAULTS = {
    "external_data_enabled": False,
    "region_label": "",
    "evaluation_dt_s": 0.02,
    "evaluation_horizon_s": 20.0,
    "evaluation_repeats": 20,
    "transition_deadline_s": 10.0,
    "handoff_count_min": 1,
    "disturbance_channel": "",
    "disturbance_start_s": None,
    "disturbance_amplitude": None,
    "disturbance_duration_s": None,
    "recovery_deadline_s": 10.0,
}


DRAFT_FIELDS = tuple(empty_draft())
PAGE_FIELDS = (
    (
        "description",
        "task_type",
        "initial_region",
        "goal_region",
        "initial_output_value_enabled",
        "initial_output_value",
        "intermediate_targets",
        "disturbance_event",
        "recovery_start_condition",
        "disturbance_hold_region",
    ),
    ("outputs", "inputs", "input_unit"),
    tuple(
        key
        for key in DRAFT_FIELDS
        if key
        not in {
            "description",
            "task_type",
            "outputs",
            "inputs",
            "input_unit",
            "initial_region",
            "goal_region",
            "initial_output_value_enabled",
            "initial_output_value",
            "intermediate_targets",
            "disturbance_event",
            "recovery_start_condition",
            "disturbance_hold_region",
        }
    ),
)


def task_from_draft(
    form: Mapping[str, Any], *, case_id: str = "", locale: Locale = "zh-CN"
) -> dict[str, Any]:
    """Build the existing task contract; UI defaults never become evidence."""
    values = {**empty_draft(), **EXTERNAL_DRAFT_DEFAULTS, **dict(form)}
    errors: dict[str, Mapping[str, Any]] = {}

    def required_text(key: str, message: Mapping[str, Any]) -> str:
        value = str(values.get(key) or "").strip()
        if not value:
            errors[key] = message
        return value

    def number(
        key: str, *, positive: bool = False, nonnegative: bool = False
    ) -> float | None:
        raw = values.get(key)
        try:
            if raw is None or isinstance(raw, bool) or raw == "":
                raise ValueError
            value = float(raw)
            if not math.isfinite(value):
                raise ValueError
        except (ValueError, TypeError):
            errors[key] = message_ref("presentation.draft.finite_number")
            return None
        if positive and value <= 0:
            errors[key] = message_ref("presentation.draft.positive_number")
        if nonnegative and value < 0:
            errors[key] = message_ref("presentation.draft.nonnegative_number")
        return value

    def names(key: str, width: int) -> list[list[str]]:
        rows = values.get(key)
        result = []
        seen = set()
        for row in rows if isinstance(rows, (list, tuple)) else ():
            if not isinstance(row, (list, tuple)) or len(row) != width:
                errors[key] = message_ref("presentation.draft.row_name_unit")
                continue
            cells = [str(item or "").strip() for item in row]
            if not any(cells):
                continue
            if not cells[0] or cells[0] in seen:
                errors[key] = message_ref("presentation.draft.unique_name")
            seen.add(cells[0])
            result.append(cells)
        if not result:
            errors[key] = message_ref("presentation.draft.at_least_one_name")
        return result

    description = required_text(
        "description", message_ref("presentation.draft.description")
    )
    task_type = values["task_type"]
    if task_type not in {value for _, value in TASK_TYPES}:
        errors["task_type"] = message_ref("presentation.draft.task_type")
    outputs = names("outputs", 2)
    inputs = names("inputs", 1)
    task = {
        "description": description,
        "task_type": task_type,
        "measured_signals": [row[0] for row in outputs],
        "signal_units": {row[0]: row[1] for row in outputs if row[1]},
        "control_inputs": [row[0] for row in inputs],
        "control_input": inputs[0][0] if inputs else "",
        "input_units": str(values.get("input_unit") or "").strip() or None,
        "input_min": number("input_min"),
        "input_max": number("input_max"),
        "state_stop": number("state_stop", positive=True),
        "reference": number("reference") if values["reference_enabled"] else None,
        "output_min": number("output_min") if values["output_bounds_enabled"] else None,
        "output_max": number("output_max") if values["output_bounds_enabled"] else None,
        "success_requirements": {},
        "budgets": {},
        "response_time_preference_s": number(
            "response_time_preference_s", positive=True
        )
        if values["response_time_preference_enabled"]
        else None,
    }
    for lower, upper in (("input_min", "input_max"), ("output_min", "output_max")):
        if (
            task[lower] is not None
            and task[upper] is not None
            and task[lower] >= task[upper]
        ):
            errors[upper] = message_ref("presentation.draft.ordered_bounds")
    for key in values["success_requirement_fields"] or ():
        if key not in REQUIREMENTS:
            errors["success_requirement_fields"] = message_ref(
                "presentation.draft.unsupported_requirements"
            )
            continue
        value = number(
            key,
            positive=key not in {"overshoot_max", "perturbed_success_rate_min"},
            nonnegative=True,
        )
        if (
            key == "perturbed_success_rate_min"
            and value is not None
            and not 0 < value <= 1
        ):
            errors[key] = message_ref("presentation.draft.success_rate")
        task["success_requirements"][key] = value
    for key in values["budget_fields"] or ():
        if key not in BUDGETS:
            errors["budget_fields"] = message_ref(
                "presentation.draft.unsupported_budgets"
            )
            continue
        value = number(key, positive=True)
        if key == "distinct_experiments" and value is not None:
            if not value.is_integer():
                errors[key] = message_ref("presentation.draft.experiment_count")
            else:
                value = int(value)
        task["budgets"][key] = value
    if task_type == "transition_then_hold":
        task["initial_region"] = required_text(
            "initial_region", message_ref("presentation.draft.initial_region")
        )
        task["goal_region"] = required_text(
            "goal_region", message_ref("presentation.draft.goal_region")
        )
        task["initial_output_value"] = (
            number("initial_output_value")
            if values["initial_output_value_enabled"]
            else None
        )
        try:
            targets = [
                float(item.strip())
                for item in str(values["intermediate_targets"] or "")
                .replace("，", ",")
                .replace("、", ",")
                .split(",")
                if item.strip()
            ]
            if not all(math.isfinite(item) for item in targets):
                raise ValueError
            task["intermediate_targets"] = targets
        except (ValueError, TypeError):
            errors["intermediate_targets"] = message_ref(
                "presentation.draft.intermediate_targets"
            )
    elif task_type == "disturbance_recovery_to_hold":
        for key in (
            "disturbance_event",
            "recovery_start_condition",
            "disturbance_hold_region",
        ):
            task[key] = required_text(key, message_ref(f"presentation.draft.{key}"))
    if values["external_data_enabled"] and not case_id:
        task["operating_region"] = required_text(
            "region_label", message_ref("presentation.draft.operating_region")
        )
        if task["reference"] is None:
            errors["reference"] = message_ref("presentation.draft.external_reference")
        if "final_abs_error_max" not in task["success_requirements"]:
            errors["success_requirement_fields"] = message_ref(
                "presentation.draft.external_error_requirement"
            )
        dt = number("evaluation_dt_s", positive=True)
        horizon = number("evaluation_horizon_s", positive=True)
        repeats = number("evaluation_repeats", positive=True)
        if repeats is not None and (not repeats.is_integer() or repeats > 100):
            errors["evaluation_repeats"] = message_ref("presentation.draft.repeats")
        if horizon is not None and dt is not None and horizon <= dt:
            errors["evaluation_horizon_s"] = message_ref(
                "presentation.draft.horizon_sample_period"
            )
        task["budgets"].update(
            evaluation_sample_time_s=dt,
            evaluation_horizon_s=horizon,
            evaluation_repeats=int(repeats) if repeats is not None else None,
        )
        if task_type == "transition_then_hold":
            if task["initial_output_value"] is None:
                errors["initial_output_value"] = message_ref(
                    "presentation.draft.initial_output"
                )
            handoffs = number("handoff_count_min", positive=True)
            phase_count = len(task.get("intermediate_targets", ())) + 2
            if handoffs is not None and (
                not handoffs.is_integer() or handoffs != phase_count - 1
            ):
                errors["handoff_count_min"] = message_ref(
                    "presentation.draft.handoff_count"
                )
            deadline = number("transition_deadline_s", positive=True)
            task["success_requirements"].update(
                required_phase_count_min=phase_count,
                verified_handoff_count_min=int(handoffs)
                if handoffs is not None
                else None,
                goal_region_entry_required=True,
                settling_time_max_s=deadline,
                final_hold_duration_min_s=task["success_requirements"].get(
                    "hold_duration_min_s", 1.0
                ),
            )
        elif task_type == "disturbance_recovery_to_hold":
            channel = required_text(
                "disturbance_channel",
                message_ref("presentation.draft.disturbance_channel"),
            )
            if channel not in task["control_inputs"]:
                errors["disturbance_channel"] = message_ref(
                    "presentation.draft.declared_channel"
                )
            start = number("disturbance_start_s", nonnegative=True)
            duration = number("disturbance_duration_s", positive=True)
            amplitude = number("disturbance_amplitude")
            if amplitude == 0:
                errors["disturbance_amplitude"] = message_ref(
                    "presentation.draft.disturbance_amplitude"
                )
            recovery = number("recovery_deadline_s", positive=True)
            hold = task["success_requirements"].get("hold_duration_min_s", 1.0)
            if (
                all(value is not None for value in (start, duration, horizon, recovery))
                and start + duration + recovery + hold > horizon
            ):
                errors["evaluation_horizon_s"] = message_ref(
                    "presentation.draft.horizon_coverage"
                )
            task["disturbance_contract"] = {
                "channel": channel,
                "time_s": start,
                "duration_s": duration,
                "amplitude": amplitude,
            }
            task["success_requirements"].update(
                recovery_abs_error_max=task["success_requirements"].get(
                    "final_abs_error_max"
                ),
                recovery_time_max_s=recovery,
                post_recovery_hold_duration_min_s=hold,
            )
    if values.get("execution_mode") not in (None, "", "manual") or any(
        values.get(key) for key in ("runner_id", "model_id")
    ):
        errors["execution_mode"] = message_ref(
            "presentation.draft.removed_execution_mode"
        )
    if errors:
        raise DraftValidationError(errors, locale=locale)
    if case_id:
        canonical = public_training_case(case_id)["task"]
        task = {
            **canonical,
            **{
                key: value
                for key, value in task.items()
                if not (
                    key in {"signal_units", "input_units"} and value in ({}, "", None)
                )
            },
        }
        if registered_task_scope_fingerprint(
            TaskContract.from_user_input(task)
        ) != registered_task_scope_fingerprint(TaskContract.from_user_input(canonical)):
            raise DraftValidationError(
                {"case_id": message_ref("presentation.draft.case_changed")},
                locale=locale,
            )
    return task


def case_draft(case_id: str) -> dict[str, Any]:
    task = public_training_case(case_id)["task"]
    form = empty_draft()
    for key in form:
        if key in task:
            form[key] = deepcopy(task[key])
    units = task.get("engineering_units") or {}
    outputs = units.get("outputs") or {}
    form["outputs"] = [
        [
            name,
            (task.get("signal_units") or {}).get(name)
            or (outputs.get(name) or {}).get("unit", ""),
        ]
        for name in task.get("measured_signals", ())
    ]
    form["inputs"] = [
        [name] for name in task.get("control_inputs") or [task["control_input"]]
    ]
    form["input_unit"] = task.get("input_units") or (units.get("input") or {}).get(
        "unit", ""
    )
    for field in ("reference", "initial_output_value", "response_time_preference_s"):
        enabled_key = (
            "response_time_preference_enabled"
            if field == "response_time_preference_s"
            else f"{field}_enabled"
        )
        form[enabled_key] = task.get(field) is not None
    form["output_bounds_enabled"] = task.get("output_min") is not None
    for source, selection in (
        ("success_requirements", "success_requirement_fields"),
        ("budgets", "budget_fields"),
    ):
        names = REQUIREMENTS if source == "success_requirements" else BUDGETS
        raw = task.get(source) or (task if source == "success_requirements" else {})
        values = {key: raw[key] for key in names if raw.get(key) is not None}
        form[selection] = list(values)
        form.update(values)
    form["intermediate_targets"] = ", ".join(
        str(item) for item in task.get("intermediate_targets", ())
    )
    return form
