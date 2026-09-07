import pytest

from cfdc.kernel import WorkflowService
from cfdc.kernel.external import select_external_source


def test_external_source_is_persisted_and_cannot_claim_registered_authority(tmp_path):
    service = WorkflowService(tmp_path)
    session = service.create_task(
        {
            "description": "Hold output",
            "measured_signals": ["output"],
            "control_input": "input",
        }
    )
    session = select_external_source(
        service,
        session.session_id,
        action_id="source",
        revision=session.revision,
        source_kind="software",
    )
    restored = service.read(session.session_id)
    assert restored.external_workflow["source"]["source_kind"] == "software"
    assert restored.provider_bindings["evaluation"]["execution_kind"] == "external"
    with pytest.raises(ValueError, match="external_source_kind_invalid"):
        select_external_source(
            service,
            session.session_id,
            action_id="bad",
            revision=session.revision,
            source_kind="registered",
        )


def external_prepared(tmp_path):
    from dataclasses import replace

    from test_service_evaluation_replay import prepared_service, successful_packet

    from cfdc.kernel.contracts import fingerprint
    from cfdc.kernel.external import VERSION

    service, session, _ = prepared_service(tmp_path, successful_packet)
    binding = {
        "provider_id": "external-software",
        "provider_version": VERSION,
        "source_kind": "software",
        "execution_kind": "external",
    }
    freeze = dict(session.controller_freeze)
    freeze["runtime_contract"] = {
        **freeze["runtime_contract"],
        "provider_bindings": {"evaluation": binding},
    }
    freeze.pop("freeze_fingerprint")
    freeze["freeze_fingerprint"] = fingerprint(freeze)
    state = {
        "workflow_version": VERSION,
        "source": binding,
        "active_request": None,
        "requests": [],
        "receipts": [],
        "tuning": None,
    }
    session = service._save(
        service._append(
            replace(
                session,
                controller_freeze=freeze,
                external_workflow=state,
                provider_bindings={"evaluation": binding},
            ),
            "external_test_prepared",
            "external-prepare",
            {},
        )
    )
    return service, session


def result_zip(
    tmp_path, active, *, corrupt=False, summary=False, output_scale=1.0, stopped=False
):
    import json
    import zipfile
    from copy import deepcopy

    from test_service_evaluation_replay import successful_packet

    manifest = deepcopy(active["manifest"])
    if corrupt:
        manifest["candidate_id"] = "forged"
    trials = successful_packet(active["execution_request"])["trials"]
    path = tmp_path / "results.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("manifest.json", json.dumps(manifest))
        for row, trial in zip(manifest["trials"], trials, strict=True):
            for name in ("outputs", "measurements"):
                for channel, values in trial["trajectory"][name].items():
                    trial["trajectory"][name][channel] = [
                        value * output_scale for value in values
                    ]
            if stopped:
                trial["stop_event"].update(triggered=True, reason="state_limit")
            if summary:
                trial.pop("trajectory")
                trial["performance_pass"] = True
            archive.writestr(row["file"], json.dumps(trial))
    return path


def test_external_package_records_full_trace_and_replays_after_restart(tmp_path):
    import zipfile

    from cfdc.kernel.external import prepare_external_run, submit_external_results

    service, session = external_prepared(tmp_path)
    session = prepare_external_run(
        service, session.session_id, action_id="request", revision=session.revision
    )
    active = session.external_workflow["active_request"]
    with zipfile.ZipFile(active["package_path"]) as archive:
        assert (
            "final_abs_error_max" not in archive.read("execution-request.json").decode()
        )
    service = WorkflowService(tmp_path)
    path = result_zip(tmp_path, active)
    session = submit_external_results(
        service,
        session.session_id,
        action_id="results",
        revision=session.revision,
        paths=[path],
    )
    assert session.status == "performance_met"
    assert session.evaluation_replays[-1]["matches_previous"]
    assert session.external_workflow["active_request"] is None
    assert session.external_workflow["receipts"][-1]["accepted"]
    same = submit_external_results(
        service, session.session_id, action_id="results", revision=0, paths=[path]
    )
    assert same.revision == session.revision


