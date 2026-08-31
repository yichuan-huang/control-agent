from __future__ import annotations

import json

import pytest

from cfdc.agents import AgentReviewBlocked, AgentRuntime, CompositeAgentAdapter
from cfdc.kernel import (
    AgentRole,
    CallableExperimentProvider,
    ControllerIR,
    DiagnosticLedger,
    EvidenceSession,
    KernelAgentCoordinator,
    ProviderRegistry,
    PublicTrace,
    TaskContract,
    TuningContract,
    WorkflowService,
    build_migration_manifest,
    compile_phase_plan,
    evidence_from_trace,
    run_bounded_tuning,
    validate_handoff,
)
from cfdc.kernel.service import _boolean_sequence
from cfdc.models import SystemDescription


def test_task_contract_rejects_adjacent_task_types() -> None:
    with pytest.raises(ValueError, match="unsupported_task_type"):
        TaskContract.from_user_input(
            {
                "description": "Track a periodic trajectory",
                "task_type": "periodic_operation",
                "measured_signals": ["output"],
                "control_input": "input",
            }
        )


def test_migration_manifest_covers_dynamic_route_and_schema_resources() -> None:
    manifest = build_migration_manifest("archive/CFDC_Project_v3")
    sources = {item["source"] for item in manifest["items"]}
    assert {
        "src/control_route_registry.py",
        "control_route_registry.json",
        "control_route_extensions.json",
        "unified_executor_capabilities.json",
        "cfdc_loop_schema.json",
        "diagnostic_ledger_schema.json",
        "performance_evaluation_packet_schema.json",
    } <= sources
    assert all(item["source_hash"] for item in manifest["items"])
    assert manifest["runtime_archive_dependency"] is False


def test_diagnostic_ledger_requires_all_eight_dimensions() -> None:
    ledger = DiagnosticLedger.initial()
    assert len(ledger.entries) == 8
    assert ledger.readiness().status == "diagnostic_blocker"
    assert "open_loop_stability" in ledger.readiness().unresolved_dimension_ids


def test_not_relevant_is_deterministic_and_scoped() -> None:
    ledger = DiagnosticLedger.initial()
    updated = ledger.apply_not_relevant(
        {"coupling_underactuation": "SISO interface has one input and one output"},
        task_type="local_setpoint_hold",
        measured_signals=("output",),
        control_input="input",
    )
    item = updated.entry("coupling_underactuation")
    assert item.status == "not_relevant"
    assert item.blocking_for_current_route is False
    assert updated.entry("open_loop_stability").status == "unknown"


def test_not_relevant_dimensions_do_not_block_when_remaining_evidence_is_known() -> None:
    ledger = DiagnosticLedger.initial().apply_not_relevant(
        {"coupling_underactuation": "SISO interface"},
        task_type="local_setpoint_hold",
        measured_signals=("output",),
        control_input="input",
    )
    updates = {
        dimension.id: {
            "status": "known",
            "evidence": f"stable {dimension.id}",
            "confidence": 0.9,
        }
        for dimension in ledger.entries
        if dimension.id != "coupling_underactuation"
    }
    resolved = ledger.update(updates, source="human_operator")
    assert resolved.readiness().status == "ready"


def test_workflow_session_is_revisioned_and_duplicate_action_is_idempotent(tmp_path) -> None:
    service = WorkflowService(tmp_path)
    task = service.start(
        {
            "description": "Keep the output near a setpoint.",
            "task_type": "local_setpoint_hold",
            "measured_signals": ["output"],
            "control_input": "input",
            "input_min": -1,
            "input_max": 1,
            "state_stop": 3,
        }
    )
    first = service.submit_answer(
        task.session_id,
        action_id="answer-1",
        revision=task.revision,
        answer={"open_loop_stability": "unknown"},
    )
    repeated = service.submit_answer(
        task.session_id,
        action_id="answer-1",
        revision=task.revision,
        answer={"open_loop_stability": "unknown"},
    )
    assert first.revision == repeated.revision
    assert len(first.events) == len(repeated.events)
    with pytest.raises(ValueError, match="stale_revision"):
        service.submit_answer(
            task.session_id,
            action_id="answer-2",
            revision=task.revision,
            answer={"relative_degree": "unknown"},
        )


