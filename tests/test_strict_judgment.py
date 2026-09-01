"""Independent, hand-calculated oracles for the new trajectory-only judge."""

from copy import deepcopy

import pytest

from cfdc.kernel.contracts import fingerprint
from cfdc.kernel.judging import judge_packet


def freeze_packet(outputs=None):
    """Four one-second samples: error [1,.5,0,0], trapezoid IAE=1."""
    freeze = {
        "freeze_version": "cfdc-freeze/v2.0",
        "session_id": "manual",
        "task_fingerprint": "task",
        "evidence_fingerprints": ["evidence"],
        "controller": {"family": "PI"},
        "runtime_contract": {
            "tracked_signals": ["y"],
            "control_inputs": ["u"],
            "input_bounds": {"u": [-2, 2]},
            "output_bounds": {"y": [-5, 5]},
            "provider_bindings": {
                "evaluation": {"provider_id": "manual", "provider_version": "1"}
            },
        },
        "evaluation_contract": {
            "task_type": "local_setpoint_hold",
            "horizon_s": 3.0,
            "references": {"y": 1.0},
            "sample_time_s": 1.0,
            "final_abs_error_max": 0.1,
            "overshoot_max": 0.1,
            "settling_time_max_s": 2.0,
            "hold_duration_min_s": 1.0,
            "trial_manifest": {
                "development": [
                    {"trial_id": "d0", "scenario_id": "nominal", "seed": 1}
                ],
                "fresh_confirmation": [
                    {"trial_id": "f0", "scenario_id": "nominal", "seed": 2}
                ],
            },
        },
    }
    freeze["freeze_fingerprint"] = fingerprint(freeze)
    packet = {
        "packet_version": "cfdc-evaluation-packet/v2.0",
        "session_id": "manual",
        "task_fingerprint": "task",
        "freeze_fingerprint": freeze["freeze_fingerprint"],
        "evidence_fingerprints": ["evidence"],
        "provider_id": "manual",
        "provider_version": "1",
        "evaluation_split": "development",
        "trials": [
            {
                "trial_id": "d0",
                "scenario_id": "nominal",
                "seed": 1,
                "trajectory": {
                    "time_s": [0, 1, 2, 3],
                    "outputs": {
                        "y": outputs if outputs is not None else [0, 0.5, 1, 1]
                    },
                    "references": {"y": [1, 1, 1, 1]},
                    "control_inputs": {"u": [2, 1, 0, 0]},
                    "raw_control_inputs": {"u": [3, 1, 0, 0]},
                    "controller_states": [{"integral": 0}] * 4,
                    "phase_ids": ["hold"] * 4,
                },
                "stop_event": {
                    "triggered": False,
                    "time_s": 3.0,
                    "reason": "horizon_complete",
                },
                "events": [],
            }
        ],
    }
    packet["packet_fingerprint"] = fingerprint(packet)
    return freeze, packet


def rehash(value, key):
    value.pop(key, None)
    value[key] = fingerprint(value)


def test_hand_calculated_metrics_ignore_provider_scores_and_pass_flags():
    freeze, packet = freeze_packet()
    packet["trials"][0].update(stable=False, performance_pass=False, score=-999)
    rehash(packet, "packet_fingerprint")
    result = judge_packet(freeze, packet)
    metrics = result["trials"][0]["metrics"]
    assert metrics["channels"]["y"]["iae"] == pytest.approx(1)
    assert metrics["channels"]["y"]["settling_time_s"] == 2
    assert metrics["channels"]["y"]["hold_duration_s"] == 1
    assert metrics["inputs"]["u"]["saturation_duration_s"] == 1
    assert result["score"] == 0
    assert result["status"] == "performance_met"
    assert result["wilson_lower_bound_95"] == pytest.approx(0.20654931437723745)


@pytest.mark.parametrize("missing", ["trajectory", "stop_event"])
def test_no_summary_or_missing_stop_can_become_trusted(missing):
    freeze, packet = freeze_packet()
    packet["trials"][0].pop(missing)
    packet["trials"][0].update(stable=True, performance_pass=True, score=1)
    rehash(packet, "packet_fingerprint")
    with pytest.raises(ValueError, match=missing):
        judge_packet(freeze, packet)


