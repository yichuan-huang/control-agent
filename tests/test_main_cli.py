import json
import math
import sys

import pytest

from main import main


def write_step_result(path, estimates):
    time_s = [index * 0.1 for index in range(301)]
    input_signal = [0.0 if time < 1.0 else 0.5 for time in time_s]
    output_signal = [
        0.0
        if time < 1.0
        else 1.0 * (1.0 - math.exp(-(time - 1.0) / 3.0))
        for time in time_s
    ]
    path.write_text(
        json.dumps(
            {
                "primitive": "ramp_step",
                "estimates": estimates,
                "trace": {
                    "time_s": time_s,
                    "signals": {
                        "input setting": input_signal,
                        "measured output": output_signal,
                    },
                },
            }
        ),
        encoding="utf-8",
    )


def test_cli_propagates_safety_time_scale_and_experiment_result(
    tmp_path,
    monkeypatch,
    capsys,
):
    result_path = tmp_path / "step.json"
    write_step_result(result_path, ["static_gain", "time_constant"])
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "main.py",
            "--description",
            "A first order temperature process settles after a small heater change.",
            "--observed-output",
            "temperature",
            "--actuator",
            "heater",
            "--safety-bound",
            "output_min=20",
            "--safety-bound",
            "output_max=250",
            "--time-scale-hint-s",
            "300",
            "--experiment-result",
            str(result_path),
        ],
    )

    main()
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "controller_candidate_ready"
    assert payload["system_description"]["safety_bounds"] == {
        "output_min": 20.0,
        "output_max": 250.0,
    }
    assert payload["system_description"]["time_scale_hint_s"] == 300.0
    assert len(payload["experiment_results"]) == 1


def test_cli_rejects_duplicate_safety_bounds(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "main.py",
            "--description",
            "A first order process settles.",
            "--safety-bound",
            "output_max=1",
            "--safety-bound",
            "output_max=2",
        ],
    )

    with pytest.raises(SystemExit, match="duplicate --safety-bound key 'output_max'"):
        main()


def test_cli_rejects_invalid_experiment_json_with_path(tmp_path, monkeypatch):
    result_path = tmp_path / "bad.json"
    result_path.write_text("not-json", encoding="utf-8")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "main.py",
            "--description",
            "A first order process settles.",
            "--experiment-result",
            str(result_path),
        ],
    )

    with pytest.raises(SystemExit, match=str(result_path)):
        main()


def test_cli_rejects_overlapping_experiment_estimates(tmp_path, monkeypatch):
    first_path = tmp_path / "first.json"
    second_path = tmp_path / "second.json"
    write_step_result(first_path, ["static_gain", "time_constant"])
    write_step_result(second_path, ["time_constant"])
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "main.py",
            "--description",
            "A first order process settles.",
            "--experiment-result",
            str(first_path),
            "--experiment-result",
            str(second_path),
        ],
    )

    with pytest.raises(SystemExit, match="duplicate experiment estimate 'time_constant'"):
        main()


def test_cli_rejects_experiment_files_for_builtin_route(tmp_path, monkeypatch):
    result_path = tmp_path / "step.json"
    write_step_result(result_path, ["static_gain", "time_constant"])
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "main.py",
            "--run-route",
            "cartpole",
            "--experiment-result",
            str(result_path),
        ],
    )

    with pytest.raises(SystemExit, match="built-in route"):
        main()
