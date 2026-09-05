"""Measure real loopback HTTP responses using a reproducible 50 MiB session.

Run from the repository root with ``uv run --locked python scripts/benchmark_web_api.py``.
Use --serve-directory and --port to leave the generated sample available for
manual browser checks; the default benchmark uses only a temporary directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import socket
import statistics
import sys
import tempfile
import threading
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import uvicorn

from cfdc.web.api import create_app
from cfdc.web.service import start_kernel_case_run


def sample(directory: Path) -> tuple[str, Path]:
    report, _ = start_kernel_case_run(
        "tclab_single_heater_v1", session_dir=directory, use_rag=False
    )
    task_id = report["session_id"]
    path = directory / f"{task_id}.json"
    document = json.loads(path.read_text())
    document["agent_records"] = [{"kind": "synthetic", "source_text": "x" * 1024}] * (
        50 * 1024
    )
    path.write_text(json.dumps(document))
    assert path.stat().st_size >= 50 * 1024 * 1024
    return task_id, path


def measure(directory: Path) -> dict:
    task_id, path = sample(directory / "sessions")
    source_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    app = create_app(
        session_dir=path.parent,
        runtime_dir=directory / "web",
        prepare_rag=False,
    )
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
        server = uvicorn.Server(
            uvicorn.Config(app, log_level="error", access_log=False)
        )
        thread = threading.Thread(
            target=server.run, kwargs={"sockets": [listener]}, daemon=True
        )
        thread.start()
        try:
            deadline = time.monotonic() + 15
            while not server.started:
                if time.monotonic() > deadline:
                    raise RuntimeError("benchmark_server_start_timeout")
                time.sleep(0.01)
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            base = f"http://127.0.0.1:{port}/api/v1/tasks/{task_id}"

            def get(suffix: str = "") -> bytes:
                with opener.open(base + suffix, timeout=30) as response:
                    assert response.status == 200
                    return response.read()

            results = {"source_bytes": path.stat().st_size, "samples": 20}
            for name, suffix in (
                ("summary", ""),
                ("node", "/artifacts/agent_records/node?offset=40000&limit=50"),
            ):
                cold_started = time.perf_counter()
                body = get(suffix)
                cold = time.perf_counter() - cold_started
                durations = []
                for _ in range(20):
                    started = time.perf_counter()
                    body = get(suffix)
                    durations.append(time.perf_counter() - started)
                p95 = statistics.quantiles(durations, n=20)[18]
                assert len(body) <= 256 * 1024 and p95 <= 1
                results[name] = {
                    "bytes": len(body),
                    "first_s": cold,
                    "warm_p95_s": p95,
                }
            full = get("/downloads/artifact?artifact_id=agent_records")
            downloaded = json.loads(full)
            original = json.loads(path.read_text())["agent_records"]
            assert downloaded == original
            assert hashlib.sha256(path.read_bytes()).hexdigest() == source_hash
            results["full_download_bytes"] = len(full)
            results["full_download_matches_source"] = True
            results["source_sha256_unchanged"] = source_hash
            return results
        finally:
            server.should_exit = True
            thread.join(timeout=10)
            assert not thread.is_alive(), "benchmark_server_stop_timeout"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serve-directory", type=Path)
    parser.add_argument("--port", type=int, default=7864)
    args = parser.parse_args()
    if args.serve_directory:
        directory = args.serve_directory.resolve()
        task_id, path = sample(directory / "sessions")
        print(
            json.dumps(
                {
                    "url": f"http://127.0.0.1:{args.port}/tasks/{task_id}",
                    "source_bytes": path.stat().st_size,
                }
            ),
            flush=True,
        )
        uvicorn.run(
            create_app(
                session_dir=path.parent,
                runtime_dir=directory / "web",
                prepare_rag=False,
            ),
            host="127.0.0.1",
            port=args.port,
            access_log=False,
        )
    else:
        with tempfile.TemporaryDirectory(prefix="cfdc-http-benchmark-") as tmp:
            print(json.dumps(measure(Path(tmp)), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
