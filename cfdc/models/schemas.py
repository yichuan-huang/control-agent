from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class CFDCModel(BaseModel):
    """Base model that rejects undeclared fields for auditable JSON output."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True, allow_inf_nan=False)


class SystemDescription(CFDCModel):
    text: str = Field(min_length=1)
    observed_outputs: list[str] = Field(default_factory=list)
    actuators: list[str] = Field(default_factory=list)
    safety_bounds: dict[str, float] = Field(default_factory=dict)
    forbidden_actions: list[str] = Field(default_factory=list)
    time_scale_hint_s: float | None = Field(default=None, gt=0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DiagnosticField(CFDCModel):
    status: Literal["known", "inferred", "unknown"]
    value: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list)


class DelayAssessment(str, Enum):
    SIGNIFICANT = "significant"
    NOT_SIGNIFICANT = "not_significant"
    UNKNOWN = "unknown"


class SignificantDelayField(DiagnosticField):
    assessment: DelayAssessment

    @model_validator(mode="after")
    def validate_status_assessment_consistency(self) -> "SignificantDelayField":
        status_unknown = self.status == "unknown"
        assessment_unknown = self.assessment == DelayAssessment.UNKNOWN.value
        if status_unknown != assessment_unknown:
            raise ValueError(
                "significant_delay status and assessment must both be unknown or both be resolved"
            )
        return self


class StructuralDiagnosis(CFDCModel):
    open_loop_stability: DiagnosticField
    minimum_phase: DiagnosticField
    significant_delay: SignificantDelayField
    relative_degree: DiagnosticField
    controllability_observability: DiagnosticField
    nonlinearity_strength: DiagnosticField
    coupling_severity: DiagnosticField
    uncertainty_magnitude: DiagnosticField
    clarification_questions: list[str] = Field(default_factory=list, max_length=4)
    complete: bool

    @model_validator(mode="after")
    def validate_questions(self) -> "StructuralDiagnosis":
        if not self.complete and not (2 <= len(self.clarification_questions) <= 4):
            raise ValueError("Incomplete diagnosis must include 2-4 clarification questions")
        if self.complete and self.clarification_questions:
            raise ValueError("Complete diagnosis should not include clarification questions")
        return self

    @property
    def fields(self) -> list[DiagnosticField]:
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


class ExperimentPlan(CFDCModel):
    archetype: ArchetypeClass
    instructions: list[ExperimentInstruction] = Field(min_length=1, max_length=5)
    evidence_boundary: str = "experiment_plan_only_not_physical_validation"


class ExperimentTrace(CFDCModel):
    time_s: list[float] = Field(min_length=3)
    signals: dict[str, list[float]] = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("time_s")
    @classmethod
    def validate_time(cls, values: list[float]) -> list[float]:
        if any(curr <= prev for prev, curr in zip(values, values[1:])):
            raise ValueError("time_s must be strictly increasing")
        return values

    @field_validator("signals")
    @classmethod
    def validate_signals(cls, signals: dict[str, list[float]]) -> dict[str, list[float]]:
        cleaned: dict[str, list[float]] = {}
        for name, values in signals.items():
            clean_name = name.strip()
            if not clean_name:
                raise ValueError("signal names must be non-empty")
            if len(values) < 3:
                raise ValueError(f"signal '{clean_name}' must contain at least three samples")
            cleaned[clean_name] = values
        return cleaned

    @model_validator(mode="after")
    def validate_signal_lengths(self) -> "ExperimentTrace":
        expected = len(self.time_s)
        mismatched = [name for name, values in self.signals.items() if len(values) != expected]
        if mismatched:
            names = ", ".join(sorted(mismatched))
            raise ValueError(f"signals must match time_s length: {names}")
        return self


class ExperimentResult(CFDCModel):
    primitive: ExperimentPrimitive
    estimates: list[str] = Field(min_length=1)
    trace: ExperimentTrace
    instruction_title: str | None = None
    evidence_boundary: str = "raw_experiment_trace_not_physical_validation_by_itself"
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
    feature_id: str
    value: float
    lower_bound: float
    upper_bound: float
    confidence: float = Field(ge=0.0, le=1.0)
    units: str
    method: str
    source_experiment: ExperimentPrimitive
    data_quality_flags: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_bounds(self) -> "CoreFeatureArtifact":
        if self.lower_bound > self.value or self.upper_bound < self.value:
            raise ValueError("Feature value must lie inside confidence bounds")
        return self


class ControllerCandidate(CFDCModel):
    architecture: str
    gains: dict[str, float] = Field(default_factory=dict)
    design_parameters: dict[str, float] = Field(default_factory=dict)
    tunable_gain_names: list[str] = Field(default_factory=list)
    feedforward: dict[str, float] = Field(default_factory=dict)
    saturation: dict[str, float] = Field(default_factory=dict)
    constraints: list[str] = Field(default_factory=list)
    source_features: list[str] = Field(default_factory=list)
    status: Literal["ready_for_conservative_trial", "requires_online_search", "refuse"]
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_tunable_gain_names(self) -> "ControllerCandidate":
        unknown = set(self.tunable_gain_names) - set(self.gains)
        if unknown:
            raise ValueError(f"tunable gains must exist in gains: {', '.join(sorted(unknown))}")
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
    evidence_boundary: str = "software_controller_comparison_not_physical_validation"


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
    evidence_boundary: str = "synthetic_benchmark_route_ir_not_physical_validation"


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
    evidence_boundary: str = "synthetic_closed_loop_benchmark_not_physical_validation"


class FeatureAblationTrial(CFDCModel):
    case_id: str
    variant: Literal["minimal_core_feature", "wrong_or_noisy_feature", "full_model_reference"]
    feature_values: dict[str, float]
    controller: ControllerCandidate
    performance: SimulationPerformanceSummary
    success: bool
    evidence_boundary: str = "synthetic_feature_ablation_not_physical_validation"


class FeatureAblationResult(CFDCModel):
    success: bool
    case_count: int = Field(ge=1)
    trial_count: int = Field(ge=1)
    trials: list[FeatureAblationTrial] = Field(min_length=1)
    notes: list[str] = Field(default_factory=list)
    evidence_boundary: str = "synthetic_feature_ablation_suite_not_physical_validation"


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
    evidence_boundary: str = "structured_diagnostic_responses_not_controller_or_physical_validation"


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
    evidence_boundary: str = "offline_diagnostic_evaluation_not_controller_validation"


class DiagnosticEvaluationComparison(CFDCModel):
    evaluation_spec_version: str
    case_catalog_sha256: str
    deterministic: DiagnosticEvaluationResult
    llm: DiagnosticEvaluationResult
    metric_deltas_llm_minus_deterministic: dict[str, float]
    evidence_boundary: str = "diagnostic_response_comparison_not_controller_or_physical_validation"


class OnlineTuningState(CFDCModel):
    gains: dict[str, float]
    previous_gains: dict[str, float] = Field(default_factory=dict)
    frozen: bool = False
    freeze_reason: str | None = None
    step_fraction: float = Field(default=0.05, ge=0.0, le=0.10)
    history: list[dict[str, Any]] = Field(default_factory=list)


class SafeGainSearchState(CFDCModel):
    accepted_gains: dict[str, float]
    candidate_gains: dict[str, float] | None = None
    search_direction: dict[str, float] = Field(default_factory=dict)
    step_fraction: float = Field(default=0.05, ge=0.05, le=0.10)
    trial_index: int = Field(default=0, ge=0)
    frozen: bool = False
    freeze_reason: str | None = None
    status: Literal["ready_for_trial", "trial_pending", "accepted", "frozen"] = "ready_for_trial"
    history: list[dict[str, Any]] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_candidate_when_pending(self) -> "SafeGainSearchState":
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
    events: list[dict[str, int | float | str | bool | None]] = Field(default_factory=list)
    final_gains: dict[str, float] = Field(default_factory=dict)
    trajectory: list[dict[str, float | str]] = Field(default_factory=list)
    evidence_boundary: str = "deterministic_cartpole_simulation_not_hardware_validation"


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
    evidence_boundary: str = "bounded_software_trial_not_physical_validation"


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
    evidence_boundary: str = "deterministic_cartpole_nmp_boundary_not_hardware_validation"


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
    events: list[dict[str, int | float | str | bool | None]] = Field(default_factory=list)
    trajectory: list[dict[str, float | str]] = Field(default_factory=list)
    evidence_boundary: str = "deterministic_vtol_simulation_not_hardware_validation"


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
    evidence_boundary: str = "deterministic_vtol_variation_study_not_online_or_hardware_validation"


class CFDCRunReport(CFDCModel):
    run_id: str
    route_id: str = "generic"
    status: Literal[
        "need_more_information",
        "experiments_required",
        "controller_candidate_ready",
        "accepted",
        "rejected",
        "frozen",
        "completed",
    ]
    system_description: SystemDescription | None = None
    diagnosis: StructuralDiagnosis | None = None
    classification: ArchetypeClassification | None = None
    experiment_plan: ExperimentPlan | None = None
    experiment_results: list[ExperimentResult] = Field(default_factory=list)
    features: list[CoreFeatureArtifact] = Field(default_factory=list)
    controller: ControllerCandidate | None = None
    trial_reports: list[TrialReport] = Field(default_factory=list)
    online_tuning_state: OnlineTuningState | None = None
    safe_gain_search_state: SafeGainSearchState | None = None
    feature_tracking_updates: list[FeatureTrackingUpdate] = Field(default_factory=list)
    cartpole_simulation: CartpoleSimulationResult | None = None
    cartpole_boundary: CartpoleBoundaryResult | None = None
    vtol_simulation: VtolSimulationResult | None = None
    vtol_variation: VtolVariationResult | None = None
    baseline_comparison: ControllerComparison | None = None
    final_gains: dict[str, float] = Field(default_factory=dict)
    final_feedforward: dict[str, float] = Field(default_factory=dict)
    go_no_go: GoNoGoDecision | None = None
    notes: list[str] = Field(default_factory=list)
    evidence_boundary: str = "software_runtime_report_not_physical_validation"
