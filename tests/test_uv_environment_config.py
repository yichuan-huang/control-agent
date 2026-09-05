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


def test_python_uses_uv_lock_and_frontend_has_its_own_npm_lock():
    assert (ROOT / "uv.lock").is_file()
    assert not (ROOT / "requirements.txt").exists()
    assert (ROOT / "cfdc/web/frontend/package-lock.json").is_file()


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
            "uv run --locked python -m compileall -q -x "
            "'(^|/)(frontend|gradio_archive)(/|$)' cfdc tests main.py app.py"
        )
        node_check = text.index("node --version")
        npm_check = text.index("npm --version")
        frontend_install = text.index("npm --prefix cfdc/web/frontend ci")
        frontend_build = text.index("npm --prefix cfdc/web/frontend run build")
        web_start = text.index("uv run python app.py")
        cli_usage = text.index("uv run python main.py --use-llm")

        assert (
            sync
            < compile_check
            < node_check
            < npm_check
            < frontend_install
            < frontend_build
            < web_start
            < cli_usage
        )
