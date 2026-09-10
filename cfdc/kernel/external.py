"""Persisted external execution boundaries; uploaded traces never grant authority."""

from __future__ import annotations

import hashlib
import json
import zipfile
from copy import deepcopy
from pathlib import Path
from uuid import uuid4

from .contracts import PACKET_VERSION, ControllerFreeze, fingerprint
from .execution_contract import execution_request
from .tuning import TuningContract, bounded_parameter_candidates

VERSION = "cfdc-external-workflow/v1"
_SAFE_RESULT_ERRORS = frozenset(
    {
        "external_results_zip_required",
        "external_results_archive_invalid",
        "external_results_binding_mismatch",
        "external_results_files_mismatch",
        "external_trial_binding_mismatch",
        "external_active_freeze_mismatch",
        "error_criterion_required",
        "evaluation_repeat_count_mismatch",
        "trial_partition_missing",
        "trial_partition_invalid",
        "evaluation_provider_mismatch",
        "evaluation_evidence_binding_mismatch",
        "trial_manifest_mismatch",
        "trial_id_mismatch",
        "trajectory_required",
    }
)


def _state(session):
    value = deepcopy(session.external_workflow or {})
    if value.get("workflow_version") != VERSION:
        raise ValueError("external_source_required")
    return value


def _save(service, session, state, action_id, kind, **changes):
    return service._save(
        service._append(
            service._replace(session, external_workflow=state, **changes),
            kind,
            action_id,
            {"external_workflow_fingerprint": fingerprint(state)},
        )
    )


def select_external_source(
    service,
    session_id,
    *,
    action_id,
    revision,
    source_kind,
    source_id=None,
    execution_mode="manual",
    runner_id=None,
    model_id=None,
):
    session = service.read(session_id)
    if service._event_for_action(session, action_id):
        return session
    service._check_mutable(session, revision)
    service._check_not_frozen(session)
    if source_kind not in {"software", "measured"}:
        raise ValueError("external_source_kind_invalid")
    if execution_mode not in (None, "", "manual") or runner_id or model_id:
        raise ValueError("automatic_execution_removed")

    if session.external_workflow and (
        session.external_workflow.get("requests")
        or session.protocols
        or session.evidence
    ):
        raise ValueError("external_source_already_in_use")
    provider = {
        "provider_id": f"external-{source_kind}",
        "provider_version": VERSION,
        "execution_kind": "external",
        "source_kind": source_kind,
        "capabilities": [
            "public_trace",
            "external_execution",
            "siso_repeated_timeseries",
            "step_b_repeated_staircase",
            "class_iv_frequency_repeats",
            "class_iv_amplitude_release_repeats",
            "class_iv_release_repeats",
            "unstable_local_balance_repeats",
            "class_v_mimo_summary",
        ],
        "source_id": str(source_id or source_kind),
    }
    for role in ("identification", "evaluation"):
        session = service.set_provider(
            session_id,
            action_id=f"{action_id}:{role}",
            revision=session.revision,
            provider={**provider, "binding_role": role},
        )
    state = {
        "workflow_version": VERSION,
        "source": provider,
        "active_request": None,
        "requests": [],
        "receipts": [],
        "tuning": None,
    }
    return _save(service, session, state, action_id, "external_source_selected")


