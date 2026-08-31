"""Deterministic, bounded performance tuning after controller qualification."""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from .contracts import TUNING_CONTRACT_VERSION, fingerprint

DEFAULT_PROBE_MULTIPLIERS = (0.5, 0.75, 1.25, 1.5, 2.0, 3.0)


@dataclass(frozen=True)
class TuningContract:
    parameter_whitelist: tuple[str, ...]
    parameter_domains: Mapping[str, tuple[float, float]]
    max_probes: int = 6
    baseline_multiplier_min: float = 0.25
    baseline_multiplier_max: float = 3.0
    minimum_relative_improvement: float = 0.02
    development_repeats: int = 20
    fresh_repeats: int = 20
    budget_confirmed: bool = False
    probe_multipliers: tuple[float, ...] = DEFAULT_PROBE_MULTIPLIERS
    task_fingerprint: str | None = None
    initial_freeze_fingerprint: str | None = None
    evaluation_contract_fingerprint: str | None = None
    contract_version: str = TUNING_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if self.contract_version != TUNING_CONTRACT_VERSION:
            raise ValueError("tuning_contract_version_mismatch")
        if not isinstance(self.budget_confirmed, bool):
            raise ValueError("tuning_budget_confirmed_must_be_boolean")  # noqa: TRY004 - stable API error
        if not 0 < self.max_probes <= 6:
            raise ValueError("tuning_probe_budget_invalid")
        if (
            not math.isfinite(float(self.baseline_multiplier_min))
            or not math.isfinite(float(self.baseline_multiplier_max))
            or self.baseline_multiplier_min <= 0
            or self.baseline_multiplier_min > self.baseline_multiplier_max
        ):
            raise ValueError("tuning_multiplier_domain_invalid")
        if (
            not math.isfinite(float(self.minimum_relative_improvement))
            or self.minimum_relative_improvement < 0
        ):
            raise ValueError("tuning_improvement_threshold_invalid")
        if self.development_repeats <= 0 or self.fresh_repeats <= 0:
            raise ValueError("tuning_repeat_count_invalid")
        if not self.parameter_whitelist:
            raise ValueError("tuning_parameter_whitelist_required")
        if len(set(self.parameter_whitelist)) != len(self.parameter_whitelist):
            raise ValueError("duplicate_tuning_parameter")
        for name in self.parameter_whitelist:
            if name not in self.parameter_domains:
                raise ValueError(f"tuning_domain_missing: {name}")
            lower, upper = self.parameter_domains[name]
            if (
                not math.isfinite(float(lower))
                or not math.isfinite(float(upper))
                or float(lower) >= float(upper)
            ):
                raise ValueError(f"tuning_domain_invalid: {name}")
        if not self.probe_multipliers:
            raise ValueError("tuning_probe_sequence_empty")
        for multiplier in self.probe_multipliers:
            value = float(multiplier)
            if not math.isfinite(value) or value <= 0:
                raise ValueError("tuning_probe_multiplier_invalid")

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> TuningContract:
        raw = dict(value)
        supplied = raw.pop("contract_fingerprint", None)
        budget_confirmed = raw.get("budget_confirmed", False)
        if not isinstance(budget_confirmed, bool):
            raise ValueError("tuning_budget_confirmed_must_be_boolean")  # noqa: TRY004 - stable API error
        contract = cls(
            parameter_whitelist=tuple(
                str(item) for item in raw.get("parameter_whitelist", ()) or ()
            ),
            parameter_domains={
                str(key): tuple(float(bound) for bound in bounds)
                for key, bounds in dict(raw.get("parameter_domains", {})).items()
            },
            max_probes=int(raw.get("max_probes", 6)),
            baseline_multiplier_min=float(raw.get("baseline_multiplier_min", 0.25)),
            baseline_multiplier_max=float(raw.get("baseline_multiplier_max", 3.0)),
            minimum_relative_improvement=float(
                raw.get("minimum_relative_improvement", 0.02)
            ),
            development_repeats=int(raw.get("development_repeats", 20)),
            fresh_repeats=int(raw.get("fresh_repeats", 20)),
            budget_confirmed=budget_confirmed,
            probe_multipliers=tuple(
                float(item)
                for item in raw.get("probe_multipliers", DEFAULT_PROBE_MULTIPLIERS)
            ),
            task_fingerprint=(
                str(
                    raw.get("task_fingerprint")
                    or raw.get("task_contract_fingerprint")
                    or ""
                )
                or None
            ),
            initial_freeze_fingerprint=(
                str(
                    raw.get("initial_freeze_fingerprint")
                    or raw.get("initial_controller_freeze_fingerprint")
                    or ""
                )
                or None
            ),
            evaluation_contract_fingerprint=(
                str(
                    raw.get("evaluation_contract_fingerprint")
                    or raw.get("independent_judge_contract_fingerprint")
                    or ""
                )
                or None
            ),
            contract_version=str(
                raw.get("contract_version") or TUNING_CONTRACT_VERSION
            ),
        )
        if supplied is not None and str(supplied) != contract.fingerprint:
            raise ValueError("tuning_contract_fingerprint_mismatch")
        return contract

    @property
    def fingerprint(self) -> str:
        return fingerprint(self.to_dict(include_fingerprint=False))

    def to_dict(self, *, include_fingerprint: bool = True) -> dict[str, Any]:
        value = {
            "contract_version": self.contract_version,
            "parameter_whitelist": list(self.parameter_whitelist),
            "parameter_domains": {
                key: list(bounds) for key, bounds in self.parameter_domains.items()
            },
            "max_probes": self.max_probes,
            "baseline_multiplier_min": self.baseline_multiplier_min,
            "baseline_multiplier_max": self.baseline_multiplier_max,
            "minimum_relative_improvement": self.minimum_relative_improvement,
            "development_repeats": self.development_repeats,
            "fresh_repeats": self.fresh_repeats,
            "budget_confirmed": self.budget_confirmed,
            "probe_multipliers": list(self.probe_multipliers),
            "task_fingerprint": self.task_fingerprint,
            "initial_freeze_fingerprint": self.initial_freeze_fingerprint,
            "evaluation_contract_fingerprint": self.evaluation_contract_fingerprint,
        }
        if include_fingerprint:
            value["contract_fingerprint"] = self.fingerprint
        return value


