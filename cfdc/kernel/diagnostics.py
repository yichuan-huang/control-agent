"""Append-only dynamic eight-dimension diagnostic ledger."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass, replace
from typing import Any

from .contracts import DIAGNOSTIC_IDS, DIAGNOSTIC_LEDGER_VERSION, fingerprint


@dataclass(frozen=True)
class DiagnosticEntry:
    id: str
    status: str = "unknown"
    evidence: str = ""
    source: str = ""
    confidence: float = 0.0
    route_consequence: str = ""
    blocking_for_current_route: bool = True
    next_resolving_action: str | None = None
    valid_region: str | None = None
    assessment: str | None = None
    value: Any = None

    def __post_init__(self) -> None:
        if self.id not in DIAGNOSTIC_IDS:
            raise ValueError(f"unknown_diagnostic_id: {self.id}")
        if self.status not in {"known", "unknown", "not_relevant"}:
            raise ValueError(f"invalid_diagnostic_status: {self.status}")
        if not isinstance(self.blocking_for_current_route, bool):
            raise ValueError("diagnostic_blocking_for_current_route_must_be_boolean")  # noqa: TRY004
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("diagnostic_confidence_invalid")
        if self.status == "known" and not self.evidence.strip():
            raise ValueError("known_diagnostic_requires_evidence")
        if self.status == "not_relevant":
            if not self.evidence.strip() or not self.source.startswith("task_policy:"):
                raise ValueError("not_relevant_requires_deterministic_policy")
            if (
                self.blocking_for_current_route
                or self.next_resolving_action is not None
            ):
                raise ValueError("not_relevant_cannot_block_or_require_action")
        if (
            self.status == "known"
            and self.assessment is not None
            and not str(self.assessment).strip()
        ):
            raise ValueError("diagnostic_assessment_invalid")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DiagnosticReadiness:
    status: str
    complete: bool
    unresolved_dimension_ids: tuple[str, ...]
    blocking_dimension_ids: tuple[str, ...]
    required_dimensions_not_known: tuple[str, ...]
    invalid_entries: tuple[str, ...] = ()

    @property
    def audit_fingerprint(self) -> str:
        return fingerprint(asdict(self))

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        for key in (
            "unresolved_dimension_ids",
            "blocking_dimension_ids",
            "required_dimensions_not_known",
            "invalid_entries",
        ):
            value[key] = list(value[key])
        value["audit_fingerprint"] = self.audit_fingerprint
        return value


@dataclass(frozen=True)
class DiagnosticLedger:
    entries: tuple[DiagnosticEntry, ...]
    revision: int = 0
    ledger_version: str = DIAGNOSTIC_LEDGER_VERSION

    @classmethod
    def initial(cls) -> DiagnosticLedger:
        return cls(tuple(DiagnosticEntry(id=item) for item in DIAGNOSTIC_IDS))

    def __post_init__(self) -> None:
        ids = tuple(item.id for item in self.entries)
        if ids != DIAGNOSTIC_IDS:
            raise ValueError(
                "diagnostic_ledger_must_contain_exactly_eight_ordered_dimensions"
            )
        if self.revision < 0:
            raise ValueError("diagnostic_revision_invalid")

    def entry(self, dimension_id: str) -> DiagnosticEntry:
        try:
            return next(item for item in self.entries if item.id == dimension_id)
        except StopIteration as exc:
            raise KeyError(dimension_id) from exc

    def update(
        self,
        updates: Mapping[str, Mapping[str, Any] | str],
        *,
        source: str,
        valid_region: str | None = None,
    ) -> DiagnosticLedger:
        """Apply only explicitly supplied evidence; omitted dimensions persist."""

        if not source.strip():
            raise ValueError("diagnostic_source_required")
        by_id = {item.id: item for item in self.entries}
        for dimension_id, raw in updates.items():
            if dimension_id not in by_id:
                raise ValueError(f"unknown_diagnostic_id: {dimension_id}")
            if isinstance(raw, str):
                value = {"status": "known", "evidence": raw, "confidence": 0.75}
            else:
                value = dict(raw)
            status = str(value.get("status", "known"))
            evidence = str(value.get("evidence", "")).strip()
            blocking_value = value.get(
                "blocking_for_current_route",
                status == "unknown",
            )
            if not isinstance(blocking_value, bool):
                raise ValueError(  # noqa: TRY004
                    "diagnostic_blocking_for_current_route_must_be_boolean"
                )
            if status == "unknown":
                by_id[dimension_id] = DiagnosticEntry(
                    id=dimension_id,
                    status="unknown",
                    evidence=evidence,
                    source=source,
                    confidence=float(value.get("confidence", 0.0)),
                    route_consequence=str(value.get("route_consequence", "")),
                    blocking_for_current_route=blocking_value,
                    next_resolving_action=value.get("next_resolving_action"),
                    valid_region=value.get("valid_region", valid_region),
                    assessment=value.get("assessment"),
                    value=value.get("value"),
                )
            else:
                by_id[dimension_id] = DiagnosticEntry(
                    id=dimension_id,
                    status=status,
                    evidence=evidence,
                    source=source,
                    confidence=float(value.get("confidence", 0.75)),
                    route_consequence=str(value.get("route_consequence", "")),
                    blocking_for_current_route=blocking_value,
                    next_resolving_action=value.get("next_resolving_action"),
                    valid_region=value.get("valid_region", valid_region),
                    assessment=value.get("assessment"),
                    value=value.get("value"),
                )
        return replace(
            self,
            entries=tuple(by_id[item] for item in DIAGNOSTIC_IDS),
            revision=self.revision + 1,
        )

    def apply_not_relevant(
        self,
        declarations: Mapping[str, str],
        *,
        task_type: str,
        measured_signals: tuple[str, ...],
        control_input: str,
    ) -> DiagnosticLedger:
        """Apply the small deterministic relevance policy, never an LLM claim."""

        if (
            task_type != "local_setpoint_hold"
            or len(measured_signals) != 1
            or not control_input
        ):
            raise ValueError("task_relevance_policy_not_activated")
        allowed = {"coupling_underactuation"}
        unknown = set(declarations) - allowed
        if unknown:
            raise ValueError(
                "not_relevant_dimension_not_authorized: " + ", ".join(sorted(unknown))
            )
        updates = {
            key: {
                "status": "not_relevant",
                "evidence": value,
                "confidence": 1.0,
                "blocking_for_current_route": False,
                "next_resolving_action": None,
            }
            for key, value in declarations.items()
        }
        return self.update(updates, source="task_policy:v1")

    def readiness(
        self, required_dimensions: tuple[str, ...] | None = None
    ) -> DiagnosticReadiness:
        required = set(required_dimensions or DIAGNOSTIC_IDS)
        by_id = {item.id: item for item in self.entries}
        unresolved = tuple(item.id for item in self.entries if item.status == "unknown")
        blocking = tuple(
            item.id for item in self.entries if item.blocking_for_current_route
        )
        required_not_known = tuple(
            item
            for item in DIAGNOSTIC_IDS
            if item in required and by_id[item].status not in {"known", "not_relevant"}
        )
        invalid = tuple(
            item.id
            for item in self.entries
            if item.status == "not_relevant"
            and (
                item.blocking_for_current_route
                or not item.source.startswith("task_policy:")
            )
        )
        complete = len(self.entries) == len(DIAGNOSTIC_IDS)
        passed = complete and not blocking and not required_not_known and not invalid
        return DiagnosticReadiness(
            status="ready" if passed else "diagnostic_blocker",
            complete=complete,
            unresolved_dimension_ids=unresolved,
            blocking_dimension_ids=blocking,
            required_dimensions_not_known=required_not_known,
            invalid_entries=invalid,
        )

    def to_dict(self) -> dict[str, Any]:
        value = {
            "ledger_version": self.ledger_version,
            "revision": self.revision,
            "entries": [item.to_dict() for item in self.entries],
        }
        value["ledger_fingerprint"] = fingerprint(value)
        return value

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> DiagnosticLedger:
        if value.get("ledger_version") != DIAGNOSTIC_LEDGER_VERSION:
            raise ValueError("diagnostic_ledger_version_mismatch")
        entries = tuple(
            DiagnosticEntry(**dict(item)) for item in value.get("entries", ())
        )
        ledger = cls(entries=entries, revision=int(value.get("revision", 0)))
        stored = value.get("ledger_fingerprint")
        if stored is not None and stored != fingerprint(
            {k: v for k, v in value.items() if k != "ledger_fingerprint"}
        ):
            raise ValueError("diagnostic_ledger_fingerprint_mismatch")
        return ledger
