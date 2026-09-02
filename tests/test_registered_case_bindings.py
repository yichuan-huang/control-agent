from __future__ import annotations

import json
from dataclasses import replace

import pytest

from cfdc.kernel import EvidenceSession, WorkflowService
from cfdc.kernel.cases import public_training_case
from cfdc.kernel.contracts import TaskContract, fingerprint
from cfdc.kernel.replies import _ACTION_ALIASES, build_kernel_input_contract
from cfdc.kernel.session import registered_task_scope_fingerprint
from cfdc.sim.training import build_training_provider_registries
from cfdc.web import ui as web_ui
from cfdc.web.service import (
    continue_kernel_app_run,
    kernel_action_error_payload,
    start_kernel_app_run,
    start_kernel_case_run,
)


def _recompute_binding_fingerprint(binding: dict) -> None:
    raw = dict(binding)
    raw.pop("binding_fingerprint", None)
    binding["binding_fingerprint"] = fingerprint(raw)


def _registered_raw_session(service: WorkflowService) -> dict:
    session = service.start_registered_case("dc_motor_speed_v1")
    return session.to_dict()


@pytest.mark.parametrize("mutation", ["case", "provider", "task", "event"])
def test_registered_binding_is_rederived_from_catalog_and_event_chain(
    tmp_path, mutation: str
) -> None:
    service = WorkflowService(tmp_path)
    payload = _registered_raw_session(service)
    binding = payload["registered_case_binding"]

    if mutation == "case":
        binding["case_id"] = "quadruple_tank_nmp_v1"
        _recompute_binding_fingerprint(binding)
    elif mutation == "provider":
        binding["provider_references"]["identification"]["provider_id"] = (
            "physical-training:quadruple_tank_nmp_v1"
        )
        _recompute_binding_fingerprint(binding)
    elif mutation == "task":
        task = dict(payload["task"])
        task["description"] = "tampered public task"
        task.pop("task_fingerprint", None)
        parsed = TaskContract.from_user_input(task)
        payload["task"] = parsed.to_dict()
        binding["task_scope_fingerprint"] = registered_task_scope_fingerprint(parsed)
        _recompute_binding_fingerprint(binding)
        for role in ("identification", "evaluation"):
            payload["provider_bindings"][role]["task_scope_fingerprint"] = binding[
                "task_scope_fingerprint"
            ]
            payload["provider_bindings"][role][
                "registered_case_binding_fingerprint"
            ] = binding["binding_fingerprint"]
    else:
        event = payload["events"][-1]
        event["payload"]["case_id"] = "quadruple_tank_nmp_v1"
        event_raw = dict(event)
        event_raw.pop("event_fingerprint", None)
        event["event_fingerprint"] = fingerprint(event_raw)

    with pytest.raises(ValueError, match="registered_case_(catalog|event)_.*mismatch"):
        EvidenceSession.from_dict(payload)


def test_session_with_unavailable_registered_catalog_loads_read_only(tmp_path) -> None:
    service = WorkflowService(tmp_path)
    payload = _registered_raw_session(service)
    binding = payload["registered_case_binding"]
    binding["catalog_version"] = "cfdc-public-cases/future"
    _recompute_binding_fingerprint(binding)
    event = payload["events"][-1]
    event["payload"]["binding_fingerprint"] = binding["binding_fingerprint"]
    event_raw = dict(event)
    event_raw.pop("event_fingerprint", None)
    event["event_fingerprint"] = fingerprint(event_raw)

    loaded = EvidenceSession.from_dict(payload)

    assert loaded.read_only is True
    assert loaded.registered_case_binding["catalog_version"] == (
        "cfdc-public-cases/future"
    )


def test_registered_scope_changes_for_every_non_budget_task_fact() -> None:
    original = TaskContract.from_user_input(
        public_training_case("dc_motor_speed_v1")["task"]
    )
    changed = TaskContract.from_user_input(
        {
            **original.to_dict(include_fingerprint=False),
            "reference": float(original.reference or 0) + 1.0,
        }
    )
    confirmed = TaskContract.from_user_input(
        {
            **original.to_dict(include_fingerprint=False),
            "budget_confirmed": True,
        }
    )
    assert registered_task_scope_fingerprint(
        original
    ) != registered_task_scope_fingerprint(changed)
    assert registered_task_scope_fingerprint(
        original
    ) == registered_task_scope_fingerprint(confirmed)


