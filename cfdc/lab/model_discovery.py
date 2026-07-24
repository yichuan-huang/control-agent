"""Revisioned state for model discovery between Stage 5 and simulation."""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping
from copy import deepcopy
from datetime import UTC, datetime
from typing import Any, Literal
from uuid import uuid4

from pydantic import Field, model_validator

from cfdc.diagnosis.llm import SimulationProposalAdapter
from cfdc.lab.contracts import ControllerRuntimeSpec
from cfdc.lab.controller_compatibility import ControllerCompatibilityResult
from cfdc.lab.model_contracts import (
    DiscoveryQuestion,
    GeneratedModelEnvelopeV1,
    ModelFactAnswer,
    ModelQuestionExampleCatalog,
    NaturalLanguageModelAnswer,
)
from cfdc.lab.model_discovery_llm import (
    ModelDiscoveryContext,
    request_model_discovery,
)
from cfdc.lab.model_questions import adopt_example_answer, load_model_question_examples
from cfdc.lab.session import (
    LLMCallRecord,
    SessionActionError,
    SimulationRunConfig,
    StaleRevisionError,
    TuningProfile,
)
from cfdc.models.schemas import (
    ArchetypeClassification,
    CFDCModel,
    ControllerCandidate,
    StructuralDiagnosis,
    SystemDescription,
)

