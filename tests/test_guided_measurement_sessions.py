import math

import pytest
from pydantic import ValidationError

from cfdc.diagnosis import (
    DeterministicDiagnosticAdapter,
    build_diagnostic_checklist,
    continue_description_session,
    continue_diagnostic_session,
    migrate_diagnostic_session_payload,
    reduce_measurement_history_to_diagnosis,
    start_diagnostic_session,
    submit_measurement_assessment,
    submit_profile_measurement_assessment,
    validate_grounded_measurement_assessment,
)
from cfdc.diagnosis.engine import DiagnosticEngine
from cfdc.models import (
    DiagnosticSessionState,
    MeasuredFact,
    MeasurementAssessment,
    MeasurementRequest,
    SemanticRouteSelection,
    SystemDescription,
)
from cfdc.runtime import run_cfdc_route
from cfdc.specifications import (
    build_initial_specification_assessment,
    specification_template_for_profile,
)
from cfdc.workflow import (
    apply_profile_to_classification,
    default_control_method_profile_catalog,
    validate_semantic_selection,
)


def _description() -> SystemDescription:
    return SystemDescription(
        text="A temperature output is recorded after a heater command.",
        observed_outputs=["temperature"],
        actuators=["heater"],
    )


_THERMOSTAT_DESCRIPTION = "这是一个由恒温器监测房间温度并控制电加热器通断的住宅供暖系统"


class _UnknownDescriptionGuidanceAdapter:
    def guide_description(self, description, guidance):
        del description
        return {
            "guidance": [
                {**item.model_dump(mode="json"), "response": "unknown"}
                for item in guidance
            ],
            "observed_outputs": [{"name": "房间温度", "source_excerpt": "房间温度"}],
            "actuators": [{"name": "电加热器", "source_excerpt": "电加热器"}],
        }

    def phrase_measurement_plan(self, description, checklist, plan):
        del description, checklist
        return plan.model_dump(mode="json")


