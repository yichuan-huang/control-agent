from __future__ import annotations

import json
import os
from typing import Any, Protocol
from urllib.parse import urlparse

from openai import OpenAI

from cfdc.models import DelayAssessment, StructuralDiagnosis, SystemDescription


PROMPT_VERSION = "cfdc-stage0-v3-normalized-delay"


class DiagnosticAdapter(Protocol):
    """LLM-facing adapter: implementations must return structured data only."""

    def diagnose(self, description: SystemDescription) -> dict[str, Any]:
        ...


def parse_json_content(content: str) -> dict[str, Any]:
    parsed = json.loads(content)
    if not isinstance(parsed, dict):
        raise ValueError("LLM response content must be a JSON object")
    return parsed


def build_diagnostic_prompt(description: SystemDescription) -> str:
    return (
        "You are the Stage 0 diagnostic engine for an independent "
        "Core-Feature-Driven Control (CFDC) framework.\n\n"
        "Return ONLY one JSON object. Do not include markdown, prose, or code fences.\n\n"
        "The JSON object must match this shape exactly:\n"
        "{\n"
        '  "open_loop_stability": {"status": "known|inferred|unknown", "value": "...", "confidence": 0.0, "evidence": ["..."]},\n'
        '  "minimum_phase": {"status": "known|inferred|unknown", "value": "...", "confidence": 0.0, "evidence": ["..."]},\n'
        '  "significant_delay": {"status": "known|inferred|unknown", "value": "...", "assessment": "significant|not_significant|unknown", "confidence": 0.0, "evidence": ["..."]},\n'
        '  "relative_degree": {"status": "known|inferred|unknown", "value": "...", "confidence": 0.0, "evidence": ["..."]},\n'
        '  "controllability_observability": {"status": "known|inferred|unknown", "value": "...", "confidence": 0.0, "evidence": ["..."]},\n'
        '  "nonlinearity_strength": {"status": "known|inferred|unknown", "value": "...", "confidence": 0.0, "evidence": ["..."]},\n'
        '  "coupling_severity": {"status": "known|inferred|unknown", "value": "...", "confidence": 0.0, "evidence": ["..."]},\n'
        '  "uncertainty_magnitude": {"status": "known|inferred|unknown", "value": "...", "confidence": 0.0, "evidence": ["..."]},\n'
        '  "clarification_questions": ["..."],\n'
        '  "complete": true\n'
        "}\n\n"
        "Rules:\n"
        "- Fill all eight diagnostic fields.\n"
        "- significant_delay.assessment must be exactly significant, not_significant, or unknown.\n"
        "- significant_delay status=unknown if and only if assessment=unknown.\n"
        "- If any field is unknown, set complete=false and ask 2-4 plain-language clarification questions.\n"
        "- If all fields are known or reasonably inferred, set complete=true and use an empty clarification_questions list.\n"
        "- An explicitly unobserved or unknown delay must remain unknown; absence of a delay statement is not evidence of zero delay.\n"
        "- If several inputs visibly affect several outputs, mark coupling as significant multivariable interaction.\n"
        "- Initial opposite or unfavorable motion is non-minimum-phase or inverse-response evidence.\n"
        "- If gain or time scale changes materially with operating point, mark strong operating-point-dependent nonlinearity and large uncertainty.\n"
        "- Ask about observable behavior and available sensors/actuators, not about control-theory jargon.\n"
        "- Do not synthesize controller gains. Numeric control computation happens later in deterministic code.\n\n"
        "System description artifact:\n"
        f"{description.model_dump_json()}"
    )


def normalize_legacy_delay_assessment(value: str) -> DelayAssessment:
    """Normalize recognized legacy wording only at the structured adapter boundary."""

    normalized = " ".join(
        value.lower().replace("_", " ").replace("-", " ").split()
    )
    negative_patterns = (
        "no significant delay",
        "not significant delay",
        "negligible delay",
        "without significant delay",
        "no noticeable delay",
        "no dead time",
        "reacts instantly",
        "no delay",
    )
    positive_patterns = (
        "significant delay",
        "noticeable dead time",
        "dead time present",
        "transport delay",
        "noticeable pause",
    )
    unknown_patterns = (
        "not enough information",
        "unknown delay",
        "delay unknown",
        "dead time unknown",
        "timing has not been observed",
        "timing has not been measured",
    )

    matched_negative = any(pattern in normalized for pattern in negative_patterns)
    positive_remainder = normalized
    for pattern in negative_patterns:
        positive_remainder = positive_remainder.replace(pattern, " ")
    matched_positive = any(
        pattern in positive_remainder for pattern in positive_patterns
    )
    matched_unknown = any(pattern in normalized for pattern in unknown_patterns)
    match_count = sum((matched_negative, matched_positive, matched_unknown))
    if match_count > 1:
        raise ValueError(f"contradictory significant_delay value: {value!r}")
    if matched_negative:
        return DelayAssessment.NOT_SIGNIFICANT
    if matched_positive:
        return DelayAssessment.SIGNIFICANT
    if matched_unknown:
        return DelayAssessment.UNKNOWN
    raise ValueError(f"unrecognized significant_delay value: {value!r}")


