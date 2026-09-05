"""Read models preserve recorded evidence and keep interactive reads bounded."""

from __future__ import annotations

import copy
import json
import statistics
import time

import pytest

from cfdc.web import readmodels as rm
from cfdc.web.service import start_kernel_case_run


def report_fixture():
    return {
        "session_id": "sample",
        "revision": 3,
        "status": "awaiting_confirmation",
        "task": {
            "description": "test",
            "measured_signals": ["y"],
            "signal_units": {"y": "K"},
            "input_units": "W",
        },
        "input_contract": {"action": "confirm_result", "allowed_modes": []},
        "pending_actions": [],
        "evaluation_packets": [
            {
                "packet_fingerprint": "dev",
                "evaluation_split": "development",
                "trials": [
                    {
                        "trial_id": "same",
                        "trajectory": {
                            "time_s": [0.0, 1.0, 2.0],
                            "outputs": {"y": [10.0, 20.0, 30.0]},
                            "references": {"y": [20.0, 20.0, 20.0]},
                            "control_inputs": {
                                "u": [1.0, 2.0, 3.0],
                                "v": [4.0, 5.0, 6.0],
                            },
                        },
                    }
                ],
            },
            {
                "packet_fingerprint": "confirm",
                "evaluation_split": "fresh_confirmation",
                "trials": [
                    {
                        "trial_id": "same",
                        "trajectory": {
                            "time_s": [0.0, 1.0, 2.0],
                            "outputs": {"y": [40.0, 50.0, 60.0]},
                            "control_inputs": {"u": [7.0, 8.0, 9.0]},
                        },
                    }
                ],
            },
        ],
        "evaluation": {
            "packet_fingerprint": "confirm",
            "evaluation_split": "fresh_confirmation",
            "status": "performance_not_met",
            "trials": [
                {
                    "trial_id": "same",
                    "metrics": {"channels": {"y": {"final_abs_error": 123.0}}},
                }
            ],
        },
    }


def test_summary_is_bounded_and_keeps_authority():
    report = report_fixture()
    report["read_only"] = True
    report["active_protocol_fingerprint"] = "new"
    report["operator_handoffs"] = [
        {"protocol_fingerprint": "new", "prechecks": ["units", "logger"]},
        {"protocol_fingerprint": "old", "prechecks": ["wrong"]},
    ]
    result = rm.summary(report)
    assert result.read_only and not result.workspace.actionable
    assert result.input_contract["operator_prechecks"] == ["units", "logger"]
    assert "evaluation_packets" not in result.model_dump()
    assert result.workspace.result_visible


def test_shallow_json_pointer_paging_and_scalar_text():
    report = report_fixture()
    report["evidence"] = {"a/b~c": list(range(200)), "text": "x" * 20000}
    catalog = rm.artifact_catalog(report)
    assert {"report", "evidence"} <= {item.id for item in catalog.items}
    page = rm.node_page(report, "evidence")
    assert page.items[0].pointer == "/a~1b~0c"
    assert page.items[0].expandable
    child = rm.node_page(report, "evidence", "/a~1b~0c", offset=100, limit=20)
    assert child.total == 200 and len(child.items) == 20
    assert child.items[0].preview == "100"
    assert len(rm.node_page(report, "evidence", "/text").text) <= 8192
    assert rm.node_page(report, "evidence", "/text", offset=8192).text == "x" * 8192
    for pointer in ["a", "/a~2b", "/a~1b~0c/-1", "/a~1b~0c/01"]:
        with pytest.raises(ValueError):
            rm.node_page(report, "evidence", pointer)
    with pytest.raises(ValueError):
        rm.node_page(report, "../evidence")
    with pytest.raises(ValueError):
        rm.node_page(report, "evidence", limit=101)
    report["huge"] = {"x" * 2000: 1}
    with pytest.raises(ValueError):
        rm.node_page(report, "huge")


def test_sections_are_shallow_and_paginated():
    report = report_fixture()
    report["events"] = [{"type": "audit", "payload": {"large": "x" * 100000}}] * 100
    page = rm.section_page(report, "events", offset=10, limit=2)
    assert page.total == 100 and len(page.items) == 2
    assert len(page.model_dump_json()) < 10000