_GROUNDED_FACTS = {
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


def _raw_response(assessment: MeasurementAssessment) -> str:
    parts = []
    for fact in assessment.facts:
        parts.append(fact.source_excerpt)
        if fact.text_value is not None:
            parts.append(fact.text_value)
    parts.extend(assessment.conflicts)
    return "\n".join(parts)


def test_measurement_contracts_are_strict_and_numeric_facts_require_units():
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        MeasurementRequest(
            request_id="open_loop_stability",
            diagnostic_field_id="open_loop_stability",
            title="Open-loop stability",
            instruction="Review existing records and report what they show.",
            unexpected=True,
        )
    with pytest.raises(ValidationError, match="unit"):
        MeasuredFact(
            request_id="open_loop_stability",
            source_excerpt="The log reports a peak of 2.",
            numeric_value=2.0,
        )
    with pytest.raises(ValidationError):
        MeasuredFact(
            request_id="open_loop_stability",
            source_excerpt="The log reports a non-finite number.",
            numeric_value=math.inf,
            unit="degC",
        )
    with pytest.raises(
        ValidationError, match="unknown values belong in assessment gaps"
    ):
        MeasuredFact(
            request_id="open_loop_stability",
            source_excerpt="The record has no stability finding.",
            text_value="unknown",
        )
    with pytest.raises(ValidationError, match="source_excerpt must be non-empty"):
        MeasuredFact(
            request_id="open_loop_stability",
            source_excerpt="   ",
            text_value="settled",
        )
    for unsafe_instruction in (
        "Review an existing record, then set the heater actuator.",
        "Review an existing record and apply a command to the valve.",
        "Review an existing record before moving physical hardware.",
    ):
        with pytest.raises(ValidationError, match="source lookup text"):
            MeasurementRequest(
                request_id="open_loop_stability",
                diagnostic_field_id="open_loop_stability",
                title="Open-loop stability",
                instruction=unsafe_instruction,
            )


@pytest.mark.parametrize(
    "unsafe_text",
    [
        "Review an existing record, then set this actuator to zero",
        "Review an existing record, then apply 10 V to the heater",
        "Review an existing record and set this actuator to zero",
        "Review an existing record\nthen apply 10 V to the heater",
    ],
)
def test_measurement_request_text_cannot_carry_operator_steps(unsafe_text):
    with pytest.raises(ValidationError, match="source lookup text"):
        MeasurementRequest(
            request_id="open_loop_stability",
            diagnostic_field_id="open_loop_stability",
            title="Open-loop stability",
            instruction=unsafe_text,
            source_hint=unsafe_text,
        )


@pytest.mark.parametrize(
    ("field", "unsafe_text"),
    [
        ("report_template", "Report the observation, then set this actuator to zero"),
        ("response_hint", "Describe the observation and apply 10 V to the heater"),
    ],
)
def test_every_measurement_request_text_field_uses_a_nonexecutable_template(
    field, unsafe_text
):
    with pytest.raises(ValidationError, match="observation-reporting template"):
        MeasurementRequest(
            request_id="open_loop_stability",
            diagnostic_field_id="open_loop_stability",
            title="Open-loop stability",
            **{field: unsafe_text},
        )


def test_checklist_has_the_eight_fixed_diagnostic_field_ids():
    checklist = build_diagnostic_checklist(_description())

    assert [item.diagnostic_field_id for item in checklist] == [
        "open_loop_stability",
        "minimum_phase",
        "significant_delay",
        "relative_degree",
        "controllability_observability",
        "nonlinearity_strength",
        "coupling_severity",
        "uncertainty_magnitude",
    ]
    assert all("existing" in item.guidance.prompt.lower() for item in checklist)


def test_thermostat_description_unknown_guidance_stays_on_all_eight_gaps():
    state = start_diagnostic_session(
        SystemDescription(text=_THERMOSTAT_DESCRIPTION),
        diagnostic_adapter=_UnknownDescriptionGuidanceAdapter(),
    )

    assert state.status == "collecting_description"
    assert len(state.checklist) == 8
    assert {item.status for item in state.checklist} == {"unknown"}
    assert state.accumulated_description.observed_outputs == ["房间温度"]
    assert state.accumulated_description.actuators == ["电加热器"]


def test_v4_session_rejects_a_checklist_that_loses_a_required_field_identity():
    state = start_diagnostic_session(_description())
    payload = state.model_dump(mode="json")
    payload["checklist"][-1]["diagnostic_field_id"] = "open_loop_stability"

    with pytest.raises(ValidationError, match="fixed eight-field checklist"):
        DiagnosticSessionState.model_validate(payload)


def test_v4_session_gates_classification_until_measurements_are_verified():
    state = start_diagnostic_session(_description())

    assert state.schema_version == "4.0"
    assert state.evidence_level == "description_only"
    assert state.classification is None
    assert state.semantic_selection is None
    assert state.status == "awaiting_measurements"
    assert state.measurement_plan is not None


def test_description_turn_is_revisioned_and_stops_after_eight_rounds():
    state = start_diagnostic_session(SystemDescription(text="I have a machine."))
    for index in range(8):
        state = continue_description_session(
            state,
            f"Existing record {index} names the observed output.",
            expected_revision=index,
        )

    assert state.description_turn_count == 8
    assert state.revision == 8
    assert state.status == "refused"
    assert state.refusal_reason == "maximum_description_turns_reached"
    with pytest.raises(ValueError, match="stale diagnostic session revision"):
        continue_description_session(state, "Another record.", expected_revision=0)


def test_measurement_assessment_preserves_conflicts_and_only_verified_evidence_advances():
    state = start_diagnostic_session(_description())
    request = state.measurement_plan.requests[0]
    assessment = MeasurementAssessment(
        status="conflict",
        conflicts=["Log B reports an unbounded response for the same record."],
        conflict_request_ids=[request.request_id],
        gaps=[item.diagnostic_field_id for item in state.checklist[1:]],
    )

    updated = submit_measurement_assessment(
        state,
        assessment,
        raw_response=_raw_response(assessment),
        expected_revision=state.revision,
    )

    assert updated.status == "measurement_conflict"
    assert updated.evidence_level == "description_only"
    assert updated.measurement_assessment == assessment
    assert updated.classification is None


def test_complete_record_assessment_sets_the_measurement_verified_gate_only():
    state = start_diagnostic_session(_description())
    assessment = MeasurementAssessment(
        status="ready",
        facts=[
            MeasuredFact(
                request_id=request.request_id,
                source_excerpt=_GROUNDED_FACTS[request.request_id],
                text_value=_GROUNDED_FACTS[request.request_id],
            )
            for request in state.measurement_plan.requests
        ],
    )

    updated = submit_measurement_assessment(
        state,
        assessment,
        raw_response=_raw_response(assessment),
        expected_revision=state.revision,
    )

    assert updated.status == "measurement_verified"
    assert updated.evidence_level == "measurement_verified"
    assert updated.classification is None
    assert updated.semantic_selection is None


def test_measurement_rounds_refuse_after_eight_incomplete_assessments():
    state = start_diagnostic_session(_description())
    assessment = MeasurementAssessment(
        status="need_more",
        gaps=[item.diagnostic_field_id for item in state.checklist],
    )

    for _ in range(8):
        state = submit_measurement_assessment(
            state,
            assessment,
            raw_response="No existing record is available for these fields.",
            expected_revision=state.revision,
        )

    assert state.measurement_round_count == 8
    assert state.status == "refused"
    assert state.refusal_reason == "maximum_measurement_rounds_reached"


def test_diagnostic_rounds_accumulate_exact_grounded_facts_from_need_more():
    state = start_diagnostic_session(_description())
    first_text = _GROUNDED_FACTS["open_loop_stability"]
    first = MeasurementAssessment(
        status="need_more",
        facts=[
            MeasuredFact(
                request_id="open_loop_stability",
                source_excerpt=first_text,
                text_value=first_text,
            )
        ],
        gaps=[item.diagnostic_field_id for item in state.checklist[1:]],
    )
    after_first = submit_measurement_assessment(
        state,
        first,
        raw_response=first_text,
        expected_revision=state.revision,
    )
    second_text = _GROUNDED_FACTS["minimum_phase"]
    second = MeasurementAssessment(
        status="need_more",
        facts=[
            first.facts[0],
            MeasuredFact(
                request_id="minimum_phase",
                source_excerpt=second_text,
                text_value=second_text,
            ),
        ],
        gaps=[
            item.diagnostic_field_id
            for item in state.checklist
            if item.diagnostic_field_id not in {"open_loop_stability", "minimum_phase"}
        ],
    )

    accumulated = submit_measurement_assessment(
        after_first,
        second,
        raw_response=second_text,
        expected_revision=after_first.revision,
    )

    assert accumulated.status == "measurement_needs_more"
    assert [fact.request_id for fact in accumulated.measurement_assessment.facts] == [
        "open_loop_stability",
        "minimum_phase",
    ]
    assert "open_loop_stability" not in accumulated.measurement_assessment.gaps
    assert "minimum_phase" not in accumulated.measurement_assessment.gaps
    assert accumulated.measurement_response_history == [first_text, second_text]
    restored = migrate_diagnostic_session_payload(accumulated.model_dump(mode="json"))
    assert restored.measurement_assessment == accumulated.measurement_assessment


def test_later_diagnostic_gap_explicitly_clears_a_previously_grounded_fact():
    state = start_diagnostic_session(_description())
    stability_text = _GROUNDED_FACTS["open_loop_stability"]
    first = MeasurementAssessment(
        status="need_more",
        facts=[
            MeasuredFact(
                request_id="open_loop_stability",
                source_excerpt=stability_text,
                text_value=stability_text,
            )
        ],
        gaps=[item.diagnostic_field_id for item in state.checklist[1:]],
    )
    after_first = submit_measurement_assessment(
        state,
        first,
        raw_response=stability_text,
        expected_revision=state.revision,
    )
    phase_text = _GROUNDED_FACTS["minimum_phase"]
    explicit_gap = MeasurementAssessment(
        status="need_more",
        facts=[
            MeasuredFact(
                request_id="minimum_phase",
                source_excerpt=phase_text,
                text_value=phase_text,
            )
        ],
        gaps=[
            item.diagnostic_field_id
            for item in state.checklist
            if item.diagnostic_field_id != "minimum_phase"
        ],
    )

    cleared = submit_measurement_assessment(
        after_first,
        explicit_gap,
        raw_response=(
            "The newer record marks open-loop stability unknown. " + phase_text
        ),
        expected_revision=after_first.revision,
    )
    reduced = reduce_measurement_history_to_diagnosis(
        cleared.measurement_plan,
        cleared.measurement_history,
    )

    assert cleared.status == "measurement_needs_more"
    assert cleared.measurement_assessment == explicit_gap
    assert all(
        fact.request_id != "open_loop_stability"
        for fact in cleared.measurement_assessment.facts
    )
    assert "open_loop_stability" in cleared.measurement_assessment.gaps
    assert reduced.open_loop_stability.status == "unknown"
    assert reduced.complete is False


def test_later_diagnostic_round_rejects_changed_fact_not_grounded_in_current_raw():
    state = start_diagnostic_session(_description())
    first_text = _GROUNDED_FACTS["open_loop_stability"]
    first = MeasurementAssessment(
        status="need_more",
        facts=[
            MeasuredFact(
                request_id="open_loop_stability",
                source_excerpt=first_text,
                text_value=first_text,
            )
        ],
        gaps=[item.diagnostic_field_id for item in state.checklist[1:]],
    )
    after_first = submit_measurement_assessment(
        state,
        first,
        raw_response=first_text,
        expected_revision=state.revision,
    )
    second_text = _GROUNDED_FACTS["minimum_phase"]
    changed = MeasurementAssessment(
        status="need_more",
        facts=[
            MeasuredFact(
                request_id="open_loop_stability",
                source_excerpt="the output grows without bound",
                text_value="the output grows without bound",
            ),
            MeasuredFact(
                request_id="minimum_phase",
                source_excerpt=second_text,
                text_value=second_text,
            ),
        ],
        gaps=[item.diagnostic_field_id for item in state.checklist[2:]],
    )

    with pytest.raises(ValueError, match="source_excerpt"):
        submit_measurement_assessment(
            after_first,
            changed,
            raw_response=second_text,
            expected_revision=after_first.revision,
        )

    assert after_first.classification is None
    assert after_first.measurement_round_count == 1


def test_measurement_assessment_rejects_unknown_request_ids_and_v3_payloads():
    state = start_diagnostic_session(_description())
    invalid = MeasurementAssessment(
        status="need_more",
        facts=[
            MeasuredFact(
                request_id="not-in-plan",
                source_excerpt="A record says something.",
                text_value="something",
            )
        ],
        gaps=[item.diagnostic_field_id for item in state.checklist],
    )
    with pytest.raises(ValueError, match="unknown measurement request"):
        submit_measurement_assessment(
            state,
            invalid,
            raw_response=_raw_response(invalid),
            expected_revision=state.revision,
        )

    payload = state.model_dump(mode="json")
    payload["schema_version"] = "3.0"
    with pytest.raises(ValidationError, match="4.0"):
        DiagnosticSessionState.model_validate(payload)


def _ready_assessment(state):
    return MeasurementAssessment(
        status="ready",
        facts=[
            MeasuredFact(
                request_id=request.request_id,
                source_excerpt=_GROUNDED_FACTS[request.request_id],
                text_value=_GROUNDED_FACTS[request.request_id],
            )
            for request in state.measurement_plan.requests
        ],
    )


def test_session_model_rejects_classification_before_measurement_verification():
    state = start_diagnostic_session(_description())
    report = run_cfdc_route("generic", description=_description())
    payload = state.model_dump(mode="json")
    payload["classification"] = report.classification.model_dump(mode="json")
    payload["semantic_selection"] = report.semantic_selection.model_dump(mode="json")

    with pytest.raises(ValidationError, match="before measurement verification"):
        DiagnosticSessionState.model_validate(payload)


def test_measurement_verified_transition_cannot_smuggle_a_profile_selection():
    state = start_diagnostic_session(_description())
    verified = submit_measurement_assessment(
        state,
        _ready_assessment(state),
        raw_response=_raw_response(_ready_assessment(state)),
        expected_revision=state.revision,
    )
    report = run_cfdc_route("generic", description=_description())
    payload = verified.model_dump(mode="json")
    payload["classification"] = report.classification.model_dump(mode="json")
    payload["semantic_selection"] = report.semantic_selection.model_dump(mode="json")

    with pytest.raises(ValidationError, match="must remain absent"):
        DiagnosticSessionState.model_validate(payload)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("no_plan", "measurement_verified status requires a measurement plan"),
        ("partial_plan", "exact fixed eight-field measurement plan"),
        ("missing_fact", "must account for every active measurement request"),
        ("unknown_fact", "unknown measurement request id"),
    ],
)
def test_direct_v4_payload_validation_cannot_forge_measurement_verified(
    mutation, message
):
    state = start_diagnostic_session(_description())
    verified = submit_measurement_assessment(
        state,
        _ready_assessment(state),
        raw_response=_raw_response(_ready_assessment(state)),
        expected_revision=state.revision,
    )
    payload = verified.model_dump(mode="json")
    if mutation == "no_plan":
        payload["measurement_plan"] = None
    elif mutation == "partial_plan":
        payload["measurement_plan"]["requests"] = payload["measurement_plan"][
            "requests"
        ][:-1]
    elif mutation == "missing_fact":
        payload["measurement_assessment"]["facts"] = payload["measurement_assessment"][
            "facts"
        ][:-1]
    else:
        payload["measurement_assessment"]["facts"][0]["request_id"] = "unknown"

    with pytest.raises(ValidationError, match=message):
        DiagnosticSessionState.model_validate(payload)


