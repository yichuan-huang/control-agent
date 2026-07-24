"""Constrained Stage-6 LLM proposals and sanitized, hash-bound audit records."""

from __future__ import annotations

import math
import re
from collections.abc import Mapping, Sequence
from typing import Any, Literal
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import numpy as np
from pydantic import Field, model_validator

from cfdc.diagnosis.llm import SimulationProposalAdapter
from cfdc.lab.session import (
    TERMINAL_STATES,
    LLMCallRecord,
    LLMMessageRecord,
    ParameterProposal,
    ProposalValidationError,
    SimulationSession,
    append_llm_call,
    build_parameter_proposal,
    controller_architecture_hash,
    extract_tunable_parameters,
    make_llm_call_record,
    register_llm_proposal,
    set_pending_model,
)
from cfdc.models.schemas import (
    ArchetypeClassification,
    CFDCModel,
    ExecutableModelSpec,
    RegisteredNonlinearModelSpec,
    StateSpaceModelSpec,
    StructuralDiagnosis,
    SystemDescription,
    TransferFunctionModelSpec,
)

_PLACEHOLDER_UNITS = frozenset(
    {"", "unspecified", "unknown", "n/a", "na", "none", "tbd", "-", "?"}
)
_FORBIDDEN_KEYS = (
    "code",
    "ode",
    "expression",
    "equation",
    "script",
    "callable",
    "function",
)
_FORBIDDEN_TEXT = re.compile(
    r"```|\b(?:import|exec|eval|lambda)\b|__[A-Za-z0-9_]+__",
    re.IGNORECASE,
)
_URL_RE = re.compile(r"https?://[^\s\"'<>]+", re.IGNORECASE)
_SENSITIVE_MARKERS = ("apikey", "authorization", "token", "secret", "password")


class ModelProposalContext(CFDCModel):
    description: SystemDescription
    diagnosis: StructuralDiagnosis
    classification: ArchetypeClassification
    allowed_model_kinds: list[
        Literal["transfer_function", "state_space", "registered_nonlinear"]
    ] = Field(
        default_factory=lambda: [
            "transfer_function",
            "state_space",
            "registered_nonlinear",
        ],
        min_length=1,
    )
    allowed_registered_templates: list[
        Literal["underactuated_cartpole", "vtol_cascaded"]
    ] = Field(
        default_factory=lambda: [
            "underactuated_cartpole",
            "vtol_cascaded",
        ]
    )
    clarification_answers: list[str] = Field(default_factory=list, max_length=20)

    @model_validator(mode="after")
    def validate_closed_sets(self) -> ModelProposalContext:
        if len(self.allowed_model_kinds) != len(set(self.allowed_model_kinds)):
            raise ValueError("allowed model kinds must be unique")
        if len(self.allowed_registered_templates) != len(
            set(self.allowed_registered_templates)
        ):
            raise ValueError("allowed registered templates must be unique")
        return self


class ModelProposal(CFDCModel):
    schema_version: Literal["model_proposal/v1"] = "model_proposal/v1"
    status: Literal["ready", "need_more", "rejected"]
    model: ExecutableModelSpec | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    assumptions: list[str] = Field(default_factory=list, max_length=20)
    evidence: list[str] = Field(default_factory=list, max_length=40)
    validation_errors: list[str] = Field(default_factory=list, max_length=40)
    questions: list[str] = Field(default_factory=list, max_length=4)
    evidence_boundary: Literal["llm_proposed_model_hypothesis"] = (
        "llm_proposed_model_hypothesis"
    )

    @model_validator(mode="after")
    def validate_status(self) -> ModelProposal:
        if any(
            len(item) > 4000
            for item in (
                self.assumptions
                + self.evidence
                + self.validation_errors
                + self.questions
            )
        ):
            raise ValueError("model-proposal audit text is too long")
        if self.status == "ready":
            if (
                self.model is None
                or self.confidence < 0.70
                or not self.assumptions
                or not self.evidence
                or self.validation_errors
                or self.questions
            ):
                raise ValueError(
                    "ready proposal requires a complete model, confidence >= "
                    "0.70, assumptions/evidence, and no unresolved questions"
                )
        elif self.status == "need_more":
            if not 2 <= len(self.questions) <= 4:
                raise ValueError("need_more requires 2-4 questions")
            if self.model is not None:
                raise ValueError("an unresolved proposal cannot enter simulation")
        elif self.model is not None:
            raise ValueError("a rejected proposal cannot carry a runnable model")
        return self


