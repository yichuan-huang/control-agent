from dataclasses import replace

import pytest

from cfdc.kernel import WorkflowService
from cfdc.kernel.service import _active_evidence


def resolved(service):
    session = service.start(
        {
            "description": "Hold spectrometer intensity",
            "measured_signals": ["intensity"],
            "control_input": "led_current",
            "reference": 0.5,
            "input_min": -1,
            "input_max": 1,
            "state_stop": 3,
        }
    )
    session = service.confirm_task(
        session.session_id, action_id="confirm", revision=session.revision
    )
    assessments = {
        "open_loop_stability": "stable",
        "nonminimum_phase": "minimum_phase",
        "significant_delay": "not_significant",
        "relative_degree": "low",
        "sensing_actuation_adequacy": "adequate",
        "nonlinearity_strength": "weak",
        "coupling_underactuation": "siso",
        "uncertainty_variation": "small",
    }
    session = service.submit_answer(
        session.session_id,
        action_id="answers",
        revision=session.revision,
        answer={
            key: {
                "status": "known",
                "assessment": value,
                "evidence": value,
                "confidence": 1,
            }
            for key, value in assessments.items()
        },
    )
    return service.advance(
        session.session_id, action_id="route", revision=session.revision
    )


def test_current_custom_task_requires_provider_before_collecting_evidence(tmp_path):
    session = resolved(WorkflowService(tmp_path))
    assert session.pending_actions[0]["action"] == "set_provider"


def test_unbound_history_is_preserved_but_cannot_be_active_evidence(tmp_path):
    session = resolved(WorkflowService(tmp_path))
    evidence = ({"evidence_id": "old", "kind": "experiment"},)
    session = replace(session, evidence=evidence)
    assert _active_evidence(session) == ()
    assert session.evidence == evidence


@pytest.mark.parametrize(
    "action,payload",
    [
        (
            "submit_features",
            {"features": {"static_gain": {"value": 1, "source_evidence_ids": ["old"]}}},
        ),
        ("derive_features", {}),
        ("submit_controller", {"controller": {}}),
        ("qualify_controller", {}),
    ],
)
def test_current_synthesis_steps_reject_missing_protocol_without_mutation(
    tmp_path, action, payload
):
    service = WorkflowService(tmp_path)
    session = resolved(service)
    with pytest.raises(ValueError, match="compiled_protocol_required"):
        getattr(service, action)(
            session.session_id,
            action_id="invalid",
            revision=session.revision,
            **payload,
        )
    assert service.read(session.session_id).to_dict() == session.to_dict()


def test_residual_alias_normalizes_without_discarding_other_features():
    from cfdc.kernel.service import _normalize_feature_aliases

    entry = {"value": 0.02, "source_evidence_ids": ["trace"]}
    assert _normalize_feature_aliases(
        {"low_order_residual": entry, "custom": entry}
    ) == {
        "low_order_residual_index": entry,
        "custom": entry,
    }
    assert _normalize_feature_aliases(
        {"low_order_residual": entry, "low_order_residual_index": entry}
    ) == {
        "low_order_residual_index": entry,
    }


def test_residual_alias_conflict_rejects_instead_of_preferring_one_value():
    from cfdc.kernel.service import _normalize_feature_aliases

    with pytest.raises(ValueError, match="feature_alias_conflict"):
        _normalize_feature_aliases(
            {
                "low_order_residual": {"value": 0.1},
                "low_order_residual_index": {"value": 0.2},
            }
        )


def test_external_public_export_preserves_bindings_without_local_paths(tmp_path):
    import json
    import zipfile

    from test_kernel_external import external_prepared

    from cfdc.kernel.external import prepare_external_run

    service, session = external_prepared(tmp_path)
    session = prepare_external_run(
        service, session.session_id, action_id="download", revision=session.revision
    )
    original = service.read(session.session_id).to_dict()
    bundle = service.export_result_bundle(session.session_id)
    with zipfile.ZipFile(bundle) as archive:
        exported = json.loads(archive.read("session.json"))
    active = exported["external_workflow"]["active_request"]
    assert "package_path" not in active
    assert (
        active["request_fingerprint"]
        == original["external_workflow"]["active_request"]["request_fingerprint"]
    )
    assert service.read(session.session_id).to_dict() == original


def test_current_public_evidence_cannot_impersonate_protocol_upload(tmp_path):
    from cfdc.kernel.external import select_external_source

    service = WorkflowService(tmp_path)
    session = resolved(service)
    session = select_external_source(
        service,
        session.session_id,
        action_id="source",
        revision=session.revision,
        source_kind="software",
    )
    session = service.compile_protocol(
        session.session_id, action_id="compile", revision=session.revision
    )
    with pytest.raises(ValueError, match="protocol_bound_acquisition_required"):
        service.submit_evidence(
            session.session_id,
            action_id="impersonate",
            revision=session.revision,
            evidence={
                "evidence_id": "manual",
                "kind": "observation",
                "source": "model",
                "protocol_fingerprint": session.active_protocol_fingerprint,
                "signal_units": {"time": "s"},
            },
        )
    assert service.read(session.session_id).evidence == ()


def test_invalid_evidence_disqualifies_numerically_stable_tuning_results():
    from cfdc.kernel.service import _evaluation_hard_failure

    assert _evaluation_hard_failure(
        {"stability_gate": {"passed": True}, "evidence_gate": {"passed": False}}
    )
    assert not _evaluation_hard_failure(
        {"stability_gate": {"passed": True}, "evidence_gate": {"passed": True}}
    )


def test_matching_old_evidence_is_not_retroactively_approved_by_a_new_protocol(
    tmp_path,
):
    session = resolved(WorkflowService(tmp_path))
    unbound = {
        "evidence_id": "old",
        "protocol_fingerprint": "future-protocol",
        "kind": "experiment",
    }
    later = replace(
        session,
        evidence=(unbound,),
        protocols=({"protocol_fingerprint": "future-protocol"},),
        active_protocol_fingerprint="future-protocol",
    )
    assert _active_evidence(later) == ()
    assert later.evidence == (unbound,)
