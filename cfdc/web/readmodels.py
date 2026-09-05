"""Bounded, read-only projections of already verified Kernel session reports.

Raw artifacts remain authoritative. Display reduction never feeds evaluation,
replay, protocol acceptance, or a persisted session.
"""

from __future__ import annotations

import json
import math
import re
from collections import OrderedDict
from collections.abc import Mapping
from itertools import islice, pairwise
from pathlib import Path
from threading import RLock
from typing import Any, Literal

from pydantic import BaseModel, Field

from cfdc.kernel import WorkflowService
from cfdc.web.presentation import (
    evaluation_options,
    project_workspace,
    protocol_summary,
    result_rows,
    trace_preview,
    upload_feedback,
)
from cfdc.web.service import load_kernel_app_run


class Identity(BaseModel):
    session_id: str
    revision: int


class Workspace(BaseModel):
    stage: int
    title: str
    explanation: str
    action: str
    action_title: str
    action_help: str
    actionable: bool
    advanced: bool
    result_visible: bool
    task_summary: str


class TaskSummary(Identity):
    status: str
    read_only: bool
    task: dict[str, Any]
    workspace: Workspace
    input_contract: dict[str, Any]
    pending_actions: list[dict[str, Any]]
    rag_snapshot: str | None = None
    registered_case_id: str | None = None


class CatalogItem(BaseModel):
    id: str
    label: str
    kind: str
    fingerprint: str | None = None


class ArtifactCatalog(Identity):
    items: list[CatalogItem]


class NodeItem(BaseModel):
    key: str
    pointer: str
    kind: Literal["object", "array", "string", "value"]
    preview: str
    expandable: bool
    total: int | None = None


class NodePage(Identity):
    artifact_id: str
    fingerprint: str | None = None
    pointer: str
    kind: Literal["object", "array", "string", "value"]
    total: int
    offset: int
    limit: int
    items: list[NodeItem] = Field(default_factory=list)
    text: str | None = None
    value: str | float | int | bool | None = None


class SectionPage(Identity):
    section: str
    total: int
    offset: int
    limit: int
    items: list[dict[str, Any]]


class Column(BaseModel):
    name: str
    unit: str


class Preview(BaseModel):
    columns: list[str]
    rows: list[list[Any]]


class EvidenceOption(BaseModel):
    label: str
    value: str
    signals: list[str]
    trial_id: str
    fingerprint: str | None = None
    protocol_fingerprint: str


class ProtocolView(Identity):
    summary: str
    feedback: str
    columns: list[Column]
    preview: Preview
    protocol_fingerprint: str | None = None
    repeat_count: int | None = None
    accepted: bool | None = None
    evidence_options: list[EvidenceOption] = Field(default_factory=list)


class EvaluationOption(BaseModel):
    label: str
    value: str
    signals: list[str]
    control_signals: list[str]
    stage: Literal["development", "confirmation"]
    fingerprint: str | None = None


class EvaluationsView(Identity):
    options: list[EvaluationOption]
    metrics: list[list[str]]
    selected_selection: str | None = None
    selected_stage: Literal["development", "confirmation"] | None = None


class Curve(BaseModel):
    name: str
    x: list[float]
    y: list[float]
    unit: str


class EvidenceCurveView(Identity):
    selection: str
    signal: str
    stage: Literal["evidence"] = "evidence"
    fingerprint: str | None = None
    protocol_fingerprint: str
    trial_id: str
    original_points: int
    display_points: int
    output: list[Curve]


class CurveView(Identity):
    selection: str
    signal: str
    stage: Literal["development", "confirmation"]
    fingerprint: str | None = None
    selected_control: str | None = None
    original_points: int
    display_points: int
    output: list[Curve]
    control: list[Curve]


