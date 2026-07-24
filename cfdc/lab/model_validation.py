"""Deterministic safety gate for LLM-generated plant-model envelopes."""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal

import numpy as np
from pydantic import Field, TypeAdapter, model_validator

from cfdc.lab.model_contracts import (
    GeneratedModelEnvelopeV1,
    GeneratedModelResult,
    ModelFactAnswer,
    ModelQuestionExampleCatalog,
    NaturalLanguageModelAnswer,
    ReadyModelResult,
    RejectedModelResult,
)
from cfdc.models.schemas import (
    ArchetypeClassification,
    CFDCModel,
    RegisteredNonlinearModelSpec,
    StateSpaceModelSpec,
    StructuralDiagnosis,
    SystemDescription,
    TransferFunctionModelSpec,
)


ModelKind = Literal[
    "transfer_function", "state_space", "registered_nonlinear"
]
RegisteredTemplate = Literal["underactuated_cartpole", "vtol_cascaded"]

_FORBIDDEN_KEYS = frozenset(
    {
        "code",
        "ode",
        "callback",
        "url",
        "module",
        "path",
        "expression",
        "function",
        "script",
        "callable",
        "import",
    }
)
_FORBIDDEN_TEXT = re.compile(
    r"```"
    r"|\b(?:import|exec|eval|lambda)\b"
    r"|__[A-Za-z0-9_]+__"
    r"|https?://"
    r"|\b(?:os|subprocess|pathlib|sys)\s*\."
    r"|\b(?:rm\s+-[a-z]*r[a-z]*|curl|wget|powershell)\b"
    r"|\b(?:bash|sh)\s+-c\b"
    r"|(?:\.\./)+(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+"
    r"|(?:^|\s)/(?:etc|tmp|var|usr|bin)/[^\s]*"
    r"|\b[A-Za-z_]\w*\.(?:py|sh|bash|exe|dll|so)\b"
    r"|\b[A-Za-z_]\w*(?:\.[A-Za-z_]\w*){1,}\b"
    r"|\b(?:d[A-Za-z_]\w*/dt|dx/dt)\s*="
    r"|\b[A-Za-z_]\w*\s*=\s*[A-Za-z_]\w*\s*\("
    r"|\b(?:def|class)\s+[A-Za-z_]\w*\s*[:(]"
    r"|\$\(",
    re.IGNORECASE,
)
_FORBIDDEN_LATEX_TEXT = re.compile(
    r"```|\b(?:import|exec|lambda)\b|__[A-Za-z0-9_]+__|https?://"
    r"|\b(?:os|subprocess|pathlib|sys)\s*\."
    r"|\b[A-Za-z_]\w*(?:\.[A-Za-z_]\w*){1,}\b"
    r"|\b(?:rm\s+-[a-z]*r[a-z]*|curl|wget|powershell)\b"
    r"|(?:\.\./)+",
    re.IGNORECASE,
)
_REGISTERED_PARAMETERS = {
    "underactuated_cartpole": frozenset(
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
    ),
    "vtol_cascaded": frozenset(
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
    ),
}
_REGISTERED_PARAMETER_UNITS = {
    "cart_mass_kg": "kg",
    "pole_mass_kg": "kg",
    "com_length_m": "m",
    "pole_inertia_kg_m2": "kg*m^2",
    "cart_friction_n_s_m": "N*s/m",
    "gravity_m_s2": "m/s^2",
    "force_limit_n": "N",
    "cart_position_limit_m": "m",
    "mass_kg": "kg",
    "pitch_inertia_kg_m2": "kg*m^2",
    "linear_drag_n_s_m": "N*s/m",
    "pitch_damping_n_m_s": "N*m*s",
    "thrust_min_n": "N",
    "thrust_max_n": "N",
    "torque_limit_n_m": "N*m",
}
_REGISTERED_UNIT_CONVERSIONS: dict[
    str, tuple[str, str, float, float]
] = {
    "milliseconds_to_seconds/v1": ("ms", "s", 0.001, 0.0),
    "seconds_to_milliseconds/v1": ("s", "ms", 1000.0, 0.0),
    "kilowatts_to_watts/v1": ("kW", "W", 1000.0, 0.0),
    "watts_to_kilowatts/v1": ("W", "kW", 0.001, 0.0),
    "degrees_to_radians/v1": ("deg", "rad", math.pi / 180.0, 0.0),
    "radians_to_degrees/v1": ("rad", "deg", 180.0 / math.pi, 0.0),
    "percent_to_fraction/v1": ("%", "1", 0.01, 0.0),
    "celsius_to_kelvin/v1": ("degC", "K", 1.0, 273.15),
    "kelvin_to_celsius/v1": ("K", "degC", 1.0, -273.15),
}
_REGISTERED_DERIVATION_RULES = frozenset(
    {
        "first_order_step_gain/v1",
        "step_response_gain/v1",
        "step_ratio_gain/v1",
        "first_order_time_constant/v1",
        "response_time_63/v1",
        "response_delay/v1",
        "sample_time/v1",
        "normalized_one/v1",
        "constant_one/v1",
        "normalized_zero/v1",
        "constant_zero/v1",
        "six_time_constants_horizon/v1",
        "time_constant_div_50_sample/v1",
        "output_step_delta_reference/v1",
        "center_actuator_bounds_at_input_before/v1",
        "center_output_bounds_at_output_before/v1",
    }
)
_REGISTERED_POLICY_IDS = frozenset(
    {
        "registered_cartpole_five_scenario/v1",
        "registered_vtol_five_scenario/v1",
    }
)
_SIMPLE_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,199}$")
_NUMBER_LITERAL = re.compile(
    r"(?<![A-Za-z0-9_.])[-+]?(?:\d+(?:\.\d*)?|\.\d+)"
    r"(?:[eE][-+]?\d+)?(?![A-Za-z0-9_.])"
)
_VERSIONED_IDENTIFIER = re.compile(
    r"^[a-z0-9][a-z0-9_.-]{0,190}\.v[0-9]{1,6}$"
)
_PARAMETER_PATH = re.compile(
    r"^[A-Za-z][A-Za-z0-9_]*"
    r"(?:\.[A-Za-z][A-Za-z0-9_]*|\[\d{1,6}\]){1,30}$"
)
_DANGEROUS_IDENTIFIER = re.compile(
    r"https?://|(?:\.\./)|```|\b(?:import|exec|eval|lambda)\b"
    r"|^(?:os|sys|pathlib|subprocess)(?:[./]|$)"
    r"|\b(?:system|popen|spawn|shell|callback|module|function)\b",
    re.IGNORECASE,
)
_UNSAFE_MAPPING_KEY = re.compile(
    r"https?://|(?:\.\./)|```|\b(?:import|exec|eval|lambda)\b"
    r"|^(?:os|sys|pathlib|subprocess)(?:[./]|$)"
    r"|^/(?:etc|tmp|var|usr|bin)/"
    r"|\.(?:py|sh|bash|exe|dll|so)$"
    r"|\$\(|\b(?:system|popen|spawn|shell|callback|function)\b",
    re.IGNORECASE,
)
_IDENTIFIER_MAP_FIELDS = frozenset(
    {
        "states",
        "inputs",
        "outputs",
        "signal_units",
        "parameters",
        "parameter_uncertainty",
        "parameter_units",
        "initial_state",
        "reference",
        "actuator_bounds",
        "state_bounds",
        "output_bounds",
        "input_ranges",
        "state_ranges",
        "output_ranges",
        "ranges",
        "values",
    }
)


@dataclass(frozen=True)
class _NumericFactLeaf:
    fact_type: str
    payload_path: str
    value: float
    unit: str


