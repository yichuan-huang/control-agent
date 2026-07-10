from __future__ import annotations

from typing import Iterable

from cfdc.diagnosis.llm import DiagnosticAdapter, DeterministicDiagnosticAdapter, validate_agent_payload
from cfdc.diagnosis.safety import enforce_shared_diagnostic_safety_rules
from cfdc.models import (
    ArchetypeClass,
    ArchetypeClassification,
    DelayAssessment,
    DiagnosticField,
    SignificantDelayField,
    StructuralDiagnosis,
    SystemDescription,
)


def _contains(text: str, terms: Iterable[str]) -> bool:
    return any(term in text for term in terms)


def _field(status: str, value: str, confidence: float, evidence: list[str]) -> DiagnosticField:
    return DiagnosticField(status=status, value=value, confidence=confidence, evidence=evidence)


def _delay_field(
    status: str,
    value: str,
    assessment: DelayAssessment,
    confidence: float,
    evidence: list[str],
) -> SignificantDelayField:
    return SignificantDelayField(
        status=status,
        value=value,
        assessment=assessment,
        confidence=confidence,
        evidence=evidence,
    )


def _question_pool(description: SystemDescription, diagnosis: dict[str, DiagnosticField]) -> list[str]:
    questions: list[str] = []
    if not description.observed_outputs:
        questions.append("Which quantities can you watch or record during motion?")
    if not description.actuators:
        questions.append("What physical action or device can change the system?")
    if diagnosis["minimum_phase"].status == "unknown":
        questions.append("When you make a small change, does the measured output first move the expected way or briefly the opposite way?")
    if diagnosis["significant_delay"].status == "unknown":
        questions.append("After a small change, is there a noticeable pause before anything moves?")
    if diagnosis["controllability_observability"].status == "unknown":
        questions.append("Can the device you change affect every motion that might become unsafe?")
    if diagnosis["coupling_severity"].status == "unknown":
        questions.append("If there are several inputs and outputs, does one input strongly move more than one output?")
    if diagnosis["uncertainty_magnitude"].status == "unknown":
        questions.append("Do load, wear, or operating conditions change the behavior noticeably?")
    if len(questions) < 2:
        questions.append("What motion range should never be exceeded during a first test?")
    return questions[:4]


