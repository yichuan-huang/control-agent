"""Revisioned, record-only diagnostic measurement sessions."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping
from copy import deepcopy
from uuid import uuid4

from cfdc.diagnosis.engine import DiagnosticEngine
from cfdc.diagnosis.llm import DiagnosticAdapter
from cfdc.diagnosis.measurements import (
    apply_description_guidance,
    apply_guidance_responses_to_checklist,
    build_description_assessment,
    build_diagnostic_checklist,
    build_measurement_plan,
    filter_description_checklist_semantics,
    reduce_measurement_history_to_diagnosis,
    render_measurement_evidence,
    validate_description_assessment_semantics,
    validate_grounded_measurement_assessment,
    validate_phrased_measurement_plan,
)
from cfdc.evidence import plant_id_for_description, validate_evidence_package
from cfdc.models import (
    DiagnosticSessionState,
    DiagnosticTurn,
    MeasurementAssessment,
    PlantEvidencePackage,
    ProfileFactCandidateAssessment,
    SimulationBoundaryConfirmation,
    SpecificationQuestion,
    StructuralDiagnosis,
    SystemDescription,
)
from cfdc.specifications import (
    assess_specification_text,
    build_initial_specification_assessment,
    collect_profile_fact_candidates,
    compile_specification_model,
    merge_specification_facts,
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


_PROFILE_RETRACTION_MARKERS = re.compile(
    r"(?:unknown|do not know|don't know|not establish|not available|"
    r"cannot determine|retract|withdraw|未知|不知道|不清楚|无法确定|撤回|无记录)",
    flags=re.IGNORECASE,
)
_PROFILE_RETRACTION_FIELD_MARKERS = {
    "open_loop_stability": r"(?:stability|bounded|settle|稳定|有界|收敛)",
    "minimum_phase": r"(?:minimum phase|initial direction|reverse|相位|初始方向|反向)",
    "significant_delay": r"(?:delay|response start|时延|延迟|开始变化)",
    "relative_degree": r"(?:relative degree|order|stage|相对阶|阶次|阶段)",
    "controllability_observability": (
        r"(?:controllability|observability|driven|recorded|可控|可观|带动|记录)"
    ),
    "nonlinearity_strength": (
        r"(?:nonlinearity|proportional|hysteresis|非线性|比例|滞回)"
    ),
    "coupling_severity": r"(?:coupling|channel|input-output|耦合|通道|输入输出)",
    "uncertainty_magnitude": (
        r"(?:uncertainty|load|operating condition|不确定|负载|工况)"
    ),
}


def _profile_gap_is_explicit(field_id: str, raw_response: str) -> bool:
    for clause in re.split(r"[.!?。！？；;\n]+", raw_response):
        if (
            _PROFILE_RETRACTION_MARKERS.search(clause)
            and re.search(
                _PROFILE_RETRACTION_FIELD_MARKERS[field_id],
                clause,
                flags=re.IGNORECASE,
            )
            and re.search(
                r"(?:remains? unchanged|still valid|保持不变|仍然有效|未改变)",
                clause,
                flags=re.IGNORECASE,
            )
            is None
        ):
            return True
    return False


def _restore_unattested_profile_gaps(
    assessment: MeasurementAssessment,
    previous_ready: MeasurementAssessment,
    raw_response: str,
) -> MeasurementAssessment:
    previous_by_id = {fact.request_id: fact for fact in previous_ready.facts}
    restored_ids = {
        field_id
        for field_id in assessment.gaps
        if field_id in previous_by_id
        and not _profile_gap_is_explicit(field_id, raw_response)
    }
    if not restored_ids:
        return assessment
    facts = [*assessment.facts]
    existing_ids = {fact.request_id for fact in facts}
    facts.extend(
        previous_by_id[field_id]
        for field_id in restored_ids
        if field_id not in existing_ids
    )
    gaps = [field_id for field_id in assessment.gaps if field_id not in restored_ids]
    status = "conflict" if assessment.conflicts else "need_more" if gaps else "ready"
    return MeasurementAssessment(
        status=status,
        facts=facts,
        gaps=gaps,
        conflicts=assessment.conflicts,
        conflict_request_ids=assessment.conflict_request_ids,
        rationale=(
            f"{assessment.rationale} Unattested Profile gaps retained their prior "
            "grounded diagnostic facts."
        ),
    )


def _ground_description_checklist(
    checklist,
    measurement_plan,
    description_text: str,
):
    checklist = filter_description_checklist_semantics(checklist, description_text)
    assessment, diagnosis = build_description_assessment(
        measurement_plan, checklist, description_text
    )
    if diagnosis is not None and not diagnosis.complete:
        checklist = [
            (
                item.model_copy(
                    update={
                        "status": "unknown",
                        "evidence": [],
                        "guidance": item.guidance.model_copy(
                            update={"response": "unknown"}
                        ),
                    }
                )
                if getattr(diagnosis, item.diagnostic_field_id).status == "unknown"
                else item
            )
            for item in checklist
        ]
    return checklist, assessment, diagnosis


def _collect_profile_description_assessment(
    description: SystemDescription,
    diagnostic_adapter: DiagnosticAdapter | None,
    previous: ProfileFactCandidateAssessment | None,
) -> ProfileFactCandidateAssessment:
    """Collect optional Profile facts without blocking structural guidance."""

    try:
        return collect_profile_fact_candidates(
            description,
            adapter=diagnostic_adapter,
            previous=previous,
        )
    except Exception:  # noqa: BLE001 - optional Profile enrichment fails closed
        return collect_profile_fact_candidates(
            description,
            adapter=None,
            previous=previous,
        )


def start_diagnostic_session(
    description: SystemDescription,
    *,
    route_id: str = "generic",
    diagnostic_adapter: DiagnosticAdapter | None = None,
    use_mechanism_cards: bool = False,
    diagnosis: StructuralDiagnosis | None = None,
) -> DiagnosticSessionState:
    """Create a v4 session without making a classification or profile selection."""

    initial_description = description.model_copy(deep=True)
    working_description = description.model_copy(deep=True)
    guided = diagnostic_adapter is not None and hasattr(
        diagnostic_adapter, "guide_description"
    )
    accumulated_description = working_description
    if guided:
        preliminary_diagnosis = DiagnosticEngine(
            adapter=None, use_mechanism_cards=use_mechanism_cards
        ).diagnose(working_description)
        preliminary_checklist = build_diagnostic_checklist(
            working_description, preliminary_diagnosis
        )
        expected_guidance = [item.guidance for item in preliminary_checklist]
        accumulated_description, guided_items = apply_description_guidance(
            working_description,
            diagnostic_adapter.guide_description(
                working_description.model_copy(deep=True),
                deepcopy(expected_guidance),
            ),
            expected_guidance,
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
            working_description, diagnostic_adapter, use_mechanism_cards
        )
        checklist = build_diagnostic_checklist(working_description, resolved_diagnosis)
    description_profile_assessment = _collect_profile_description_assessment(
        accumulated_description,
        diagnostic_adapter,
        None,
    )
    measurement_plan = build_measurement_plan(checklist)
    if diagnostic_adapter is not None and hasattr(
        diagnostic_adapter, "phrase_measurement_plan"
    ):
        measurement_plan = validate_phrased_measurement_plan(
            measurement_plan,
            diagnostic_adapter.phrase_measurement_plan(
                accumulated_description.model_copy(deep=True),
                deepcopy(checklist),
                measurement_plan.model_copy(deep=True),
            ),
        )
    description_assessment = None
    if guided:
        checklist, description_assessment, grounded_diagnosis = (
            _ground_description_checklist(
                checklist, measurement_plan, accumulated_description.text
            )
        )
        if description_assessment is not None:
            resolved_diagnosis = grounded_diagnosis
    return DiagnosticSessionState(
        session_id=f"diagnostic-{uuid4().hex[:16]}",
        route_id=route_id,
        initial_description=initial_description,
        accumulated_description=accumulated_description.model_copy(deep=True),
        current_diagnosis=resolved_diagnosis,
        description_guidance=[item.guidance for item in checklist],
        checklist=checklist,
        measurement_plan=measurement_plan,
        description_assessment=description_assessment,
        description_profile_assessment=description_profile_assessment,
        pending_clarification_questions=[],
        evidence_level=(
            "description_grounded"
            if description_assessment is not None
            else "description_only"
        ),
        status=(
            "description_grounded"
            if description_assessment is not None
            else ("collecting_description" if guided else "awaiting_measurements")
        ),
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
            text_parts.append(f"Supplemental description: {prior_supplement.strip()}")
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
        expected_guidance = [item.guidance for item in preliminary_checklist]
        accumulated, guided_items = apply_description_guidance(
            accumulated,
            diagnostic_adapter.guide_description(
                accumulated.model_copy(deep=True),
                deepcopy(expected_guidance),
            ),
            expected_guidance,
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
                accumulated.model_copy(deep=True),
                deepcopy(checklist),
                measurement_plan.model_copy(deep=True),
            ),
        )
    description_assessment = None
    if guided:
        checklist, description_assessment, grounded_diagnosis = (
            _ground_description_checklist(checklist, measurement_plan, accumulated.text)
        )
        if description_assessment is not None:
            diagnosis = grounded_diagnosis
    profile_source_description = accumulated.model_copy(
        update={
            "text": "\n\n".join(
                [accumulated.text, *state.specification_answer_history]
            )
        }
    )
    description_profile_assessment = _collect_profile_description_assessment(
        profile_source_description,
        diagnostic_adapter,
        state.description_profile_assessment,
    )
    updates = {
        "accumulated_description": accumulated,
        "turns": [*state.turns, turn],
        "current_diagnosis": diagnosis,
        "description_guidance": [item.guidance for item in checklist],
        "checklist": checklist,
        "measurement_plan": measurement_plan,
        "description_assessment": description_assessment,
        "description_profile_assessment": description_profile_assessment,
        "description_turn_count": state.description_turn_count + 1,
        "measurement_assessment": None,
        "measurement_history": [],
        "measurement_response_history": [],
        "measurement_round_count": 0,
        "profile_measurement_round_count": state.profile_measurement_round_count,
        "evidence_level": (
            "description_grounded"
            if description_assessment is not None
            else "description_only"
        ),
        "classification": None,
        "semantic_selection": None,
        "experiment_plan": None,
        "evidence_requirement_plan": None,
        "evidence_readiness": None,
        "specification_templates": [],
        "specification_assessment": None,
        "compiled_specification_model": None,
        "candidate_route": None,
        "compiled_route": None,
        "status": (
            "description_grounded"
            if description_assessment is not None
            else ("collecting_description" if guided else "awaiting_measurements")
        ),
        "refusal_reason": None,
    }
    if (
        description_assessment is None
        and updates["description_turn_count"] >= state.maximum_turns
    ):
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
            if getattr(reduced_diagnosis, request.diagnostic_field_id).status
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
            update={"text": f"{state.accumulated_description.text}\n\n{evidence_text}"}
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
    expected_revision: int,
) -> DiagnosticSessionState:
    """Check a Profile reply for explicit diagnostic changes without persisting copies."""

    _expect_revision(state, expected_revision)
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
    previous_ready = state.description_assessment or next(
        (
            item
            for item in reversed(
                state.measurement_history[: state.measurement_round_count]
            )
            if item.status == "ready"
        ),
        None,
    )
    if previous_ready is None:
        raise ValueError(
            "Profile measurement collection requires a prior ready diagnostic assessment"
        )
    typed_assessment = _restore_unattested_profile_gaps(
        typed_assessment,
        previous_ready,
        raw_response,
    )
    validate_grounded_measurement_assessment(
        state.measurement_plan,
        typed_assessment,
        raw_response,
        previous_assessment=previous_ready,
    )
    diagnosis = reduce_measurement_history_to_diagnosis(
        state.measurement_plan,
        [previous_ready, typed_assessment],
    )
    payload = state.model_dump(mode="python")
    payload["revision"] = state.revision + 1
    payload["profile_measurement_round_count"] = (
        state.profile_measurement_round_count + 1
    )
    if diagnosis != state.current_diagnosis:
        description_budget_exhausted = (
            state.description_turn_count >= state.maximum_turns
        )
        prior_checklist = {item.diagnostic_field_id: item for item in state.checklist}
        checklist = []
        for field_id in (
            "open_loop_stability",
            "minimum_phase",
            "significant_delay",
            "relative_degree",
            "controllability_observability",
            "nonlinearity_strength",
            "coupling_severity",
            "uncertainty_magnitude",
        ):
            prior_item = prior_checklist[field_id]
            changed = getattr(diagnosis, field_id) != getattr(
                state.current_diagnosis, field_id
            )
            if changed or getattr(diagnosis, field_id).status == "unknown":
                checklist.append(
                    prior_item.model_copy(
                        update={
                            "status": "unknown",
                            "evidence": [],
                            "guidance": prior_item.guidance.model_copy(
                                update={"response": "unknown"}
                            ),
                        }
                    )
                )
            else:
                checklist.append(prior_item)
        payload.update(
            {
                "current_diagnosis": diagnosis,
                "accumulated_description": state.accumulated_description.model_copy(
                    update={"simulation_boundary_confirmation": None}
                ),
                "checklist": checklist,
                "description_guidance": [item.guidance for item in checklist],
                "description_assessment": None,
                "measurement_assessment": None,
                "measurement_history": [],
                "measurement_response_history": [],
                "measurement_round_count": 0,
                "evidence_level": "description_only",
                "classification": None,
                "semantic_selection": None,
                "experiment_plan": None,
                "evidence_requirement_plan": None,
                "evidence_readiness": None,
                "specification_templates": [],
                "specification_assessment": None,
                "compiled_specification_model": None,
                "candidate_route": None,
                "compiled_route": None,
                "status": (
                    "refused"
                    if description_budget_exhausted
                    else "collecting_description"
                ),
                "refusal_reason": (
                    "maximum_description_turns_reached"
                    if description_budget_exhausted
                    else None
                ),
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


def _merge_cached_profile_facts(
    state: DiagnosticSessionState,
    template,
    assessment,
):
    """Merge facts already grounded by the description/Profile candidate channel."""

    cached = state.description_profile_assessment
    if cached is None:
        return assessment
    candidate_facts = [
        candidate.fact
        for candidate in cached.candidates
        if candidate.template_id == template.template_id
    ]
    if not candidate_facts:
        return assessment
    facts, cache_conflicts = merge_specification_facts(
        assessment.facts,
        candidate_facts,
    )
    conflicts = list(dict.fromkeys([*assessment.conflicts, *cache_conflicts]))
    rebuilt = build_initial_specification_assessment(
        state.accumulated_description,
        template,
        facts=facts,
        conflicts=conflicts,
    )
    changed = facts != assessment.facts or conflicts != assessment.conflicts
    return rebuilt.model_copy(
        update={
            "rejected_facts": assessment.rejected_facts,
            "no_progress": False if changed else assessment.no_progress,
        }
    )


_SCOPE_SENTENCE_BOUNDARY = re.compile(
    r"(?<=[。！？!?])|(?<=\.)(?=\s|$)|[;；\n]+"
)
_SCOPE_NEGATION = re.compile(
    r"(?:\b(?:ranges?|bounds?|limits?)\b.{0,24}"
    r"\b(?:are\s+not|aren't|do\s+not|don't)\b.{0,24}"
    r"(?:used|intended|for|simulation|boundary)|"
    r"\b(?:does\s+not|doesn't|cannot|can't)\s+"
    r"(?:use|apply|serve|define|set)\b.{0,30}"
    r"(?:ranges?|bounds?|limits?|simulation)|"
    r"\b(?:not|never)\s+(?:used|intended|applied|treated)\b.{0,30}"
    r"(?:software\s+simulation|simulation)|"
    r"(?:software\s+simulation|simulation).{0,24}"
    r"\b(?:does\s+not|doesn't|is\s+not|isn't|cannot|can't)\b.{0,24}"
    r"(?:use|range|bound|limit)|"
    r"(?:不用于|不用作|不作为|未用于|未用作|未作为).{0,24}"
    r"(?:软件仿真|仿真)|"
    r"(?:范围|边界|上下限).{0,20}(?:并非|不是|不能作为|不可作为).{0,20}"
    r"(?:软件仿真|仿真|边界)|"
    r"(?:软件仿真|仿真).{0,20}(?:不使用|未使用|不用|不能使用).{0,20}"
    r"(?:范围|边界|上下限))",
    flags=re.IGNORECASE,
)


def _scope_statement_is_negated(text: str) -> bool:
    return _SCOPE_NEGATION.search(text) is not None


def _has_per_fact_simulation_boundary_scope(fact_id: str, text: str) -> bool:
    """Require simulation purpose, signal role, and bound in one local clause."""

    clauses = [
        clause
        for sentence in _SCOPE_SENTENCE_BOUNDARY.split(text)
        for clause in re.split(r"[,，]+", sentence)
        if clause.strip()
    ]
    if any(_scope_statement_is_negated(clause) for clause in clauses):
        return False
    role_pattern = (
        r"(?:input|command|actuat|throttle|heater|valve|pump|"
        r"输入|命令|执行|油门|加热|阀|泵)"
        if fact_id.startswith("input_")
        else r"(?:output|response|speed|temperature|level|position|输出|响应|车速|温度|液位|位置)"
    )
    direction_pattern = (
        r"(?:min|lower|下限|最小|range|bounds?|limits?|范围|边界|上下限)"
        if fact_id.endswith("_min")
        else r"(?:max|upper|上限|最大|range|bounds?|limits?|范围|边界|上下限)"
    )
    explicit_scope_pattern = re.compile(
        r"(?:(?:software\s+)?simulation|simulation[- ]only|软件仿真|仿真)"
        r".{0,24}(?:run|stop|range|bounds?|limits?|boundary|"
        r"运行|停止|范围|边界|上下限|下限|上限)|"
        r"(?:run|stop|range|bounds?|limits?|boundary|"
        r"运行|停止|范围|边界|上下限|下限|上限)"
        r".{0,24}(?:(?:software\s+)?simulation|simulation[- ]only|软件仿真|仿真)",
        flags=re.IGNORECASE,
    )
    return any(
        re.search(role_pattern, clause, flags=re.IGNORECASE)
        and re.search(direction_pattern, clause, flags=re.IGNORECASE)
        and explicit_scope_pattern.search(clause)
        for clause in clauses
    )


def _simulation_scope_is_negated(text: str) -> bool:
    return any(
        _scope_statement_is_negated(sentence)
        for sentence in _SCOPE_SENTENCE_BOUNDARY.split(text)
        if sentence.strip()
    )


def _has_global_simulation_boundary_scope(text: str) -> bool:
    """Require one local statement tying all ranges to software simulation use."""

    sentences = [
        sentence
        for sentence in _SCOPE_SENTENCE_BOUNDARY.split(text.casefold())
        if sentence.strip()
    ]
    if any(_scope_statement_is_negated(sentence) for sentence in sentences):
        return False
    for sentence in sentences:
        if re.search(
            r"(?:software\s+simulation|simulation[- ]only|软件仿真|仅限仿真)",
            sentence,
        ) is None:
            continue
        input_role = re.search(
            r"(?:input|command|actuat|throttle|heater|valve|pump|"
            r"输入|命令|执行|油门|加热|阀|泵)",
            sentence,
        )
        output_role = re.search(
            r"(?:output|response|speed|temperature|level|position|"
            r"输出|响应|车速|温度|液位|位置)",
            sentence,
        )
        collective_reference = re.search(
            r"(?:(?:these|those|above|all)(?:\s+input\s*/?\s*output)?\s+"
            r"(?:ranges?|bounds?|limits?)|the\s+(?:ranges?|bounds?|limits?)\s+above|"
            r"(?:这些|上述|所有|全部)(?:输入[/、和及]?输出)?(?:范围|边界|上下限)|"
            r"(?:这些|上述|所有|全部)(?:范围|边界|上下限))",
            sentence,
        )
        has_both_scoped_roles = bool(
            input_role
            and output_role
            and re.search(r"(?:ranges?|bounds?|limits?|范围|边界|上下限)", sentence)
        )
        if collective_reference is None and not has_both_scoped_roles:
            continue
        direct_scope = re.search(
            r"(?:software\s+simulation(?:'s)?\s+"
            r"(?:input|output|run|stop|throttle|speed|temperature|level|position)\s+"
            r"(?:ranges?|bounds?|limits?)|"
            r"软件仿真(?:的)?(?:输入|输出|运行|停止|油门|车速|温度|液位|位置)"
            r"(?:范围|边界|上下限))",
            sentence,
        )
        purpose_scope = re.search(
            r"(?:(?:used|serve|apply|only|solely|for).{0,30}"
            r"(?:run|stop|bound|limit)|"
            r"(?:用于|用作|作为|仅供).{0,24}(?:运行|停止|边界|上下限))",
            sentence,
        )
        if direct_scope is not None or purpose_scope is not None:
            return True
    return False


def _simulation_boundary_scope_is_grounded(
    description: SystemDescription,
    required_boundary_ids: set[str],
    assessment,
    history: list[str],
) -> bool:
    facts_by_id = {fact.fact_id: fact for fact in assessment.facts}
    if not required_boundary_ids or not required_boundary_ids <= set(facts_by_id):
        return False
    scope_text = "\n".join([description.text, *history]).casefold()
    if _simulation_scope_is_negated(scope_text):
        return False
    per_fact_scope = all(
        _has_per_fact_simulation_boundary_scope(
            fact_id,
            facts_by_id[fact_id].source_text,
        )
        for fact_id in required_boundary_ids
    )
    return per_fact_scope or _has_global_simulation_boundary_scope(scope_text)


def submit_specifications_to_session(
    state: DiagnosticSessionState,
    specification_text: str,
    *,
    specification_adapter=None,
    simulation_bounds_confirmed: bool = False,
    auto_confirm_simulation_bounds: bool = False,
    _revision_already_advanced: bool = False,
) -> DiagnosticSessionState:
    """Assess post-classification profile facts supplied through the shared textbox."""

    if state.status not in {
        "awaiting_profile_measurements",
        "specification_conflict",
    }:
        raise ValueError(
            "only an awaiting_profile_measurements session accepts profile facts"
        )

    def transition(updates: dict) -> DiagnosticSessionState:
        if not _revision_already_advanced:
            return _transition(state, updates=updates)
        payload = deepcopy(state.model_dump(mode="python"))
        payload.update(deepcopy(updates))
        return DiagnosticSessionState.model_validate(payload)

    text = specification_text.strip()
    if state.semantic_selection is None or state.classification is None:
        raise ValueError("profile fact collection requires a selected method profile")
    template = (
        state.specification_templates[0]
        if state.specification_templates
        else specification_template_for_profile(
            state.semantic_selection.simulation_profile_id
        )
    )
    boundary_fact_ids = {
        "input_min",
        "input_max",
        "output_min",
        "output_max",
    }
    template_fact_ids = {field.fact_id for field in template.fields}
    required_boundary_ids = boundary_fact_ids & template_fact_ids
    history = (
        [*state.specification_answer_history, text]
        if text
        else list(state.specification_answer_history)
    )
    previous_assessment = state.specification_assessment
    scope_only_submission = bool(
        text
        and previous_assessment is not None
        and previous_assessment.status == "need_more"
        and previous_assessment.missing_fact_ids == ["simulation_boundary_scope"]
        and not previous_assessment.conflicts
        and _simulation_boundary_scope_is_grounded(
            state.accumulated_description,
            required_boundary_ids,
            previous_assessment,
            history,
        )
    )
    if scope_only_submission:
        assessment = previous_assessment.model_copy(
            update={
                "status": "ready",
                "missing_fact_ids": [],
                "questions": [],
                "rationale": (
                    "All required Profile facts and their software-simulation "
                    "boundary purpose are explicit."
                ),
                "no_progress": False,
            }
        )
    elif text:
        assessment = assess_specification_text(
            state.accumulated_description.model_copy(deep=True),
            template.model_copy(deep=True),
            text,
            previous=deepcopy(state.specification_assessment),
            adapter=specification_adapter,
            diagnosis=state.current_diagnosis.model_copy(deep=True),
            classification=state.classification.model_copy(deep=True),
            method_profile_id=state.semantic_selection.simulation_profile_id,
            answer_history=state.specification_answer_history,
        )
    else:
        assessment = deepcopy(state.specification_assessment)
        if assessment is None or assessment.status != "ready":
            raise ValueError("measurement response must be non-empty")
    assessment = _merge_cached_profile_facts(state, template, assessment)
    if assessment.status == "conflict":
        return transition(
            {
                "specification_assessment": assessment,
                "specification_answer_history": history,
                "compiled_specification_model": None,
                "status": "specification_conflict",
            },
        )
    if assessment.status != "ready":
        return transition(
            {
                "specification_assessment": assessment,
                "specification_answer_history": history,
                "compiled_specification_model": None,
                "status": "awaiting_profile_measurements",
            },
        )
    scope_grounded = _simulation_boundary_scope_is_grounded(
        state.accumulated_description,
        required_boundary_ids,
        assessment,
        history,
    )
    legacy_explicit_submission = bool(text) and text.lstrip().casefold().startswith(
        ("manual:", "json:", "structured:")
    )
    auto_scope_confirmation = auto_confirm_simulation_bounds and not (
        legacy_explicit_submission
    )
    if (
        required_boundary_ids
        and state.accumulated_description.simulation_boundary_confirmation is None
        and not simulation_bounds_confirmed
        and auto_scope_confirmation
        and not scope_grounded
    ):
        scope_question = SpecificationQuestion(
            question_id="spec_simulation_boundary_scope",
            requested_fact_ids=["simulation_boundary_scope"],
            prompt=(
                "请说明输入和输出范围仅作为本次软件仿真的运行/停止边界，"
                "而不是实体硬件操作或安全认证范围。"
            ),
            why_needed="软件模型只能在明确声明的仿真边界内运行。",
            where_to_find="可直接在本次 Profile 回复中补充这句范围用途说明。",
            unit_hint="无需填写单位",
            example="这些输入/输出范围只用于软件仿真的运行和停止边界。",
        )
        scoped_assessment = assessment.model_copy(
            update={
                "status": "need_more",
                "missing_fact_ids": ["simulation_boundary_scope"],
                "questions": [scope_question],
                "rationale": (
                    "数值范围已具备，但原文没有明确说明它们仅用于软件仿真边界。"
                ),
            }
        )
        return transition(
            {
                "specification_assessment": scoped_assessment,
                "specification_answer_history": history,
                "compiled_specification_model": None,
                "status": "awaiting_profile_measurements",
            }
    )
    if (
        required_boundary_ids
        and state.accumulated_description.simulation_boundary_confirmation is None
        and not simulation_bounds_confirmed
        and not auto_scope_confirmation
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
    return transition(
        {
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
        if persisted_status in {
            "collecting_description",
            "awaiting_measurements",
            "measurement_needs_more",
            "measurement_conflict",
            "description_grounded",
            "measurement_verified",
        }:
            payload["profile_measurement_round_count"] = 0
        is_post_measurement = persisted_status in post_measurement_statuses
        description_assessment_payload = payload.get("description_assessment")
        persisted_description_grounded = (
            payload.get("evidence_level") == "description_grounded"
            and description_assessment_payload is not None
        )
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
            raise ValueError("measurement response history entries must be strings")
        if persisted_description_grounded and (
            history_payload
            or response_history
            or payload.get("measurement_assessment") is not None
            or payload.get("measurement_round_count", 0)
        ):
            raise ValueError(
                "description and measurement diagnostic evidence sources are mutually exclusive"
            )
        plan = None
        assessments = []
        diagnosis = None
        if (
            history_payload
            or is_post_measurement
            or persisted_status == "measurement_verified"
            or persisted_description_grounded
        ):
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
            accepted_history_lengths = {
                diagnostic_round_count,
                diagnostic_round_count + profile_round_count,
            }
            if (
                len(assessments) != len(response_history)
                or len(assessments) not in accepted_history_lengths
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
                    previous_assessment=(previous_assessment if index > 0 else None),
                )
                previous_assessment = assessment
            if len(assessments) > diagnostic_round_count:
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
                    }
                )
                if is_post_measurement:
                    payload["profile_measurement_round_count"] = 0
            if assessments:
                diagnosis = reduce_measurement_history_to_diagnosis(plan, assessments)

        derived_fields = {
            "experiment_plan": None,
            "evidence_requirement_plan": None,
            "evidence_readiness": None,
            "specification_templates": [],
            "specification_assessment": None,
            "compiled_specification_model": None,
            "pending_clarification_questions": [],
            "candidate_route": None,
            "compiled_route": None,
        }
        payload.update(derived_fields)
        if is_post_measurement:
            payload["profile_measurement_round_count"] = 0
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
        ).model_copy(update={"simulation_boundary_confirmation": None})
        payload["initial_description"] = initial_description.model_dump(mode="python")
        persisted_accumulated = SystemDescription.model_validate(
            payload.get("accumulated_description")
        )
        text_parts = [initial_description.text]
        turns_payload = payload.get("turns", [])
        if not isinstance(turns_payload, list):
            raise ValueError("diagnostic description turns must be an array")
        normalized_turns = []
        for turn_index, turn in enumerate(turns_payload, start=1):
            if not isinstance(turn, Mapping):
                raise TypeError("diagnostic description turns must be JSON objects")
            answers = turn.get("answers")
            if not isinstance(answers, Mapping):
                raise TypeError("diagnostic description turn answers must be an object")
            supplemental = answers.get("supplemental_description")
            if not isinstance(supplemental, str) or not supplemental.strip():
                raise ValueError(
                    "diagnostic description turns require a non-empty supplemental_description"
                )
            normalized_supplemental = supplemental.strip()
            evidence = f"Supplemental description: {normalized_supplemental}"
            text_parts.append(evidence)
            turn_description = initial_description.model_copy(
                update={"text": "\n\n".join(text_parts)}
            )
            normalized_turns.append(
                DiagnosticTurn(
                    turn_index=turn_index,
                    questions=["supplemental_description"],
                    answers={"supplemental_description": normalized_supplemental},
                    evidence=[evidence],
                    diagnosis=DiagnosticEngine(adapter=None).diagnose(turn_description),
                )
            )
        payload["turns"] = [turn.model_dump(mode="python") for turn in normalized_turns]
        payload["description_turn_count"] = len(normalized_turns)
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
        # v4 sessions created before the description/Profile split have no cache.
        # Rebuild deterministic candidates from the full accumulated description;
        # if a newer payload already carries LLM-enriched candidates, merge them
        # without dropping their auditable history.
        persisted_profile_payload = payload.get("description_profile_assessment")
        persisted_profile = None
        if persisted_profile_payload is not None:
            persisted_profile = ProfileFactCandidateAssessment.model_validate(
                persisted_profile_payload
            )
        specification_history = payload.get("specification_answer_history", [])
        if not isinstance(specification_history, list) or any(
            not isinstance(item, str) for item in specification_history
        ):
            raise ValueError("specification answer history entries must be strings")
        profile_source_description = rebuilt_accumulated.model_copy(
            update={
                "text": "\n\n".join(
                    [rebuilt_accumulated.text, *specification_history]
                )
            }
        )
        payload["description_profile_assessment"] = (
            collect_profile_fact_candidates(
                profile_source_description,
                previous=persisted_profile,
            ).model_dump(mode="python")
        )
        if diagnosis is None:
            diagnosis = DiagnosticEngine(adapter=None).diagnose(rebuilt_accumulated)
            payload["current_diagnosis"] = diagnosis.model_dump(mode="python")
        checklist = build_diagnostic_checklist(rebuilt_accumulated, diagnosis)
        payload["checklist"] = [item.model_dump(mode="python") for item in checklist]
        payload["description_guidance"] = [
            item.guidance.model_dump(mode="python") for item in checklist
        ]

        if persisted_description_grounded:
            if plan is None:
                raise ValueError(
                    "description-grounded payload requires the fixed diagnostic plan"
                )
            description_assessment = MeasurementAssessment.model_validate(
                description_assessment_payload
            )
            validate_grounded_measurement_assessment(
                plan,
                description_assessment,
                rebuilt_accumulated.text,
            )
            validate_description_assessment_semantics(
                plan,
                description_assessment,
                rebuilt_accumulated.text,
            )
            diagnosis = reduce_measurement_history_to_diagnosis(
                plan, [description_assessment]
            )
            if description_assessment.status != "ready" or not diagnosis.complete:
                raise ValueError(
                    "description-grounded payload requires a complete ready assessment"
                )
            fact_by_request = {
                fact.request_id: fact for fact in description_assessment.facts
            }
            checklist = build_diagnostic_checklist(rebuilt_accumulated, diagnosis)
            checklist = apply_guidance_responses_to_checklist(
                checklist,
                [
                    item.guidance.model_copy(
                        update={
                            "response": fact_by_request[
                                item.diagnostic_field_id
                            ].source_excerpt
                        }
                    )
                    for item in checklist
                ],
                rebuilt_accumulated.text,
            )
            profile_cap_refusal = (
                persisted_status == "refused"
                and payload.get("refusal_reason")
                == "maximum_profile_measurement_rounds_reached"
                and payload.get("profile_measurement_round_count", 0)
                >= payload.get("maximum_turns", 8)
            )
            payload.update(
                {
                    "current_diagnosis": diagnosis.model_dump(mode="python"),
                    "description_guidance": [
                        item.guidance.model_dump(mode="python") for item in checklist
                    ],
                    "checklist": [item.model_dump(mode="python") for item in checklist],
                    "description_assessment": description_assessment.model_dump(
                        mode="python"
                    ),
                    "measurement_assessment": None,
                    "measurement_history": [],
                    "measurement_response_history": [],
                    "measurement_round_count": 0,
                    "profile_measurement_round_count": (
                        payload.get("profile_measurement_round_count", 0)
                        if profile_cap_refusal
                        else 0
                    ),
                    "evidence_level": "description_grounded",
                    "classification": None,
                    "semantic_selection": None,
                    "status": "refused"
                    if profile_cap_refusal
                    else "description_grounded",
                    "refusal_reason": (
                        "maximum_profile_measurement_rounds_reached"
                        if profile_cap_refusal
                        else None
                    ),
                }
            )
            return DiagnosticSessionState.model_validate(payload)

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
                    "description_assessment": None,
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