class ModelValidationContext(CFDCModel):
    """Evidence and closed runtime sets used by the deterministic gate."""

    description: SystemDescription
    diagnosis: StructuralDiagnosis
    classification: ArchetypeClassification
    facts: list[ModelFactAnswer] = Field(default_factory=list, max_length=200)
    natural_language_answers: list[NaturalLanguageModelAnswer] = Field(
        default_factory=list, max_length=200
    )
    allowed_model_kinds: list[ModelKind] = Field(
        default_factory=lambda: [
            "transfer_function",
            "state_space",
            "registered_nonlinear",
        ],
        min_length=1,
    )
    allowed_registered_templates: list[RegisteredTemplate] = Field(
        default_factory=lambda: [
            "underactuated_cartpole",
            "vtol_cascaded",
        ]
    )

    @model_validator(mode="after")
    def validate_closed_sets(self) -> "ModelValidationContext":
        fact_ids = [fact.fact_id for fact in self.facts]
        if len(fact_ids) != len(set(fact_ids)):
            raise ValueError("model validation fact IDs must be unique")
        answer_fact_ids = [
            answer.fact_id for answer in self.natural_language_answers
        ]
        if len(answer_fact_ids) != len(set(answer_fact_ids)):
            raise ValueError(
                "natural-language model answer fact IDs must be unique"
            )
        if set(fact_ids) & set(answer_fact_ids):
            raise ValueError(
                "typed facts and untyped answer texts cannot share fact IDs"
            )
        if len(self.allowed_model_kinds) != len(
            set(self.allowed_model_kinds)
        ):
            raise ValueError("allowed model kinds must be unique")
        if len(self.allowed_registered_templates) != len(
            set(self.allowed_registered_templates)
        ):
            raise ValueError("allowed registered templates must be unique")
        return self


def _normalized_key(value: Any) -> str:
    return "".join(
        character
        for character in str(value).casefold()
        if character.isalnum()
    )


def _unsafe_findings(
    value: Any,
    path: str = "$",
    *,
    display_latex: bool = False,
    identifier_kind: str | None = None,
    identifier_map: bool = False,
) -> list[str]:
    findings: list[str] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str) or _UNSAFE_MAPPING_KEY.search(str(key)):
                findings.append(f"forbidden mapping key at {path}")
            if identifier_map and (
                not isinstance(key, str)
                or _SIMPLE_IDENTIFIER.fullmatch(key) is None
            ):
                findings.append(f"invalid identifier mapping key at {path}")
            normalized = _normalized_key(key)
            if normalized in _FORBIDDEN_KEYS or any(
                normalized.endswith(suffix)
                for suffix in ("code", "script", "callable", "function")
            ):
                findings.append(f"forbidden executable field at {path}.{key}")
            findings.extend(
                _unsafe_findings(
                    item,
                    f"{path}.{key}",
                    display_latex=(str(key) == "equation_latex"),
                    identifier_map=str(key) in _IDENTIFIER_MAP_FIELDS,
                    identifier_kind=(
                        str(key)
                        if str(key)
                        in {
                            "parameter_path",
                            "derivation_rule_id",
                            "unit_conversion",
                            "example_id",
                            "fact_id",
                            "question_id",
                            "registry_policy_id",
                            "source_fact_ids",
                            "signal_id",
                            "input_signal_id",
                            "output_signal_id",
                            "state_names",
                            "input_signal_ids",
                            "output_signal_ids",
                        }
                        else None
                    ),
                )
            )
    elif isinstance(value, Sequence) and not isinstance(
        value, (str, bytes, bytearray)
    ):
        for index, item in enumerate(value):
            findings.extend(
                _unsafe_findings(
                    item,
                    f"{path}[{index}]",
                    display_latex=display_latex,
                    identifier_kind=identifier_kind,
                    identifier_map=identifier_map,
                )
            )
    elif isinstance(value, str):
        if identifier_kind is not None:
            findings.extend(
                _identifier_findings(identifier_kind, value, path)
            )
        else:
            pattern = (
                _FORBIDDEN_LATEX_TEXT if display_latex else _FORBIDDEN_TEXT
            )
            if pattern.search(value):
                findings.append(f"forbidden executable text at {path}")
    elif isinstance(value, float) and not math.isfinite(value):
        findings.append(f"non-finite numeric value at {path}")
    return findings


def _identifier_findings(
    kind: str, value: str, path: str
) -> list[str]:
    if _DANGEROUS_IDENTIFIER.search(value):
        return [f"forbidden identifier content at {path}"]
    valid = False
    if kind in {
        "fact_id",
        "question_id",
        "source_fact_ids",
        "signal_id",
        "input_signal_id",
        "output_signal_id",
        "state_names",
        "input_signal_ids",
        "output_signal_ids",
    }:
        valid = _SIMPLE_IDENTIFIER.fullmatch(value) is not None
    elif kind == "example_id":
        valid = (
            len(value) <= 200
            and ".." not in value
            and _VERSIONED_IDENTIFIER.fullmatch(value) is not None
        )
    elif kind == "parameter_path":
        valid = (
            len(value) <= 500
            and _PARAMETER_PATH.fullmatch(value) is not None
        )
    elif kind == "derivation_rule_id":
        valid = value in _REGISTERED_DERIVATION_RULES
    elif kind == "unit_conversion":
        valid = value in _REGISTERED_UNIT_CONVERSIONS
    elif kind == "registry_policy_id":
        valid = value in _REGISTERED_POLICY_IDS
    if not valid:
        return [f"invalid closed identifier at {path}"]
    return []


def validate_non_executable_content(value: Any) -> None:
    """Reject code-like or external-reference content without evaluating it."""

    findings = _unsafe_findings(value)
    if findings:
        raise ValueError("unsafe non-executable content: " + "; ".join(findings))


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


def _reject(reason: str) -> RejectedModelResult:
    return RejectedModelResult(
        reason=reason[:8000],
        next_steps=[
            "Provide complete numeric facts and units, then request a new model."
        ],
    )


def _signals(
    model: TransferFunctionModelSpec
    | StateSpaceModelSpec
    | RegisteredNonlinearModelSpec,
) -> tuple[set[str], set[str]]:
    if isinstance(model, TransferFunctionModelSpec):
        return {model.input_signal_id}, {model.output_signal_id}
    return set(model.input_signal_ids), set(model.output_signal_ids)


def _effective_polynomial_length(values: Sequence[float]) -> int:
    for index, value in enumerate(values):
        if abs(value) > 0.0:
            return len(values) - index
    return 0


def _validate_model_shape(
    envelope: GeneratedModelEnvelopeV1,
    context: ModelValidationContext,
) -> None:
    model = envelope.model
    if model.kind not in context.allowed_model_kinds:
        raise ValueError("generated model kind is not allowlisted")
    if isinstance(model, TransferFunctionModelSpec):
        if len(model.numerator) > 128 or len(model.denominator) > 128:
            raise ValueError(
                "transfer-function coefficient count exceeds the safety limit"
            )
        if _effective_polynomial_length(
            model.numerator
        ) > _effective_polynomial_length(model.denominator):
            raise ValueError("transfer function must be proper")
        if model.time_domain == "continuous" and model.sample_time_s is not None:
            raise ValueError("continuous transfer function cannot set sample time")
        if model.time_domain == "discrete":
            if model.sample_time_s is None:
                raise ValueError(
                    "discrete transfer function requires sample time"
                )
            if not math.isclose(
                envelope.experiment_proposal.sample_time_s,
                model.sample_time_s,
                rel_tol=0.0,
                abs_tol=1e-12,
            ):
                raise ValueError(
                    "discrete model and experiment sample times must match"
                )
            delay_steps = model.input_delay_s / model.sample_time_s
            if not math.isclose(
                delay_steps, round(delay_steps), rel_tol=0.0, abs_tol=1e-9
            ):
                raise ValueError(
                    "discrete transfer-function delay must be whole samples"
                )
    elif isinstance(model, StateSpaceModelSpec):
        state_count = len(model.state_names)
        input_count = len(model.input_signal_ids)
        output_count = len(model.output_signal_ids)
        if state_count > 32 or input_count > 8 or output_count > 8:
            raise ValueError("state-space dimensions exceed the safety limit")
        if len(set(model.state_names)) != state_count:
            raise ValueError("state names must be unique")
        if len(set(model.input_signal_ids)) != input_count:
            raise ValueError("input signal IDs must be unique")
        if len(set(model.output_signal_ids)) != output_count:
            raise ValueError("output signal IDs must be unique")
        if model.time_domain == "continuous" and model.sample_time_s is not None:
            raise ValueError("continuous state-space model cannot set sample time")
        if model.time_domain == "discrete":
            if model.sample_time_s is None:
                raise ValueError("discrete state-space model requires sample time")
            if not math.isclose(
                envelope.experiment_proposal.sample_time_s,
                model.sample_time_s,
                rel_tol=0.0,
                abs_tol=1e-12,
            ):
                raise ValueError(
                    "discrete model and experiment sample times must match"
                )
    else:
        if model.template_id not in context.allowed_registered_templates:
            raise ValueError("registered template is not allowlisted")
        if set(model.parameters) != _REGISTERED_PARAMETERS[model.template_id]:
            raise ValueError(
                "registered template parameters must use the exact set"
            )
        if envelope.model_role != "registered_nonlinear_model":
            raise ValueError(
                "registered runtime requires registered_nonlinear_model role"
            )


