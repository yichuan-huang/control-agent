"""Prepare valid and invalid download packets for native MATLAB preflight tests."""

from __future__ import annotations

import copy
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from reference_parity import prepare as prepare_reference

from cfdc.kernel.contracts import fingerprint


def prepare(folder: Path):
    folder.mkdir(parents=True, exist_ok=True)
    u, y = "led_current", "optical_intensity"
    card = {
        "handoff_version": "cfdc-operator-handoff/v1",
        "session_id": "test-session",
        "task_fingerprint": "task",
        "protocol_fingerprint": "protocol",
        "data_kind": "siso_repeated_timeseries",
        "requested_signals": [y],
        "control_inputs": [u],
        "units": {"input": "normalized", "outputs": {y: "normalized"}, "time": "s"},
        "repeats": 1,
        "duration_s": 1.0,
        "sample_period_s": 0.05,
        "input_bounds": [-1.0, 1.0],
        "stop_condition": {"state_stop": 3.0, "output_bounds": None},
        "note": '中文设计条件，"quoted"; keep integer 1 and float 1.0',
    }
    card["handoff_fingerprint"] = fingerprint(card)
    csv = "session_id,protocol_fingerprint,repeat,time_s," + u + "," + y + "\r\n"
    csv += "".join(
        f"test-session,protocol,1,{i * 0.05:.12g},0.3,\r\n" for i in range(21)
    )

    def write(name, members):
        with zipfile.ZipFile(folder / name, "w") as archive:
            for path, value in members.items():
                archive.writestr(
                    path,
                    value
                    if isinstance(value, str)
                    else json.dumps(value, ensure_ascii=False, indent=2),
                )

    members = {"operator_card.json": card, "data_templates/repeat_01.csv": csv}
    write("operator_valid.zip", members)
    for name, field, value in [
        ("operator_stop", "stop_condition", {"state_stop": 4.0}),
        ("operator_timing", "duration_s", 2.0),
        ("operator_bounds", "input_bounds", [-2.0, 2.0]),
    ]:
        altered = copy.deepcopy(members)
        altered["operator_card.json"][field] = value
        write(name + ".zip", altered)
    write(
        "operator_cross_session.zip",
        {
            **members,
            "data_templates/repeat_01.csv": csv.replace(
                "test-session,", "other-session,"
            ),
        },
    )
    write("operator_missing.zip", {"operator_card.json": card})
    changed = csv.split("\r\n")[0] + "\r\n"
    for row in csv.split("\r\n")[1:]:
        if row:
            fields = row.split(",")
            fields[-2] = "0.6"
            changed += ",".join(fields) + "\r\n"
    write(
        "operator_changed_input.zip",
        {**members, "data_templates/repeat_01.csv": changed},
    )
    prepare_reference(folder / "reference")
    fixture = json.loads((folder / "reference" / "fixtures.json").read_text())[0]
    req = fixture["request"]
    req.update(
        request_version="cfdc-execution/v1",
        session_id="test-session",
        task_fingerprint="task",
        freeze_fingerprint="freeze",
        evaluation_split="development",
        trials=[fixture["scenario"]],
    )
    binding = {
        "request_id": "request",
        "session_id": "test-session",
        "task_fingerprint": "task",
        "freeze_fingerprint": "freeze",
        "stage": "development",
        "candidate_id": None,
    }
    manifest = dict(
        **binding,
        format_version="cfdc-external-workflow/v1",
        trials=[
            {"trial_id": fixture["scenario"]["trial_id"], "file": "trial-0001.json"}
        ],
        request_fingerprint=fingerprint({**binding, "execution_request": req}),
    )
    members = {
        "execution-request.json": req,
        "manifest.json": manifest,
        "templates/trial-0001.json": {
            **fixture["scenario"],
            "trajectory": {"time_s": []},
        },
    }
    write("execution_valid.zip", members)
    modifications = {
        "controller": lambda r: r["controller"]["parameters"].update(kp=3.0),
        "timing": lambda r: r.update(sample_time_s=0.04),
        "phases": lambda r: r.update(phases=[{"phase_id": "tampered"}]),
        "disturbance": lambda r: r.update(disturbance={"amplitude": 0.2}),
        "seed": lambda r: r["trials"][0].update(seed=999),
        "split": lambda r: r.update(evaluation_split="fresh_confirmation"),
        "session": lambda r: r.update(session_id="other-session"),
    }
    for name, modify in modifications.items():
        altered = copy.deepcopy(members)
        modify(altered["execution-request.json"])
        write("execution_" + name + ".zip", altered)
    write(
        "execution_missing.zip",
        {k: v for k, v in members.items() if not k.startswith("templates/")},
    )
    print("Prepared packet fixtures", folder)


if __name__ == "__main__":
    prepare(Path(sys.argv[1]))
