from __future__ import annotations

from cfdc.models import (
    ArchetypeClass,
    CandidateRouteIR,
    CapabilityCatalog,
    CapabilityGap,
    CompiledRoute,
    ControllerTemplateCapability,
    DataProvenance,
    ExperimentPrimitive,
    PrimitiveSignalRequirement,
    WorkflowMode,
)


def default_capability_catalog() -> CapabilityCatalog:
    class_i = ArchetypeClass.CLASS_I_FIRST_ORDER_LAG
    class_ii = ArchetypeClass.CLASS_II_SECOND_ORDER_OSCILLATOR
    class_iii = ArchetypeClass.CLASS_III_DOUBLE_OR_PURE_INTEGRATOR
    class_iv = ArchetypeClass.CLASS_IV_HIGHER_ORDER_UNSTABLE_NONLINEAR_OR_NMP
    class_v = ArchetypeClass.CLASS_V_MULTIVARIABLE_SIGNIFICANT_COUPLING
    return CapabilityCatalog(
        experiment_primitive_classes={
            ExperimentPrimitive.FREE_DECAY.value: [class_ii, class_iv],
            ExperimentPrimitive.RAMP_STEP.value: [class_i, class_iv],
            ExperimentPrimitive.PULSE.value: [class_ii, class_iii, class_iv],
            ExperimentPrimitive.HOVER_THRUST.value: [class_iv],
            ExperimentPrimitive.BOUNDED_SCAN.value: [class_v],
        },
        primitive_signal_requirements={
            ExperimentPrimitive.FREE_DECAY.value: PrimitiveSignalRequirement(
                input_required=False,
                output_required=True,
            ),
            ExperimentPrimitive.RAMP_STEP.value: PrimitiveSignalRequirement(),
            ExperimentPrimitive.PULSE.value: PrimitiveSignalRequirement(),
            ExperimentPrimitive.HOVER_THRUST.value: PrimitiveSignalRequirement(),
            ExperimentPrimitive.BOUNDED_SCAN.value: PrimitiveSignalRequirement(),
        },
        feature_extractors={
            "static_gain": [ExperimentPrimitive.RAMP_STEP.value],
            "time_constant": [ExperimentPrimitive.RAMP_STEP.value],
            "dead_time": [ExperimentPrimitive.RAMP_STEP.value],
            "inverse_response_severity": [ExperimentPrimitive.RAMP_STEP.value],
            "natural_frequency": [ExperimentPrimitive.FREE_DECAY.value],
            "damping_ratio": [ExperimentPrimitive.FREE_DECAY.value],
            "input_gain": [ExperimentPrimitive.PULSE.value],
            "hover_thrust": [ExperimentPrimitive.HOVER_THRUST.value],
            "angular_acceleration_gain": [ExperimentPrimitive.PULSE.value],
            "lateral_coupling_gain": [ExperimentPrimitive.PULSE.value],
            "coupling_gain": [ExperimentPrimitive.BOUNDED_SCAN.value],
        },
        controller_templates={
            "detuned_pi": ControllerTemplateCapability(
                compatible_classes=[class_i],
                required_feature_ids=["static_gain", "time_constant"],
            ),
            "damping_pd": ControllerTemplateCapability(
                compatible_classes=[class_ii],
                required_feature_ids=["natural_frequency", "damping_ratio", "input_gain"],
            ),
            "saturated_pd": ControllerTemplateCapability(
                compatible_classes=[class_iii],
                required_feature_ids=["input_gain"],
            ),
            "cartpole_cascaded": ControllerTemplateCapability(
                compatible_classes=[class_iv],
                required_feature_ids=["natural_frequency"],
            ),
            "vtol_cascaded": ControllerTemplateCapability(
                compatible_classes=[class_iv],
                required_feature_ids=[
                    "hover_thrust",
                    "angular_acceleration_gain",
                    "lateral_coupling_gain",
                ],
            ),
            "nmp_outer_loop": ControllerTemplateCapability(
                compatible_classes=[class_iv],
            ),
            "gain_scheduled_pi": ControllerTemplateCapability(
                compatible_classes=[class_iv],
            ),
            "class_iv_conservative": ControllerTemplateCapability(
                compatible_classes=[class_iv],
            ),
            "mimo_decoupling_matrix": ControllerTemplateCapability(
                compatible_classes=[class_v],
                required_feature_ids=["local_gain_matrix", "pairing_indicator"],
                implemented=False,
            ),
        },
        online_refinement_policies=["bounded_gain_refinement"],
        tracking_implementations=[
            "frequency_locked_loop",
            "scalar_rls",
            "hover_average",
        ],
        simulation_fixture_routes=[
            "cartpole",
            "cartpole-boundary",
            "vtol-position",
            "vtol-boundary",
            "vtol-altitude",
            "vtol-hover",
            "vtol-variation",
        ],
    )


def _gap(
    code: str,
    stage: str,
    capability_id: str,
    explanation: str,
    required_next_action: str,
    *,
    resolvable_by_measurement: bool = False,
) -> CapabilityGap:
    return CapabilityGap(
        code=code,
        stage=stage,
        capability_id=capability_id,
        explanation=explanation,
        resolvable_by_measurement=resolvable_by_measurement,
        required_next_action=required_next_action,
    )


