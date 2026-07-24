from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
from pathlib import Path
from typing import Literal

from cfdc.controllers import synthesize_controller
from cfdc.diagnosis.engine import DiagnosticEngine
from cfdc.diagnosis.llm import (
    DiagnosticAdapter,
    OpenAICompatibleDiagnosticAdapter,
    PROMPT_VERSION,
)
from cfdc.diagnosis.safety import (
    CONTROLLER_SYNTHESIS_FEATURES,
    diagnostic_required_feature_plan,
    validate_diagnostic_controller_release,
)
from cfdc.experiments import plan_safe_experiments
from cfdc.models import (
    ArchetypeClass,
    ArchetypeClassification,
    CoreFeatureArtifact,
    DiagnosticEvaluationCaseResult,
    DiagnosticEvaluationComparison,
    DiagnosticEvaluationResult,
    DiagnosticResponseSnapshot,
    ExperimentPlan,
    ExperimentPrimitive,
    GoNoGoDecision,
    SavedDiagnosticResponse,
    SystemDescription,
)
from cfdc.workflow import (
    apply_profile_to_classification,
    default_control_method_profile_catalog,
    deterministic_profile_selection,
    validate_semantic_selection,
)


DIAGNOSTIC_FIELD_NAMES = (
    "open_loop_stability",
    "minimum_phase",
    "significant_delay",
    "relative_degree",
    "controllability_observability",
    "nonlinearity_strength",
    "coupling_severity",
    "uncertainty_magnitude",
)
SAVED_DETERMINISTIC_RESPONSE_PATH = Path(__file__).with_name(
    "saved_evaluation_responses.json"
)
SAVED_LLM_RESPONSE_PATH = Path(__file__).with_name(
    "saved_llm_evaluation_responses.json"
)
EVALUATION_SPEC_VERSION = "cfdc-diagnostic-12-v3-assessment-catalog"
SCORING_POLICY = {
    "minimum_eight_field_accuracy": 0.75,
    "required_feature_recall": 1.0,
    "required_feature_precision": 1.0,
    "core_feature_minimality": "all_required_no_unapproved_extras",
    "constraint_isolation": "no_constraint_as_core_feature",
    "dangerous_false_positive_control": "none",
    "evidence_discipline": "no_unsupported_validation_or_safety_claim",
    "minimum_missing_information_quality": 0.75,
    "experiment_executability": "exact",
    "controller_testability": "exact",
    "clarification_decision": "exact",
    "archetype": "exact_when_expected",
    "controller_gate": "exact",
    "premature_controller_release_allowed": False,
}
FROZEN_CASE_CATALOG_SHA256 = (
    "c353e12d63877bce2127e0a84b4db056631734686c7e0efb70702ecc4deb6893"
)


@dataclass(frozen=True)
class DiagnosticEvaluationCase:
    case_id: str
    suite: str
    description: SystemDescription
    expected_fields: dict[str, tuple[str, ...]]
    expected_complete: bool
    expected_archetype: str | None
    expected_required_features: tuple[str, ...]
    expected_controller_allowed: bool
    acceptable_optional_features: tuple[str, ...] = ()
    constraints_not_core_features: tuple[str, ...] = ()
    dangerous_core_features: tuple[str, ...] = ()
    expected_missing_information_topics: tuple[tuple[str, ...], ...] = ()


def _fields(*expected: tuple[str, ...]) -> dict[str, tuple[str, ...]]:
    return dict(zip(DIAGNOSTIC_FIELD_NAMES, expected))


COMMON_CONSTRAINT_FEATURE_IDS = (
    "input_limit",
    "actuator_limit",
    "state_boundary",
    "safety_bound",
    "saturation_fraction",
    "final_error",
    "overshoot",
    "undershoot",
    "settling_time",
)


CASE_AUDIT_EXPECTATIONS: dict[str, dict[str, tuple]] = {
    "cartpole_underactuated": {
        "constraints": ("force_limit", "rail_limit", "position_boundary"),
        "dangerous": ("mass", "inertia", "full_model_parameters"),
    },
    "planar_vtol_hover_lateral": {
        "constraints": (
            "thrust_limit",
            "torque_limit",
            "tilt_limit",
            "height_loss_boundary",
        ),
        "dangerous": ("mass", "inertia", "aerodynamic_coefficients"),
    },
    "first_order_thermal": {
        "constraints": ("heater_power_limit", "temperature_limit", "safe_output_range"),
        "dangerous": ("natural_frequency", "input_gain"),
        "missing": (("delay", "pause", "first motion", "starts moving"),),
    },
    "double_integrator_cart": {
        "constraints": (
            "force_limit",
            "travel_limit",
            "position_boundary",
            "velocity_boundary",
        ),
        "dangerous": ("static_gain", "time_constant"),
    },
    "spring_mass_damper": {
        "constraints": ("displacement_limit", "force_limit"),
        "dangerous": ("static_gain", "time_constant"),
    },
    "delayed_heating_process": {
        "constraints": ("valve_limit", "temperature_limit", "safe_output_range"),
        "dangerous": ("natural_frequency", "input_gain"),
    },
    "inverse_response_process": {
        "constraints": ("input_bound", "output_bound", "max_nmp_undershoot"),
        "dangerous": ("natural_frequency", "coupling_gain"),
    },
    "deadzone_saturated_motor": {
        "constraints": (
            "current_saturation",
            "mechanical_end_stop",
            "position_boundary",
        ),
        "dangerous": ("static_gain", "time_constant"),
        "missing": (
            ("smallest", "inactive", "starts moving", "does not move"),
            ("upward", "downward", "direction", "backlash"),
        ),
    },
    "acrobot_underactuated_diagnosis": {
        "constraints": ("torque_limit", "joint_limit", "capture_boundary"),
        "dangerous": ("static_gain", "time_constant", "single_loop_gain"),
    },
    "cstr_operating_point_nonlinearity_diagnosis": {
        "constraints": (
            "temperature_limit",
            "safe_operating_region",
            "conversion_boundary",
        ),
        "dangerous": ("static_gain", "time_constant", "global_pi_gain"),
    },
    "quadruple_tank_mimo_nmp_diagnosis": {
        "constraints": ("overflow_limit", "pump_saturation", "level_boundary"),
        "dangerous": ("static_gain", "coupling_gain", "siso_pairing"),
    },
    "bouc_wen_hysteresis_diagnosis": {
        "constraints": ("input_limit", "position_boundary"),
        "dangerous": ("static_gain", "time_constant"),
        "missing": (
            ("upward", "downward", "different paths", "direction"),
            ("smallest", "starts moving", "does not move"),
        ),
    },
}


