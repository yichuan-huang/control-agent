"""Public experiment provider interfaces for software-only CFDC runs."""

from __future__ import annotations

import csv
import json
import math
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from .contracts import fingerprint


@dataclass(frozen=True)
class PublicTrace:
    """A source-bound, public trajectory with no hidden object state."""

    trace_id: str
    source: str
    time_s: tuple[float, ...]
    signals: Mapping[str, tuple[float, ...]]
    units: Mapping[str, str]
    protocol_fingerprint: str
    operating_region: str
    trial_id: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
    quality: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not str(self.trace_id).strip() or not str(self.trial_id).strip():
            raise ValueError("public_trace_binding_required")
        if self.source not in {"measured_trace", "model", "demo_fixture", "user_upload"}:
            raise ValueError("public_trace_source_invalid")
        if len(self.time_s) < 2:
            raise ValueError("public_trace_requires_two_samples")
        if any(not math.isfinite(float(value)) for value in self.time_s):
            raise ValueError("public_trace_time_non_finite")
        if any(second <= first for first, second in zip(self.time_s, self.time_s[1:])):
            raise ValueError("public_trace_time_not_increasing")
        if not self.signals:
            raise ValueError("public_trace_signals_required")
        length = len(self.time_s)
        for name, values in self.signals.items():
            if len(values) != length:
                raise ValueError(f"public_trace_signal_length_mismatch: {name}")
            if any(not math.isfinite(float(value)) for value in values):
                raise ValueError(f"public_trace_signal_non_finite: {name}")
            if name not in self.units or not str(self.units[name]).strip():
                raise ValueError(f"public_trace_unit_missing: {name}")
        if not self.protocol_fingerprint.strip() or not self.trial_id.strip():
            raise ValueError("public_trace_binding_required")
        # Canonicalize numeric containers before hashing.  JSON can represent
        # the same sample as ``1`` or ``1.0``; a trace fingerprint must remain
        # stable across constructor and file-loading paths.
        object.__setattr__(self, "time_s", tuple(float(value) for value in self.time_s))
        object.__setattr__(
            self,
            "signals",
            {str(name): tuple(float(value) for value in values) for name, values in self.signals.items()},
        )
        object.__setattr__(self, "units", {str(name): str(unit) for name, unit in self.units.items()})

    @property
    def fingerprint(self) -> str:
        return fingerprint(self.to_dict(include_fingerprint=False))

    def to_dict(self, *, include_fingerprint: bool = True) -> dict[str, Any]:
        value = {
            "trace_id": self.trace_id,
            "source": self.source,
            "time_s": list(self.time_s),
            "signals": {key: list(values) for key, values in self.signals.items()},
            "units": dict(self.units),
            "protocol_fingerprint": self.protocol_fingerprint,
            "operating_region": self.operating_region,
            "trial_id": self.trial_id,
            "metadata": dict(self.metadata),
            "quality": dict(self.quality),
        }
        if include_fingerprint:
            value["trace_fingerprint"] = self.fingerprint
        return value

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> PublicTrace:
        raw = dict(value)
        # Accept both the canonical trace object and the compact public upload
        # vocabulary used by the v3 workbench.  This adapter is deliberately
        # limited to public arrays; it never accepts an object/model payload.
        nested = raw.get("trace")
        if isinstance(nested, Mapping) and not raw.get("signals") and not raw.get("time_s"):
            raw = {**dict(nested), **{key: item for key, item in raw.items() if key != "trace"}}
        supplied_fingerprint = raw.pop("trace_fingerprint", raw.pop("fingerprint", None))
        raw_signals = raw.get("signals") or raw.get("outputs")
        if isinstance(raw_signals, Mapping):
            signals = {
                str(key): tuple(float(item) for item in values)
                for key, values in raw_signals.items()
            }
        else:
            output = raw.get("output")
            if output is None:
                output = raw.get("measured_output")
            signals = (
                {"output": tuple(float(item) for item in output)}
                if isinstance(output, (list, tuple))
                else {}
            )
        units_raw = raw.get("units") or raw.get("signal_units") or {}
        units = {str(key): str(item) for key, item in dict(units_raw).items()}
        if "output" in signals and "output" not in units:
            output_unit = raw.get("output_unit") or raw.get("unit")
            if output_unit:
                units["output"] = str(output_unit)
        trace = cls(
            trace_id=str(raw.get("trace_id") or raw.get("evidence_id") or raw.get("id") or ""),
            source=str(raw.get("source") or raw.get("source_type") or ""),
            time_s=tuple(float(item) for item in (raw.get("time_s") or raw.get("time") or raw.get("timestamps") or raw.get("t") or ())),
            signals=signals,
            units=units,
            protocol_fingerprint=str(raw.get("protocol_fingerprint") or raw.get("protocol_id") or ""),
            operating_region=str(raw.get("operating_region") or raw.get("valid_region") or "declared_operating_region"),
            trial_id=str(raw.get("trial_id") or raw.get("trial") or raw.get("trace_id") or raw.get("id") or ""),
            metadata=dict(raw.get("metadata") or {}),
            quality=dict(raw.get("quality") or {}),
        )
        if supplied_fingerprint is not None and str(supplied_fingerprint) != trace.fingerprint:
            raise ValueError("public_trace_fingerprint_mismatch")
        return trace

    @classmethod
    def from_json_file(cls, path: str | Path, **overrides: Any) -> PublicTrace:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(value, Mapping):
            raise TypeError("public_trace_json_object_required")
        return cls.from_mapping({**dict(value), **overrides})

    @classmethod
    def from_csv_file(
        cls,
        path: str | Path,
        *,
        source: str,
        units: Mapping[str, str],
        protocol_fingerprint: str,
        operating_region: str = "declared_operating_region",
        trial_id: str | None = None,
    ) -> PublicTrace:
        with Path(path).open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        if not rows or "time_s" not in rows[0]:
            raise ValueError("public_trace_csv_requires_time_s_column")
        signals = {name: tuple(float(row[name]) for row in rows) for name in rows[0] if name != "time_s"}
        return cls(
            trace_id=trial_id or Path(path).stem,
            source=source,
            time_s=tuple(float(row["time_s"]) for row in rows),
            signals=signals,
            units=dict(units),
            protocol_fingerprint=protocol_fingerprint,
            operating_region=operating_region,
            trial_id=trial_id or Path(path).stem,
        )