class _RawModelProposal(CFDCModel):
    status: Literal["ready", "need_more", "rejected"]
    model: ExecutableModelSpec | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    assumptions: list[str] = Field(default_factory=list, max_length=20)
    evidence: list[str] = Field(default_factory=list, max_length=40)
    questions: list[str] = Field(default_factory=list, max_length=4)

    @model_validator(mode="after")
    def validate_text_limits(self) -> _RawModelProposal:
        if any(
            len(item) > 4000
            for item in self.assumptions + self.evidence + self.questions
        ):
            raise ValueError("raw model-proposal text is too long")
        return self


class MinimalStabilityEvidence(CFDCModel):
    status: Literal["stable", "unstable", "inconclusive"]
    analysis_domain: Literal["continuous", "discrete"]
    normalized_margin: float
    tail_error_envelope_contraction: float
    saturation_fraction: float = Field(ge=0.0, le=1.0)
    hard_failure: bool
    violations: list[str] = Field(default_factory=list, max_length=20)


class GainProposalContext(CFDCModel):
    session_id: str
    revision: int = Field(ge=0)
    base_trial_iteration: int = Field(ge=1, le=20)
    controller_kind: str = Field(min_length=1)
    registered_controller_id: str | None = None
    architecture_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    current_parameters: dict[str, float] = Field(min_length=1)
    tunable_whitelist: list[str] = Field(min_length=1)
    parameter_bounds: dict[str, tuple[float, float]] = Field(min_length=1)
    maximum_relative_change: Literal[0.1] = 0.1
    last_stability_evidence: MinimalStabilityEvidence

    @model_validator(mode="after")
    def validate_exact_whitelist(self) -> GainProposalContext:
        expected = set(self.tunable_whitelist)
        if (
            len(expected) != len(self.tunable_whitelist)
            or set(self.current_parameters) != expected
            or set(self.parameter_bounds) != expected
        ):
            raise ValueError("gain context must use one exact whitelist")
        return self


class _RawGainProposal(CFDCModel):
    new_parameters: dict[str, float] = Field(min_length=1)
    rationale: str = Field(min_length=1, max_length=4000)


class ProposalCallResult(CFDCModel):
    proposal: ModelProposal | ParameterProposal | None = None
    call_record: LLMCallRecord


def _normalized_key(key: str) -> str:
    return re.sub(r"[_\-\s]", "", key).casefold()


def _sanitize_url(url: str) -> str:
    try:
        parsed = urlsplit(url)
    except ValueError:
        return "[REDACTED_URL]"
    host = parsed.hostname or ""
    if parsed.port:
        host = f"{host}:{parsed.port}"
    query: list[tuple[str, str]] = []
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        if any(marker in _normalized_key(key) for marker in _SENSITIVE_MARKERS):
            query.append(("redacted", "[REDACTED]"))
        else:
            query.append((key, value))
    return urlunsplit(
        (
            parsed.scheme,
            host,
            parsed.path,
            urlencode(query),
            "",
        )
    )


