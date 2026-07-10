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


class StructuralDiagnosis(CFDCModel):
    open_loop_stability: DiagnosticField
    minimum_phase: DiagnosticField
    significant_delay: DiagnosticField
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
    vtol_simulation: VtolSimulationResult | None = None
    final_gains: dict[str, float] = Field(default_factory=dict)
    final_feedforward: dict[str, float] = Field(default_factory=dict)
    go_no_go: GoNoGoDecision | None = None
    notes: list[str] = Field(default_factory=list)
    evidence_boundary: str = "software_runtime_report_not_physical_validation"
