from __future__ import annotations

import math
from copy import deepcopy

import pytest

from cfdc.diagnosis import continue_description_session
from cfdc.diagnosis.llm import DiagnosticAdapter
from cfdc.models import SystemDescription
from cfdc.runtime import run_cfdc_route
from cfdc.web.linked_tuning_presentation import output_plot_frame
from cfdc.web.linked_tuning_service import (
    decode_lab_state,
    link_stage5_report,
    run_linked_trial,
)

_DIAGNOSTIC_FACTS = {
    "open_loop_stability": "settles or remains bounded",
    "minimum_phase": (
        "starts in its final direction rather than moving the opposite way first"
    ),
    "significant_delay": (
        "begins within one sample without a separate silent interval"
    ),
    "relative_degree": "one or two dominant storage or integration processes",
    "controllability_observability": (
        "all relevant motion can be reconstructed from these synchronized records"
    ),
    "nonlinearity_strength": (
        "small positive and negative trials are smooth, reversible, and nearly proportional"
    ),
    "coupling_severity": (
        "one main physical route from actuation to the measured motion"
    ),
    "uncertainty_magnitude": (
        "change the response rate and final level by a modest amount"
    ),
}

_FIELD_IDS = [
    "open_loop_stability",
    "minimum_phase",
    "significant_delay",
    "relative_degree",
    "controllability_observability",
    "nonlinearity_strength",
    "coupling_severity",
    "uncertainty_magnitude",
]

_DIAGNOSTIC_RESPONSE = "\n".join(
    f"{request_id}: {source_excerpt}"
    for request_id, source_excerpt in _DIAGNOSTIC_FACTS.items()
)
_CONFLICT_RESPONSE = "One saved record settles while another grows."
_PARTIAL_RESPONSE = (
    f"{_DIAGNOSTIC_FACTS['open_loop_stability']}. "
    "The remaining fields are unknown."
)

_GUIDANCE_PAYLOADS = [
    {
        "diagnostic_field_id": "open_loop_stability",
        "prompt": (
            "For Open-loop stability, review an existing record or manual report and "
            "describe whether the unforced recorded output settles, grows, or is "
            "unavailable. If no such record exists, say unknown."
        ),
        "why_needed": (
            "This keeps the open-loop stability diagnostic field evidence-backed."
        ),
        "response": "unknown",
        "accepted_sources": ["existing_record", "manual_report"],
    },
    {
        "diagnostic_field_id": "minimum_phase",
        "prompt": (
            "For Minimum-phase behavior, review an existing record or manual report "
            "and describe whether an existing response record initially moves opposite "
            "to its eventual direction. If no such record exists, say unknown."
        ),
        "why_needed": (
            "This keeps the minimum-phase behavior diagnostic field evidence-backed."
        ),
        "response": "unknown",
        "accepted_sources": ["existing_record", "manual_report"],
    },
    {
        "diagnostic_field_id": "significant_delay",
        "prompt": (
            "For Significant delay, review an existing record or manual report and "
            "describe the delay already reported between an input record and its "
            "observed output response. If no such record exists, say unknown."
        ),
        "why_needed": (
            "This keeps the significant delay diagnostic field evidence-backed."
        ),
        "response": "unknown",
        "accepted_sources": ["existing_record", "manual_report"],
    },
    {
        "diagnostic_field_id": "relative_degree",
        "prompt": (
            "For Relative degree, review an existing record or manual report and "
            "describe the earliest response shape already reported in an input/output "
            "record. If no such record exists, say unknown."
        ),
        "why_needed": "This keeps the relative degree diagnostic field evidence-backed.",
        "response": "unknown",
        "accepted_sources": ["existing_record", "manual_report"],
    },
    {
        "diagnostic_field_id": "controllability_observability",
        "prompt": (
            "For Controllability and observability, review an existing record or manual "
            "report and describe whether existing records or a manual report identify "
            "an input that affects each reported output. If no such record exists, say "
            "unknown."
        ),
        "why_needed": (
            "This keeps the controllability and observability diagnostic field "
            "evidence-backed."
        ),
        "response": "unknown",
        "accepted_sources": ["existing_record", "manual_report"],
    },
    {
        "diagnostic_field_id": "nonlinearity_strength",
        "prompt": (
            "For Nonlinearity strength, review an existing record or manual report and "
            "describe whether existing records report materially different behavior "
            "across operating conditions. If no such record exists, say unknown."
        ),
        "why_needed": (
            "This keeps the nonlinearity strength diagnostic field evidence-backed."
        ),
        "response": "unknown",
        "accepted_sources": ["existing_record", "manual_report"],
    },
    {
        "diagnostic_field_id": "coupling_severity",
        "prompt": (
            "For Coupling severity, review an existing record or manual report and "
            "describe whether existing records or a manual report show one input "
            "affecting multiple outputs. If no such record exists, say unknown."
        ),
        "why_needed": (
            "This keeps the coupling severity diagnostic field evidence-backed."
        ),
        "response": "unknown",
        "accepted_sources": ["existing_record", "manual_report"],
    },
    {
        "diagnostic_field_id": "uncertainty_magnitude",
        "prompt": (
            "For Uncertainty magnitude, review an existing record or manual report and "
            "describe the repeatability or uncertainty already reported in existing "
            "records or a manual report. If no such record exists, say unknown."
        ),
        "why_needed": (
            "This keeps the uncertainty magnitude diagnostic field evidence-backed."
        ),
        "response": "unknown",
        "accepted_sources": ["existing_record", "manual_report"],
    },
]