def _validate_signal_and_structure(
    envelope: GeneratedModelEnvelopeV1,
    context: ModelValidationContext,
) -> None:
    model = envelope.model
    inputs, outputs = _signals(model)
    if inputs != set(context.description.actuators):
        raise ValueError("model inputs conflict with declared actuators")
    if outputs != set(context.description.observed_outputs):
        raise ValueError("model outputs conflict with declared observed outputs")

    coupling = str(context.diagnosis.coupling_severity.assessment)
    input_count, output_count = len(inputs), len(outputs)
    if coupling == "siso" and (input_count != 1 or output_count != 1):
        raise ValueError("MIMO model conflicts with SISO diagnosis")
    if coupling in {"weak_mimo", "severe_mimo"} and (
        input_count < 2 or output_count < 2
    ):
        raise ValueError("SISO model conflicts with multivariable diagnosis")
    expected_template = {
        "underactuated": "underactuated_cartpole",
        "cascaded": "vtol_cascaded",
    }.get(coupling)
    if expected_template is not None and (
        not isinstance(model, RegisteredNonlinearModelSpec)
        or model.template_id != expected_template
    ):
        raise ValueError(
            "coupling diagnosis requires its exact registered template"
        )
    if isinstance(model, RegisteredNonlinearModelSpec):
        expected_coupling = (
            "underactuated"
            if model.template_id == "underactuated_cartpole"
            else "cascaded"
        )
        if coupling not in {expected_coupling, "unknown"}:
            raise ValueError(
                "registered model conflicts with coupling diagnosis"
            )

    if isinstance(model, RegisteredNonlinearModelSpec):
        poles = np.asarray([], dtype=complex)
        model_order = len(model.initial_state)
        model_stability = "unstable"
        relative_degree: int | None = None
        nonminimum_phase: bool | None = None
        oscillatory = False
        integrator = False
    elif isinstance(model, TransferFunctionModelSpec):
        poles = np.roots(np.asarray(model.denominator, dtype=float))
        zeros = (
            np.roots(np.asarray(model.numerator, dtype=float))
            if _effective_polynomial_length(model.numerator) > 1
            else np.asarray([], dtype=complex)
        )
        model_order = _effective_polynomial_length(model.denominator) - 1
        numerator_order = (
            _effective_polynomial_length(model.numerator) - 1
        )
        relative_degree = model_order - numerator_order
        model_stability = (
            "stable"
            if (
                all(root.real < -1e-6 for root in poles)
                if model.time_domain == "continuous"
                else all(abs(root) < 1.0 - 1e-6 for root in poles)
            )
            else "unstable"
        )
        nonminimum_phase = (
            any(zero.real >= -1e-8 for zero in zeros)
            if model.time_domain == "continuous"
            else any(abs(zero) >= 1.0 - 1e-8 for zero in zeros)
        )
        oscillatory = any(abs(pole.imag) > 1e-6 for pole in poles)
        integrator = (
            any(abs(pole) <= 1e-6 for pole in poles)
            if model.time_domain == "continuous"
            else any(abs(pole - 1.0) <= 1e-6 for pole in poles)
        )
    else:
        poles = np.linalg.eigvals(np.asarray(model.a, dtype=float))
        model_order = len(model.state_names)
        model_stability = (
            "stable"
            if (
                all(value.real < -1e-6 for value in poles)
                if model.time_domain == "continuous"
                else all(abs(value) < 1.0 - 1e-6 for value in poles)
            )
            else "unstable"
        )
        a = np.asarray(model.a, dtype=float)
        b = np.asarray(model.b, dtype=float)
        c = np.asarray(model.c, dtype=float)
        d = np.asarray(model.d, dtype=float)
        relative_degree = None
        if input_count == 1 and output_count == 1:
            if np.any(np.abs(d) > 1e-10):
                relative_degree = 0
            else:
                for degree in range(1, model_order + 1):
                    markov = c @ np.linalg.matrix_power(a, degree - 1) @ b
                    if np.any(np.abs(markov) > 1e-10):
                        relative_degree = degree
                        break
        nonminimum_phase = None
        if input_count == 1 and output_count == 1:
            from scipy.signal import ss2zpk

            zeros, _, _ = ss2zpk(a, b, c, d)
            nonminimum_phase = (
                any(zero.real >= -1e-8 for zero in zeros)
                if model.time_domain == "continuous"
                else any(abs(zero) >= 1.0 - 1e-8 for zero in zeros)
            )
        oscillatory = any(abs(pole.imag) > 1e-6 for pole in poles)
        integrator = (
            any(abs(pole) <= 1e-6 for pole in poles)
            if model.time_domain == "continuous"
            else any(abs(pole - 1.0) <= 1e-6 for pole in poles)
        )

    diagnosed_stability = str(
        context.diagnosis.open_loop_stability.assessment
    )
    if (
        diagnosed_stability in {"stable", "unstable"}
        and diagnosed_stability != model_stability
    ):
        raise ValueError(
            "generated model stability conflicts with the diagnosis"
        )

    primary_class = str(context.classification.primary_class)
    if primary_class == "class_i_first_order_lag":
        if (
            model_order != 1
            or model_stability != "stable"
            or nonminimum_phase is not False
            or input_count != 1
            or output_count != 1
        ):
            raise ValueError(
                "generated model conflicts with Class I first-order lag"
            )
    elif primary_class == "class_ii_second_order_oscillator":
        if model_order != 2 or not oscillatory:
            raise ValueError(
                "generated model lacks Class II second-order oscillatory poles"
            )
    elif primary_class == "class_iii_double_or_pure_integrator":
        if not integrator:
            raise ValueError(
                "generated model lacks a Class III integrator pole"
            )
    elif (
        primary_class
        == "class_iv_higher_order_unstable_nonlinear_or_nmp"
    ):
        local_nonlinear = (
            envelope.model_role == "local_linear_hypothesis"
            and envelope.validity_region is not None
            and str(
                context.diagnosis.nonlinearity_strength.assessment
            )
            == "strong_dynamic"
        )
        if not (
            model_order >= 3
            or model_stability == "unstable"
            or isinstance(model, RegisteredNonlinearModelSpec)
            or nonminimum_phase is True
            or local_nonlinear
        ):
            raise ValueError(
                "generated model lacks any inspectable Class IV property"
            )
    elif primary_class == "class_v_multivariable_significant_coupling":
        if input_count < 2 or output_count < 2:
            raise ValueError(
                "generated model conflicts with Class V multivariable structure"
            )

    delay = str(context.diagnosis.significant_delay.assessment)
    if isinstance(model, TransferFunctionModelSpec):
        has_delay = model.input_delay_s > 1e-12
        if delay == "significant" and not has_delay:
            raise ValueError(
                "zero-delay model conflicts with significant-delay diagnosis"
            )
        if delay == "not_significant" and has_delay:
            raise ValueError(
                "delayed model conflicts with no-significant-delay diagnosis"
            )
    elif delay == "significant":
        raise ValueError(
            "model schema has no explicit delay representation and "
            "cannot satisfy a significant-delay diagnosis"
        )

    phase = str(context.diagnosis.minimum_phase.assessment)
    if nonminimum_phase is not None:
        if phase == "minimum_phase" and nonminimum_phase:
            raise ValueError(
                "nonminimum-phase model conflicts with minimum-phase diagnosis"
            )
        if phase == "nonminimum_phase" and not nonminimum_phase:
            raise ValueError(
                "minimum-phase model conflicts with nonminimum-phase diagnosis"
            )

    degree_field = context.diagnosis.relative_degree
    degree_assessment = str(degree_field.assessment)
    if relative_degree is not None:
        if (
            degree_field.estimated_order is not None
            and relative_degree != degree_field.estimated_order
        ):
            raise ValueError(
                "model relative degree conflicts with diagnosed order"
            )
        if degree_assessment == "low" and relative_degree > 2:
            raise ValueError(
                "high relative-degree model conflicts with low diagnosis"
            )
        if degree_assessment == "high" and relative_degree <= 2:
            raise ValueError(
                "low relative-degree model conflicts with high diagnosis"
            )

    nonlinearity = str(
        context.diagnosis.nonlinearity_strength.assessment
    )
    if nonlinearity == "strong_dynamic" and not (
        isinstance(model, RegisteredNonlinearModelSpec)
        or (
            envelope.model_role == "local_linear_hypothesis"
            and envelope.operating_point is not None
            and envelope.validity_region is not None
        )
    ):
        raise ValueError(
            "strong nonlinearity requires a registered model or explicit "
            "local-linear validity boundary"
        )