def test_session_round_trip_and_old_payload_is_read_only(tmp_path) -> None:
    service = WorkflowService(tmp_path)
    task = service.start(
        {
            "description": "Keep output stable.",
            "measured_signals": ["output"],
            "control_input": "input",
            "input_min": -1,
            "input_max": 1,
            "state_stop": 3,
        }
    )
    restored = EvidenceSession.from_json(task.to_json())
    assert restored.session_id == task.session_id
    old = tmp_path / "old-session.json"
    old.write_text(json.dumps({"schema_version": "4.0", "status": "complete"}), encoding="utf-8")
    imported = service.import_legacy(old)
    assert imported.read_only is True
    with pytest.raises(ValueError, match="read_only"):
        service.submit_answer(imported.session_id, action_id="x", revision=0, answer={})


def _resolved_session(service: WorkflowService):
    session = service.start(
        {
            "description": "Keep the output near a setpoint.",
            "measured_signals": ["output"],
            "control_input": "input",
            "input_min": -1,
            "input_max": 1,
            "state_stop": 3,
        }
    )
    answers = {
        dimension.id: {
            "status": "known",
            "evidence": f"confirmed {dimension.id}",
            "confidence": 0.9,
        }
        for dimension in session.ledger.entries
    }
    session = service.submit_answer(
        session.session_id,
        action_id="answer-all",
        revision=session.revision,
        answer=answers,
    )
    return service.advance(session.session_id, action_id="advance", revision=session.revision)


def test_route_freeze_and_independent_judge_are_bound_to_public_evidence(tmp_path) -> None:
    service = WorkflowService(tmp_path)
    session = service.start(
        {
            "description": "Keep a stable scalar output at a setpoint.",
            "measured_signals": ["output"],
            "control_input": "input",
        }
    )
    answers = {
        "open_loop_stability": {"status": "known", "assessment": "stable", "evidence": "stable", "confidence": 0.9},
        "nonminimum_phase": {"status": "known", "assessment": "minimum_phase", "evidence": "minimum phase", "confidence": 0.9},
        "significant_delay": {"status": "known", "assessment": "not_significant", "evidence": "no significant delay", "confidence": 0.9},
        "relative_degree": {"status": "known", "assessment": "low", "evidence": "low order", "confidence": 0.9},
        "sensing_actuation_adequacy": {"status": "known", "assessment": "adequate", "evidence": "adequate", "confidence": 0.9},
        "nonlinearity_strength": {"status": "known", "assessment": "weak", "evidence": "weak", "confidence": 0.9},
        "coupling_underactuation": {"status": "known", "assessment": "siso", "evidence": "SISO", "confidence": 0.9},
        "uncertainty_variation": {"status": "known", "assessment": "small", "evidence": "small", "confidence": 0.9},
    }
    session = service.submit_answer(session.session_id, action_id="answer", revision=session.revision, answer=answers)
    session = service.advance(session.session_id, action_id="advance", revision=session.revision)
    assert session.status == "route_ready"
    evidence = service.submit_evidence(
        session.session_id,
        action_id="evidence-1",
        revision=session.revision,
        evidence={
            "evidence_id": "trace-1",
            "kind": "experiment",
            "source": "model",
            "protocol_fingerprint": "protocol-1",
            "signal_units": {"time": "s", "output": "unit"},
        },
    )
    frozen = service.freeze_controller(
        evidence.session_id,
        action_id="freeze-1",
        revision=evidence.revision,
        controller={"family": "PI", "parameters": {"kp": 1.0, "ki": 0.1}},
        runtime_contract={"command_bounds": [-1.0, 1.0]},
        evaluation_contract={"success": {"final_error": 0.1}},
    )
    assert frozen.status == "controller_ready"
    result = service.record_evaluation(
        frozen.session_id,
        action_id="judge-1",
        revision=frozen.revision,
        packet={
            "session_id": frozen.session_id,
            "freeze_fingerprint": frozen.controller_freeze["freeze_fingerprint"],
            "task_fingerprint": frozen.task.fingerprint,
            "provider_id": "model-provider",
            "provider_version": "test-v1",
            "private_truth_returned": False,
            "trials": [{"trial_id": "trial-1", "stable": True, "stopped_on_limit": False, "performance_pass": True}],
        },
    )
    assert result.status == "performance_met"
    assert result.evaluation["private_truth_used"] is False


