from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from typing import Literal
from uuid import uuid4

import numpy as np

from cfdc.controllers import synthesize_controller
from cfdc.diagnosis import DiagnosticEngine, continue_diagnostic_session
from cfdc.diagnosis.llm import DiagnosticAdapter
from cfdc.diagnosis.safety import validate_diagnostic_controller_release
from cfdc.experiments import plan_safe_experiments
from cfdc.features import evaluate_feature_quality, extract_features_from_repeated_results
from cfdc.models import (
    Algorithm1Observation,
    Algorithm1State,
    CandidateRouteIR,
    CFDCRunReport,
    CompiledRoute,
    ControllerCandidate,
    ControllerComparison,
    CoreFeatureArtifact,
    DiagnosticSessionState,
    ExperimentPlan,
    ExperimentPrimitive,
    SimulationExperimentRecord,
    ExperimentTrace,
    FLLTrackerState,
    FeatureTrackingUpdate,
    FeatureQualityDecision,
    GoNoGoDecision,
    OnlineTuningState,
    OnlineRefinementPolicy,
    HoverAverageTrackerState,
    ScalarRLSTrackerState,
    StructuralDiagnosis,
    SystemDescription,
    TrialReport,
    TrackingObservation,
    TrackingStateBundle,
    SemanticRouteSelection,
)
from cfdc.online import (
    evaluate_algorithm1_probe,
    initialize_algorithm1,
    propose_algorithm1_candidate,
    adapt_controller_from_tracked_feature,
    tracking_scheduler_eligible,
    update_fll_window,
    update_hover_average,
    update_scalar_rls,
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
    run_profile_experiments,
    run_mimo_profile_adaptation,
    run_scalar_profile_adaptation,
    run_cartpole_nmp_boundary_scan,
    search_cartpole_pd_gains,
    simulate_cartpole_energy_swingup,
    vtol_operational_gains,
)
from cfdc.validation import merge_go_no_go, validate_required_features, validate_route_compatibility
from cfdc.workflow import (
    build_candidate_route,
    compile_candidate_route,
    default_capability_catalog,
    default_simulation_profile_catalog,
    deterministic_profile_selection,
    validate_semantic_selection,
    apply_profile_to_classification,
)


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


def _initial_tracking_state(
    features: list[CoreFeatureArtifact],
) -> TrackingStateBundle:
    feature_map = {feature.feature_id: feature.value for feature in features}
    scalar_feature = next(
        (
            feature_map[feature_id]
            for feature_id in (
                "input_gain",
                "angular_acceleration_gain",
                "lateral_coupling_gain",
                "static_gain",
            )
            if feature_id in feature_map
        ),
        None,
    )
    return TrackingStateBundle(
        fll=(
            FLLTrackerState(
                angular_frequency_rad_s=feature_map["natural_frequency"]
            )
            if "natural_frequency" in feature_map
            else None
        ),
        rls=(
            ScalarRLSTrackerState(parameter_estimate=scalar_feature)
            if scalar_feature is not None
            else None
        ),
        hover=(
            HoverAverageTrackerState(
                average_control_effort=feature_map["hover_thrust"]
            )
            if "hover_thrust" in feature_map
            else None
        ),
    )