def test_curves_and_metrics_never_borrow_another_packet_or_trial():
    report = report_fixture()
    before = copy.deepcopy(report)
    curve = rm.curve_view(report, "0:0", "y", control="v")
    assert curve.stage == "development" and curve.fingerprint == "dev"
    assert curve.output[0].y == [10.0, 20.0, 30.0]
    assert curve.control[0].y == [4.0, 5.0, 6.0]
    assert curve.selected_control == "v"
    assert rm.curve_view(report, "1:0", "y").output[0].y == [40.0, 50.0, 60.0]
    dev = rm.evaluations_view(report, selection="0:0")
    assert "123" not in dev.model_dump_json()
    assert dev.selected_stage == "development"
    confirmed = rm.evaluations_view(report, selection="1:0")
    assert any("123" in cell for row in confirmed.metrics for cell in row)
    for selection, signal, control in [
        ("99:0", "y", None),
        ("0:0", "z", None),
        ("0:0", "y", "missing"),
        ("-1:0", "y", None),
    ]:
        with pytest.raises(ValueError):
            rm.curve_view(report, selection, signal, control=control)
    assert report == before


def test_minmax_display_preserves_endpoints_extrema_and_window():
    report = report_fixture()
    n = 10001
    values = [0.0] * n
    values[1234], values[5678] = 999.0, -888.0
    trajectory = report["evaluation_packets"][0]["trials"][0]["trajectory"]
    trajectory.update(
        time_s=list(range(n)), outputs={"y": values}, references={}, control_inputs={}
    )
    curve = rm.curve_view(report, "0:0", "y")
    assert curve.original_points == n and curve.display_points <= 2000
    assert curve.output[0].x[0] == 0 and curve.output[0].x[-1] == n - 1
    assert max(curve.output[0].y) == 999 and min(curve.output[0].y) == -888
    window = rm.curve_view(report, "0:0", "y", start=1000, end=2000, max_points=100)
    assert window.original_points == 1001 and window.display_points <= 100
    assert window.output[0].x[0] == 1000 and window.output[0].x[-1] == 2000
    for kwargs in [
        {"start": 2, "end": 1},
        {"start": float("nan")},
        {"start": 10002},
        {"max_points": 2001},
    ]:
        with pytest.raises(ValueError):
            rm.curve_view(report, "0:0", "y", **kwargs)


def test_protocol_preview_only_current_verified_evidence():
    report = report_fixture()
    report.update(
        active_protocol_fingerprint="current",
        protocols=[
            {
                "protocol_fingerprint": "current",
                "repeats": 2,
                "requested_signals": ["y"],
                "units": {"outputs": {"y": "K"}},
            }
        ],
        evidence=[
            {
                "protocol_fingerprint": "current",
                "trace": {"time_s": [0.0, 1.0], "signals": {"y": [1.0, 2.0]}},
            },
            {
                "protocol_fingerprint": "old",
                "trace": {"time_s": [0.0], "signals": {"y": [99.0]}},
            },
            {
                "protocol_fingerprint": "current",
                "status": "rejected",
                "trace": {"time_s": [0.0], "signals": {"y": [88.0]}},
            },
        ],
    )
    view = rm.protocol_view(report)
    assert view.protocol_fingerprint == "current" and view.repeat_count == 2
    assert len(view.preview.rows) == 2 and view.preview.rows[0][-1] == 1
    report["active_protocol_fingerprint"] = "absent"
    assert rm.protocol_view(report).preview.rows == []


def test_report_cache_validates_real_sources_and_invalidates(tmp_path):
    report, _ = start_kernel_case_run(
        "tclab_single_heater_v1", session_dir=tmp_path, use_rag=False
    )
    sid = report["session_id"]
    cache = rm.ReportCache(tmp_path)
    first, _ = cache.get(sid)
    assert cache.get(sid)[0] is first
    path = tmp_path / f"{sid}.json"
    raw = path.read_text()
    path.write_text(raw + "\n")
    assert cache.get(sid)[0] is not first
    cache.invalidate(sid)
    current = cache.get(sid)[0]
    assert current is not first
    path.write_text("{}")
    with pytest.raises((ValueError, TypeError, KeyError)):
        cache.get(sid)
    with pytest.raises(ValueError):
        cache.get("../outside")


