"""Pure, read-only presentation helpers for the guided Kernel WebUI."""

from __future__ import annotations

import html
import math
import re
from collections.abc import Mapping
from typing import Any

import plotly.graph_objects as go

from cfdc.evidence import GATE_DEFINITIONS
from cfdc.i18n import Locale, t
from cfdc.kernel.contracts import DIAGNOSTIC_IDS

_TERMINAL_STATES = frozenset({"performance_met", "capability_gap", "cancelled"})
_ACTION_ALIASES = {"submit_answer": "answer"}
_KNOWN_ACTIONS = frozenset(
    {
        "select_external_source",
        "prepare_external_run",
        "submit_external_results",
        "start_external_tuning",
        "restart_external_acquisition",
        "confirm_task",
        "answer",
        "relevance",
        "advance",
        "evidence",
        "phase",
        "features",
        "controller",
        "freeze",
        "evaluation",
        "cancel",
        "replay",
        "confirmation",
        "revise_diagnostic",
        "compile_protocol",
        "prepare_operator_handoff",
        "prepare_training_exercise_bundle",
        "record_operator_report",
        "ingest_upload",
        "derive_features",
        "synthesize_controller",
        "qualify_controller",
        "run_provider",
        "run_evaluation",
        "run_feedback_iteration",
        "confirm_result",
    }
)
_ACTION_COPY = {
    "select_external_source": (
        "presentation.copy.select_external_data_source",
        "presentation.copy.choose_software_simulation_or_externally_measured_data",
    ),
    "prepare_external_run": (
        "presentation.copy.prepare_external_experiment",
        "presentation.copy.download_the_frozen_request_and_execute_it_externally",
    ),
    "submit_external_results": (
        "presentation.copy.validate_external_results",
        "presentation.copy.upload_the_result_zip_bound_to_the_current_request",
    ),
    "start_external_tuning": (
        "presentation.copy.start_bounded_tuning",
        "presentation.copy.evaluate_candidates_under_the_frozen_contract",
    ),
    "restart_external_acquisition": (
        "presentation.copy.collect_evidence_again",
        "presentation.copy.create_a_new_task_and_confirm_its_boundaries_again",
    ),
    "confirm_task": (
        "presentation.copy.confirm_task_boundaries",
        "presentation.copy.confirm_the_objective_software_experiment_boundaries_and_budget_to_begin",
    ),
    "answer": (
        "presentation.copy.describe_known_observations",
        "presentation.copy.describe_observed_system_properties_explicitly_mark_uncertain_items_as_unknown",
    ),
    "relevance": (
        "presentation.copy.explain_irrelevant_items",
        "presentation.copy.explain_why_a_diagnostic_item_does_not_apply_to_this_task",
    ),
    "advance": (
        "presentation.copy.continue",
        "presentation.copy.proceed_to_the_next_stage_using_recorded_information",
    ),
    "evidence": (
        "presentation.copy.verifiable_evidence_required",
        "presentation.copy.prepare_public_experiment_records_matching_this_task_and_route_open_advanced_submission_for_required",
    ),
    "phase": (
        "presentation.copy.confirm_phase_plan",
        "presentation.copy.check_the_phase_objectives_before_continuing",
    ),
    "features": (
        "presentation.copy.record_features",
        "presentation.copy.submit_features_supported_by_public_evidence",
    ),
    "derive_features": (
        "presentation.copy.extract_features",
        "presentation.copy.extract_features_from_accepted_public_evidence",
    ),
    "controller": (
        "presentation.copy.submit_controller",
        "presentation.copy.submit_a_controller_description_satisfying_the_current_typed_contract",
    ),
    "synthesize_controller": (
        "presentation.copy.generate_controller",
        "presentation.copy.generate_a_candidate_controller_from_confirmed_features",
    ),
    "freeze": (
        "presentation.copy.freeze_candidate",
        "presentation.copy.freeze_the_controller_and_its_evaluation_conditions_for_independent_evaluation",
    ),
    "qualify_controller": (
        "presentation.copy.check_controller_qualification",
        "presentation.copy.run_deterministic_qualification_checks_before_freezing",
    ),
    "evaluation": (
        "presentation.copy.record_evaluation",
        "presentation.copy.submit_evaluation_data_bound_to_the_frozen_candidate",
    ),
    "run_evaluation": (
        "presentation.copy.run_development_evaluation",
        "presentation.copy.run_software_development_evaluation_under_the_frozen_evaluation_contract",
    ),
    "replay": (
        "presentation.copy.replay_evaluation_records",
        "presentation.copy.read_the_recorded_data_again_and_verify_the_evaluation_outcome",
    ),
    "confirmation": (
        "presentation.copy.submit_independent_confirmation",
        "presentation.copy.submit_fresh_confirmation_data_bound_to_the_frozen_candidate",
    ),
    "confirm_result": (
        "presentation.copy.run_independent_confirmation",
        "presentation.copy.use_reserved_trials_for_one_independent_confirmation_of_the_frozen_candidate",
    ),
    "run_feedback_iteration": (
        "presentation.copy.run_bounded_tuning",
        "presentation.copy.evaluate_candidates_within_predefined_bounds",
    ),
    "compile_protocol": (
        "presentation.copy.compile_experiment_protocol",
        "presentation.copy.compile_the_bounded_protocol_for_the_current_evidence_collection_step",
    ),
    "prepare_operator_handoff": (
        "presentation.copy.download_operator_package",
        "presentation.copy.download_the_current_protocol_and_operating_instructions",
    ),
    "prepare_training_exercise_bundle": (
        "presentation.copy.generate_exercise_bundle",
        "presentation.copy.generate_the_data_bundle_for_the_current_training_exercise",
    ),
    "record_operator_report": (
        "presentation.copy.confirm_operator_checks",
        "presentation.copy.record_the_pre_operation_check_results",
    ),
    "ingest_upload": (
        "presentation.copy.check_uploaded_data",
        "presentation.copy.check_uploaded_files_against_the_current_protocol",
    ),
    "run_provider": (
        "presentation.copy.run_current_step",
        "presentation.copy.run_the_currently_configured_deterministic_provider",
    ),
    "revise_diagnostic": (
        "presentation.copy.revise_diagnostics",
        "presentation.copy.revise_diagnostics_using_recorded_evidence",
    ),
    "cancel": (
        "presentation.copy.cancel_task",
        "presentation.copy.end_the_current_task",
    ),
}
_STAGE_BY_STATUS = {
    "intake": 0,
    "diagnostic": 0,
    "awaiting_evidence": 1,
    "protocol_ready": 1,
    "awaiting_operator_report": 1,
    "awaiting_provider": 1,
    "route_ready": 2,
    "controller_pending": 2,
    "controller_candidate_ready": 2,
    "controller_qualified": 2,
    "controller_ready": 2,
    "evaluation_recorded_pending_replay": 3,
    "tuning_eligible": 3,
    "awaiting_confirmation": 3,
    "performance_met": 3,
    "capability_gap": 3,
    "cancelled": 3,
}
_REQUIREMENT_LABELS = {
    "final_abs_error_max": "presentation.copy.final_absolute_error_at_most",
    "overshoot_max": "presentation.copy.overshoot_at_most",
    "settling_time_max_s": "presentation.copy.settling_time_at_most",
    "hold_duration_min_s": "presentation.copy.hold_duration_at_least",
    "hold_duration_s": "presentation.copy.hold_duration_at_least",
    "recovery_time_max_s": "presentation.copy.recovery_time_at_most",
    "perturbed_success_rate_min": "presentation.copy.perturbed_trial_success_rate_at_least",
    "success_rate_min": "presentation.copy.trial_success_rate_at_least",
    "worst_trial_violation_max": "presentation.copy.worst_trial_violation_at_most",
    "required_phase_count_min": "presentation.copy.completed_phase_count_at_least",
    "verified_handoff_count_min": "presentation.copy.verified_handoff_count_at_least",
    "goal_region_entry_required": "presentation.copy.must_enter_the_goal_region",
    "final_hold_duration_min_s": "presentation.copy.final_hold_duration_at_least",
    "recovery_abs_error_max": "presentation.copy.recovery_absolute_error_at_most",
    "post_recovery_hold_duration_min_s": "presentation.copy.post_recovery_hold_duration_at_least",
    "iae_max": "presentation.copy.integral_absolute_error_at_most",
    "peak_abs_input_max": "presentation.copy.peak_input_at_most",
    "peak_abs_output_max": "presentation.copy.peak_output_at_most",
    "saturation_duration_max_s": "presentation.copy.saturation_duration_at_most",
    "saturation_ratio_max": "presentation.copy.saturation_fraction_at_most",
}
_METRIC_LABELS = {
    "final_abs_error": "presentation.copy.final_absolute_error",
    "overshoot": "presentation.copy.overshoot",
    "settling_time_s": "presentation.copy.settling_time",
    "hold_duration_s": "presentation.copy.hold_duration",
    "iae": "presentation.copy.integral_absolute_error",
    "peak_abs_output": "presentation.copy.peak_absolute_output",
    "peak_abs_input": "presentation.copy.peak_absolute_input",
    "raw_peak_abs_input": "presentation.copy.peak_absolute_input_before_clipping",
    "saturation_duration_s": "presentation.copy.saturation_duration",
    "saturation_fraction": "presentation.copy.saturation_fraction",
    "completed_phase_count": "presentation.copy.completed_phases",
    "verified_handoff_count": "presentation.copy.verified_handoffs",
    "final_hold_duration_s": "presentation.copy.final_hold_duration",
    "entered_goal_region": "presentation.copy.entered_goal_region",
    "recovered_to_hold": "presentation.copy.recovered_and_held",
    "recovery_time_s": "presentation.copy.recovery_time",
    "post_recovery_hold_duration_s": "presentation.copy.post_recovery_hold_duration",
    "disturbance_event_verified": "presentation.copy.disturbance_event_verified",
}
_METRIC_REQUIREMENTS = {
    "final_abs_error": ("final_abs_error_max", "recovery_abs_error_max"),
    "overshoot": ("overshoot_max",),
    "settling_time_s": ("settling_time_max_s",),
    "hold_duration_s": ("hold_duration_min_s",),
    "iae": ("iae_max",),
    "peak_abs_output": ("peak_abs_output_max",),
    "peak_abs_input": ("peak_abs_input_max",),
    "saturation_duration_s": ("saturation_duration_max_s",),
    "saturation_fraction": ("saturation_ratio_max",),
    "completed_phase_count": ("required_phase_count_min",),
    "verified_handoff_count": ("verified_handoff_count_min",),
    "final_hold_duration_s": ("final_hold_duration_min_s",),
    "entered_goal_region": ("goal_region_entry_required",),
    "recovery_time_s": ("recovery_time_max_s",),
    "post_recovery_hold_duration_s": ("post_recovery_hold_duration_min_s",),
}
_TOP_LEVEL_METRICS = (
    "completed_phase_count",
    "verified_handoff_count",
    "final_hold_duration_s",
    "entered_goal_region",
    "recovered_to_hold",
    "recovery_time_s",
    "post_recovery_hold_duration_s",
    "disturbance_event_verified",
)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _items(value: Any) -> list[Any]:
    if isinstance(value, list | tuple):
        return list(value)
    return []