def test_incomplete_sample_sequence_rejected_even_when_end_error_is_zero():
    freeze, packet = freeze_packet()
    trace = packet["trials"][0]["trajectory"]
    trace["time_s"] = [0, 1, 3, 4]
    rehash(packet, "packet_fingerprint")
    with pytest.raises(ValueError, match="sampling|horizon"):
        judge_packet(freeze, packet)


def test_one_channel_failure_cannot_be_hidden_by_averaging():
    freeze, packet = freeze_packet()
    freeze["runtime_contract"]["tracked_signals"].append("z")
    freeze["evaluation_contract"]["references"]["z"] = 1.0
    freeze["runtime_contract"]["output_bounds"]["z"] = [-5, 5]
    rehash(freeze, "freeze_fingerprint")
    packet["freeze_fingerprint"] = freeze["freeze_fingerprint"]
    trace = packet["trials"][0]["trajectory"]
    trace["outputs"]["z"] = [0, 0, 0, 0]
    trace["references"]["z"] = [1, 1, 1, 1]
    rehash(packet, "packet_fingerprint")
    result = judge_packet(freeze, packet)
    assert result["status"] == "performance_not_met"
    assert result["score"] > 0
    assert result["trials"][0]["metrics"]["channels"]["z"]["final_abs_error"] == 1


@pytest.mark.parametrize(
    "tamper", ["duplicate", "missing", "seed", "scenario", "split"]
)
def test_frozen_denominator_and_trial_identity_cannot_be_changed(tamper):
    freeze, packet = freeze_packet()
    if tamper == "duplicate":
        packet["trials"].append(deepcopy(packet["trials"][0]))
    elif tamper == "missing":
        packet["trials"] = []
    elif tamper == "seed":
        packet["trials"][0]["seed"] = 500
    elif tamper == "scenario":
        packet["trials"][0]["scenario_id"] = "easier"
    else:
        packet["evaluation_split"] = "fresh_confirmation"
    rehash(packet, "packet_fingerprint")
    with pytest.raises(ValueError, match="trial|scenario"):
        judge_packet(freeze, packet)


def test_wrong_fingerprint_is_rejected_and_identical_packet_replays_identically():
    freeze, packet = freeze_packet()
    assert judge_packet(freeze, packet) == judge_packet(
        deepcopy(freeze), deepcopy(packet)
    )
    packet["trials"][0]["trajectory"]["outputs"]["y"][-1] = 500
    with pytest.raises(ValueError, match="fingerprint"):
        judge_packet(freeze, packet)


def test_input_limit_failure_is_hard_failure_even_with_perfect_output():
    freeze, packet = freeze_packet([1, 1, 1, 1])
    packet["trials"][0]["trajectory"]["control_inputs"]["u"][0] = 9
    rehash(packet, "packet_fingerprint")
    result = judge_packet(freeze, packet)
    assert result["stability_gate"]["passed"] is False
    assert result["status"] == "performance_not_met"


def test_provider_cannot_change_reference_to_match_bad_output():
    freeze, packet = freeze_packet([0, 0, 0, 0])
    freeze["evaluation_contract"]["references"] = {"y": 1.0}
    rehash(freeze, "freeze_fingerprint")
    packet["freeze_fingerprint"] = freeze["freeze_fingerprint"]
    packet["trials"][0]["trajectory"]["references"]["y"] = [0, 0, 0, 0]
    rehash(packet, "packet_fingerprint")
    with pytest.raises(ValueError, match="reference"):
        judge_packet(freeze, packet)


def test_same_scenario_seed_cannot_be_declared_for_development_and_fresh():
    freeze, packet = freeze_packet()
    freeze["evaluation_contract"]["trial_manifest"]["fresh_confirmation"][0]["seed"] = 1
    rehash(freeze, "freeze_fingerprint")
    packet["freeze_fingerprint"] = freeze["freeze_fingerprint"]
    rehash(packet, "packet_fingerprint")
    with pytest.raises(ValueError, match="partition"):
        judge_packet(freeze, packet)


