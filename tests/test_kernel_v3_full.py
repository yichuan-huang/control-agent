from __future__ import annotations

import copy
import hashlib
import json
import zipfile
from pathlib import Path

import pytest

from cfdc.controllers.kernel_synthesis import synthesize_controller
from cfdc.controllers.qualification import OFFLINE_QUALIFIED, qualify_controller
from cfdc.evidence.ingestion import GATE_DEFINITIONS, inspect_upload
from cfdc.evidence.physical import (
    audit_physical_preflight,
    normalize_engineering_values,
)
from cfdc.experiments.operator import build_operator_handoff, expected_input_waveforms
from cfdc.experiments.protocols import compile_protocol, verify_protocol
from cfdc.kernel import (
    ControllerFreeze,
    ControllerIR,
    EvaluationPacket,
    TaskContract,
    WorkflowService,
    build_migration_manifest,
    build_v3_parity_matrix,
)
from cfdc.kernel.cases import (
    AUDIT_CASES,
    TRANSITION_VARIANTS,
    public_case_catalog,
    public_training_case,
    training_catalog,
)
from cfdc.kernel.contracts import fingerprint
from cfdc.kernel.route_catalog import (
    capability_gap_routes,
    controller_contract,
    implemented_controller_families,
)
from cfdc.sim.training import build_training_provider_registries
from cfdc.web.service import validate_kernel_artifact


def _diagnostic_answers(*, mimo: bool = False) -> dict[str, dict[str, object]]:
    assessments = {
        "open_loop_stability": "stable",
        "nonminimum_phase": "minimum_phase",
        "significant_delay": "not_significant",
        "relative_degree": "low",
        "sensing_actuation_adequacy": "adequate",
        "nonlinearity_strength": "weak",
        "coupling_underactuation": "severe_mimo" if mimo else "siso",
        "uncertainty_variation": "small",
    }
    return {
        key: {
            "status": "known",
            "assessment": assessment,
            "evidence": f"public operator evidence for {key}",
            "confidence": 0.95,
        }
        for key, assessment in assessments.items()
    }


def _resolved_case(service: WorkflowService, case_id: str, *, mimo: bool = False):
    task = public_training_case(case_id)["task"]
    session = service.start(task)
    session = service.confirm_task(
        session.session_id,
        action_id="confirm",
        revision=session.revision,
    )
    session = service.submit_answer(
        session.session_id,
        action_id="diagnosis",
        revision=session.revision,
        answer=_diagnostic_answers(mimo=mimo),
    )
    return service.advance(
        session.session_id,
        action_id="route",
        revision=session.revision,
    )


def test_migration_manifest_and_v3_parity_matrix_have_source_hashes() -> None:
    source = Path("archive/CFDC_Project_v3")
    if not source.is_dir():
        pytest.skip(
            "development-only CFDC v3 archive is not shipped in release checkouts"
        )
    manifest = build_migration_manifest(source)
    matrix = build_v3_parity_matrix(source)

    assert len(manifest["items"]) == 41
    assert all(item["source_hash"] for item in manifest["items"])
    assert len(matrix["rows"]) == 11
    assert all(
        digest for row in matrix["rows"] for digest in row["source_hashes"].values()
    )
    assert manifest["runtime_archive_dependency"] is False
    assert matrix["runtime_archive_dependency"] is False


def test_case_catalog_has_five_training_six_transition_and_seven_audit_cases() -> None:
    catalog = public_case_catalog()

    assert len(training_catalog()) == 5
    assert len(TRANSITION_VARIANTS) == 6
    assert len(AUDIT_CASES) == 7
    assert len(catalog) == 18
    assert (
        public_training_case("audit_class_v_mimo")["base_case_id"]
        == "tclab_dual_heater_v1"
    )
    mimo_task = public_training_case("tclab_dual_heater_v1")["task"]
    assert len(mimo_task["control_inputs"]) == 2


