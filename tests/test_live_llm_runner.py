"""Exercise the live-test boundary without any provider calls or real secrets."""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _launcher(tmp_path):
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    shutil.copyfile(ROOT / "scripts/test_live_llm.sh", scripts / "test_live_llm.sh")
    (tmp_path / "compose.yaml").write_text("services: {}\n")
    binary = tmp_path / "bin"
    binary.mkdir()
    docker = binary / "docker"
    docker.write_text(
        f"#!{sys.executable}\n"
        "import json, os, sys\n"
        "with open(os.environ['CALLS'], 'a') as stream:\n"
        "    stream.write(json.dumps({'args': sys.argv[1:], 'inherited': "
        "{k: v for k, v in os.environ.items() if k.startswith('CFDC_LLM_')}}) + '\\n')\n"
        "sys.exit(int(os.environ.get('DOCKER_EXIT', '0')))\n"
    )
    docker.chmod(0o700)
    env = dict(
        os.environ, PATH=f"{binary}:{os.environ['PATH']}", CALLS=str(tmp_path / "calls")
    )
    env.update(
        {
            name: "stale-host-value"
            for name in ("CFDC_LLM_BASE_URL", "CFDC_LLM_MODEL", "CFDC_LLM_API_KEY")
        }
    )
    return ["bash", str(scripts / "test_live_llm.sh")], env


def test_missing_env_creates_private_template_and_stops_before_docker(tmp_path):
    command, env = _launcher(tmp_path)
    result = subprocess.run(
        [*command, "service"], env=env, capture_output=True, check=False, text=True
    )
    assert result.returncode == 2
    local = tmp_path / ".env"
    assert (
        local.read_text() == "CFDC_LLM_BASE_URL=\nCFDC_LLM_MODEL=\nCFDC_LLM_API_KEY=\n"
    )
    assert local.stat().st_mode & 0o777 == 0o600
    assert "fill" in (result.stdout + result.stderr).lower()
    assert not (tmp_path / "calls").exists()


@pytest.mark.parametrize("mode", ["service", "browser", "all"])
def test_launcher_preserves_file_and_passes_only_names_without_host_overrides(
    tmp_path, mode
):
    command, env = _launcher(tmp_path)
    content = "CFDC_LLM_BASE_URL=https://provider.example/v1\nCFDC_LLM_MODEL=model\nCFDC_LLM_API_KEY='fake-key-$-#'\n"
    local = tmp_path / ".env"
    local.write_text(content)
    result = subprocess.run(
        [*command, mode], env=env, capture_output=True, check=False, text=True
    )
    assert result.returncode == 0
    assert local.read_text() == content
    calls = [json.loads(line) for line in (tmp_path / "calls").read_text().splitlines()]
    invocation = calls[-1]
    assert invocation["inherited"] == {}
    for name in ("CFDC_LLM_BASE_URL", "CFDC_LLM_MODEL", "CFDC_LLM_API_KEY"):
        assert name in invocation["args"]
    assert "--env-file" in invocation["args"]
    assert str(local) in invocation["args"]
    assert invocation["args"][-1] == mode
    assert "fake-key" not in json.dumps(calls) + result.stdout + result.stderr


def test_invalid_mode_has_no_side_effects(tmp_path):
    command, env = _launcher(tmp_path)
    result = subprocess.run(
        [*command, "invalid"], env=env, capture_output=True, check=False
    )
    assert result.returncode == 2
    assert not (tmp_path / ".env").exists()
    assert not (tmp_path / "calls").exists()


def test_compose_config_errors_are_not_echoed_and_do_not_run_tests(tmp_path):
    command, env = _launcher(tmp_path)
    (tmp_path / ".env").write_text("CFDC_LLM_API_KEY='synthetic-broken-key\n")
    docker = tmp_path / "bin/docker"
    docker.write_text(
        "#!/bin/sh\necho 'synthetic-broken-key from parser' >&2\nexit 1\n"
    )
    docker.chmod(0o700)
    result = subprocess.run(
        [*command, "service"], env=env, capture_output=True, check=False, text=True
    )
    assert result.returncode == 2
    assert "synthetic-broken-key" not in result.stdout + result.stderr
    assert "Cannot load" in result.stderr


def _runner():
    spec = importlib.util.spec_from_file_location(
        "live_runner", ROOT / "scripts/run_live_llm.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_missing_live_credentials_cannot_use_openai_fallback():
    env = {
        "CFDC_RUN_LIVE_LLM": "1",
        "CFDC_LLM_API_KEY": "fake-secret",
        "OPENAI_BASE_URL": "https://fallback.example",
        "OPENAI_MODEL": "fallback",
    }
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/run_live_llm.py"), "service"],
        env=env,
        capture_output=True,
        check=False,
        text=True,
    )
    assert result.returncode == 2
    assert "CFDC_LLM_BASE_URL" in result.stdout + result.stderr
    assert "CFDC_LLM_MODEL" in result.stdout + result.stderr
    assert "fake-secret" not in result.stdout + result.stderr


def test_live_runner_requires_opt_in_even_with_credentials():
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/run_live_llm.py"), "service"],
        env={
            "CFDC_LLM_BASE_URL": "https://provider.example",
            "CFDC_LLM_MODEL": "model",
            "CFDC_LLM_API_KEY": "fake-secret",
        },
        capture_output=True,
        check=False,
        text=True,
    )
    assert result.returncode == 2
    assert "CFDC_RUN_LIVE_LLM" in result.stdout + result.stderr


def test_subprocess_redacts_split_and_escaped_secrets_and_preserves_exit(
    tmp_path, capsys
):
    runner = _runner()
    secret = 'fake-"key\\value'
    code = "import os, json, sys; key=os.environ['CFDC_LLM_API_KEY']; sys.stdout.write(key[:4]); sys.stdout.flush(); sys.stdout.write(key[4:]); print(json.dumps(key), file=sys.stderr); sys.exit(7)"
    result = runner.run_redacted(
        [sys.executable, "-c", code],
        env=dict(os.environ, CFDC_LLM_API_KEY=secret),
        cwd=tmp_path,
        timeout=5,
    )
    assert result == 7
    output = capsys.readouterr().out
    assert secret not in output
    assert json.dumps(secret)[1:-1] not in output
    assert "[REDACTED]" in output


def test_subprocess_timeout_fails_without_exposing_credentials(tmp_path, capsys):
    runner = _runner()
    result = runner.run_redacted(
        [
            sys.executable,
            "-c",
            "import os,time; print(os.environ['CFDC_LLM_API_KEY'], flush=True); time.sleep(30)",
        ],
        env=dict(os.environ, CFDC_LLM_API_KEY="fake-timeout-secret"),
        cwd=tmp_path,
        timeout=0.2,
    )
    assert result == 124
    output = capsys.readouterr().out
    assert "fake-timeout-secret" not in output
    assert "timed out" in output.lower()


def test_subprocess_output_overflow_stops_without_spooling_or_printing(
    tmp_path, capsys
):
    runner = _runner()
    result = runner.run_redacted(
        [sys.executable, "-c", "import os; os.write(1, b'x' * 65536)"],
        env=dict(os.environ, CFDC_LLM_API_KEY="fake-secret"),
        cwd=tmp_path,
        timeout=5,
        max_output_bytes=128,
    )
    assert result == 125
    output = capsys.readouterr().out
    assert "output limit" in output.lower()
    assert "x" * 128 not in output
    assert not list(tmp_path.iterdir())