def test_finite_stopped_trial_cannot_be_mistaken_for_stability():
    freeze, packet = freeze_packet([1, 1, 1, 1])
    packet["trials"][0]["stop_event"].update(triggered=True, reason="state_limit")
    rehash(packet, "packet_fingerprint")
    result = judge_packet(freeze, packet)
    assert result["stability_gate"]["passed"] is False


def resign(freeze, packet):
    rehash(freeze, "freeze_fingerprint")
    packet["freeze_fingerprint"] = freeze["freeze_fingerprint"]
    rehash(packet, "packet_fingerprint")


def repeated_packet():
    freeze, packet = freeze_packet([1, 1, 1, 1])
    # Ten distinct deterministic realizations, with one bounded soft failure.
    rows, trials = [], []
    for index in range(10):
        identity = {
            "trial_id": f"d{index}",
            "scenario_id": "nominal",
            "seed": 10 + index,
        }
        rows.append(identity)
        trial = deepcopy(packet["trials"][0])
        trial.update(identity)
        if index == 9:
            trial["trajectory"]["outputs"]["y"][-1] = 1.2
        trials.append(trial)
    freeze["evaluation_contract"]["trial_manifest"]["development"] = rows
    packet["trials"] = trials
    resign(freeze, packet)
    return freeze, packet


def test_frozen_wilson_accepts_soft_failure_but_default_requires_all_trials():
    freeze, packet = repeated_packet()
    assert judge_packet(freeze, packet)["status"] == "performance_not_met"
    freeze["evaluation_contract"]["perturbed_success_rate_min"] = 0.5
    resign(freeze, packet)
    result = judge_packet(freeze, packet)
    assert result["success_count"] == 9
    assert result["wilson_lower_bound_95"] == pytest.approx(0.5958499732047616)
    assert result["status"] == "performance_met"
    assert result["score"] > 0  # A lower-is-better diagnostic is not a pass bit.


def test_frozen_worst_trial_requirement_still_gates_wilson_acceptance():
    freeze, packet = repeated_packet()
    freeze["evaluation_contract"].update(
        perturbed_success_rate_min=0.5, worst_trial_violation_max=0.5
    )
    resign(freeze, packet)
    result = judge_packet(freeze, packet)
    assert result["status"] == "performance_not_met"
    assert "worst_trial_violation_above_frozen_requirement" in result["failure_reasons"]


def test_unmet_wilson_requirement_has_nonzero_score_even_when_all_trials_pass():
    freeze, packet = freeze_packet([1, 1, 1, 1])
    freeze["evaluation_contract"]["perturbed_success_rate_min"] = 0.5
    resign(freeze, packet)
    result = judge_packet(freeze, packet)
    assert result["status"] == "performance_not_met"
    assert result["score"] == pytest.approx(0.5869013712455251)


def test_wilson_never_waives_hard_safety_failure():
    freeze, packet = repeated_packet()
    freeze["evaluation_contract"]["perturbed_success_rate_min"] = 0.5
    packet["trials"][-1]["trajectory"]["control_inputs"]["u"][0] = 9
    resign(freeze, packet)
    result = judge_packet(freeze, packet)
    assert result["performance_gate"]["success_rate_passed"]
    assert not result["stability_gate"]["passed"]
    assert result["status"] == "performance_not_met"


@pytest.mark.parametrize("partition", ["development", "fresh_confirmation"])
def test_duplicate_realization_rejected_in_either_frozen_partition(partition):
    freeze, packet = freeze_packet()
    rows = freeze["evaluation_contract"]["trial_manifest"][partition]
    duplicate = {**rows[0], "trial_id": "extra"}
    rows.append(duplicate)
    if partition == "development":
        packet["trials"].append({**deepcopy(packet["trials"][0]), **duplicate})
    resign(freeze, packet)
    with pytest.raises(ValueError, match="partition|manifest"):
        judge_packet(freeze, packet)


@pytest.mark.parametrize(
    "field,value", [("trial_id", 3), ("scenario_id", []), ("seed", True)]
)
def test_unused_partition_also_validates_identity_types(field, value):
    freeze, packet = freeze_packet()
    freeze["evaluation_contract"]["trial_manifest"]["fresh_confirmation"][0][
        "scenario_id"
    ] = "fresh"
    freeze["evaluation_contract"]["trial_manifest"]["fresh_confirmation"][0][field] = (
        value
    )
    resign(freeze, packet)
    with pytest.raises(ValueError, match="partition|manifest"):
        judge_packet(freeze, packet)