def test_all_executable_controller_contracts_synthesize_and_qualify() -> None:
    mimo_families = {
        "decentralized_channel_PI",
        "static_decoupler_then_PI",
        "lag_dynamic_decoupler_then_PI",
    }
    families = implemented_controller_families()

    assert len(families) == 20
    assert capability_gap_routes()
    for family in families:
        contract = controller_contract(family)
        assert contract is not None
        feature_ids = set(contract.get("controller_features", ())) | set(
            contract.get("route_guard_features", ())
        )
        values = {feature_id: 1.0 for feature_id in feature_ids}
        values.update(
            local_gain_k11=1.0,
            local_gain_k12=0.1,
            local_gain_k21=0.1,
            local_gain_k22=1.0,
            gain_matrix_condition=1.22,
            static_inverse_amplification=1.2,
            base_decay_rate=1.0,
            capture_damping=1.0,
            unstable_mode_rate=1.0,
            angular_input_gain=1.0,
        )
        artifact = {
            "features": {
                key: {
                    "value": value,
                    "uncertainty": {
                        "lower_bound": value * 0.9,
                        "upper_bound": value * 1.1,
                    },
                }
                for key, value in values.items()
            },
            "missing_feature_ids": [],
            "quality": {"passed": True},
            "artifact_fingerprint": f"features-{family}",
        }
        is_mimo = family in mimo_families
        task = {
            "measured_signals": ["y1", "y2"] if is_mimo else ["y"],
            "control_inputs": ["u1", "u2"] if is_mimo else ["u"],
            "control_input": "u1" if is_mimo else "u",
            "input_min": -10.0,
            "input_max": 10.0,
            "state_stop": 100.0,
        }
        route = {
            "route_id": f"test:{family}",
            "profile_id": "mimo_2x2_coupled" if is_mimo else "first_order_lag",
            "controller_contract_id": family,
        }
        controller, audit = synthesize_controller(task, route, artifact)
        qualification = qualify_controller(
            controller,
            task=task,
            route=route,
            feature_artifact=artifact,
            protocol={"protocol_fingerprint": "test-protocol"},
        )

        assert set(contract["required_parameters"]) <= set(controller.parameters)
        assert audit["status"] == "consistent"
        assert qualification["status"] == OFFLINE_QUALIFIED


def _protocol_fixture() -> tuple[TaskContract, dict, dict]:
    task = TaskContract.from_user_input(
        {
            "description": "Measure a bounded two-input process.",
            "measured_signals": ["y1", "y2"],
            "control_inputs": ["u1", "u2"],
            "input_min": -2.0,
            "input_max": 2.0,
            "state_stop": 10.0,
            "signal_units": {"y1": "K", "y2": "K"},
            "input_units": "V",
            "budget_confirmed": True,
        }
    )
    route = {
        "route_id": "class_v_multivariable_significant_coupling:mimo_2x2_coupled",
        "profile_id": "mimo_2x2_coupled",
        "experiment_primitives": ["bounded_scan"],
    }
    provider = {
        "provider_id": "physical-provider",
        "provider_version": "v1",
        "capabilities": ["class_v_mimo_summary"],
        "execution_kind": "physical",
    }
    return task, route, provider


def test_protocol_tampering_and_operator_bundle(tmp_path: Path) -> None:
    task, route, provider = _protocol_fixture()
    protocol = compile_protocol(task, route, provider=provider).to_dict()

    assert protocol["operation"] == "bounded_mimo_dc_then_hadamard_multisine"
    assert protocol["control_inputs"] == ["u1", "u2"]
    tampered = copy.deepcopy(protocol)
    tampered["segments"][0]["input_value"] = 1.5
    with pytest.raises(ValueError, match="protocol_fingerprint_mismatch"):
        verify_protocol(tampered, task=task, route=route, provider=provider)

    handoff = build_operator_handoff(
        session_id="session-test",
        task=task.to_dict(),
        protocol=protocol,
        output_dir=tmp_path / "operator",
    )
    assert Path(handoff["operator_card_path"]).is_file()
    assert Path(handoff["precheck_checklist_path"]).is_file()
    with zipfile.ZipFile(handoff["bundle_path"]) as archive:
        names = set(archive.namelist())
    assert {
        "operator_card.json",
        "upload_schema.json",
        "precheck_checklist.json",
    } <= names
    assert (
        len([name for name in names if name.startswith("data_templates/")])
        == protocol["repeats"]
    )


