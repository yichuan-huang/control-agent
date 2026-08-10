"""Record-only guidance and deterministic validation for diagnostic measurements."""

from __future__ import annotations

from cfdc.models import (
    DescriptionGuidance,
    DescriptionGuidanceAssessment,
    DiagnosticChecklistItem,
    MeasurementAssessment,
    MeasurementPlan,
    MeasurementRequest,
    StructuralDiagnosis,
    SystemDescription,
)
from cfdc.models.schemas import validate_measurement_assessment_for_plan

DIAGNOSTIC_FIELD_IDS = (
    "open_loop_stability",
    "minimum_phase",
    "significant_delay",
    "relative_degree",
    "controllability_observability",
    "nonlinearity_strength",
    "coupling_severity",
    "uncertainty_magnitude",
)

_FIELD_DETAILS = {
    "open_loop_stability": (
        "Open-loop stability",
        "whether the unforced recorded output settles, grows, or is unavailable",
        None,
    ),
    "minimum_phase": (
        "Minimum-phase behavior",
        "whether an existing response record initially moves opposite to its eventual direction",
        None,
    ),
    "significant_delay": (
        "Significant delay",
        "the delay already reported between an input record and its observed output response",
        "s",
    ),
    "relative_degree": (
        "Relative degree",
        "the earliest response shape already reported in an input/output record",
        None,
    ),
    "controllability_observability": (
        "Controllability and observability",
        "whether existing records or a manual report identify an input that affects each reported output",
        None,
    ),
    "nonlinearity_strength": (
        "Nonlinearity strength",
        "whether existing records report materially different behavior across operating conditions",
        None,
    ),
    "coupling_severity": (
        "Coupling severity",
        "whether existing records or a manual report show one input affecting multiple outputs",
        None,
    ),
    "uncertainty_magnitude": (
        "Uncertainty magnitude",
        "the repeatability or uncertainty already reported in existing records or a manual report",
        None,
    ),
}


def _guidance(field_id: str) -> DescriptionGuidance:
    title, detail, _ = _FIELD_DETAILS[field_id]
    return DescriptionGuidance(
        diagnostic_field_id=field_id,
        prompt=(
            f"For {title}, review an existing record or manual report and describe "
            f"{detail}. If no such record exists, say unknown."
        ),
        why_needed=f"This keeps the {title.lower()} diagnostic field evidence-backed.",
    )


def build_diagnostic_checklist(
    description: SystemDescription,
    diagnosis: StructuralDiagnosis | None = None,
) -> list[DiagnosticChecklistItem]:
    """Build the fixed, auditable eight-field checklist without classifying a plant."""

    by_id = {}
    if diagnosis is not None:
        by_id = dict(zip(DIAGNOSTIC_FIELD_IDS, diagnosis.fields, strict=True))
    items: list[DiagnosticChecklistItem] = []
    for field_id in DIAGNOSTIC_FIELD_IDS:
        title, _, _ = _FIELD_DETAILS[field_id]
        field = by_id.get(field_id)
        items.append(
            DiagnosticChecklistItem(
                diagnostic_field_id=field_id,
                label=title,
                status=field.status if field is not None else "unknown",
                evidence=list(field.evidence) if field is not None else [],
                guidance=_guidance(field_id),
            )
        )
    return items


def build_measurement_plan(
    checklist: list[DiagnosticChecklistItem],
) -> MeasurementPlan:
    """Request only excerpts and values already present in records or manuals."""

    if [item.diagnostic_field_id for item in checklist] != list(DIAGNOSTIC_FIELD_IDS):
        raise ValueError("measurement plans require the fixed eight-field diagnostic checklist")
    requests = []
    for item in checklist:
        _, _, unit_hint = _FIELD_DETAILS[item.diagnostic_field_id]
        requests.append(
            MeasurementRequest(
                request_id=item.diagnostic_field_id,
                diagnostic_field_id=item.diagnostic_field_id,
                title=item.label,
                safety_scope="existing_records_only",
                instruction="Review an existing record.",
                source_hint="Review an existing record.",
                report_template="Report the source excerpt and recorded observation.",
                response_hint="Report the source excerpt and recorded observation.",
                unit_hint=unit_hint,
            )
        )
    return MeasurementPlan(
        requests=requests,
        rationale=(
            "The plan collects only existing-record or manual-report evidence; it does "
            "not ask for a new physical action."
        ),
    )


def validate_measurement_assessment(
    plan: MeasurementPlan,
    assessment: MeasurementAssessment,
) -> None:
    """Check adapter output against the active plan before a state transition."""

    validate_measurement_assessment_for_plan(plan, assessment)


