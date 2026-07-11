from __future__ import annotations

from collections.abc import Iterable

from cfdc.diagnosis.llm import DiagnosticAdapter, DeterministicDiagnosticAdapter, validate_agent_payload
from cfdc.models import (
    ArchetypeClass,
    ArchetypeClassification,
    ControllabilityObservabilityAssessment,
    ControllabilityObservabilityField,
    CouplingAssessment,
    CouplingField,
    DelayAssessment,
    NonlinearityAssessment,
    NonlinearityField,
    PhaseAssessment,
    PhaseField,
    RelativeDegreeAssessment,
    RelativeDegreeField,
    SignificantDelayField,
    StabilityAssessment,
    StabilityField,
    StructuralDiagnosis,
    SystemDescription,
    UncertaintyAssessment,
    UncertaintyField,
)


def _contains(text: str, terms: Iterable[str]) -> bool:
    return any(term in text for term in terms)


def _question_pool(description: SystemDescription, diagnosis: StructuralDiagnosis) -> list[str]:
    questions: list[str] = []
    if not description.observed_outputs:
        questions.append("Which quantities can you watch or record during motion?")
    if not description.actuators:
        questions.append("What physical action or device can change the system?")
    if diagnosis.minimum_phase.assessment == PhaseAssessment.UNKNOWN.value:
        questions.append("After a small change, does the output first move the expected way or briefly the opposite way?")
    if diagnosis.significant_delay.assessment == DelayAssessment.UNKNOWN.value:
        questions.append("After a small change, is there a noticeable pause before anything moves?")
    if diagnosis.coupling_severity.assessment == CouplingAssessment.UNKNOWN.value:
        questions.append("Does one input strongly move more than one measured output?")
    if diagnosis.uncertainty_magnitude.assessment == UncertaintyAssessment.UNKNOWN.value:
        questions.append("Do load, wear, or operating conditions change the behavior noticeably?")
    return questions[:4]


def _status(assessment: str) -> str:
    return "unknown" if assessment == "unknown" else "inferred"


