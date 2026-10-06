"""Guidance projected from the current Kernel step; never execution authority."""

from pathlib import Path

from cfdc.i18n import Locale, t


def upload_requirements(report, locale: Locale = "zh-CN"):
    external = report.get("external_workflow") or {}
    active = external.get("active_request") or {}
    if active:
        request = active.get("execution_request") or {}
        manifest = active.get("manifest") or {}
        trials = manifest.get("trials") or request.get("trials") or []
        task = report.get("task") or {}
        units = {
            **(task.get("signal_units") or {}),
            **{
                name: task.get("input_units")
                or t("presentation.copy.as_declared_by_the_task", locale)
                for name in request.get("control_inputs", [])
            },
        }
        columns = [{"name": "trajectory.time_s", "unit": "s"}]
        for field, names in (
            ("outputs", request.get("tracked_signals", [])),
            ("measurements", request.get("measured_signals", [])),
            ("references", request.get("tracked_signals", [])),
            ("control_inputs", request.get("control_inputs", [])),
            ("raw_control_inputs", request.get("control_inputs", [])),
        ):
            columns.extend(
                {
                    "name": f"trajectory.{field}.{name}",
                    "unit": str(
                        units.get(
                            name, t("presentation.copy.as_declared_by_the_task", locale)
                        )
                    ),
                }
                for name in names
            )
        columns.extend(
            {"name": name, "unit": ""}
            for name in (
                "trajectory.controller_states",
                "trajectory.phase_ids",
                "events",
                "stop_event",
            )
        )
        return {
            "expected_format": t(
                "presentation.copy.an_evaluation_result_zip_with_the_original_manifest_json_and_the_following_per_trial_json_files_at_i",
                locale,
            ),
            "stage": active.get("stage"),
            "file_count": len(trials),
            "repeats": len(trials),
            "files": [
                {
                    "filename": "manifest.json",
                    "columns": [
                        {
                            "name": t(
                                "presentation.copy.preserve_the_binding_fields_from_the_execution_package_exactly",
                                locale,
                            ),
                            "unit": "",
                        }
                    ],
                },
                *[
                    {"filename": row.get("file", ""), "columns": columns}
                    for row in trials
                ],
            ],
        }

    handoffs = report.get("operator_handoffs") or []
    if not handoffs:
        return None
    card = handoffs[-1]
    units = card.get("units") or {}
    names = [
        "session_id",
        "protocol_fingerprint",
        "repeat",
        "time_s",
        *card.get("control_inputs", []),
        *card.get("requested_signals", []),
    ]
    columns = [
        {
            "name": name,
            "unit": (
                "s"
                if name == "time_s"
                else str(
                    (units.get("outputs") or {}).get(name)
                    or (
                        units.get("input", "")
                        if name in card.get("control_inputs", [])
                        else ""
                    )
                )
            ),
        }
        for name in names
    ]
    return {
        "expected_format": t(
            "presentation.copy.complete_repeated_trial_csv_json", locale
        ),
        "stage": "identification",
        "file_count": card.get("repeats", 0),
        "repeats": card.get("repeats", 0),
        "files": [
            {"filename": Path(path).name, "columns": columns}
            for path in card.get("template_paths", [])
        ],
    }


