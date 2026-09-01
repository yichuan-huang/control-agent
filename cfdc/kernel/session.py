"""Persistent, revisioned session state for the migrated CFDC workflow."""

from __future__ import annotations

import json
import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from uuid import uuid4

from .contracts import (
    EVIDENCE_SESSION_VERSION,
    READABLE_EVIDENCE_SESSION_VERSIONS,
    ControllerFreeze,
    TaskContract,
    fingerprint,
    utc_now,
)
from .diagnostics import DiagnosticLedger
from .multistage import MultiStagePlan

TERMINAL_STATES = frozenset({"performance_met", "capability_gap", "cancelled"})


@dataclass(frozen=True)
class SessionEvent:
    event_id: str
    action_id: str
    event_type: str
    revision_before: int
    revision_after: int
    payload: Mapping[str, Any]
    occurred_at: str
    previous_fingerprint: str | None
    event_fingerprint: str

    @classmethod
    def create(
        cls,
        *,
        event_id: str,
        action_id: str,
        event_type: str,
        revision_before: int,
        revision_after: int,
        payload: Mapping[str, Any],
        previous_fingerprint: str | None,
    ) -> SessionEvent:
        value = {
            "event_id": event_id,
            "action_id": action_id,
            "event_type": event_type,
            "revision_before": revision_before,
            "revision_after": revision_after,
            "payload": dict(payload),
            "occurred_at": utc_now(),
            "previous_fingerprint": previous_fingerprint,
        }
        return cls(**value, event_fingerprint=fingerprint(value))

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "action_id": self.action_id,
            "event_type": self.event_type,
            "revision_before": self.revision_before,
            "revision_after": self.revision_after,
            "payload": dict(self.payload),
            "occurred_at": self.occurred_at,
            "previous_fingerprint": self.previous_fingerprint,
            "event_fingerprint": self.event_fingerprint,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> SessionEvent:
        event = cls(
            event_id=str(value["event_id"]),
            action_id=str(value["action_id"]),
            event_type=str(value["event_type"]),
            revision_before=int(value["revision_before"]),
            revision_after=int(value["revision_after"]),
            payload=dict(value.get("payload") or {}),
            occurred_at=str(value["occurred_at"]),
            previous_fingerprint=value.get("previous_fingerprint"),
            event_fingerprint=str(value["event_fingerprint"]),
        )
        raw = event.to_dict()
        raw.pop("event_fingerprint")
        if fingerprint(raw) != event.event_fingerprint:
            raise ValueError("session_event_fingerprint_mismatch")
        return event


