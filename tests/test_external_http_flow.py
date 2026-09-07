"""HTTP external workflow using only downloaded artifacts in a subprocess."""

import json
import os
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from test_web_api import finish

from cfdc.web.api import create_app


def action(client, task, action, payload=None, file_ids=None):
    summary = client.get(f"/api/v1/tasks/{task}").json()
    response = client.post(
        f"/api/v1/tasks/{task}/actions",
        json={
            "request_id": str(uuid4()),
            "expected_revision": summary["revision"],
            "action": action,
            "input": {
                "mode": "json",
                "text": json.dumps(payload or {}),
                "payload": payload or {},
                "file_ids": file_ids or [],
            },
        },
    )
    assert response.status_code == 202, response.text
    operation = finish(client, response.json(), timeout=30)
    assert operation["status"] == "completed", json.dumps(operation)
    return client.get(f"/api/v1/tasks/{task}").json()


def simulate(bundle, output):
    subprocess.run(
        [
            sys.executable,
            str(Path(__file__).with_name("external_synthetic.py")),
            str(bundle),
            str(output),
        ],
        check=True,
        cwd=Path(__file__).parents[1],
        env={
            "PATH": os.environ.get("PATH", ""),
            "PYTHONPATH": str(Path(__file__).parents[1]),
        },
    )


def upload(client, task, path):
    response = client.post(
        "/api/v1/uploads",
        data={"session_id": task},
        files={"file": (path.name, path.read_bytes(), "application/octet-stream")},
    )
    assert response.status_code == 200, response.text
    return response.json()["file_id"]


@pytest.mark.parametrize(
    "settling_limit,expected_status",
    [(5.0, "capability_gap"), (6.0, "performance_met")],
)
def test_external_optical_http_from_downloaded_artifacts(
    tmp_path, settling_limit, expected_status
):
    app = create_app(
        session_dir=tmp_path / "sessions",
        runtime_dir=tmp_path / "web",
        frontend_dir=tmp_path / "frontend",
        prepare_rag=False,
    )
    with TestClient(app, base_url="http://127.0.0.1:7860") as client:
        response = client.post(
            "/api/v1/tasks",
            json={
                "request_id": str(uuid4()),
                "task": {
                    "description": "Hold independent optical intensity",
                    "measured_signals": ["intensity"],
                    "control_input": "led_current",
                    "reference": 0.5,
                    "input_min": -1,
                    "input_max": 1,
                    "state_stop": 3,
                    "final_abs_error_max": 0.05,
                    "overshoot_max": 0.1,
                    "settling_time_max_s": settling_limit,
                },
                "confirmed": True,
                "use_rag": False,
            },
        )
        assert response.status_code == 202, response.text
        operation = finish(client, response.json())
        assert operation["status"] == "completed", json.dumps(operation)
        task = operation["session_id"]
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
        action(
            client,
            task,
            "answer",
            {
                key: {
                    "status": "known",
                    "assessment": value,
                    "evidence": "Synthetic apparatus design statement: " + value,
                    "confidence": 1,
                }
                for key, value in assessments.items()
            },
        )
        action(client, task, "advance")
        summary = action(
            client, task, "select_external_source", {"source_kind": "software"}
        )
        bundle_response = client.get(f"/api/v1/tasks/{task}/downloads/operator")
        assert bundle_response.status_code == 200, bundle_response.text
        bundle = tmp_path / "operator.zip"
        bundle.write_bytes(bundle_response.content)
        import zipfile

        with zipfile.ZipFile(bundle) as archive:
            card = json.loads(archive.read("operator_card.json"))
        action(
            client,
            task,
            "record_operator_report",
            {
                "decision": "accepted",
                "prechecks_completed": card["prechecks"],
                "note": "Independent software apparatus; no hardware",
            },
        )
        data = tmp_path / "data"
        simulate(bundle, data)
        summary = action(
            client,
            task,
            "ingest_upload",
            file_ids=[
                upload(client, task, path) for path in sorted(data.glob("*.csv"))
            ],
        )
        assert summary["status"] == "controller_qualified", json.dumps(summary)
        assert summary["workspace"]["action"] == "freeze"
        summary = action(client, task, "freeze")
        assert summary["status"] == "controller_ready", json.dumps(summary)
        summary = action(client, task, "prepare_external_run", {"stage": "development"})
        response = client.get(f"/api/v1/tasks/{task}/downloads/external_run")
        assert response.status_code == 200, response.text
        bundle = tmp_path / "execution.zip"
        bundle.write_bytes(response.content)
        results = tmp_path / "results.zip"
        simulate(bundle, results)
        summary = action(
            client,
            task,
            "submit_external_results",
            file_ids=[upload(client, task, results)],
        )
        assert summary["status"] == "tuning_eligible", summary
        summary = action(client, task, "start_external_tuning")
        stages = []
        for index in range(7):
            if summary["status"] in {"performance_met", "capability_gap"}:
                break
            summary = action(client, task, "prepare_external_run")
            response = client.get(f"/api/v1/tasks/{task}/downloads/external_run")
            assert response.status_code == 200, response.text
            bundle = tmp_path / f"probe-{index}.zip"
            bundle.write_bytes(response.content)
            with zipfile.ZipFile(bundle) as archive:
                manifest = json.loads(archive.read("manifest.json"))
            stages.append(manifest["stage"])
            results = tmp_path / f"probe-result-{index}.zip"
            simulate(bundle, results)
            summary = action(
                client,
                task,
                "submit_external_results",
                file_ids=[upload(client, task, results)],
            )
        assert stages.count("tuning_probe") >= 1
        assert stages[-1] == "fresh_confirmation", json.dumps(summary)
        assert summary["status"] == expected_status, json.dumps(summary)