def test_report_cache_capacity_by_entries_and_source_bytes(tmp_path):
    ids = [
        start_kernel_case_run(
            "tclab_single_heater_v1", session_dir=tmp_path, use_rag=False
        )[0]["session_id"]
        for _ in range(3)
    ]
    cache = rm.ReportCache(tmp_path, max_entries=1)
    first = cache.get(ids[0])[0]
    cache.get(ids[1])
    assert cache.get(ids[0])[0] is not first
    cache = rm.ReportCache(tmp_path, max_bytes=1)
    first = cache.get(ids[0])[0]
    assert cache.get(ids[0])[0] is not first


def test_synthetic_50mib_warm_payload_latency(capsys):
    report = report_fixture()
    report["events"] = [{"type": "synthetic", "payload": "x" * 1024}] * (50 * 1024)
    assert len(json.dumps(report).encode()) >= 50 * 1024 * 1024
    durations = []
    sizes = []
    for _ in range(21):
        started = time.perf_counter()
        bodies = [
            rm.summary(report).model_dump_json(),
            rm.node_page(report, "events", offset=20000).model_dump_json(),
        ]
        durations.append(time.perf_counter() - started)
        sizes = [len(body.encode()) for body in bodies]
    p95 = statistics.quantiles(durations[1:], n=20)[18]
    assert max(sizes) <= 256 * 1024
    assert p95 <= 1.0
    print(f"50MiB warmed summary+node P95={p95:.6f}s bytes={sizes}")


def test_summary_global_budget_and_hostile_unicode_nodes():
    report = report_fixture()
    report["task"] = {
        str(i): {str(j): {str(k): "量" * 1000 for k in range(32)} for j in range(32)}
        for i in range(32)
    }
    assert len(rm.summary(report).model_dump_json().encode()) <= 256 * 1024
    report["events"] = [{"量" * 100: "量" * 1000} for _ in range(100)]
    assert (
        len(rm.node_page(report, "events", limit=100).model_dump_json().encode())
        <= 256 * 1024
    )


def test_cache_rejects_symlink_and_missing_source(tmp_path):
    outside = tmp_path / "other"
    outside.mkdir()
    (outside / "record.json").write_text("{}")
    (tmp_path / "link.json").symlink_to(outside / "record.json")
    cache = rm.ReportCache(tmp_path)
    with pytest.raises(ValueError):
        cache.get("link")
    with pytest.raises(FileNotFoundError):
        cache.get("missing")


def test_real_50mib_cached_session_read_latency(tmp_path):
    report, _ = start_kernel_case_run(
        "tclab_single_heater_v1", session_dir=tmp_path, use_rag=False
    )
    sid = report["session_id"]
    path = tmp_path / f"{sid}.json"
    document = json.loads(path.read_text())
    document["agent_records"] = [{"kind": "synthetic", "source_text": "x" * 1024}] * (
        50 * 1024
    )
    path.write_text(json.dumps(document))
    assert path.stat().st_size >= 50 * 1024 * 1024
    cache = rm.ReportCache(tmp_path)
    started = time.perf_counter()
    cache.get(sid)
    cold = time.perf_counter() - started
    durations = []
    for _ in range(20):
        started = time.perf_counter()
        current, _ = cache.get(sid)
        summary_body = rm.summary(current).model_dump_json().encode()
        node_body = (
            rm.node_page(current, "agent_records", offset=40000)
            .model_dump_json()
            .encode()
        )
        durations.append(time.perf_counter() - started)
    p95 = statistics.quantiles(durations, n=20)[18]
    assert p95 <= 1 and max(len(summary_body), len(node_body)) <= 256 * 1024
    print(
        f"Verified cached file bytes={path.stat().st_size}; cold={cold:.4f}s; warmP95={p95:.6f}s; summary={len(summary_body)}B node={len(node_body)}B"
    )


