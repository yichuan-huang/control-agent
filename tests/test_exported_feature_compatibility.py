from copy import deepcopy
from pathlib import Path

import pytest
from test_training_exercise_bundle import _ready_exercise_session

from cfdc.features.kernel import derive_feature_artifact
from cfdc.kernel.contracts import fingerprint
from cfdc.sim.training import build_training_provider_registries


@pytest.fixture
def acquired(tmp_path):
    service, session = _ready_exercise_session(tmp_path)
    registry, provider_id, _, _ = build_training_provider_registries(
        "dc_motor_speed_v1"
    )
    session = service.prepare_training_exercise_bundle(
        session.session_id,
        action_id="bundle",
        revision=session.revision,
        provider_registry=registry,
        provider_id=provider_id,
    )
    session = service.ingest_upload(
        session.session_id,
        action_id="upload",
        revision=session.revision,
        paths=[Path(session.training_exercise_bundles[-1]["bundle_path"])],
    )
    artifact = derive_feature_artifact(session.evidence, session.route).to_dict()
    return service, session, artifact


def resign(artifact):
    artifact.pop("artifact_fingerprint", None)
    artifact["artifact_fingerprint"] = fingerprint(artifact)
    return artifact


@pytest.mark.parametrize("legacy_alias", [False, True])
def test_accepts_exported_full_wrapper_before_alias_normalization(
    acquired, legacy_alias
):
    service, session, artifact = acquired
    artifact = deepcopy(artifact)
    canonical = artifact["features"]["low_order_residual_index"]
    if legacy_alias:
        artifact["features"].pop("low_order_residual_index")
        artifact["features"]["low_order_residual"] = canonical
        resign(artifact)
    original = deepcopy(artifact)
    result = service.submit_features(
        session.session_id,
        action_id="exported",
        revision=session.revision,
        features=artifact,
    )
    assert (
        result.feature_artifact["features"]["low_order_residual_index"]["value"]
        == canonical["value"]
    )
    assert "low_order_residual" not in result.feature_artifact["features"]
    assert result.feature_artifact["source_artifact"] == original
    assert artifact == original


@pytest.mark.parametrize(
    "corruption,error",
    [
        ("tamper", "feature_artifact_fingerprint_mismatch"),
        ("conflict", "feature_alias_conflict"),
        ("unknown", "unknown_feature_id"),
        ("protocol", "feature_protocol_binding_mismatch"),
    ],
)
def test_exported_feature_rejection_preserves_session(acquired, corruption, error):
    service, session, artifact = acquired
    artifact = deepcopy(artifact)
    if corruption == "tamper":
        artifact["quality"]["fit_residual"] = 500
    elif corruption == "conflict":
        artifact["features"]["low_order_residual"] = {
            **artifact["features"]["low_order_residual_index"],
            "value": 999,
        }
        resign(artifact)
    elif corruption == "unknown":
        artifact["features"]["unknown_metric"] = deepcopy(
            next(iter(artifact["features"].values()))
        )
        resign(artifact)
    else:
        artifact["selected_protocol_fingerprint"] = "another-protocol"
        resign(artifact)
    with pytest.raises(ValueError, match=error):
        service.submit_features(
            session.session_id,
            action_id="bad",
            revision=session.revision,
            features=artifact,
        )
    assert service.read(session.session_id).to_dict() == session.to_dict()


def test_web_adapter_preserves_exported_wrapper_for_kernel_validation(acquired):
    from dataclasses import replace

    from cfdc.web.service import continue_kernel_app_run, load_kernel_app_run

    service, session, artifact = acquired
    session = service._save(
        service._append(
            replace(
                session,
                pending_actions=({"kind": "feature", "action": "submit_features"},),
            ),
            "expert_feature_requested",
            "expert-fixture",
            {},
        )
    )
    _, state = load_kernel_app_run(session.session_id, session_dir=service.root)
    tampered = deepcopy(artifact)
    tampered["quality"]["fit_residual"] += 1
    with pytest.raises(ValueError, match="feature_artifact_fingerprint_mismatch"):
        continue_kernel_app_run(state, action="features", payload=tampered)
    assert service.read(session.session_id).to_dict() == session.to_dict()
    report, _ = continue_kernel_app_run(state, action="features", payload=artifact)
    assert report["features"]["source_artifact"] == artifact
