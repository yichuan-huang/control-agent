"""Revisioned, record-only diagnostic measurement sessions."""

from __future__ import annotations

import hashlib
from copy import deepcopy
from uuid import uuid4

from cfdc.diagnosis.engine import DiagnosticEngine
from cfdc.diagnosis.llm import DiagnosticAdapter
from cfdc.diagnosis.measurements import (
    build_diagnostic_checklist,
    build_measurement_plan,
    validate_measurement_assessment,
)
from cfdc.models import (
    DiagnosticSessionState,
    DiagnosticTurn,
    MeasurementAssessment,
    PlantEvidencePackage,
    StructuralDiagnosis,
    SystemDescription,
)


def clarification_question_id(question: str) -> str:
    return f"q_{hashlib.sha256(question.encode()).hexdigest()[:10]}"


def clarification_question_map(state: DiagnosticSessionState) -> dict[str, str]:
    """Retained for callers that render the description guidance as question IDs."""

    return {
        clarification_question_id(guidance.prompt): guidance.prompt
        for guidance in state.description_guidance
    }


def _expect_revision(state: DiagnosticSessionState, expected_revision: int) -> None:
    if expected_revision != state.revision:
        raise ValueError(
            f"stale diagnostic session revision {expected_revision}; current={state.revision}"
        )


def _transition(
    state: DiagnosticSessionState,
    *,
    updates: dict,
) -> DiagnosticSessionState:
    """Produce one validated copy-on-write revision of a diagnostic session."""

    payload = deepcopy(state.model_dump(mode="python"))
    payload.update(deepcopy(updates))
    payload["revision"] = state.revision + 1
    return DiagnosticSessionState.model_validate(payload)


def _diagnose(
    description: SystemDescription,
    diagnostic_adapter: DiagnosticAdapter | None,
    use_mechanism_cards: bool,
):
    return DiagnosticEngine(
        adapter=diagnostic_adapter, use_mechanism_cards=use_mechanism_cards
    ).diagnose(description)


def start_diagnostic_session(
    description: SystemDescription,
    *,
    route_id: str = "generic",
    diagnostic_adapter: DiagnosticAdapter | None = None,
    use_mechanism_cards: bool = False,
    diagnosis: StructuralDiagnosis | None = None,
) -> DiagnosticSessionState:
    """Create a v4 session without making a classification or profile selection."""

    resolved_diagnosis = diagnosis or _diagnose(
        description, diagnostic_adapter, use_mechanism_cards
    )
    checklist = build_diagnostic_checklist(description, resolved_diagnosis)
    return DiagnosticSessionState(
        session_id=f"diagnostic-{uuid4().hex[:16]}",
        route_id=route_id,
        initial_description=description,
        accumulated_description=description,
        current_diagnosis=resolved_diagnosis,
        description_guidance=[item.guidance for item in checklist],
        checklist=checklist,
        measurement_plan=build_measurement_plan(checklist),
        pending_clarification_questions=[],
        status="awaiting_measurements",
    )


def continue_description_session(
    state: DiagnosticSessionState,
    supplemental_description: str,
    *,
    expected_revision: int,
    diagnostic_adapter: DiagnosticAdapter | None = None,
    use_mechanism_cards: bool = False,
) -> DiagnosticSessionState:
    """Add a user-supplied description of existing records, at most eight times."""

    _expect_revision(state, expected_revision)
    if state.status not in {
        "collecting_description",
        "awaiting_measurements",
        "measurement_conflict",
    }:
        raise ValueError(
            "only a description or measurement-waiting session can continue"
        )
    text = supplemental_description.strip()
    if not text:
        raise ValueError("supplemental description must be non-empty")
    if state.description_turn_count >= state.maximum_turns:
        raise ValueError("maximum description turns already reached")

    evidence = f"Supplemental description: {text}"
    accumulated = state.accumulated_description.model_copy(
        update={"text": "\n\n".join([state.accumulated_description.text, evidence])}
    )
    diagnosis = _diagnose(accumulated, diagnostic_adapter, use_mechanism_cards)
    turn = DiagnosticTurn(
        turn_index=state.description_turn_count + 1,
        questions=["supplemental_description"],
        answers={"supplemental_description": text},
        evidence=[evidence],
        diagnosis=diagnosis,
    )
    checklist = build_diagnostic_checklist(accumulated, diagnosis)
    updates = {
        "accumulated_description": accumulated,
        "turns": [*state.turns, turn],
        "current_diagnosis": diagnosis,
        "description_guidance": [item.guidance for item in checklist],
        "checklist": checklist,
        "measurement_plan": build_measurement_plan(checklist),
        "description_turn_count": state.description_turn_count + 1,
        "measurement_assessment": None,
        "status": "awaiting_measurements",
        "refusal_reason": None,
    }
    if updates["description_turn_count"] >= state.maximum_turns:
        updates.update(
            {
                "status": "refused",
                "refusal_reason": "maximum_description_turns_reached",
            }
        )
    return _transition(state, updates=updates)


