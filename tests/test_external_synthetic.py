import csv
import io
import json
import math
import os
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from tests import external_synthetic


def _operator_bundle(path: Path, *, inputs=("drive",), outputs=("sense",)) -> Path:
    card = {
        "control_inputs": list(inputs),
        "requested_signals": list(outputs),
        "sample_period_s": 0.1,
    }
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=["time_s", *inputs, *outputs])
    writer.writeheader()
    for index in range(4):
        writer.writerow(
            {
                "time_s": index / 10,
                **dict.fromkeys(inputs, 1),
                **dict.fromkeys(outputs, ""),
            }
        )
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("operator_card.json", json.dumps(card))
        archive.writestr("data_templates/repeat_01.csv", stream.getvalue())
    return path


def _evaluation_bundle(path: Path) -> Path:
    controller = {
        "family": "PI",
        "measured_signals": ["temperature"],
        "control_inputs": ["heater"],
        "parameters": {"kp": 0.5, "ki": 0.1, "reference_filter_rate": 5.0},
        "parameter_domains": {
            "kp": [-10, 10],
            "ki": [-10, 10],
            "reference_filter_rate": [0.1, 20],
        },
    }
    request = {
        "controller": controller,
        "sample_time_s": 0.1,
        "horizon_s": 0.3,
        "measured_signals": ["temperature"],
        "tracked_signals": ["temperature"],
        "control_inputs": ["heater"],
        "input_bounds": {"heater": [-1, 1]},
        "output_bounds": {},
        "state_bounds": {},
        "controller_state_bounds": {},
        "state_stop": None,
        "references": {"temperature": 0.5},
        "trials": [{"trial_id": "trial-a", "seed": 123, "scenario_id": "nominal"}],
        "phases": [],
        "disturbance": None,
        "evaluation_split": "development",
    }
    manifest = {
        "request_id": "req-1",
        "trials": [{"trial_id": "trial-a", "file": "trial-0001.json"}],
    }
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("execution-request.json", json.dumps(request))
        archive.writestr("manifest.json", json.dumps(manifest))
    return path


def test_fixture_catalog_and_validation_require_explicit_siso_model():
    assert {row["model_id"] for row in external_synthetic.catalog()} == {
        "optical",
        "vacuum",
        "ink",
    }
    task = {"control_inputs": ["任意输入"], "measured_signals": ["任意输出"]}
    external_synthetic.validate_task("optical", task)
    assert external_synthetic.apparatus(
        "vacuum", ["custom-u"], ["custom-y"]
    ).inputs == ("custom-u",)
    with pytest.raises(ValueError, match="synthetic_model_unknown"):
        external_synthetic.validate_task("guessed-from-task", task)
    with pytest.raises(ValueError, match="synthetic_model_requires_siso"):
        external_synthetic.validate_task(
            "ink", {"control_inputs": ["u1", "u2"], "measured_signals": ["y"]}
        )


@pytest.mark.parametrize(
    ("model_id", "expected"),
    [
        ("optical", 1.6 * (1 - math.exp(-1 / 1.1))),
        ("vacuum", -1.4 * (1 - math.exp(-0.6 / 1.3))),
        ("ink", -1.8 * (1 - 1.5 * math.exp(-2 / 3) + 0.5 * math.exp(-2))),
    ],
)
def test_synthetic_apparatus_matches_analytic_unit_step_response(model_id, expected):
    plant = external_synthetic.apparatus(model_id, ["u"], ["y"])
    assert plant.measure() == {"y": 0.0}
    for _ in range(10):
        plant.advance({"u": 1.0}, 0.1)
    assert plant.measure()["y"] == pytest.approx(expected)


def test_trial_checkpoint_resume_tamper_rejection_and_result_assembly(tmp_path):
    bundle = _evaluation_bundle(tmp_path / "request.zip")
    output = tmp_path / "checkpoints"
    assert external_synthetic.bundle_trials(bundle) == ["trial-a"]
    first = external_synthetic.execute_trial(bundle, output, "optical", "trial-a")
    assert first["status"] == "completed"
    assert first["reused"] is False
    (output / f"{first['output_filename']}.completed.json").unlink()
    recovered = external_synthetic.execute_trial(bundle, output, "optical", "trial-a")
    assert recovered == {**first, "reused": False, "recovered": True}
    second = external_synthetic.execute_trial(bundle, output, "optical", "trial-a")
    assert second == {**first, "reused": True, "recovered": True}
    result = external_synthetic.assemble_results(
        bundle, output, tmp_path / "result.zip"
    )
    with zipfile.ZipFile(result) as archive:
        assert set(archive.namelist()) == {"manifest.json", "trial-0001.json"}
        assert json.loads(archive.read("trial-0001.json"))["trial_id"] == "trial-a"
    assert external_synthetic.assemble_results(bundle, output, result) == result
    (output / first["output_filename"]).write_text("tampered", encoding="utf-8")
    with pytest.raises(ValueError, match="synthetic_checkpoint_conflict"):
        external_synthetic.execute_trial(bundle, output, "optical", "trial-a")