@pytest.mark.parametrize("corrupt,summary", [(True, False), (False, True)])
def test_external_rejected_results_are_audited_without_consuming_request(
    tmp_path, corrupt, summary
):
    from cfdc.kernel.external import prepare_external_run, submit_external_results

    service, session = external_prepared(tmp_path)
    session = prepare_external_run(
        service, session.session_id, action_id="request", revision=session.revision
    )
    active = session.external_workflow["active_request"]
    path = result_zip(tmp_path, active, corrupt=corrupt, summary=summary)
    session = submit_external_results(
        service,
        session.session_id,
        action_id="results",
        revision=session.revision,
        paths=[path],
    )
    assert not session.external_workflow["receipts"][-1]["accepted"]
    if corrupt:
        assert (
            session.external_workflow["receipts"][-1]["reason"]
            == "external_results_binding_mismatch"
        )
    assert session.external_workflow["active_request"] == active
    assert not session.evaluation_packets


@pytest.mark.parametrize(
    "outcome",
    ["selected", "confirmation_failed", "no_improvement", "qualification_failed"],
)
@pytest.mark.parametrize("crash_after_last_receipt", [False, True])
def test_external_tuning_persists_fixed_candidates_and_confirms_disjoint_trials(
    tmp_path, monkeypatch, crash_after_last_receipt, outcome
):
    from copy import deepcopy
    from dataclasses import replace

    from cfdc.kernel import ControllerIR, TuningContract, run_bounded_tuning
    from cfdc.kernel.contracts import fingerprint
    from cfdc.kernel.external import (
        prepare_external_run,
        start_external_tuning,
        submit_external_results,
    )

    service, session = external_prepared(tmp_path)
    freeze = deepcopy(session.controller_freeze)
    freeze["controller"] = ControllerIR(
        family="PI",
        measured_signals=("y",),
        control_inputs=("u",),
        parameters={"kp": 1.0},
        parameter_domains={"kp": (0.1, 4.0)},
    ).to_dict()
    freeze.pop("freeze_fingerprint")
    freeze["freeze_fingerprint"] = fingerprint(freeze)
    session = service._save(
        service._append(
            replace(
                session,
                controller_freeze=freeze,
                status="tuning_eligible",
                evaluation={
                    "status": "performance_not_met",
                    "score": 5,
                    "stability_gate": {"passed": True},
                },
                evaluation_replays=({"matches_previous": True},),
                route={"route_id": "test"},
                feature_artifact={"test": True},
                protocols=({"protocol_fingerprint": "test"},),
                active_protocol_fingerprint="test",
            ),
            "test_tuning_ready",
            "ready",
            {},
        )
    )
    monkeypatch.setattr(
        "cfdc.controllers.qualification.qualify_controller",
        lambda *args, **kwargs: {
            "status": "qualification_failed"
            if outcome == "qualification_failed"
            else "offline_qualified"
        },
    )
    contract = TuningContract(
        parameter_whitelist=("kp",),
        parameter_domains={"kp": (0.1, 4.0)},
        max_probes=2,
        budget_confirmed=True,
        development_repeats=1,
        fresh_repeats=1,
    )
    baseline_result = {
        **deepcopy(session.evaluation),
        "stable": session.evaluation["stability_gate"]["passed"],
        "performance_pass": False,
    }

    def assert_sync_equivalent(completed):
        rows = completed.external_workflow["tuning"]["candidates"]

        def lookup(parameters):
            return next(row for row in rows if row["parameters"] == parameters)

        synchronous = run_bounded_tuning(
            freeze["controller"]["parameters"],
            contract,
            lambda parameters, split, repeats: lookup(parameters)["result"],
            baseline_result=baseline_result,
            confirm_selected=False,
            qualify=lambda parameters: lookup(parameters)["qualification"],
        ).to_dict()
        for key in ("best_parameters", "best_score", "status", "reason", "accepted"):
            assert completed.tuning[key] == synchronous[key]
        assert [row["parameters"] for row in completed.tuning["probes"]] == [
            row["parameters"] for row in synchronous["probes"]
        ]

    session = start_external_tuning(
        service,
        session.session_id,
        action_id="tune",
        revision=session.revision,
        contract=contract,
    )
    if outcome == "qualification_failed":
        assert_sync_equivalent(session)
        assert session.status == "capability_gap"
        assert not session.tuning["accepted"]
        assert all(
            row["reason"] == "candidate_qualification_failed"
            for row in session.tuning["probes"]
        )
        assert not session.external_workflow["requests"]
        return
    candidates = deepcopy(session.external_workflow["tuning"]["candidates"])
    assert [row["parameters"] for row in candidates] == [{"kp": 0.5}, {"kp": 0.75}]
    original = session.controller_freeze
    for index in range(2):
        service = WorkflowService(tmp_path)
        session = prepare_external_run(
            service,
            session.session_id,
            action_id=f"probe{index}",
            revision=session.revision,
            stage="tuning_probe",
        )
        path = result_zip(
            tmp_path,
            session.external_workflow["active_request"],
            output_scale=0.4 if outcome == "no_improvement" else 1.0,
        )
        if crash_after_last_receipt and index == 1:
            from cfdc.kernel import external

            original_finish = external._finish_tuning

            def crash(*args):
                raise RuntimeError("simulated process loss after persisted receipt")

            monkeypatch.setattr(external, "_finish_tuning", crash)
            with pytest.raises(RuntimeError, match="simulated process loss"):
                submit_external_results(
                    service,
                    session.session_id,
                    action_id=f"result{index}",
                    revision=session.revision,
                    paths=[path],
                )
            monkeypatch.setattr(external, "_finish_tuning", original_finish)
            service = WorkflowService(tmp_path)
            session = service.read(session.session_id)
            session = prepare_external_run(
                service,
                session.session_id,
                action_id="resume-after-crash",
                revision=session.revision,
                stage="tuning_probe",
            )
        else:
            session = submit_external_results(
                service,
                session.session_id,
                action_id=f"result{index}",
                revision=session.revision,
                paths=[path],
            )
        if index == 0:
            assert session.controller_freeze == original
    assert_sync_equivalent(session)
    if outcome == "no_improvement":
        assert session.status == "capability_gap"
        assert session.tuning["reason"] == "no_strict_development_improvement"
        assert not session.tuning["accepted"]
        assert session.controller_freeze == original
        assert not session.confirmation
        return
    assert session.status == "awaiting_confirmation"
    assert session.tuning["best_parameters"] == {"kp": 0.5}
    assert session.freeze_history[-1] == original
    assert session.external_workflow["tuning"]["completed"]
    assert [
        row["freeze"] for row in session.external_workflow["tuning"]["candidates"]
    ] == [row["freeze"] for row in candidates]
    session = prepare_external_run(
        service,
        session.session_id,
        action_id="fresh",
        revision=session.revision,
        stage="fresh_confirmation",
    )
    active = session.external_workflow["active_request"]
    assert active["execution_request"]["trials"][0]["trial_id"] == "f0"
    path = result_zip(
        tmp_path, active, output_scale=0.4 if outcome == "confirmation_failed" else 1.0
    )
    session = submit_external_results(
        service,
        session.session_id,
        action_id="fresh-result",
        revision=session.revision,
        paths=[path],
    )
    expected = (
        "capability_gap" if outcome == "confirmation_failed" else "performance_met"
    )
    assert session.status == expected
    assert session.confirmation["status"] == (
        "performance_not_met" if outcome == "confirmation_failed" else "performance_met"
    )
    if outcome == "confirmation_failed":
        assert not session.pending_actions
        assert len(session.confirmation_history) == 2
        assert (
            sum("calculated_status" in item for item in session.confirmation_history)
            == 1
        )
        assert (
            sum(
                item["stage"] == "fresh_confirmation"
                for item in session.external_workflow["requests"]
            )
            == 1
        )
        assert len(session.external_workflow["tuning"]["candidates"]) == 2
        assert session.external_workflow["tuning"]["completed"]
        assert session.evaluation_replays[-1]["matches_previous"]


