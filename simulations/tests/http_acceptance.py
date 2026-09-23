"""Stage real HTTP packets for manual/native MATLAB execution (no model calls).

Run `init DIRECTORY`, MATLAB run_http_jobs(DIRECTORY), then `advance DIRECTORY`
and repeat until the printed terminal results. No production runner imports this.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import zipfile
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from fastapi.testclient import TestClient

from cfdc.web.api import create_app

EXPECTED_STATUSES = {
    "01_optical_hold": "capability_gap",
    "02_vacuum_hold": "performance_met",
    "03_ink_viscosity_hold": "performance_met",
    "04_optical_transition": "capability_gap",
    "05_ink_disturbance_recovery": "performance_met",
}


def selected_cases(cases):
    selected = tuple(cases) if cases is not None else tuple(EXPECTED_STATUSES)
    if not selected or len(set(selected)) != len(selected):
        raise ValueError("Select one or more distinct simulation cases")
    unknown = set(selected) - EXPECTED_STATUSES.keys()
    if unknown:
        raise ValueError(f"Unknown simulation cases: {sorted(unknown)}")
    return selected


def finish(client, response):
    assert response.status_code == 202, response.text
    operation = response.json()
    deadline = time.monotonic() + 60
    while operation["status"] in {"queued", "running"}:
        assert time.monotonic() < deadline, operation
        time.sleep(0.05)
        operation = client.get(f"/api/v1/operations/{operation['operation_id']}").json()
    assert operation["status"] == "completed", operation
    return operation


def action(client, sid, name, payload=None, files=None):
    revision = client.get(f"/api/v1/tasks/{sid}").json()["revision"]
    finish(
        client,
        client.post(
            f"/api/v1/tasks/{sid}/actions",
            json={
                "request_id": str(uuid4()),
                "expected_revision": revision,
                "action": name,
                "input": {
                    "mode": "json",
                    "text": json.dumps(payload or {}),
                    "payload": payload or {},
                    "file_ids": files or [],
                },
            },
        ),
    )
    return client.get(f"/api/v1/tasks/{sid}").json()


def stage(client, folder, row, kind, number):
    sid = row["session_id"]
    response = client.get(
        f"/api/v1/tasks/{sid}/downloads/{'operator' if kind == 'identification' else 'external_run'}"
    )
    assert response.status_code == 200, response.text
    packet = folder / f"{row['case_id']}-{number}-{kind}.zip"
    if packet.exists():
        assert packet.read_bytes() == response.content, "Existing test packet differs"
    else:
        packet.write_bytes(response.content)
    if kind == "identification":
        with zipfile.ZipFile(packet) as archive:
            card = json.loads(archive.read("operator_card.json"))
        action(
            client,
            sid,
            "record_operator_report",
            {
                "decision": "accepted",
                "prechecks_completed": card["prechecks"],
                "note": "Acceptance fixture: fixed normalized SISO software apparatus, zero initial state and bounded execution.",
            },
        )
    return dict(
        **row,
        package_path=str(packet),
        kind=kind,
        response_path=str(folder / (packet.stem + "-response.json")),
    )


def verify(folder, *, cases=None):
    """Verify unchanged benchmark outcomes, accepted packets and fresh seeds."""
    if cases is None:
        state = json.loads((folder / "state.json").read_text())
        cases = [row["case_id"] for row in state["cases"]]
    for case_id in selected_cases(cases):
        status = EXPECTED_STATUSES[case_id]
        report = json.loads((folder / (case_id + "-report.json")).read_text())
        assert report["status"] == status, (case_id, report["status"])
        workflow = report["external_workflow"]
        assert workflow["receipts"] and all(r["accepted"] for r in workflow["receipts"])
        assert report["evaluation_replays"] and all(
            r["matches_previous"] for r in report["evaluation_replays"]
        )
        if status == "performance_met":
            assert report["confirmation"]["status"] == status
            requests = [r["execution_request"] for r in workflow["requests"]]
            fresh = [
                r for r in requests if r["evaluation_split"] == "fresh_confirmation"
            ]
            assert len(fresh) == 1 and len(fresh[0]["trials"]) == 20
            prior_seeds = {
                t["seed"]
                for r in requests
                if r["evaluation_split"] != "fresh_confirmation"
                for t in r["trials"]
            }
            assert prior_seeds.isdisjoint(t["seed"] for t in fresh[0]["trials"])
        print("PASS", case_id, status)


def run(mode, folder, *, cases=None, case_root=None):
    folder = folder.resolve()
    folder.mkdir(parents=True, exist_ok=True)
    app = create_app(
        session_dir=folder / "sessions",
        runtime_dir=folder / "web",
        frontend_dir=folder / "frontend",
        prepare_rag=False,
    )
    jobs = []
    with TestClient(app, base_url="http://127.0.0.1:7860") as client:
        if mode == "init":
            assert not (folder / "state.json").exists()
            selected = selected_cases(cases)
            source_root = (case_root or ROOT / "simulations").resolve()
            rows = []
            for case_id in selected:
                config_path = source_root / case_id / "case_config.json"
                config = json.loads(config_path.read_text())
                assert config["case_id"] == case_id
                sid = finish(
                    client,
                    client.post(
                        "/api/v1/tasks",
                        json={
                            "request_id": str(uuid4()),
                            "task": config["task"],
                            "confirmed": True,
                            "use_rag": False,
                        },
                    ),
                )["session_id"]
                assessments = {
                    "open_loop_stability": "stable",
                    "nonminimum_phase": "minimum_phase",
                    "significant_delay": "significant"
                    if config["plant"]["kind"] == "vacuum"
                    else "not_significant",
                    "relative_degree": "low",
                    "sensing_actuation_adequacy": "adequate",
                    "nonlinearity_strength": "weak",
                    "coupling_underactuation": "siso",
                    "uncertainty_variation": "small",
                }
                action(
                    client,
                    sid,
                    "answer",
                    {
                        key: {
                            "status": "known",
                            "assessment": value,
                            "evidence": "Known fixed model design condition: " + value,
                            "confidence": 1,
                        }
                        for key, value in assessments.items()
                    },
                )
                action(client, sid, "advance")
                action(
                    client, sid, "select_external_source", {"source_kind": "software"}
                )
                row = {
                    "case_id": config["case_id"],
                    "case_dir": str(config_path.parent),
                    "session_id": sid,
                }
                rows.append(row)
                jobs.append(stage(client, folder, row, "identification", 0))
            state = {"round": 0, "cases": rows, "terminal": {}}
            if case_root is not None:
                state["exchange_root"] = str(folder.parent)
        else:
            state = json.loads((folder / "state.json").read_text())
            if cases is not None:
                assert set(selected_cases(cases)) == {
                    row["case_id"] for row in state["cases"]
                }
            old_jobs = json.loads((folder / "jobs.json").read_text())
            for job in old_jobs:
                result = json.loads(Path(job["response_path"]).read_text())
                paths = (
                    result["files"]
                    if job["kind"] == "identification"
                    else [result["result_zip"]]
                )
                if isinstance(paths, str):
                    paths = [paths]
                already_accepted = False
                if job["kind"] == "evaluation":
                    with zipfile.ZipFile(job["package_path"]) as archive:
                        manifest = json.loads(archive.read("manifest.json"))
                    report = client.get(
                        f"/api/v1/tasks/{job['session_id']}/downloads/report"
                    ).json()
                    already_accepted = any(
                        row.get("accepted")
                        and row.get("request_id") == manifest["request_id"]
                        for row in report.get("external_workflow", {}).get(
                            "receipts", []
                        )
                    )
                if already_accepted:
                    summary = client.get(f"/api/v1/tasks/{job['session_id']}").json()
                else:
                    ids = []
                    for path in map(Path, paths):
                        if not path.is_absolute():
                            path = Path(state["exchange_root"]) / path
                        upload = client.post(
                            "/api/v1/uploads",
                            data={"session_id": job["session_id"]},
                            files={
                                "file": (
                                    path.name,
                                    path.read_bytes(),
                                    "application/octet-stream",
                                )
                            },
                        )
                        assert upload.status_code == 200, upload.text
                        ids.append(upload.json()["file_id"])
                    summary = action(
                        client,
                        job["session_id"],
                        "ingest_upload"
                        if job["kind"] == "identification"
                        else "submit_external_results",
                        files=ids,
                    )
                if summary["workspace"]["action"] == "freeze":
                    summary = action(client, job["session_id"], "freeze")
                if summary["workspace"]["action"] == "start_external_tuning":
                    summary = action(client, job["session_id"], "start_external_tuning")
                if summary["status"] in {
                    "performance_met",
                    "capability_gap",
                    "experiment_failed",
                    "performance_not_met",
                }:
                    state["terminal"][job["case_id"]] = summary
                    report = client.get(
                        f"/api/v1/tasks/{job['session_id']}/downloads/report"
                    )
                    (folder / (job["case_id"] + "-report.json")).write_bytes(
                        report.content
                    )
                    print(job["case_id"], summary["status"])
                else:
                    print(
                        job["case_id"],
                        summary["status"],
                        summary["workspace"]["action"],
                    )
                    action(client, job["session_id"], "prepare_external_run")
                    row = {
                        key: job[key] for key in ("case_id", "case_dir", "session_id")
                    }
                    jobs.append(
                        stage(client, folder, row, "evaluation", state["round"] + 1)
                    )
            state["round"] += 1
        (folder / "state.json").write_text(
            json.dumps(state, ensure_ascii=False, indent=2)
        )
        (folder / "jobs.json").write_text(json.dumps(jobs, indent=2))
        if exchange_root := state.get("exchange_root"):
            root = Path(exchange_root)
            portable = []
            for job in jobs:
                item = dict(job)
                for key in ("case_dir", "package_path", "response_path"):
                    path = Path(job[key]).resolve()
                    if not path.is_relative_to(root):
                        raise ValueError(f"Exchange path escaped its root: {path}")
                    item[key] = os.path.relpath(path, root)
                portable.append(item)
            (folder / "jobs-exchange.json").write_text(json.dumps(portable, indent=2))
        print(
            f"Round {state['round']}: {len(jobs)} MATLAB jobs; {len(state['terminal'])}/{len(state['cases'])} terminal."
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["init", "advance", "verify"])
    parser.add_argument("directory", type=Path)
    parser.add_argument("--cases", nargs="+", metavar="CASE_ID")
    parser.add_argument("--case-root", type=Path)
    args = parser.parse_args()
    if args.mode == "verify":
        verify(args.directory, cases=args.cases)
    else:
        run(args.mode, args.directory, cases=args.cases, case_root=args.case_root)
