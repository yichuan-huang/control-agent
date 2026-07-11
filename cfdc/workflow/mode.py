from __future__ import annotations

from typing import Any

from cfdc.models import WorkflowMode


def resolve_workflow_mode(
    workflow_mode: WorkflowMode | str | None,
    diagnostic_adapter: Any | None,
) -> WorkflowMode:
    """Resolve the data boundary before diagnosis or fixture selection."""

    explicit_mode = WorkflowMode(workflow_mode) if workflow_mode is not None else None
    if diagnostic_adapter is not None:
        if explicit_mode == WorkflowMode.SIMULATION:
            raise ValueError(
                "diagnostic adapter cannot be used with simulation workflow mode"
            )
        return WorkflowMode.REAL
    return explicit_mode or WorkflowMode.SIMULATION
