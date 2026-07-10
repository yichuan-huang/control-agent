from __future__ import annotations

from typing import Any

from cfdc.runtime import run_cfdc_route


STABLE_DEMO_ROUTES = ("cartpole", "vtol-position", "vtol-boundary")


def _cartpole_result(report) -> dict[str, Any]:
    simulation = report.cartpole_simulation
    metrics = simulation.metrics if simulation is not None else {}
    performance = simulation.performance if simulation is not None else None
    passed = bool(
        report.status == "completed"
        and simulation is not None
        and simulation.success
        and performance is not None
        and performance.success
        and performance.capture_success is True
        and performance.saturation_fraction <= performance.limits["max_force_saturation_fraction"]
        and simulation.max_abs_cart_position_m < 2.4
        and simulation.max_abs_force_n <= 10.0
        and report.classification is not None
        and report.classification.required_core_features == ["natural_frequency"]
    )
    return {
        "route_id": report.route_id,
        "status": report.status,
        "passed": passed,
        "stop_reason": simulation.stop_reason if simulation is not None else "not_run",
        "final_gains": report.final_gains,
        "performance": performance.model_dump(mode="json") if performance is not None else None,
        "metrics": metrics,
    }


def _vtol_result(report) -> dict[str, Any]:
    simulation = report.vtol_simulation
    metrics = simulation.metrics if simulation is not None else {}
    performance = simulation.performance if simulation is not None else None
    if report.route_id == "vtol-position":
        lateral = performance.channels.get("lateral_position") if performance is not None else None
        altitude = performance.channels.get("altitude") if performance is not None else None
        passed = bool(
            report.status == "completed"
            and simulation is not None
            and simulation.success
            and performance is not None
            and performance.success
            and lateral is not None
            and altitude is not None
            and lateral.abs_final_error < 0.18
            and altitude.abs_final_error < 0.08
        )
    else:
        passed = bool(
            report.status == "completed"
            and simulation is not None
            and simulation.success
            and performance is not None
            and performance.success
            and metrics.get("boundary_reason") == "nmp_undershoot"
            and float(metrics.get("boundary_nmp_undershoot", 0.0)) >= 0.15
            and float(metrics.get("nmp_undershoot", float("inf"))) < 0.15
            and metrics.get("rollback_applied") is True
        )
    return {
        "route_id": report.route_id,
        "status": report.status,
        "passed": passed,
        "stop_reason": simulation.stop_reason if simulation is not None else "not_run",
        "final_gains": report.final_gains,
        "performance": performance.model_dump(mode="json") if performance is not None else None,
        "metrics": metrics,
    }


def run_demo_validation() -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    for route_id in STABLE_DEMO_ROUTES:
        report = run_cfdc_route(route_id, include_trajectory=False, run_id=f"stable-demo-{route_id}")
        result = _cartpole_result(report) if route_id == "cartpole" else _vtol_result(report)
        results.append(result)
    return {
        "validation_scope": "stable_software_demo",
        "route_count": len(results),
        "passed_count": sum(1 for result in results if result["passed"]),
        "passed": all(result["passed"] for result in results),
        "results": results,
    }
