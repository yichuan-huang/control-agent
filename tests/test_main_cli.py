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
            "guidance": [
                {
                    **item.model_dump(mode="json"),
                    "response": (
                        _VALID_FIELD_FACTS[item.diagnostic_field_id]
                        if _VALID_FIELD_FACTS[item.diagnostic_field_id]
                        in description.text
                        else "unknown"
                    ),
                }
                for item in guidance
            ],
            "observed_outputs": [
                {"name": name, "source_excerpt": name} for name in output
            ],
            "actuators": [{"name": name, "source_excerpt": name} for name in actuators],
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


def _complete_description(text: str) -> str:
    return text + "\n" + "\n".join(_VALID_FIELD_FACTS.values())


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

    with pytest.raises(
        SystemExit, match="v3 diagnostic session payloads are not supported"
    ):
        load_diagnostic_session(source)


@pytest.mark.parametrize("payload", [[], "session", None, 7])
def test_cli_rejects_non_object_diagnostic_session_json(payload, tmp_path):
    source = tmp_path / "not-an-object.json"
    source.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(
        SystemExit, match="invalid --diagnostic-session-input.*JSON object"
    ):
        load_diagnostic_session(source)


@pytest.mark.parametrize("raw_entry", [None, 7, {}, []])
def test_cli_rejects_non_string_measurement_response_history(raw_entry, tmp_path):
    session = start_diagnostic_session(SystemDescription(text="I have a machine."))
    payload = session.model_dump(mode="json")
    payload["measurement_history"] = [
        {
            "status": "need_more",
            "facts": [],
            "gaps": [item["diagnostic_field_id"] for item in payload["checklist"]],
            "conflicts": [],
            "conflict_request_ids": [],
            "rationale": "No record was available.",
        }
    ]
    payload["measurement_response_history"] = [raw_entry]
    payload["measurement_assessment"] = payload["measurement_history"][0]
    payload["measurement_round_count"] = 1
    payload["status"] = "measurement_needs_more"
    source = tmp_path / "invalid-raw-history.json"
    source.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(
        SystemExit,
        match="invalid --diagnostic-session-input.*response history entries must be strings",
    ):
        load_diagnostic_session(source)


def test_cli_v4_session_round_trip_accepts_measurement_response_file(
    tmp_path, monkeypatch, capsys
):
    _enable_cli_guided_adapter(monkeypatch)
    initial_path = tmp_path / "initial-v4.json"
    advanced_path = tmp_path / "advanced-v4.json"
    response_path = tmp_path / "records.txt"
    response_path.write_text(
        (
            "input_change=1 V; steady_output_change=10 degC; response_time_s=5 s; "
            "input_min=-2 V; input_max=2 V; output_min=-30 degC; output_max=80 degC;"
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "main.py",
            "--description",
            _complete_description(
                "A first order temperature process settles after a heater change."
            ),
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
    assert initial_payload["status"] == "awaiting_profile_measurements"
    assert initial_payload["diagnostic_session"]["revision"] == 1
    assert initial_payload["diagnostic_session"]["measurement_round_count"] == 0
    assert initial_payload["classification"] is not None
    assert initial_payload["semantic_selection"] is not None

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
            "--confirm-simulation-bounds",
            *_llm_args(),
        ],
    )
    main()
    advanced_payload = json.loads(capsys.readouterr().out)
    restored = DiagnosticSessionState.model_validate_json(
        advanced_path.read_text(encoding="utf-8")
    )
    assert advanced_payload["status"] == "candidate_unvalidated"
    assert restored.status == "specification_model_ready"
    assert restored.revision == 3
    assert restored.classification is not None
    assert restored.measurement_round_count == 0
    assert restored.profile_measurement_round_count == 1