def test_case_form_locks_contract_and_convert_to_custom_preserves_values() -> None:
    locked = web_ui.load_case_into_form("case-01")
    assert all(
        isinstance(value, dict) and value.get("interactive") is False
        for value in locked
    )

    unlocked = web_ui.convert_case_to_custom("case-01", *locked)
    assert unlocked[0]["value"] == ""
    assert all(value.get("interactive") is True for value in unlocked)


def test_web_reply_contract_has_no_public_set_provider_action(tmp_path) -> None:
    assert "set_provider" not in _ACTION_ALIASES
    session = WorkflowService(tmp_path).start(
        {
            "description": "Hold output.",
            "task_type": "local_setpoint_hold",
            "measured_signals": ["output"],
            "control_input": "input",
            "input_min": -1,
            "input_max": 1,
            "state_stop": 2,
        }
    )
    contract = build_kernel_input_contract(
        session, pending_actions=[{"kind": "provider", "action": "set_provider"}]
    )
    assert contract["disabled_reason"]


def test_registered_projection_contains_three_step_learning_boundary(tmp_path) -> None:
    report, _ = start_kernel_app_run(
        public_training_case("dc_motor_speed_v1")["task"],
        provider_case_id="dc_motor_speed_v1",
        session_dir=tmp_path,
        use_rag=False,
    )

    assert len(report["teaching_steps"]) == 3
    assert report["education"]["learning_goal"]
    assert report["education"]["cannot_prove"]
    assert "证据边界" in web_ui._guidance_text(report)


def test_web_error_projection_does_not_echo_unrecognised_exception_text() -> None:
    payload = kernel_action_error_payload(
        ValueError("unexpected internal detail <script>alert(1)</script>")
    )

    assert payload["code"] == "action_failed"
    assert "script" not in str(payload)


def test_failed_mutation_refreshes_the_returned_web_state(
    tmp_path, monkeypatch
) -> None:
    _, state = start_kernel_app_run(
        {
            "description": "Hold output.",
            "task_type": "local_setpoint_hold",
            "measured_signals": ["output"],
            "control_input": "input",
            "input_min": -1,
            "input_max": 1,
            "state_stop": 2,
        },
        session_dir=tmp_path,
        use_rag=False,
    )
    service = WorkflowService(tmp_path)
    session = service.read(state["kernel_session_id"])
    current = service.confirm_task(
        session.session_id, action_id="other-tab", revision=session.revision
    )
    warnings: list[str] = []
    monkeypatch.setattr(web_ui.gr, "Warning", warnings.append)

    outputs = web_ui._refresh_mutation_error(ValueError("stale_revision"), state)

    assert outputs[0]["kernel_revision"] == current.revision
    assert f'"revision": {current.revision}' in warnings[0]


def test_registered_case_binding_is_persisted_and_scope_survives_budget_confirmation(
    tmp_path,
) -> None:
    service = WorkflowService(tmp_path)
    session = service.start_registered_case("dc_motor_speed_v1")

    binding = session.registered_case_binding
    assert binding is not None
    assert binding["case_id"] == "dc_motor_speed_v1"
    assert binding["case_kind"] == "training"
    assert binding["evidence_mode"] == "automatic"
    assert binding["task_scope_fingerprint"] != session.task.fingerprint
    assert set(binding["provider_references"]) == {"identification", "evaluation"}
    assert (
        session.provider_bindings["identification"]["task_scope_fingerprint"]
        == binding["task_scope_fingerprint"]
    )

    confirmed = service.confirm_task(
        session.session_id, action_id="confirm", revision=session.revision
    )
    assert confirmed.registered_case_binding == binding
    assert confirmed.task.budget_confirmed is True