def infer_structural_diagnosis(description: SystemDescription) -> StructuralDiagnosis:
    text = description.text.lower()
    outputs = [item.lower() for item in description.observed_outputs]
    actuators = [item.lower() for item in description.actuators]

    pendulum = _contains(text, ["pendulum", "rod", "cart-pole", "cartpole"])
    vtol = _contains(text, ["vtol", "vertical take", "two rotors", "hover", "aircraft"])
    oscillator = _contains(text, ["oscillat", "vibrat", "reson", "spring", "natural frequency"])
    first_order = _contains(text, ["first-order", "first order", "temperature", "tank level", "lag", "self-regulating", "settles"])
    integrator = _contains(text, ["integrator", "drift", "low-friction", "cart", "position keeps moving"])
    mimo = _contains(text, ["mimo", "multi-input", "multi output", "multiple inputs", "multiple outputs", "coupled"])
    nmp = _contains(text, ["reverse", "opposite", "undershoot", "non-minimum", "nonminimum"]) or pendulum or vtol

    fields: dict[str, DiagnosticField] = {}

    if _contains(text, ["unstable", "falls over", "fall over", "diverge", "upright"]) or pendulum or vtol:
        fields["open_loop_stability"] = _field("inferred", "unstable or safety-critical equilibrium", 0.82, ["description implies an equilibrium that does not hold itself"])
    elif integrator:
        fields["open_loop_stability"] = _field("inferred", "marginally stable drifting motion", 0.75, ["description indicates accumulated motion or drift"])
    elif first_order or oscillator or _contains(text, ["settle", "returns", "decay"]):
        fields["open_loop_stability"] = _field("inferred", "open-loop stable near the operating point", 0.78, ["description suggests settling or free decay"])
    else:
        fields["open_loop_stability"] = _field("unknown", "not enough information", 0.2, [])

    if nmp:
        fields["minimum_phase"] = _field("inferred", "non-minimum phase or inverse-response risk", 0.75, ["description implies initial reverse motion or underactuated outer-loop behavior"])
    elif first_order or oscillator or integrator:
        fields["minimum_phase"] = _field("inferred", "minimum phase expected for the first safe test", 0.62, ["no reverse response was described"])
    else:
        fields["minimum_phase"] = _field("unknown", "not enough information", 0.2, [])

    if _contains(text, ["dead time", "delay", "transport", "noticeable pause"]):
        fields["significant_delay"] = _delay_field(
            "known",
            "significant delay likely",
            DelayAssessment.SIGNIFICANT,
            0.82,
            ["delay is explicitly mentioned"],
        )
    elif _contains(text, ["fast actuator", "reacts instantly", "no delay"]) or pendulum or vtol:
        fields["significant_delay"] = _delay_field(
            "known",
            "no significant delay reported",
            DelayAssessment.NOT_SIGNIFICANT,
            0.7,
            ["fast response is stated or typical for the described benchmark"],
        )
    elif first_order or oscillator or integrator:
        fields["significant_delay"] = _delay_field(
            "inferred",
            "no significant delay reported",
            DelayAssessment.NOT_SIGNIFICANT,
            0.55,
            ["description does not mention a visible pause before motion"],
        )
    else:
        fields["significant_delay"] = _delay_field(
            "unknown",
            "not enough information",
            DelayAssessment.UNKNOWN,
            0.2,
            [],
        )

    if vtol:
        fields["relative_degree"] = _field("inferred", "2 for vertical/attitude channels and high relative degree for lateral motion", 0.82, ["hovering vehicle uses cascaded attitude-to-position motion"])
    elif pendulum:
        fields["relative_degree"] = _field("inferred", "2 for angle stabilization and higher for cart position", 0.82, ["cart force affects rod angle before cart outer-loop objective"])
    elif integrator:
        fields["relative_degree"] = _field("inferred", "2 for double-integrator-like motion", 0.72, ["position changes through velocity"])
    elif oscillator:
        fields["relative_degree"] = _field("inferred", "2 for the dominant oscillatory mode", 0.72, ["second-order oscillation described"])
    elif first_order:
        fields["relative_degree"] = _field("inferred", "1 for first-order lag", 0.72, ["self-regulating lag described"])
    else:
        fields["relative_degree"] = _field("unknown", "not enough information", 0.2, [])

    if outputs and actuators:
        fields["controllability_observability"] = _field("known", "available input and measured output are declared", 0.7, ["actuators and measured outputs are provided"])
    elif _contains(text, ["measured", "sensor", "record", "encoder"]) and _contains(text, ["motor", "throttle", "force", "heater", "pump"]):
        fields["controllability_observability"] = _field("inferred", "likely adequate but should be confirmed", 0.58, ["sensors and actuation are mentioned"])
    else:
        fields["controllability_observability"] = _field("unknown", "sensor-actuator adequacy not confirmed", 0.25, [])

    if pendulum or _contains(text, ["hysteresis", "dead zone", "deadzone", "backlash", "large angle"]):
        fields["nonlinearity_strength"] = _field("inferred", "strong nonlinearity", 0.82, ["description includes large-angle, dead-zone, or hysteresis behavior"])
    elif vtol:
        fields["nonlinearity_strength"] = _field("inferred", "moderate nonlinearity near hover", 0.7, ["tilt and thrust geometry are nonlinear but small hover motions can be localized"])
    elif first_order or oscillator or integrator:
        fields["nonlinearity_strength"] = _field("inferred", "weak nonlinearity or local nonlinearity", 0.62, ["dominant behavior fits a low-order local model"])
    else:
        fields["nonlinearity_strength"] = _field("unknown", "not enough information", 0.2, [])

    if mimo:
        fields["coupling_severity"] = _field("inferred", "significant multivariable coupling possible", 0.78, ["multiple interacting inputs/outputs are described"])
    elif vtol:
        fields["coupling_severity"] = _field("inferred", "moderate cascaded coupling", 0.72, ["lateral motion is mediated by tilt"])
    elif pendulum:
        fields["coupling_severity"] = _field("inferred", "underactuated coupling between cart and rod", 0.74, ["one actuator affects two motions"])
    elif first_order or oscillator or integrator:
        fields["coupling_severity"] = _field("inferred", "single-loop or weak coupling", 0.66, ["no strong multivariable interaction was described"])
    else:
        fields["coupling_severity"] = _field("unknown", "not enough information", 0.2, [])

    if _contains(text, ["unknown parameters", "payload", "wear", "varies", "load change", "operating conditions", "no parameters"]) or pendulum or vtol:
        fields["uncertainty_magnitude"] = _field("inferred", "large uncertainty", 0.8, ["parameters or payload changes are unknown"])
    elif first_order or oscillator or integrator:
        fields["uncertainty_magnitude"] = _field("inferred", "moderate uncertainty", 0.55, ["parameters still need feature extraction"])
    else:
        fields["uncertainty_magnitude"] = _field("unknown", "not enough information", 0.2, [])

    complete = all(field.status != "unknown" for field in fields.values())
    questions = [] if complete else _question_pool(description, fields)
    if not complete and len(questions) < 2:
        questions = (questions + ["What output should be kept safe?", "What is the smallest safe action you can try?"])[:2]

    return StructuralDiagnosis(
        open_loop_stability=fields["open_loop_stability"],
        minimum_phase=fields["minimum_phase"],
        significant_delay=fields["significant_delay"],
        relative_degree=fields["relative_degree"],
        controllability_observability=fields["controllability_observability"],
        nonlinearity_strength=fields["nonlinearity_strength"],
        coupling_severity=fields["coupling_severity"],
        uncertainty_magnitude=fields["uncertainty_magnitude"],
        clarification_questions=questions,
        complete=complete,
    )


