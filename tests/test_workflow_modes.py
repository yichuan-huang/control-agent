from cfdc.diagnosis.llm import DeterministicDiagnosticAdapter
from cfdc.runtime import run_cfdc_route


def test_llm_adapter_and_builtin_route_share_simulation_pipeline():
    report = run_cfdc_route("cartpole", diagnostic_adapter=DeterministicDiagnosticAdapter(), include_trajectory=False)
    assert report.status == "completed"
    assert report.evidence_boundary == "software_simulation_only"
    assert report.experiment_results
    assert report.features
    assert report.controller is not None
    assert report.semantic_selection.simulation_profile_id == "underactuated_cartpole"


def test_internal_experiment_records_are_repeated_and_hashed():
    report = run_cfdc_route("generic", include_trajectory=False)
    assert {record.repeat_index for record in report.experiment_results} == {1, 2, 3}
    assert all(record.evidence_boundary == "software_simulation_only" for record in report.experiment_results)
    assert all(feature.trace_sha256 and len(feature.trace_sha256) == 64 for feature in report.features)
