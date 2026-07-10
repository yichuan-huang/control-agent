from __future__ import annotations

from typing import Literal
from uuid import uuid4

import numpy as np

from cfdc.controllers import synthesize_controller
from cfdc.diagnosis import DiagnosticEngine
from cfdc.diagnosis.llm import DiagnosticAdapter
from cfdc.experiments import plan_safe_experiments
from cfdc.features import extract_features_from_results
from cfdc.models import (
    CFDCRunReport,
    ControllerCandidate,
    CoreFeatureArtifact,
    ExperimentPlan,
    ExperimentPrimitive,
    ExperimentResult,
    ExperimentTrace,
    GoNoGoDecision,
    OnlineTuningState,
    StructuralDiagnosis,
    SystemDescription,
    TrialReport,
)
from cfdc.online import (
    refine_gains_once,
)
from cfdc.runtime.trial import SafeTrialConfig, SafeTrialRunner
from cfdc.sim import (
    CartpoleParams,
    VtolConfig,
    VtolParams,
    run_vtol_simulation,
    search_cartpole_pd_gains,
    simulate_cartpole_energy_swingup,
)
from cfdc.sim.traces import hover_trace, modal_trace, pulse_trace, vtol_pulse_trace
from cfdc.validation import merge_go_no_go, validate_required_features, validate_route_compatibility


RouteId = Literal[
    "generic",
    "cartpole",
    "vtol-position",
    "vtol-boundary",
    "vtol-altitude",
    "vtol-hover",
]


def _cartpole_description() -> SystemDescription:
    return SystemDescription(
        text=(
            "A rod hinged on a cart falls over when upright. The cart motor can push left "
            "and right, and both cart position and rod angle are measured. The cart has "
            "limited travel and the motor has a bounded force."
        ),
        observed_outputs=["cart position", "rod angle"],
        actuators=["cart motor force"],
        safety_bounds={"max_abs_position": 2.4, "max_abs_control": 10.0},
    )


def _vtol_description() -> SystemDescription:
    return SystemDescription(
        text=(
            "A vertical take-off aircraft with two rotors can hover and move sideways by "
            "tilting. Altitude, lateral position, and roll angle are measured; payload is "
            "unknown and can change."
        ),
        observed_outputs=["altitude", "lateral position", "roll angle"],
        actuators=["total thrust", "roll torque"],
        safety_bounds={"max_tilt_rad": 0.70, "max_torque": 0.9, "gravity": 9.81},
    )


def _default_description(route_id: RouteId) -> SystemDescription:
    if route_id == "cartpole":
        return _cartpole_description()
    if route_id.startswith("vtol"):
        return _vtol_description()
    return SystemDescription(
        text="A self-regulating first order process settles after a small input change.",
        observed_outputs=["measured output"],
        actuators=["small input setting"],
    )


def _free_decay_result(
    omega_rad_s: float,
    feature_ids: list[str],
    damping_ratio: float = 0.08,
    duration_s: float = 8.0,
    sample_count: int = 1600,
) -> ExperimentResult:
    time_s, signal = modal_trace(
        omega_rad_s,
        damping_ratio,
        duration_s,
        sample_count,
    )
    return ExperimentResult(
        primitive=ExperimentPrimitive.FREE_DECAY,
        estimates=feature_ids,
        trace=ExperimentTrace(
            time_s=time_s.tolist(),
            signals={"measured position or angle": signal.tolist()},
        ),
        instruction_title="Synthetic safe resting-motion recording",
    )


def _pulse_result(
    gain: float,
    feature_id: str = "input_gain",
    duration_s: float = 3.0,
    sample_count: int = 900,
) -> ExperimentResult:
    time_s, input_signal, acceleration = pulse_trace(gain, duration_s, sample_count)
    return ExperimentResult(
        primitive=ExperimentPrimitive.PULSE,
        estimates=[feature_id],
        trace=ExperimentTrace(
            time_s=time_s.tolist(),
            signals={"input setting": input_signal.tolist(), "acceleration": acceleration.tolist()},
        ),
        instruction_title="Synthetic brief nudge recording",
    )