def _write_upload(
    path: Path,
    protocol: dict,
    *,
    session_id: str = "session-test",
    repeats: int | None = None,
    time_offset: float = 0.0,
    input_offset: float = 0.0,
    noisy_outputs: bool = False,
) -> None:
    time_s, commands = expected_input_waveforms(protocol)
    rows = []
    repeat_count = protocol["repeats"] if repeats is None else repeats
    command_values = list(commands.values())
    for index in range(repeat_count):
        scale = 100.0 * (index - 1) if noisy_outputs else 1.0
        rows.append(
            {
                "repeat": index + 1,
                "time_s": (time_s + time_offset).tolist(),
                "inputs": {
                    name: (
                        values + (input_offset if input_index == 0 else 0.0)
                    ).tolist()
                    for input_index, (name, values) in enumerate(commands.items())
                },
                **{
                    output_name: (
                        scale * command_values[output_index % len(command_values)]
                    ).tolist()
                    for output_index, output_name in enumerate(
                        protocol["requested_signals"]
                    )
                },
            }
        )
    path.write_text(
        json.dumps(
            {
                "session_id": session_id,
                "protocol_fingerprint": protocol["protocol_fingerprint"],
                "repeats": rows,
            }
        ),
        encoding="utf-8",
    )


def test_upload_all_eight_gates_and_rejected_attempt_is_non_consuming(
    tmp_path: Path,
) -> None:
    task, route, provider = _protocol_fixture()
    protocol = compile_protocol(task, route, provider=provider).to_dict()
    operator_report = {"decision": "accepted"}
    valid = tmp_path / "valid.json"
    _write_upload(valid, protocol)

    accepted = inspect_upload(
        [valid],
        session_id="session-test",
        protocol=protocol,
        operator_report=operator_report,
    )
    assert accepted["audit"]["status"] == "accepted"
    assert len(accepted["traces"]) == protocol["repeats"]
    assert set(GATE_DEFINITIONS) == {item["id"] for item in accepted["audit"]["gates"]}

    invalid_format = tmp_path / "invalid.txt"
    invalid_format.write_text("invalid", encoding="utf-8")
    cases = [("operator_authorization", [valid], None, {})]
    cases.append(("file_format", [invalid_format], operator_report, {}))
    wrong_session = tmp_path / "wrong-session.json"
    _write_upload(wrong_session, protocol, session_id="other-session")
    cases.append(("session_binding", [wrong_session], operator_report, {}))
    wrong_repeats = tmp_path / "wrong-repeats.json"
    _write_upload(wrong_repeats, protocol, repeats=1)
    cases.append(("repeat_count", [wrong_repeats], operator_report, {}))
    wrong_time = tmp_path / "wrong-time.json"
    _write_upload(wrong_time, protocol, time_offset=1.0)
    cases.append(("timebase", [wrong_time], operator_report, {}))
    wrong_input = tmp_path / "wrong-input.json"
    _write_upload(wrong_input, protocol, input_offset=0.5)
    cases.append(("input_waveform", [wrong_input], operator_report, {}))
    cases.append(
        ("safety_limits", [valid], operator_report, {"stopped_on_limit": True})
    )
    noisy = tmp_path / "noisy.json"
    _write_upload(noisy, protocol, noisy_outputs=True)
    cases.append(("signal_quality", [noisy], operator_report, {}))

    assert len(cases) == len(GATE_DEFINITIONS)
    for expected_gate, paths, report, kwargs in cases:
        result = inspect_upload(
            paths,
            session_id="session-test",
            protocol=protocol,
            operator_report=report,
            **kwargs,
        )
        assert result["audit"]["status"] == "rejected"
        assert result["audit"]["failed_gate"] == expected_gate
        assert result["traces"] == []
        assert result["audit"]["raw_files_persisted"] is False


