from __future__ import annotations

from typing import Any

from cfdc.runtime import run_cfdc_route

STABLE_DEMO_ROUTES = ("cartpole", "vtol-position", "vtol-boundary", "vtol-variation")


def _cartpole_result(report) -> dict[str, Any]:
    simulation = report.cartpole_simulation
    boundary = report.cartpole_boundary
    comparison = report.baseline_comparison
    metrics = simulation.metrics if simulation is not None else {}
    performance = simulation.performance if simulation is not None else None
    position = (
        performance.channels.get("cart_position") if performance is not None else None
    )
    angle = performance.channels.get("pole_angle") if performance is not None else None
    passed = bool(
        report.status == "demo_completed"
        and simulation is not None
        and simulation.success
        and performance is not None
        and performance.success
        and performance.capture_success is True
        and position is not None
        and position.settled
        and position.abs_final_error <= 0.02
        and angle is not None
        and angle.settled
        and angle.abs_final_error <= 0.12
        and performance.saturation_fraction
        <= performance.limits["max_force_saturation_fraction"]
        and simulation.max_abs_cart_position_m < 2.4
        and simulation.max_abs_force_n <= 10.0
        and boundary is not None
        and boundary.success
        and boundary.performance.boundary_triggered is True
        and boundary.rollback_applied
        and boundary.rollback_verified
        and boundary.rollback_trial is not None
        and boundary.rollback_trial.accepted
        and comparison is not None
        and comparison.same_plant
        and comparison.same_initial_state
        and comparison.same_reference
        and comparison.same_horizon
        and comparison.same_limits
        and comparison.cfdc_performance.success
        and comparison.baseline_performance.success
        and report.classification is not None
        and report.classification.required_core_features == ["natural_frequency"]
    )
    return {
        "route_id": report.route_id,
        "status": report.status,
        "passed": passed,
        "stop_reason": simulation.stop_reason if simulation is not None else "not_run",
        "final_gains": report.final_gains,
        "performance": performance.model_dump(mode="json")
        if performance is not None
        else None,
        "boundary": boundary.model_dump(
            mode="json",
            exclude={
                "candidate_trials": {"__all__": {"samples"}},
                "rollback_trial": {"samples"},
                "trajectory": True,
            },
        )
        if boundary is not None
        else None,
        "baseline_comparison": comparison.model_dump(mode="json")
        if comparison is not None
        else None,
        "metrics": metrics,
    }


def _vtol_result(report) -> dict[str, Any]:
    simulation = report.vtol_simulation
    metrics = simulation.metrics if simulation is not None else {}
    performance = simulation.performance if simulation is not None else None
    comparison = report.baseline_comparison
    if report.route_id == "vtol-variation":
        variation = report.vtol_variation
        updated = (
            [
                scenario
                for scenario in variation.scenarios
                if scenario.feature_source == "updated"
            ]
            if variation is not None
            else []
        )
        passed = bool(
            report.status == "demo_completed"
            and variation is not None
            and variation.success
            and len(variation.scenarios) == 6
            and variation.updated_scenario_count == 4
            and variation.stale_scenario_count == 2
            and all(scenario.expectation_met for scenario in variation.scenarios)
            and all(
                scenario.simulation.success
                and all(
                    scenario.simulation.performance.channels[channel].settled
                    for channel in ["lateral_position", "altitude", "attitude"]
                )
                for scenario in updated
            )
        )
        return {
            "route_id": report.route_id,
            "status": report.status,
            "passed": passed,
            "stop_reason": "variation_complete" if variation is not None else "not_run",
            "final_gains": report.final_gains,
            "performance": performance.model_dump(mode="json")
            if performance is not None
            else None,
            "variation": variation.model_dump(
                mode="json",
                exclude={"scenarios": {"__all__": {"simulation": {"trajectory"}}}},
            )
            if variation is not None
            else None,
            "metrics": metrics,
        }
    if report.route_id == "vtol-position":
        lateral = (
            performance.channels.get("lateral_position")
            if performance is not None
            else None
        )
        altitude = (
            performance.channels.get("altitude") if performance is not None else None
        )
        attitude = (
            performance.channels.get("attitude") if performance is not None else None
        )
        passed = bool(
            report.status == "demo_completed"
            and simulation is not None
            and simulation.success
            and performance is not None
            and performance.success
            and lateral is not None
            and altitude is not None
            and attitude is not None
            and lateral.settled
            and altitude.settled
            and attitude.settled
            and lateral.abs_final_error < 0.18
            and altitude.abs_final_error < 0.08
            and not performance.violations
            and comparison is not None
            and comparison.same_plant
            and comparison.same_initial_state
            and comparison.same_reference
            and comparison.same_horizon
            and comparison.same_limits
            and comparison.cfdc_performance.success
            and comparison.baseline_performance.success
        )
    else:
        channels_settled = bool(
            performance is not None
            and all(
                performance.channels[channel].settled
                for channel in ["lateral_position", "altitude", "attitude"]
            )
        )
        passed = bool(
            report.status == "demo_completed"
            and simulation is not None
            and simulation.success
            and performance is not None
            and performance.success
            and metrics.get("boundary_reason") == "nmp_undershoot"
            and float(metrics.get("boundary_nmp_undershoot", 0.0)) >= 0.15
            and float(metrics.get("nmp_undershoot", float("inf"))) < 0.15
            and metrics.get("rollback_applied") is True
            and channels_settled
            and not performance.violations
        )
    return {
        "route_id": report.route_id,
        "status": report.status,
        "passed": passed,
        "stop_reason": simulation.stop_reason if simulation is not None else "not_run",
        "final_gains": report.final_gains,
        "performance": performance.model_dump(mode="json")
        if performance is not None
        else None,
        "baseline_comparison": comparison.model_dump(mode="json")
        if comparison is not None
        else None,
        "metrics": metrics,
    }


def run_demo_validation() -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    for route_id in STABLE_DEMO_ROUTES:
        report = run_cfdc_route(
            route_id, include_trajectory=False, run_id=f"stable-demo-{route_id}"
        )
        result = (
            _cartpole_result(report) if route_id == "cartpole" else _vtol_result(report)
        )
        results.append(result)
    return {
        "validation_scope": "stable_software_demo",
        "route_count": len(results),
        "passed_count": sum(1 for result in results if result["passed"]),
        "passed": all(result["passed"] for result in results),
        "results": results,
    }
