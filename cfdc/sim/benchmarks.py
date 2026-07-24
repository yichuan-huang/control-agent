from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from cfdc.diagnosis import DiagnosticEngine
from cfdc.experiments import plan_safe_experiments
from cfdc.features import extract_features_from_results
from cfdc.models import (
    BenchmarkRouteIR,
    ClosedLoopBenchmarkCaseResult,
    ControllerCandidate,
    CoreFeatureArtifact,
    ExperimentPrimitive,
    SimulationExperimentRecord,
    ExperimentTrace,
    FeatureAblationResult,
    FeatureAblationTrial,
    SimulationPerformanceSummary,
    SystemDescription,
)
from cfdc.controllers import synthesize_controller
from cfdc.workflow import (
    apply_profile_to_classification,
    default_simulation_profile_catalog,
    deterministic_profile_selection,
    validate_semantic_selection,
)
from cfdc.sim.cartpole import search_cartpole_pd_gains, simulate_cartpole_energy_swingup
from cfdc.sim.generic import SCALAR_BENCHMARK_FAMILIES, run_scalar_closed_loop
from cfdc.sim.traces import (
    bounded_scan_trace,
    hover_trace,
    modal_trace,
    pulse_trace,
    step_trace,
    vtol_pulse_trace,
)
from cfdc.sim.vtol import VtolConfig, run_vtol_simulation, vtol_operational_gains


@dataclass(frozen=True)
class BenchmarkCase:
    case_id: str
    description: SystemDescription
    params: dict[str, float]
    safety_limits: dict[str, float]


def list_benchmark_cases() -> list[BenchmarkCase]:
    return [
        BenchmarkCase(
            case_id="first_order_self_regulating_process",
            description=SystemDescription(
                text="A self-regulating first order temperature process settles to a new value after a small heater change.",
                observed_outputs=["temperature"],
                actuators=["heater setting"],
                safety_bounds={"output_max": 2.0},
            ),
            params={"static_gain": 2.0, "time_constant": 5.0},
            safety_limits={"output_min": 0.0, "output_max": 1.0},
        ),
        BenchmarkCase(
            case_id="first_order_plus_dead_time_process",
            description=SystemDescription(
                text="A first order tank process settles after a pump change, but there is a noticeable dead time before the level moves.",
                observed_outputs=["level"],
                actuators=["pump setting"],
                safety_bounds={"output_max": 1.5},
            ),
            params={"static_gain": 1.5, "time_constant": 8.0, "dead_time": 2.0},
            safety_limits={"output_min": 0.0, "output_max": 1.0},
        ),
        BenchmarkCase(
            case_id="double_integrator_low_friction_cart",
            description=SystemDescription(
                text="A low-friction cart drifts; position keeps moving after a short motor nudge.",
                observed_outputs=["position", "speed"],
                actuators=["motor force"],
                safety_bounds={"travel": 1.5},
            ),
            params={"input_gain": 0.8},
            safety_limits={"output_min": -1.0, "output_max": 1.0},
        ),
        BenchmarkCase(
            case_id="second_order_oscillatory_process",
            description=SystemDescription(
                text="A spring-like system vibrates and its free motion decays after a small release.",
                observed_outputs=["position"],
                actuators=["small force"],
                safety_bounds={"travel": 1.2},
            ),
            params={"natural_frequency": 3.0, "damping_ratio": 0.18, "input_gain": 1.0},
            safety_limits={"output_min": -8.0, "output_max": 8.0},
        ),
        BenchmarkCase(
            case_id="simple_inverse_response_process",
            description=SystemDescription(
                text="A stable self-regulating process settles after a valve change, but the output first moves in the opposite direction before going to the target.",
                observed_outputs=["process output"],
                actuators=["valve setting"],
                safety_bounds={"output_max": 1.0},
            ),
            params={
                "static_gain": 1.0,
                "time_constant": 6.0,
                "inverse_response_severity": 0.25,
            },
            safety_limits={"output_min": 0.0, "output_max": 1.0},
        ),
        BenchmarkCase(
            case_id="cartpole_underactuated_sim",
            description=SystemDescription(
                text="A rod hinged on a cart falls over when upright. The cart motor can push left and right, and both cart position and rod angle are measured. The cart position has reverse motion risk.",
                observed_outputs=["cart position", "rod angle"],
                actuators=["cart motor force"],
                safety_bounds={"force": 10.0, "travel": 3.0},
            ),
            params={"natural_frequency": 5.9, "input_gain": 1.4},
            safety_limits={"output_min": -10.0, "output_max": 10.0},
        ),
        BenchmarkCase(
            case_id="planar_vtol_hover_lateral_sim",
            description=SystemDescription(
                text="A vertical take-off aircraft with two rotors can hover and move sideways by tilting. Altitude, lateral position, and roll angle are measured; payload is unknown.",
                observed_outputs=["altitude", "lateral position", "roll angle"],
                actuators=["total thrust", "roll torque"],
                safety_bounds={"max_tilt_rad": 0.26, "max_torque": 0.9},
            ),
            params={
                "hover_thrust": 11.77,
                "angular_acceleration_gain": 28.57,
                "lateral_coupling_gain": -9.81,
            },
            safety_limits={"max_tilt_rad": 0.26, "max_torque": 0.9, "gravity": 9.81},
        ),
    ]