def test_documented_legacy_cli_three_step_flow_is_offline_and_auditable(
    tmp_path, monkeypatch, capsys
):
    _enable_cli_guided_adapter(monkeypatch)
    monkeypatch.setenv("CFDC_LLM_BASE_URL", "https://your-provider.example/v1")
    monkeypatch.setenv("CFDC_LLM_MODEL", "your-model")
    monkeypatch.setenv("CFDC_LLM_API_KEY", "test-secret")
    session_paths = [tmp_path / f"legacy-0{index}.json" for index in range(1, 4)]
    compatibility_args = [
        "--workflow-version",
        "legacy",
        "--use-llm",
        "--agent-mode",
        "single",
        "--no-rag",
    ]
    commands = [
        [
            "main.py",
            *compatibility_args,
            "--description",
            "A heater changes measured temperature.",
            "--diagnostic-session-output",
            str(session_paths[0]),
        ],
        [
            "main.py",
            *compatibility_args,
            "--diagnostic-session-input",
            str(session_paths[0]),
            "--diagnostic-description",
            _complete_description(
                "The observed output is temperature and the actuator is heater."
            ),
            "--diagnostic-session-output",
            str(session_paths[1]),
        ],
        [
            "main.py",
            *compatibility_args,
            "--diagnostic-session-input",
            str(session_paths[1]),
            "--measurement-response",
            (
                "input_change=1 V; steady_output_change=10 degC; "
                "response_time_s=5 s; input_min=-2 V; input_max=2 V; "
                "output_min=-30 degC; output_max=80 degC; all ranges are "
                "software simulation run and stop bounds."
            ),
            "--confirm-simulation-bounds",
            "--diagnostic-session-output",
            str(session_paths[2]),
        ],
    ]

    payloads = []
    for command in commands:
        monkeypatch.setattr(sys, "argv", command)
        main()
        payloads.append(json.loads(capsys.readouterr().out))

    restored = [
        DiagnosticSessionState.model_validate_json(path.read_text(encoding="utf-8"))
        for path in session_paths
    ]
    assert [payload["status"] for payload in payloads] == [
        "need_more_information",
        "awaiting_profile_measurements",
        "candidate_unvalidated",
    ]
    assert len({session.session_id for session in restored}) == 1
    assert [session.revision for session in restored] == [0, 2, 4]
    assert [session.status for session in restored] == [
        "collecting_description",
        "awaiting_profile_measurements",
        "specification_model_ready",
    ]


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
            "--workflow-version",
            "kernel",
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

    assert payload["status"] == "performance_met"
    assert payload["feature_artifact"]["feature_version"] == "cfdc-features/v1"
    assert payload["controller_qualification"]["status"] == "offline_qualified"
    assert payload["provider_bindings"]["identification"]["provider_id"] != payload[
        "provider_bindings"
    ]["evaluation"]["provider_id"]
    bundle = Path(payload["result_bundle_path"])
    assert bundle.parent == result_dir
    assert bundle.is_file()


def test_kernel_cli_v3_import_creates_new_session_without_modifying_source(
    tmp_path, monkeypatch, capsys
):
    source = tmp_path / "v3"
    source.mkdir()
    task = source / "task.json"
    task.write_text(
        json.dumps(
            {
                "task": {
                    "description": "Hold a public measured output.",
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
    original = task.read_bytes()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "main.py",
            "--workflow-version",
            "kernel",
            "--kernel-session-dir",
            str(tmp_path / "sessions"),
            "--kernel-import-v3",
            str(source),
            "--no-rag",
        ],
    )

    main()
    payload = json.loads(capsys.readouterr().out)

    assert payload["session_id"].startswith("cfdc-import-")
    assert payload["import_report"]["source_modified"] is False
    assert payload["pending_actions"][0]["action"] == "confirm_task"
    assert task.read_bytes() == original


def test_documented_deepseek_model_is_v4_pro():
    for readme in (Path("README.md"), Path("README_CN.md")):
        content = readme.read_text(encoding="utf-8")
        assert "deepseek" + "-chat" not in content
        assert '--llm-model "deepseek-v4-pro"' in content


def test_cli_incomplete_description_returns_checklist_without_profile(
    monkeypatch, capsys
):
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
    assert payload["status"] == "need_more_information"
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

    assert payload["status"] == "need_more_information"
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