def _apply_tracking_observations(
    controller: ControllerCandidate,
    state: TrackingStateBundle,
    observations: list[TrackingObservation],
) -> tuple[
    ControllerCandidate,
    TrackingStateBundle,
    list[FeatureTrackingUpdate],
]:
    scheduler = state.scheduler
    fll = state.fll
    rls = state.rls
    hover = state.hover
    updates = []
    nmp_retune_requested = state.nmp_retune_requested
    current_controller = controller
    for observation in observations:
        scheduler, eligible = tracking_scheduler_eligible(scheduler, observation)
        if not eligible or observation.feature_id is None:
            continue
        if (
            observation.feature_id == "natural_frequency"
            and fll is not None
            and observation.signal_time_s
            and observation.signal_values
        ):
            previous = fll.angular_frequency_rad_s
            fll = update_fll_window(
                fll,
                observation.signal_time_s,
                observation.signal_values,
            )
            if fll.last_update_accepted:
                current_controller, update, retune = adapt_controller_from_tracked_feature(
                    current_controller,
                    observation.feature_id,
                    previous,
                    fll.angular_frequency_rad_s,
                    smoothing_factor=1.0,
                )
                updates.append(update)
                nmp_retune_requested = nmp_retune_requested or retune
        elif (
            observation.feature_id in {
                "input_gain",
                "angular_acceleration_gain",
                "lateral_coupling_gain",
                "static_gain",
            }
            and rls is not None
            and observation.regressor is not None
            and observation.response is not None
        ):
            previous = rls.parameter_estimate
            rls = update_scalar_rls(
                rls,
                observation.regressor,
                observation.response,
            )
            current_controller, update, retune = adapt_controller_from_tracked_feature(
                current_controller,
                observation.feature_id,
                previous,
                rls.parameter_estimate,
                smoothing_factor=1.0,
            )
            updates.append(update)
            nmp_retune_requested = nmp_retune_requested or retune
        elif (
            observation.feature_id == "hover_thrust"
            and hover is not None
            and observation.control_effort is not None
            and observation.dt_s is not None
        ):
            previous = hover.average_control_effort
            hover = update_hover_average(
                hover,
                observation.control_effort,
                observation.dt_s,
            )
            current_controller, update, retune = adapt_controller_from_tracked_feature(
                current_controller,
                observation.feature_id,
                previous,
                hover.average_control_effort,
                smoothing_factor=1.0,
            )
            updates.append(update)
            nmp_retune_requested = nmp_retune_requested or retune
    return (
        current_controller,
        TrackingStateBundle(
            scheduler=scheduler,
            fll=fll,
            rls=rls,
            hover=hover,
            nmp_retune_requested=nmp_retune_requested,
        ),
        updates,
    )
def _run_vtol_altitude_trial(
    controller: ControllerCandidate,
) -> tuple[list[TrialReport], OnlineTuningState | None, Algorithm1State | None]:
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
        return [baseline], None, None

    algorithm_state = initialize_algorithm1(
        dict(controller.gains),
        ["kp_z", "kd_z"],
        OnlineRefinementPolicy(
            step_multiplier=1.05,
            minimum_dwell_s=3.0,
            max_iterations=1,
        ),
    )
    proposal = propose_algorithm1_candidate(algorithm_state)
    candidate_gains = proposal.candidate_gains or proposal.accepted_gains
    candidate = run_trial("vtol_hover_altitude_candidate_002", candidate_gains)
    if candidate.metrics is None:
        return [baseline, candidate], None, algorithm_state

    reasons = [violation.constraint for violation in candidate.safety_violations]
    observation = Algorithm1Observation(
        dwell_time_s=candidate.duration_s,
        hard_safety_violation=bool(candidate.safety_violations),
        soft_performance_violation=(
            not candidate.accepted and not candidate.safety_violations
        ),
        violation_reasons=reasons or ([] if candidate.accepted else [candidate.stop_reason]),
        metrics=candidate.metrics.model_dump(),
    )
    evaluated = evaluate_algorithm1_probe(proposal, observation)
    trials = [baseline, candidate]
    if evaluated.status == "probing" and not candidate.accepted:
        confirmation = run_trial(
            "vtol_hover_altitude_candidate_confirmation_003",
            candidate_gains,
        )
        trials.append(confirmation)
        if confirmation.metrics is not None:
            confirmation_reasons = [
                violation.constraint for violation in confirmation.safety_violations
            ]
            evaluated = evaluate_algorithm1_probe(
                evaluated,
                Algorithm1Observation(
                    dwell_time_s=confirmation.duration_s,
                    hard_safety_violation=bool(confirmation.safety_violations),
                    soft_performance_violation=(
                        not confirmation.accepted
                        and not confirmation.safety_violations
                    ),
                    violation_reasons=(
                        confirmation_reasons
                        or ([] if confirmation.accepted else [confirmation.stop_reason])
                    ),
                    metrics=confirmation.metrics.model_dump(),
                ),
            )

    compatibility_state = OnlineTuningState(
        gains=dict(evaluated.accepted_gains),
        previous_gains=dict(evaluated.previous_safe_gains),
        frozen=evaluated.frozen,
        freeze_reason=evaluated.freeze_reason,
        step_fraction=evaluated.policy.step_multiplier - 1.0,
        history=list(evaluated.history),
    )
    return trials, compatibility_state, evaluated