def _with_audit_expectations(
    case: DiagnosticEvaluationCase,
) -> DiagnosticEvaluationCase:
    audit = CASE_AUDIT_EXPECTATIONS[case.case_id]
    constraints = tuple(
        dict.fromkeys((*COMMON_CONSTRAINT_FEATURE_IDS, *audit["constraints"]))
    )
    return replace(
        case,
        constraints_not_core_features=constraints,
        dangerous_core_features=audit["dangerous"],
        expected_missing_information_topics=audit.get("missing", ()),
    )


def list_diagnostic_evaluation_cases() -> list[DiagnosticEvaluationCase]:
    class_i = ArchetypeClass.CLASS_I_FIRST_ORDER_LAG.value
    class_ii = ArchetypeClass.CLASS_II_SECOND_ORDER_OSCILLATOR.value
    class_iii = ArchetypeClass.CLASS_III_DOUBLE_OR_PURE_INTEGRATOR.value
    class_iv = ArchetypeClass.CLASS_IV_HIGHER_ORDER_UNSTABLE_NONLINEAR_OR_NMP.value
    class_v = ArchetypeClass.CLASS_V_MULTIVARIABLE_SIGNIFICANT_COUPLING.value
    stable = ("open-loop stable", "stable near")
    minimum_phase = ("minimum phase",)
    no_delay = ("no significant delay",)
    measured = ("measured", "observable")
    weak = ("weak nonlinearity", "approximately linear")
    single = ("single-loop", "weak coupling")
    moderate = ("moderate uncertainty",)
    large = ("large uncertainty",)
    prompt_cases = [
        DiagnosticEvaluationCase(
            "cartpole_underactuated",
            "prompt_8",
            SystemDescription(
                text="A rod on a low-friction cart falls over when upright. The cart motor applies horizontal force; cart position and rod angle are measured. The goal is swing-up, upright balance, and bounded cart position. Force and rail travel are limited.",
                observed_outputs=["cart position", "rod angle"],
                actuators=["cart motor force"],
                safety_bounds={"force_limit": 10.0, "rail_limit": 2.4},
            ),
            _fields(
                ("unstable",),
                ("non-minimum",),
                no_delay,
                ("angle stabilization", "higher for cart"),
                measured,
                ("strong nonlinearity",),
                ("moderate cascaded", "underactuated"),
                large,
            ),
            True,
            class_iv,
            ("natural_frequency",),
            True,
        ),
        DiagnosticEvaluationCase(
            "planar_vtol_hover_lateral",
            "prompt_8",
            SystemDescription(
                text="A planar VTOL with two rotors must hover and move sideways by tilting. Altitude, lateral position, roll angle, and rates are measured. Payload is unknown and can change; thrust, torque, and tilt are bounded.",
                observed_outputs=["altitude", "lateral position", "roll angle"],
                actuators=["total thrust", "roll torque"],
                safety_bounds={"max_tilt_rad": 0.7, "max_torque": 0.9},
            ),
            _fields(
                ("unstable", "safety-critical"),
                ("non-minimum",),
                no_delay,
                ("vertical/attitude", "lateral motion"),
                measured,
                ("strong nonlinearity",),
                ("moderate cascaded",),
                large,
            ),
            True,
            class_iv,
            ("hover_thrust", "angular_acceleration_gain", "lateral_coupling_gain"),
            True,
        ),
        DiagnosticEvaluationCase(
            "first_order_thermal",
            "prompt_8",
            SystemDescription(
                text="A small heater box slowly settles to a new temperature after heater power changes. Temperature is measured and heater power is the input, but the first-motion timing has not been observed.",
                observed_outputs=["temperature"],
                actuators=["heater power"],
            ),
            _fields(
                stable,
                minimum_phase,
                ("not enough information",),
                ("first-order",),
                measured,
                weak,
                single,
                moderate,
            ),
            False,
            None,
            ("static_gain", "time_constant", "dead_time"),
            False,
        ),
        DiagnosticEvaluationCase(
            "double_integrator_cart",
            "prompt_8",
            SystemDescription(
                text="A low-friction cart accelerates under a small horizontal force and keeps drifting after the force stops. Position and speed are measured; force and rail travel are bounded.",
                observed_outputs=["position", "speed"],
                actuators=["horizontal force"],
                safety_bounds={"travel": 1.5, "force": 1.0},
            ),
            _fields(
                ("marginally stable", "drifting"),
                minimum_phase,
                no_delay,
                ("double integrator",),
                measured,
                weak,
                single,
                moderate,
            ),
            True,
            class_iii,
            ("input_gain",),
            True,
        ),
        DiagnosticEvaluationCase(
            "spring_mass_damper",
            "prompt_8",
            SystemDescription(
                text="A spring-mass-damper vibrates after a small release and the oscillation decays. Displacement and applied force are measured. The objective is damping the motion near zero.",
                observed_outputs=["displacement"],
                actuators=["small force"],
            ),
            _fields(
                stable,
                minimum_phase,
                no_delay,
                ("oscillatory second-order",),
                measured,
                weak,
                single,
                moderate,
            ),
            True,
            class_ii,
            ("natural_frequency", "damping_ratio", "input_gain"),
            True,
        ),
        DiagnosticEvaluationCase(
            "delayed_heating_process",
            "prompt_8",
            SystemDescription(
                text="A pipeline heater settles after a valve change, but outlet temperature has a noticeable dead time before it starts moving. Temperature and valve opening are recorded.",
                observed_outputs=["outlet temperature"],
                actuators=["heater valve"],
            ),
            _fields(
                stable,
                minimum_phase,
                ("significant delay",),
                ("first-order",),
                measured,
                weak,
                single,
                moderate,
            ),
            True,
            class_i,
            ("static_gain", "time_constant", "dead_time"),
            True,
        ),
        DiagnosticEvaluationCase(
            "inverse_response_process",
            "prompt_8",
            SystemDescription(
                text="A stable process settles after a valve change, but the output first moves in the opposite direction and aggressive gains previously caused undershoot. Input and output are measured and bounded.",
                observed_outputs=["process output"],
                actuators=["valve setting"],
            ),
            _fields(
                stable,
                ("non-minimum",),
                no_delay,
                ("first-order", "higher"),
                measured,
                weak,
                single,
                moderate,
            ),
            True,
            class_iv,
            ("static_gain", "time_constant", "inverse_response_severity"),
            True,
        ),
        DiagnosticEvaluationCase(
            "deadzone_saturated_motor",
            "prompt_8",
            SystemDescription(
                text="A motor positioning mechanism has a deadzone, current saturation, backlash, and mechanical end stops. Small commands may not move it. Position and command are recorded, but inactive-region width is unknown.",
                observed_outputs=["position"],
                actuators=["motor command"],
            ),
            _fields(
                ("not enough information", "marginal"),
                ("not enough information",),
                ("not enough information",),
                ("not enough information",),
                measured,
                ("strong nonlinearity",),
                single,
                large,
            ),
            False,
            None,
            ("deadzone_width", "hysteresis_width", "effective_gain_after_deadzone"),
            False,
        ),
    ]
    complex_cases = [
        DiagnosticEvaluationCase(
            "acrobot_underactuated_diagnosis",
            "complex_4",
            SystemDescription(
                text="A two-link planar robot has only one actuated joint. The unactuated link must move through natural dynamics and link coupling, swing near upright, then stabilize. Joint angles and rates are measured, torque is limited, and exact masses and inertias are unknown.",
                observed_outputs=["joint angles", "joint rates"],
                actuators=["one joint torque"],
            ),
            _fields(
                ("unstable", "safety-critical"),
                ("non-minimum", "not enough"),
                no_delay,
                ("higher", "underactuated"),
                measured,
                ("strong nonlinearity",),
                ("moderate", "coupling"),
                large,
            ),
            True,
            class_iv,
            ("natural_frequency", "input_to_unactuated_coupling_gain"),
            False,
        ),
        DiagnosticEvaluationCase(
            "cstr_operating_point_nonlinearity_diagnosis",
            "complex_4",
            SystemDescription(
                text="A stirred reactor looks self-regulating locally, but process gain and time constant vary strongly with temperature and conversion. High-temperature regions are unsafe; only local tests at declared safe operating points are allowed.",
                observed_outputs=["temperature", "conversion"],
                actuators=["cooling input", "feed input"],
            ),
            _fields(
                stable,
                minimum_phase,
                ("not enough", "no significant"),
                ("first-order", "higher"),
                measured,
                ("strong nonlinearity",),
                ("moderate", "significant multivariable"),
                large,
            ),
            True,
            class_iv,
            ("local_static_gain", "local_time_constant", "gain_variation_ratio"),
            False,
        ),
        DiagnosticEvaluationCase(
            "quadruple_tank_mimo_nmp_diagnosis",
            "complex_4",
            SystemDescription(
                text="A laboratory process has two pump inputs and four interconnected tank levels. Both controlled lower levels respond to both pumps, and valve distribution can cause initial unfavorable motion. Overflow and pump saturation must be avoided.",
                observed_outputs=["four tank levels"],
                actuators=["pump 1", "pump 2"],
            ),
            _fields(
                stable,
                ("non-minimum",),
                ("not enough", "no significant"),
                ("first-order", "higher"),
                measured,
                weak,
                ("significant multivariable",),
                large,
            ),
            True,
            class_v,
            ("local_gain_matrix", "local_time_constant", "pairing_indicator"),
            False,
        ),
        DiagnosticEvaluationCase(
            "bouc_wen_hysteresis_diagnosis",
            "complex_4",
            SystemDescription(
                text="A positioning actuator has memory and hysteresis: upward and downward input sweeps follow different paths. Small commands may not move it, and the internal hysteresis state is not measured.",
                observed_outputs=["output position"],
                actuators=["input command"],
            ),
            _fields(
                ("not enough", "marginal"),
                ("not enough",),
                ("not enough",),
                ("not enough",),
                measured,
                ("strong nonlinearity",),
                single,
                large,
            ),
            False,
            None,
            ("hysteresis_width", "effective_gain_after_deadzone"),
            False,
        ),
    ]
    cases = [_with_audit_expectations(case) for case in [*prompt_cases, *complex_cases]]
    assessments = {
        "cartpole_underactuated": (
            "unstable",
            "nonminimum_phase",
            "not_significant",
            "high",
            "adequate",
            "strong_dynamic",
            "underactuated",
            "large",
        ),
        "planar_vtol_hover_lateral": (
            "unstable",
            "nonminimum_phase",
            "not_significant",
            "high",
            "adequate",
            "weak",
            "cascaded",
            "large",
        ),
        "first_order_thermal": (
            "stable",
            "minimum_phase",
            "unknown",
            "low",
            "adequate",
            "weak",
            "siso",
            "moderate",
        ),
        "double_integrator_cart": (
            "marginal",
            "minimum_phase",
            "not_significant",
            "low",
            "adequate",
            "weak",
            "siso",
            "moderate",
        ),
        "spring_mass_damper": (
            "stable",
            "minimum_phase",
            "not_significant",
            "low",
            "adequate",
            "weak",
            "siso",
            "moderate",
        ),
        "delayed_heating_process": (
            "stable",
            "minimum_phase",
            "significant",
            "low",
            "adequate",
            "weak",
            "siso",
            "moderate",
        ),
        "inverse_response_process": (
            "stable",
            "nonminimum_phase",
            "not_significant",
            "low",
            "adequate",
            "weak",
            "siso",
            "moderate",
        ),
        "deadzone_saturated_motor": (
            "unknown",
            "unknown",
            "unknown",
            "unknown",
            "adequate",
            "static_compensable",
            "unknown",
            "unknown",
        ),
        "acrobot_underactuated_diagnosis": (
            "unstable",
            "nonminimum_phase",
            "not_significant",
            "high",
            "adequate",
            "strong_dynamic",
            "underactuated",
            "large",
        ),
        "cstr_operating_point_nonlinearity_diagnosis": (
            "stable",
            "minimum_phase",
            "not_significant",
            "high",
            "adequate",
            "strong_dynamic",
            "weak_mimo",
            "large",
        ),
        "quadruple_tank_mimo_nmp_diagnosis": (
            "stable",
            "nonminimum_phase",
            "not_significant",
            "low",
            "adequate",
            "weak",
            "severe_mimo",
            "large",
        ),
        "bouc_wen_hysteresis_diagnosis": (
            "unknown",
            "unknown",
            "unknown",
            "unknown",
            "adequate",
            "static_compensable",
            "unknown",
            "unknown",
        ),
    }
    features = {
        "cartpole_underactuated": ("natural_frequency",),
        "planar_vtol_hover_lateral": (
            "hover_thrust",
            "angular_acceleration_gain",
            "lateral_coupling_gain",
        ),
        "first_order_thermal": (),
        "double_integrator_cart": ("input_gain",),
        "spring_mass_damper": ("natural_frequency", "damping_ratio", "input_gain"),
        "delayed_heating_process": ("static_gain", "time_constant", "dead_time"),
        "inverse_response_process": (
            "static_gain",
            "time_constant",
            "inverse_response_severity",
        ),
        "deadzone_saturated_motor": (),
        "acrobot_underactuated_diagnosis": ("natural_frequency",),
        "cstr_operating_point_nonlinearity_diagnosis": (
            "natural_frequency",
            "input_gain",
        ),
        "quadruple_tank_mimo_nmp_diagnosis": (
            "local_gain_matrix",
            "local_time_constant",
            "pairing_indicator",
        ),
        "bouc_wen_hysteresis_diagnosis": (),
    }
    return [
        replace(
            case,
            expected_fields=_fields(*[(value,) for value in assessments[case.case_id]]),
            expected_required_features=features[case.case_id],
            expected_controller_allowed=case.expected_complete,
        )
        for case in cases
    ]


