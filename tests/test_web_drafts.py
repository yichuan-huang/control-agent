from copy import deepcopy

import pytest

from cfdc.web import drafts


def valid_draft(**updates):
    return {
        **drafts.empty_draft(),
        "description": "保持箱体温度",
        "outputs": [["temperature", "degC"]],
        "inputs": [["heater"]],
        "input_unit": "V",
        "input_min": 0,
        "input_max": 10,
        "state_stop": 80,
        **updates,
    }


def test_draft_keeps_disabled_values_absent_and_does_not_mutate_form():
    form = valid_draft(reference=0, final_abs_error_max=2)
    before = deepcopy(form)
    task = drafts.task_from_draft(form)
    assert task["reference"] is None
    assert task["success_requirements"] == {}
    assert task["signal_units"] == {"temperature": "degC"}
    assert task["input_min"] == 0
    assert form == before


@pytest.mark.parametrize(
    ("updates", "field"),
    [
        ({"description": ""}, "description"),
        ({"outputs": [["", ""]]}, "outputs"),
        ({"outputs": [["y", "K"], ["y", "K"]]}, "outputs"),
        ({"input_min": None}, "input_min"),
        ({"input_max": 0}, "input_max"),
        ({"state_stop": 0}, "state_stop"),
        ({"state_stop": float("nan")}, "state_stop"),
        ({"output_bounds_enabled": True, "output_min": 0}, "output_max"),
        ({"reference_enabled": True, "reference": None}, "reference"),
        (
            {"budget_fields": ["distinct_experiments"], "distinct_experiments": 1.5},
            "distinct_experiments",
        ),
        (
            {"task_type": "transition_then_hold", "initial_region": "起点"},
            "goal_region",
        ),
        ({"task_type": "disturbance_recovery_to_hold"}, "disturbance_event"),
    ],
)
def test_draft_errors_identify_the_field_without_creating_a_task(updates, field):
    with pytest.raises(drafts.DraftValidationError) as caught:
        drafts.task_from_draft(valid_draft(**updates))
    assert field in caught.value.errors


@pytest.mark.parametrize(
    "kind",
    ["local_setpoint_hold", "transition_then_hold", "disturbance_recovery_to_hold"],
)
def test_supported_tasks_preserve_only_relevant_phase_fields(kind):
    task = drafts.task_from_draft(
        valid_draft(
            task_type=kind,
            initial_region="起点",
            goal_region="目标",
            intermediate_targets="3，6",
            disturbance_event="负载变化",
            recovery_start_condition="变化后",
            disturbance_hold_region="目标附近",
        )
    )
    assert task["task_type"] == kind
    assert ("goal_region" in task) == (kind == "transition_then_hold")
    assert ("disturbance_event" in task) == (kind == "disturbance_recovery_to_hold")
    if kind == "transition_then_hold":
        assert task["intermediate_targets"] == [3.0, 6.0]


def test_all_case_drafts_roundtrip_registered_scope_and_editing_is_rejected():
    from cfdc.kernel.cases import public_case_catalog, public_training_case
    from cfdc.kernel.contracts import TaskContract
    from cfdc.kernel.session import registered_task_scope_fingerprint

    for case_id in public_case_catalog():
        form = drafts.case_draft(case_id)
        task = drafts.task_from_draft(form, case_id=case_id)
        canonical = TaskContract.from_user_input(public_training_case(case_id)["task"])
        assert registered_task_scope_fingerprint(
            TaskContract.from_user_input(task)
        ) == registered_task_scope_fingerprint(canonical)
        with pytest.raises(drafts.DraftValidationError):
            drafts.task_from_draft(
                {**form, "input_max": form["input_max"] + 1}, case_id=case_id
            )


def test_converted_case_has_no_provider_authority_and_keeps_explicit_values():
    form = drafts.case_draft("dc_motor_speed_v1")
    task = drafts.task_from_draft(form)
    assert task["reference"] == 20
    assert task["success_requirements"]["final_abs_error_max"] == 1.5
    assert "registered_case_binding" not in task
    assert "provider_references" not in task


def external_draft(**updates):
    return valid_draft(
        external_data_enabled=True,
        reference_enabled=True,
        reference=0.5,
        region_label="intensity 0 to 1",
        evaluation_dt_s=0.02,
        evaluation_horizon_s=20,
        evaluation_repeats=20,
        success_requirement_fields=["final_abs_error_max"],
        final_abs_error_max=0.03,
        **updates,
    )


def test_external_draft_freezes_explicit_evaluation_inputs():
    task = drafts.task_from_draft(external_draft())
    assert task["operating_region"] == "intensity 0 to 1"
    assert task["budgets"]["evaluation_sample_time_s"] == 0.02
    assert task["budgets"]["evaluation_horizon_s"] == 20
    assert task["budgets"]["evaluation_repeats"] == 20


@pytest.mark.parametrize(
    "updates,field",
    [
        ({"evaluation_dt_s": 0}, "evaluation_dt_s"),
        ({"evaluation_horizon_s": 0.01}, "evaluation_horizon_s"),
        ({"evaluation_repeats": 1.5}, "evaluation_repeats"),
        ({"reference_enabled": False}, "reference"),
        ({"region_label": ""}, "region_label"),
        ({"success_requirement_fields": []}, "success_requirement_fields"),
    ],
)
def test_external_draft_reports_missing_or_invalid_frozen_inputs(updates, field):
    with pytest.raises(drafts.DraftValidationError) as exc:
        drafts.task_from_draft({**external_draft(), **updates})
    assert field in exc.value.errors


def test_external_disturbance_parameters_are_numeric_execution_contract():
    task = drafts.task_from_draft(
        external_draft(
            task_type="disturbance_recovery_to_hold",
            disturbance_event="diluent pulse",
            recovery_start_condition="pulse ends",
            disturbance_hold_region="target",
            disturbance_channel="heater",
            disturbance_start_s=2,
            disturbance_amplitude=0.1,
            disturbance_duration_s=1,
            recovery_deadline_s=10,
        )
    )
    assert task["disturbance_contract"]["channel"] == "heater"
    assert task["disturbance_contract"]["time_s"] == 2
    assert task["success_requirements"]["recovery_time_max_s"] == 10
