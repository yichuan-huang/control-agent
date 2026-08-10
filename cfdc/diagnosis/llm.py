from __future__ import annotations

import json
import os
from typing import Any, Protocol
from urllib.parse import urlparse

from openai import OpenAI

from cfdc.models import (
    ArchetypeClassification,
    ControlMethodProfileCatalog,
    DescriptionGuidance,
    DescriptionGuidanceAssessment,
    DiagnosticChecklistItem,
    MeasurementAssessment,
    MeasurementPlan,
    SemanticRouteSelection,
    SpecificationAssessment,
    SpecificationTemplate,
    StructuralDiagnosis,
    SystemDescription,
)

PROMPT_VERSION = "cfdc-stage0-v5-negation-and-order-bounds"
GUIDED_ADAPTER_CAPABILITIES = (
    "guide_description",
    "phrase_measurement_plan",
    "extract_measurements",
    "select_profile",
)


def validate_guided_adapter_capabilities(adapter: object) -> None:
    """Fail closed when a guided adapter cannot perform every required operation."""

    missing = [
        name
        for name in GUIDED_ADAPTER_CAPABILITIES
        if not callable(getattr(adapter, name, None))
    ]
    if missing:
        raise ValueError(
            "guided adapter is missing required capabilities: " + ", ".join(missing)
        )


class DiagnosticAdapter(Protocol):
    """LLM-facing adapter: implementations must return structured data only."""

    def diagnose(self, description: SystemDescription) -> dict[str, Any]: ...

    def select_profile(
        self,
        description: SystemDescription,
        diagnosis: StructuralDiagnosis,
        classification: ArchetypeClassification,
        catalog: ControlMethodProfileCatalog,
    ) -> dict[str, Any]: ...

    def guide_description(
        self,
        description: SystemDescription,
        guidance: list[DescriptionGuidance],
    ) -> dict[str, Any]: ...

    def phrase_measurement_plan(
        self,
        description: SystemDescription,
        checklist: list[DiagnosticChecklistItem],
        plan: MeasurementPlan,
    ) -> dict[str, Any]: ...

    def extract_measurements(
        self,
        description: SystemDescription,
        measurement_plan: MeasurementPlan,
        measurement_response: str,
        previous_assessment: MeasurementAssessment | None,
    ) -> dict[str, Any]: ...

    def assess_specifications(
        self,
        description: SystemDescription,
        diagnosis: StructuralDiagnosis,
        classification: ArchetypeClassification,
        method_profile_id: str,
        allowed_specification_templates: list[SpecificationTemplate],
        accumulated_specification_answers: list[str],
        previous_assessment: SpecificationAssessment | None,
    ) -> dict[str, Any]: ...