def compile_candidate_route(
    route: CandidateRouteIR,
    catalog: CapabilityCatalog,
) -> CompiledRoute:
    """Resolve every requested capability or emit an explicit blocking gap."""

    if not isinstance(route, CandidateRouteIR):
        raise TypeError(
            "compile_candidate_route accepts CandidateRouteIR only; "
            "BenchmarkRouteIR may contain hidden simulator parameters"
        )

    gaps: list[CapabilityGap] = []
    compiled_experiments: list[str] = []
    compiled_extractors: list[str] = []
    canonical_class = str(route.canonical_class)

    for request in route.experiment_requests:
        primitive = str(request.primitive)
        compatible_classes = catalog.experiment_primitive_classes.get(primitive)
        if compatible_classes is None:
            gaps.append(
                _gap(
                    "unknown_experiment_primitive",
                    "experiment_design",
                    primitive,
                    f"Experiment primitive '{primitive}' is not in capability catalog {catalog.schema_version}.",
                    "select a supported experiment primitive or implement and register it",
                )
            )
            continue
        if canonical_class not in {str(item) for item in compatible_classes}:
            gaps.append(
                _gap(
                    "experiment_class_mismatch",
                    "experiment_design",
                    primitive,
                    f"Experiment primitive '{primitive}' is not compatible with {canonical_class}.",
                    "select a primitive compatible with the diagnosed canonical class",
                )
            )
        signal_requirement = catalog.primitive_signal_requirements[primitive]
        if (
            signal_requirement.input_required
            and not request.input_signal_ids
        ) or (
            signal_requirement.output_required
            and not request.output_signal_ids
        ):
            gaps.append(
                _gap(
                    "missing_experiment_signal",
                    "experiment_design",
                    request.request_id,
                    f"Experiment request '{request.request_id}' lacks a required input or output signal.",
                    "declare measurable input and output signal identifiers",
                    resolvable_by_measurement=True,
                )
            )
        if (
            WorkflowMode(route.workflow_mode) == WorkflowMode.REAL
            and DataProvenance(request.provenance_requirement)
            == DataProvenance.SYNTHETIC_FIXTURE
        ):
            gaps.append(
                _gap(
                    "synthetic_provenance_forbidden",
                    "experiment_design",
                    request.request_id,
                    "Real workflow requests cannot be satisfied by synthetic fixture provenance.",
                    "provide a real experiment protocol or externally reviewed features",
                    resolvable_by_measurement=True,
                )
            )
        for feature_id in request.feature_ids:
            permitted_sources = catalog.feature_extractors.get(feature_id)
            if permitted_sources is None:
                gaps.append(
                    _gap(
                        "unsupported_feature_extractor",
                        "feature_extraction",
                        feature_id,
                        f"No registered extractor produces feature '{feature_id}'.",
                        "implement and validate the feature extractor",
                        resolvable_by_measurement=True,
                    )
                )
            elif primitive not in permitted_sources:
                gaps.append(
                    _gap(
                        "feature_source_mismatch",
                        "feature_extraction",
                        feature_id,
                        f"Feature '{feature_id}' cannot be extracted from '{primitive}'.",
                        "select a permitted experiment source for this feature",
                        resolvable_by_measurement=True,
                    )
                )
            elif feature_id not in compiled_extractors:
                compiled_extractors.append(feature_id)
        compiled_experiments.append(request.request_id)

    template = catalog.controller_templates.get(route.controller_template_id)
    compiled_controller: str | None = None
    if template is None:
        gaps.append(
            _gap(
                "unknown_controller_template",
                "controller_synthesis",
                route.controller_template_id,
                f"Controller template '{route.controller_template_id}' is not registered.",
                "select or implement a registered controller template",
            )
        )
    else:
        if canonical_class not in {str(item) for item in template.compatible_classes}:
            gaps.append(
                _gap(
                    "controller_class_mismatch",
                    "controller_synthesis",
                    route.controller_template_id,
                    f"Controller template '{route.controller_template_id}' is not compatible with {canonical_class}.",
                    "select a controller template compatible with the canonical class",
                )
            )
        missing = set(template.required_feature_ids) - set(
            route.required_core_feature_ids
        )
        if missing:
            gaps.append(
                _gap(
                    "controller_feature_contract_mismatch",
                    "controller_synthesis",
                    route.controller_template_id,
                    f"Candidate route omits controller features: {', '.join(sorted(missing))}.",
                    "add the controller-required core features and experiment requests",
                    resolvable_by_measurement=True,
                )
            )
        if not template.implemented:
            code = (
                "unimplemented_mimo_matrix_route"
                if route.controller_template_id == "mimo_decoupling_matrix"
                else "controller_template_not_implemented"
            )
            gaps.append(
                _gap(
                    code,
                    "controller_synthesis",
                    route.controller_template_id,
                    f"Controller template '{route.controller_template_id}' is declared but not implemented.",
                    "implement and validate the controller template before release",
                )
            )
        else:
            compiled_controller = route.controller_template_id

    if route.online_refinement_policy_id not in catalog.online_refinement_policies:
        gaps.append(
            _gap(
                "missing_online_refinement_policy",
                "online_refinement",
                route.online_refinement_policy_id,
                f"Online policy '{route.online_refinement_policy_id}' is not registered.",
                "implement and register the online refinement policy",
            )
        )

    compiled_tracking: list[str] = []
    for tracker_id in route.feature_tracking_requests:
        if tracker_id not in catalog.tracking_implementations:
            gaps.append(
                _gap(
                    "missing_tracking_implementation",
                    "feature_tracking",
                    tracker_id,
                    f"Feature tracker '{tracker_id}' is not registered.",
                    "implement and register the requested feature tracker",
                )
            )
        else:
            compiled_tracking.append(tracker_id)

    return CompiledRoute(
        candidate_route=route,
        capability_catalog_version=catalog.schema_version,
        gaps=gaps,
        executable=not any(gap.blocking for gap in gaps),
        compiled_experiment_ids=compiled_experiments,
        compiled_feature_extractor_ids=compiled_extractors,
        compiled_controller_template_id=compiled_controller,
        compiled_tracking_ids=compiled_tracking,
    )