def validate_phrased_measurement_plan(
    base_plan: MeasurementPlan,
    candidate: MeasurementPlan | dict,
) -> MeasurementPlan:
    """Allow safe phrasing changes without allowing the LLM to replace the plan."""

    phrased = MeasurementPlan.model_validate(candidate)
    if len(phrased.requests) != len(base_plan.requests):
        raise ValueError("phrased measurement plan must preserve all fixed requests")
    identity_fields = (
        "request_id",
        "diagnostic_field_id",
        "title",
        "safety_scope",
        "unit_hint",
    )
    for index, (expected, actual) in enumerate(
        zip(base_plan.requests, phrased.requests, strict=True)
    ):
        for field_name in identity_fields:
            if getattr(actual, field_name) != getattr(expected, field_name):
                raise ValueError(
                    "phrased measurement plan changed authoritative request "
                    f"{index} field {field_name}"
                )
    if phrased.rationale != base_plan.rationale:
        raise ValueError("phrased measurement plan must preserve deterministic rationale")
    return phrased


def apply_description_guidance(
    description: SystemDescription,
    payload: DescriptionGuidanceAssessment | dict,
    expected_guidance: list[DescriptionGuidance],
) -> tuple[SystemDescription, list[DescriptionGuidance]]:
    """Validate strict guidance and verbatim signal provenance."""

    assessment = DescriptionGuidanceAssessment.model_validate(payload)
    if assessment.guidance != expected_guidance:
        raise ValueError(
            "adapter guidance must exactly preserve deterministic safe guidance"
        )
    for item in [*assessment.observed_outputs, *assessment.actuators]:
        if item.source_excerpt not in description.text:
            raise ValueError(
                "description signal source_excerpt must appear verbatim in the original description"
            )

    def merged(existing: list[str], extracted) -> list[str]:
        result = list(existing)
        for item in extracted:
            if item.name not in result:
                result.append(item.name)
        return result

    updated = description.model_copy(
        update={
            "observed_outputs": merged(
                description.observed_outputs, assessment.observed_outputs
            ),
            "actuators": merged(description.actuators, assessment.actuators),
        }
    )
    return updated, assessment.guidance


def render_measurement_evidence(
    assessments: list[MeasurementAssessment],
) -> str:
    """Render validated facts deterministically without retaining raw responses."""

    lines = ["Validated diagnostic measurement evidence:"]
    for round_index, assessment in enumerate(assessments, start=1):
        for fact in assessment.facts:
            value = (
                f"numeric_value={fact.numeric_value:.17g}; unit={fact.unit}"
                if fact.numeric_value is not None
                else f"text_value={fact.text_value}"
            )
            lines.extend(
                [
                    f"round={round_index}; request_id={fact.request_id}; {value}",
                    "source_excerpt:",
                    fact.source_excerpt,
                ]
            )
    return "\n".join(lines)


def reduce_measurement_history_to_diagnosis(
    plan: MeasurementPlan,
    assessments: list[MeasurementAssessment],
) -> StructuralDiagnosis:
    """Resolve each structural field only from its own latest validated outcome."""

    request_by_id = {request.request_id: request for request in plan.requests}
    if len(request_by_id) != len(DIAGNOSTIC_FIELD_IDS):
        raise ValueError("typed measurement reduction requires exactly eight requests")
    if {request.diagnostic_field_id for request in plan.requests} != set(
        DIAGNOSTIC_FIELD_IDS
    ):
        raise ValueError(
            "typed measurement reduction requires one request per diagnostic field"
        )

    latest_fact_by_request = dict.fromkeys(request_by_id)
    for assessment in assessments:
        validate_measurement_assessment(plan, assessment)
        fact_by_request = {fact.request_id: fact for fact in assessment.facts}
        for request_id, request in request_by_id.items():
            if request_id in fact_by_request:
                latest_fact_by_request[request_id] = fact_by_request[request_id]
            elif (
                request.diagnostic_field_id in assessment.gaps
                or request_id in assessment.conflict_request_ids
            ):
                latest_fact_by_request[request_id] = None

    from cfdc.diagnosis.engine import infer_structural_diagnosis

    resolved_fields = {}
    for request_id, request in request_by_id.items():
        fact = latest_fact_by_request[request_id]
        parts = ["No validated evidence is available for this field."]
        if fact is not None:
            parts = [fact.source_excerpt]
            if fact.text_value is not None:
                parts.append(fact.text_value)
            if fact.numeric_value is not None:
                parts.append(f"{fact.numeric_value:.17g} {fact.unit}")
        isolated = infer_structural_diagnosis(
            SystemDescription(text="\n".join(parts))
        )
        resolved_fields[request.diagnostic_field_id] = getattr(
            isolated, request.diagnostic_field_id
        )

    complete = all(field.status != "unknown" for field in resolved_fields.values())
    questions = []
    if not complete:
        questions = [
            f"Provide validated existing-record evidence for {field_id}."
            for field_id in DIAGNOSTIC_FIELD_IDS
            if resolved_fields[field_id].status == "unknown"
        ][:4]
        while len(questions) < 2:
            questions.append(
                "Provide another field-specific existing-record observation."
            )
    return StructuralDiagnosis(
        **resolved_fields,
        clarification_questions=questions,
        complete=complete,
    )
