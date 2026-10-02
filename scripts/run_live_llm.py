"""Run explicitly selected live validation inside Docker, redacting child output."""

from __future__ import annotations

import argparse
import json
import os
import selectors
import signal
import subprocess
import time
from pathlib import Path
from urllib.parse import quote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ("CFDC_LLM_BASE_URL", "CFDC_LLM_MODEL", "CFDC_LLM_API_KEY")


def redact_output(text: str, secret: str) -> str:
    if secret:
        variants = {
            secret,
            json.dumps(secret, ensure_ascii=True)[1:-1],
            json.dumps(secret, ensure_ascii=False)[1:-1],
            repr(secret)[1:-1],
            quote(secret, safe=""),
        }
        for value in sorted(variants, key=len, reverse=True):
            text = text.replace(value, "[REDACTED]")
    return text


def run_redacted(
    command: list[str],
    *,
    env: dict[str, str],
    cwd: Path,
    timeout: float,
    max_output_bytes: int = 2 * 1024 * 1024,
) -> int:
    """Buffer raw output only in memory, preserving failures and bounding children."""
    with subprocess.Popen(
        command,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    ) as process:
        output = bytearray()
        stopped = 0
        deadline = time.monotonic() + timeout
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout, selectors.EVENT_READ)
            try:
                while True:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0 or not selector.select(remaining):
                        stopped = 124
                        break
                    chunk = os.read(process.stdout.fileno(), 65536)
                    if not chunk:
                        process.wait(timeout=max(0, deadline - time.monotonic()))
                        break
                    if len(output) + len(chunk) > max_output_bytes:
                        stopped = 125
                        break
                    output.extend(chunk)
            except subprocess.TimeoutExpired:
                stopped = 124
            except KeyboardInterrupt:
                stopped = 130
            finally:
                if stopped:
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    process.wait()
        if stopped:
            # A truncated buffer might contain only part of a credential.
            # Discard it entirely rather than exposing unmatched fragments.
            messages = {
                124: "Live validation timed out; its process group was stopped.",
                125: "Live validation exceeded its output limit; its process group was stopped.",
                130: "Live validation interrupted.",
            }
            print(messages[stopped], flush=True)
            return stopped
    print(
        redact_output(
            output.decode("utf-8", errors="replace"), env.get("CFDC_LLM_API_KEY", "")
        ),
        end="",
        flush=True,
    )
    return process.returncode if process.returncode >= 0 else 128 - process.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("service", "browser", "all", "command"))
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if (args.mode == "command") != bool(args.command):
        parser.error("Only command mode takes an additional command")
    if os.getenv("CFDC_RUN_LIVE_LLM") != "1":
        print("Real API testing requires CFDC_RUN_LIVE_LLM=1.")
        return 2
    missing = [name for name in FIELDS if not os.getenv(name, "").strip()]
    if missing:
        print("Fill the missing .env fields locally: " + ", ".join(missing))
        return 2
    env = dict(os.environ)
    for name in FIELDS:
        env[name] = env[name].strip()
    try:
        address = urlsplit(env["CFDC_LLM_BASE_URL"])
        if (
            address.scheme not in {"http", "https"}
            or not address.hostname
            or address.username
            or address.password
            or address.query
            or address.fragment
        ):
            raise ValueError
    except ValueError:
        print(
            "CFDC_LLM_BASE_URL must be an HTTP(S) API root without embedded credentials, query or fragment."
        )
        return 2
    env.update(OPENAI_LOG="", DEBUG="", PWDEBUG="0", PYTEST_ADDOPTS="")
    frontend = ROOT / "cfdc/web/frontend"
    commands = []
    if args.mode in {"service", "all"}:
        commands.append(
            (
                "service",
                ROOT,
                [
                    "uv",
                    "run",
                    "--locked",
                    "pytest",
                    "-q",
                    "--tb=short",
                    "tests/test_kernel_webui.py::test_live_llm_dc_motor_flow_fails_closed_after_bounded_tuning",
                ],
            )
        )
    if args.mode in {"browser", "all"}:
        env.pop("CFDC_E2E_URL", None)
        commands.append(
            (
                "browser",
                frontend,
                ["pnpm", "run", "test:e2e", "live-llm.spec.ts", "settings.spec.ts"],
            )
        )
    if args.mode == "command":
        commands.append(("command", Path.cwd(), args.command))
    for label, directory, command in commands:
        print(f"Running live {label} validation (credentials hidden).", flush=True)
        try:
            status = run_redacted(command, env=env, cwd=directory, timeout=900)
        except OSError:
            print(
                "Cannot start the validation process. Run this entry in the Docker check image."
            )
            return 2
        if status:
            return status
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
