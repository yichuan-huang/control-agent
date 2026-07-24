from __future__ import annotations

import importlib.util
from pathlib import Path

from cfdc import lab, models, sim
from cfdc.lab import SimulationSession, load_model_question_examples

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def test_only_raw_control_problem_dataset_remains() -> None:
    assert not (REPOSITORY_ROOT / "cfdc" / "cases").exists()
    assert (REPOSITORY_ROOT / "dataset" / "control_problems.md").is_file()
    assert (REPOSITORY_ROOT / "dataset" / "control_problem_prompts.md").is_file()
    assert (REPOSITORY_ROOT / "dataset" / "control_problem_prompts_cn.md").is_file()


def test_question_examples_are_a_generic_lab_resource() -> None:
    catalog = load_model_question_examples()
    assert catalog.catalog_version == "v1"
    assert (
        REPOSITORY_ROOT
        / "cfdc"
        / "lab"
        / "resources"
        / "model_question_examples.v1.json"
    ).is_file()


def test_benchmark_and_mimo_demo_public_apis_are_removed() -> None:
    for module, names in (
        (
            lab,
            (
                "create_benchmark_session",
                "create_mimo_demo_session",
            ),
        ),
        (
            models,
            (
                "ControlProblemIR",
                "ControlProblemCatalog",
            ),
        ),
        (
            sim,
            (
                "MIMO_DEMO_FIXTURE",
                "run_mimo_demo_validation",
            ),
        ),
    ):
        for name in names:
            assert not hasattr(module, name)
    assert "benchmark_case_id" not in SimulationSession.model_fields
    assert "demo_fixture_id" not in SimulationSession.model_fields


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
        text = path.read_text(encoding="utf-8")
        for marker in forbidden:
            assert marker not in text, f"{path} still contains {marker}"