def infer_structural_diagnosis(description: SystemDescription) -> StructuralDiagnosis:
    """Deterministic fixture adapter for tests and registered benchmark descriptions."""

    text = description.text.lower()
    pendulum = _contains(text, ["pendulum", "rod", "cart-pole", "cartpole"])
    underactuated = pendulum or _contains(text, ["acrobot", "unactuated link", "unactuated joint", "only one actuated joint"])
    vtol = _contains(text, ["vtol", "vertical take", "two rotors", "hover", "aircraft"])
    oscillator = _contains(text, ["oscillat", "vibrat", "reson", "spring", "natural frequency"])
    first_order = _contains(text, ["first-order", "first order", "temperature", "tank", "lag", "self-regulating", "settles"])
    integrator = _contains(text, ["integrator", "drift", "low-friction", "position keeps moving"])
    mimo = _contains(text, ["mimo", "multi-input", "multiple inputs", "multiple outputs", "strongly coupled", "two pump inputs", "both controlled lower levels", "interconnected tank levels"])
    operating_dependent = _contains(text, ["operating point", "operating points", "vary strongly with temperature", "vary strongly with conversion", "gain and time constant vary"])
    nmp = _contains(text, ["reverse", "opposite", "undershoot", "non-minimum", "nonminimum", "unfavorable motion"]) or underactuated or vtol
    delay_unknown = _contains(text, ["timing has not been observed", "delay is unknown", "unknown delay", "dead time is unknown"])

    stability = (
        StabilityAssessment.UNSTABLE
        if underactuated or vtol or _contains(text, ["unstable", "falls over", "diverge", "upright"])
        else StabilityAssessment.MARGINAL
        if integrator
        else StabilityAssessment.STABLE
        if first_order or oscillator or mimo or operating_dependent or _contains(text, ["settle", "returns", "decay"])
        else StabilityAssessment.UNKNOWN
    )
    phase = PhaseAssessment.NONMINIMUM_PHASE if nmp else PhaseAssessment.MINIMUM_PHASE if first_order or oscillator or integrator or mimo or operating_dependent else PhaseAssessment.UNKNOWN
    delay = DelayAssessment.UNKNOWN if delay_unknown else DelayAssessment.SIGNIFICANT if _contains(text, ["dead time", "delay", "transport", "noticeable pause"]) else DelayAssessment.NOT_SIGNIFICANT if underactuated or vtol or first_order or oscillator or integrator or mimo or operating_dependent else DelayAssessment.UNKNOWN
    degree = RelativeDegreeAssessment.HIGH if underactuated or vtol or operating_dependent or _contains(text, ["higher order", "high relative degree"]) else RelativeDegreeAssessment.LOW if first_order or oscillator or integrator or mimo else RelativeDegreeAssessment.UNKNOWN
    co = ControllabilityObservabilityAssessment.ADEQUATE if description.observed_outputs and description.actuators else ControllabilityObservabilityAssessment.UNKNOWN
    nonlinear = NonlinearityAssessment.STRONG_DYNAMIC if underactuated or operating_dependent or _contains(text, ["large angle", "limit cycle", "state-dependent"]) else NonlinearityAssessment.STATIC_COMPENSABLE if _contains(text, ["hysteresis", "dead zone", "deadzone", "backlash"]) else NonlinearityAssessment.WEAK if vtol or first_order or oscillator or integrator or mimo else NonlinearityAssessment.UNKNOWN
    coupling = CouplingAssessment.SEVERE_MIMO if mimo else CouplingAssessment.CASCADED if vtol else CouplingAssessment.UNDERACTUATED if underactuated else CouplingAssessment.WEAK_MIMO if operating_dependent and len(description.actuators) > 1 else CouplingAssessment.SISO if first_order or oscillator or integrator else CouplingAssessment.UNKNOWN
    uncertainty = UncertaintyAssessment.LARGE if underactuated or vtol or operating_dependent or mimo or _contains(text, ["unknown parameters", "payload", "wear", "varies", "load change"]) else UncertaintyAssessment.MODERATE if first_order or oscillator or integrator else UncertaintyAssessment.UNKNOWN

    def evidence(resolved: bool, message: str) -> list[str]:
        return [message] if resolved else []

    diagnosis = StructuralDiagnosis(
        open_loop_stability=StabilityField(status=_status(stability.value), value="deterministic benchmark inference", assessment=stability, confidence=0.8 if stability != StabilityAssessment.UNKNOWN else 0.2, evidence=evidence(stability != StabilityAssessment.UNKNOWN, "observable settling, drift, or divergence pattern")),
        minimum_phase=PhaseField(status=_status(phase.value), value="deterministic benchmark inference", assessment=phase, confidence=0.75 if phase != PhaseAssessment.UNKNOWN else 0.2, evidence=evidence(phase != PhaseAssessment.UNKNOWN, "reported initial motion direction and actuation geometry")),
        significant_delay=SignificantDelayField(status=_status(delay.value), value="deterministic benchmark inference", assessment=delay, confidence=0.72 if delay != DelayAssessment.UNKNOWN else 0.2, evidence=evidence(delay != DelayAssessment.UNKNOWN, "reported response timing")),
        relative_degree=RelativeDegreeField(status=_status(degree.value), value="deterministic benchmark inference", assessment=degree, estimated_order=(4 if vtol or operating_dependent else 2 if underactuated or oscillator or integrator or mimo else 1 if first_order else None), confidence=0.75 if degree != RelativeDegreeAssessment.UNKNOWN else 0.2, evidence=evidence(degree != RelativeDegreeAssessment.UNKNOWN, "input-to-output motion chain")),
        controllability_observability=ControllabilityObservabilityField(status=_status(co.value), value="deterministic benchmark inference", assessment=co, confidence=0.72 if co != ControllabilityObservabilityAssessment.UNKNOWN else 0.2, evidence=evidence(co != ControllabilityObservabilityAssessment.UNKNOWN, "declared measured outputs and actuators")),
        nonlinearity_strength=NonlinearityField(status=_status(nonlinear.value), value="deterministic benchmark inference", assessment=nonlinear, confidence=0.72 if nonlinear != NonlinearityAssessment.UNKNOWN else 0.2, evidence=evidence(nonlinear != NonlinearityAssessment.UNKNOWN, "reported operating geometry and nonlinear effects")),
        coupling_severity=CouplingField(status=_status(coupling.value), value="deterministic benchmark inference", assessment=coupling, confidence=0.75 if coupling != CouplingAssessment.UNKNOWN else 0.2, evidence=evidence(coupling != CouplingAssessment.UNKNOWN, "declared input-output interaction pattern")),
        uncertainty_magnitude=UncertaintyField(status=_status(uncertainty.value), value="deterministic benchmark inference", assessment=uncertainty, confidence=0.7 if uncertainty != UncertaintyAssessment.UNKNOWN else 0.2, evidence=evidence(uncertainty != UncertaintyAssessment.UNKNOWN, "reported parameter or load variability")),
        clarification_questions=["placeholder", "placeholder"],
        complete=False,
    )
    complete = all(field.status != "unknown" for field in diagnosis.fields)
    questions = [] if complete else _question_pool(description, diagnosis)
    if not complete:
        while len(questions) < 2:
            questions.append("What safe motion can be observed after the smallest input change?")
    return diagnosis.model_copy(update={"complete": complete, "clarification_questions": questions[:4]})