def test_private_plant_definition_change_invalidates_binding_and_checkpoint(
    tmp_path, monkeypatch
):
    bundle = _evaluation_bundle(tmp_path / "request.zip")
    output = tmp_path / "checkpoints"
    original_binding = external_synthetic.binding("optical")
    external_synthetic.execute_trial(bundle, output, "optical", "trial-a")

    monkeypatch.setitem(external_synthetic._TRANSFERS, "optical", ([1.7], [1.1, 1.0]))

    changed_binding = external_synthetic.binding("optical")
    assert changed_binding["model_fingerprint"] != original_binding["model_fingerprint"]
    assert "transfer" not in changed_binding
    assert "delay" not in changed_binding
    with pytest.raises(ValueError, match="synthetic_checkpoint_conflict"):
        external_synthetic.execute_trial(bundle, output, "optical", "trial-a")

    monkeypatch.setitem(external_synthetic._TRANSFERS, "optical", ([1.6], [1.1, 1.0]))
    monkeypatch.setitem(external_synthetic._INPUT_DELAYS_S, "optical", 0.1)
    delay_binding = external_synthetic.binding("optical")
    assert delay_binding["model_fingerprint"] != original_binding["model_fingerprint"]


def test_identification_cli_runs_one_trial_independently(tmp_path):
    bundle = _operator_bundle(tmp_path / "operator.zip")
    assert external_synthetic.bundle_trials(bundle) == ["repeat_01.csv"]
    output = tmp_path / "output"
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "tests.external_synthetic",
            "--bundle",
            str(bundle),
            "--output-dir",
            str(output),
            "--model",
            "vacuum",
            "--trial",
            "repeat_01.csv",
        ],
        check=True,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parents[1],
        env={
            "PATH": os.environ.get("PATH", ""),
            "PYTHONPATH": str(Path(__file__).parents[1]),
        },
    )
    result = json.loads(completed.stdout)
    assert result["status"] == "completed"
    rows = list(csv.DictReader((output / result["output_filename"]).open()))
    assert rows[0]["sense"] == "0"
    assert rows[-1]["sense"] != ""


@pytest.mark.parametrize("bundle_kind", ["identification", "evaluation"])
def test_legacy_positional_cli_generates_download_upload_evidence(
    tmp_path, bundle_kind
):
    bundle = (
        _operator_bundle(tmp_path / "operator.zip")
        if bundle_kind == "identification"
        else _evaluation_bundle(tmp_path / "request.zip")
    )
    output = tmp_path / (
        "identification" if bundle_kind == "identification" else "results.zip"
    )
    completed = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).with_name("external_synthetic.py")),
            str(bundle),
            str(output),
            "--plant",
            "optical",
        ],
        check=True,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parents[1],
        env={
            "PATH": os.environ.get("PATH", ""),
            "PYTHONPATH": str(Path(__file__).parents[1]),
        },
    )
    assert completed.stdout == ""
    if bundle_kind == "identification":
        with (output / "repeat_01.csv").open() as stream:
            rows = list(csv.DictReader(stream))
        assert len(rows) == 4
        assert float(rows[0]["sense"]) == 0
        assert float(rows[-1]["sense"]) > 0
    else:
        with zipfile.ZipFile(output) as archive:
            assert set(archive.namelist()) == {"manifest.json", "trial-0001.json"}
            assert json.loads(archive.read("trial-0001.json"))["trial_id"] == "trial-a"


def test_real_operator_handoff_templates_are_runner_trials(tmp_path):
    from cfdc.experiments.operator import build_operator_handoff

    protocol = {
        "protocol_fingerprint": "protocol-1",
        "operation": "bounded_step",
        "data_kind": "timeseries",
        "repeats": 2,
        "sample_period_s": 0.1,
        "duration_s": 0.2,
        "expected_sample_count": 3,
        "input_bounds": {"actuator": [-1, 1]},
        "stop_condition": "bounded",
        "requested_signals": ["sensor"],
        "control_inputs": ["actuator"],
        "units": {"actuator": "1", "sensor": "1"},
        "segments": [{"duration_s": 0.2, "input_value": 0.5}],
    }
    handoff = build_operator_handoff(
        session_id="managed-test",
        task={"task_fingerprint": "task-1"},
        protocol=protocol,
        output_dir=tmp_path / "handoff",
    )
    bundle = Path(handoff["bundle_path"])
    assert external_synthetic.bundle_trials(bundle) == [
        "repeat_01.csv",
        "repeat_02.csv",
    ]
    completed = external_synthetic.execute_trial(
        bundle, tmp_path / "checkpoints", "ink", "repeat_01.csv"
    )
    assert completed["status"] == "completed"
