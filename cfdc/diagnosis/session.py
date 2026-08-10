"""Revisioned, record-only diagnostic measurement sessions."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from copy import deepcopy
from uuid import uuid4

from cfdc.diagnosis.engine import DiagnosticEngine
from cfdc.diagnosis.llm import DiagnosticAdapter
from cfdc.diagnosis.measurements import (
    apply_description_guidance,
    apply_guidance_responses_to_checklist,
    build_diagnostic_checklist,
    build_measurement_plan,
    reduce_measurement_history_to_diagnosis,
    render_measurement_evidence,
    validate_grounded_measurement_assessment,
    validate_phrased_measurement_plan,
)
from cfdc.evidence import plant_id_for_description, validate_evidence_package
from cfdc.models import (
    DiagnosticSessionState,
    DiagnosticTurn,
    MeasurementAssessment,
    PlantEvidencePackage,
    SimulationBoundaryConfirmation,
    StructuralDiagnosis,
    SystemDescription,
)
from cfdc.specifications import (
    assess_specification_text,
    compile_specification_model,
    specification_template_for_profile,
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

    guided = diagnostic_adapter is not None and hasattr(
        diagnostic_adapter, "guide_description"
    )
    accumulated_description = description
    if guided:
        preliminary_diagnosis = DiagnosticEngine(
            adapter=None, use_mechanism_cards=use_mechanism_cards
        ).diagnose(description)
        preliminary_checklist = build_diagnostic_checklist(
            description, preliminary_diagnosis
        )
        accumulated_description, guided_items = apply_description_guidance(
            description,
            diagnostic_adapter.guide_description(
                description, [item.guidance for item in preliminary_checklist]
            ),
            [item.guidance for item in preliminary_checklist],
        )
        resolved_diagnosis = DiagnosticEngine(
            adapter=None, use_mechanism_cards=use_mechanism_cards
        ).diagnose(accumulated_description)
        checklist = build_diagnostic_checklist(
            accumulated_description, resolved_diagnosis
        )
        checklist = apply_guidance_responses_to_checklist(
            checklist,
            guided_items,
            accumulated_description.text,
        )
    else:
        resolved_diagnosis = diagnosis or _diagnose(
            description, diagnostic_adapter, use_mechanism_cards
        )
        checklist = build_diagnostic_checklist(description, resolved_diagnosis)
    measurement_plan = build_measurement_plan(checklist)
    if diagnostic_adapter is not None and hasattr(
        diagnostic_adapter, "phrase_measurement_plan"
    ):
        measurement_plan = validate_phrased_measurement_plan(
            measurement_plan,
            diagnostic_adapter.phrase_measurement_plan(
                accumulated_description, checklist, measurement_plan
            ),
        )
    return DiagnosticSessionState(
        session_id=f"diagnostic-{uuid4().hex[:16]}",
        route_id=route_id,
        initial_description=description,
        accumulated_description=accumulated_description,
        current_diagnosis=resolved_diagnosis,
        description_guidance=[item.guidance for item in checklist],
        checklist=checklist,
        measurement_plan=measurement_plan,
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
        "measurement_needs_more",
        "measurement_conflict",
        "awaiting_profile_measurements",
        "specification_conflict",
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
    text_parts = [state.initial_description.text]
    for turn in state.turns:
        prior_supplement = turn.answers.get("supplemental_description")
        if isinstance(prior_supplement, str) and prior_supplement.strip():
            text_parts.append(
                f"Supplemental description: {prior_supplement.strip()}"
            )
    text_parts.append(evidence)
    accumulated = state.accumulated_description.model_copy(
        update={"text": "\n\n".join(text_parts)}
    )
    guided = diagnostic_adapter is not None and hasattr(
        diagnostic_adapter, "guide_description"
    )
    if guided:
        preliminary = DiagnosticEngine(
            adapter=None, use_mechanism_cards=use_mechanism_cards
        ).diagnose(accumulated)
        preliminary_checklist = build_diagnostic_checklist(accumulated, preliminary)
        accumulated, guided_items = apply_description_guidance(
            accumulated,
            diagnostic_adapter.guide_description(
                accumulated, [item.guidance for item in preliminary_checklist]
            ),
            [item.guidance for item in preliminary_checklist],
        )
        diagnosis = DiagnosticEngine(
            adapter=None, use_mechanism_cards=use_mechanism_cards
        ).diagnose(accumulated)
    else:
        diagnosis = _diagnose(accumulated, diagnostic_adapter, use_mechanism_cards)
    turn = DiagnosticTurn(
        turn_index=state.description_turn_count + 1,
        questions=["supplemental_description"],
        answers={"supplemental_description": text},
        evidence=[evidence],
        diagnosis=diagnosis,
    )
    checklist = build_diagnostic_checklist(accumulated, diagnosis)
    if guided:
        checklist = apply_guidance_responses_to_checklist(
            checklist,
            guided_items,
            accumulated.text,
        )
    measurement_plan = build_measurement_plan(checklist)
    if diagnostic_adapter is not None and hasattr(
        diagnostic_adapter, "phrase_measurement_plan"
    ):
        measurement_plan = validate_phrased_measurement_plan(
            measurement_plan,
            diagnostic_adapter.phrase_measurement_plan(
                accumulated, checklist, measurement_plan
            ),
        )
    updates = {
        "accumulated_description": accumulated,
        "turns": [*state.turns, turn],
        "current_diagnosis": diagnosis,
        "description_guidance": [item.guidance for item in checklist],
        "checklist": checklist,
        "measurement_plan": measurement_plan,
        "description_turn_count": state.description_turn_count + 1,
        "measurement_assessment": None,
        "measurement_history": [],
        "measurement_response_history": [],
        "measurement_round_count": 0,
        "profile_measurement_round_count": 0,
        "evidence_level": "description_only",
        "classification": None,
        "semantic_selection": None,
        "experiment_plan": None,
        "evidence_requirement_plan": None,
        "evidence_readiness": None,
        "specification_templates": [],
        "specification_assessment": None,
        "specification_answer_history": [],
        "compiled_specification_model": None,
        "candidate_route": None,
        "compiled_route": None,
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
    raw_response: str,
    expected_revision: int,
) -> DiagnosticSessionState:
    """Apply a structured adapter assessment after deterministic plan validation."""

    _expect_revision(state, expected_revision)
    if state.status not in {
        "awaiting_measurements",
        "measurement_needs_more",
        "measurement_conflict",
    }:
        raise ValueError(
            "only a measurement-waiting session accepts a measurement assessment"
        )
    if state.measurement_round_count >= state.maximum_turns:
        raise ValueError("maximum measurement rounds already reached")
    if state.measurement_plan is None:
        raise ValueError("diagnostic session is missing its measurement plan")
    typed_assessment = MeasurementAssessment.model_validate(assessment)
    validate_grounded_measurement_assessment(
        state.measurement_plan,
        typed_assessment,
        raw_response,
        previous_assessment=state.measurement_assessment,
    )
    reduced_diagnosis = None
    if typed_assessment.status == "ready":
        reduced_diagnosis = reduce_measurement_history_to_diagnosis(
            state.measurement_plan,
            [*state.measurement_history, typed_assessment],
        )
        unresolved_field_ids = [
            request.diagnostic_field_id
            for request in state.measurement_plan.requests
            if getattr(
                reduced_diagnosis, request.diagnostic_field_id
            ).status
            == "unknown"
        ]
        if unresolved_field_ids:
            unresolved_request_ids = {
                request.request_id
                for request in state.measurement_plan.requests
                if request.diagnostic_field_id in unresolved_field_ids
            }
            typed_assessment = MeasurementAssessment(
                status="need_more",
                facts=[
                    fact
                    for fact in typed_assessment.facts
                    if fact.request_id not in unresolved_request_ids
                ],
                gaps=unresolved_field_ids,
                rationale=(
                    "The deterministic diagnostic reducer could not resolve every "
                    "field from the submitted excerpts. Please clarify the listed gaps."
                ),
            )
            validate_grounded_measurement_assessment(
                state.measurement_plan,
                typed_assessment,
                raw_response,
                previous_assessment=state.measurement_assessment,
            )
    round_count = state.measurement_round_count + 1
    updates = {
        "measurement_assessment": typed_assessment,
        "measurement_history": [*state.measurement_history, typed_assessment],
        "measurement_response_history": [
            *state.measurement_response_history,
            raw_response,
        ],
        "measurement_round_count": round_count,
        "evidence_level": "description_only",
        "status": (
            "measurement_conflict"
            if typed_assessment.status == "conflict"
            else "measurement_needs_more"
        ),
        "refusal_reason": None,
    }
    if reduced_diagnosis is not None:
        updates["current_diagnosis"] = reduced_diagnosis
    if typed_assessment.status == "ready":
        evidence_text = render_measurement_evidence(updates["measurement_history"])
        accumulated = state.accumulated_description.model_copy(
            update={
                "text": f"{state.accumulated_description.text}\n\n{evidence_text}"
            }
        )
        updates.update(
            {
                "accumulated_description": accumulated,
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
    raw_response: str,
    expected_revision: int,
) -> DiagnosticSessionState:
    """Plural alias used by adapters submitting one structured assessment."""

    return submit_measurement_assessment(
        state,
        assessment,
        raw_response=raw_response,
        expected_revision=expected_revision,
    )


def submit_profile_measurement_assessment(
    state: DiagnosticSessionState,
    assessment: MeasurementAssessment | dict,
    *,
    raw_response: str,
) -> DiagnosticSessionState:
    """Persist one Profile reply's diagnostic assessment without using its counter."""

    if state.status not in {
        "awaiting_profile_measurements",
        "specification_conflict",
    }:
        raise ValueError(
            "only a profile-measurement session accepts a Profile assessment"
        )
    if state.profile_measurement_round_count >= state.maximum_turns:
        raise ValueError("maximum Profile measurement rounds already reached")
    if state.measurement_plan is None:
        raise ValueError("diagnostic session is missing its measurement plan")
    typed_assessment = MeasurementAssessment.model_validate(assessment)
    previous_ready = next(
        (
            item
            for item in reversed(state.measurement_history)
            if item.status == "ready"
        ),
        None,
    )
    if previous_ready is None:
        raise ValueError(
            "Profile measurement collection requires a prior ready diagnostic assessment"
        )
    validate_grounded_measurement_assessment(
        state.measurement_plan,
        typed_assessment,
        raw_response,
        previous_assessment=previous_ready,
    )
    payload = state.model_dump(mode="python")
    payload.update(
        {
            "measurement_assessment": typed_assessment,
            "measurement_history": [*state.measurement_history, typed_assessment],
            "measurement_response_history": [
                *state.measurement_response_history,
                raw_response,
            ],
            "profile_measurement_round_count": (
                state.profile_measurement_round_count + 1
            ),
        }
    )
    if typed_assessment.status != "ready":
        history = [*state.measurement_history, typed_assessment]
        diagnosis = reduce_measurement_history_to_diagnosis(
            state.measurement_plan,
            history,
        )
        checklist = build_diagnostic_checklist(
            state.accumulated_description,
            diagnosis,
        )
        payload.update(
            {
                "revision": state.revision + 1,
                "current_diagnosis": diagnosis,
                "checklist": checklist,
                "description_guidance": [
                    item.guidance for item in checklist
                ],
                "evidence_level": "description_only",
                "classification": None,
                "semantic_selection": None,
                "experiment_plan": None,
                "evidence_requirement_plan": None,
                "evidence_readiness": None,
                "specification_templates": [],
                "specification_assessment": None,
                "specification_answer_history": [],
                "compiled_specification_model": None,
                "candidate_route": None,
                "compiled_route": None,
                "status": (
                    "measurement_conflict"
                    if typed_assessment.status == "conflict"
                    else "measurement_needs_more"
                ),
                "refusal_reason": None,
            }
        )
    return DiagnosticSessionState.model_validate(payload)