@pytest.mark.parametrize(
    ("case_id", "mimo", "family"),
    [
        ("dc_motor_speed_v1", False, "PI"),
        ("tclab_dual_heater_v1", True, "decentralized_channel_PI"),
    ],
)
def test_registered_case_full_chain_reaches_independent_evaluation(
    tmp_path: Path,
    case_id: str,
    mimo: bool,
    family: str,
) -> None:
    service = WorkflowService(tmp_path / case_id)
    session = _resolved_case(service, case_id, mimo=mimo)
    identification, identification_id, evaluation, evaluation_id = (
        build_training_provider_registries(case_id)
    )
    session = service.run_until_blocked(
        session.session_id,
        provider_registry=identification,
        identification_provider_id=identification_id,
        evaluation_provider_registry=evaluation,
        evaluation_provider_id=evaluation_id,
    )

    assert session.status == "performance_met"
    assert session.feature_artifact["feature_version"] == "cfdc-features/v1"
    assert not session.feature_artifact["missing_feature_ids"]
    assert session.controller_candidate["ir"]["family"] == family
    assert session.controller_qualification["status"] == OFFLINE_QUALIFIED
    assert (
        session.provider_bindings["identification"]["provider_id"]
        != session.provider_bindings["evaluation"]["provider_id"]
    )
    assert session.evaluation["wilson_lower_bound_95"] >= 0.8
    assert all(
        "dc_gain_matrix" not in json.dumps(item, ensure_ascii=False)
        for item in session.evidence
    )
    assert session.evaluation["private_truth_used"] is False
    if mimo:
        assert session.protocols[-1]["data_kind"] == "class_v_mimo_summary"
        assert len(session.task.control_inputs) == 2
        assert {
            "local_gain_k11",
            "local_gain_k12",
            "local_gain_k21",
            "local_gain_k22",
        } <= set(session.feature_artifact["features"])


def test_v3_import_is_read_only_safe_and_idempotent(tmp_path: Path) -> None:
    source = tmp_path / "v3-source"
    source.mkdir()
    task_path = source / "task.json"
    task_path.write_text(
        json.dumps(
            {
                "task": {
                    "description": "Hold a measured public output.",
                    "task_type": "local_setpoint_hold",
                    "measured_signals": ["output"],
                    "control_input": "input",
                    "input_min": -1,
                    "input_max": 1,
                    "state_stop": 4,
                }
            }
        ),
        encoding="utf-8",
    )
    private_path = source / "private.json"
    private_path.write_text(
        json.dumps({"private_truth": {"gain": 2.0}}),
        encoding="utf-8",
    )
    before = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in source.iterdir()
    }
    service = WorkflowService(tmp_path / "sessions")

    imported = service.import_v3(source)
    repeated = service.import_v3(source)

    after = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in source.iterdir()
    }
    assert repeated.session_id == imported.session_id
    assert before == after
    assert imported.import_report["source_modified"] is False
    assert imported.import_report["private_truth_imported"] is False
    assert imported.pending_actions[0]["action"] == "confirm_task"

    unsafe = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(unsafe, "w") as archive:
        archive.writestr("../task.json", task_path.read_bytes())
    with pytest.raises(ValueError, match="v3_import_unsafe_path"):
        service.import_v3(unsafe)


def test_session_v1_upgrades_on_first_explicit_mutation(tmp_path: Path) -> None:
    service = WorkflowService(tmp_path)
    session = service.start(
        {
            "description": "Hold a measured output in a bounded software experiment.",
            "measured_signals": ["output"],
            "control_input": "input",
            "input_min": -1.0,
            "input_max": 1.0,
            "state_stop": 4.0,
        }
    )
    path = tmp_path / f"{session.session_id}.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    raw["session_version"] = "cfdc-session/v1.0"
    path.write_text(json.dumps(raw), encoding="utf-8")

    loaded = service.read(session.session_id)
    assert loaded.session_version == "cfdc-session/v1.0"

    upgraded = service.confirm_task(
        loaded.session_id,
        action_id="upgrade-v1",
        revision=loaded.revision,
    )
    assert upgraded.session_version == "cfdc-session/v2.0"
    assert (
        json.loads(path.read_text(encoding="utf-8"))["session_version"]
        == "cfdc-session/v2.0"
    )