def test_descendant_nodes_keep_packet_fingerprint():
    report = report_fixture()
    page = rm.node_page(report, "evaluation_packets", "/0/trials/0/trajectory")
    assert page.fingerprint == "dev"


def test_curve_response_budget_with_long_finite_floats():
    report = report_fixture()
    trajectory = report["evaluation_packets"][0]["trials"][0]["trajectory"]
    values = [
        1.1234567890123456e-120 if i % 2 else -1.2345678901234567e-120
        for i in range(5000)
    ]
    trajectory.update(
        time_s=[i * 1.2345678901234567e-100 for i in range(5000)],
        outputs={"y": values},
        references={"y": values},
        control_inputs={"u": values},
    )
    curve = rm.curve_view(report, "0:0", "y")
    assert len(curve.model_dump_json().encode()) <= 256 * 1024
    assert curve.output[0].x[-1] == trajectory["time_s"][-1]


def test_section_response_budget_with_unicode_text():
    report = report_fixture()
    report["events"] = [{str(i): "量" * 1000 for i in range(20)}] * 100
    assert (
        len(rm.section_page(report, "events", limit=100).model_dump_json().encode())
        <= 256 * 1024
    )


def test_cache_byte_sum_and_atomic_replacement_invalidation(tmp_path):
    ids = [
        start_kernel_case_run(
            "tclab_single_heater_v1", session_dir=tmp_path, use_rag=False
        )[0]["session_id"]
        for _ in range(2)
    ]
    paths = [tmp_path / f"{sid}.json" for sid in ids]
    budget = max(path.stat().st_size for path in paths) + 1
    cache = rm.ReportCache(tmp_path, max_entries=4, max_bytes=budget)
    first = cache.get(ids[0])[0]
    cache.get(ids[1])
    assert cache.get(ids[0])[0] is not first
    first = cache.get(ids[0])[0]
    replacement = tmp_path / "replacement.json"
    replacement.write_bytes(paths[0].read_bytes())
    replacement.replace(paths[0])
    assert cache.get(ids[0])[0] is not first


def test_node_rejects_escape_expanded_selectors_in_verified_session(tmp_path):
    report, _ = start_kernel_case_run(
        "tclab_single_heater_v1", session_dir=tmp_path, use_rag=False
    )
    sid = report["session_id"]
    path = tmp_path / f"{sid}.json"
    document = json.loads(path.read_text())
    record = {("\x01" * 490) + str(i): "\x02" * 200 for i in range(100)}
    document["agent_records"] = [record]
    path.write_text(json.dumps(document))
    loaded, _ = rm.ReportCache(tmp_path).get(sid)
    with pytest.raises(ValueError, match="selector_too_large"):
        rm.node_page(loaded, "agent_records", "/0", limit=100)
    assert loaded["agent_records"][0] == record
    assert json.loads(path.read_text())["agent_records"][0] == record


def test_node_escaped_text_stays_bounded_without_skipping_items():
    report = report_fixture()
    report["agent_records"] = [
        {("\x01" * 60) + str(i): "\x02" * 200 for i in range(150)}
    ]
    first = rm.node_page(report, "agent_records", "/0", limit=100)
    second = rm.node_page(report, "agent_records", "/0", offset=100, limit=100)
    assert first.total == second.total == 150
    assert len(first.items) == 100 and len(second.items) == 50
    assert [item.key for item in first.items + second.items] == list(
        report["agent_records"][0]
    )
    assert (
        max(len(page.model_dump_json().encode()) for page in (first, second))
        <= 256 * 1024
    )