_FIELD_TITLES = [
    "Open-loop stability",
    "Minimum-phase behavior",
    "Significant delay",
    "Relative degree",
    "Controllability and observability",
    "Nonlinearity strength",
    "Coupling severity",
    "Uncertainty magnitude",
]

_MEASUREMENT_PLAN_PAYLOAD = {
    "requests": [
        {
            "request_id": "open_loop_stability",
            "diagnostic_field_id": "open_loop_stability",
            "title": "Open-loop stability",
            "safety_scope": "existing_records_only",
            "instruction": "Review an existing record.",
            "source_hint": "Review an existing record.",
            "report_template": "Report the source excerpt and recorded observation.",
            "response_hint": "Report the source excerpt and recorded observation.",
            "unit_hint": None,
        },
        {
            "request_id": "minimum_phase",
            "diagnostic_field_id": "minimum_phase",
            "title": "Minimum-phase behavior",
            "safety_scope": "existing_records_only",
            "instruction": "Review an existing record.",
            "source_hint": "Review an existing record.",
            "report_template": "Report the source excerpt and recorded observation.",
            "response_hint": "Report the source excerpt and recorded observation.",
            "unit_hint": None,
        },
        {
            "request_id": "significant_delay",
            "diagnostic_field_id": "significant_delay",
            "title": "Significant delay",
            "safety_scope": "existing_records_only",
            "instruction": "Review an existing record.",
            "source_hint": "Review an existing record.",
            "report_template": "Report the source excerpt and recorded observation.",
            "response_hint": "Report the source excerpt and recorded observation.",
            "unit_hint": "s",
        },
        {
            "request_id": "relative_degree",
            "diagnostic_field_id": "relative_degree",
            "title": "Relative degree",
            "safety_scope": "existing_records_only",
            "instruction": "Review an existing record.",
            "source_hint": "Review an existing record.",
            "report_template": "Report the source excerpt and recorded observation.",
            "response_hint": "Report the source excerpt and recorded observation.",
            "unit_hint": None,
        },
        {
            "request_id": "controllability_observability",
            "diagnostic_field_id": "controllability_observability",
            "title": "Controllability and observability",
            "safety_scope": "existing_records_only",
            "instruction": "Review an existing record.",
            "source_hint": "Review an existing record.",
            "report_template": "Report the source excerpt and recorded observation.",
            "response_hint": "Report the source excerpt and recorded observation.",
            "unit_hint": None,
        },
        {
            "request_id": "nonlinearity_strength",
            "diagnostic_field_id": "nonlinearity_strength",
            "title": "Nonlinearity strength",
            "safety_scope": "existing_records_only",
            "instruction": "Review an existing record.",
            "source_hint": "Review an existing record.",
            "report_template": "Report the source excerpt and recorded observation.",
            "response_hint": "Report the source excerpt and recorded observation.",
            "unit_hint": None,
        },
        {
            "request_id": "coupling_severity",
            "diagnostic_field_id": "coupling_severity",
            "title": "Coupling severity",
            "safety_scope": "existing_records_only",
            "instruction": "Review an existing record.",
            "source_hint": "Review an existing record.",
            "report_template": "Report the source excerpt and recorded observation.",
            "response_hint": "Report the source excerpt and recorded observation.",
            "unit_hint": None,
        },
        {
            "request_id": "uncertainty_magnitude",
            "diagnostic_field_id": "uncertainty_magnitude",
            "title": "Uncertainty magnitude",
            "safety_scope": "existing_records_only",
            "instruction": "Review an existing record.",
            "source_hint": "Review an existing record.",
            "report_template": "Report the source excerpt and recorded observation.",
            "response_hint": "Report the source excerpt and recorded observation.",
            "unit_hint": None,
        },
    ],
    "rationale": (
        "The plan collects only existing-record or manual-report evidence; it does "
        "not ask for a new physical action."
    ),
}

