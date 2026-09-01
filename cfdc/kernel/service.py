"""Deterministic orchestration service for the migrated CFDC workflow."""

from __future__ import annotations

import hashlib
import json
import math
import zipfile
from collections.abc import Mapping
from copy import deepcopy
from dataclasses import replace
from datetime import UTC, datetime
from itertools import pairwise
from pathlib import Path
from threading import RLock
from typing import Any
from uuid import uuid4

from cfdc.controllers.execution import runtime_contract as controller_runtime_contract
from cfdc.controllers.kernel_synthesis import (
    synthesize_controller as synthesize_registered_controller,
)
from cfdc.controllers.qualification import (
    qualify_controller as run_controller_qualification,
)
from cfdc.evidence.ingestion import inspect_upload
from cfdc.experiments.operator import build_operator_handoff, validate_operator_report
from cfdc.experiments.protocols import (
    compile_protocol as compile_experiment_protocol,
)
from cfdc.experiments.protocols import (
    verify_protocol,
)
from cfdc.features.kernel import derive_feature_artifact
from cfdc.knowledge import REGISTRY_VERSION, feature_definitions
from cfdc.specifications.templates import default_specification_template_catalog

from .acquisition import ActionBudget, InformationAction, select_action
from .contracts import (
    DIAGNOSTIC_IDS,
    EVIDENCE_SESSION_VERSION,
    PACKET_VERSION,
    ControllerFreeze,
    TaskContract,
    fingerprint,
)
from .controllers import (
    ControllerIR,
    validate_controller_family_for_route,
    validate_controller_for_route,
)
from .diagnostics import DiagnosticLedger
from .execution_contract import execution_request, freeze_trial_manifest
from .importer import build_import_report, inspect_v3_source
from .multistage import MultiStagePlan, compile_phase_plan
from .providers import (
    EvaluationProviderRegistry,
    ProviderRegistry,
    PublicTrace,
    evidence_from_trace,
)
from .route_catalog import known_feature_ids, select_route_from_features
from .routes import resolve_route
from .session import TERMINAL_STATES, EvidenceSession, SessionEvent
from .tuning import TuningContract, run_bounded_tuning

_SESSION_SAVE_LOCK = RLock()


