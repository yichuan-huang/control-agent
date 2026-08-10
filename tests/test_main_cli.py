import json
import sys
from pathlib import Path

import pytest

from cfdc.diagnosis import DeterministicDiagnosticAdapter, start_diagnostic_session
from cfdc.models import (
    DiagnosticSessionState,
    MeasuredFact,
    MeasurementAssessment,
    SystemDescription,
)
from main import load_diagnostic_session, main, parse_args

_VALID_FIELD_FACTS = {
    "open_loop_stability": "settles or remains bounded",
    "minimum_phase": (
        "starts in its final direction rather than moving the opposite way first"
    ),
    "significant_delay": (
        "begins within one sample without a separate silent interval"
    ),
    "relative_degree": "one or two dominant storage or integration processes",
    "controllability_observability": (
        "all relevant motion can be reconstructed from these synchronized records"
    ),
    "nonlinearity_strength": (
        "small positive and negative trials are smooth, reversible, and nearly proportional"
    ),
    "coupling_severity": "one main physical route from actuation to the measured motion",
    "uncertainty_magnitude": (
        "change the response rate and final level by a modest amount"
    ),
}


class CliGuidedAdapter(DeterministicDiagnosticAdapter):
    def guide_description(self, description, guidance):
        output = description.observed_outputs or ["temperature"]
        actuators = description.actuators or ["heater"]
        return {
            "guidance": [item.model_dump(mode="json") for item in guidance],
            "observed_outputs": [
                {"name": name, "source_excerpt": name} for name in output
            ],
            "actuators": [
                {"name": name, "source_excerpt": name} for name in actuators
            ],
        }

    def extract_measurements(
        self, description, measurement_plan, measurement_response, previous_assessment
    ):
        del description, measurement_response, previous_assessment
        return MeasurementAssessment(
            status="ready",
            facts=[
                MeasuredFact(
                    request_id=request.request_id,
                    source_excerpt=_VALID_FIELD_FACTS[request.request_id],
                    text_value=_VALID_FIELD_FACTS[request.request_id],
                )
                for request in measurement_plan.requests
            ],
            rationale="All diagnostic records were verified.",
        ).model_dump(mode="json")


def _enable_cli_guided_adapter(monkeypatch):
    monkeypatch.setattr(
        "main.OpenAICompatibleDiagnosticAdapter",
        lambda **kwargs: CliGuidedAdapter(),
    )


def _llm_args():
    return [
        "--use-llm",
        "--llm-base-url",
        "https://provider.example/v1",
        "--llm-model",
        "provider-model",
        "--llm-api-key",
        "test-secret",
    ]


def test_cli_measurement_response_text_and_file_are_mutually_exclusive(tmp_path):
    response_file = tmp_path / "response.txt"
    response_file.write_text("existing record", encoding="utf-8")

    with pytest.raises(SystemExit):
        parse_args(
            [
                "--measurement-response",
                "existing record",
                "--measurement-response-file",
                str(response_file),
            ]
        )


def test_cli_generic_guided_flow_requires_llm(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["main.py", "--description", "A heater changes measured temperature."],
    )

    with pytest.raises(SystemExit, match="LLM"):
        main()


def test_cli_rejects_partial_guided_adapter_capabilities(monkeypatch):
    class PartialAdapter:
        def guide_description(self, description, guidance):
            raise AssertionError("capability validation must run first")

    monkeypatch.setattr(
        "main.OpenAICompatibleDiagnosticAdapter", lambda **kwargs: PartialAdapter()
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "main.py",
            "--description",
            "A temperature process settles after a heater change.",
            "--observed-output",
            "temperature",
            "--actuator",
            "heater",
            *_llm_args(),
        ],
    )

    with pytest.raises(SystemExit, match="phrase_measurement_plan"):
        main()


def test_cli_measurement_response_requires_session(monkeypatch):
    _enable_cli_guided_adapter(monkeypatch)
    monkeypatch.setattr(
        sys,
        "argv",
        ["main.py", "--measurement-response", "record", *_llm_args()],
    )

    with pytest.raises(SystemExit, match="diagnostic-session-input"):
        main()


def test_cli_v4_session_rejects_specification_text(tmp_path, monkeypatch):
    _enable_cli_guided_adapter(monkeypatch)
    session = start_diagnostic_session(SystemDescription(text="I have a machine."))
    source = tmp_path / "v4.json"
    source.write_text(session.model_dump_json(), encoding="utf-8")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "main.py",
            "--diagnostic-session-input",
            str(source),
            "--specification-text",
            "manual facts",
            *_llm_args(),
        ],
    )

    with pytest.raises(SystemExit, match="measurement-response"):
        main()