class ExperimentProvider(Protocol):
    provider_id: str
    provider_version: str
    capabilities: frozenset[str]

    def execute(self, operation: Mapping[str, Any], *, task: Mapping[str, Any]) -> PublicTrace | Sequence[PublicTrace]: ...


class EvaluationProvider(Protocol):
    provider_id: str
    provider_version: str
    capabilities: frozenset[str]

    def evaluate(
        self,
        freeze: Mapping[str, Any],
        *,
        task: Mapping[str, Any],
        evaluation_split: str,
        repeats: int,
    ) -> Mapping[str, Any]: ...


@dataclass
class CallableExperimentProvider:
    """Adapter for an existing deterministic simulator or reviewed provider."""

    provider_id: str
    provider_version: str
    callback: Callable[[Mapping[str, Any], Mapping[str, Any]], PublicTrace | Sequence[PublicTrace]]
    capabilities: frozenset[str] = frozenset()

    def execute(self, operation: Mapping[str, Any], *, task: Mapping[str, Any]) -> PublicTrace | Sequence[PublicTrace]:
        result = self.callback(operation, task)
        if isinstance(result, PublicTrace):
            return result
        values = tuple(result)
        if not values or not all(isinstance(item, PublicTrace) for item in values):
            raise ValueError("experiment_provider_must_return_public_trace")
        return values


@dataclass
class CallableEvaluationProvider:
    """Adapter for an isolated evaluator that returns public trial records."""

    provider_id: str
    provider_version: str
    callback: Callable[[Mapping[str, Any], Mapping[str, Any], str, int], Mapping[str, Any]]
    capabilities: frozenset[str] = frozenset({"software_evaluation"})

    def evaluate(
        self,
        freeze: Mapping[str, Any],
        *,
        task: Mapping[str, Any],
        evaluation_split: str,
        repeats: int,
    ) -> Mapping[str, Any]:
        value = self.callback(freeze, task, evaluation_split, repeats)
        if not isinstance(value, Mapping):
            raise TypeError("evaluation_provider_must_return_mapping")
        return value