class WorkflowService:
    """Own task lifecycle, durable state, budgets, and deterministic routing.

    Agent adapters and RAG are intentionally dependencies of the callers, not
    authorities in this service.  This keeps a failed LLM call from changing
    the task, route, or numerical result.
    """

    def __init__(self, root: Path, *, registry_version: str = REGISTRY_VERSION) -> None:
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.registry_version = registry_version

    def start(
        self,
        payload: Mapping[str, Any] | TaskContract,
        *,
        agent_config: Mapping[str, Any] | None = None,
        rag_snapshot: str | None = None,
    ) -> EvidenceSession:
        task = (
            payload
            if isinstance(payload, TaskContract)
            else TaskContract.from_user_input(payload)
        )
        if agent_config is not None:
            configured_mode = agent_config.get("mode")
            if configured_mode is not None and str(configured_mode) not in {
                "single",
                "multi",
            }:
                raise ValueError("agent_mode_must_be_single_or_multi")
            if (
                agent_config.get("rag_enabled") is True
                and agent_config.get("rag_index_dir")
                and not rag_snapshot
            ):
                # The UI/CLI resolves and pins a snapshot before calling this
                # entry point.  Requiring that pin prevents a session from
                # silently switching CURRENT halfway through a run.
                raise ValueError("rag_snapshot_required_when_rag_enabled")
        session_id = f"cfdc-v4-{uuid4().hex[:12]}"
        session = EvidenceSession(
            session_id=session_id,
            task=task,
            ledger=DiagnosticLedger.initial(),
            pending_actions=(
                ()
                if task.budget_confirmed
                else (
                    {
                        "kind": "budget",
                        "action": "confirm_task",
                        "reason": "task_boundary_confirmation_required",
                    },
                )
            ),
            agent_config=deepcopy(dict(agent_config))
            if agent_config is not None
            else None,
            rag_snapshot=rag_snapshot,
        )
        session = self._append(
            session, "task_started", "start", {"task_fingerprint": task.fingerprint}
        )
        return self._save(session)

    def create_task(
        self,
        payload: Mapping[str, Any] | TaskContract,
        *,
        agent_config: Mapping[str, Any] | None = None,
        rag_snapshot: str | None = None,
    ) -> EvidenceSession:
        """Named public alias used by embedding applications and adapters."""

        return self.start(payload, agent_config=agent_config, rag_snapshot=rag_snapshot)

    @staticmethod
    def project(session: EvidenceSession) -> dict[str, Any]:
        """Return the shared JSON projection used by WebUI, CLI and exports."""

        value = session.to_dict()
        value["readiness_gates"] = _readiness_gates(session)
        budget = _action_budget(session)
        value["information_budget"] = {
            "budget_version": "cfdc-information-budget/v1.0",
            "attempts": budget.attempts,
            "failed_attempts": budget.failed_attempts,
            "valid_experiments": budget.valid_experiments,
            "distinct_protocols_used": len(budget.distinct_protocols),
            "distinct_protocols_limit": budget.max_distinct_experiments,
            "distinct_protocols_remaining": max(
                budget.max_distinct_experiments - len(budget.distinct_protocols), 0
            ),
            "excitation_time_used_s": budget.excitation_time_s,
            "excitation_time_limit_s": budget.max_excitation_time_s,
            "excitation_time_remaining_s": max(
                budget.max_excitation_time_s - budget.excitation_time_s, 0.0
            ),
            "failures_by_action": dict(budget.action_failures),
        }
        if (
            not value["pending_actions"]
            and value["status"] == "intake"
            and not value["task"].get("budget_confirmed", False)
            and not value.get("read_only", False)
        ):
            value["pending_actions"] = [
                {
                    "kind": "budget",
                    "action": "confirm_task",
                    "reason": "task_boundary_confirmation_required",
                }
            ]
        return value

    def read(self, session_id: str) -> EvidenceSession:
        path = self._path(session_id)
        if not path.exists():
            raise FileNotFoundError(f"unknown_session: {session_id}")
        return EvidenceSession.from_json(path.read_text(encoding="utf-8"), path=path)

    def fork_session(
        self, session_id: str, *, agent_config: Mapping[str, Any] | None = None
    ) -> EvidenceSession:
        """Derive a task and human priors, never numerical or approval authority."""
        parent = self.read(session_id)
        task_value = parent.task.to_dict(include_fingerprint=False)
        task_value["budget_confirmed"] = False
        child = self.start(
            TaskContract.from_user_input(task_value), agent_config=agent_config
        )
        human = {
            entry.id: entry.to_dict()
            for entry in parent.ledger.entries
            if entry.source == "human_operator" and entry.status in {"known", "unknown"}
        }
        ledger = (
            child.ledger.update(human, source="human_operator")
            if human
            else child.ledger
        )
        child = self._replace(
            child,
            ledger=ledger,
            legacy_lineage={
                "source_session_id": parent.session_id,
                "source_session_fingerprint": parent.fingerprint,
                "source_session_version": parent.session_version,
                "import_policy": "task_and_human_priors_only; no_experimental_or_approval_authority",
            },
        )
        return self._save(
            self._append(
                child,
                "task_derived_from_session",
                "derive-task",
                {"parent_session_id": parent.session_id},
            )
        )

    def confirm_task(
        self,
        session_id: str,
        *,
        action_id: str,
        revision: int,
        budgets: Mapping[str, Any] | None = None,
    ) -> EvidenceSession:
        """Confirm software-experiment boundaries before execution."""

        session = self.read(session_id)
        if self._event_for_action(session, action_id) is not None:
            return session
        self._check_mutable(session, revision)
        self._check_not_frozen(session)
        self._check_clarification_budget(session)
        task = session.task
        if budgets is not None:
            merged = dict(task.budgets)
            merged.update(dict(budgets))
            if (
                task.budget_confirmed
                and merged != dict(task.budgets)
                and _execution_started(session)
            ):
                raise ValueError("task_budget_immutable_after_execution")
            task = TaskContract.from_user_input(
                {
                    **task.to_dict(include_fingerprint=False),
                    "budgets": merged,
                    "budget_confirmed": True,
                }
            )
        elif not task.budget_confirmed:
            task = replace(task, budget_confirmed=True)
        updated = self._replace(
            session,
            task=task,
            status="diagnostic",
            pending_actions=({"kind": "diagnostic", "action": "submit_answer"},),
        )
        return self._save(
            self._append(
                updated,
                "task_boundaries_confirmed",
                action_id,
                {"task_fingerprint": task.fingerprint, "budgets": dict(task.budgets)},
            )
        )

    def submit_answer(
        self,
        session_id: str,
        *,
        action_id: str,
        revision: int,
        answer: Mapping[str, Any],
    ) -> EvidenceSession:
        session = self.read(session_id)
        existing = self._event_for_action(session, action_id)
        if existing is not None:
            return session
        self._check_mutable(session, revision)
        self._check_not_frozen(session)
        self._check_elapsed_budget(session)
        self._check_clarification_budget(session)
        if not action_id.strip():
            raise ValueError("action_id_required")
        if not isinstance(answer, Mapping) or not answer:
            raise ValueError("answer_required")
        updates: dict[str, Any] = {}
        for raw_key, raw_value in answer.items():
            key = _canonical_dimension(str(raw_key))
            if key not in DIAGNOSTIC_IDS:
                raise ValueError(f"unknown_diagnostic_id: {raw_key}")
            update = _answer_to_update(raw_value)
            if str(raw_key).strip() == "minimum_phase" and update.get("assessment"):
                assessment = str(update["assessment"]).casefold()
                if assessment in {"minimum_phase", "minimum", "是", "yes"}:
                    update["assessment"] = "minimum_phase"
                elif assessment in {"nonminimum_phase", "nonminimum", "否", "no"}:
                    update["assessment"] = "nonminimum_phase"
            updates[key] = update
        ledger = session.ledger.update(updates, source="human_operator")
        status = "awaiting_evidence"
        readiness = ledger.readiness()
        pending = (
            ({"kind": "route", "action": "advance"},)
            if readiness.status == "ready"
            else ({"kind": "diagnostic", "action": "submit_answer"},)
        )
        updated = self._replace(
            session,
            ledger=ledger,
            status=status,
            clarification_rounds=session.clarification_rounds + 1,
            pending_actions=pending,
        )
        # A new public diagnostic answer may change the resolved mechanism
        # class or its route.  Do not leave a previously compiled route,
        # feature artifact, phase plan, or controller candidate looking valid
        # after that revision; the historical evidence remains available, but
        # all route-dependent artifacts must be regenerated deterministically.
        if _has_route_dependents(session):
            updated = self._replace(
                updated,
                route=None,
                feature_artifact=None,
                controller_candidate=None,
                phase_plan=None,
                phase_results=(),
                provider=None,
            )
        return self._save(
            self._append(
                updated,
                "diagnostic_answered",
                action_id,
                {"dimensions": sorted(updates)},
            )
        )

    def submit_reply(
        self,
        session_id: str,
        *,
        action_id: str,
        revision: int,
        diagnostic_updates: Mapping[str, Any] | None = None,
        parameter_facts: Any = (),
        source_text: str,
        input_mode: str,
        agent_records: Any = (),
    ) -> EvidenceSession:
        """Atomically persist one validated natural-language/JSON reply.

        This boundary is intentionally narrower than ``submit_answer``: it
        accepts only already source-checked user reply data and optional audit
        records.  Public traces, features, controllers, and task boundaries
        continue through their dedicated contracts.
        """

        session = self.read(session_id)
        if self._event_for_action(session, action_id) is not None:
            return session
        self._check_mutable(session, revision)
        self._check_not_frozen(session)
        self._check_elapsed_budget(session)
        self._check_clarification_budget(session)
        pending = session.pending_actions[0] if session.pending_actions else None
        expected_action = str(
            pending.get("action") if isinstance(pending, Mapping) else ""
        ).strip()
        if expected_action not in {"submit_answer", "resolve", "answer"}:
            raise ValueError("kernel_reply_not_expected_for_current_action")
        if input_mode not in {"natural_language", "json"}:
            raise ValueError("kernel_reply_input_mode_invalid")
        source = str(source_text or "")
        if not source.strip():
            raise ValueError("kernel_reply_source_text_required")
        if diagnostic_updates is None:
            diagnostic_updates = {}
        elif not isinstance(diagnostic_updates, Mapping):
            raise TypeError("kernel_reply_diagnostic_updates_required")

        updates: dict[str, dict[str, Any]] = {}
        for raw_key, raw_value in diagnostic_updates.items():
            key = _canonical_dimension(str(raw_key))
            if key not in DIAGNOSTIC_IDS:
                raise ValueError(f"unknown_diagnostic_id: {raw_key}")
            if not isinstance(raw_value, Mapping):
                raw_value = {"status": "known", "evidence": str(raw_value)}
            value = _answer_to_update(raw_value)
            status = str(value.get("status", "known"))
            if status == "not_relevant":
                raise ValueError("not_relevant_requires_task_policy")
            if status not in {"known", "unknown"}:
                raise ValueError(f"invalid_diagnostic_status: {status}")
            evidence_values = _reply_evidence_excerpts(value)
            if not evidence_values or not all(
                _contains_verbatim_text(source, item) for item in evidence_values
            ):
                raise ValueError(
                    f"diagnostic evidence for {key} is not in the user reply"
                )
            previous = session.ledger.entry(key)
            if previous.status == "known":
                if status == "unknown":
                    raise ValueError(
                        f"diagnostic_conflict_requires_clarification: {key}"
                    )
                previous_assessment = str(previous.assessment or "").strip().casefold()
                current_assessment = (
                    str(value.get("assessment") or "").strip().casefold()
                )
                if (
                    previous_assessment
                    and current_assessment
                    and previous_assessment != current_assessment
                ):
                    raise ValueError(
                        f"diagnostic_conflict_requires_clarification: {key}"
                    )
                if (
                    previous.value is not None
                    and value.get("value") is not None
                    and previous.value != value.get("value")
                ):
                    raise ValueError(
                        f"diagnostic_conflict_requires_clarification: {key}"
                    )
                if previous_assessment and not current_assessment:
                    value["assessment"] = previous.assessment
                if previous.value is not None and value.get("value") is None:
                    value["value"] = previous.value
            value["status"] = status
            value["evidence"] = evidence_values[0]
            if len(evidence_values) > 1:
                value["evidence_excerpts"] = evidence_values
            updates[key] = value

        normalized_parameters = _validate_reply_parameter_facts(parameter_facts, source)
        existing_by_id = {
            str(item.get("fact_id")): dict(item)
            for item in session.parameter_facts
            if isinstance(item, Mapping) and item.get("fact_id")
        }
        for item in normalized_parameters:
            fact_id = str(item["fact_id"])
            previous = existing_by_id.get(fact_id)
            if previous is not None and (
                previous.get("value") != item.get("value")
                or previous.get("unit") != item.get("unit")
            ):
                raise ValueError(
                    f"parameter_conflict_requires_clarification: {fact_id}"
                )
            existing_by_id[fact_id] = item

        ledger = (
            session.ledger.update(updates, source="human_operator")
            if updates
            else session.ledger
        )
        readiness = ledger.readiness()
        pending = (
            ({"kind": "route", "action": "advance"},)
            if readiness.status == "ready"
            else ({"kind": "diagnostic", "action": "submit_answer"},)
        )
        updated = self._replace(
            session,
            ledger=ledger,
            parameter_facts=tuple(existing_by_id.values()),
            status="awaiting_evidence",
            clarification_rounds=session.clarification_rounds + 1,
            pending_actions=pending,
        )
        if updates and _has_route_dependents(session):
            updated = self._replace(
                updated,
                route=None,
                feature_artifact=None,
                controller_candidate=None,
                phase_plan=None,
                phase_results=(),
                provider=None,
            )
        records = _sanitize_reply_agent_records(agent_records)
        if records:
            updated = self._replace(
                updated, agent_records=(*session.agent_records, *records)
            )
        event_payload = {
            "input_mode": input_mode,
            "diagnostic_ids": sorted(updates),
            "parameter_ids": sorted(item["fact_id"] for item in normalized_parameters),
            "source_text": source,
        }
        return self._save(
            self._append(updated, "user_reply_recorded", action_id, event_payload)
        )

    def apply_task_relevance(
        self,
        session_id: str,
        *,
        action_id: str,
        revision: int,
        declarations: Mapping[str, str],
    ) -> EvidenceSession:
        session = self.read(session_id)
        if self._event_for_action(session, action_id) is not None:
            return session
        self._check_mutable(session, revision)
        self._check_not_frozen(session)
        ledger = session.ledger.apply_not_relevant(
            declarations,
            task_type=session.task.task_type,
            measured_signals=session.task.measured_signals,
            control_input=session.task.control_input,
        )
        updated = self._replace(session, ledger=ledger, status="awaiting_evidence")
        if _has_route_dependents(session):
            updated = self._replace(
                updated,
                route=None,
                feature_artifact=None,
                controller_candidate=None,
                phase_plan=None,
                phase_results=(),
                provider=None,
            )
        return self._save(
            self._append(
                updated,
                "diagnostic_relevance_applied",
                action_id,
                {"dimensions": sorted(declarations)},
            )
        )

    def submit_evidence(
        self,
        session_id: str,
        *,
        action_id: str,
        revision: int,
        evidence: Mapping[str, Any],
    ) -> EvidenceSession:
        session = self.read(session_id)
        if self._event_for_action(session, action_id) is not None:
            return session
        self._check_mutable(session, revision)
        self._check_not_frozen(session)
        self._check_elapsed_budget(session)
        payload = _validate_public_evidence(evidence)
        if (
            session.session_version == EVIDENCE_SESSION_VERSION
            and payload.get("kind") == "experiment"
        ):
            if not isinstance(payload.get("trace"), Mapping):
                raise ValueError("public_trace_required_for_v3_task")
            if not payload.get("trial_id"):
                raise ValueError("trial_id_required_for_v3_task")
        if any(
            item.get("evidence_id") == payload["evidence_id"]
            for item in session.evidence
        ):
            raise ValueError("evidence_already_submitted")
        budget = int(session.task.budgets.get("distinct_experiments", 4))
        used_ids = {
            str(item.get("protocol_fingerprint"))
            for item in session.evidence
            if item.get("kind") == "experiment" and item.get("protocol_fingerprint")
        }
        protocol_id = str(payload.get("protocol_fingerprint") or payload["evidence_id"])
        excitation_limit = float(
            session.task.budgets.get("cumulative_excitation_time_s", 1800.0)
        )
        used_excitation = sum(_evidence_duration(item) for item in session.evidence)
        prospective_excitation = used_excitation + _evidence_duration(payload)
        if (
            payload.get("kind") == "experiment"
            and prospective_excitation > excitation_limit + 1e-9
        ):
            updated = self._replace(
                session,
                status="capability_gap",
                pending_actions=(
                    {
                        "kind": "budget",
                        "reason": "cumulative_excitation_budget_exhausted",
                    },
                ),
            )
            return self._save(
                self._append(
                    updated,
                    "cumulative_excitation_budget_exhausted",
                    action_id,
                    {
                        "limit": excitation_limit,
                        "used": used_excitation,
                        "prospective": prospective_excitation,
                    },
                )
            )
        if (
            payload.get("kind") == "experiment"
            and protocol_id not in used_ids
            and len(used_ids) >= budget
        ):
            updated = self._replace(
                session,
                status="capability_gap",
                pending_actions=(
                    {"kind": "budget", "reason": "experiment_budget_exhausted"},
                ),
            )
            return self._save(
                self._append(
                    updated,
                    "experiment_budget_exhausted",
                    action_id,
                    {"budget": budget, "used": len(used_ids)},
                )
            )
        updated = self._replace(
            session,
            status="route_ready" if session.route is not None else "awaiting_evidence",
            evidence=(*session.evidence, payload),
            pending_actions=(
                ({"kind": "feature", "action": "submit_features"},)
                if session.route is not None
                else ()
            ),
        )
        return self._save(
            self._append(
                updated,
                "public_evidence_submitted",
                action_id,
                {"evidence_id": payload["evidence_id"], "kind": payload.get("kind")},
            )
        )

    def submit_measurement(self, session_id: str, **kwargs: Any) -> EvidenceSession:
        """Name-compatible entry point for UI/CLI measurement submissions."""

        return self.submit_evidence(session_id, **kwargs)

    def run_experiment(
        self,
        session_id: str,
        *,
        action_id: str,
        revision: int,
        provider_registry: ProviderRegistry,
        provider_id: str,
        operation: Mapping[str, Any],
    ) -> EvidenceSession:
        """Execute one explicitly registered software experiment provider."""

        session = self.read(session_id)
        if self._event_for_action(session, action_id) is not None:
            return session
        self._check_mutable(session, revision)
        self._check_not_frozen(session)
        self._check_elapsed_budget(session)
        if not session.task.budget_confirmed:
            raise ValueError("task_boundary_confirmation_required")
        if session.route is None:
            raise ValueError("route_not_resolved")
        if session.route.get("capability_gap"):
            raise ValueError(f"route_capability_gap: {session.route['capability_gap']}")
        provider = provider_registry.get(provider_id)
        operation_id = str(
            operation.get("operation") or operation.get("primitive") or ""
        )
        if not operation_id:
            raise ValueError("experiment_operation_required")
        if provider.capabilities and operation_id not in provider.capabilities:
            raise ValueError(f"provider_operation_not_supported: {operation_id}")
        retries = int(session.task.budgets.get("same_failure_retries", 1))
        previous_failures = [
            item
            for item in session.experiment_failures
            if str(item.get("operation")) == operation_id
            and str(item.get("provider_id")) == str(provider.provider_id)
        ]
        if len(previous_failures) > retries:
            raise ValueError("same_experiment_failure_retry_budget_exhausted")
        try:
            result = provider.execute(dict(operation), task=session.task.to_dict())
        except Exception as exc:
            failure = {
                "operation": operation_id,
                "provider_id": str(provider.provider_id),
                "provider_version": str(provider.provider_version),
                "failure_index": len(previous_failures) + 1,
                "error_type": type(exc).__name__,
            }
            failures = (*session.experiment_failures, failure)
            exhausted = len(previous_failures) >= retries
            updated = self._replace(
                session,
                experiment_failures=failures,
                status="capability_gap" if exhausted else "awaiting_evidence",
                pending_actions=(
                    (
                        {
                            "kind": "budget",
                            "reason": "same_experiment_failure_retry_budget_exhausted",
                        },
                    )
                    if exhausted
                    else (
                        {
                            "kind": "experiment",
                            "action": "retry",
                            "operation": operation_id,
                        },
                    )
                ),
            )
            self._save(
                self._append(
                    updated,
                    "experiment_failed",
                    action_id,
                    {
                        "operation": operation_id,
                        "provider_id": provider.provider_id,
                        "error_type": type(exc).__name__,
                        "retry_index": len(previous_failures) + 1,
                    },
                )
            )
            raise
        traces = (result,) if isinstance(result, PublicTrace) else tuple(result)
        if not traces or not all(isinstance(item, PublicTrace) for item in traces):
            raise ValueError("experiment_provider_must_return_public_trace")
        current = self.set_provider(
            session.session_id,
            action_id=f"{action_id}:provider",
            revision=session.revision,
            provider={
                "provider_id": provider.provider_id,
                "provider_version": provider.provider_version,
                "capabilities": sorted(str(item) for item in provider.capabilities),
                "operation": operation_id,
                "private_truth": False,
            },
        )
        for index, trace in enumerate(traces):
            evidence = evidence_from_trace(trace)
            evidence["provider_id"] = provider.provider_id
            evidence["provider_version"] = provider.provider_version
            evidence["operation"] = operation_id
            # Each trace is an auditable event; only the first receives the
            # caller's action id so a repeated request cannot rerun the provider.
            event_action = action_id if index == 0 else f"{action_id}:{index}"
            current = self.submit_evidence(
                current.session_id,
                action_id=event_action,
                revision=current.revision,
                evidence=evidence,
            )
        return current

    def advance(
        self, session_id: str, *, action_id: str, revision: int
    ) -> EvidenceSession:
        session = self.read(session_id)
        if self._event_for_action(session, action_id) is not None:
            return session
        self._check_mutable(session, revision)
        self._check_not_frozen(session)
        if not session.task.budget_confirmed and (
            session.status == "intake"
            or any(
                str(item.get("action") or "") == "confirm_task"
                for item in session.pending_actions
            )
        ):
            raise ValueError("task_boundary_confirmation_required")
        readiness = session.ledger.readiness()
        if readiness.status != "ready":
            information_route = _information_route(session)
            if information_route is not None:
                updated = self._replace(
                    session,
                    status="route_ready",
                    route=information_route,
                    route_history=(*session.route_history, deepcopy(information_route)),
                    pending_actions=(
                        {
                            "kind": "information_action",
                            "action": "set_provider",
                            "operation": information_route["experiment_primitives"][0],
                            "target_unknowns": information_route["target_unknowns"],
                            "reason": information_route["selection_reason"],
                        },
                    ),
                )
                return self._save(
                    self._append(
                        updated,
                        "information_action_selected",
                        action_id,
                        {
                            "operation": information_route["experiment_primitives"][0],
                            "candidate_profiles": information_route[
                                "candidate_profile_ids"
                            ],
                            "target_unknowns": information_route["target_unknowns"],
                            "selection_reason": information_route["selection_reason"],
                            "blocked_actions": information_route["blocked_actions"],
                        },
                    )
                )
            updated = self._replace(
                session,
                status="awaiting_evidence",
                pending_actions=tuple(
                    {"kind": "diagnostic", "dimension_id": item, "action": "resolve"}
                    for item in readiness.required_dimensions_not_known
                )
                or ({"kind": "diagnostic", "action": "resolve"},),
            )
            return self._save(
                self._append(updated, "advance_blocked", action_id, readiness.to_dict())
            )
        route = self._resolve_route(session.ledger)
        next_experiment = (
            None
            if route.get("capability_gap")
            else self._select_experiment_for_session(session, route)
        )
        pending = (
            ({"kind": "capability_gap", "reason": route["capability_gap"]},)
            if route.get("capability_gap")
            else (
                {
                    "kind": "experiment",
                    "action": "run_experiment",
                    "operation": next_experiment["operation"]
                    if next_experiment
                    else None,
                    "reason": next_experiment["reason"] if next_experiment else None,
                },
            )
        )
        updated = self._replace(
            session,
            status="capability_gap" if route.get("capability_gap") else "route_ready",
            route=route,
            route_history=(*session.route_history, deepcopy(route)),
            pending_actions=pending,
        )
        return self._save(
            self._append(
                updated,
                "route_resolved",
                action_id,
                {"route_id": route["route_id"], "profile_id": route["profile_id"]},
            )
        )

    def select_experiment(self, session_id: str) -> dict[str, Any]:
        """Select the next registered information action deterministically.

        This is a read-only route decision.  An agent may explain it, but the
        provider operation is selected from the frozen profile catalog and is
        never executed as a result of generated text.
        """

        session = self.read(session_id)
        if session.route is None:
            raise ValueError("route_not_resolved")
        return self._select_experiment_for_session(session, session.route)

    @staticmethod
    def _select_experiment_for_session(
        session: EvidenceSession, route: Mapping[str, Any]
    ) -> dict[str, Any]:
        operations = tuple(
            str(item) for item in route.get("experiment_primitives", ()) or ()
        )
        attempted = {
            str(item.get("operation"))
            for item in session.evidence
            if item.get("operation")
        }
        attempted.update(
            str(item.get("operation"))
            for item in session.experiment_failures
            if item.get("operation")
        )
        for operation in operations:
            if operation not in attempted:
                return {
                    "operation": operation,
                    "candidate_operations": list(operations),
                    "attempted_operations": sorted(attempted),
                    "reason": "first unattempted registered profile primitive; risk and cost remain provider-bound",
                    "authorized": False,
                }
        if operations:
            # Repeated measurements may be useful after a quality failure, but
            # the caller must explicitly request the operation again.
            return {
                "operation": operations[0],
                "candidate_operations": list(operations),
                "attempted_operations": sorted(attempted),
                "reason": "all registered primitives have been attempted; explicit repeat is required",
                "authorized": False,
            }
        raise ValueError("route_has_no_registered_experiment")

    def submit_features(
        self,
        session_id: str,
        *,
        action_id: str,
        revision: int,
        features: Mapping[str, Any],
        quality: Mapping[str, Any] | None = None,
    ) -> EvidenceSession:
        """Accept only source-bound public features after route resolution."""

        # Accept the exported artifact shape as well as the historical
        # ``features={feature_id: ...}`` call.  Keeping this adapter here means
        # WebUI, CLI and embedding callers all pass through the same
        # validation and fingerprint boundary.
        if isinstance(features, Mapping) and isinstance(
            features.get("features"), Mapping
        ):
            wrapper = dict(features)
            supplied_artifact_fingerprint = wrapper.pop("artifact_fingerprint", None)
            if quality is None and isinstance(wrapper.get("quality"), Mapping):
                quality = wrapper.get("quality")
            features = wrapper["features"]
        else:
            supplied_artifact_fingerprint = None

        session = self.read(session_id)
        if self._event_for_action(session, action_id) is not None:
            return session
        self._check_mutable(session, revision)
        if session.controller_freeze is not None:
            raise ValueError("controller_already_frozen_create_new_session")
        if session.route is None:
            raise ValueError("route_not_resolved")
        if session.route.get("capability_gap"):
            raise ValueError(f"route_capability_gap: {session.route['capability_gap']}")
        if not session.evidence:
            raise ValueError("public_evidence_required_before_features")
        if not isinstance(features, Mapping) or not features:
            raise ValueError("features_required")
        if _contains_private_marker(features):
            raise ValueError("private_feature_not_allowed")
        normalized: dict[str, Any] = {}
        evidence_ids = {str(item.get("evidence_id")) for item in session.evidence}
        for feature_id, raw in features.items():
            key = str(feature_id).strip()
            if not key:
                raise ValueError("feature_id_required")
            if key not in (
                {item.feature_id for item in feature_definitions()}
                | set(known_feature_ids())
            ):
                raise ValueError(f"unknown_feature_id: {key}")
            item = dict(raw) if isinstance(raw, Mapping) else {"value": raw}
            source_ids = tuple(
                str(value) for value in item.get("source_evidence_ids", ()) or ()
            )
            if not source_ids:
                raise ValueError(f"feature_source_required: {key}")
            if source_ids and not set(source_ids) <= evidence_ids:
                raise ValueError(f"feature_source_mismatch: {key}")
            if "value" not in item:
                raise ValueError(f"feature_value_required: {key}")
            try:
                numeric = float(item["value"])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"feature_value_invalid: {key}") from exc
            if not math.isfinite(numeric):
                raise ValueError(f"feature_value_invalid: {key}")
            normalized[key] = {
                "value": numeric,
                "unit": str(item.get("unit") or ""),
                "source_evidence_ids": list(source_ids),
                "derivation": str(
                    item.get("derivation") or "public_feature_extraction"
                ),
            }
        # v1 expert payloads used ``time_constant`` while the v3 catalog names
        # the same task-band estimate ``dominant_time_constant``.  Preserve the
        # public source binding when normalizing that contract alias.
        if "time_constant" in normalized and "dominant_time_constant" not in normalized:
            normalized["dominant_time_constant"] = {
                **deepcopy(normalized["time_constant"]),
                "derivation": "canonical_alias_of_time_constant",
            }
        required = {str(item) for item in session.route.get("feature_ids", ())}
        missing = sorted(required - set(normalized))
        if quality is not None and not isinstance(quality, Mapping):
            raise TypeError("feature_quality_object_required")
        quality_value = dict(quality or {"passed": not missing})
        if "passed" in quality_value and not isinstance(quality_value["passed"], bool):
            raise ValueError("feature_quality_passed_must_be_boolean")
        if not bool(quality_value.get("passed", False)):
            status = "awaiting_evidence"
            pending = ({"kind": "evidence_quality", "missing": missing},)
        elif missing:
            status = "awaiting_evidence"
            pending = ({"kind": "feature", "missing": missing},)
        else:
            status = "controller_pending"
            pending = ({"kind": "controller", "action": "submit_controller"},)
        artifact = {
            "features": normalized,
            "required_feature_ids": sorted(required),
            "missing_feature_ids": missing,
            "quality": quality_value,
            "evidence_fingerprints": [
                str(item.get("fingerprint")) for item in session.evidence
            ],
            "artifact_fingerprint": fingerprint(
                {"features": normalized, "quality": quality_value}
            ),
        }
        if (
            supplied_artifact_fingerprint is not None
            and str(supplied_artifact_fingerprint) != artifact["artifact_fingerprint"]
        ):
            raise ValueError("feature_artifact_fingerprint_mismatch")
        updated = self._replace(
            session,
            feature_artifact=artifact,
            feature_history=(*session.feature_history, deepcopy(artifact)),
            status=status,
            pending_actions=pending,
        )
        return self._save(
            self._append(
                updated,
                "features_submitted",
                action_id,
                {
                    "missing": missing,
                    "quality_passed": bool(quality_value.get("passed", False)),
                },
            )
        )

    def submit_controller(
        self,
        session_id: str,
        *,
        action_id: str,
        revision: int,
        controller: Mapping[str, Any] | ControllerIR,
        phases: tuple[Mapping[str, Any], ...] | list[Mapping[str, Any]] | None = None,
    ) -> EvidenceSession:
        session = self.read(session_id)
        if self._event_for_action(session, action_id) is not None:
            return session
        self._check_mutable(session, revision)
        if session.controller_freeze is not None:
            raise ValueError("controller_already_frozen_create_new_session")
        if session.route is None:
            raise ValueError("route_not_resolved")
        if session.route.get("capability_gap"):
            raise ValueError(f"route_capability_gap: {session.route['capability_gap']}")
        if session.feature_artifact is not None and session.feature_artifact.get(
            "missing_feature_ids"
        ):
            raise ValueError("required_features_missing")
        ir = (
            controller
            if isinstance(controller, ControllerIR)
            else ControllerIR.from_mapping(controller)
        )
        validation = validate_controller_for_route(ir, session.route)
        if not set(session.task.measured_signals) <= set(ir.measured_signals):
            raise ValueError("controller_measured_signal_binding_mismatch")
        required_inputs = set(
            session.task.control_inputs or (session.task.control_input,)
        )
        if not required_inputs <= set(ir.control_inputs):
            raise ValueError("controller_control_input_binding_mismatch")
        if (
            session.task.input_min is not None
            and ir.output_bounds is not None
            and ir.output_bounds[0] < session.task.input_min
        ):
            raise ValueError("controller_output_bounds_exceed_task_bounds")
        if (
            session.task.input_max is not None
            and ir.output_bounds is not None
            and ir.output_bounds[1] > session.task.input_max
        ):
            raise ValueError("controller_output_bounds_exceed_task_bounds")
        phase_plan = compile_phase_plan(
            session.task, session.route, controller=ir.to_dict(), phases=phases
        )
        candidate = {
            "ir": ir.to_dict(),
            "validation": validation,
            "phase_plan": phase_plan.to_dict(),
        }
        updated = self._replace(
            session,
            controller_candidate=candidate,
            controller_history=(*session.controller_history, deepcopy(candidate)),
            phase_plan=phase_plan.to_dict(),
            status="controller_candidate_ready",
            pending_actions=(
                {"kind": "qualification", "action": "qualify_controller"},
            ),
        )
        return self._save(
            self._append(
                updated,
                "controller_candidate_submitted",
                action_id,
                {
                    "controller_fingerprint": ir.fingerprint,
                    "phase_plan_fingerprint": phase_plan.fingerprint,
                },
            )
        )

    def set_provider(
        self,
        session_id: str,
        *,
        action_id: str,
        revision: int,
        provider: Mapping[str, Any],
    ) -> EvidenceSession:
        session = self.read(session_id)
        if self._event_for_action(session, action_id) is not None:
            return session
        self._check_mutable(session, revision)
        self._check_not_frozen(session)
        if (
            not isinstance(provider, Mapping)
            or not provider.get("provider_id")
            or not str(provider.get("provider_version") or "").strip()
        ):
            raise ValueError("provider_contract_required")
        provider_public = dict(provider)
        provider_public.pop("private_truth", None)
        if provider.get("private_truth") is True or _contains_private_marker(
            provider_public
        ):
            raise ValueError("private_provider_not_allowed")
        capabilities = provider.get("capabilities", ())
        if not isinstance(capabilities, (list, tuple, set, frozenset)):
            raise TypeError("provider_capabilities_must_be_collection")
        binding_role = str(provider_public.pop("binding_role", "identification"))
        if binding_role not in {"identification", "evaluation"}:
            raise ValueError("provider_binding_role_invalid")
        provider_public["binding_role"] = binding_role
        bindings = {
            **session.provider_bindings,
            binding_role: deepcopy(provider_public),
        }
        updated = self._replace(
            session,
            provider=deepcopy(provider_public)
            if binding_role == "identification"
            else session.provider,
            provider_bindings=bindings,
        )
        return self._save(
            self._append(
                updated,
                "provider_bound",
                action_id,
                {"provider_id": provider["provider_id"], "binding_role": binding_role},
            )
        )

    def compile_protocol(
        self,
        session_id: str,
        *,
        action_id: str,
        revision: int,
        request: Mapping[str, Any] | None = None,
        phase: Mapping[str, Any] | None = None,
    ) -> EvidenceSession:
        session = self.read(session_id)
        if self._event_for_action(session, action_id) is not None:
            return session
        self._check_mutable(session, revision)
        self._check_not_frozen(session)
        if session.route is None:
            raise ValueError("route_not_resolved")
        provider = session.provider_bindings.get("identification") or session.provider
        if not isinstance(provider, Mapping):
            raise TypeError("identification_provider_required")
        protocol = compile_experiment_protocol(
            session.task,
            session.route,
            provider=provider,
            request=request or session.route.get("experiment_request"),
            phase=phase,
        ).to_dict()
        software_provider = str(provider.get("execution_kind") or "") == "software"
        updated = self._replace(
            session,
            protocols=(*session.protocols, protocol),
            active_protocol_fingerprint=protocol["protocol_fingerprint"],
            status="protocol_ready",
            pending_actions=(
                ({"kind": "provider_run", "action": "run_provider"},)
                if software_provider
                else (
                    {"kind": "operator_handoff", "action": "prepare_operator_handoff"},
                )
            ),
        )
        return self._save(
            self._append(
                updated,
                "experiment_protocol_compiled",
                action_id,
                {
                    "protocol_fingerprint": protocol["protocol_fingerprint"],
                    "operation": protocol["operation"],
                },
            )
        )

    def run_provider(
        self,
        session_id: str,
        *,
        action_id: str,
        revision: int,
        provider_registry: ProviderRegistry,
        provider_id: str | None = None,
    ) -> EvidenceSession:
        """Execute the active protocol after recompiling all public bindings."""

        session = self.read(session_id)
        if self._event_for_action(session, action_id) is not None:
            return session
        self._check_mutable(session, revision)
        self._check_not_frozen(session)
        self._check_elapsed_budget(session)
        if not session.task.budget_confirmed:
            raise ValueError("task_boundary_confirmation_required")
        if (
            session.route is None
            or not session.protocols
            or not session.active_protocol_fingerprint
        ):
            raise ValueError("route_and_compiled_protocol_required")
        binding = session.provider_bindings.get("identification") or session.provider
        if not isinstance(binding, Mapping):
            raise TypeError("identification_provider_required")
        selected_id = str(provider_id or binding.get("provider_id") or "")
        if selected_id != str(binding.get("provider_id") or ""):
            raise ValueError("identification_provider_binding_mismatch")
        provider = provider_registry.get(selected_id)
        if str(provider.provider_version) != str(binding.get("provider_version") or ""):
            raise ValueError("identification_provider_version_mismatch")
        protocol = next(
            item
            for item in reversed(session.protocols)
            if item.get("protocol_fingerprint") == session.active_protocol_fingerprint
        )
        verified = verify_protocol(
            protocol,
            task=session.task,
            route=session.route,
            provider=binding,
        ).to_dict()
        if verified["protocol_fingerprint"] != session.active_protocol_fingerprint:
            raise ValueError("active_protocol_fingerprint_mismatch")
        declared_capabilities = sorted(str(item) for item in provider.capabilities)
        if fingerprint(declared_capabilities) != protocol.get(
            "provider_capabilities_fingerprint"
        ):
            raise ValueError("provider_capabilities_changed_after_protocol_compile")
        budget = _action_budget(session)
        try:
            budget.reserve(
                str(protocol["operation"]),
                protocol_fingerprint=str(protocol["protocol_fingerprint"]),
                excitation_time_s=float(
                    protocol["derived_limits"]["cumulative_excitation_time_s"]
                ),
            )
        except ValueError as exc:
            updated = self._replace(
                session,
                status="capability_gap",
                pending_actions=({"kind": "budget", "reason": str(exc)},),
            )
            return self._save(
                self._append(
                    updated,
                    "experiment_budget_exhausted",
                    action_id,
                    {
                        "reason": str(exc),
                        "protocol_fingerprint": protocol["protocol_fingerprint"],
                    },
                )
            )
        reserved = self._save(
            self._append(
                session,
                "experiment_attempt_reserved",
                f"{action_id}:reservation",
                {
                    "requested_action_id": action_id,
                    "operation": protocol["operation"],
                    "protocol_fingerprint": protocol["protocol_fingerprint"],
                    "excitation_time_s": protocol["derived_limits"][
                        "cumulative_excitation_time_s"
                    ],
                },
            )
        )
        try:
            result = provider.execute(verified, task=reserved.task.to_dict())
            traces = (result,) if isinstance(result, PublicTrace) else tuple(result)
            if not traces or not all(isinstance(item, PublicTrace) for item in traces):
                raise ValueError("experiment_provider_must_return_public_trace")
            if len(traces) != int(protocol["repeats"]):
                raise ValueError("provider_repeat_count_mismatch")
            if any(
                item.protocol_fingerprint != protocol["protocol_fingerprint"]
                for item in traces
            ):
                raise ValueError("provider_trace_protocol_binding_mismatch")
            if len({item.trial_id for item in traces}) != len(traces):
                raise ValueError("provider_trial_id_duplicate")
        except Exception as exc:
            failure = {
                "operation": protocol["operation"],
                "provider_id": provider.provider_id,
                "provider_version": provider.provider_version,
                "error_type": type(exc).__name__,
                "protocol_fingerprint": protocol["protocol_fingerprint"],
            }
            updated = self._replace(
                reserved,
                experiment_failures=(*session.experiment_failures, failure),
                status="awaiting_evidence",
                pending_actions=(
                    {
                        "kind": "provider_run",
                        "action": "run_provider",
                        "reason": "provider_failed",
                    },
                ),
            )
            self._save(self._append(updated, "provider_run_failed", action_id, failure))
            raise
        current = reserved
        for index, trace in enumerate(traces):
            evidence = evidence_from_trace(trace)
            evidence.update(
                provider_id=provider.provider_id,
                provider_version=provider.provider_version,
                operation=protocol["operation"],
            )
            current = self.submit_evidence(
                session_id,
                action_id=action_id if index == 0 else f"{action_id}:{index}",
                revision=current.revision,
                evidence=evidence,
            )
        return current

    def prepare_operator_handoff(
        self,
        session_id: str,
        *,
        action_id: str,
        revision: int,
        output_dir: Path | None = None,
    ) -> EvidenceSession:
        session = self.read(session_id)
        if self._event_for_action(session, action_id) is not None:
            return session
        self._check_mutable(session, revision)
        if not session.protocols or not session.active_protocol_fingerprint:
            raise ValueError("compiled_protocol_required")
        protocol = next(
            item
            for item in reversed(session.protocols)
            if item.get("protocol_fingerprint") == session.active_protocol_fingerprint
        )
        artifact_dir = (
            Path(output_dir)
            if output_dir is not None
            else self.root
            / f"{session.session_id}.artifacts"
            / protocol["protocol_fingerprint"][:12]
        )
        result = build_operator_handoff(
            session_id=session.session_id,
            task=session.task.to_dict(),
            protocol=protocol,
            output_dir=artifact_dir,
        )
        record = {
            **result["handoff"],
            "operator_card_path": result["operator_card_path"],
            "precheck_checklist_path": result["precheck_checklist_path"],
            "template_paths": result["template_paths"],
            "bundle_path": result["bundle_path"],
        }
        updated = self._replace(
            session,
            operator_handoffs=(*session.operator_handoffs, record),
            status="awaiting_operator_report",
            pending_actions=(
                {"kind": "operator_report", "action": "record_operator_report"},
            ),
        )
        return self._save(
            self._append(
                updated,
                "operator_handoff_prepared",
                action_id,
                {
                    "handoff_fingerprint": record["handoff_fingerprint"],
                    "protocol_fingerprint": protocol["protocol_fingerprint"],
                },
            )
        )

    def record_operator_report(
        self,
        session_id: str,
        *,
        action_id: str,
        revision: int,
        report: Mapping[str, Any],
    ) -> EvidenceSession:
        session = self.read(session_id)
        if self._event_for_action(session, action_id) is not None:
            return session
        self._check_mutable(session, revision)
        if not session.operator_handoffs:
            raise ValueError("operator_handoff_required")
        normalized = validate_operator_report(report, session.operator_handoffs[-1])
        decision = normalized["decision"]
        if decision == "accepted":
            status = "awaiting_evidence"
            pending = ({"kind": "upload", "action": "ingest_upload"},)
        elif decision == "needs_clarification":
            status = "awaiting_operator_report"
            pending = (
                {
                    "kind": "operator_report",
                    "action": "record_operator_report",
                    "reason": "operator_requested_clarification",
                },
            )
        else:
            status = "awaiting_provider"
            pending = (
                {
                    "kind": "provider",
                    "action": "set_provider",
                    "reason": "operator_refused_protocol",
                },
            )
        updated = self._replace(
            session,
            operator_reports=(*session.operator_reports, normalized),
            status=status,
            pending_actions=pending,
        )
        return self._save(
            self._append(
                updated,
                "operator_report_recorded",
                action_id,
                {
                    "decision": decision,
                    "report_fingerprint": normalized["report_fingerprint"],
                },
            )
        )

    def ingest_upload(
        self,
        session_id: str,
        *,
        action_id: str,
        revision: int,
        paths: tuple[Path, ...] | list[Path],
        stopped_on_limit: bool = False,
    ) -> EvidenceSession:
        session = self.read(session_id)
        if self._event_for_action(session, action_id) is not None:
            return session
        self._check_mutable(session, revision)
        self._check_not_frozen(session)
        if not session.protocols or not session.active_protocol_fingerprint:
            raise ValueError("compiled_protocol_required")
        protocol = next(
            item
            for item in reversed(session.protocols)
            if item.get("protocol_fingerprint") == session.active_protocol_fingerprint
        )
        report = session.operator_reports[-1] if session.operator_reports else None
        result = inspect_upload(
            [Path(item) for item in paths],
            session_id=session.session_id,
            protocol=protocol,
            operator_report=report,
            stopped_on_limit=stopped_on_limit,
        )
        audit = result["audit"]
        if audit["status"] != "accepted":
            updated = self._replace(
                session,
                upload_attempts=(*session.upload_attempts, audit),
                status="awaiting_evidence",
                pending_actions=(
                    {
                        "kind": "upload",
                        "action": "ingest_upload",
                        "failed_gate": audit["failed_gate"],
                        "redo": next(
                            item["redo"]
                            for item in audit["gates"]
                            if item["id"] == audit["failed_gate"]
                        ),
                    },
                ),
            )
            return self._save(
                self._append(
                    updated,
                    "upload_rejected",
                    action_id,
                    {
                        "upload_fingerprint": audit["upload_fingerprint"],
                        "failed_gate": audit["failed_gate"],
                    },
                )
            )
        new_evidence = list(session.evidence)
        for trace_value in result["traces"]:
            trace = PublicTrace.from_mapping(trace_value)
            payload = evidence_from_trace(trace)
            payload["source"] = "user_upload"
            payload["operation"] = protocol["operation"]
            payload["provider_id"] = (session.provider or {}).get("provider_id")
            new_evidence.append(_validate_public_evidence(payload))
        updated = self._replace(
            session,
            upload_attempts=(*session.upload_attempts, audit),
            evidence=tuple(new_evidence),
            status="route_ready",
            pending_actions=({"kind": "feature", "action": "derive_features"},),
        )
        return self._save(
            self._append(
                updated,
                "upload_accepted",
                action_id,
                {
                    "upload_fingerprint": audit["upload_fingerprint"],
                    "evidence_ids": [
                        item["evidence_id"]
                        for item in new_evidence[len(session.evidence) :]
                    ],
                },
            )
        )

    def derive_features(
        self, session_id: str, *, action_id: str, revision: int
    ) -> EvidenceSession:
        session = self.read(session_id)
        if self._event_for_action(session, action_id) is not None:
            return session
        self._check_mutable(session, revision)
        if session.route is None or not session.evidence:
            raise ValueError("route_and_public_evidence_required")
        artifact = derive_feature_artifact(session.evidence, session.route).to_dict()
        revised_route = select_route_from_features(
            artifact, session.task.to_dict(), prior_route=dict(session.route)
        )
        revised_required = {str(item) for item in revised_route.get("feature_ids", ())}
        missing = sorted(revised_required - set(artifact.get("features", {})))
        artifact["required_feature_ids"] = sorted(revised_required)
        artifact["missing_feature_ids"] = missing
        artifact["quality"] = {
            **dict(artifact.get("quality") or {}),
            "passed": bool(
                (artifact.get("quality") or {}).get("passed", False) and not missing
            ),
        }
        artifact.pop("artifact_fingerprint", None)
        artifact["artifact_fingerprint"] = fingerprint(artifact)
        passed = bool((artifact.get("quality") or {}).get("passed", False))
        route_gap = revised_route.get("capability_gap")
        revised_ledger = _ledger_from_public_features(session.ledger, artifact)
        updated = self._replace(
            session,
            ledger=revised_ledger,
            route=revised_route,
            route_history=(*session.route_history, deepcopy(revised_route)),
            feature_artifact=artifact,
            feature_history=(*session.feature_history, deepcopy(artifact)),
            status="controller_pending"
            if passed and not missing and not route_gap
            else ("capability_gap" if route_gap else "awaiting_evidence"),
            pending_actions=(
                ({"kind": "controller", "action": "synthesize_controller"},)
                if passed and not missing and not route_gap
                else (
                    ({"kind": "route_gap", "reason": route_gap},)
                    if route_gap
                    else ({"kind": "feature", "missing": missing},)
                )
            ),
        )
        return self._save(
            self._append(
                updated,
                "features_derived",
                action_id,
                {
                    "artifact_fingerprint": artifact["artifact_fingerprint"],
                    "missing": missing,
                    "quality_passed": passed,
                    "previous_route_id": session.route.get("route_id"),
                    "revised_route_id": revised_route.get("route_id"),
                    "route_revision_reason": revised_route.get("selection_basis"),
                },
            )
        )

    def synthesize_controller(
        self, session_id: str, *, action_id: str, revision: int
    ) -> EvidenceSession:
        session = self.read(session_id)
        if self._event_for_action(session, action_id) is not None:
            return session
        self._check_mutable(session, revision)
        if session.route is None or session.feature_artifact is None:
            raise ValueError("route_and_features_required")
        ir, synthesis_audit = synthesize_registered_controller(
            session.task.to_dict(),
            session.route,
            session.feature_artifact,
        )
        current = self.submit_controller(
            session_id,
            action_id=action_id,
            revision=revision,
            controller=ir,
        )
        candidate = {
            **dict(current.controller_candidate or {}),
            "synthesis_audit": synthesis_audit,
        }
        return self._save(
            self._replace(
                current,
                controller_candidate=candidate,
                controller_history=(
                    *current.controller_history[:-1],
                    deepcopy(candidate),
                ),
            )
        )

    def qualify_controller(
        self, session_id: str, *, action_id: str, revision: int
    ) -> EvidenceSession:
        session = self.read(session_id)
        if self._event_for_action(session, action_id) is not None:
            return session
        self._check_mutable(session, revision)
        if (
            session.controller_candidate is None
            or session.feature_artifact is None
            or session.route is None
        ):
            raise ValueError("controller_candidate_and_features_required")
        if not session.protocols or not session.active_protocol_fingerprint:
            raise ValueError("compiled_protocol_required")
        protocol = next(
            item
            for item in reversed(session.protocols)
            if item.get("protocol_fingerprint") == session.active_protocol_fingerprint
        )
        ir = ControllerIR.from_mapping(session.controller_candidate["ir"])
        qualification = run_controller_qualification(
            ir,
            task=session.task.to_dict(),
            route=session.route,
            feature_artifact=session.feature_artifact,
            protocol=protocol,
        )
        qualified = qualification["status"] == "offline_qualified"
        updated = self._replace(
            session,
            controller_qualification=qualification,
            qualification_history=(
                *session.qualification_history,
                deepcopy(qualification),
            ),
            status="controller_qualified" if qualified else "capability_gap",
            pending_actions=({"kind": "freeze", "action": "freeze_controller"},)
            if qualified
            else ({"kind": "qualification_gap", "reason": qualification["reasons"]},),
        )
        return self._save(
            self._append(
                updated,
                "controller_qualification_recorded",
                action_id,
                {
                    "status": qualification["status"],
                    "qualification_fingerprint": qualification[
                        "qualification_fingerprint"
                    ],
                },
            )
        )

    def record_phase_result(
        self,
        session_id: str,
        *,
        action_id: str,
        revision: int,
        result: Mapping[str, Any],
    ) -> EvidenceSession:
        """Record one public multi-stage phase observation after freeze.

        The method is intentionally a data boundary.  It records named entry,
        exit, safety and handoff observations; it never evaluates a condition
        string or executes controller code.  Full-task acceptance remains the
        independent judge's responsibility.
        """

        session = self.read(session_id)
        if self._event_for_action(session, action_id) is not None:
            return session
        self._check_mutable(session, revision)
        self._check_elapsed_budget(session)
        if session.controller_freeze is None or not session.phase_plan:
            raise ValueError("phase_result_requires_frozen_controller")
        if not isinstance(result, Mapping):
            raise TypeError("phase_result_object_required")
        if _contains_private_marker(result):
            raise ValueError("private_phase_result_not_allowed")
        phase_id = str(result.get("phase_id") or result.get("id") or "").strip()
        phases = session.phase_plan.get("phases", ())
        expected_ids = [
            str(item.get("phase_id") or item.get("id"))
            for item in phases
            if isinstance(item, Mapping) and (item.get("phase_id") or item.get("id"))
        ]
        if phase_id not in expected_ids:
            raise ValueError("phase_result_unknown_phase")
        if any(str(item.get("phase_id")) == phase_id for item in session.phase_results):
            raise ValueError("phase_result_already_recorded")
        next_index = len(session.phase_results)
        if next_index >= len(expected_ids) or phase_id != expected_ids[next_index]:
            raise ValueError("phase_result_order_mismatch")
        phase = dict(result)
        phase["phase_id"] = phase_id
        # Accept the archive's public observation spellings at this boundary,
        # then require the canonical booleans before the result can advance the
        # phase cursor.  No condition string is evaluated here.
        if "entry_condition_met" not in phase and "entry_passed" in phase:
            phase["entry_condition_met"] = phase["entry_passed"]
        if "exit_condition_met" not in phase and "exit_passed" in phase:
            phase["exit_condition_met"] = phase["exit_passed"]
        if "success" not in phase and "status" in phase:
            phase["success"] = str(phase["status"]).casefold() in {
                "completed",
                "passed",
                "success",
            }
        required_fields = ("entry_condition_met", "exit_condition_met", "success")
        missing_fields = [
            field_name for field_name in required_fields if field_name not in phase
        ]
        if missing_fields:
            raise ValueError(
                "phase_result_fields_required: " + ", ".join(missing_fields)
            )
        for field_name in (
            "entry_condition_met",
            "exit_condition_met",
            "success",
            "safety_failure",
            "stopped_on_limit",
            "hard_failure",
            "safety_violation",
            "constraint_violation",
        ):
            if field_name in phase and not isinstance(phase[field_name], bool):
                raise ValueError(f"phase_result_{field_name}_must_be_boolean")
        timeout = None
        phase_spec = (
            phases[next_index]
            if next_index < len(phases) and isinstance(phases[next_index], Mapping)
            else {}
        )
        try:
            timeout = float(
                phase_spec.get("timeout_s", phase_spec.get("max_duration_s"))
            )
        except (TypeError, ValueError):
            timeout = None
        duration = phase.get("duration_s", phase.get("elapsed_s"))
        if duration is not None:
            try:
                duration_value = float(duration)
            except (TypeError, ValueError) as exc:
                raise ValueError("phase_result_duration_invalid") from exc
            if (
                not math.isfinite(duration_value)
                or duration_value < 0
                or (timeout is not None and duration_value > timeout + 1e-9)
            ):
                raise ValueError("phase_result_timeout_exceeded")
            phase["duration_s"] = duration_value
        phase["result_fingerprint"] = fingerprint(
            {key: value for key, value in phase.items() if key != "result_fingerprint"}
        )
        failures = bool(
            phase.get("safety_failure")
            or phase.get("stopped_on_limit")
            or phase.get("hard_failure")
            or phase.get("safety_violation")
            or phase.get("constraint_violation")
            or phase.get("entry_condition_met") is False
            or phase.get("exit_condition_met") is False
            or phase.get("success") is False
        )
        phase_results = (*session.phase_results, phase)
        updated = self._replace(
            session,
            phase_results=phase_results,
            status="capability_gap"
            if failures
            else (
                "phase_executing"
                if len(phase_results) < len(expected_ids)
                else "controller_ready"
            ),
            pending_actions=(
                (
                    {
                        "kind": "phase",
                        "action": "record_phase_result",
                        "phase_id": expected_ids[len(phase_results)],
                    },
                )
                if not failures and len(phase_results) < len(expected_ids)
                else (
                    ({"kind": "evaluation", "action": "record_evaluation"},)
                    if not failures
                    else ({"kind": "capability_gap", "reason": "phase_result_failed"},)
                )
            ),
        )
        return self._save(
            self._append(
                updated,
                "phase_result_recorded",
                action_id,
                {
                    "phase_id": phase_id,
                    "result_fingerprint": phase["result_fingerprint"],
                    "failed": failures,
                },
            )
        )

    def record_agent_execution(
        self,
        session_id: str,
        *,
        action_id: str,
        revision: int,
        record: Mapping[str, Any],
    ) -> EvidenceSession:
        """Persist role/RAG/audit metadata separately from business payloads."""

        session = self.read(session_id)
        if self._event_for_action(session, action_id) is not None:
            return session
        self._check_mutable(session, revision)
        if not isinstance(record, Mapping) or not record.get("role"):
            raise ValueError("agent_record_required")
        if _contains_private_marker(record):
            raise ValueError("agent_record_secret_not_allowed")
        # Agent records are audit data, not a second business payload.  Apply
        # the repository's credential/url sanitizer before persistence so
        # provider messages cannot leak API keys or bearer values into a
        # session export.  Private-truth markers were rejected above rather
        # than silently redacted because they would also violate the evidence
        # boundary.
        from cfdc.lab.llm import sanitize_for_audit

        sanitized = sanitize_for_audit(deepcopy(dict(record)))
        role_value = (
            getattr(record.get("role"), "value", str(record.get("role")))
            .strip()
            .casefold()
        )
        if role_value not in {"diagnosis", "modeling", "controller", "critic"}:
            raise ValueError("agent_role_not_allowed")
        sanitized["role"] = role_value
        sanitized.pop("payload", None)
        sanitized["record_fingerprint"] = fingerprint(sanitized)
        updated = self._replace(
            session, agent_records=(*session.agent_records, sanitized)
        )
        return self._save(
            self._append(
                updated,
                "agent_execution_recorded",
                action_id,
                {
                    "role": role_value,
                    "stage": record.get("stage"),
                    "record_fingerprint": sanitized["record_fingerprint"],
                },
            )
        )

    def execute_agent(
        self,
        session_id: str,
        *,
        action_id: str,
        revision: int,
        coordinator: Any,
        role: Any,
        operation: str,
        task_payload: Mapping[str, Any] | None = None,
        feedback: str | None = None,
    ) -> EvidenceSession:
        """Run one role-scoped agent and persist only its audit metadata.

        The coordinator is deliberately supplied by the embedding layer so a
        missing LLM or RAG index cannot silently become a business decision.
        Agent output is never merged into task facts by this method.
        """

        session = self.read(session_id)
        if self._event_for_action(session, action_id) is not None:
            return session
        self._check_mutable(session, revision)
        record = coordinator.execute(
            session,
            role=role,
            operation=operation,
            task_payload=task_payload,
            feedback=feedback,
            revision=revision,
        )
        if hasattr(record, "__dict__"):
            value = dict(record.__dict__)
            value["role"] = getattr(record.role, "value", str(record.role))
        elif isinstance(record, Mapping):
            value = dict(record)
        else:
            raise TypeError("agent_coordinator_record_required")
        return self.record_agent_execution(
            session_id,
            action_id=action_id,
            revision=revision,
            record=value,
        )

    def cancel(
        self,
        session_id: str,
        *,
        action_id: str,
        revision: int,
        reason: str = "operator_cancelled",
    ) -> EvidenceSession:
        session = self.read(session_id)
        if self._event_for_action(session, action_id) is not None:
            return session
        self._check_mutable(session, revision)
        updated = self._replace(session, status="cancelled", pending_actions=())
        return self._save(
            self._append(
                updated, "session_cancelled", action_id, {"reason": str(reason)}
            )
        )

    def freeze_controller(
        self,
        session_id: str,
        *,
        action_id: str,
        revision: int,
        controller: Mapping[str, Any] | None = None,
        runtime_contract: Mapping[str, Any] | None = None,
        evaluation_contract: Mapping[str, Any] | None = None,
    ) -> EvidenceSession:
        session = self.read(session_id)
        if self._event_for_action(session, action_id) is not None:
            return session
        self._check_mutable(session, revision)
        if session.controller_freeze is not None:
            raise ValueError("controller_already_frozen_create_new_session")
        if session.route is None:
            raise ValueError("route_not_resolved")
        if session.route.get("capability_gap"):
            raise ValueError(f"route_capability_gap: {session.route['capability_gap']}")
        if not session.evidence:
            raise ValueError("public_evidence_required_before_freeze")
        if controller is None and isinstance(session.controller_candidate, Mapping):
            candidate_value = session.controller_candidate.get("ir")
            controller = (
                dict(candidate_value) if isinstance(candidate_value, Mapping) else None
            )
        if runtime_contract is None and isinstance(
            session.controller_candidate, Mapping
        ):
            audit = session.controller_candidate.get("synthesis_audit")
            catalog_runtime = (
                audit.get("runtime_contract") if isinstance(audit, Mapping) else None
            )
            runtime_contract = {
                **(
                    dict(catalog_runtime)
                    if isinstance(catalog_runtime, Mapping)
                    else {}
                )
            }
        if evaluation_contract is None:
            criteria = dict(session.task.success_requirements)
            reference = session.task.reference
            if reference is None:
                raise ValueError("evaluation_reference_required")
            sample_time = float(
                session.task.engineering_units.get(
                    "acquisition_sample_time_s",
                    session.task.budgets.get("evaluation_sample_time_s", 0.02),
                )
            )
            hold = float(
                criteria.get(
                    "hold_duration_min_s",
                    criteria.get(
                        "final_hold_duration_min_s",
                        criteria.get("post_recovery_hold_duration_min_s", 1.0),
                    ),
                )
            )
            response = float(
                criteria.get(
                    "settling_time_max_s",
                    criteria.get(
                        "recovery_time_max_s",
                        session.task.response_time_preference_s or 10.0,
                    ),
                )
            )
            horizon = float(
                session.task.budgets.get(
                    "evaluation_horizon_s",
                    max(response + hold + 2 * sample_time, 2 * response),
                )
            )
            repeats = int(session.task.budgets.get("evaluation_repeats", 20))
            evaluation_contract = {
                "judge": "cfdc-independent-judge/v2.0",
                "task_type": session.task.task_type,
                "references": {
                    name: float(reference) for name in session.task.measured_signals
                },
                "sample_time_s": sample_time,
                "horizon_s": horizon,
                "trial_manifest": freeze_trial_manifest(repeats),
                **criteria,
            }
        if not controller or runtime_contract is None or not evaluation_contract:
            raise ValueError("freeze_contract_incomplete")
        strict_contract = session.session_version == EVIDENCE_SESSION_VERSION
        if strict_contract and session.provider is None:
            raise ValueError("provider_required_before_freeze")
        if strict_contract and session.controller_candidate is None:
            raise ValueError("controller_ir_required_before_freeze")
        if strict_contract and session.route.get("feature_ids"):
            if session.feature_artifact is None:
                raise ValueError("features_required_before_freeze")
            if session.feature_artifact.get("missing_feature_ids") or not bool(
                (session.feature_artifact.get("quality") or {}).get("passed", False)
            ):
                raise ValueError("features_quality_failed_before_freeze")
        if strict_contract and not any(
            item.get("kind") == "experiment" and isinstance(item.get("trace"), Mapping)
            for item in session.evidence
        ):
            raise ValueError("public_trace_required_before_freeze")
        if session.controller_candidate is not None and session.provider is None:
            raise ValueError("provider_required_before_freeze")
        if session.protocols:
            qualification = session.controller_qualification
            if (
                not isinstance(qualification, Mapping)
                or qualification.get("status") != "offline_qualified"
            ):
                raise ValueError(
                    "offline_controller_qualification_required_before_freeze"
                )
            if not isinstance(session.provider_bindings.get("evaluation"), Mapping):
                raise ValueError("evaluation_provider_required_before_freeze")
        if any(
            _contains_private_marker(value)
            for value in (controller, runtime_contract, evaluation_contract)
        ):
            raise ValueError("private_truth_not_allowed")
        candidate_ir = None
        if isinstance(controller, ControllerIR):
            candidate_ir = controller
            controller = controller.to_dict()
        elif (
            isinstance(controller, Mapping)
            and "family" in controller
            and "parameter_domains" in controller
        ):
            candidate_ir = ControllerIR.from_mapping(controller)
            controller = candidate_ir.to_dict()
        if candidate_ir is not None:
            if strict_contract and session.controller_candidate is not None:
                submitted_ir = session.controller_candidate.get("ir")
                if isinstance(submitted_ir, Mapping) and fingerprint(
                    dict(submitted_ir)
                ) != fingerprint(controller):
                    raise ValueError("controller_candidate_binding_mismatch")
            validate_controller_for_route(candidate_ir, session.route)
            required_signals = set(session.task.measured_signals)
            if not required_signals <= set(candidate_ir.measured_signals):
                raise ValueError("controller_measured_signal_binding_mismatch")
            required_inputs = set(
                session.task.control_inputs or (session.task.control_input,)
            )
            if not required_inputs <= set(candidate_ir.control_inputs):
                raise ValueError("controller_control_input_binding_mismatch")
            if (
                session.task.input_min is not None
                and candidate_ir.output_bounds is not None
                and candidate_ir.output_bounds[0] < session.task.input_min
            ):
                raise ValueError("controller_output_bounds_exceed_task_bounds")
            if (
                session.task.input_max is not None
                and candidate_ir.output_bounds is not None
                and candidate_ir.output_bounds[1] > session.task.input_max
            ):
                raise ValueError("controller_output_bounds_exceed_task_bounds")
        elif isinstance(controller, Mapping):
            validate_controller_family_for_route(
                str(controller.get("family") or ""), session.route
            )
            allowed = {
                str(item) for item in session.route.get("tunable_gain_names", ()) or ()
            }
            supplied_parameters = controller.get("parameters")
            if allowed and isinstance(supplied_parameters, Mapping):
                extra = sorted(
                    str(key) for key in supplied_parameters if str(key) not in allowed
                )
                if extra:
                    raise ValueError(
                        "controller_parameter_not_allowed: " + ", ".join(extra)
                    )
        phase_plan = compile_phase_plan(
            session.task,
            session.route,
            controller=dict(controller),
            phases=tuple(session.phase_plan.get("phases", ()))
            if session.phase_plan and session.controller_candidate
            else None,
        )
        registered_runtime = controller_runtime_contract(str(controller["family"]))
        input_names = tuple(
            session.task.control_inputs or (session.task.control_input,)
        )
        if session.task.input_min is None or session.task.input_max is None:
            raise ValueError("evaluation_input_bounds_required")
        state_bounds = (
            {
                name: [-float(session.task.state_stop), float(session.task.state_stop)]
                for name in candidate_ir.measured_signals
            }
            if candidate_ir is not None and session.task.state_stop is not None
            else {}
        )
        output_bounds = (
            {
                name: [float(session.task.output_min), float(session.task.output_max)]
                for name in session.task.measured_signals
            }
            if session.task.output_min is not None
            and session.task.output_max is not None
            else {}
        )
        runtime_value = {
            **dict(runtime_contract),
            **registered_runtime,
            "tracked_signals": list(session.task.measured_signals),
            "measured_signals": list(candidate_ir.measured_signals)
            if candidate_ir is not None
            else list(session.task.measured_signals),
            "control_inputs": list(input_names),
            "input_bounds": {
                name: [float(session.task.input_min), float(session.task.input_max)]
                for name in input_names
            },
            "output_bounds": output_bounds,
            "state_bounds": state_bounds,
            "controller_state_bounds": {
                key: list(value)
                for key, value in (
                    candidate_ir.state_limits.items()
                    if candidate_ir is not None
                    else ()
                )
            },
            "state_stop": session.task.state_stop,
            "phase_plan": phase_plan.to_dict(),
            "provider": deepcopy(session.provider)
            if session.provider is not None
            else None,
            "provider_bindings": deepcopy(dict(session.provider_bindings)),
            "protocol_fingerprint": session.active_protocol_fingerprint,
            "qualification": deepcopy(session.controller_qualification),
        }
        evaluation_value = deepcopy(dict(evaluation_contract))
        # The task contract is the authority for success thresholds.  A caller
        # may add judge-specific labels, but cannot silently replace a bound
        # task criterion with an example value.
        evaluation_value["task_type"] = session.task.task_type
        evaluation_value["task_fingerprint"] = session.task.fingerprint
        evaluation_value["task_success_requirements"] = deepcopy(
            dict(session.task.success_requirements)
        )
        evaluation_value["task_reference"] = session.task.reference
        evaluation_value["task_input_bounds"] = (
            [session.task.input_min, session.task.input_max]
            if session.task.input_min is not None and session.task.input_max is not None
            else None
        )
        evaluation_value["task_output_bounds"] = (
            [session.task.output_min, session.task.output_max]
            if session.task.output_min is not None
            and session.task.output_max is not None
            else None
        )
        evaluation_value["task_state_stop"] = session.task.state_stop
        evaluation_value["task_operating_region"] = session.task.operating_region
        evaluation_value["task_signal_units"] = dict(session.task.signal_units)
        evaluation_value["task_input_unit"] = session.task.input_units
        evaluation_value["runtime_contract"] = deepcopy(runtime_value)
        evaluation_value["phase_plan"] = phase_plan.to_dict()
        evaluation_value["phases"] = _execution_phases(
            session, phase_plan, evaluation_value
        )
        if session.task.task_type == "disturbance_recovery_to_hold":
            disturbance = dict(session.task.disturbance_contract)
            required = {"time_s", "duration_s", "channel", "amplitude"}
            if not required <= set(disturbance):
                raise ValueError("disturbance_execution_contract_incomplete")
            evaluation_value["disturbance"] = disturbance
        for key, value in session.task.success_requirements.items():
            evaluation_value[str(key)] = deepcopy(value)
        if session.task.task_type == "disturbance_recovery_to_hold":
            evaluation_value["disturbance_event_fingerprint"] = fingerprint(
                session.task.disturbance_contract
            )
        freeze = ControllerFreeze(
            session_id=session.session_id,
            task_fingerprint=session.task.fingerprint,
            controller=deepcopy(dict(controller)),
            evidence_fingerprints=tuple(
                str(item["fingerprint"]) for item in session.evidence
            ),
            runtime_contract=deepcopy(runtime_value),
            evaluation_contract=evaluation_value,
            source_version="cfdc-kernel/v2",
        )
        freeze_value = freeze.to_dict()
        updated = self._replace(
            session,
            status="controller_ready",
            phase_plan=phase_plan.to_dict(),
            controller_freeze=freeze_value,
            pending_actions=({"kind": "evaluation", "action": "record_evaluation"},),
        )
        return self._save(
            self._append(
                updated,
                "controller_frozen",
                action_id,
                {"freeze_fingerprint": freeze_value["freeze_fingerprint"]},
            )
        )

    def run_evaluation(
        self,
        session_id: str,
        *,
        action_id: str,
        revision: int,
        provider_registry: EvaluationProviderRegistry,
        provider_id: str | None = None,
        evaluation_split: str = "development",
        repeats: int | None = None,
    ) -> EvidenceSession:
        """Run an isolated evaluation provider and judge its public packet."""

        session = self.read(session_id)
        if self._event_for_action(session, action_id) is not None:
            return session
        self._check_mutable(session, revision)
        self._check_elapsed_budget(session)
        if session.controller_freeze is None:
            raise ValueError("controller_freeze_required")
        binding = session.provider_bindings.get("evaluation")
        if not isinstance(binding, Mapping):
            raise TypeError("evaluation_provider_required")
        selected_id = str(provider_id or binding.get("provider_id") or "")
        if selected_id != str(binding.get("provider_id") or ""):
            raise ValueError("evaluation_provider_binding_mismatch")
        provider = provider_registry.get(selected_id)
        if str(provider.provider_version) != str(binding.get("provider_version") or ""):
            raise ValueError("evaluation_provider_version_mismatch")
        if evaluation_split not in {"development", "fresh_confirmation"}:
            raise ValueError("evaluation_packet_split_invalid")
        repeat_count = int(
            repeats or session.task.budgets.get("evaluation_repeats", 20)
        )
        if repeat_count < 1 or repeat_count > 10_000:
            raise ValueError("evaluation_repeat_count_invalid")
        request = execution_request(session.controller_freeze, evaluation_split)
        if repeat_count != len(request["trials"]):
            raise ValueError("evaluation_repeat_count_frozen")
        raw_packet = provider.evaluate(request)
        if not isinstance(raw_packet, Mapping):
            raise TypeError("evaluation_provider_must_return_mapping")
        public_packet = deepcopy(dict(raw_packet))
        private_truth_returned = public_packet.pop("private_truth_returned", False)
        if _contains_private_marker(public_packet) or private_truth_returned is True:
            raise ValueError("private_truth_not_allowed")
        trials = raw_packet.get("trials")
        if not isinstance(trials, (list, tuple)) or len(trials) != repeat_count:
            raise ValueError("evaluation_provider_repeat_count_mismatch")
        packet = {
            **public_packet,
            "session_id": session.session_id,
            "task_fingerprint": session.task.fingerprint,
            "freeze_fingerprint": session.controller_freeze["freeze_fingerprint"],
            "evidence_fingerprints": list(
                session.controller_freeze.get("evidence_fingerprints", ())
            ),
            "provider_id": provider.provider_id,
            "provider_version": provider.provider_version,
            "provider_contract": {
                "provider_id": provider.provider_id,
                "provider_version": provider.provider_version,
                "capabilities": sorted(str(item) for item in provider.capabilities),
                "binding_role": "evaluation",
            },
            "evaluation_split": evaluation_split,
            "private_truth_returned": False,
            "packet_version": PACKET_VERSION,
        }
        packet.pop("packet_fingerprint", None)
        packet["packet_fingerprint"] = fingerprint(packet)
        return self.record_evaluation(
            session_id,
            action_id=action_id,
            revision=revision,
            packet=packet,
        )

    def record_evaluation(
        self,
        session_id: str,
        *,
        action_id: str,
        revision: int,
        packet: Mapping[str, Any],
    ) -> EvidenceSession:
        session = self.read(session_id)
        if self._event_for_action(session, action_id) is not None:
            return session
        self._check_mutable(session, revision)
        self._check_elapsed_budget(session)
        if session.controller_freeze is None:
            raise ValueError("controller_freeze_required")
        if hasattr(packet, "to_dict"):
            packet = packet.to_dict()
        if not isinstance(packet, Mapping):
            raise TypeError("evaluation_packet_object_required")
        evaluation_split = str(packet.get("evaluation_split") or "development")
        if evaluation_split not in {"development", "fresh_confirmation", "replay"}:
            raise ValueError("evaluation_packet_split_invalid")
        if evaluation_split == "fresh_confirmation" and not (
            session.tuning and session.tuning.get("accepted")
        ):
            raise ValueError("fresh_confirmation_requires_accepted_tuning")
        if (
            session.tuning
            and session.tuning.get("accepted")
            and evaluation_split != "fresh_confirmation"
        ):
            raise ValueError("fresh_confirmation_required_after_tuning")
        if session.evaluation_packets and evaluation_split != "fresh_confirmation":
            raise ValueError(
                "evaluation_already_recorded_use_replay_or_fresh_confirmation"
            )
        if evaluation_split == "fresh_confirmation" and any(
            item.get("evaluation_split") == "fresh_confirmation"
            for item in session.evaluation_packets
        ):
            raise ValueError("fresh_confirmation_already_consumed")
        result = independent_judge(session.controller_freeze, packet)
        # A calculated result is evidence, not yet a publishable state. The
        # exact stored packet must be read back and reproduce its judge hash.
        status = "evaluation_recorded_pending_replay"
        pending = ({"kind": "evaluation_replay", "action": "replay_evaluation"},)
        packets = (*session.evaluation_packets, deepcopy(dict(packet)))
        confirmation = (
            {
                "status": "pending_replay",
                "calculated_status": result["status"],
                "packet_fingerprint": result["packet_fingerprint"],
                "judge_fingerprint": result["judge_fingerprint"],
                "freeze_fingerprint": session.controller_freeze.get(
                    "freeze_fingerprint"
                ),
            }
            if evaluation_split == "fresh_confirmation"
            else session.confirmation
        )
        updated = self._replace(
            session,
            status=status,
            evaluation=result,
            evaluation_packets=packets,
            confirmation=confirmation,
            confirmation_history=(
                (*session.confirmation_history, deepcopy(confirmation))
                if evaluation_split == "fresh_confirmation" and confirmation is not None
                else session.confirmation_history
            ),
            pending_actions=pending,
        )
        return self._save(
            self._append(
                updated,
                "independent_evaluation_recorded",
                action_id,
                {
                    "status": result["status"],
                    "evaluation_split": evaluation_split,
                    "packet_fingerprint": result["packet_fingerprint"],
                },
            )
        )

    def run_tuning(
        self,
        session_id: str,
        *,
        action_id: str,
        revision: int,
        contract: TuningContract | Mapping[str, Any],
        evaluate: Any,
        qualify: Any | None = None,
    ) -> EvidenceSession:
        """Run the deterministic tuning contract after an evaluation gate."""

        session = self.read(session_id)
        if self._event_for_action(session, action_id) is not None:
            return session
        self._check_mutable(session, revision)
        self._check_elapsed_budget(session)
        if not session.task.budget_confirmed:
            raise ValueError("task_boundary_confirmation_required")
        if session.controller_freeze is None or session.evaluation is None:
            raise ValueError("tuning_requires_frozen_evaluated_controller")
        if session.evaluation.get("status") != "performance_not_met":
            raise ValueError("tuning_requires_performance_gap")
        if (
            not session.evaluation_replays
            or not session.evaluation_replays[-1].get("matches_previous")
            or session.status != "tuning_eligible"
        ):
            raise ValueError("tuning_requires_verified_evaluation_replay")
        raw_contract = (
            contract
            if isinstance(contract, TuningContract)
            else TuningContract.from_mapping(contract)
        )
        active_freeze_fingerprint = str(
            session.controller_freeze.get("freeze_fingerprint") or ""
        )
        evaluation_contract_fingerprint = fingerprint(
            session.controller_freeze.get("evaluation_contract", {})
        )
        if (
            raw_contract.task_fingerprint
            and raw_contract.task_fingerprint != session.task.fingerprint
        ):
            raise ValueError("tuning_task_binding_mismatch")
        if (
            raw_contract.initial_freeze_fingerprint
            and raw_contract.initial_freeze_fingerprint != active_freeze_fingerprint
        ):
            raise ValueError("tuning_freeze_binding_mismatch")
        if (
            raw_contract.evaluation_contract_fingerprint
            and raw_contract.evaluation_contract_fingerprint
            != evaluation_contract_fingerprint
        ):
            raise ValueError("tuning_evaluation_contract_binding_mismatch")
        controller = session.controller_freeze.get("controller", {})
        parameters = (
            dict(controller.get("parameters", {}))
            if isinstance(controller, Mapping)
            else {}
        )
        baseline_result = {
            **dict(session.evaluation),
            "stable": bool(
                session.evaluation.get("stability_gate", {}).get("passed", False)
            ),
            "performance_pass": session.evaluation.get("status") == "performance_met",
        }
        result = run_bounded_tuning(
            parameters,
            raw_contract,
            evaluate,
            baseline_result=baseline_result,
            confirm_selected=False,
            qualify=qualify,
        )
        tuning_value = result.to_dict()
        tuning_value.update(
            {
                "task_fingerprint": session.task.fingerprint,
                "initial_freeze_fingerprint": active_freeze_fingerprint,
                "evaluation_contract_fingerprint": evaluation_contract_fingerprint,
            }
        )
        next_freeze = session.controller_freeze
        next_history = session.freeze_history
        next_candidate = session.controller_candidate
        next_status = session.status
        if result.status in {"blocked", "exhausted"}:
            next_status = "capability_gap"
        elif result.accepted:
            # An accepted development candidate receives a new immutable
            # freeze.  The previous freeze and its evaluation remain in
            # history; fresh confirmation is bound to this candidate only.
            candidate_controller = _controller_with_parameters(
                session.controller_freeze.get("controller", {}),
                result.best_parameters,
            )
            # The phase topology remains frozen, but each declarative phase
            # controller must bind to the accepted parameter candidate.  Do
            # not leave the old IR hidden inside runtime/evaluation contracts.
            phase_plan_value = deepcopy(session.phase_plan)
            if isinstance(phase_plan_value, Mapping):
                phase_plan_value.pop("plan_fingerprint", None)
                phase_items = phase_plan_value.get("phases")
                if isinstance(phase_items, list):
                    for phase_item in phase_items:
                        if isinstance(phase_item, Mapping):
                            phase_item["controller"] = deepcopy(candidate_controller)
                phase_plan_value = MultiStagePlan.from_mapping(
                    phase_plan_value
                ).to_dict()
            active = ControllerFreeze(
                session_id=session.session_id,
                task_fingerprint=session.task.fingerprint,
                controller=candidate_controller,
                evidence_fingerprints=tuple(
                    session.controller_freeze.get("evidence_fingerprints", ())
                ),
                runtime_contract={
                    **dict(session.controller_freeze.get("runtime_contract", {})),
                    "predecessor_freeze_fingerprint": session.controller_freeze.get(
                        "freeze_fingerprint"
                    ),
                    "tuning_contract_fingerprint": result.contract_fingerprint,
                    "phase_plan": deepcopy(phase_plan_value),
                },
                evaluation_contract={
                    **deepcopy(
                        dict(session.controller_freeze.get("evaluation_contract", {}))
                    ),
                    "phase_plan": deepcopy(phase_plan_value),
                },
                source_version="cfdc-kernel/v1+tuned",
            )
            next_history = (
                *session.freeze_history,
                deepcopy(dict(session.controller_freeze)),
            )
            next_freeze = active.to_dict()
            if session.controller_candidate is not None:
                next_candidate = {
                    **deepcopy(dict(session.controller_candidate)),
                    "ir": deepcopy(candidate_controller),
                    "phase_plan": deepcopy(phase_plan_value),
                }
            tuning_value.update(
                {
                    "predecessor_freeze_fingerprint": session.controller_freeze.get(
                        "freeze_fingerprint"
                    ),
                    "incumbent_freeze_fingerprint": next_freeze["freeze_fingerprint"],
                }
            )
            next_status = "awaiting_confirmation"
        updated = self._replace(
            session,
            tuning=tuning_value,
            tuning_history=(*session.tuning_history, deepcopy(tuning_value)),
            controller_candidate=next_candidate,
            controller_freeze=next_freeze,
            freeze_history=next_history,
            status=next_status,
            pending_actions=(
                ({"kind": "confirmation", "action": "record_fresh_confirmation"},)
                if result.accepted
                else ()
            ),
        )
        return self._save(
            self._append(
                updated,
                "bounded_tuning_completed",
                action_id,
                {
                    "status": result.status,
                    "accepted": result.accepted,
                    "contract_fingerprint": result.contract_fingerprint,
                },
            )
        )

    def run_feedback_iteration(
        self,
        session_id: str,
        *,
        action_id: str,
        revision: int,
        provider_registry: EvaluationProviderRegistry,
        provider_id: str | None = None,
        contract: TuningContract | Mapping[str, Any] | None = None,
    ) -> EvidenceSession:
        """Run one bounded development/fresh feedback iteration."""

        session = self.read(session_id)
        if self._event_for_action(session, action_id) is not None:
            return session
        self._check_mutable(session, revision)
        if session.status != "tuning_eligible":
            raise ValueError("feedback_iteration_requires_tuning_eligible_session")
        if session.controller_freeze is None or session.evaluation is None:
            raise ValueError("tuning_requires_frozen_evaluated_controller")
        binding = session.provider_bindings.get("evaluation")
        if not isinstance(binding, Mapping):
            raise TypeError("evaluation_provider_required")
        selected_id = str(provider_id or binding.get("provider_id") or "")
        if selected_id != str(binding.get("provider_id") or ""):
            raise ValueError("evaluation_provider_binding_mismatch")
        provider = provider_registry.get(selected_id)
        controller = session.controller_freeze.get("controller")
        if not isinstance(controller, Mapping):
            raise TypeError("frozen_controller_object_required")
        domains = controller.get("parameter_domains")
        parameters = controller.get("parameters")
        if not isinstance(domains, Mapping) or not isinstance(parameters, Mapping):
            raise TypeError("bounded_controller_parameter_domains_required")
        if contract is None:
            contract = TuningContract(
                parameter_whitelist=tuple(str(item) for item in parameters),
                parameter_domains={
                    str(key): (float(value[0]), float(value[1]))
                    for key, value in domains.items()
                    if key in parameters
                    and isinstance(value, (list, tuple))
                    and len(value) == 2
                },
                budget_confirmed=True,
                task_fingerprint=session.task.fingerprint,
                initial_freeze_fingerprint=session.controller_freeze[
                    "freeze_fingerprint"
                ],
                evaluation_contract_fingerprint=fingerprint(
                    session.controller_freeze.get("evaluation_contract", {})
                ),
            )

        if (
            session.route is None
            or session.feature_artifact is None
            or not session.protocols
            or not session.active_protocol_fingerprint
        ):
            raise ValueError("tuning_candidate_qualification_context_required")
        protocol = next(
            item
            for item in reversed(session.protocols)
            if item.get("protocol_fingerprint") == session.active_protocol_fingerprint
        )

        def qualify_candidate(candidate: Mapping[str, float]) -> dict[str, Any]:
            candidate_controller = _controller_with_parameters(controller, candidate)
            candidate_ir = ControllerIR.from_mapping(candidate_controller)
            return run_controller_qualification(
                candidate_ir,
                task=session.task.to_dict(),
                route=session.route,
                feature_artifact=session.feature_artifact,
                protocol=protocol,
            )

        def evaluate_candidate(
            candidate: Mapping[str, float], split: str, repeats: int
        ) -> dict[str, Any]:
            candidate_controller = _controller_with_parameters(controller, candidate)
            candidate_freeze = ControllerFreeze(
                session_id=session.session_id,
                task_fingerprint=session.task.fingerprint,
                controller=candidate_controller,
                evidence_fingerprints=tuple(
                    session.controller_freeze.get("evidence_fingerprints", ())
                ),
                runtime_contract=deepcopy(
                    dict(session.controller_freeze.get("runtime_contract", {}))
                ),
                evaluation_contract=deepcopy(
                    dict(session.controller_freeze.get("evaluation_contract", {}))
                ),
                source_version="cfdc-kernel/tuning-probe-v1",
            ).to_dict()
            provider_split = "fresh_confirmation" if split == "fresh" else "development"
            request = execution_request(candidate_freeze, provider_split)
            if len(request["trials"]) != repeats:
                raise ValueError("tuning_repeat_count_frozen")
            raw = provider.evaluate(request)
            if not isinstance(raw, Mapping):
                raise TypeError("evaluation_provider_public_packet_required")
            public_raw = deepcopy(dict(raw))
            private_truth_returned = public_raw.pop("private_truth_returned", False)
            if _contains_private_marker(public_raw) or private_truth_returned is True:
                raise ValueError("evaluation_provider_public_packet_required")
            packet = {
                **public_raw,
                "session_id": session.session_id,
                "task_fingerprint": session.task.fingerprint,
                "freeze_fingerprint": candidate_freeze["freeze_fingerprint"],
                "evidence_fingerprints": list(
                    candidate_freeze["evidence_fingerprints"]
                ),
                "provider_id": provider.provider_id,
                "provider_version": provider.provider_version,
                "provider_contract": {
                    "provider_id": provider.provider_id,
                    "provider_version": provider.provider_version,
                    "binding_role": "evaluation",
                },
                "evaluation_split": provider_split,
                "private_truth_returned": False,
                "packet_version": PACKET_VERSION,
            }
            packet.pop("packet_fingerprint", None)
            packet["packet_fingerprint"] = fingerprint(packet)
            result = independent_judge(candidate_freeze, packet)
            replay = independent_judge(candidate_freeze, deepcopy(packet))
            if replay["judge_fingerprint"] != result["judge_fingerprint"]:
                raise ValueError("tuning_probe_replay_mismatch")
            return {
                "stable": bool(result["stability_gate"]["passed"]),
                "performance_pass": result["status"] == "performance_met",
                "hard_failure": not bool(result["stability_gate"]["passed"]),
                "score": float(result["score"]),
                "packet_fingerprint": result["packet_fingerprint"],
                "judge_fingerprint": result["judge_fingerprint"],
                "freeze": candidate_freeze,
                "packet": packet,
                "judge": result,
                "replay": {
                    "matches_previous": True,
                    "packet_fingerprint": replay["packet_fingerprint"],
                    "judge_fingerprint": replay["judge_fingerprint"],
                },
            }

        return self.run_tuning(
            session_id,
            action_id=action_id,
            revision=revision,
            contract=contract,
            evaluate=evaluate_candidate,
            qualify=qualify_candidate,
        )

    def confirm_result(
        self,
        session_id: str,
        *,
        action_id: str,
        revision: int,
        provider_registry: EvaluationProviderRegistry | None = None,
        provider_id: str | None = None,
        packet: Mapping[str, Any] | None = None,
        repeats: int | None = None,
    ) -> EvidenceSession:
        """Run or record the mandatory fresh confirmation for a tuned freeze."""

        if packet is not None:
            return self.record_confirmation(
                session_id,
                action_id=action_id,
                revision=revision,
                packet=packet,
            )
        if provider_registry is None:
            raise ValueError("confirmation_provider_or_packet_required")
        return self.run_evaluation(
            session_id,
            action_id=action_id,
            revision=revision,
            provider_registry=provider_registry,
            provider_id=provider_id,
            evaluation_split="fresh_confirmation",
            repeats=repeats,
        )

    def run_until_blocked(
        self,
        session_id: str,
        *,
        provider_registry: ProviderRegistry | None = None,
        identification_provider_id: str | None = None,
        evaluation_provider_registry: EvaluationProviderRegistry | None = None,
        evaluation_provider_id: str | None = None,
        max_steps: int = 32,
    ) -> EvidenceSession:
        """Advance deterministic stages until a human or external boundary."""

        if max_steps < 1 or max_steps > 256:
            raise ValueError("automatic_step_budget_invalid")
        session = self.read(session_id)
        for _ in range(max_steps):
            if session.status in TERMINAL_STATES or session.read_only:
                return session
            if not session.task.budget_confirmed:
                return session
            action_id = f"auto:{session.session_id}:{session.revision}"
            if session.route is None:
                session = self.advance(
                    session_id,
                    action_id=f"{action_id}:route",
                    revision=session.revision,
                )
                continue
            if session.route.get("capability_gap"):
                return session
            identification = session.provider_bindings.get("identification")
            if not isinstance(identification, Mapping):
                if provider_registry is None or not identification_provider_id:
                    return session
                provider = provider_registry.get(identification_provider_id)
                session = self.set_provider(
                    session_id,
                    action_id=f"{action_id}:identification-provider",
                    revision=session.revision,
                    provider={
                        "provider_id": provider.provider_id,
                        "provider_version": provider.provider_version,
                        "capabilities": sorted(
                            str(item) for item in provider.capabilities
                        ),
                        "binding_role": "identification",
                        "execution_kind": "software",
                    },
                )
                continue
            evaluation_binding = session.provider_bindings.get("evaluation")
            if (
                not isinstance(evaluation_binding, Mapping)
                and evaluation_provider_registry is not None
                and evaluation_provider_id
            ):
                provider = evaluation_provider_registry.get(evaluation_provider_id)
                session = self.set_provider(
                    session_id,
                    action_id=f"{action_id}:evaluation-provider",
                    revision=session.revision,
                    provider={
                        "provider_id": provider.provider_id,
                        "provider_version": provider.provider_version,
                        "capabilities": sorted(
                            str(item) for item in provider.capabilities
                        ),
                        "binding_role": "evaluation",
                        "execution_kind": "software",
                    },
                )
                continue
            if not session.protocols or not session.active_protocol_fingerprint:
                session = self.compile_protocol(
                    session_id,
                    action_id=f"{action_id}:protocol",
                    revision=session.revision,
                )
                continue
            if not session.evidence:
                if provider_registry is None:
                    return session
                session = self.run_provider(
                    session_id,
                    action_id=f"{action_id}:provider-run",
                    revision=session.revision,
                    provider_registry=provider_registry,
                    provider_id=identification_provider_id,
                )
                continue
            if session.feature_artifact is None:
                session = self.derive_features(
                    session_id,
                    action_id=f"{action_id}:features",
                    revision=session.revision,
                )
                continue
            if session.feature_artifact.get("missing_feature_ids"):
                return session
            if session.controller_candidate is None:
                session = self.synthesize_controller(
                    session_id,
                    action_id=f"{action_id}:controller",
                    revision=session.revision,
                )
                continue
            if session.controller_qualification is None:
                session = self.qualify_controller(
                    session_id,
                    action_id=f"{action_id}:qualification",
                    revision=session.revision,
                )
                continue
            if session.controller_qualification.get("status") != "offline_qualified":
                return session
            if session.controller_freeze is None:
                if not isinstance(session.provider_bindings.get("evaluation"), Mapping):
                    return session
                session = self.freeze_controller(
                    session_id,
                    action_id=f"{action_id}:freeze",
                    revision=session.revision,
                )
                continue
            if session.evaluation is None:
                if evaluation_provider_registry is None:
                    return session
                session = self.run_evaluation(
                    session_id,
                    action_id=f"{action_id}:evaluation",
                    revision=session.revision,
                    provider_registry=evaluation_provider_registry,
                    provider_id=evaluation_provider_id,
                )
                continue
            if len(session.evaluation_replays) < len(session.evaluation_packets):
                session = self.replay_evaluation(
                    session_id,
                    action_id=f"{action_id}:evaluation-replay:{len(session.evaluation_replays)}",
                    revision=session.revision,
                )
                continue
            # Tuning acceptance and the final fresh confirmation are explicit
            # user decisions, even when their evaluators are registered.
            return session
        raise ValueError("automatic_step_budget_exhausted")

    def replay_evaluation(
        self,
        session_id: str,
        *,
        action_id: str,
        revision: int,
    ) -> EvidenceSession:
        """Rejudge the latest stored public packet without running a provider."""

        session = self.read(session_id)
        if self._event_for_action(session, action_id) is not None:
            return session
        self._check_mutable(session, revision)
        if session.controller_freeze is None or not session.evaluation_packets:
            raise ValueError("evaluation_packet_required_for_replay")
        packet = deepcopy(dict(session.evaluation_packets[-1]))
        result = independent_judge(session.controller_freeze, packet)
        previous = session.evaluation or {}
        replay = {
            "packet_fingerprint": result["packet_fingerprint"],
            "judge_fingerprint": result["judge_fingerprint"],
            "matches_previous": result["judge_fingerprint"]
            == previous.get("judge_fingerprint"),
            "evaluation_split": packet.get("evaluation_split", "development"),
        }
        if not replay["matches_previous"]:
            status, pending = (
                "capability_gap",
                ({"kind": "evaluation_integrity", "reason": "replay_mismatch"},),
            )
        elif packet.get("evaluation_split") == "fresh_confirmation":
            status = (
                "performance_met"
                if result["status"] == "performance_met"
                else "capability_gap"
            )
            pending = ()
        elif result["status"] == "performance_met":
            status, pending = "performance_met", ()
        elif result.get("stability_gate", {}).get("passed") and result.get(
            "evidence_gate", {}
        ).get("passed", True):
            status, pending = (
                "tuning_eligible",
                ({"kind": "tuning", "action": "run_tuning"},),
            )
        else:
            status, pending = "capability_gap", ()
        confirmation = session.confirmation
        confirmation_history = session.confirmation_history
        if packet.get("evaluation_split") == "fresh_confirmation":
            confirmation = {
                "status": result["status"]
                if replay["matches_previous"]
                else "replay_mismatch",
                "packet_fingerprint": result["packet_fingerprint"],
                "judge_fingerprint": result["judge_fingerprint"],
                "freeze_fingerprint": session.controller_freeze.get(
                    "freeze_fingerprint"
                ),
            }
            confirmation_history = (*confirmation_history, deepcopy(confirmation))
        updated = self._replace(
            session,
            status=status,
            pending_actions=pending,
            confirmation=confirmation,
            confirmation_history=confirmation_history,
            evaluation_replays=(*session.evaluation_replays, replay),
        )
        return self._save(
            self._append(
                updated,
                "evaluation_replayed",
                action_id,
                replay,
            )
        )

    def record_confirmation(
        self,
        session_id: str,
        *,
        action_id: str,
        revision: int,
        packet: Mapping[str, Any],
    ) -> EvidenceSession:
        """Record an untouched fresh confirmation after tuning."""

        session = self.read(session_id)
        if session.tuning is None or not session.tuning.get("accepted"):
            raise ValueError("fresh_confirmation_requires_accepted_tuning")
        if hasattr(packet, "to_dict"):
            packet = packet.to_dict()
        if not isinstance(packet, Mapping):
            raise TypeError("evaluation_packet_object_required")
        expected = session.tuning.get("best_parameters")
        supplied = packet.get("tuned_parameters")
        if supplied is not None and fingerprint(supplied) != fingerprint(expected):
            raise ValueError("fresh_confirmation_parameter_binding_mismatch")
        packet_value = dict(packet)
        if packet_value.get("evaluation_split") != "fresh_confirmation":
            raise ValueError("fresh_confirmation_packet_required")
        return self.record_evaluation(
            session_id,
            action_id=action_id,
            revision=revision,
            packet=packet_value,
        )

    def export(self, session_id: str, path: Path | None = None) -> str:
        session = self.read(session_id)
        value = session.to_json()
        if path is not None:
            Path(path).write_text(value, encoding="utf-8")
        return value

    def export_artifact(
        self,
        session_id: str,
        artifact_kind: str,
        path: Path | None = None,
    ) -> Path:
        """Export one current public artifact without exposing raw uploads."""

        session = self.read(session_id)
        kind = str(artifact_kind).strip()
        values: dict[str, Any] = {
            "protocol": session.protocols[-1] if session.protocols else None,
            "upload_receipt": session.upload_attempts[-1]
            if session.upload_attempts
            else None,
            "features": session.feature_artifact,
            "controller_ir": (
                session.controller_candidate.get("ir")
                if isinstance(session.controller_candidate, Mapping)
                else None
            ),
            "qualification": session.controller_qualification,
            "freeze": session.controller_freeze,
            "evaluation": session.evaluation,
            "feedback": session.tuning,
            "confirmation": session.confirmation,
            "result": {
                "result_version": "cfdc-result/v1",
                "session_id": session.session_id,
                "status": session.status,
                "task_fingerprint": session.task.fingerprint,
                "active_protocol_fingerprint": session.active_protocol_fingerprint,
                "active_freeze_fingerprint": (session.controller_freeze or {}).get(
                    "freeze_fingerprint"
                ),
                "evaluation": deepcopy(session.evaluation),
                "confirmation": deepcopy(session.confirmation),
            },
            "audit": session.to_dict(),
        }
        feedback = values["feedback"]
        if isinstance(feedback, Mapping):
            feedback = {
                "feedback_version": "cfdc-feedback/v1",
                **deepcopy(dict(feedback)),
            }
            feedback["feedback_fingerprint"] = fingerprint(feedback)
            values["feedback"] = feedback
        confirmation = values["confirmation"]
        if isinstance(confirmation, Mapping):
            confirmation = {
                "confirmation_version": "cfdc-confirmation/v1",
                **deepcopy(dict(confirmation)),
            }
            confirmation["confirmation_fingerprint"] = fingerprint(confirmation)
            values["confirmation"] = confirmation
        result = values["result"]
        if isinstance(result, dict):
            result["result_fingerprint"] = fingerprint(result)
        if kind == "operator_bundle":
            handoff = (
                session.operator_handoffs[-1] if session.operator_handoffs else None
            )
            bundle_path = (
                handoff.get("bundle_path") if isinstance(handoff, Mapping) else None
            )
            if not bundle_path or not Path(bundle_path).is_file():
                raise ValueError("operator_bundle_not_available")
            return Path(bundle_path)
        if kind not in values:
            raise ValueError(f"unknown_artifact_kind: {kind}")
        value = values[kind]
        if value is None:
            raise ValueError(f"artifact_not_available: {kind}")
        output = (
            Path(path)
            if path is not None
            else self.root / f"{session.session_id}.downloads" / f"{kind}.json"
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_name(f".{output.name}.{uuid4().hex}.tmp")
        try:
            temporary.write_text(
                json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
            )
            temporary.replace(output)
        finally:
            temporary.unlink(missing_ok=True)
        return output

    def export_result_bundle(
        self,
        session_id: str,
        path: Path | None = None,
    ) -> Path:
        """Write a public, replayable result and audit ZIP."""

        session = self.read(session_id)
        output = (
            Path(path)
            if path is not None
            else self.root / f"{session.session_id}.result.zip"
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        artifacts: dict[str, Any] = {
            "task.json": session.task.to_dict(),
            "diagnostic_ledger.json": session.ledger.to_dict(),
            "route_history.json": list(session.route_history),
            "protocols.json": list(session.protocols),
            "operator_handoffs.json": list(session.operator_handoffs),
            "operator_reports.json": list(session.operator_reports),
            "upload_attempts.json": list(session.upload_attempts),
            "public_evidence.json": list(session.evidence),
            "feature_history.json": list(session.feature_history),
            "controller_history.json": list(session.controller_history),
            "qualification_history.json": list(session.qualification_history),
            "freeze_history.json": [
                *session.freeze_history,
                *([session.controller_freeze] if session.controller_freeze else []),
            ],
            "evaluation_packets.json": list(session.evaluation_packets),
            "evaluation_replays.json": list(session.evaluation_replays),
            "tuning_history.json": list(session.tuning_history),
            "confirmation_history.json": list(session.confirmation_history),
            "event_chain.json": [item.to_dict() for item in session.events],
        }
        if session.import_report is not None:
            artifacts["import_report.json"] = session.import_report
        result = {
            "result_version": "cfdc-result/v1",
            "session_id": session.session_id,
            "status": session.status,
            "task_fingerprint": session.task.fingerprint,
            "active_protocol_fingerprint": session.active_protocol_fingerprint,
            "active_freeze_fingerprint": (session.controller_freeze or {}).get(
                "freeze_fingerprint"
            ),
            "evaluation": deepcopy(session.evaluation),
            "confirmation": deepcopy(session.confirmation),
            "claims_allowed": [
                "task-bound software result"
                if session.evaluation
                else "auditable workflow progress",
            ],
            "claims_forbidden": [
                "physical safety certification",
                "global stability",
                "universal controller performance",
            ],
        }
        result["result_fingerprint"] = fingerprint(result)
        artifacts["result.json"] = result
        manifest = {
            "bundle_version": "cfdc-result-bundle/v1",
            "session_id": session.session_id,
            "artifacts": {
                name: fingerprint(value) for name, value in sorted(artifacts.items())
            },
            "raw_uploads_included": False,
            "private_truth_included": False,
        }
        manifest["bundle_fingerprint"] = fingerprint(manifest)
        temporary = output.with_name(f".{output.name}.{uuid4().hex}.tmp")
        try:
            with zipfile.ZipFile(
                temporary, "w", compression=zipfile.ZIP_DEFLATED
            ) as archive:
                archive.writestr("session.json", session.to_json())
                archive.writestr(
                    "manifest.json",
                    json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2)
                    + "\n",
                )
                for name, value in sorted(artifacts.items()):
                    archive.writestr(
                        name,
                        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2)
                        + "\n",
                    )
            temporary.replace(output)
        finally:
            temporary.unlink(missing_ok=True)
        return output

    def import_v3(self, source: str | Path) -> EvidenceSession:
        """Create a new mutable Kernel session from a read-only v3 bundle.

        Only public facts that validate under current contracts are carried
        forward.  Old execution authority, private provider state, and
        performance claims are deliberately excluded.
        """

        inspection = inspect_v3_source(source)
        session_id = f"cfdc-import-{inspection.source_digest[:16]}"
        target = self._path(session_id)
        if target.exists():
            existing = self.read(session_id)
            report = existing.import_report or {}
            if report.get("source_digest") == inspection.source_digest:
                return existing
            raise ValueError("v3_import_digest_collision")

        raw_task = deepcopy(dict(inspection.task_payload))
        for key in (
            "task_fingerprint",
            "schema_version",
            "contract_version",
            "task_contract_version",
        ):
            raw_task.pop(key, None)
        if "measured_signals" not in raw_task and raw_task.get("observed_outputs"):
            raw_task["measured_signals"] = raw_task["observed_outputs"]
        if (
            "control_input" not in raw_task
            and not raw_task.get("control_inputs")
            and raw_task.get("actuator")
        ):
            raw_task["control_input"] = raw_task["actuator"]
        raw_task["budget_confirmed"] = False
        task = TaskContract.from_user_input(raw_task)

        ledger = DiagnosticLedger.initial()
        accepted: list[dict[str, Any]] = [
            {
                "artifact": "task",
                "status": "revalidated",
                "task_fingerprint": task.fingerprint,
            }
        ]
        discarded: list[dict[str, Any]] = [
            {
                "artifact": "legacy_execution_authority",
                "reason": "fresh Kernel confirmation required",
            },
            {
                "artifact": "raw_llm_responses",
                "reason": "not part of the public typed interface",
            },
            {
                "artifact": "private_truth",
                "reason": "private provider state is never imported",
            },
        ]
        if inspection.diagnostic_updates:
            try:
                ledger = ledger.update(
                    inspection.diagnostic_updates, source="v3_import:public_evidence"
                )
                accepted.append(
                    {
                        "artifact": "diagnostic_ledger",
                        "status": "revalidated",
                        "ledger_fingerprint": ledger.to_dict()["ledger_fingerprint"],
                    }
                )
            except (TypeError, ValueError) as exc:
                ledger = DiagnosticLedger.initial()
                discarded.append({"artifact": "diagnostic_ledger", "reason": str(exc)})

        resumed_stage = "diagnostic"
        if ledger.readiness().status == "ready":
            try:
                route = self._resolve_route(ledger)
                supplied_routes = inspection.candidates.get("route", ())
                if supplied_routes and not any(
                    str(item.get("route_id")) == route["route_id"]
                    or str(item.get("profile_id")) == route["profile_id"]
                    for item in supplied_routes
                ):
                    raise ValueError("v3_route_disagrees_with_current_kernel")
                accepted.append(
                    {
                        "artifact": "route",
                        "status": "recomputed_after_confirmation",
                        "route_id": route["route_id"],
                    }
                )
                resumed_stage = "route"
            except (TypeError, ValueError) as exc:
                discarded.append({"artifact": "route", "reason": str(exc)})

        # Validate portable artifact syntax for the report, but leave all
        # execution-bound objects out of the new session until the new task,
        # provider and protocol fingerprints have been confirmed.
        for candidate in inspection.candidates.get("controller", ()):
            raw_controller = (
                candidate.get("controller_ir")
                if isinstance(candidate.get("controller_ir"), Mapping)
                else candidate
            )
            try:
                controller = ControllerIR.from_mapping(raw_controller)
                discarded.append(
                    {
                        "artifact": "controller",
                        "source_fingerprint": controller.fingerprint,
                        "reason": "source controller requires current features, qualification and a new freeze",
                    }
                )
            except (TypeError, ValueError) as exc:
                discarded.append(
                    {"artifact": "controller", "reason": f"validation_failed: {exc}"}
                )
        for kind in ("protocol", "evidence", "features", "freeze", "evaluation_packet"):
            for candidate in inspection.candidates.get(kind, ()):
                discarded.append(
                    {
                        "artifact": kind,
                        "source_fingerprint": candidate.get(
                            "protocol_fingerprint",
                            candidate.get(
                                "artifact_fingerprint",
                                candidate.get(
                                    "freeze_fingerprint",
                                    candidate.get("packet_fingerprint"),
                                ),
                            ),
                        ),
                        "reason": "source binding must be regenerated or resubmitted under the new Kernel session",
                    }
                )

        session = EvidenceSession(
            session_id=session_id,
            task=task,
            ledger=ledger,
            status="intake",
            pending_actions=(
                {
                    "kind": "budget",
                    "action": "confirm_task",
                    "reason": "imported_task_requires_fresh_boundary_confirmation",
                },
            ),
            agent_config={"mode": "multi", "source": "v3_import"},
        )
        report = build_import_report(
            inspection,
            session_id=session_id,
            accepted=accepted,
            discarded=discarded,
            resumed_stage=resumed_stage,
        )
        session = self._replace(session, import_report=report)
        session = self._append(
            session,
            "v3_bundle_imported",
            f"v3-import:{inspection.source_digest[:24]}",
            {
                "source_digest": inspection.source_digest,
                "import_fingerprint": report["import_fingerprint"],
                "resumed_stage": resumed_stage,
            },
        )
        return self._save(session)

    def import_legacy(self, path: Path) -> EvidenceSession:
        """Import a v0/v1 receipt as a read-only view without inventing facts."""

        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        source_id = hashlib.sha256(Path(path).read_bytes()).hexdigest()[:12]
        existing_path = self._path(f"legacy-{source_id}")
        if existing_path.exists():
            existing = EvidenceSession.from_json(
                existing_path.read_text(encoding="utf-8"), path=existing_path
            )
            if existing.read_only:
                return existing
            raise ValueError("legacy_import_target_not_read_only")
        # Carry only explicitly public task text and interface names.  Legacy
        # approvals, routes, controller parameters, and performance claims are
        # intentionally discarded and must be re-confirmed in a new task.
        legacy_task = raw.get("task") if isinstance(raw.get("task"), Mapping) else raw
        description = str(
            legacy_task.get("description")
            or legacy_task.get("natural_language_description")
            or f"Legacy session {source_id}; task contract unavailable"
        ).strip()
        signals = (
            legacy_task.get("measured_signals")
            or legacy_task.get("observed_outputs")
            or ["output"]
        )
        control_input = (
            legacy_task.get("control_input") or legacy_task.get("actuator") or "input"
        )
        task = TaskContract.from_user_input(
            {
                "description": description,
                "measured_signals": signals,
                "control_input": control_input,
            }
        )
        session = EvidenceSession(
            session_id=f"legacy-{source_id}",
            task=task,
            ledger=DiagnosticLedger.initial(),
            status=str(raw.get("status", "legacy_read_only")),
            read_only=True,
            legacy_lineage={
                "source_path": str(Path(path).resolve()),
                "source_hash": hashlib.sha256(Path(path).read_bytes()).hexdigest(),
                "source_schema": str(
                    raw.get("schema_version") or raw.get("session_version") or "unknown"
                ),
                "import_policy": "public_task_facts_only; approvals_and_results_discarded",
            },
        )
        return self._save(session)

    def create_task_from_legacy(
        self,
        path: Path,
        *,
        agent_config: Mapping[str, Any] | None = None,
    ) -> EvidenceSession:
        """Start a fresh mutable task carrying only public legacy facts."""

        legacy = self.import_legacy(path)
        task = legacy.task
        session = self.start(task, agent_config=agent_config)
        lineage = {
            "source_session_id": legacy.session_id,
            "source_hash": legacy.legacy_lineage.get("source_hash")
            if legacy.legacy_lineage
            else None,
            "import_policy": "public_task_facts_only; approvals_and_results_discarded",
        }
        updated = self._replace(session, legacy_lineage=lineage)
        return self._save(
            self._append(
                updated, "legacy_public_facts_carried_forward", "legacy-import", lineage
            )
        )

    continue_from_legacy = create_task_from_legacy

    def _resolve_route(self, ledger: DiagnosticLedger) -> dict[str, Any]:
        route = resolve_route(ledger)
        if route["registry_version"] != self.registry_version:
            raise ValueError("route_registry_version_mismatch")
        return route

    def _path(self, session_id: str) -> Path:
        if (
            not session_id
            or "/" in session_id
            or "\\" in session_id
            or ".." in session_id
        ):
            raise ValueError("invalid_session_id")
        return self.root / f"{session_id}.json"

    def _save(self, session: EvidenceSession) -> EvidenceSession:
        path = self._path(session.session_id)
        # Keep the revision comparison and atomic replacement in one critical
        # section.  EvidenceSession.save() already writes a temporary file and
        # replaces the target, while this lock prevents two threads in the same
        # process from both passing the compare-and-swap check.
        with _SESSION_SAVE_LOCK:
            if path.exists():
                # A duplicate action is idempotent and returns the already
                # committed session.
                current = EvidenceSession.from_json(
                    path.read_text(encoding="utf-8"), path=path
                )
                if current.revision >= session.revision:
                    new_action = (
                        session.events[-1].action_id if session.events else None
                    )
                    if (
                        new_action
                        and self._event_for_action(current, new_action) is not None
                    ):
                        return current
                    raise ValueError(
                        f"concurrent_revision_conflict: expected {session.revision - 1}, got {current.revision}"
                    )
                if current.revision != session.revision - 1:
                    raise ValueError(
                        f"concurrent_revision_conflict: expected {session.revision - 1}, got {current.revision}"
                    )
            session = EvidenceSession(**{**session.__dict__, "_path": str(path)})
            session.save(path)
            return session

    @staticmethod
    def _replace(session: EvidenceSession, **changes: Any) -> EvidenceSession:
        values = {
            **session.__dict__,
            "session_version": EVIDENCE_SESSION_VERSION,
            **changes,
        }
        values.pop("_path", None)
        return EvidenceSession(**values)

    @staticmethod
    def _append(
        session: EvidenceSession,
        event_type: str,
        action_id: str,
        payload: Mapping[str, Any],
    ) -> EvidenceSession:
        event = SessionEvent.create(
            event_id=f"evt-{uuid4().hex}",
            action_id=action_id,
            event_type=event_type,
            revision_before=session.revision,
            revision_after=session.revision + 1,
            payload=payload,
            previous_fingerprint=session.events[-1].event_fingerprint
            if session.events
            else None,
        )
        return WorkflowService._replace(
            session, revision=event.revision_after, events=(*session.events, event)
        )

    @staticmethod
    def _event_for_action(
        session: EvidenceSession, action_id: str
    ) -> SessionEvent | None:
        if not str(action_id).strip():
            raise ValueError("action_id_required")
        return next(
            (event for event in session.events if event.action_id == action_id), None
        )

    @staticmethod
    def _check_mutable(session: EvidenceSession, revision: int) -> None:
        if session.read_only:
            raise ValueError("read_only_legacy_session")
        if session.status in TERMINAL_STATES:
            raise ValueError(f"terminal_session: {session.status}")
        if revision != session.revision:
            raise ValueError(
                f"stale_revision: expected {session.revision}, got {revision}"
            )

    @staticmethod
    def _check_not_frozen(session: EvidenceSession) -> None:
        """Guard mutations that would invalidate an immutable freeze."""

        if session.controller_freeze is not None:
            raise ValueError("controller_already_frozen_create_new_session")

    @staticmethod
    def _check_clarification_budget(session: EvidenceSession) -> None:
        limit = int(session.task.budgets.get("clarification_rounds", 6))
        if session.clarification_rounds >= limit:
            raise ValueError("clarification_budget_exhausted")

    @staticmethod
    def _check_elapsed_budget(session: EvidenceSession) -> None:
        limit = float(session.task.budgets.get("elapsed_time_s", 7200.0))
        try:
            created = datetime.fromisoformat(session.created_at)
            if created.tzinfo is None:
                created = created.replace(tzinfo=UTC)
            elapsed = max(0.0, (datetime.now(UTC) - created).total_seconds())
        except (TypeError, ValueError):
            raise ValueError("session_created_at_invalid") from None
        if elapsed > limit:
            raise ValueError("elapsed_interaction_budget_exhausted")