def test_independent_judge_rejects_private_truth_and_freeze_mismatch(tmp_path) -> None:
    service = WorkflowService(tmp_path)
    session = _resolved_session(service)
    evidence = service.submit_evidence(
        session.session_id,
        action_id="evidence-1",
        revision=session.revision,
        evidence={
            "evidence_id": "trace-1",
            "source": "model",
            "kind": "experiment",
            "protocol_fingerprint": "protocol-1",
            "units": {"time": "s"},
        },
    )
    frozen = service.freeze_controller(
        evidence.session_id,
        action_id="freeze-1",
        revision=evidence.revision,
        controller={"family": "PI", "parameters": {"kp": 1.0}},
        runtime_contract={"command_bounds": [-1.0, 1.0]},
        evaluation_contract={"success": {}},
    )
    with pytest.raises(ValueError, match="private_truth"):
        service.record_evaluation(
            frozen.session_id,
            action_id="judge-private",
            revision=frozen.revision,
            packet={
                "session_id": frozen.session_id,
                "freeze_fingerprint": frozen.controller_freeze["freeze_fingerprint"],
                "task_fingerprint": frozen.task.fingerprint,
                "private_truth_returned": True,
                "trials": [{"stable": True, "performance_pass": True}],
            },
        )


def test_public_provider_and_multistage_contract_are_explicit() -> None:
    task = TaskContract.from_user_input(
        {
            "description": "Move from a low operating point and then hold.",
            "task_type": "transition_then_hold",
            "measured_signals": ["position"],
            "control_input": "force",
            "initial_region": "position near 0",
            "goal_region": "position near 1",
        }
    )
    route = {"route_id": "class_i_first_order_lag:first_order_lag", "profile_id": "first_order_lag", "controller_template_id": "detuned_pi"}
    plan = compile_phase_plan(task, route)
    assert [phase.phase_id for phase in plan.phases] == ["transition", "hold"]
    assert validate_handoff(plan, {"transition": {"entry_passed": True, "exit_passed": True}, "hold": {"entry_passed": True, "exit_passed": True}})["status"] == "passed"

    trace = PublicTrace(
        trace_id="trace-1",
        source="model",
        time_s=(0.0, 1.0),
        signals={"position": (0.0, 1.0)},
        units={"position": "m"},
        protocol_fingerprint="p1",
        operating_region="declared",
        trial_id="trial-1",
    )
    provider = CallableExperimentProvider("model", "v1", lambda operation, task: trace, frozenset({"pulse"}))
    registry = ProviderRegistry()
    registry.register(provider)
    assert registry.get("model").provider_id == "model"
    assert evidence_from_trace(trace)["trace_fingerprint"] == trace.fingerprint