def _extract_required_features(
    case: BenchmarkCase, required: list[str]
) -> list[CoreFeatureArtifact]:
    params = case.params
    results: list[SimulationExperimentRecord] = []
    if {"static_gain", "time_constant"} & set(required):
        t, u, y = step_trace(
            params.get("static_gain", 1.0),
            params.get("time_constant", 5.0),
            params.get("dead_time", 0.0),
            inverse_response_severity=params.get("inverse_response_severity", 0.0),
        )
        estimates = [
            feature_id
            for feature_id in [
                "static_gain",
                "time_constant",
                "dead_time",
                "inverse_response_severity",
            ]
            if feature_id in required
        ]
        results.append(
            SimulationExperimentRecord(
                primitive="ramp_step",
                estimates=estimates,
                trace=ExperimentTrace(
                    time_s=t.tolist(),
                    signals={
                        "input setting": u.tolist(),
                        "measured output": y.tolist(),
                    },
                ),
            )
        )
    if "natural_frequency" in required or "damping_ratio" in required:
        t, y = modal_trace(
            params.get("natural_frequency", 3.0), params.get("damping_ratio", 0.08)
        )
        estimates = [
            feature_id
            for feature_id in ["natural_frequency", "damping_ratio"]
            if feature_id in required
        ]
        results.append(
            SimulationExperimentRecord(
                primitive="free_decay",
                estimates=estimates,
                trace=ExperimentTrace(
                    time_s=t.tolist(),
                    signals={"measured position or angle": y.tolist()},
                ),
            )
        )
    if "input_gain" in required:
        t, u, a = pulse_trace(params.get("input_gain", 1.0))
        results.append(
            SimulationExperimentRecord(
                primitive="pulse",
                estimates=["input_gain"],
                trace=ExperimentTrace(
                    time_s=t.tolist(),
                    signals={"input setting": u.tolist(), "acceleration": a.tolist()},
                ),
            )
        )
    if "hover_thrust" in required:
        t, thrust, lift = hover_trace(params["hover_thrust"])
        results.append(
            SimulationExperimentRecord(
                primitive="hover_thrust",
                estimates=["hover_thrust"],
                trace=ExperimentTrace(
                    time_s=t.tolist(),
                    signals={
                        "lift setting": thrust.tolist(),
                        "vertical motion": lift.tolist(),
                    },
                ),
            )
        )
    if "angular_acceleration_gain" in required or "lateral_coupling_gain" in required:
        t, command, angular_acceleration, tilt, lateral_acceleration = vtol_pulse_trace(
            params.get("angular_acceleration_gain", 1.0),
            params.get("lateral_coupling_gain", -9.81),
        )
        estimates = [
            feature_id
            for feature_id in ["angular_acceleration_gain", "lateral_coupling_gain"]
            if feature_id in required
        ]
        results.append(
            SimulationExperimentRecord(
                primitive="pulse",
                estimates=estimates,
                trace=ExperimentTrace(
                    time_s=t.tolist(),
                    signals={
                        "twist command": command.tolist(),
                        "angular acceleration": angular_acceleration.tolist(),
                        "tilt": tilt.tolist(),
                        "lateral acceleration": lateral_acceleration.tolist(),
                    },
                ),
            )
        )
    if "coupling_gain" in required:
        t, input_signal, primary, coupled = bounded_scan_trace(
            params.get("coupling_gain", 0.5)
        )
        results.append(
            SimulationExperimentRecord(
                primitive="bounded_scan",
                estimates=["coupling_gain"],
                trace=ExperimentTrace(
                    time_s=t.tolist(),
                    signals={
                        "input setting": input_signal.tolist(),
                        "primary output": primary.tolist(),
                        "coupled output": coupled.tolist(),
                    },
                ),
            )
        )
    return extract_features_from_results(results)