class SimulationProposalAdapter(Protocol):
    """Separate Stage-6 proposal surface; legacy diagnostic fakes need not implement it."""

    def propose_model(self, context: Any) -> dict[str, Any]: ...

    def propose_model_with_messages(
        self, context: Any, messages: list[dict[str, str]]
    ) -> dict[str, Any]: ...

    def propose_gain_update(self, context: Any) -> dict[str, Any]: ...


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
        '  "open_loop_stability": {"status": "known|inferred|unknown", "value": "...", "assessment": "stable|marginal|unstable|unknown", "confidence": 0.0, "evidence": ["..."]},\n'
        '  "minimum_phase": {"status": "known|inferred|unknown", "value": "...", "assessment": "minimum_phase|nonminimum_phase|unknown", "confidence": 0.0, "evidence": ["..."]},\n'
        '  "significant_delay": {"status": "known|inferred|unknown", "value": "...", "assessment": "significant|not_significant|unknown", "confidence": 0.0, "evidence": ["..."]},\n'
        '  "relative_degree": {"status": "known|inferred|unknown", "value": "...", "assessment": "low|high|unknown", "estimated_order": 1, "confidence": 0.0, "evidence": ["..."]},\n'
        '  "controllability_observability": {"status": "known|inferred|unknown", "value": "...", "assessment": "adequate|inadequate|unknown", "confidence": 0.0, "evidence": ["..."]},\n'
        '  "nonlinearity_strength": {"status": "known|inferred|unknown", "value": "...", "assessment": "weak|static_compensable|strong_dynamic|unknown", "confidence": 0.0, "evidence": ["..."]},\n'
        '  "coupling_severity": {"status": "known|inferred|unknown", "value": "...", "assessment": "siso|weak_mimo|severe_mimo|underactuated|cascaded|unknown", "confidence": 0.0, "evidence": ["..."]},\n'
        '  "uncertainty_magnitude": {"status": "known|inferred|unknown", "value": "...", "assessment": "small|moderate|large|unknown", "confidence": 0.0, "evidence": ["..."]},\n'
        '  "clarification_questions": ["..."],\n'
        '  "complete": true\n'
        "}\n\n"
        "Rules:\n"
        "- Fill all eight diagnostic fields.\n"
        "- Every field must use exactly one assessment value listed in the schema.\n"
        "- status=unknown if and only if assessment=unknown.\n"
        "- Every resolved field needs direct or analogy-based evidence and confidence at least 0.5.\n"
        "- If any field is unknown, set complete=false and ask 2-4 plain-language clarification questions.\n"
        "- If all fields are known or reasonably inferred, set complete=true and use an empty clarification_questions list.\n"
        "- An explicitly unobserved or unknown delay must remain unknown; absence of a delay statement is not evidence of zero delay.\n"
        "- If several inputs visibly affect several outputs, mark coupling as significant multivariable interaction.\n"
        "- Initial opposite or unfavorable motion is non-minimum-phase or inverse-response evidence.\n"
        "- Read negation literally: 'does not move opposite first' is minimum-phase evidence, and 'no independent pause/transport delay' is not-significant-delay evidence.\n"
        "- 'at most two' or 'no more than two' storage/integration stages is an upper bound on relative degree, not an exact second-order oscillator model.\n"
        "- Select a second-order oscillator only when positive oscillation evidence exists, such as ringing, repeated peaks, free vibration, a restoring spring, or a natural frequency.\n"
        "- fixed thermostat hysteresis is a static-compensable switching law; it does not create a mechanical oscillatory mode or justify peak-spacing and acceleration questions.\n"
        "- If gain or time scale changes materially with operating point, mark strong operating-point-dependent nonlinearity and large uncertainty.\n"
        "- Ask about observable behavior and available sensors/actuators, not about control-theory jargon.\n"
        "- Do not synthesize controller gains. Numeric control computation happens later in deterministic code.\n\n"
        "System description artifact:\n"
        f"{description.model_dump_json()}"
    )


