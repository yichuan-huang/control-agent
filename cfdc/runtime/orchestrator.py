from __future__ import annotations

from typing import Literal
from uuid import uuid4

import numpy as np

from cfdc.controllers import synthesize_controller
from cfdc.diagnosis import DiagnosticEngine
from cfdc.diagnosis.llm import DiagnosticAdapter
from cfdc.diagnosis.safety import validate_diagnostic_controller_release
from cfdc.experiments import plan_safe_experiments
from cfdc.features import extract_features_from_results
from cfdc.models import (
    CFDCRunReport,
    ControllerCandidate,
    ControllerComparison,
    CoreFeatureArtifact,
    DataProvenance,
    ExperimentPlan,
    ExperimentPrimitive,
    ExperimentResult,
    ExperimentTrace,
    GoNoGoDecision,
    OnlineTuningState,
    StructuralDiagnosis,
    SystemDescription,
    TrialReport,
    WorkflowMode,
)
from cfdc.online import (
    refine_gains_once,
)
from cfdc.runtime.trial import SafeTrialConfig, SafeTrialRunner
from cfdc.sim import (
    CartpoleSwingupConfig,
    CartpoleParams,
    VtolConfig,
    VtolParams,
    run_vtol_simulation,
    run_vtol_lqr_baseline,
    run_vtol_variation,
    run_cartpole_nmp_boundary_scan,
    search_cartpole_pd_gains,
    simulate_cartpole_energy_swingup,
    vtol_operational_gains,
)
from cfdc.sim.traces import hover_trace, modal_trace, pulse_trace, vtol_pulse_trace
from cfdc.validation import merge_go_no_go, validate_required_features, validate_route_compatibility
from cfdc.workflow import resolve_workflow_mode


