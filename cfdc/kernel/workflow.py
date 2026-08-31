"""Workflow service compatibility imports."""

from .service import WorkflowService
from .session import EvidenceSession, SessionEvent

__all__ = ["EvidenceSession", "SessionEvent", "WorkflowService"]