def validate_agent_payload(payload: Any) -> StructuralDiagnosis:
    """Reject free text and parse only dictionary-like diagnostic payloads."""

    if isinstance(payload, str):
        raise ValueError("Agent output must be a dictionary or JSON object, not free text")
    if not isinstance(payload, dict):
        raise ValueError("Agent output must be a dictionary")
    normalized_payload = dict(payload)
    delay_payload = normalized_payload.get("significant_delay")
    if not isinstance(delay_payload, dict):
        raise ValueError("significant_delay must be a dictionary")
    normalized_delay = dict(delay_payload)
    if "assessment" not in normalized_delay:
        value = normalized_delay.get("value")
        if not isinstance(value, str):
            raise ValueError(
                "legacy significant_delay payload requires a string value"
            )
        normalized_delay["assessment"] = normalize_legacy_delay_assessment(value)
    normalized_payload["significant_delay"] = normalized_delay
    return StructuralDiagnosis.model_validate(normalized_payload)


class DeterministicDiagnosticAdapter:
    """Offline adapter used in tests and local demos.

    It mimics the shape of an LLM response without calling a model. The
    deterministic rules are intentionally simple and auditable.
    """

    def diagnose(self, description: SystemDescription) -> dict[str, Any]:
        from cfdc.diagnosis.engine import infer_structural_diagnosis

        return infer_structural_diagnosis(description).model_dump()


class OpenAICompatibleDiagnosticAdapter:
    """OpenAI-compatible chat-completions adapter for CFDC Stage 0.

    Configuration order:
    1. explicit constructor arguments
    2. CFDC_LLM_* environment variables
    3. CONTROL_PROJECT_LLM_* environment variables
    4. OPENAI_* environment variables
    """

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
        timeout_s: float = 60.0,
        temperature: float = 0.0,
        max_tokens: int = 1400,
    ):
        self.base_url = (
            base_url
            or os.getenv("CFDC_LLM_BASE_URL")
            or os.getenv("CONTROL_PROJECT_LLM_BASE_URL")
            or os.getenv("OPENAI_BASE_URL")
            or "https://api.openai.com/v1"
        )
        self.model = (
            model
            or os.getenv("CFDC_LLM_MODEL")
            or os.getenv("CONTROL_PROJECT_LLM_MODEL")
            or os.getenv("OPENAI_MODEL")
            or "gpt-4o-mini"
        )
        self.api_key = (
            api_key
            or os.getenv("CFDC_LLM_API_KEY")
            or os.getenv("CONTROL_PROJECT_LLM_API_KEY")
            or os.getenv("OPENAI_API_KEY")
        )
        if not self.api_key:
            raise ValueError(
                "Missing LLM API key. Set CFDC_LLM_API_KEY, "
                "CONTROL_PROJECT_LLM_API_KEY, or OPENAI_API_KEY."
            )
        self.timeout_s = timeout_s
        self.temperature = temperature
        self.max_tokens = max_tokens
        client_base_url = self.base_url.rstrip("/").removesuffix("/chat/completions")
        self._disable_thinking = (
            urlparse(client_base_url).hostname or ""
        ).lower() == "api.deepseek.com"
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=client_base_url,
            timeout=self.timeout_s,
        )

    def diagnose(self, description: SystemDescription) -> dict[str, Any]:
        request_options: dict[str, Any] = dict(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a CFDC diagnostic engine. You output strict JSON only. "
                        "You do not design controller gains."
                    ),
                },
                {"role": "user", "content": build_diagnostic_prompt(description)},
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            response_format={"type": "json_object"},
        )
        if self._disable_thinking:
            request_options["extra_body"] = {"thinking": {"type": "disabled"}}
        response = self.client.chat.completions.create(**request_options)
        choice = response.choices[0]
        content = choice.message.content
        if not isinstance(content, str):
            raise ValueError("OpenAI-compatible response content must be a string")
        if not content.strip():
            reasoning_content = getattr(choice.message, "reasoning_content", None)
            raise ValueError(
                "OpenAI-compatible response content was empty "
                f"(finish_reason={getattr(choice, 'finish_reason', None)!r}, "
                f"reasoning_content_present={bool(reasoning_content)})"
            )
        return parse_json_content(content)