def test_registered_case_start_rejects_tampered_task_before_creating_session(
    tmp_path,
) -> None:
    task = public_training_case("dc_motor_speed_v1")["task"]
    tampered = {**task, "reference": float(task["reference"]) + 1.0}

    with pytest.raises(ValueError, match="registered_case_task_contract_mismatch"):
        start_kernel_app_run(
            tampered,
            provider_case_id="dc_motor_speed_v1",
            session_dir=tmp_path,
            use_rag=False,
        )

    assert list(tmp_path.glob("*.json")) == []


def test_web_provider_actions_use_session_binding_not_tampered_page_state(
    tmp_path,
) -> None:
    report, state = start_kernel_case_run(
        "dc_motor_speed_v1", session_dir=tmp_path, use_rag=False
    )
    assert "provider_case_id" not in state
    assert report["registered_case_binding"]["case_id"] == "dc_motor_speed_v1"

    report, _ = continue_kernel_app_run(
        {**state, "provider_case_id": "quadruple_tank_nmp_v1"},
        action="confirm_task",
        payload={},
    )
    persisted = WorkflowService(tmp_path).read(report["session_id"])
    assert persisted.registered_case_binding["case_id"] == "dc_motor_speed_v1"
    assert persisted.provider_bindings["identification"]["provider_id"] == (
        "physical-training:dc_motor_speed_v1"
    )


def test_registered_case_provider_binding_cannot_be_overridden(tmp_path) -> None:
    service = WorkflowService(tmp_path)
    session = service.start_registered_case("dc_motor_speed_v1")

    with pytest.raises(ValueError, match="registered_case_provider_binding_immutable"):
        service.set_provider(
            session.session_id,
            action_id="replace",
            revision=session.revision,
            provider={
                "provider_id": "physical-training:quadruple_tank_nmp_v1",
                "provider_version": "physical-training-provider/v1",
                "capabilities": [],
                "binding_role": "identification",
                "execution_kind": "software",
            },
        )

    assert service.read(session.session_id).revision == session.revision


def test_previous_session_version_is_read_only_and_lacks_provider_authority(
    tmp_path,
) -> None:
    service = WorkflowService(tmp_path)
    current = service.start(
        {
            "description": "Keep output near a reference.",
            "task_type": "local_setpoint_hold",
            "measured_signals": ["output"],
            "control_input": "input",
            "input_min": -1,
            "input_max": 1,
            "state_stop": 2,
        }
    )
    payload = current.to_dict()
    payload["session_version"] = "cfdc-session/v3.0"
    payload.pop("registered_case_binding", None)

    restored = EvidenceSession.from_json(json.dumps(payload))
    assert restored.read_only is True
    assert restored.registered_case_binding is None


def test_submit_answer_cannot_overwrite_known_diagnostic(tmp_path) -> None:
    service = WorkflowService(tmp_path)
    session = service.start(
        {
            "description": "Keep output near a reference.",
            "task_type": "local_setpoint_hold",
            "measured_signals": ["output"],
            "control_input": "input",
            "input_min": -1,
            "input_max": 1,
            "state_stop": 2,
        }
    )
    known = service.submit_answer(
        session.session_id,
        action_id="known",
        revision=session.revision,
        answer={
            "open_loop_stability": {
                "status": "known",
                "assessment": "stable",
                "evidence": "stable observation",
            }
        },
    )

    with pytest.raises(ValueError, match="diagnostic_conflict_requires_clarification"):
        service.submit_answer(
            known.session_id,
            action_id="conflict",
            revision=known.revision,
            answer={
                "open_loop_stability": {
                    "status": "known",
                    "assessment": "unstable",
                }
            },
        )
    assert service.read(known.session_id).revision == known.revision