def test_assessments_must_account_for_every_active_request():
    state = start_diagnostic_session(_description())
    incomplete = MeasurementAssessment(
        status="need_more",
        gaps=[state.checklist[0].diagnostic_field_id],
    )
    with pytest.raises(
        ValueError, match="must account for every active measurement request"
    ):
        submit_measurement_assessment(
            state,
            incomplete,
            raw_response="Only one record was checked.",
            expected_revision=state.revision,
        )

    incomplete_conflict = MeasurementAssessment(
        status="conflict",
        conflicts=["Two records disagree."],
        conflict_request_ids=[state.measurement_plan.requests[0].request_id],
        gaps=[state.checklist[1].diagnostic_field_id],
    )
    with pytest.raises(
        ValueError, match="must account for every active measurement request"
    ):
        submit_measurement_assessment(
            state,
            incomplete_conflict,
            raw_response=_raw_response(incomplete_conflict),
            expected_revision=state.revision,
        )


@pytest.mark.parametrize("status", ["need_more", "conflict"])
def test_direct_nonverified_payload_assessments_cannot_omit_active_requests(status):
    state = start_diagnostic_session(_description())
    if status == "need_more":
        assessment = MeasurementAssessment(
            status=status,
            gaps=[state.checklist[0].diagnostic_field_id],
        )
    else:
        assessment = MeasurementAssessment(
            status=status,
            conflicts=["Two existing records disagree."],
            conflict_request_ids=[state.measurement_plan.requests[0].request_id],
            gaps=[state.checklist[1].diagnostic_field_id],
        )
    payload = state.model_dump(mode="json")
    payload["measurement_assessment"] = assessment.model_dump(mode="json")
    payload["measurement_history"] = [assessment.model_dump(mode="json")]
    payload["measurement_response_history"] = [
        "The current response accounts for only part of the plan."
    ]
    payload["measurement_round_count"] = 1
    payload["status"] = (
        "measurement_conflict" if status == "conflict" else "awaiting_measurements"
    )

    with pytest.raises(
        ValidationError, match="must account for every active measurement request"
    ):
        DiagnosticSessionState.model_validate(payload)


