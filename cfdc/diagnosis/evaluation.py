from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from cfdc.diagnosis.engine import DiagnosticEngine
from cfdc.models import (
    ArchetypeClass,
    DiagnosticEvaluationCaseResult,
    DiagnosticEvaluationResult,
    SavedDiagnosticResponse,
    SystemDescription,
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
SAVED_RESPONSE_PATH = Path(__file__).with_name("saved_evaluation_responses.json")


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


def _fields(*expected: tuple[str, ...]) -> dict[str, tuple[str, ...]]:
    return dict(zip(DIAGNOSTIC_FIELD_NAMES, expected))


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
            _fields(("unstable",), ("non-minimum",), no_delay, ("angle stabilization", "higher for cart"), measured, ("strong nonlinearity",), ("moderate cascaded", "underactuated"), large),
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
            _fields(("unstable", "safety-critical"), ("non-minimum",), no_delay, ("vertical/attitude", "lateral motion"), measured, ("strong nonlinearity",), ("moderate cascaded",), large),
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
            _fields(stable, minimum_phase, ("not enough information",), ("first-order",), measured, weak, single, moderate),
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
            _fields(("marginally stable", "drifting"), minimum_phase, no_delay, ("double integrator",), measured, weak, single, moderate),
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
            _fields(stable, minimum_phase, no_delay, ("oscillatory second-order",), measured, weak, single, moderate),
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
            _fields(stable, minimum_phase, ("significant delay",), ("first-order",), measured, weak, single, moderate),
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
            _fields(stable, ("non-minimum",), no_delay, ("first-order", "higher"), measured, weak, single, moderate),
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
            _fields(("not enough information", "marginal"), ("not enough information",), ("not enough information",), ("not enough information",), measured, ("strong nonlinearity",), single, large),
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
            _fields(("unstable", "safety-critical"), ("non-minimum", "not enough"), no_delay, ("higher", "underactuated"), measured, ("strong nonlinearity",), ("moderate", "coupling"), large),
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
            _fields(stable, minimum_phase, ("not enough", "no significant"), ("first-order", "higher"), measured, ("strong nonlinearity",), ("moderate", "significant multivariable"), large),
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
            _fields(stable, ("non-minimum",), ("not enough", "no significant"), ("first-order", "higher"), measured, weak, ("significant multivariable",), large),
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
            _fields(("not enough", "marginal"), ("not enough",), ("not enough",), ("not enough",), measured, ("strong nonlinearity",), single, large),
            False,
            None,
            ("hysteresis_width", "effective_gain_after_deadzone"),
            False,
        ),
    ]
    return [*prompt_cases, *complex_cases]


def snapshot_current_diagnostic_responses() -> list[SavedDiagnosticResponse]:
    engine = DiagnosticEngine()
    responses: list[SavedDiagnosticResponse] = []
    for case in list_diagnostic_evaluation_cases():
        diagnosis = engine.diagnose(case.description)
        classification = engine.classify(diagnosis) if diagnosis.complete else None
        responses.append(
            SavedDiagnosticResponse(
                case_id=case.case_id,
                field_values={
                    field_name: getattr(diagnosis, field_name).value
                    for field_name in DIAGNOSTIC_FIELD_NAMES
                },
                complete=diagnosis.complete,
                clarification_questions=diagnosis.clarification_questions,
                primary_class=(
                    str(classification.primary_class) if classification is not None else None
                ),
                required_core_features=(
                    classification.required_core_features if classification is not None else []
                ),
                generator="deterministic_diagnostic_engine_v1",
            )
        )
    return responses


def load_saved_diagnostic_responses() -> list[SavedDiagnosticResponse]:
    payload = json.loads(SAVED_RESPONSE_PATH.read_text(encoding="utf-8"))
    return [SavedDiagnosticResponse.model_validate(item) for item in payload["responses"]]


def _field_match(actual: str, expected_tokens: tuple[str, ...]) -> bool:
    normalized = actual.lower()
    return any(token.lower() in normalized for token in expected_tokens)


def run_diagnostic_evaluation(*, use_saved_responses: bool = True) -> DiagnosticEvaluationResult:
    cases = list_diagnostic_evaluation_cases()
    responses = load_saved_diagnostic_responses() if use_saved_responses else snapshot_current_diagnostic_responses()
    response_by_id = {response.case_id: response for response in responses}
    source = "saved_response" if use_saved_responses else "current_engine"
    rows: list[DiagnosticEvaluationCaseResult] = []
    for case in cases:
        response = response_by_id[case.case_id]
        field_matches = {
            field_name: _field_match(response.field_values[field_name], case.expected_fields[field_name])
            for field_name in DIAGNOSTIC_FIELD_NAMES
        }
        expected_features = set(case.expected_required_features)
        actual_features = set(response.required_core_features)
        feature_recall = len(expected_features & actual_features) / len(expected_features) if expected_features else 1.0
        actual_archetype = response.primary_class
        clarification_correct = response.complete == case.expected_complete
        actual_controller_allowed = response.complete and response.primary_class is not None
        gate_correct = actual_controller_allowed == case.expected_controller_allowed
        premature_release = actual_controller_allowed and (
            not case.expected_controller_allowed or feature_recall < 1.0
        )
        archetype_correct = actual_archetype == case.expected_archetype if case.expected_archetype is not None else response.primary_class is None
        field_accuracy = sum(field_matches.values()) / len(DIAGNOSTIC_FIELD_NAMES)
        passed = bool(
            field_accuracy >= 0.75
            and feature_recall == 1.0
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
        case_count=count,
        prompt_case_count=sum(row.suite == "prompt_8" for row in rows),
        complex_case_count=sum(row.suite == "complex_4" for row in rows),
        mean_eight_field_accuracy=sum(row.eight_field_accuracy for row in rows) / count,
        mean_required_feature_recall=sum(row.required_feature_recall for row in rows) / count,
        clarification_accuracy=sum(row.clarification_correct for row in rows) / count,
        controller_gate_accuracy=sum(row.controller_gate_correct for row in rows) / count,
        premature_controller_release_count=sum(row.premature_controller_release for row in rows),
        passed_count=sum(row.passed for row in rows),
        cases=rows,
    )