def _validate_runtime_signals(envelope: GeneratedModelEnvelopeV1) -> None:
    model = envelope.model
    inputs, outputs = _signals(model)
    if isinstance(model, TransferFunctionModelSpec):
        states: set[str] = set()
        model_units = {
            model.input_signal_id: model.input_units,
            model.output_signal_id: model.output_units,
        }
    else:
        states = (
            set(model.state_names)
            if isinstance(model, StateSpaceModelSpec)
            else set(model.initial_state)
        )
        model_units = dict(model.signal_units)

    experiment = envelope.experiment_proposal
    exact_groups = (
        ("initial_state", set(experiment.initial_state), states),
        ("actuator_bounds", set(experiment.actuator_bounds), inputs),
        ("state_bounds", set(experiment.state_bounds), states),
        ("output_bounds", set(experiment.output_bounds), outputs),
    )
    for field_name, proposed, expected in exact_groups:
        if proposed != expected:
            raise ValueError(
                f"experiment {field_name} must exactly cover model signals"
            )
    if not set(experiment.reference) <= outputs:
        raise ValueError(
            "experiment reference must use only generated-model outputs"
        )
    if experiment.signal_units != model_units:
        raise ValueError(
            "experiment units must exactly match the generated model units"
        )

    if envelope.operating_point is not None:
        operating_point = envelope.operating_point
        for field_name, proposed, expected in (
            ("states", set(operating_point.states), states),
            ("inputs", set(operating_point.inputs), inputs),
            ("outputs", set(operating_point.outputs), outputs),
        ):
            if proposed != expected:
                raise ValueError(
                    f"operating point {field_name} must exactly cover model signals"
                )
        if operating_point.signal_units != model_units:
            raise ValueError(
                "operating-point units must exactly match model units"
            )

    if envelope.validity_region is not None:
        region = envelope.validity_region
        for field_name, proposed, expected in (
            ("state_ranges", set(region.state_ranges), states),
            ("input_ranges", set(region.input_ranges), inputs),
            ("output_ranges", set(region.output_ranges), outputs),
        ):
            if proposed != expected:
                raise ValueError(
                    f"validity region {field_name} must exactly cover model signals"
                )
        if region.signal_units != model_units:
            raise ValueError(
                "validity-region units must exactly match model units"
            )


def _add_matrix_paths(
    result: dict[str, float], name: str, matrix: Sequence[Sequence[float]]
) -> None:
    for row_index, row in enumerate(matrix):
        for column_index, value in enumerate(row):
            result[f"model.{name}[{row_index}][{column_index}]"] = float(value)


def _numeric_paths(envelope: GeneratedModelEnvelopeV1) -> dict[str, float]:
    model = envelope.model
    result: dict[str, float] = {}
    if isinstance(model, TransferFunctionModelSpec):
        for index, value in enumerate(model.numerator):
            result[f"model.numerator[{index}]"] = float(value)
        for index, value in enumerate(model.denominator):
            result[f"model.denominator[{index}]"] = float(value)
        result["model.input_delay_s"] = float(model.input_delay_s)
        if model.sample_time_s is not None:
            result["model.sample_time_s"] = float(model.sample_time_s)
    elif isinstance(model, StateSpaceModelSpec):
        for name in ("a", "b", "c", "d"):
            _add_matrix_paths(result, name, getattr(model, name))
        for index, value in enumerate(model.initial_state):
            result[f"model.initial_state[{index}]"] = float(value)
        if model.sample_time_s is not None:
            result["model.sample_time_s"] = float(model.sample_time_s)
    else:
        for name, value in model.parameters.items():
            result[f"model.parameters.{name}"] = float(value)
        for name, value in model.initial_state.items():
            result[f"model.initial_state.{name}"] = float(value)
    for name, value in model.parameter_uncertainty.items():
        result[f"model.parameter_uncertainty.{name}"] = float(value)

    experiment = envelope.experiment_proposal
    for name, value in experiment.initial_state.items():
        result[f"experiment_proposal.initial_state.{name}"] = float(value)
    for name, value in experiment.reference.items():
        result[f"experiment_proposal.reference.{name}"] = float(value)
    result["experiment_proposal.horizon_s"] = float(experiment.horizon_s)
    result["experiment_proposal.sample_time_s"] = float(
        experiment.sample_time_s
    )
    for group_name in ("actuator_bounds", "state_bounds", "output_bounds"):
        for name, bounds in getattr(experiment, group_name).items():
            result[f"experiment_proposal.{group_name}.{name}[0]"] = float(
                bounds[0]
            )
            result[f"experiment_proposal.{group_name}.{name}[1]"] = float(
                bounds[1]
            )
    if envelope.operating_point is not None:
        for group_name in ("states", "inputs", "outputs"):
            for name, value in getattr(
                envelope.operating_point, group_name
            ).items():
                result[f"operating_point.{group_name}.{name}"] = float(value)
    if envelope.validity_region is not None:
        for group_name in (
            "input_ranges",
            "output_ranges",
            "state_ranges",
        ):
            for name, bounds in getattr(
                envelope.validity_region, group_name
            ).items():
                result[f"validity_region.{group_name}.{name}[0]"] = float(
                    bounds[0]
                )
                result[f"validity_region.{group_name}.{name}[1]"] = float(
                    bounds[1]
                )
    return result


def _single_fact_scalar(
    facts: Sequence[ModelFactAnswer], fact_type: str
) -> tuple[float, str]:
    matches = [fact for fact in facts if fact.fact_type == fact_type]
    if len(matches) != 1:
        raise ValueError(
            f"derivation requires exactly one {fact_type} fact"
        )
    return (
        float(matches[0].value_payload["value"]),
        str(matches[0].value_payload["unit"]),
    )


def _single_seconds_fact(
    facts: Sequence[ModelFactAnswer], fact_type: str
) -> tuple[float, str]:
    value, unit = _single_fact_scalar(facts, fact_type)
    if unit != "s":
        raise ValueError(
            f"{fact_type} derivation requires target unit s"
        )
    return value, unit


def _continuous_first_order_step_form(
    model: Any,
) -> bool:
    return bool(
        isinstance(model, TransferFunctionModelSpec)
        and model.time_domain == "continuous"
        and model.sample_time_s is None
        and len(model.numerator) == 1
        and len(model.denominator) == 2
        and math.isclose(
            model.denominator[1], 1.0, rel_tol=0.0, abs_tol=1e-12
        )
    )


