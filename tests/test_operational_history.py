from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from cfdc.history import (
    RECORD_TYPES,
    OperationalHistoryRequest,
    build_history_index,
    load_history_index,
)
from cfdc.kernel import WorkflowService

FIXTURE = Path(__file__).parent / "fixtures/operational_history/records.json"
CONFIG_A = "02bdb8321718d93c1fdb7323aa18446244808dfdabcd7814d8a82c738ebcc6d4"
CONFIG_B = "f36dd28a9f5e598259f313264f654c2eadb78cb37aef0944c1fe6d58b1e46c2d"
REGION_A = "2b55d39a4985d28ba8d686885d602451d09952a263a5435d7b51bd24fc2c502a"
REGION_B = "3b160f2a92a26fab6e9472fb3e7c0ca23188d6efae6a81de314b64b9bbbdc9b7"


class HistoryKeywordEncoder:
    model_name = "test-history-keyword"
    model_revision = "test-revision"

    def encode(self, texts, *, is_query=False):
        del is_query
        if isinstance(texts, str):
            texts = [texts]
        vocabulary = ("rollback", "degraded", "baseline", "maintenance")
        return np.asarray(
            [[text.casefold().count(word) for word in vocabulary] for text in texts],
            dtype=float,
        )


def _build(tmp_path: Path):
    return build_history_index(
        FIXTURE,
        tmp_path / "history-index",
        encoder=HistoryKeywordEncoder(),
    )


def _request(**updates):
    values = {
        "plant_id": "plant-a",
        "configuration_fingerprint": CONFIG_A,
        "operating_region_fingerprint": REGION_A,
        "as_of": "2026-09-03T00:00:00Z",
    }
    values.update(updates)
    return OperationalHistoryRequest(**values)


def test_history_returns_only_exact_identity_and_active_records(tmp_path):
    index = _build(tmp_path)
    result = index.query(_request())
    record_ids = {item.record_id for item in result.records}

    assert result.empty_reason is None
    assert record_ids == {"baseline-v2", "rollback-a", "malicious-a"}
    assert "baseline-v1" not in record_ids
    assert "expired-a" not in record_ids
    assert all(item.plant_id == "plant-a" for item in result.records)
    assert all(item.configuration_fingerprint == CONFIG_A for item in result.records)
    assert all(item.operating_region_fingerprint == REGION_A for item in result.records)


@pytest.mark.parametrize(
    "updates",
    [
        {"plant_id": "plant-missing"},
        {"configuration_fingerprint": "f" * 64},
        {"operating_region_fingerprint": "e" * 64},
    ],
)
def test_history_identity_mismatch_returns_structured_empty_result(tmp_path, updates):
    result = _build(tmp_path).query(_request(**updates))

    assert result.records == ()
    assert result.empty_reason == "identity_not_found"
    assert result.request_identity == {
        "plant_id": updates.get("plant_id", "plant-a"),
        "configuration_fingerprint": updates.get("configuration_fingerprint", CONFIG_A),
        "operating_region_fingerprint": updates.get(
            "operating_region_fingerprint", REGION_A
        ),
    }


@pytest.mark.parametrize(
    ("updates", "expected"),
    [
        ({"configuration_fingerprint": CONFIG_B}, "other-config"),
        ({"operating_region_fingerprint": REGION_B}, "other-region"),
        ({"plant_id": "plant-b"}, "other-plant"),
    ],
)
def test_history_known_identities_never_leak_neighbors(tmp_path, updates, expected):
    result = _build(tmp_path).query(_request(**updates))

    assert [item.record_id for item in result.records] == [expected]
    assert all(
        item.plant_id == result.request_identity["plant_id"]
        and item.configuration_fingerprint
        == result.request_identity["configuration_fingerprint"]
        and item.operating_region_fingerprint
        == result.request_identity["operating_region_fingerprint"]
        for item in result.records
    )


def test_history_type_filter_and_as_of_exclude_stale_records(tmp_path):
    index = _build(tmp_path)

    current = index.query(_request(record_types=("performance_baseline",)))
    historical = index.query(
        _request(
            record_types=("performance_baseline",),
            as_of="2026-01-20T00:00:00Z",
        )
    )

    assert [item.record_id for item in current.records] == ["baseline-v2"]
    assert [item.record_id for item in historical.records] == ["baseline-v1"]

    empty = index.query(_request(record_types=("equipment_manual",)))
    assert empty.records == ()
    assert empty.empty_reason == "no_active_records"


@pytest.mark.parametrize("mutation", ["cycle", "cross_identity", "payload_hash"])
def test_history_rejects_invalid_supersedes_and_hashes(tmp_path, mutation):
    source = tmp_path / "records.json"
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    records = {item["record_id"]: item for item in payload["records"]}
    if mutation == "cycle":
        records["baseline-v1"]["supersedes"] = ["baseline-v2"]
    elif mutation == "cross_identity":
        records["baseline-v2"]["supersedes"] = ["other-config"]
    else:
        records["rollback-a"]["payload_sha256"] = "0" * 64
    source.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError):
        build_history_index(
            source,
            tmp_path / "index",
            encoder=HistoryKeywordEncoder(),
        )