def evidence_report_fixture():
    report = report_fixture()
    report.update(
        active_protocol_fingerprint="active",
        protocols=[{"protocol_fingerprint": "active"}],
        evidence=[
            {
                "protocol_fingerprint": "active",
                "trace_fingerprint": "trace-a",
                "trial_id": "first",
                "trace": {
                    "protocol_fingerprint": "active",
                    "time_s": [0.0, 1.0, 2.0],
                    "signals": {
                        "temperature": [10.0, 11.0, 12.0],
                        "power": [20.0, 21.0, 22.0],
                    },
                    "units": {"temperature": "degC", "power": "%"},
                },
            },
            {
                "protocol_fingerprint": "old",
                "trace_fingerprint": "trace-old",
                "trace": {
                    "protocol_fingerprint": "old",
                    "time_s": [0.0, 1.0],
                    "signals": {"temperature": [99.0, 99.0]},
                },
            },
            {
                "protocol_fingerprint": "active",
                "status": "rejected",
                "trace": {
                    "protocol_fingerprint": "active",
                    "time_s": [0.0, 1.0],
                    "signals": {"temperature": [88.0, 88.0]},
                },
            },
            {
                "protocol_fingerprint": "active",
                "status": "accepted",
                "trace_fingerprint": "trace-b",
                "trial_id": "second",
                "trace": {
                    "protocol_fingerprint": "active",
                    "time_s": [0.0, 1.0, 2.0],
                    "signals": {"temperature": [30.0, 31.0, 32.0]},
                    "units": {"temperature": "degC"},
                },
            },
        ],
        upload_attempts=[
            {
                "protocol_fingerprint": "active",
                "status": "rejected",
                "trace": {
                    "time_s": [0.0, 1.0],
                    "signals": {"temperature": [777.0, 777.0]},
                },
            }
        ],
    )
    return report


def test_evidence_curve_selects_only_current_accepted_trace_without_mutation():
    report = evidence_report_fixture()
    before = copy.deepcopy(report)
    view = rm.protocol_view(report)
    assert [option.value for option in view.evidence_options] == ["0", "3"]
    assert view.preview.rows[0][-1] == 30
    first = rm.evidence_curve_view(report, "0", "power")
    assert first.fingerprint == "trace-a" and first.protocol_fingerprint == "active"
    assert first.stage == "evidence" and first.trial_id == "first"
    assert len(first.output) == 1 and first.output[0].unit == "%"
    assert first.output[0].y == [20.0, 21.0, 22.0]
    second = rm.evidence_curve_view(report, "3", "temperature", start=1, end=2)
    assert second.output[0].y == [31.0, 32.0] and second.original_points == 2
    for selection, signal in [
        ("1", "temperature"),
        ("2", "temperature"),
        ("9", "temperature"),
        ("-1", "temperature"),
        ("00", "temperature"),
        ("0", "missing"),
    ]:
        with pytest.raises(ValueError):
            rm.evidence_curve_view(report, selection, signal)
    assert report == before


def test_evidence_preview_and_curve_reject_nested_protocol_mismatch():
    report = evidence_report_fixture()
    report["evidence"][0]["trace"]["protocol_fingerprint"] = "other"
    assert [item.value for item in rm.protocol_view(report).evidence_options] == ["3"]
    with pytest.raises(ValueError):
        rm.evidence_curve_view(report, "0", "temperature")
    report["active_protocol_fingerprint"] = "missing"
    assert rm.protocol_view(report).preview.rows == []
    assert rm.protocol_view(report).evidence_options == []


def test_evidence_curve_bounds_window_and_display_preserves_extrema():
    report = evidence_report_fixture()
    trace = report["evidence"][0]["trace"]
    values = [0.0] * 10001
    values[1234], values[5678] = 999.0, -888.0
    trace.update(time_s=list(range(10001)), signals={"temperature": values})
    curve = rm.evidence_curve_view(report, "0", "temperature")
    assert curve.original_points == 10001 and curve.display_points <= 2000
    assert curve.output[0].x[0] == 0 and curve.output[0].x[-1] == 10000
    assert max(curve.output[0].y) == 999 and min(curve.output[0].y) == -888
    assert len(curve.model_dump_json().encode()) <= 256 * 1024
    for kwargs in [{"start": 2, "end": 1}, {"start": float("nan")}, {"start": 10002}]:
        with pytest.raises(ValueError):
            rm.evidence_curve_view(report, "0", "temperature", **kwargs)