@dataclass(frozen=True)
class EvidenceSession:
    session_id: str
    task: TaskContract
    ledger: DiagnosticLedger
    status: str = "intake"
    revision: int = 0
    created_at: str = field(default_factory=utc_now)
    clarification_rounds: int = 0
    events: tuple[SessionEvent, ...] = ()
    pending_actions: tuple[Mapping[str, Any], ...] = ()
    evidence: tuple[Mapping[str, Any], ...] = ()
    protocols: tuple[Mapping[str, Any], ...] = ()
    active_protocol_fingerprint: str | None = None
    operator_handoffs: tuple[Mapping[str, Any], ...] = ()
    operator_reports: tuple[Mapping[str, Any], ...] = ()
    upload_attempts: tuple[Mapping[str, Any], ...] = ()
    # User supplied model/specification statements remain separate from public
    # measured traces and derived feature artifacts.  They are never treated as
    # verified evidence until a deterministic backend consumes them.
    parameter_facts: tuple[Mapping[str, Any], ...] = ()
    experiment_failures: tuple[Mapping[str, Any], ...] = ()
    route: Mapping[str, Any] | None = None
    route_history: tuple[Mapping[str, Any], ...] = ()
    feature_artifact: Mapping[str, Any] | None = None
    feature_history: tuple[Mapping[str, Any], ...] = ()
    controller_candidate: Mapping[str, Any] | None = None
    controller_history: tuple[Mapping[str, Any], ...] = ()
    controller_qualification: Mapping[str, Any] | None = None
    qualification_history: tuple[Mapping[str, Any], ...] = ()
    phase_plan: Mapping[str, Any] | None = None
    phase_results: tuple[Mapping[str, Any], ...] = ()
    controller_freeze: Mapping[str, Any] | None = None
    # Previous freezes remain immutable history when a bounded tuning
    # candidate is accepted.  The active freeze is always the last item in
    # ``controller_freeze`` and is never overwritten in place.
    freeze_history: tuple[Mapping[str, Any], ...] = ()
    evaluation: Mapping[str, Any] | None = None
    evaluation_packets: tuple[Mapping[str, Any], ...] = ()
    evaluation_replays: tuple[Mapping[str, Any], ...] = ()
    tuning: Mapping[str, Any] | None = None
    tuning_history: tuple[Mapping[str, Any], ...] = ()
    confirmation: Mapping[str, Any] | None = None
    confirmation_history: tuple[Mapping[str, Any], ...] = ()
    provider: Mapping[str, Any] | None = None
    provider_bindings: Mapping[str, Any] = field(default_factory=dict)
    agent_records: tuple[Mapping[str, Any], ...] = ()
    agent_config: Mapping[str, Any] | None = None
    rag_snapshot: str | None = None
    workflow_version: str = "cfdc-v6-kernel/v1"
    legacy_lineage: Mapping[str, Any] | None = None
    import_report: Mapping[str, Any] | None = None
    read_only: bool = False
    session_version: str = EVIDENCE_SESSION_VERSION
    _path: str | None = field(default=None, repr=False, compare=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_version": self.session_version,
            "session_id": self.session_id,
            "task": self.task.to_dict(),
            "diagnostic_ledger": self.ledger.to_dict(),
            "status": self.status,
            "revision": self.revision,
            "created_at": self.created_at,
            "clarification_rounds": self.clarification_rounds,
            "events": [event.to_dict() for event in self.events],
            "pending_actions": [dict(item) for item in self.pending_actions],
            "evidence": [dict(item) for item in self.evidence],
            "protocols": [dict(item) for item in self.protocols],
            "active_protocol_fingerprint": self.active_protocol_fingerprint,
            "operator_handoffs": [dict(item) for item in self.operator_handoffs],
            "operator_reports": [dict(item) for item in self.operator_reports],
            "upload_attempts": [dict(item) for item in self.upload_attempts],
            "parameter_facts": [dict(item) for item in self.parameter_facts],
            "experiment_failures": [dict(item) for item in self.experiment_failures],
            "route": dict(self.route) if self.route is not None else None,
            "route_history": [dict(item) for item in self.route_history],
            "feature_artifact": dict(self.feature_artifact)
            if self.feature_artifact is not None
            else None,
            "feature_history": [dict(item) for item in self.feature_history],
            "controller_candidate": dict(self.controller_candidate)
            if self.controller_candidate is not None
            else None,
            "controller_history": [dict(item) for item in self.controller_history],
            "controller_qualification": dict(self.controller_qualification)
            if self.controller_qualification is not None
            else None,
            "qualification_history": [
                dict(item) for item in self.qualification_history
            ],
            "phase_plan": dict(self.phase_plan)
            if self.phase_plan is not None
            else None,
            "phase_results": [dict(item) for item in self.phase_results],
            "controller_freeze": dict(self.controller_freeze)
            if self.controller_freeze is not None
            else None,
            "freeze_history": [dict(item) for item in self.freeze_history],
            "evaluation": dict(self.evaluation)
            if self.evaluation is not None
            else None,
            "evaluation_packets": [dict(item) for item in self.evaluation_packets],
            "evaluation_replays": [dict(item) for item in self.evaluation_replays],
            "tuning": dict(self.tuning) if self.tuning is not None else None,
            "tuning_history": [dict(item) for item in self.tuning_history],
            "confirmation": dict(self.confirmation)
            if self.confirmation is not None
            else None,
            "confirmation_history": [dict(item) for item in self.confirmation_history],
            "provider": dict(self.provider) if self.provider is not None else None,
            "provider_bindings": dict(self.provider_bindings),
            "agent_records": [dict(item) for item in self.agent_records],
            "agent_config": dict(self.agent_config)
            if self.agent_config is not None
            else None,
            "rag_snapshot": self.rag_snapshot,
            "workflow_version": self.workflow_version,
            "legacy_lineage": dict(self.legacy_lineage)
            if self.legacy_lineage is not None
            else None,
            "import_report": dict(self.import_report)
            if self.import_report is not None
            else None,
            "read_only": self.read_only,
        }

    def to_json(self) -> str:
        return (
            json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True, indent=2)
            + "\n"
        )

    @property
    def fingerprint(self) -> str:
        return fingerprint(self.to_dict())

    def save(self, path: Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
        try:
            with temporary.open("w", encoding="utf-8") as handle:
                handle.write(self.to_json())
                handle.flush()
                os.fsync(handle.fileno())
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)

    @classmethod
    def from_dict(
        cls, value: Mapping[str, Any], *, path: Path | None = None
    ) -> EvidenceSession:
        version = value.get("session_version")
        if version not in READABLE_EVIDENCE_SESSION_VERSIONS:
            raise ValueError("evidence_session_version_mismatch")
        task_value = dict(value["task"])
        task_value.pop("task_fingerprint", None)
        task = TaskContract.from_user_input(task_value)
        stored_task = value["task"].get("task_fingerprint")
        if stored_task is not None and stored_task != task.fingerprint:
            raise ValueError("task_contract_fingerprint_mismatch")
        ledger = DiagnosticLedger.from_dict(value["diagnostic_ledger"])
        events = tuple(SessionEvent.from_dict(item) for item in value.get("events", ()))
        _validate_event_chain(events)
        session_id = str(value["session_id"])
        controller_freeze = value.get("controller_freeze")
        historical = version != EVIDENCE_SESSION_VERSION
        if historical and controller_freeze is not None:
            _validate_historical_freeze(controller_freeze, session_id, task.fingerprint)
        if controller_freeze is not None and not historical:
            freeze = ControllerFreeze.from_mapping(controller_freeze)
            if (
                freeze.session_id != session_id
                or freeze.task_fingerprint != task.fingerprint
            ):
                raise ValueError("controller_freeze_session_binding_mismatch")
        freeze_history = tuple(dict(item) for item in value.get("freeze_history", ()))
        for previous_freeze in freeze_history:
            if historical:
                _validate_historical_freeze(
                    previous_freeze, session_id, task.fingerprint
                )
                continue
            freeze = ControllerFreeze.from_mapping(previous_freeze)
            if (
                freeze.session_id != session_id
                or freeze.task_fingerprint != task.fingerprint
            ):
                raise ValueError("controller_freeze_history_binding_mismatch")
        session = cls(
            session_id=session_id,
            task=task,
            ledger=ledger,
            status=str(value.get("status", "intake")),
            revision=int(value.get("revision", 0)),
            created_at=str(value.get("created_at") or utc_now()),
            clarification_rounds=int(value.get("clarification_rounds", 0)),
            events=events,
            pending_actions=tuple(
                dict(item) for item in value.get("pending_actions", ())
            ),
            evidence=tuple(dict(item) for item in value.get("evidence", ())),
            protocols=tuple(dict(item) for item in value.get("protocols", ())),
            active_protocol_fingerprint=(
                str(value["active_protocol_fingerprint"])
                if value.get("active_protocol_fingerprint")
                else None
            ),
            operator_handoffs=tuple(
                dict(item) for item in value.get("operator_handoffs", ())
            ),
            operator_reports=tuple(
                dict(item) for item in value.get("operator_reports", ())
            ),
            upload_attempts=tuple(
                dict(item) for item in value.get("upload_attempts", ())
            ),
            parameter_facts=tuple(
                dict(item) for item in value.get("parameter_facts", ())
            ),
            experiment_failures=tuple(
                dict(item) for item in value.get("experiment_failures", ())
            ),
            route=value.get("route"),
            route_history=tuple(dict(item) for item in value.get("route_history", ())),
            feature_artifact=value.get("feature_artifact"),
            feature_history=tuple(
                dict(item) for item in value.get("feature_history", ())
            ),
            controller_candidate=value.get("controller_candidate"),
            controller_history=tuple(
                dict(item) for item in value.get("controller_history", ())
            ),
            controller_qualification=value.get("controller_qualification"),
            qualification_history=tuple(
                dict(item) for item in value.get("qualification_history", ())
            ),
            phase_plan=value.get("phase_plan"),
            phase_results=tuple(dict(item) for item in value.get("phase_results", ())),
            controller_freeze=controller_freeze,
            freeze_history=freeze_history,
            evaluation=value.get("evaluation"),
            evaluation_packets=tuple(
                dict(item) for item in value.get("evaluation_packets", ())
            ),
            evaluation_replays=tuple(
                dict(item) for item in value.get("evaluation_replays", ())
            ),
            tuning=value.get("tuning"),
            tuning_history=tuple(
                dict(item) for item in value.get("tuning_history", ())
            ),
            confirmation=value.get("confirmation"),
            confirmation_history=tuple(
                dict(item) for item in value.get("confirmation_history", ())
            ),
            provider=value.get("provider"),
            provider_bindings=dict(value.get("provider_bindings") or {}),
            agent_records=tuple(dict(item) for item in value.get("agent_records", ())),
            agent_config=value.get("agent_config"),
            rag_snapshot=(
                str(value["rag_snapshot"])
                if value.get("rag_snapshot") is not None
                else None
            ),
            workflow_version=str(value.get("workflow_version", "cfdc-v6-kernel/v1")),
            legacy_lineage=value.get("legacy_lineage"),
            import_report=value.get("import_report"),
            read_only=historical or bool(value.get("read_only", False)),
            session_version=str(version),
            _path=str(path) if path is not None else None,
        )
        if session.phase_plan is not None and historical:
            plan_raw = dict(session.phase_plan)
            plan_digest = plan_raw.pop("plan_fingerprint", None)
            if plan_digest and fingerprint(plan_raw) != plan_digest:
                raise ValueError("historical_phase_plan_fingerprint_mismatch")
        if session.phase_plan is not None and not historical:
            plan = MultiStagePlan.from_mapping(session.phase_plan)
            if plan.task_fingerprint != task.fingerprint:
                raise ValueError("phase_plan_task_binding_mismatch")
        expected_phase_ids: list[str] = []
        if isinstance(session.phase_plan, Mapping):
            expected_phase_ids = [
                str(item.get("phase_id") or item.get("id"))
                for item in session.phase_plan.get("phases", ())
                if isinstance(item, Mapping)
                and (item.get("phase_id") or item.get("id"))
            ]
        if len(session.phase_results) > len(expected_phase_ids):
            raise ValueError("phase_result_count_invalid")
        for index, phase_value in enumerate(session.phase_results):
            if not isinstance(phase_value, Mapping):
                raise TypeError("phase_result_object_required")
            phase = dict(phase_value)
            stored_phase_fingerprint = phase.pop("result_fingerprint", None)
            if (
                not stored_phase_fingerprint
                or fingerprint(phase) != stored_phase_fingerprint
            ):
                raise ValueError("phase_result_fingerprint_mismatch")
            phase_id = str(phase.get("phase_id") or phase.get("id") or "")
            if not phase_id or (
                expected_phase_ids and phase_id != expected_phase_ids[index]
            ):
                raise ValueError("phase_result_order_invalid")
        if not events and session.revision != 0:
            raise ValueError("session_revision_does_not_match_event_chain")
        if events and events[-1].revision_after != session.revision:
            raise ValueError("session_revision_does_not_match_event_chain")
        return session

    @classmethod
    def from_json(cls, value: str, *, path: Path | None = None) -> EvidenceSession:
        return cls.from_dict(json.loads(value), path=path)


def _validate_event_chain(events: tuple[SessionEvent, ...]) -> None:
    previous: str | None = None
    expected_revision = 0
    for event in events:
        if (
            event.previous_fingerprint != previous
            or event.revision_before != expected_revision
        ):
            raise ValueError("session_event_chain_invalid")
        if event.revision_after != event.revision_before + 1:
            raise ValueError("session_event_revision_invalid")
        previous = event.event_fingerprint
        expected_revision = event.revision_after


def _validate_historical_freeze(
    value: Mapping[str, Any], session_id: str, task_fingerprint: str
) -> None:
    """Check stored integrity without upgrading historical execution authority."""
    raw = dict(value)
    supplied = raw.pop("freeze_fingerprint", None)
    if not supplied or fingerprint(raw) != supplied:
        raise ValueError("historical_freeze_fingerprint_mismatch")
    if (
        raw.get("session_id") != session_id
        or raw.get("task_fingerprint") != task_fingerprint
    ):
        raise ValueError("historical_freeze_session_binding_mismatch")