@dataclass(frozen=True)
class TuningResult:
    status: str
    baseline: Mapping[str, Any]
    best_parameters: Mapping[str, float]
    best_score: float | None
    probes: tuple[Mapping[str, Any], ...] = ()
    accepted: bool = False
    reason: str = ""
    contract_fingerprint: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "baseline": dict(self.baseline),
            "best_parameters": dict(self.best_parameters),
            "best_score": self.best_score,
            "probes": [dict(item) for item in self.probes],
            "accepted": self.accepted,
            "reason": self.reason,
            "contract_fingerprint": self.contract_fingerprint,
        }


def _validate_parameters(
    parameters: Mapping[str, Any], contract: TuningContract
) -> dict[str, float]:
    values: dict[str, float] = {}
    for name in contract.parameter_whitelist:
        if name not in parameters:
            raise ValueError(f"tuning_baseline_parameter_missing: {name}")
        number = float(parameters[name])
        if not math.isfinite(number):
            raise ValueError(f"tuning_parameter_non_finite: {name}")
        lower, upper = contract.parameter_domains[name]
        if not float(lower) <= number <= float(upper):
            raise ValueError(f"tuning_baseline_out_of_domain: {name}")
        values[name] = number
    return values


def bounded_parameter_candidates(
    baseline: Mapping[str, Any], contract: TuningContract
) -> tuple[dict[str, float], ...]:
    """Generate a fixed, reproducible probe sequence in the legal domain."""

    values = _validate_parameters(baseline, contract)
    candidates: list[dict[str, float]] = []
    for multiplier in contract.probe_multipliers:
        if len(candidates) >= contract.max_probes:
            break
        candidate = dict(values)
        legal = True
        for name in contract.parameter_whitelist:
            value = values[name] * float(multiplier)
            lower, upper = contract.parameter_domains[name]
            lower = max(float(lower), values[name] * contract.baseline_multiplier_min)
            upper = min(float(upper), values[name] * contract.baseline_multiplier_max)
            if lower > upper or not lower <= value <= upper:
                legal = False
                break
            candidate[name] = value
        if legal and candidate != values and candidate not in candidates:
            candidates.append(candidate)
    return tuple(candidates)