def _derive_value(
    rule_id: str,
    facts: Sequence[ModelFactAnswer],
    parameter_path: str,
    envelope: GeneratedModelEnvelopeV1,
) -> tuple[float, str]:
    model = envelope.model
    if rule_id in {
        "first_order_step_gain/v1",
        "step_response_gain/v1",
        "step_ratio_gain/v1",
    }:
        if not (
            _continuous_first_order_step_form(model)
            and parameter_path == "model.numerator[0]"
        ):
            raise ValueError(
                "step-gain derivation is valid only for the scalar transfer-"
                "function numerator gain path"
            )
        input_facts = [fact for fact in facts if fact.fact_type == "input_step"]
        output_facts = [
            fact for fact in facts if fact.fact_type == "output_step"
        ]
        if len(input_facts) != 1 or len(output_facts) != 1:
            raise ValueError(
                "step-gain derivation requires one input and one output step"
            )
        input_delta = (
            float(input_facts[0].value_payload["after"])
            - float(input_facts[0].value_payload["before"])
        )
        output_delta = (
            float(output_facts[0].value_payload["after"])
            - float(output_facts[0].value_payload["before"])
        )
        if abs(input_delta) <= 1e-15:
            raise ValueError("step-gain derivation has zero input change")
        derived_unit = (
            f"{output_facts[0].value_payload['unit']}/"
            f"{input_facts[0].value_payload['unit']}"
        )
        expected_unit = f"{model.output_units}/{model.input_units}"
        if derived_unit != expected_unit:
            raise ValueError(
                "step-gain derivation units conflict with model signal units"
            )
        return (
            output_delta / input_delta,
            derived_unit,
        )
    if rule_id in {
        "first_order_time_constant/v1",
        "response_time_63/v1",
    }:
        if not (
            _continuous_first_order_step_form(model)
            and parameter_path == "model.denominator[0]"
        ):
            raise ValueError(
                "response-time derivation is valid only for the leading "
                "transfer-function response-time coefficient path"
            )
        return _single_seconds_fact(facts, "response_time_63")
    if rule_id == "response_delay/v1":
        if not (
            _continuous_first_order_step_form(model)
            and parameter_path == "model.input_delay_s"
        ):
            raise ValueError(
                "response-delay derivation is valid only for the transfer-"
                "function input-delay path"
            )
        return _single_seconds_fact(facts, "response_delay")
    if rule_id == "sample_time/v1":
        allowed_paths = {"experiment_proposal.sample_time_s"}
        if (
            isinstance(model, (TransferFunctionModelSpec, StateSpaceModelSpec))
            and model.time_domain == "discrete"
        ):
            allowed_paths.add("model.sample_time_s")
        if parameter_path not in allowed_paths:
            raise ValueError(
                "sample-time derivation is not valid for this path"
            )
        return _single_seconds_fact(facts, "sample_time")
    if rule_id in {"normalized_one/v1", "constant_one/v1"}:
        if not (
            _continuous_first_order_step_form(model)
            and parameter_path == "model.denominator[1]"
        ):
            raise ValueError(
                "normalized-one derivation is valid only for the unique "
                "monic coefficient of the registered canonical form"
            )
        return 1.0, "1"
    if rule_id in {"normalized_zero/v1", "constant_zero/v1"}:
        if not (
            _continuous_first_order_step_form(model)
            and parameter_path == "model.input_delay_s"
        ):
            raise ValueError(
                "normalized-zero derivation is not valid for this path"
            )
        return 0.0, "s"
    if rule_id == "six_time_constants_horizon/v1":
        if parameter_path != "experiment_proposal.horizon_s":
            raise ValueError("horizon derivation is not valid for this path")
        value, unit = _single_seconds_fact(facts, "response_time_63")
        return 6.0 * value, unit
    if rule_id == "time_constant_div_50_sample/v1":
        if parameter_path != "experiment_proposal.sample_time_s":
            raise ValueError(
                "sample-interval derivation is not valid for this path"
            )
        value, unit = _single_seconds_fact(facts, "response_time_63")
        return value / 50.0, unit
    if rule_id == "output_step_delta_reference/v1":
        if not isinstance(model, TransferFunctionModelSpec):
            raise ValueError(
                "output-step reference derivation requires a transfer function"
            )
        expected_path = (
            "experiment_proposal.reference."
            f"{model.output_signal_id}"
        )
        if parameter_path != expected_path:
            raise ValueError(
                "output-step reference derivation targets only the model output"
            )
        output_facts = [
            fact for fact in facts if fact.fact_type == "output_step"
        ]
        if len(output_facts) != 1:
            raise ValueError(
                "output-step reference derivation requires one output step"
            )
        payload = output_facts[0].value_payload
        return (
            float(payload["after"]) - float(payload["before"]),
            str(payload["unit"]),
        )
    if rule_id == "center_actuator_bounds_at_input_before/v1":
        if not isinstance(model, TransferFunctionModelSpec):
            raise ValueError(
                "centered actuator bounds require a transfer function"
            )
        match = re.fullmatch(
            r"experiment_proposal\.actuator_bounds\."
            r"([A-Za-z0-9_]+)\[([01])\]",
            parameter_path,
        )
        if match is None or match.group(1) != model.input_signal_id:
            raise ValueError(
                "centered actuator bounds target only the model input"
            )
        input_facts = [
            fact for fact in facts if fact.fact_type == "input_step"
        ]
        bound_facts = [
            fact for fact in facts if fact.fact_type == "actuator_bounds"
        ]
        if len(input_facts) != 1 or len(bound_facts) != 1:
            raise ValueError(
                "centered actuator bounds require one input step and one "
                "actuator-bounds fact"
            )
        step = input_facts[0].value_payload
        bounds = bound_facts[0].value_payload
        signal = model.input_signal_id
        if (
            step["unit"] != model.input_units
            or bounds["signal_units"].get(signal) != model.input_units
            or signal not in bounds["ranges"]
        ):
            raise ValueError(
                "centered actuator bounds conflict with input units or signal"
            )
        index = int(match.group(2))
        return (
            float(bounds["ranges"][signal][index])
            - float(step["before"]),
            model.input_units,
        )
    if rule_id == "center_output_bounds_at_output_before/v1":
        if not isinstance(model, TransferFunctionModelSpec):
            raise ValueError(
                "centered output bounds require a transfer function"
            )
        match = re.fullmatch(
            r"experiment_proposal\.output_bounds\."
            r"([A-Za-z0-9_]+)\[([01])\]",
            parameter_path,
        )
        if match is None or match.group(1) != model.output_signal_id:
            raise ValueError(
                "centered output bounds target only the model output"
            )
        output_facts = [
            fact for fact in facts if fact.fact_type == "output_step"
        ]
        bound_facts = [
            fact for fact in facts if fact.fact_type == "output_bounds"
        ]
        if len(output_facts) != 1 or len(bound_facts) != 1:
            raise ValueError(
                "centered output bounds require one output step and one "
                "output-bounds fact"
            )
        step = output_facts[0].value_payload
        bounds = bound_facts[0].value_payload
        signal = model.output_signal_id
        if (
            step["unit"] != model.output_units
            or bounds["signal_units"].get(signal) != model.output_units
            or signal not in bounds["ranges"]
        ):
            raise ValueError(
                "centered output bounds conflict with output units or signal"
            )
        index = int(match.group(2))
        return (
            float(bounds["ranges"][signal][index])
            - float(step["before"]),
            model.output_units,
        )
    raise ValueError("unregistered deterministic derivation rule")


def _matrix_fact_leaves(
    fact_type: str,
    matrix_name: str,
    values: Any,
    units: Any,
) -> list[_NumericFactLeaf]:
    if not isinstance(values, list) or not isinstance(units, list):
        return []
    leaves: list[_NumericFactLeaf] = []
    for row_index, (value_row, unit_row) in enumerate(zip(values, units)):
        if not isinstance(value_row, list) or not isinstance(unit_row, list):
            return []
        for column_index, (value, unit) in enumerate(
            zip(value_row, unit_row)
        ):
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                leaves.append(
                    _NumericFactLeaf(
                        fact_type,
                        f"{matrix_name}[{row_index}][{column_index}]",
                        float(value),
                        str(unit),
                    )
                )
    return leaves