def test_history_ranking_never_expands_beyond_exact_identity(tmp_path):
    index = _build(tmp_path)

    by_time = index.query(_request())
    by_query = index.query(_request(query_text="rollback degraded"))

    assert [item.record_id for item in by_time.records] == [
        "malicious-a",
        "rollback-a",
        "baseline-v2",
    ]
    assert by_query.records[0].record_id == "rollback-a"
    assert all(item.plant_id == "plant-a" for item in by_query.records)
    assert all(item.configuration_fingerprint == CONFIG_A for item in by_query.records)
    assert all(
        item.operating_region_fingerprint == REGION_A for item in by_query.records
    )


def test_history_query_is_read_only_and_never_exposes_payload_or_changes_kernel(
    tmp_path,
):
    index = _build(tmp_path)
    service = WorkflowService(tmp_path / "sessions")
    session = service.start(
        {
            "description": "A separate Kernel task",
            "measured_signals": ["y"],
            "control_input": "u",
        }
    )
    before_session = session.to_dict()
    before_files = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in index.snapshot.iterdir()
        if path.is_file()
    }

    result = index.query(_request(record_types=("maintenance_record",)))
    serialized = json.dumps(result.model_dump(), ensure_ascii=False)
    after_files = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in index.snapshot.iterdir()
        if path.is_file()
    }

    assert [item.record_id for item in result.records] == ["malicious-a"]
    assert "os.system" not in serialized
    assert "subprocess" not in serialized
    assert "/tmp/attack.py" not in serialized
    assert "file:///etc/passwd" not in serialized
    database = (index.snapshot / "metadata.sqlite3").read_bytes()
    assert b"os.system" not in database
    assert b"subprocess" not in database
    assert b"/tmp/attack.py" not in database
    assert b"file:///etc/passwd" not in database
    assert session.to_dict() == before_session
    assert after_files == before_files


def test_history_is_not_imported_or_injected_by_agents():
    root = Path(__file__).parents[1]

    for relative_path in ("cfdc/agents.py", "cfdc/kernel/agents.py"):
        text = (root / relative_path).read_text(encoding="utf-8")
        assert "cfdc.history" not in text
        assert "OperationalHistory" not in text


def test_history_snapshots_are_immutable_and_reloadable(tmp_path):
    first = _build(tmp_path)
    before = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in first.snapshot.iterdir()
        if path.is_file()
    }
    second = _build(tmp_path)
    reloaded = load_history_index(
        tmp_path / "history-index",
        snapshot_name=first.index_snapshot,
        encoder=HistoryKeywordEncoder(),
    )

    assert first.index_snapshot != second.index_snapshot
    assert before == {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in first.snapshot.iterdir()
        if path.is_file()
    }
    assert reloaded.index_snapshot == first.index_snapshot
    assert reloaded.query(_request()).records


def test_history_rejects_corrupt_snapshot(tmp_path):
    index = _build(tmp_path)
    with (index.snapshot / "vectors.npy").open("ab") as handle:
        handle.write(b"corrupt")

    with pytest.raises(ValueError, match="checksum mismatch"):
        load_history_index(
            tmp_path / "history-index",
            snapshot_name=index.index_snapshot,
            load_encoder=False,
        )


def test_history_schema_is_packaged_and_fixture_remains_synthetic():
    from importlib.resources import files

    schema = files("cfdc.history").joinpath(
        "resources", "operational_history_schema.json"
    )
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))

    assert schema.is_file()
    assert payload["records"]
    assert RECORD_TYPES == {
        "equipment_manual",
        "feature_artifact",
        "controller_freeze",
        "qualification_report",
        "performance_baseline",
        "adaptation_episode",
        "degradation_event",
        "rollback_report",
        "maintenance_record",
    }
    assert all(
        all(ref.startswith("session-synthetic-") for ref in item["session_refs"])
        for item in payload["records"]
    )


def test_history_cli_inspect_and_query_without_encoder(tmp_path):
    index = _build(tmp_path)
    root = Path(__file__).parents[1]
    base = [sys.executable, "-m", "cfdc.history"]

    inspected = subprocess.run(
        [*base, "inspect", "--index-dir", str(tmp_path / "history-index")],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    queried = subprocess.run(
        [
            *base,
            "query",
            "--index-dir",
            str(tmp_path / "history-index"),
            "--plant-id",
            "plant-a",
            "--configuration-fingerprint",
            CONFIG_A,
            "--operating-region-fingerprint",
            REGION_A,
            "--record-type",
            "rollback_report",
            "--as-of",
            "2026-09-03T00:00:00Z",
        ],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )

    assert json.loads(inspected.stdout)["snapshot"] == index.index_snapshot
    payload = json.loads(queried.stdout)
    assert [item["record_id"] for item in payload["records"]] == ["rollback-a"]
    assert "payload" not in payload["records"][0]