def _cartpole_experiment_results(required_features: list[str]) -> list[ExperimentResult]:
    params = CartpoleParams()
    results: list[ExperimentResult] = []
    modal_features = [feature for feature in ["natural_frequency", "damping_ratio"] if feature in required_features]
    if modal_features:
        results.append(
            _free_decay_result(
                params.free_cart_natural_frequency_down_rad_s,
                modal_features,
                damping_ratio=0.08,
            )
        )
    if "input_gain" in required_features:
        cart_acceleration_gain = 1.0 / (params.cart_mass_kg + params.pole_mass_kg)
        results.append(_pulse_result(cart_acceleration_gain))
    return results


def _vtol_experiment_results(required_features: list[str]) -> list[ExperimentResult]:
    params = VtolParams()
    results: list[ExperimentResult] = []
    if "hover_thrust" in required_features:
        time_s, thrust, lift = hover_trace(params.hover_thrust_n)
        results.append(
            ExperimentResult(
                primitive=ExperimentPrimitive.HOVER_THRUST,
                estimates=["hover_thrust"],
                trace=ExperimentTrace(
                    time_s=time_s.tolist(),
                    signals={"lift setting": thrust.tolist(), "vertical motion": lift.tolist()},
                ),
                instruction_title="Synthetic light-on-supports recording",
            )
        )
    pulse_features = [
        feature
        for feature in ["angular_acceleration_gain", "lateral_coupling_gain"]
        if feature in required_features
    ]
    if pulse_features:
        time_s, command, angular_acceleration, tilt, lateral_acceleration = vtol_pulse_trace(
            1.0 / params.pitch_inertia_kg_m2,
            -params.gravity_m_s2,
        )
        results.append(
            ExperimentResult(
                primitive=ExperimentPrimitive.PULSE,
                estimates=pulse_features,
                trace=ExperimentTrace(
                    time_s=time_s.tolist(),
                    signals={
                        "twist command": command.tolist(),
                        "angular acceleration": angular_acceleration.tolist(),
                        "tilt": tilt.tolist(),
                        "lateral acceleration": lateral_acceleration.tolist(),
                    },
                ),
                instruction_title="Synthetic small twist recording",
            )
        )
    return results


def _status_from_simulation(success: bool, trial_reports: list[TrialReport]) -> str:
    if any(not report.accepted for report in trial_reports):
        return "rejected"
    return "completed" if success else "rejected"


def _run_vtol_altitude_trial(controller: ControllerCandidate) -> tuple[list[TrialReport], OnlineTuningState | None]:
    hover = controller.feedforward.get("hover_thrust", VtolParams().hover_thrust_n)
    mass_estimate = hover / 9.81
    kp = controller.gains.get("kp_z", 0.05)
    kd = controller.gains.get("kd_z", 0.05)

    def controller_fn(
        plant_state: dict[str, float],
        reference: dict[str, float],
        gains: dict[str, float],
        time_s: float,
    ) -> dict[str, float]:
        del time_s
        thrust_delta = gains.get("kp_z", kp) * (reference["output"] - plant_state["output"]) - gains.get("kd_z", kd) * plant_state["velocity"]
        return {"input": float(np.clip(thrust_delta, -3.0, 3.0))}

    def plant_step(
        plant_state: dict[str, float],
        control: dict[str, float],
        dt_s: float,
    ) -> dict[str, float]:
        acceleration = control["input"] / max(mass_estimate, 1e-9)
        velocity = plant_state["velocity"] + dt_s * acceleration
        altitude = plant_state["output"] + dt_s * velocity
        return {"output": altitude, "velocity": velocity, "altitude": altitude}

    constraints = {
        "max_abs_output": 1.60,
        "max_abs_control": 3.0,
        "max_overshoot": 0.40,
        "max_integral_absolute_error": 1.0,
        "max_high_frequency_control_rms": 1.5,
        "max_actuator_saturation_fraction": 0.02,
    }

    def run_trial(trial_id: str, gains: dict[str, float]) -> TrialReport:
        runner = SafeTrialRunner(
            SafeTrialConfig(
                trial_id=trial_id,
                dt_s=0.02,
                duration_s=3.0,
                constraints=constraints,
            )
        )
        return runner.run(
            initial_state={"output": 0.80, "velocity": 0.0, "altitude": 0.80},
            controller=controller_fn,
            plant_step=plant_step,
            gains={name: value for name, value in gains.items() if name in {"kp_z", "kd_z"}},
            reference={"output": 1.0},
        )

    baseline = run_trial("vtol_hover_altitude_baseline_001", controller.gains)
    if baseline.metrics is None:
        return [baseline], None

    initial_state = OnlineTuningState(
        gains=dict(controller.gains),
        previous_gains=dict(controller.gains),
        step_fraction=0.05,
    )
    proposal = refine_gains_once(
        initial_state,
        baseline.metrics,
        constraints,
        tunable_gain_names=["kp_z", "kd_z"],
    )
    if proposal.frozen:
        return [baseline], proposal

    candidate = run_trial("vtol_hover_altitude_candidate_002", proposal.gains)
    if candidate.metrics is None:
        return [baseline, candidate], initial_state
    if candidate.accepted:
        accepted = proposal.model_copy(
            update={
                "history": proposal.history
                + [
                    {
                        "action": "candidate_validated",
                        "tested_gains": candidate.tested_gains,
                    }
                ]
            }
        )
        return [baseline, candidate], accepted

    rollback = refine_gains_once(
        proposal,
        candidate.metrics,
        constraints,
        tunable_gain_names=["kp_z", "kd_z"],
    )
    return [baseline, candidate], rollback