def test_workflow_service_runs_explicit_provider_features_and_controller(tmp_path) -> None:
    service = WorkflowService(tmp_path)
    session = service.start(
        {
            "description": "Keep a stable scalar output at a setpoint.",
            "measured_signals": ["output"],
            "control_input": "input",
        }
    )
    session = service.confirm_task(session.session_id, action_id="confirm-budget", revision=session.revision)
    answers = {
        "open_loop_stability": {"status": "known", "assessment": "stable", "evidence": "stable", "confidence": 0.9},
        "nonminimum_phase": {"status": "known", "assessment": "minimum_phase", "evidence": "minimum phase", "confidence": 0.9},
        "significant_delay": {"status": "known", "assessment": "not_significant", "evidence": "no significant delay", "confidence": 0.9},
        "relative_degree": {"status": "known", "assessment": "low", "evidence": "low order", "confidence": 0.9},
        "sensing_actuation_adequacy": {"status": "known", "assessment": "adequate", "evidence": "adequate", "confidence": 0.9},
        "nonlinearity_strength": {"status": "known", "assessment": "weak", "evidence": "weak", "confidence": 0.9},
        "coupling_underactuation": {"status": "known", "assessment": "siso", "evidence": "SISO", "confidence": 0.9},
        "uncertainty_variation": {"status": "known", "assessment": "small", "evidence": "small", "confidence": 0.9},
    }
    session = service.submit_answer(session.session_id, action_id="answer", revision=session.revision, answer=answers)
    session = service.advance(session.session_id, action_id="advance", revision=session.revision)
    trace = PublicTrace(
        trace_id="trace-service",
        source="model",
        time_s=(0.0, 1.0, 2.0),
        signals={"output": (0.0, 0.5, 1.0)},
        units={"output": "unit"},
        protocol_fingerprint="protocol-service",
        operating_region="declared",
        trial_id="trial-service",
    )
    registry = ProviderRegistry()
    registry.register(CallableExperimentProvider("model", "v1", lambda operation, task: trace, frozenset({"ramp_step"})))
    measured = service.run_experiment(
        session.session_id,
        action_id="experiment-service",
        revision=session.revision,
        provider_registry=registry,
        provider_id="model",
        operation={"operation": "ramp_step"},
    )
    features = service.submit_features(
        measured.session_id,
        action_id="features-service",
        revision=measured.revision,
        features={
            "static_gain": {"value": 1.0, "unit": "unit/unit", "source_evidence_ids": ["trace-service"]},
            "time_constant": {"value": 1.0, "unit": "s", "source_evidence_ids": ["trace-service"]},
        },
        quality={"passed": True},
    )
    candidate = service.submit_controller(
        features.session_id,
        action_id="controller-service",
        revision=features.revision,
        controller={
            "family": "detuned_pi",
            "measured_signals": ["output"],
            "control_inputs": ["input"],
            "parameters": {"kp": 0.5, "ki": 0.1},
            "parameter_domains": {"kp": [0.1, 2.0], "ki": [0.01, 1.0]},
            "output_bounds": [-1.0, 1.0],
        },
    )
    assert candidate.status == "controller_candidate_ready"
    assert candidate.phase_plan["phases"][0]["phase_id"] == "hold"


def test_controller_ir_rejects_executable_payload_and_enforces_domains() -> None:
    with pytest.raises(ValueError, match="executable"):
        ControllerIR.from_mapping(
            {
                "family": "detuned_pi",
                "measured_signals": ["y"],
                "control_inputs": ["u"],
                "parameters": {"kp": 1},
                "parameter_domains": {"kp": [0, 2]},
                "code": "exec('bad')",
            }
        )
    with pytest.raises(ValueError, match="out_of_domain"):
        ControllerIR.from_mapping(
            {
                "family": "detuned_pi",
                "measured_signals": ["y"],
                "control_inputs": ["u"],
                "parameters": {"kp": 3},
                "parameter_domains": {"kp": [0, 2]},
            }
        )


def test_bounded_tuning_has_stability_hard_gate_and_fresh_is_not_feedback() -> None:
    contract = TuningContract(
        parameter_whitelist=("kp",),
        parameter_domains={"kp": (0.1, 5.0)},
        budget_confirmed=True,
    )
    calls = []

    def evaluate(parameters, split, repeats):
        calls.append((dict(parameters), split, repeats))
        if split == "development":
            return {"stable": True, "performance_pass": False, "score": 2.1}
        return {"stable": True, "performance_pass": False, "score": 2.2}

    result = run_bounded_tuning(
        {"kp": 1.0},
        contract,
        evaluate,
        baseline_result={"stable": True, "performance_pass": False, "score": 2.0},
    )
    assert result.status == "completed"
    assert len(result.probes) <= 6
    assert all(repeats == 20 for _params, _split, repeats in calls)
    assert [split for _params, split, _repeats in calls].count("fresh") >= 1

    blocked = run_bounded_tuning(
        {"kp": 1.0},
        contract,
        evaluate,
        baseline_result={"stable": False, "performance_pass": False, "score": 2.0},
    )
    assert blocked.reason == "initial_qualification_failed"
    assert calls[-1][1] != "fresh" or blocked.probes == ()


