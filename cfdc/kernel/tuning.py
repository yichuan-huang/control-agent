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
        if not 0 < self.max_probes <= 100:
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
            scaled = sorted(
                (
                    values[name] * contract.baseline_multiplier_min,
                    values[name] * contract.baseline_multiplier_max,
                )
            )
            lower = max(float(lower), scaled[0])
            upper = min(float(upper), scaled[1])
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
    confirm_selected: bool = True,
    qualify: Callable[[Mapping[str, float]], Mapping[str, Any]] | None = None,
) -> TuningResult:
    """Select using development only; optionally confirm the frozen winner once.

    Callbacks are trusted Kernel numerical adapters, never decoded provider or
    LLM verdicts. The service sets ``confirm_selected=False`` to persist the new
    freeze before its separate one-shot confirmation command. Direct numerical
    callers may complete both steps here. Fresh scores never affect selection.
    """
    baseline = _validate_parameters(baseline_parameters, contract)
    baseline_score = _score(baseline_result)

    def result(status, parameters, score, probes=(), accepted=False, reason=""):
        return TuningResult(
            status,
            baseline_result,
            dict(parameters),
            score,
            tuple(probes),
            accepted,
            reason,
            contract.fingerprint,
        )

    if not contract.budget_confirmed:
        return result(
            "blocked", baseline, baseline_score, reason="tuning_budget_not_confirmed"
        )
    if baseline_result.get("stable") is not True:
        return result(
            "blocked", baseline, baseline_score, reason="initial_qualification_failed"
        )
    if baseline_result.get("performance_pass") is True:
        return result(
            "skipped",
            baseline,
            baseline_score,
            reason="baseline_already_meets_contract",
        )
    if baseline_score is None or baseline_score < 0:
        return result(
            "blocked",
            baseline,
            baseline_score,
            reason="baseline_violation_score_required",
        )
    best_parameters = dict(baseline)
    best_score = baseline_score
    probes: list[Mapping[str, Any]] = []
    # Materialize candidate order before the first result can influence it.
    candidates = bounded_parameter_candidates(baseline, contract)
    for index, candidate in enumerate(candidates, 1):
        row: dict[str, Any] = {
            "probe_index": index,
            "parameters": dict(candidate),
            "development": None,
            "fresh": None,
            "accepted": False,
        }
        try:
            if qualify is not None:
                qualification = dict(qualify(candidate))
                row["qualification"] = qualification
                if qualification.get("status") != "offline_qualified":
                    row["reason"] = "candidate_qualification_failed"
                    probes.append(row)
                    continue
            development = dict(
                evaluate(candidate, "development", contract.development_repeats)
            )
            row["development"] = development
        except Exception as exc:  # noqa: BLE001 - stop on infrastructure failure
            row.update(
                reason="evaluation_infrastructure_error", error_type=type(exc).__name__
            )
            probes.append(row)
            return result(
                "blocked",
                best_parameters,
                best_score,
                probes,
                reason="evaluation_infrastructure_error",
            )
        if (
            development.get("hard_failure") is True
            or development.get("stable") is not True
        ):
            row["reason"] = "stability_or_hard_failure"
            probes.append(row)
            continue
        score = _score(development)
        strict_gain = best_score - score if score is not None else -1.0
        numerical_floor = max(1e-12, abs(best_score) * 1e-12)
        relative_gain = strict_gain / max(abs(best_score), 1e-12)
        if (
            score is None
            or score < 0
            or strict_gain <= numerical_floor
            or relative_gain < contract.minimum_relative_improvement
        ):
            row["reason"] = "improvement_below_threshold"
            probes.append(row)
            continue
        row.update(
            accepted=True,
            reason="accepted_development_improvement",
            relative_improvement=relative_gain,
        )
        probes.append(row)
        best_parameters, best_score = dict(candidate), score
    if best_parameters == baseline:
        return result(
            "exhausted",
            baseline,
            baseline_score,
            probes,
            reason="no_strict_development_improvement",
        )
    if not confirm_selected:
        return result(
            "selected",
            best_parameters,
            best_score,
            probes,
            True,
            "development_winner_requires_frozen_confirmation",
        )
    # There are no development calls after this point, even if fresh fails.
    row = {
        "kind": "final_confirmation",
        "parameters": dict(best_parameters),
        "fresh": None,
        "accepted": False,
    }
    try:
        fresh = dict(evaluate(best_parameters, "fresh", contract.fresh_repeats))
        row["fresh"] = fresh
    except Exception as exc:  # noqa: BLE001 - final confirmation is never retried here
        row.update(
            reason="confirmation_infrastructure_error", error_type=type(exc).__name__
        )
        probes.append(row)
        return result(
            "confirmation_failed",
            best_parameters,
            best_score,
            probes,
            reason="confirmation_infrastructure_error",
        )
    passed = (
        fresh.get("stable") is True
        and fresh.get("hard_failure") is not True
        and fresh.get("performance_pass") is True
    )
    row.update(
        accepted=passed,
        reason="fresh_confirmation_passed" if passed else "fresh_confirmation_failed",
    )
    probes.append(row)
    return result(
        "completed" if passed else "confirmation_failed",
        best_parameters,
        best_score,
        probes,
        passed,
        row["reason"],
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
