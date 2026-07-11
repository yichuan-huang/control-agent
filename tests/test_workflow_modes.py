import pytest

from cfdc.diagnosis.llm import DeterministicDiagnosticAdapter
from cfdc.models import DataProvenance, WorkflowMode
from cfdc.runtime import run_cfdc_route
from cfdc.workflow import resolve_workflow_mode


def test_adapter_free_route_defaults_to_simulation_mode():
    assert resolve_workflow_mode(None, None) == WorkflowMode.SIMULATION

    report = run_cfdc_route("cartpole", include_trajectory=False)

    assert report.workflow_mode == WorkflowMode.SIMULATION


def test_diagnostic_adapter_defaults_to_real_mode_without_synthetic_fallback():
    adapter = DeterministicDiagnosticAdapter()

    assert resolve_workflow_mode(None, adapter) == WorkflowMode.REAL

    report = run_cfdc_route(
        "cartpole",
        diagnostic_adapter=adapter,
        include_trajectory=False,
    )

    assert report.workflow_mode == WorkflowMode.REAL
    assert report.status == "experiments_required"
    assert report.experiment_results == []
    assert report.features == []
    assert report.controller is None
    assert report.cartpole_simulation is None


def test_explicit_simulation_mode_rejects_diagnostic_adapter():
    with pytest.raises(ValueError, match="diagnostic adapter.*simulation"):
        run_cfdc_route(
            "cartpole",
            diagnostic_adapter=DeterministicDiagnosticAdapter(),
            workflow_mode=WorkflowMode.SIMULATION,
        )


@pytest.mark.parametrize("route_id", ["cartpole", "vtol-hover"])
def test_simulation_fixtures_and_extracted_features_are_labeled_synthetic(route_id):
    report = run_cfdc_route(
        route_id,
        workflow_mode=WorkflowMode.SIMULATION,
        include_trajectory=False,
    )

    assert report.experiment_results
    assert report.features
    assert {
        result.provenance for result in report.experiment_results
    } == {DataProvenance.SYNTHETIC_FIXTURE}
    assert {
        feature.provenance for feature in report.features
    } == {DataProvenance.SYNTHETIC_FIXTURE}
