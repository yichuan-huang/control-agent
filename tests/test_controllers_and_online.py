from cfdc.controllers import pair_mimo_loops, synthesize_controller
from cfdc.models import (
    ArchetypeClass,
    ArchetypeClassification,
    CoreFeatureArtifact,
    ExperimentPrimitive,
    OnlinePerformanceMetrics,
    OnlineTuningState,
)
from cfdc.online import (
    evaluate_unstable_gain_trial,
    initialize_safe_gain_search,
    propose_unstable_gain_candidate,
    refine_gains_once,
    update_tracked_feature,
)


def feature(fid, value):
    width = max(abs(value) * 0.05, 1e-6)
    return CoreFeatureArtifact(
        feature_id=fid,
        value=value,
        lower_bound=value - width,
        upper_bound=value + width,
        confidence=0.85,
        units="unit",
        method="test",
        source_experiment=ExperimentPrimitive.PULSE,
    )


def bounded_feature(fid, value, lower, upper):
    return CoreFeatureArtifact(
        feature_id=fid,
        value=value,
        lower_bound=lower,
        upper_bound=upper,
        confidence=0.85,
        units="unit",
        method="test",
        source_experiment=ExperimentPrimitive.PULSE,
    )


def test_stable_plant_controller_is_detuned():
    classification = ArchetypeClassification(
        primary_class=ArchetypeClass.CLASS_I_FIRST_ORDER_LAG,
        control_architecture="detuned PI",
        required_core_features=["static_gain", "time_constant"],
        safety_constraints=[],
        rationale="test",
    )
    controller = synthesize_controller(
        classification,
        [feature("static_gain", 2.0), feature("time_constant", 5.0)],
    )
    assert controller.architecture == "detuned_PI"
    assert abs(controller.gains["kp"]) < 0.1
    assert controller.status == "ready_for_conservative_trial"


def test_synthesis_rejects_incomplete_required_features_with_clear_error():
    classification = ArchetypeClassification(
        primary_class=ArchetypeClass.CLASS_I_FIRST_ORDER_LAG,
        control_architecture="detuned PI",
        required_core_features=["static_gain", "time_constant"],
        safety_constraints=[],
        rationale="test",
    )
    try:
        synthesize_controller(classification, [feature("static_gain", 2.0)])
    except ValueError as exc:
        assert "time_constant" in str(exc)
        return
    raise AssertionError("synthesis accepted an incomplete feature set")


def test_marginal_plant_controller_scales_pd_from_input_gain_and_saturates():
    classification = ArchetypeClassification(
        primary_class=ArchetypeClass.CLASS_III_DOUBLE_OR_PURE_INTEGRATOR,
        control_architecture="small saturated PD",
        required_core_features=["input_gain"],
        safety_constraints=[],
        rationale="test",
    )
    controller = synthesize_controller(classification, [feature("input_gain", 1.0)], {"output_max": 0.4})
    conservative_gain = 1.05
    assert controller.gains == {
        "kp": 0.9**2 / conservative_gain,
        "kd": 2.0 * 1.15 * 0.9 / conservative_gain,
    }
    assert controller.saturation["output_max"] == 0.4

    half_gain = synthesize_controller(
        classification,
        [feature("input_gain", 0.5)],
        {"output_max": 0.4},
    )
    assert half_gain.gains["kp"] == 2.0 * controller.gains["kp"]
    assert half_gain.gains["kd"] == 2.0 * controller.gains["kd"]


def test_second_order_controller_scales_from_input_gain():
    classification = ArchetypeClassification(
        primary_class=ArchetypeClass.CLASS_II_SECOND_ORDER_OSCILLATOR,
        control_architecture="detuned PD",
        required_core_features=["natural_frequency", "damping_ratio", "input_gain"],
        safety_constraints=[],
        rationale="test",
    )
    unit_gain = synthesize_controller(
        classification,
        [feature("natural_frequency", 3.0), feature("damping_ratio", 0.2), feature("input_gain", 1.0)],
    )
    double_gain = synthesize_controller(
        classification,
        [feature("natural_frequency", 3.0), feature("damping_ratio", 0.2), feature("input_gain", 2.0)],
    )

    assert double_gain.gains["kp"] == 0.5 * unit_gain.gains["kp"]
    assert double_gain.gains["kd"] == 0.5 * unit_gain.gains["kd"]
    assert unit_gain.source_features == ["natural_frequency", "damping_ratio", "input_gain"]