def test_physical_preflight_and_engineering_unit_normalization() -> None:
    ready = audit_physical_preflight(
        {
            "task": {"task_fingerprint": "task-1"},
            "protocol": {"protocol_fingerprint": "protocol-1"},
            "controller_freeze": {"protocol_fingerprint": "protocol-1"},
            "provider": {"provider_id": "physical-provider", "provider_version": "v1"},
            "device_id": "device-01",
            "attestation": {"operator": "operator-01", "prechecks_complete": True},
        }
    )
    assert ready["status"] == "ready_for_operator_review"
    assert ready["hardware_execution_authorized"] is False
    assert normalize_engineering_values(
        [10.0, 12.0, 14.0], {"zero": 10.0, "scale": 2.0}
    ) == [0.0, 1.0, 2.0]

    mismatch = audit_physical_preflight(
        {
            "task": {"task_fingerprint": "task-1"},
            "protocol": {"protocol_fingerprint": "protocol-2"},
            "controller_freeze": {"protocol_fingerprint": "protocol-1"},
            "provider": {"provider_id": "physical-provider", "provider_version": "v1"},
            "device_id": "device-01",
            "attestation": {"operator": "operator-01", "prechecks_complete": True},
        }
    )
    assert mismatch["status"] == "not_ready"
    assert mismatch["reasons"] == ["freeze_protocol_binding_mismatch"]
    with pytest.raises(ValueError, match="engineering_unit_scale_invalid"):
        normalize_engineering_values([1.0], {"scale": 0.0})


def test_expert_artifact_validation_checks_typed_fingerprints(tmp_path: Path) -> None:
    task, route, provider = _protocol_fixture()
    protocol = compile_protocol(task, route, provider=provider).to_dict()
    controller = ControllerIR(
        family="PI",
        measured_signals=("y1", "y2"),
        control_inputs=("u1", "u2"),
        parameters={"kp": 1.0, "ki": 0.2},
        parameter_domains={"kp": (0.1, 2.0), "ki": (0.01, 1.0)},
        output_bounds=(-2.0, 2.0),
        stop_conditions=("state_stop",),
        integral_handling="anti_windup",
    ).to_dict()
    freeze = ControllerFreeze(
        session_id="session-artifact",
        task_fingerprint=task.fingerprint,
        controller=controller,
        evidence_fingerprints=("evidence-1",),
        runtime_contract={"command_bounds": [-2.0, 2.0]},
        evaluation_contract={"success": {"steady_state_error_max": 0.2}},
        source_version="test",
    ).to_dict()
    packet = EvaluationPacket(
        session_id="session-artifact",
        task_fingerprint=task.fingerprint,
        freeze_fingerprint=freeze["freeze_fingerprint"],
        provider_id="evaluation-provider",
        provider_version="v1",
        trials=({"trial_id": "trial-1", "stable": True, "performance_pass": True},),
        evidence_fingerprints=("evidence-1",),
    ).to_dict()
    feature_artifact = {
        "feature_version": "cfdc-features/v1",
        "features": {},
        "missing_feature_ids": [],
    }
    feature_artifact["artifact_fingerprint"] = fingerprint(feature_artifact)
    qualification = {
        "qualification_version": "cfdc-qualification/v1",
        "status": "offline_qualified",
    }
    qualification["qualification_fingerprint"] = fingerprint(qualification)

    service = WorkflowService(tmp_path)
    session = service.start(task)
    artifacts = {
        "task": task.to_dict(),
        "protocol": protocol,
        "controller_ir": controller,
        "freeze": freeze,
        "evaluation_packet": packet,
        "features": feature_artifact,
        "qualification": qualification,
        "session": session.to_dict(),
    }
    for expected_kind, artifact in artifacts.items():
        validated = validate_kernel_artifact(artifact)
        assert validated["status"] == "valid"
        assert validated["artifact_kind"] == expected_kind

    tampered = copy.deepcopy(protocol)
    tampered["repeats"] += 1
    with pytest.raises(ValueError, match="protocol_fingerprint_mismatch"):
        validate_kernel_artifact(tampered)
    fake = {
        "feature_version": "unknown",
        "artifact_fingerprint": fingerprint({"feature_version": "unknown"}),
    }
    with pytest.raises(ValueError, match="无法识别版本化"):
        validate_kernel_artifact(fake)