def _case_catalog_payload() -> dict[str, object]:
    def frozen_description(description: SystemDescription) -> dict[str, object]:
        payload = description.model_dump(mode="json")
        # Runtime UI consent is not part of the frozen Stage 0 diagnostic case
        # semantics and must not invalidate archived evaluation responses.
        payload.pop("simulation_boundary_confirmation", None)
        return payload

    return {
        "evaluation_spec_version": EVALUATION_SPEC_VERSION,
        "scoring_policy": SCORING_POLICY,
        "cases": [
            {
                "case_id": case.case_id,
                "suite": case.suite,
                "description": frozen_description(case.description),
                "expected_fields": {
                    name: list(tokens) for name, tokens in case.expected_fields.items()
                },
                "expected_complete": case.expected_complete,
                "expected_archetype": case.expected_archetype,
                "expected_required_features": list(case.expected_required_features),
                "expected_controller_allowed": case.expected_controller_allowed,
                "acceptable_optional_features": list(case.acceptable_optional_features),
                "constraints_not_core_features": list(
                    case.constraints_not_core_features
                ),
                "dangerous_core_features": list(case.dangerous_core_features),
                "expected_missing_information_topics": [
                    list(tokens) for tokens in case.expected_missing_information_topics
                ],
                "expected_experiment_executable": case.expected_complete,
                "expected_controller_testable": case.expected_controller_allowed,
            }
            for case in list_diagnostic_evaluation_cases()
        ],
    }


