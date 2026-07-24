"""Strict contracts for auditable, LLM-proposed plant models.

The generated-model envelope deliberately wraps the existing
``ExecutableModelSpec`` union. It does not add fields to any executable model
schema, which preserves existing model/session serialization and hashes.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping, Sequence
from typing import Annotated, Any, Literal

from pydantic import Field, ValidationInfo, field_validator, model_validator

from cfdc.models.schemas import (
    CFDCModel,
    ExecutableModelSpec,
    RegisteredNonlinearModelSpec,
    StateSpaceModelSpec,
    TransferFunctionModelSpec,
)


MODEL_QUESTION_CATALOG_VERSION = "v1"
_PLACEHOLDER_UNITS = frozenset(
    {
        "",
        "-",
        "n/a",
        "na",
        "none",
        "null",
        "tbd",
        "unknown",
        "unspecified",
        "unitless?",
        "待定",
        "未知",
        "未指定",
    }
)
_FORBIDDEN_PAYLOAD_KEYS = frozenset(
    {
        "code",
        "ode",
        "callback",
        "url",
        "module",
        "path",
        "expression",
        "function",
        "apikey",
        "token",
        "secret",
        "password",
    }
)


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def _scan_finite(value: Any, path: str = "$") -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"non-finite value at {path}")
    if isinstance(value, Mapping):
        for key, item in value.items():
            _scan_finite(item, f"{path}.{key}")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, item in enumerate(value):
            _scan_finite(item, f"{path}[{index}]")


def _scan_forbidden_payload_keys(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            normalized = "".join(
                character for character in str(key).casefold() if character.isalnum()
            )
            if normalized in _FORBIDDEN_PAYLOAD_KEYS:
                raise ValueError(f"forbidden payload key at {path}.{key}")
            _scan_forbidden_payload_keys(item, f"{path}.{key}")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, item in enumerate(value):
            _scan_forbidden_payload_keys(item, f"{path}[{index}]")


def _validate_unit(unit: str) -> str:
    if not isinstance(unit, str):
        raise ValueError("unit must be a string")
    if unit.strip().casefold() in _PLACEHOLDER_UNITS:
        raise ValueError("placeholder units are not allowed")
    return unit


def _validate_bounds(
    groups: Sequence[Mapping[str, tuple[float, float]]],
) -> None:
    for group in groups:
        for lower, upper in group.values():
            if lower >= upper:
                raise ValueError("every lower bound must be below its upper bound")


def _require_payload_keys(
    payload: Mapping[str, Any],
    *,
    required: set[str],
    optional: set[str] | None = None,
) -> None:
    allowed = required | (optional or set())
    missing = required - set(payload)
    unknown = set(payload) - allowed
    if missing or unknown:
        raise ValueError(
            "fact payload must use its closed field set; "
            f"missing={sorted(missing)}, unknown={sorted(unknown)}"
        )


def _number(value: Any, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{path} must be a finite number")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{path} must be a finite number")
    return number


def _numeric_mapping(value: Any, path: str) -> dict[str, float]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{path} must be an object")
    result: dict[str, float] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not key:
            raise ValueError(f"{path} signal names must be non-empty strings")
        result[key] = _number(item, f"{path}.{key}")
    return result


def _unit_mapping(value: Any, path: str) -> dict[str, str]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{path} must be an object")
    result: dict[str, str] = {}
    for key, unit in value.items():
        if not isinstance(key, str) or not key:
            raise ValueError(f"{path} signal names must be non-empty strings")
        result[key] = _validate_unit(unit)
    return result


def _range_mapping(value: Any, path: str) -> dict[str, tuple[float, float]]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{path} range payload must be an object")
    result: dict[str, tuple[float, float]] = {}
    for key, pair in value.items():
        if (
            not isinstance(key, str)
            or not key
            or not isinstance(pair, (list, tuple))
            or len(pair) != 2
        ):
            raise ValueError(f"{path} range entries must be [lower, upper]")
        lower = _number(pair[0], f"{path}.{key}[0]")
        upper = _number(pair[1], f"{path}.{key}[1]")
        if lower >= upper:
            raise ValueError(f"{path}.{key} range lower value must be below upper")
        result[key] = (lower, upper)
    return result


def _matrix(value: Any, path: str) -> list[list[float]]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{path} must be a non-empty matrix")
    rows: list[list[float]] = []
    width: int | None = None
    for row_index, row in enumerate(value):
        if not isinstance(row, list) or not row:
            raise ValueError(f"{path} must be a non-empty rectangular matrix")
        numeric_row = [
            _number(item, f"{path}[{row_index}][{column_index}]")
            for column_index, item in enumerate(row)
        ]
        if width is None:
            width = len(numeric_row)
        elif len(numeric_row) != width:
            raise ValueError(f"{path} must be a rectangular matrix")
        rows.append(numeric_row)
    return rows


def _validate_step_payload(payload: Mapping[str, Any]) -> None:
    _require_payload_keys(payload, required={"before", "after", "unit"})
    _number(payload["before"], "value_payload.before")
    _number(payload["after"], "value_payload.after")
    _validate_unit(payload["unit"])


def _validate_scalar_payload(fact_type: str, payload: Mapping[str, Any]) -> None:
    _require_payload_keys(payload, required={"value", "unit"})
    value = _number(payload["value"], "value_payload.value")
    _validate_unit(payload["unit"])
    if fact_type == "response_delay":
        if value < 0.0:
            raise ValueError("response delay cannot be negative")
    elif value <= 0.0:
        raise ValueError(f"{fact_type} must be positive")


def _validate_operating_point_payload(payload: Mapping[str, Any]) -> None:
    _require_payload_keys(
        payload,
        required={"inputs", "outputs", "signal_units"},
        optional={"states"},
    )
    groups = [
        _numeric_mapping(payload[name], f"value_payload.{name}")
        for name in ("inputs", "outputs")
    ]
    if "states" in payload:
        groups.append(_numeric_mapping(payload["states"], "value_payload.states"))
    signals = set().union(*(set(group) for group in groups))
    units = _unit_mapping(payload["signal_units"], "value_payload.signal_units")
    if not signals or set(units) != signals:
        raise ValueError(
            "operating-point payload units must exactly cover every signal"
        )


def _validate_validity_region_payload(payload: Mapping[str, Any]) -> None:
    _require_payload_keys(
        payload,
        required={"input_ranges", "output_ranges", "signal_units"},
        optional={"state_ranges"},
    )
    groups = [
        _range_mapping(payload[name], f"value_payload.{name}")
        for name in ("input_ranges", "output_ranges")
    ]
    if "state_ranges" in payload:
        groups.append(
            _range_mapping(payload["state_ranges"], "value_payload.state_ranges")
        )
    signals = set().union(*(set(group) for group in groups))
    units = _unit_mapping(payload["signal_units"], "value_payload.signal_units")
    if not signals or set(units) != signals:
        raise ValueError("validity-region payload units must exactly cover every range")


def _validate_signal_definition_payload(payload: Mapping[str, Any]) -> None:
    _require_payload_keys(payload, required={"inputs", "outputs"}, optional={"states"})
    seen: set[str] = set()
    for group_name in ("inputs", "outputs", "states"):
        if group_name not in payload:
            continue
        group = payload[group_name]
        if not isinstance(group, list) or not group:
            raise ValueError(f"value_payload.{group_name} must be a non-empty list")
        for index, item in enumerate(group):
            if not isinstance(item, Mapping):
                raise ValueError("signal definitions must be objects")
            _require_payload_keys(item, required={"signal_id", "unit"})
            signal_id = item["signal_id"]
            if not isinstance(signal_id, str) or not signal_id:
                raise ValueError("signal_id must be a non-empty string")
            if signal_id in seen:
                raise ValueError("signal IDs must be unique")
            seen.add(signal_id)
            _validate_unit(item["unit"])


def _validate_state_space_payload(payload: Mapping[str, Any]) -> None:
    _require_payload_keys(
        payload,
        required={"a", "b", "c", "d"},
        optional={"matrix_units"},
    )
    a = _matrix(payload["a"], "value_payload.a")
    b = _matrix(payload["b"], "value_payload.b")
    c = _matrix(payload["c"], "value_payload.c")
    d = _matrix(payload["d"], "value_payload.d")
    state_count = len(a)
    input_count = len(b[0])
    output_count = len(c)
    if (
        any(len(row) != state_count for row in a)
        or len(b) != state_count
        or any(len(row) != state_count for row in c)
        or len(d) != output_count
        or any(len(row) != input_count for row in d)
    ):
        raise ValueError("state-space payload matrix dimensions are inconsistent")
    if "matrix_units" in payload:
        matrix_units = payload["matrix_units"]
        if not isinstance(matrix_units, Mapping) or set(matrix_units) != {
            "a",
            "b",
            "c",
            "d",
        }:
            raise ValueError(
                "state-space matrix_units must exactly cover A, B, C, and D"
            )
        for name, matrix in (("a", a), ("b", b), ("c", c), ("d", d)):
            units = matrix_units[name]
            if (
                not isinstance(units, list)
                or len(units) != len(matrix)
                or any(
                    not isinstance(row, list) or len(row) != len(matrix[row_index])
                    for row_index, row in enumerate(units)
                )
            ):
                raise ValueError(
                    "state-space matrix unit dimensions must match matrices"
                )
            for row in units:
                for unit in row:
                    _validate_unit(unit)


def _validate_reference_target_payload(payload: Mapping[str, Any]) -> None:
    _require_payload_keys(payload, required={"values", "signal_units"})
    values = _numeric_mapping(payload["values"], "value_payload.values")
    units = _unit_mapping(payload["signal_units"], "value_payload.signal_units")
    if not values or set(values) != set(units):
        raise ValueError("reference-target units must exactly cover every signal")


def _validate_bound_fact_payload(payload: Mapping[str, Any]) -> None:
    _require_payload_keys(payload, required={"ranges", "signal_units"})
    ranges = _range_mapping(payload["ranges"], "value_payload.ranges")
    units = _unit_mapping(payload["signal_units"], "value_payload.signal_units")
    if not ranges or set(ranges) != set(units):
        raise ValueError("bound-fact units must exactly cover every signal")


def _validate_parameter_uncertainty_payload(
    payload: Mapping[str, Any],
) -> None:
    _require_payload_keys(payload, required={"values", "parameter_units"})
    values = _numeric_mapping(payload["values"], "value_payload.values")
    units = _unit_mapping(
        payload["parameter_units"],
        "value_payload.parameter_units",
    )
    if not values or set(values) != set(units):
        raise ValueError(
            "parameter-uncertainty units must exactly cover every parameter"
        )
    if any(value < 0.0 for value in values.values()):
        raise ValueError("parameter uncertainty cannot be negative")
    if set(units.values()) != {"1"}:
        raise ValueError("parameter uncertainty is relative and must use unit 1")


_CARTPOLE_PARAMETER_NAMES = frozenset(
    {
        "cart_mass_kg",
        "pole_mass_kg",
        "com_length_m",
        "pole_inertia_kg_m2",
        "cart_friction_n_s_m",
        "gravity_m_s2",
        "force_limit_n",
        "cart_position_limit_m",
    }
)
_VTOL_PARAMETER_NAMES = frozenset(
    {
        "mass_kg",
        "pitch_inertia_kg_m2",
        "gravity_m_s2",
        "linear_drag_n_s_m",
        "pitch_damping_n_m_s",
        "thrust_min_n",
        "thrust_max_n",
        "torque_limit_n_m",
    }
)


def _validate_registered_parameter_payload(
    fact_type: str, payload: Mapping[str, Any]
) -> None:
    allowed = (
        _CARTPOLE_PARAMETER_NAMES
        if fact_type == "cartpole_parameters"
        else _VTOL_PARAMETER_NAMES
    )
    if not payload or set(payload) - allowed:
        raise ValueError(
            f"{fact_type} payload contains unknown parameter keys: "
            f"{sorted(set(payload) - allowed)}"
        )
    for name, value in payload.items():
        _number(value, f"value_payload.{name}")


def _validate_fact_payload(
    fact_type: str, value_payload: dict[str, Any]
) -> dict[str, Any]:
    _scan_finite(value_payload)
    _scan_forbidden_payload_keys(value_payload)
    if fact_type in {"input_step", "output_step"}:
        _validate_step_payload(value_payload)
    elif fact_type in {
        "response_delay",
        "response_time_63",
        "oscillation_period",
        "peak_ratio",
        "sample_time",
    }:
        _validate_scalar_payload(fact_type, value_payload)
    elif fact_type == "operating_point":
        _validate_operating_point_payload(value_payload)
    elif fact_type == "validity_region":
        _validate_validity_region_payload(value_payload)
    elif fact_type == "signal_definition":
        _validate_signal_definition_payload(value_payload)
    elif fact_type == "state_space_data":
        _validate_state_space_payload(value_payload)
    elif fact_type == "reference_target":
        _validate_reference_target_payload(value_payload)
    elif fact_type in {"actuator_bounds", "output_bounds"}:
        _validate_bound_fact_payload(value_payload)
    elif fact_type == "parameter_uncertainty":
        _validate_parameter_uncertainty_payload(value_payload)
    elif fact_type in {"cartpole_parameters", "vtol_parameters"}:
        _validate_registered_parameter_payload(fact_type, value_payload)
    else:
        raise ValueError(f"unsupported model fact type: {fact_type}")
    return value_payload


def _fact_type_from_validation_info(info: ValidationInfo) -> str:
    fact_type = info.data.get("fact_type")
    if not isinstance(fact_type, str) or not fact_type:
        raise ValueError("value_payload requires a valid fact_type")
    return fact_type


class ModelQuestionExample(CFDCModel):
    example_id: str = Field(min_length=1, max_length=200)
    fact_type: str = Field(min_length=1, max_length=100)
    unit_family: str = Field(min_length=1, max_length=100)
    context_tags: list[str] = Field(min_length=1, max_length=12)
    answer_text: str = Field(min_length=1, max_length=4000)
    value_payload: dict[str, Any] = Field(min_length=1)

    @field_validator("unit_family")
    @classmethod
    def validate_unit_family(cls, unit_family: str) -> str:
        return _validate_unit(unit_family)

    @field_validator("value_payload")
    @classmethod
    def validate_value_payload(
        cls,
        value_payload: dict[str, Any],
        info: ValidationInfo,
    ) -> dict[str, Any]:
        return _validate_fact_payload(
            _fact_type_from_validation_info(info), value_payload
        )


class ModelQuestionExampleCatalog(CFDCModel):
    schema_version: Literal["model_question_examples/v1"] = "model_question_examples/v1"
    catalog_version: Literal[MODEL_QUESTION_CATALOG_VERSION] = (
        MODEL_QUESTION_CATALOG_VERSION
    )
    examples: list[ModelQuestionExample] = Field(min_length=1)
    content_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_identity_and_hash(self) -> "ModelQuestionExampleCatalog":
        example_ids = [item.example_id for item in self.examples]
        if len(example_ids) != len(set(example_ids)):
            raise ValueError("catalog example IDs must be unique")
        expected_hash = _canonical_sha256(
            self.model_dump(mode="json", exclude={"content_sha256"})
        )
        if self.content_sha256 != expected_hash:
            raise ValueError("model question example catalog content hash mismatch")
        return self


class DiscoveryQuestion(CFDCModel):
    question_id: str = Field(min_length=1, max_length=200)
    fact_id: str = Field(min_length=1, max_length=200)
    fact_type: str = Field(min_length=1, max_length=100)
    prompt: str = Field(min_length=1, max_length=4000)
    answer_kind: Literal["text", "number", "matrix", "structured"]
    unit_family: str = Field(min_length=1, max_length=100)
    example_id: str = Field(min_length=1, max_length=200)
    why_needed: str = Field(min_length=1, max_length=4000)

    @field_validator("unit_family")
    @classmethod
    def validate_unit_family(cls, unit_family: str) -> str:
        return _validate_unit(unit_family)


class NaturalLanguageModelAnswer(CFDCModel):
    """Verbatim answer text awaiting deterministic, typed fact extraction."""

    question_id: str = Field(min_length=1, max_length=200)
    fact_id: str = Field(min_length=1, max_length=200)
    fact_type: str = Field(min_length=1, max_length=100)
    unit_family: str = Field(min_length=1, max_length=100)
    answer_text: str = Field(min_length=1, max_length=10_000)

    @field_validator("unit_family")
    @classmethod
    def validate_unit_family(cls, unit_family: str) -> str:
        return _validate_unit(unit_family)


class ModelFactAnswer(CFDCModel):
    fact_id: str = Field(min_length=1, max_length=200)
    fact_type: str = Field(min_length=1, max_length=100)
    answer_text: str = Field(min_length=1, max_length=10_000)
    value_payload: dict[str, Any] = Field(min_length=1)
    unit_family: str = Field(min_length=1, max_length=100)
    source: Literal[
        "user_supplied",
        "user_adopted_example",
        "problem_statement",
        "manual_or_datasheet",
    ]
    example_id: str | None = Field(default=None, min_length=1, max_length=200)
    example_catalog_version: str | None = Field(
        default=None, min_length=1, max_length=100
    )
    example_content_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    adopted_at: str | None = Field(default=None, min_length=1, max_length=100)

    @field_validator("unit_family")
    @classmethod
    def validate_unit_family(cls, unit_family: str) -> str:
        return _validate_unit(unit_family)

    @field_validator("value_payload")
    @classmethod
    def validate_value_payload(
        cls,
        value_payload: dict[str, Any],
        info: ValidationInfo,
    ) -> dict[str, Any]:
        return _validate_fact_payload(
            _fact_type_from_validation_info(info), value_payload
        )

    @model_validator(mode="after")
    def validate_example_provenance(self) -> "ModelFactAnswer":
        provenance = (
            self.example_id,
            self.example_catalog_version,
            self.example_content_sha256,
            self.adopted_at,
        )
        if self.source == "user_adopted_example":
            if any(value is None for value in provenance):
                raise ValueError(
                    "adopted examples require ID, catalog version, content hash, "
                    "and adoption time"
                )
        elif any(value is not None for value in provenance):
            raise ValueError("only user-adopted examples may carry example provenance")
        return self


class ParameterEvidence(CFDCModel):
    parameter_path: str = Field(min_length=1, max_length=500)
    value: float
    unit: str = Field(min_length=1, max_length=100)
    source: Literal[
        "user_supplied",
        "user_adopted_example",
        "problem_statement",
        "manual_or_datasheet",
        "deterministic_derivation",
        "registry_policy",
    ]
    source_fact_ids: list[str] = Field(min_length=1, max_length=40)
    derivation_rule_id: str | None = Field(default=None, min_length=1, max_length=200)
    unit_conversion: str | None = Field(default=None, min_length=1, max_length=1000)

    @field_validator("unit")
    @classmethod
    def validate_unit(cls, unit: str) -> str:
        return _validate_unit(unit)

    @model_validator(mode="after")
    def validate_derivation_metadata(self) -> "ParameterEvidence":
        if (
            self.source == "deterministic_derivation"
            and self.derivation_rule_id is None
        ):
            raise ValueError(
                "deterministic derivation evidence requires derivation_rule_id"
            )
        if (
            self.source != "deterministic_derivation"
            and self.derivation_rule_id is not None
        ):
            raise ValueError(
                "derivation_rule_id is only valid for deterministic derivations"
            )
        return self


class OperatingPoint(CFDCModel):
    description: str = Field(min_length=1, max_length=4000)
    states: dict[str, float] = Field(default_factory=dict)
    inputs: dict[str, float] = Field(default_factory=dict)
    outputs: dict[str, float] = Field(default_factory=dict)
    signal_units: dict[str, str] = Field(min_length=1)

    @field_validator("signal_units")
    @classmethod
    def validate_units(cls, signal_units: dict[str, str]) -> dict[str, str]:
        for unit in signal_units.values():
            _validate_unit(unit)
        return signal_units

    @model_validator(mode="after")
    def validate_signal_coverage(self) -> "OperatingPoint":
        signals = set(self.states) | set(self.inputs) | set(self.outputs)
        if not signals:
            raise ValueError("operating point requires at least one signal value")
        if set(self.signal_units) != signals:
            raise ValueError(
                "operating-point units must exactly cover states, inputs, and outputs"
            )
        return self


class ValidityRegion(CFDCModel):
    description: str = Field(min_length=1, max_length=4000)
    input_ranges: dict[str, tuple[float, float]] = Field(default_factory=dict)
    output_ranges: dict[str, tuple[float, float]] = Field(default_factory=dict)
    state_ranges: dict[str, tuple[float, float]] = Field(default_factory=dict)
    signal_units: dict[str, str] = Field(min_length=1)
    constant_conditions: list[str] = Field(min_length=1, max_length=20)
    out_of_range_effect: str = Field(min_length=1, max_length=4000)

    @field_validator("signal_units")
    @classmethod
    def validate_units(cls, signal_units: dict[str, str]) -> dict[str, str]:
        for unit in signal_units.values():
            _validate_unit(unit)
        return signal_units

    @model_validator(mode="after")
    def validate_region(self) -> "ValidityRegion":
        groups = (self.input_ranges, self.output_ranges, self.state_ranges)
        _validate_bounds(groups)
        signals = set().union(*(set(group) for group in groups))
        if not signals:
            raise ValueError("validity region requires at least one bounded signal")
        if set(self.signal_units) != signals:
            raise ValueError(
                "validity-region units must exactly cover every bounded signal"
            )
        return self


class ExperimentProposal(CFDCModel):
    initial_state: dict[str, float] = Field(default_factory=dict)
    reference: dict[str, float] = Field(min_length=1)
    horizon_s: float = Field(gt=0.0)
    sample_time_s: float = Field(gt=0.0)
    actuator_bounds: dict[str, tuple[float, float]] = Field(min_length=1)
    state_bounds: dict[str, tuple[float, float]] = Field(default_factory=dict)
    output_bounds: dict[str, tuple[float, float]] = Field(min_length=1)
    signal_units: dict[str, str] = Field(min_length=1)
    evidence_fact_ids: list[str] = Field(min_length=1, max_length=100)
    registry_policy_id: str | None = Field(default=None, min_length=1, max_length=200)

    @field_validator("signal_units")
    @classmethod
    def validate_units(cls, signal_units: dict[str, str]) -> dict[str, str]:
        for unit in signal_units.values():
            _validate_unit(unit)
        return signal_units

    @model_validator(mode="after")
    def validate_experiment(self) -> "ExperimentProposal":
        _validate_bounds((self.actuator_bounds, self.state_bounds, self.output_bounds))
        sample_count = math.floor(self.horizon_s / self.sample_time_s + 1e-12) + 1
        if sample_count > 20_000:
            raise ValueError("experiment proposal exceeds 20,000 samples")
        signals = (
            set(self.initial_state)
            | set(self.reference)
            | set(self.actuator_bounds)
            | set(self.state_bounds)
            | set(self.output_bounds)
        )
        if set(self.signal_units) != signals:
            raise ValueError(
                "experiment units must exactly cover initial, reference, actuator, "
                "state, and output signals"
            )
        return self


_REGISTERED_POLICY_IDS = {
    "underactuated_cartpole": "registered_cartpole_five_scenario/v1",
    "vtol_cascaded": "registered_vtol_five_scenario/v1",
}


def _validate_registered_bounds(
    proposed: Mapping[str, tuple[float, float]],
    registered: Mapping[str, tuple[float, float]],
    field_name: str,
) -> None:
    if set(proposed) != set(registered):
        raise ValueError(
            f"registered experiment {field_name} must use the exact registry "
            "signal-name set"
        )
    for signal_name, (lower, upper) in proposed.items():
        registry_lower, registry_upper = registered[signal_name]
        if lower < registry_lower or upper > registry_upper:
            raise ValueError(
                f"registered experiment {field_name} intervals must be equal "
                "to or inside the registry intervals; "
                f"signal={signal_name!r}"
            )


def _validate_registered_experiment(
    model: RegisteredNonlinearModelSpec,
    experiment: ExperimentProposal,
) -> None:
    expected_policy_id = _REGISTERED_POLICY_IDS[model.template_id]
    if experiment.registry_policy_id != expected_policy_id:
        raise ValueError(
            f"registered model requires exact registry policy ID {expected_policy_id!r}"
        )

    # Imported lazily because the registered runtime imports the public lab
    # contracts while it initializes.
    from cfdc.sim.registered_runtime import registered_run_envelope

    registered = registered_run_envelope(model)
    exact_fields = (
        "reference",
        "horizon_s",
        "sample_time_s",
    )
    for field_name in exact_fields:
        if getattr(experiment, field_name) != registered[field_name]:
            raise ValueError(
                f"registered experiment {field_name} must exactly match "
                "the registry policy"
            )

    for field_name in (
        "actuator_bounds",
        "output_bounds",
        "state_bounds",
    ):
        _validate_registered_bounds(
            getattr(experiment, field_name),
            registered[field_name],
            field_name,
        )


class GeneratedModelEnvelopeV1(CFDCModel):
    envelope_schema_version: Literal["generated_model_envelope/v1"] = (
        "generated_model_envelope/v1"
    )
    model_role: Literal[
        "user_evidence_model",
        "example_hypothesis",
        "local_linear_hypothesis",
        "registered_nonlinear_model",
    ]
    model: ExecutableModelSpec
    operating_point: OperatingPoint | None = None
    validity_region: ValidityRegion | None = None
    parameter_evidence: list[ParameterEvidence] = Field(min_length=1)
    assumptions: list[str] = Field(min_length=1, max_length=20)
    limitations: list[str] = Field(min_length=1, max_length=20)
    plain_language_summary: str = Field(min_length=1, max_length=8000)
    equation_latex: list[str] = Field(min_length=1, max_length=8)
    experiment_proposal: ExperimentProposal

    @model_validator(mode="after")
    def validate_envelope_boundary(self) -> "GeneratedModelEnvelopeV1":
        if self.model_role == "local_linear_hypothesis" and (
            self.operating_point is None or self.validity_region is None
        ):
            raise ValueError(
                "a local-linear hypothesis requires an operating point and "
                "validity region"
            )
        if (
            any(
                item.source == "user_adopted_example"
                for item in self.parameter_evidence
            )
            and self.model_role != "example_hypothesis"
        ):
            raise ValueError(
                "adopted example evidence requires model_role=example_hypothesis"
            )
        if isinstance(self.model, RegisteredNonlinearModelSpec):
            _validate_registered_experiment(self.model, self.experiment_proposal)
        elif self.experiment_proposal.registry_policy_id is not None:
            raise ValueError("a non-registered model cannot claim a registry policy")
        self._validate_model_units()
        return self

    def _validate_model_units(self) -> None:
        if isinstance(self.model, TransferFunctionModelSpec):
            _validate_unit(self.model.input_units)
            _validate_unit(self.model.output_units)
            return
        if isinstance(self.model, StateSpaceModelSpec):
            expected = (
                set(self.model.state_names)
                | set(self.model.input_signal_ids)
                | set(self.model.output_signal_ids)
            )
            if set(self.model.signal_units) != expected:
                raise ValueError(
                    "state-space signal_units must exactly cover every state, "
                    "input, and output"
                )
        elif isinstance(self.model, RegisteredNonlinearModelSpec):
            expected = (
                set(self.model.initial_state)
                | set(self.model.input_signal_ids)
                | set(self.model.output_signal_ids)
            )
            if set(self.model.signal_units) != expected:
                raise ValueError(
                    "registered-model signal_units must exactly cover every state, "
                    "input, and output"
                )
        for unit in self.model.signal_units.values():
            _validate_unit(unit)


class NeedMoreModelResult(CFDCModel):
    status: Literal["need_more"] = "need_more"
    missing_fact_ids: list[str] = Field(min_length=1, max_length=100)
    questions: list[DiscoveryQuestion] = Field(min_length=1, max_length=4)
    recognized_facts: list[ModelFactAnswer] = Field(
        default_factory=list, max_length=100
    )
    rationale: str = Field(min_length=1, max_length=8000)


class ReadyModelResult(CFDCModel):
    status: Literal["ready"] = "ready"
    envelope: GeneratedModelEnvelopeV1
    recognized_facts: list[ModelFactAnswer] = Field(
        default_factory=list, max_length=100
    )
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str = Field(min_length=1, max_length=8000)


class RejectedModelResult(CFDCModel):
    status: Literal["rejected"] = "rejected"
    reason: str = Field(min_length=1, max_length=8000)
    next_steps: list[str] = Field(min_length=1, max_length=4)


GeneratedModelResult = Annotated[
    NeedMoreModelResult | ReadyModelResult | RejectedModelResult,
    Field(discriminator="status"),
]


__all__ = [
    "DiscoveryQuestion",
    "ExperimentProposal",
    "GeneratedModelEnvelopeV1",
    "GeneratedModelResult",
    "MODEL_QUESTION_CATALOG_VERSION",
    "ModelFactAnswer",
    "NaturalLanguageModelAnswer",
    "ModelQuestionExample",
    "ModelQuestionExampleCatalog",
    "NeedMoreModelResult",
    "OperatingPoint",
    "ParameterEvidence",
    "ReadyModelResult",
    "RejectedModelResult",
    "ValidityRegion",
]