def test_revise_diagnostic_records_supersession_and_invalidates_dependents(
    tmp_path,
) -> None:
    service = WorkflowService(tmp_path)
    session = service.start(
        {
            "description": "Keep output near a reference.",
            "task_type": "local_setpoint_hold",
            "measured_signals": ["output"],
            "control_input": "input",
            "input_min": -1,
            "input_max": 1,
            "state_stop": 2,
        }
    )
    known = service.submit_answer(
        session.session_id,
        action_id="known",
        revision=session.revision,
        answer={
            "open_loop_stability": {
                "status": "known",
                "assessment": "stable",
                "evidence": "stable observation",
            }
        },
    )

    revised = service.revise_diagnostic(
        known.session_id,
        action_id="revise",
        revision=known.revision,
        confirmation=True,
        source_text="新的实验记录表明对象不稳定。",
        diagnostic_updates={
            "open_loop_stability": {
                "status": "known",
                "assessment": "unstable",
                "evidence": "对象不稳定",
            }
        },
    )
    assert revised.ledger.entry("open_loop_stability").assessment == "unstable"
    assert revised.events[-1].event_type == "diagnostic_revised"
    assert (
        revised.events[-1].payload["superseded"]["open_loop_stability"]["assessment"]
        == "stable"
    )


def test_revise_diagnostic_invalidates_active_protocol_and_qualification(
    tmp_path,
) -> None:
    service = WorkflowService(tmp_path)
    session = service.start_registered_case("dc_motor_speed_v1")
    session = service.confirm_task(
        session.session_id, action_id="confirm", revision=session.revision
    )
    diagnostics = {
        "open_loop_stability": "stable",
        "nonminimum_phase": "minimum_phase",
        "significant_delay": "not_significant",
        "relative_degree": "low",
        "sensing_actuation_adequacy": "adequate",
        "nonlinearity_strength": "weak",
        "coupling_underactuation": "siso",
        "uncertainty_variation": "small",
    }
    session = service.submit_answer(
        session.session_id,
        action_id="diagnostics",
        revision=session.revision,
        answer={
            key: {
                "status": "known",
                "assessment": value,
                "evidence": f"confirmed {key}",
            }
            for key, value in diagnostics.items()
        },
    )
    identification, identification_id, _, _ = build_training_provider_registries(
        "dc_motor_speed_v1"
    )
    session = service.advance(
        session.session_id, action_id="route", revision=session.revision
    )
    session = service.compile_protocol(
        session.session_id, action_id="protocol", revision=session.revision
    )
    session = service.run_provider(
        session.session_id,
        action_id="provider",
        revision=session.revision,
        provider_registry=identification,
        provider_id=identification_id,
    )
    session = service.derive_features(
        session.session_id, action_id="features", revision=session.revision
    )
    session = service.synthesize_controller(
        session.session_id, action_id="controller", revision=session.revision
    )
    session = service.qualify_controller(
        session.session_id, action_id="qualification", revision=session.revision
    )
    assert session.controller_qualification["status"] == "offline_qualified"
    old_protocol = session.active_protocol_fingerprint
    old_evidence_count = len(session.evidence)
    old_evidence_id = str(session.evidence[0]["evidence_id"])

    revised = service.revise_diagnostic(
        session.session_id,
        action_id="revise",
        revision=session.revision,
        confirmation=True,
        source_text="新的公开试验记录表明时延显著。",
        diagnostic_updates={
            "significant_delay": {
                "status": "known",
                "assessment": "significant",
                "evidence": "时延显著",
            }
        },
    )

    assert revised.active_protocol_fingerprint is None
    assert revised.controller_qualification is None
    assert revised.controller_freeze is None
    assert revised.evaluation is None
    assert revised.tuning is None
    assert revised.confirmation is None
    assert revised.controller_candidate is None
    assert old_protocol in {item["protocol_fingerprint"] for item in revised.protocols}
    assert len(revised.evidence) == old_evidence_count

    rerouted = service.advance(
        revised.session_id, action_id="reroute", revision=revised.revision
    )
    recompiled = service.compile_protocol(
        rerouted.session_id, action_id="recompile", revision=rerouted.revision
    )
    with pytest.raises(ValueError, match="public_evidence_required_before_features"):
        service.submit_features(
            recompiled.session_id,
            action_id="reuse-stale-features",
            revision=recompiled.revision,
            features={
                str(recompiled.route["feature_ids"][0]): {
                    "value": 1.0,
                    "source_evidence_ids": [old_evidence_id],
                }
            },
        )