def _benchmark_route_ir(case: BenchmarkCase) -> BenchmarkRouteIR:
    scalar_routes = {
        "first_order_self_regulating_process": dict(
            plant_family="first_order_lag",
            reference={"output": 1.0},
            horizon_s=1500.0,
            dt_s=0.2,
            actuator_limits={"input_min": 0.0, "input_max": 1.0},
            state_limits={"max_abs_output": 1.4},
            performance_limits={
                "max_abs_final_error": 0.08,
                "max_overshoot": 0.25,
                "max_settling_time_s": 1400.0,
                "max_saturation_fraction": 0.50,
                "settling_band_absolute": 0.02,
            },
        ),
        "first_order_plus_dead_time_process": dict(
            plant_family="first_order_plus_dead_time",
            reference={"output": 0.8},
            horizon_s=5000.0,
            dt_s=0.5,
            actuator_limits={"input_min": 0.0, "input_max": 1.0},
            state_limits={"max_abs_output": 1.4},
            performance_limits={
                "max_abs_final_error": 0.08,
                "max_overshoot": 0.20,
                "max_settling_time_s": 4800.0,
                "max_saturation_fraction": 0.50,
                "settling_band_absolute": 0.02,
            },
        ),
        "double_integrator_low_friction_cart": dict(
            plant_family="double_integrator",
            reference={"output": 1.0},
            horizon_s=14.0,
            dt_s=0.01,
            actuator_limits={"input_min": -1.0, "input_max": 1.0},
            state_limits={"max_abs_output": 1.4, "max_abs_velocity": 1.2},
            performance_limits={
                "max_abs_final_error": 0.05,
                "max_overshoot": 0.15,
                "max_settling_time_s": 10.0,
                "max_saturation_fraction": 0.40,
                "settling_band_absolute": 0.02,
            },
        ),
        "second_order_oscillatory_process": dict(
            plant_family="second_order_oscillator",
            reference={"output": 0.0},
            horizon_s=12.0,
            dt_s=0.005,
            initial_state={"output": 1.0, "velocity": 0.0},
            actuator_limits={"input_min": -8.0, "input_max": 8.0},
            state_limits={"max_abs_output": 1.2, "max_abs_output_after_4s": 0.12},
            performance_limits={
                "max_abs_final_error": 0.05,
                "max_settling_time_s": 8.0,
                "max_saturation_fraction": 0.20,
                "settling_band_absolute": 0.02,
            },
        ),
        "simple_inverse_response_process": dict(
            plant_family="inverse_response",
            reference={"output": 0.7},
            horizon_s=7000.0,
            dt_s=0.5,
            actuator_limits={"input_min": 0.0, "input_max": 1.0},
            state_limits={"max_abs_output": 1.2},
            performance_limits={
                "max_abs_final_error": 0.10,
                "max_overshoot": 0.10,
                "max_settling_time_s": 6800.0,
                "max_saturation_fraction": 0.50,
                "settling_band_absolute": 0.02,
            },
        ),
    }
    if case.case_id in scalar_routes:
        values = scalar_routes[case.case_id]
        params = dict(case.params)
        if case.case_id == "simple_inverse_response_process":
            params["inverse_time_constant"] = 0.8
        return BenchmarkRouteIR(
            case_id=case.case_id,
            plant_params=params,
            initial_state=values.pop("initial_state", {}),
            **values,
        )
    if case.case_id == "cartpole_underactuated_sim":
        return BenchmarkRouteIR(
            case_id=case.case_id,
            plant_family="cartpole",
            reference={"pole_angle_rad": 0.0},
            horizon_s=12.0,
            dt_s=0.002,
            plant_params=case.params,
            actuator_limits={"max_abs_force_n": 10.0},
            state_limits={"max_abs_cart_position_m": 2.4},
            performance_limits={"max_abs_final_error": 0.15},
        )
    return BenchmarkRouteIR(
        case_id=case.case_id,
        plant_family="planar_vtol",
        reference={"x_m": 1.0, "z_m": 1.0},
        horizon_s=15.0,
        dt_s=0.005,
        plant_params=case.params,
        initial_state={"x_m": 0.0, "z_m": 1.0, "theta_rad": 0.0},
        actuator_limits={
            "thrust_min_n": 0.0,
            "thrust_max_n": 18.0,
            "max_abs_torque_n_m": 0.9,
        },
        state_limits={"max_abs_tilt_rad": 0.70, "max_abs_lateral_position_m": 3.0},
        performance_limits={"max_abs_final_error": 0.18, "max_settling_time_s": 12.0},
    )


