"""Legal information-action choice and pre-execution budget accounting."""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass, field, replace


@dataclass(frozen=True)
class InformationAction:
    action_id: str
    purpose: str
    prerequisites: Mapping[str, bool]
    candidate_outcomes: Mapping[str, tuple[str, ...]]
    risk: float
    cost: float

    def __post_init__(self) -> None:
        if not self.action_id or not self.purpose or not self.candidate_outcomes:
            raise ValueError("information_action_incomplete")
        if (
            not math.isfinite(self.risk)
            or not math.isfinite(self.cost)
            or self.risk < 0
            or self.cost < 0
        ):
            raise ValueError("information_action_risk_cost_invalid")
        if any(not outcomes for outcomes in self.candidate_outcomes.values()):
            raise ValueError("information_action_outcomes_required")


@dataclass(frozen=True)
class ActionSelection:
    action_id: str | None
    target_unknowns: tuple[str, ...]
    score: tuple[float, ...] | None
    reason: str
    blocked_actions: Mapping[str, list[str]] = field(default_factory=dict)


@dataclass(frozen=True)
class ActionBudget:
    max_distinct_experiments: int
    max_excitation_time_s: float
    max_failures_per_action: int
    attempts: int = 0
    failed_attempts: int = 0
    excitation_time_s: float = 0.0
    valid_experiments: int = 0
    distinct_protocols: tuple[str, ...] = ()
    action_failures: Mapping[str, int] = field(default_factory=dict)
    pending: tuple[tuple[str, str, float], ...] = ()

    def __post_init__(self) -> None:
        if (
            self.max_distinct_experiments < 0
            or self.max_failures_per_action < 0
            or not math.isfinite(self.max_excitation_time_s)
            or self.max_excitation_time_s < 0
        ):
            raise ValueError("action_budget_invalid")

    def reserve(
        self, action_id: str, *, protocol_fingerprint: str, excitation_time_s: float
    ) -> ActionBudget:
        """Reserve before calling a provider; even a crash consumes the attempt/time."""
        if (
            not action_id
            or not protocol_fingerprint
            or not math.isfinite(excitation_time_s)
            or excitation_time_s < 0
        ):
            raise ValueError("action_reservation_invalid")
        if self.action_failures.get(action_id, 0) > self.max_failures_per_action:
            raise ValueError("action_failure_retry_budget_exhausted")
        distinct = self.distinct_protocols + (
            (protocol_fingerprint,)
            if protocol_fingerprint not in self.distinct_protocols
            else ()
        )
        if len(distinct) > self.max_distinct_experiments:
            raise ValueError("distinct_experiment_budget_exhausted")
        if (
            self.excitation_time_s + excitation_time_s
            > self.max_excitation_time_s + 1e-12
        ):
            raise ValueError("excitation_time_budget_exhausted")
        return replace(
            self,
            attempts=self.attempts + 1,
            excitation_time_s=self.excitation_time_s + excitation_time_s,
            distinct_protocols=distinct,
            pending=(
                *self.pending,
                (action_id, protocol_fingerprint, excitation_time_s),
            ),
        )

    def _consume(
        self, action_id: str, protocol_fingerprint: str
    ) -> tuple[tuple[str, str, float], ...]:
        pending = list(self.pending)
        try:
            pending.remove(
                next(
                    item
                    for item in pending
                    if item[:2] == (action_id, protocol_fingerprint)
                )
            )
        except StopIteration as exc:
            raise ValueError("action_attempt_not_reserved") from exc
        return tuple(pending)

    def record_failure(
        self, action_id: str, *, protocol_fingerprint: str
    ) -> ActionBudget:
        failures = Counter(self.action_failures)
        failures[action_id] += 1
        return replace(
            self,
            failed_attempts=self.failed_attempts + 1,
            action_failures=dict(failures),
            pending=self._consume(action_id, protocol_fingerprint),
        )

    def record_valid(
        self, action_id: str, *, protocol_fingerprint: str
    ) -> ActionBudget:
        return replace(
            self,
            valid_experiments=self.valid_experiments + 1,
            pending=self._consume(action_id, protocol_fingerprint),
        )


def select_action(
    candidates: tuple[str, ...],
    actions: list[InformationAction],
    prerequisites: Mapping[str, bool | None],
    budget: ActionBudget,
) -> ActionSelection:
    """Maximize worst elimination, then expected elimination, then risk/cost."""
    unique = tuple(dict.fromkeys(candidates))
    if len(unique) < 2:
        return ActionSelection(None, unique, None, "candidate_set_already_resolved")
    blocked: dict[str, list[str]] = {}
    ranked: list[tuple[tuple[float, ...], InformationAction]] = []
    for action in actions:
        missing = [
            name
            for name, required in action.prerequisites.items()
            if required and prerequisites.get(name) is not True
        ]
        if missing:
            blocked[action.action_id] = missing
            continue
        if not set(unique) <= set(action.candidate_outcomes):
            blocked[action.action_id] = ["candidate_outcome_contract"]
            continue
        # A candidate may permit multiple result labels. Conservative bins add
        # it to each possible partition; the worst retained size drives choice.
        bins: Counter[str] = Counter()
        for candidate in unique:
            for outcome in set(action.candidate_outcomes[candidate]):
                bins[outcome] += 1
        maximum = max(bins.values())
        worst_elimination = len(unique) - maximum
        average_elimination = len(unique) - sum(
            value * value for value in bins.values()
        ) / max(sum(bins.values()), 1)
        score = (
            float(worst_elimination),
            float(average_elimination),
            -action.risk,
            -action.cost,
        )
        ranked.append((score, action))
    if not ranked:
        return ActionSelection(
            None, unique, None, "no_legal_information_action", blocked
        )
    score, action = max(ranked, key=lambda row: (row[0], row[1].action_id))
    # Non-discriminating passive observation remains actionable when every
    # excitation is illegal; its zero information score is explicit.
    return ActionSelection(
        action.action_id,
        unique,
        score,
        f"selected_by_maximin_information_then_expected_elimination_risk_cost:{action.purpose}",
        blocked,
    )