def measured_packet():
    freeze, packet = freeze_packet()
    freeze["runtime_contract"].update(
        measured_signals=["y", "x"],
        state_bounds={"x": [-1, 1]},
        controller_state_bounds={"integral": [-2, 2]},
    )
    packet["trials"][0]["trajectory"]["measurements"] = {
        "y": [0, 0.5, 1, 1],
        "x": [0, 0, 0, 0],
    }
    resign(freeze, packet)
    return freeze, packet


@pytest.mark.parametrize(
    "bound_kind", ["measured_state", "controller_state", "state_stop"]
)
def test_state_limits_are_hard_failures_without_provider_stop(bound_kind):
    freeze, packet = measured_packet()
    trace = packet["trials"][0]["trajectory"]
    if bound_kind == "controller_state":
        trace["controller_states"][1] = {"integral": 3}
    else:
        trace["measurements"]["x"][1] = 3
        if bound_kind == "state_stop":
            freeze["runtime_contract"].pop("state_bounds")
            freeze["runtime_contract"]["state_stop"] = 2
    resign(freeze, packet)
    result = judge_packet(freeze, packet)
    assert not result["stability_gate"]["passed"]
    assert result["status"] == "performance_not_met"


@pytest.mark.parametrize(
    "tamper",
    [
        "missing_measurement",
        "missing_bounded_state",
        "missing_controller_state",
        "output_mismatch",
    ],
)
def test_public_state_schema_cannot_omit_or_disagree_with_typed_channels(tamper):
    freeze, packet = measured_packet()
    trace = packet["trials"][0]["trajectory"]
    if tamper == "missing_measurement":
        del trace["measurements"]["y"]
    elif tamper == "missing_bounded_state":
        freeze["runtime_contract"].pop("measured_signals")
        del trace["measurements"]["x"]
    elif tamper == "missing_controller_state":
        trace["controller_states"][1] = {}
    else:
        trace["measurements"]["y"][1] = 9
    resign(freeze, packet)
    with pytest.raises(ValueError, match="measurement|state"):
        judge_packet(freeze, packet)


def phase_packet():
    freeze, packet = freeze_packet([1, 1, 1, 2, 2])
    freeze["evaluation_contract"].update(
        task_type="transition_then_hold",
        horizon_s=4,
        settling_time_max_s=3,
        hold_duration_min_s=0,
        phases=[
            {
                "phase_id": "launch",
                "references": {"y": 1},
                "exit_predicate": {
                    "kind": "within_band",
                    "signal": "y",
                    "target": 1,
                    "tolerance": 0.1,
                },
                "dwell_s": 1,
                "timeout_s": 3,
                "hysteresis": 0,
                "state_policy": "reset",
            },
            {
                "phase_id": "hold",
                "references": {"y": 2},
                "exit_predicate": {
                    "kind": "within_band",
                    "signal": "y",
                    "target": 2,
                    "tolerance": 1.1,
                },
                "dwell_s": 1,
                "timeout_s": 3,
                "hysteresis": 0,
                "state_policy": "inherit",
            },
        ],
    )
    trace = packet["trials"][0]["trajectory"]
    trace["time_s"] = [0, 1, 2, 3, 4]
    trace["phase_ids"] = ["launch", "launch", "hold", "hold", "hold"]
    trace["references"]["y"] = [1, 1, 2, 2, 2]
    trace["control_inputs"]["u"] = [2, 1, 0, 0, 0]
    trace["raw_control_inputs"]["u"] = [3, 1, 0, 0, 0]
    trace["controller_states"] = [{"integral": i} for i in range(5)]
    packet["trials"][0]["stop_event"]["time_s"] = 4
    packet["trials"][0]["events"] = [
        {
            "kind": "handoff",
            "time_s": 2,
            "sample_index": 2,
            "from_phase": "launch",
            "to_phase": "hold",
            "state_policy": "inherit",
            "state_on_entry": {"integral": 1},
            "state_before": {"integral": 1},
            "state_after": {"integral": 2},
            "command_before": {"u": 1},
            "command_after": {"u": 0},
        }
    ]
    resign(freeze, packet)
    return freeze, packet