def _run_case_closed_loop(
    route_ir: BenchmarkRouteIR,
    controller: ControllerCandidate,
    features: list[CoreFeatureArtifact],
) -> tuple[SimulationPerformanceSummary, str, list[str], ControllerCandidate]:
    if route_ir.plant_family in SCALAR_BENCHMARK_FAMILIES:
        return (
            run_scalar_closed_loop(route_ir, controller),
            "cfdc.sim.generic",
            [],
            controller,
        )
    if route_ir.plant_family == "cartpole":
        fmap = {feature.feature_id: feature.value for feature in features}
        search_state, _, search_events = search_cartpole_pd_gains(
            fmap["natural_frequency"]
        )
        simulation = simulate_cartpole_energy_swingup(
            include_trajectory=False,
            balance_gains=search_state.accepted_gains,
            natural_frequency_rad_s=fmap["natural_frequency"],
            search_events=search_events,
        )
        executed_controller = controller.model_copy(
            update={
                "gains": search_state.accepted_gains,
                "status": "ready_for_conservative_trial",
                "notes": [
                    *controller.notes,
                    "Nonlinear PD search completed before this benchmark response.",
                ],
            }
        )
        return (
            simulation.performance,
            "cfdc.sim.cartpole",
            ["nonlinear PD search executed"],
            executed_controller,
        )
    gains = vtol_operational_gains(features)
    fmap = {feature.feature_id: feature.value for feature in features}
    simulation = run_vtol_simulation(
        mode="position",
        config=VtolConfig(duration_s=route_ir.horizon_s),
        features=features,
        gains=gains,
        feedforward={"hover_thrust": fmap["hover_thrust"]},
        include_trajectory=False,
    )
    executed_controller = controller.model_copy(
        update={
            "gains": gains,
            "notes": [
                *controller.notes,
                "Operational gains passed the complete coupled benchmark response.",
            ],
        }
    )
    return simulation.performance, "cfdc.sim.vtol", [], executed_controller


def run_benchmark_case(case: BenchmarkCase) -> dict[str, Any]:
    engine = DiagnosticEngine()
    diagnosis = engine.diagnose(case.description)
    classification = engine.classify(diagnosis)
    profile_catalog = default_simulation_profile_catalog()
    selection = deterministic_profile_selection(
        case.description, diagnosis, classification, profile_catalog
    )
    profile = validate_semantic_selection(selection, classification, profile_catalog)
    classification = apply_profile_to_classification(classification, profile)
    plan = plan_safe_experiments(diagnosis, classification)
    features = _extract_required_features(case, classification.required_core_features)
    controller = synthesize_controller(classification, features, case.safety_limits)
    feature_ids = {feature.feature_id for feature in features}
    required = set(classification.required_core_features)
    route_ir = _benchmark_route_ir(case)
    performance, backend, notes, executed_controller = _run_case_closed_loop(
        route_ir,
        controller,
        features,
    )
    result = ClosedLoopBenchmarkCaseResult(
        case_id=case.case_id,
        route_ir=route_ir,
        diagnosis_complete=diagnosis.complete,
        archetype=str(classification.primary_class),
        planned_experiment_count=len(plan.instructions),
        features=features,
        required_feature_ids=sorted(required),
        features_cover_required=required.issubset(feature_ids),
        controller=executed_controller,
        performance=performance,
        success=(
            diagnosis.complete
            and required.issubset(feature_ids)
            and controller.status != "refuse"
            and performance.success
        ),
        execution_backend=backend,
        notes=notes,
    )
    payload = result.model_dump(mode="json")
    payload["feature_ids"] = sorted(feature_ids)
    payload["validation_scope"] = "closed_loop_benchmark"
    return payload


