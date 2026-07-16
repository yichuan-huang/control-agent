from __future__ import annotations

from cfdc.models import ArchetypeClass, ControlMethodProfile, ControlMethodProfileCatalog


def _method(
    profile_id: str,
    compatible_class: ArchetypeClass,
    semantic_description: str,
    feature_bundle_id: str,
    required_feature_ids: list[str],
    controller_template_id: str,
    experiment_primitives: list[str],
    tunable_gain_names: list[str],
    tracking_ids: list[str],
) -> ControlMethodProfile:
    return ControlMethodProfile(
        profile_id=profile_id,
        compatible_class=compatible_class,
        semantic_description=semantic_description,
        feature_bundle_id=feature_bundle_id,
        required_feature_ids=required_feature_ids,
        controller_template_id=controller_template_id,
        experiment_primitives=experiment_primitives,
        tunable_gain_names=tunable_gain_names,
        tracking_ids=tracking_ids,
    )


def default_control_method_profile_catalog() -> ControlMethodProfileCatalog:
    """Return method metadata with no simulator backend or plant numbers."""

    return ControlMethodProfileCatalog(
        profiles=[
            _method(
                "first_order_lag",
                ArchetypeClass.CLASS_I_FIRST_ORDER_LAG,
                "Stable self-regulating scalar process, optionally with transport delay.",
                "class_i_minimal",
                ["static_gain", "time_constant"],
                "detuned_pi",
                ["ramp_step"],
                ["kp", "ki"],
                ["scalar_rls"],
            ),
            _method(
                "first_order_lag_with_delay",
                ArchetypeClass.CLASS_I_FIRST_ORDER_LAG,
                "Stable self-regulating scalar process with significant dead time.",
                "class_i_delay_minimal",
                ["static_gain", "time_constant", "dead_time"],
                "detuned_pi",
                ["ramp_step"],
                ["kp", "ki"],
                ["scalar_rls"],
            ),
            _method(
                "second_order_oscillator",
                ArchetypeClass.CLASS_II_SECOND_ORDER_OSCILLATOR,
                "Stable damped oscillatory scalar mode with a restoring force.",
                "class_ii_minimal",
                ["natural_frequency", "damping_ratio", "input_gain"],
                "damping_pd",
                ["free_decay", "pulse"],
                ["kp", "kd"],
                ["frequency_locked_loop", "scalar_rls"],
            ),
            _method(
                "double_integrator",
                ArchetypeClass.CLASS_III_DOUBLE_OR_PURE_INTEGRATOR,
                "Marginal non-restoring scalar motion such as position driven through acceleration.",
                "class_iii_minimal",
                ["input_gain"],
                "saturated_pd",
                ["pulse"],
                ["kp", "kd"],
                ["scalar_rls"],
            ),
            _method(
                "nmp_inverse_response",
                ArchetypeClass.CLASS_IV_HIGHER_ORDER_UNSTABLE_NONLINEAR_OR_NMP,
                "Stable scalar process whose measured output initially moves opposite to its final direction.",
                "class_iv_nmp_minimal",
                ["static_gain", "time_constant", "inverse_response_severity"],
                "nmp_outer_loop",
                ["ramp_step"],
                ["kp", "ki"],
                ["scalar_rls"],
            ),
            _method(
                "generic_unstable_higher_order",
                ArchetypeClass.CLASS_IV_HIGHER_ORDER_UNSTABLE_NONLINEAR_OR_NMP,
                "Generic unstable or higher-order scalar plant without a registered specification compiler.",
                "class_iv_unstable_minimal",
                ["natural_frequency", "input_gain"],
                "class_iv_conservative",
                ["free_decay", "pulse"],
                ["kp", "kd"],
                ["frequency_locked_loop", "scalar_rls"],
            ),
            _method(
                "underactuated_cartpole",
                ArchetypeClass.CLASS_IV_HIGHER_ORDER_UNSTABLE_NONLINEAR_OR_NMP,
                "One actuator exchanges energy between a translating base and an unactuated link.",
                "cartpole_minimal",
                ["natural_frequency"],
                "cartpole_cascaded",
                ["free_decay"],
                ["kp", "kd", "kp_y", "kd_y"],
                ["frequency_locked_loop"],
            ),
            _method(
                "vtol_cascaded",
                ArchetypeClass.CLASS_IV_HIGHER_ORDER_UNSTABLE_NONLINEAR_OR_NMP,
                "Hovering vehicle where lateral motion is mediated through attitude and thrust.",
                "vtol_minimal",
                ["hover_thrust", "angular_acceleration_gain", "lateral_coupling_gain"],
                "vtol_cascaded",
                ["hover_thrust", "pulse"],
                ["kp_z", "kd_z", "kp_theta", "kd_theta", "kp_y", "kd_y"],
                ["hover_average", "scalar_rls"],
            ),
            _method(
                "mimo_2x2_coupled",
                ArchetypeClass.CLASS_V_MULTIVARIABLE_SIGNIFICANT_COUPLING,
                "Generic two-input two-output process with material cross-channel interaction.",
                "class_v_matrix_minimal",
                ["local_gain_matrix", "local_time_constant", "pairing_indicator"],
                "mimo_decoupling_matrix",
                ["bounded_scan"],
                ["loop_1_gain", "loop_2_gain"],
                ["matrix_rls"],
            ),
        ]
    )