_PROFILE_RESPONSE = (
    "Manual excerpt: input_change = 1 normalized_input. "
    "Manual excerpt: steady_output_change = 10 degC. "
    "Manual excerpt: response_time_s = 20 s. "
    "Manual excerpt: input_min = -2 normalized_input. "
    "Manual excerpt: input_max = 2 normalized_input. "
    "Manual excerpt: output_min = -30 degC. "
    "Manual excerpt: output_max = 80 degC."
)

_SPECIFICATION_FACT_PAYLOADS = [
    {
        "fact_id": "input_change",
        "value": 1.0,
        "unit": "normalized_input",
        "source_type": "manufacturer_document",
        "source_text": "Manual excerpt: input_change = 1 normalized_input.",
        "derivation": None,
        "lower_bound": None,
        "upper_bound": None,
    },
    {
        "fact_id": "steady_output_change",
        "value": 10.0,
        "unit": "degC",
        "source_type": "manufacturer_document",
        "source_text": "Manual excerpt: steady_output_change = 10 degC.",
        "derivation": None,
        "lower_bound": None,
        "upper_bound": None,
    },
    {
        "fact_id": "response_time_s",
        "value": 20.0,
        "unit": "s",
        "source_type": "manufacturer_document",
        "source_text": "Manual excerpt: response_time_s = 20 s.",
        "derivation": None,
        "lower_bound": None,
        "upper_bound": None,
    },
    {
        "fact_id": "input_min",
        "value": -2.0,
        "unit": "normalized_input",
        "source_type": "manufacturer_document",
        "source_text": "Manual excerpt: input_min = -2 normalized_input.",
        "derivation": None,
        "lower_bound": None,
        "upper_bound": None,
    },
    {
        "fact_id": "input_max",
        "value": 2.0,
        "unit": "normalized_input",
        "source_type": "manufacturer_document",
        "source_text": "Manual excerpt: input_max = 2 normalized_input.",
        "derivation": None,
        "lower_bound": None,
        "upper_bound": None,
    },
    {
        "fact_id": "output_min",
        "value": -30.0,
        "unit": "degC",
        "source_type": "manufacturer_document",
        "source_text": "Manual excerpt: output_min = -30 degC.",
        "derivation": None,
        "lower_bound": None,
        "upper_bound": None,
    },
    {
        "fact_id": "output_max",
        "value": 80.0,
        "unit": "degC",
        "source_type": "manufacturer_document",
        "source_text": "Manual excerpt: output_max = 80 degC.",
        "derivation": None,
        "lower_bound": None,
        "upper_bound": None,
    },
]


