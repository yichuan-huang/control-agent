"""Prompting, parsing, and sanitized auditing for model discovery calls."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any, Literal
from urllib.parse import urlsplit

from pydantic import TypeAdapter

from cfdc.diagnosis.llm import SimulationProposalAdapter
from cfdc.lab.llm import sanitize_for_audit
from cfdc.lab.model_contracts import (
    GeneratedModelResult,
    ModelQuestionExampleCatalog,
)
from cfdc.lab.model_validation import (
    ModelValidationContext,
    validate_generated_model_payload,
    validate_non_executable_content,
)
from cfdc.lab.session import (
    LLMCallRecord,
    LLMMessageRecord,
    make_llm_call_record,
)
from cfdc.models.schemas import CFDCModel


class ModelDiscoveryContext(ModelValidationContext):
    """Typed request context for the new three-state discovery protocol."""


class ModelDiscoveryCallResult(CFDCModel):
    result: GeneratedModelResult | None = None
    call_record: LLMCallRecord


def build_model_discovery_messages(
    context: ModelDiscoveryContext,
    catalog: ModelQuestionExampleCatalog,
) -> list[dict[str, str]]:
    typed_context = (
        context
        if isinstance(context, ModelDiscoveryContext)
        else ModelDiscoveryContext.model_validate(context)
    )
    typed_catalog = (
        catalog
        if isinstance(catalog, ModelQuestionExampleCatalog)
        else ModelQuestionExampleCatalog.model_validate(catalog)
    )
    validate_non_executable_content(typed_context.model_dump(mode="json"))
    validate_non_executable_content(typed_catalog.model_dump(mode="json"))
    examples = [
        {
            "example_id": example.example_id,
            "fact_type": example.fact_type,
            "unit_family": example.unit_family,
            "answer_text": example.answer_text,
            "value_payload": example.value_payload,
        }
        for example in typed_catalog.examples
    ]
    system = (
        "You discover a software-only control-object model and return strict "
        "JSON only. Return one object with status=need_more|ready|rejected. "
        "Never emit executable code, arbitrary ODEs, imports, callbacks, URLs, "
        "module paths, functions, or controller gains. equation_latex is "
        "display-only text and is never evaluated."
    )
    user = (
        "Use exactly one of these three result shapes:\n"
        'need_more={"status":"need_more","missing_fact_ids":["fact"],'
        '"questions":[{"question_id":"id","fact_id":"fact",'
        '"fact_type":"catalog fact type","prompt":"plain question",'
        '"answer_kind":"text|number|matrix|structured",'
        '"unit_family":"catalog unit family","example_id":"existing catalog ID",'
        '"why_needed":"plain reason"}],"recognized_facts":[],'
        '"rationale":"reason"}\n'
        'ready={"status":"ready","envelope":{"envelope_schema_version":'
        '"generated_model_envelope/v1","model_role":"typed role",'
        '"model":{"kind":"typed executable model"},"operating_point":null,'
        '"validity_region":null,"parameter_evidence":[{"parameter_path":'
        '"exact numeric path","value":0.0,"unit":"explicit unit","source":'
        '"typed source","source_fact_ids":["existing fact"],'
        '"derivation_rule_id":null,"unit_conversion":null}],'
        '"assumptions":["text"],"limitations":["text"],'
        '"plain_language_summary":"text","equation_latex":["display only"],'
        '"experiment_proposal":{"initial_state":{},"reference":{"signal":0.0},'
        '"horizon_s":1.0,"sample_time_s":0.1,"actuator_bounds":'
        '{"signal":[-1.0,1.0]},"state_bounds":{},"output_bounds":'
        '{"signal":[-1.0,1.0]},"signal_units":{"signal":"unit"},'
        '"evidence_fact_ids":["existing fact"],"registry_policy_id":null}},'
        '"recognized_facts":[],"confidence":0.0,"rationale":"reason"}\n'
        'rejected={"status":"rejected","reason":"reason","next_steps":'
        '["plain next step"]}\n'
        "Rules: ask 1-4 plain questions; each question must use an existing "
        "catalog example_id with matching fact_type and unit_family. A ready "
        "or need_more result may type a verbatim natural_language_answer into "
        "recognized_facts. Its fact ID, type, unit family, and answer_text must "
        "match exactly, and every numeric value and unit must appear literally "
        "in that answer; never rewrite, infer, or add a number. "
        "Do not repeat facts that are already typed. A ready "
        "result must include evidence for every model coefficient, matrix "
        "element, registered parameter, initial value, bound, and runtime "
        "number. Direct evidence must identify a semantically matching numeric "
        "fact leaf with the same unit. Computed fields must use only these "
        "registered derivations: step_ratio_gain/v1, response_time_63/v1, "
        "response_delay/v1, sample_time/v1, normalized_one/v1, "
        "normalized_zero/v1, six_time_constants_horizon/v1, and "
        "time_constant_div_50_sample/v1. For transfer functions expressed "
        "around the measured starting point, use "
        "output_step_delta_reference/v1, "
        "center_actuator_bounds_at_input_before/v1, and "
        "center_output_bounds_at_output_before/v1 so absolute user values "
        "become consistent deviation-coordinate trial values. "
        "Step gain, response time, normalized coefficients, and delay may "
        "parameterize only the registered continuous first-order canonical "
        "form numerator=[gain], denominator=[time_constant,1]. Discrete and "
        "higher-order coefficients fail closed without a dedicated closed "
        "coefficient fact contract. "
        "registry_policy may attest only exact "
        "registered experiment paths and values, never model parameters or "
        "initial state. parameter_uncertainty values require exact matching "
        "parameter_uncertainty facts with relative unit 1. Use only "
        "supplied/adopted facts. confidence is not a gate. "
        "Do not add fields or use code fences.\n"
        f"context={typed_context.model_dump_json()}\n"
        "fixed_examples="
        f"{json.dumps(examples, ensure_ascii=False, separators=(',', ':'))}"
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def _secret_literals(adapter: Any, additional: Sequence[str]) -> list[str]:
    secrets = [secret for secret in additional if secret]
    api_key = getattr(adapter, "api_key", None)
    if isinstance(api_key, str) and api_key:
        secrets.append(api_key)
    return secrets


def _adapter_identity(adapter: Any, secrets: Sequence[str]) -> tuple[str, str]:
    base_url = str(getattr(adapter, "base_url", "custom-adapter"))
    try:
        provider = urlsplit(base_url).hostname or base_url
    except ValueError:
        provider = "custom-adapter"
    model = str(getattr(adapter, "model", type(adapter).__name__))
    safe_provider = str(sanitize_for_audit(provider, secret_literals=secrets))[:200]
    safe_model = str(sanitize_for_audit(model, secret_literals=secrets))[:300]
    return safe_provider or "custom-adapter", safe_model or "unknown-model"


def _audit_messages(
    messages: Sequence[Mapping[str, str]], secrets: Sequence[str]
) -> list[LLMMessageRecord]:
    sanitized = sanitize_for_audit(messages, secret_literals=secrets)
    return [LLMMessageRecord.model_validate(message) for message in sanitized]


def request_model_discovery(
    adapter: SimulationProposalAdapter,
    context: ModelDiscoveryContext,
    catalog: ModelQuestionExampleCatalog,
    *,
    secret_literals: Sequence[str] = (),
) -> ModelDiscoveryCallResult:
    """Request and deterministically gate one three-state discovery result."""

    secrets = _secret_literals(adapter, secret_literals)
    provider, model_name = _adapter_identity(adapter, secrets)
    safe_context_payload = sanitize_for_audit(
        context.model_dump(mode="python"), secret_literals=secrets
    )
    try:
        safe_context = ModelDiscoveryContext.model_validate(safe_context_payload)
        messages = build_model_discovery_messages(safe_context, catalog)
    except Exception as exc:
        audit_messages = _audit_messages(
            [
                {
                    "role": "system",
                    "content": (
                        "Model discovery context was rejected before any "
                        "provider invocation."
                    ),
                }
            ],
            secrets,
        )
        safe_error = str(
            sanitize_for_audit(
                f"{type(exc).__name__}: {exc}",
                secret_literals=secrets,
            )
        )
        record = make_llm_call_record(
            operation="model_proposal",
            provider=provider,
            model=model_name,
            messages=audit_messages,
            invalid_raw_text=safe_error[:20_000],
            validation_status="error",
            validation_errors=[safe_error[:2000]],
        )
        return ModelDiscoveryCallResult(call_record=record)

    audit_messages = _audit_messages(messages, secrets)
    provider_messages = [message.model_dump(mode="json") for message in audit_messages]
    try:
        propose_with_messages = getattr(adapter, "propose_model_with_messages", None)
        if not callable(propose_with_messages):
            raise ValueError(
                "model-discovery adapter cannot send the exact audited message list"
            )
        raw = propose_with_messages(safe_context, provider_messages)
        result = validate_generated_model_payload(raw, safe_context, catalog)
        safe_raw = sanitize_for_audit(raw, secret_literals=secrets)
        safe_validated = sanitize_for_audit(
            result.model_dump(mode="json"), secret_literals=secrets
        )
        result = TypeAdapter(GeneratedModelResult).validate_python(safe_validated)
        structured_response = {
            "raw": (
                dict(safe_raw)
                if isinstance(safe_raw, Mapping)
                else {"response": safe_raw}
            ),
            "validated": safe_validated,
        }
        status: Literal["accepted", "rejected", "need_more", "error"] = (
            "accepted" if result.status == "ready" else result.status
        )
        errors = (
            []
            if result.status != "rejected"
            else [
                str(sanitize_for_audit(result.reason, secret_literals=secrets))[:2000]
            ]
        )
        record = make_llm_call_record(
            operation="model_proposal",
            provider=provider,
            model=model_name,
            messages=audit_messages,
            structured_response=structured_response,
            validation_status=status,
            validation_errors=errors,
        )
        return ModelDiscoveryCallResult(result=result, call_record=record)
    except Exception as exc:
        safe_error = str(
            sanitize_for_audit(
                f"{type(exc).__name__}: {exc}",
                secret_literals=secrets,
            )
        )
        record = make_llm_call_record(
            operation="model_proposal",
            provider=provider,
            model=model_name,
            messages=audit_messages,
            invalid_raw_text=safe_error[:20_000],
            validation_status="error",
            validation_errors=[safe_error[:2000]],
        )
        return ModelDiscoveryCallResult(call_record=record)


__all__ = [
    "ModelDiscoveryCallResult",
    "ModelDiscoveryContext",
    "build_model_discovery_messages",
    "request_model_discovery",
]
