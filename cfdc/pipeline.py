from __future__ import annotations

from typing import Any

from cfdc.diagnosis.llm import DiagnosticAdapter
from cfdc.models import SystemDescription


def run_cfdc_pipeline(
    description: SystemDescription,
    *,
    safety_limits: dict[str, float] | None = None,
    diagnostic_adapter: DiagnosticAdapter | None = None,
    use_mechanism_cards: bool = False,
) -> dict[str, Any]:
    """Run the same simulation-first workflow used by the route API."""

    from cfdc.runtime.orchestrator import run_cfdc_route

    return run_cfdc_route(
        "generic",
        description=description,
        safety_limits=safety_limits,
        diagnostic_adapter=diagnostic_adapter,
        use_mechanism_cards=use_mechanism_cards,
        include_trajectory=False,
    ).model_dump(mode="json")
