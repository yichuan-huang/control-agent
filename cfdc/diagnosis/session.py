from __future__ import annotations

import hashlib
from uuid import uuid4

from cfdc.diagnosis.engine import DiagnosticEngine
from cfdc.diagnosis.llm import DiagnosticAdapter
from cfdc.experiments import plan_safe_experiments
from cfdc.models import DiagnosticSessionState, DiagnosticTurn, SemanticRouteSelection, StructuralDiagnosis, SystemDescription
from cfdc.workflow import (
    apply_profile_to_classification,
    build_candidate_route,
    compile_candidate_route,
    default_capability_catalog,
    default_simulation_profile_catalog,
    deterministic_profile_selection,
    validate_semantic_selection,
)


def clarification_question_id(question: str) -> str:
    return f"q_{hashlib.sha256(question.encode()).hexdigest()[:10]}"


def clarification_question_map(state: DiagnosticSessionState) -> dict[str, str]:
    return {clarification_question_id(question): question for question in state.pending_clarification_questions}


def _select_profile(adapter, description, diagnosis, classification):
    catalog = default_simulation_profile_catalog()
    if adapter is not None and hasattr(adapter, "select_profile"):
        payload = adapter.select_profile(description, diagnosis, classification, catalog)
        selection = SemanticRouteSelection.model_validate(payload)
    else:
        selection = deterministic_profile_selection(description, diagnosis, classification, catalog)
    profile = validate_semantic_selection(selection, classification, catalog)
    return selection, profile, apply_profile_to_classification(classification, profile)


def _advance_complete_diagnosis(state, diagnosis, engine, adapter):
    description = state.accumulated_description
    raw_classification = engine.classify(diagnosis, description)
    selection, profile, classification = _select_profile(adapter, description, diagnosis, raw_classification)
    experiment_plan = plan_safe_experiments(diagnosis, classification, description)
    candidate_route = build_candidate_route(state.route_id, diagnosis, classification, description, experiment_plan, profile)
    compiled_route = compile_candidate_route(candidate_route, default_capability_catalog())
    return state.model_copy(update={
        "current_diagnosis": diagnosis,
        "classification": classification,
        "semantic_selection": selection,
        "experiment_plan": experiment_plan,
        "pending_clarification_questions": [],
        "candidate_route": candidate_route,
        "compiled_route": compiled_route,
        "status": "ready_for_experiments" if compiled_route.executable else "refused",
        "refusal_reason": None if compiled_route.executable else "blocking_capability_gap",
    })


def start_diagnostic_session(
    description: SystemDescription,
    *,
    route_id: str = "generic",
    diagnostic_adapter: DiagnosticAdapter | None = None,
    use_mechanism_cards: bool = False,
    diagnosis: StructuralDiagnosis | None = None,
) -> DiagnosticSessionState:
    engine = DiagnosticEngine(adapter=diagnostic_adapter, use_mechanism_cards=use_mechanism_cards)
    resolved_diagnosis = diagnosis or engine.diagnose(description)
    state = DiagnosticSessionState(
        session_id=f"diagnostic-{uuid4().hex[:16]}", route_id=route_id,
        initial_description=description, accumulated_description=description,
        current_diagnosis=resolved_diagnosis,
        pending_clarification_questions=list(resolved_diagnosis.clarification_questions),
        status="ready_for_experiments" if resolved_diagnosis.complete else "collecting_information",
    )
    return _advance_complete_diagnosis(state, resolved_diagnosis, engine, diagnostic_adapter) if resolved_diagnosis.complete else state


def continue_diagnostic_session(state: DiagnosticSessionState, answers: dict[str, str] | None = None, *, supplemental_description: str | None = None, diagnostic_adapter: DiagnosticAdapter | None = None, use_mechanism_cards: bool = False) -> DiagnosticSessionState:
    if state.status != "collecting_information":
        raise ValueError("only a collecting_information session can be continued")
    answers = answers or {}
    question_map = clarification_question_map(state)
    normalized_answers: dict[str, str] = {}
    for key, answer in answers.items():
        question = question_map.get(key, key if key in question_map.values() else None)
        if question is None:
            raise ValueError(f"unknown clarification question id '{key}'")
        if not answer.strip():
            raise ValueError("clarification answers must be non-empty")
        normalized_answers[question] = answer.strip()
    if not normalized_answers and not (supplemental_description or "").strip():
        raise ValueError("provide at least one clarification answer or supplemental description")

    evidence = [
        f"Clarification {clarification_question_id(question)}: {answer}"
        for question, answer in normalized_answers.items()
    ]
    if supplemental_description and supplemental_description.strip():
        evidence.append(f"Supplemental description: {supplemental_description.strip()}")
    accumulated = state.accumulated_description.model_copy(update={"text": "\n\n".join([state.accumulated_description.text, *evidence])})
    engine = DiagnosticEngine(adapter=diagnostic_adapter, use_mechanism_cards=use_mechanism_cards)
    diagnosis = engine.diagnose(accumulated)
    turn_questions = list(normalized_answers) or ["supplemental_description"]
    turn_answers = normalized_answers or {"supplemental_description": supplemental_description.strip()}
    turn = DiagnosticTurn(turn_index=len(state.turns) + 1, questions=turn_questions, answers=turn_answers, evidence=evidence, diagnosis=diagnosis)
    updated = state.model_copy(update={"accumulated_description": accumulated, "turns": [*state.turns, turn], "current_diagnosis": diagnosis, "pending_clarification_questions": list(diagnosis.clarification_questions)})
    if diagnosis.complete:
        return _advance_complete_diagnosis(updated, diagnosis, engine, diagnostic_adapter)
    if len(updated.turns) >= updated.maximum_turns:
        return updated.model_copy(update={"status": "refused", "pending_clarification_questions": [], "refusal_reason": "maximum_clarification_turns_reached"})
    return updated
