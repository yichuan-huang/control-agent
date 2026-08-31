"""Public runtime bridge for the migrated kernel workflow.

This module is intentionally thin: CLI, WebUI and embedding applications use
the same :class:`cfdc.kernel.WorkflowService` entry points rather than creating
their own state machines.  Existing ``run_cfdc_route`` remains available for
read-only legacy/demo routes.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from cfdc.kernel import EvidenceSession, TaskContract, WorkflowService


def kernel_session_root(root: str | Path | None = None) -> Path:
    if root is not None:
        return Path(root)
    configured = os.getenv("CFDC_KERNEL_SESSION_DIR")
    return Path(configured) if configured else Path("output") / "kernel-sessions"


def create_kernel_service(root: str | Path | None = None) -> WorkflowService:
    return WorkflowService(kernel_session_root(root))


def start_kernel_workflow(
    payload: Mapping[str, Any] | TaskContract,
    *,
    root: str | Path | None = None,
) -> EvidenceSession:
    return create_kernel_service(root).start(payload)


def read_kernel_workflow(
    session_id: str, *, root: str | Path | None = None
) -> EvidenceSession:
    return create_kernel_service(root).read(session_id)


__all__ = [
    "create_kernel_service",
    "kernel_session_root",
    "read_kernel_workflow",
    "start_kernel_workflow",
]
