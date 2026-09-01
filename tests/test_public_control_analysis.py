from __future__ import annotations

import copy
import math

import numpy as np
from scipy import signal

from cfdc.controllers.kernel_synthesis import synthesize_controller
from cfdc.controllers.qualification import NOT_QUALIFIED, qualify_controller
from cfdc.features.kernel import derive_feature_artifact
from cfdc.kernel.contracts import fingerprint
from cfdc.kernel.controllers import ControllerIR
from cfdc.kernel.route_catalog import select_route_from_features
from cfdc.sim.execution import OscillatorPlant


def _evidence(
    trace_id: str,
    protocol: str,
    time_s: np.ndarray,
    signals: dict[str, np.ndarray],
    *,
    kind: str,
    measured: tuple[str, ...],
    controls: tuple[str, ...],
    units: dict[str, str] | None = None,
    operating_region: str = "synthetic bounded region",
) -> dict[str, object]:
    trace = {
        "trace_id": trace_id,
        "source": "demo_fixture",
        "time_s": time_s.tolist(),
        "signals": {name: values.tolist() for name, values in signals.items()},
        "units": units
        or {
            **dict.fromkeys(controls, "V"),
            **dict.fromkeys(measured, "m"),
        },
        "protocol_fingerprint": protocol,
        "operating_region": operating_region,
        "trial_id": trace_id,
        "metadata": {
            "experiment_kind": kind,
            "control_inputs": list(controls),
            "measured_signals": list(measured),
        },
        "quality": {"passed": True, "static_gain": 9999.0},
    }
    trace["trace_fingerprint"] = fingerprint(trace)
    return {
        "evidence_id": trace_id,
        "kind": "experiment",
        "source": "demo_fixture",
        "protocol_fingerprint": protocol,
        "signal_units": trace["units"],
        "operating_region": operating_region,
        "trial_id": trace_id,
        "trace": trace,
        "trace_fingerprint": trace["trace_fingerprint"],
        # These are deliberately false numerical claims. Public arrays are the
        # only admissible numerical source.
        "summary": {"static_gain": 9999.0, "damping_ratio": 0.7},
        "quality": {"passed": True, "static_gain": 9999.0},
    }


def _stable_lag_evidence(protocol: str = "protocol-lag") -> list[dict[str, object]]:
    time_s = np.arange(0.0, 14.0, 0.02)
    command = np.where(time_s >= 1.0, 0.8, 0.0)
    nominal = np.where(
        time_s >= 1.0,
        -1.6 * (1.0 - np.exp(-(time_s - 1.0) / 1.5)),
        0.0,
    )
    return [
        _evidence(
            f"lag-repeat-{repeat}",
            protocol,
            time_s,
            {
                "u": command,
                "y": nominal + 0.0005 * np.sin((repeat + 1) * time_s),
            },
            kind="siso_step_pulse_modal",
            measured=("y",),
            controls=("u",),
        )
        for repeat in range(3)
    ]


def _task(*, measured: list[str], controls: list[str]) -> dict[str, object]:
    return {
        "measured_signals": measured,
        "control_inputs": controls,
        "control_input": controls[0],
        "input_min": -5.0,
        "input_max": 5.0,
        "output_min": -4.0,
        "output_max": 4.0,
        "state_stop": 8.0,
        "target_bandwidth_rad_s": 0.25,
    }


def test_public_lag_fit_ignores_summary_and_preserves_signed_gain() -> None:
    artifact = derive_feature_artifact(
        _stable_lag_evidence(),
        {"feature_ids": ["static_gain", "dominant_time_constant"]},
    ).to_dict()

    gain = artifact["features"]["static_gain"]
    tau = artifact["features"]["dominant_time_constant"]
    assert -2.2 < gain["value"] < -1.8
    assert 1.2 < tau["value"] < 1.8
    assert gain["protocol_fingerprint"] == "protocol-lag"
    assert len(gain["source_trace_sha256"]) == 3
    assert gain["uncertainty"]["method"] in {
        "repeat_quantile_95",
        "regression_t_interval_95",
    }
    assert artifact["public_models"][0]["model_type"] == "linear_siso_rational_delay"
    assert artifact["quality"]["passed"] is True


def test_protocol_groups_are_not_median_mixed() -> None:
    other = copy.deepcopy(_stable_lag_evidence("protocol-other"))
    for item in other:
        trace = item["trace"]
        trace["signals"]["y"] = (-3.0 * np.asarray(trace["signals"]["y"])).tolist()
        trace.pop("trace_fingerprint")
        trace["trace_fingerprint"] = fingerprint(trace)
        item["trace_fingerprint"] = trace["trace_fingerprint"]

    artifact = derive_feature_artifact(
        [*_stable_lag_evidence(), *other],
        {"feature_ids": ["static_gain", "dominant_time_constant"]},
    ).to_dict()

    assert len(artifact["analysis_groups"]) == 2
    assert len(artifact["public_models"]) == 2
    assert artifact["features"]["static_gain"]["protocol_fingerprint"] in {
        "protocol-lag",
        "protocol-other",
    }
    assert abs(artifact["features"]["static_gain"]["value"] - 2.0) > 0.5