def _canonical_dimension(value: str) -> str:
    aliases = {
        "minimum_phase": "nonminimum_phase",
        "controllability_observability": "sensing_actuation_adequacy",
        "coupling_severity": "coupling_underactuation",
        "uncertainty_magnitude": "uncertainty_variation",
    }
    return aliases.get(value.strip(), value.strip())


def _evidence_duration(value: Mapping[str, Any]) -> float:
    trace = value.get("trace") if isinstance(value, Mapping) else None
    if not isinstance(trace, Mapping):
        return 0.0
    times = trace.get("time_s")
    if not isinstance(times, (list, tuple)) or len(times) < 2:
        return 0.0
    try:
        duration = float(times[-1]) - float(times[0])
    except (TypeError, ValueError):
        return 0.0
    return duration if math.isfinite(duration) and duration > 0 else 0.0


def _execution_started(session: EvidenceSession) -> bool:
    """Whether a confirmed task has crossed its pre-execution boundary."""

    return bool(
        session.evidence
        or session.experiment_failures
        or session.provider
        or session.evaluation_packets
        or session.controller_candidate
        or session.controller_freeze
    )


def _has_route_dependents(session: EvidenceSession) -> bool:
    """Return whether a new diagnostic answer must invalidate route artifacts."""

    return any(
        value is not None
        for value in (
            session.route,
            session.feature_artifact,
            session.controller_candidate,
            session.phase_plan,
            session.provider,
        )
    ) or bool(session.phase_results)


