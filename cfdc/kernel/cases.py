"""Public built-in audit and engineering training case catalog."""

from __future__ import annotations

import json
from copy import deepcopy
from functools import lru_cache
from importlib.resources import files
from typing import Any

TRANSITION_VARIANTS: dict[str, dict[str, Any]] = {
    "dc_motor_speed_transition_hold_v1": {
        "base": "dc_motor_speed_v1",
        "label_cn": "06｜直流电机转速：进入目标区后保持",
        "initial_region": "转速接近 0 rad/s",
        "initial_output_value": 0.0,
        "goal_region": "转速 20 rad/s 附近",
        "intermediate_targets": [],
    },
    "tclab_single_heater_transition_hold_v1": {
        "base": "tclab_single_heater_v1",
        "label_cn": "07｜单加热器：升温后保持",
        "initial_region": "温升接近 0 degC",
        "initial_output_value": 0.0,
        "goal_region": "温升 8 degC 附近",
        "intermediate_targets": [],
    },
    "quadruple_tank_transition_hold_v1": {
        "base": "quadruple_tank_nmp_v1",
        "label_cn": "08｜四水箱：进入目标区后保持",
        "initial_region": "液位变化接近 0 cm",
        "initial_output_value": 0.0,
        "goal_region": "液位变化 2 cm 附近",
        "intermediate_targets": [],
    },
    "dc_motor_speed_staged_transition_hold_v1": {
        "base": "dc_motor_speed_v1",
        "label_cn": "09｜直流电机：10 → 20 rad/s 分段保持",
        "initial_region": "转速接近 0 rad/s",
        "initial_output_value": 0.0,
        "goal_region": "转速 20 rad/s 附近",
        "intermediate_targets": [10.0],
    },
    "tclab_single_heater_staged_transition_hold_v1": {
        "base": "tclab_single_heater_v1",
        "label_cn": "10｜单加热器：3 → 6 → 8 degC 分段保持",
        "initial_region": "温升接近 0 degC",
        "initial_output_value": 0.0,
        "goal_region": "温升 8 degC 附近",
        "intermediate_targets": [3.0, 6.0],
    },
    "quadruple_tank_staged_transition_hold_v1": {
        "base": "quadruple_tank_nmp_v1",
        "label_cn": "11｜四水箱：1 → 2 cm 分段保持",
        "initial_region": "液位变化接近 0 cm",
        "initial_output_value": 0.0,
        "goal_region": "液位变化 2 cm 附近",
        "intermediate_targets": [1.0],
    },
}

AUDIT_CASES: dict[str, dict[str, Any]] = {
    "audit_class_i_level": {
        "label_cn": "Class I｜液位通道：一阶自调节",
    },
    "audit_class_ii_thermal": {
        "label_cn": "Class II｜温度通道：双滞后与短延迟",
    },
    "audit_class_ii_oscillator": {
        "label_cn": "Class II｜柔性台架：欠阻尼振荡",
    },
    "audit_class_iii_motion": {
        "label_cn": "Class III｜低摩擦平台：积分运动",
    },
    "audit_class_iv_nmp": {
        "label_cn": "Class IV｜外部位置：稳定逆响应",
    },
    "audit_class_iv_high_order": {
        "label_cn": "Class IV｜多储能过程：稳定高阶",
    },
    "audit_class_v_mimo": {
        "label_cn": "Class V｜双变量过程：动态耦合",
    },
}


@lru_cache(maxsize=1)
def training_catalog() -> dict[str, dict[str, Any]]:
    path = files("cfdc.kernel").joinpath("resources", "physical_training_cases.v1.json")
    return json.loads(path.read_text(encoding="utf-8"))["cases"]


@lru_cache(maxsize=1)
def audit_catalog() -> dict[str, dict[str, Any]]:
    """Return public audit task contracts, never private provider models."""

    path = files("cfdc.kernel").joinpath("resources", "audit_cases.v1.json")
    return json.loads(path.read_text(encoding="utf-8"))["cases"]


def public_training_case(case_id: str) -> dict[str, Any]:
    if case_id in AUDIT_CASES:
        value = deepcopy(audit_catalog()[case_id])
        value["case_kind"] = "audit"
        return value
    if case_id in TRANSITION_VARIANTS:
        variant = TRANSITION_VARIANTS[case_id]
        value = deepcopy(training_catalog()[variant["base"]])
        task = value["task"]
        task.update(
            {
                "task_type": "transition_then_hold",
                "initial_region": variant["initial_region"],
                "initial_output_value": variant["initial_output_value"],
                "goal_region": variant["goal_region"],
                "intermediate_targets": deepcopy(variant["intermediate_targets"]),
                "objective": "依次进入公开目标区域并在最终区域保持。",
            }
        )
        value["label_cn"] = variant["label_cn"]
        value["base_case_id"] = variant["base"]
        return value
    if case_id not in training_catalog():
        raise ValueError(f"unknown_training_case: {case_id}")
    return deepcopy(training_catalog()[case_id])


def public_case_catalog() -> dict[str, dict[str, Any]]:
    result = {
        case_id: {
            "kind": "training",
            "label": item["label_cn"],
            "task": deepcopy(item["task"]),
        }
        for case_id, item in training_catalog().items()
    }
    for case_id, item in TRANSITION_VARIANTS.items():
        case = public_training_case(case_id)
        result[case_id] = {
            "kind": "training",
            "label": case["label_cn"],
            "task": case["task"],
        }
    for case_id, item in AUDIT_CASES.items():
        case = public_training_case(case_id)
        result[case_id] = {
            "kind": "audit",
            "label": item["label_cn"],
            "task": case["task"],
        }
    return result


def case_learning_material(case_id: str | None = None) -> dict[str, Any]:
    """Return concise, public teaching guidance for the three-step workbench."""

    if case_id:
        case = public_training_case(str(case_id))
        task = case.get("task") if isinstance(case.get("task"), dict) else {}
        goal = (
            case.get("learning_goal")
            or case.get("learning_purpose_cn")
            or task.get("objective")
            or "从当前任务和公开证据建立可审计的控制结论。"
        )
        source_kind = "注册案例绑定的公开软件 Provider"
    else:
        goal = "把自定义任务拆成边界、证据、路线和独立评价。"
        source_kind = "当前协议绑定的外部公开证据"
    return {
        "learning_goal": str(goal),
        "key_terms": [
            "任务合同",
            "公开证据",
            "路线与特征",
            "控制器冻结",
            "独立评价",
        ],
        "evidence_boundary": f"{source_kind}；不自动代表真实硬件测量。",
        "cannot_prove": [
            "物理安全认证",
            "未测工作区的全局稳定性",
            "未声明工况之外的控制性能",
        ],
    }


__all__ = [
    "AUDIT_CASES",
    "TRANSITION_VARIANTS",
    "audit_catalog",
    "case_learning_material",
    "public_case_catalog",
    "public_training_case",
    "training_catalog",
]