def _safe(value: Any) -> str:
    """Escape untrusted text for Markdown, including embedded HTML."""

    text = html.escape(str(value), quote=True)
    return re.sub(r"([\\`*_{}\[\]()#+.!|>\-])", r"\\\1", text)


def _plain(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _number(value: Any) -> str:
    if isinstance(value, bool):
        return _safe(value)
    if isinstance(value, int | float) and math.isfinite(float(value)):
        return f"{float(value):g}"
    return _safe(value)


def _unit_suffix(unit: Any) -> str:
    text = str(unit or "").strip()
    return f" {_safe(text)}" if text and text != "unspecified" else ""


def _named_signals(
    names: Any, units: Mapping[str, Any], locale: Locale = "zh-CN"
) -> str:
    values = []
    for name in _items(names):
        clean_name = str(name).strip()
        if not clean_name:
            continue
        unit = str(units.get(clean_name) or "").strip()
        rendered = _safe(clean_name)
        if unit and unit != "unspecified":
            rendered += f"（{_safe(unit)}）"
        values.append(rendered)
    return "、".join(values) if values else t("presentation.copy.not_provided", locale)


def _criterion_unit(
    task: Mapping[str, Any], key: str, signal: str | None = None
) -> str:
    if key.endswith("_s"):
        return "s"
    if {"rate", "ratio"}.intersection(key.split("_")):
        return "%"
    if key == "iae_max":
        base = _mapping(task.get("signal_units")).get(signal or "")
        return f"{base}·s" if base else ""
    if "input" in key:
        return str(task.get("input_units") or "")
    if any(marker in key for marker in ("error", "overshoot", "output")):
        signal_units = _mapping(task.get("signal_units"))
        if signal:
            return str(signal_units.get(signal) or "")
        units = {str(value) for value in signal_units.values() if value}
        return units.pop() if len(units) == 1 else ""
    return ""


def _criterion_value(
    task: Mapping[str, Any],
    key: str,
    value: Any,
    signal: str | None = None,
    locale: Locale = "zh-CN",
) -> str:
    if isinstance(value, bool):
        return (
            t("presentation.copy.yes", locale)
            if value
            else t("presentation.copy.no", locale)
        )
    if {"rate", "ratio"}.intersection(key.split("_")) and isinstance(
        value, int | float
    ):
        return _percent(value, locale=locale)
    return f"{_number(value)}{_unit_suffix(_criterion_unit(task, key, signal))}"


def _finite_numeric(value: Any) -> bool:
    return (
        isinstance(value, int | float)
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def _requirement_signals(task: Mapping[str, Any], key: str) -> set[str]:
    if "input" in key or "saturation" in key:
        names = _items(task.get("control_inputs"))
        if not names and task.get("control_input"):
            names = [task["control_input"]]
    else:
        names = _items(task.get("measured_signals"))
    return {str(name) for name in names if str(name).strip()}


def _requirement_text(
    requirements: Mapping[str, Any], task: Mapping[str, Any], locale: Locale = "zh-CN"
) -> str:
    rendered = []
    for raw_key, value in requirements.items():
        key = str(raw_key)
        label_key = _REQUIREMENT_LABELS.get(key)
        label = t(label_key, locale) if label_key is not None else None
        if label is None or value is None:
            continue
        if isinstance(value, Mapping):
            allowed_signals = _requirement_signals(task, key)
            safe_values = [
                (str(signal), item)
                for signal, item in value.items()
                if str(signal) in allowed_signals and _finite_numeric(item)
            ]
            if not safe_values:
                continue
            shown = "、".join(
                f"{_safe(signal)} {_criterion_value(task, key, item, signal, locale=locale)}"
                for signal, item in safe_values
            )
        elif key == "goal_region_entry_required":
            if not isinstance(value, bool):
                continue
            shown = _criterion_value(task, key, value, locale=locale)
        else:
            if not _finite_numeric(value):
                continue
            shown = _criterion_value(task, key, value, locale=locale)
        if key == "goal_region_entry_required" and value is True:
            rendered.append(label)
        else:
            rendered.append(f"{label} {shown}")
    return (
        "；".join(rendered) if rendered else t("presentation.copy.not_provided", locale)
    )


def task_summary(task: Mapping[str, Any], locale: Locale = "zh-CN") -> str:
    """Summarize only whitelisted, user-facing task fields."""

    task = _mapping(task)
    if not task:
        return t("presentation.copy.no_task_description_has_been_provided", locale)
    signal_units = _mapping(task.get("signal_units"))
    measured = _named_signals(task.get("measured_signals"), signal_units, locale=locale)
    control_names = task.get("control_inputs")
    if not _items(control_names) and task.get("control_input"):
        control_names = [task["control_input"]]
    input_unit = task.get("input_units")
    control_units = {
        str(name): input_unit for name in _items(control_names) if input_unit
    }
    controls = _named_signals(control_names, control_units, locale=locale)

    input_low = task.get("input_min")
    input_high = task.get("input_max")
    if input_low is None or input_high is None:
        missing = []
        if input_low is None:
            missing.append(
                t("presentation.copy.input_lower_bound_not_provided", locale)
            )
        if input_high is None:
            missing.append(
                t("presentation.copy.input_upper_bound_not_provided", locale)
            )
        input_bounds = "；".join(missing)
    else:
        input_bounds = (
            f"{_number(input_low)}–{_number(input_high)}{_unit_suffix(input_unit)}"
        )

    output_low = task.get("output_min")
    output_high = task.get("output_max")
    output_unit = None
    measured_names = _items(task.get("measured_signals"))
    if len(measured_names) == 1:
        output_unit = signal_units.get(str(measured_names[0]))
    output_parts = []
    output_parts.append(
        t("presentation.copy.output_lower_bound_not_provided", locale)
        if output_low is None
        else t(
            "presentation.copy.lower_bound",
            locale,
            p0=_number(output_low),
            p1=_unit_suffix(output_unit),
        )
    )
    output_parts.append(
        t("presentation.copy.output_upper_bound_not_provided", locale)
        if output_high is None
        else t(
            "presentation.copy.upper_bound",
            locale,
            p0=_number(output_high),
            p1=_unit_suffix(output_unit),
        )
    )

    reference = task.get("reference")
    goal_region = task.get("goal_region")
    control_target = _mapping(task.get("control_target"))
    if reference is not None:
        target = f"{_number(reference)}{_unit_suffix(output_unit)}"
    elif goal_region:
        target = _safe(goal_region)
    elif control_target:
        target = _safe(
            ", ".join(f"{key}={value}" for key, value in control_target.items())
        )
    else:
        target = t("presentation.copy.not_provided", locale)

    description = (
        task.get("description")
        or task.get("objective")
        or t("presentation.copy.not_provided", locale)
    )
    requirements = _mapping(task.get("success_requirements"))
    return "\n\n".join(
        (
            t("presentation.copy.objective", locale, p0=_safe(description)),
            t("presentation.copy.measured_signals", locale, p0=measured),
            t("presentation.copy.control_inputs", locale, p0=controls),
            t("presentation.copy.input_bounds", locale, p0=input_bounds),
            t("presentation.copy.output_bounds", locale, p0="；".join(output_parts)),
            t("presentation.copy.declared_target", locale, p0=target),
            t(
                "presentation.copy.acceptance_requirements",
                locale,
                p0=_requirement_text(requirements, task, locale=locale),
            ),
        )
    )


def _confirmed_success(report: Mapping[str, Any]) -> bool:
    confirmation = _mapping(report.get("confirmation"))
    evaluation = _mapping(report.get("evaluation"))
    packet_fingerprint = str(confirmation.get("packet_fingerprint") or "")
    if not (
        report.get("status") == "performance_met"
        and confirmation.get("status") == "performance_met"
        and evaluation.get("status") == "performance_met"
        and evaluation.get("evaluation_split") == "fresh_confirmation"
        and packet_fingerprint
    ):
        return False
    packet_bound = any(
        isinstance(packet, Mapping)
        and packet.get("packet_fingerprint") == packet_fingerprint
        and packet.get("evaluation_split") == "fresh_confirmation"
        for packet in _items(report.get("evaluation_packets"))
    )
    replay_bound = any(
        isinstance(replay, Mapping)
        and replay.get("packet_fingerprint") == packet_fingerprint
        and replay.get("evaluation_split") == "fresh_confirmation"
        and replay.get("matches_previous") is True
        for replay in _items(report.get("evaluation_replays"))
    )
    return packet_bound and replay_bound


def _workspace_copy(
    report: Mapping[str, Any], locale: Locale = "zh-CN"
) -> tuple[str, str]:
    status = str(report.get("status") or "")
    evaluation = _mapping(report.get("evaluation"))
    qualification = _mapping(report.get("qualification"))
    confirmation = _mapping(report.get("confirmation"))

    if status == "cancelled":
        return t("presentation.copy.task_cancelled", locale), t(
            "presentation.copy.this_task_has_ended_create_a_new_task_to_continue",
            locale,
        )
    if status == "evaluation_recorded_pending_replay":
        return t("presentation.copy.evaluation_recorded_awaiting_replay", locale), t(
            "presentation.copy.calculated_results_cannot_be_treated_as_final_until_replay_is_complete",
            locale,
        )
    if status == "awaiting_confirmation":
        return t(
            "presentation.copy.development_evaluation_complete_awaiting_independent_confirmation",
            locale,
        ), t(
            "presentation.copy.confirm_the_frozen_candidate_using_reserved_fresh_trials",
            locale,
        )
    if status == "awaiting_provider":
        return (
            t("presentation.copy.choose_a_new_data_source", locale),
            t(
                "presentation.copy.the_current_protocol_was_rejected_choose_a_new_data_source_through_a_supported_entry_point",
                locale,
            ),
        )
    if _confirmed_success(report):
        return t("presentation.copy.independent_confirmation_passed", locale), t(
            "presentation.copy.the_frozen_candidate_passed_independent_confirmation_using_fresh_trials",
            locale,
        )
    if confirmation.get("status") == "performance_not_met":
        return t("presentation.copy.independent_confirmation_failed", locale), t(
            "presentation.copy.fresh_confirmation_trials_did_not_meet_the_declared_requirements",
            locale,
        )
    if confirmation.get("status") == "replay_mismatch":
        return t(
            "presentation.copy.independent_confirmation_records_disagree", locale
        ), t(
            "presentation.copy.evaluation_replay_disagrees_with_the_original_record_results_cannot_be_released",
            locale,
        )
    if confirmation.get("status") == "pending_replay":
        return t(
            "presentation.copy.independent_confirmation_awaiting_replay", locale
        ), t(
            "presentation.copy.confirmation_data_is_recorded_results_cannot_be_released_before_replay_completes",
            locale,
        )
    if status == "capability_gap":
        tuning = _mapping(report.get("tuning"))
        if tuning.get("reason") == "no_strict_development_improvement":
            return t(
                "presentation.copy.bounded_tuning_found_no_candidate_for_confirmation",
                locale,
            ), t(
                "presentation.copy.no_candidate_met_the_predefined_improvement_threshold",
                locale,
            )
        if qualification and qualification.get("status") != "offline_qualified":
            return t("presentation.copy.controller_qualification_failed", locale), t(
                "presentation.copy.the_candidate_did_not_pass_the_recorded_offline_qualification_checks",
                locale,
            )
        return t("presentation.copy.current_capabilities_are_insufficient", locale), t(
            "presentation.copy.available_evidence_or_methods_are_insufficient_to_complete_this_task_safely",
            locale,
        )
    if evaluation.get("status") == "performance_not_met":
        stable = _mapping(evaluation.get("stability_gate")).get("passed") is True
        evidence = _mapping(evaluation.get("evidence_gate")).get("passed", True) is True
        if stable and evidence:
            return t(
                "presentation.copy.stable_performance_requirements_not_met", locale
            ), t(
                "presentation.copy.the_candidate_remained_stable_but_recorded_performance_did_not_meet_the_target",
                locale,
            )
        return t("presentation.copy.evaluation_failed", locale), t(
            "presentation.copy.a_stability_or_evidence_gate_failed_this_candidate_cannot_proceed_to_confirmation",
            locale,
        )
    if (
        evaluation.get("status") == "performance_met"
        and evaluation.get("evaluation_split") == "development"
    ):
        return t(
            "presentation.copy.development_evaluation_met_requirements", locale
        ), t(
            "presentation.copy.this_is_a_software_development_evaluation_fresh_independent_confirmation_is_still_required",
            locale,
        )
    if evaluation.get("status") == "performance_met":
        return t(
            "presentation.copy.confirmation_results_cannot_yet_be_released", locale
        ), t(
            "presentation.copy.confirmation_records_still_require_strict_binding_and_replay_verification",
            locale,
        )
    if qualification and qualification.get("status") != "offline_qualified":
        return t("presentation.copy.controller_qualification_failed", locale), t(
            "presentation.copy.the_candidate_did_not_pass_the_recorded_offline_qualification_checks",
            locale,
        )
    if status in {"awaiting_evidence", "protocol_ready", "awaiting_operator_report"}:
        return t("presentation.copy.more_evidence_is_required", locale), t(
            "presentation.copy.prepare_and_submit_auditable_data_under_the_current_protocol",
            locale,
        )
    if status == "intake":
        return t("presentation.copy.describe_the_objective_and_boundaries", locale), t(
            "presentation.copy.complete_the_objective_signals_and_safety_boundaries_before_continuing",
            locale,
        )
    if status == "diagnostic":
        return (
            t("presentation.copy.describe_observed_system_behavior", locale),
            t(
                "presentation.copy.describe_observed_stability_delay_coupling_and_other_properties_explicitly_mark_unknown_items",
                locale,
            ),
        )
    if status in _STAGE_BY_STATUS:
        return t(
            "presentation.copy.generating_and_validating_the_candidate", locale
        ), t(
            "presentation.copy.follow_the_current_guidance_to_complete_the_next_validation_step",
            locale,
        )
    return t("presentation.copy.current_state_cannot_be_safely_identified", locale), t(
        "presentation.copy.refresh_the_report_actions_remain_disabled_until_the_state_is_known",
        locale,
    )


def project_workspace(
    report: Mapping[str, Any], locale: Locale = "zh-CN"
) -> dict[str, Any]:
    """Project an authoritative Kernel report into the novice workspace model."""

    report = _mapping(report)
    contract = _mapping(report.get("input_contract"))
    status = str(report.get("status") or "")
    raw_action = str(contract.get("action") or "")
    action = _ACTION_ALIASES.get(raw_action, raw_action)
    disabled = bool(contract.get("disabled_reason"))
    actionable = bool(
        action
        and action in _KNOWN_ACTIONS
        and status in _STAGE_BY_STATUS
        and status not in _TERMINAL_STATES
        and not report.get("read_only")
        and not disabled
    )
    modes = [str(item) for item in _items(contract.get("allowed_modes"))]
    title, explanation = _workspace_copy(report, locale=locale)
    if report.get("read_only"):
        title = t("presentation.copy.read_only", locale, p0=title)
        explanation = t(
            "presentation.copy.this_task_is_read_only_so_actions_and_cancellation_are_unavailable",
            locale,
            p0=explanation,
        )
    action_title, action_help = _ACTION_COPY.get(
        action,
        (
            t("presentation.copy.current_action_unavailable", locale),
            t("presentation.copy.refresh_the_report_and_try_again", locale),
        ),
    )
    if action in _ACTION_COPY:
        action_title, action_help = (t(key, locale) for key in _ACTION_COPY[action])
    result_visible = bool(
        isinstance(report.get("evaluation"), Mapping)
        or isinstance(report.get("qualification"), Mapping)
        or isinstance(report.get("confirmation"), Mapping)
        or status in _TERMINAL_STATES
    )
    return {
        "stage": _STAGE_BY_STATUS.get(status, 0),
        "title": title,
        "explanation": explanation,
        "action": action,
        "action_title": action_title,
        "action_help": action_help,
        "actionable": actionable,
        "advanced": actionable
        and modes == ["json"]
        and action not in {"record_operator_report", "ingest_upload"},
        "result_visible": result_visible,
        "task_summary": task_summary(_mapping(report.get("task")), locale=locale),
    }


def input_contract_copy(
    contract: Mapping[str, Any], status: str, locale: Locale = "zh-CN"
) -> dict[str, Any]:
    """Localize known contract prose without altering action or validation fields."""
    result = dict(contract)
    action = str(contract.get("action") or "")
    canonical = _ACTION_ALIASES.get(action, action)
    if canonical in _ACTION_COPY:
        result["title"] = t(_ACTION_COPY[canonical][0], locale)
        if canonical == "confirm_task":
            guidance = "confirm_task"
        elif canonical == "answer":
            guidance = "answer"
        elif canonical == "relevance":
            guidance = "relevance"
        elif canonical in {
            "select_external_source",
            "prepare_external_run",
            "submit_external_results",
            "start_external_tuning",
            "restart_external_acquisition",
        }:
            guidance = "dedicated_form"
        elif not contract.get("allowed_modes"):
            guidance = "dedicated_button"
        else:
            guidance = "structured"
        result["guidance"] = t(f"presentation.contract.{guidance}", locale)
    disabled = contract.get("disabled_reason")
    if disabled:
        if not action and status in _TERMINAL_STATES:
            result["disabled_reason"] = t(
                "presentation.contract.terminal", locale, status=status
            )
        elif disabled == "当前没有待处理动作，请刷新页面。":
            result["disabled_reason"] = t("presentation.contract.no_action", locale)
        elif disabled == "当前 WebUI 尚未提供该实验动作的执行适配。":
            result["disabled_reason"] = t(
                "presentation.contract.unsupported_action", locale
            )
        elif disabled == f"未知待处理动作：{action}":
            result["disabled_reason"] = t(
                "presentation.contract.unknown_action", locale, action=action
            )
    template = _mapping(contract.get("json_template"))
    if canonical == "answer" and template:
        template = dict(template)
        annotations = {
            "assessment": ("可选字符串", "optional_text"),
            "evidence": ("用户原文摘录", "original_excerpt"),
            "confidence": ("0 到 1（可选）", "optional_confidence"),
        }
        for dimension in DIAGNOSTIC_IDS:
            fields = _mapping(template.get(dimension))
            if not fields:
                continue
            localized = dict(fields)
            for field, (original, key) in annotations.items():
                if fields.get(field) == original:
                    localized[field] = t(f"presentation.contract.{key}", locale)
            template[dimension] = localized
        candidates = template.get("parameter_candidates")
        if isinstance(candidates, list):
            replacements = {
                "value": ("用户原文中的数值", "original_value"),
                "unit": ("用户原文中的单位", "original_unit"),
                "source_text": ("原文摘录", "original_excerpt"),
            }
            template["parameter_candidates"] = [
                {
                    key: t(f"presentation.contract.{replacements[key][1]}", locale)
                    if key in replacements and value == replacements[key][0]
                    else value
                    for key, value in item.items()
                }
                if isinstance(item, Mapping)
                else item
                for item in candidates
            ]
        result["json_template"] = template
    elif (
        canonical == "relevance"
        and template.get("coupling_underactuation") == "不相关的确定性说明"
    ):
        result["json_template"] = {
            **template,
            "coupling_underactuation": t(
                "presentation.contract.irrelevance_explanation", locale
            ),
        }
    return result


def steps_html(report: Mapping[str, Any], locale: Locale = "zh-CN") -> str:
    """Render a semantic, noninteractive four-step progress indicator."""

    report = _mapping(report)
    task = _mapping(report.get("task"))
    task_done = bool(
        task.get("budget_confirmed")
        or report.get("protocols")
        or report.get("evidence")
        or report.get("route")
        or report.get("features")
        or report.get("controller")
        or report.get("qualification")
        or report.get("evaluation")
    )
    data_done = bool(
        report.get("route")
        or report.get("features")
        or report.get("controller")
        or report.get("qualification")
        or report.get("evaluation")
    )
    synthesis_done = isinstance(report.get("evaluation"), Mapping)
    if not task_done:
        current = 0
    elif not data_done:
        current = 1
    elif not synthesis_done:
        current = 2
    else:
        current = 3
    labels = (
        t("presentation.copy.describe_objective", locale),
        t("presentation.copy.prepare_data", locale),
        t("presentation.copy.generate_and_validate_candidate", locale),
        t("presentation.copy.view_results", locale),
    )
    rows = []
    for index, label in enumerate(labels):
        state = (
            "complete"
            if index < current
            else "current"
            if index == current
            else "pending"
        )
        current_attr = ' aria-current="step"' if index == current else ""
        rows.append(
            f'<li class="guided-step {state}"{current_attr}>'
            f'<span aria-hidden="true">{index + 1}</span><span>{label}</span></li>'
        )
    return (
        t("presentation.copy.ol_class_guided_steps_aria_label_task_progress", locale)
        + "".join(rows)
        + "</ol>"
    )


def _status_label(status: Any, locale: Locale = "zh-CN") -> str:
    return {
        "performance_met": t("presentation.copy.passed", locale),
        "performance_not_met": t("presentation.copy.failed", locale),
        "pending_replay": t("presentation.copy.awaiting_replay", locale),
        "replay_mismatch": t("presentation.copy.replay_mismatch", locale),
    }.get(str(status or ""), t("presentation.copy.not_recorded", locale))


def _percent(value: Any, locale: Locale = "zh-CN") -> str:
    if isinstance(value, int | float) and not isinstance(value, bool):
        return f"{100 * float(value):g}%"
    return t("presentation.copy.not_recorded", locale)


def _metric_target(
    report: Mapping[str, Any],
    metric: str,
    signal: str | None = None,
    locale: Locale = "zh-CN",
) -> str:
    requirement_names = _METRIC_REQUIREMENTS.get(metric, ())
    if not requirement_names:
        if metric in {
            "recovered_to_hold",
            "disturbance_event_verified",
        }:
            return t("presentation.copy.must_be_yes", locale)
        return t("presentation.copy.not_declared", locale)
    task = _mapping(report.get("task"))
    requirements = _mapping(task.get("success_requirements"))
    requirement = next(
        (name for name in requirement_names if requirements.get(name) is not None),
        None,
    )
    if requirement is None:
        return t("presentation.copy.not_declared", locale)
    value = requirements[requirement]
    if isinstance(value, Mapping):
        value = value.get(signal) if signal is not None else None
    if value is None:
        return t("presentation.copy.not_declared", locale)
    if requirement == "goal_region_entry_required":
        return (
            t("presentation.copy.must_be_yes", locale)
            if value is True
            else t("presentation.copy.not_declared", locale)
        )
    relation = (
        t("presentation.copy.at_least", locale)
        if requirement.endswith(("_min", "_min_s"))
        else t("presentation.copy.at_most", locale)
    )
    return f"{relation} {_criterion_value(task, requirement, value, signal, locale=locale)}"


def _metric_value(
    report: Mapping[str, Any],
    metric: str,
    value: Any,
    signal: str | None = None,
    locale: Locale = "zh-CN",
) -> str:
    if isinstance(value, bool):
        return (
            t("presentation.copy.yes", locale)
            if value
            else t("presentation.copy.no", locale)
        )
    task = _mapping(report.get("task"))
    if metric in {"saturation_fraction"} and isinstance(value, int | float):
        return _percent(value, locale=locale)
    if metric in {
        "settling_time_s",
        "hold_duration_s",
        "saturation_duration_s",
        "final_hold_duration_s",
        "recovery_time_s",
        "post_recovery_hold_duration_s",
    }:
        unit = "s"
    elif metric == "iae":
        base = _mapping(task.get("signal_units")).get(signal or "")
        unit = f"{base}·s" if base else ""
    elif metric in {"peak_abs_input", "raw_peak_abs_input"}:
        unit = str(task.get("input_units") or "")
    elif metric in {"final_abs_error", "overshoot", "peak_abs_output"}:
        unit = str(_mapping(task.get("signal_units")).get(signal or "") or "")
    else:
        unit = ""
    return f"{_number(value)}{_unit_suffix(unit)}"


def _recorded_metric_rows(
    report: Mapping[str, Any], evaluation: Mapping[str, Any], locale: Locale = "zh-CN"
) -> list[list[Any]]:
    rows: list[list[Any]] = []
    for trial_index, trial in enumerate(_items(evaluation.get("trials")), 1):
        if not isinstance(trial, Mapping):
            continue
        trial_id = _plain(
            trial.get("trial_id")
            or t("presentation.copy.trial", locale, p0=trial_index)
        )
        metrics = _mapping(trial.get("metrics"))
        for group_name, group in (
            (t("presentation.copy.output", locale), _mapping(metrics.get("channels"))),
            (t("presentation.copy.input", locale), _mapping(metrics.get("inputs"))),
        ):
            for signal, values in group.items():
                if not isinstance(values, Mapping):
                    continue
                for metric, value in values.items():
                    if metric not in _METRIC_LABELS or value is None:
                        continue
                    rows.append(
                        [
                            f"{_plain(signal)} · {t(_METRIC_LABELS[metric], locale)}",
                            _metric_target(report, metric, str(signal), locale=locale),
                            _metric_value(
                                report, metric, value, str(signal), locale=locale
                            ),
                            t(
                                "presentation.copy.recorded_metrics_for",
                                locale,
                                p0=trial_id,
                                p1=group_name,
                            ),
                        ]
                    )
        for metric in _TOP_LEVEL_METRICS:
            if metrics.get(metric) is not None:
                rows.append(
                    [
                        t(_METRIC_LABELS[metric], locale),
                        _metric_target(report, metric, locale=locale),
                        _metric_value(report, metric, metrics[metric], locale=locale),
                        t(
                            "presentation.copy.recorded_metrics_for_2",
                            locale,
                            p0=trial_id,
                        ),
                    ]
                )
    return rows


def result_rows(
    report: Mapping[str, Any], selection: str | None = None, locale: Locale = "zh-CN"
) -> list[list[Any]]:
    """Return recorded result rows without deriving metrics from trajectories."""

    report = _mapping(report)
    evaluation = _mapping(report.get("evaluation"))
    confirmation = _mapping(report.get("confirmation"))
    if not evaluation and not confirmation:
        return []
    split = str(evaluation.get("evaluation_split") or "")
    phase = (
        t("presentation.copy.independent_confirmation", locale)
        if split == "fresh_confirmation" or confirmation
        else t("presentation.copy.development_evaluation", locale)
    )
    if report.get("status") == "evaluation_recorded_pending_replay":
        status = "pending_replay"
    else:
        status = (
            confirmation.get("status") if confirmation else evaluation.get("status")
        )
    rows: list[list[Any]] = [
        [
            t("presentation.copy.outcome", locale),
            t(
                "presentation.copy.pass_the_recorded_stability_evidence_and_performance_gates",
                locale,
            ),
            _status_label(status, locale=locale),
            t("presentation.copy.recorded_outcome_of", locale, p0=phase),
        ]
    ]
    performance = _mapping(evaluation.get("performance_gate"))
    if evaluation.get("success_rate") is not None:
        minimum = performance.get("success_rate_min")
        rows.append(
            [
                t("presentation.copy.trial_success_rate", locale),
                _percent(minimum, locale=locale)
                if minimum is not None
                else t("presentation.copy.not_declared", locale),
                _percent(evaluation.get("success_rate"), locale=locale),
                t("presentation.copy.recorded_summary_of", locale, p0=phase),
            ]
        )
    if evaluation.get("wilson_lower_bound_95") is not None:
        rows.append(
            [
                t("presentation.copy.95_wilson_lower_bound_for_success_rate", locale),
                _percent(performance.get("success_rate_min"), locale=locale)
                if performance.get("success_rate_min") is not None
                else t("presentation.copy.not_declared", locale),
                _percent(evaluation.get("wilson_lower_bound_95"), locale=locale),
                t(
                    "presentation.copy.recorded_conservative_lower_bound_for_success_rate",
                    locale,
                ),
            ]
        )
    metric_evaluation = evaluation
    if selection is not None:
        _, selected_trial = _selected_trial(report, selection, locale=locale)
        if selected_trial:
            trial_id = str(selected_trial.get("trial_id") or "")
            metric_trial = selected_trial
            if not _mapping(selected_trial.get("metrics")) and trial_id:
                metric_trial = next(
                    (
                        trial
                        for trial in _items(evaluation.get("trials"))
                        if isinstance(trial, Mapping)
                        and str(trial.get("trial_id") or "") == trial_id
                    ),
                    selected_trial,
                )
            metric_evaluation = {**evaluation, "trials": [metric_trial]}
    metric_rows = _recorded_metric_rows(report, metric_evaluation, locale=locale)
    rows.extend(metric_rows)
    if evaluation and not metric_rows:
        rows.append(
            [
                t("presentation.copy.trial_metrics", locale),
                t("presentation.copy.under_the_frozen_evaluation_contract", locale),
                t("presentation.copy.not_recorded", locale),
                t(
                    "presentation.copy.the_current_evaluation_provides_no_per_trial_metrics_trajectories_were_not_used_to_recalculate_them",
                    locale,
                ),
            ]
        )
    return rows


def _packet_order(report: Mapping[str, Any]) -> list[int]:
    packets = _items(report.get("evaluation_packets"))
    linked = str(_mapping(report.get("confirmation")).get("packet_fingerprint") or "")
    preferred: list[int] = []
    if linked:
        preferred.extend(
            index
            for index, packet in enumerate(packets)
            if isinstance(packet, Mapping)
            and packet.get("packet_fingerprint") == linked
            and packet.get("evaluation_split") == "fresh_confirmation"
        )
    evaluation = _mapping(report.get("evaluation"))
    current = str(evaluation.get("packet_fingerprint") or "")
    if current and evaluation.get("evaluation_split") == "development":
        preferred.extend(
            index
            for index, packet in enumerate(packets)
            if isinstance(packet, Mapping)
            and packet.get("packet_fingerprint") == current
            and packet.get("evaluation_split") == "development"
        )
    preferred.extend(
        index
        for index in reversed(range(len(packets)))
        if isinstance(packets[index], Mapping)
        and packets[index].get("evaluation_split") == "development"
    )
    preferred.extend(reversed(range(len(packets))))
    return list(dict.fromkeys(preferred))


def evaluation_options(
    report: Mapping[str, Any], locale: Locale = "zh-CN"
) -> list[tuple[str, str]]:
    """List stable packet/trial selections with their true evaluation phase."""

    report = _mapping(report)
    packets = _items(report.get("evaluation_packets"))
    labels = {
        "development": t("presentation.copy.development_evaluation", locale),
        "fresh_confirmation": t("presentation.copy.independent_confirmation", locale),
        "replay": t("presentation.copy.replay_check", locale),
    }
    options: list[tuple[str, str]] = []
    for packet_index in _packet_order(report):
        packet = packets[packet_index]
        split = str(packet.get("evaluation_split") or "")
        phase = labels.get(
            split, t("presentation.copy.unrecognized_evaluation", locale)
        )
        for trial_index, trial in enumerate(_items(packet.get("trials"))):
            if not isinstance(trial, Mapping):
                continue
            trial_id = _plain(
                trial.get("trial_id")
                or t("presentation.copy.trial", locale, p0=trial_index + 1)
            )
            options.append(
                (
                    t(
                        "presentation.copy.trial_2",
                        locale,
                        p0=phase,
                        p1=trial_index + 1,
                        p2=trial_id,
                    ),
                    f"{packet_index}:{trial_index}",
                )
            )
    return options


def _selected_trial(
    report: Mapping[str, Any], selection: str | None, locale: Locale = "zh-CN"
) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    packets = _items(report.get("evaluation_packets"))
    allowed = {value for _, value in evaluation_options(report, locale=locale)}
    chosen = str(selection or "")
    if chosen not in allowed:
        options = evaluation_options(report, locale=locale)
        chosen = options[0][1] if options else ""
    try:
        packet_index, trial_index = (int(item) for item in chosen.split(":"))
        packet = packets[packet_index]
        trial = _items(packet.get("trials"))[trial_index]
    except (AttributeError, IndexError, TypeError, ValueError):
        return {}, {}
    if not isinstance(packet, Mapping) or not isinstance(trial, Mapping):
        return {}, {}
    return packet, trial


def signal_options(
    report: Mapping[str, Any], selection: str | None, locale: Locale = "zh-CN"
) -> list[str]:
    """List output signals present in the selected recorded trial."""

    _, trial = _selected_trial(_mapping(report), selection, locale=locale)
    outputs = _mapping(_mapping(trial.get("trajectory")).get("outputs"))
    return [str(name) for name, values in outputs.items() if isinstance(values, list)]


def _signal_unit(
    report: Mapping[str, Any], trial: Mapping[str, Any], signal: str, *, control: bool
) -> str:
    task = _mapping(report.get("task"))
    if control:
        unit = task.get("input_units")
    else:
        unit = _mapping(task.get("signal_units")).get(signal)
    for container in (trial, _mapping(trial.get("trajectory"))):
        units = _mapping(container.get("units"))
        if control:
            unit = units.get("input", unit)
        else:
            outputs = _mapping(units.get("outputs"))
            unit = outputs.get(signal, units.get(signal, unit))
    text = str(unit or "").strip()
    return "" if text == "unspecified" else _plain(text)


def _base_figure(title: str, locale: Locale = "zh-CN") -> go.Figure:
    figure = go.Figure()
    figure.update_layout(
        height=320,
        margin={"l": 48, "r": 18, "t": 48, "b": 42},
        title=title,
        xaxis_title=t("presentation.copy.time_s", locale),
    )
    return figure


def evaluation_figures(
    report: Mapping[str, Any],
    selection: str | None = None,
    signal: str | None = None,
    locale: Locale = "zh-CN",
) -> tuple[go.Figure, go.Figure]:
    """Plot one recorded output/reference and its recorded control inputs."""

    report = _mapping(report)
    output_figure = _base_figure(
        t("presentation.copy.output_and_target", locale), locale=locale
    )
    control_figure = _base_figure(
        t("presentation.copy.control_inputs_2", locale), locale=locale
    )
    _, trial = _selected_trial(report, selection, locale=locale)
    trajectory = _mapping(trial.get("trajectory"))
    time_s = trajectory.get("time_s")
    if not isinstance(time_s, list):
        return output_figure, control_figure
    outputs = _mapping(trajectory.get("outputs"))
    available = [
        str(name) for name, values in outputs.items() if isinstance(values, list)
    ]
    selected = str(signal or "")
    if selected not in available:
        selected = available[0] if available else ""
    values = outputs.get(selected)
    if isinstance(values, list) and len(values) == len(time_s):
        output_figure.add_scatter(
            x=time_s, y=values, mode="lines", name=_plain(selected)
        )
        references = _mapping(trajectory.get("references"))
        reference = references.get(selected)
        if isinstance(reference, list) and len(reference) == len(time_s):
            output_figure.add_scatter(
                x=time_s,
                y=reference,
                mode="lines",
                line={"dash": "dash"},
                name=t("presentation.copy.target", locale),
            )
        output_unit = _signal_unit(report, trial, selected, control=False)
        output_figure.update_yaxes(
            title=f"{_plain(selected)} ({output_unit})"
            if output_unit
            else _plain(selected)
        )
    controls = _mapping(trajectory.get("control_inputs"))
    control_units = []
    for name, control_values in controls.items():
        if not isinstance(control_values, list) or len(control_values) != len(time_s):
            continue
        clean_name = str(name)
        control_figure.add_scatter(
            x=time_s, y=control_values, mode="lines", name=_plain(clean_name)
        )
        unit = _signal_unit(report, trial, clean_name, control=True)
        if unit and unit not in control_units:
            control_units.append(unit)
    control_figure.update_yaxes(
        title=t(
            "presentation.copy.control_inputs_3", locale, p0=" / ".join(control_units)
        )
        if control_units
        else t("presentation.copy.control_inputs_2", locale)
    )
    return output_figure, control_figure


def upload_feedback(report: Mapping[str, Any], locale: Locale = "zh-CN") -> str:
    """Explain the latest authoritative upload audit and its next repair."""

    attempts = _items(_mapping(report).get("upload_attempts"))
    if not attempts or not isinstance(attempts[-1], Mapping):
        return t("presentation.copy.no_upload_inspection_has_been_recorded", locale)
    audit = _mapping(attempts[-1].get("audit")) or attempts[-1]
    gates = [gate for gate in _items(audit.get("gates")) if isinstance(gate, Mapping)]
    passed = sum(gate.get("status") == "passed" for gate in gates)
    unreached = sum(gate.get("status") == "not_reached" for gate in gates)
    status = str(audit.get("status") or "")
    if status == "accepted":
        return t(
            "presentation.copy.upload_accepted_checks_passed_rejected_data_was_not_counted_as_evidence",
            locale,
            p0=passed,
        )
    failed_id = str(audit.get("failed_gate") or "")
    definition = GATE_DEFINITIONS.get(failed_id)
    failed_gate = next((gate for gate in gates if gate.get("id") == failed_id), {})
    label = (
        t(f"presentation.gate.{failed_id}.label", locale)
        if definition
        else failed_gate.get("label") or t("presentation.copy.unknown_check", locale)
    )
    redo = (
        t(f"presentation.gate.{failed_id}.redo", locale)
        if definition
        else failed_gate.get("redo")
        or t("presentation.copy.prepare_new_data_under_the_current_protocol", locale)
    )
    binding = _mapping(report.get("registered_case_binding"))
    if failed_id == "file_format" and binding.get("evidence_mode") == "exercise_bundle":
        redo = t(
            "presentation.copy.download_and_upload_the_complete_training_exercise_zip_generated_by_the_current_protocol_preserving_",
            locale,
        )
    details = str(failed_gate.get("details") or audit.get("message") or "").strip()
    parts = [
        t(
            "presentation.copy.upload_rejected_the_check_failed",
            locale,
            p0=_safe(label),
        ),
        t("presentation.copy.recommended_action", locale, p0=_safe(redo)),
        t(
            "presentation.copy.check_progress_passed_not_yet_checked",
            locale,
            p0=passed,
            p1=unreached,
        ),
    ]
    if details:
        parts.append(
            t("presentation.copy.technical_details", locale, p0=_safe(details))
        )
    return "\n\n".join(parts)


def trace_preview(
    report: Mapping[str, Any], locale: Locale = "zh-CN"
) -> tuple[list[str], list[list[Any]]]:
    """Preview at most twenty samples from the latest accepted public trace."""

    for evidence in reversed(_items(_mapping(report).get("evidence"))):
        if not isinstance(evidence, Mapping):
            continue
        if "status" in evidence and evidence.get("status") not in {
            "accepted",
            "passed",
            "valid",
        }:
            continue
        trace = _mapping(evidence.get("trace"))
        time_s = trace.get("time_s")
        signals = _mapping(trace.get("signals"))
        if not isinstance(time_s, list) or not time_s or not signals:
            continue
        valid_signals = [
            str(name)
            for name, values in signals.items()
            if isinstance(values, list) and len(values) == len(time_s)
        ]
        if not valid_signals:
            continue
        trial = _plain(
            evidence.get("trial_id")
            or trace.get("trial_id")
            or t("presentation.copy.unlabeled_trial", locale)
        )
        headers = [
            t("presentation.copy.time_s", locale),
            t("presentation.copy.trial_3", locale),
            *[_plain(name) for name in valid_signals],
        ]
        rows = [
            [time_s[index], trial, *[signals[name][index] for name in valid_signals]]
            for index in range(min(20, len(time_s)))
        ]
        return headers, rows
    return [t("presentation.copy.time_s", locale)], []


def protocol_summary(
    report: Mapping[str, Any], *, request_upload: bool = True, locale: Locale = "zh-CN"
) -> str:
    """Summarize the active protocol without exposing a hardware command."""

    report = _mapping(report)
    protocols = _items(report.get("protocols"))
    active_fingerprint = str(report.get("active_protocol_fingerprint") or "")
    protocol = next(
        (
            item
            for item in protocols
            if isinstance(item, Mapping)
            and active_fingerprint
            and item.get("protocol_fingerprint") == active_fingerprint
        ),
        None,
    )
    if protocol is None:
        return t(
            "presentation.copy.no_executable_experiment_protocol_is_available_yet",
            locale,
        )
    units = _mapping(protocol.get("units"))
    output_units = _mapping(units.get("outputs"))
    requested = _named_signals(
        protocol.get("requested_signals"), output_units, locale=locale
    )
    control_names = protocol.get("control_inputs")
    control_units = {str(name): units.get("input") for name in _items(control_names)}
    controls = _named_signals(control_names, control_units, locale=locale)
    repeats = protocol.get("repeats")
    sample_period = protocol.get("sample_period_s")
    exercise = (
        _mapping(report.get("registered_case_binding")).get("evidence_mode")
        == "exercise_bundle"
    )
    file_type = (
        t("presentation.copy.training_exercise_zip", locale)
        if exercise
        else t("presentation.copy.csv_or_json", locale)
    )
    lines = [
        t("presentation.copy.measured_signals_2", locale, p0=requested),
        t("presentation.copy.control_input_records", locale, p0=controls),
        t(
            "presentation.copy.independent_repeats",
            locale,
            p0=_number(repeats)
            if repeats is not None
            else t("presentation.copy.not_provided", locale),
        ),
        t(
            "presentation.copy.sample_interval_s",
            locale,
            p0=_number(sample_period)
            if sample_period is not None
            else t("presentation.copy.not_provided", locale),
        ),
        t(
            "presentation.copy.data_kind_upload_format",
            locale,
            p0=_safe(
                protocol.get("data_kind") or t("presentation.copy.not_provided", locale)
            ),
            p1=file_type,
        ),
    ]
    if request_upload:
        lines.append(
            t(
                "presentation.copy.download_the_current_operator_package_collect_or_prepare_data_under_its_protocol_then_upload_it",
                locale,
            )
        )
    return "\n".join(lines)


__all__ = [
    "evaluation_figures",
    "evaluation_options",
    "input_contract_copy",
    "project_workspace",
    "protocol_summary",
    "result_rows",
    "signal_options",
    "steps_html",
    "task_summary",
    "trace_preview",
    "upload_feedback",
]