def _fact_numeric_leaves(fact: ModelFactAnswer) -> list[_NumericFactLeaf]:
    payload = fact.value_payload
    if fact.fact_type in {"input_step", "output_step"}:
        unit = str(payload["unit"])
        return [
            _NumericFactLeaf(
                fact.fact_type, "before", float(payload["before"]), unit
            ),
            _NumericFactLeaf(
                fact.fact_type, "after", float(payload["after"]), unit
            ),
        ]
    if fact.fact_type in {
        "response_delay",
        "response_time_63",
        "oscillation_period",
        "peak_ratio",
        "sample_time",
    }:
        return [
            _NumericFactLeaf(
                fact.fact_type,
                "value",
                float(payload["value"]),
                str(payload["unit"]),
            )
        ]
    if fact.fact_type == "operating_point":
        units = payload["signal_units"]
        leaves: list[_NumericFactLeaf] = []
        for group_name in ("states", "inputs", "outputs"):
            for name, value in payload.get(group_name, {}).items():
                leaves.append(
                    _NumericFactLeaf(
                        fact.fact_type,
                        f"{group_name}.{name}",
                        float(value),
                        str(units[name]),
                    )
                )
        return leaves
    if fact.fact_type == "validity_region":
        units = payload["signal_units"]
        leaves = []
        for group_name in (
            "state_ranges",
            "input_ranges",
            "output_ranges",
        ):
            for name, bounds in payload.get(group_name, {}).items():
                leaves.extend(
                    [
                        _NumericFactLeaf(
                            fact.fact_type,
                            f"{group_name}.{name}[0]",
                            float(bounds[0]),
                            str(units[name]),
                        ),
                        _NumericFactLeaf(
                            fact.fact_type,
                            f"{group_name}.{name}[1]",
                            float(bounds[1]),
                            str(units[name]),
                        ),
                    ]
                )
        return leaves
    if fact.fact_type == "state_space_data":
        matrix_units = payload.get("matrix_units", {})
        leaves = []
        for name in ("a", "b", "c", "d"):
            leaves.extend(
                _matrix_fact_leaves(
                    fact.fact_type,
                    name,
                    payload.get(name),
                    matrix_units.get(name),
                )
            )
        return leaves
    if fact.fact_type in {"cartpole_parameters", "vtol_parameters"}:
        return [
            _NumericFactLeaf(
                fact.fact_type,
                name,
                float(value),
                _REGISTERED_PARAMETER_UNITS[name],
            )
            for name, value in payload.items()
        ]
    if fact.fact_type == "reference_target":
        units = payload["signal_units"]
        return [
            _NumericFactLeaf(
                fact.fact_type,
                f"values.{name}",
                float(value),
                str(units[name]),
            )
            for name, value in payload["values"].items()
        ]
    if fact.fact_type in {"actuator_bounds", "output_bounds"}:
        units = payload["signal_units"]
        return [
            _NumericFactLeaf(
                fact.fact_type,
                f"ranges.{name}[{index}]",
                float(value),
                str(units[name]),
            )
            for name, bounds in payload["ranges"].items()
            for index, value in enumerate(bounds)
        ]
    if fact.fact_type == "parameter_uncertainty":
        units = payload["parameter_units"]
        return [
            _NumericFactLeaf(
                fact.fact_type,
                f"values.{name}",
                float(value),
                str(units[name]),
            )
            for name, value in payload["values"].items()
        ]
    return []


def _unit_dimensions(unit: str) -> dict[str, int]:
    token_pattern = re.compile(
        r"\s*([A-Za-z%][A-Za-z0-9_%]*|1|-?\d+|[*/^()])"
    )
    tokens: list[str] = []
    position = 0
    while position < len(unit):
        match = token_pattern.match(unit, position)
        if match is None:
            raise ValueError("unsupported unit syntax")
        tokens.append(match.group(1))
        position = match.end()
    if not tokens:
        raise ValueError("empty unit expression")
    cursor = 0

    def combine(
        left: dict[str, int],
        right: dict[str, int],
        sign: int,
    ) -> dict[str, int]:
        result = dict(left)
        for symbol, exponent in right.items():
            result[symbol] = result.get(symbol, 0) + sign * exponent
            if result[symbol] == 0:
                del result[symbol]
        return result

    def factor() -> dict[str, int]:
        nonlocal cursor
        if cursor >= len(tokens):
            raise ValueError("incomplete unit expression")
        token = tokens[cursor]
        cursor += 1
        if token == "(":
            value = expression()
            if cursor >= len(tokens) or tokens[cursor] != ")":
                raise ValueError("unclosed unit parenthesis")
            cursor += 1
        elif token == "1":
            value = {}
        elif re.fullmatch(r"[A-Za-z%][A-Za-z0-9_%]*", token):
            value = {token: 1}
        else:
            raise ValueError("invalid unit factor")
        if cursor < len(tokens) and tokens[cursor] == "^":
            cursor += 1
            if (
                cursor >= len(tokens)
                or re.fullmatch(r"-?\d+", tokens[cursor]) is None
            ):
                raise ValueError("unit exponent must be an integer")
            exponent = int(tokens[cursor])
            cursor += 1
            value = {
                symbol: power * exponent
                for symbol, power in value.items()
                if power * exponent
            }
        return value

    def expression() -> dict[str, int]:
        nonlocal cursor
        value = factor()
        while cursor < len(tokens) and tokens[cursor] in {"*", "/"}:
            operator = tokens[cursor]
            cursor += 1
            value = combine(value, factor(), 1 if operator == "*" else -1)
        return value

    dimensions = expression()
    if cursor != len(tokens):
        raise ValueError("unsupported unit expression")
    return dimensions


def _units_equivalent(left: str, right: str) -> bool:
    return _unit_dimensions(left) == _unit_dimensions(right)


def _matrix_expected_dimensions(
    envelope: GeneratedModelEnvelopeV1,
    parameter_path: str,
) -> dict[str, int] | None:
    model = envelope.model
    if not isinstance(model, StateSpaceModelSpec):
        return None
    match = re.fullmatch(
        r"model\.(a|b|c|d)\[(\d+)\]\[(\d+)\]",
        parameter_path,
    )
    if match is None:
        return None
    matrix, row_text, column_text = match.groups()
    row = int(row_text)
    column = int(column_text)

    def dimensions(name: str) -> dict[str, int]:
        return _unit_dimensions(model.signal_units[name])

    def ratio(
        numerator: dict[str, int], denominator: dict[str, int]
    ) -> dict[str, int]:
        result = dict(numerator)
        for symbol, exponent in denominator.items():
            result[symbol] = result.get(symbol, 0) - exponent
            if result[symbol] == 0:
                del result[symbol]
        return result

    if matrix == "a":
        result = ratio(
            dimensions(model.state_names[row]),
            dimensions(model.state_names[column]),
        )
    elif matrix == "b":
        result = ratio(
            dimensions(model.state_names[row]),
            dimensions(model.input_signal_ids[column]),
        )
    elif matrix == "c":
        result = ratio(
            dimensions(model.output_signal_ids[row]),
            dimensions(model.state_names[column]),
        )
    else:
        result = ratio(
            dimensions(model.output_signal_ids[row]),
            dimensions(model.input_signal_ids[column]),
        )
    if model.time_domain == "continuous" and matrix in {"a", "b"}:
        result["s"] = result.get("s", 0) - 1
        if result["s"] == 0:
            del result["s"]
    return result


def _direct_evidence_matches(
    evidence: Any,
    facts: Sequence[ModelFactAnswer],
    envelope: GeneratedModelEnvelopeV1,
) -> bool:
    allowed = _allowed_fact_leaf_keys(
        evidence.parameter_path, envelope
    )
    leaves = [
        leaf
        for fact in facts
        for leaf in _fact_numeric_leaves(fact)
        if (leaf.fact_type, leaf.payload_path) in allowed
    ]
    if evidence.unit_conversion is None:
        return any(
            _units_equivalent(leaf.unit, evidence.unit)
            and math.isclose(
                leaf.value,
                evidence.value,
                rel_tol=1e-9,
                abs_tol=1e-12,
            )
            for leaf in leaves
        )
    conversion = _REGISTERED_UNIT_CONVERSIONS.get(
        evidence.unit_conversion
    )
    if conversion is None:
        raise ValueError("unregistered unit conversion")
    source_unit, target_unit, scale, offset = conversion
    if evidence.unit != target_unit:
        raise ValueError("unit conversion target unit mismatch")
    return any(
        leaf.unit == source_unit
        and math.isclose(
            leaf.value * scale + offset,
            evidence.value,
            rel_tol=1e-9,
            abs_tol=1e-12,
        )
        for leaf in leaves
    )


