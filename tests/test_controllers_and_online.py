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


def test_marginal_plant_controller_has_tiny_pd_and_saturation():
    classification = ArchetypeClassification(
        primary_class=ArchetypeClass.CLASS_III_DOUBLE_OR_PURE_INTEGRATOR,
        control_architecture="small saturated PD",
        required_core_features=["input_gain"],
        safety_constraints=[],
        rationale="test",
    )
    controller = synthesize_controller(classification, [feature("input_gain", 1.0)], {"output_max": 0.4})
    assert controller.gains == {"kp": 1e-3, "kd": 1e-2}
    assert controller.saturation["output_max"] == 0.4


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
    assert pending.candidate_gains["kp"] == 0.05
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