def build_specification_prompt(
    description: SystemDescription,
    diagnosis: StructuralDiagnosis,
    classification: ArchetypeClassification,
    method_profile_id: str,
    allowed_specification_templates: list[SpecificationTemplate],
    accumulated_specification_answers: list[str],
    previous_assessment: SpecificationAssessment | None,
) -> str:
    return (
        "You are the object-specification evidence assessor for CFDC. "
        "Return ONLY one JSON object and no markdown.\n\n"
        "Required JSON shape:\n"
        "{\n"
        '  "status": "need_more|conflict|ready",\n'
        '  "template_id": "string",\n'
        '  "facts": [{"fact_id":"string","value":0.0,"unit":"string",'
        '"source_type":"manufacturer_document|user_known_behavior|structured_answer|derived_from_declared_physics",'
        '"source_text":"verbatim excerpt or derivation summary",'
        '"derivation":null|{"rule_id":"string","expression":"string",'
        '"inputs":[{"name":"string","value":0.0,"unit":"string",'
        '"source_text":"verbatim excerpt"}],"source_excerpts":["verbatim excerpt"]},'
        '"lower_bound":null,"upper_bound":null}],\n'
        '  "missing_fact_ids": ["string"],\n'
        '  "conflicts": ["string"],\n'
        '  "questions": [{"question_id":"string","requested_fact_ids":["string"],'
        '"prompt":"plain-language object-specific question","why_needed":"string",'
        '"where_to_find":"plain-language source hint",'
        '"answer_kind":"number|matrix|structured_model","unit_hint":"string",'
        '"example":"object-specific example","answer_options":'
        '["填写已知数值","粘贴手册规格","暂时不知道","改用完整数值模型"]}],\n'
        '  "rationale": "string"\n'
        "}\n\n"
        "Rules:\n"
        "- Select only one supplied template and only its declared fact IDs.\n"
        "- Do not infer or invent any numeric value from general knowledge, defaults, or a demo fixture. Direct facts require a verbatim source_text.\n"
        "- You may propose derived_from_declared_physics facts only with one registered rule below. Include every numeric input, its stated unit, and a verbatim source excerpt. The backend will recompute the result and reject any mismatch; the expression string is audit text, not executable code.\n"
        "- Registered rules: thermal_time_constant_c_over_h produces response_time_s = 3600 * heat_capacity[Btu/degF] / heat_transfer_coefficient[Btu/(h degF)]; thermal_steady_rise_q_over_h produces steady_output_change[degF] = furnace_rate[Btu/h] / heat_transfer_coefficient[Btu/(h degF)]; thermostat_band_setpoint_plus_minus_half_width produces output_min/output_max[degF] from setpoint[degF] and hysteresis_half_width[degF]; binary_command_domain produces input_change/input_min/input_max in binary_command only when the user explicitly declares a binary or on/off command.\n"
        "- For direct facts set derivation to null. For derived facts use source_type=derived_from_declared_physics and provide derivation. Never propose an unregistered rule.\n"
        "- Qualitative words such as fast, slow, weak, or strong are not numeric facts.\n"
        "- Every numeric fact must include the unit explicitly stated by the user. Preserve that raw unit in source_text.\n"
        "- accepted_units are examples, not a finite whitelist. Device-specific command or sensor units are allowed for fields whose unit_policy is open.\n"
        "- Never guess a missing unit. If a value has no unit, leave the fact missing and ask for its unit.\n"
        "- Do not use demo fixture values or general engineering knowledge to fill gaps.\n"
        "- Do not produce controller gains or claim real-object validation.\n"
        "- Ask at most four current questions, using the actual object, sensor, and actuator names.\n"
        "- Questions must explain why the value is needed and where an ordinary user might find it.\n"
        "- Never require the user to perform repeated experiments or upload CSV files in this stage.\n"
        "- Avoid internal feature identifiers in user-facing prompt text.\n\n"
        f"description={description.model_dump_json()}\n"
        f"diagnosis={diagnosis.model_dump_json()}\n"
        f"classification={classification.model_dump_json()}\n"
        f"method_profile_id={method_profile_id}\n"
        "allowed_templates="
        f"{json.dumps([item.model_dump(mode='json') for item in allowed_specification_templates], ensure_ascii=False)}\n"
        "answer_history="
        f"{json.dumps(accumulated_specification_answers, ensure_ascii=False)}\n"
        "previous_assessment="
        f"{previous_assessment.model_dump_json() if previous_assessment else 'null'}"
    )


def validate_agent_payload(payload: Any) -> StructuralDiagnosis:
    """Reject free text and parse only dictionary-like diagnostic payloads."""

    if isinstance(payload, str):
        raise ValueError(
            "Agent output must be a dictionary or JSON object, not free text"
        )
    if not isinstance(payload, dict):
        raise ValueError("Agent output must be a dictionary")
    return StructuralDiagnosis.model_validate(payload)


