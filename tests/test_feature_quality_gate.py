import math

import numpy as np

from cfdc.controllers import synthesize_controller
from cfdc.features import evaluate_feature_quality, extract_features_from_result
from cfdc.models import (
    ArchetypeClass,
    ArchetypeClassification,
    CoreFeatureArtifact,
    ExperimentPrimitive,
    ExperimentTrace,
    SimulationExperimentRecord,
)


def _classification():
    return ArchetypeClassification(
        primary_class=ArchetypeClass.CLASS_I_FIRST_ORDER_LAG,
        control_architecture="detuned PI",
        required_core_features=["static_gain", "time_constant"],
        rationale="test",
    )


def _feature(
    fid, value, confidence=0.9, lower=None, upper=None, flags=None, trace_sha256=None
):
    width = max(abs(value) * 0.1, 0.1)
    return CoreFeatureArtifact(
        feature_id=fid,
        value=value,
        lower_bound=value - width if lower is None else lower,
        upper_bound=value + width if upper is None else upper,
        confidence=confidence,
        units="unit",
        method="test",
        source_experiment=ExperimentPrimitive.RAMP_STEP,
        data_quality_flags=flags or [],
        trace_sha256=trace_sha256,
    )


def test_quality_gate_repeats_low_confidence_and_refuses_invalid_domain():
    repeat = evaluate_feature_quality(
        _classification(),
        [_feature("static_gain", 2, confidence=0.1), _feature("time_constant", 5)],
    )
    refuse = evaluate_feature_quality(
        _classification(), [_feature("static_gain", 2), _feature("time_constant", -1)]
    )
    assert repeat.decision == "repeat_experiment"
    assert refuse.decision == "refuse"


def test_simulation_record_extraction_attaches_trace_hash():
    t = np.linspace(0, 30, 1500)
    u = np.zeros_like(t)
    u[t >= 1] = 0.5
    y = 1 - np.exp(-np.maximum(0, t - 1) / 3)
    record = SimulationExperimentRecord(
        primitive=ExperimentPrimitive.RAMP_STEP,
        estimates=["static_gain", "time_constant"],
        trace=ExperimentTrace(
            time_s=t.tolist(), signals={"input": u.tolist(), "output": y.tolist()}
        ),
    )
    features = extract_features_from_result(record)
    assert evaluate_feature_quality(_classification(), features).decision == "accept"
    assert len({feature.trace_sha256 for feature in features}) == 1


def test_controller_uses_conservative_bounds():
    features = [
        _feature("static_gain", 2, lower=1, upper=4),
        _feature("time_constant", 5, lower=4, upper=8),
    ]
    controller = synthesize_controller(_classification(), features)
    assert math.isclose(controller.gains["kp"], 0.1 / 4 / (1 + 3))
    assert math.isclose(controller.gains["integral_time"], 40)