def test_absent_external_state_is_omitted_and_unknown_version_rejected(tmp_path):
    from cfdc.kernel import EvidenceSession

    session = WorkflowService(tmp_path).create_task(
        {
            "description": "Hold output",
            "measured_signals": ["output"],
            "control_input": "input",
        }
    )
    assert "external_workflow" not in session.to_dict()
    value = session.to_dict()
    value["external_workflow"] = {"workflow_version": "future/v99"}
    with pytest.raises(ValueError, match="external_workflow_version_mismatch"):
        EvidenceSession.from_dict(value)


@pytest.mark.parametrize("stage", ["development", "fresh_confirmation"])
@pytest.mark.parametrize("crash_method", ["record_evaluation", "replay_evaluation"])
def test_external_evaluation_recovers_recorded_packet_without_upload_or_duplicate(
    tmp_path, monkeypatch, stage, crash_method
):
    from dataclasses import replace

    from cfdc.kernel.external import prepare_external_run, submit_external_results

    service, session = external_prepared(tmp_path)
    if stage == "fresh_confirmation":
        session = service._save(
            service._append(
                replace(
                    session, status="awaiting_confirmation", tuning={"accepted": True}
                ),
                "test_confirmation_ready",
                "confirmation-ready",
                {},
            )
        )
    session = prepare_external_run(
        service,
        session.session_id,
        action_id="request",
        revision=session.revision,
        stage=stage,
    )
    active = session.external_workflow["active_request"]
    path = result_zip(tmp_path, active)
    original = getattr(service, crash_method)

    def crash(*args, **kwargs):
        original(*args, **kwargs)
        raise RuntimeError("process lost after evaluation save")

    monkeypatch.setattr(service, crash_method, crash)
    with pytest.raises(RuntimeError, match="process lost"):
        submit_external_results(
            service,
            session.session_id,
            action_id="results",
            revision=session.revision,
            paths=[path],
        )
    path.unlink()
    service = WorkflowService(tmp_path)
    session = service.read(session.session_id)
    assert len(session.evaluation_packets) == 1
    session = submit_external_results(
        service,
        session.session_id,
        action_id="resume",
        revision=session.revision,
        paths=[],
    )
    assert session.status == "performance_met"
    assert len(session.evaluation_packets) == 1
    assert len(session.evaluation_replays) == 1
    assert session.external_workflow["active_request"] is None
    assert len(session.external_workflow["receipts"]) == 1
    assert session.external_workflow["receipts"][0]["uploads"][0]["sha256"]
    again = submit_external_results(
        service, session.session_id, action_id="resume", revision=0, paths=[]
    )
    assert again.revision == session.revision