DiscoveryState = Literal[
    "collecting_model_information",
    "model_proposed",
    "model_review",
    "controller_compatibility_check",
    "controller_replacement_review",
    "simulation_ready",
]


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _normalize_for_hash(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="json")
    if isinstance(value, dict):
        return {
            str(key): _normalize_for_hash(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, (list, tuple)):
        return [_normalize_for_hash(item) for item in value]
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite values cannot be hashed")
        return 0.0 if value == 0.0 else value
    return value


def _sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            _normalize_for_hash(value),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


class Stage5DiscoverySnapshot(CFDCModel):
    """Immutable evidence passed from controller synthesis to model discovery."""

    source_run_id: str = Field(min_length=1)
    description: SystemDescription
    diagnosis: StructuralDiagnosis
    classification: ArchetypeClassification
    initial_controller_candidate: ControllerCandidate

    @model_validator(mode="after")
    def validate_candidate_boundary(self) -> Stage5DiscoverySnapshot:
        if self.initial_controller_candidate.release_level != "candidate_unvalidated":
            raise ValueError(
                "model discovery requires an unvalidated Stage-5 controller candidate"
            )
        if self.initial_controller_candidate.status == "refuse":
            raise ValueError("a refused controller cannot start model discovery")
        return self


class DiscoveryTransitionRecord(CFDCModel):
    action: str = Field(min_length=1)
    from_state: DiscoveryState
    to_state: DiscoveryState
    revision_before: int = Field(ge=0)
    revision_after: int = Field(ge=1)
    occurred_at: str = Field(min_length=1)
    reason: str | None = Field(default=None, max_length=8000)

    @model_validator(mode="after")
    def validate_revision_step(self) -> DiscoveryTransitionRecord:
        if self.revision_after != self.revision_before + 1:
            raise ValueError("each discovery transition increments revision once")
        return self


class ModelAnswerRecord(CFDCModel):
    question_id: str = Field(min_length=1, max_length=200)
    fact_id: str = Field(min_length=1, max_length=200)
    fact_type: str = Field(min_length=1, max_length=100)
    unit_family: str = Field(min_length=1, max_length=100)
    answer_text: str = Field(min_length=1, max_length=10_000)
    source: Literal["user_supplied", "user_adopted_example"]
    typed_fact: ModelFactAnswer | None = None
    example_id: str | None = Field(default=None, min_length=1, max_length=200)
    recorded_at: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_provenance(self) -> ModelAnswerRecord:
        if self.source == "user_adopted_example":
            if (
                self.typed_fact is None
                or self.typed_fact.source != "user_adopted_example"
                or self.example_id is None
            ):
                raise ValueError(
                    "adopted answer records require the typed example fact"
                )
        elif self.example_id is not None:
            raise ValueError("user-supplied answers cannot claim an example")
        if self.typed_fact is not None and (
            self.typed_fact.fact_id != self.fact_id
            or self.typed_fact.fact_type != self.fact_type
            or self.typed_fact.unit_family != self.unit_family
            or self.typed_fact.answer_text != self.answer_text
        ):
            raise ValueError("typed fact does not match its answer record")
        return self


class ModelDiscoverySession(CFDCModel):
    schema_version: Literal["model_discovery_session/v1"] = "model_discovery_session/v1"
    session_id: str = Field(pattern=r"^discovery-[0-9a-f]{20}$")
    state: DiscoveryState
    stage5: Stage5DiscoverySnapshot
    stage5_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    current_questions: list[DiscoveryQuestion] = Field(
        default_factory=list, max_length=4
    )
    missing_fact_ids: list[str] = Field(default_factory=list, max_length=100)
    answers: list[ModelAnswerRecord] = Field(default_factory=list, max_length=200)
    answer_history: list[ModelAnswerRecord] = Field(
        default_factory=list, max_length=1000
    )
    facts: list[ModelFactAnswer] = Field(default_factory=list, max_length=200)
    model_rationale: str | None = Field(default=None, max_length=8000)
    material_requests: list[str] = Field(default_factory=list, max_length=20)
    pending_envelope: GeneratedModelEnvelopeV1 | None = None
    pending_envelope_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    confirmed_envelope: GeneratedModelEnvelopeV1 | None = None
    confirmed_envelope_sha256: str | None = Field(
        default=None, pattern=r"^[0-9a-f]{64}$"
    )
    compatibility_result: ControllerCompatibilityResult | None = None
    selected_controller: ControllerRuntimeSpec | None = None
    selected_tuning_profile: TuningProfile | None = None
    recommended_controller: ControllerRuntimeSpec | None = None
    recommended_tuning_profile: TuningProfile | None = None
    replacement_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    bound_model_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    run_config: SimulationRunConfig | None = None
    llm_calls: list[LLMCallRecord] = Field(default_factory=list)
    transition_history: list[DiscoveryTransitionRecord] = Field(default_factory=list)
    simulation_session_id: str | None = None
    revision: int = Field(ge=0)
    created_at: str = Field(min_length=1)
    updated_at: str = Field(min_length=1)
    content_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_hashes(self) -> ModelDiscoverySession:
        if self.stage5_sha256 != _sha256(self.stage5):
            raise ValueError("Stage-5 snapshot hash mismatch")
        if (self.pending_envelope is None) != (self.pending_envelope_sha256 is None):
            raise ValueError("pending envelope and hash must resolve together")
        if self.pending_envelope is not None and (
            self.pending_envelope_sha256 != _sha256(self.pending_envelope)
        ):
            raise ValueError("pending envelope hash mismatch")
        if (self.confirmed_envelope is None) != (
            self.confirmed_envelope_sha256 is None
        ):
            raise ValueError("confirmed envelope and hash must resolve together")
        if self.confirmed_envelope is not None and (
            self.confirmed_envelope_sha256 != _sha256(self.confirmed_envelope)
        ):
            raise ValueError("confirmed envelope hash mismatch")
        if (self.selected_controller is None) != (self.selected_tuning_profile is None):
            raise ValueError("selected controller/profile must resolve together")
        if (self.recommended_controller is None) != (
            self.recommended_tuning_profile is None
        ):
            raise ValueError("recommended controller/profile must resolve together")
        if (self.recommended_controller is None) != (self.replacement_sha256 is None):
            raise ValueError(
                "recommended controller and replacement hash must resolve together"
            )
        if self.bound_model_sha256 is not None and (
            self.bound_model_sha256 != self.confirmed_envelope_sha256
        ):
            raise ValueError("controller is not bound to the confirmed model hash")
        if self.state == "controller_compatibility_check" and (
            self.confirmed_envelope is None
        ):
            raise ValueError("compatibility check requires a confirmed generated model")
        if self.state == "simulation_ready" and (
            self.selected_controller is None
            or self.selected_tuning_profile is None
            or self.run_config is None
            or self.bound_model_sha256 is None
        ):
            raise ValueError(
                "simulation-ready discovery state requires a bound controller"
            )
        if self.content_sha256 is not None:
            expected = _sha256(self.model_dump(mode="json", exclude={"content_sha256"}))
            if self.content_sha256 != expected:
                raise ValueError("model-discovery session content hash mismatch")
        return self


def _rehash(payload: dict[str, Any]) -> ModelDiscoverySession:
    data = deepcopy(payload)
    data["content_sha256"] = None
    session = ModelDiscoverySession.model_validate(data)
    data["content_sha256"] = _sha256(
        session.model_dump(mode="json", exclude={"content_sha256"})
    )
    return ModelDiscoverySession.model_validate(data)


def create_model_discovery_session(
    *,
    stage5: Stage5DiscoverySnapshot,
    initial_facts: list[ModelFactAnswer] | None = None,
) -> ModelDiscoverySession:
    typed_stage5 = (
        stage5
        if isinstance(stage5, Stage5DiscoverySnapshot)
        else Stage5DiscoverySnapshot.model_validate(stage5)
    )
    now = _utc_now()
    return _rehash(
        {
            "session_id": f"discovery-{uuid4().hex[:20]}",
            "state": "collecting_model_information",
            "stage5": typed_stage5,
            "stage5_sha256": _sha256(typed_stage5),
            "facts": list(initial_facts or []),
            "revision": 0,
            "created_at": now,
            "updated_at": now,
        }
    )


def _expect_revision(session: ModelDiscoverySession, expected_revision: int) -> None:
    if expected_revision != session.revision:
        raise StaleRevisionError(
            f"stale discovery revision {expected_revision}; current={session.revision}"
        )


def _transition(
    session: ModelDiscoverySession,
    *,
    action: str,
    to_state: DiscoveryState,
    updates: dict[str, Any],
    reason: str | None = None,
) -> ModelDiscoverySession:
    payload = session.model_dump(mode="python")
    before = session.revision
    payload.update(deepcopy(updates))
    payload["state"] = to_state
    payload["revision"] = before + 1
    payload["updated_at"] = _utc_now()
    history = list(payload["transition_history"])
    history.append(
        DiscoveryTransitionRecord(
            action=action,
            from_state=session.state,
            to_state=to_state,
            revision_before=before,
            revision_after=before + 1,
            occurred_at=payload["updated_at"],
            reason=reason,
        ).model_dump(mode="python")
    )
    payload["transition_history"] = history
    return _rehash(payload)


def _question_by_id(
    session: ModelDiscoverySession, question_id: str
) -> DiscoveryQuestion:
    for question in session.current_questions:
        if question.question_id == question_id:
            return question
    raise SessionActionError(f"unknown current model question: {question_id}")


def _answer_record(
    question: DiscoveryQuestion,
    value: str | ModelFactAnswer | Mapping[str, Any],
    *,
    recorded_at: str,
) -> ModelAnswerRecord | None:
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        return ModelAnswerRecord(
            question_id=question.question_id,
            fact_id=question.fact_id,
            fact_type=question.fact_type,
            unit_family=question.unit_family,
            answer_text=text,
            source="user_supplied",
            recorded_at=recorded_at,
        )
    fact = (
        value
        if isinstance(value, ModelFactAnswer)
        else ModelFactAnswer.model_validate(value)
    )
    if (
        fact.fact_id != question.fact_id
        or fact.fact_type != question.fact_type
        or fact.unit_family != question.unit_family
    ):
        raise SessionActionError(
            "typed answer does not match its current discovery question"
        )
    if fact.source not in {"user_supplied", "user_adopted_example"}:
        raise SessionActionError(
            "interactive model answers must be user supplied or explicitly adopted"
        )
    return ModelAnswerRecord(
        question_id=question.question_id,
        fact_id=question.fact_id,
        fact_type=question.fact_type,
        unit_family=question.unit_family,
        answer_text=fact.answer_text,
        source=fact.source,
        typed_fact=fact,
        example_id=fact.example_id,
        recorded_at=recorded_at,
    )


def _replace_answer_payload(
    session: ModelDiscoverySession,
    records: list[ModelAnswerRecord],
) -> dict[str, Any]:
    current = {item.question_id: item for item in session.answers}
    facts = {item.fact_id: item for item in session.facts}
    for record in records:
        current[record.question_id] = record
        if record.typed_fact is None:
            facts.pop(record.fact_id, None)
        else:
            facts[record.fact_id] = record.typed_fact
    return {
        "answers": list(current.values()),
        "answer_history": [*session.answer_history, *records],
        "facts": list(facts.values()),
        "pending_envelope": None,
        "pending_envelope_sha256": None,
        "confirmed_envelope": None,
        "confirmed_envelope_sha256": None,
        "simulation_session_id": None,
        "compatibility_result": None,
        "selected_controller": None,
        "selected_tuning_profile": None,
        "recommended_controller": None,
        "recommended_tuning_profile": None,
        "replacement_sha256": None,
        "bound_model_sha256": None,
        "run_config": None,
        "model_rationale": None,
        "material_requests": [],
    }


def record_model_answers(
    session: ModelDiscoverySession,
    answers: Mapping[str, str | ModelFactAnswer | Mapping[str, Any]],
    *,
    expected_revision: int,
) -> ModelDiscoverySession:
    """Record plain answers without treating blank text as example adoption."""

    _expect_revision(session, expected_revision)
    if session.state != "collecting_model_information":
        raise SessionActionError(
            "model answers are only editable while collecting information"
        )
    now = _utc_now()
    records: list[ModelAnswerRecord] = []
    for question_id, value in answers.items():
        question = _question_by_id(session, question_id)
        record = _answer_record(question, value, recorded_at=now)
        if record is not None:
            records.append(record)
    if not records:
        return session
    return _transition(
        session,
        action="record_model_answers",
        to_state="collecting_model_information",
        updates=_replace_answer_payload(session, records),
        reason=f"Recorded {len(records)} model answer(s).",
    )


def adopt_model_question_example(
    session: ModelDiscoverySession,
    question_id: str,
    *,
    expected_revision: int,
    catalog: ModelQuestionExampleCatalog | None = None,
) -> ModelDiscoverySession:
    """Adopt one versioned example only after this explicit button action."""

    _expect_revision(session, expected_revision)
    if session.state != "collecting_model_information":
        raise SessionActionError(
            "examples are only adoptable while collecting information"
        )
    question = _question_by_id(session, question_id)
    now = _utc_now()
    fact = adopt_example_answer(
        question,
        catalog or load_model_question_examples(),
        adopted_at=now,
    )
    record = _answer_record(question, fact, recorded_at=now)
    assert record is not None
    return _transition(
        session,
        action="adopt_model_question_example",
        to_state="collecting_model_information",
        updates=_replace_answer_payload(session, [record]),
        reason=f"Adopted fixed example {fact.example_id}.",
    )


def request_model_for_discovery_session(
    session: ModelDiscoverySession,
    adapter: SimulationProposalAdapter,
    *,
    expected_revision: int,
    catalog: ModelQuestionExampleCatalog | None = None,
) -> ModelDiscoverySession:
    """Request one audited discovery step without binding a simulation model."""

    _expect_revision(session, expected_revision)
    if session.state != "collecting_model_information":
        raise SessionActionError(
            "model request is only legal while collecting model information"
        )
    typed_catalog = catalog or load_model_question_examples()
    context = ModelDiscoveryContext(
        description=session.stage5.description,
        diagnosis=session.stage5.diagnosis,
        classification=session.stage5.classification,
        facts=session.facts,
        natural_language_answers=[
            NaturalLanguageModelAnswer(
                question_id=answer.question_id,
                fact_id=answer.fact_id,
                fact_type=answer.fact_type,
                unit_family=answer.unit_family,
                answer_text=answer.answer_text,
            )
            for answer in session.answers
            if answer.typed_fact is None
        ],
    )
    call = request_model_discovery(adapter, context, typed_catalog)
    llm_calls = [*session.llm_calls, call.call_record]
    if call.result is None:
        errors = call.call_record.validation_errors or [
            "模型服务调用失败；已保留现有回答，请重试。"
        ]
        return _transition(
            session,
            action="request_model",
            to_state="collecting_model_information",
            updates={
                "llm_calls": llm_calls,
                "material_requests": errors,
            },
            reason=errors[0],
        )
    recognized = list(getattr(call.result, "recognized_facts", []))
    recognized_by_id = {fact.fact_id: fact for fact in recognized}
    recognized_answers = [
        answer.model_copy(update={"typed_fact": recognized_by_id[answer.fact_id]})
        if answer.fact_id in recognized_by_id
        else answer
        for answer in session.answers
    ]
    recognized_facts = {fact.fact_id: fact for fact in session.facts}
    recognized_facts.update(recognized_by_id)
    recognized_updates = {
        "answers": recognized_answers,
        "facts": list(recognized_facts.values()),
    }
    if call.result.status == "need_more":
        return _transition(
            session,
            action="request_model",
            to_state="collecting_model_information",
            updates={
                "llm_calls": llm_calls,
                "current_questions": call.result.questions,
                "missing_fact_ids": call.result.missing_fact_ids,
                "model_rationale": call.result.rationale,
                "material_requests": [],
                **recognized_updates,
            },
            reason=call.result.rationale,
        )
    if call.result.status == "ready":
        envelope = call.result.envelope
        return _transition(
            session,
            action="request_model",
            to_state="model_review",
            updates={
                "llm_calls": llm_calls,
                "current_questions": [],
                "missing_fact_ids": [],
                "pending_envelope": envelope,
                "pending_envelope_sha256": _sha256(envelope),
                "model_rationale": call.result.rationale,
                "material_requests": [],
                **recognized_updates,
            },
            reason=call.result.rationale,
        )
    return _transition(
        session,
        action="request_model",
        to_state="collecting_model_information",
        updates={
            "llm_calls": llm_calls,
            "current_questions": [],
            "missing_fact_ids": [],
            "material_requests": [
                call.result.reason,
                *call.result.next_steps,
            ][:20],
        },
        reason=call.result.reason,
    )


def confirm_generated_model(
    session: ModelDiscoverySession,
    *,
    expected_revision: int,
) -> ModelDiscoverySession:
    """Freeze the reviewed envelope before any compatibility or simulation work."""

    _expect_revision(session, expected_revision)
    if session.state != "model_review":
        raise SessionActionError(
            "generated model confirmation requires model_review state"
        )
    if session.pending_envelope is None or session.pending_envelope_sha256 is None:
        raise SessionActionError("there is no generated model to confirm")
    return _transition(
        session,
        action="confirm_generated_model",
        to_state="controller_compatibility_check",
        updates={
            "confirmed_envelope": session.pending_envelope,
            "confirmed_envelope_sha256": (session.pending_envelope_sha256),
            "material_requests": [],
        },
        reason="The user explicitly confirmed the generated software model.",
    )


def return_to_model_answers(
    session: ModelDiscoverySession,
    *,
    expected_revision: int,
) -> ModelDiscoverySession:
    """Discard model/compatibility artifacts while preserving the audit trail."""

    _expect_revision(session, expected_revision)
    if session.state == "collecting_model_information":
        raise SessionActionError(
            "the discovery session is already collecting model information"
        )
    return _transition(
        session,
        action="return_to_model_answers",
        to_state="collecting_model_information",
        updates={
            "pending_envelope": None,
            "pending_envelope_sha256": None,
            "confirmed_envelope": None,
            "confirmed_envelope_sha256": None,
            "simulation_session_id": None,
            "compatibility_result": None,
            "selected_controller": None,
            "selected_tuning_profile": None,
            "recommended_controller": None,
            "recommended_tuning_profile": None,
            "replacement_sha256": None,
            "bound_model_sha256": None,
            "run_config": None,
            "model_rationale": None,
            "material_requests": [
                "请修改已有回答，或继续请求 AI 判断还缺少哪些建模信息。"
            ],
        },
        reason="The user returned to model information collection.",
    )


__all__ = [
    "DiscoveryState",
    "DiscoveryTransitionRecord",
    "ModelAnswerRecord",
    "ModelDiscoverySession",
    "Stage5DiscoverySnapshot",
    "adopt_model_question_example",
    "confirm_generated_model",
    "create_model_discovery_session",
    "record_model_answers",
    "request_model_for_discovery_session",
    "return_to_model_answers",
]