def _allowed_fact_leaf_keys(
    parameter_path: str,
    envelope: GeneratedModelEnvelopeV1,
) -> set[tuple[str, str]]:
    keys: set[tuple[str, str]] = set()
    match = re.fullmatch(
        r"model\.parameter_uncertainty\.([A-Za-z0-9_]+)",
        parameter_path,
    )
    if match:
        keys.add(("parameter_uncertainty", f"values.{match.group(1)}"))
        return keys
    match = re.fullmatch(r"model\.(a|b|c|d)(\[\d+\]\[\d+\])", parameter_path)
    if match:
        keys.add(("state_space_data", f"{match.group(1)}{match.group(2)}"))
        return keys
    match = re.fullmatch(r"model\.parameters\.([A-Za-z0-9_]+)", parameter_path)
    if match and isinstance(envelope.model, RegisteredNonlinearModelSpec):
        fact_type = (
            "cartpole_parameters"
            if envelope.model.template_id == "underactuated_cartpole"
            else "vtol_parameters"
        )
        keys.add((fact_type, match.group(1)))
        return keys
    match = re.fullmatch(r"model\.initial_state\[(\d+)\]", parameter_path)
    if match and isinstance(envelope.model, StateSpaceModelSpec):
        index = int(match.group(1))
        if index < len(envelope.model.state_names):
            keys.add(
                ("operating_point", f"states.{envelope.model.state_names[index]}")
            )
        return keys
    match = re.fullmatch(
        r"model\.initial_state\.([A-Za-z0-9_]+)", parameter_path
    )
    if match:
        keys.add(("operating_point", f"states.{match.group(1)}"))
        return keys
    match = re.fullmatch(
        r"experiment_proposal\.initial_state\.([A-Za-z0-9_]+)",
        parameter_path,
    )
    if match:
        keys.add(("operating_point", f"states.{match.group(1)}"))
        return keys
    match = re.fullmatch(
        r"experiment_proposal\.reference\.([A-Za-z0-9_]+)",
        parameter_path,
    )
    if match:
        signal = match.group(1)
        keys.update(
            {
                ("reference_target", f"values.{signal}"),
                ("operating_point", f"outputs.{signal}"),
            }
        )
        return keys
    for experiment_group, fact_type, fact_group in (
        ("actuator_bounds", "actuator_bounds", "ranges"),
        ("actuator_bounds", "validity_region", "input_ranges"),
        ("state_bounds", "validity_region", "state_ranges"),
        ("output_bounds", "output_bounds", "ranges"),
        ("output_bounds", "validity_region", "output_ranges"),
    ):
        match = re.fullmatch(
            rf"experiment_proposal\.{experiment_group}\."
            r"([A-Za-z0-9_]+)(\[[01]\])",
            parameter_path,
        )
        if match:
            keys.add(
                (
                    fact_type,
                    f"{fact_group}.{match.group(1)}{match.group(2)}",
                )
            )
    match = re.fullmatch(
        r"operating_point\.(states|inputs|outputs)\.([A-Za-z0-9_]+)",
        parameter_path,
    )
    if match:
        keys.add(
            ("operating_point", f"{match.group(1)}.{match.group(2)}")
        )
        return keys
    match = re.fullmatch(
        r"validity_region\."
        r"(input_ranges|output_ranges|state_ranges)\."
        r"([A-Za-z0-9_]+)(\[[01]\])",
        parameter_path,
    )
    if match:
        keys.add(
            (
                "validity_region",
                f"{match.group(1)}.{match.group(2)}{match.group(3)}",
            )
        )
    return keys


def _requires_derivation(parameter_path: str) -> bool:
    return bool(
        re.fullmatch(
            r"model\.(?:numerator|denominator)\[\d+\]",
            parameter_path,
        )
        or parameter_path
        in {
            "model.input_delay_s",
            "model.sample_time_s",
            "experiment_proposal.horizon_s",
            "experiment_proposal.sample_time_s",
        }
    )


def _registry_policy_paths(
    envelope: GeneratedModelEnvelopeV1,
) -> dict[str, _NumericFactLeaf]:
    if not isinstance(envelope.model, RegisteredNonlinearModelSpec):
        return {}
    from cfdc.sim.registered_runtime import registered_run_envelope

    registered = registered_run_envelope(envelope.model)
    result: dict[str, _NumericFactLeaf] = {
        "experiment_proposal.horizon_s": _NumericFactLeaf(
            "registry_policy",
            "horizon_s",
            float(registered["horizon_s"]),
            "s",
        ),
        "experiment_proposal.sample_time_s": _NumericFactLeaf(
            "registry_policy",
            "sample_time_s",
            float(registered["sample_time_s"]),
            "s",
        ),
    }
    for name, value in registered["reference"].items():
        result[f"experiment_proposal.reference.{name}"] = _NumericFactLeaf(
            "registry_policy",
            f"reference.{name}",
            float(value),
            envelope.model.signal_units[name],
        )
    for group_name in ("actuator_bounds", "state_bounds", "output_bounds"):
        for name, bounds in registered[group_name].items():
            unit = envelope.model.signal_units[name]
            result[
                f"experiment_proposal.{group_name}.{name}[0]"
            ] = _NumericFactLeaf(
                "registry_policy",
                f"{group_name}.{name}[0]",
                float(bounds[0]),
                unit,
            )
            result[
                f"experiment_proposal.{group_name}.{name}[1]"
            ] = _NumericFactLeaf(
                "registry_policy",
                f"{group_name}.{name}[1]",
                float(bounds[1]),
                unit,
            )
    return result


def _validate_evidence(
    envelope: GeneratedModelEnvelopeV1,
    context: ModelValidationContext,
) -> None:
    facts_by_id = {fact.fact_id: fact for fact in context.facts}
    expected = _numeric_paths(envelope)
    registry_policy_paths = _registry_policy_paths(envelope)
    evidence_by_path: dict[str, Any] = {}
    referenced_fact_ids: set[str] = set()
    for evidence in envelope.parameter_evidence:
        if evidence.parameter_path in evidence_by_path:
            raise ValueError("parameter evidence paths must be unique")
        evidence_by_path[evidence.parameter_path] = evidence
        if evidence.parameter_path not in expected:
            raise ValueError("parameter evidence contains an unknown path")
        missing_fact_ids = set(evidence.source_fact_ids) - set(facts_by_id)
        if missing_fact_ids:
            raise ValueError("parameter evidence references unknown facts")
        source_facts = [
            facts_by_id[fact_id] for fact_id in evidence.source_fact_ids
        ]
        referenced_fact_ids.update(evidence.source_fact_ids)
        matrix_dimensions = _matrix_expected_dimensions(
            envelope, evidence.parameter_path
        )
        if (
            matrix_dimensions is not None
            and _unit_dimensions(evidence.unit) != matrix_dimensions
        ):
            raise ValueError(
                "state-space matrix evidence unit conflicts with derived "
                "signal dimensions"
            )
        if evidence.source == "user_adopted_example":
            if any(
                fact.source != "user_adopted_example" for fact in source_facts
            ):
                raise ValueError(
                    "adopted-example evidence requires explicit adopted facts"
                )
        elif evidence.source not in {
            "deterministic_derivation",
            "registry_policy",
        } and any(
            fact.source != evidence.source for fact in source_facts
        ):
            raise ValueError(
                "parameter evidence source conflicts with referenced facts"
            )
        if evidence.source == "registry_policy":
            registered = registry_policy_paths.get(evidence.parameter_path)
            if (
                registered is None
                or evidence.unit_conversion is not None
                or evidence.unit != registered.unit
                or not math.isclose(
                    evidence.value,
                    registered.value,
                    rel_tol=1e-9,
                    abs_tol=1e-12,
                )
            ):
                raise ValueError(
                    "registry policy may attest only exact registered "
                    "experiment paths, values, and units"
                )
        elif evidence.source == "deterministic_derivation":
            if evidence.unit_conversion is not None:
                raise ValueError(
                    "derived evidence cannot claim a separate unit conversion"
                )
            assert evidence.derivation_rule_id is not None
            derived, derived_unit = _derive_value(
                evidence.derivation_rule_id,
                source_facts,
                evidence.parameter_path,
                envelope,
            )
            if not math.isclose(
                evidence.value, derived, rel_tol=1e-9, abs_tol=1e-12
            ):
                raise ValueError(
                    "deterministic derivation value does not recompute"
                )
            if evidence.unit != derived_unit:
                raise ValueError(
                    "deterministic derivation unit does not recompute"
                )
        else:
            if _requires_derivation(evidence.parameter_path):
                raise ValueError(
                    "computed model and timing fields require a registered "
                    "deterministic derivation"
                )
            if not _direct_evidence_matches(
                evidence, source_facts, envelope
            ):
                raise ValueError(
                    "direct evidence value/unit is not a referenced fact leaf"
                )
        if not math.isclose(
            evidence.value,
            expected[evidence.parameter_path],
            rel_tol=1e-9,
            abs_tol=1e-12,
        ):
            raise ValueError(
                "parameter evidence value differs from the generated envelope"
            )
    missing_paths = set(expected) - set(evidence_by_path)
    if missing_paths:
        raise ValueError(
            "generated envelope lacks evidence for every numeric path"
        )
    if set(envelope.experiment_proposal.evidence_fact_ids) - set(facts_by_id):
        raise ValueError("experiment references unknown evidence facts")
    referenced_fact_ids.update(
        envelope.experiment_proposal.evidence_fact_ids
    )
    uses_adopted_example = any(
        facts_by_id[fact_id].source == "user_adopted_example"
        for fact_id in referenced_fact_ids
    )
    if uses_adopted_example and envelope.model_role != "example_hypothesis":
        raise ValueError(
            "a model derived from adopted example facts must use "
            "model_role=example_hypothesis"
        )
    if (
        envelope.model_role == "example_hypothesis"
        and not uses_adopted_example
    ):
        raise ValueError(
            "example_hypothesis requires a referenced explicitly adopted "
            "example fact"
        )


