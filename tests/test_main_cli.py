import json
import sys

import pytest

from cfdc.diagnosis import DeterministicDiagnosticAdapter, start_diagnostic_session
from cfdc.models import DiagnosticSessionState, SystemDescription
from main import main, parse_args


def test_cli_description_runs_full_automatic_simulation(monkeypatch, capsys):
    monkeypatch.setattr(sys,"argv",["main.py","--description","A first order temperature process settles after a small heater change.","--observed-output","temperature","--actuator","heater"])
    main(); payload=json.loads(capsys.readouterr().out)
    assert payload["status"]=="completed"
    assert payload["semantic_selection"]["simulation_profile_id"]=="first_order_lag"
    assert payload["experiment_results"]
    assert payload["controller"] is not None
    assert payload["adapted_controller_performance"] is not None


def test_cli_llm_runs_same_simulation_pipeline(monkeypatch,capsys):
    captured = {}
    def adapter_factory(**kwargs):
        captured.update(kwargs)
        return DeterministicDiagnosticAdapter()
    monkeypatch.setattr("main.OpenAICompatibleDiagnosticAdapter",adapter_factory)
    monkeypatch.setattr(sys,"argv",["main.py","--run-route","cartpole","--use-llm","--llm-base-url","https://provider.example/v1","--llm-model","provider-model","--llm-api-key","test"])
    main(); payload=json.loads(capsys.readouterr().out)
    assert payload["status"]=="completed"
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
