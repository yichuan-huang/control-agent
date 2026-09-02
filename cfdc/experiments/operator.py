"""Non-expert operator handoff artifacts for a compiled protocol."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import zipfile
from collections.abc import Mapping, Sequence
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


def build_training_exercise_bundle(
    *,
    session_id: str,
    task: Mapping[str, Any],
    protocol: Mapping[str, Any],
    traces: Sequence[Any],
    provider_id: str,
    provider_version: str,
    registered_case_binding_fingerprint: str,
    output_dir: Path,
) -> dict[str, Any]:
    """Package provider-generated traces as a clearly non-physical exercise.

    The ZIP contains only protocol-bound public arrays.  It is deliberately a
    separate artifact from the operator handoff: downloading it does not add
    evidence, and re-uploading it still goes through the normal ingestion
    gates in :mod:`cfdc.evidence.ingestion`.
    """

    if not traces:
        raise ValueError("training_exercise_traces_required")
    if len(traces) != int(protocol["repeats"]):
        raise ValueError("training_exercise_repeat_count_mismatch")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    input_names = tuple(str(item) for item in protocol.get("control_inputs", ())) or (
        "input",
    )
    output_names = tuple(str(item) for item in protocol.get("requested_signals", ()))
    if not output_names:
        raise ValueError("training_exercise_outputs_required")
    files_in_manifest: list[dict[str, Any]] = []
    csv_files: list[Path] = []
    for index, trace in enumerate(traces, 1):
        time_values = tuple(float(item) for item in trace.time_s)
        signals = {
            str(name): tuple(float(item) for item in values)
            for name, values in trace.signals.items()
        }
        if any(
            name not in signals and not (name == input_names[0] and "input" in signals)
            for name in (*input_names, *output_names)
        ):
            raise ValueError("training_exercise_trace_channels_mismatch")
        if input_names[0] not in signals and "input" in signals:
            signals[input_names[0]] = signals["input"]
        stream = io.StringIO(newline="")
        writer = csv.writer(stream)
        writer.writerow(
            [
                "session_id",
                "protocol_fingerprint",
                "repeat",
                "time_s",
                *input_names,
                *output_names,
            ]
        )
        for sample_index, time_value in enumerate(time_values):
            writer.writerow(
                [
                    session_id,
                    protocol["protocol_fingerprint"],
                    index,
                    f"{time_value:.12g}",
                    *(f"{signals[name][sample_index]:.12g}" for name in input_names),
                    *(f"{signals[name][sample_index]:.12g}" for name in output_names),
                ]
            )
        payload = stream.getvalue().encode("utf-8-sig")
        relative = Path("data") / f"repeat_{index:02d}.csv"
        path = output_dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
        csv_files.append(path)
        files_in_manifest.append(
            {
                "path": relative.as_posix(),
                "repeat": index,
                "trace_fingerprint": str(
                    getattr(trace, "fingerprint", "")
                    or fingerprint(trace.to_dict(include_fingerprint=False))
                ),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        )
    manifest = {
        "bundle_version": "cfdc-training-exercise/v1",
        "session_id": session_id,
        "task_fingerprint": task.get("task_fingerprint"),
        "protocol_fingerprint": protocol["protocol_fingerprint"],
        "registered_case_binding_fingerprint": registered_case_binding_fingerprint,
        "provider_id": str(provider_id),
        "provider_version": str(provider_version),
        "evidence_mode": "exercise_bundle",
        "source_boundary": "software_provider_exercise_only; not physical evidence",
        "repeats": len(traces),
        "files": files_in_manifest,
        "claims_forbidden": [
            "physical measurement",
            "hardware safety certification",
            "controller approval",
        ],
    }
    instructions = (
        "# 教学练习包\n\n"
        "这是绑定到当前软件协议的练习数据，不是物理测量，也不授予硬件控制权限。\n"
        "请保留 manifest.json 和 data/ 下的全部重复文件；重新上传 ZIP 后，系统仍会执行会话、协议、时间轴、输入波形、停止边界和重复质量校验。\n"
        "任何修改都会导致绑定校验失败，不会自动修复，也不会消耗有效实验数。\n"
    )
    manifest["instructions_sha256"] = hashlib.sha256(
        instructions.encode("utf-8")
    ).hexdigest()
    # The manifest fingerprint covers the instruction digest as well as the
    # data rows, so a changed teaching note cannot silently become a different
    # exercise while retaining the same authority binding.
    manifest.pop("manifest_fingerprint", None)
    manifest["manifest_fingerprint"] = fingerprint(manifest)
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    instructions_path = output_dir / "instructions.md"
    instructions_path.write_text(instructions, encoding="utf-8")
    bundle = output_dir / "training_exercise_bundle.zip"
    with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "manifest.json",
            json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        )
        archive.writestr("instructions.md", instructions)
        for path in csv_files:
            archive.write(path, path.relative_to(output_dir).as_posix())
    return {
        "manifest": manifest,
        "manifest_path": str(manifest_path),
        "instructions_path": str(instructions_path),
        "data_paths": [str(path) for path in csv_files],
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
    "build_training_exercise_bundle",
    "expected_input_waveforms",
    "expected_waveform",
    "validate_operator_report",
]
