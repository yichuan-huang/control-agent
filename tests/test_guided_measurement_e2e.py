from __future__ import annotations

import pytest

from cfdc.diagnosis import continue_description_session
from cfdc.diagnosis.llm import DiagnosticAdapter
from cfdc.models import (
    MeasuredFact,
    MeasurementAssessment,
    SpecificationAssessment,
    SpecificationFact,
    SystemDescription,
)
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

_PROFILE_RESPONSE = (
    "Manual excerpt: input_change = 1 normalized_input. "
    "Manual excerpt: steady_output_change = 10 degC. "
    "Manual excerpt: response_time_s = 20 s. "
    "Manual excerpt: input_min = -2 normalized_input. "
    "Manual excerpt: input_max = 2 normalized_input. "
    "Manual excerpt: output_min = -30 degC. "
    "Manual excerpt: output_max = 80 degC."
)


class StructuredGuidedLLM(DiagnosticAdapter):
    """Complete deterministic double for every structured guided-LLM operation."""

    def diagnose(self, description):
        raise AssertionError("formal guided diagnosis must use verified evidence")

    def guide_description(self, description, guidance):
        observed_outputs = []
        actuators = []
        if "temperature" in description.text:
            observed_outputs.append(
                {"name": "temperature", "source_excerpt": "temperature"}
            )
        if "heater" in description.text:
            actuators.append({"name": "heater", "source_excerpt": "heater"})
        return {
            "guidance": [item.model_dump(mode="json") for item in guidance],
            "observed_outputs": observed_outputs,
            "actuators": actuators,
        }

    def phrase_measurement_plan(self, description, checklist, plan):
        del description, checklist
        return plan.model_dump(mode="json")

    def extract_measurements(
        self,
        description,
        measurement_plan,
        measurement_response,
        previous_assessment,
    ):
        del description, previous_assessment
        request_ids = [request.request_id for request in measurement_plan.requests]
        if measurement_response == "The log excerpt is incomplete.":
            return MeasurementAssessment(
                status="need_more",
                gaps=request_ids,
                rationale="No field-specific record excerpt was supplied.",
            ).model_dump(mode="json")
        if measurement_response == "Two saved records conflict about settling.":
            return MeasurementAssessment(
                status="conflict",
                gaps=request_ids[1:],
                conflicts=["One saved record settles while another grows."],
                conflict_request_ids=["open_loop_stability"],
                rationale="The stability evidence conflicts and other facts are unknown.",
            ).model_dump(mode="json")
        if measurement_response == "The remaining fields are unknown.":
            return MeasurementAssessment(
                status="need_more",
                facts=[
                    MeasuredFact(
                        request_id="open_loop_stability",
                        source_excerpt=_DIAGNOSTIC_FACTS["open_loop_stability"],
                        text_value=_DIAGNOSTIC_FACTS["open_loop_stability"],
                    )
                ],
                gaps=request_ids[1:],
                rationale="Only stability is known; seven fields remain unknown.",
            ).model_dump(mode="json")
        if measurement_response not in {
            "All eight record excerpts are verified.",
            _PROFILE_RESPONSE,
        }:
            raise AssertionError(
                f"unexpected measurement response: {measurement_response}"
            )
        return MeasurementAssessment(
            status="ready",
            facts=[
                MeasuredFact(
                    request_id=request.request_id,
                    source_excerpt=_DIAGNOSTIC_FACTS[request.request_id],
                    text_value=_DIAGNOSTIC_FACTS[request.request_id],
                )
                for request in measurement_plan.requests
            ],
            rationale="Every fixed diagnostic request has verified record evidence.",
        ).model_dump(mode="json")

    def select_profile(self, description, diagnosis, classification, catalog):
        del description, diagnosis, classification, catalog
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
        template = allowed_specification_templates[0]
        values = {
            "input_change": (1.0, "normalized_input"),
            "steady_output_change": (10.0, "degC"),
            "response_time_s": (20.0, "s"),
            "input_min": (-2.0, "normalized_input"),
            "input_max": (2.0, "normalized_input"),
            "output_min": (-30.0, "degC"),
            "output_max": (80.0, "degC"),
        }
        facts = [
            SpecificationFact(
                fact_id=fact_id,
                value=value,
                unit=unit,
                source_type="manufacturer_document",
                source_text=f"Manual excerpt: {fact_id} = {value:g} {unit}.",
            )
            for fact_id, (value, unit) in values.items()
        ]
        return SpecificationAssessment(
            status="ready",
            template_id=template.template_id,
            facts=facts,
            rationale="The manual excerpts provide every selected-profile fact.",
        ).model_dump(mode="json")


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
    assert len(initial.diagnostic_session.checklist) == 8
    assert len(initial.diagnostic_session.measurement_plan.requests) == 8
    assert all(
        request.safety_scope == "existing_records_only"
        for request in initial.diagnostic_session.measurement_plan.requests
    )
    rendered_plan = " ".join(
        f"{request.instruction} {request.source_hint} "
        f"{request.report_template} {request.response_hint}"
        for request in initial.diagnostic_session.measurement_plan.requests
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
    assert (
        supplemented.diagnostic_session.revision
        > initial.diagnostic_session.revision
    )
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
    expected_statuses = [
        ("The log excerpt is incomplete.", "measurement_needs_more"),
        ("Two saved records conflict about settling.", "measurement_conflict"),
        ("The remaining fields are unknown.", "measurement_needs_more"),
    ]
    for response, expected_status in expected_statuses:
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
        assert current.diagnostic_session.revision > prior.diagnostic_session.revision
        prior = current

    verified = run_cfdc_route(
        "generic",
        diagnostic_session_state=prior.diagnostic_session,
        diagnostic_adapter=adapter,
        measurement_response="All eight record excerpts are verified.",
        run_id="guided-e2e",
    )

    assert verified.status == "awaiting_profile_measurements"
    assert verified.diagnostic_session.evidence_level == "measurement_verified"
    assert verified.classification.primary_class == "class_i_first_order_lag"
    assert verified.semantic_selection.simulation_profile_id == "first_order_lag"
    assert verified.diagnostic_session.measurement_history[1].status == "conflict"
    assert verified.diagnostic_session.measurement_history[2].gaps

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
    assert (
        completed.diagnostic_session.accumulated_description.simulation_boundary_confirmation.scope
        == "software_simulation_only"
    )
    assert completed.compiled_specification_model is not None
    assert completed.controller is not None
    assert completed.controller.release_level == "candidate_unvalidated"
    assert completed.controller_validation is None

    linked_state, linked_view = link_stage5_report(
        completed.model_dump(mode="json")
    )
    assert linked_view["available"] is True
    assert linked_state["state"] == "trial_pending"
    initial_linked_revision = linked_state["revision"]
    evaluated_state, evaluated_view = run_linked_trial(
        linked_state,
        linked_view["parameter_rows"],
        expected_revision=initial_linked_revision,
    )
    with pytest.raises(ValueError, match="revision"):
        run_linked_trial(
            evaluated_state,
            evaluated_view["parameter_rows"],
            expected_revision=initial_linked_revision,
        )

    frame = output_plot_frame(decode_lab_state(evaluated_state))
    series = set(frame["series"])
    assert any("参考" in label for label in series)
    assert any("初始控制器输出" in label for label in series)
    assert any("输出下界" in label for label in series)
    assert any("输出上界" in label for label in series)
