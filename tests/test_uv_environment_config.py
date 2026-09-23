import json
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_project_metadata() -> dict:
    with (ROOT / "pyproject.toml").open("rb") as handle:
        return tomllib.load(handle)


def test_project_uses_uv_managed_python_and_dev_dependency_group():
    metadata = load_project_metadata()

    assert (ROOT / ".python-version").read_text(encoding="utf-8") == "3.12\n"
    assert metadata["tool"]["uv"]["python-preference"] == "only-managed"
    assert metadata["dependency-groups"]["dev"] == [
        "pytest>=8.0,<10",
        "ruff>=0.16,<0.17",
    ]
    assert "test" not in metadata["project"].get("optional-dependencies", {})


def test_python_uses_uv_lock_and_frontend_has_its_own_pnpm_lock():
    assert (ROOT / "uv.lock").is_file()
    assert not (ROOT / "requirements.txt").exists()
    frontend = ROOT / "cfdc/web/frontend"
    assert (frontend / "pnpm-lock.yaml").is_file()
    assert not (frontend / "package-lock.json").exists()
    package = json.loads((frontend / "package.json").read_text(encoding="utf-8"))
    assert package["packageManager"] == "pnpm@12.4.1"
    assert package["engines"]["node"] == ">=24.21.0 <25"
    assert (ROOT / ".nvmrc").read_text(encoding="utf-8") == "24.21.0\n"


def test_docs_and_ci_use_docker_for_project_checks():
    readmes = [ROOT / "README.md", ROOT / "README_CN.md"]
    for path in readmes:
        text = path.read_text(encoding="utf-8")
        assert "docker compose up --build -d app" in text
        assert "docker compose --profile checks run --build --rm python-check" in text
        assert "docker compose --profile checks run --build --rm frontend-check" in text
        assert not re.search(r"(?m)^(?:uv|node|pnpm) ", text)
        assert "conda create" not in text
        assert "conda activate" not in text
        assert "pip install" not in text
        assert ".[test]" not in text
        assert "requirements.txt" not in text

    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert 'python-version: ["3.11", "3.12", "3.13"]' in ci
    assert "CFDC_PYTHON_VERSION: ${{ matrix.python-version }}" in ci
    assert "docker compose --profile checks run --build --rm python-check" in ci
    assert "docker compose --profile checks run --build --rm frontend-check" in ci
    assert "docker compose build app" in ci
    assert not re.search(r"(?m)\s+- run: (?:uv|pnpm|node) ", ci)

    check = (ROOT / "scripts/check_container.sh").read_text(encoding="utf-8")
    for command in (
        "uv lock --check",
        "uv sync --locked",
        "uv run --locked ruff format --check .",
        "uv run --locked ruff check .",
        "uv run --locked pytest -q",
        "uv run --locked pytest -q tests/test_main_cli.py",
        "pnpm install --frozen-lockfile",
        "pnpm run test:e2e",
    ):
        assert command in check


def test_readmes_build_before_web_start_and_cli():
    for path in [ROOT / "README.md", ROOT / "README_CN.md"]:
        text = path.read_text(encoding="utf-8")
        build = text.index("docker compose up --build -d app")
        web_start = text.index("docker compose up -d app")
        cli_usage = text.index("--kernel-session-dir ./output/kernel-sessions")
        assert build < web_start < cli_usage


def test_frontend_docs_and_ci_use_frozen_pnpm_inside_docker():
    paths = [
        ROOT / "README.md",
        ROOT / "README_CN.md",
        ROOT / "AGENTS.md",
        ROOT / "cfdc/web/frontend/README.md",
        ROOT / "simulations/README_CN.md",
    ]
    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert "docker compose" in text
        assert not re.search(r"(?m)^(?:uv|node|pnpm) ", text)

    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "node:24.21.0-bookworm-slim" in dockerfile
    assert "corepack prepare pnpm@12.4.1 --activate" in dockerfile
    assert "pnpm --dir cfdc/web/frontend install --frozen-lockfile" in dockerfile
    assert "COPY --from=frontend-build /root/.cache/node/corepack" in dockerfile
    assert "pnpm exec playwright install --with-deps chromium" in dockerfile
    compose = (ROOT / "compose.yaml").read_text(encoding="utf-8")
    assert "127.0.0.1:${CFDC_PORT:-7860}:7860" in compose
    assert "cfdc-data:/app/output" in compose
    assert "cfdc-hf-cache:/home/cfdc/.cache/huggingface" in compose


def test_release_version_matches_frontend_and_public_api():
    version = load_project_metadata()["project"]["version"]
    assert version == "0.3.12"
    package = json.loads(
        (ROOT / "cfdc/web/frontend/package.json").read_text(encoding="utf-8")
    )
    openapi = json.loads(
        (ROOT / "cfdc/web/frontend/openapi.json").read_text(encoding="utf-8")
    )
    assert package["version"] == openapi["info"]["version"] == version