def _complete_gap_assessment(state):
    return MeasurementAssessment(
        status="need_more",
        gaps=[item.diagnostic_field_id for item in state.checklist],
    )


def _complete_conflict_assessment(state):
    return MeasurementAssessment(
        status="conflict",
        conflicts=["Two existing records disagree."],
        conflict_request_ids=[state.measurement_plan.requests[0].request_id],
        gaps=[item.diagnostic_field_id for item in state.checklist[1:]],
    )


def test_direct_v4_payload_rejects_incomplete_measurement_history_entry():
    state = start_diagnostic_session(_description())
    incomplete = MeasurementAssessment(
        status="need_more",
        gaps=[state.checklist[0].diagnostic_field_id],
    )
    payload = state.model_dump(mode="json")
    payload["measurement_history"] = [incomplete.model_dump(mode="json")]
    payload["measurement_response_history"] = ["One field was reviewed."]
    payload["measurement_round_count"] = 1

    with pytest.raises(
        ValidationError, match="must account for every active measurement request"
    ):
        DiagnosticSessionState.model_validate(payload)


def test_direct_v4_payload_rejects_current_assessment_that_is_not_last_history_entry():
    state = start_diagnostic_session(_description())
    prior = _complete_gap_assessment(state)
    current = _complete_conflict_assessment(state)
    payload = state.model_dump(mode="json")
    payload["measurement_history"] = [prior.model_dump(mode="json")]
    payload["measurement_response_history"] = ["No records were available."]
    payload["measurement_round_count"] = 1
    payload["measurement_assessment"] = current.model_dump(mode="json")
    payload["status"] = "measurement_conflict"

    with pytest.raises(ValidationError, match="final measurement history entry"):
        DiagnosticSessionState.model_validate(payload)