class DeterministicDiagnosticAdapter:
    """Offline adapter used in tests and local demos.

    It mimics the shape of an LLM response without calling a model. The
    deterministic rules are intentionally simple and auditable.
    """

    def diagnose(self, description: SystemDescription) -> dict[str, Any]:
        from cfdc.diagnosis.engine import infer_structural_diagnosis

        return infer_structural_diagnosis(description).model_dump()

    def select_profile(self, description, diagnosis, classification, catalog):
        from cfdc.workflow.profiles import deterministic_profile_selection

        return deterministic_profile_selection(
            description, diagnosis, classification, catalog
        ).model_dump()

    def phrase_measurement_plan(self, description, checklist, plan):
        del description, checklist
        return plan.model_dump(mode="json")


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
        )
        self.model = (
            model
            or os.getenv("CFDC_LLM_MODEL")
            or os.getenv("CONTROL_PROJECT_LLM_MODEL")
            or os.getenv("OPENAI_MODEL")
        )
        self.api_key = (
            api_key
            or os.getenv("CFDC_LLM_API_KEY")
            or os.getenv("CONTROL_PROJECT_LLM_API_KEY")
            or os.getenv("OPENAI_API_KEY")
        )
        missing = [
            name
            for name, value in (
                ("base URL", self.base_url),
                ("model", self.model),
                ("API key", self.api_key),
            )
            if not value
        ]
        if missing:
            raise ValueError(
                "Missing OpenAI-compatible LLM configuration: "
                f"{', '.join(missing)}. Set CFDC_LLM_BASE_URL, "
                "CFDC_LLM_MODEL, and CFDC_LLM_API_KEY (or pass the matching "
                "--llm-* flags)."
            )
        assert self.base_url is not None
        assert self.model is not None
        assert self.api_key is not None
        self.timeout_s = timeout_s
        self.temperature = temperature
        self.max_tokens = max_tokens
        client_base_url = self.base_url.rstrip("/").removesuffix("/chat/completions")
        parsed_base_url = urlparse(client_base_url)
        if (
            parsed_base_url.scheme not in {"http", "https"}
            or not parsed_base_url.netloc
        ):
            raise ValueError(
                "LLM base URL must be an absolute http(s) OpenAI-compatible API root."
            )
        self._disable_thinking = (
            urlparse(client_base_url).hostname or ""
        ).lower() == "api.deepseek.com"
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=client_base_url,
            timeout=self.timeout_s,
        )

    def _stage6_json_completion(
        self,
        *,
        messages: list[dict[str, str]],
        max_tokens: int,
    ) -> dict[str, Any]:
        options: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"},
        }
        if self._disable_thinking:
            options["extra_body"] = {"thinking": {"type": "disabled"}}
        response = self.client.chat.completions.create(**options)
        content = response.choices[0].message.content
        if not isinstance(content, str) or not content.strip():
            raise ValueError("Stage-6 proposal returned empty content")
        return parse_json_content(content)

    def propose_model(self, context: Any) -> dict[str, Any]:
        from cfdc.lab.llm import build_model_proposal_messages
        from cfdc.lab.model_discovery_llm import (
            ModelDiscoveryContext,
            build_model_discovery_messages,
        )
        from cfdc.lab.model_questions import load_model_question_examples

        messages = (
            build_model_discovery_messages(context, load_model_question_examples())
            if isinstance(context, ModelDiscoveryContext)
            else build_model_proposal_messages(context)
        )

        return self._stage6_json_completion(
            messages=messages,
            max_tokens=min(max(self.max_tokens, 1400), 2600),
        )

    def propose_model_with_messages(
        self,
        context: Any,
        messages: list[dict[str, str]],
    ) -> dict[str, Any]:
        """Send the exact prevalidated prompt recorded by the caller."""

        from cfdc.lab.model_discovery_llm import ModelDiscoveryContext

        if not isinstance(context, ModelDiscoveryContext):
            raise TypeError(
                "prebuilt model-discovery messages require a typed "
                "ModelDiscoveryContext"
            )
        return self._stage6_json_completion(
            messages=messages,
            max_tokens=min(max(self.max_tokens, 1400), 2600),
        )

    def propose_gain_update(self, context: Any) -> dict[str, Any]:
        from cfdc.lab.llm import build_gain_proposal_messages

        return self._stage6_json_completion(
            messages=build_gain_proposal_messages(context),
            max_tokens=min(self.max_tokens, 900),
        )

    def diagnose(self, description: SystemDescription) -> dict[str, Any]:
        request_options: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a CFDC diagnostic engine. You output strict JSON only. "
                        "You do not design controller gains."
                    ),
                },
                {"role": "user", "content": build_diagnostic_prompt(description)},
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "response_format": {"type": "json_object"},
        }
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

    def phrase_measurement_plan(self, description, checklist, plan):
        prompt = (
            "Rephrase no behavior and add no instructions. Return ONLY the supplied "
            "record-only measurement plan as one JSON object with every field present. "
            "The requests must remain the fixed eight requests, in order. Only the "
            "closed source lookup and observation-reporting template strings already "
            "present in the plan may be used. Never request a physical command, new "
            "experiment, amplitude, or duration.\n\n"
            f"description={description.model_dump_json()}\n"
            f"checklist={json.dumps([item.model_dump(mode='json') for item in checklist], ensure_ascii=False)}\n"
            f"plan={plan.model_dump_json()}"
        )
        options: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You return strict JSON for a record-only measurement plan.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": self.temperature,
            "max_tokens": min(max(self.max_tokens, 1400), 2400),
            "response_format": {"type": "json_object"},
        }
        if self._disable_thinking:
            options["extra_body"] = {"thinking": {"type": "disabled"}}
        response = self.client.chat.completions.create(**options)
        content = response.choices[0].message.content
        if not isinstance(content, str) or not content.strip():
            raise ValueError("measurement-plan phrasing returned empty content")
        return MeasurementPlan.model_validate(parse_json_content(content)).model_dump(
            mode="json"
        )

    def guide_description(self, description, guidance):
        prompt = (
            "Return one strict JSON object containing exactly the supplied eight "
            "record/manual guidance entries in their fixed diagnostic-field order, "
            "plus observed output and actuator names explicitly present in the "
            "description. Every extracted name requires a non-empty verbatim source "
            "excerpt copied from the description. Do not infer an unstated signal. "
            "Guidance must remain record/manual-report-only and must never prescribe "
            "a physical command, amplitude, or duration.\n\n"
            "Required shape: {\"guidance\":[DescriptionGuidance x8],"
            "\"observed_outputs\":[{\"name\":\"string\","
            "\"source_excerpt\":\"verbatim string\"}],"
            "\"actuators\":[{\"name\":\"string\","
            "\"source_excerpt\":\"verbatim string\"}]}.\n"
            f"description={description.model_dump_json()}\n"
            f"guidance={json.dumps([item.model_dump(mode='json') for item in guidance], ensure_ascii=False)}"
        )
        options: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You extract description signals and return safe record-only "
                        "guidance as strict JSON."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": self.temperature,
            "max_tokens": min(max(self.max_tokens, 1400), 2400),
            "response_format": {"type": "json_object"},
        }
        if self._disable_thinking:
            options["extra_body"] = {"thinking": {"type": "disabled"}}
        response = self.client.chat.completions.create(**options)
        content = response.choices[0].message.content
        if not isinstance(content, str) or not content.strip():
            raise ValueError("description guidance returned empty content")
        return DescriptionGuidanceAssessment.model_validate(
            parse_json_content(content)
        ).model_dump(mode="json")

    def extract_measurements(
        self,
        description,
        measurement_plan,
        measurement_response,
        previous_assessment,
    ):
        prompt = (
            "Extract evidence from the user's response into one strict JSON object. "
            "Do not invent facts. Account for every active request exactly once as a "
            "fact, gap, or mapped conflict. Numeric facts require the unit stated by "
            "the user. Unknown values are gaps. Preserve short source excerpts. "
            "If previous_assessment is ready, an unmentioned diagnostic field means "
            "carry-forward with no change: copy its previous fact exactly instead of "
            "turning omission into a gap or retraction. Only emit a changed fact or "
            "conflict when the current user_response explicitly supplies the supporting "
            "source excerpt. Profile-specific numeric facts are not diagnostic changes.\n\n"
            "Required shape: {\"status\":\"need_more|conflict|ready\","
            "\"facts\":[{\"request_id\":\"string\",\"source_excerpt\":\"string\","
            "\"numeric_value\":null,\"unit\":null,\"text_value\":\"string\"}],"
            "\"gaps\":[\"diagnostic_field_id\"],\"conflicts\":[\"string\"],"
            "\"conflict_request_ids\":[\"request_id\"],\"rationale\":\"string\"}.\n"
            f"description={description.model_dump_json()}\n"
            f"measurement_plan={measurement_plan.model_dump_json()}\n"
            f"previous_assessment={previous_assessment.model_dump_json() if previous_assessment else 'null'}\n"
            f"user_response={json.dumps(measurement_response, ensure_ascii=False)}"
        )
        options: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You extract auditable record evidence into strict JSON. "
                        "You never invent facts or prescribe hardware actions."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": self.temperature,
            "max_tokens": min(max(self.max_tokens, 1400), 2400),
            "response_format": {"type": "json_object"},
        }
        if self._disable_thinking:
            options["extra_body"] = {"thinking": {"type": "disabled"}}
        response = self.client.chat.completions.create(**options)
        content = response.choices[0].message.content
        if not isinstance(content, str) or not content.strip():
            raise ValueError("measurement extraction returned empty content")
        return MeasurementAssessment.model_validate(
            parse_json_content(content)
        ).model_dump(mode="json")

    def select_profile(self, description, diagnosis, classification, catalog):
        compatible = [
            profile.model_dump()
            for profile in catalog.profiles
            if str(profile.compatible_class) == str(classification.primary_class)
        ]
        prompt = (
            "Select exactly one CFDC simulation profile from the supplied catalog. "
            "Return ONLY one JSON object. Do not include markdown, prose, or code fences.\n\n"
            "The JSON object must match this shape and these field types exactly:\n"
            "{\n"
            '  "simulation_profile_id": "string",\n'
            '  "feature_bundle_id": "string",\n'
            '  "selected_feature_ids": ["string"],\n'
            '  "confidence": 0.0,\n'
            '  "evidence": ["string"],\n'
            '  "rationale": "string"\n'
            "}\n\n"
            "Rules:\n"
            "- Include all six keys exactly once. Do not add any other keys.\n"
            "- simulation_profile_id, feature_bundle_id, and rationale must be non-empty JSON strings.\n"
            "- selected_feature_ids must be a non-empty JSON array of strings and must exactly equal the selected profile's required_feature_ids; never invent or add features.\n"
            "- confidence must be a JSON number from 0.0 through 1.0.\n"
            "- evidence must be a non-empty JSON array of strings, even when there is only one evidence item; never return evidence as a single string.\n"
            "- Do not use null for any field.\n\n"
            f"description={description.model_dump_json()}\n"
            f"diagnosis={diagnosis.model_dump_json()}\n"
            f"classification={classification.model_dump_json()}\n"
            f"compatible_profiles={json.dumps(compatible)}"
        )
        options: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You select from a closed CFDC profile catalog and output "
                        "strict JSON only. Follow the exact JSON schema and field "
                        "types in the user prompt."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": self.temperature,
            "max_tokens": min(self.max_tokens, 800),
            "response_format": {"type": "json_object"},
        }
        if self._disable_thinking:
            options["extra_body"] = {"thinking": {"type": "disabled"}}
        response = self.client.chat.completions.create(**options)
        content = response.choices[0].message.content
        if not isinstance(content, str) or not content.strip():
            raise ValueError("semantic profile selection returned empty content")
        return SemanticRouteSelection.model_validate(
            parse_json_content(content)
        ).model_dump()

    def assess_specifications(
        self,
        description,
        diagnosis,
        classification,
        method_profile_id,
        allowed_specification_templates,
        accumulated_specification_answers,
        previous_assessment,
    ):
        prompt = build_specification_prompt(
            description,
            diagnosis,
            classification,
            method_profile_id,
            allowed_specification_templates,
            accumulated_specification_answers,
            previous_assessment,
        )
        options: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You extract auditable object specifications into strict JSON. "
                        "You never invent numbers and never design controller gains."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": self.temperature,
            "max_tokens": min(max(self.max_tokens, 1400), 2400),
            "response_format": {"type": "json_object"},
        }
        if self._disable_thinking:
            options["extra_body"] = {"thinking": {"type": "disabled"}}
        response = self.client.chat.completions.create(**options)
        content = response.choices[0].message.content
        if not isinstance(content, str) or not content.strip():
            raise ValueError("specification assessment returned empty content")
        payload = parse_json_content(content)
        if not isinstance(payload, dict):
            raise ValueError("specification assessment must return one JSON object")
        return payload
