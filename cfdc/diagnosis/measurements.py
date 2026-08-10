"""Record-only guidance and deterministic validation for diagnostic measurements."""

from __future__ import annotations

from cfdc.models import (
    DescriptionGuidance,
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