def validate_generated_model_envelope(
    envelope: GeneratedModelEnvelopeV1 | Mapping[str, Any],
    context: ModelValidationContext,
) -> GeneratedModelEnvelopeV1:
    """Validate a typed envelope without executing any supplied text."""

    typed_context = (
        context
        if isinstance(context, ModelValidationContext)
        else ModelValidationContext.model_validate(context)
    )
    typed = (
        envelope
        if isinstance(envelope, GeneratedModelEnvelopeV1)
        else GeneratedModelEnvelopeV1.model_validate(envelope)
    )
    validate_non_executable_content(typed.model_dump(mode="json"))
    _validate_model_shape(typed, typed_context)
    _validate_signal_and_structure(typed, typed_context)
    _validate_runtime_signals(typed)
    _validate_evidence(typed, typed_context)
    return typed


def _validate_adopted_facts(
    context: ModelValidationContext,
    catalog: ModelQuestionExampleCatalog,
) -> None:
    examples = {example.example_id: example for example in catalog.examples}
    for fact in context.facts:
        if fact.source != "user_adopted_example":
            continue
        example = examples.get(fact.example_id or "")
        if example is None:
            raise ValueError("adopted model fact references an unknown example")
        if fact.example_catalog_version != catalog.catalog_version:
            raise ValueError("adopted model fact catalog version mismatch")
        if (
            fact.fact_type != example.fact_type
            or fact.unit_family != example.unit_family
        ):
            raise ValueError("adopted model fact does not match its example")
        expected_hash = _canonical_sha256(example.model_dump(mode="json"))
        if fact.example_content_sha256 != expected_hash:
            raise ValueError("adopted model fact content hash mismatch")


def _validate_questions(
    result: Any, catalog: ModelQuestionExampleCatalog
) -> None:
    examples = {example.example_id: example for example in catalog.examples}
    if len(result.missing_fact_ids) != len(set(result.missing_fact_ids)):
        raise ValueError("missing fact IDs must be unique")
    for question in result.questions:
        example = examples.get(question.example_id)
        if example is None:
            raise ValueError("discovery question references an unknown example")
        if (
            example.fact_type != question.fact_type
            or example.unit_family != question.unit_family
        ):
            raise ValueError(
                "discovery question and fixed example metadata do not match"
            )
        if question.fact_id not in result.missing_fact_ids:
            raise ValueError(
                "every discovery question must reference a missing fact"
            )


def _numeric_values(value: Any) -> list[float]:
    if isinstance(value, bool):
        return []
    if isinstance(value, (int, float)):
        return [float(value)]
    if isinstance(value, Mapping):
        result: list[float] = []
        for item in value.values():
            result.extend(_numeric_values(item))
        return result
    if isinstance(value, Sequence) and not isinstance(
        value, (str, bytes, bytearray)
    ):
        result = []
        for item in value:
            result.extend(_numeric_values(item))
        return result
    return []


def _unit_values(
    value: Any,
    *,
    in_unit_field: bool = False,
) -> list[str]:
    if isinstance(value, Mapping):
        result: list[str] = []
        for key, item in value.items():
            normalized = _normalized_key(key)
            result.extend(
                _unit_values(
                    item,
                    in_unit_field=(
                        in_unit_field
                        or normalized
                        in {
                            "unit",
                            "signalunits",
                            "parameterunits",
                            "matrixunits",
                        }
                    ),
                )
            )
        return result
    if isinstance(value, Sequence) and not isinstance(
        value, (str, bytes, bytearray)
    ):
        result = []
        for item in value:
            result.extend(
                _unit_values(item, in_unit_field=in_unit_field)
            )
        return result
    if in_unit_field and isinstance(value, str):
        return [value]
    return []


def _validate_recognized_facts(
    result: Any,
    context: ModelValidationContext,
) -> list[ModelFactAnswer]:
    recognized = list(getattr(result, "recognized_facts", []))
    if not recognized:
        return []
    answer_by_fact_id = {
        answer.fact_id: answer
        for answer in context.natural_language_answers
    }
    known_ids = {fact.fact_id for fact in context.facts}
    seen: set[str] = set()
    for fact in recognized:
        if fact.fact_id in known_ids or fact.fact_id in seen:
            raise ValueError(
                "recognized model facts must be new and uniquely identified"
            )
        seen.add(fact.fact_id)
        answer = answer_by_fact_id.get(fact.fact_id)
        if answer is None:
            raise ValueError(
                "recognized model fact has no matching verbatim answer"
            )
        if (
            fact.source != "user_supplied"
            or fact.fact_type != answer.fact_type
            or fact.unit_family != answer.unit_family
            or fact.answer_text != answer.answer_text
        ):
            raise ValueError(
                "recognized model fact metadata must match the verbatim answer"
            )
        written_numbers = [
            float(match.group(0))
            for match in _NUMBER_LITERAL.finditer(answer.answer_text)
        ]
        for number in _numeric_values(fact.value_payload):
            if not any(
                math.isclose(
                    number,
                    written,
                    rel_tol=1e-12,
                    abs_tol=1e-12,
                )
                for written in written_numbers
            ):
                raise ValueError(
                    "recognized model fact introduced an unwritten number"
                )
        answer_casefold = answer.answer_text.casefold()
        for unit in set(_unit_values(fact.value_payload)):
            if unit.casefold() not in answer_casefold:
                raise ValueError(
                    "recognized model fact introduced an unwritten unit"
                )
    return recognized


def validate_generated_model_payload(
    payload: Any,
    context: ModelValidationContext,
    catalog: ModelQuestionExampleCatalog,
) -> GeneratedModelResult:
    """Parse the three-state result and fail closed on unproven models."""

    typed_context = (
        context
        if isinstance(context, ModelValidationContext)
        else ModelValidationContext.model_validate(context)
    )
    typed_catalog = (
        catalog
        if isinstance(catalog, ModelQuestionExampleCatalog)
        else ModelQuestionExampleCatalog.model_validate(catalog)
    )
    if not isinstance(payload, Mapping):
        return _reject("LLM response must be one JSON object.")
    try:
        validate_non_executable_content(payload)
    except ValueError:
        return _reject("Generated model response contains unsafe content.")
    try:
        result = TypeAdapter(GeneratedModelResult).validate_python(payload)
        recognized = _validate_recognized_facts(result, typed_context)
        recognized_ids = {fact.fact_id for fact in recognized}
        effective_context = typed_context.model_copy(
            update={
                "facts": [*typed_context.facts, *recognized],
                "natural_language_answers": [
                    answer
                    for answer in typed_context.natural_language_answers
                    if answer.fact_id not in recognized_ids
                ],
            }
        )
        effective_context = ModelValidationContext.model_validate(
            effective_context.model_dump(mode="python")
        )
        _validate_adopted_facts(effective_context, typed_catalog)
        if result.status == "need_more":
            _validate_questions(result, typed_catalog)
            return result
        if isinstance(result, ReadyModelResult):
            envelope = validate_generated_model_envelope(
                result.envelope, effective_context
            )
            return result.model_copy(update={"envelope": envelope})
        return result
    except (TypeError, ValueError):
        return _reject(
            "Generated model response failed deterministic contract validation."
        )


__all__ = [
    "ModelValidationContext",
    "validate_non_executable_content",
    "validate_generated_model_envelope",
    "validate_generated_model_payload",
]