def workflow_guide(report, locale: Locale = "zh-CN"):
    if report.get("registered_case_binding"):
        return None
    action = (report.get("input_contract") or {}).get("action", "")
    status = report.get("status", "")
    if status in {"performance_met", "capability_gap", "cancelled"}:
        title, purpose, actor, next_step, rows = (
            t("presentation.copy.view_results_and_process_records", locale),
            t(
                "presentation.copy.review_the_outcome_based_on_accepted_data_independent_evaluation_and_replay",
                locale,
            ),
            t("presentation.copy.user", locale),
            t("presentation.copy.export_records_or_create_a_new_task", locale),
            [
                (
                    t("presentation.copy.view_results", locale),
                    t(
                        "presentation.copy.review_requirements_failure_reasons_and_capability_gaps_in_the_results_and_curves",
                        locale,
                    ),
                ),
                (
                    t("presentation.copy.download_records", locale),
                    t(
                        "presentation.copy.export_the_complete_public_package_downloading_does_not_change_the_task_outcome",
                        locale,
                    ),
                ),
            ],
        )
    elif action in {"answer", "submit_answer", "revise_diagnostic"}:
        title, purpose, actor, next_step, rows = (
            t("presentation.copy.describe_actual_observations", locale),
            t(
                "presentation.copy.use_observed_input_and_output_changes_to_help_determine_an_executable_collection_protocol",
                locale,
            ),
            t(
                "presentation.copy.the_user_describes_observations_the_system_parses_and_validates_them",
                locale,
            ),
            t(
                "presentation.copy.choose_a_data_source_and_compile_the_collection_protocol",
                locale,
            ),
            [
                (
                    t("presentation.copy.answer_the_current_question", locale),
                    t(
                        "presentation.copy.describe_observations_in_natural_language_for_the_diagnostic_question_shown_write_unknown_for_uncert",
                        locale,
                    ),
                ),
                (
                    t("presentation.copy.submit_diagnostics", locale),
                    t(
                        "presentation.copy.the_system_preserves_the_original_text_and_checks_the_diagnostic_evidence_the_next_specific_question",
                        locale,
                    ),
                ),
            ],
        )
    elif action in {"select_external_source", "set_provider"}:
        title, purpose, actor, next_step, rows = (
            t("presentation.copy.confirm_external_data_source", locale),
            t(
                "presentation.copy.bind_an_identification_and_evaluation_data_source_to_the_custom_task",
                locale,
            ),
            t(
                "presentation.copy.the_user_confirms_the_system_compiles_the_protocol",
                locale,
            ),
            t(
                "presentation.copy.download_the_collection_package_and_review_the_checklist",
                locale,
            ),
            [
                (
                    t("presentation.copy.choose_source", locale),
                    t(
                        "presentation.copy.choose_software_experiments_or_physical_measurements_to_match_the_actual_data_source",
                        locale,
                    ),
                ),
                (
                    t("presentation.copy.confirm_source", locale),
                    t(
                        "presentation.copy.the_system_generates_the_task_protocol_check_instructions_and_record_templates_it_does_not_select_a_",
                        locale,
                    ),
                ),
            ],
        )
    elif action in {
        "compile_protocol",
        "prepare_operator_handoff",
        "record_operator_report",
        "ingest_upload",
        "evidence",
    }:
        title, purpose, actor, next_step, rows = (
            t(
                "presentation.copy.collect_and_upload_evidence_under_the_protocol",
                locale,
            ),
            t(
                "presentation.copy.collect_sufficient_raw_input_and_output_records_for_feature_extraction_and_controller_qualification",
                locale,
            ),
            t(
                "presentation.copy.the_user_collects_data_externally_the_system_checks_uploads",
                locale,
            ),
            t(
                "presentation.copy.the_system_extracts_features_synthesizes_a_controller_and_checks_qualification",
                locale,
            ),
            [
                (
                    t("presentation.copy.download_collection_package", locale),
                    t(
                        "presentation.copy.download_the_current_collection_protocol_operating_instructions_and_csv_json_templates_check_channel",
                        locale,
                    ),
                ),
                (
                    t("presentation.copy.confirm_each_check", locale),
                    t(
                        "presentation.copy.complete_the_checks_in_your_software_or_physical_experiment_environment_and_submit_the_checklist_tru",
                        locale,
                    ),
                ),
                (
                    t("presentation.copy.collect_data_externally", locale),
                    t(
                        "presentation.copy.follow_the_protocol_input_sequence_and_repeat_count_preserving_all_original_records_do_not_modify_ta",
                        locale,
                    ),
                ),
                (
                    t("presentation.copy.upload_collection_results", locale),
                    t(
                        "presentation.copy.return_here_to_select_the_completed_csv_json_and_review_file_requirements_and_inspection_receipts_on",
                        locale,
                    ),
                ),
            ],
        )
    elif action in {"freeze", "freeze_controller"}:
        title, purpose, actor, next_step, rows = (
            t("presentation.copy.confirm_and_freeze_evaluation_conditions", locale),
            t(
                "presentation.copy.fix_the_controller_operating_region_performance_requirements_and_trial_budget",
                locale,
            ),
            t("presentation.copy.user_confirmation", locale),
            t(
                "presentation.copy.generate_and_download_the_development_evaluation_execution_package",
                locale,
            ),
            [
                (
                    t("presentation.copy.review_candidate", locale),
                    t(
                        "presentation.copy.review_the_generated_features_controller_and_qualification_results_without_manually_writing_intermed",
                        locale,
                    ),
                ),
                (
                    t("presentation.copy.confirm_freeze", locale),
                    t(
                        "presentation.copy.confirm_reference_values_boundaries_performance_metrics_and_repeats_later_uploads_must_not_change_fr",
                        locale,
                    ),
                ),
            ],
        )
    elif action in {"run_tuning", "run_feedback_iteration", "start_external_tuning"}:
        title, purpose, actor, next_step, rows = (
            t("presentation.copy.confirm_bounded_tuning_budget", locale),
            t(
                "presentation.copy.if_initial_evaluation_is_insufficient_try_improvements_in_the_fixed_candidate_order_within_the_exist",
                locale,
            ),
            t(
                "presentation.copy.the_user_confirms_the_system_generates_candidates",
                locale,
            ),
            t(
                "presentation.copy.download_the_current_candidate_execution_package_and_run_experiments_externally",
                locale,
            ),
            [
                (
                    t("presentation.copy.review_budget", locale),
                    t(
                        "presentation.copy.check_the_candidate_limit_repeats_per_round_minimum_improvement_and_termination_conditions",
                        locale,
                    ),
                ),
                (
                    t("presentation.copy.confirm_tuning", locale),
                    t(
                        "presentation.copy.for_each_round_download_the_candidate_package_execute_externally_and_upload_results_as_instructed_th",
                        locale,
                    ),
                ),
            ],
        )
    elif action in {
        "prepare_external_run",
        "submit_external_results",
        "evaluation",
        "confirmation",
        "run_evaluation",
        "run_confirmation",
    }:
        pending = (report.get("pending_actions") or [{}])[0]
        stage = (
            ((report.get("external_workflow") or {}).get("active_request") or {}).get(
                "stage"
            )
            or pending.get("stage")
            or (
                "fresh_confirmation"
                if pending.get("action") == "record_fresh_confirmation"
                or action in {"confirmation", "run_confirmation"}
                else "development"
            )
        )
        label = {
            "development": t("presentation.copy.development_evaluation", locale),
            "tuning_probe": t("presentation.copy.candidate_tuning", locale),
            "fresh_confirmation": t("presentation.copy.fresh_confirmation", locale),
        }.get(stage, t("presentation.copy.closed_loop_evaluation", locale))
        title, purpose, actor, next_step, rows = (
            t("presentation.copy.complete_the_experiment", locale, p0=label),
            t(
                "presentation.copy.collect_complete_closed_loop_trajectories_using_the_frozen_controller_and_fixed_trial_schedule",
                locale,
            ),
            t(
                "presentation.copy.the_user_executes_externally_the_system_evaluates_and_replays",
                locale,
            ),
            t(
                "presentation.copy.review_the_outcome_or_follow_the_page_to_the_next_candidate_and_fresh_confirmation",
                locale,
            ),
            [
                (
                    t(
                        "presentation.copy.download_experiment_execution_package",
                        locale,
                    ),
                    t(
                        "presentation.copy.the_package_contains_the_controller_execution_configuration_fixed_trial_list_instructions_and_result",
                        locale,
                    ),
                ),
                (
                    t("presentation.copy.execute_each_trial", locale),
                    t(
                        "presentation.copy.for_each_trial_record_outputs_references_actual_and_raw_control_inputs_controller_states_phases_and_",
                        locale,
                    ),
                ),
                (
                    t("presentation.copy.upload_executed_results", locale),
                    t(
                        "presentation.copy.upload_a_result_zip_containing_the_original_manifest_json_and_every_per_trial_json_for_this_round_do",
                        locale,
                    ),
                ),
                (
                    t("presentation.copy.review_validation_results", locale),
                    t(
                        "presentation.copy.the_system_validates_bindings_and_trajectories_evaluates_independently_then_replays_saved_data_if_re",
                        locale,
                    ),
                ),
            ],
        )
    else:
        title, purpose, actor, next_step, rows = (
            t("presentation.copy.complete_the_current_task_step", locale),
            t(
                "presentation.copy.proceed_according_to_the_current_kernel_state",
                locale,
            ),
            t(
                "presentation.copy.the_user_follows_the_page_instructions_the_system_validates",
                locale,
            ),
            t(
                "presentation.copy.follow_the_current_step_shown_after_completion",
                locale,
            ),
            [
                (
                    t("presentation.copy.review_current_step", locale),
                    t(
                        "presentation.copy.review_task_boundaries_current_requirements_and_missing_information_use_the_current_step_s_primary_b",
                        locale,
                    ),
                )
            ],
        )
    return {
        "title": title,
        "purpose": purpose,
        "actor": actor,
        "next_step": next_step,
        "steps": [
            {"title": title, "description": description} for title, description in rows
        ],
    }