@pytest.mark.parametrize("contents", [b"", b"\xff\xfe"])
def test_cli_rejects_empty_or_non_utf8_measurement_response_file(
    contents, tmp_path, monkeypatch
):
    _enable_cli_guided_adapter(monkeypatch)
    session = start_diagnostic_session(SystemDescription(text="I have a machine."))
    source = tmp_path / "v4.json"
    source.write_text(session.model_dump_json(), encoding="utf-8")
    response = tmp_path / "response.txt"
    response.write_bytes(contents)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "main.py",
            "--diagnostic-session-input",
            str(source),
            "--measurement-response-file",
            str(response),
            *_llm_args(),
        ],
    )

    with pytest.raises(SystemExit, match="measurement-response-file"):
        main()


def test_cli_converts_measurement_response_file_os_error_to_system_exit(
    tmp_path, monkeypatch
):
    _enable_cli_guided_adapter(monkeypatch)
    session = start_diagnostic_session(SystemDescription(text="I have a machine."))
    source = tmp_path / "v4.json"
    source.write_text(session.model_dump_json(), encoding="utf-8")
    missing_response = tmp_path / "missing-response.txt"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "main.py",
            "--diagnostic-session-input",
            str(source),
            "--measurement-response-file",
            str(missing_response),
            *_llm_args(),
        ],
    )

    with pytest.raises(SystemExit, match="invalid --measurement-response-file"):
        main()


def test_cli_rejects_v3_session_payload(tmp_path):
    session = start_diagnostic_session(SystemDescription(text="I have a machine."))
    payload = session.model_dump(mode="json")
    payload["schema_version"] = "3.0"
    source = tmp_path / "v3.json"
    source.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(SystemExit, match="v3 diagnostic session payloads are not supported"):
        load_diagnostic_session(source)


@pytest.mark.parametrize("payload", [[], "session", None, 7])
def test_cli_rejects_non_object_diagnostic_session_json(payload, tmp_path):
    source = tmp_path / "not-an-object.json"
    source.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(
        SystemExit, match="invalid --diagnostic-session-input.*JSON object"
    ):
        load_diagnostic_session(source)


def test_cli_v4_session_round_trip_accepts_measurement_response_file(
    tmp_path, monkeypatch, capsys
):
    _enable_cli_guided_adapter(monkeypatch)
    initial_path = tmp_path / "initial-v4.json"
    advanced_path = tmp_path / "advanced-v4.json"
    response_path = tmp_path / "records.txt"
    response_path.write_text("\n".join(_VALID_FIELD_FACTS.values()), encoding="utf-8")
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
            "--diagnostic-session-output",
            str(initial_path),
            *_llm_args(),
        ],
    )
    main()
    initial_payload = json.loads(capsys.readouterr().out)
    assert initial_payload["status"] == "awaiting_measurements"
    assert initial_payload["diagnostic_session"]["revision"] == 0

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "main.py",
            "--diagnostic-session-input",
            str(initial_path),
            "--diagnostic-session-output",
            str(advanced_path),
            "--measurement-response-file",
            str(response_path),
            *_llm_args(),
        ],
    )
    main()
    advanced_payload = json.loads(capsys.readouterr().out)
    restored = DiagnosticSessionState.model_validate_json(
        advanced_path.read_text(encoding="utf-8")
    )
    assert advanced_payload["status"] == "awaiting_profile_measurements"
    assert restored.status == "awaiting_profile_measurements"
    assert restored.revision == 2
    assert restored.classification is not None


def test_documented_deepseek_model_is_v4_pro():
    for readme in (Path("README.md"), Path("README_CN.md")):
        content = readme.read_text(encoding="utf-8")
        assert "deepseek" + "-chat" not in content
        assert '--llm-model "deepseek-v4-pro"' in content


def test_cli_description_waits_for_object_evidence(monkeypatch, capsys):
    _enable_cli_guided_adapter(monkeypatch)
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
            *_llm_args(),
        ],
    )
    main()
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "awaiting_measurements"
    assert payload["semantic_selection"] is None
    assert payload["experiment_results"] == []
    assert payload["controller"] is None
    assert payload["evidence_requirement_plan"] is None
    assert len(payload["diagnostic_session"]["measurement_plan"]["requests"]) == 8


