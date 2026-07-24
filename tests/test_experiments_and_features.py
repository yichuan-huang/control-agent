import math

import numpy as np
import pytest

from cfdc.diagnosis import DiagnosticEngine
from cfdc.experiments import plan_safe_experiments
from cfdc.features import (
    estimate_damping_ratio,
    estimate_hover_thrust,
    estimate_natural_frequency,
    estimate_pulse_input_gain,
    estimate_step_features,
    extract_features_from_repeated_results,
    extract_features_from_result,
)
from cfdc.models import (
    CoreFeatureArtifact,
    ExperimentPrimitive,
    ExperimentTrace,
    SimulationExperimentRecord,
    SystemDescription,
)
from cfdc.pipeline import run_cfdc_pipeline
from cfdc.workflow import (
    apply_profile_to_classification,
    default_simulation_profile_catalog,
    deterministic_profile_selection,
    validate_semantic_selection,
)


def feature(fid, value):
    width = max(abs(value) * 0.05, 1e-6)
    return CoreFeatureArtifact(
        feature_id=fid,
        value=value,
        lower_bound=value - width,
        upper_bound=value + width,
        confidence=0.85,
        units="unit",
        method="test",
        source_experiment=ExperimentPrimitive.PULSE,
    )


def test_experiment_steps_are_operator_facing():
    engine = DiagnosticEngine()
    diagnosis = engine.diagnose(
        SystemDescription(
            text="A spring-like system vibrates and its free motion decays.",
            observed_outputs=["position"],
            actuators=["small force"],
        )
    )
    classification = engine.classify(diagnosis)
    catalog = default_simulation_profile_catalog()
    selection = deterministic_profile_selection(
        SystemDescription(text="unused"), diagnosis, classification, catalog
    )
    profile = validate_semantic_selection(selection, classification, catalog)
    classification = apply_profile_to_classification(classification, profile)
    plan = plan_safe_experiments(diagnosis, classification)
    forbidden = {
        "controller",
        "gain",
        "feedback",
        "pole",
        "zero",
        "bandwidth",
        "relative degree",
    }
    step_text = " ".join(
        step for item in plan.instructions for step in item.operator_steps
    ).lower()
    assert not (forbidden & set(step_text.replace("-", " ").split()))


def test_inverse_response_class_iv_plan_covers_required_features():
    engine = DiagnosticEngine()
    diagnosis = engine.diagnose(
        SystemDescription(
            text="A stable self-regulating process settles after a valve change, but the output first moves in the opposite direction before going to the target.",
            observed_outputs=["process output"],
            actuators=["valve setting"],
        )
    )
    classification = engine.classify(diagnosis)
    catalog = default_simulation_profile_catalog()
    selection = deterministic_profile_selection(
        SystemDescription(text="unused"), diagnosis, classification, catalog
    )
    profile = validate_semantic_selection(selection, classification, catalog)
    classification = apply_profile_to_classification(classification, profile)
    plan = plan_safe_experiments(diagnosis, classification)
    estimates = {
        feature
        for instruction in plan.instructions
        for feature in instruction.estimates
    }
    assert set(classification.required_core_features).issubset(estimates)
    assert estimates == {"static_gain", "time_constant", "inverse_response_severity"}
    assert plan.instructions[0].primitive == "ramp_step"


def test_natural_frequency_estimator_on_decaying_sine():
    omega = 4.0
    t = np.linspace(0.0, 8.0, 2000)
    y = np.exp(-0.08 * t) * np.cos(omega * t)
    feature = estimate_natural_frequency(t, y, bandwidth_hz=0.05)
    assert feature.feature_id == "natural_frequency"
    assert math.isclose(feature.value, omega, rel_tol=0.04)
    assert feature.lower_bound <= feature.value <= feature.upper_bound


def test_modal_estimators_are_stable_with_measurement_noise():
    rng = np.random.default_rng(7)
    omega = 4.0
    damping = 0.08
    t = np.linspace(0.0, 10.0, 2500)
    clean = np.exp(-damping * omega * t) * np.cos(omega * t)
    noisy = clean + rng.normal(0.0, 0.008, size=t.size)

    frequency = estimate_natural_frequency(t, noisy, bandwidth_hz=0.05)
    damping_ratio = estimate_damping_ratio(t, noisy)

    assert math.isclose(frequency.value, omega, rel_tol=0.05)
    assert math.isclose(damping_ratio.value, damping, rel_tol=0.30)


