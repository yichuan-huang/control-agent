"""Role-scoped Agent facade for kernel tasks.

It reuses the existing audit and one-correction implementation in
``cfdc.agents`` while replacing the old ``SystemDescription``-centric context
with the immutable kernel session contract.  There is intentionally no
supervisor role: Python decides which role is called and when.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from cfdc.agents import (
    AgentExecutionRecord,
    AgentReviewBlocked,
    AgentRole,
    AgentRuntime,
    RetrievalSnippet,
)
from cfdc.knowledge import (
    KnowledgeArtifact,
    KnowledgeContext,
    RetrievalRequest,
    canonical_knowledge_documents,
)

from .session import EvidenceSession

ROLE_OPERATIONS = {
    AgentRole.DIAGNOSIS: {"diagnosis", "clarification", "evidence_gap", "user_reply"},
    AgentRole.MODELING: {"model", "feature", "data_quality", "user_reply"},
    AgentRole.CONTROLLER: {"route_explanation", "controller", "tuning_explanation"},
    AgentRole.CRITIC: {"review", "critic"},
}


class KernelAgentCoordinator:
    """Build auditable role messages and optionally invoke a completion."""

    def __init__(self, completion: Any | None = None, *, retriever: Any | None = None, agent_mode: str = "multi") -> None:
        if agent_mode not in {"single", "multi"}:
            raise ValueError("agent_mode_must_be_single_or_multi")
        if completion is not None and not callable(completion):
            # OpenAICompatibleDiagnosticAdapter exposes ``complete_agent``;
            # accepting the object here keeps the kernel entry point aligned
            # with the existing adapter while preserving provider telemetry.
            complete_agent = getattr(completion, "complete_agent", None)
            if callable(complete_agent) and not hasattr(completion, "complete"):
                completion = complete_agent
        self.completion = completion
        self.retriever = retriever
        self.agent_mode = agent_mode
        self.runtime = AgentRuntime(completion) if completion is not None else None

    @property
    def audit_log(self) -> list[AgentExecutionRecord]:
        return self.runtime.audit_log if self.runtime is not None else []

    def build_context(
        self,
        session: EvidenceSession,
        *,
        role: AgentRole | str,
        operation: str,
        task_payload: Mapping[str, Any] | None = None,
        feedback: str | None = None,
    ) -> dict[str, Any]:
        role_value = role.value if isinstance(role, AgentRole) else str(role)
        if role_value not in {item.value for item in AgentRole}:
            raise ValueError(f"unknown_agent_role: {role_value}")
        allowed_operations = ROLE_OPERATIONS[AgentRole(role_value)]
        if operation not in allowed_operations:
            raise ValueError(f"agent_operation_not_allowed: {role_value}/{operation}")
        current = {
            "task": session.task.to_dict(),
            "diagnostic": session.ledger.to_dict(),
            "route": dict(session.route) if session.route else None,
            "features": dict(session.feature_artifact) if session.feature_artifact else None,
            "controller": dict(session.controller_candidate) if session.controller_candidate else None,
            "phase_plan": dict(session.phase_plan) if session.phase_plan else None,
            "freeze": dict(session.controller_freeze) if session.controller_freeze else None,
            "evaluation": dict(session.evaluation) if session.evaluation else None,
            "tuning": dict(session.tuning) if session.tuning else None,
            "evidence": [dict(item) for item in session.evidence],
            "pending_actions": [dict(item) for item in session.pending_actions],
        }
        if task_payload:
            current["task_payload"] = dict(task_payload)
        # Keep role context narrow and never pass private provider state.
        if (
            operation == "review"
            and role_value == AgentRole.CRITIC.value
            and str((task_payload or {}).get("operation") or "") == "user_reply"
        ):
            # User-reply review is an extraction check.  Keep task limits and
            # other session numbers out of the prompt so they cannot be copied
            # into a revised parameter candidate.
            allowed = {"task_payload"}
        elif operation == "user_reply" and role_value == AgentRole.DIAGNOSIS.value:
            allowed = {"diagnostic", "pending_actions", "task_payload"}
        elif operation == "user_reply" and role_value == AgentRole.MODELING.value:
            allowed = {"task_payload"}
        elif role_value == AgentRole.DIAGNOSIS.value:
            allowed = {"task", "diagnostic", "pending_actions", "task_payload"}
        elif role_value == AgentRole.MODELING.value:
            allowed = {"task", "diagnostic", "route", "features", "evidence", "pending_actions", "task_payload"}
        elif role_value == AgentRole.CONTROLLER.value:
            allowed = {"task", "diagnostic", "route", "features", "controller", "phase_plan", "pending_actions", "task_payload"}
        else:
            allowed = set(current)
        current = {key: value for key, value in current.items() if key in allowed}
        request = RetrievalRequest(
            role=role_value,
            operation=operation,
            canonical_class=(str(session.route.get("class")) if session.route else None),
            profile_id=(str(session.route.get("profile_id")) if session.route else None),
            missing_fields=tuple(
                str(item.get("dimension_id") or item.get("missing"))
                for item in session.pending_actions
                if item.get("dimension_id") or item.get("missing")
            ),
            summary=session.task.description[:800],
            stage=operation,
        )
        snippets = [] if operation == "user_reply" else self._retrieve(request)
        required = () if operation == "user_reply" else self._required_rules(session, role_value)
        return {
            "role": role_value,
            "operation": operation,
            "payload": current,
            "required_rules": [item.model_dump() for item in required],
            "references": snippets,
            "registry_version": required[0].registry_version if required else None,
            "index_snapshot": getattr(self.retriever, "index_snapshot", None),
            "feedback": feedback,
        }

    def execute(
        self,
        session: EvidenceSession,
        *,
        role: AgentRole | str,
        operation: str,
        task_payload: Mapping[str, Any] | None = None,
        feedback: str | None = None,
        revision: int = 0,
    ) -> AgentExecutionRecord:
        if self.runtime is None:
            raise ValueError("agent_completion_not_configured")
        role_value = role if isinstance(role, AgentRole) else AgentRole(str(role))
        context = self.build_context(session, role=role_value, operation=operation, task_payload=task_payload, feedback=feedback)
        return self.runtime.execute(
            role_value,
            description=None,
            stage=operation,
            request=context["payload"],
            retrieval=tuple(context["references"]),
            feedback=feedback,
            revision=revision,
            index_snapshot=context["index_snapshot"],
            knowledge=KnowledgeContext(
                required_rules=tuple(self._artifact_from_dict(item) for item in context["required_rules"]),
                references=tuple(context["references"]),
                index_snapshot=context["index_snapshot"],
            ),
        )

    def review_and_correct(
        self,
        session: EvidenceSession,
        *,
        owner_role: AgentRole | str,
        operation: str,
        candidate: Any,
        task_payload: Mapping[str, Any] | None = None,
        corrector: Any | None = None,
    ) -> Any:
        """Give an artifact one Critic review and, when safe, one correction."""

        if self.runtime is None:
            raise ValueError("agent_completion_not_configured")
        owner = owner_role if isinstance(owner_role, AgentRole) else AgentRole(str(owner_role))
        context = self.build_context(
            session,
            role=AgentRole.CRITIC,
            operation="review",
            task_payload={"owner_role": owner.value, "operation": operation, "candidate": candidate, **dict(task_payload or {})},
        )
        return self.runtime.review_and_correct(
            role=owner,
            description=None,
            stage=operation,
            request=context["payload"],
            candidate=candidate,
            retrieval=tuple(context["references"]),
            index_snapshot=context["index_snapshot"],
            corrector=corrector,
            knowledge=KnowledgeContext(
                required_rules=tuple(self._artifact_from_dict(item) for item in context["required_rules"]),
                references=tuple(context["references"]),
                index_snapshot=context["index_snapshot"],
            ),
        )

    def _retrieve(self, request: RetrievalRequest) -> list[Any]:
        if self.retriever is None:
            return []
        if hasattr(self.retriever, "retrieve"):
            rows = self.retriever.retrieve(request, limit=4)
        else:
            rows = self.retriever.search(request.query_text(), limit=4)
        # RAG fakes and older adapters commonly return dictionaries while the
        # agent runtime deliberately consumes typed snippets.  Normalize at
        # this boundary so the exact same source metadata is used in prompt
        # construction, provider calls and audit records.
        snippets: list[RetrievalSnippet] = []
        for row in rows or ():
            if isinstance(row, RetrievalSnippet):
                snippets.append(row)
                continue
            if isinstance(row, Mapping):
                value = row
                getter = value.get
            else:
                value = row
                getter = lambda key, default=None, value=value: getattr(value, key, default)
            snippets.append(
                RetrievalSnippet(
                    source_id=str(getter("source_id", getter("artifact_id", getter("id", ""))) or ""),
                    content=str(getter("content", getter("text", getter("excerpt", ""))) or ""),
                    score=getter("score"),
                    source_path=getter("source_path"),
                    section=getter("section"),
                    page=getter("page"),
                    content_hash=getter("content_hash"),
                    artifact_type=getter("artifact_type"),
                    artifact_id=getter("artifact_id"),
                    source_kind=getter("source_kind"),
                    canonical_class=getter("canonical_class"),
                    profile_id=getter("profile_id"),
                    rule_id=getter("rule_id"),
                )
            )
        return snippets

    @staticmethod
    def _required_rules(session: EvidenceSession, role: str) -> tuple[KnowledgeArtifact, ...]:
        documents = canonical_knowledge_documents()
        route = session.route or {}
        profile_id = route.get("profile_id")
        class_id = route.get("class")
        selected = []
        for item in documents:
            if (
                item.artifact_type == "classification_rule"
                and (role == "diagnosis" or item.canonical_class == class_id)
            ) or (
                item.artifact_type == "profile" and item.profile_id == profile_id
            ) or (
                item.artifact_type == "feature" and role == "modeling"
            ):
                selected.append(item)
        return tuple(selected)

    @staticmethod
    def _artifact_from_dict(value: Mapping[str, Any]) -> KnowledgeArtifact:
        return KnowledgeArtifact(
            artifact_id=str(value.get("artifact_id") or ""),
            artifact_type=str(value.get("artifact_type") or "rule"),
            title=str(value.get("title") or value.get("artifact_id") or "registry rule"),
            text=str(value.get("text") or ""),
            role=tuple(str(item) for item in value.get("role", ()) or ()),
            stage=tuple(str(item) for item in value.get("stage", ()) or ()),
            canonical_class=value.get("canonical_class"),
            profile_id=value.get("profile_id"),
            rule_id=value.get("rule_id"),
            source_kind=str(value.get("source_kind") or "builtin_registry"),
            registry_version=str(value.get("registry_version") or "cfdc-knowledge/v1"),
        )


__all__ = ["ROLE_OPERATIONS", "AgentReviewBlocked", "AgentRole", "KernelAgentCoordinator"]