def test_second_order_controller_rejects_missing_input_gain_clearly():
    classification = ArchetypeClassification(
        primary_class=ArchetypeClass.CLASS_II_SECOND_ORDER_OSCILLATOR,
        control_architecture="detuned PD",
        required_core_features=["natural_frequency", "damping_ratio"],
        safety_constraints=[],
        rationale="legacy incomplete contract",
    )

    try:
        synthesize_controller(
            classification,
            [feature("natural_frequency", 3.0), feature("damping_ratio", 0.2)],
        )
    except ValueError as exc:
        assert "input_gain" in str(exc)
        return
    raise AssertionError("Class II synthesis accepted a missing input_gain")


def test_first_order_dead_time_detunes_gain_and_integral_speed():
    without_delay = ArchetypeClassification(
        primary_class=ArchetypeClass.CLASS_I_FIRST_ORDER_LAG,
        control_architecture="detuned PI",
        required_core_features=["static_gain", "time_constant"],
        safety_constraints=[],
        rationale="test",
    )
    with_delay = without_delay.model_copy(
        update={"required_core_features": ["static_gain", "time_constant", "dead_time"]}
    )
    common = [feature("static_gain", 2.0), feature("time_constant", 8.0)]
    nominal = synthesize_controller(without_delay, common)
    delayed = synthesize_controller(with_delay, [*common, feature("dead_time", 2.0)])

    assert delayed.gains["kp"] < nominal.gains["kp"]
    assert delayed.gains["ki"] < nominal.gains["ki"]
    assert delayed.gains["integral_time"] > nominal.gains["integral_time"]
    assert delayed.source_features == ["static_gain", "time_constant", "dead_time"]


def test_first_order_delay_strategy_uses_conservative_uncertainty_boundaries():
    classification = ArchetypeClassification(
        primary_class=ArchetypeClass.CLASS_I_FIRST_ORDER_LAG,
        control_architecture="delay-aware PI selection",
        required_core_features=["static_gain", "time_constant", "dead_time"],
        safety_constraints=[],
        rationale="test",
    )
    gain = bounded_feature("static_gain", 2.0, 1.9, 2.1)
    tau = bounded_feature("time_constant", 10.0, 10.0, 10.0)

    ordinary = synthesize_controller(
        classification,
        [gain, tau, bounded_feature("dead_time", 0.5, 0.4, 0.999)],
    )
    at_delay_threshold = synthesize_controller(
        classification,
        [gain, tau, bounded_feature("dead_time", 0.5, 0.4, 1.0)],
    )
    below_refusal = synthesize_controller(
        classification,
        [gain, tau, bounded_feature("dead_time", 5.0, 4.0, 9.999)],
    )
    at_refusal = synthesize_controller(
        classification,
        [gain, tau, bounded_feature("dead_time", 5.0, 4.0, 10.0)],
    )

    assert ordinary.architecture == "detuned_PI"
    assert ordinary.design_parameters["rho_high"] == 0.0999
    assert at_delay_threshold.architecture == "delay_detuned_PI"
    assert below_refusal.architecture == "delay_detuned_PI"
    assert at_refusal.architecture == "large_delay_compensation_required"
    assert at_refusal.status == "refuse"
    assert at_refusal.gains == {}
    assert at_refusal.design_parameters == {
        "rho_nominal": 0.5,
        "rho_low": 0.4,
        "rho_high": 1.0,
    }


def test_delay_uncertainty_crossing_threshold_fails_closed():
    classification = ArchetypeClassification(
        primary_class=ArchetypeClass.CLASS_I_FIRST_ORDER_LAG,
        control_architecture="delay-aware PI selection",
        required_core_features=["static_gain", "time_constant", "dead_time"],
        safety_constraints=[],
        rationale="test",
    )
    controller = synthesize_controller(
        classification,
        [
            bounded_feature("static_gain", 2.0, 1.9, 2.1),
            bounded_feature("time_constant", 10.0, 8.0, 12.0),
            bounded_feature("dead_time", 6.0, 4.0, 8.0),
        ],
    )

    assert controller.design_parameters["rho_nominal"] == 0.6
    assert controller.design_parameters["rho_high"] == 1.0
    assert controller.status == "refuse"