RouteId = Literal[
    "generic",
    "cartpole",
    "cartpole-boundary",
    "vtol-position",
    "vtol-boundary",
    "vtol-altitude",
    "vtol-hover",
    "vtol-variation",
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
    if route_id.startswith("cartpole"):
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
        provenance=DataProvenance.SYNTHETIC_FIXTURE,
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
        provenance=DataProvenance.SYNTHETIC_FIXTURE,
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
                provenance=DataProvenance.SYNTHETIC_FIXTURE,
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
                provenance=DataProvenance.SYNTHETIC_FIXTURE,
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


def _comparison_report(
    case_id: str,
    cfdc_controller: str,
    baseline_controller: str,
    cfdc_performance,
    baseline_performance,
    matched_conditions: dict,
) -> ControllerComparison:
    cfdc_settling = cfdc_performance.settling_time_s
    baseline_settling = baseline_performance.settling_time_s
    settling_delta = (
        cfdc_settling - baseline_settling
        if cfdc_settling is not None and baseline_settling is not None
        else None
    )
    return ControllerComparison(
        case_id=case_id,
        cfdc_controller=cfdc_controller,
        baseline_controller=baseline_controller,
        primary_channel=cfdc_performance.primary_channel,
        cfdc_performance=cfdc_performance,
        baseline_performance=baseline_performance,
        matched_conditions=matched_conditions,
        settling_time_delta_s=settling_delta,
        abs_final_error_delta=(
            cfdc_performance.abs_final_error - baseline_performance.abs_final_error
        ),
        saturation_fraction_delta=(
            cfdc_performance.saturation_fraction - baseline_performance.saturation_fraction
        ),
        notes=[
            "Both controllers use the same software plant, initial state, reference, horizon, and actuator limits.",
            "The LQR baseline uses full model parameters; CFDC uses extracted core features and validated gain searches.",
        ],
    )


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
    workflow_mode: WorkflowMode,
) -> CFDCRunReport:
    diagnostic_gate = validate_diagnostic_controller_release(
        description,
        diagnosis,
        None,
    )
    return CFDCRunReport(
        run_id=run_id or f"cfdc-{uuid4().hex[:12]}",
        route_id=route_id,
        workflow_mode=workflow_mode,
        status="need_more_information",
        system_description=description,
        diagnosis=diagnosis,
        go_no_go=diagnostic_gate,
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
    workflow_mode: WorkflowMode,
    features: list[CoreFeatureArtifact] | None = None,
    experiment_results: list[ExperimentResult] | None = None,
    controller: ControllerCandidate | None = None,
    status: Literal["experiments_required", "rejected"] = "rejected",
) -> CFDCRunReport:
    return CFDCRunReport(
        run_id=run_id or f"cfdc-{uuid4().hex[:12]}",
        route_id=route_id,
        workflow_mode=workflow_mode,
        status=status,
        system_description=description,
        diagnosis=diagnosis,
        classification=classification,
        experiment_plan=plan,
        experiment_results=list(experiment_results or []),
        features=list(features or []),
        controller=controller,
        go_no_go=go_no_go,
        notes=[
            (
                "CFDC controller synthesis returned a refusal candidate before route-specific simulation."
                if controller is not None
                else "CFDC deterministic validator returned no-go before controller synthesis or route-specific simulation."
            ),
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
    use_mechanism_cards: bool = False,
    workflow_mode: WorkflowMode | str | None = None,
) -> CFDCRunReport:
    """Run an auditable end-to-end CFDC route.

    The route-specific simulation blocks are deterministic software checks. They
    do not replace physical validation or operator approval.
    """

    resolved_mode = resolve_workflow_mode(workflow_mode, diagnostic_adapter)
    description = description or _default_description(route_id)
    engine = DiagnosticEngine(
        adapter=diagnostic_adapter,
        use_mechanism_cards=use_mechanism_cards,
    )
    diagnosis = engine.diagnose(description)
    if not diagnosis.complete:
        return _base_report(
            route_id,
            description,
            diagnosis,
            run_id,
            resolved_mode,
        )

    classification = engine.classify(diagnosis, description)
    plan: ExperimentPlan = plan_safe_experiments(diagnosis, classification)
    diagnostic_gate = validate_diagnostic_controller_release(
        description,
        diagnosis,
        classification,
    )
    compatibility_gate = validate_route_compatibility(route_id, classification)
    route_gate = merge_go_no_go(diagnostic_gate, compatibility_gate)
    if route_gate.decision == "no_go":
        return _no_go_report(
            route_id,
            description,
            diagnosis,
            classification,
            plan,
            route_gate,
            run_id,
            resolved_mode,
            status=(
                "experiments_required"
                if diagnostic_gate.decision == "no_go"
                else "rejected"
            ),
        )
    resolved_results = list(experiment_results or [])
    notes = ["Completed Stage 0-4 with deterministic CFDC computation after structured diagnosis."]

    if (
        resolved_mode == WorkflowMode.SIMULATION
        and not resolved_results
        and features is None
    ):
        if route_id.startswith("cartpole"):
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
            workflow_mode=resolved_mode,
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
            resolved_mode,
            features=resolved_features,
            experiment_results=resolved_results,
            status="experiments_required",
        )

    controller = synthesize_controller(classification, resolved_features, safety_limits or description.safety_bounds)
    if controller.status == "refuse":
        controller_gate = GoNoGoDecision(
            decision="no_go",
            reasons=[
                f"Controller synthesis refused release for architecture '{controller.architecture}'.",
                *controller.notes,
            ],
        )
        return _no_go_report(
            route_id,
            description,
            diagnosis,
            classification,
            plan,
            merge_go_no_go(go_no_go, controller_gate),
            run_id,
            resolved_mode,
            features=resolved_features,
            experiment_results=resolved_results,
            controller=controller,
            status="rejected",
        )
    trial_reports: list[TrialReport] = []
    safe_search_state = None
    tuning_state = None
    tracking_updates = []
    cartpole_simulation = None
    cartpole_boundary = None
    vtol_simulation = None
    vtol_variation = None
    baseline_comparison = None
    final_gains = dict(controller.gains)
    final_feedforward = dict(controller.feedforward)

    if route_id.startswith("cartpole"):
        fmap = {feature.feature_id: feature.value for feature in resolved_features}
        natural_frequency = fmap["natural_frequency"]
        safe_search_state, cartpole_trials, search_events = search_cartpole_pd_gains(
            natural_frequency,
        )
        trial_reports.extend(cartpole_trials)
        balance_gains = dict(safe_search_state.accepted_gains)
        cartpole_boundary = run_cartpole_nmp_boundary_scan(
            natural_frequency,
            balance_gains,
            include_trajectory=include_trajectory,
        )
        final_gains = {
            **balance_gains,
            **cartpole_boundary.accepted_outer_gains,
        }
        cartpole_config = CartpoleSwingupConfig(
            duration_s=20.0,
            normalized_energy_gain=0.65,
            swing_cart_position_gain=3.6,
            swing_cart_velocity_gain=3.2,
            outer_reference_m=0.2,
            outer_kpy_initial=final_gains.get("kp_y", 0.0),
            outer_kdy_initial=final_gains.get("kd_y", 0.0),
            outer_theta_ref_limit_rad=0.25,
            max_force_saturation_fraction=0.35,
        )
        cartpole_simulation = simulate_cartpole_energy_swingup(
            config=cartpole_config,
            include_trajectory=include_trajectory,
            balance_gains=balance_gains,
            natural_frequency_rad_s=natural_frequency,
            search_events=search_events,
            stop_after_handoff=False,
        )
        cartpole_simulation = cartpole_simulation.model_copy(
            update={"final_gains": final_gains}
        )
        cartpole_lqr = simulate_cartpole_energy_swingup(
            config=cartpole_config,
            include_trajectory=False,
            stop_after_handoff=False,
        )
        baseline_comparison = _comparison_report(
            "cartpole_outer_position",
            "feature_energy_swingup_and_searched_pd",
            "full_model_energy_swingup_and_lqr",
            cartpole_simulation.performance,
            cartpole_lqr.performance,
            matched_conditions={
                "plant": "CartpoleParams defaults",
                "initial_state": {
                    "cart_position_m": 0.0,
                    "cart_velocity_m_s": 0.0,
                    "pole_angle_rad": cartpole_config.initial_angle_from_upright_rad,
                    "pole_angular_velocity_rad_s": 0.0,
                },
                "reference": {"cart_position_m": cartpole_config.outer_reference_m},
                "horizon_s": cartpole_config.duration_s,
                "actuator_limits": {"max_abs_force_n": CartpoleParams().force_limit_n},
                "state_limits": {"max_abs_cart_position_m": CartpoleParams().cart_position_limit_m},
            },
        )
        cartpole_success = (
            cartpole_boundary.success
            and cartpole_simulation.success
            and cartpole_lqr.success
        )
        status = _status_from_simulation(cartpole_success, trial_reports)
        notes.append("Cartpole route runs outer-position NMP discovery, validates rollback over a long horizon, then checks the accepted gains in a complete swing-up response.")
        notes.append("The safe_gain_search_state history records each 0.05 PD gain-search increment.")
        notes.append("The CFDC/LQR comparison uses the same plant, initial state, position reference, 20 s horizon, and force/travel limits.")
    elif route_id.startswith("vtol"):
        vtol_trials, tuning_state = _run_vtol_altitude_trial(controller)
        trial_reports.extend(vtol_trials)
        if tuning_state is not None:
            final_gains = dict(tuning_state.gains)
        mode = route_id.removeprefix("vtol-")
        if mode in {"position", "boundary", "variation"}:
            previous_gains = dict(final_gains)
            final_gains = vtol_operational_gains(resolved_features)
            if tuning_state is not None:
                tuning_state = tuning_state.model_copy(
                    update={
                        "previous_gains": previous_gains,
                        "gains": final_gains,
                        "history": tuning_state.history
                        + [
                            {
                                "action": "coupled_operational_candidate",
                                "tested_gains": final_gains,
                                "validation": "route_specific_full_simulation",
                            }
                        ],
                    }
                )
        if mode == "variation":
            vtol_variation = run_vtol_variation(
                include_trajectory=include_trajectory,
            )
            vtol_simulation = vtol_variation.scenarios[0].simulation
            status = _status_from_simulation(vtol_variation.success, trial_reports)
            notes.append("VTOL variation route evaluates six nominal, mass, and inertia cases with explicit stale-versus-updated core features.")
        else:
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
                if tuning_state is not None:
                    tuning_state = tuning_state.model_copy(
                        update={
                            "gains": final_gains,
                            "history": tuning_state.history
                            + [
                                {
                                    "action": "boundary_rollback_validated",
                                    "accepted_gains": final_gains,
                                }
                            ],
                        }
                    )
            if mode == "position":
                vtol_lqr = run_vtol_lqr_baseline(
                    config=route_config,
                    include_trajectory=False,
                )
                baseline_comparison = _comparison_report(
                    "vtol_lateral_position",
                    "core_feature_cascaded_controller",
                    "full_state_full_model_lqr",
                    vtol_simulation.performance,
                    vtol_lqr.performance,
                    matched_conditions={
                        "plant": "VtolParams defaults",
                        "initial_state": {
                            "x_m": 0.0,
                            "z_m": route_config.altitude_ref_m,
                            "theta_rad": 0.0,
                            "x_dot_m_s": 0.0,
                            "z_dot_m_s": 0.0,
                            "theta_dot_rad_s": 0.0,
                        },
                        "reference": {
                            "x_m": route_config.position_ref_m,
                            "z_m": route_config.altitude_ref_m,
                        },
                        "horizon_s": route_config.duration_s,
                        "actuator_limits": {
                            "thrust_min_n": VtolParams().thrust_min_n,
                            "thrust_max_n": VtolParams().thrust_max_n,
                            "max_abs_torque_n_m": VtolParams().torque_limit_n_m,
                        },
                    },
                )
                simulation_success = vtol_simulation.success and vtol_lqr.success
            else:
                simulation_success = vtol_simulation.success
            status = _status_from_simulation(simulation_success, trial_reports)
            notes.append("VTOL route uses only gains that passed their channel-specific bounded or complete coupled software checks.")
            if mode == "position":
                notes.append("The CFDC/LQR comparison uses the same plant, initial state, references, 15 s horizon, and thrust/torque limits.")
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
        workflow_mode=resolved_mode,
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
        cartpole_boundary=cartpole_boundary,
        vtol_simulation=vtol_simulation,
        vtol_variation=vtol_variation,
        baseline_comparison=baseline_comparison,
        final_gains=final_gains,
        final_feedforward=final_feedforward,
        go_no_go=go_no_go,
        notes=notes,
    )


def run_cfdc_end_to_end(*args, **kwargs) -> CFDCRunReport:
    """Backward-readable alias for the route orchestrator."""

    return run_cfdc_route(*args, **kwargs)
