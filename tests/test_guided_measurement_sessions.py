import math

import pytest
from pydantic import ValidationError

from cfdc.diagnosis import (
    build_diagnostic_checklist,
    continue_description_session,
    continue_diagnostic_session,
    start_diagnostic_session,
    submit_measurement_assessment,
)
from cfdc.models import (
    DiagnosticSessionState,
    MeasuredFact,
    MeasurementAssessment,
    MeasurementRequest,
    SystemDescription,
)
from cfdc.runtime import run_cfdc_route


def _description() -> SystemDescription:
    return SystemDescription(
        text="A temperature output is recorded after a heater command.",
        observed_outputs=["temperature"],
        actuators=["heater"],
    )


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
    with pytest.raises(ValidationError, match="unknown values belong in assessment gaps"):
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
        state, assessment, expected_revision=state.revision
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
                source_excerpt=f"Existing record: {request.title} was reviewed.",
                text_value="reported observation",
            )
            for request in state.measurement_plan.requests
        ],
    )

    updated = submit_measurement_assessment(
        state, assessment, expected_revision=state.revision
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
            state, assessment, expected_revision=state.revision
        )

    assert state.measurement_round_count == 8
    assert state.status == "refused"
    assert state.refusal_reason == "maximum_measurement_rounds_reached"


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
            state, invalid, expected_revision=state.revision
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
                source_excerpt=f"Existing record: {request.title} was reviewed.",
                text_value="reported observation",
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


def test_session_model_allows_paired_later_stage_selection_after_measurement_verification():
    state = start_diagnostic_session(_description())
    verified = submit_measurement_assessment(
        state, _ready_assessment(state), expected_revision=state.revision
    )
    report = run_cfdc_route("generic", description=_description())
    payload = verified.model_dump(mode="json")
    payload["classification"] = report.classification.model_dump(mode="json")
    payload["semantic_selection"] = report.semantic_selection.model_dump(mode="json")

    restored = DiagnosticSessionState.model_validate(payload)

    assert restored.classification == report.classification
    assert restored.semantic_selection == report.semantic_selection


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("no_plan", "measurement_verified status requires a measurement plan"),
        ("partial_plan", "fixed eight diagnostic fields"),
        ("missing_fact", "must account for every active measurement request"),
        ("unknown_fact", "unknown measurement request id"),
    ],
)
def test_direct_v4_payload_validation_cannot_forge_measurement_verified(
    mutation, message
):
    state = start_diagnostic_session(_description())
    verified = submit_measurement_assessment(
        state, _ready_assessment(state), expected_revision=state.revision
    )
    payload = verified.model_dump(mode="json")
    if mutation == "no_plan":
        payload["measurement_plan"] = None
    elif mutation == "partial_plan":
        payload["measurement_plan"]["requests"] = payload["measurement_plan"][
            "requests"
        ][:-1]
    elif mutation == "missing_fact":
        payload["measurement_assessment"]["facts"] = payload[
            "measurement_assessment"
        ]["facts"][:-1]
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
    with pytest.raises(ValueError, match="must account for every active measurement request"):
        submit_measurement_assessment(
            state, incomplete, expected_revision=state.revision
        )

    incomplete_conflict = MeasurementAssessment(
        status="conflict",
        conflicts=["Two records disagree."],
        conflict_request_ids=[state.measurement_plan.requests[0].request_id],
        gaps=[state.checklist[1].diagnostic_field_id],
    )
    with pytest.raises(ValueError, match="must account for every active measurement request"):
        submit_measurement_assessment(
            state, incomplete_conflict, expected_revision=state.revision
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
    payload["measurement_round_count"] = 1
    payload["status"] = "measurement_conflict" if status == "conflict" else "awaiting_measurements"

    with pytest.raises(ValidationError, match="must account for every active measurement request"):
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
    payload["measurement_round_count"] = 1

    with pytest.raises(ValidationError, match="must account for every active measurement request"):
        DiagnosticSessionState.model_validate(payload)


def test_direct_v4_payload_rejects_current_assessment_that_is_not_last_history_entry():
    state = start_diagnostic_session(_description())
    prior = _complete_gap_assessment(state)
    current = _complete_conflict_assessment(state)
    payload = state.model_dump(mode="json")
    payload["measurement_history"] = [prior.model_dump(mode="json")]
    payload["measurement_round_count"] = 1
    payload["measurement_assessment"] = current.model_dump(mode="json")
    payload["status"] = "measurement_conflict"

    with pytest.raises(ValidationError, match="final measurement history entry"):
        DiagnosticSessionState.model_validate(payload)


def test_direct_v4_payload_accepts_empty_or_complete_auditable_measurement_history():
    state = start_diagnostic_session(_description())
    restored_empty = DiagnosticSessionState.model_validate(state.model_dump(mode="json"))
    assert restored_empty.measurement_history == []
    assert restored_empty.measurement_assessment is None

    first = _complete_gap_assessment(state)
    current = _complete_conflict_assessment(state)
    payload = state.model_dump(mode="json")
    payload["measurement_history"] = [
        first.model_dump(mode="json"),
        current.model_dump(mode="json"),
    ]
    payload["measurement_round_count"] = 2
    payload["measurement_assessment"] = current.model_dump(mode="json")
    payload["status"] = "measurement_conflict"

    restored = DiagnosticSessionState.model_validate(payload)
    assert restored.measurement_history == [first, current]
    assert restored.measurement_assessment == current


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