def submit_evidence_to_session(
    state: DiagnosticSessionState,
    package: PlantEvidencePackage,
) -> DiagnosticSessionState:
    """The v4 guided workflow accepts only its typed record assessment at this stage."""

    if state.status not in {
        "awaiting_profile_measurements",
        "specification_conflict",
        "awaiting_evidence",
        "evidence_rejected",
    }:
        raise ValueError("only an evidence-waiting diagnostic session accepts evidence")
    if state.evidence_requirement_plan is None:
        raise ValueError("diagnostic session is missing its evidence requirement plan")
    readiness = validate_evidence_package(
        package, state.evidence_requirement_plan, state.accumulated_description
    )
    return _transition(
        state,
        updates={
            "evidence_readiness": readiness,
            "status": (
                "ready_for_experiments"
                if readiness.decision == "ready"
                else "evidence_rejected"
            ),
            "refusal_reason": (
                None
                if readiness.decision == "ready"
                else "object_evidence_validation_failed"
            ),
        },
    )


def submit_specifications_to_session(
    state: DiagnosticSessionState,
    specification_text: str,
    *,
    specification_adapter=None,
    simulation_bounds_confirmed: bool = False,
) -> DiagnosticSessionState:
    """Assess post-classification profile facts supplied through the shared textbox."""

    if state.status not in {
        "awaiting_profile_measurements",
        "specification_conflict",
    }:
        raise ValueError(
            "only an awaiting_profile_measurements session accepts profile facts"
        )
    text = specification_text.strip()
    if not text:
        raise ValueError("measurement response must be non-empty")
    if state.semantic_selection is None or state.classification is None:
        raise ValueError("profile fact collection requires a selected method profile")
    template = (
        state.specification_templates[0]
        if state.specification_templates
        else specification_template_for_profile(
            state.semantic_selection.simulation_profile_id
        )
    )
    assessment = assess_specification_text(
        state.accumulated_description,
        template,
        text,
        previous=state.specification_assessment,
        adapter=specification_adapter,
        diagnosis=state.current_diagnosis,
        classification=state.classification,
        method_profile_id=state.semantic_selection.simulation_profile_id,
        answer_history=state.specification_answer_history,
    )
    history = [*state.specification_answer_history, text]
    if assessment.status == "conflict":
        return _transition(
            state,
            updates={
                "specification_assessment": assessment,
                "specification_answer_history": history,
                "compiled_specification_model": None,
                "status": "specification_conflict",
            },
        )
    if assessment.status != "ready":
        return _transition(
            state,
            updates={
                "specification_assessment": assessment,
                "specification_answer_history": history,
                "compiled_specification_model": None,
                "status": "awaiting_profile_measurements",
            },
        )
    if (
        state.accumulated_description.simulation_boundary_confirmation is None
        and not simulation_bounds_confirmed
    ):
        raise ValueError(
            "confirmed simulation bounds are required before compiling a software model"
        )
    confirmed_description = state.accumulated_description
    if confirmed_description.simulation_boundary_confirmation is None:
        confirmed_description = confirmed_description.model_copy(
            update={
                "simulation_boundary_confirmation": SimulationBoundaryConfirmation()
            }
        )
    compiled = compile_specification_model(
        plant_id=plant_id_for_description(confirmed_description),
        description=confirmed_description,
        template=template,
        assessment=assessment,
    )
    updated_description = confirmed_description.model_copy(
        update={
            "safety_bounds": {
                **state.accumulated_description.safety_bounds,
                **compiled.safety_bounds,
            },
            "time_scale_hint_s": (
                state.accumulated_description.time_scale_hint_s
                or compiled.time_scale_hint_s
            ),
        }
    )
    return _transition(
        state,
        updates={
            "accumulated_description": updated_description,
            "specification_assessment": assessment,
            "specification_answer_history": history,
            "compiled_specification_model": compiled,
            "status": "specification_model_ready",
        },
    )