class StructuredGuidedLLM(DiagnosticAdapter):
    """Complete deterministic double for every structured guided-LLM operation."""

    def __init__(self):
        self.calls: list[str] = []

    def diagnose(self, description):
        raise AssertionError("formal guided diagnosis must use verified evidence")

    def guide_description(self, description, guidance):
        assert [item.model_dump(mode="json") for item in guidance] == (
            _GUIDANCE_PAYLOADS
        )
        self.calls.append("guide")
        observed_outputs = []
        actuators = []
        if "temperature" in description.text:
            observed_outputs.append(
                {"name": "temperature", "source_excerpt": "temperature"}
            )
        if "heater" in description.text:
            actuators.append({"name": "heater", "source_excerpt": "heater"})
        return {
            "guidance": deepcopy(_GUIDANCE_PAYLOADS),
            "observed_outputs": observed_outputs,
            "actuators": actuators,
        }

    def phrase_measurement_plan(self, description, checklist, plan):
        del description
        assert [item.diagnostic_field_id for item in checklist] == _FIELD_IDS
        assert [item.label for item in checklist] == _FIELD_TITLES
        assert plan.model_dump(mode="json") == _MEASUREMENT_PLAN_PAYLOAD
        self.calls.append("phrase")
        return deepcopy(_MEASUREMENT_PLAN_PAYLOAD)

    def extract_measurements(
        self,
        description,
        measurement_plan,
        measurement_response,
        previous_assessment,
    ):
        del description
        assert measurement_plan.model_dump(mode="json") == _MEASUREMENT_PLAN_PAYLOAD
        if measurement_response == "The log excerpt is incomplete.":
            assert previous_assessment is None
            self.calls.append("extract:incomplete")
            return {
                "status": "need_more",
                "facts": [],
                "gaps": list(_FIELD_IDS),
                "conflicts": [],
                "conflict_request_ids": [],
                "rationale": "No field-specific record excerpt was supplied.",
            }
        if measurement_response == _CONFLICT_RESPONSE:
            assert previous_assessment.status == "need_more"
            self.calls.append("extract:conflict")
            return {
                "status": "conflict",
                "facts": [],
                "gaps": list(_FIELD_IDS[1:]),
                "conflicts": ["One saved record settles while another grows."],
                "conflict_request_ids": ["open_loop_stability"],
                "rationale": (
                    "The stability evidence conflicts and other facts are unknown."
                ),
            }
        if measurement_response == _PARTIAL_RESPONSE:
            assert previous_assessment.status == "conflict"
            self.calls.append("extract:unknown")
            return {
                "status": "need_more",
                "facts": [
                    {
                        "request_id": "open_loop_stability",
                        "source_excerpt": _DIAGNOSTIC_FACTS[
                            "open_loop_stability"
                        ],
                        "numeric_value": None,
                        "unit": None,
                        "text_value": _DIAGNOSTIC_FACTS[
                            "open_loop_stability"
                        ],
                    }
                ],
                "gaps": list(_FIELD_IDS[1:]),
                "conflicts": [],
                "conflict_request_ids": [],
                "rationale": "Only stability is known; seven fields remain unknown.",
            }
        if measurement_response not in {
            _DIAGNOSTIC_RESPONSE,
            _PROFILE_RESPONSE,
        }:
            raise AssertionError(
                f"unexpected measurement response: {measurement_response}"
            )
        if measurement_response == _PROFILE_RESPONSE:
            assert previous_assessment.status == "ready"
            self.calls.append("extract:profile")
            return previous_assessment.model_dump(mode="json")
        else:
            assert previous_assessment.status == "need_more"
            self.calls.append("extract:ready")
        return {
            "status": "ready",
            "facts": [
                {
                    "request_id": request_id,
                    "source_excerpt": _DIAGNOSTIC_FACTS[request_id],
                    "numeric_value": None,
                    "unit": None,
                    "text_value": _DIAGNOSTIC_FACTS[request_id],
                }
                for request_id in _FIELD_IDS
            ],
            "gaps": [],
            "conflicts": [],
            "conflict_request_ids": [],
            "rationale": (
                "Every fixed diagnostic request has verified record evidence."
            ),
        }

    def select_profile(self, description, diagnosis, classification, catalog):
        del description, diagnosis
        expected = next(
            item for item in catalog.profiles if item.profile_id == "first_order_lag"
        )
        assert classification.primary_class == "class_i_first_order_lag"
        assert expected.feature_bundle_id == "class_i_minimal"
        assert expected.required_feature_ids == ["static_gain", "time_constant"]
        self.calls.append("select")
        return {
            "simulation_profile_id": "first_order_lag",
            "feature_bundle_id": "class_i_minimal",
            "selected_feature_ids": ["static_gain", "time_constant"],
            "confidence": 0.95,
            "evidence": ["verified eight-field record assessment"],
            "rationale": "Select the compatible closed-catalog first-order Profile.",
        }

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
        del description, diagnosis, classification, previous_assessment
        assert method_profile_id == "first_order_lag"
        assert accumulated_specification_answers[-1] == _PROFILE_RESPONSE
        templates = {
            template.template_id: template
            for template in allowed_specification_templates
        }
        assert set(templates) == {"spec_first_order_lag"}
        assert templates["spec_first_order_lag"].method_profile_id == (
            "first_order_lag"
        )
        self.calls.append("assess")
        return {
            "status": "ready",
            "template_id": "spec_first_order_lag",
            "facts": deepcopy(_SPECIFICATION_FACT_PAYLOADS),
            "missing_fact_ids": [],
            "conflicts": [],
            "rejected_facts": [],
            "questions": [],
            "rationale": (
                "The manual excerpts provide every selected-profile fact."
            ),
            "no_progress": False,
        }