def run_bounded_tuning(
    baseline_parameters: Mapping[str, Any],
    contract: TuningContract,
    evaluate: Callable[[Mapping[str, float], str, int], Mapping[str, Any]],
    *,
    baseline_result: Mapping[str, Any],
) -> TuningResult:
    """Evaluate deterministic probes and confirm only the selected best.

    ``evaluate(parameters, split, repeats)`` must return public metrics.  The
    callback may be backed by the existing simulator but cannot expose private
    object truth.  Fresh confirmation is deliberately never fed back into the
    development search.
    """

    if not contract.budget_confirmed:
        return TuningResult(
            "blocked",
            baseline_result,
            dict(baseline_parameters),
            None,
            reason="tuning_budget_not_confirmed",
            contract_fingerprint=contract.fingerprint,
        )
    baseline = _validate_parameters(baseline_parameters, contract)
    if baseline_result.get("stable") is not True:
        return TuningResult(
            "blocked",
            baseline_result,
            baseline,
            _score(baseline_result),
            reason="initial_qualification_failed",
            contract_fingerprint=contract.fingerprint,
        )
    if baseline_result.get("performance_pass") is True:
        return TuningResult(
            "skipped",
            baseline_result,
            baseline,
            _score(baseline_result),
            reason="baseline_already_meets_contract",
            contract_fingerprint=contract.fingerprint,
        )
    baseline_score = _score(baseline_result)
    if baseline_score is None:
        return TuningResult(
            "blocked",
            baseline_result,
            baseline,
            None,
            reason="baseline_score_missing",
            contract_fingerprint=contract.fingerprint,
        )
    best_parameters = dict(baseline)
    best_score = baseline_score
    best_development_score = baseline_score
    probes: list[Mapping[str, Any]] = []
    for index, candidate in enumerate(
        bounded_parameter_candidates(baseline, contract), 1
    ):
        try:
            development = dict(
                evaluate(candidate, "development", contract.development_repeats)
            )
        except Exception as exc:  # noqa: BLE001 - provider failures are a hard tuning stop
            probes.append(
                {
                    "probe_index": index,
                    "parameters": dict(candidate),
                    "development": None,
                    "fresh": None,
                    "accepted": False,
                    "reason": "evaluation_infrastructure_error",
                    "error_type": type(exc).__name__,
                }
            )
            return TuningResult(
                "blocked",
                baseline_result,
                best_parameters,
                best_score,
                tuple(probes),
                False,
                "evaluation_infrastructure_error",
                contract.fingerprint,
            )
        row: dict[str, Any] = {
            "probe_index": index,
            "parameters": dict(candidate),
            "development": development,
            "fresh": None,
            "accepted": False,
        }
        if (
            development.get("hard_failure") is True
            or development.get("stable") is not True
        ):
            row["reason"] = "stability_or_hard_failure"
            probes.append(row)
            continue
        score = _score(development)
        if score is None or score < best_development_score * (
            1.0 + contract.minimum_relative_improvement
        ):
            row["reason"] = "improvement_below_threshold"
            probes.append(row)
            continue
        try:
            fresh = dict(evaluate(candidate, "fresh", contract.fresh_repeats))
        except Exception as exc:  # noqa: BLE001 - provider failures are a hard tuning stop
            row["reason"] = "evaluation_infrastructure_error"
            row["error_type"] = type(exc).__name__
            probes.append(row)
            return TuningResult(
                "blocked",
                baseline_result,
                best_parameters,
                best_score,
                tuple(probes),
                False,
                "evaluation_infrastructure_error",
                contract.fingerprint,
            )
        row["fresh"] = fresh
        if fresh.get("hard_failure") is True or fresh.get("stable") is not True:
            row["reason"] = "fresh_confirmation_failed"
            probes.append(row)
            continue
        fresh_score = _score(fresh)
        if fresh_score is None or fresh_score < best_development_score * (
            1.0 + contract.minimum_relative_improvement
        ):
            row["reason"] = "fresh_improvement_below_threshold"
            probes.append(row)
            continue
        row["accepted"] = True
        row["reason"] = "accepted_improvement"
        probes.append(row)
        # Fresh data confirms the candidate, but is not reused to generate new
        # probes.  The deterministic sequence continues to exhaust the budget.
        # Development results decide which later probes are eligible.  Fresh
        # confirmation is retained as holdout evidence and never changes the
        # next probe's threshold or sequence.
        best_development_score = score
        best_score = fresh_score
        best_parameters = dict(candidate)
    accepted = best_parameters != baseline
    return TuningResult(
        "completed",
        baseline_result,
        best_parameters,
        best_score,
        tuple(probes),
        accepted,
        "best_candidate_selected"
        if accepted
        else "no_candidate_met_improvement_and_fresh_gates",
        contract.fingerprint,
    )


def _score(result: Mapping[str, Any]) -> float | None:
    for key in ("score", "performance_score", "objective"):
        if result.get(key) is not None:
            try:
                number = float(result[key])
            except (TypeError, ValueError):
                return None
            return number if math.isfinite(number) else None
    metrics = result.get("metrics")
    if isinstance(metrics, Mapping) and metrics.get("score") is not None:
        return _score({"score": metrics["score"]})
    return None


__all__ = [
    "TuningContract",
    "TuningResult",
    "bounded_parameter_candidates",
    "run_bounded_tuning",
]