def test_step_feature_estimator_gain_and_time_constant():
    gain = 2.0
    tau = 3.0
    t = np.linspace(0.0, 30.0, 1500)
    u = np.zeros_like(t)
    u[t >= 1.0] = 0.5
    y = gain * 0.5 * (1.0 - np.exp(-np.maximum(0.0, t - 1.0) / tau))
    features = {
        feature.feature_id: feature for feature in estimate_step_features(t, u, y)
    }
    assert math.isclose(features["static_gain"].value, gain, rel_tol=0.05)
    assert math.isclose(features["time_constant"].value, tau, rel_tol=0.08)


def test_pulse_integration_estimates_input_gain():
    t = np.linspace(0.0, 2.0, 500)
    u = np.zeros_like(t)
    u[(t >= 0.2) & (t <= 0.4)] = 0.3
    u[(t >= 1.0) & (t <= 1.2)] = -0.3
    acceleration = 1.7 * u
    feature = estimate_pulse_input_gain(t, u, acceleration)
    assert math.isclose(feature.value, 1.7, rel_tol=0.02)


def test_hover_thrust_estimator_uses_liftoff_threshold():
    hover = 12.0
    t = np.linspace(0.0, 8.0, 800)
    thrust = np.clip(hover * t / 5.0, 0.0, 1.2 * hover)
    lift = (thrust >= hover).astype(float)
    feature = estimate_hover_thrust(t, thrust, lift)
    assert math.isclose(feature.value, hover, rel_tol=0.03)


def test_experiment_trace_rejects_mismatched_signal_lengths():
    try:
        ExperimentTrace(time_s=[0.0, 1.0, 2.0], signals={"output": [0.0, 1.0]})
    except ValueError:
        return
    raise AssertionError("mismatched experiment trace was accepted")


def test_inconsistent_repeated_mimo_matrices_are_not_silently_averaged(monkeypatch):
    records = [
        SimulationExperimentRecord(
            primitive="bounded_scan",
            estimates=["local_gain_matrix"],
            repeat_index=index,
            operating_region="nominal",
            trace=ExperimentTrace(
                time_s=[0.0, 1.0, 2.0],
                signals={"output": [0.0, 0.0, 0.0]},
            ),
        )
        for index in range(1, 4)
    ]
    matrices = {
        1: [[2.0, 0.4], [0.3, 1.5]],
        2: [[2.1, 0.42], [0.28, 1.55]],
        3: [[8.0, 3.0], [2.5, 6.0]],
    }

    def fake_extract(record):
        return [
            CoreFeatureArtifact(
                feature_id="local_gain_matrix",
                value=matrices[record.repeat_index],
                confidence=0.9,
                units="output/input",
                method="test matrix",
                source_experiment="bounded_scan",
                operating_region="nominal",
            )
        ]

    monkeypatch.setattr(
        "cfdc.features.dispatcher.extract_features_from_result",
        fake_extract,
    )

    with pytest.raises(ValueError, match="inconsistent local gain matrices"):
        extract_features_from_repeated_results(records)


def test_free_decay_dispatcher_returns_frequency_and_damping():
    omega = 5.0
    damping = 0.12
    t = np.linspace(0.0, 10.0, 2500)
    y = np.exp(-damping * omega * t) * np.cos(omega * t)
    result = SimulationExperimentRecord(
        primitive="free_decay",
        estimates=["natural_frequency", "damping_ratio"],
        trace=ExperimentTrace(
            time_s=t.tolist(), signals={"measured position or angle": y.tolist()}
        ),
    )
    features = {
        feature.feature_id: feature for feature in extract_features_from_result(result)
    }
    assert math.isclose(features["natural_frequency"].value, omega, rel_tol=0.04)
    assert math.isclose(features["damping_ratio"].value, damping, rel_tol=0.25)


def test_ramp_step_dispatcher_returns_requested_features():
    gain = 1.4
    tau = 4.0
    t = np.linspace(0.0, 40.0, 1600)
    u = np.zeros_like(t)
    u[t >= 1.5] = 0.5
    y = gain * 0.5 * (1.0 - np.exp(-np.maximum(0.0, t - 1.5) / tau))
    y -= 0.15 * gain * 0.5 * np.exp(-np.maximum(0.0, t - 1.5) / 0.6)
    y[t < 1.5] = 0.0
    result = SimulationExperimentRecord(
        primitive="ramp_step",
        estimates=["static_gain", "time_constant", "inverse_response_severity"],
        trace=ExperimentTrace(
            time_s=t.tolist(),
            signals={"input setting": u.tolist(), "measured output": y.tolist()},
        ),
    )
    features = {
        feature.feature_id: feature for feature in extract_features_from_result(result)
    }
    assert set(features) == {
        "static_gain",
        "time_constant",
        "inverse_response_severity",
    }
    assert math.isclose(features["static_gain"].value, gain, rel_tol=0.08)
    assert math.isclose(features["time_constant"].value, tau, rel_tol=0.12)
    assert features["inverse_response_severity"].value > 0.05