def continue_diagnostic_session(
    state: DiagnosticSessionState,
    answers: dict[str, str] | None = None,
    *,
    supplemental_description: str | None = None,
    expected_revision: int,
    diagnostic_adapter: DiagnosticAdapter | None = None,
    use_mechanism_cards: bool = False,
) -> DiagnosticSessionState:
    """Compatibility wrapper for description continuation in the v4 workflow."""

    answer_text = "\n".join(
        value.strip() for value in (answers or {}).values() if value.strip()
    )
    description = supplemental_description or answer_text
    if not (description or "").strip():
        raise ValueError(
            "provide a supplemental description of an existing record or manual report"
        )
    return continue_description_session(
        state,
        description,
        expected_revision=expected_revision,
        diagnostic_adapter=diagnostic_adapter,
        use_mechanism_cards=use_mechanism_cards,
    )


def submit_measurement_assessment(
    state: DiagnosticSessionState,
    assessment: MeasurementAssessment | dict,
    *,
    expected_revision: int,
) -> DiagnosticSessionState:
    """Apply a structured adapter assessment after deterministic plan validation."""

    _expect_revision(state, expected_revision)
    if state.status not in {"awaiting_measurements", "measurement_conflict"}:
        raise ValueError(
            "only a measurement-waiting session accepts a measurement assessment"
        )
    if state.measurement_round_count >= state.maximum_turns:
        raise ValueError("maximum measurement rounds already reached")
    if state.measurement_plan is None:
        raise ValueError("diagnostic session is missing its measurement plan")
    typed_assessment = MeasurementAssessment.model_validate(assessment)
    validate_measurement_assessment(state.measurement_plan, typed_assessment)
    round_count = state.measurement_round_count + 1
    updates = {
        "measurement_assessment": typed_assessment,
        "measurement_history": [*state.measurement_history, typed_assessment],
        "measurement_round_count": round_count,
        "evidence_level": "description_only",
        "status": "measurement_conflict"
        if typed_assessment.status == "conflict"
        else "awaiting_measurements",
        "refusal_reason": None,
    }
    if typed_assessment.status == "ready":
        updates.update(
            {
                "evidence_level": "measurement_verified",
                "status": "measurement_verified",
            }
        )
    elif round_count >= state.maximum_turns:
        updates.update(
            {
                "status": "refused",
                "refusal_reason": "maximum_measurement_rounds_reached",
            }
        )
    return _transition(state, updates=updates)


def submit_measurements_to_session(
    state: DiagnosticSessionState,
    assessment: MeasurementAssessment | dict,
    *,
    expected_revision: int,
) -> DiagnosticSessionState:
    """Plural alias used by adapters submitting one structured assessment."""

    return submit_measurement_assessment(
        state, assessment, expected_revision=expected_revision
    )


def submit_evidence_to_session(
    state: DiagnosticSessionState,
    package: PlantEvidencePackage,
) -> DiagnosticSessionState:
    """The v4 guided workflow accepts only its typed record assessment at this stage."""

    del state, package
    raise ValueError(
        "v4 diagnostic sessions require a measurement assessment before evidence submission"
    )


def submit_specifications_to_session(*args, **kwargs):
    """Specification collection is unavailable before the measurement gate releases it."""

    del args, kwargs
    raise ValueError(
        "v4 diagnostic sessions require measurement verification before specifications"
    )


def migrate_diagnostic_session_payload(payload: dict) -> DiagnosticSessionState:
    """Accept v4 payloads and explicitly refuse unsafe v3 persisted sessions."""

    version = payload.get("schema_version")
    if version == "3.0":
        raise ValueError(
            "v3 diagnostic session payloads are not supported; start a v4 session"
        )
    if version == "4.0":
        return DiagnosticSessionState.model_validate(payload)
    if version in {"1.0", "2.0", None}:
        description = SystemDescription.model_validate(
            payload.get("initial_description") or payload.get("accumulated_description")
        )
        return start_diagnostic_session(
            description,
            route_id=payload.get("route_id", "generic"),
        )
    raise ValueError(f"unsupported diagnostic session schema version: {version}")