def test_direct_v4_payload_accepts_empty_or_complete_auditable_measurement_history():
    state = start_diagnostic_session(_description())
    restored_empty = DiagnosticSessionState.model_validate(
        state.model_dump(mode="json")
    )
    assert restored_empty.measurement_history == []
    assert restored_empty.measurement_assessment is None

    first = _complete_gap_assessment(state)
    current = _complete_conflict_assessment(state)
    payload = state.model_dump(mode="json")
    payload["measurement_history"] = [
        first.model_dump(mode="json"),
        current.model_dump(mode="json"),
    ]
    payload["measurement_response_history"] = [
        "No records were available.",
        "Two existing records disagree.",
    ]
    payload["measurement_round_count"] = 2
    payload["measurement_assessment"] = current.model_dump(mode="json")
    payload["status"] = "measurement_conflict"

    restored = DiagnosticSessionState.model_validate(payload)
    assert restored.measurement_history == [first, current]
    assert restored.measurement_response_history == [
        "No records were available.",
        "Two existing records disagree.",
    ]
    assert restored.measurement_assessment == current


def _grounded_ready_assessment(state) -> MeasurementAssessment:
    return MeasurementAssessment(
        status="ready",
        facts=[
            MeasuredFact(
                request_id=request.request_id,
                source_excerpt=_GROUNDED_FACTS[request.request_id],
                text_value=_GROUNDED_FACTS[request.request_id],
            )
            for request in state.measurement_plan.requests
        ],
    )


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("excerpt", "source_excerpt"),
        ("text", "text_value"),
        ("numeric", "numeric_value"),
        ("unit", "unit"),
    ],
)
def test_new_or_changed_measurement_fact_must_be_grounded_in_current_response(
    mutation, message
):
    state = start_diagnostic_session(_description())
    assessment = _grounded_ready_assessment(state)
    raw_response = _raw_response(assessment)
    facts = [fact.model_copy(deep=True) for fact in assessment.facts]
    if mutation == "excerpt":
        facts[0] = facts[0].model_copy(
            update={"source_excerpt": "an invented source excerpt"}
        )
    elif mutation == "text":
        facts[0] = facts[0].model_copy(update={"text_value": "invented conclusion"})
    elif mutation == "numeric":
        facts[0] = facts[0].model_copy(
            update={
                "source_excerpt": "the record reports 2.5 seconds",
                "text_value": None,
                "numeric_value": 9.5,
                "unit": "seconds",
            }
        )
        raw_response += "\nthe record reports 2.5 seconds"
    else:
        facts[0] = facts[0].model_copy(
            update={
                "source_excerpt": "the record reports 2.5 milliseconds",
                "text_value": None,
                "numeric_value": 2.5,
                "unit": "seconds",
            }
        )
        raw_response += "\nthe record reports 2.5 milliseconds"
    mutated = assessment.model_copy(update={"facts": facts})

    with pytest.raises(ValueError, match=message):
        submit_measurement_assessment(
            state,
            mutated,
            raw_response=raw_response,
            expected_revision=state.revision,
        )


def test_grounding_normalizes_only_whitespace_and_rejects_invented_conflicts():
    state = start_diagnostic_session(_description())
    request = state.measurement_plan.requests[0]
    fact = MeasuredFact(
        request_id=request.request_id,
        source_excerpt="the record says the output settles",
        text_value="output settles",
    )
    assessment = MeasurementAssessment(
        status="need_more",
        facts=[fact],
        gaps=[item.diagnostic_field_id for item in state.checklist[1:]],
    )
    validate_grounded_measurement_assessment(
        state.measurement_plan,
        assessment,
        "the record says\n\t the output settles",
    )

    conflict = MeasurementAssessment(
        status="conflict",
        conflicts=["Record B says the output grows."],
        conflict_request_ids=[request.request_id],
        gaps=[item.diagnostic_field_id for item in state.checklist[1:]],
    )
    with pytest.raises(ValueError, match="conflict"):
        validate_grounded_measurement_assessment(
            state.measurement_plan,
            conflict,
            "Record A says the output settles.",
        )


def test_submit_measurement_rejects_non_string_raw_response_without_attribute_error():
    state = start_diagnostic_session(_description())
    assessment = _grounded_ready_assessment(state)

    with pytest.raises(ValueError, match="raw measurement response must be a string"):
        submit_measurement_assessment(
            state,
            assessment,
            raw_response=123,
            expected_revision=state.revision,
        )


def test_exact_ready_fact_carry_forward_is_unchanged_not_new_evidence():
    state = start_diagnostic_session(_description())
    previous = _grounded_ready_assessment(state)

    validate_grounded_measurement_assessment(
        state.measurement_plan,
        previous,
        "This Profile reply contains no new diagnostic claim.",
        previous_assessment=previous,
    )
    changed = previous.model_copy(
        update={
            "facts": [
                previous.facts[0].model_copy(update={"text_value": "output grows"}),
                *previous.facts[1:],
            ]
        }
    )
    with pytest.raises(ValueError, match="text_value"):
        validate_grounded_measurement_assessment(
            state.measurement_plan,
            changed,
            previous.facts[0].source_excerpt,
            previous_assessment=previous,
        )


