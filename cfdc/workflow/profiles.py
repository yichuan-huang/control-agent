from __future__ import annotations

from cfdc.models import (
    ArchetypeClass,
    ArchetypeClassification,
    CouplingAssessment,
    PhaseAssessment,
    SemanticRouteSelection,
    SimulationProfile,
    SimulationProfileCatalog,
    StabilityAssessment,
    StructuralDiagnosis,
    SystemDescription,
)


def default_simulation_profile_catalog() -> SimulationProfileCatalog:
    profiles = [
        SimulationProfile(profile_id="first_order_lag", compatible_class=ArchetypeClass.CLASS_I_FIRST_ORDER_LAG, semantic_description="Stable self-regulating scalar process, optionally with transport delay.", feature_bundle_id="class_i_minimal", required_feature_ids=["static_gain", "time_constant"], controller_template_id="detuned_pi", simulator_backend="scalar_first_order", experiment_primitives=["ramp_step"], tunable_gain_names=["kp", "ki"], tracking_ids=["scalar_rls"], change_scenario_id="gain_and_time_constant_drift"),
        SimulationProfile(profile_id="first_order_lag_with_delay", compatible_class=ArchetypeClass.CLASS_I_FIRST_ORDER_LAG, semantic_description="Stable self-regulating scalar process with significant dead time.", feature_bundle_id="class_i_delay_minimal", required_feature_ids=["static_gain", "time_constant", "dead_time"], controller_template_id="detuned_pi", simulator_backend="scalar_first_order_delay", experiment_primitives=["ramp_step"], tunable_gain_names=["kp", "ki"], tracking_ids=["scalar_rls"], change_scenario_id="gain_and_time_constant_drift"),
        SimulationProfile(profile_id="second_order_oscillator", compatible_class=ArchetypeClass.CLASS_II_SECOND_ORDER_OSCILLATOR, semantic_description="Stable damped oscillatory scalar mode with a restoring force.", feature_bundle_id="class_ii_minimal", required_feature_ids=["natural_frequency", "damping_ratio", "input_gain"], controller_template_id="damping_pd", simulator_backend="scalar_second_order", experiment_primitives=["free_decay", "pulse"], tunable_gain_names=["kp", "kd"], tracking_ids=["frequency_locked_loop", "scalar_rls"], change_scenario_id="frequency_and_gain_drift"),
        SimulationProfile(profile_id="double_integrator", compatible_class=ArchetypeClass.CLASS_III_DOUBLE_OR_PURE_INTEGRATOR, semantic_description="Marginal non-restoring scalar motion such as position driven through acceleration.", feature_bundle_id="class_iii_minimal", required_feature_ids=["input_gain"], controller_template_id="saturated_pd", simulator_backend="scalar_double_integrator", experiment_primitives=["pulse"], tunable_gain_names=["kp", "kd"], tracking_ids=["scalar_rls"], change_scenario_id="input_gain_drift"),
        SimulationProfile(profile_id="nmp_inverse_response", compatible_class=ArchetypeClass.CLASS_IV_HIGHER_ORDER_UNSTABLE_NONLINEAR_OR_NMP, semantic_description="Stable scalar process whose measured output initially moves opposite to its final direction.", feature_bundle_id="class_iv_nmp_minimal", required_feature_ids=["static_gain", "time_constant", "inverse_response_severity"], controller_template_id="nmp_outer_loop", simulator_backend="scalar_inverse_response", experiment_primitives=["ramp_step"], tunable_gain_names=["kp", "ki"], tracking_ids=["scalar_rls"], change_scenario_id="gain_and_inverse_response_drift"),
        SimulationProfile(profile_id="generic_unstable_higher_order", compatible_class=ArchetypeClass.CLASS_IV_HIGHER_ORDER_UNSTABLE_NONLINEAR_OR_NMP, semantic_description="Generic unstable or higher-order scalar prototype without a more specific mechanism profile.", feature_bundle_id="class_iv_unstable_minimal", required_feature_ids=["natural_frequency", "input_gain"], controller_template_id="class_iv_conservative", simulator_backend="generic_unstable", experiment_primitives=["free_decay", "pulse"], tunable_gain_names=["kp", "kd"], tracking_ids=["frequency_locked_loop", "scalar_rls"], change_scenario_id="unstable_mode_drift"),
        SimulationProfile(profile_id="underactuated_cartpole", compatible_class=ArchetypeClass.CLASS_IV_HIGHER_ORDER_UNSTABLE_NONLINEAR_OR_NMP, semantic_description="One actuator exchanges energy between a translating base and an unactuated falling or balancing link.", feature_bundle_id="cartpole_minimal", required_feature_ids=["natural_frequency"], controller_template_id="cartpole_cascaded", simulator_backend="cartpole", experiment_primitives=["free_decay"], tunable_gain_names=["kp", "kd", "kp_y", "kd_y"], tracking_ids=["frequency_locked_loop"], change_scenario_id="pole_frequency_drift"),
        SimulationProfile(profile_id="vtol_cascaded", compatible_class=ArchetypeClass.CLASS_IV_HIGHER_ORDER_UNSTABLE_NONLINEAR_OR_NMP, semantic_description="Hovering vehicle where lateral motion is mediated through attitude and thrust.", feature_bundle_id="vtol_minimal", required_feature_ids=["hover_thrust", "angular_acceleration_gain", "lateral_coupling_gain"], controller_template_id="vtol_cascaded", simulator_backend="vtol", experiment_primitives=["hover_thrust", "pulse"], tunable_gain_names=["kp_z", "kd_z", "kp_theta", "kd_theta", "kp_y", "kd_y"], tracking_ids=["hover_average", "scalar_rls"], change_scenario_id="payload_and_inertia_drift"),
        SimulationProfile(profile_id="mimo_2x2_coupled", compatible_class=ArchetypeClass.CLASS_V_MULTIVARIABLE_SIGNIFICANT_COUPLING, semantic_description="Generic two-input two-output process with material cross-channel interaction.", feature_bundle_id="class_v_matrix_minimal", required_feature_ids=["local_gain_matrix", "local_time_constant", "pairing_indicator"], controller_template_id="mimo_decoupling_matrix", simulator_backend="mimo_2x2", experiment_primitives=["bounded_scan"], tunable_gain_names=["loop_1_gain", "loop_2_gain"], tracking_ids=["matrix_rls"], change_scenario_id="coupling_matrix_drift"),
    ]
    return SimulationProfileCatalog(profiles=profiles)