def _base_report(
    route_id: str,
    description: SystemDescription,
    diagnosis: StructuralDiagnosis,
    run_id: str | None,
) -> CFDCRunReport:
    return CFDCRunReport(
        run_id=run_id or f"cfdc-{uuid4().hex[:12]}",
        route_id=route_id,
        status="need_more_information",
        system_description=description,
        diagnosis=diagnosis,
        notes=["Stage 0 stopped because the description needs clarification."],
    )


def _no_go_report(
    route_id: str,
    description: SystemDescription,
    diagnosis: StructuralDiagnosis,
    classification,
    plan: ExperimentPlan,
    go_no_go: GoNoGoDecision,
    run_id: str | None,
    features: list[CoreFeatureArtifact] | None = None,
    experiment_results: list[ExperimentResult] | None = None,
    status: Literal["experiments_required", "rejected"] = "rejected",
) -> CFDCRunReport:
    return CFDCRunReport(
        run_id=run_id or f"cfdc-{uuid4().hex[:12]}",
        route_id=route_id,
        status=status,
        system_description=description,
        diagnosis=diagnosis,
        classification=classification,
        experiment_plan=plan,
        experiment_results=list(experiment_results or []),
        features=list(features or []),
        go_no_go=go_no_go,
        notes=[
            "CFDC deterministic validator returned no-go before controller synthesis or route-specific simulation.",
            *go_no_go.reasons,
            *[f"missing required feature: {feature_id}" for feature_id in go_no_go.missing_features],
        ],
    )


