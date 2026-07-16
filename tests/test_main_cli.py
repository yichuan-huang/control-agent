import json
import sys
from pathlib import Path

import pytest

from cfdc.diagnosis import DeterministicDiagnosticAdapter, start_diagnostic_session
from cfdc.models import DiagnosticSessionState, SystemDescription
from main import load_diagnostic_session, main, parse_args


def test_documented_deepseek_model_is_v4_pro():
    for readme in (Path("README.md"), Path("README_CN.md")):
        content = readme.read_text(encoding="utf-8")
        assert "deepseek" + "-chat" not in content
        assert '--llm-model "deepseek-v4-pro"' in content


def test_cli_description_waits_for_object_evidence(monkeypatch, capsys):
    monkeypatch.setattr(sys,"argv",["main.py","--description","A first order temperature process settles after a small heater change.","--observed-output","temperature","--actuator","heater"])
    main(); payload=json.loads(capsys.readouterr().out)
    assert payload["status"]=="awaiting_specifications"
    assert payload["semantic_selection"]["simulation_profile_id"]=="first_order_lag"
    assert payload["experiment_results"] == []
    assert payload["controller"] is None
    assert payload["evidence_requirement_plan"] is not None


def test_cli_llm_runs_same_simulation_pipeline(monkeypatch,capsys):
    captured = {}
    def adapter_factory(**kwargs):
        captured.update(kwargs)
        return DeterministicDiagnosticAdapter()
    monkeypatch.setattr("main.OpenAICompatibleDiagnosticAdapter",adapter_factory)
    monkeypatch.setattr(sys,"argv",["main.py","--run-route","cartpole","--use-llm","--llm-base-url","https://provider.example/v1","--llm-model","provider-model","--llm-api-key","test"])
    main(); payload=json.loads(capsys.readouterr().out)
    assert payload["status"]=="demo_completed"
    assert payload["semantic_selection"]["simulation_profile_id"]=="underactuated_cartpole"
    assert payload["experiment_results"] and payload["features"]
    assert captured["base_url"]=="https://provider.example/v1"
    assert captured["model"]=="provider-model"


@pytest.mark.parametrize("removed",["--workflow-mode","--experiment-result"])
def test_removed_real_and_user_experiment_options_are_rejected(removed):
    with pytest.raises(SystemExit): parse_args([removed,"value"])


def test_cli_propagates_safety_and_time_scale(monkeypatch,capsys):
    monkeypatch.setattr(sys,"argv",["main.py","--description","A first order temperature process settles after a heater change.","--observed-output","temperature","--actuator","heater","--safety-bound","max_abs_control=20","--time-scale-hint-s","2"])
    main(); payload=json.loads(capsys.readouterr().out)
    instruction=payload["experiment_plan"]["instructions"][0]
    assert instruction["input_amplitude"]==2.0
    assert instruction["duration_s"]==16.0


def test_cli_reads_and_atomically_writes_session(tmp_path,monkeypatch,capsys):
    session=start_diagnostic_session(SystemDescription(text="I have a machine."))
    source=tmp_path/"in.json"; target=tmp_path/"out.json"; source.write_text(session.model_dump_json())
    monkeypatch.setattr(sys,"argv",["main.py","--diagnostic-session-input",str(source),"--diagnostic-session-output",str(target)])
    main(); payload=json.loads(capsys.readouterr().out)
    restored=DiagnosticSessionState.model_validate_json(target.read_text())
    assert payload["diagnostic_session"]["session_id"]==session.session_id
    assert restored==session


def test_v1_complete_session_migrates_to_awaiting_specifications(tmp_path):
    state = start_diagnostic_session(
        SystemDescription(
            text="A measured first order heater settles after a small change.",
            observed_outputs=["temperature"],
            actuators=["heater"],
        )
    )
    payload = state.model_dump(mode="json")
    payload["schema_version"] = "1.0"
    payload["status"] = "ready_for_experiments"
    payload.pop("evidence_requirement_plan", None)
    payload.pop("evidence_readiness", None)
    path = tmp_path / "legacy-session.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    migrated = load_diagnostic_session(path)

    assert migrated.schema_version == "3.0"
    assert migrated.status == "awaiting_specifications"
    assert migrated.evidence_requirement_plan is not None


def test_cli_accepts_natural_language_specifications(monkeypatch, capsys):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "main.py",
            "--description",
            "A first order temperature process settles after a heater change.",
            "--observed-output", "temperature",
            "--actuator", "heater power",
            "--specification-text",
            (
                "From the manual: input_change=1 normalized_input; "
                "steady_output_change=10 degC; response_time_s=20 s; "
                "input_min=-2 normalized_input; input_max=2 normalized_input; "
                "output_min=-30 degC; output_max=80 degC."
            ),
        ],
    )

    main()
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "candidate_unvalidated"
    assert payload["evidence_boundary"] == "declared_specification_model_only"
    assert payload["controller"]["release_level"] == "candidate_unvalidated"


def test_cli_collects_repeatable_specification_answers():
    args = parse_args(
        [
            "--specification-text", "manual excerpt",
            "--specification-answer", "response_time_s=20 s",
            "--specification-answer", "output_max=80 degC",
        ]
    )

    assert args.specification_text == "manual excerpt"
    assert args.specification_answer == [
        "response_time_s=20 s",
        "output_max=80 degC",
    ]


def test_cli_accepts_structured_model_evidence(tmp_path, monkeypatch, capsys):
    model_path = tmp_path / "model.json"
    model_path.write_text(
        json.dumps(
            {
                "kind": "transfer_function",
                "numerator": [1.0],
                "denominator": [2.0, 1.0],
                "input_signal_id": "heater",
                "output_signal_id": "temperature",
                "input_units": "V",
                "output_units": "degC",
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "main.py",
            "--description",
            "A first order temperature process settles after a heater change.",
            "--observed-output",
            "temperature",
            "--actuator",
            "heater",
            "--safety-bound",
            "input_min=-1",
            "--safety-bound",
            "input_max=1",
            "--safety-bound",
            "output_min=-10",
            "--safety-bound",
            "output_max=10",
            "--time-scale-hint-s",
            "4",
            "--model-spec",
            str(model_path),
        ],
    )

    main()
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "validation_pending"
    assert payload["controller"]["release_level"] == "candidate_unvalidated"
    assert payload["features"]


def test_cli_can_submit_structured_model_to_an_awaiting_specification_session(
    tmp_path, monkeypatch, capsys
):
    session = start_diagnostic_session(
        SystemDescription(
            text="A first order temperature process settles after a heater change.",
            observed_outputs=["temperature"],
            actuators=["heater"],
            safety_bounds={
                "input_min": -1.0,
                "input_max": 1.0,
                "output_min": -10.0,
                "output_max": 10.0,
            },
            time_scale_hint_s=4.0,
        )
    )
    session_path = tmp_path / "session.json"
    session_path.write_text(session.model_dump_json(), encoding="utf-8")
    model_path = tmp_path / "model.json"
    model_path.write_text(
        json.dumps({
            "kind": "transfer_function",
            "numerator": [1.0],
            "denominator": [2.0, 1.0],
            "input_signal_id": "heater",
            "output_signal_id": "temperature",
            "input_units": "V",
            "output_units": "degC",
        }),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "main.py",
            "--diagnostic-session-input", str(session_path),
            "--model-spec", str(model_path),
        ],
    )

    main()
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "validation_pending"
    assert payload["controller"]["release_level"] == "candidate_unvalidated"