def test_guided_description_to_linked_first_trial_is_evidence_gated_end_to_end():
    adapter = StructuredGuidedLLM()
    initial = run_cfdc_route(
        "generic",
        description=SystemDescription(
            text="A heater influences a measured temperature in an industrial vessel."
        ),
        diagnostic_adapter=adapter,
        run_id="guided-e2e",
    )

    assert initial.status == "awaiting_measurements"
    assert initial.classification is None
    assert initial.semantic_selection is None
    assert initial.diagnostic_session.schema_version == "4.0"
    assert initial.diagnostic_session.revision == 0
    assert [
        item.diagnostic_field_id for item in initial.diagnostic_session.checklist
    ] == _FIELD_IDS
    assert [
        item.guidance.model_dump(mode="json")
        for item in initial.diagnostic_session.checklist
    ] == _GUIDANCE_PAYLOADS
    assert initial.diagnostic_session.measurement_plan.model_dump(
        mode="json"
    ) == _MEASUREMENT_PLAN_PAYLOAD
    assert {
        request.safety_scope
        for request in initial.diagnostic_session.measurement_plan.requests
    } == {"existing_records_only"}
    assert all(
        request.instruction
        in {
            "Review an existing record.",
            "Review a manual report.",
            "Read an existing record.",
            "Read a manual report.",
            "Find an existing record.",
            "Find a manual report.",
            "Compare existing records.",
            "Compare manual reports.",
        }
        for request in initial.diagnostic_session.measurement_plan.requests
    )
    assert all(
        "existing record" in item.guidance.prompt.lower()
        and "manual report" in item.guidance.prompt.lower()
        and item.guidance.accepted_sources == [
            "existing_record",
            "manual_report",
        ]
        for item in initial.diagnostic_session.checklist
    )
    rendered_plan = " ".join(
        [
            *(
                f"{item.guidance.prompt} {item.guidance.why_needed}"
                for item in initial.diagnostic_session.checklist
            ),
            *(
                f"{request.instruction} {request.source_hint} "
                f"{request.report_template} {request.response_hint}"
                for request in initial.diagnostic_session.measurement_plan.requests
            ),
            initial.diagnostic_session.measurement_plan.rationale,
        ]
    ).lower()
    assert all(
        forbidden not in rendered_plan
        for forbidden in ("amplitude", "duration", "apply", "command", "hardware")
    )

    supplemented = run_cfdc_route(
        "generic",
        diagnostic_session_state=initial.diagnostic_session,
        diagnostic_adapter=adapter,
        supplemental_description=(
            "An existing manual identifies heater power as the input and temperature "
            "as the recorded output."
        ),
        run_id="guided-e2e",
    )
    assert supplemented.diagnostic_session.revision == 1
    assert supplemented.diagnostic_session.description_turn_count == 1
    assert supplemented.classification is None
    assert supplemented.semantic_selection is None
    with pytest.raises(ValueError, match="stale diagnostic session revision"):
        continue_description_session(
            supplemented.diagnostic_session,
            "Another existing manual excerpt.",
            expected_revision=initial.diagnostic_session.revision,
            diagnostic_adapter=adapter,
        )

    prior = supplemented
    expected_rounds = [
        (
            "The log excerpt is incomplete.",
            "measurement_needs_more",
            2,
            list(_FIELD_IDS),
        ),
        (
            _CONFLICT_RESPONSE,
            "measurement_conflict",
            3,
            list(_FIELD_IDS[1:]),
        ),
        (
            _PARTIAL_RESPONSE,
            "measurement_needs_more",
            4,
            list(_FIELD_IDS[1:]),
        ),
    ]
    for response, expected_status, expected_revision, expected_gaps in expected_rounds:
        current = run_cfdc_route(
            "generic",
            diagnostic_session_state=prior.diagnostic_session,
            diagnostic_adapter=adapter,
            measurement_response=response,
            run_id="guided-e2e",
        )
        assert current.status == expected_status
        assert current.classification is None
        assert current.semantic_selection is None
        assert current.diagnostic_session.revision == expected_revision
        assert current.diagnostic_session.measurement_round_count == (
            expected_revision - 1
        )
        assert current.diagnostic_session.measurement_assessment.gaps == expected_gaps
        prior = current

    verified = run_cfdc_route(
        "generic",
        diagnostic_session_state=prior.diagnostic_session,
        diagnostic_adapter=adapter,
        measurement_response=_DIAGNOSTIC_RESPONSE,
        run_id="guided-e2e",
    )

    assert verified.status == "awaiting_profile_measurements"
    assert verified.diagnostic_session.revision == 6
    assert verified.diagnostic_session.evidence_level == "measurement_verified"
    assert verified.classification.primary_class == "class_i_first_order_lag"
    assert verified.semantic_selection.simulation_profile_id == "first_order_lag"
    assert verified.diagnostic_session.measurement_round_count == 4
    assert [
        assessment.status
        for assessment in verified.diagnostic_session.measurement_history
    ] == ["need_more", "conflict", "need_more", "ready"]
    assert [
        assessment.gaps
        for assessment in verified.diagnostic_session.measurement_history
    ] == [list(_FIELD_IDS), list(_FIELD_IDS[1:]), list(_FIELD_IDS[1:]), []]
    assert [
        assessment.conflict_request_ids
        for assessment in verified.diagnostic_session.measurement_history
    ] == [[], ["open_loop_stability"], [], []]
    assert [
        assessment.conflicts
        for assessment in verified.diagnostic_session.measurement_history
    ] == [[], ["One saved record settles while another grows."], [], []]
    assert verified.diagnostic_session.measurement_response_history[-1] == (
        _DIAGNOSTIC_RESPONSE
    )
    assert all(
        fact.source_excerpt in _DIAGNOSTIC_RESPONSE
        for fact in verified.diagnostic_session.measurement_assessment.facts
    )
    assert adapter.calls == [
        "guide",
        "phrase",
        "guide",
        "phrase",
        "extract:incomplete",
        "extract:conflict",
        "extract:unknown",
        "extract:ready",
        "select",
    ]

    completed = run_cfdc_route(
        "generic",
        diagnostic_session_state=verified.diagnostic_session,
        diagnostic_adapter=adapter,
        measurement_response=_PROFILE_RESPONSE,
        simulation_bounds_confirmed=True,
        run_id="guided-e2e",
    )

    assert completed.status == "candidate_unvalidated"
    assert completed.evidence_boundary == "declared_specification_model_only"
    assert completed.diagnostic_session.revision == 7
    assert completed.diagnostic_session.measurement_round_count == 4
    assert completed.diagnostic_session.profile_measurement_round_count == 1
    assert [
        assessment.status
        for assessment in completed.diagnostic_session.measurement_history
    ] == ["need_more", "conflict", "need_more", "ready", "ready"]
    assert [
        assessment.gaps
        for assessment in completed.diagnostic_session.measurement_history
    ] == [
        list(_FIELD_IDS),
        list(_FIELD_IDS[1:]),
        list(_FIELD_IDS[1:]),
        [],
        [],
    ]
    assert [
        assessment.conflict_request_ids
        for assessment in completed.diagnostic_session.measurement_history
    ] == [[], ["open_loop_stability"], [], [], []]
    assert [
        assessment.conflicts
        for assessment in completed.diagnostic_session.measurement_history
    ] == [[], ["One saved record settles while another grows."], [], [], []]
    assert [
        (
            fact.request_id,
            fact.source_excerpt,
            fact.text_value,
            fact.numeric_value,
            fact.unit,
        )
        for fact in completed.diagnostic_session.measurement_history[-1].facts
    ] == [
        (request_id, text, text, None, None)
        for request_id, text in _DIAGNOSTIC_FACTS.items()
    ]
    assert completed.diagnostic_session.specification_answer_history == [
        _PROFILE_RESPONSE
    ]
    assert completed.diagnostic_session.measurement_response_history[-1] == (
        _PROFILE_RESPONSE
    )
    assert all(
        diagnostic_excerpt not in _PROFILE_RESPONSE
        for diagnostic_excerpt in _DIAGNOSTIC_FACTS.values()
    )
    assert (
        completed.diagnostic_session.accumulated_description.simulation_boundary_confirmation.scope
        == "software_simulation_only"
    )
    assert completed.compiled_specification_model is not None
    compiled = completed.compiled_specification_model
    assert compiled.template_id == "spec_first_order_lag"
    assert compiled.model.kind == "transfer_function"
    assert compiled.model.numerator == [10.0]
    assert compiled.model.denominator == [20.0, 1.0]
    assert compiled.model.time_domain == "continuous"
    assert compiled.model.sample_time_s is None
    assert compiled.model.input_delay_s == 0.0
    assert compiled.model.input_signal_id == "heater"
    assert compiled.model.output_signal_id == "temperature"
    assert compiled.model.input_units == "normalized_input"
    assert compiled.model.output_units == "degC"
    assert compiled.safety_bounds == {
        "input_min": -2.0,
        "input_max": 2.0,
        "output_min": -30.0,
        "output_max": 80.0,
        "input_range": 4.0,
        "max_abs_control": 2.0,
        "per_input_limit": 2.0,
        "state_range": 110.0,
        "max_abs_position": 80.0,
    }
    assert completed.controller is not None
    controller = completed.controller
    assert controller.plant_id == compiled.plant_id
    assert controller.method_profile_id == "first_order_lag"
    assert controller.architecture == "detuned_PI"
    assert controller.gains == {
        "kp": 0.008295377335188023,
        "ki": 7.541252122898203e-05,
        "integral_time": 110.0,
    }
    assert controller.tunable_gain_names == ["kp", "ki"]
    assert controller.release_level == "candidate_unvalidated"
    assert controller.status == "ready_for_conservative_trial"
    assert completed.controller_validation is None
    assert adapter.calls == [
        "guide",
        "phrase",
        "guide",
        "phrase",
        "extract:incomplete",
        "extract:conflict",
        "extract:unknown",
        "extract:ready",
        "select",
        "extract:profile",
        "assess",
    ]

    linked_state, linked_view = link_stage5_report(
        completed.model_dump(mode="json")
    )
    assert linked_view["available"] is True
    assert linked_state["state"] == "trial_pending"
    initial_linked_revision = linked_state["revision"]
    assert initial_linked_revision == 1
    evaluated_state, evaluated_view = run_linked_trial(
        linked_state,
        linked_view["parameter_rows"],
        expected_revision=initial_linked_revision,
    )
    evaluated_session = decode_lab_state(evaluated_state)
    assert evaluated_state["revision"] == initial_linked_revision + 2
    assert evaluated_state["state"] == "stable"
    assert len(evaluated_session.trials) == 1
    trial = evaluated_session.trials[0]
    assert trial.iteration == 1
    assert trial.creation_source == "initial"
    assert trial.controller.kind == "pi"
    assert trial.controller.kp == 0.008295377335188023
    assert trial.controller.ki == 7.541252122898203e-05
    assert trial.rolled_back is False
    assert trial.hard_violation is False
    assert trial.stability.status == "stable"
    assert trial.stability.analysis_domain == "continuous"
    assert (
        trial.stability.pole_analysis_method
        == "exact_continuous_interconnection"
    )
    assert trial.stability.trajectory_finite is True
    assert trial.stability.trajectory_bounded is True
    assert trial.stability.saturation_fraction == 0.0
    assert trial.stability.hard_failure is False
    assert trial.stability.violations == []
    assert trial.stability.evidence == [
        (
            "actual sampled rollout-map spectral radius=0.99985888; this numerical "
            "boundedness check is independent of reference-tracking performance"
        ),
        (
            "Continuous poles were computed from the exact nominal linear "
            "interconnection."
        ),
        (
            "largest closed-loop pole real part=-0.000705553028; stable threshold is "
            "strictly below -1e-6"
        ),
        "rollout remained finite",
        "rollout stayed inside all declared hard state/output bounds",
        "actuator saturation fraction=0; stable trials require at most 0.1",
        (
            "tail error-envelope contraction=0.126181; recorded for iteration "
            "diagnostics and not used as a linear performance gate"
        ),
    ]
    with pytest.raises(ValueError, match="revision"):
        run_linked_trial(
            evaluated_state,
            evaluated_view["parameter_rows"],
            expected_revision=initial_linked_revision,
        )

    frame = output_plot_frame(evaluated_session)
    assert not frame.empty
    assert len(frame) == 256
    assert all(math.isfinite(value) for value in frame["time_s"])
    assert all(math.isfinite(value) for value in frame["value"])
    series = set(frame["series"])
    assert series == {
        "scenario-1 · 参考 · temperature",
        "scenario-1 · 初始控制器输出 · temperature",
        "scenario-1 · 输出下界 · temperature",
        "scenario-1 · 输出上界 · temperature",
    }
    reference = frame[frame["series"] == "scenario-1 · 参考 · temperature"]
    initial_output = frame[
        frame["series"] == "scenario-1 · 初始控制器输出 · temperature"
    ]
    lower_bound = frame[
        frame["series"] == "scenario-1 · 输出下界 · temperature"
    ]
    upper_bound = frame[
        frame["series"] == "scenario-1 · 输出上界 · temperature"
    ]
    assert reference.iloc[0][["time_s", "value"]].tolist() == [0.0, 11.0]
    assert reference.iloc[-1][["time_s", "value"]].tolist() == [120.0, 11.0]
    assert set(reference["value"]) == {11.0}
    assert initial_output.iloc[0][["time_s", "value"]].tolist() == [0.0, 0.0]
    assert set(lower_bound["value"]) == {-30.0}
    assert set(upper_bound["value"]) == {80.0}
