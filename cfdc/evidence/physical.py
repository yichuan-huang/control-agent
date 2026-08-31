"""Physical experiment preflight and engineering-unit normalization."""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

from cfdc.kernel.contracts import fingerprint

_UNRESOLVED = frozenset({"", "unknown", "todo", "tbd", "pending", "null", "none", "待填写", "未知"})


def unresolved_fields(value: Any, path: str = "") -> list[str]:
    if isinstance(value, Mapping):
        result: list[str] = []
        for key, item in value.items():
            child = f"{path}.{key}" if path else str(key)
            result.extend(unresolved_fields(item, child))
        return result
    if isinstance(value, (list, tuple)):
        result = []
        for index, item in enumerate(value):
            result.extend(unresolved_fields(item, f"{path}[{index}]"))
        return result
    if value is None or (isinstance(value, str) and value.strip().casefold() in _UNRESOLVED):
        return [path]
    if isinstance(value, float) and not math.isfinite(value):
        return [path]
    return []


def audit_physical_preflight(bundle: Mapping[str, Any]) -> dict[str, Any]:
    required = {
        "task": bundle.get("task"),
        "protocol": bundle.get("protocol"),
        "controller_freeze": bundle.get("controller_freeze"),
        "provider": bundle.get("provider"),
        "device_id": bundle.get("device_id"),
        "attestation": bundle.get("attestation"),
    }
    unresolved = unresolved_fields(required)
    freeze = bundle.get("controller_freeze")
    protocol = bundle.get("protocol")
    reasons: list[str] = []
    if isinstance(freeze, Mapping) and isinstance(protocol, Mapping):
        expected = freeze.get("protocol_fingerprint") or freeze.get("evidence_fingerprint")
        if expected and expected != protocol.get("protocol_fingerprint"):
            reasons.append("freeze_protocol_binding_mismatch")
    status = "ready_for_operator_review" if not unresolved and not reasons else "not_ready"
    result = {
        "preflight_version": "cfdc-physical-preflight/v1",
        "status": status,
        "unresolved_fields": unresolved,
        "reasons": reasons,
        "hardware_execution_authorized": False,
        "claims_forbidden": ["physical safety certification", "autonomous hardware execution"],
    }
    result["preflight_fingerprint"] = fingerprint(result)
    return result


def normalize_engineering_values(values: Any, contract: Mapping[str, Any]) -> list[float]:
    zero = float(contract.get("zero", 0.0))
    scale = float(contract.get("scale", 1.0))
    if not math.isfinite(scale) or scale == 0.0:
        raise ValueError("engineering_unit_scale_invalid")
    result = [(float(item) - zero) / scale for item in values]
    if not all(math.isfinite(item) for item in result):
        raise ValueError("engineering_values_non_finite")
    return result


__all__ = ["audit_physical_preflight", "normalize_engineering_values", "unresolved_fields"]