def test_pulse_dispatcher_returns_input_and_vtol_coupling_features():
    t = np.linspace(0.0, 3.0, 900)
    command = np.zeros_like(t)
    command[(t >= 0.4) & (t <= 0.6)] = 0.4
    command[(t >= 1.6) & (t <= 1.8)] = -0.4
    angular_acceleration = 20.0 * command
    tilt = 0.04 * command
    lateral_acceleration = -9.81 * tilt

    angular_result = SimulationExperimentRecord(
        primitive="pulse",
        estimates=["angular_acceleration_gain", "lateral_coupling_gain"],
        trace=ExperimentTrace(
            time_s=t.tolist(),
            signals={
                "twist command": command.tolist(),
                "angular acceleration": angular_acceleration.tolist(),
                "tilt": tilt.tolist(),
                "lateral acceleration": lateral_acceleration.tolist(),
            },
        ),
    )
    features = {
        feature.feature_id: feature
        for feature in extract_features_from_result(angular_result)
    }
    assert math.isclose(features["angular_acceleration_gain"].value, 20.0, rel_tol=0.02)
    assert math.isclose(features["lateral_coupling_gain"].value, -9.81, rel_tol=0.02)


def test_hover_and_bounded_scan_dispatchers_return_scalar_features():
    hover = 11.0
    t = np.linspace(0.0, 8.0, 800)
    thrust = np.clip(hover * t / 5.0, 0.0, 1.2 * hover)
    lift = (thrust >= hover).astype(float)
    hover_result = SimulationExperimentRecord(
        primitive="hover_thrust",
        estimates=["hover_thrust"],
        trace=ExperimentTrace(
            time_s=t.tolist(),
            signals={"lift setting": thrust.tolist(), "vertical motion": lift.tolist()},
        ),
    )
    hover_feature = extract_features_from_result(hover_result)[0]
    assert math.isclose(hover_feature.value, hover, rel_tol=0.03)

    scan_input = np.zeros_like(t)
    scan_input[(t >= 1.0) & (t <= 4.0)] = 0.5
    primary = 2.0 * scan_input
    coupled = 0.4 * primary
    scan_result = SimulationExperimentRecord(
        primitive="bounded_scan",
        estimates=["coupling_gain"],
        trace=ExperimentTrace(
            time_s=t.tolist(),
            signals={
                "input setting": scan_input.tolist(),
                "primary output": primary.tolist(),
                "coupled output": coupled.tolist(),
            },
        ),
    )
    coupling_feature = extract_features_from_result(scan_result)[0]
    assert math.isclose(coupling_feature.value, 0.4, rel_tol=0.02)


def test_pipeline_waits_for_object_specifications_before_experiments_or_controller():
    result = run_cfdc_pipeline(
        SystemDescription(
            text="A first order temperature process settles after a small heater change.",
            observed_outputs=["temperature"],
            actuators=["heater"],
        ),
    )
    assert result["status"] == "awaiting_specifications"
    assert result["experiment_results"] == []
    assert result["features"] == []
    assert result["controller"] is None


def test_pipeline_reports_required_features_without_fabricating_them():
    result = run_cfdc_pipeline(
        SystemDescription(
            text="A first order temperature process settles after a small heater change.",
            observed_outputs=["temperature"],
            actuators=["heater"],
        ),
    )
    assert result["classification"]["required_core_features"] == [
        "static_gain",
        "time_constant",
    ]
    assert result["features"] == []
    assert result["go_no_go"] is None


def test_significant_delay_pipeline_requests_specs_before_measuring_dead_time():
    description = SystemDescription(
        text="A first order temperature process settles after a heater change with noticeable dead time.",
        observed_outputs=["temperature"],
        actuators=["heater"],
    )

    result = run_cfdc_pipeline(
        description,
    )
    assert (
        result["semantic_selection"]["simulation_profile_id"]
        == "first_order_lag_with_delay"
    )
    assert set(result["classification"]["required_core_features"]) == {
        "static_gain",
        "time_constant",
        "dead_time",
    }
    assert result["features"] == []


def test_pipeline_does_not_accept_user_supplied_feature_packets():
    description = SystemDescription(
        text="A first order temperature process settles after a heater change with noticeable dead time.",
        observed_outputs=["temperature"],
        actuators=["heater"],
    )

    import pytest

    with pytest.raises(TypeError, match="features"):
        run_cfdc_pipeline(description, features=[feature("static_gain", 2.0)])
