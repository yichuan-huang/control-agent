"""Non-expert operator handoff artifacts for a compiled protocol."""

from __future__ import annotations

import csv
import io
import json
import zipfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import numpy as np

from cfdc.kernel.contracts import OPERATOR_HANDOFF_VERSION, fingerprint, utc_now

OPERATOR_DECISIONS = frozenset({"accepted", "needs_clarification", "refused"})


def expected_input_waveforms(
    protocol: Mapping[str, Any],
) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    dt = float(protocol["sample_period_s"])
    count = int(
        protocol.get("expected_sample_count")
        or round(float(protocol["duration_s"]) / dt) + 1
    )
    times = np.arange(count, dtype=float) * dt
    command = np.zeros_like(times)
    cursor = 0.0
    for segment in protocol["segments"]:
        end = cursor + float(segment["duration_s"])
        command[(times >= cursor - 1e-12) & (times < end - 1e-12)] = float(
            segment["input_value"]
        )
        cursor = end
    command[times >= cursor - 1e-12] = 0.0
    input_names = tuple(str(item) for item in protocol.get("control_inputs", ())) or (
        "input",
    )
    commands = {input_names[0]: command}
    for index, name in enumerate(input_names[1:], 1):
        shift = max(1, index * len(command) // (8 * len(input_names)))
        commands[name] = np.roll(command * (-1.0 if index % 2 else 1.0), shift)
    return times, commands


def expected_waveform(protocol: Mapping[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    times, commands = expected_input_waveforms(protocol)
    return times, next(iter(commands.values()))


def build_operator_handoff(
    *,
    session_id: str,
    task: Mapping[str, Any],
    protocol: Mapping[str, Any],
    output_dir: Path,
) -> dict[str, Any]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    times, expected_inputs = expected_input_waveforms(protocol)
    input_names = tuple(expected_inputs)
    card = {
        "handoff_version": OPERATOR_HANDOFF_VERSION,
        "session_id": session_id,
        "created_at": utc_now(),
        "scope": "execute-and-report only",
        "task_fingerprint": task.get("task_fingerprint"),
        "protocol_fingerprint": protocol["protocol_fingerprint"],
        "operation": protocol["operation"],
        "data_kind": protocol["data_kind"],
        "repeats": protocol["repeats"],
        "sample_period_s": protocol["sample_period_s"],
        "duration_s": protocol["duration_s"],
        "input_bounds": protocol["input_bounds"],
        "stop_condition": protocol["stop_condition"],
        "requested_signals": protocol["requested_signals"],
        "control_inputs": list(input_names),
        "units": protocol["units"],
        "prechecks": [
            "channels",
            "units",
            "logger",
            "stop condition",
            "initial condition",
        ],
        "claims_forbidden": [
            "controller approval",
            "data repair",
            "physical safety certification",
        ],
    }
    card["handoff_fingerprint"] = fingerprint(card)
    card_path = output_dir / "operator_card.json"
    card_path.write_text(
        json.dumps(card, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    checklist = {
        "session_id": session_id,
        "protocol_fingerprint": protocol["protocol_fingerprint"],
        "required_prechecks": card["prechecks"],
        "operator_decisions": ["accepted", "needs_clarification", "refused"],
    }
    checklist_path = output_dir / "precheck_checklist.json"
    checklist_path.write_text(
        json.dumps(checklist, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    template_paths: list[str] = []
    memory_files: list[tuple[str, bytes]] = []
    for index in range(int(protocol["repeats"])):
        stream = io.StringIO(newline="")
        writer = csv.writer(stream)
        writer.writerow(
            [
                "session_id",
                "protocol_fingerprint",
                "repeat",
                "time_s",
                *input_names,
                *protocol["requested_signals"],
            ]
        )
        for sample_index, time_value in enumerate(times):
            writer.writerow(
                [
                    session_id,
                    protocol["protocol_fingerprint"],
                    index + 1,
                    f"{time_value:.12g}",
                    *(
                        f"{expected_inputs[name][sample_index]:.12g}"
                        for name in input_names
                    ),
                    *("" for _ in protocol["requested_signals"]),
                ]
            )
        payload = stream.getvalue().encode("utf-8-sig")
        name = f"repeat_{index + 1:02d}.csv"
        path = output_dir / name
        path.write_bytes(payload)
        template_paths.append(str(path))
        memory_files.append((name, payload))
    bundle = output_dir / "operator_bundle.zip"
    with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "operator_card.json", json.dumps(card, ensure_ascii=False, indent=2) + "\n"
        )
        archive.writestr(
            "upload_schema.json",
            json.dumps(
                {
                    "required_columns": [
                        "time_s",
                        *input_names,
                        *protocol["requested_signals"],
                    ],
                    "json_modes": ["repeats", "records", "mimo_inputs"],
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
        )
        archive.writestr(
            "precheck_checklist.json",
            json.dumps(checklist, ensure_ascii=False, indent=2) + "\n",
        )
        for name, payload in memory_files:
            archive.writestr(f"data_templates/{name}", payload)
    return {
        "handoff": card,
        "operator_card_path": str(card_path),
        "precheck_checklist_path": str(checklist_path),
        "template_paths": template_paths,
        "bundle_path": str(bundle),
    }


def validate_operator_report(
    report: Mapping[str, Any], handoff: Mapping[str, Any]
) -> dict[str, Any]:
    decision = str(report.get("decision") or "").strip()
    if decision not in OPERATOR_DECISIONS:
        raise ValueError("operator_decision_invalid")
    prechecks = tuple(
        str(item).strip()
        for item in report.get("prechecks_completed", ())
        if str(item).strip()
    )
    if decision == "accepted" and not set(handoff.get("prechecks", ())) <= set(
        prechecks
    ):
        raise ValueError("operator_prechecks_incomplete")
    value = {
        "decision": decision,
        "prechecks_completed": list(prechecks),
        "note": str(report.get("note") or "").strip(),
        "handoff_fingerprint": handoff.get("handoff_fingerprint"),
        "recorded_at": utc_now(),
    }
    value["report_fingerprint"] = fingerprint(value)
    return value


__all__ = [
    "OPERATOR_DECISIONS",
    "build_operator_handoff",
    "expected_input_waveforms",
    "expected_waveform",
    "validate_operator_report",
]