def test_external_probe_evidence_failure_is_a_hard_gate(tmp_path, monkeypatch):
    from copy import deepcopy
    from dataclasses import replace

    from cfdc.kernel import TuningContract
    from cfdc.kernel.external import prepare_external_run, submit_external_results
    from cfdc.kernel.service import independent_judge

    service, session = external_prepared(tmp_path)
    state = deepcopy(session.external_workflow)
    state["tuning"] = {
        "contract": TuningContract(
            parameter_whitelist=("kp",),
            parameter_domains={"kp": (0.1, 4.0)},
            budget_confirmed=True,
            development_repeats=1,
            fresh_repeats=1,
        ).to_dict(),
        "candidates": [
            {
                "candidate_id": f"probe-{index}",
                "qualification": {"status": "offline_qualified"},
                "freeze": session.controller_freeze,
                "result": None,
            }
            for index in range(2)
        ],
        "completed": False,
    }
    session = service._save(
        service._append(
            replace(session, external_workflow=state),
            "test_probes_ready",
            "probes-ready",
            {},
        )
    )
    session = prepare_external_run(
        service,
        session.session_id,
        action_id="request",
        revision=session.revision,
        stage="tuning_probe",
    )
    path = result_zip(tmp_path, session.external_workflow["active_request"])

    def invalid_evidence(freeze, packet):
        judge = independent_judge(freeze, packet)
        judge["evidence_gate"] = {"passed": False}
        return judge

    monkeypatch.setattr("cfdc.kernel.service.independent_judge", invalid_evidence)
    session = submit_external_results(
        service,
        session.session_id,
        action_id="results",
        revision=session.revision,
        paths=[path],
    )
    probe = session.external_workflow["tuning"]["candidates"][0]
    assert probe["result"]["stable"]
    assert probe["result"]["hard_failure"]


def test_external_stop_is_terminal_failure_not_tuning_feedback(tmp_path):
    from cfdc.kernel.external import prepare_external_run, submit_external_results

    service, session = external_prepared(tmp_path)
    session = prepare_external_run(
        service, session.session_id, action_id="request", revision=session.revision
    )
    path = result_zip(
        tmp_path, session.external_workflow["active_request"], stopped=True
    )
    session = submit_external_results(
        service,
        session.session_id,
        action_id="results",
        revision=session.revision,
        paths=[path],
    )
    assert session.status == "capability_gap"
    assert not session.evaluation["stability_gate"]["passed"]
    assert session.external_workflow["active_request"] is None
    assert session.tuning is None