def test_cli_llm_runs_same_simulation_pipeline(monkeypatch, capsys):
    captured = {}

    def adapter_factory(**kwargs):
        captured.update(kwargs)
        return DeterministicDiagnosticAdapter()

    monkeypatch.setattr("main.OpenAICompatibleDiagnosticAdapter", adapter_factory)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "main.py",
            "--run-route",
            "cartpole",
            "--use-llm",
            "--llm-base-url",
            "https://provider.example/v1",
            "--llm-model",
            "provider-model",
            "--llm-api-key",
            "test",
        ],
    )
    main()
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "demo_completed"
    assert (
        payload["semantic_selection"]["simulation_profile_id"]
        == "underactuated_cartpole"
    )
    assert payload["experiment_results"] and payload["features"]
    assert captured["base_url"] == "https://provider.example/v1"
    assert captured["model"] == "provider-model"


@pytest.mark.parametrize("removed", ["--workflow-mode", "--experiment-result"])
def test_removed_real_and_user_experiment_options_are_rejected(removed):
    with pytest.raises(SystemExit):
        parse_args([removed, "value"])


def test_cli_propagates_safety_and_time_scale(monkeypatch, capsys):
    _enable_cli_guided_adapter(monkeypatch)
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
            "max_abs_control=20",
            "--time-scale-hint-s",
            "2",
            *_llm_args(),
        ],
    )
    main()
    payload = json.loads(capsys.readouterr().out)
    description = payload["diagnostic_session"]["accumulated_description"]
    assert description["safety_bounds"]["max_abs_control"] == 20.0
    assert description["time_scale_hint_s"] == 2.0
    assert payload["experiment_plan"] is None


def test_cli_reads_and_atomically_writes_session(tmp_path, monkeypatch, capsys):
    _enable_cli_guided_adapter(monkeypatch)
    session = start_diagnostic_session(SystemDescription(text="I have a machine."))
    source = tmp_path / "in.json"
    target = tmp_path / "out.json"
    source.write_text(session.model_dump_json())
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "main.py",
            "--diagnostic-session-input",
            str(source),
            "--diagnostic-session-output",
            str(target),
            *_llm_args(),
        ],
    )
    main()
    payload = json.loads(capsys.readouterr().out)
    restored = DiagnosticSessionState.model_validate_json(target.read_text())
    assert payload["diagnostic_session"]["session_id"] == session.session_id
    assert restored == session


def test_v1_complete_session_restarts_at_v4_measurement_gate(tmp_path):
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

    assert migrated.schema_version == "4.0"
    assert migrated.status == "awaiting_measurements"
    assert migrated.evidence_requirement_plan is None


def test_cli_does_not_allow_specifications_to_bypass_measurement_gate(monkeypatch):
    _enable_cli_guided_adapter(monkeypatch)
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
            "heater power",
            "--specification-text",
            (
                "From the manual: input_change=1 normalized_input; "
                "steady_output_change=10 degC; response_time_s=20 s; "
                "input_min=-2 normalized_input; input_max=2 normalized_input; "
                "output_min=-30 degC; output_max=80 degC."
                ),
                *_llm_args(),
            ],
        )

    with pytest.raises(SystemExit, match="require --measurement-response"):
        main()


def test_cli_collects_repeatable_specification_answers():
    args = parse_args(
        [
            "--specification-text",
            "manual excerpt",
            "--specification-answer",
            "response_time_s=20 s",
            "--specification-answer",
            "output_max=80 degC",
        ]
    )

    assert args.specification_text == "manual excerpt"
    assert args.specification_answer == [
        "response_time_s=20 s",
        "output_max=80 degC",
    ]


def test_cli_accepts_structured_model_evidence(tmp_path, monkeypatch, capsys):
    _enable_cli_guided_adapter(monkeypatch)
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
            *_llm_args(),
        ],
    )

    main()
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "awaiting_measurements"
    assert payload["controller"] is None


def test_cli_can_submit_structured_model_to_an_awaiting_specification_session(
    tmp_path, monkeypatch, capsys
):
    _enable_cli_guided_adapter(monkeypatch)
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
            "--diagnostic-session-input",
            str(session_path),
            "--model-spec",
            str(model_path),
            *_llm_args(),
        ],
    )

    with pytest.raises(ValueError, match="complete diagnostic session"):
        main()