def classify_archetype(diagnosis: StructuralDiagnosis) -> ArchetypeClassification:
    """Classify from normalized assessments only; explanatory text is never inspected."""

    stability = diagnosis.open_loop_stability.assessment
    phase = diagnosis.minimum_phase.assessment
    degree = diagnosis.relative_degree.assessment
    nonlinear = diagnosis.nonlinearity_strength.assessment
    coupling = diagnosis.coupling_severity.assessment

    if coupling == CouplingAssessment.SEVERE_MIMO.value:
        return ArchetypeClassification(primary_class=ArchetypeClass.CLASS_V_MULTIVARIABLE_SIGNIFICANT_COUPLING, control_architecture="conservative decentralized MIMO control with half-strength static decoupling", required_core_features=["local_gain_matrix", "local_time_constant", "pairing_indicator"], safety_constraints=["bound each input separately", "freeze on unexpected cross-channel motion"], rationale="The normalized diagnosis reports severe multivariable coupling.")
    if stability == StabilityAssessment.UNSTABLE.value or phase == PhaseAssessment.NONMINIMUM_PHASE.value or degree == RelativeDegreeAssessment.HIGH.value or nonlinear == NonlinearityAssessment.STRONG_DYNAMIC.value or coupling in {CouplingAssessment.UNDERACTUATED.value, CouplingAssessment.CASCADED.value}:
        return ArchetypeClassification(primary_class=ArchetypeClass.CLASS_IV_HIGHER_ORDER_UNSTABLE_NONLINEAR_OR_NMP, control_architecture="profile-selected cascaded or nonlinear conservative control", required_core_features=["natural_frequency", "input_gain"], safety_constraints=["start from the safest simulated configuration", "use reversible five-percent gain increments", "rollback on structural or safety limits"], rationale="At least one normalized Class IV condition is present.")
    if stability == StabilityAssessment.MARGINAL.value:
        return ArchetypeClassification(primary_class=ArchetypeClass.CLASS_III_DOUBLE_OR_PURE_INTEGRATOR, control_architecture="small saturated PD controller", required_core_features=["input_gain"], safety_constraints=["hard output saturation", "short bounded pulse"], rationale="The normalized diagnosis reports marginal non-restoring dynamics.")
    if diagnosis.relative_degree.estimated_order == 2:
        return ArchetypeClassification(primary_class=ArchetypeClass.CLASS_II_SECOND_ORDER_OSCILLATOR, control_architecture="low-bandwidth damping-enhancing PD controller", required_core_features=["natural_frequency", "damping_ratio", "input_gain"], safety_constraints=["free response stays in the normalized safe range"], rationale="A stable second-order dominant mode is diagnosed.")
    features = ["static_gain", "time_constant"]
    if diagnosis.significant_delay.assessment == DelayAssessment.SIGNIFICANT.value:
        features.append("dead_time")
    return ArchetypeClassification(primary_class=ArchetypeClass.CLASS_I_FIRST_ORDER_LAG, control_architecture="detuned PI controller", required_core_features=features, safety_constraints=["small normalized step", "stop at the configured output bound"], rationale="The remaining normalized signature is a stable first-order dominant response.")


class DiagnosticEngine:
    def __init__(self, adapter: DiagnosticAdapter | None = None, use_mechanism_cards: bool = False):
        self.adapter = adapter or DeterministicDiagnosticAdapter()
        self.use_mechanism_cards = use_mechanism_cards

    def diagnose(self, description: SystemDescription) -> StructuralDiagnosis:
        return validate_agent_payload(self.adapter.diagnose(description))

    def classify(self, diagnosis: StructuralDiagnosis, description: SystemDescription | None = None, use_mechanism_cards: bool | None = None) -> ArchetypeClassification:
        classification = classify_archetype(diagnosis)
        enabled = self.use_mechanism_cards if use_mechanism_cards is None else use_mechanism_cards
        if not enabled:
            return classification
        from cfdc.diagnosis.mechanism_cards import supplement_with_mechanism_cards
        return supplement_with_mechanism_cards(description, diagnosis, classification)

    def run(self, description: SystemDescription) -> tuple[StructuralDiagnosis, ArchetypeClassification | None]:
        diagnosis = self.diagnose(description)
        return diagnosis, self.classify(diagnosis, description) if diagnosis.complete else None