@pytest.mark.parametrize(
    "field,value",
    [
        ("time_s", 1),
        ("sample_index", 1),
        ("sample_index", True),
        ("from_phase", "elsewhere"),
        ("to_phase", "elsewhere"),
        ("state_before", {}),
        ("state_after", {}),
        ("command_before", {}),
        ("command_after", {}),
        ("state_policy", "reset"),
        ("state_on_entry", {}),
    ],
)
def test_handoff_evidence_must_match_boundary_and_adjacent_samples(field, value):
    freeze, packet = phase_packet()
    assert judge_packet(freeze, packet)["status"] == "performance_met"
    packet["trials"][0]["events"][0][field] = value
    resign(freeze, packet)
    result = judge_packet(freeze, packet)
    assert result["status"] == "performance_not_met"
    assert result["trials"][0]["metrics"]["verified_handoff_count"] == 0


def test_phase_dwell_includes_transition_boundary_under_previous_predicate():
    freeze, packet = phase_packet()
    freeze["evaluation_contract"]["phases"][0]["dwell_s"] = 2
    resign(freeze, packet)
    result = judge_packet(freeze, packet)
    assert result["status"] == "performance_met"
    assert result["trials"][0]["metrics"]["verified_handoff_count"] == 1


def test_bad_boundary_measurement_cannot_satisfy_prior_phase_dwell():
    freeze, packet = phase_packet()
    packet["trials"][0]["trajectory"]["outputs"]["y"][2] = 2
    resign(freeze, packet)
    result = judge_packet(freeze, packet)
    assert result["status"] == "performance_not_met"
    assert "phase_dwell_not_verified:launch" in result["failure_reasons"]


def test_boundary_measurement_is_not_double_counted_for_destination_dwell():
    freeze, packet = phase_packet()
    freeze["evaluation_contract"]["phases"][1]["dwell_s"] = 1.5
    resign(freeze, packet)
    result = judge_packet(freeze, packet)
    assert result["status"] == "performance_not_met"
    assert "phase_dwell_not_verified:hold" in result["failure_reasons"]


def test_phase_references_are_bound_to_freeze_not_provider_packet():
    freeze, packet = phase_packet()
    packet["trials"][0]["trajectory"]["references"]["y"][1] = 1.01
    resign(freeze, packet)
    with pytest.raises(ValueError, match="reference"):
        judge_packet(freeze, packet)


@pytest.mark.parametrize(
    "field,value",
    [
        ("dwell_s", 0),
        ("timeout_s", 0),
        ("hysteresis", -1),
        ("state_policy", "arbitrary"),
    ],
)
def test_invalid_frozen_phase_configuration_rejected(field, value):
    freeze, packet = phase_packet()
    freeze["evaluation_contract"]["phases"][0][field] = value
    resign(freeze, packet)
    with pytest.raises(ValueError, match="phase"):
        judge_packet(freeze, packet)


@pytest.mark.parametrize("field,value", [("tolerance", 0), ("kind", "claimed_success")])
def test_phase_predicate_requires_registered_kind_and_positive_tolerance(field, value):
    freeze, packet = phase_packet()
    freeze["evaluation_contract"]["phases"][0]["exit_predicate"][field] = value
    resign(freeze, packet)
    with pytest.raises(ValueError, match="phase"):
        judge_packet(freeze, packet)


def test_handoff_checks_declared_stable_region_at_boundary():
    freeze, packet = phase_packet()
    freeze["evaluation_contract"]["phases"][1]["stable_region"] = {"y": [1.5, 2.5]}
    freeze["runtime_contract"]["measured_signals"] = ["y"]
    packet["trials"][0]["trajectory"]["measurements"] = {"y": [1, 1, 1, 2, 2]}
    resign(freeze, packet)
    result = judge_packet(freeze, packet)
    assert result["status"] == "performance_not_met"
    assert "handoff_outside_stable_region:y" in result["failure_reasons"]