def test_feedback_creates_new_freeze_and_requires_fresh_confirmation(tmp_path) -> None:
    service = WorkflowService(tmp_path)
    session = _resolved_session(service)
    session = service.confirm_task(
        session.session_id,
        action_id="feedback-confirm-budget",
        revision=session.revision,
    )
    evidence = service.submit_evidence(
        session.session_id,
        action_id="feedback-evidence",
        revision=session.revision,
        evidence={
            "evidence_id": "trace-feedback",
            "source": "model",
            "kind": "experiment",
            "protocol_fingerprint": "protocol-feedback",
            "signal_units": {"time": "s", "output": "unit"},
        },
    )
    frozen = service.freeze_controller(
        evidence.session_id,
        action_id="feedback-freeze",
        revision=evidence.revision,
        controller={"family": "PI", "parameters": {"kp": 1.0}},
        runtime_contract={"command_bounds": [-1.0, 1.0]},
        evaluation_contract={"success": {}},
    )
    predecessor = frozen.controller_freeze["freeze_fingerprint"]
    evaluated = service.record_evaluation(
        frozen.session_id,
        action_id="feedback-baseline",
        revision=frozen.revision,
        packet={
            "session_id": frozen.session_id,
            "task_fingerprint": frozen.task.fingerprint,
            "freeze_fingerprint": predecessor,
            "trials": [
                {
                    "trial_id": "baseline",
                    "stable": True,
                    "performance_pass": False,
                    "metrics": {"score": 1.0},
                }
            ],
        },
    )
    assert evaluated.status == "tuning_eligible"

    def evaluate(parameters, split, repeats):
        del split, repeats
        return {
            "stable": True,
            "performance_pass": False,
            "score": 1.0 + float(parameters["kp"]),
        }

    tuned = service.run_tuning(
        evaluated.session_id,
        action_id="feedback-tuning",
        revision=evaluated.revision,
        contract=TuningContract(
            parameter_whitelist=("kp",),
            parameter_domains={"kp": (0.1, 4.0)},
            budget_confirmed=True,
            initial_freeze_fingerprint=predecessor,
            task_fingerprint=evaluated.task.fingerprint,
        ),
        evaluate=evaluate,
    )
    incumbent = tuned.controller_freeze["freeze_fingerprint"]
    assert tuned.tuning["accepted"] is True
    assert tuned.status == "awaiting_confirmation"
    assert incumbent != predecessor
    assert tuned.freeze_history[-1]["freeze_fingerprint"] == predecessor

    development_packet = {
        "session_id": tuned.session_id,
        "task_fingerprint": tuned.task.fingerprint,
        "freeze_fingerprint": incumbent,
        "trials": [
            {
                "trial_id": "confirmation",
                "stable": True,
                "performance_pass": True,
            }
        ],
    }
    with pytest.raises(ValueError, match="fresh_confirmation_required_after_tuning"):
        service.record_evaluation(
            tuned.session_id,
            action_id="feedback-stale-development",
            revision=tuned.revision,
            packet=development_packet,
        )

    confirmed = service.record_confirmation(
        tuned.session_id,
        action_id="feedback-confirmation",
        revision=tuned.revision,
        packet=development_packet,
    )
    assert confirmed.status == "performance_met"
    assert confirmed.confirmation["freeze_fingerprint"] == incumbent


def test_kernel_agent_context_is_role_scoped_and_has_no_supervisor(tmp_path) -> None:
    service = WorkflowService(tmp_path)
    session = service.start({"description": "A scalar control task", "measured_signals": ["y"], "control_input": "u"})
    coordinator = KernelAgentCoordinator(lambda request: {"ok": True}, agent_mode="multi")
    diagnosis = coordinator.build_context(session, role=AgentRole.DIAGNOSIS, operation="diagnosis")
    assert "route" not in diagnosis["payload"]
    assert "controller" not in diagnosis["payload"]
    assert {role.value for role in AgentRole} == {"diagnosis", "modeling", "controller", "critic"}
    record = coordinator.execute(session, role=AgentRole.MODELING, operation="feature")
    assert record.role is AgentRole.MODELING
    assert record.messages[0]["role"] == "system"