def test_web_allows_explicit_diagnostic_revision_while_answer_is_pending(
    tmp_path,
) -> None:
    _, state = start_kernel_app_run(
        {
            "description": "Keep output near a reference.",
            "task_type": "local_setpoint_hold",
            "measured_signals": ["output"],
            "control_input": "input",
            "input_min": -1,
            "input_max": 1,
            "state_stop": 2,
        },
        session_dir=tmp_path,
        use_rag=False,
    )
    _, state = continue_kernel_app_run(state, action="confirm_task", payload={})
    _, state = continue_kernel_app_run(
        state,
        action="answer",
        payload={
            "diagnostic_updates": {
                "open_loop_stability": {
                    "status": "known",
                    "assessment": "stable",
                    "evidence": "对象稳定",
                }
            },
            "source_text": "公开记录显示对象稳定。",
        },
        reply_source_text="公开记录显示对象稳定。",
        reply_input_mode="json",
    )

    report, _ = continue_kernel_app_run(
        state,
        action="revise_diagnostic",
        payload={
            "diagnostic_updates": {
                "open_loop_stability": {
                    "status": "known",
                    "assessment": "unstable",
                    "evidence": "对象不稳定",
                }
            },
            "source_text": "新的公开记录显示对象不稳定。",
            "confirmation": True,
        },
        reply_source_text="新的公开记录显示对象不稳定。",
        reply_input_mode="json",
    )

    assert (
        next(
            item
            for item in report["diagnostic"]["entries"]
            if item["id"] == "open_loop_stability"
        )["assessment"]
        == "unstable"
    )


def test_synthesize_controller_requires_controller_pending_and_quality(
    tmp_path,
) -> None:
    service = WorkflowService(tmp_path)
    session = service.start(
        {
            "description": "Keep output near a reference.",
            "task_type": "local_setpoint_hold",
            "measured_signals": ["output"],
            "control_input": "input",
            "input_min": -1,
            "input_max": 1,
            "state_stop": 2,
        }
    )
    with pytest.raises(ValueError, match="controller_synthesis_not_ready"):
        service.synthesize_controller(
            session.session_id, action_id="synth", revision=session.revision
        )


def test_automatic_runner_stops_when_feature_quality_is_not_ready(tmp_path) -> None:
    service = WorkflowService(tmp_path)
    session = service.start(
        {
            "description": "Keep output near a reference.",
            "task_type": "local_setpoint_hold",
            "measured_signals": ["output"],
            "control_input": "input",
            "input_min": -1,
            "input_max": 1,
            "state_stop": 2,
            "budget_confirmed": True,
        }
    )
    provider = {
        "provider_id": "reviewed-provider",
        "provider_version": "v1",
        "capabilities": [],
        "binding_role": "identification",
        "execution_kind": "software",
    }
    evaluation_provider = {**provider, "binding_role": "evaluation"}
    staged = replace(
        session,
        status="awaiting_evidence",
        route={"route_id": "route", "capability_gap": None},
        provider=provider,
        provider_bindings={
            "identification": provider,
            "evaluation": evaluation_provider,
        },
        protocols=({"protocol_fingerprint": "protocol"},),
        active_protocol_fingerprint="protocol",
        evidence=({"evidence_id": "trace"},),
        feature_artifact={"quality": {"passed": False}, "missing_feature_ids": []},
        pending_actions=({"kind": "feature", "action": "derive_features"},),
    )
    staged.save(tmp_path / f"{session.session_id}.json")

    result = service.run_until_blocked(session.session_id)

    assert result.status == "awaiting_evidence"
    assert result.feature_artifact is not None
    assert result.controller_candidate is None
    assert service.read(session.session_id).revision == session.revision


def test_web_answer_requires_source_checked_reply(tmp_path) -> None:
    _, state = start_kernel_app_run(
        {
            "description": "Keep output near a reference.",
            "task_type": "local_setpoint_hold",
            "measured_signals": ["output"],
            "control_input": "input",
            "input_min": -1,
            "input_max": 1,
            "state_stop": 2,
        },
        session_dir=tmp_path,
        use_rag=False,
    )
    _, state = continue_kernel_app_run(state, action="confirm_task", payload={})
    with pytest.raises(ValueError, match="kernel_reply_source_text_required"):
        continue_kernel_app_run(
            state,
            action="answer",
            payload={"open_loop_stability": "stable"},
        )
