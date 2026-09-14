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


def test_docs_and_ci_publish_only_uv_workflow():
    readmes = [ROOT / "README.md", ROOT / "README_CN.md"]
    for path in readmes:
        text = path.read_text(encoding="utf-8")
        assert "uv sync" in text
        assert "uv run --locked pytest -q" in text
        assert "uv run pytest -q" not in text
        assert "conda create" not in text
        assert "conda activate" not in text
        assert "pip install" not in text
        assert ".[test]" not in text
        assert "requirements.txt" not in text

    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "astral-sh/setup-uv@" in ci
    assert "python-version: ${{ matrix.python-version }}" in ci
    assert "enable-cache: true" in ci
    assert "uv lock --check" in ci
    assert "uv sync --locked" in ci
    assert "uv run --locked pytest -q" in ci
    assert "actions/setup-python" not in ci
    assert "pip install" not in ci
    assert ".[test]" not in ci


def test_readmes_install_and_check_before_web_start_and_cli():
    for path in [ROOT / "README.md", ROOT / "README_CN.md"]:
        text = path.read_text(encoding="utf-8")
        sync = text.index("uv sync --locked")
        compile_check = text.index(
            "uv run --locked python -m compileall -q cfdc tests main.py app.py"
        )
        node_check = text.index("node --version")
        pnpm_check = text.index("pnpm --version")
        frontend_install = text.index(
            "pnpm --dir cfdc/web/frontend install --frozen-lockfile"
        )
        frontend_build = text.index("pnpm --dir cfdc/web/frontend run build")
        web_start = text.index("uv run --locked python app.py")
        cli_usage = text.index("--kernel-session-dir ./output/kernel-sessions")

        assert (
            sync
            < compile_check
            < node_check
            < pnpm_check
            < frontend_install
            < frontend_build
            < web_start
            < cli_usage
        )


def test_frontend_docs_and_ci_use_frozen_pnpm_workflow():
    paths = [
        ROOT / "README.md",
        ROOT / "README_CN.md",
        ROOT / "AGENTS.md",
        ROOT / "cfdc/web/frontend/README.md",
        ROOT / "simulations/README_CN.md",
    ]
    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert "pnpm 12.4.1" in text
        assert "22.13" in text
        assert not re.search(r"\b(?:npm|npx)\b", text)

    for path in [ROOT / "README.md", ROOT / "README_CN.md"]:
        text = path.read_text(encoding="utf-8")
        assert "PNPM_VERSION=12.4.1" in text
        assert "https://pnpm.io/installation" in text

    ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "cache: pnpm" in ci
    assert "cache-dependency-path: cfdc/web/frontend/pnpm-lock.yaml" in ci
    assert not re.search(r"\b(?:npm|npx)\b", ci)
    steps = [
        "pnpm --dir cfdc/web/frontend install --frozen-lockfile",
        "pnpm --dir cfdc/web/frontend run format:check",
        "pnpm --dir cfdc/web/frontend run typecheck",
        "pnpm --dir cfdc/web/frontend run lint",
        "pnpm --dir cfdc/web/frontend run test",
        "pnpm --dir cfdc/web/frontend run build",
        "pnpm exec playwright install --with-deps chromium",
        "pnpm --dir cfdc/web/frontend run test:e2e",
    ]
    positions = [ci.index(step) for step in steps]
    assert positions == sorted(positions)
