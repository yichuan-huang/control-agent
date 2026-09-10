from __future__ import annotations

import importlib.util
from pathlib import Path

from cfdc import sim

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def test_only_raw_control_problem_dataset_remains() -> None:
    assert not (REPOSITORY_ROOT / "cfdc" / "cases").exists()
    assert (REPOSITORY_ROOT / "dataset" / "control_problems.md").is_file()
    assert (REPOSITORY_ROOT / "dataset" / "control_problem_prompts.md").is_file()
    assert (REPOSITORY_ROOT / "dataset" / "control_problem_prompts_cn.md").is_file()


def test_standalone_lab_modules_are_removed() -> None:
    assert importlib.util.find_spec("cfdc.web.lab_ui") is None
    assert importlib.util.find_spec("cfdc.web.lab_service") is None
    assert importlib.util.find_spec("cfdc.web.lab_presentation") is None


def test_production_code_does_not_reference_removed_assets() -> None:
    forbidden = (
        "cfdc.cases",
        "benchmark_case_id",
        "benchmark_fixture",
        "demo:mimo_2x2",
        "MIMO_DEMO_FIXTURE",
        "run_mimo_demo_validation",
    )
    for path in (REPOSITORY_ROOT / "cfdc").rglob("*.py"):
        if path.is_relative_to(
            REPOSITORY_ROOT / "cfdc/web/frontend"
        ) or path.is_relative_to(REPOSITORY_ROOT / "cfdc/web/gradio_archive"):
            continue
        text = path.read_text(encoding="utf-8")
        for marker in forbidden:
            assert marker not in text, f"{path} still contains {marker}"


def test_current_package_does_not_expose_retired_simulators():
    for name in (
        "run_benchmark_suite",
        "run_feature_ablation_suite",
        "run_vtol_simulation",
        "simulate_cartpole_energy_swingup",
    ):
        assert not hasattr(sim, name)


def test_active_python_sources_do_not_import_retired_workflows():
    import ast

    forbidden = (
        "cfdc.runtime",
        "cfdc.pipeline",
        "cfdc.demo",
        "cfdc.diagnosis",
        "cfdc.lab",
        "cfdc.workflow",
        "cfdc.online",
        "cfdc.models",
    )
    paths = [REPOSITORY_ROOT / "main.py", REPOSITORY_ROOT / "app.py"]
    paths.extend(
        path
        for path in (REPOSITORY_ROOT / "cfdc").rglob("*.py")
        if "gradio_archive" not in path.parts and "frontend" not in path.parts
    )
    for path in paths:
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            modules = (
                [node.module]
                if isinstance(node, ast.ImportFrom)
                else [alias.name for alias in node.names]
                if isinstance(node, ast.Import)
                else []
            )
            for module in modules:
                assert not module or not any(
                    module == old or module.startswith(old + ".") for old in forbidden
                ), f"{path}: {module}"