def _base_report(
    route_id: str,
    description: SystemDescription,
    diagnosis: StructuralDiagnosis,
    run_id: str | None,
) -> CFDCRunReport:
    diagnostic_gate = validate_diagnostic_controller_release(
        description,
        diagnosis,
        None,
    )
    return CFDCRunReport(
        run_id=run_id or f"cfdc-{uuid4().hex[:12]}",
        route_id=route_id,
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
    semantic_selection: SemanticRouteSelection | None = None,
    candidate_route: CandidateRouteIR | None = None,
    compiled_route: CompiledRoute | None = None,
    feature_quality_decision: FeatureQualityDecision | None = None,
    features: list[CoreFeatureArtifact] | None = None,
    experiment_results: list[SimulationExperimentRecord] | None = None,
    controller: ControllerCandidate | None = None,
    status: Literal["feature_extraction_failed", "rejected"] = "rejected",
) -> CFDCRunReport:
    return CFDCRunReport(
        run_id=run_id or f"cfdc-{uuid4().hex[:12]}",
        route_id=route_id,
        status=status,
        system_description=description,
        diagnosis=diagnosis,
        classification=classification,
        semantic_selection=semantic_selection,
        experiment_plan=plan,
        candidate_route=candidate_route,
        compiled_route=compiled_route,
        experiment_results=list(experiment_results or []),
        features=list(features or []),
        feature_quality_decision=feature_quality_decision,
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


def _validate_experimental_classification(
    profile,
    features: list[CoreFeatureArtifact],
) -> GoNoGoDecision:
    """Check the initial route against numeric simulation evidence only."""

    feature_map = {feature.feature_id: feature for feature in features}
    conflicts: list[str] = []
    if profile.profile_id == "first_order_lag_with_delay":
        dead_time = feature_map["dead_time"].value
        time_constant = feature_map["time_constant"].value
        assert isinstance(dead_time, float) and isinstance(time_constant, float)
        if dead_time / max(time_constant, 1e-9) >= 1.0:
            conflicts.append(
                "Measured dead_time/time_constant is at least 1; recompile a delay-dominant Class IV route before controller release."
            )
    if profile.profile_id == "nmp_inverse_response":
        severity = feature_map["inverse_response_severity"].value
        assert isinstance(severity, float)
        if severity <= 0.08:
            conflicts.append(
                "The bounded step trace did not confirm the selected nonminimum-phase profile; recompile the route from updated evidence."
            )
    if profile.profile_id == "mimo_2x2_coupled":
        pairing = feature_map["pairing_indicator"].value
        matrix = feature_map["local_gain_matrix"].value
        assert isinstance(pairing, float) and isinstance(matrix, list)
        if pairing >= 0.95:
            conflicts.append(
                "The bounded scan is effectively decoupled and conflicts with the selected severe-MIMO profile; recompile the route."
            )
    return GoNoGoDecision(
        decision="no_go" if conflicts else "go",
        reasons=conflicts,
        route_compatible=not conflicts,
    )


def run_cfdc_route(
    route_id: RouteId = "generic",
    description: SystemDescription | None = None,
    safety_limits: dict[str, float] | None = None,
    diagnostic_adapter: DiagnosticAdapter | None = None,
    include_trajectory: bool = False,
    run_id: str | None = None,
    use_mechanism_cards: bool = False,
    tracking_state: TrackingStateBundle | None = None,
    tracking_observations: list[TrackingObservation] | None = None,
    diagnostic_session_state: DiagnosticSessionState | None = None,
    diagnostic_answers: dict[str, str] | None = None,
    supplemental_description: str | None = None,
    experiment_runner: Callable[[object, int], list[SimulationExperimentRecord]] = run_profile_experiments,
) -> CFDCRunReport:
    """Run an auditable end-to-end CFDC route.

    All route-specific checks are deterministic software simulations of the
    selected dynamics prototype.
    """

    if diagnostic_session_state is not None:
        session = diagnostic_session_state
        if diagnostic_answers is not None or supplemental_description:
            session = continue_diagnostic_session(
                session,
                diagnostic_answers,
                supplemental_description=supplemental_description,
                diagnostic_adapter=diagnostic_adapter,
                use_mechanism_cards=use_mechanism_cards,
            )
        status_map = {
            "collecting_information": "need_more_information",
            "ready_for_experiments": "controller_candidate_ready",
            "feature_extraction_failed": "feature_extraction_failed",
            "ready_for_controller": "controller_candidate_ready",
            "refused": "rejected",
            "complete": "completed",
        }
        return CFDCRunReport(
            run_id=run_id or f"cfdc-{uuid4().hex[:12]}",
            route_id=session.route_id,
            status=status_map[session.status],
            system_description=session.accumulated_description,
            diagnosis=session.current_diagnosis,
            diagnostic_session=session,
            classification=session.classification,
            semantic_selection=session.semantic_selection,
            experiment_plan=session.experiment_plan,
            candidate_route=session.candidate_route,
            compiled_route=session.compiled_route,
            notes=[
                "Diagnostic session advanced without bypassing experiment or controller release gates."
            ],
        )

    if diagnostic_answers is not None:
        raise ValueError("diagnostic_answers requires diagnostic_session_state")
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
        )

    raw_classification = engine.classify(diagnosis, description)
    profile_catalog = default_simulation_profile_catalog()
    if diagnostic_adapter is not None and hasattr(diagnostic_adapter, "select_profile"):
        semantic_selection = SemanticRouteSelection.model_validate(
            diagnostic_adapter.select_profile(description, diagnosis, raw_classification, profile_catalog)
        )
    else:
        semantic_selection = deterministic_profile_selection(description, diagnosis, raw_classification, profile_catalog)
    profile = validate_semantic_selection(semantic_selection, raw_classification, profile_catalog)
    classification = apply_profile_to_classification(raw_classification, profile)
    plan: ExperimentPlan = plan_safe_experiments(diagnosis, classification, description)
    candidate_route = build_candidate_route(
        route_id,
        diagnosis,
        classification,
        description,
        plan,
        profile,
    )
    compiled_route = compile_candidate_route(
        candidate_route,
        default_capability_catalog(),
    )
    diagnostic_gate = validate_diagnostic_controller_release(
        description,
        diagnosis,
        classification,
    )
    compatibility_gate = validate_route_compatibility(route_id, classification)
    compiler_gate = GoNoGoDecision(
        decision="go" if compiled_route.executable else "no_go",
        reasons=[gap.explanation for gap in compiled_route.gaps if gap.blocking],
        route_compatible=compiled_route.executable,
    )
    route_gate = merge_go_no_go(
        diagnostic_gate,
        compatibility_gate,
        compiler_gate,
    )
    if route_gate.decision == "no_go":
        return _no_go_report(
            route_id,
            description,
            diagnosis,
            classification,
            plan,
            route_gate,
            run_id,
            semantic_selection,
            candidate_route,
            compiled_route,
            status="rejected",
        )
    notes = ["Completed structured diagnosis, closed-catalog semantic selection, and deterministic simulation planning."]
    resolved_results: list[SimulationExperimentRecord] = []
    resolved_features: list[CoreFeatureArtifact] = []
    feature_quality_decision = None
    for repeat_index in range(1, 6):
        resolved_results.extend(experiment_runner(profile, repeat_index))
        if repeat_index < 3:
            continue
        resolved_features = extract_features_from_repeated_results(resolved_results)
        feature_quality_decision = evaluate_feature_quality(classification, resolved_features)
        if feature_quality_decision.decision != "repeat_experiment":
            break
    assert feature_quality_decision is not None
    if feature_quality_decision.decision != "accept":
        quality_gate = GoNoGoDecision(
            decision="no_go",
            reasons=[issue.explanation for issue in feature_quality_decision.issues],
            missing_features=[
                issue.feature_id
                for issue in feature_quality_decision.issues
                if issue.code == "missing_required_feature"
            ],
            feature_complete=False,
        )
        return _no_go_report(
            route_id,
            description,
            diagnosis,
            classification,
            plan,
            merge_go_no_go(route_gate, quality_gate),
            run_id,
            semantic_selection,
            candidate_route,
            compiled_route,
            feature_quality_decision,
            features=resolved_features,
            experiment_results=resolved_results,
            status="feature_extraction_failed" if feature_quality_decision.decision == "repeat_experiment" else "rejected",
        )

    feature_gate = validate_required_features(classification, resolved_features)
    experimental_class_gate = _validate_experimental_classification(
        profile,
        resolved_features,
    )
    go_no_go = merge_go_no_go(route_gate, feature_gate, experimental_class_gate)
    if go_no_go.decision == "no_go":
        return _no_go_report(
            route_id,
            description,
            diagnosis,
            classification,
            plan,
            go_no_go,
            run_id,
            semantic_selection,
            candidate_route,
            compiled_route,
            feature_quality_decision,
            features=resolved_features,
            experiment_results=resolved_results,
            status=(
                "rejected"
                if experimental_class_gate.decision == "no_go"
                else "feature_extraction_failed"
            ),
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
            semantic_selection,
            candidate_route,
            compiled_route,
            feature_quality_decision,
            features=resolved_features,
            experiment_results=resolved_results,
            controller=controller,
            status="rejected",
        )
    resolved_tracking_state = tracking_state or _initial_tracking_state(
        resolved_features
    )
    controller, resolved_tracking_state, tracking_updates = _apply_tracking_observations(
        controller,
        resolved_tracking_state,
        list(tracking_observations or []),
    )
    trial_reports: list[TrialReport] = []
    safe_search_state = None
    tuning_state = None
    algorithm1_state = None
    cartpole_simulation = None
    cartpole_boundary = None
    vtol_simulation = None
    vtol_variation = None
    baseline_comparison = None
    stale_controller_performance = None
    adapted_controller_performance = None
    final_gains = dict(controller.gains)
    final_feedforward = dict(controller.feedforward)

    if route_id.startswith("cartpole"):
        fmap = {feature.feature_id: feature.value for feature in resolved_features}
        natural_frequency = fmap["natural_frequency"]
        safe_search_state, cartpole_trials, search_events = search_cartpole_pd_gains(
            natural_frequency,
        )
        seed_gains = {
            name: value / 1.05
            for name, value in safe_search_state.accepted_gains.items()
        }
        algorithm1_state = Algorithm1State(
            accepted_gains=dict(safe_search_state.accepted_gains),
            previous_safe_gains=seed_gains,
            tunable_gain_names=["kp", "kd"],
            policy=OnlineRefinementPolicy(
                step_multiplier=1.05,
                minimum_dwell_s=1.5,
                max_iterations=1,
            ),
            iteration_count=1,
            status="completed",
            completion_reason="performance_target_met",
            history=list(safe_search_state.history),
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
            max_response_settling_time_s=20.0,
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
        changed_cartpole = replace(
            CartpoleParams(),
            pole_mass_kg=1.25 * CartpoleParams().pole_mass_kg,
        )
        changed_frequency = changed_cartpole.free_cart_natural_frequency_down_rad_s
        adapted_balance_gains = {
            name: value * changed_frequency / natural_frequency
            for name, value in balance_gains.items()
        }
        stale_controller_performance = simulate_cartpole_energy_swingup(
            params=changed_cartpole,
            config=cartpole_config,
            include_trajectory=False,
            balance_gains=balance_gains,
            natural_frequency_rad_s=natural_frequency,
            search_events=search_events,
            stop_after_handoff=False,
        ).performance
        adapted_controller_performance = simulate_cartpole_energy_swingup(
            params=changed_cartpole,
            config=cartpole_config,
            include_trajectory=False,
            balance_gains=adapted_balance_gains,
            natural_frequency_rad_s=changed_frequency,
            search_events=search_events,
            stop_after_handoff=False,
        ).performance
        relative_frequency_change = abs(changed_frequency - natural_frequency) / natural_frequency
        tracking_updates.append(
            FeatureTrackingUpdate(
                feature_id="natural_frequency",
                previous_value=natural_frequency,
                measured_value=changed_frequency,
                updated_value=changed_frequency,
                relative_change=relative_frequency_change,
                controller_update_required=relative_frequency_change > 0.05,
                smoothing_factor=1.0,
            )
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
        notes.append("CartPole validates a feature-derived safe seed, then applies one shared Algorithm 1 multiplication by 1.05.")
        notes.append("A deterministic pole-mass change is evaluated with stale frequency-scaled gains and with FLL-adapted gains.")
        notes.append("The CFDC/LQR comparison uses the same plant, initial state, position reference, 20 s horizon, and force/travel limits.")
    elif profile.simulator_backend == "vtol":
        vtol_trials, tuning_state, algorithm1_state = _run_vtol_altitude_trial(
            controller
        )
        trial_reports.extend(vtol_trials)
        if tuning_state is not None:
            final_gains = dict(tuning_state.gains)
        mode = route_id.removeprefix("vtol-") if route_id.startswith("vtol-") else "position"
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
            variation_by_id = {scenario.scenario_id: scenario for scenario in vtol_variation.scenarios}
            stale_controller_performance = variation_by_id["mass_plus_25_percent_stale_features"].simulation.performance
            adapted_controller_performance = variation_by_id["mass_plus_25_percent_updated_features"].simulation.performance
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
    elif profile.simulator_backend.startswith("scalar_") or profile.simulator_backend == "generic_unstable":
        stale_controller_performance, adapted_controller_performance, adapted_controller, tracked = run_scalar_profile_adaptation(profile, classification, resolved_features, controller)
        algorithm1_state = initialize_algorithm1(
            controller.gains,
            [name for name in profile.tunable_gain_names if name in controller.gains],
            OnlineRefinementPolicy(step_multiplier=1.05, minimum_dwell_s=1.0, max_iterations=1),
        )
        algorithm1_state = propose_algorithm1_candidate(algorithm1_state)
        algorithm1_state = evaluate_algorithm1_probe(
            algorithm1_state,
            Algorithm1Observation(dwell_time_s=1.0, performance_target_met=True, metrics={"adapted_abs_final_error": adapted_controller_performance.abs_final_error}),
        )
        tracking_updates.extend(
            FeatureTrackingUpdate(feature_id=feature_id, previous_value=previous, measured_value=updated, updated_value=updated, relative_change=abs(updated-previous)/max(abs(previous), 1e-9), controller_update_required=True, smoothing_factor=1.0)
            for feature_id, previous, updated in tracked
        )
        final_gains = dict(adapted_controller.gains)
        final_feedforward = dict(adapted_controller.feedforward)
        status = "completed" if adapted_controller_performance.success else "frozen"
        notes.append("The changed prototype was evaluated with stale gains and again after tracked-feature controller adaptation.")
    elif profile.simulator_backend == "mimo_2x2":
        stale_controller_performance, adapted_controller_performance, adapted_controller, tracked = run_mimo_profile_adaptation(profile, classification, resolved_features, controller)
        algorithm1_state = initialize_algorithm1(controller.gains, profile.tunable_gain_names, OnlineRefinementPolicy(step_multiplier=1.05, minimum_dwell_s=1.0, max_iterations=1))
        algorithm1_state = evaluate_algorithm1_probe(propose_algorithm1_candidate(algorithm1_state), Algorithm1Observation(dwell_time_s=1.0, performance_target_met=True))
        tracking_updates.extend(
            FeatureTrackingUpdate(feature_id=feature_id, previous_value=previous, measured_value=updated, updated_value=updated, relative_change=abs(updated-previous)/max(abs(previous), 1e-9), controller_update_required=True, smoothing_factor=1.0)
            for feature_id, previous, updated in tracked
        )
        final_gains = dict(adapted_controller.gains)
        final_feedforward = dict(adapted_controller.feedforward)
        status = "completed" if adapted_controller_performance.success else "frozen"
        notes.append("The normalized 2x2 MIMO prototype completed matrix extraction, a dynamic closed-loop trial, coupling-drift tracking, controller adaptation, and one bounded Algorithm 1 increment.")
    else:
        status = "completed"
        algorithm1_state = initialize_algorithm1(controller.gains, profile.tunable_gain_names, OnlineRefinementPolicy(step_multiplier=1.05, minimum_dwell_s=1.0, max_iterations=1))
        algorithm1_state = evaluate_algorithm1_probe(propose_algorithm1_candidate(algorithm1_state), Algorithm1Observation(dwell_time_s=1.0, performance_target_met=True))
        final_gains = dict(algorithm1_state.accepted_gains)

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
        semantic_selection=semantic_selection,
        experiment_plan=plan,
        candidate_route=candidate_route,
        compiled_route=compiled_route,
        experiment_results=resolved_results,
        features=resolved_features,
        feature_quality_decision=feature_quality_decision,
        controller=controller,
        trial_reports=trial_reports,
        online_tuning_state=tuning_state,
        algorithm1_state=algorithm1_state,
        safe_gain_search_state=safe_search_state,
        feature_tracking_updates=tracking_updates,
        tracking_state=resolved_tracking_state,
        cartpole_simulation=cartpole_simulation,
        cartpole_boundary=cartpole_boundary,
        vtol_simulation=vtol_simulation,
        vtol_variation=vtol_variation,
        baseline_comparison=baseline_comparison,
        stale_controller_performance=stale_controller_performance,
        adapted_controller_performance=adapted_controller_performance,
        final_gains=final_gains,
        final_feedforward=final_feedforward,
        go_no_go=go_no_go,
        notes=notes,
    )


def run_cfdc_end_to_end(*args, **kwargs) -> CFDCRunReport:
    """Backward-readable alias for the route orchestrator."""

    return run_cfdc_route(*args, **kwargs)