def test_signed_controller_qualifies_and_sign_wrong_copy_is_rejected() -> None:
    artifact = derive_feature_artifact(
        _stable_lag_evidence(),
        {"feature_ids": ["static_gain", "dominant_time_constant"]},
    ).to_dict()
    task = _task(measured=["y"], controls=["u"])
    route = select_route_from_features(artifact, task)
    controller, audit = synthesize_controller(task, route, artifact)

    assert route["controller_family"] == "PI"
    assert controller.parameters["kp"] < 0.0
    assert controller.parameters["ki"] < 0.0
    assert audit["parameter_provenance"]["kp"]["feature_ids"] == [
        "static_gain",
        "dominant_time_constant",
    ]
    qualification = qualify_controller(
        controller,
        task=task,
        route=route,
        feature_artifact=artifact,
        protocol={"protocol_fingerprint": "protocol-lag"},
    )
    assert qualification["status"] == "offline_qualified"
    assert qualification["validated_region"] == {"y": [-4.0, 4.0]}
    assert qualification["checks"]["actual_runtime_trajectories"] == "pass"

    wrong_parameters = dict(controller.parameters)
    wrong_parameters["kp"] *= -1.0
    wrong_parameters["ki"] *= -1.0
    wrong = ControllerIR(
        family=controller.family,
        measured_signals=controller.measured_signals,
        control_inputs=controller.control_inputs,
        parameters=wrong_parameters,
        parameter_domains={name: (-100.0, 100.0) for name in wrong_parameters},
        output_bounds=controller.output_bounds,
        state_limits=controller.state_limits,
        integral_handling=controller.integral_handling,
    )
    rejected = qualify_controller(
        wrong,
        task=task,
        route=route,
        feature_artifact=artifact,
        protocol={"protocol_fingerprint": "protocol-lag"},
    )
    assert rejected["status"] == NOT_QUALIFIED
    assert rejected["checks"]["signed_feedback"] == "fail"


def _staircase_evidence(*, history: bool = False) -> list[dict[str, object]]:
    dt = 0.04
    dwell = 1.6
    levels = np.array([-1.0, -0.5, 0.0, 0.5, 1.0, 0.5, 0.0, -0.5, -1.0])
    per = round(dwell / dt)
    command = np.repeat(levels, per)
    time_s = np.arange(len(command)) * dt
    result = []
    for repeat in range(3):
        value = 0.0
        output = []
        for index, u in enumerate(command):
            target = 1.2 * u + 0.45 * u**3
            if history and index >= 5 * per:
                target += 0.18 * math.copysign(1.0, u) if u else 0.18
            value += (1.0 - math.exp(-dt / 0.22)) * (target - value)
            output.append(value + 0.001 * math.sin((repeat + 1) * index))
        result.append(
            _evidence(
                f"stairs-{repeat}",
                "protocol-stairs-history" if history else "protocol-stairs",
                time_s,
                {"u": command, "y": np.asarray(output)},
                kind="bidirectional_staircase",
                measured=("y",),
                controls=("u",),
            )
        )
    return result


def test_cubic_static_map_changes_route_and_history_blocks_inverse() -> None:
    task = _task(measured=["y"], controls=["u"])
    artifact = derive_feature_artifact(_staircase_evidence(), {}).to_dict()
    route = select_route_from_features(artifact, task)

    assert route["controller_family"] == "partial_inverse_then_PI"
    assert artifact["features"]["static_map_cubic_coefficient"]["value"] > 0.3
    controller, _ = synthesize_controller(task, route, artifact)
    assert controller.parameters["map_cubic"] > 0.3
    assert controller.parameters["inverse_input_lower"] == -1.0
    assert controller.parameters["inverse_input_upper"] == 1.0

    history_artifact = derive_feature_artifact(
        _staircase_evidence(history=True), {}
    ).to_dict()
    history_route = select_route_from_features(history_artifact, task)
    assert history_route["capability_gap"] == "history_dependent_static_inverse_gap"
    assert history_route["controller_family"] is None


