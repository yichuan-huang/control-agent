from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from cfdc.diagnosis import DiagnosticEngine
from cfdc.experiments import plan_safe_experiments
from cfdc.features import extract_features_from_results
from cfdc.models import ControllerCandidate, CoreFeatureArtifact, ExperimentResult, ExperimentTrace, SystemDescription
from cfdc.controllers import synthesize_controller
from cfdc.sim.traces import (
    bounded_scan_trace,
    hover_trace,
    modal_trace,
    pulse_trace,
    step_trace,
    vtol_pulse_trace,
)


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
            params={"static_gain": 1.0, "time_constant": 6.0, "inverse_response_severity": 0.25},
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
            params={"hover_thrust": 11.77, "angular_acceleration_gain": 28.57, "lateral_coupling_gain": -9.81},
            safety_limits={"max_tilt_rad": 0.26, "max_torque": 0.9, "gravity": 9.81},
        ),
    ]


def _extract_required_features(case: BenchmarkCase, required: list[str]) -> list[CoreFeatureArtifact]:
    params = case.params
    results: list[ExperimentResult] = []
    if {"static_gain", "time_constant"} & set(required):
        t, u, y = step_trace(
            params.get("static_gain", 1.0),
            params.get("time_constant", 5.0),
            params.get("dead_time", 0.0),
            inverse_response_severity=params.get("inverse_response_severity", 0.0),
        )
        estimates = [
            feature_id
            for feature_id in ["static_gain", "time_constant", "dead_time", "inverse_response_severity"]
            if feature_id in required
        ]
        results.append(
            ExperimentResult(
                primitive="ramp_step",
                estimates=estimates,
                trace=ExperimentTrace(
                    time_s=t.tolist(),
                    signals={"input setting": u.tolist(), "measured output": y.tolist()},
                ),
            )
        )
    if "natural_frequency" in required or "damping_ratio" in required:
        t, y = modal_trace(params.get("natural_frequency", 3.0), params.get("damping_ratio", 0.08))
        estimates = [feature_id for feature_id in ["natural_frequency", "damping_ratio"] if feature_id in required]
        results.append(
            ExperimentResult(
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
            ExperimentResult(
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
            ExperimentResult(
                primitive="hover_thrust",
                estimates=["hover_thrust"],
                trace=ExperimentTrace(
                    time_s=t.tolist(),
                    signals={"lift setting": thrust.tolist(), "vertical motion": lift.tolist()},
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
            ExperimentResult(
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
        t, input_signal, primary, coupled = bounded_scan_trace(params.get("coupling_gain", 0.5))
        results.append(
            ExperimentResult(
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


def run_benchmark_case(case: BenchmarkCase) -> dict[str, Any]:
    engine = DiagnosticEngine()
    diagnosis = engine.diagnose(case.description)
    classification = engine.classify(diagnosis)
    plan = plan_safe_experiments(diagnosis, classification)
    features = _extract_required_features(case, classification.required_core_features)
    controller = synthesize_controller(classification, features, case.safety_limits)
    feature_ids = {feature.feature_id for feature in features}
    required = set(classification.required_core_features)
    return {
        "case_id": case.case_id,
        "diagnosis_complete": diagnosis.complete,
        "archetype": classification.primary_class,
        "planned_experiment_count": len(plan.instructions),
        "feature_ids": sorted(feature_ids),
        "required_feature_ids": sorted(required),
        "features_cover_required": required.issubset(feature_ids),
        "controller": controller.model_dump(),
        "success": diagnosis.complete and required.issubset(feature_ids) and controller.status != "refuse",
        "validation_scope": "feature_chain_smoke",
        "closed_loop_executed": False,
        "evidence_boundary": "synthetic_feature_chain_only_not_physical_validation",
    }


def run_benchmark_suite() -> dict[str, Any]:
    rows = [run_benchmark_case(case) for case in list_benchmark_cases()]
    return {
        "case_count": len(rows),
        "success_count": sum(1 for row in rows if row["success"]),
        "validation_scope": "feature_chain_smoke",
        "closed_loop_executed": False,
        "results": rows,
    }