def prepare_external_run(
    service, session_id, *, action_id, revision, stage="development"
):
    session = service.read(session_id)
    if service._event_for_action(session, action_id):
        return session
    service._check_mutable(session, revision)
    service._check_elapsed_budget(session)
    state = _state(session)
    if state.get("active_request"):
        raise ValueError("external_request_already_pending")
    freeze = session.controller_freeze
    candidate_id = "baseline"
    if stage == "tuning_probe":
        tuning = state.get("tuning")
        if not tuning or tuning.get("completed"):
            raise ValueError("external_tuning_required")
        remaining = [
            row
            for row in tuning["candidates"]
            if row["qualification"].get("status") == "offline_qualified"
            and row.get("result") is None
        ]
        if not remaining:
            return _finish_tuning(service, session, action_id)
        row = remaining[0]
        freeze, candidate_id = row["freeze"], row["candidate_id"]
    elif stage == "fresh_confirmation":
        if (
            session.status != "awaiting_confirmation"
            or not session.tuning
            or not session.tuning.get("accepted")
        ):
            raise ValueError("fresh_confirmation_requires_accepted_tuning")
        candidate_id = "selected"
    elif stage != "development":
        raise ValueError("external_stage_invalid")
    elif session.evaluation_packets or state.get("tuning"):
        raise ValueError("external_development_already_consumed")
    if freeze is None:
        raise ValueError("controller_freeze_required")
    split = "fresh_confirmation" if stage == "fresh_confirmation" else "development"
    request = execution_request(freeze, split)
    binding = {
        "request_id": uuid4().hex,
        "session_id": session_id,
        "task_fingerprint": session.task.fingerprint,
        "freeze_fingerprint": freeze["freeze_fingerprint"],
        "stage": stage,
        "candidate_id": candidate_id,
    }
    manifest = {
        **binding,
        "format_version": VERSION,
        "trials": [
            {"trial_id": t["trial_id"], "file": f"trial-{i:04d}.json"}
            for i, t in enumerate(request["trials"], 1)
        ],
    }
    request_value = {**binding, "execution_request": request, "manifest": manifest}
    request_value["request_fingerprint"] = fingerprint(
        {**binding, "execution_request": request}
    )
    manifest["request_fingerprint"] = request_value["request_fingerprint"]
    directory = service.root / "external" / session_id / binding["request_id"]
    directory.mkdir(parents=True, exist_ok=False)
    package = directory / "execution-package.zip"
    with zipfile.ZipFile(package, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("execution-request.json", json.dumps(request, indent=2))
        archive.writestr("manifest.json", json.dumps(manifest, indent=2))
        archive.writestr(
            "README.txt",
            "外部执行与回传：按 execution-request.json 的固定控制器、输入边界、时间轴和试次种子执行。templates/ 内每个 JSON 是未填写的记录模板；请填入完整轨迹，将填写后的文件移到 ZIP 根目录，与原始 manifest.json 一起打包上传。不得修改绑定字段，不接受汇总指标代替轨迹。软件实验确认不授予硬件运行许可。\n",
        )
        for spec, file in zip(request["trials"], manifest["trials"], strict=True):
            template = {
                **spec,
                "trajectory": {
                    "time_s": [],
                    "outputs": {name: [] for name in request["tracked_signals"]},
                    "measurements": {name: [] for name in request["measured_signals"]},
                    "references": {name: [] for name in request["tracked_signals"]},
                    "control_inputs": {name: [] for name in request["control_inputs"]},
                    "raw_control_inputs": {
                        name: [] for name in request["control_inputs"]
                    },
                    "controller_states": [],
                    "phase_ids": [],
                },
                "events": [],
                "stop_event": {"triggered": False, "time_s": None, "reason": ""},
            }
            archive.writestr(
                f"templates/{file['file']}",
                json.dumps(template, ensure_ascii=False, indent=2),
            )
    request_value["package_path"] = str(package)
    state["active_request"] = request_value
    state["requests"].append(deepcopy(request_value))
    return _save(
        service,
        session,
        state,
        action_id,
        "external_request_prepared",
        pending_actions=(
            {
                "kind": "external_results",
                "action": "submit_external_results",
                "stage": stage,
            },
        ),
    )


def _read_results(paths, active):
    if len(paths) != 1 or Path(paths[0]).suffix.lower() != ".zip":
        raise ValueError("external_results_zip_required")
    with zipfile.ZipFile(paths[0]) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        if (
            len(names) != len(set(names))
            or len(names) > 10002
            or sum(i.file_size for i in infos) > 100_000_000
        ):
            raise ValueError("external_results_archive_invalid")
        manifest = json.loads(archive.read("manifest.json"))
        if manifest != active["manifest"]:
            raise ValueError("external_results_binding_mismatch")
        expected = {"manifest.json", *(row["file"] for row in manifest["trials"])}
        if set(names) != expected:
            raise ValueError("external_results_files_mismatch")
        trials = []
        for row in manifest["trials"]:
            trial = json.loads(archive.read(row["file"]))
            if not isinstance(trial, dict) or trial.get("trial_id") != row["trial_id"]:
                raise ValueError("external_trial_binding_mismatch")
            trials.append(trial)
    return trials


def submit_external_results(service, session_id, *, action_id, revision, paths):
    from .service import _evaluation_hard_failure, independent_judge

    session = service.read(session_id)
    if service._event_for_action(session, action_id):
        if (
            session.external_workflow
            and session.external_workflow.get("tuning")
            and not session.external_workflow["tuning"].get("completed")
        ):
            return _finish_tuning(service, session, action_id)
        return session
    state = _state(session)
    active = state.get("active_request")
    if active and active.get("pending_submission"):
        # Only finish the immutable packet already accepted before the crash.
        # No new trial is executed or ingested, even when replay already made
        # the session terminal. Revision and historical read-only gates remain.
        if session.read_only:
            raise ValueError("read_only_legacy_session")
        if revision != session.revision:
            raise ValueError(
                f"stale_revision: expected {session.revision}, got {revision}"
            )
        return _complete_recorded_evaluation(service, session, state, action_id)
    service._check_mutable(session, revision)
    service._check_elapsed_budget(session)
    if not active:
        raise ValueError("external_request_required")
    uploads = []
    for raw_path in paths:
        path = Path(raw_path)
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
        uploads.append(
            {
                "name": path.name,
                "size_bytes": path.stat().st_size,
                "sha256": digest.hexdigest(),
            }
        )
    try:
        trials = _read_results(paths, active)
        freeze = session.controller_freeze
        row = None
        if active["stage"] == "tuning_probe":
            row = next(
                row
                for row in state["tuning"]["candidates"]
                if row["candidate_id"] == active["candidate_id"]
            )
            freeze = row["freeze"]
        if not freeze or freeze["freeze_fingerprint"] != active["freeze_fingerprint"]:
            raise ValueError("external_active_freeze_mismatch")
        source = state["source"]
        packet = {
            "session_id": session_id,
            "task_fingerprint": session.task.fingerprint,
            "freeze_fingerprint": freeze["freeze_fingerprint"],
            "evidence_fingerprints": list(freeze["evidence_fingerprints"]),
            "provider_id": source["provider_id"],
            "provider_version": source["provider_version"],
            "provider_contract": {**source, "binding_role": "evaluation"},
            "evaluation_split": active["execution_request"]["evaluation_split"],
            "private_truth_returned": False,
            "packet_version": PACKET_VERSION,
            "trials": trials,
        }
        packet["packet_fingerprint"] = fingerprint(packet)
        judge = independent_judge(freeze, packet)
    except (ValueError, TypeError, KeyError, OSError, zipfile.BadZipFile) as exc:
        state["receipts"].append(
            {
                "request_id": active["request_id"],
                "accepted": False,
                "reason": str(exc)
                if str(exc) in _SAFE_RESULT_ERRORS
                else "external_results_invalid_trace",
                "error_type": type(exc).__name__,
                "uploads": uploads,
                "action_id": action_id,
            }
        )
        return _save(service, session, state, action_id, "external_results_rejected")
    artifact = (
        Path(active["package_path"]).parent
        / f"packet-{packet['packet_fingerprint']}.json"
    )
    if artifact.exists():
        if json.loads(artifact.read_text()) != packet:
            raise ValueError("external_packet_artifact_conflict")
    else:
        with artifact.open("x") as handle:
            json.dump(packet, handle, sort_keys=True)
    replay_packet = json.loads(artifact.read_text())
    replay = independent_judge(freeze, replay_packet)
    if judge["judge_fingerprint"] != replay["judge_fingerprint"]:
        raise ValueError("external_packet_replay_mismatch")
    if row is not None:
        row["result"] = {
            "stable": bool(judge["stability_gate"]["passed"]),
            "hard_failure": _evaluation_hard_failure(judge),
            "performance_pass": judge["status"] == "performance_met",
            "score": judge["score"],
            "packet": packet,
            "judge": judge,
            "freeze": freeze,
            "replay": {
                "matches_previous": True,
                "judge_fingerprint": replay["judge_fingerprint"],
            },
        }
    else:
        active["pending_submission"] = {
            "packet_path": str(artifact),
            "packet_fingerprint": packet["packet_fingerprint"],
            "judge_fingerprint": judge["judge_fingerprint"],
            "uploads": uploads,
        }
        session = _save(
            service,
            session,
            state,
            f"external:{active['request_id']}:received",
            "external_results_validated",
        )
        return _complete_recorded_evaluation(service, session, state, action_id)
    state["receipts"].append(
        {
            "request_id": active["request_id"],
            "accepted": True,
            "uploads": uploads,
            "packet_fingerprint": packet["packet_fingerprint"],
            "packet_path": str(artifact),
            "action_id": action_id,
        }
    )
    state["active_request"] = None
    session = _save(
        service,
        session,
        state,
        action_id,
        "external_results_accepted",
        **(
            {
                "pending_actions": (
                    {
                        "kind": "external_run",
                        "action": "prepare_external_run",
                        "stage": "tuning_probe",
                    },
                )
            }
            if row is not None
            else {}
        ),
    )
    if row is not None:
        return _finish_tuning(service, session, action_id)
    return session


def _complete_recorded_evaluation(service, session, state, action_id):
    """Finalize a persisted valid packet, including after terminal replay."""
    from .service import independent_judge

    active = state["active_request"]
    submission = active["pending_submission"]
    packet = json.loads(Path(submission["packet_path"]).read_text())
    freeze = session.controller_freeze
    if not freeze or freeze["freeze_fingerprint"] != active["freeze_fingerprint"]:
        raise ValueError("external_active_freeze_mismatch")
    if packet.get("packet_fingerprint") != submission["packet_fingerprint"]:
        raise ValueError("external_packet_artifact_conflict")
    judge = independent_judge(freeze, packet)
    if judge["judge_fingerprint"] != submission["judge_fingerprint"]:
        raise ValueError("external_packet_replay_mismatch")
    session = service.record_evaluation(
        session.session_id,
        action_id=f"external:{active['request_id']}:record",
        revision=session.revision,
        packet=packet,
    )
    session = service.replay_evaluation(
        session.session_id,
        action_id=f"external:{active['request_id']}:replay",
        revision=session.revision,
    )
    state = _state(session)
    if state.get("active_request") is None:
        # A concurrent retry may already have completed this exact request.
        return session
    if state["active_request"]["request_id"] != active["request_id"]:
        raise ValueError("external_request_completion_conflict")
    state["receipts"].append(
        {
            "request_id": active["request_id"],
            "accepted": True,
            "uploads": submission["uploads"],
            "packet_fingerprint": submission["packet_fingerprint"],
            "packet_path": submission["packet_path"],
            "action_id": action_id,
        }
    )
    state["active_request"] = None
    return _save(service, session, state, action_id, "external_results_accepted")


def _finish_tuning(service, session, action_id):
    state = _state(session)
    tuning = state["tuning"]
    finish_id = (
        f"external-tuning:{session.session_id}:{fingerprint(tuning['contract'])}"
    )
    candidates = tuning["candidates"]
    if any(
        row["qualification"].get("status") == "offline_qualified"
        and row.get("result") is None
        for row in candidates
    ):
        return session

    def lookup(parameters):
        return next(row for row in candidates if row["parameters"] == parameters)

    session = service.run_tuning(
        session.session_id,
        action_id=f"{finish_id}:finish",
        revision=session.revision,
        contract=tuning["contract"],
        qualify=lambda parameters: lookup(parameters)["qualification"],
        evaluate=lambda parameters, split, repeats: lookup(parameters)["result"],
    )
    tuning["completed"] = True
    return _save(
        service, session, state, f"{finish_id}:completed", "external_tuning_completed"
    )


def start_external_tuning(service, session_id, *, action_id, revision, contract=None):
    from cfdc.controllers.qualification import qualify_controller

    from .controllers import ControllerIR
    from .service import _controller_with_parameters

    session = service.read(session_id)
    if service._event_for_action(session, action_id):
        return session
    service._check_mutable(session, revision)
    service._check_elapsed_budget(session)
    state = _state(session)
    if state.get("active_request") or state.get("tuning"):
        raise ValueError("external_tuning_already_started")
    if (
        session.status != "tuning_eligible"
        or not session.task.budget_confirmed
        or not session.evaluation_replays
        or not session.evaluation_replays[-1].get("matches_previous")
    ):
        raise ValueError("tuning_requires_verified_evaluation_replay")
    freeze = session.controller_freeze
    controller = freeze["controller"]
    parameters = controller["parameters"]
    if contract is None:
        repeats = len(execution_request(freeze, "development")["trials"])
        contract = TuningContract(
            parameter_whitelist=tuple(parameters),
            parameter_domains={
                key: tuple(bounds)
                for key, bounds in controller["parameter_domains"].items()
                if key in parameters
            },
            development_repeats=repeats,
            fresh_repeats=repeats,
            budget_confirmed=True,
        )
    elif not isinstance(contract, TuningContract):
        contract = TuningContract.from_mapping(contract)
    if not contract.budget_confirmed:
        raise ValueError("tuning_budget_not_confirmed")
    for supplied, actual in (
        (contract.task_fingerprint, session.task.fingerprint),
        (contract.initial_freeze_fingerprint, freeze["freeze_fingerprint"]),
        (
            contract.evaluation_contract_fingerprint,
            fingerprint(freeze["evaluation_contract"]),
        ),
    ):
        if supplied and supplied != actual:
            raise ValueError("external_tuning_contract_binding_mismatch")
    for split, repeats in (
        ("development", contract.development_repeats),
        ("fresh_confirmation", contract.fresh_repeats),
    ):
        if len(execution_request(freeze, split)["trials"]) != repeats:
            raise ValueError("tuning_repeat_count_frozen")
    protocol = next(
        (
            item
            for item in session.protocols
            if item["protocol_fingerprint"] == session.active_protocol_fingerprint
        ),
        None,
    )
    if not protocol or not session.route or not session.feature_artifact:
        raise ValueError("tuning_candidate_qualification_context_required")
    rows = []
    for index, candidate in enumerate(
        bounded_parameter_candidates(parameters, contract), 1
    ):
        ir = _controller_with_parameters(controller, candidate)
        qualification = qualify_controller(
            ControllerIR.from_mapping(ir),
            task=session.task.to_dict(),
            route=session.route,
            feature_artifact=session.feature_artifact,
            protocol=protocol,
        )
        from .multistage import MultiStagePlan

        runtime = deepcopy(freeze["runtime_contract"])
        evaluation = deepcopy(freeze["evaluation_contract"])
        phase_plan = deepcopy(session.phase_plan)
        if phase_plan:
            phase_plan.pop("plan_fingerprint", None)
            for phase in phase_plan["phases"]:
                phase["controller"] = deepcopy(ir)
            phase_plan = MultiStagePlan.from_mapping(phase_plan).to_dict()
            runtime["phase_plan"] = deepcopy(phase_plan)
            evaluation["phase_plan"] = deepcopy(phase_plan)
        probe = ControllerFreeze(
            session_id=session_id,
            task_fingerprint=session.task.fingerprint,
            controller=ir,
            evidence_fingerprints=tuple(freeze["evidence_fingerprints"]),
            runtime_contract=runtime,
            evaluation_contract=evaluation,
            source_version="cfdc-kernel/tuning-probe-v1",
        ).to_dict()
        freeze_directory = service.root / "external" / session_id / "freezes"
        freeze_directory.mkdir(parents=True, exist_ok=True)
        freeze_path = freeze_directory / f"{probe['freeze_fingerprint']}.json"
        if freeze_path.exists():
            if json.loads(freeze_path.read_text()) != probe:
                raise ValueError("external_candidate_freeze_artifact_conflict")
        else:
            with freeze_path.open("x") as handle:
                json.dump(probe, handle, sort_keys=True)
        rows.append(
            {
                "candidate_id": f"probe-{index:04d}",
                "freeze_path": str(freeze_path),
                "parameters": candidate,
                "qualification": qualification,
                "freeze": probe,
                "result": None,
            }
        )
    state["tuning"] = {
        "contract": contract.to_dict(),
        "candidates": rows,
        "completed": False,
    }
    session = _save(
        service,
        session,
        state,
        action_id,
        "external_tuning_started",
        pending_actions=(
            {
                "kind": "external_run",
                "action": "prepare_external_run",
                "stage": "tuning_probe",
            },
        ),
    )
    return _finish_tuning(service, session, action_id)