class CurrentModelExperimentProvider:
    """Adapter around the repository's existing typed model experiment runner."""

    provider_id = "current-model-simulator"
    provider_version = "cfdc-sim/v1"

    def __init__(self, package: Any, plan: Any) -> None:
        if getattr(package, "model", None) is None:
            raise ValueError("model_provider_requires_explicit_model")
        self.package = package
        self.plan = plan
        self.capabilities = frozenset(str(item.primitive) for item in getattr(plan, "instructions", ()))

    def execute(self, operation: Mapping[str, Any], *, task: Mapping[str, Any]) -> tuple[PublicTrace, ...]:
        del task
        primitive = str(operation.get("operation") or operation.get("primitive") or "")
        if primitive and primitive not in self.capabilities:
            raise ValueError(f"provider_operation_not_supported: {primitive}")
        from cfdc.evidence.sources import run_model_experiments

        records = run_model_experiments(self.package, self.plan)
        selected = [record for record in records if not primitive or str(record.primitive) == primitive]
        if not selected:
            raise ValueError("model_provider_returned_no_public_experiment")
        traces: list[PublicTrace] = []
        for index, record in enumerate(selected, 1):
            raw_trace = record.trace
            metadata = dict(getattr(raw_trace, "metadata", {}) or {})
            units = dict(metadata.get("signal_units") or {})
            model = getattr(self.package, "model", None)
            if model is not None:
                output_id = getattr(model, "output_signal_id", None)
                if output_id and getattr(model, "output_units", None):
                    units.setdefault(str(output_id), str(model.output_units))
                for output_id in getattr(model, "output_signal_ids", ()) or ():
                    model_units = getattr(model, "signal_units", {}) or {}
                    if model_units.get(output_id):
                        units.setdefault(str(output_id), str(model_units[output_id]))
            units.setdefault("time", "s")
            traces.append(
                PublicTrace(
                    trace_id=f"model-{index}-{record.primitive}",
                    source="model",
                    time_s=tuple(float(item) for item in raw_trace.time_s),
                    signals={str(key): tuple(float(item) for item in values) for key, values in raw_trace.signals.items()},
                    units={str(key): str(value) for key, value in units.items() if key != "time"},
                    protocol_fingerprint=fingerprint({"provider": self.provider_id, "primitive": record.primitive, "plan": getattr(self.plan, "model_dump", lambda: repr(self.plan))()}),
                    operating_region=str(record.operating_region),
                    trial_id=f"model-{index}",
                    metadata={"evidence_boundary": "user_object_model_simulation", "primitive": str(record.primitive)},
                )
            )
        return tuple(traces)


@dataclass
class ProviderRegistry:
    """Explicit provider registry; it never resolves a Demo from object text."""

    _providers: dict[str, ExperimentProvider] = field(default_factory=dict)

    def register(self, provider: ExperimentProvider) -> None:
        provider_id = str(provider.provider_id).strip()
        if not provider_id:
            raise ValueError("provider_id_required")
        if not str(getattr(provider, "provider_version", "")).strip():
            raise ValueError("provider_version_required")
        capabilities = getattr(provider, "capabilities", frozenset())
        if not isinstance(capabilities, (set, frozenset, tuple, list)):
            raise TypeError("provider_capabilities_must_be_collection")
        if provider_id in self._providers:
            raise ValueError(f"provider_already_registered: {provider_id}")
        self._providers[provider_id] = provider

    def get(self, provider_id: str) -> ExperimentProvider:
        try:
            return self._providers[str(provider_id)]
        except KeyError as exc:
            raise ValueError(f"provider_not_registered: {provider_id}") from exc

    def capabilities(self) -> dict[str, list[str]]:
        return {
            provider_id: sorted(str(item) for item in provider.capabilities)
            for provider_id, provider in sorted(self._providers.items())
        }


@dataclass
class EvaluationProviderRegistry:
    """Registry kept separate from experiment execution providers."""

    _providers: dict[str, EvaluationProvider] = field(default_factory=dict)

    def register(self, provider: EvaluationProvider) -> None:
        provider_id = str(provider.provider_id).strip()
        if not provider_id or not str(getattr(provider, "provider_version", "")).strip():
            raise ValueError("evaluation_provider_contract_required")
        if not callable(getattr(provider, "evaluate", None)):
            raise TypeError("evaluation_provider_evaluate_required")
        capabilities = getattr(provider, "capabilities", frozenset())
        if not isinstance(capabilities, (set, frozenset, tuple, list)):
            raise TypeError("provider_capabilities_must_be_collection")
        if provider_id in self._providers:
            raise ValueError(f"evaluation_provider_already_registered: {provider_id}")
        self._providers[provider_id] = provider

    def get(self, provider_id: str) -> EvaluationProvider:
        try:
            return self._providers[str(provider_id)]
        except KeyError as exc:
            raise ValueError(f"evaluation_provider_not_registered: {provider_id}") from exc

    def capabilities(self) -> dict[str, list[str]]:
        return {
            provider_id: sorted(str(item) for item in provider.capabilities)
            for provider_id, provider in sorted(self._providers.items())
        }


def evidence_from_trace(trace: PublicTrace, *, kind: str = "experiment") -> dict[str, Any]:
    """Convert a public trace to the kernel evidence shape."""

    return {
        "evidence_id": trace.trace_id,
        "kind": kind,
        "source": trace.source,
        "protocol_fingerprint": trace.protocol_fingerprint,
        "signal_units": dict(trace.units),
        "operating_region": trace.operating_region,
        "trial_id": trace.trial_id,
        "trace": trace.to_dict(),
        "trace_fingerprint": trace.fingerprint,
        "provider_metadata": dict(trace.metadata),
        "quality": dict(trace.quality),
    }


__all__ = [
    "CallableEvaluationProvider",
    "CallableExperimentProvider",
    "CurrentModelExperimentProvider",
    "EvaluationProvider",
    "EvaluationProviderRegistry",
    "ExperimentProvider",
    "ProviderRegistry",
    "PublicTrace",
    "evidence_from_trace",
]