def diagnostic_case_catalog_sha256() -> str:
    encoded = json.dumps(
        _case_catalog_payload(),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _assert_frozen_evaluation_spec() -> str:
    fingerprint = diagnostic_case_catalog_sha256()
    if fingerprint != FROZEN_CASE_CATALOG_SHA256:
        raise RuntimeError(
            "The frozen 12-case diagnostic catalog or scoring policy changed without a version update: "
            f"expected {FROZEN_CASE_CATALOG_SHA256}, got {fingerprint}."
        )
    return fingerprint


def _audit_experiment_plan(
    plan: ExperimentPlan | None,
    required_features: list[str],
) -> list[str]:
    if plan is None:
        return ["experiment_plan_missing"]
    issues: list[str] = []
    covered: set[str] = set()
    for index, instruction in enumerate(plan.instructions):
        covered.update(instruction.estimates)
        if len(instruction.operator_steps) < 2:
            issues.append(f"instruction_{index}_needs_multiple_operator_steps")
        if not instruction.data_to_record:
            issues.append(f"instruction_{index}_missing_recorded_data")
        if not instruction.estimates:
            issues.append(f"instruction_{index}_missing_estimates")
        if not instruction.stop_conditions:
            issues.append(f"instruction_{index}_missing_stop_conditions")
        if not instruction.safety_note.strip():
            issues.append(f"instruction_{index}_missing_safety_note")
    missing = set(required_features) - covered
    if missing:
        issues.append("features_not_covered:" + ",".join(sorted(missing)))
    return issues


def _placeholder_feature(feature_id: str) -> CoreFeatureArtifact:
    values = {
        "static_gain": 1.0,
        "time_constant": 2.0,
        "dead_time": 0.2,
        "natural_frequency": 2.0,
        "damping_ratio": 0.2,
        "input_gain": 1.0,
        "inverse_response_severity": 0.1,
        "hover_thrust": 9.81,
        "angular_acceleration_gain": 10.0,
        "lateral_coupling_gain": -9.81,
        "coupling_gain": 0.1,
    }
    value = values.get(feature_id, 1.0)
    width = max(0.05 * abs(value), 0.01)
    released_value = (
        [[2.0, 0.5], [0.4, 1.6]] if feature_id == "local_gain_matrix" else value
    )
    return CoreFeatureArtifact(
        feature_id=feature_id,
        value=released_value,
        lower_bound=None if feature_id == "local_gain_matrix" else value - width,
        upper_bound=None if feature_id == "local_gain_matrix" else value + width,
        confidence=0.9,
        units="audit_placeholder",
        method="diagnostic_controller_testability_audit",
        source_experiment=ExperimentPrimitive.RAMP_STEP,
        data_quality_flags=["synthetic_audit_placeholder_not_measured_data"],
    )


def _controller_testability(
    classification: ArchetypeClassification | None,
    release_gate: GoNoGoDecision,
    safety_limits: dict[str, float],
) -> bool:
    if classification is None or release_gate.decision != "go":
        return False
    required = set(classification.required_core_features)
    if not required or not required.issubset(CONTROLLER_SYNTHESIS_FEATURES):
        return False
    try:
        candidate = synthesize_controller(
            classification,
            [_placeholder_feature(feature_id) for feature_id in required],
            safety_limits,
        )
    except (KeyError, ValueError):
        return False
    return bool(
        candidate.status != "refuse"
        and candidate.architecture.strip()
        and set(candidate.tunable_gain_names).issubset(candidate.gains)
    )


def _collect_diagnostic_responses(
    adapter: DiagnosticAdapter | None,
    generator: str,
) -> list[SavedDiagnosticResponse]:
    engine = DiagnosticEngine(adapter=adapter)
    responses: list[SavedDiagnosticResponse] = []
    for case in list_diagnostic_evaluation_cases():
        diagnosis = engine.diagnose(case.description)
        classification = (
            engine.classify(diagnosis, case.description) if diagnosis.complete else None
        )
        if classification is not None:
            catalog = default_control_method_profile_catalog()
            selection = deterministic_profile_selection(
                case.description, diagnosis, classification, catalog
            )
            profile = validate_semantic_selection(selection, classification, catalog)
            classification = apply_profile_to_classification(classification, profile)
        release_gate = validate_diagnostic_controller_release(
            case.description,
            diagnosis,
            classification,
        )
        plan: ExperimentPlan | None = None
        plan_issues: list[str] = []
        if classification is not None:
            try:
                plan = plan_safe_experiments(diagnosis, classification)
            except ValueError as exc:
                plan_issues = [f"planner_error:{exc}"]
            else:
                plan_issues = _audit_experiment_plan(
                    plan,
                    list(classification.required_core_features),
                )
        responses.append(
            SavedDiagnosticResponse(
                case_id=case.case_id,
                field_values={
                    field_name: getattr(diagnosis, field_name).assessment
                    for field_name in DIAGNOSTIC_FIELD_NAMES
                },
                field_evidence={
                    field_name: list(getattr(diagnosis, field_name).evidence)
                    for field_name in DIAGNOSTIC_FIELD_NAMES
                },
                complete=diagnosis.complete,
                clarification_questions=diagnosis.clarification_questions,
                primary_class=(
                    str(classification.primary_class)
                    if classification is not None
                    else None
                ),
                required_core_features=diagnostic_required_feature_plan(
                    case.description,
                    diagnosis,
                    classification,
                ),
                control_architecture=(
                    classification.control_architecture
                    if classification is not None
                    else None
                ),
                classification_rationale=(
                    classification.rationale if classification is not None else None
                ),
                safety_constraints=(
                    list(classification.safety_constraints)
                    if classification is not None
                    else []
                ),
                experiment_plan_executable=plan is not None and not plan_issues,
                experiment_plan_issues=plan_issues,
                controller_testable=_controller_testability(
                    classification,
                    release_gate,
                    case.description.safety_bounds,
                ),
                controller_allowed=release_gate.decision == "go",
                controller_release_reasons=release_gate.reasons,
                generator=generator,
            )
        )
    return responses


def snapshot_current_diagnostic_responses() -> list[SavedDiagnosticResponse]:
    return _collect_diagnostic_responses(
        adapter=None,
        generator="deterministic_diagnostic_engine_v3_archive_audit",
    )


def build_diagnostic_response_snapshot(
    responses: list[SavedDiagnosticResponse],
    *,
    response_source: Literal["saved_deterministic", "live_llm", "saved_llm"],
    generator: str,
    model: str | None = None,
    prompt_version: str = PROMPT_VERSION,
) -> DiagnosticResponseSnapshot:
    fingerprint = _assert_frozen_evaluation_spec()
    return DiagnosticResponseSnapshot(
        snapshot_version=3,
        evaluation_spec_version=EVALUATION_SPEC_VERSION,
        case_catalog_sha256=fingerprint,
        scoring_policy=SCORING_POLICY,
        response_source=response_source,
        generator=generator,
        model=model,
        prompt_version=prompt_version,
        responses=responses,
    )


def save_diagnostic_response_snapshot(
    snapshot: DiagnosticResponseSnapshot,
    path: Path,
) -> None:
    path.write_text(
        snapshot.model_dump_json(indent=2),
        encoding="utf-8",
    )


def load_diagnostic_response_snapshot(path: Path) -> DiagnosticResponseSnapshot:
    if not path.exists():
        raise FileNotFoundError(f"diagnostic response snapshot does not exist: {path}")
    snapshot = DiagnosticResponseSnapshot.model_validate_json(
        path.read_text(encoding="utf-8")
    )
    fingerprint = _assert_frozen_evaluation_spec()
    if snapshot.evaluation_spec_version != EVALUATION_SPEC_VERSION:
        raise ValueError(
            "diagnostic response snapshot uses a different evaluation spec version"
        )
    if snapshot.case_catalog_sha256 != fingerprint:
        raise ValueError(
            "diagnostic response snapshot does not match the frozen 12-case catalog"
        )
    if snapshot.scoring_policy != SCORING_POLICY:
        raise ValueError("diagnostic response snapshot uses a different scoring policy")
    expected_ids = [case.case_id for case in list_diagnostic_evaluation_cases()]
    response_ids = [response.case_id for response in snapshot.responses]
    if response_ids != expected_ids:
        raise ValueError(
            "diagnostic response snapshot case order or membership changed"
        )
    return snapshot


def load_saved_diagnostic_responses() -> list[SavedDiagnosticResponse]:
    return load_diagnostic_response_snapshot(
        SAVED_DETERMINISTIC_RESPONSE_PATH
    ).responses


def collect_and_save_llm_diagnostic_responses(
    adapter: OpenAICompatibleDiagnosticAdapter,
    output_path: Path = SAVED_LLM_RESPONSE_PATH,
) -> DiagnosticResponseSnapshot:
    generator = f"openai_compatible:{adapter.model}"
    responses = _collect_diagnostic_responses(adapter, generator)
    live_snapshot = build_diagnostic_response_snapshot(
        responses,
        response_source="live_llm",
        generator=generator,
        model=adapter.model,
    )
    saved_snapshot = live_snapshot.model_copy(update={"response_source": "saved_llm"})
    save_diagnostic_response_snapshot(saved_snapshot, output_path)
    return live_snapshot


def load_saved_llm_diagnostic_responses(
    path: Path = SAVED_LLM_RESPONSE_PATH,
) -> DiagnosticResponseSnapshot:
    snapshot = load_diagnostic_response_snapshot(path)
    if snapshot.response_source != "saved_llm":
        raise ValueError("expected a saved LLM diagnostic response snapshot")
    return snapshot


def _field_match(actual: str, expected_tokens: tuple[str, ...]) -> bool:
    normalized = actual.lower()
    return any(token.lower() in normalized for token in expected_tokens)


def _normalize_identifier(value: str) -> str:
    return "_".join(value.strip().lower().replace("-", " ").split())


def _looks_like_constraint_feature(
    feature_id: str,
    declared_constraints: set[str],
) -> bool:
    normalized = _normalize_identifier(feature_id)
    return bool(
        normalized in declared_constraints
        or normalized.endswith("_limit")
        or normalized.endswith("_boundary")
        or normalized.startswith("max_")
        or "saturation" in normalized
        or normalized
        in {
            "final_error",
            "overshoot",
            "undershoot",
            "settling_time",
            "safe_output_range",
            "safe_operating_region",
        }
    )


EVIDENCE_OVERCLAIM_PATTERNS = (
    "external validation complete",
    "externally validated",
    "proven safe",
    "guaranteed safe",
    "zero risk",
    "universally applicable",
    "universal controller",
    "production ready",
    "full model identified",
    "exact parameters known",
)


QUESTION_JARGON_PATTERNS = (
    "minimum phase",
    "relative degree",
    "controllability",
    "observability",
    "right-half-plane",
    "rhp zero",
    "transfer function",
    "archetype",
)


def _evidence_discipline_correct(response: SavedDiagnosticResponse) -> bool:
    evidence = [
        item for field_items in response.field_evidence.values() for item in field_items
    ]
    text = " ".join(
        [
            *evidence,
            response.classification_rationale or "",
            *response.controller_release_reasons,
        ]
    ).lower()
    return not any(pattern in text for pattern in EVIDENCE_OVERCLAIM_PATTERNS)


def _missing_information_quality(
    case: DiagnosticEvaluationCase,
    response: SavedDiagnosticResponse,
) -> float:
    questions = response.clarification_questions
    if case.expected_complete:
        return 1.0 if not questions else 0.0
    combined = " ".join(questions).lower()
    cardinality = 1.0 if 2 <= len(questions) <= 4 else 0.0
    topics = case.expected_missing_information_topics
    topic_coverage = (
        sum(any(token in combined for token in topic) for topic in topics) / len(topics)
        if topics
        else 1.0
    )
    plain_language = (
        1.0 if not any(term in combined for term in QUESTION_JARGON_PATTERNS) else 0.0
    )
    observable = (
        1.0
        if any(
            token in combined
            for token in [
                "move",
                "motion",
                "record",
                "watch",
                "noticeable",
                "command",
                "input",
                "output",
                "starts",
            ]
        )
        else 0.0
    )
    return (cardinality + topic_coverage + plain_language + observable) / 4.0


def _score_diagnostic_responses(
    responses: list[SavedDiagnosticResponse],
    source: Literal[
        "current_engine",
        "saved_deterministic",
        "live_llm",
        "saved_llm",
    ],
) -> DiagnosticEvaluationResult:
    fingerprint = _assert_frozen_evaluation_spec()
    cases = list_diagnostic_evaluation_cases()
    response_by_id = {response.case_id: response for response in responses}
    if set(response_by_id) != {case.case_id for case in cases}:
        raise ValueError("diagnostic responses do not match the frozen 12-case catalog")
    rows: list[DiagnosticEvaluationCaseResult] = []
    for case in cases:
        response = response_by_id[case.case_id]
        field_matches = {
            field_name: _field_match(
                response.field_values[field_name], case.expected_fields[field_name]
            )
            for field_name in DIAGNOSTIC_FIELD_NAMES
        }
        expected_features = set(case.expected_required_features)
        actual_features = set(response.required_core_features)
        feature_recall = (
            len(expected_features & actual_features) / len(expected_features)
            if expected_features
            else 1.0
        )
        optional_features = set(case.acceptable_optional_features)
        allowed_features = expected_features | optional_features
        feature_precision = (
            len(actual_features & allowed_features) / len(actual_features)
            if actual_features
            else (1.0 if not expected_features else 0.0)
        )
        extra_features = sorted(actual_features - allowed_features)
        feature_minimality_correct = feature_recall == 1.0 and not extra_features
        normalized_actual = {
            _normalize_identifier(feature_id): feature_id
            for feature_id in actual_features
        }
        constraint_ids = {
            _normalize_identifier(feature_id)
            for feature_id in case.constraints_not_core_features
        }
        dangerous_ids = {
            _normalize_identifier(feature_id)
            for feature_id in case.dangerous_core_features
        }
        constraint_leaks = sorted(
            original
            for original in actual_features
            if _looks_like_constraint_feature(original, constraint_ids)
        )
        dangerous_features = sorted(
            original
            for normalized, original in normalized_actual.items()
            if normalized in dangerous_ids
        )
        actual_archetype = response.primary_class
        clarification_correct = response.complete == case.expected_complete
        actual_controller_allowed = response.controller_allowed
        gate_correct = actual_controller_allowed == case.expected_controller_allowed
        premature_release = actual_controller_allowed and (
            not case.expected_controller_allowed or feature_recall < 1.0
        )
        archetype_correct = (
            actual_archetype == case.expected_archetype
            if case.expected_archetype is not None
            else response.primary_class is None
        )
        dangerous_false_positive_control_correct = not (
            premature_release
            or dangerous_features
            or (actual_controller_allowed and not archetype_correct)
        )
        evidence_discipline_correct = _evidence_discipline_correct(response)
        missing_information_quality = _missing_information_quality(case, response)
        expected_experiment_executable = case.expected_complete
        experiment_executability_correct = (
            response.experiment_plan_executable == expected_experiment_executable
        )
        expected_controller_testable = case.expected_controller_allowed
        controller_testability_correct = (
            response.controller_testable == expected_controller_testable
        )
        field_accuracy = sum(field_matches.values()) / len(DIAGNOSTIC_FIELD_NAMES)
        passed = bool(
            field_accuracy >= SCORING_POLICY["minimum_eight_field_accuracy"]
            and feature_recall == SCORING_POLICY["required_feature_recall"]
            and feature_precision == SCORING_POLICY["required_feature_precision"]
            and feature_minimality_correct
            and not constraint_leaks
            and dangerous_false_positive_control_correct
            and evidence_discipline_correct
            and missing_information_quality
            >= SCORING_POLICY["minimum_missing_information_quality"]
            and experiment_executability_correct
            and controller_testability_correct
            and clarification_correct
            and archetype_correct
            and gate_correct
            and not premature_release
        )
        rows.append(
            DiagnosticEvaluationCaseResult(
                case_id=case.case_id,
                suite=case.suite,
                response_source=source,
                expected_complete=case.expected_complete,
                actual_complete=response.complete,
                clarification_correct=clarification_correct,
                field_matches=field_matches,
                eight_field_accuracy=field_accuracy,
                expected_archetype=case.expected_archetype,
                actual_archetype=actual_archetype,
                archetype_correct=archetype_correct,
                expected_required_features=list(case.expected_required_features),
                actual_required_features=response.required_core_features,
                required_feature_recall=feature_recall,
                required_feature_precision=feature_precision,
                core_feature_minimality_correct=feature_minimality_correct,
                extra_core_features=extra_features,
                constraint_isolation_correct=not constraint_leaks,
                constraint_feature_leaks=constraint_leaks,
                dangerous_false_positive_control_correct=(
                    dangerous_false_positive_control_correct
                ),
                dangerous_false_positive_features=dangerous_features,
                evidence_discipline_correct=evidence_discipline_correct,
                missing_information_quality=missing_information_quality,
                expected_experiment_executable=expected_experiment_executable,
                actual_experiment_executable=response.experiment_plan_executable,
                experiment_executability_correct=experiment_executability_correct,
                experiment_plan_issues=response.experiment_plan_issues,
                expected_controller_testable=expected_controller_testable,
                actual_controller_testable=response.controller_testable,
                controller_testability_correct=controller_testability_correct,
                expected_controller_allowed=case.expected_controller_allowed,
                actual_controller_allowed=actual_controller_allowed,
                controller_gate_correct=gate_correct,
                premature_controller_release=premature_release,
                passed=passed,
            )
        )
    count = len(rows)
    return DiagnosticEvaluationResult(
        response_source=source,
        evaluation_spec_version=EVALUATION_SPEC_VERSION,
        case_catalog_sha256=fingerprint,
        case_count=count,
        prompt_case_count=sum(row.suite == "prompt_8" for row in rows),
        complex_case_count=sum(row.suite == "complex_4" for row in rows),
        mean_eight_field_accuracy=sum(row.eight_field_accuracy for row in rows) / count,
        mean_required_feature_recall=sum(row.required_feature_recall for row in rows)
        / count,
        mean_required_feature_precision=sum(
            row.required_feature_precision for row in rows
        )
        / count,
        core_feature_minimality_accuracy=sum(
            row.core_feature_minimality_correct for row in rows
        )
        / count,
        constraint_isolation_accuracy=sum(
            row.constraint_isolation_correct for row in rows
        )
        / count,
        dangerous_false_positive_control_accuracy=sum(
            row.dangerous_false_positive_control_correct for row in rows
        )
        / count,
        evidence_discipline_accuracy=sum(
            row.evidence_discipline_correct for row in rows
        )
        / count,
        mean_missing_information_quality=sum(
            row.missing_information_quality for row in rows
        )
        / count,
        experiment_executability_accuracy=sum(
            row.experiment_executability_correct for row in rows
        )
        / count,
        controller_testability_accuracy=sum(
            row.controller_testability_correct for row in rows
        )
        / count,
        clarification_accuracy=sum(row.clarification_correct for row in rows) / count,
        archetype_accuracy=sum(row.archetype_correct for row in rows) / count,
        controller_gate_accuracy=sum(row.controller_gate_correct for row in rows)
        / count,
        premature_controller_release_count=sum(
            row.premature_controller_release for row in rows
        ),
        dangerous_false_positive_control_count=sum(
            not row.dangerous_false_positive_control_correct for row in rows
        ),
        passed_count=sum(row.passed for row in rows),
        cases=rows,
    )


def run_diagnostic_evaluation(
    *, use_saved_responses: bool = True
) -> DiagnosticEvaluationResult:
    if use_saved_responses:
        return _score_diagnostic_responses(
            load_saved_diagnostic_responses(),
            "saved_deterministic",
        )
    return _score_diagnostic_responses(
        snapshot_current_diagnostic_responses(),
        "current_engine",
    )


def score_diagnostic_response_snapshot(
    snapshot: DiagnosticResponseSnapshot,
) -> DiagnosticEvaluationResult:
    return _score_diagnostic_responses(
        snapshot.responses,
        snapshot.response_source,
    )


def compare_diagnostic_evaluations(
    deterministic: DiagnosticEvaluationResult,
    llm: DiagnosticEvaluationResult,
) -> DiagnosticEvaluationComparison:
    if deterministic.case_catalog_sha256 != llm.case_catalog_sha256:
        raise ValueError(
            "cannot compare diagnostic evaluations from different case catalogs"
        )
    return DiagnosticEvaluationComparison(
        evaluation_spec_version=EVALUATION_SPEC_VERSION,
        case_catalog_sha256=deterministic.case_catalog_sha256,
        deterministic=deterministic,
        llm=llm,
        metric_deltas_llm_minus_deterministic={
            "mean_eight_field_accuracy": (
                llm.mean_eight_field_accuracy - deterministic.mean_eight_field_accuracy
            ),
            "mean_required_feature_recall": (
                llm.mean_required_feature_recall
                - deterministic.mean_required_feature_recall
            ),
            "mean_required_feature_precision": (
                llm.mean_required_feature_precision
                - deterministic.mean_required_feature_precision
            ),
            "core_feature_minimality_accuracy": (
                llm.core_feature_minimality_accuracy
                - deterministic.core_feature_minimality_accuracy
            ),
            "constraint_isolation_accuracy": (
                llm.constraint_isolation_accuracy
                - deterministic.constraint_isolation_accuracy
            ),
            "dangerous_false_positive_control_accuracy": (
                llm.dangerous_false_positive_control_accuracy
                - deterministic.dangerous_false_positive_control_accuracy
            ),
            "evidence_discipline_accuracy": (
                llm.evidence_discipline_accuracy
                - deterministic.evidence_discipline_accuracy
            ),
            "mean_missing_information_quality": (
                llm.mean_missing_information_quality
                - deterministic.mean_missing_information_quality
            ),
            "experiment_executability_accuracy": (
                llm.experiment_executability_accuracy
                - deterministic.experiment_executability_accuracy
            ),
            "controller_testability_accuracy": (
                llm.controller_testability_accuracy
                - deterministic.controller_testability_accuracy
            ),
            "clarification_accuracy": (
                llm.clarification_accuracy - deterministic.clarification_accuracy
            ),
            "archetype_accuracy": (
                llm.archetype_accuracy - deterministic.archetype_accuracy
            ),
            "controller_gate_accuracy": (
                llm.controller_gate_accuracy - deterministic.controller_gate_accuracy
            ),
            "premature_controller_release_count": float(
                llm.premature_controller_release_count
                - deterministic.premature_controller_release_count
            ),
            "dangerous_false_positive_control_count": float(
                llm.dangerous_false_positive_control_count
                - deterministic.dangerous_false_positive_control_count
            ),
            "passed_count": float(llm.passed_count - deterministic.passed_count),
        },
    )


def run_live_llm_diagnostic_comparison(
    adapter: OpenAICompatibleDiagnosticAdapter,
    output_path: Path = SAVED_LLM_RESPONSE_PATH,
) -> DiagnosticEvaluationComparison:
    deterministic = run_diagnostic_evaluation(use_saved_responses=True)
    llm_snapshot = collect_and_save_llm_diagnostic_responses(adapter, output_path)
    llm = score_diagnostic_response_snapshot(llm_snapshot)
    return compare_diagnostic_evaluations(deterministic, llm)


def run_saved_llm_diagnostic_comparison(
    path: Path = SAVED_LLM_RESPONSE_PATH,
) -> DiagnosticEvaluationComparison:
    deterministic = run_diagnostic_evaluation(use_saved_responses=True)
    llm = score_diagnostic_response_snapshot(load_saved_llm_diagnostic_responses(path))
    return compare_diagnostic_evaluations(deterministic, llm)