def classify_archetype(diagnosis: StructuralDiagnosis) -> ArchetypeClassification:
    stability = diagnosis.open_loop_stability.value.lower()
    phase = diagnosis.minimum_phase.value.lower()
    rel_degree = diagnosis.relative_degree.value.lower()
    nonlinear = diagnosis.nonlinearity_strength.value.lower()
    coupling = diagnosis.coupling_severity.value.lower()
    pendulum_like = "rod angle" in rel_degree or "angle stabilization" in rel_degree

    if "significant multivariable" in coupling:
        matrix_route = "local gain matrix" in coupling or "pairing" in coupling
        return ArchetypeClassification(
            primary_class=ArchetypeClass.CLASS_V_MULTIVARIABLE_SIGNIFICANT_COUPLING,
            control_architecture=(
                "local MIMO gain-matrix experiment and pairing review"
                if matrix_route
                else "conservative loop pairing with optional half-strength static decoupling"
            ),
            required_core_features=(
                ["local_gain_matrix", "local_time_constant", "pairing_indicator"]
                if matrix_route
                else ["coupling_gain"]
            ),
            safety_constraints=["bound each input separately", "freeze if one input moves multiple outputs unexpectedly"],
            rationale="The dominant limitation is cross-channel interaction, so Class V takes precedence.",
        )
    if "unstable" in stability or "non-minimum" in phase or "strong" in nonlinear or "higher" in rel_degree:
        if "operating-point-dependent" in nonlinear:
            features = ["local_static_gain", "local_time_constant", "gain_variation_ratio"]
            architecture = "local operating-region control with gain-scheduling review"
        elif "energy-exchange" in coupling:
            features = ["natural_frequency", "input_to_unactuated_coupling_gain"]
            architecture = "underactuated energy-exchange and capture route"
        elif "non-minimum" in phase and "stable" in stability and "unstable" not in stability:
            features = ["static_gain", "time_constant", "inverse_response_severity"]
            architecture = "NMP-aware conservative outer-loop control with undershoot-limited gain search"
        elif pendulum_like:
            features = ["natural_frequency"]
            architecture = "cascaded inner-outer control with safe online gain search"
        else:
            features = ["natural_frequency", "input_gain"]
            architecture = "cascaded inner-outer control with safe online gain search"
        if (
            "non-minimum" in phase
            and "operating-point-dependent" not in nonlinear
            and "energy-exchange" not in coupling
        ):
            architecture = "NMP-aware conservative outer-loop control with undershoot-limited gain search"
        if "moderate cascaded" in coupling:
            features = ["hover_thrust", "angular_acceleration_gain", "lateral_coupling_gain"]
        return ArchetypeClassification(
            primary_class=ArchetypeClass.CLASS_IV_HIGHER_ORDER_UNSTABLE_NONLINEAR_OR_NMP,
            control_architecture=architecture,
            required_core_features=features,
            safety_constraints=["start from the safest physical configuration", "use small reversible gain increments", "stop on overshoot, undershoot, saturation, or unsafe motion"],
            rationale="Unstable, nonlinear, or non-minimum-phase dominant behavior requires Class IV handling.",
        )
    if "drifting" in stability or "integrator" in rel_degree or "double" in rel_degree:
        return ArchetypeClassification(
            primary_class=ArchetypeClass.CLASS_III_DOUBLE_OR_PURE_INTEGRATOR,
            control_architecture="small saturated PD controller for marginally stable motion",
            required_core_features=["input_gain"],
            safety_constraints=["hard output saturation", "short pulse only inside travel bounds"],
            rationale="The dominant behavior lacks a restoring force and behaves like an integrator chain.",
        )
    if "oscillatory" in rel_degree or "oscillation" in diagnosis.open_loop_stability.evidence[0:1]:
        return ArchetypeClassification(
            primary_class=ArchetypeClass.CLASS_II_SECOND_ORDER_OSCILLATOR,
            control_architecture="low-bandwidth damping-enhancing PD controller",
            required_core_features=["natural_frequency", "damping_ratio", "input_gain"],
            safety_constraints=["free response must stay inside a small displacement range"],
            rationale="The dominant low-order behavior is a damped oscillatory mode.",
        )
    features = ["static_gain", "time_constant"]
    if diagnosis.significant_delay.assessment == DelayAssessment.SIGNIFICANT.value:
        features.append("dead_time")
    return ArchetypeClassification(
        primary_class=ArchetypeClass.CLASS_I_FIRST_ORDER_LAG,
        control_architecture="detuned PI controller for a self-regulating response",
        required_core_features=features,
        safety_constraints=["small step only", "stop if output exceeds operator bounds"],
        rationale="The dominant behavior settles toward a new steady value after a small input change.",
    )