def test_reset_policy_requires_empty_state_on_entry_not_empty_post_step_state():
    freeze, packet = phase_packet()
    freeze["evaluation_contract"]["phases"][1]["state_policy"] = "reset"
    event = packet["trials"][0]["events"][0]
    event.update(state_policy="reset", state_on_entry={})
    resign(freeze, packet)
    assert judge_packet(freeze, packet)["status"] == "performance_met"
    event["state_on_entry"] = {"integral": 1}
    resign(freeze, packet)
    assert judge_packet(freeze, packet)["status"] == "performance_not_met"


def test_truly_stateless_handoff_can_have_empty_state_snapshots():
    freeze, packet = phase_packet()
    packet["trials"][0]["trajectory"]["controller_states"] = [{} for _ in range(5)]
    packet["trials"][0]["events"][0].update(
        state_before={}, state_after={}, state_on_entry={}
    )
    resign(freeze, packet)
    assert judge_packet(freeze, packet)["status"] == "performance_met"


def disturbance_packet():
    freeze, packet = freeze_packet([1, 1, 1, 1])
    freeze["evaluation_contract"].update(
        task_type="disturbance_recovery_to_hold",
        recovery_abs_error_max=0.1,
        recovery_time_max_s=1,
        post_recovery_hold_duration_min_s=1,
        disturbance={"time_s": 0.5, "duration_s": 1, "amplitude": 0.5, "channel": "u"},
    )
    packet["trials"][0]["events"] = [
        {
            "kind": "disturbance",
            "sample_index": 0,
            "time_s": 0.5,
            "duration_s": 1,
            "amplitude": 0.5,
            "channel": "u",
        }
    ]
    resign(freeze, packet)
    return freeze, packet


def test_between_sample_disturbance_proves_event_binding_and_recovery_only():
    freeze, packet = disturbance_packet()
    result = judge_packet(freeze, packet)
    assert result["status"] == "performance_met"
    metrics = result["trials"][0]["metrics"]
    assert metrics["recovery_time_s"] == 0.5
    assert metrics["post_recovery_hold_duration_s"] == 1
    assert metrics["disturbance_event_verified"] is True
    assert "disturbance_executed" not in metrics


@pytest.mark.parametrize(
    "field,value",
    [
        ("time_s", -1),
        ("duration_s", 0),
        ("duration_s", -0.1),
        ("duration_s", 2.5),
        ("amplitude", 0),
        ("channel", "unknown"),
    ],
)
def test_invalid_frozen_disturbance_rejected_even_with_matching_event(field, value):
    freeze, packet = disturbance_packet()
    freeze["evaluation_contract"]["disturbance"][field] = value
    packet["trials"][0]["events"][0][field] = value
    resign(freeze, packet)
    with pytest.raises(ValueError, match="disturbance"):
        judge_packet(freeze, packet)


@pytest.mark.parametrize("index", [None, -1, 1, True])
def test_disturbance_index_anchors_interval_containing_exact_event_start(index):
    freeze, packet = disturbance_packet()
    packet["trials"][0]["events"][0]["sample_index"] = index
    resign(freeze, packet)
    result = judge_packet(freeze, packet)
    assert result["status"] == "performance_not_met"
    assert "disturbance_event_sample_mismatch" in result["failure_reasons"]


def test_wilson_rule_cannot_waive_forged_handoff_evidence():
    freeze, packet = phase_packet()
    rows, trials = [], []
    for index in range(10):
        identity = {
            "trial_id": f"p{index}",
            "scenario_id": "phase",
            "seed": 100 + index,
        }
        rows.append(identity)
        trial = deepcopy(packet["trials"][0])
        trial.update(identity)
        trials.append(trial)
    trials[-1]["events"][0]["sample_index"] = 1
    freeze["evaluation_contract"]["trial_manifest"]["development"] = rows
    freeze["evaluation_contract"]["perturbed_success_rate_min"] = 0.5
    packet["trials"] = trials
    resign(freeze, packet)
    result = judge_packet(freeze, packet)
    assert result["success_count"] == 9
    assert result["performance_gate"]["success_rate_passed"]
    assert not result["evidence_gate"]["passed"]
    assert result["status"] == "performance_not_met"