def test_v4_schema_requires_aligned_nonempty_raw_measurement_responses():
    state = start_diagnostic_session(_description())
    assessment = _grounded_ready_assessment(state)
    verified = submit_measurement_assessment(
        state,
        assessment,
        raw_response=_raw_response(assessment),
        expected_revision=state.revision,
    )
    payload = verified.model_dump(mode="json")
    payload["measurement_response_history"] = []

    with pytest.raises(ValidationError, match="response history"):
        DiagnosticSessionState.model_validate(payload)


def _post_measurement_payload(
    state: DiagnosticSessionState | None = None,
) -> dict:
    state = state or start_diagnostic_session(_description())
    assessment = _grounded_ready_assessment(state)
    verified = submit_measurement_assessment(
        state,
        assessment,
        raw_response=_raw_response(assessment),
        expected_revision=state.revision,
    )
    diagnosis = reduce_measurement_history_to_diagnosis(
        verified.measurement_plan,
        verified.measurement_history,
    )
    assert diagnosis.complete
    raw_classification = DiagnosticEngine().classify(diagnosis, None)
    catalog = default_control_method_profile_catalog()
    selection = SemanticRouteSelection.model_validate(
        DeterministicDiagnosticAdapter().select_profile(
            verified.accumulated_description,
            diagnosis,
            raw_classification,
            catalog,
        )
    )
    profile = validate_semantic_selection(selection, raw_classification, catalog)
    classification = apply_profile_to_classification(raw_classification, profile)
    template = specification_template_for_profile(selection.simulation_profile_id)
    initial_assessment = build_initial_specification_assessment(
        verified.accumulated_description, template
    )
    payload = verified.model_dump(mode="json")
    payload.update(
        {
            "revision": verified.revision + 1,
            "current_diagnosis": diagnosis.model_dump(mode="json"),
            "classification": classification.model_dump(mode="json"),
            "semantic_selection": selection.model_dump(mode="json"),
            "specification_templates": [template.model_dump(mode="json")],
            "specification_assessment": initial_assessment.model_dump(mode="json"),
            "status": "awaiting_profile_measurements",
        }
    )
    return payload


def test_description_supplement_discards_rendered_measurement_evidence_text():
    prior_supplement = "A prior manual names temperature as the recorded output."
    described = continue_description_session(
        start_diagnostic_session(_description()),
        prior_supplement,
        expected_revision=0,
    )
    post_measurement = DiagnosticSessionState.model_validate(
        _post_measurement_payload(described)
    )
    assert "Validated diagnostic measurement evidence:" in (
        post_measurement.accumulated_description.text
    )
    supplement = "An existing manual lists the heater and temperature signal names."

    restarted = continue_description_session(
        post_measurement,
        supplement,
        expected_revision=post_measurement.revision,
    )

    assert restarted.accumulated_description.text == (
        f"{post_measurement.initial_description.text}\n\n"
        f"Supplemental description: {prior_supplement}\n\n"
        f"Supplemental description: {supplement}"
    )
    assert "Validated diagnostic measurement evidence:" not in (
        restarted.accumulated_description.text
    )
    assert _GROUNDED_FACTS["open_loop_stability"] not in (
        restarted.accumulated_description.text
    )
    diagnosis_payload = restarted.current_diagnosis.model_dump_json()
    assert all(
        source_excerpt not in diagnosis_payload
        for source_excerpt in _GROUNDED_FACTS.values()
    )
    assert restarted.status == "awaiting_measurements"
    assert restarted.evidence_level == "description_only"
    assert restarted.measurement_history == []
    assert restarted.measurement_response_history == []
    assert restarted.classification is None
    assert restarted.semantic_selection is None


def test_migration_rejects_forged_postmeasurement_state_without_grounded_history():
    payload = _post_measurement_payload()
    payload["measurement_history"] = []
    payload["measurement_response_history"] = []
    payload["measurement_round_count"] = 0
    payload["measurement_assessment"] = None

    with pytest.raises((ValidationError, ValueError), match="grounded|history|ready"):
        migrate_diagnostic_session_payload(payload)


def test_postmeasurement_state_requires_a_ready_diagnostic_round_before_profile_rounds():
    payload = _post_measurement_payload()
    payload["measurement_round_count"] = 0
    payload["profile_measurement_round_count"] = 1

    with pytest.raises((ValidationError, ValueError), match="diagnostic.*ready"):
        migrate_diagnostic_session_payload(payload)


def test_migration_rejects_invented_evidence_in_persisted_history():
    payload = _post_measurement_payload()
    payload["measurement_history"][-1]["facts"][0]["source_excerpt"] = (
        "an invented persisted excerpt"
    )

    with pytest.raises(ValueError, match="source_excerpt"):
        migrate_diagnostic_session_payload(payload)


def test_migration_recomputes_diagnosis_but_requires_fresh_profile_selection():
    payload = _post_measurement_payload()
    expected = migrate_diagnostic_session_payload(payload)
    payload["current_diagnosis"]["open_loop_stability"]["assessment"] = "unstable"
    payload["classification"]["control_architecture"] = "injected architecture"

    restored = migrate_diagnostic_session_payload(payload)

    assert restored.current_diagnosis == expected.current_diagnosis
    assert restored.status == "measurement_verified"
    assert restored.classification is None
    assert restored.semantic_selection is None


def test_migration_discards_incompatible_or_invented_profile_selection():
    payload = _post_measurement_payload()
    payload["semantic_selection"].update(
        {
            "simulation_profile_id": "mimo_2x2_coupled",
            "feature_bundle_id": "class_v_matrix_minimal",
            "selected_feature_ids": [
                "local_gain_matrix",
                "local_time_constant",
                "pairing_indicator",
            ],
        }
    )

    restored = migrate_diagnostic_session_payload(payload)

    assert restored.status == "measurement_verified"
    assert restored.classification is None
    assert restored.semantic_selection is None