class DiagnosticEngine:
    def __init__(
        self,
        adapter: DiagnosticAdapter | None = None,
        use_mechanism_cards: bool = False,
    ):
        self.adapter = adapter or DeterministicDiagnosticAdapter()
        self.use_mechanism_cards = use_mechanism_cards

    def diagnose(self, description: SystemDescription) -> StructuralDiagnosis:
        diagnosis = validate_agent_payload(self.adapter.diagnose(description))
        return enforce_shared_diagnostic_safety_rules(description, diagnosis)

    def classify(
        self,
        diagnosis: StructuralDiagnosis,
        description: SystemDescription | None = None,
        use_mechanism_cards: bool | None = None,
    ) -> ArchetypeClassification:
        classification = classify_archetype(diagnosis)
        enabled = self.use_mechanism_cards if use_mechanism_cards is None else use_mechanism_cards
        if not enabled:
            return classification

        from cfdc.diagnosis.mechanism_cards import supplement_with_mechanism_cards

        return supplement_with_mechanism_cards(description, diagnosis, classification)

    def run(self, description: SystemDescription) -> tuple[StructuralDiagnosis, ArchetypeClassification | None]:
        diagnosis = self.diagnose(description)
        if not diagnosis.complete:
            return diagnosis, None
        return diagnosis, self.classify(diagnosis, description)