def test_unstable_safe_gain_search_accepts_then_freezes_on_violation():
    classification = ArchetypeClassification(
        primary_class=ArchetypeClass.CLASS_IV_HIGHER_ORDER_UNSTABLE_NONLINEAR_OR_NMP,
        control_architecture="safe online gain search",
        required_core_features=["natural_frequency", "input_gain"],
        safety_constraints=[],
        rationale="test",
    )
    controller = synthesize_controller(
        classification,
        [feature("natural_frequency", 4.0), feature("input_gain", 1.0)],
        {"output_min": -1.0, "output_max": 1.0},
    )
    state = initialize_safe_gain_search(controller, search_direction={"kp": 1.0, "kd": 1.0})
    pending = propose_unstable_gain_candidate(state)
    assert pending.status == "trial_pending"
    assert pending.candidate_gains["kp"] == state.accepted_gains["kp"] * 1.05
    assert pending.candidate_gains["kd"] > state.accepted_gains["kd"]

    safe_metrics = OnlinePerformanceMetrics(
        overshoot=0.05,
        settling_time_s=2.0,
        integral_absolute_error=0.5,
        high_frequency_control_rms=0.01,
        actuator_saturation_fraction=0.0,
        nmp_undershoot=0.02,
    )
    accepted = evaluate_unstable_gain_trial(pending, safe_metrics, {"max_overshoot": 0.2})
    assert accepted.status == "accepted"
    assert accepted.accepted_gains == pending.candidate_gains

    unsafe_pending = propose_unstable_gain_candidate(accepted)
    unsafe_metrics = OnlinePerformanceMetrics(
        overshoot=0.3,
        settling_time_s=2.0,
        integral_absolute_error=0.5,
        high_frequency_control_rms=0.01,
        actuator_saturation_fraction=0.0,
        nmp_undershoot=0.02,
    )
    frozen = evaluate_unstable_gain_trial(unsafe_pending, unsafe_metrics, {"max_overshoot": 0.2})
    assert frozen.frozen
    assert frozen.status == "frozen"
    assert frozen.accepted_gains == accepted.accepted_gains
    assert "overshoot" in frozen.freeze_reason


def test_online_refinement_rolls_back_and_freezes_on_violation():
    state = OnlineTuningState(gains={"kp": 1.1, "kd": 0.2}, previous_gains={"kp": 1.0, "kd": 0.19})
    metrics = OnlinePerformanceMetrics(
        overshoot=0.3,
        settling_time_s=2.0,
        integral_absolute_error=1.0,
        high_frequency_control_rms=0.01,
        actuator_saturation_fraction=0.0,
        nmp_undershoot=0.05,
    )
    new_state = refine_gains_once(state, metrics, {"max_overshoot": 0.2})
    assert new_state.frozen
    assert new_state.gains == {"kp": 1.0, "kd": 0.19}
    assert "overshoot" in new_state.freeze_reason


def test_online_refinement_changes_only_declared_tunable_gains():
    state = OnlineTuningState(
        gains={"kp_z": 1.0, "kd_z": 2.0, "plant_feature": -9.81},
        previous_gains={"kp_z": 1.0, "kd_z": 2.0, "plant_feature": -9.81},
    )
    metrics = OnlinePerformanceMetrics(
        overshoot=0.0,
        settling_time_s=1.0,
        integral_absolute_error=0.1,
        high_frequency_control_rms=0.01,
        actuator_saturation_fraction=0.0,
        nmp_undershoot=0.0,
    )
    proposed = refine_gains_once(
        state,
        metrics,
        {},
        tunable_gain_names=["kp_z", "kd_z"],
    )
    assert proposed.gains["kp_z"] == 1.05
    assert proposed.gains["kd_z"] == 2.10
    assert proposed.gains["plant_feature"] == -9.81


def test_feature_tracking_smoothly_updates_after_threshold():
    update = update_tracked_feature("hover_thrust", previous_value=10.0, measured_value=10.8)
    assert update.controller_update_required
    assert abs(update.updated_value - 10.008) < 1e-12


def test_mimo_pairing_returns_half_strength_decoupler():
    result = pair_mimo_loops([[2.0, 0.2], [0.1, 1.5]])
    assert result["pairing"][0]["input_index"] == 0
    assert result["pairing"][1]["input_index"] == 1
    assert result["unpaired_output_indices"] == []
    assert result["unpaired_input_indices"] == []
    assert result["requires_centralized_review"] is False


def test_mimo_pairing_uses_global_maximum_weight_assignment():
    result = pair_mimo_loops([[10.0, 9.0], [9.0, 0.0]])

    assert [(item["output_index"], item["input_index"]) for item in result["pairing"]] == [
        (0, 1),
        (1, 0),
    ]


def test_rectangular_mimo_pairing_reports_unpaired_channels():
    result = pair_mimo_loops([[3.0], [2.0]])

    assert result["unpaired_output_indices"] == [1]
    assert result["unpaired_input_indices"] == []
    assert result["requires_centralized_review"] is True