def _release_evidence() -> list[dict[str, object]]:
    dt = 0.01
    duration = 14.0
    time_s = np.arange(0.0, duration, dt)
    traces: list[dict[str, object]] = []
    for index, amplitude in enumerate((0.12, 0.42, 0.78)):
        plant = OscillatorPlant(
            natural_frequency=2.0,
            damping_constant=-0.08,
            damping_quadratic=0.60,
            input_gain=1.4,
            initial_position=amplitude,
        )
        position = []
        velocity = []
        command = np.zeros_like(time_s)
        # One signed probe on the middle release identifies actuation sign and
        # authority without exposing model coefficients in metadata.
        if index == 1:
            command[(time_s >= 0.25) & (time_s < 0.45)] = 0.35
        for u in command:
            measured = plant.measure()
            position.append(measured["position"])
            velocity.append(measured["velocity"])
            plant.advance({"u": float(u)}, dt)
        traces.append(
            _evidence(
                f"release-{index}",
                "protocol-release",
                time_s,
                {
                    "u": command,
                    "position": np.asarray(position),
                    "velocity": np.asarray(velocity),
                },
                kind="amplitude_release_signed_input",
                measured=("position", "velocity"),
                controls=("u",),
                units={"u": "N", "position": "m", "velocity": "m/s"},
            )
        )
    return traces


def test_negative_small_amplitude_decay_selects_guarded_capture() -> None:
    artifact = derive_feature_artifact(_release_evidence(), {}).to_dict()
    task = _task(measured=["position", "velocity"], controls=["u"])
    route = select_route_from_features(artifact, task)

    assert artifact["features"]["small_amplitude_decay_rate"]["value"] < 0.0
    assert artifact["features"]["quadratic_decay_rate"]["value"] > 0.0
    crossing = artifact["features"]["zero_decay_crossing_amplitude"]["value"]
    assert 0.2 < crossing < 0.6
    assert route["controller_family"] == "self_excitation_energy_guarded_PID"
    controller, _ = synthesize_controller(task, route, artifact)
    assert controller.parameters["capture_damping_gain"] > 0.0


def _mimo_evidence(matrix: np.ndarray) -> list[dict[str, object]]:
    dt = 0.02
    time_s = np.arange(0.0, 40.0, dt)
    result = []
    for repeat in range(3):
        u1 = 0.5 * np.sin(0.7 * time_s) + 0.25 * np.sin(1.7 * time_s)
        u2 = 0.45 * np.sin(1.1 * time_s) + 0.2 * np.cos(2.1 * time_s)
        inputs = np.column_stack([u1, u2])
        state = np.zeros(2)
        outputs = []
        for row in inputs:
            target = matrix @ row
            state += (1.0 - np.exp(-dt / np.array([0.8, 1.2]))) * (target - state)
            outputs.append(state.copy())
        values = np.asarray(outputs)
        result.append(
            _evidence(
                f"mimo-{repeat}",
                "protocol-mimo",
                time_s,
                {"u1": u1, "u2": u2, "y1": values[:, 0], "y2": values[:, 1]},
                kind="mimo_dc_independent_multisine",
                measured=("y1", "y2"),
                controls=("u1", "u2"),
                units={"u1": "V", "u2": "V", "y1": "K", "y2": "K"},
            )
        )
    return result


def test_near_singular_mimo_data_cannot_authorize_inverse() -> None:
    artifact = derive_feature_artifact(
        _mimo_evidence(np.array([[1.0, 0.99], [0.99, 0.9802]])), {}
    ).to_dict()
    task = _task(measured=["y1", "y2"], controls=["u1", "u2"])
    route = select_route_from_features(artifact, task)

    assert artifact["features"]["gain_matrix_condition"]["value"] > 100.0
    assert route["controller_family"] is None
    assert route["capability_gap"] == "static_decoupling_capability_gap"


def test_two_amplitude_frequency_analysis_uses_excited_lines_and_detects_change():
    dt = 0.02
    time_s = np.arange(0.0, 50.0, dt)
    traces = []
    for index, amplitude in enumerate((0.15, 0.15, 0.55, 0.55)):
        command = amplitude * (
            np.sin(2 * math.pi * 0.2 * time_s)
            + 0.6 * np.sin(2 * math.pi * 0.5 * time_s)
            + 0.3 * np.sin(2 * math.pi * 0.8 * time_s)
        )
        nonlinear_input = command + 0.8 * command**3
        _, output, _ = signal.lsim(
            signal.TransferFunction([1.4], [0.7, 1.0]),
            U=nonlinear_input,
            T=time_s,
        )
        traces.append(
            _evidence(
                f"frequency-{index}",
                "protocol-two-amplitude",
                time_s,
                {"u": command, "y": output},
                kind="bounded_two_level_multisine",
                measured=("y",),
                controls=("u",),
            )
        )
    artifact = derive_feature_artifact(
        traces,
        {
            "feature_ids": [
                "low_order_residual_index",
                "phase_guard_frequency",
                "amplitude_dependence_index",
            ]
        },
    ).to_dict()

    assert artifact["quality"]["passed"] is True
    assert artifact["features"]["phase_guard_frequency"]["value"] > 0.0
    assert artifact["features"]["low_order_residual_index"]["value"] < 0.5
    assert artifact["features"]["amplitude_dependence_index"]["value"] > 0.05
    assert (
        artifact["features"]["phase_guard_frequency"]["derivation"]
        == "excited_line_frf_low_order_fit"
    )