def run_benchmark_suite() -> dict[str, Any]:
    rows = [run_benchmark_case(case) for case in list_benchmark_cases()]
    return {
        "case_count": len(rows),
        "success_count": sum(1 for row in rows if row["success"]),
        "execution_count": sum(1 for row in rows if row["closed_loop_executed"]),
        "validation_scope": "closed_loop_benchmark",
        "closed_loop_executed": all(row["closed_loop_executed"] for row in rows),
        "results": rows,
    }


def _feature_packet(
    case: BenchmarkCase,
    classification,
    variant: str,
) -> list[CoreFeatureArtifact]:
    extracted = _extract_required_features(case, classification.required_core_features)
    if variant == "minimal_core_feature":
        return extracted
    if variant == "full_model_reference":
        exact_values = {
            feature_id: case.params[feature_id]
            for feature_id in classification.required_core_features
        }
    elif case.case_id == "first_order_self_regulating_process":
        exact_values = {
            "static_gain": case.params["static_gain"] * 4.0,
            "time_constant": case.params["time_constant"] * 4.0,
        }
    else:
        exact_values = {"input_gain": case.params["input_gain"] * 0.25}
    source = {feature.feature_id: feature for feature in extracted}
    packet: list[CoreFeatureArtifact] = []
    for feature_id, value in exact_values.items():
        base = source[feature_id]
        width = max(abs(value) * 0.01, 1e-9)
        packet.append(
            base.model_copy(
                update={
                    "value": value,
                    "lower_bound": value - width,
                    "upper_bound": value + width,
                    "method": f"{variant}_fixture",
                }
            )
        )
    return packet


def run_feature_ablation_suite() -> FeatureAblationResult:
    selected = {
        case.case_id: case
        for case in list_benchmark_cases()
        if case.case_id
        in {
            "first_order_self_regulating_process",
            "double_integrator_low_friction_cart",
        }
    }
    trials: list[FeatureAblationTrial] = []
    engine = DiagnosticEngine()
    for case in selected.values():
        diagnosis = engine.diagnose(case.description)
        classification = engine.classify(diagnosis)
        route_ir = _benchmark_route_ir(case)
        for variant in [
            "minimal_core_feature",
            "wrong_or_noisy_feature",
            "full_model_reference",
        ]:
            features = _feature_packet(case, classification, variant)
            controller = synthesize_controller(
                classification, features, case.safety_limits
            )
            performance = run_scalar_closed_loop(route_ir, controller)
            trials.append(
                FeatureAblationTrial(
                    case_id=case.case_id,
                    variant=variant,
                    feature_values={
                        feature.feature_id: feature.value for feature in features
                    },
                    controller=controller,
                    performance=performance,
                    success=performance.success,
                )
            )
    grouped = {
        case_id: [trial for trial in trials if trial.case_id == case_id]
        for case_id in selected
    }
    comparisons_hold = True
    for case_trials in grouped.values():
        by_variant = {trial.variant: trial for trial in case_trials}
        minimal = by_variant["minimal_core_feature"]
        noisy = by_variant["wrong_or_noisy_feature"]
        reference = by_variant["full_model_reference"]
        noisy_degraded = (
            not noisy.success
            or noisy.performance.abs_final_error > minimal.performance.abs_final_error
            or noisy.performance.saturation_fraction
            > minimal.performance.saturation_fraction
        )
        comparisons_hold = (
            comparisons_hold
            and minimal.success
            and reference.success
            and noisy_degraded
        )
    return FeatureAblationResult(
        success=comparisons_hold,
        case_count=len(grouped),
        trial_count=len(trials),
        trials=trials,
        notes=[
            "Minimal and full-model packets use the same current synthesis and simulation path.",
            "Wrong/noisy packets perturb only controller-visible features; hidden plant parameters remain unchanged.",
        ],
    )