def migrate_diagnostic_session_payload(payload: object) -> DiagnosticSessionState:
    """Accept v4 payloads and explicitly refuse unsafe v3 persisted sessions."""

    if not isinstance(payload, Mapping):
        raise TypeError("diagnostic session payload must be a JSON object")
    payload = deepcopy(dict(payload))
    version = payload.get("schema_version")
    if version == "3.0":
        raise ValueError(
            "v3 diagnostic session payloads are not supported; start a v4 session"
        )
    if version == "4.0":
        post_measurement_statuses = {
            "awaiting_profile_measurements",
            "specification_conflict",
            "specification_model_ready",
            "awaiting_evidence",
            "evidence_rejected",
            "ready_for_experiments",
            "feature_extraction_failed",
            "ready_for_controller",
            "complete",
        }
        persisted_status = payload.get("status")
        is_post_measurement = persisted_status in post_measurement_statuses
        if persisted_status == "measurement_verified" and (
            payload.get("classification") is not None
            or payload.get("semantic_selection") is not None
        ):
            raise ValueError(
                "measurement_verified payloads cannot contain a Profile selection"
            )

        plan_payload = payload.get("measurement_plan")
        history_payload = payload.get("measurement_history", [])
        response_history = payload.get("measurement_response_history", [])
        if not isinstance(history_payload, list) or not isinstance(
            response_history, list
        ):
            raise ValueError(
                "measurement assessment and response histories must be arrays"
            )
        if any(not isinstance(item, str) for item in response_history):
            raise ValueError(
                "measurement response history entries must be strings"
            )
        plan = None
        assessments = []
        diagnosis = None
        if history_payload or is_post_measurement or persisted_status == "measurement_verified":
            from cfdc.models import MeasurementPlan

            plan = MeasurementPlan.model_validate(plan_payload)
            assessments = [
                MeasurementAssessment.model_validate(item) for item in history_payload
            ]
            diagnostic_round_count = payload.get("measurement_round_count", 0)
            profile_round_count = payload.get("profile_measurement_round_count", 0)
            if not isinstance(diagnostic_round_count, int) or not isinstance(
                profile_round_count, int
            ):
                raise ValueError("measurement round counts must be integers")
            if (
                len(assessments) != len(response_history)
                or len(assessments)
                != diagnostic_round_count + profile_round_count
            ):
                raise ValueError(
                    "grounded measurement assessment and response histories must align"
                )
            previous_assessment = None
            for index, (response, assessment) in enumerate(
                zip(response_history, assessments, strict=True)
            ):
                validate_grounded_measurement_assessment(
                    plan,
                    assessment,
                    response,
                    previous_assessment=(
                        previous_assessment if index > 0 else None
                    ),
                )
                previous_assessment = assessment
            if is_post_measurement:
                assessments = assessments[:diagnostic_round_count]
                response_history = response_history[:diagnostic_round_count]
                payload.update(
                    {
                        "measurement_history": [
                            item.model_dump(mode="python") for item in assessments
                        ],
                        "measurement_response_history": response_history,
                        "measurement_assessment": (
                            assessments[-1].model_dump(mode="python")
                            if assessments
                            else None
                        ),
                        "profile_measurement_round_count": 0,
                    }
                )
            diagnosis = reduce_measurement_history_to_diagnosis(plan, assessments)

        derived_fields = {
            "experiment_plan": None,
            "evidence_requirement_plan": None,
            "evidence_readiness": None,
            "specification_templates": [],
            "specification_assessment": None,
            "specification_answer_history": [],
            "compiled_specification_model": None,
            "pending_clarification_questions": [],
            "candidate_route": None,
            "compiled_route": None,
        }
        payload.update(derived_fields)
        if diagnosis is not None:
            payload["current_diagnosis"] = diagnosis.model_dump(mode="python")
        if persisted_status == "refused":
            payload.update(
                {
                    "classification": None,
                    "semantic_selection": None,
                }
            )
            diagnostic_round_count = payload.get("measurement_round_count", 0)
            diagnostic_history = assessments[:diagnostic_round_count]
            if (
                not diagnostic_history
                or diagnostic_history[-1].status != "ready"
                or diagnosis is None
                or not diagnosis.complete
            ):
                payload["evidence_level"] = "description_only"

        initial_description = SystemDescription.model_validate(
            payload.get("initial_description")
        )
        persisted_accumulated = SystemDescription.model_validate(
            payload.get("accumulated_description")
        )
        text_parts = [initial_description.text]
        turns_payload = payload.get("turns", [])
        if not isinstance(turns_payload, list):
            raise ValueError("diagnostic description turns must be an array")
        for turn in turns_payload:
            if not isinstance(turn, Mapping):
                raise TypeError("diagnostic description turns must be JSON objects")
            answers = turn.get("answers")
            if not isinstance(answers, Mapping):
                raise TypeError("diagnostic description turn answers must be an object")
            supplemental = answers.get("supplemental_description")
            if isinstance(supplemental, str) and supplemental.strip():
                text_parts.append(f"Supplemental description: {supplemental.strip()}")
        if assessments:
            text_parts.append(render_measurement_evidence(assessments))
        rebuilt_text = "\n\n".join(text_parts)
        normalized_rebuilt_text = " ".join(rebuilt_text.casefold().split())

        def retained_grounded_names(
            initial_names: list[str],
            candidate_names: list[str],
        ) -> list[str]:
            retained = list(initial_names)
            for name in candidate_names:
                normalized_name = " ".join(name.casefold().split())
                if (
                    normalized_name
                    and normalized_name in normalized_rebuilt_text
                    and name not in retained
                ):
                    retained.append(name)
            return retained

        rebuilt_accumulated = initial_description.model_copy(
            update={
                "text": rebuilt_text,
                "observed_outputs": retained_grounded_names(
                    initial_description.observed_outputs,
                    persisted_accumulated.observed_outputs,
                ),
                "actuators": retained_grounded_names(
                    initial_description.actuators,
                    persisted_accumulated.actuators,
                ),
            }
        )
        payload["accumulated_description"] = rebuilt_accumulated.model_dump(
            mode="python"
        )
        if diagnosis is None:
            diagnosis = DiagnosticEngine(adapter=None).diagnose(rebuilt_accumulated)
            payload["current_diagnosis"] = diagnosis.model_dump(mode="python")
        checklist = build_diagnostic_checklist(rebuilt_accumulated, diagnosis)
        payload["checklist"] = [
            item.model_dump(mode="python") for item in checklist
        ]
        payload["description_guidance"] = [
            item.guidance.model_dump(mode="python") for item in checklist
        ]

        if is_post_measurement:
            if (
                plan is None
                or not assessments
                or assessments[-1].status != "ready"
                or diagnosis is None
                or not diagnosis.complete
            ):
                raise ValueError(
                    "post-measurement payload requires complete grounded diagnostic "
                    "ready history"
                )
            payload.update(
                {
                    "evidence_level": "measurement_verified",
                    "classification": None,
                    "semantic_selection": None,
                    "status": "measurement_verified",
                    "refusal_reason": None,
                }
            )
            return DiagnosticSessionState.model_validate(payload)

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
