"""Record-only guidance and deterministic validation for diagnostic measurements."""

from __future__ import annotations

import re

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
        raise ValueError(
            "measurement plans require the fixed eight-field diagnostic checklist"
        )
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


def _normalize_whitespace(value: str) -> str:
    return " ".join(value.split())


_NUMBER_TOKEN = re.compile(
    r"(?<![\w.])[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?(?![\w.])"
)


def _contains_unit_token(excerpt: str, unit: str) -> bool:
    normalized_excerpt = _normalize_whitespace(excerpt)
    normalized_unit = _normalize_whitespace(unit)
    prefix = r"(?<!\w)" if normalized_unit[0].isalnum() else ""
    suffix = r"(?!\w)" if normalized_unit[-1].isalnum() else ""
    return (
        re.search(
            prefix + re.escape(normalized_unit) + suffix,
            normalized_excerpt,
        )
        is not None
    )


def validate_grounded_measurement_assessment(
    plan: MeasurementPlan,
    assessment: MeasurementAssessment,
    raw_response: str,
    *,
    previous_assessment: MeasurementAssessment | None = None,
) -> None:
    """Fail closed unless every new claim is attested by the current response."""

    validate_measurement_assessment(plan, assessment)
    if not isinstance(raw_response, str):
        raise ValueError(  # noqa: TRY004 - public validation contract
            "raw measurement response must be a string"
        )
    normalized_response = _normalize_whitespace(raw_response)
    if not normalized_response:
        raise ValueError("raw measurement response must be non-empty")
    previous_by_request = {}
    if previous_assessment is not None:
        validate_measurement_assessment(plan, previous_assessment)
        previous_by_request = {
            fact.request_id: fact for fact in previous_assessment.facts
        }

    for fact in assessment.facts:
        if previous_by_request.get(fact.request_id) == fact:
            continue
        normalized_excerpt = _normalize_whitespace(fact.source_excerpt)
        if normalized_excerpt not in normalized_response:
            raise ValueError(
                f"measurement source_excerpt for {fact.request_id} is not grounded "
                "in the current raw response"
            )
        if fact.text_value is not None:
            normalized_text = _normalize_whitespace(fact.text_value)
            if (
                normalized_text not in normalized_excerpt
                and normalized_text not in normalized_response
            ):
                raise ValueError(
                    f"measurement text_value for {fact.request_id} is not grounded "
                    "in the current raw response"
                )
        if fact.numeric_value is not None:
            attested_values = [
                float(match.group(0))
                for match in _NUMBER_TOKEN.finditer(normalized_excerpt)
            ]
            if fact.numeric_value not in attested_values:
                raise ValueError(
                    f"measurement numeric_value for {fact.request_id} is not "
                    "attested in source_excerpt"
                )
            if not _contains_unit_token(normalized_excerpt, fact.unit or ""):
                raise ValueError(
                    f"measurement unit for {fact.request_id} is not attested in "
                    "source_excerpt"
                )

    for conflict in assessment.conflicts:
        if _normalize_whitespace(conflict) not in normalized_response:
            raise ValueError(
                "measurement conflict is not grounded in the current raw response"
            )


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
        raise ValueError(
            "phrased measurement plan must preserve deterministic rationale"
        )
    return phrased


def apply_description_guidance(
    description: SystemDescription,
    payload: DescriptionGuidanceAssessment | dict,
    expected_guidance: list[DescriptionGuidance],
) -> tuple[SystemDescription, list[DescriptionGuidance]]:
    """Validate strict guidance and verbatim signal provenance."""

    assessment = DescriptionGuidanceAssessment.model_validate(payload)
    normalized_guidance = [
        item.model_copy(update={"response": "unknown"}) for item in assessment.guidance
    ]
    normalized_expected = [
        item.model_copy(update={"response": "unknown"}) for item in expected_guidance
    ]
    if normalized_guidance != normalized_expected:
        raise ValueError(
            "adapter guidance must exactly preserve deterministic safe guidance"
        )
    for item in assessment.guidance:
        if (
            item.response.casefold() != "unknown"
            and item.response not in description.text
        ):
            raise ValueError(
                "description guidance response must appear verbatim in the original description"
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


def apply_guidance_responses_to_checklist(
    checklist: list[DiagnosticChecklistItem],
    guidance: list[DescriptionGuidance],
    description_text: str,
) -> list[DiagnosticChecklistItem]:
    """Use only grounded LLM excerpts to mark description checklist progress."""

    if len(checklist) != len(guidance):
        raise ValueError("description guidance must match the fixed checklist length")
    result = []
    for item, guided in zip(checklist, guidance, strict=True):
        if item.diagnostic_field_id != guided.diagnostic_field_id:
            raise ValueError("description guidance must match checklist field order")
        response = guided.response.strip()
        if response.casefold() == "unknown":
            result.append(
                item.model_copy(
                    update={
                        "status": "unknown",
                        "evidence": [],
                        "guidance": guided,
                    }
                )
            )
            continue
        if response not in description_text:
            raise ValueError(
                "description guidance response must appear verbatim in the original description"
            )
        result.append(
            item.model_copy(
                update={
                    "status": "inferred",
                    "evidence": [response],
                    "guidance": guided,
                }
            )
        )
    return result


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
        isolated = infer_structural_diagnosis(SystemDescription(text="\n".join(parts)))
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