def run_cfdc_route(
    route_id: RouteId = "generic",
    description: SystemDescription | None = None,
    features: list[CoreFeatureArtifact] | None = None,
    experiment_results: list[ExperimentResult] | None = None,
    safety_limits: dict[str, float] | None = None,
    diagnostic_adapter: DiagnosticAdapter | None = None,
    include_trajectory: bool = False,
    run_id: str | None = None,
) -> CFDCRunReport:
    """Run an auditable end-to-end CFDC route.

    The route-specific simulation blocks are deterministic software checks. They
    do not replace physical validation or operator approval.
    """

    description = description or _default_description(route_id)
    engine = DiagnosticEngine(adapter=diagnostic_adapter)
    diagnosis = engine.diagnose(description)
    if not diagnosis.complete:
        return _base_report(route_id, description, diagnosis, run_id)

    classification = engine.classify(diagnosis)
    plan: ExperimentPlan = plan_safe_experiments(diagnosis, classification)
    route_gate = validate_route_compatibility(route_id, classification)
    if route_gate.decision == "no_go":
        return _no_go_report(
            route_id,
            description,
            diagnosis,
            classification,
            plan,
            route_gate,
            run_id,
            status="rejected",
        )
    resolved_results = list(experiment_results or [])
    notes = ["Completed Stage 0-4 with deterministic CFDC computation after structured diagnosis."]

    if not resolved_results and features is None:
        if route_id == "cartpole":
            resolved_results = _cartpole_experiment_results(classification.required_core_features)
        elif route_id.startswith("vtol"):
            resolved_results = _vtol_experiment_results(classification.required_core_features)

    resolved_features = list(features or [])
    if not resolved_features and resolved_results:
        resolved_features = extract_features_from_results(resolved_results)

    if not resolved_features:
        feature_gate = validate_required_features(classification, [])
        return CFDCRunReport(
            run_id=run_id or f"cfdc-{uuid4().hex[:12]}",
            route_id=route_id,
            status="experiments_required",
            system_description=description,
            diagnosis=diagnosis,
            classification=classification,
            experiment_plan=plan,
            go_no_go=merge_go_no_go(route_gate, feature_gate),
            notes=["Stage 2 plan is ready; Stage 3 requires experiment traces before controller synthesis."],
        )

    feature_gate = validate_required_features(classification, resolved_features)
    go_no_go = merge_go_no_go(route_gate, feature_gate)
    if go_no_go.decision == "no_go":
        return _no_go_report(
            route_id,
            description,
            diagnosis,
            classification,
            plan,
            go_no_go,
            run_id,
            features=resolved_features,
            experiment_results=resolved_results,
            status="experiments_required",
        )

    controller = synthesize_controller(classification, resolved_features, safety_limits or description.safety_bounds)
    trial_reports: list[TrialReport] = []
    safe_search_state = None
    tuning_state = None
    tracking_updates = []
    cartpole_simulation = None
    vtol_simulation = None
    final_gains = dict(controller.gains)
    final_feedforward = dict(controller.feedforward)

    if route_id == "cartpole":
        fmap = {feature.feature_id: feature.value for feature in resolved_features}
        natural_frequency = fmap["natural_frequency"]
        safe_search_state, cartpole_trials, search_events = search_cartpole_pd_gains(
            natural_frequency,
        )
        trial_reports.extend(cartpole_trials)
        final_gains = dict(safe_search_state.accepted_gains)
        cartpole_simulation = simulate_cartpole_energy_swingup(
            include_trajectory=include_trajectory,
            balance_gains=final_gains,
            natural_frequency_rad_s=natural_frequency,
            search_events=search_events,
        )
        status = _status_from_simulation(cartpole_simulation.success, trial_reports)
        notes.append("Cartpole route uses accepted CFDC online-search gains in the final energy swing-up software simulation.")
        notes.append("The safe_gain_search_state history records each 0.05 PD gain-search increment.")
    elif route_id.startswith("vtol"):
        vtol_trials, tuning_state = _run_vtol_altitude_trial(controller)
        trial_reports.extend(vtol_trials)
        if tuning_state is not None:
            final_gains = dict(tuning_state.gains)
        mode = route_id.replace("vtol-", "")
        route_config = VtolConfig(duration_s=15.0) if mode == "position" else VtolConfig()
        vtol_simulation = run_vtol_simulation(
            mode=mode,
            config=route_config,
            features=resolved_features,
            gains=final_gains,
            feedforward=final_feedforward,
            include_trajectory=include_trajectory,
        )
        if mode == "boundary" and vtol_simulation.metrics.get("rollback_applied") is True:
            final_gains["kp_y"] = float(vtol_simulation.metrics["accepted_lateral_kp"])
            final_gains["kd_y"] = float(vtol_simulation.metrics["accepted_lateral_kd"])
        status = _status_from_simulation(vtol_simulation.success, trial_reports)
        notes.append("VTOL route uses only gains that passed their channel-specific bounded software trials.")
    else:
        status = "controller_candidate_ready"
        notes.append("Generic route stops at Stage 4 because no plant-specific safe trial is configured.")

    if safe_search_state is not None and getattr(safe_search_state, "frozen", False):
        status = "frozen"
    if tuning_state is not None and tuning_state.frozen:
        status = "frozen"

    return CFDCRunReport(
        run_id=run_id or f"cfdc-{uuid4().hex[:12]}",
        route_id=route_id,
        status=status,
        system_description=description,
        diagnosis=diagnosis,
        classification=classification,
        experiment_plan=plan,
        experiment_results=resolved_results,
        features=resolved_features,
        controller=controller,
        trial_reports=trial_reports,
        online_tuning_state=tuning_state,
        safe_gain_search_state=safe_search_state,
        feature_tracking_updates=tracking_updates,
        cartpole_simulation=cartpole_simulation,
        vtol_simulation=vtol_simulation,
        final_gains=final_gains,
        final_feedforward=final_feedforward,
        go_no_go=go_no_go,
        notes=notes,
    )


def run_cfdc_end_to_end(*args, **kwargs) -> CFDCRunReport:
    """Backward-readable alias for the route orchestrator."""

    return run_cfdc_route(*args, **kwargs)