def _sanitize_string(text: str, secrets: Sequence[str]) -> str:
    clean = text
    for secret in sorted({item for item in secrets if item}, key=len, reverse=True):
        clean = clean.replace(secret, "[REDACTED]")
    clean = re.sub(
        r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+",
        "Bearer [REDACTED]",
        clean,
    )
    clean = re.sub(
        r"(?i)\b(api[_ -]?key|authorization|token|secret|password)"
        r"\s*[:=]\s*[^\s,;\"'}]+",
        lambda match: f"{match.group(1)}=[REDACTED]",
        clean,
    )
    clean = _URL_RE.sub(lambda match: _sanitize_url(match.group(0)), clean)
    return clean[:50_000]


def sanitize_for_audit(value: Any, *, secret_literals: Sequence[str] = ()) -> Any:
    """Recursively redact credentials and URL secrets before hashing/logging."""

    if isinstance(value, Mapping):
        result: dict[str, Any] = {}
        redacted_index = 0
        for key, item in value.items():
            if any(
                marker in _normalized_key(str(key)) for marker in _SENSITIVE_MARKERS
            ):
                redacted_index += 1
                result[f"redacted_{redacted_index}"] = "[REDACTED]"
            else:
                safe_key = _sanitize_string(str(key), secret_literals)
                if safe_key in result:
                    redacted_index += 1
                    safe_key = f"redacted_{redacted_index}"
                result[safe_key] = sanitize_for_audit(
                    item, secret_literals=secret_literals
                )
        return result
    if isinstance(value, (list, tuple)):
        return [
            sanitize_for_audit(item, secret_literals=secret_literals) for item in value
        ]
    if isinstance(value, str):
        return _sanitize_string(value, secret_literals)
    if isinstance(value, float) and not math.isfinite(value):
        return "[REDACTED_NON_FINITE]"
    return value