def test_migration_discards_an_alternate_catalog_compatible_profile_choice():
    payload = _post_measurement_payload()
    payload["semantic_selection"].update(
        {
            "simulation_profile_id": "first_order_lag_with_delay",
            "feature_bundle_id": "class_i_delay_minimal",
            "selected_feature_ids": [
                "static_gain",
                "time_constant",
                "dead_time",
            ],
        }
    )

    restored = migrate_diagnostic_session_payload(payload)

    assert restored.status == "measurement_verified"
    assert restored.classification is None
    assert restored.semantic_selection is None
    assert restored.specification_templates == []
    assert restored.specification_assessment is None


def test_migration_clears_downstream_derived_artifacts_before_profile_reselection():
    payload = _post_measurement_payload()
    payload["experiment_plan"] = {
        "experiments": [],
        "rationale": "injected",
    }
    payload["specification_answer_history"] = ["untrusted prior answer"]

    restored = migrate_diagnostic_session_payload(payload)

    assert restored.status == "measurement_verified"
    assert restored.classification is None
    assert restored.semantic_selection is None
    assert restored.experiment_plan is None
    assert restored.evidence_requirement_plan is None
    assert restored.evidence_readiness is None
    assert restored.compiled_specification_model is None
    assert restored.candidate_route is None
    assert restored.compiled_route is None
    assert restored.specification_answer_history == []


def test_migration_rebuilds_accumulated_description_from_retained_raw_inputs():
    payload = _post_measurement_payload()
    payload["accumulated_description"]["text"] += (
        "\nInjected derived profile facts: input_change=99 V and output_max=999 degC."
    )
    payload["accumulated_description"]["safety_bounds"] = {"output_max": 999.0}
    payload["accumulated_description"]["simulation_boundary_confirmation"] = {
        "confirmed": True,
        "scope": "software_simulation_only",
        "statement_version": "v1",
    }

    restored = migrate_diagnostic_session_payload(payload)

    assert "Injected derived profile facts" not in restored.accumulated_description.text
    assert restored.accumulated_description.safety_bounds == {}
    assert restored.accumulated_description.simulation_boundary_confirmation is None


def test_session_round_counters_cannot_exceed_the_configured_budget():
    payload = _post_measurement_payload()
    payload["maximum_turns"] = 1
    payload["profile_measurement_round_count"] = 2

    with pytest.raises(ValidationError, match="profile_measurement_round_count.*maximum_turns"):
        DiagnosticSessionState.model_validate(payload)


def test_profile_round_count_cannot_poison_a_preprofile_resumed_session():
    state = start_diagnostic_session(_description())
    payload = state.model_dump(mode="json")
    payload["profile_measurement_round_count"] = state.maximum_turns

    restored = migrate_diagnostic_session_payload(payload)
    assert restored.status == state.status
    assert restored.profile_measurement_round_count == 0


def test_migration_rebuilds_description_turn_audit_fields_from_raw_answers():
    state = start_diagnostic_session(_description())
    state = continue_description_session(
        state,
        "The room record also names the heater and temperature signals.",
        expected_revision=state.revision,
    )
    payload = state.model_dump(mode="json")
    payload["turns"][0].update(
        {
            "turn_index": 99,
            "questions": ["unsafe forged question"],
            "evidence": ["forged audit evidence"],
            "diagnosis": DiagnosticEngine().diagnose(
                SystemDescription(text="forged diagnosis input")
            ).model_dump(mode="json"),
        }
    )
    payload["description_turn_count"] = 7

    restored = migrate_diagnostic_session_payload(payload)

    assert restored.description_turn_count == 1
    assert len(restored.turns) == 1
    turn = restored.turns[0]
    assert turn.turn_index == 1
    assert turn.questions == ["supplemental_description"]
    assert turn.evidence == [
        "Supplemental description: The room record also names the heater and temperature signals."
    ]
    assert "forged" not in turn.model_dump_json()
    expected_description = state.initial_description.model_copy(
        update={"text": restored.accumulated_description.text}
    )
    assert turn.diagnosis == DiagnosticEngine().diagnose(expected_description)


def test_migration_discards_spent_profile_rounds_when_resetting_to_profile_reselection():
    payload = _post_measurement_payload()
    diagnostic_ready = payload["measurement_history"][-1]
    payload["measurement_history"].extend([diagnostic_ready for _ in range(8)])
    payload["measurement_response_history"].extend(
        ["Profile-only reply with unchanged diagnostic facts." for _ in range(8)]
    )
    payload["measurement_assessment"] = diagnostic_ready
    payload["profile_measurement_round_count"] = 8

    restored = migrate_diagnostic_session_payload(payload)

    assert restored.status == "measurement_verified"
    assert restored.measurement_round_count == 1
    assert restored.profile_measurement_round_count == 0
    assert len(restored.measurement_history) == 1
    assert len(restored.measurement_response_history) == 1
    assert restored.measurement_assessment == restored.measurement_history[-1]


def test_migration_resets_current_style_profile_counter_after_discarding_answers():
    payload = _post_measurement_payload()
    payload["profile_measurement_round_count"] = 3
    payload["specification_answer_history"] = ["reply one", "reply two", "reply three"]

    restored = migrate_diagnostic_session_payload(payload)

    assert restored.status == "measurement_verified"
    assert restored.profile_measurement_round_count == 0
    assert restored.specification_answer_history == []