def _map(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _seq(value: Any):
    return value if isinstance(value, (list, tuple)) else ()


def _identity(report):
    return {
        "session_id": str(report.get("session_id") or ""),
        "revision": int(report.get("revision") or 0),
    }


def _text(value, limit=200):
    return str(value)[:limit]


def _bounded(value, *, depth=3, width=32, text=512, budget=None):
    """Copy only a globally bounded prefix without walking unshown subtrees."""
    budget = [8192] if budget is None else budget
    if budget[0] <= 0:
        return None
    budget[0] -= 32
    if isinstance(value, Mapping):
        if depth <= 0:
            return {"kind": "object", "total": len(value)}
        result = {}
        for key, item in islice(value.items(), width):
            if budget[0] <= 0:
                break
            name = _text(key, min(128, budget[0]))
            budget[0] -= len(name) + 8
            result[name] = _bounded(
                item, depth=depth - 1, width=width, text=text, budget=budget
            )
        return result
    if isinstance(value, (list, tuple)):
        if depth <= 0:
            return {"kind": "array", "total": len(value)}
        result = []
        for item in value[:width]:
            if budget[0] <= 0:
                break
            result.append(
                _bounded(item, depth=depth - 1, width=width, text=text, budget=budget)
            )
        return result
    if isinstance(value, str):
        shown = value[: max(0, min(text, budget[0]))]
        budget[0] -= len(shown)
        return shown
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return (
        value
        if value is None or isinstance(value, (int, float, bool))
        else _text(value, text)
    )


def summary(report) -> TaskSummary:
    task = _bounded(_map(report.get("task")), depth=3, width=32)
    contract = _bounded(_map(report.get("input_contract")), depth=4, width=32)
    active = report.get("active_protocol_fingerprint")
    handoff = next(
        (
            h
            for h in reversed(_seq(report.get("operator_handoffs")))
            if active and _map(h).get("protocol_fingerprint") == active
        ),
        {},
    )
    contract["operator_prechecks"] = [
        _text(v, 256) for v in _seq(handoff.get("prechecks"))[:32]
    ]
    # Workspace needs packet/replay identity only, never trajectories or large audit data.
    projection = {
        key: report.get(key)
        for key in (
            "status",
            "read_only",
            "confirmation",
            "evaluation",
            "qualification",
            "tuning",
        )
    }
    projection.update(task=task, input_contract=contract)
    for key in ("evaluation_packets", "evaluation_replays"):
        projection[key] = [
            {
                field: _map(item).get(field)
                for field in (
                    "packet_fingerprint",
                    "evaluation_split",
                    "matches_previous",
                )
            }
            for item in _seq(report.get(key))
        ]
    workspace = project_workspace(projection)
    workspace["task_summary"] = workspace["task_summary"][:16384]
    return TaskSummary(
        **_identity(report),
        status=_text(report.get("status") or "", 128),
        read_only=bool(report.get("read_only")),
        task=task,
        workspace=workspace,
        input_contract=contract,
        pending_actions=[
            _bounded(_map(v), depth=2, width=16, budget=[1024])
            for v in _seq(report.get("pending_actions"))[:20]
        ],
        rag_snapshot=_text(report["rag_snapshot"], 256)
        if report.get("rag_snapshot")
        else None,
        registered_case_id=_map(report.get("registered_case_binding")).get("case_id"),
    )


def _fingerprint(value):
    value = _map(value)
    for name in (
        "packet_fingerprint",
        "protocol_fingerprint",
        "freeze_fingerprint",
        "controller_fingerprint",
        "fingerprint",
        "task_fingerprint",
    ):
        if value.get(name):
            return _text(value[name], 256)
    return None


def _kind(value):
    return (
        "object"
        if isinstance(value, Mapping)
        else "array"
        if isinstance(value, (list, tuple))
        else "string"
        if isinstance(value, str)
        else "value"
    )


def _selector(value):
    # JSON escapes control characters to six bytes; the serialized selector is
    # repeated in node keys and pointers. Bound the actual representation.
    if (
        not isinstance(value, str)
        or len(value.encode("utf-8")) > 512
        or len(json.dumps(value, ensure_ascii=False).encode("utf-8")) > 512
    ):
        raise ValueError("selector_too_large")
    return value


def artifact_catalog(report) -> ArtifactCatalog:
    items = [CatalogItem(id="report", label="report", kind="object")]
    for key, value in islice(report.items(), 100):
        _selector(key)
        items.append(
            CatalogItem(
                id=key, label=key, kind=_kind(value), fingerprint=_fingerprint(value)
            )
        )
    return ArtifactCatalog(**_identity(report), items=items)


def _artifact(report, artifact_id):
    _selector(artifact_id)
    if artifact_id == "report":
        return report
    if artifact_id not in report:
        raise ValueError("unknown_artifact")
    return report[artifact_id]


def _page_args(offset, limit):
    if (
        isinstance(offset, bool)
        or not isinstance(offset, int)
        or offset < 0
        or not isinstance(limit, int)
        or isinstance(limit, bool)
        or not 1 <= limit <= 100
    ):
        raise ValueError("invalid_pagination")


def _resolve(value, pointer):
    _selector(pointer)
    if not pointer:
        return value
    if not pointer.startswith("/"):
        raise ValueError("invalid_json_pointer")
    for raw in pointer[1:].split("/"):
        if re.search(r"~(?![01])", raw):
            raise ValueError("invalid_json_pointer")
        key = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(value, Mapping) and key in value:
            value = value[key]
        elif (
            isinstance(value, (list, tuple))
            and re.fullmatch(r"0|[1-9][0-9]*", key)
            and len(key) < 20
            and int(key) < len(value)
        ):
            value = value[int(key)]
        else:
            raise ValueError("unknown_json_pointer")
    return value


def _node_item(key, value, pointer):
    key = _selector(str(key))
    child = _selector(pointer + "/" + key.replace("~", "~0").replace("/", "~1"))
    kind = _kind(value)
    total = len(value) if kind != "value" else None
    preview = f"{kind} ({total})" if kind in {"object", "array"} else _text(value)
    return NodeItem(
        key=key,
        pointer=child,
        kind=kind,
        preview=preview,
        expandable=kind != "value",
        total=total,
    )


def node_page(report, artifact_id, pointer="", offset=0, limit=50) -> NodePage:
    _page_args(offset, limit)
    artifact = _artifact(report, artifact_id)
    value = _resolve(artifact, pointer)
    kind = _kind(value)
    bound_fingerprint = _fingerprint(artifact)
    prefix = ""
    for token in pointer.split("/")[1:]:
        prefix += "/" + token
        bound_fingerprint = (
            _fingerprint(_resolve(artifact, prefix)) or bound_fingerprint
        )
    page = NodePage(
        **_identity(report),
        artifact_id=artifact_id,
        fingerprint=bound_fingerprint,
        pointer=pointer,
        kind=kind,
        total=len(value) if kind != "value" else 1,
        offset=offset,
        limit=limit,
    )
    if kind == "object":
        page.items = [
            _node_item(k, v, pointer)
            for k, v in islice(value.items(), offset, offset + limit)
        ]
    elif kind == "array":
        page.items = [
            _node_item(i, value[i], pointer)
            for i in range(offset, min(offset + limit, len(value)))
        ]
    elif kind == "string":
        page.text = value[offset : offset + 8192]
    else:
        page.value = _bounded(value)
    # Keep the response budget explicit even if future DTO fields or previews
    # change. Reject the whole page rather than silently dropping children and
    # making the caller's offset + limit pagination skip evidence.
    if len(page.model_dump_json().encode("utf-8")) > 256 * 1024:
        raise ValueError("node_response_too_large")
    return page


def section_page(report, section, offset=0, limit=50) -> SectionPage:
    _page_args(offset, limit)
    value = _artifact(report, section)
    if not isinstance(value, (list, tuple)):
        raise TypeError("section_array_required")
    items = []
    for item in value[offset : offset + limit]:
        if isinstance(item, Mapping):
            items.append(_bounded(item, depth=1, width=20, text=200, budget=[512]))
        else:
            items.append({"value": _bounded(item, depth=0, text=200)})
    return SectionPage(
        **_identity(report),
        section=section,
        total=len(value),
        offset=offset,
        limit=limit,
        items=items,
    )


def _accepted_evidence(report):
    """Yield accepted, currently protocol-bound records from verified evidence."""
    active = report.get("active_protocol_fingerprint")
    if not active or not any(
        _map(p).get("protocol_fingerprint") == active
        for p in _seq(report.get("protocols"))
    ):
        return
    for index, item in enumerate(_seq(report.get("evidence"))):
        item = _map(item)
        trace = _map(item.get("trace"))
        if (
            item.get("protocol_fingerprint") == active
            and item.get("status", "accepted") in {"accepted", "passed", "valid"}
            and trace.get("protocol_fingerprint", active) == active
            and _seq(trace.get("time_s"))
            and _map(trace.get("signals"))
        ):
            yield index, item


def _trace_fingerprint(item):
    value = item.get("trace_fingerprint") or _map(item.get("trace")).get(
        "trace_fingerprint"
    )
    return _text(value, 256) if value else None


def protocol_view(report) -> ProtocolView:
    active = report.get("active_protocol_fingerprint")
    protocol = next(
        (
            p
            for p in _seq(report.get("protocols"))
            if active and _map(p).get("protocol_fingerprint") == active
        ),
        {},
    )
    accepted_evidence = list(_accepted_evidence(report))
    evidence = [item for _, item in accepted_evidence]
    evidence_options = []
    option_bytes = 0
    for index, item in accepted_evidence[:100]:
        trace = _map(item.get("trace"))
        trial_id = _text(item.get("trial_id") or trace.get("trial_id") or "", 200)
        option = EvidenceOption(
            label=trial_id or f"Trace {index + 1}",
            value=str(index),
            signals=[
                _selector(name) for name in islice(_map(trace.get("signals")), 32)
            ],
            trial_id=trial_id,
            fingerprint=_trace_fingerprint(item),
            protocol_fingerprint=_text(active, 256),
        )
        option_bytes += len(option.model_dump_json().encode("utf-8"))
        if option_bytes > 128 * 1024:
            raise ValueError("evidence_options_too_large")
        evidence_options.append(option)
    # Kernel report evidence has passed typed validation. Upload attempts are never previews.
    preview_report = {"evidence": evidence[-1:]}
    headers, rows = trace_preview(preview_report)
    headers = [_text(v, 200) for v in headers[:32]]
    rows = [[_bounded(v, depth=0, text=200) for v in row[:32]] for row in rows[:20]]
    units = _map(_map(protocol.get("units")).get("outputs"))
    columns = [
        Column(name=_text(name, 200), unit=_text(units.get(name) or "", 100))
        for name in _seq(protocol.get("requested_signals"))[:32]
    ]
    attempts = [
        a
        for a in _seq(report.get("upload_attempts"))
        if active
        and (
            _map(a).get("protocol_fingerprint") == active
            or _map(_map(a).get("audit")).get("protocol_fingerprint") == active
        )
    ]
    audit = (
        _map(_map(attempts[-1]).get("audit")) or _map(attempts[-1]) if attempts else {}
    )
    return ProtocolView(
        **_identity(report),
        summary=protocol_summary(
            {
                "protocols": [protocol] if protocol else [],
                "active_protocol_fingerprint": active,
                "registered_case_binding": report.get("registered_case_binding"),
            }
        )[:8192],
        feedback=upload_feedback(
            {
                "upload_attempts": attempts[-1:],
                "registered_case_binding": report.get("registered_case_binding"),
            }
        )[:8192],
        columns=columns,
        preview=Preview(columns=headers, rows=rows),
        protocol_fingerprint=active if protocol else None,
        repeat_count=protocol.get("repeats"),
        accepted=audit.get("status") == "accepted" if audit else None,
        evidence_options=evidence_options,
    )


def _selected(report, selection):
    if (
        not isinstance(selection, str)
        or not re.fullmatch(r"(0|[1-9][0-9]*):(0|[1-9][0-9]*)", selection)
        or len(selection) > 40
    ):
        raise ValueError("invalid_evaluation_selection")
    p, t = map(int, selection.split(":"))
    packets = _seq(report.get("evaluation_packets"))
    if p >= len(packets):
        raise ValueError("unknown_evaluation_selection")
    packet = _map(packets[p])
    trials = _seq(packet.get("trials"))
    if t >= len(trials) or packet.get("evaluation_split") not in {
        "development",
        "fresh_confirmation",
    }:
        raise ValueError("unknown_evaluation_selection")
    return packet, _map(trials[t])


def _stage(packet):
    return (
        "confirmation"
        if packet.get("evaluation_split") == "fresh_confirmation"
        else "development"
    )


def evaluations_view(report, selection=None) -> EvaluationsView:
    options = []
    for label, value in evaluation_options(report):
        try:
            packet, trial = _selected(report, value)
        except ValueError:
            continue
        trajectory = _map(trial.get("trajectory"))
        options.append(
            EvaluationOption(
                label=_text(label, 300),
                value=value,
                stage=_stage(packet),
                fingerprint=_fingerprint(packet),
                signals=[_selector(name) for name in _map(trajectory.get("outputs"))],
                control_signals=[
                    _selector(name) for name in _map(trajectory.get("control_inputs"))
                ],
            )
        )
    if selection is None:
        selection = options[0].value if options else None
    if selection is None:
        return EvaluationsView(**_identity(report), options=options, metrics=[])
    packet, trial = _selected(report, selection)
    evaluation = _map(report.get("evaluation"))
    bound = (
        bool(packet.get("packet_fingerprint"))
        and evaluation.get("packet_fingerprint") == packet.get("packet_fingerprint")
        and evaluation.get("evaluation_split") == packet.get("evaluation_split")
    )
    if bound:
        isolated = dict(evaluation)
        isolated["trials"] = [
            item
            for item in _seq(evaluation.get("trials"))
            if _map(item).get("trial_id") == trial.get("trial_id")
        ][:1]
        confirmation = _map(report.get("confirmation"))
        if confirmation.get("packet_fingerprint") != packet.get("packet_fingerprint"):
            confirmation = {}
        metric_report = {
            "task": report.get("task"),
            "status": report.get("status"),
            "evaluation": isolated,
            "confirmation": confirmation,
        }
        metrics = [
            [_text(cell, 512) for cell in row]
            for row in result_rows(metric_report)[:200]
        ]
    else:
        metrics = [
            [
                "试次指标",
                "按冻结的评价合同",
                "未评估",
                "未保存与此数据包绑定的评价指标；未从轨迹重新计算。",
            ]
        ]
    return EvaluationsView(
        **_identity(report),
        options=options,
        metrics=metrics,
        selected_selection=selection,
        selected_stage=_stage(packet),
    )


def _finite(value):
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def _display_indices(values, indices, maximum):
    if len(indices) <= maximum:
        return indices
    # Two extrema per disjoint bucket plus both endpoints, in original time order.
    count = max(1, (maximum - 2) // 2)
    interior = indices[1:-1]
    selected = [indices[0]]
    for bucket in range(count):
        group = interior[
            bucket * len(interior) // count : (bucket + 1) * len(interior) // count
        ]
        if group:
            selected.extend(
                sorted(
                    {
                        min(group, key=lambda i: values[i]),
                        max(group, key=lambda i: values[i]),
                    }
                )
            )
    selected.append(indices[-1])
    return selected


def curve_view(
    report, selection, signal, start=None, end=None, max_points=2000, control=None
) -> CurveView:
    if (
        not isinstance(max_points, int)
        or isinstance(max_points, bool)
        or not 4 <= max_points <= 2000
    ):
        raise ValueError("invalid_max_points")
    if any(value is not None and not _finite(value) for value in (start, end)) or (
        start is not None and end is not None and start > end
    ):
        raise ValueError("invalid_curve_window")
    _selector(signal)
    if control is not None:
        _selector(control)
    packet, trial = _selected(report, selection)
    trajectory = _map(trial.get("trajectory"))
    times = _seq(trajectory.get("time_s"))
    outputs = _map(trajectory.get("outputs"))
    controls = _map(trajectory.get("control_inputs"))
    if signal not in outputs:
        raise ValueError("unknown_output_signal")
    if control is not None and control not in controls:
        raise ValueError("unknown_control_signal")
    control = control if control is not None else next(iter(controls), None)
    if (
        not times
        or not all(_finite(v) for v in times)
        or any(b < a for a, b in pairwise(times))
    ):
        raise ValueError("invalid_recorded_time")
    indices = [
        i
        for i, t in enumerate(times)
        if (start is None or t >= start) and (end is None or t <= end)
    ]
    if not indices:
        raise ValueError("empty_curve_window")
    task = _map(report.get("task"))
    units = _map(trajectory.get("units")) or _map(trial.get("units"))
    output_unit = _map(units.get("outputs")).get(
        signal, _map(task.get("signal_units")).get(signal, "")
    )
    input_unit = units.get("input", task.get("input_units", ""))

    def line(name, values, unit):
        if (
            not isinstance(values, (list, tuple))
            or len(values) != len(times)
            or not all(_finite(values[i]) for i in indices)
        ):
            raise ValueError("invalid_recorded_series")
        shown = _display_indices(values, indices, max_points)
        return Curve(
            name=_text(name, 200),
            x=[times[i] for i in shown],
            y=[values[i] for i in shown],
            unit=_text(unit or "", 100),
        )

    output = [line(signal, outputs[signal], output_unit)]
    reference = _map(trajectory.get("references")).get(signal)
    if reference is not None:
        output.append(line("目标值", reference, output_unit))
    control_lines = (
        [line(control, controls[control], input_unit)] if control is not None else []
    )
    result = CurveView(
        **_identity(report),
        selection=selection,
        signal=signal,
        stage=_stage(packet),
        fingerprint=_fingerprint(packet),
        selected_control=control,
        original_points=len(indices),
        display_points=len(output[0].x),
        output=output,
        control=control_lines,
    )
    if len(result.model_dump_json().encode("utf-8")) > 256 * 1024:
        return curve_view(
            report,
            selection,
            signal,
            start=start,
            end=end,
            max_points=min(max_points - 1, 1300),
            control=control,
        )
    return result


def evidence_curve_view(
    report, selection: str, signal: str, start=None, end=None
) -> EvidenceCurveView:
    """Display one recorded accepted trace signal, without inventing a target."""
    if (
        not isinstance(selection, str)
        or len(selection) > 20
        or not re.fullmatch(r"0|[1-9][0-9]*", selection)
    ):
        raise ValueError("invalid_evidence_selection")
    item = next(
        (item for index, item in _accepted_evidence(report) if str(index) == selection),
        None,
    )
    if item is None:
        raise ValueError("unknown_evidence_selection")
    _selector(signal)
    trace = _map(item.get("trace"))
    signals = _map(trace.get("signals"))
    if signal not in signals:
        raise ValueError("unknown_evidence_signal")
    if any(value is not None and not _finite(value) for value in (start, end)) or (
        start is not None and end is not None and start > end
    ):
        raise ValueError("invalid_curve_window")
    times = _seq(trace.get("time_s"))
    values = signals[signal]
    if (
        not times
        or not all(_finite(value) for value in times)
        or any(b <= a for a, b in pairwise(times))
    ):
        raise ValueError("invalid_recorded_time")
    indices = [
        i
        for i, value in enumerate(times)
        if (start is None or value >= start) and (end is None or value <= end)
    ]
    if not indices:
        raise ValueError("empty_curve_window")
    if (
        not isinstance(values, (list, tuple))
        or len(values) != len(times)
        or not all(_finite(values[i]) for i in indices)
    ):
        raise ValueError("invalid_recorded_series")
    shown = _display_indices(values, indices, 2000)
    result = EvidenceCurveView(
        **_identity(report),
        selection=selection,
        signal=signal,
        fingerprint=_trace_fingerprint(item),
        protocol_fingerprint=_text(report["active_protocol_fingerprint"], 256),
        trial_id=_text(item.get("trial_id") or trace.get("trial_id") or "", 200),
        original_points=len(indices),
        display_points=len(shown),
        output=[
            Curve(
                name=signal,
                x=[times[i] for i in shown],
                y=[values[i] for i in shown],
                unit=_text(_map(trace.get("units")).get(signal) or "", 100),
            )
        ],
    )
    if len(result.model_dump_json().encode("utf-8")) > 256 * 1024:
        raise ValueError("evidence_curve_response_too_large")
    return result


class ReportCache:
    """LRU of verified reports; source identity is checked before every hit.

    Capacity counts source JSON bytes, not an estimate of Python heap usage.
    Oversized records are verified and served but never retained. Callers must
    treat cached report/state objects as immutable.
    """

    def __init__(self, session_dir: Path, max_entries=4, max_bytes=128 * 1024 * 1024):
        if max_entries < 1 or max_bytes < 1:
            raise ValueError("invalid_cache_capacity")
        self.service = WorkflowService(session_dir)
        self.max_entries = max_entries
        self.max_bytes = max_bytes
        self._entries = OrderedDict()
        self._bytes = 0
        self._lock = RLock()

    def _path(self, session_id):
        path = self.service._path(session_id)
        if path.resolve().parent != self.service.root or path.is_symlink():
            raise ValueError("invalid_session_path")
        return path

    @staticmethod
    def _stat(path):
        stat = path.stat()
        return (
            stat.st_dev,
            stat.st_ino,
            stat.st_size,
            stat.st_mtime_ns,
            stat.st_ctime_ns,
        )

    def invalidate(self, session_id):
        with self._lock:
            entry = self._entries.pop(session_id, None)
            if entry:
                self._bytes -= entry[0][2]

    def get(self, session_id):
        with self._lock:
            path = self._path(session_id)
            source = self._stat(path)
            cached = self._entries.get(session_id)
            if cached and cached[0] == source:
                self._entries.move_to_end(session_id)
                return cached[1]
            self.invalidate(session_id)
            for _ in range(3):
                source = self._stat(self._path(session_id))
                loaded = load_kernel_app_run(session_id, session_dir=self.service.root)
                if self._stat(self._path(session_id)) == source:
                    break
            else:
                raise ValueError("session_changed_during_read")
            size = source[2]
            if size <= self.max_bytes:
                while self._entries and (
                    len(self._entries) >= self.max_entries
                    or self._bytes + size > self.max_bytes
                ):
                    _, removed = self._entries.popitem(last=False)
                    self._bytes -= removed[0][2]
                self._entries[session_id] = (source, loaded)
                self._bytes += size
            return loaded
