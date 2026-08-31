"""Evidence-conditioned numerical qualification before controller freeze."""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

import numpy as np

from cfdc.kernel.contracts import QUALIFICATION_VERSION, fingerprint
from cfdc.kernel.controllers import ControllerIR

OFFLINE_QUALIFIED = "offline_qualified"
DIAGNOSTIC_TRIAL_ONLY = "diagnostic_trial_only"
NOT_QUALIFIED = "not_qualified"


def _feature_values(artifact: Mapping[str, Any]) -> dict[str, float]:
    result = {}
    for key, item in (artifact.get("features") or {}).items():
        if isinstance(item, Mapping) and isinstance(item.get("value"), (int, float)):
            result[str(key)] = float(item["value"])
    return result


def qualify_controller(
    controller: ControllerIR,
    *,
    task: Mapping[str, Any],
    route: Mapping[str, Any],
    feature_artifact: Mapping[str, Any],
    protocol: Mapping[str, Any],
) -> dict[str, Any]:
    reasons: list[str] = []
    checks: dict[str, str] = {}
    features = _feature_values(feature_artifact)
    if feature_artifact.get("missing_feature_ids") or not bool((feature_artifact.get("quality") or {}).get("passed", False)):
        reasons.append("required public features are missing or failed quality checks")
    lower, upper = controller.output_bounds or (float("nan"), float("nan"))
    bounds_ok = math.isfinite(lower) and math.isfinite(upper) and lower < upper
    if task.get("input_min") is not None:
        bounds_ok &= lower >= float(task["input_min"]) - 1e-12
    if task.get("input_max") is not None:
        bounds_ok &= upper <= float(task["input_max"]) + 1e-12
    checks["constraints"] = "pass" if bounds_ok else "fail"
    if not bounds_ok:
        reasons.append("controller output bounds exceed the declared task envelope")
    domains_ok = all(bounds[0] <= controller.parameters[name] <= bounds[1] for name, bounds in controller.parameter_domains.items())
    checks["parameter_domains"] = "pass" if domains_ok else "fail"
    if not domains_ok:
        reasons.append("one or more controller parameters are outside their frozen domains")
    uncertainty_ok = True
    worst_relative = 0.0
    for item in (feature_artifact.get("features") or {}).values():
        if not isinstance(item, Mapping):
            continue
        signed_value = float(item.get("value", 0.0))
        value = abs(signed_value)
        interval = item.get("uncertainty") or {}
        width = max(
            abs(float(interval.get("upper_bound", signed_value)) - signed_value),
            abs(signed_value - float(interval.get("lower_bound", signed_value))),
        )
        relative = width / max(value, 1e-6)
        worst_relative = max(worst_relative, relative)
        uncertainty_ok &= relative <= 1.0
    checks["evidence_uncertainty"] = "pass" if uncertainty_ok else "fail"
    if not uncertainty_ok:
        reasons.append("feature uncertainty is too wide for a bounded first trial")
    family = controller.family
    stability_ok = True
    recoverability = "pass"
    metrics: dict[str, Any] = {"worst_relative_feature_uncertainty": worst_relative}
    if family in {"decentralized_channel_PI", "static_decoupler_then_PI", "lag_dynamic_decoupler_then_PI"}:
        matrix = np.asarray([[features.get("local_gain_k11", 1.0), features.get("local_gain_k12", 0.0)], [features.get("local_gain_k21", 0.0), features.get("local_gain_k22", 1.0)]])
        condition = float(features.get("gain_matrix_condition", np.linalg.cond(matrix)))
        metrics["gain_matrix_condition"] = condition
        stability_ok = math.isfinite(condition) and condition <= 50.0 and abs(float(np.linalg.det(matrix))) > 1e-8
        if not stability_ok:
            reasons.append("the measured 2x2 gain map is singular or too ill-conditioned")
    elif family == "cascaded_control":
        required = {"unstable_mode_rate", "angular_input_gain"}
        stability_ok = required <= set(features)
        recoverability = "conditional"
        if not stability_ok:
            reasons.append("unstable balance route lacks internal-mode rate or input-gain evidence")
    elif family == "self_excitation_energy_guarded_PID":
        stability_ok = features.get("base_decay_rate", 0.0) > 0.0 or features.get("capture_damping", 0.0) > 0.0
        recoverability = "conditional"
        if not stability_ok:
            reasons.append("no positive capture or decay evidence supports the guarded handoff")
    else:
        gain = abs(features.get("static_gain", features.get("input_gain", features.get("acceleration_gain", 1.0))))
        bandwidth = abs(controller.parameters.get("target_bandwidth", controller.parameters.get("reference_filter_rate", 0.5)))
        loop_scale = gain * abs(controller.parameters.get("kp", controller.parameters.get("Kp_virtual", controller.parameters.get("gain", 1.0))))
        metrics.update(loop_scale=loop_scale, target_bandwidth_rad_s=bandwidth)
        stability_ok = math.isfinite(loop_scale) and math.isfinite(bandwidth) and loop_scale < 100.0 and bandwidth > 0.0
        if family in {"two_dof_PI", "phase_guarded_2dof_PI"}:
            guard = features.get("phase_guard_frequency", features.get("nmp_zero_rate_estimate"))
            if guard is not None:
                stability_ok &= bandwidth <= max(float(guard), 1e-6)
        if not stability_ok:
            reasons.append("conservative task-band loop screen failed")
    checks["stability"] = "pass" if stability_ok else "fail"
    checks["recoverability"] = recoverability
    hard_pass = not reasons and bounds_ok and domains_ok and uncertainty_ok and stability_ok
    if hard_pass:
        status = OFFLINE_QUALIFIED
        scope = ["isolated_software_evaluation", "bounded_first_trial_after_physical_preflight"]
        next_action = "freeze the qualified candidate and run an isolated evaluation"
    elif stability_ok and bounds_ok and domains_ok and not feature_artifact.get("missing_feature_ids"):
        status = DIAGNOSTIC_TRIAL_ONLY
        scope = ["isolated_software_diagnostic_evaluation"]
        next_action = "run software-only diagnostics or collect the named missing evidence"
    else:
        status = NOT_QUALIFIED
        scope = []
        next_action = "do not freeze; reduce bandwidth or collect the named evidence"
    result = {
        "qualification_version": QUALIFICATION_VERSION,
        "status": status,
        "limited_trial_authorized": status == OFFLINE_QUALIFIED,
        "authorization_scope": scope,
        "checks": checks,
        "metrics": metrics,
        "reasons": reasons,
        "next_action": next_action,
        "controller_fingerprint": controller.fingerprint,
        "feature_artifact_fingerprint": feature_artifact.get("artifact_fingerprint"),
        "protocol_fingerprint": protocol.get("protocol_fingerprint"),
        "route_id": route.get("route_id"),
        "claims_forbidden": ["physical safety certification", "global stability", "performance optimality"],
    }
    result["qualification_fingerprint"] = fingerprint(result)
    return result


__all__ = ["DIAGNOSTIC_TRIAL_ONLY", "NOT_QUALIFIED", "OFFLINE_QUALIFIED", "qualify_controller"]