def test_public_artifact_exports_validate_and_bundle_excludes_raw_uploads(
    tmp_path: Path,
) -> None:
    service = WorkflowService(tmp_path / "sessions")
    session = _resolved_case(service, "dc_motor_speed_v1")
    identification, identification_id, evaluation, evaluation_id = (
        build_training_provider_registries("dc_motor_speed_v1")
    )
    session = service.run_until_blocked(
        session.session_id,
        provider_registry=identification,
        identification_provider_id=identification_id,
        evaluation_provider_registry=evaluation,
        evaluation_provider_id=evaluation_id,
    )
    assert session.status == "performance_met"

    for artifact_kind in (
        "protocol",
        "features",
        "controller_ir",
        "qualification",
        "freeze",
        "evaluation",
        "result",
        "audit",
    ):
        path = service.export_artifact(session.session_id, artifact_kind)
        validated = validate_kernel_artifact(
            json.loads(path.read_text(encoding="utf-8"))
        )
        assert validated["status"] == "valid"

    session_path = service.root / f"{session.session_id}.json"
    raw_session = json.loads(session_path.read_text(encoding="utf-8"))
    raw_session["tuning"] = {"status": "completed", "accepted": True}
    raw_session["confirmation"] = {
        "status": "performance_met",
        "freeze_fingerprint": session.controller_freeze["freeze_fingerprint"],
    }
    session_path.write_text(json.dumps(raw_session), encoding="utf-8")
    for artifact_kind in ("feedback", "confirmation"):
        path = service.export_artifact(session.session_id, artifact_kind)
        validated = validate_kernel_artifact(
            json.loads(path.read_text(encoding="utf-8"))
        )
        assert validated["artifact_kind"] == artifact_kind

    bundle = service.export_result_bundle(session.session_id)
    with zipfile.ZipFile(bundle) as archive:
        names = set(archive.namelist())
        manifest = json.loads(archive.read("manifest.json"))
        assert not any("raw_upload" in name for name in names)
        assert manifest["raw_uploads_included"] is False
        assert manifest["private_truth_included"] is False
        result = json.loads(archive.read("result.json"))
    assert validate_kernel_artifact(result)["artifact_kind"] == "result"


def test_physical_upload_receipt_and_operator_bundle_are_exportable(
    tmp_path: Path,
) -> None:
    service = WorkflowService(tmp_path / "physical")
    session = _resolved_case(service, "tclab_dual_heater_v1", mimo=True)
    provider = {
        "provider_id": "physical-provider",
        "provider_version": "v1",
        "capabilities": ["class_v_mimo_summary"],
        "execution_kind": "physical",
        "binding_role": "identification",
    }
    session = service.set_provider(
        session.session_id,
        action_id="physical-provider",
        revision=session.revision,
        provider=provider,
    )
    session = service.compile_protocol(
        session.session_id,
        action_id="physical-protocol",
        revision=session.revision,
    )
    session = service.prepare_operator_handoff(
        session.session_id,
        action_id="physical-handoff",
        revision=session.revision,
    )
    handoff = session.operator_handoffs[-1]
    session = service.record_operator_report(
        session.session_id,
        action_id="physical-report",
        revision=session.revision,
        report={
            "decision": "accepted",
            "prechecks_completed": handoff["prechecks"],
            "note": "checked by operator",
        },
    )
    upload = tmp_path / "physical-upload.json"
    _write_upload(
        upload,
        session.protocols[-1],
        session_id=session.session_id,
    )
    session = service.ingest_upload(
        session.session_id,
        action_id="physical-upload",
        revision=session.revision,
        paths=[upload],
    )
    assert session.upload_attempts[-1]["status"] == "accepted"

    receipt_path = service.export_artifact(session.session_id, "upload_receipt")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert validate_kernel_artifact(receipt)["artifact_kind"] == "upload_receipt"
    assert service.export_artifact(session.session_id, "operator_bundle").is_file()
