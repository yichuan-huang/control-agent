from __future__ import annotations

import hashlib
import itertools
from enum import Enum
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class CFDCModel(BaseModel):
    """Base model that rejects undeclared fields for auditable JSON output."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True, allow_inf_nan=False)


class SimulationBoundaryConfirmation(CFDCModel):
    confirmed: Literal[True] = True
    scope: Literal["software_simulation_only"] = "software_simulation_only"
    statement_version: Literal["v1"] = "v1"


class SystemDescription(CFDCModel):
    text: str = Field(min_length=1)
    observed_outputs: list[str] = Field(default_factory=list)
    actuators: list[str] = Field(default_factory=list)
    safety_bounds: dict[str, float] = Field(default_factory=dict)
    forbidden_actions: list[str] = Field(default_factory=list)
    time_scale_hint_s: float | None = Field(default=None, gt=0)
    simulation_boundary_confirmation: SimulationBoundaryConfirmation | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class DiagnosticField(CFDCModel):
    status: Literal["known", "inferred", "unknown"]
    value: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list)


class StabilityAssessment(str, Enum):
    STABLE = "stable"
    MARGINAL = "marginal"
    UNSTABLE = "unstable"
    UNKNOWN = "unknown"


class PhaseAssessment(str, Enum):
    MINIMUM_PHASE = "minimum_phase"
    NONMINIMUM_PHASE = "nonminimum_phase"
    UNKNOWN = "unknown"


class DelayAssessment(str, Enum):
    SIGNIFICANT = "significant"
    NOT_SIGNIFICANT = "not_significant"
    UNKNOWN = "unknown"


class RelativeDegreeAssessment(str, Enum):
    LOW = "low"
    HIGH = "high"
    UNKNOWN = "unknown"


class ControllabilityObservabilityAssessment(str, Enum):
    ADEQUATE = "adequate"
    INADEQUATE = "inadequate"
    UNKNOWN = "unknown"


class NonlinearityAssessment(str, Enum):
    WEAK = "weak"
    STATIC_COMPENSABLE = "static_compensable"
    STRONG_DYNAMIC = "strong_dynamic"
    UNKNOWN = "unknown"


class CouplingAssessment(str, Enum):
    SISO = "siso"
    WEAK_MIMO = "weak_mimo"
    SEVERE_MIMO = "severe_mimo"
    UNDERACTUATED = "underactuated"
    CASCADED = "cascaded"
    UNKNOWN = "unknown"


class UncertaintyAssessment(str, Enum):
    SMALL = "small"
    MODERATE = "moderate"
    LARGE = "large"
    UNKNOWN = "unknown"


class AssessedDiagnosticField(DiagnosticField):
    @model_validator(mode="after")
    def validate_unknown_consistency(self) -> AssessedDiagnosticField:
        assessment = getattr(self, "assessment", None)
        is_unknown = str(assessment) == "unknown"
        if (self.status == "unknown") != is_unknown:
            raise ValueError("diagnostic status and assessment must resolve together")
        if self.status != "unknown" and (not self.evidence or self.confidence < 0.5):
            raise ValueError(
                "resolved diagnostic fields require evidence and confidence >= 0.5"
            )
        return self


class StabilityField(AssessedDiagnosticField):
    assessment: StabilityAssessment


class PhaseField(AssessedDiagnosticField):
    assessment: PhaseAssessment


class SignificantDelayField(AssessedDiagnosticField):
    assessment: DelayAssessment


class RelativeDegreeField(AssessedDiagnosticField):
    assessment: RelativeDegreeAssessment
    estimated_order: int | None = Field(default=None, ge=1)


class ControllabilityObservabilityField(AssessedDiagnosticField):
    assessment: ControllabilityObservabilityAssessment


class NonlinearityField(AssessedDiagnosticField):
    assessment: NonlinearityAssessment


class CouplingField(AssessedDiagnosticField):
    assessment: CouplingAssessment


class UncertaintyField(AssessedDiagnosticField):
    assessment: UncertaintyAssessment


class StructuralDiagnosis(CFDCModel):
    open_loop_stability: StabilityField
    minimum_phase: PhaseField
    significant_delay: SignificantDelayField
    relative_degree: RelativeDegreeField
    controllability_observability: ControllabilityObservabilityField
    nonlinearity_strength: NonlinearityField
    coupling_severity: CouplingField
    uncertainty_magnitude: UncertaintyField
    clarification_questions: list[str] = Field(default_factory=list, max_length=4)
    complete: bool

    @model_validator(mode="after")
    def validate_questions(self) -> StructuralDiagnosis:
        if not self.complete and not (2 <= len(self.clarification_questions) <= 4):
            raise ValueError(
                "Incomplete diagnosis must include 2-4 clarification questions"
            )
        if self.complete and self.clarification_questions:
            raise ValueError(
                "Complete diagnosis should not include clarification questions"
            )
        return self

    @property
    def fields(self) -> list[AssessedDiagnosticField]:
        return [
            self.open_loop_stability,
            self.minimum_phase,
            self.significant_delay,
            self.relative_degree,
            self.controllability_observability,
            self.nonlinearity_strength,
            self.coupling_severity,
            self.uncertainty_magnitude,
        ]


class ArchetypeClass(str, Enum):
    CLASS_I_FIRST_ORDER_LAG = "class_i_first_order_lag"
    CLASS_II_SECOND_ORDER_OSCILLATOR = "class_ii_second_order_oscillator"
    CLASS_III_DOUBLE_OR_PURE_INTEGRATOR = "class_iii_double_or_pure_integrator"
    CLASS_IV_HIGHER_ORDER_UNSTABLE_NONLINEAR_OR_NMP = (
        "class_iv_higher_order_unstable_nonlinear_or_nmp"
    )
    CLASS_V_MULTIVARIABLE_SIGNIFICANT_COUPLING = (
        "class_v_multivariable_significant_coupling"
    )


class ArchetypeClassification(CFDCModel):
    primary_class: ArchetypeClass
    control_architecture: str
    required_core_features: list[str] = Field(min_length=1, max_length=6)
    safety_constraints: list[str] = Field(default_factory=list)
    rationale: str
    supplemental_mechanism_cards: list[str] = Field(default_factory=list)


class SimulationProfile(CFDCModel):
    profile_id: str = Field(min_length=1)
    compatible_class: ArchetypeClass
    semantic_description: str = Field(min_length=1)
    feature_bundle_id: str = Field(min_length=1)
    required_feature_ids: list[str] = Field(min_length=1)
    controller_template_id: str = Field(min_length=1)
    simulator_backend: str = Field(min_length=1)
    experiment_primitives: list[str] = Field(min_length=1)
    tunable_gain_names: list[str] = Field(default_factory=list)
    tracking_ids: list[str] = Field(default_factory=list)
    change_scenario_id: str = Field(min_length=1)


class SimulationProfileCatalog(CFDCModel):
    schema_version: str = "1.0"
    profiles: list[SimulationProfile] = Field(min_length=1)


class ControlMethodProfile(CFDCModel):
    profile_id: str = Field(min_length=1)
    compatible_class: ArchetypeClass
    semantic_description: str = Field(min_length=1)
    feature_bundle_id: str = Field(min_length=1)
    required_feature_ids: list[str] = Field(min_length=1)
    controller_template_id: str = Field(min_length=1)
    experiment_primitives: list[str] = Field(min_length=1)
    tunable_gain_names: list[str] = Field(default_factory=list)
    tracking_ids: list[str] = Field(default_factory=list)


class ControlMethodProfileCatalog(CFDCModel):
    schema_version: str = "2.0"
    profiles: list[ControlMethodProfile] = Field(min_length=1)


class DemoPlantFixture(CFDCModel):
    fixture_id: str = Field(min_length=1)
    method_profile_id: str = Field(min_length=1)
    simulator_backend: str = Field(min_length=1)
    nominal_parameters: dict[str, Any] = Field(min_length=1)
    initial_state: dict[str, float] = Field(default_factory=dict)
    change_scenario_id: str = Field(min_length=1)
    evidence_boundary: str = "demo_fixture_only"


class DemoPlantFixtureCatalog(CFDCModel):
    schema_version: str = "2.0"
    fixtures: list[DemoPlantFixture] = Field(min_length=1)


class SemanticRouteSelection(CFDCModel):
    simulation_profile_id: str = Field(min_length=1)
    feature_bundle_id: str = Field(min_length=1)
    selected_feature_ids: list[str] = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[str] = Field(min_length=1)
    rationale: str = Field(min_length=1)


class EvidenceExperimentRequirement(CFDCModel):
    primitive: str = Field(min_length=1)
    feature_ids: list[str] = Field(min_length=1)
    required_signal_ids: list[str] = Field(min_length=1)
    minimum_measured_repeats: int = Field(default=3, ge=1)
    metadata_requirements: list[str] = Field(
        default_factory=lambda: [
            "signal_units",
            "operating_region",
            "trial_id",
            "data_source",
        ]
    )


class EvidenceRequirementPlan(CFDCModel):
    plant_id: str = Field(min_length=1)
    method_profile_id: str = Field(min_length=1)
    required_feature_ids: list[str] = Field(min_length=1)
    accepted_sources: list[
        Literal[
            "declared_specification",
            "structured_mathematical_model",
            "measured_traces_reserved_for_later",
        ]
    ] = Field(min_length=2)
    experiment_requirements: list[EvidenceExperimentRequirement] = Field(min_length=1)
    missing_items: list[str] = Field(default_factory=list)
    supplemental_questions: list[str] = Field(default_factory=list)
    evidence_boundary: str = "object_evidence_requirements_only"


class SpecificationFieldDefinition(CFDCModel):
    fact_id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    canonical_unit: str = Field(min_length=1)
    accepted_units: list[str] = Field(min_length=1)
    unit_policy: Literal[
        "dimensioned",
        "open",
        "motion_acceleration",
        "actuator_per_input",
        "structured",
    ] = "dimensioned"
    prompt_template: str = Field(min_length=1)
    why_needed: str = Field(min_length=1)
    where_to_find: str = Field(min_length=1)
    example_template: str = Field(min_length=1)
    answer_kind: Literal["number", "matrix", "structured_model"] = "number"


class SpecificationCompletionPath(CFDCModel):
    path_id: str = Field(min_length=1)
    required_fact_ids: list[str] = Field(min_length=1)


class SpecificationTemplate(CFDCModel):
    template_id: str = Field(min_length=1)
    method_profile_id: str = Field(min_length=1)
    user_summary: str = Field(min_length=1)
    fields: list[SpecificationFieldDefinition] = Field(default_factory=list)
    completion_paths: list[SpecificationCompletionPath] = Field(min_length=1)
    compiler_id: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_completion_paths(self) -> SpecificationTemplate:
        known = {item.fact_id for item in self.fields}
        referenced = {
            fact_id
            for path in self.completion_paths
            for fact_id in path.required_fact_ids
        }
        if referenced - known:
            raise ValueError(
                "completion paths reference unknown specification facts: "
                + ", ".join(sorted(referenced - known))
            )
        return self


class SpecificationTemplateCatalog(CFDCModel):
    schema_version: str = "1.0"
    templates: list[SpecificationTemplate] = Field(min_length=1)


SpecificationValue = float | list[float] | list[list[float]]


class SpecificationDerivationInput(CFDCModel):
    name: str = Field(min_length=1)
    value: float
    unit: str = Field(min_length=1)
    source_text: str = Field(min_length=1)


class SpecificationDerivation(CFDCModel):
    rule_id: str = Field(min_length=1)
    expression: str = Field(min_length=1)
    inputs: list[SpecificationDerivationInput] = Field(default_factory=list)
    source_excerpts: list[str] = Field(min_length=1)


class SpecificationFact(CFDCModel):
    fact_id: str = Field(min_length=1)
    value: SpecificationValue
    unit: str = Field(min_length=1)
    source_type: Literal[
        "manufacturer_document",
        "user_known_behavior",
        "structured_answer",
        "derived_from_declared_physics",
    ]
    source_text: str = Field(min_length=1)
    derivation: SpecificationDerivation | None = None
    lower_bound: float | None = None
    upper_bound: float | None = None

    @model_validator(mode="after")
    def validate_uncertainty_bounds(self) -> SpecificationFact:
        is_derived = self.source_type == "derived_from_declared_physics"
        if is_derived != (self.derivation is not None):
            raise ValueError(
                "derived specification facts require derivation evidence, and direct facts must not include it"
            )
        if isinstance(self.value, float):
            if self.lower_bound is not None and self.lower_bound > self.value:
                raise ValueError("lower_bound cannot exceed the specification value")
            if self.upper_bound is not None and self.upper_bound < self.value:
                raise ValueError("upper_bound cannot be below the specification value")
        elif self.lower_bound is not None or self.upper_bound is not None:
            raise ValueError("matrix/list specification facts do not use scalar bounds")
        return self


class SpecificationQuestion(CFDCModel):
    question_id: str = Field(min_length=1)
    requested_fact_ids: list[str] = Field(min_length=1)
    prompt: str = Field(min_length=1)
    why_needed: str = Field(min_length=1)
    where_to_find: str = Field(min_length=1)
    answer_kind: Literal["number", "matrix", "structured_model"] = "number"
    unit_hint: str = Field(min_length=1)
    example: str = Field(min_length=1)
    answer_options: list[str] = Field(
        default_factory=lambda: [
            "填写已知数值",
            "粘贴手册规格",
            "暂时不知道",
            "改用完整数值模型",
        ],
        min_length=4,
        max_length=4,
    )


class SpecificationAssessment(CFDCModel):
    status: Literal["need_more", "conflict", "ready"]
    template_id: str = Field(min_length=1)
    facts: list[SpecificationFact] = Field(default_factory=list)
    missing_fact_ids: list[str] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)
    rejected_facts: list[str] = Field(default_factory=list)
    questions: list[SpecificationQuestion] = Field(default_factory=list, max_length=4)
    rationale: str = Field(min_length=1)
    no_progress: bool = False

    @model_validator(mode="after")
    def validate_status_consistency(self) -> SpecificationAssessment:
        if self.status == "ready" and (self.missing_fact_ids or self.conflicts):
            raise ValueError(
                "a ready specification assessment cannot contain gaps or conflicts"
            )
        if self.status == "conflict" and not self.conflicts:
            raise ValueError("a conflict assessment must explain at least one conflict")
        return self


class TransferFunctionModelSpec(CFDCModel):
    kind: Literal["transfer_function"] = "transfer_function"
    numerator: list[float] = Field(min_length=1)
    denominator: list[float] = Field(min_length=1)
    time_domain: Literal["continuous", "discrete"] = "continuous"
    sample_time_s: float | None = Field(default=None, gt=0.0)
    input_delay_s: float = Field(default=0.0, ge=0.0)
    input_signal_id: str = Field(min_length=1)
    output_signal_id: str = Field(min_length=1)
    input_units: str = "unspecified"
    output_units: str = "unspecified"
    parameter_uncertainty: dict[str, float] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_transfer_function(self) -> TransferFunctionModelSpec:
        if not any(abs(value) > 0.0 for value in self.denominator):
            raise ValueError("denominator must contain a non-zero coefficient")
        if self.time_domain == "discrete" and self.sample_time_s is None:
            raise ValueError(
                "sample_time_s is required for a discrete transfer function"
            )
        if self.time_domain == "continuous" and self.sample_time_s is not None:
            raise ValueError(
                "sample_time_s is only valid for a discrete transfer function"
            )
        return self


class StateSpaceModelSpec(CFDCModel):
    kind: Literal["state_space"] = "state_space"
    a: list[list[float]] = Field(min_length=1)
    b: list[list[float]] = Field(min_length=1)
    c: list[list[float]] = Field(min_length=1)
    d: list[list[float]] = Field(min_length=1)
    time_domain: Literal["continuous", "discrete"] = "continuous"
    sample_time_s: float | None = Field(default=None, gt=0.0)
    state_names: list[str] = Field(min_length=1)
    input_signal_ids: list[str] = Field(min_length=1)
    output_signal_ids: list[str] = Field(min_length=1)
    initial_state: list[float] = Field(min_length=1)
    signal_units: dict[str, str] = Field(default_factory=dict)
    parameter_uncertainty: dict[str, float] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_state_space_dimensions(self) -> StateSpaceModelSpec:
        n = len(self.a)
        m = len(self.input_signal_ids)
        p = len(self.output_signal_ids)
        if any(len(row) != n for row in self.a):
            raise ValueError("A must be square")
        if len(self.b) != n or any(len(row) != m for row in self.b):
            raise ValueError("B dimensions must be state_count x input_count")
        if len(self.c) != p or any(len(row) != n for row in self.c):
            raise ValueError("C dimensions must be output_count x state_count")
        if len(self.d) != p or any(len(row) != m for row in self.d):
            raise ValueError("D dimensions must be output_count x input_count")
        if len(self.state_names) != n:
            raise ValueError("state_names must match A dimensions")
        if len(self.initial_state) != n:
            raise ValueError("initial_state must match A dimensions")
        if self.time_domain == "discrete" and self.sample_time_s is None:
            raise ValueError(
                "sample_time_s is required for a discrete state-space model"
            )
        if self.time_domain == "continuous" and self.sample_time_s is not None:
            raise ValueError(
                "sample_time_s is only valid for a discrete state-space model"
            )
        return self


class RegisteredNonlinearModelSpec(CFDCModel):
    kind: Literal["registered_nonlinear"] = "registered_nonlinear"
    template_id: Literal["underactuated_cartpole", "vtol_cascaded"]
    parameters: dict[str, float] = Field(min_length=1)
    initial_state: dict[str, float] = Field(default_factory=dict)
    input_signal_ids: list[str] = Field(min_length=1)
    output_signal_ids: list[str] = Field(min_length=1)
    signal_units: dict[str, str] = Field(default_factory=dict)
    parameter_uncertainty: dict[str, float] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_registered_model_is_complete(self) -> RegisteredNonlinearModelSpec:
        required_parameters = {
            "underactuated_cartpole": {
                "cart_mass_kg",
                "pole_mass_kg",
                "com_length_m",
                "pole_inertia_kg_m2",
                "cart_friction_n_s_m",
                "gravity_m_s2",
                "force_limit_n",
                "cart_position_limit_m",
            },
            "vtol_cascaded": {
                "mass_kg",
                "pitch_inertia_kg_m2",
                "gravity_m_s2",
                "linear_drag_n_s_m",
                "pitch_damping_n_m_s",
                "thrust_min_n",
                "thrust_max_n",
                "torque_limit_n_m",
            },
        }[self.template_id]
        required_initial_state = {
            "underactuated_cartpole": {
                "position_m",
                "velocity_m_s",
                "angle_rad",
                "angular_rate_rad_s",
            },
            "vtol_cascaded": {
                "x_m",
                "z_m",
                "pitch_rad",
                "x_velocity_m_s",
                "z_velocity_m_s",
                "pitch_rate_rad_s",
            },
        }[self.template_id]
        if set(self.parameters) != required_parameters:
            missing = sorted(required_parameters - set(self.parameters))
            unknown = sorted(set(self.parameters) - required_parameters)
            raise ValueError(
                "registered nonlinear models require the complete parameter set; "
                f"missing={missing}, unknown={unknown}"
            )
        strictly_positive = {
            "underactuated_cartpole": {
                "cart_mass_kg",
                "pole_mass_kg",
                "com_length_m",
                "pole_inertia_kg_m2",
                "gravity_m_s2",
                "force_limit_n",
                "cart_position_limit_m",
            },
            "vtol_cascaded": {
                "mass_kg",
                "pitch_inertia_kg_m2",
                "gravity_m_s2",
                "thrust_max_n",
                "torque_limit_n_m",
            },
        }[self.template_id]
        nonnegative = {
            "underactuated_cartpole": {"cart_friction_n_s_m"},
            "vtol_cascaded": {
                "linear_drag_n_s_m",
                "pitch_damping_n_m_s",
                "thrust_min_n",
            },
        }[self.template_id]
        invalid_positive = sorted(
            name for name in strictly_positive if self.parameters[name] <= 0.0
        )
        invalid_nonnegative = sorted(
            name for name in nonnegative if self.parameters[name] < 0.0
        )
        if invalid_positive or invalid_nonnegative:
            raise ValueError(
                "registered nonlinear model parameters are outside their physical domain; "
                f"must_be_positive={invalid_positive}, must_be_nonnegative={invalid_nonnegative}"
            )
        if (
            self.template_id == "vtol_cascaded"
            and self.parameters["thrust_min_n"] >= self.parameters["thrust_max_n"]
        ):
            raise ValueError("thrust_min_n must be less than thrust_max_n")
        if set(self.initial_state) != required_initial_state:
            missing = sorted(required_initial_state - set(self.initial_state))
            unknown = sorted(set(self.initial_state) - required_initial_state)
            raise ValueError(
                "registered nonlinear models require the complete initial state; "
                f"missing={missing}, unknown={unknown}"
            )
        if (
            self.template_id == "underactuated_cartpole"
            and abs(self.initial_state["position_m"])
            > self.parameters["cart_position_limit_m"]
        ):
            raise ValueError("initial cart position exceeds cart_position_limit_m")
        return self


ExecutableModelSpec = Annotated[
    TransferFunctionModelSpec | StateSpaceModelSpec | RegisteredNonlinearModelSpec,
    Field(discriminator="kind"),
]


class MeasuredTraceManifest(CFDCModel):
    csv_path: str = Field(min_length=1)
    primitive: ExperimentPrimitive
    repeat_index: int = Field(ge=1)
    time_column: str = Field(min_length=1)
    signal_columns: dict[str, str] = Field(min_length=1)
    signal_units: dict[str, str] = Field(min_length=1)
    estimates: list[str] = Field(min_length=1)
    operating_region: str = Field(min_length=1)
    trial_id: str = Field(min_length=1)
    data_source: str = Field(min_length=1)


class ClosedLoopValidationSpec(CFDCModel):
    reference: dict[str, float] = Field(min_length=1)
    horizon_s: float = Field(gt=0.0)
    sample_time_s: float = Field(gt=0.0)
    actuator_limits: dict[str, float] = Field(min_length=1)
    state_limits: dict[str, float] = Field(min_length=1)
    performance_limits: dict[str, float] = Field(min_length=1)
    initial_state: dict[str, float] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_required_limits(self) -> ClosedLoopValidationSpec:
        required = {
            "actuator_limits": {"input_min", "input_max"},
            "state_limits": {"output_min", "output_max"},
            "performance_limits": {
                "max_abs_final_error",
                "max_overshoot",
                "max_settling_time_s",
                "max_saturation_fraction",
            },
        }
        for field_name, keys in required.items():
            values = getattr(self, field_name)
            missing = sorted(keys - set(values))
            if missing:
                raise ValueError(
                    f"{field_name} is missing required key(s): {', '.join(missing)}"
                )
        if self.actuator_limits["input_min"] >= self.actuator_limits["input_max"]:
            raise ValueError("input_min must be less than input_max")
        if self.state_limits["output_min"] >= self.state_limits["output_max"]:
            raise ValueError("output_min must be less than output_max")
        if not 0.0 <= self.performance_limits["max_saturation_fraction"] <= 1.0:
            raise ValueError("max_saturation_fraction must lie between 0 and 1")
        if self.sample_time_s * 2.0 > self.horizon_s:
            raise ValueError("validation horizon must contain at least three samples")
        return self


class PlantEvidencePackage(CFDCModel):
    evidence_package_id: str | None = None
    plant_id: str = Field(min_length=1)
    model: ExecutableModelSpec | None = None
    measured_traces: list[MeasuredTraceManifest] = Field(default_factory=list)
    validation_spec: ClosedLoopValidationSpec | None = None
    provenance: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_evidence_source(self) -> PlantEvidencePackage:
        if self.model is None and not self.measured_traces:
            raise ValueError(
                "evidence package requires a model or measured trace manifest"
            )
        if self.evidence_package_id is None:
            payload = self.model_dump_json(exclude={"evidence_package_id"})
            self.evidence_package_id = (
                f"evidence-{hashlib.sha256(payload.encode()).hexdigest()[:20]}"
            )
        return self


class DeclaredSpecificationEvidence(CFDCModel):
    plant_id: str = Field(min_length=1)
    template_id: str = Field(min_length=1)
    facts: list[SpecificationFact] = Field(min_length=1)
    answer_history: list[str] = Field(default_factory=list)
    evidence_boundary: str = "declared_specification_only"


class CompiledSpecificationModel(CFDCModel):
    plant_id: str = Field(min_length=1)
    template_id: str = Field(min_length=1)
    model: ExecutableModelSpec
    derived_features: dict[str, float | list[list[float]]] = Field(default_factory=dict)
    parameter_sources: dict[str, list[str]] = Field(default_factory=dict)
    safety_bounds: dict[str, float] = Field(default_factory=dict)
    time_scale_hint_s: float = Field(gt=0.0)
    assumptions: list[str] = Field(default_factory=list)
    model_sha256: str | None = None
    evidence_boundary: str = "declared_specification_model_only"

    @model_validator(mode="after")
    def populate_model_hash(self) -> CompiledSpecificationModel:
        if self.model_sha256 is None:
            payload = self.model.model_dump_json()
            self.model_sha256 = hashlib.sha256(payload.encode()).hexdigest()
        return self


class EvidenceReadinessDecision(CFDCModel):
    decision: Literal["ready", "rejected"]
    source_types: list[Literal["mathematical_model", "measured_traces"]] = Field(
        default_factory=list
    )
    gaps: list[CapabilityGap] = Field(default_factory=list)
    evidence_boundary: str = "object_evidence_readiness"


class ExperimentPrimitive(str, Enum):
    FREE_DECAY = "free_decay"
    RAMP_STEP = "ramp_step"
    PULSE = "pulse"
    HOVER_THRUST = "hover_thrust"
    BOUNDED_SCAN = "bounded_scan"


class ExperimentInstruction(CFDCModel):
    primitive: ExperimentPrimitive
    title: str
    operator_steps: list[str] = Field(min_length=1)
    data_to_record: list[str] = Field(min_length=1)
    estimates: list[str] = Field(min_length=1)
    stop_conditions: list[str] = Field(min_length=1)
    safety_note: str
    input_amplitude: float | None = None
    input_amplitude_units: str | None = None
    duration_s: float | None = Field(default=None, gt=0.0)
    sample_rate_hz: float | None = Field(default=None, gt=0.0)
    operating_region: str | None = None
    required_safety_bounds: list[str] = Field(default_factory=list)


class ExperimentPlan(CFDCModel):
    archetype: ArchetypeClass
    instructions: list[ExperimentInstruction] = Field(max_length=5)
    planning_gaps: list[CapabilityGap] = Field(default_factory=list)
    parameterization_status: Literal[
        "unparameterized_simulation_template",
        "parameterized",
        "blocked",
    ] = "unparameterized_simulation_template"
    evidence_boundary: str = "software_simulation_experiment_plan"


class ExperimentTrace(CFDCModel):
    time_s: list[float] = Field(min_length=3)
    signals: dict[str, list[float]] = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("time_s")
    @classmethod
    def validate_time(cls, values: list[float]) -> list[float]:
        if any(curr <= prev for prev, curr in itertools.pairwise(values)):
            raise ValueError("time_s must be strictly increasing")
        return values

    @field_validator("signals")
    @classmethod
    def validate_signals(
        cls, signals: dict[str, list[float]]
    ) -> dict[str, list[float]]:
        cleaned: dict[str, list[float]] = {}
        for name, values in signals.items():
            clean_name = name.strip()
            if not clean_name:
                raise ValueError("signal names must be non-empty")
            if len(values) < 3:
                raise ValueError(
                    f"signal '{clean_name}' must contain at least three samples"
                )
            cleaned[clean_name] = values
        return cleaned

    @model_validator(mode="after")
    def validate_signal_lengths(self) -> ExperimentTrace:
        expected = len(self.time_s)
        mismatched = [
            name for name, values in self.signals.items() if len(values) != expected
        ]
        if mismatched:
            names = ", ".join(sorted(mismatched))
            raise ValueError(f"signals must match time_s length: {names}")
        return self


class SimulationExperimentRecord(CFDCModel):
    plant_id: str | None = None
    evidence_package_id: str | None = None
    model_sha256: str | None = None
    evidence_source: Literal[
        "legacy_simulation",
        "model_simulation",
        "measured_trace",
        "demo_fixture",
    ] = "legacy_simulation"
    primitive: ExperimentPrimitive
    estimates: list[str] = Field(min_length=1)
    trace: ExperimentTrace
    instruction_title: str | None = None
    repeat_index: int = Field(default=1, ge=1, le=5)
    experiment_protocol_version: str = "simulation-v1"
    operating_region: str = "unspecified"
    evidence_boundary: str = "software_simulation_only"
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("estimates")
    @classmethod
    def validate_estimates(cls, estimates: list[str]) -> list[str]:
        deduped: list[str] = []
        for estimate in estimates:
            clean = estimate.strip()
            if not clean:
                raise ValueError("estimates must be non-empty strings")
            if clean not in deduped:
                deduped.append(clean)
        return deduped


class CoreFeatureArtifact(CFDCModel):
    object_id: str | None = None
    plant_id: str | None = None
    evidence_package_id: str | None = None
    model_sha256: str | None = None
    evidence_source: Literal[
        "legacy",
        "model_simulation",
        "measured_trace",
        "demo_fixture",
    ] = "legacy"
    feature_id: str
    value: float | list[list[float]]
    lower_bound: float | None = None
    upper_bound: float | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    units: str
    method: str
    source_experiment: ExperimentPrimitive
    trace_sha256: str | None = None
    experiment_protocol_version: str = "legacy-v1"
    estimator_version: str = "cfdc-estimator-v1"
    operating_region: str = "unspecified"
    applicable_plant_families: list[str] = Field(default_factory=list)
    invalidating_conditions: list[str] = Field(default_factory=list)
    data_quality_flags: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_bounds(self) -> CoreFeatureArtifact:
        if isinstance(self.value, list):
            if self.feature_id != "local_gain_matrix":
                raise ValueError("Only local_gain_matrix may carry a matrix value")
            if self.lower_bound is not None or self.upper_bound is not None:
                raise ValueError(
                    "Matrix features use element values instead of scalar bounds"
                )
            width = len(self.value[0]) if self.value else 0
            if (
                len(self.value) < 2
                or width < 2
                or any(len(row) != width for row in self.value)
            ):
                raise ValueError(
                    "local_gain_matrix must be a rectangular matrix of at least 2x2"
                )
        else:
            if self.lower_bound is None or self.upper_bound is None:
                raise ValueError("Scalar features require lower_bound and upper_bound")
            if self.lower_bound > self.value or self.upper_bound < self.value:
                raise ValueError("Feature value must lie inside confidence bounds")
        if self.object_id is None:
            serialized_value = (
                repr(self.value)
                if isinstance(self.value, list)
                else f"{self.value:.17g}"
            )
            identity = "|".join(
                (
                    self.feature_id,
                    str(self.source_experiment),
                    self.method,
                    serialized_value,
                    self.trace_sha256 or "no-trace",
                )
            )
            self.object_id = (
                f"feature-{hashlib.sha256(identity.encode()).hexdigest()[:20]}"
            )
        return self


class FeatureQualityPolicy(CFDCModel):
    minimum_confidence: float = Field(default=0.70, ge=0.0, le=1.0)
    maximum_relative_half_width: float = Field(default=0.50, gt=0.0)


class FeatureQualityIssue(CFDCModel):
    code: str = Field(min_length=1)
    feature_id: str
    severity: Literal["repeat_experiment", "refuse"]
    explanation: str = Field(min_length=1)


class FeatureQualityDecision(CFDCModel):
    decision: Literal["accept", "repeat_experiment", "refuse"]
    issues: list[FeatureQualityIssue] = Field(default_factory=list)
    accepted_feature_ids: list[str] = Field(default_factory=list)
    policy: FeatureQualityPolicy = Field(default_factory=FeatureQualityPolicy)
    evidence_boundary: str = "software_simulation_feature_release_decision"


class ControllerCandidate(CFDCModel):
    plant_id: str | None = None
    method_profile_id: str | None = None
    architecture: str
    gains: dict[str, float] = Field(default_factory=dict)
    design_parameters: dict[str, float] = Field(default_factory=dict)
    tunable_gain_names: list[str] = Field(default_factory=list)
    feedforward: dict[str, float] = Field(default_factory=dict)
    saturation: dict[str, float] = Field(default_factory=dict)
    constraints: list[str] = Field(default_factory=list)
    source_features: list[str] = Field(default_factory=list)
    source_feature_artifact_ids: list[str] = Field(default_factory=list)
    parameter_provenance: dict[str, list[str]] = Field(default_factory=dict)
    release_level: Literal[
        "legacy",
        "candidate_unvalidated",
        "validated_in_simulation",
        "demo_fixture_only",
        "refuse",
    ] = "legacy"
    status: Literal["ready_for_conservative_trial", "requires_online_search", "refuse"]
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_tunable_gain_names(self) -> ControllerCandidate:
        unknown = set(self.tunable_gain_names) - set(self.gains)
        if unknown:
            raise ValueError(
                f"tunable gains must exist in gains: {', '.join(sorted(unknown))}"
            )
        if len(self.tunable_gain_names) != len(set(self.tunable_gain_names)):
            raise ValueError("tunable_gain_names must not contain duplicates")
        return self


class GoNoGoDecision(CFDCModel):
    decision: Literal["go", "no_go"]
    reasons: list[str] = Field(default_factory=list)
    missing_features: list[str] = Field(default_factory=list)
    route_compatible: bool = True
    feature_complete: bool = True


class OnlinePerformanceMetrics(CFDCModel):
    overshoot: float = Field(ge=0.0)
    settling_time_s: float | None = Field(default=None, ge=0.0)
    integral_absolute_error: float = Field(ge=0.0)
    high_frequency_control_rms: float = Field(ge=0.0)
    actuator_saturation_fraction: float = Field(ge=0.0, le=1.0)
    nmp_undershoot: float = Field(default=0.0, ge=0.0)


class ChannelPerformanceMetrics(CFDCModel):
    reference: float
    final_output: float
    final_error: float
    abs_final_error: float = Field(ge=0.0)
    overshoot: float = Field(ge=0.0)
    undershoot: float = Field(ge=0.0)
    settled: bool
    settling_time_s: float | None = Field(default=None, ge=0.0)
    integral_absolute_error: float = Field(ge=0.0)
    max_abs_output: float = Field(ge=0.0)
    max_abs_error: float = Field(ge=0.0)


class SimulationPerformanceSummary(CFDCModel):
    primary_channel: str
    final_output: float
    final_error: float
    abs_final_error: float = Field(ge=0.0)
    overshoot: float = Field(ge=0.0)
    undershoot: float = Field(ge=0.0)
    settled: bool
    settling_time_s: float | None = Field(default=None, ge=0.0)
    saturation_fraction: float = Field(ge=0.0, le=1.0)
    success: bool
    channels: dict[str, ChannelPerformanceMetrics] = Field(default_factory=dict)
    actuator_saturation_fractions: dict[str, float] = Field(default_factory=dict)
    state_boundaries: dict[str, float] = Field(default_factory=dict)
    limits: dict[str, float] = Field(default_factory=dict)
    violations: list[str] = Field(default_factory=list)
    capture_success: bool | None = None
    capture_time_s: float | None = Field(default=None, ge=0.0)
    boundary_triggered: bool | None = None
    boundary_reason: str | None = None


class ControllerComparison(CFDCModel):
    case_id: str
    cfdc_controller: str
    baseline_controller: str
    primary_channel: str
    same_plant: bool = True
    same_initial_state: bool = True
    same_reference: bool = True
    same_horizon: bool = True
    same_limits: bool = True
    matched_conditions: dict[str, Any] = Field(default_factory=dict)
    cfdc_performance: SimulationPerformanceSummary
    baseline_performance: SimulationPerformanceSummary
    settling_time_delta_s: float | None = None
    abs_final_error_delta: float
    saturation_fraction_delta: float
    notes: list[str] = Field(default_factory=list)
    evidence_boundary: str = "software_simulation_controller_comparison"


class BenchmarkRouteIR(CFDCModel):
    case_id: str
    plant_family: str
    reference: dict[str, float]
    horizon_s: float = Field(gt=0.0)
    dt_s: float = Field(gt=0.0)
    plant_params: dict[str, float]
    initial_state: dict[str, float] = Field(default_factory=dict)
    actuator_limits: dict[str, float]
    state_limits: dict[str, float] = Field(default_factory=dict)
    performance_limits: dict[str, float] = Field(default_factory=dict)
    evidence_boundary: str = "software_simulation_benchmark_route_ir"


class CandidateExperimentRequest(CFDCModel):
    request_id: str = Field(min_length=1)
    primitive: str = Field(min_length=1)
    input_signal_ids: list[str] = Field(default_factory=list)
    output_signal_ids: list[str] = Field(default_factory=list)
    feature_ids: list[str] = Field(min_length=1)
    input_amplitude: float | None = None
    duration_s: float | None = Field(default=None, gt=0.0)
    sample_rate_hz: float | None = Field(default=None, gt=0.0)
    operating_region: str = "declared_safe_operating_region"
    stop_conditions: list[str] = Field(min_length=1)


class CandidateRouteIR(CFDCModel):
    schema_version: str = "1.0"
    route_id: str = Field(min_length=1)
    canonical_class: ArchetypeClass
    simulation_profile_id: str = Field(min_length=1)
    supplemental_mechanism_cards: list[str] = Field(default_factory=list)
    control_architecture_id: str = Field(min_length=1)
    experiment_requests: list[CandidateExperimentRequest] = Field(default_factory=list)
    required_core_feature_ids: list[str] = Field(min_length=1)
    optional_core_feature_ids: list[str] = Field(default_factory=list)
    controller_template_id: str = Field(min_length=1)
    tunable_gain_names: list[str] = Field(default_factory=list)
    online_refinement_policy_id: str = Field(min_length=1)
    feature_tracking_requests: list[str] = Field(default_factory=list)
    validation_metrics: list[str] = Field(min_length=1)
    safety_constraints: list[str] = Field(min_length=1)
    evidence_boundary: str = "software_simulation_candidate_route"


class CapabilityGap(CFDCModel):
    code: str = Field(min_length=1)
    stage: str = Field(min_length=1)
    capability_id: str = Field(min_length=1)
    explanation: str = Field(min_length=1)
    resolvable_by_measurement: bool = False
    required_next_action: str = Field(min_length=1)
    blocking: bool = True


class PrimitiveSignalRequirement(CFDCModel):
    input_required: bool = True
    output_required: bool = True


class ControllerTemplateCapability(CFDCModel):
    compatible_classes: list[ArchetypeClass] = Field(min_length=1)
    required_feature_ids: list[str] = Field(default_factory=list)
    implemented: bool = True


class CapabilityCatalog(CFDCModel):
    schema_version: str = "1.0"
    experiment_primitive_classes: dict[str, list[ArchetypeClass]]
    primitive_signal_requirements: dict[str, PrimitiveSignalRequirement]
    feature_extractors: dict[str, list[str]]
    controller_templates: dict[str, ControllerTemplateCapability]
    online_refinement_policies: list[str]
    tracking_implementations: list[str]
    simulation_fixture_routes: list[str]


class CompiledRoute(CFDCModel):
    candidate_route: CandidateRouteIR
    capability_catalog_version: str
    gaps: list[CapabilityGap] = Field(default_factory=list)
    executable: bool
    compiled_experiment_ids: list[str] = Field(default_factory=list)
    compiled_feature_extractor_ids: list[str] = Field(default_factory=list)
    compiled_controller_template_id: str | None = None
    compiled_tracking_ids: list[str] = Field(default_factory=list)
    evidence_boundary: str = "software_simulation_capability_compilation"


class DiagnosticTurn(CFDCModel):
    turn_index: int = Field(ge=1)
    questions: list[str] = Field(min_length=1)
    answers: dict[str, str]
    evidence: list[str] = Field(min_length=1)
    diagnosis: StructuralDiagnosis


DiagnosticFieldId = Literal[
    "open_loop_stability",
    "minimum_phase",
    "significant_delay",
    "relative_degree",
    "controllability_observability",
    "nonlinearity_strength",
    "coupling_severity",
    "uncertainty_magnitude",
]


class DescriptionGuidance(CFDCModel):
    """A record-only prompt for one structural diagnostic field."""

    diagnostic_field_id: DiagnosticFieldId
    prompt: str = Field(min_length=1)
    why_needed: str = Field(min_length=1)
    response: str = "unknown"
    accepted_sources: list[Literal["existing_record", "manual_report"]] = Field(
        default_factory=lambda: ["existing_record", "manual_report"], min_length=1
    )

    @field_validator("prompt", "response")
    @classmethod
    def strip_guidance_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("description guidance text must be non-empty")
        return normalized

    @field_validator("prompt")
    @classmethod
    def validate_record_only_prompt(cls, value: str) -> str:
        normalized = value.strip()
        if (
            "existing record" not in normalized.lower()
            and "manual report" not in normalized.lower()
        ):
            raise ValueError(
                "description guidance must request an existing record or manual report"
            )
        forbidden = ("amplitude", "duration", "physical hardware", "issue a command")
        if any(term in normalized.lower() for term in forbidden):
            raise ValueError(
                "description guidance must not prescribe physical measurements"
            )
        return normalized


class DescriptionSignalEvidence(CFDCModel):
    """One signal name extracted from a verbatim description excerpt."""

    name: str = Field(min_length=1)
    source_excerpt: str = Field(min_length=1)

    @field_validator("name", "source_excerpt")
    @classmethod
    def strip_nonblank_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("description signal evidence must be non-empty")
        return normalized

    @model_validator(mode="after")
    def validate_name_provenance(self) -> DescriptionSignalEvidence:
        def normalize(value: str) -> str:
            return " ".join(value.casefold().split())

        if normalize(self.name) not in normalize(self.source_excerpt):
            raise ValueError(
                "description signal name must occur within its source_excerpt"
            )
        return self


class DescriptionGuidanceAssessment(CFDCModel):
    """Strict LLM extraction result for the fixed description checklist."""

    guidance: list[DescriptionGuidance] = Field(min_length=8, max_length=8)
    observed_outputs: list[DescriptionSignalEvidence] = Field(default_factory=list)
    actuators: list[DescriptionSignalEvidence] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_fixed_guidance_order(self) -> DescriptionGuidanceAssessment:
        required = [
            "open_loop_stability",
            "minimum_phase",
            "significant_delay",
            "relative_degree",
            "controllability_observability",
            "nonlinearity_strength",
            "coupling_severity",
            "uncertainty_magnitude",
        ]
        if [item.diagnostic_field_id for item in self.guidance] != required:
            raise ValueError(
                "description guidance must preserve the fixed diagnostic-field order"
            )
        return self


class DiagnosticChecklistItem(CFDCModel):
    diagnostic_field_id: DiagnosticFieldId
    label: str = Field(min_length=1)
    status: Literal["known", "inferred", "unknown"]
    evidence: list[str] = Field(default_factory=list)
    guidance: DescriptionGuidance


class MeasurementRequest(CFDCModel):
    """One request to report facts already present in a record or manual."""

    request_id: str = Field(min_length=1)
    diagnostic_field_id: DiagnosticFieldId
    title: str = Field(min_length=1)
    safety_scope: Literal["existing_records_only"] = "existing_records_only"
    instruction: str = Field(default="Review an existing record.", min_length=1)
    source_hint: str = Field(default="Review an existing record.", min_length=1)
    report_template: str = Field(
        default="Report the source excerpt and recorded observation.",
        min_length=1,
    )
    response_hint: str = Field(
        default="Report the source excerpt and recorded observation.", min_length=1
    )
    unit_hint: str | None = None

    @field_validator("title")
    @classmethod
    def validate_fixed_title(cls, value: str, info) -> str:
        expected_titles = {
            "open_loop_stability": "Open-loop stability",
            "minimum_phase": "Minimum-phase behavior",
            "significant_delay": "Significant delay",
            "relative_degree": "Relative degree",
            "controllability_observability": "Controllability and observability",
            "nonlinearity_strength": "Nonlinearity strength",
            "coupling_severity": "Coupling severity",
            "uncertainty_magnitude": "Uncertainty magnitude",
        }
        field_id = info.data.get("diagnostic_field_id")
        if field_id in expected_titles and value.strip() != expected_titles[field_id]:
            raise ValueError(
                "measurement request title must be the fixed diagnostic label"
            )
        return value.strip()

    @field_validator("instruction", "source_hint")
    @classmethod
    def validate_source_lookup_text(cls, value: str) -> str:
        normalized = " ".join(value.split())
        allowed = {
            "Review an existing record.",
            "Review a manual report.",
            "Read an existing record.",
            "Read a manual report.",
            "Find an existing record.",
            "Find a manual report.",
            "Compare existing records.",
            "Compare manual reports.",
        }
        if normalized not in allowed:
            raise ValueError(
                "measurement source lookup text must be a record-only lookup template"
            )
        return normalized

    @field_validator("report_template", "response_hint")
    @classmethod
    def validate_report_template(cls, value: str) -> str:
        normalized = " ".join(value.split())
        allowed = {
            "Report the recorded observation.",
            "Describe the recorded observation.",
            "Report the source excerpt and recorded observation.",
            "Describe the source excerpt and recorded observation.",
        }
        if normalized not in allowed:
            raise ValueError(
                "measurement report text must be an observation-reporting template"
            )
        return normalized


class MeasurementPlan(CFDCModel):
    requests: list[MeasurementRequest] = Field(min_length=1, max_length=8)
    rationale: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_requests(self) -> MeasurementPlan:
        request_ids = [item.request_id for item in self.requests]
        diagnostic_field_ids = [item.diagnostic_field_id for item in self.requests]
        if len(request_ids) != len(set(request_ids)):
            raise ValueError("measurement request ids must be unique")
        if len(diagnostic_field_ids) != len(set(diagnostic_field_ids)):
            raise ValueError(
                "measurement plan may contain only one request per diagnostic field"
            )
        return self


class MeasuredFact(CFDCModel):
    request_id: str = Field(min_length=1)
    source_excerpt: str = Field(min_length=1)
    numeric_value: float | None = None
    unit: str | None = None
    text_value: str | None = None

    @field_validator("source_excerpt")
    @classmethod
    def validate_source_excerpt(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("source_excerpt must be non-empty")
        return normalized

    @model_validator(mode="after")
    def validate_value_and_provenance(self) -> MeasuredFact:
        if self.numeric_value is None and not (self.text_value or "").strip():
            raise ValueError("measured facts require a numeric_value or text_value")
        if self.numeric_value is not None and not (self.unit or "").strip():
            raise ValueError("numeric measured facts require a unit")
        if self.text_value is not None and not self.text_value.strip():
            raise ValueError("text_value must be non-empty when supplied")
        if (self.text_value or "").strip().lower() == "unknown":
            raise ValueError(
                "unknown values belong in assessment gaps, not measured facts"
            )
        return self


class MeasurementAssessment(CFDCModel):
    """Structured adapter output; session code validates it against the active plan."""

    status: Literal["need_more", "conflict", "ready"]
    facts: list[MeasuredFact] = Field(default_factory=list)
    gaps: list[DiagnosticFieldId] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)
    conflict_request_ids: list[str] = Field(default_factory=list)
    rationale: str = Field(
        default="Measurement evidence has not been fully verified.", min_length=1
    )

    @model_validator(mode="after")
    def validate_status(self) -> MeasurementAssessment:
        if self.status == "conflict" and (
            not self.conflicts or not self.conflict_request_ids
        ):
            raise ValueError(
                "a conflicting measurement assessment requires mapped conflicts"
            )
        if len(self.conflicts) != len(self.conflict_request_ids):
            raise ValueError("measurement conflicts require one request id each")
        if len(self.conflict_request_ids) != len(set(self.conflict_request_ids)):
            raise ValueError("measurement conflict request ids must be unique")
        if self.status != "conflict" and (self.conflicts or self.conflict_request_ids):
            raise ValueError("only conflict assessments may contain conflicts")
        if self.status == "ready" and (self.gaps or self.conflicts):
            raise ValueError(
                "a ready measurement assessment cannot contain gaps or conflicts"
            )
        return self


def validate_measurement_assessment_for_plan(
    plan: MeasurementPlan,
    assessment: MeasurementAssessment,
) -> None:
    """Require each active record request to have exactly one auditable outcome."""

    active_request_ids = [request.request_id for request in plan.requests]
    active_request_id_set = set(active_request_ids)
    request_field_by_id = {
        request.request_id: request.diagnostic_field_id for request in plan.requests
    }
    fact_request_ids = [fact.request_id for fact in assessment.facts]
    unknown_fact_ids = set(fact_request_ids) - active_request_id_set
    if unknown_fact_ids:
        raise ValueError(
            "unknown measurement request id(s): " + ", ".join(sorted(unknown_fact_ids))
        )
    if len(fact_request_ids) != len(set(fact_request_ids)):
        raise ValueError(
            "measurement assessments may contain only one fact per request"
        )
    active_field_ids = set(request_field_by_id.values())
    unknown_gaps = set(assessment.gaps) - active_field_ids
    if unknown_gaps:
        raise ValueError(
            "unknown measurement gap(s): " + ", ".join(sorted(unknown_gaps))
        )
    gap_request_ids = {
        request_id
        for request_id, field_id in request_field_by_id.items()
        if field_id in assessment.gaps
    }
    conflict_request_ids = set(assessment.conflict_request_ids)
    unknown_conflict_ids = conflict_request_ids - active_request_id_set
    if unknown_conflict_ids:
        raise ValueError(
            "unknown measurement conflict request id(s): "
            + ", ".join(sorted(unknown_conflict_ids))
        )
    fact_request_id_set = set(fact_request_ids)
    if fact_request_id_set & gap_request_ids:
        raise ValueError("measurement facts and gaps must not overlap")
    if fact_request_id_set & conflict_request_ids:
        raise ValueError("measurement facts and conflicts must not overlap")
    if gap_request_ids & conflict_request_ids:
        raise ValueError("measurement gaps and conflicts must not overlap")
    accounted_request_ids = fact_request_id_set | gap_request_ids | conflict_request_ids
    if accounted_request_ids != active_request_id_set:
        raise ValueError(
            "measurement assessments must account for every active measurement request"
        )
    if assessment.status == "ready" and fact_request_id_set != active_request_id_set:
        raise ValueError("ready measurement assessments require one fact per request")


class DiagnosticSessionState(CFDCModel):
    session_id: str = Field(min_length=1)
    schema_version: Literal["4.0"] = "4.0"
    route_id: str = "generic"
    initial_description: SystemDescription
    accumulated_description: SystemDescription
    turns: list[DiagnosticTurn] = Field(default_factory=list)
    current_diagnosis: StructuralDiagnosis
    revision: int = Field(default=0, ge=0)
    evidence_level: Literal[
        "description_only", "description_grounded", "measurement_verified"
    ] = "description_only"
    description_guidance: list[DescriptionGuidance] = Field(
        default_factory=list, max_length=8
    )
    checklist: list[DiagnosticChecklistItem] = Field(min_length=8, max_length=8)
    measurement_plan: MeasurementPlan | None = None
    description_assessment: MeasurementAssessment | None = None
    measurement_assessment: MeasurementAssessment | None = None
    measurement_history: list[MeasurementAssessment] = Field(
        default_factory=list, max_length=16
    )
    measurement_response_history: list[str] = Field(default_factory=list, max_length=16)
    description_turn_count: int = Field(default=0, ge=0, le=8)
    measurement_round_count: int = Field(default=0, ge=0, le=8)
    profile_measurement_round_count: int = Field(default=0, ge=0, le=8)
    classification: ArchetypeClassification | None = None
    semantic_selection: SemanticRouteSelection | None = None
    experiment_plan: ExperimentPlan | None = None
    evidence_requirement_plan: EvidenceRequirementPlan | None = None
    evidence_readiness: EvidenceReadinessDecision | None = None
    specification_templates: list[SpecificationTemplate] = Field(default_factory=list)
    specification_assessment: SpecificationAssessment | None = None
    specification_answer_history: list[str] = Field(default_factory=list)
    compiled_specification_model: CompiledSpecificationModel | None = None
    pending_clarification_questions: list[str] = Field(default_factory=list)
    candidate_route: CandidateRouteIR | None = None
    compiled_route: CompiledRoute | None = None
    status: Literal[
        "collecting_description",
        "awaiting_measurements",
        "measurement_needs_more",
        "measurement_conflict",
        "description_grounded",
        "measurement_verified",
        "awaiting_profile_measurements",
        "specification_conflict",
        "specification_model_ready",
        "awaiting_evidence",
        "evidence_rejected",
        "ready_for_experiments",
        "feature_extraction_failed",
        "ready_for_controller",
        "complete",
        "refused",
    ]
    maximum_turns: int = Field(default=8, ge=1, le=8)
    refusal_reason: str | None = None
    evidence_boundary: str = "software_simulation_diagnostic_session"

    @field_validator("measurement_response_history")
    @classmethod
    def validate_raw_measurement_responses(cls, value: list[str]) -> list[str]:
        if any(not isinstance(item, str) for item in value):
            raise ValueError("measurement response history entries must be strings")
        if any(not item.strip() for item in value):
            raise ValueError("measurement response history entries must be non-empty")
        return value

    @model_validator(mode="after")
    def validate_guided_measurement_state(self) -> DiagnosticSessionState:
        required_field_ids = [
            "open_loop_stability",
            "minimum_phase",
            "significant_delay",
            "relative_degree",
            "controllability_observability",
            "nonlinearity_strength",
            "coupling_severity",
            "uncertainty_magnitude",
        ]
        for field_name in (
            "description_turn_count",
            "measurement_round_count",
            "profile_measurement_round_count",
        ):
            if getattr(self, field_name) > self.maximum_turns:
                raise ValueError(f"{field_name} cannot exceed maximum_turns")
        if [item.diagnostic_field_id for item in self.checklist] != required_field_ids:
            raise ValueError("v4 sessions require the fixed eight-field checklist")
        if [
            item.diagnostic_field_id for item in self.description_guidance
        ] != required_field_ids:
            raise ValueError("v4 sessions require guidance for each diagnostic field")
        has_classification = self.classification is not None
        has_selection = self.semantic_selection is not None
        if self.evidence_level == "description_only" and (
            has_classification or has_selection
        ):
            raise ValueError(
                "classification and semantic_selection must be absent before measurement verification"
            )
        if self.evidence_level in {"description_grounded", "measurement_verified"} and (
            has_classification != has_selection
        ):
            raise ValueError(
                "classification and semantic_selection must be populated together after diagnostic verification"
            )
        if self.description_turn_count != len(self.turns):
            raise ValueError(
                "description_turn_count must match the description turn history"
            )
        if self.measurement_round_count != len(self.measurement_history):
            raise ValueError(
                "diagnostic measurement round count must match the diagnostic history"
            )
        if len(self.measurement_response_history) != len(self.measurement_history):
            raise ValueError(
                "measurement response history must align with measurement history"
            )
        if self.description_assessment is not None and (
            self.measurement_assessment is not None
            or self.measurement_history
            or self.measurement_round_count
        ):
            raise ValueError(
                "description and measurement diagnostic evidence sources are mutually exclusive"
            )
        if (
            self.evidence_level == "measurement_verified"
            and self.description_assessment is not None
        ):
            raise ValueError(
                "measurement-verified sessions cannot retain description evidence"
            )
        if self.evidence_level == "measurement_verified":
            diagnostic_history = self.measurement_history[
                : self.measurement_round_count
            ]
            if not diagnostic_history or diagnostic_history[-1].status != "ready":
                raise ValueError(
                    "verified evidence requires a diagnostic ready assessment before "
                    "any Profile rounds"
                )
            if any(item.status == "ready" for item in diagnostic_history[:-1]):
                raise ValueError(
                    "diagnostic measurement collection must stop at its first ready "
                    "assessment"
                )
        if self.measurement_plan is not None:
            plan_request_ids = [
                request.request_id for request in self.measurement_plan.requests
            ]
            plan_field_ids = [
                request.diagnostic_field_id
                for request in self.measurement_plan.requests
            ]
            if (
                plan_request_ids != required_field_ids
                or plan_field_ids != required_field_ids
            ):
                raise ValueError(
                    "v4 sessions require the exact fixed eight-field measurement plan"
                )
        if self.description_assessment is not None:
            if self.measurement_plan is None:
                raise ValueError(
                    "description assessments require the fixed diagnostic plan"
                )
            validate_measurement_assessment_for_plan(
                self.measurement_plan, self.description_assessment
            )
            if self.description_assessment.status != "ready":
                raise ValueError("description assessments must be ready")
            from cfdc.diagnosis.measurements import (
                reduce_measurement_history_to_diagnosis,
                validate_description_assessment_semantics,
                validate_grounded_measurement_assessment,
            )

            validate_grounded_measurement_assessment(
                self.measurement_plan,
                self.description_assessment,
                self.accumulated_description.text,
            )
            validate_description_assessment_semantics(
                self.measurement_plan,
                self.description_assessment,
                self.accumulated_description.text,
            )
            grounded_diagnosis = reduce_measurement_history_to_diagnosis(
                self.measurement_plan, [self.description_assessment]
            )
            if not grounded_diagnosis.complete:
                raise ValueError(
                    "description assessment must resolve all eight diagnostic fields"
                )
            if grounded_diagnosis != self.current_diagnosis:
                raise ValueError(
                    "current diagnosis must match the grounded description assessment"
                )
        if self.evidence_level == "description_only" and self.description_assessment:
            raise ValueError(
                "description-only sessions cannot contain a ready description assessment"
            )
        if self.evidence_level == "description_grounded" and (
            self.description_assessment is None or not self.current_diagnosis.complete
        ):
            raise ValueError(
                "description-grounded sessions require a complete grounded assessment"
            )
        if self.status == "description_grounded":
            if self.evidence_level != "description_grounded":
                raise ValueError(
                    "description_grounded status requires grounded description evidence"
                )
            if has_classification or has_selection:
                raise ValueError(
                    "classification and semantic_selection must remain absent during the description_grounded transition"
                )
        if self.status == "measurement_verified":
            if self.evidence_level != "measurement_verified":
                raise ValueError(
                    "measurement_verified status requires verified measurement evidence"
                )
            if self.measurement_plan is None:
                raise ValueError(
                    "measurement_verified status requires a measurement plan"
                )
            if self.measurement_assessment is None:
                raise ValueError(
                    "measurement_verified status requires a ready measurement assessment"
                )
        if self.measurement_history:
            if self.measurement_plan is None:
                raise ValueError(
                    "measurement history requires an active measurement plan"
                )
            for assessment in self.measurement_history:
                validate_measurement_assessment_for_plan(
                    self.measurement_plan, assessment
                )
            from cfdc.diagnosis.measurements import (
                reduce_measurement_history_to_diagnosis,
                validate_grounded_measurement_assessment,
            )

            previous_assessment = None
            for index, (response, assessment) in enumerate(
                zip(
                    self.measurement_response_history,
                    self.measurement_history,
                    strict=True,
                )
            ):
                validate_grounded_measurement_assessment(
                    self.measurement_plan,
                    assessment,
                    response,
                    previous_assessment=(previous_assessment if index > 0 else None),
                )
                previous_assessment = assessment
            if self.evidence_level == "measurement_verified":
                grounded_diagnosis = reduce_measurement_history_to_diagnosis(
                    self.measurement_plan,
                    self.measurement_history,
                )
                if grounded_diagnosis != self.current_diagnosis:
                    raise ValueError(
                        "current diagnosis must match the grounded measurement history"
                    )
        if self.measurement_assessment is not None:
            if self.measurement_plan is None:
                raise ValueError(
                    "measurement assessments require an active measurement plan"
                )
            validate_measurement_assessment_for_plan(
                self.measurement_plan, self.measurement_assessment
            )
            if (
                not self.measurement_history
                or self.measurement_history[-1] != self.measurement_assessment
            ):
                raise ValueError(
                    "current measurement assessment must be the final measurement history entry"
                )
        if (
            self.status == "measurement_verified"
            and self.measurement_assessment.status != "ready"
        ):
            raise ValueError(
                "measurement_verified status requires a ready measurement assessment"
            )
        if self.status == "measurement_verified" and (
            has_classification or has_selection
        ):
            raise ValueError(
                "classification and semantic_selection must remain absent during the "
                "measurement_verified transition"
            )
        post_measurement_statuses = {
            "awaiting_profile_measurements",
            "specification_conflict",
            "specification_model_ready",
            "awaiting_evidence",
            "evidence_rejected",
            "ready_for_experiments",
            "feature_extraction_failed",
            "ready_for_controller",
            "complete",
        }
        if self.status in post_measurement_statuses:
            if self.evidence_level not in {
                "description_grounded",
                "measurement_verified",
            }:
                raise ValueError(
                    "post-diagnosis states require grounded diagnostic evidence"
                )
            if not has_classification or not has_selection:
                raise ValueError(
                    "post-measurement states require classification and semantic_selection"
                )
            has_ready_source = (
                self.description_assessment is not None
                if self.evidence_level == "description_grounded"
                else bool(
                    self.measurement_history
                    and self.measurement_assessment is not None
                    and self.measurement_assessment.status == "ready"
                )
            )
            if self.measurement_plan is None or not has_ready_source or not self.current_diagnosis.complete:
                raise ValueError(
                    "post-diagnosis states require complete grounded diagnostic evidence"
                )
        elif self.evidence_level == "measurement_verified" and self.status not in {
            "measurement_verified",
            "refused",
        }:
            raise ValueError(
                "verified measurement evidence must use a post-measurement status"
            )
        elif self.evidence_level == "description_grounded" and self.status not in {
            "description_grounded",
            "refused",
        }:
            raise ValueError(
                "grounded description evidence must use a post-diagnosis status"
            )
        if self.status == "awaiting_profile_measurements" and (
            not self.specification_templates or self.specification_assessment is None
        ):
            raise ValueError(
                "awaiting_profile_measurements requires a specification assessment"
            )
        if (
            self.status == "specification_model_ready"
            and self.compiled_specification_model is None
        ):
            raise ValueError(
                "specification_model_ready requires a compiled specification model"
            )
        return self


class ClosedLoopBenchmarkCaseResult(CFDCModel):
    case_id: str
    route_ir: BenchmarkRouteIR
    diagnosis_complete: bool
    archetype: str
    planned_experiment_count: int = Field(ge=0)
    features: list[CoreFeatureArtifact]
    required_feature_ids: list[str]
    features_cover_required: bool
    controller: ControllerCandidate
    performance: SimulationPerformanceSummary
    success: bool
    closed_loop_executed: bool = True
    execution_backend: str
    notes: list[str] = Field(default_factory=list)
    evidence_boundary: str = "software_simulation_closed_loop_benchmark"


class FeatureAblationTrial(CFDCModel):
    case_id: str
    variant: Literal[
        "minimal_core_feature", "wrong_or_noisy_feature", "full_model_reference"
    ]
    feature_values: dict[str, float]
    controller: ControllerCandidate
    performance: SimulationPerformanceSummary
    success: bool
    evidence_boundary: str = "software_simulation_feature_ablation"


class FeatureAblationResult(CFDCModel):
    success: bool
    case_count: int = Field(ge=1)
    trial_count: int = Field(ge=1)
    trials: list[FeatureAblationTrial] = Field(min_length=1)
    notes: list[str] = Field(default_factory=list)
    evidence_boundary: str = "software_simulation_feature_ablation_suite"


class SavedDiagnosticResponse(CFDCModel):
    case_id: str
    field_values: dict[str, str]
    field_evidence: dict[str, list[str]] = Field(default_factory=dict)
    complete: bool
    clarification_questions: list[str] = Field(default_factory=list)
    primary_class: str | None = None
    required_core_features: list[str] = Field(default_factory=list)
    control_architecture: str | None = None
    classification_rationale: str | None = None
    safety_constraints: list[str] = Field(default_factory=list)
    experiment_plan_executable: bool = False
    experiment_plan_issues: list[str] = Field(default_factory=list)
    controller_testable: bool = False
    controller_allowed: bool = False
    controller_release_reasons: list[str] = Field(default_factory=list)
    generator: str


class DiagnosticResponseSnapshot(CFDCModel):
    snapshot_version: int = Field(ge=1)
    evaluation_spec_version: str
    case_catalog_sha256: str
    scoring_policy: dict[str, Any]
    response_source: Literal["saved_deterministic", "live_llm", "saved_llm"]
    generator: str
    model: str | None = None
    prompt_version: str
    responses: list[SavedDiagnosticResponse] = Field(min_length=1)
    evidence_boundary: str = "software_simulation_structural_diagnosis"


class DiagnosticEvaluationCaseResult(CFDCModel):
    case_id: str
    suite: Literal["prompt_8", "complex_4"]
    response_source: Literal[
        "current_engine",
        "saved_deterministic",
        "live_llm",
        "saved_llm",
    ]
    expected_complete: bool
    actual_complete: bool
    clarification_correct: bool
    field_matches: dict[str, bool]
    eight_field_accuracy: float = Field(ge=0.0, le=1.0)
    expected_archetype: str | None = None
    actual_archetype: str | None = None
    archetype_correct: bool
    expected_required_features: list[str]
    actual_required_features: list[str]
    required_feature_recall: float = Field(ge=0.0, le=1.0)
    required_feature_precision: float = Field(ge=0.0, le=1.0)
    core_feature_minimality_correct: bool
    extra_core_features: list[str] = Field(default_factory=list)
    constraint_isolation_correct: bool
    constraint_feature_leaks: list[str] = Field(default_factory=list)
    dangerous_false_positive_control_correct: bool
    dangerous_false_positive_features: list[str] = Field(default_factory=list)
    evidence_discipline_correct: bool
    missing_information_quality: float = Field(ge=0.0, le=1.0)
    expected_experiment_executable: bool
    actual_experiment_executable: bool
    experiment_executability_correct: bool
    experiment_plan_issues: list[str] = Field(default_factory=list)
    expected_controller_testable: bool
    actual_controller_testable: bool
    controller_testability_correct: bool
    expected_controller_allowed: bool
    actual_controller_allowed: bool
    controller_gate_correct: bool
    premature_controller_release: bool
    passed: bool


class DiagnosticEvaluationResult(CFDCModel):
    response_source: Literal[
        "current_engine",
        "saved_deterministic",
        "live_llm",
        "saved_llm",
    ]
    evaluation_spec_version: str
    case_catalog_sha256: str
    case_count: int = Field(ge=1)
    prompt_case_count: int = Field(ge=1)
    complex_case_count: int = Field(ge=1)
    mean_eight_field_accuracy: float = Field(ge=0.0, le=1.0)
    mean_required_feature_recall: float = Field(ge=0.0, le=1.0)
    mean_required_feature_precision: float = Field(ge=0.0, le=1.0)
    core_feature_minimality_accuracy: float = Field(ge=0.0, le=1.0)
    constraint_isolation_accuracy: float = Field(ge=0.0, le=1.0)
    dangerous_false_positive_control_accuracy: float = Field(ge=0.0, le=1.0)
    evidence_discipline_accuracy: float = Field(ge=0.0, le=1.0)
    mean_missing_information_quality: float = Field(ge=0.0, le=1.0)
    experiment_executability_accuracy: float = Field(ge=0.0, le=1.0)
    controller_testability_accuracy: float = Field(ge=0.0, le=1.0)
    clarification_accuracy: float = Field(ge=0.0, le=1.0)
    archetype_accuracy: float = Field(ge=0.0, le=1.0)
    controller_gate_accuracy: float = Field(ge=0.0, le=1.0)
    premature_controller_release_count: int = Field(ge=0)
    dangerous_false_positive_control_count: int = Field(ge=0)
    passed_count: int = Field(ge=0)
    cases: list[DiagnosticEvaluationCaseResult] = Field(min_length=1)
    evidence_boundary: str = "software_simulation_offline_diagnostic_evaluation"


class DiagnosticEvaluationComparison(CFDCModel):
    evaluation_spec_version: str
    case_catalog_sha256: str
    deterministic: DiagnosticEvaluationResult
    llm: DiagnosticEvaluationResult
    metric_deltas_llm_minus_deterministic: dict[str, float]
    evidence_boundary: str = "software_simulation_diagnostic_response_comparison"


class OnlineTuningState(CFDCModel):
    gains: dict[str, float]
    previous_gains: dict[str, float] = Field(default_factory=dict)
    frozen: bool = False
    freeze_reason: str | None = None
    step_fraction: float = Field(default=0.05, ge=0.0, le=0.10)
    history: list[dict[str, Any]] = Field(default_factory=list)


class OnlineRefinementPolicy(CFDCModel):
    step_multiplier: float = Field(default=1.05, ge=1.05, le=1.10)
    minimum_dwell_s: float = Field(default=0.0, ge=0.0)
    soft_violation_confirmations: int = Field(default=2, ge=2)
    max_iterations: int = Field(default=20, ge=1)


class Algorithm1Observation(CFDCModel):
    dwell_time_s: float = Field(ge=0.0)
    hard_safety_violation: bool = False
    soft_performance_violation: bool = False
    nmp_violation: bool = False
    performance_target_met: bool = False
    violation_reasons: list[str] = Field(default_factory=list)
    metrics: dict[str, float | None] = Field(default_factory=dict)


class Algorithm1State(CFDCModel):
    accepted_gains: dict[str, float]
    previous_safe_gains: dict[str, float]
    candidate_gains: dict[str, float] | None = None
    tunable_gain_names: list[str] = Field(min_length=1)
    policy: OnlineRefinementPolicy = Field(default_factory=OnlineRefinementPolicy)
    iteration_count: int = Field(default=0, ge=0)
    consecutive_soft_violations: int = Field(default=0, ge=0)
    status: Literal["ready", "probing", "frozen", "completed"] = "ready"
    frozen: bool = False
    freeze_reason: str | None = None
    completion_reason: str | None = None
    history: list[dict[str, Any]] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_tunable_gains(self) -> Algorithm1State:
        unknown = set(self.tunable_gain_names) - set(self.accepted_gains)
        if unknown:
            raise ValueError(
                f"tunable gains must exist in accepted_gains: {', '.join(sorted(unknown))}"
            )
        return self


class SafeGainSearchState(CFDCModel):
    accepted_gains: dict[str, float]
    candidate_gains: dict[str, float] | None = None
    search_direction: dict[str, float] = Field(default_factory=dict)
    step_fraction: float = Field(default=0.05, ge=0.05, le=0.10)
    trial_index: int = Field(default=0, ge=0)
    frozen: bool = False
    freeze_reason: str | None = None
    status: Literal["ready_for_trial", "trial_pending", "accepted", "frozen"] = (
        "ready_for_trial"
    )
    history: list[dict[str, Any]] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_candidate_when_pending(self) -> SafeGainSearchState:
        if self.status == "trial_pending" and not self.candidate_gains:
            raise ValueError("trial_pending state requires candidate_gains")
        if self.frozen and self.status != "frozen":
            raise ValueError("frozen state must use status='frozen'")
        return self


class FeatureTrackingUpdate(CFDCModel):
    feature_id: str
    previous_value: float
    measured_value: float
    updated_value: float
    relative_change: float = Field(ge=0.0)
    controller_update_required: bool
    smoothing_factor: float = Field(ge=0.0, le=1.0)


class TrackingObservation(CFDCModel):
    time_s: float = Field(ge=0.0)
    steady_operating_mode: bool
    tracking_error: float = Field(default=0.0, ge=0.0)
    hard_safety_active: bool = False
    aggressive_maneuver: bool = False
    feature_id: str | None = None
    signal_time_s: list[float] = Field(default_factory=list)
    signal_values: list[float] = Field(default_factory=list)
    regressor: float | None = None
    response: float | None = None
    control_effort: float | None = None
    dt_s: float | None = Field(default=None, gt=0.0)


class TrackingSchedulerState(CFDCModel):
    duty_interval_s: float = Field(default=1.0, ge=0.0)
    tracking_error_threshold: float = Field(default=0.05, ge=0.0)
    last_eligible_time_s: float | None = Field(default=None, ge=0.0)
    pause_reason: str | None = None
    eligible_update_count: int = Field(default=0, ge=0)


class FLLTrackerState(CFDCModel):
    angular_frequency_rad_s: float = Field(gt=0.0)
    bandwidth_rad_s: float = Field(default=1.0, gt=0.0)
    smoothing_gain: float = Field(default=0.2, gt=0.0, le=1.0)
    minimum_lock_quality: float = Field(default=0.5, ge=0.0, le=1.0)
    last_lock_quality: float = Field(default=0.0, ge=0.0, le=1.0)
    last_update_accepted: bool = False
    accepted_update_count: int = Field(default=0, ge=0)
    rejected_update_count: int = Field(default=0, ge=0)
    window_time_s: list[float] = Field(default_factory=list)
    window_signal: list[float] = Field(default_factory=list)


class ScalarRLSTrackerState(CFDCModel):
    parameter_estimate: float
    covariance: float = Field(default=100.0, gt=0.0)
    forgetting_factor: float = Field(default=0.95, gt=0.0, le=1.0)
    update_count: int = Field(default=0, ge=0)
    ignored_sample_count: int = Field(default=0, ge=0)


class HoverAverageTrackerState(CFDCModel):
    average_control_effort: float
    time_constant_s: float = Field(default=10.0, gt=0.0)
    update_count: int = Field(default=0, ge=0)


class TrackingStateBundle(CFDCModel):
    scheduler: TrackingSchedulerState = Field(default_factory=TrackingSchedulerState)
    fll: FLLTrackerState | None = None
    rls: ScalarRLSTrackerState | None = None
    hover: HoverAverageTrackerState | None = None
    nmp_retune_requested: bool = False


class CartpoleState(CFDCModel):
    cart_position_m: float
    cart_velocity_m_s: float
    pole_angle_rad: float
    pole_angular_velocity_rad_s: float


class CartpoleSimulationResult(CFDCModel):
    success: bool
    stop_reason: str
    handoff_time_s: float | None = Field(default=None, ge=0.0)
    final_state: CartpoleState
    max_abs_cart_position_m: float = Field(ge=0.0)
    max_abs_force_n: float = Field(ge=0.0)
    sample_count: int = Field(ge=1)
    performance: SimulationPerformanceSummary
    metrics: dict[str, int | float | str | bool | None] = Field(default_factory=dict)
    events: list[dict[str, int | float | str | bool | None]] = Field(
        default_factory=list
    )
    final_gains: dict[str, float] = Field(default_factory=dict)
    trajectory: list[dict[str, float | str]] = Field(default_factory=list)
    evidence_boundary: str = "software_simulation_cartpole"


class TrialSample(CFDCModel):
    time_s: float = Field(ge=0.0)
    state: dict[str, float]
    control: dict[str, float]
    reference: dict[str, float] = Field(default_factory=dict)
    metadata: dict[str, float | str | bool] = Field(default_factory=dict)


class SafetyViolation(CFDCModel):
    constraint: str
    observed_value: float
    limit: float
    time_s: float = Field(ge=0.0)
    message: str


class TrialReport(CFDCModel):
    trial_id: str
    accepted: bool
    stop_reason: str
    duration_s: float = Field(ge=0.0)
    samples: list[TrialSample] = Field(default_factory=list)
    metrics: OnlinePerformanceMetrics | None = None
    safety_violations: list[SafetyViolation] = Field(default_factory=list)
    tested_gains: dict[str, float] = Field(default_factory=dict)
    accepted_gains: dict[str, float] = Field(default_factory=dict)
    evidence_boundary: str = "software_simulation_bounded_trial"


class CartpoleBoundaryResult(CFDCModel):
    success: bool
    stop_reason: str
    start_state: CartpoleState
    target_position_m: float
    candidate_trials: list[TrialReport] = Field(default_factory=list)
    accepted_outer_gains: dict[str, float] = Field(default_factory=dict)
    rejected_outer_gains: dict[str, float] = Field(default_factory=dict)
    rollback_applied: bool = False
    rollback_verified: bool = False
    rollback_trial: TrialReport | None = None
    performance: SimulationPerformanceSummary
    events: list[dict[str, Any]] = Field(default_factory=list)
    trajectory: list[dict[str, float | str]] = Field(default_factory=list)
    evidence_boundary: str = "software_simulation_cartpole_nmp_boundary"


class VtolState(CFDCModel):
    x_m: float
    z_m: float
    theta_rad: float
    x_dot_m_s: float
    z_dot_m_s: float
    theta_dot_rad_s: float


class VtolSimulationResult(CFDCModel):
    mode: str
    success: bool
    stop_reason: str
    final_state: VtolState
    performance: SimulationPerformanceSummary
    metrics: dict[str, int | float | str | bool | None]
    features: list[CoreFeatureArtifact] = Field(default_factory=list)
    events: list[dict[str, int | float | str | bool | None]] = Field(
        default_factory=list
    )
    trajectory: list[dict[str, float | str]] = Field(default_factory=list)
    evidence_boundary: str = "software_simulation_vtol"


class VtolVariationScenario(CFDCModel):
    scenario_id: str
    feature_source: Literal["stale", "updated"]
    mass_kg: float = Field(gt=0.0)
    pitch_inertia_kg_m2: float = Field(gt=0.0)
    expected_success: bool
    expectation_met: bool
    features: list[CoreFeatureArtifact]
    simulation: VtolSimulationResult


class VtolVariationResult(CFDCModel):
    success: bool
    scenarios: list[VtolVariationScenario] = Field(min_length=1)
    updated_scenario_count: int = Field(ge=0)
    stale_scenario_count: int = Field(ge=0)
    notes: list[str] = Field(default_factory=list)
    evidence_boundary: str = "software_simulation_vtol_variation_study"


class ControllerValidationResult(CFDCModel):
    status: Literal["passed", "failed", "not_supported"]
    performance: SimulationPerformanceSummary | None = None
    violations: list[str] = Field(default_factory=list)
    trace_sha256: str | None = None
    evidence_boundary: str = "user_object_model_closed_loop_validation"


class CFDCRunReport(CFDCModel):
    run_id: str
    route_id: str = "generic"
    status: Literal[
        "collecting_description",
        "description_grounded",
        "need_more_information",
        "awaiting_measurements",
        "measurement_needs_more",
        "measurement_conflict",
        "awaiting_profile_measurements",
        "awaiting_specifications",
        "need_more_specifications",
        "specification_conflict",
        "specification_model_ready",
        "awaiting_evidence",
        "evidence_rejected",
        "candidate_unvalidated",
        "validation_pending",
        "validated_in_simulation",
        "demo_completed",
        "feature_extraction_failed",
        "controller_candidate_ready",
        "accepted",
        "rejected",
        "frozen",
        "completed",
    ]
    system_description: SystemDescription | None = None
    diagnosis: StructuralDiagnosis | None = None
    diagnostic_session: DiagnosticSessionState | None = None
    classification: ArchetypeClassification | None = None
    semantic_selection: SemanticRouteSelection | None = None
    experiment_plan: ExperimentPlan | None = None
    evidence_requirement_plan: EvidenceRequirementPlan | None = None
    evidence_readiness: EvidenceReadinessDecision | None = None
    specification_templates: list[SpecificationTemplate] = Field(default_factory=list)
    specification_assessment: SpecificationAssessment | None = None
    compiled_specification_model: CompiledSpecificationModel | None = None
    candidate_route: CandidateRouteIR | None = None
    compiled_route: CompiledRoute | None = None
    experiment_results: list[SimulationExperimentRecord] = Field(default_factory=list)
    features: list[CoreFeatureArtifact] = Field(default_factory=list)
    feature_quality_decision: FeatureQualityDecision | None = None
    controller: ControllerCandidate | None = None
    controller_validation: ControllerValidationResult | None = None
    trial_reports: list[TrialReport] = Field(default_factory=list)
    online_tuning_state: OnlineTuningState | None = None
    algorithm1_state: Algorithm1State | None = None
    safe_gain_search_state: SafeGainSearchState | None = None
    feature_tracking_updates: list[FeatureTrackingUpdate] = Field(default_factory=list)
    tracking_state: TrackingStateBundle | None = None
    cartpole_simulation: CartpoleSimulationResult | None = None
    cartpole_boundary: CartpoleBoundaryResult | None = None
    vtol_simulation: VtolSimulationResult | None = None
    vtol_variation: VtolVariationResult | None = None
    baseline_comparison: ControllerComparison | None = None
    stale_controller_performance: SimulationPerformanceSummary | None = None
    adapted_controller_performance: SimulationPerformanceSummary | None = None
    final_gains: dict[str, float] = Field(default_factory=dict)
    final_feedforward: dict[str, float] = Field(default_factory=dict)
    go_no_go: GoNoGoDecision | None = None
    notes: list[str] = Field(default_factory=list)
    evidence_boundary: str = "software_simulation_only"
