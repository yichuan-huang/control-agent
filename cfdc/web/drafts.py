"""Explicit, credential-free form drafts for the guided task wizard."""

from __future__ import annotations

import math
from collections.abc import Mapping
from copy import deepcopy
from typing import Any

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
    def __init__(self, errors: Mapping[str, str]):
        self.errors = dict(errors)
        super().__init__("请完成标出的项目后继续。")


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


def task_from_draft(form: Mapping[str, Any], *, case_id: str = "") -> dict[str, Any]:
    """Build the existing task contract; UI defaults never become evidence."""
    values = {**empty_draft(), **dict(form)}
    errors: dict[str, str] = {}

    def required_text(key: str, message: str) -> str:
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
            errors[key] = "请填写有限数字。"
            return None
        if positive and value <= 0:
            errors[key] = "请填写大于 0 的数字。"
        if nonnegative and value < 0:
            errors[key] = "请填写大于或等于 0 的数字。"
        return value

    def names(key: str, width: int) -> list[list[str]]:
        rows = values.get(key)
        result = []
        seen = set()
        for row in rows if isinstance(rows, (list, tuple)) else ():
            if not isinstance(row, (list, tuple)) or len(row) != width:
                errors[key] = "请为每一行填写名称和对应单位。"
                continue
            cells = [str(item or "").strip() for item in row]
            if not any(cells):
                continue
            if not cells[0] or cells[0] in seen:
                errors[key] = "每一项需要一个不重复的名称。"
            seen.add(cells[0])
            result.append(cells)
        if not result:
            errors[key] = "请至少填写一个名称。"
        return result

    description = required_text("description", "请描述设备和希望达到的目标。")
    task_type = values["task_type"]
    if task_type not in {value for _, value in TASK_TYPES}:
        errors["task_type"] = "请选择当前支持的任务类型。"
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
            errors[upper] = "上限必须大于下限。"
    for key in values["success_requirement_fields"] or ():
        if key not in REQUIREMENTS:
            errors["success_requirement_fields"] = "包含不支持的性能要求。"
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
            errors[key] = "成功率应大于 0 且不超过 1。"
        task["success_requirements"][key] = value
    for key in values["budget_fields"] or ():
        if key not in BUDGETS:
            errors["budget_fields"] = "包含不支持的预算项目。"
            continue
        value = number(key, positive=True)
        if key == "distinct_experiments" and value is not None:
            if not value.is_integer():
                errors[key] = "实验次数必须是正整数。"
            else:
                value = int(value)
        task["budgets"][key] = value
    if task_type == "transition_then_hold":
        task["initial_region"] = required_text(
            "initial_region", "请描述开始时所在的区域。"
        )
        task["goal_region"] = required_text("goal_region", "请描述需要到达的目标区域。")
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
            errors["intermediate_targets"] = "请用逗号分隔有限数字，例如 3, 6。"
    elif task_type == "disturbance_recovery_to_hold":
        for key, label in (
            ("disturbance_event", "扰动事件"),
            ("recovery_start_condition", "恢复起点"),
            ("disturbance_hold_region", "恢复后保持区域"),
        ):
            task[key] = required_text(key, f"请描述{label}。")
    if errors:
        raise DraftValidationError(errors)
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
                {"case_id": "案例参数已发生变化。请重新选择案例，或转为自己的任务。"}
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