def test_diagnostic_revision_invalidates_stale_route_and_controller_artifacts(tmp_path) -> None:
    service = WorkflowService(tmp_path)
    session = service.start(
        {
            "description": "Keep a scalar output near a setpoint.",
            "measured_signals": ["output"],
            "control_input": "input",
        }
    )
    answers = {
        dimension.id: {
            "status": "known",
            "assessment": "stable" if dimension.id == "open_loop_stability" else "siso",
            "evidence": f"confirmed {dimension.id}",
        }
        for dimension in session.ledger.entries
    }
    session = service.submit_answer(
        session.session_id,
        action_id="answers",
        revision=session.revision,
        answer=answers,
    )
    session = service.advance(session.session_id, action_id="route", revision=session.revision)
    assert session.route is not None

    revised = service.submit_answer(
        session.session_id,
        action_id="diagnostic-revision",
        revision=session.revision,
        answer={"open_loop_stability": "unstable after the new public observation"},
    )
    assert revised.route is None
    assert revised.feature_artifact is None
    assert revised.controller_candidate is None
    assert revised.phase_plan is None
    assert revised.phase_results == ()
    assert revised.status == "awaiting_evidence"


def test_handoff_with_missing_public_booleans_is_blocked() -> None:
    task = TaskContract.from_user_input(
        {
            "description": "Move to a goal and then hold.",
            "task_type": "transition_then_hold",
            "measured_signals": ["position"],
            "control_input": "force",
            "initial_region": "near zero",
            "goal_region": "near one",
        }
    )
    plan = compile_phase_plan(
        task,
        {"route_id": "route", "profile_id": "first_order_lag", "controller_template_id": "detuned_pi"},
    )
    result = validate_handoff(
        plan,
        {phase.phase_id: {"observation": "not a gate"} for phase in plan.phases},
    )
    assert result["status"] == "blocked"
    assert all(item.startswith("missing_gate:") for item in result["failures"])


def test_phase_hard_failure_cannot_advance_to_evaluation(tmp_path) -> None:
    service = WorkflowService(tmp_path)
    session = _resolved_session(service)
    evidence = service.submit_evidence(
        session.session_id,
        action_id="phase-evidence",
        revision=session.revision,
        evidence={
            "evidence_id": "trace-phase",
            "source": "model",
            "kind": "experiment",
            "protocol_fingerprint": "protocol-phase",
            "signal_units": {"time": "s"},
        },
    )
    frozen = service.freeze_controller(
        evidence.session_id,
        action_id="phase-freeze",
        revision=evidence.revision,
        controller={"family": "PI", "parameters": {"kp": 1.0}},
        runtime_contract={"command_bounds": [-1.0, 1.0]},
        evaluation_contract={"success": {}},
    )
    failed = service.record_phase_result(
        frozen.session_id,
        action_id="phase-result",
        revision=frozen.revision,
        result={
            "phase_id": "hold",
            "entry_condition_met": True,
            "exit_condition_met": True,
            "success": True,
            "hard_failure": True,
        },
    )
    assert failed.status == "capability_gap"
    assert failed.pending_actions[0]["kind"] == "capability_gap"


def test_critic_correction_is_revalidated_before_returning() -> None:
    class GainAdapter:
        def propose_gain_update(self, context):
            del context
            return {"new_parameters": {"kp": 1.0}, "rationale": "bounded"}

    class Completion:
        def __init__(self):
            self.responses = iter(
                [
                    {"decision": "revise", "feedback": "return the typed gain proposal"},
                    {"rationale": "missing new parameters"},
                    {"decision": "pass", "feedback": ""},
                ]
            )

        def __call__(self, request):
            return next(self.responses)

    wrapped = CompositeAgentAdapter(
        GainAdapter(),
        AgentRuntime(Completion()),
        description_provider=lambda _value: SystemDescription(text="A plant."),
    )
    with pytest.raises((ValueError, AgentReviewBlocked)):
        wrapped.propose_gain_update({"context": "plant"})