def build_model_proposal_messages(
    context: ModelProposalContext | Any,
) -> list[dict[str, str]]:
    typed = (
        context
        if isinstance(context, ModelProposalContext)
        else ModelProposalContext.model_validate(context)
    )
    system = (
        "You propose a software-only control-object model. Return strict JSON "
        "only. Never emit Python, ODE code, expressions, functions, imports, "
        "controller gains, or unregistered templates."
    )
    user = (
        "Return exactly this object:\n"
        '{"status":"ready|need_more|rejected","model":null|{typed model},'
        '"confidence":0.0,"assumptions":["string"],"evidence":["string"],'
        '"questions":["string"]}\n'
        "A ready model must be one allowed typed transfer-function, "
        "state-space, CartPole, or VTOL object; include complete units and "
        "all required fields. If confidence is below 0.70 or facts are "
        "missing/conflicting, set need_more and ask 2-4 plain-language "
        "questions. Do not add keys or use code fences.\n"
        f"context={typed.model_dump_json()}"
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def build_gain_proposal_messages(
    context: GainProposalContext | Any,
) -> list[dict[str, str]]:
    typed = (
        context
        if isinstance(context, GainProposalContext)
        else GainProposalContext.model_validate(context)
    )
    system = (
        "You propose one stability-only gain update. Return strict JSON only. "
        "Do not change architecture, name a source/approval/checksum/model, or "
        "add parameters."
    )
    user = (
        "Return exactly "
        '{"new_parameters":{"every_whitelisted_gain":0.0},'
        '"rationale":"stability-only reason"}. '
        "Keep every gain finite, inside its supplied bounds, and within 10% "
        "of its current value. Change at least one whitelisted gain; never "
        "echo the complete current parameter map unchanged. Do not optimize "
        "overshoot, settling time, IAE, or performance. Do not add keys or code.\n"
        f"context={typed.model_dump_json()}"
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def _unsafe_payload_findings(value: Any, path: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            normalized = _normalized_key(str(key))
            if normalized in _FORBIDDEN_KEYS or any(
                normalized.endswith(suffix)
                for suffix in ("code", "script", "callable", "function")
            ):
                findings.append(f"forbidden executable field at {path}.{key}")
            findings.extend(_unsafe_payload_findings(item, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            findings.extend(_unsafe_payload_findings(item, f"{path}[{index}]"))
    elif isinstance(value, str) and _FORBIDDEN_TEXT.search(value):
        findings.append(f"forbidden executable text at {path}")
    elif isinstance(value, bool):
        findings.append(f"boolean is not accepted as a numeric value at {path}")
    return findings


def _plain_questions(errors: Sequence[str]) -> list[str]:
    base = [
        "What are the exact actuator and measured-output signal names and units?",
        "Can you provide the complete numeric plant model and its source?",
        "Is the model continuous or discrete, and what is the sample time if discrete?",
        "Which operating point and initial state should the software simulation use?",
    ]
    count = min(4, max(2, len(errors)))
    return base[:count]


def _unit_errors(model: ExecutableModelSpec) -> list[str]:
    errors: list[str] = []

    def placeholder(value: str | None) -> bool:
        return value is None or value.strip().casefold() in _PLACEHOLDER_UNITS

    if isinstance(model, TransferFunctionModelSpec):
        if placeholder(model.input_units) or placeholder(model.output_units):
            errors.append("transfer-function input/output units must be explicit")
        return errors
    if isinstance(model, StateSpaceModelSpec):
        if any(
            len(values) != len(set(values))
            for values in (
                model.state_names,
                model.input_signal_ids,
                model.output_signal_ids,
            )
        ):
            errors.append("state/input/output signal IDs must be unique")
        names = (
            set(model.state_names)
            | set(model.input_signal_ids)
            | set(model.output_signal_ids)
        )
    else:
        if len(model.input_signal_ids) != len(set(model.input_signal_ids)) or len(
            model.output_signal_ids
        ) != len(set(model.output_signal_ids)):
            errors.append("registered input/output signal IDs must be unique")
        names = (
            set(model.initial_state)
            | set(model.input_signal_ids)
            | set(model.output_signal_ids)
        )
    if set(model.signal_units) != names:
        errors.append(
            "signal_units must cover every declared state/input/output exactly"
        )
    if any(placeholder(model.signal_units.get(name)) for name in names):
        errors.append("all declared signal units must be non-placeholder")
    return errors


def _model_size_errors(model: ExecutableModelSpec) -> list[str]:
    if isinstance(model, TransferFunctionModelSpec):
        if len(model.numerator) > 128 or len(model.denominator) > 128:
            return ["transfer-function coefficient count exceeds the safety limit"]
        return []
    if isinstance(model, StateSpaceModelSpec) and (
        len(model.state_names) > 32
        or len(model.input_signal_ids) > 8
        or len(model.output_signal_ids) > 8
    ):
        return ["state-space dimensions exceed the Stage-6 safety limit"]
    return []


def _signal_errors(
    model: ExecutableModelSpec, description: SystemDescription
) -> list[str]:
    if isinstance(model, TransferFunctionModelSpec):
        inputs = {model.input_signal_id}
        outputs = {model.output_signal_id}
    else:
        inputs = set(model.input_signal_ids)
        outputs = set(model.output_signal_ids)
    errors: list[str] = []
    if not description.actuators or not description.observed_outputs:
        errors.append(
            "description must declare actuator and observed-output signal IDs"
        )
        return errors
    if inputs != set(description.actuators):
        errors.append("model inputs conflict with declared actuators")
    if outputs != set(description.observed_outputs):
        errors.append("model outputs conflict with declared observed outputs")
    return errors


def _structure_errors(
    model: ExecutableModelSpec,
    context: ModelProposalContext,
) -> list[str]:
    coupling = str(context.diagnosis.coupling_severity.assessment)
    errors: list[str] = []
    if isinstance(model, TransferFunctionModelSpec):
        input_count = output_count = 1
    else:
        input_count = len(model.input_signal_ids)
        output_count = len(model.output_signal_ids)
    if coupling == "siso" and (input_count != 1 or output_count != 1):
        errors.append("MIMO model conflicts with SISO diagnosis")
    if coupling in {"weak_mimo", "severe_mimo"} and (
        input_count < 2 or output_count < 2
    ):
        errors.append("SISO model conflicts with multivariable diagnosis")
    primary_class = str(context.classification.primary_class)
    if primary_class == "class_v_multivariable_significant_coupling" and (
        input_count < 2 or output_count < 2
    ):
        errors.append("SISO model conflicts with Class V classification")
    if primary_class != "class_v_multivariable_significant_coupling" and (
        coupling == "siso" and (input_count > 1 or output_count > 1)
    ):
        errors.append("MIMO model conflicts with the selected non-Class-V route")
    if coupling == "underactuated" and (
        not isinstance(model, RegisteredNonlinearModelSpec)
        or model.template_id != "underactuated_cartpole"
    ):
        errors.append(
            "underactuated diagnosis requires the registered CartPole template"
        )
    if coupling == "cascaded" and (
        not isinstance(model, RegisteredNonlinearModelSpec)
        or model.template_id != "vtol_cascaded"
    ):
        errors.append("cascaded diagnosis requires the registered VTOL template")
    if isinstance(model, RegisteredNonlinearModelSpec):
        expected = (
            "underactuated"
            if model.template_id == "underactuated_cartpole"
            else "cascaded"
        )
        if coupling not in {expected, "unknown"}:
            errors.append(
                f"registered {model.template_id} conflicts with coupling diagnosis"
            )
    stability = str(context.diagnosis.open_loop_stability.assessment)
    if isinstance(model, RegisteredNonlinearModelSpec):
        model_stability = "unstable"
    elif isinstance(model, TransferFunctionModelSpec):
        poles = np.roots(np.asarray(model.denominator, dtype=float))
        if model.time_domain == "continuous":
            model_stability = (
                "stable" if all(pole.real < -1e-6 for pole in poles) else "unstable"
            )
        else:
            model_stability = (
                "stable"
                if all(abs(pole) < 1.0 - 1e-6 for pole in poles)
                else "unstable"
            )
    else:
        poles = np.linalg.eigvals(np.asarray(model.a, dtype=float))
        if model.time_domain == "continuous":
            model_stability = (
                "stable" if all(pole.real < -1e-6 for pole in poles) else "unstable"
            )
        else:
            model_stability = (
                "stable"
                if all(abs(pole) < 1.0 - 1e-6 for pole in poles)
                else "unstable"
            )
    if stability in {"stable", "unstable"} and stability != model_stability:
        errors.append("typed model open-loop stability conflicts with the diagnosis")
    return errors


def validate_model_proposal_payload(
    payload: Any, context: ModelProposalContext
) -> ModelProposal:
    """Turn raw JSON into a simulation-gated hypothesis or questions."""

    if not isinstance(payload, dict):
        return ModelProposal(
            status="rejected",
            confidence=0.0,
            validation_errors=["LLM response must be one JSON object"],
        )
    unsafe = _unsafe_payload_findings(payload)
    if unsafe:
        return ModelProposal(
            status="rejected",
            confidence=0.0,
            validation_errors=unsafe,
        )
    try:
        raw = _RawModelProposal.model_validate(payload)
    except ValueError as exc:
        errors = [f"typed model response validation failed: {exc}"]
        return ModelProposal(
            status="need_more",
            confidence=0.0,
            validation_errors=errors,
            questions=_plain_questions(errors),
        )
    if raw.status == "rejected":
        return ModelProposal(
            status="rejected",
            confidence=raw.confidence,
            assumptions=raw.assumptions,
            evidence=raw.evidence,
            validation_errors=["LLM declined to provide a complete model"],
        )
    if raw.status == "need_more":
        questions = raw.questions or _plain_questions(["missing model facts"])
        if not 2 <= len(questions) <= 4:
            questions = _plain_questions(["invalid question count"])
        return ModelProposal(
            status="need_more",
            confidence=raw.confidence,
            assumptions=raw.assumptions,
            evidence=raw.evidence,
            validation_errors=["model facts remain incomplete"],
            questions=questions,
        )
    errors: list[str] = []
    if raw.model is None:
        errors.append("ready response omitted the typed model")
    else:
        if raw.model.kind not in context.allowed_model_kinds:
            errors.append("model kind is not allowlisted")
        if (
            isinstance(raw.model, RegisteredNonlinearModelSpec)
            and raw.model.template_id not in context.allowed_registered_templates
        ):
            errors.append("registered model template is not allowlisted")
        errors.extend(_unit_errors(raw.model))
        errors.extend(_model_size_errors(raw.model))
        errors.extend(_signal_errors(raw.model, context.description))
        errors.extend(_structure_errors(raw.model, context))
    if raw.confidence < 0.70:
        errors.append("model confidence is below 0.70")
    if not raw.assumptions:
        errors.append("ready model requires explicit assumptions")
    if not raw.evidence:
        errors.append("ready model requires source evidence")
    if errors:
        return ModelProposal(
            status="need_more",
            confidence=raw.confidence,
            assumptions=raw.assumptions,
            evidence=raw.evidence,
            validation_errors=errors,
            questions=_plain_questions(errors),
        )
    return ModelProposal(
        status="ready",
        model=raw.model,
        confidence=raw.confidence,
        assumptions=raw.assumptions,
        evidence=raw.evidence,
    )


def build_gain_proposal_context(
    session: SimulationSession,
) -> GainProposalContext:
    if session.state in TERMINAL_STATES:
        raise ProposalValidationError(
            "terminal simulation sessions cannot request another gain proposal"
        )
    if session.state not in {"needs_adjustment", "rolled_back"}:
        raise ProposalValidationError(
            "LLM gain proposals are allowed only after an adjustable or "
            "rolled-back trial"
        )
    if (
        not session.trials
        or session.trial_controller is None
        or session.tuning_profile is None
    ):
        raise ProposalValidationError("session lacks a completed trial/tuning profile")
    if (
        session.pending_proposal is not None
        and session.pending_proposal.approval_state == "pending"
    ):
        raise ProposalValidationError(
            "resolve the existing LLM proposal before requesting another"
        )
    latest = session.trials[-1].stability
    if latest.analysis_domain == "continuous":
        margin = -(max((pole.real for pole in latest.poles), default=1.0) + 1e-6)
    else:
        margin = (
            1.0
            - 1e-6
            - (latest.spectral_radius if latest.spectral_radius is not None else 2.0)
        )
    profile = session.tuning_profile
    controller = session.trial_controller
    return GainProposalContext(
        session_id=session.session_id,
        revision=session.revision,
        base_trial_iteration=len(session.trials),
        controller_kind=controller.kind,
        registered_controller_id=(
            controller.controller_id
            if controller.kind == "registered_controller"
            else None
        ),
        architecture_sha256=controller_architecture_hash(controller, profile),
        current_parameters=extract_tunable_parameters(controller, profile),
        tunable_whitelist=profile.whitelist,
        parameter_bounds={
            rule.name: (rule.lower_bound, rule.upper_bound)
            for rule in profile.parameters
        },
        last_stability_evidence=MinimalStabilityEvidence(
            status=latest.status,
            analysis_domain=latest.analysis_domain,
            normalized_margin=margin / (1.0 + abs(margin)),
            tail_error_envelope_contraction=(latest.tail_error_envelope_contraction),
            saturation_fraction=latest.saturation_fraction,
            hard_failure=latest.hard_failure,
            violations=list(latest.violations),
        ),
    )


def _adapter_identity(adapter: Any, secrets: Sequence[str] = ()) -> tuple[str, str]:
    base_url = str(getattr(adapter, "base_url", "custom-adapter"))
    try:
        provider = urlsplit(base_url).hostname or base_url
    except ValueError:
        provider = "custom-adapter"
    model = str(getattr(adapter, "model", type(adapter).__name__))
    safe_provider = str(sanitize_for_audit(provider, secret_literals=secrets))
    safe_model = str(sanitize_for_audit(model, secret_literals=secrets))
    return (
        safe_provider[:200] or "custom-adapter",
        safe_model[:300] or "unknown-model",
    )


def _secret_literals(adapter: Any, additional: Sequence[str]) -> list[str]:
    values = list(additional)
    candidate = getattr(adapter, "api_key", None)
    if isinstance(candidate, str) and candidate:
        values.append(candidate)
    return values


def _audit_messages(
    messages: Sequence[Mapping[str, str]], secrets: Sequence[str]
) -> list[LLMMessageRecord]:
    sanitized = sanitize_for_audit(messages, secret_literals=secrets)
    return [LLMMessageRecord.model_validate(item) for item in sanitized]


def request_model_proposal(
    adapter: SimulationProposalAdapter,
    context: ModelProposalContext,
    *,
    secret_literals: Sequence[str] = (),
) -> ProposalCallResult:
    """Make one model-proposal call and always return a sanitized audit record."""

    messages = build_model_proposal_messages(context)
    secrets = _secret_literals(adapter, secret_literals)
    provider, model_name = _adapter_identity(adapter, secrets)
    audit_messages = _audit_messages(messages, secrets)
    try:
        raw = adapter.propose_model(context)
        proposal = validate_model_proposal_payload(raw, context)
        sanitized_response = sanitize_for_audit(raw, secret_literals=secrets)
        status: Literal["accepted", "rejected", "need_more", "error"] = (
            "accepted" if proposal.status == "ready" else proposal.status
        )
        record = make_llm_call_record(
            operation="model_proposal",
            provider=provider,
            model=model_name,
            messages=audit_messages,
            structured_response={
                "raw": (
                    dict(sanitized_response)
                    if isinstance(sanitized_response, Mapping)
                    else {"response": sanitized_response}
                ),
                "validated": proposal.model_dump(mode="json"),
            },
            validation_status=status,
            validation_errors=proposal.validation_errors,
        )
        return ProposalCallResult(proposal=proposal, call_record=record)
    except Exception as exc:  # noqa: BLE001 - audit arbitrary adapter failures
        safe_error = sanitize_for_audit(
            f"{type(exc).__name__}: {exc}", secret_literals=secrets
        )
        record = make_llm_call_record(
            operation="model_proposal",
            provider=provider,
            model=model_name,
            messages=audit_messages,
            invalid_raw_text=str(safe_error)[:20_000],
            validation_status="error",
            validation_errors=[str(safe_error)[:2000]],
        )
        return ProposalCallResult(call_record=record)


def request_model_for_session(
    session: SimulationSession,
    adapter: SimulationProposalAdapter,
    context: ModelProposalContext,
    *,
    expected_revision: int | None = None,
    secret_literals: Sequence[str] = (),
) -> tuple[SimulationSession, ProposalCallResult]:
    if session.state != "model_review":
        raise ProposalValidationError(
            "model proposals are allowed only in model_review"
        )
    if session.origin != "llm_proposed_model_hypothesis":
        raise ProposalValidationError(
            "audited benchmark/demo models cannot be replaced by an LLM"
        )
    expected = session.revision if expected_revision is None else expected_revision
    if expected != session.revision:
        from cfdc.lab.session import StaleRevisionError

        raise StaleRevisionError("stale model-proposal session revision")
    result = request_model_proposal(adapter, context, secret_literals=secret_literals)
    updated = append_llm_call(
        session, result.call_record, expected_revision=session.revision
    )
    proposal = result.proposal
    if isinstance(proposal, ModelProposal) and proposal.status == "ready":
        assert proposal.model is not None
        updated = set_pending_model(
            updated,
            proposal.model,
            assumptions=proposal.assumptions,
            expected_revision=updated.revision,
        )
    return updated, result


def request_gain_proposal(
    session: SimulationSession,
    adapter: SimulationProposalAdapter,
    *,
    secret_literals: Sequence[str] = (),
) -> ProposalCallResult:
    """Request one gain map; backend owns all proposal identity and approval."""

    context = build_gain_proposal_context(session)
    messages = build_gain_proposal_messages(context)
    secrets = _secret_literals(adapter, secret_literals)
    provider, model_name = _adapter_identity(adapter, secrets)
    audit_messages = _audit_messages(messages, secrets)
    try:
        raw = adapter.propose_gain_update(context)
        unsafe = _unsafe_payload_findings(raw)
        if unsafe:
            raise ProposalValidationError("; ".join(unsafe))
        typed = _RawGainProposal.model_validate(raw)
        proposal = build_parameter_proposal(
            session,
            source="llm",
            new_parameters=typed.new_parameters,
            rationale=typed.rationale,
        )
        sanitized_response = sanitize_for_audit(raw, secret_literals=secrets)
        record = make_llm_call_record(
            operation="gain_proposal",
            provider=provider,
            model=model_name,
            messages=audit_messages,
            structured_response=sanitized_response,
            validation_status="accepted",
        )
        return ProposalCallResult(proposal=proposal, call_record=record)
    except Exception as exc:  # noqa: BLE001 - audit arbitrary adapter failures
        safe_error = sanitize_for_audit(
            f"{type(exc).__name__}: {exc}", secret_literals=secrets
        )
        raw_response = locals().get("raw")
        sanitized_response = sanitize_for_audit(raw_response, secret_literals=secrets)
        if isinstance(sanitized_response, Mapping):
            record = make_llm_call_record(
                operation="gain_proposal",
                provider=provider,
                model=model_name,
                messages=audit_messages,
                structured_response=sanitized_response,
                validation_status="rejected",
                validation_errors=[str(safe_error)[:2000]],
            )
        else:
            record = make_llm_call_record(
                operation="gain_proposal",
                provider=provider,
                model=model_name,
                messages=audit_messages,
                invalid_raw_text=str(safe_error)[:20_000],
                validation_status="error",
                validation_errors=[str(safe_error)[:2000]],
            )
        return ProposalCallResult(call_record=record)


def request_gain_for_session(
    session: SimulationSession,
    adapter: SimulationProposalAdapter,
    *,
    expected_revision: int | None = None,
    secret_literals: Sequence[str] = (),
) -> tuple[SimulationSession, ProposalCallResult]:
    expected = session.revision if expected_revision is None else expected_revision
    if expected != session.revision:
        from cfdc.lab.session import StaleRevisionError

        raise StaleRevisionError("stale gain-proposal session revision")
    result = request_gain_proposal(session, adapter, secret_literals=secret_literals)
    proposal = result.proposal
    if isinstance(proposal, ParameterProposal):
        updated = register_llm_proposal(
            session,
            new_parameters=proposal.new_parameters,
            rationale=proposal.rationale,
            llm_call_record=result.call_record,
            expected_revision=session.revision,
        )
        # Return the exact registered/backend proposal snapshot.
        result = ProposalCallResult(
            proposal=updated.pending_proposal,
            call_record=result.call_record,
        )
    else:
        updated = append_llm_call(
            session,
            result.call_record,
            expected_revision=session.revision,
        )
    return updated, result


__all__ = [
    "GainProposalContext",
    "MinimalStabilityEvidence",
    "ModelProposal",
    "ModelProposalContext",
    "ProposalCallResult",
    "build_gain_proposal_context",
    "build_gain_proposal_messages",
    "build_model_proposal_messages",
    "request_gain_for_session",
    "request_gain_proposal",
    "request_model_for_session",
    "request_model_proposal",
    "sanitize_for_audit",
    "validate_model_proposal_payload",
]
