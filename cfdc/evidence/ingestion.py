"""Protocol-bound CSV/JSON ingestion and non-expert quality gates."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np

from cfdc.experiments.operator import expected_input_waveforms
from cfdc.kernel.contracts import UPLOAD_AUDIT_VERSION, fingerprint, utc_now
from cfdc.kernel.providers import PublicTrace

GATE_DEFINITIONS = {
    "operator_authorization": ("操作角色权限", "先阅读操作卡并完成全部预检查。"),
    "file_format": (
        "文件与列格式",
        "重新导出包含 time_s、input 和全部观测输出的 CSV/JSON。",
    ),
    "session_binding": ("会话与协议绑定", "只上传当前会话和当前协议采集的数据。"),
    "repeat_count": ("重复次数", "按操作卡完成全部独立重复。"),
    "timebase": ("时间轴与采样", "从 0 秒开始，保持严格递增并覆盖完整时长。"),
    "input_waveform": ("输入波形符合协议", "上传实际输入日志并按当前协议重新执行。"),
    "safety_limits": ("安全停止与幅值边界", "触发停止条件后如实停止和报告，不得裁剪。"),
    "signal_quality": ("重复一致性与信噪比", "检查传感器、同步和重复条件后重测。"),
}


class UploadGateError(ValueError):
    def __init__(self, gate_id: str, message: str) -> None:
        super().__init__(message)
        self.gate_id = gate_id


def _gates() -> list[dict[str, Any]]:
    return [
        {
            "id": key,
            "label": label,
            "status": "not_reached",
            "details": "",
            "redo": redo,
        }
        for key, (label, redo) in GATE_DEFINITIONS.items()
    ]


def _set(
    gates: list[dict[str, Any]], gate_id: str, status: str, details: str = ""
) -> None:
    next(item for item in gates if item["id"] == gate_id).update(
        status=status, details=details
    )


def _receipt(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    return {
        "name": path.name,
        "size_bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def _finite_vector(values: Sequence[Any], label: str) -> np.ndarray:
    try:
        result = np.asarray([float(item) for item in values], dtype=float)
    except (TypeError, ValueError) as exc:
        raise UploadGateError(
            "file_format", f"{label} contains a non-numeric value"
        ) from exc
    if result.ndim != 1 or not result.size or not np.all(np.isfinite(result)):
        raise UploadGateError("file_format", f"{label} must be a finite vector")
    return result


def _column(
    row: Mapping[str, Any], aliases: Sequence[str], *, required: bool = True
) -> str | None:
    lookup = {str(key).strip().casefold(): str(key) for key in row}
    for alias in aliases:
        if alias.casefold() in lookup:
            return lookup[alias.casefold()]
    if required:
        raise UploadGateError("file_format", f"missing column: {aliases[0]}")
    return None


def _csv_records(
    path: Path,
    output_names: Sequence[str],
    input_names: Sequence[str],
) -> list[dict[str, Any]]:
    try:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            rows = list(csv.DictReader(handle))
    except (OSError, UnicodeError, csv.Error) as exc:
        raise UploadGateError("file_format", f"cannot read {path.name}") from exc
    if not rows:
        raise UploadGateError("file_format", f"{path.name} has no data rows")
    first = rows[0]
    time_name = _column(first, ("time_s", "time", "timestamp"))
    input_columns: dict[str, str] = {}
    for index, input_name in enumerate(input_names):
        aliases = (
            (input_name, "input", "control_input", "command", "u", "u1")
            if index == 0
            else (input_name, f"input_{index + 1}", f"u{index + 1}")
        )
        input_columns[input_name] = _column(first, aliases)
    repeat_name = _column(first, ("repeat", "trial", "repeat_id"), required=False)
    session_name = _column(first, ("session_id",), required=False)
    protocol_name = _column(first, ("protocol_fingerprint",), required=False)
    output_columns: dict[str, str] = {}
    for index, output in enumerate(output_names):
        output_columns[output] = _column(
            first,
            (
                output,
                "output" if index == 0 else f"output_{index + 1}",
                f"y{index + 1}",
            ),
        )
    groups: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        key = str(row.get(repeat_name, "1") if repeat_name else "1")
        groups.setdefault(key, []).append(row)
    records: list[dict[str, Any]] = []
    for key, group in groups.items():
        records.append(
            {
                "repeat": key,
                "time_s": _finite_vector([row[time_name] for row in group], "time_s"),
                "inputs": {
                    name: _finite_vector([row[column] for row in group], name)
                    for name, column in input_columns.items()
                },
                "outputs": {
                    name: _finite_vector([row[column] for row in group], name)
                    for name, column in output_columns.items()
                },
                "declared_session_id": str(group[0].get(session_name) or "").strip()
                if session_name
                else None,
                "declared_protocol_fingerprint": str(
                    group[0].get(protocol_name) or ""
                ).strip()
                if protocol_name
                else None,
            }
        )
    return records


def _json_records(
    path: Path,
    output_names: Sequence[str],
    input_names: Sequence[str],
) -> list[dict[str, Any]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise UploadGateError("file_format", f"cannot read {path.name}") from exc
    if not isinstance(value, Mapping):
        raise UploadGateError("file_format", "JSON upload must contain an object")
    common = {
        "declared_session_id": str(value.get("session_id") or "").strip() or None,
        "declared_protocol_fingerprint": str(
            value.get("protocol_fingerprint") or ""
        ).strip()
        or None,
    }
    repeats = value.get("repeats")
    if isinstance(repeats, list):
        sources = repeats
    elif isinstance(value.get("records"), list):
        groups: dict[str, list[Mapping[str, Any]]] = {}
        for row in value["records"]:
            if not isinstance(row, Mapping):
                raise UploadGateError(
                    "file_format", "JSON records must contain objects"
                )
            groups.setdefault(str(row.get("repeat", 1)), []).append(row)
        sources = [
            {
                "repeat": key,
                "time_s": [row.get("time_s") for row in rows],
                "inputs": {
                    name: [
                        (
                            row.get("inputs", {}).get(name)
                            if isinstance(row.get("inputs"), Mapping)
                            else row.get(name, row.get("input") if index == 0 else None)
                        )
                        for row in rows
                    ]
                    for index, name in enumerate(input_names)
                },
                **{
                    name: [
                        row.get(name, row.get("output") if index == 0 else None)
                        for row in rows
                    ]
                    for index, name in enumerate(output_names)
                },
            }
            for key, rows in groups.items()
        ]
    elif isinstance(value.get("repeated_outputs"), list):
        sources = [
            {
                "repeat": index + 1,
                "time_s": value.get("time_s"),
                "inputs": value.get("inputs", {input_names[0]: value.get("input")}),
                output_names[0]: output,
            }
            for index, output in enumerate(value["repeated_outputs"])
        ]
    else:
        sources = [value]
    records = []
    for index, source in enumerate(sources):
        if not isinstance(source, Mapping):
            raise UploadGateError("file_format", "JSON repeats must contain objects")
        outputs = {}
        for output_index, name in enumerate(output_names):
            raw = source.get(name)
            if raw is None and output_index == 0:
                raw = source.get("output")
            if raw is None:
                raise UploadGateError("file_format", f"missing output vector: {name}")
            outputs[name] = _finite_vector(raw, name)
        raw_inputs = source.get("inputs")
        inputs: dict[str, np.ndarray] = {}
        for input_index, name in enumerate(input_names):
            raw_input = (
                raw_inputs.get(name) if isinstance(raw_inputs, Mapping) else None
            )
            if raw_input is None:
                raw_input = source.get(name)
            if raw_input is None and input_index == 0:
                raw_input = source.get("input")
            if raw_input is None:
                raise UploadGateError("file_format", f"missing input vector: {name}")
            inputs[name] = _finite_vector(raw_input, name)
        records.append(
            {
                "repeat": source.get("repeat", index + 1),
                "time_s": _finite_vector(source.get("time_s", ()), "time_s"),
                "inputs": inputs,
                "outputs": outputs,
                **common,
            }
        )
    return records


def _read(
    paths: Sequence[Path],
    output_names: Sequence[str],
    input_names: Sequence[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records: list[dict[str, Any]] = []
    receipts: list[dict[str, Any]] = []
    for path_value in paths:
        path = Path(path_value)
        if not path.is_file():
            raise UploadGateError("file_format", f"upload file is missing: {path.name}")
        receipts.append(_receipt(path))
        if path.suffix.casefold() == ".csv":
            records.extend(_csv_records(path, output_names, input_names))
        elif path.suffix.casefold() == ".json":
            records.extend(_json_records(path, output_names, input_names))
        else:
            raise UploadGateError(
                "file_format", f"unsupported upload type: {path.suffix}"
            )
    return records, receipts


def inspect_upload(
    paths: Sequence[Path],
    *,
    session_id: str,
    protocol: Mapping[str, Any],
    operator_report: Mapping[str, Any] | None,
    stopped_on_limit: bool = False,
) -> dict[str, Any]:
    gates = _gates()
    receipts: list[dict[str, Any]] = []
    metrics: dict[str, Any] = {}
    try:
        if not operator_report or operator_report.get("decision") != "accepted":
            raise UploadGateError(
                "operator_authorization",
                "operator acceptance is required before upload",
            )
        _set(gates, "operator_authorization", "passed")
        output_names = tuple(
            str(item) for item in protocol.get("requested_signals", ())
        )
        input_names = tuple(
            str(item) for item in protocol.get("control_inputs", ())
        ) or ("input",)
        records, receipts = _read(paths, output_names, input_names)
        _set(gates, "file_format", "passed", f"parsed {len(records)} repeat record(s)")
        for record in records:
            declared_session = record.get("declared_session_id")
            declared_protocol = record.get("declared_protocol_fingerprint")
            if declared_session and declared_session != session_id:
                raise UploadGateError(
                    "session_binding", "uploaded data declares a different session"
                )
            if (
                declared_protocol
                and declared_protocol != protocol["protocol_fingerprint"]
            ):
                raise UploadGateError(
                    "session_binding", "uploaded data declares a different protocol"
                )
        _set(gates, "session_binding", "passed")
        if len(records) != int(protocol["repeats"]):
            raise UploadGateError(
                "repeat_count",
                f"expected {protocol['repeats']} repeats, received {len(records)}",
            )
        _set(gates, "repeat_count", "passed")
        expected_t, expected_inputs = expected_input_waveforms(protocol)
        time_errors: list[float] = []
        input_errors: list[float] = []
        output_stacks: dict[str, list[np.ndarray]] = {name: [] for name in output_names}
        lower, upper = (float(item) for item in protocol["input_bounds"])
        for record in records:
            time_s = record["time_s"]
            inputs = record["inputs"]
            lengths = {
                len(time_s),
                *(len(values) for values in inputs.values()),
                *(len(values) for values in record["outputs"].values()),
            }
            if len(lengths) != 1 or len(time_s) != len(expected_t):
                raise UploadGateError(
                    "timebase", "sample count does not match the compiled protocol"
                )
            if abs(float(time_s[0])) > max(
                1e-9, 0.02 * float(protocol["sample_period_s"])
            ) or np.any(np.diff(time_s) <= 0):
                raise UploadGateError(
                    "timebase", "time must start at zero and be strictly increasing"
                )
            time_error = float(np.max(np.abs(time_s - expected_t)))
            if time_error > max(1e-8, 0.05 * float(protocol["sample_period_s"])):
                raise UploadGateError(
                    "timebase", "timestamps exceed the public sample-time tolerance"
                )
            time_errors.append(time_error)
            tolerance = max(1e-8, 0.02 * max(upper - lower, 1e-6))
            for name, command in inputs.items():
                expected_u = expected_inputs[name]
                input_error = float(np.max(np.abs(command - expected_u)))
                if input_error > tolerance:
                    raise UploadGateError(
                        "input_waveform",
                        f"measured input {name} does not match the authorized waveform",
                    )
                input_errors.append(input_error)
                if np.any(command < lower - tolerance) or np.any(
                    command > upper + tolerance
                ):
                    raise UploadGateError(
                        "safety_limits",
                        f"measured input {name} exceeds the declared bounds",
                    )
            for name, values in record["outputs"].items():
                output_stacks[name].append(values)
        _set(gates, "timebase", "passed")
        _set(gates, "input_waveform", "passed")
        if stopped_on_limit:
            raise UploadGateError(
                "safety_limits", "operator reported a stop-limit event"
            )
        _set(gates, "safety_limits", "passed")
        repeat_cv: dict[str, float] = {}
        for name, values in output_stacks.items():
            stack = np.stack(values)
            spread = float(np.mean(np.std(stack, axis=0)))
            span = float(np.ptp(np.median(stack, axis=0)))
            repeat_cv[name] = spread / max(span, 1e-9)
            if not math.isfinite(repeat_cv[name]) or repeat_cv[name] > 0.5:
                raise UploadGateError(
                    "signal_quality", f"repeat inconsistency is too high for {name}"
                )
        _set(gates, "signal_quality", "passed")
        metrics = {
            "max_time_error_s": max(time_errors),
            "max_input_error": max(input_errors),
            "repeat_cv": repeat_cv,
        }
        traces = []
        for index, record in enumerate(records, 1):
            primary_input = record["inputs"][input_names[0]]
            trace = PublicTrace(
                trace_id=f"upload-{fingerprint(receipts)[:10]}-{index:02d}",
                source="user_upload",
                time_s=tuple(record["time_s"].tolist()),
                signals={
                    "input": primary_input.tolist(),
                    **{
                        key: value.tolist()
                        for key, value in record["inputs"].items()
                        if key != "input"
                    },
                    **{key: value.tolist() for key, value in record["outputs"].items()},
                },
                units={
                    "input": protocol["units"]["input"],
                    **{name: protocol["units"]["input"] for name in input_names},
                    **dict(protocol["units"]["outputs"]),
                },
                metadata={
                    "control_inputs": list(input_names),
                    "measured_signals": list(output_names),
                },
                protocol_fingerprint=protocol["protocol_fingerprint"],
                operating_region=protocol.get(
                    "initial_condition_id", "declared_operating_region"
                ),
                trial_id=f"repeat-{index:02d}",
            )
            traces.append(trace.to_dict())
        status = "accepted"
        failed_gate = None
        message = "upload passed all deterministic gates"
    except UploadGateError as exc:
        failed_gate = exc.gate_id
        _set(gates, exc.gate_id, "failed", str(exc))
        status = "rejected"
        traces = []
        message = str(exc)
    audit = {
        "upload_version": UPLOAD_AUDIT_VERSION,
        "status": status,
        "session_id": session_id,
        "protocol_fingerprint": protocol.get("protocol_fingerprint"),
        "recorded_at": utc_now(),
        "file_receipts": receipts,
        "raw_files_persisted": False,
        "gates": gates,
        "failed_gate": failed_gate,
        "message": message,
        "metrics": metrics,
        "trace_fingerprints": [item["trace_fingerprint"] for item in traces],
    }
    audit["upload_fingerprint"] = fingerprint(audit)
    return {"audit": audit, "traces": traces}


__all__ = ["GATE_DEFINITIONS", "UploadGateError", "inspect_upload"]