def test_feature_quality_flag_must_be_boolean(tmp_path) -> None:
    service = WorkflowService(tmp_path)
    session = _resolved_session(service)
    evidence = service.submit_evidence(
        session.session_id,
        action_id="quality-evidence",
        revision=session.revision,
        evidence={
            "evidence_id": "trace-quality",
            "source": "model",
            "kind": "experiment",
            "protocol_fingerprint": "protocol-quality",
            "signal_units": {"time": "s"},
        },
    )
    with pytest.raises(ValueError, match="quality_passed_must_be_boolean"):
        service.submit_features(
            evidence.session_id,
            action_id="quality-features",
            revision=evidence.revision,
            features={
                "static_gain": {"value": 1.0, "source_evidence_ids": ["trace-quality"]},
                "time_constant": {"value": 2.0, "source_evidence_ids": ["trace-quality"]},
            },
            quality={"passed": "false"},
        )


def test_diagnostic_blocking_flag_must_be_boolean() -> None:
    ledger = DiagnosticLedger.initial()
    with pytest.raises(
        ValueError,
        match="diagnostic_blocking_for_current_route_must_be_boolean",
    ):
        ledger.update(
            {
                "open_loop_stability": {
                    "status": "known",
                    "evidence": "stable",
                    "blocking_for_current_route": "false",
                }
            },
            source="human_operator",
        )


def test_public_saturation_flags_must_be_boolean() -> None:
    with pytest.raises(ValueError, match="public_saturated_values_must_be_boolean"):
        _boolean_sequence(["false"])


def test_public_confirmation_and_evaluation_flags_are_strict(tmp_path) -> None:
    with pytest.raises(ValueError, match="budget_confirmed_must_be_boolean"):
        TaskContract.from_user_input(
            {
                "description": "Keep a scalar output near a setpoint.",
                "measured_signals": ["output"],
                "control_input": "input",
                "budget_confirmed": "false",
            }
        )

    service = WorkflowService(tmp_path)
    session = _resolved_session(service)
    evidence = service.submit_evidence(
        session.session_id,
        action_id="strict-evidence",
        revision=session.revision,
        evidence={
            "evidence_id": "trace-strict",
            "source": "model",
            "kind": "experiment",
            "protocol_fingerprint": "protocol-strict",
            "signal_units": {"time": "s"},
        },
    )
    frozen = service.freeze_controller(
        evidence.session_id,
        action_id="strict-freeze",
        revision=evidence.revision,
        controller={"family": "PI", "parameters": {"kp": 1.0}},
        runtime_contract={"command_bounds": [-1.0, 1.0]},
        evaluation_contract={"success": {}},
    )
    with pytest.raises(ValueError, match="evaluation_trial_stable_must_be_boolean"):
        service.record_evaluation(
            frozen.session_id,
            action_id="strict-evaluation",
            revision=frozen.revision,
            packet={
                "session_id": frozen.session_id,
                "freeze_fingerprint": frozen.controller_freeze["freeze_fingerprint"],
                "task_fingerprint": frozen.task.fingerprint,
                "private_truth_returned": False,
                "trials": [{"stable": "false", "performance_pass": False}],
            },
        )


def test_tuning_stability_gate_does_not_use_string_truthiness() -> None:
    contract = TuningContract(
        parameter_whitelist=("kp",),
        parameter_domains={"kp": (0.1, 3.0)},
        budget_confirmed=True,
    )

    def unexpected_evaluation(*_args):
        raise AssertionError("an invalid baseline must be blocked before probing")

    result = run_bounded_tuning(
        {"kp": 1.0},
        contract,
        unexpected_evaluation,
        baseline_result={"stable": "false", "performance_pass": False, "score": 1.0},
    )
    assert result.status == "blocked"
    assert result.reason == "initial_qualification_failed"
