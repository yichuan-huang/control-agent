import json
import subprocess
import sys
from pathlib import Path

import pytest

from main import main, parse_args, parse_safety_bounds


def test_cli_doctor_outputs_structured_json_and_skips_workflow(monkeypatch, capsys):
    monkeypatch.setattr(
        "main.run_doctor",
        lambda **kwargs: type(
            "Report",
            (),
            {"to_dict": lambda self: {"ok": True, "status": "pass", "checks": []}},
        )(),
    )
    monkeypatch.setattr(sys, "argv", ["main.py", "--doctor"])

    main()

    payload = json.loads(capsys.readouterr().out)
    assert payload == {"ok": True, "status": "pass", "checks": []}


def _kernel_answers() -> dict[str, dict[str, object]]:
    assessments = {
        "open_loop_stability": "stable",
        "nonminimum_phase": "minimum_phase",
        "significant_delay": "not_significant",
        "relative_degree": "low",
        "sensing_actuation_adequacy": "adequate",
        "nonlinearity_strength": "weak",
        "coupling_underactuation": "siso",
        "uncertainty_variation": "small",
    }
    return {
        key: {
            "status": "known",
            "assessment": value,
            "evidence": f"public CLI evidence for {key}",
            "confidence": 0.95,
        }
        for key, value in assessments.items()
    }


def test_kernel_cli_registered_case_auto_runs_full_chain_and_exports_bundle(
    tmp_path, monkeypatch, capsys
):
    session_dir = tmp_path / "sessions"
    result_dir = tmp_path / "results"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "main.py",
            "--kernel-session-dir",
            str(session_dir),
            "--kernel-case",
            "dc_motor_speed_v1",
            "--confirm-kernel-budget",
            "--kernel-answer",
            json.dumps(_kernel_answers()),
            "--kernel-advance",
            "--kernel-auto",
            "--kernel-result-dir",
            str(result_dir),
            "--no-rag",
        ],
    )

    main()
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "tuning_eligible"
    assert payload["feature_artifact"]["feature_version"] == "cfdc-features/v2"
    assert payload["controller_qualification"]["status"] == "offline_qualified"
    assert payload["evaluation"]["status"] == "performance_not_met"
    assert (
        payload["provider_bindings"]["identification"]["provider_id"]
        != payload["provider_bindings"]["evaluation"]["provider_id"]
    )
    bundle = Path(payload["result_bundle_path"])
    assert bundle.parent == result_dir
    assert bundle.is_file()


def test_kernel_cli_cannot_inject_evidence_into_registered_exercise_case(
    tmp_path, monkeypatch
) -> None:
    evidence_path = tmp_path / "evidence.json"
    evidence_path.write_text(
        json.dumps(
            {
                "evidence_id": "forged-cli-evidence",
                "kind": "observation",
                "source": "cli",
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "main.py",
            "--kernel-session-dir",
            str(tmp_path / "sessions"),
            "--kernel-case",
            "dc_motor_speed_v1",
            "--kernel-evidence-mode",
            "exercise_bundle",
            "--kernel-evidence",
            str(evidence_path),
            "--no-rag",
        ],
    )

    with pytest.raises(
        ValueError, match="registered_case_evidence_requires_bound_provider_or_upload"
    ):
        main()


@pytest.mark.parametrize(
    "flag",
    [
        "--workflow-version",
        "--agent-mode",
        "--use-llm",
        "--benchmark",
        "--validate-demo",
        "--diagnostic-eval",
        "--cartpole-swingup",
        "--vtol-sim",
        "--feature-ablation",
        "--run-route",
        "--model-spec",
        "--kernel-import-v3",
        "--diagnostic-session-input",
        "--measurement-response",
        "--demo-fixture",
    ],
)
def test_removed_cli_options_are_rejected(flag):
    with pytest.raises(SystemExit) as exc:
        parse_args([flag])
    assert exc.value.code == 2


@pytest.mark.parametrize("value", ["x=nan", "x=inf", "x", "=2", "x=bad"])
def test_cli_safety_bounds_reject_invalid_values(value):
    with pytest.raises(SystemExit):
        parse_safety_bounds([value])


def _run_cli(tmp_path, *args, success=True):
    result = subprocess.run(
        [
            sys.executable,
            "main.py",
            "--kernel-session-dir",
            str(tmp_path / "sessions"),
            *args,
        ],
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        capture_output=True,
        check=False,
        timeout=60,
    )
    if success:
        assert result.returncode == 0, result.stderr
        return json.loads(result.stdout)
    assert result.returncode != 0
    return result


def test_cli_subprocess_create_read_auto_export_import(tmp_path):
    created = _run_cli(tmp_path, "--kernel-case", "dc_motor_speed_v1", "--no-rag")
    session_id = created["session_id"]
    assert created["pending_actions"][0]["action"] == "confirm_task"
    read = _run_cli(tmp_path, "--kernel-session", session_id)
    assert read == created
    completed = _run_cli(
        tmp_path,
        "--kernel-session",
        session_id,
        "--kernel-case",
        "dc_motor_speed_v1",
        "--confirm-kernel-budget",
        "--kernel-answer",
        json.dumps(_kernel_answers()),
        "--kernel-advance",
        "--kernel-auto",
        "--kernel-result-dir",
        str(tmp_path / "results"),
    )
    assert completed["status"] == "tuning_eligible"
    assert completed["evaluation"]["status"] == "performance_not_met"
    features = completed["feature_artifact"]["features"]
    assert features
    evidence_ids = {row["evidence_id"] for row in completed["evidence"]}
    for feature in features.values():
        assert feature["source_evidence_ids"]
        assert set(feature["source_evidence_ids"]) <= evidence_ids
        assert (
            feature["protocol_fingerprint"]
            == completed["feature_artifact"]["selected_protocol_fingerprint"]
        )
    bundle = Path(completed["result_bundle_path"])
    before = bundle.read_bytes()
    imported = _run_cli(tmp_path, "--kernel-import-result", str(bundle))
    assert imported["session_id"] != session_id
    assert imported["pending_actions"][0]["action"] == "confirm_task"
    assert not imported.get("evaluation")
    assert not imported.get("feature_artifact")
    assert bundle.read_bytes() == before


def test_cli_subprocess_rejects_missing_task_and_invalid_options(tmp_path):
    missing = _run_cli(tmp_path, success=False)
    assert "requires --description or --kernel-case" in missing.stderr
    invalid = _run_cli(tmp_path, "--workflow-version", "legacy", success=False)
    assert invalid.returncode == 2
    assert "unrecognized arguments" in invalid.stderr


def test_cli_subprocess_description_creates_kernel_task_by_default(tmp_path):
    created = _run_cli(
        tmp_path,
        "--description",
        "A heater holds chamber temperature.",
        "--observed-output",
        "temperature",
        "--actuator",
        "voltage",
        "--safety-bound",
        "input_min=-1",
        "--safety-bound",
        "input_max=1",
        "--safety-bound",
        "state_stop=3",
        "--no-rag",
    )
    assert created["workflow_version"] == "cfdc-v6-kernel/v1"
    assert created["task"]["measured_signals"] == ["temperature"]
    assert created["task"]["control_inputs"] == ["voltage"]
    assert created["pending_actions"][0]["action"] == "confirm_task"
    assert created["agent_config"]["llm_configured"] is False