def profile_by_id(catalog: SimulationProfileCatalog, profile_id: str) -> SimulationProfile:
    for profile in catalog.profiles:
        if profile.profile_id == profile_id:
            return profile
    raise ValueError(f"unknown simulation profile '{profile_id}'")


def deterministic_profile_selection(
    description: SystemDescription,
    diagnosis: StructuralDiagnosis,
    classification: ArchetypeClassification,
    catalog: SimulationProfileCatalog,
) -> SemanticRouteSelection:
    """Select benchmark profiles from normalized diagnosis only.

    The description is accepted for adapter symmetry but is deliberately not read.
    """

    del description
    archetype = str(classification.primary_class)
    if archetype == ArchetypeClass.CLASS_I_FIRST_ORDER_LAG.value:
        profile_id = "first_order_lag_with_delay" if diagnosis.significant_delay.assessment == "significant" else "first_order_lag"
    elif archetype == ArchetypeClass.CLASS_II_SECOND_ORDER_OSCILLATOR.value:
        profile_id = "second_order_oscillator"
    elif archetype == ArchetypeClass.CLASS_III_DOUBLE_OR_PURE_INTEGRATOR.value:
        profile_id = "double_integrator"
    elif archetype == ArchetypeClass.CLASS_V_MULTIVARIABLE_SIGNIFICANT_COUPLING.value:
        profile_id = "mimo_2x2_coupled"
    elif diagnosis.coupling_severity.assessment == CouplingAssessment.UNDERACTUATED.value:
        profile_id = "underactuated_cartpole"
    elif diagnosis.coupling_severity.assessment == CouplingAssessment.CASCADED.value:
        profile_id = "vtol_cascaded"
    elif diagnosis.minimum_phase.assessment == PhaseAssessment.NONMINIMUM_PHASE.value and diagnosis.open_loop_stability.assessment == StabilityAssessment.STABLE.value:
        profile_id = "nmp_inverse_response"
    else:
        profile_id = "generic_unstable_higher_order"
    profile = profile_by_id(catalog, profile_id)
    return SemanticRouteSelection(simulation_profile_id=profile.profile_id, feature_bundle_id=profile.feature_bundle_id, selected_feature_ids=profile.required_feature_ids, confidence=1.0, evidence=["normalized eight-field diagnosis and closed profile catalog"], rationale="Deterministic benchmark selection from typed diagnostic assessments.")


def validate_semantic_selection(
    selection: SemanticRouteSelection,
    classification: ArchetypeClassification,
    catalog: SimulationProfileCatalog,
) -> SimulationProfile:
    profile = profile_by_id(catalog, selection.simulation_profile_id)
    if str(profile.compatible_class) != str(classification.primary_class):
        raise ValueError("selected simulation profile is incompatible with the canonical class")
    if selection.feature_bundle_id != profile.feature_bundle_id:
        raise ValueError("selected feature bundle does not belong to the simulation profile")
    if selection.selected_feature_ids != profile.required_feature_ids:
        raise ValueError("selected features must exactly match the catalog's minimal feature bundle")
    if selection.confidence < 0.5:
        raise ValueError("semantic route selection confidence must be at least 0.5")
    return profile


def apply_profile_to_classification(
    classification: ArchetypeClassification,
    profile: SimulationProfile,
) -> ArchetypeClassification:
    return classification.model_copy(update={
        "required_core_features": profile.required_feature_ids,
        "control_architecture": profile.controller_template_id,
        "rationale": f"{classification.rationale} Simulation profile: {profile.profile_id}.",
    })