def test_measurement_verified_state_rejects_a_second_description_evidence_source():
    payload = _post_measurement_payload()
    payload["description_assessment"] = payload["measurement_assessment"]

    with pytest.raises(ValidationError, match="mutually exclusive"):
        DiagnosticSessionState.model_validate(payload)


def test_measurement_verified_state_recomputes_current_diagnosis_from_history():
    payload = _post_measurement_payload()
    payload["current_diagnosis"]["minimum_phase"]["assessment"] = "nonminimum_phase"
    payload["current_diagnosis"]["minimum_phase"]["value"] = "forged"

    with pytest.raises(ValidationError, match="must match.*measurement history"):
        DiagnosticSessionState.model_validate(payload)


def test_profile_ready_carry_forward_uses_an_independent_round_counter():
    state = DiagnosticSessionState.model_validate(_post_measurement_payload())
    assessment = state.measurement_assessment

    updated = submit_profile_measurement_assessment(
        state,
        assessment,
        raw_response="This Profile reply adds only model specification facts.",
        expected_revision=state.revision,
    )

    assert updated.measurement_round_count == 1
    assert updated.profile_measurement_round_count == 1
    assert len(updated.measurement_history) == 1
    assert len(updated.measurement_response_history) == 1
    assert updated.measurement_assessment == assessment
    assert updated.revision == state.revision + 1

    with pytest.raises(ValueError, match="stale diagnostic session revision"):
        submit_profile_measurement_assessment(
            state,
            assessment,
            raw_response="This Profile reply adds only model specification facts.",
            expected_revision=state.revision + 1,
        )


def test_grounded_profile_conflict_invalidates_the_postmeasurement_release():
    state = DiagnosticSessionState.model_validate(_post_measurement_payload())
    conflict_text = "A newer record says the output grows without bound."
    conflict = MeasurementAssessment(
        status="conflict",
        conflicts=[conflict_text],
        conflict_request_ids=[state.measurement_plan.requests[0].request_id],
        gaps=[item.diagnostic_field_id for item in state.checklist[1:]],
    )

    invalidated = submit_profile_measurement_assessment(
        state,
        conflict,
        raw_response=conflict_text,
        expected_revision=state.revision,
    )

    assert invalidated.status == "collecting_description"
    assert invalidated.evidence_level == "description_only"
    assert invalidated.classification is None
    assert invalidated.semantic_selection is None
    assert invalidated.profile_measurement_round_count == 1


def test_refused_migration_clears_forged_release_and_downstream_fields():
    payload = _post_measurement_payload()
    diagnostic_ready = payload["measurement_history"][-1]
    payload["measurement_history"].extend([diagnostic_ready for _ in range(8)])
    payload["measurement_response_history"].extend(
        ["Profile-only reply with unchanged diagnostic facts." for _ in range(8)]
    )
    payload.update(
        {
            "measurement_assessment": diagnostic_ready,
            "profile_measurement_round_count": 8,
            "status": "refused",
            "refusal_reason": "maximum_profile_measurement_rounds_reached",
            "experiment_plan": {"forged": True},
            "candidate_route": {"forged": True},
            "compiled_route": {"forged": True},
            "specification_answer_history": ["forged prior answer"],
        }
    )

    restored = migrate_diagnostic_session_payload(payload)

    assert restored.status == "refused"
    assert restored.refusal_reason == "maximum_profile_measurement_rounds_reached"
    assert restored.measurement_round_count == 1
    assert restored.profile_measurement_round_count == 8
    assert restored.classification is None
    assert restored.semantic_selection is None
    assert restored.experiment_plan is None
    assert restored.candidate_route is None
    assert restored.compiled_route is None
    assert restored.specification_answer_history == []


def test_refused_migration_recomputes_forged_description_derived_state():
    state = start_diagnostic_session(SystemDescription(text="I have a machine."))
    for index in range(state.maximum_turns):
        state = continue_description_session(
            state,
            f"Existing record {index} names the observed output.",
            expected_revision=state.revision,
        )
    payload = state.model_dump(mode="json")
    payload["current_diagnosis"]["open_loop_stability"].update(
        {
            "status": "known",
            "value": "forged unstable result",
            "confidence": 1.0,
            "evidence": ["forged audit evidence"],
            "assessment": "unstable",
        }
    )
    payload["checklist"][0].update(
        {
            "status": "known",
            "evidence": ["forged audit evidence"],
        }
    )

    restored = migrate_diagnostic_session_payload(payload)

    assert restored.status == "refused"
    assert restored.description_turn_count == state.maximum_turns
    assert restored.current_diagnosis == state.current_diagnosis
    assert restored.checklist == state.checklist


def test_migration_rejects_non_string_raw_measurement_history_without_attribute_error():
    payload = _post_measurement_payload()
    payload["measurement_response_history"][0] = 7

    with pytest.raises(ValueError, match="response history entries must be strings"):
        migrate_diagnostic_session_payload(payload)


def test_continue_diagnostic_session_requires_and_checks_expected_revision():
    state = start_diagnostic_session(_description())
    with pytest.raises(TypeError, match="expected_revision"):
        continue_diagnostic_session(state, supplemental_description="Existing record.")
    with pytest.raises(ValueError, match="stale diagnostic session revision"):
        continue_diagnostic_session(
            state,
            supplemental_description="Existing record.",
            expected_revision=state.revision + 1,
        )