def _controller_with_parameters(
    controller: Mapping[str, Any], parameters: Mapping[str, Any]
) -> dict[str, Any]:
    """Return a declarative controller candidate with a fresh fingerprint."""

    value = deepcopy(dict(controller))
    existing = value.get("parameters")
    if not isinstance(existing, Mapping):
        raise TypeError("tuning_controller_parameters_required")
    merged = dict(existing)
    merged.update({str(key): float(item) for key, item in parameters.items()})
    value["parameters"] = merged
    value.pop("controller_fingerprint", None)
    value.pop("fingerprint", None)
    value["controller_fingerprint"] = fingerprint(value)
    return value


def _answer_to_update(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        result = dict(value)
        if "assessment" in result:
            result["assessment"] = str(result["assessment"]).strip()
        if str(result.get("status", "known")) == "unknown":
            result.setdefault("confidence", 0.0)
        return result
    text = str(value).strip()
    if text.casefold() in {"unknown", "不清楚", "不知道", "未知"}:
        return {
            "status": "unknown",
            "evidence": text,
            "confidence": 0.0,
            "blocking_for_current_route": True,
        }
    return {
        "status": "known",
        "evidence": text,
        "confidence": 0.75,
        "blocking_for_current_route": False,
        "assessment": _infer_assessment(text),
    }


def _contains_verbatim_text(source: str, excerpt: str) -> bool:
    candidate = str(excerpt or "").strip()
    if not candidate:
        return False
    if candidate in source:
        return True
    compact_source = " ".join(source.casefold().split())
    compact_candidate = " ".join(candidate.casefold().split())
    return compact_candidate in compact_source


def _reply_evidence_excerpts(value: Mapping[str, Any]) -> list[str]:
    raw = value.get("evidence")
    if isinstance(raw, (list, tuple)):
        return [str(item).strip() for item in raw if str(item).strip()]
    excerpt = str(raw or "").strip()
    return [excerpt] if excerpt else []


_REPLY_PARAMETER_FACT_IDS = frozenset(
    {item.feature_id for item in feature_definitions()}
    | {
        field.fact_id
        for template in default_specification_template_catalog().templates
        for field in template.fields
    }
)


def _validate_reply_parameter_facts(value: Any, source: str) -> list[dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, (list, tuple)):
        raise TypeError("kernel_reply_parameter_facts_must_be_array")
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in value:
        if not isinstance(raw, Mapping):
            raise TypeError("kernel_reply_parameter_fact_must_be_object")
        item = dict(raw)
        fact_id = str(item.get("fact_id") or item.get("parameter_id") or "").strip()
        if fact_id not in _REPLY_PARAMETER_FACT_IDS:
            raise ValueError(f"unknown_parameter_fact: {fact_id or 'empty'}")
        if fact_id in seen:
            raise ValueError(f"duplicate_parameter_fact: {fact_id}")
        seen.add(fact_id)
        source_excerpt = str(
            item.get("source_text") or item.get("source_excerpt") or ""
        ).strip()
        if not _contains_verbatim_text(source, source_excerpt):
            raise ValueError(f"parameter source for {fact_id} is not in the user reply")
        if "value" not in item:
            raise ValueError(f"parameter value required: {fact_id}")
        parameter_value = item["value"]
        if isinstance(parameter_value, bool):
            raise TypeError(f"parameter value invalid: {fact_id}")
        if isinstance(parameter_value, (int, float)):
            numeric = float(parameter_value)
            if not math.isfinite(numeric):
                raise ValueError(f"parameter value invalid: {fact_id}")
            parameter_value = numeric
            if not str(item.get("unit") or "").strip():
                raise ValueError(f"parameter unit required: {fact_id}")
        elif not isinstance(parameter_value, (str, list, dict)):
            raise TypeError(f"parameter value invalid: {fact_id}")
        source_type = str(item.get("source_type") or "user_reply").strip()
        if source_type != "user_reply":
            raise ValueError(f"parameter source type invalid: {fact_id}")
        result.append(
            {
                "fact_id": fact_id,
                "value": parameter_value,
                "unit": str(item.get("unit") or ""),
                "source_text": source_excerpt,
                "source_type": source_type,
            }
        )
    return result


def _sanitize_reply_agent_records(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, (list, tuple)):
        raise TypeError("kernel_reply_agent_records_must_be_array")
    from cfdc.lab.llm import sanitize_for_audit

    result: list[dict[str, Any]] = []
    for raw in value:
        if hasattr(raw, "__dict__"):
            item = dict(raw.__dict__)
            if "role" in item:
                item["role"] = getattr(item["role"], "value", str(item["role"]))
        elif isinstance(raw, Mapping):
            item = dict(raw)
        else:
            raise TypeError("kernel_reply_agent_record_must_be_object")
        role = str(item.get("role") or "").strip().casefold()
        if role not in {"diagnosis", "modeling", "controller", "critic"}:
            raise ValueError("agent_role_not_allowed")
        if _contains_private_marker(item):
            raise ValueError("agent_record_secret_not_allowed")
        sanitized = sanitize_for_audit(deepcopy(item))
        sanitized["role"] = role
        sanitized.pop("payload", None)
        result.append(sanitized)
    return result


def _infer_assessment(text: str) -> str | None:
    lowered = text.casefold()
    # Check negative/qualified forms before their positive substrings.  This
    # keeps ordinary answers such as "no significant delay" and "inadequate
    # sensing" from being recorded as the opposite assessment.
    if any(
        marker in lowered
        for marker in (
            "not significant",
            "no significant",
            "without significant",
            "无显著",
            "不显著",
        )
    ):
        return "not_significant"
    if any(
        marker in lowered for marker in ("not adequate", "inadequate", "不充分", "不够")
    ):
        return "inadequate"
    for token in (
        "unstable",
        "marginal",
        "stable",
        "nonminimum_phase",
        "nonminimum phase",
        "minimum_phase",
        "significant",
        "not_significant",
        "order2",
        "order 2",
        "high",
        "low",
        "severe_mimo",
        "severe mimo",
        "underactuated",
        "cascaded",
        "strong_dynamic",
        "strong dynamic",
        "weak",
        "adequate",
        "large",
        "moderate",
        "small",
        "siso",
    ):
        if token in lowered:
            return token.replace(" ", "_")
    return None


def _validate_public_evidence(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError("evidence_object_required")
    result = deepcopy(dict(value))
    if _contains_private_marker(result):
        raise ValueError("private_truth_not_allowed")
    supplied_fingerprint = result.pop("fingerprint", None)
    evidence_id = str(result.get("evidence_id") or "").strip()
    if not evidence_id:
        raise ValueError("evidence_id_required")
    source = str(result.get("source") or result.get("source_type") or "").strip()
    if source not in {"measured_trace", "model", "demo_fixture", "user_upload"}:
        raise ValueError("public_evidence_source_required")
    if result.get("kind", "experiment") == "experiment":
        if not result.get("protocol_fingerprint"):
            raise ValueError("protocol_fingerprint_required")
        if not result.get("units") and not result.get("signal_units"):
            raise ValueError("signal_units_required")
    if isinstance(result.get("trace"), Mapping):
        trace = PublicTrace.from_mapping(result["trace"])
        if trace.trace_id != evidence_id:
            raise ValueError("evidence_trace_id_mismatch")
        if trace.source != source:
            raise ValueError("evidence_trace_source_mismatch")
        declared_protocol = str(result.get("protocol_fingerprint") or "")
        if trace.protocol_fingerprint != declared_protocol:
            raise ValueError("evidence_trace_protocol_mismatch")
        result["trace"] = trace.to_dict()
        supplied_trace_fingerprint = result.get("trace_fingerprint")
        if (
            supplied_trace_fingerprint is not None
            and str(supplied_trace_fingerprint) != trace.fingerprint
        ):
            raise ValueError("evidence_trace_fingerprint_mismatch")
        result["trace_fingerprint"] = trace.fingerprint
    result["kind"] = str(result.get("kind", "experiment"))
    computed_fingerprint = fingerprint(result)
    if (
        supplied_fingerprint is not None
        and str(supplied_fingerprint) != computed_fingerprint
    ):
        raise ValueError("evidence_fingerprint_mismatch")
    result["fingerprint"] = computed_fingerprint
    return result


def _readiness_gates(session: EvidenceSession) -> dict[str, Any]:
    """Project independent evidence, route, and synthesis authorization gates."""

    evidence_blockers: list[str] = []
    if session.read_only:
        evidence_blockers.append("read_only_session")
    if not session.task.budget_confirmed:
        evidence_blockers.append("budget_confirmation_required")
    route = session.route if isinstance(session.route, Mapping) else {}
    has_evidence_action = bool(
        route.get("experiment_request")
        or route.get("experiment_primitives")
        or session.protocols
    )
    if not has_evidence_action:
        evidence_blockers.append("legal_information_action_not_selected")
    if session.status == "capability_gap" and not has_evidence_action:
        evidence_blockers.append("no_legal_information_action")

    route_blockers: list[str] = []
    if not route or route.get("provisional"):
        route_blockers.append("candidate_set_not_resolved")
    if route.get("capability_gap"):
        route_blockers.append(str(route["capability_gap"]))
    if (
        route
        and not route.get("provisional")
        and not route.get("controller_contract_id")
    ):
        route_blockers.append("registered_controller_route_required")

    artifact = (
        session.feature_artifact
        if isinstance(session.feature_artifact, Mapping)
        else {}
    )
    synthesis_blockers = list(route_blockers)
    if not artifact:
        synthesis_blockers.append("public_feature_artifact_required")
    else:
        missing = [str(item) for item in artifact.get("missing_feature_ids", ())]
        if missing:
            synthesis_blockers.extend(
                f"missing_feature:{feature_id}" for feature_id in missing
            )
        quality = artifact.get("quality")
        if not isinstance(quality, Mapping) or quality.get("passed") is not True:
            synthesis_blockers.append("public_feature_quality_not_passed")

    return {
        "readiness_version": "cfdc-readiness/v1.0",
        "evidence_acquisition": {
            "ready": not evidence_blockers,
            "blockers": list(dict.fromkeys(evidence_blockers)),
        },
        "route_selection": {
            "ready": not route_blockers,
            "blockers": list(dict.fromkeys(route_blockers)),
        },
        "controller_synthesis": {
            "ready": not synthesis_blockers,
            "blockers": list(dict.fromkeys(synthesis_blockers)),
        },
    }


def _contains_private_marker(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, item in value.items():
            lowered = str(key).casefold()
            if any(
                token in lowered
                for token in ("private", "truth", "oracle", "hidden", "secret")
            ):
                return True
            if _contains_private_marker(item):
                return True
    elif isinstance(value, (tuple, list)):
        return any(_contains_private_marker(item) for item in value)
    return False


def _execution_phases(
    session: EvidenceSession, phase_plan: MultiStagePlan, evaluation: Mapping[str, Any]
) -> list[dict[str, Any]]:
    if session.task.task_type != "transition_then_hold":
        return []
    targets = [*map(float, session.task.intermediate_targets)]
    if session.task.reference is None:
        raise ValueError("transition_numeric_reference_required")
    targets.extend((float(session.task.reference), float(session.task.reference)))
    if len(targets) != len(phase_plan.phases):
        raise ValueError("transition_phase_target_count_mismatch")
    qualification = session.controller_qualification or {}
    validated = qualification.get("validated_region")
    if not isinstance(validated, Mapping) or not set(
        session.task.measured_signals
    ) <= set(validated):
        raise ValueError("transition_requires_qualified_numeric_region")
    sample_time = float(evaluation["sample_time_s"])
    final_dwell = float(
        evaluation.get(
            "final_hold_duration_min_s", evaluation.get("hold_duration_min_s", 1.0)
        )
    )
    ordinary_dwell = float(
        session.task.budgets.get(
            "phase_dwell_s", max(5 * sample_time, min(final_dwell, 1.0))
        )
    )
    phase_timeout = float(evaluation["horizon_s"]) / len(targets)
    tolerance = float(
        evaluation.get(
            "final_abs_error_max", evaluation.get("recovery_abs_error_max", 0.0)
        )
    )
    if tolerance <= 0:
        raise ValueError("transition_phase_tolerance_required")
    policy = str(session.task.phase_schedule.get("state_policy", "inherit"))
    hysteresis = float(session.task.phase_schedule.get("hysteresis", tolerance * 0.2))
    return [
        {
            "phase_id": phase.phase_id,
            "references": {name: target for name in session.task.measured_signals},
            "exit_predicate": {
                "kind": "within_band",
                "signal": session.task.measured_signals[0],
                "target": target,
                "tolerance": tolerance,
            },
            "dwell_s": final_dwell if index == len(targets) - 1 else ordinary_dwell,
            "timeout_s": phase_timeout,
            "hysteresis": hysteresis,
            "state_policy": policy,
            "stable_region": {key: list(value) for key, value in validated.items()},
        }
        for index, (phase, target) in enumerate(
            zip(phase_plan.phases, targets, strict=True)
        )
    ]


def _action_budget(session: EvidenceSession) -> ActionBudget:
    reservations = [
        event
        for event in session.events
        if event.event_type == "experiment_attempt_reserved"
    ]
    distinct = tuple(
        dict.fromkeys(
            str(event.payload.get("protocol_fingerprint")) for event in reservations
        )
    )
    failures: dict[str, int] = {}
    for item in session.experiment_failures:
        operation = str(item.get("operation") or "unknown")
        failures[operation] = failures.get(operation, 0) + 1
    valid = sum(1 for item in session.evidence if item.get("kind") == "experiment")
    return ActionBudget(
        max_distinct_experiments=int(
            session.task.budgets.get("distinct_experiments", 4)
        ),
        max_excitation_time_s=float(
            session.task.budgets.get("cumulative_excitation_time_s", 1800.0)
        ),
        max_failures_per_action=int(
            session.task.budgets.get("same_failure_retries", 1)
        ),
        attempts=len(reservations),
        failed_attempts=len(session.experiment_failures),
        excitation_time_s=sum(
            float(event.payload.get("excitation_time_s", 0.0)) for event in reservations
        ),
        valid_experiments=valid,
        distinct_protocols=distinct,
        action_failures=failures,
    )


def _information_route(session: EvidenceSession) -> dict[str, Any] | None:
    """Compile one legal evidence action without pretending a final route exists."""

    task = session.task
    if task.input_min is None or task.input_max is None:
        return None
    target_unknowns = tuple(
        entry.id
        for entry in session.ledger.entries
        if entry.blocking_for_current_route and entry.status == "unknown"
    )
    if not target_unknowns:
        return None
    candidates = (
        "stable_siso",
        "delayed_or_high_order_siso",
        "static_nonlinear",
        "local_oscillator",
        "underactuated_local",
        "mimo",
    )
    bounds_known = task.input_min < task.input_max
    safe_excitation = bounds_known and task.state_stop is not None
    is_mimo = (
        len(task.control_inputs or (task.control_input,)) >= 2
        and len(task.measured_signals) >= 2
    )
    nonlinear = _assessment_text(session, "nonlinearity_strength")
    stability = _assessment_text(session, "open_loop_stability")
    if is_mimo:
        active = "bounded_mimo_dc_then_hadamard_multisine"
    elif any(word in nonlinear for word in ("strong", "nonlinear", "强", "死区")):
        active = "bounded_bidirectional_staircase"
    elif len(task.measured_signals) >= 2 and any(
        word in stability for word in ("unstable", "marginal", "不稳定", "自激")
    ):
        active = "class_iv_amplitude_release_repeats"
    else:
        active = "bounded_input_sequence"
    actions = [
        InformationAction(
            "passive_observation",
            "bounded zero-input public observation",
            {"bounds_known": True},
            {candidate: ("unresolved",) for candidate in candidates},
            risk=0.0,
            cost=1.0,
        ),
        InformationAction(
            active,
            "distinguish the current mechanism candidates from public trajectories",
            {"bounds_known": True, "safe_excitation": True},
            {
                candidate: (f"evidence_partition_{index}",)
                for index, candidate in enumerate(candidates)
            },
            risk=1.0,
            cost=2.0,
        ),
    ]
    selection = select_action(
        candidates,
        actions,
        {"bounds_known": bounds_known, "safe_excitation": safe_excitation},
        _action_budget(session),
    )
    if selection.action_id is None:
        return None
    operation = selection.action_id
    duration = min(
        max(float(task.response_time_preference_s or 10.0), 1.0),
        float(task.budgets.get("cumulative_excitation_time_s", 1800.0)) / 3.0,
    )
    amplitude = 0.1 * min(abs(float(task.input_min)), abs(float(task.input_max)))
    if amplitude <= 0:
        amplitude = 0.05 * (float(task.input_max) - float(task.input_min))
    if operation == "passive_observation":
        compiled_operation = "bounded_input_sequence"
        levels = (0.0, 0.0, 0.0, 0.0)
    else:
        compiled_operation = operation
        levels = (0.0, amplitude, -amplitude, 0.0)
    request = {
        "operation": compiled_operation,
        "segments": [
            {"duration_s": duration / 4.0, "input_value": level} for level in levels
        ],
        "repeats": 3,
        "sample_period_s": max(min(duration / 200.0, 0.1), 0.001),
        "requested_signals": list(task.measured_signals),
        "control_inputs": list(task.control_inputs or (task.control_input,)),
    }
    return {
        "route_id": f"information:{compiled_operation}",
        "profile_id": "information_acquisition",
        "provisional": True,
        "controller_contract_id": None,
        "controller_template_id": None,
        "feature_ids": [],
        "experiment_primitives": [compiled_operation],
        "experiment_request": request,
        "candidate_profile_ids": list(candidates),
        "target_unknowns": list(target_unknowns),
        "blocked_actions": dict(selection.blocked_actions),
        "selection_reason": selection.reason,
        "implemented": True,
        "capability_gap": None,
        "registry_version": REGISTRY_VERSION,
    }


def _assessment_text(session: EvidenceSession, dimension_id: str) -> str:
    entry = session.ledger.entry(dimension_id)
    return str(entry.assessment or entry.value or entry.evidence or "").casefold()


def _ledger_from_public_features(
    ledger: DiagnosticLedger, artifact: Mapping[str, Any]
) -> DiagnosticLedger:
    """Recompute task-relevant diagnoses from released numeric estimates."""

    raw = artifact.get("features") or {}

    def value(name: str, default: float = 0.0) -> float:
        item = raw.get(name)
        if isinstance(item, Mapping) and isinstance(item.get("value"), (int, float)):
            return float(item["value"])
        return default

    updates: dict[str, dict[str, Any]] = {}
    if "gain_matrix_condition" in raw:
        updates["coupling_underactuation"] = {
            "status": "known",
            "assessment": "severe_mimo"
            if value("dc_static_cross_ratio", 1.0) > 0.2
            else "mimo_weak_coupling",
            "evidence": "public 2x2 gain and dynamic coupling analysis",
            "confidence": 0.95,
        }
        updates["sensing_actuation_adequacy"] = {
            "status": "known",
            "assessment": "adequate"
            if value("mimo_input_output_rank", 0.0) >= 2
            else "inadequate",
            "evidence": "public 2x2 input-output rank estimate",
            "confidence": 0.95,
        }
    elif "history_dependence_index" in raw:
        updates["nonlinearity_strength"] = {
            "status": "known",
            "assessment": "history_dependent"
            if value("history_dependence_index") > 0.03
            else "static_nonlinear",
            "evidence": "public bidirectional staircase regression",
            "confidence": 0.95,
        }
    elif "small_amplitude_decay_rate" in raw:
        updates["open_loop_stability"] = {
            "status": "known",
            "assessment": "locally_self_excited"
            if value("small_amplitude_decay_rate") < 0
            else "locally_damped",
            "evidence": "public amplitude-release decay regression",
            "confidence": 0.95,
        }
        updates["nonlinearity_strength"] = {
            "status": "known",
            "assessment": "amplitude_dependent_dynamic",
            "evidence": "public amplitude-release decay regression",
            "confidence": 0.95,
        }
    elif "static_gain" in raw:
        tau = max(value("dominant_time_constant", 1.0), 1e-12)
        updates.update(
            open_loop_stability={
                "status": "known",
                "assessment": "stable",
                "evidence": "bounded public step converged to a finite plateau",
                "confidence": 0.95,
            },
            nonminimum_phase={
                "status": "known",
                "assessment": "nonminimum_phase"
                if value("inverse_response_severity") > 0.05
                else "minimum_phase",
                "evidence": "public signed step inverse-response estimate",
                "confidence": 0.95,
            },
            significant_delay={
                "status": "known",
                "assessment": "significant"
                if value("delay_bound") / tau > 0.15
                else "not_significant",
                "evidence": "public step delay-to-time-constant estimate",
                "confidence": 0.95,
            },
            relative_degree={
                "status": "known",
                "assessment": "low",
                "evidence": "public low-order step fit",
                "confidence": 0.9,
            },
        )
    applicable = {
        key: value
        for key, value in updates.items()
        if ledger.entry(key).status != "not_relevant"
    }
    return (
        ledger.update(applicable, source="public_numerical_analysis")
        if applicable
        else ledger
    )


def independent_judge(
    freeze: Mapping[str, Any], packet: Mapping[str, Any]
) -> dict[str, Any]:
    """The sole current judgment entry point; historical summaries are read-only."""
    from .judging import judge_packet

    if hasattr(freeze, "to_dict"):
        freeze = freeze.to_dict()
    if hasattr(packet, "to_dict"):
        packet = packet.to_dict()
    return judge_packet(freeze, packet)


def _judge_trial(
    trial: dict[str, Any], evaluation_contract: Mapping[str, Any]
) -> dict[str, Any]:
    """Derive public trajectory metrics when a packet includes raw samples.

    Providers may submit already adjudicated boolean gates.  When they submit a
    trajectory instead, this helper computes a small deterministic metric set;
    it never accesses a simulator's hidden state.
    """

    trajectory = trial.get("trajectory") or trial.get("trace") or trial.get("samples")
    trajectory = _normalize_trajectory(trajectory)
    if not isinstance(trajectory, Mapping):
        return trial
    times = _finite_sequence(trajectory.get("time_s"))
    output = _finite_sequence(trajectory.get("output"))
    if output is None:
        signals = trajectory.get("signals")
        if isinstance(signals, Mapping) and signals:
            first = next(iter(signals.values()))
            output = _finite_sequence(first)
    reference = _finite_sequence(trajectory.get("reference"))
    control = _finite_sequence(trajectory.get("control_input"))
    raw_control = _finite_sequence(trajectory.get("raw_control_input"))
    saturated = _boolean_sequence(trajectory.get("saturated"))
    stop_event = trial.get("stop_event")
    if isinstance(stop_event, Mapping) and stop_event.get("triggered") is True:
        trial["stopped_on_limit"] = True
        trial["stop_reason"] = str(stop_event.get("reason") or "public_stop")
    metrics = dict(trial.get("metrics") or {})
    invalid = (
        times is None or output is None or len(times) != len(output) or len(times) < 2
    )
    if reference is not None and len(reference) != len(output):
        invalid = True
    if control is not None and len(control) != len(output):
        invalid = True
    if raw_control is not None and len(raw_control) != len(output):
        invalid = True
    if saturated is not None and len(saturated) != len(output):
        invalid = True
    if invalid or any(
        second <= first for first, second in zip(times or (), (times or ())[1:])
    ):
        trial.update(
            {
                "stable": False,
                "performance_pass": False,
                "failure_reason": "invalid_public_trajectory",
            }
        )
        return trial
    if reference is None:
        # A public packet may omit a repeated reference column when the task
        # contract already binds a scalar target.  Use that declared target;
        # otherwise the neutral zero reference remains the only safe fallback.
        declared_reference = evaluation_contract.get("task_reference")
        try:
            declared_reference = float(declared_reference)
        except (TypeError, ValueError):
            declared_reference = 0.0
        reference = [declared_reference] * len(output)
    errors = [float(y) - float(r) for y, r in zip(output, reference)]
    final_error = abs(errors[-1])
    peak = max(output)
    trough = min(output)
    target = reference[-1]
    amplitude = max(abs(float(target) - float(reference[0])), 1e-12)
    overshoot = max(
        0.0, (peak - target) if target >= reference[0] else (target - trough)
    )
    settling_limit = _criterion_float(
        evaluation_contract,
        "settling_time_max_s",
        "settling_time_max",
    )
    final_error_limit = _criterion_float(
        evaluation_contract,
        "final_abs_error_max",
        "final_error_max",
        "final_error",
    )
    overshoot_limit = _criterion_float(evaluation_contract, "overshoot_max")
    stable = trial.get("stable")
    if stable is None:
        stable = (
            bool(all(math.isfinite(value) for value in output))
            and trial.get("stopped_on_limit") is not True
        )
    if trial.get("stopped_on_limit") is True:
        stable = False
    output_limit = _criterion_float(
        evaluation_contract, "output_abs_max", "state_stop", "max_abs_output"
    )
    output_min = _declared_scalar(evaluation_contract, "output_min")
    output_max = _declared_scalar(evaluation_contract, "output_max")
    declared_output_bounds = _declared_bounds(evaluation_contract, "task_output_bounds")
    if declared_output_bounds is not None:
        output_min = output_min if output_min is not None else declared_output_bounds[0]
        output_max = output_max if output_max is not None else declared_output_bounds[1]
    if output_limit is None:
        try:
            state_stop = float(evaluation_contract.get("task_state_stop"))
        except (TypeError, ValueError):
            state_stop = None
        if state_stop is not None and math.isfinite(state_stop) and state_stop > 0:
            output_limit = state_stop
    output_outside_bounds = (output_min is not None and min(output) < output_min) or (
        output_max is not None and max(output) > output_max
    )
    if (
        output_limit is not None and max(abs(value) for value in output) > output_limit
    ) or output_outside_bounds:
        stable = False
        trial["failure_reason"] = "public_output_limit_exceeded"
    performance_pass = trial.get("performance_pass")
    criteria_pass = True
    if final_error_limit is not None:
        criteria_pass = criteria_pass and final_error <= final_error_limit
    if overshoot_limit is not None:
        criteria_pass = criteria_pass and overshoot <= overshoot_limit
    settling_time = _settling_time(
        times, errors, final_error_limit or max(0.02 * amplitude, 1e-9)
    )
    metrics["settling_time_s"] = settling_time
    if settling_limit is not None:
        criteria_pass = (
            criteria_pass
            and settling_time is not None
            and settling_time <= settling_limit
        )
    iae = sum(
        (abs(errors[index - 1]) + abs(errors[index]))
        * (times[index] - times[index - 1])
        / 2.0
        for index in range(1, len(times))
    )
    hold_tolerance = final_error_limit or max(0.02 * amplitude, 1e-9)
    hold_duration = _trailing_hold_duration(times, errors, hold_tolerance)
    metrics.update({"iae": iae, "hold_duration_s": hold_duration})
    iae_limit = _criterion_float(
        evaluation_contract, "iae_max", "integral_absolute_error_max"
    )
    peak_input_limit = _criterion_float(
        evaluation_contract, "peak_abs_input_max", "input_peak_max"
    )
    saturation_ratio_limit = _criterion_float(
        evaluation_contract, "saturation_ratio_max", "saturation_fraction_max"
    )
    saturation_duration_limit = _criterion_float(
        evaluation_contract, "saturation_duration_max_s"
    )
    hold_min = _criterion_float(
        evaluation_contract,
        "hold_duration_min_s",
        "hold_duration_s",
        "final_hold_duration_min_s",
    )
    if iae_limit is not None:
        criteria_pass = criteria_pass and iae <= iae_limit
    if control is not None:
        peak_input = max(abs(value) for value in control)
        metrics["peak_abs_input"] = peak_input
        metrics["control_peak_abs"] = peak_input
        input_min = _declared_scalar(evaluation_contract, "input_min")
        input_max = _declared_scalar(evaluation_contract, "input_max")
        declared_input_bounds = _declared_bounds(
            evaluation_contract, "task_input_bounds"
        )
        if declared_input_bounds is not None:
            input_min = input_min if input_min is not None else declared_input_bounds[0]
            input_max = input_max if input_max is not None else declared_input_bounds[1]
        if input_min is None or input_max is None:
            runtime_bounds = _declared_bounds(
                evaluation_contract.get("runtime_contract", {}), "command_bounds"
            )
            if runtime_bounds is not None:
                input_min = input_min if input_min is not None else runtime_bounds[0]
                input_max = input_max if input_max is not None else runtime_bounds[1]
        if (input_min is not None and min(control) < input_min) or (
            input_max is not None and max(control) > input_max
        ):
            stable = False
            trial["failure_reason"] = "public_input_limit_exceeded"
        if peak_input_limit is not None:
            criteria_pass = criteria_pass and peak_input <= peak_input_limit
    if raw_control is not None:
        metrics["raw_peak_abs_input"] = max(abs(value) for value in raw_control)
    if saturated is not None:
        saturation_duration = _boolean_duration(times, saturated)
        saturation_fraction = saturation_duration / max(times[-1] - times[0], 1e-12)
        metrics["saturation_duration_s"] = saturation_duration
        metrics["saturation_fraction"] = saturation_fraction
        if saturation_ratio_limit is not None:
            criteria_pass = (
                criteria_pass and saturation_fraction <= saturation_ratio_limit
            )
        if saturation_duration_limit is not None:
            criteria_pass = (
                criteria_pass and saturation_duration <= saturation_duration_limit
            )
    if hold_min is not None:
        criteria_pass = criteria_pass and hold_duration >= hold_min
    if performance_pass is None:
        performance_pass = bool(criteria_pass)
    else:
        # A provider-supplied public flag is only an input to the judge; it
        # cannot override deterministic metric failures.
        performance_pass = bool(performance_pass) and bool(criteria_pass)
    metrics.update(
        {
            "final_abs_error": final_error,
            "overshoot": overshoot,
            "overshoot_rate": overshoot / amplitude,
            "peak_abs_output": max(abs(value) for value in output),
            "max_abs_output": max(abs(value) for value in output),
            "sample_count": len(output),
            "duration_s": times[-1] - times[0],
        }
    )
    if control is not None:
        metrics["control_peak_abs"] = max(abs(value) for value in control)
    trial.update(
        {
            "stable": bool(stable),
            "performance_pass": bool(performance_pass),
            "metrics": metrics,
        }
    )
    return trial


def _apply_task_specific_gate(
    trial: dict[str, Any], evaluation_contract: Mapping[str, Any]
) -> dict[str, Any]:
    """Apply v3 task semantics after generic public trajectory metrics.

    A provider may submit a precomputed public outcome, or the outcome can be
    derived from phase/handoff events in a packet.  Either way, the task type
    and criteria are copied into the immutable freeze, so this gate never
    consults an object model or LLM output.
    """

    task_type = str(evaluation_contract.get("task_type") or "").strip()
    if task_type not in {
        "local_setpoint_hold",
        "transition_then_hold",
        "disturbance_recovery_to_hold",
    }:
        return trial
    criteria = evaluation_contract.get("task_success_requirements")
    criteria = (
        dict(criteria) if isinstance(criteria, Mapping) else dict(evaluation_contract)
    )
    metrics = dict(trial.get("metrics") or {})
    passed = trial.get("performance_pass") is True

    if task_type == "local_setpoint_hold":
        hold_min = _criterion_float(criteria, "hold_duration_min_s", "hold_duration_s")
        if hold_min is not None:
            passed = passed and float(metrics.get("hold_duration_s", -1.0)) >= hold_min
        trial["performance_pass"] = bool(passed)
        return trial

    if task_type == "disturbance_recovery_to_hold":
        disturbance_executed = trial.get("disturbance_executed")
        if disturbance_executed is None:
            disturbance_executed = trial.get("disturbance_event") is not None
        expected_event = str(
            evaluation_contract.get("disturbance_event_fingerprint") or ""
        )
        event_fingerprint = trial.get("disturbance_event_fingerprint")
        recovered = trial.get("recovered_to_hold")
        if recovered is None:
            recovered = trial.get("recovery_success")
        recovery_time = trial.get("recovery_time_s")
        if recovery_time is None:
            recovery_time = metrics.get("recovery_time_s")
        hold_duration = trial.get("post_recovery_hold_duration_s")
        if hold_duration is None:
            hold_duration = metrics.get("hold_duration_s")
        try:
            recovery_time_value = (
                float(recovery_time) if recovery_time is not None else float("inf")
            )
        except (TypeError, ValueError):
            recovery_time_value = float("inf")
        try:
            hold_duration_value = (
                float(hold_duration) if hold_duration is not None else -1.0
            )
        except (TypeError, ValueError):
            hold_duration_value = -1.0
        recovery_limit = _criterion_float(criteria, "recovery_time_max_s")
        hold_min = _criterion_float(
            criteria, "post_recovery_hold_duration_min_s", "hold_duration_min_s"
        )
        error_limit = _criterion_float(
            criteria, "recovery_abs_error_max", "final_abs_error_max"
        )
        final_error = metrics.get("final_abs_error")
        passed = (
            passed
            and bool(disturbance_executed)
            and (not expected_event or str(event_fingerprint or "") == expected_event)
            and bool(recovered)
            and (recovery_limit is None or recovery_time_value <= recovery_limit)
            and (hold_min is None or hold_duration_value >= hold_min)
            and (
                error_limit is None
                or (final_error is not None and float(final_error) <= error_limit)
            )
        )
        metrics.update(
            {
                "recovery_time_s": recovery_time_value
                if math.isfinite(recovery_time_value)
                else None,
                "post_recovery_hold_duration_s": hold_duration_value,
            }
        )
        trial["task_outcome"] = {
            "disturbance_executed": bool(disturbance_executed),
            "disturbance_event_fingerprint": event_fingerprint,
            "recovered_to_hold": bool(recovered),
            "recovery_time_s": metrics["recovery_time_s"],
            "post_recovery_hold_duration_s": hold_duration_value,
        }
        trial["metrics"] = metrics
        trial["performance_pass"] = bool(passed)
        return trial

    phase_plan = evaluation_contract.get("phase_plan")
    phase_items = (
        phase_plan.get("phases", ()) if isinstance(phase_plan, Mapping) else ()
    )
    expected_phase_ids = [
        str(item.get("phase_id") or item.get("id"))
        for item in phase_items
        if isinstance(item, Mapping) and (item.get("phase_id") or item.get("id"))
    ]
    phase_events = trial.get("phase_events")
    if not isinstance(phase_events, (list, tuple)):
        phase_events = ()
    handoff_events = trial.get("handoff_events")
    if not isinstance(handoff_events, (list, tuple)):
        handoff_events = ()
    completed_phase_ids = trial.get("completed_phase_ids")
    if not isinstance(completed_phase_ids, list):
        completed_phase_ids = [
            str(item.get("phase_id") or item.get("id"))
            for item in phase_events
            if isinstance(item, Mapping)
            and (
                item.get("success") is True
                or item.get("exit_condition_met") is True
                or item.get("status") == "completed"
            )
            and (item.get("phase_id") or item.get("id"))
        ]
    verified_handoff_ids = trial.get("verified_handoff_ids")
    if not isinstance(verified_handoff_ids, list):
        verified_handoff_ids = [
            str(item.get("handoff_id") or item.get("id"))
            for item in handoff_events
            if isinstance(item, Mapping)
            and (
                item.get("condition_met") is True
                or item.get("success") is True
                or item.get("status") == "verified"
            )
            and (item.get("handoff_id") or item.get("id"))
        ]
    completed_phase_ids = [str(item) for item in completed_phase_ids]
    verified_handoff_ids = [str(item) for item in verified_handoff_ids]
    if not expected_phase_ids and completed_phase_ids:
        expected_phase_ids = list(completed_phase_ids)
    expected_handoff_ids = [
        f"{source}__to__{target}" for source, target in pairwise(expected_phase_ids)
    ]
    entered_goal = trial.get("entered_goal_region")
    if entered_goal is None:
        entered_goal = bool(
            completed_phase_ids
            and expected_phase_ids
            and completed_phase_ids[-1] == expected_phase_ids[-1]
        )
    final_hold = trial.get("final_hold_duration_s")
    if final_hold is None:
        final_hold = metrics.get("hold_duration_s")
    try:
        final_hold_value = float(final_hold) if final_hold is not None else -1.0
    except (TypeError, ValueError):
        final_hold_value = -1.0
    required_phase_count = _criterion_float(criteria, "required_phase_count_min")
    required_handoff_count = _criterion_float(criteria, "verified_handoff_count_min")
    final_hold_min = _criterion_float(
        criteria, "final_hold_duration_min_s", "hold_duration_min_s"
    )
    identities = (
        len(completed_phase_ids) == len(set(completed_phase_ids))
        and len(verified_handoff_ids) == len(set(verified_handoff_ids))
        and (not expected_phase_ids or completed_phase_ids == expected_phase_ids)
        and (not expected_handoff_ids or verified_handoff_ids == expected_handoff_ids)
    )
    task_outcome = {
        "completed_phase_ids": completed_phase_ids,
        "completed_phase_count": len(completed_phase_ids),
        "verified_handoff_ids": verified_handoff_ids,
        "verified_handoff_count": len(verified_handoff_ids),
        "entered_goal_region": bool(entered_goal),
        "final_hold_duration_s": final_hold_value,
        "identities_consistent": identities,
    }
    trial["task_outcome"] = task_outcome
    passed = (
        passed
        and identities
        and bool(
            entered_goal or not bool(criteria.get("goal_region_entry_required", True))
        )
        and (
            required_phase_count is None
            or len(completed_phase_ids) >= required_phase_count
        )
        and (
            required_handoff_count is None
            or len(verified_handoff_ids) >= required_handoff_count
        )
        and (final_hold_min is None or final_hold_value >= final_hold_min)
    )
    trial["performance_pass"] = bool(passed)
    return trial


def _normalize_trajectory(value: Any) -> Mapping[str, Any] | None:
    """Normalize array-style and archive row-style public traces."""

    if isinstance(value, Mapping):
        samples = value.get("samples")
        if isinstance(samples, (list, tuple)):
            return _normalize_trajectory(samples)
        return value
    if (
        not isinstance(value, (list, tuple))
        or not value
        or not all(isinstance(item, Mapping) for item in value)
    ):
        return None
    rows = [dict(item) for item in value]
    keys = set().union(*(row.keys() for row in rows))
    normalized: dict[str, Any] = {}
    for key in (
        "time_s",
        "reference",
        "output",
        "control_input",
        "raw_control_input",
        "saturated",
    ):
        if key in keys:
            normalized[key] = [row.get(key) for row in rows]
    if "output" not in normalized:
        for candidate in ("measured_output", "y", "value"):
            if candidate in keys:
                normalized["output"] = [row.get(candidate) for row in rows]
                break
    return normalized


def _trial_score(trial: Mapping[str, Any]) -> float | None:
    metrics = trial.get("metrics")
    candidates: list[Any] = [
        trial.get("score"),
        trial.get("performance_score"),
        trial.get("objective"),
    ]
    if isinstance(metrics, Mapping):
        candidates.extend(
            (
                metrics.get("score"),
                metrics.get("performance_score"),
                metrics.get("objective"),
            )
        )
    for value in candidates:
        if value is None:
            continue
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        if math.isfinite(number):
            return number
    return None


def _boolean_sequence(value: Any) -> list[bool] | None:
    if not isinstance(value, (list, tuple)):
        return None
    if any(not isinstance(item, bool) for item in value):
        raise ValueError("public_saturated_values_must_be_boolean")
    return list(value)


def _boolean_duration(times: list[float], values: list[bool]) -> float:
    if len(times) != len(values):
        return 0.0
    return sum(
        times[index] - times[index - 1]
        for index in range(1, len(times))
        if values[index] or values[index - 1]
    )


def _trailing_hold_duration(
    times: list[float], errors: list[float], tolerance: float
) -> float:
    for index in range(len(errors) - 1, -1, -1):
        if abs(errors[index]) > tolerance:
            return max(0.0, times[-1] - times[index])
    return max(0.0, times[-1] - times[0])


def _phase_failures(trials: tuple[Mapping[str, Any], ...]) -> list[str]:
    failures: list[str] = []
    for index, trial in enumerate(trials):
        for phase in (
            trial.get("phase_events", ())
            if isinstance(trial.get("phase_events"), (list, tuple))
            else ()
        ):
            if isinstance(phase, Mapping) and (
                phase.get("success") is False
                or phase.get("entry_condition_met") is False
                or phase.get("exit_condition_met") is False
            ):
                failures.append(f"trial_{index}:{phase.get('phase_id', 'phase')}")
        for handoff in (
            trial.get("handoff_events", ())
            if isinstance(trial.get("handoff_events"), (list, tuple))
            else ()
        ):
            if isinstance(handoff, Mapping) and (
                handoff.get("condition_met") is False
                or handoff.get("state_valid") is False
            ):
                failures.append(
                    f"trial_{index}:handoff:{handoff.get('handoff_id', 'handoff')}"
                )
    return failures


_EVALUATION_BOOLEAN_FIELDS = (
    "stable",
    "stopped_on_limit",
    "safety_failure",
    "hard_failure",
    "safety_violation",
    "constraint_violation",
    "performance_pass",
    "disturbance_executed",
    "recovered_to_hold",
    "recovery_success",
    "entered_goal_region",
)
_PHASE_BOOLEAN_FIELDS = (
    "entry_condition_met",
    "exit_condition_met",
    "success",
    "safety_failure",
    "stopped_on_limit",
    "hard_failure",
    "safety_violation",
    "constraint_violation",
)
_HANDOFF_BOOLEAN_FIELDS = (
    "condition_met",
    "state_valid",
    "success",
    "safety_failure",
    "hard_failure",
)


def _validate_evaluation_boolean_fields(trials: tuple[Mapping[str, Any], ...]) -> None:
    """Reject stringly typed public gates before any truthiness conversion."""

    for trial_index, trial in enumerate(trials):
        for field_name in _EVALUATION_BOOLEAN_FIELDS:
            if field_name in trial and not isinstance(trial[field_name], bool):
                raise ValueError(
                    f"evaluation_trial_{field_name}_must_be_boolean: {trial_index}"
                )
        for collection_name, field_names in (
            ("phase_events", _PHASE_BOOLEAN_FIELDS),
            ("handoff_events", _HANDOFF_BOOLEAN_FIELDS),
        ):
            collection = trial.get(collection_name)
            if not isinstance(collection, (list, tuple)):
                continue
            for event_index, event in enumerate(collection):
                if not isinstance(event, Mapping):
                    raise TypeError(
                        f"evaluation_{collection_name}_event_object_required: "
                        f"{trial_index}/{event_index}"
                    )
                for field_name in field_names:
                    if field_name in event and not isinstance(event[field_name], bool):
                        raise ValueError(
                            f"evaluation_{collection_name}_{field_name}_must_be_boolean: "
                            f"{trial_index}/{event_index}"
                        )


def _wilson_lower_bound(successes: int, total: int, z: float = 1.96) -> float:
    if total <= 0:
        return 0.0
    n = float(total)
    p = max(0.0, min(1.0, float(successes) / n))
    denominator = 1.0 + (z * z) / n
    centre = p + (z * z) / (2.0 * n)
    margin = z * math.sqrt((p * (1.0 - p) + (z * z) / (4.0 * n)) / n)
    return max(0.0, (centre - margin) / denominator)


def _finite_sequence(value: Any) -> list[float] | None:
    if not isinstance(value, (list, tuple)):
        return None
    try:
        result = [float(item) for item in value]
    except (TypeError, ValueError):
        return None
    return result if result and all(math.isfinite(item) for item in result) else None


def _criterion_float(contract: Mapping[str, Any], *keys: str) -> float | None:
    candidates: list[Any] = []
    candidates.extend(contract.get(key) for key in keys)
    success = contract.get("success")
    if isinstance(success, Mapping):
        candidates.extend(success.get(key) for key in keys)
    criteria = contract.get("criteria")
    if isinstance(criteria, Mapping):
        candidates.extend(criteria.get(key) for key in keys)
    for value in candidates:
        if value is None:
            continue
        try:
            result = float(value)
        except (TypeError, ValueError):
            continue
        if math.isfinite(result) and result >= 0:
            return result
    return None


def _declared_bounds(contract: Any, key: str) -> tuple[float, float] | None:
    """Read a public lower/upper pair without treating malformed data as safe."""

    if not isinstance(contract, Mapping):
        return None
    value = contract.get(key)
    if isinstance(value, (list, tuple)) and len(value) == 2:
        try:
            lower, upper = float(value[0]), float(value[1])
        except (TypeError, ValueError):
            return None
        if math.isfinite(lower) and math.isfinite(upper) and lower < upper:
            return lower, upper
    return None


def _declared_scalar(contract: Any, key: str) -> float | None:
    if not isinstance(contract, Mapping):
        return None
    value = contract.get(key)
    try:
        number = float(value) if value is not None else None
    except (TypeError, ValueError):
        return None
    return number if number is not None and math.isfinite(number) else None


def _settling_time(
    times: list[float], errors: list[float], tolerance: float
) -> float | None:
    for index, error in enumerate(errors):
        if all(abs(item) <= tolerance for item in errors[index:]):
            return times[index] - times[0]
    return None
