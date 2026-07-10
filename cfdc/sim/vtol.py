from __future__ import annotations

from dataclasses import dataclass, replace
import math

import numpy as np
from scipy.linalg import solve_continuous_are

from cfdc.models import (
    ChannelPerformanceMetrics,
    CoreFeatureArtifact,
    ExperimentPrimitive,
    SimulationPerformanceSummary,
    VtolSimulationResult,
    VtolState,
    VtolVariationResult,
    VtolVariationScenario,
)
from cfdc.performance import build_performance_summary, calculate_channel_performance
from cfdc.sim.integrators import rk4_step


@dataclass(frozen=True)
class VtolParams:
    mass_kg: float = 1.2
    pitch_inertia_kg_m2: float = 0.035
    gravity_m_s2: float = 9.81
    linear_drag_n_s_m: float = 0.08
    pitch_damping_n_m_s: float = 0.015
    thrust_min_n: float = 0.0
    thrust_max_n: float = 18.0
    torque_limit_n_m: float = 0.9

    @property
    def hover_thrust_n(self) -> float:
        return self.mass_kg * self.gravity_m_s2


@dataclass(frozen=True)
class VtolConfig:
    dt_s: float = 0.005
    duration_s: float = 10.0
    altitude_ref_m: float = 1.0
    position_ref_m: float = 1.0
    max_tilt_ref_rad: float = 0.48
    max_safe_tilt_rad: float = 0.70
    max_height_loss_m: float = 0.22
    max_attitude_error_rad: float = 0.35
    max_abs_lateral_position_m: float = 3.0
    max_saturation_fraction: float = 0.10
    max_nmp_undershoot: float = 0.15
    settling_band_fraction: float = 0.02
    max_settling_time_s: float = 12.0
    boundary_validation_duration_s: float = 15.0
    # A position sensor above the center of mass exposes the lateral RHP zero.
    lateral_output_angle_coupling_m: float = 0.35


@dataclass
class VtolControllerState:
    lateral_kp: float = 0.34
    lateral_kd: float = 0.70
    accepted_gain_updates: int = 0


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _dynamics(state: np.ndarray, thrust_n: float, torque_n_m: float, params: VtolParams) -> np.ndarray:
    x, z, theta, x_dot, z_dot, theta_dot = [float(value) for value in state]
    del x, z
    thrust = _clamp(thrust_n, params.thrust_min_n, params.thrust_max_n)
    torque = _clamp(torque_n_m, -params.torque_limit_n_m, params.torque_limit_n_m)
    x_ddot = (-thrust * math.sin(theta) - params.linear_drag_n_s_m * x_dot) / params.mass_kg
    z_ddot = (
        thrust * math.cos(theta)
        - params.mass_kg * params.gravity_m_s2
        - params.linear_drag_n_s_m * z_dot
    ) / params.mass_kg
    theta_ddot = (torque - params.pitch_damping_n_m_s * theta_dot) / params.pitch_inertia_kg_m2
    return np.array([x_dot, z_dot, theta_dot, x_ddot, z_ddot, theta_ddot], dtype=float)


def _acceleration_at(state: np.ndarray, thrust_n: float, torque_n_m: float, params: VtolParams) -> dict[str, float]:
    deriv = _dynamics(state, thrust_n, torque_n_m, params)
    return {
        "x_accel_m_s2": float(deriv[3]),
        "z_accel_m_s2": float(deriv[4]),
        "theta_accel_rad_s2": float(deriv[5]),
    }


def extract_vtol_core_features(params: VtolParams | None = None) -> list[CoreFeatureArtifact]:
    params = params or VtolParams()
    state_hover = np.zeros(6, dtype=float)
    thrust_samples = np.array(
        [
            0.82 * params.hover_thrust_n,
            0.92 * params.hover_thrust_n,
            1.00 * params.hover_thrust_n,
            1.08 * params.hover_thrust_n,
            1.18 * params.hover_thrust_n,
        ],
        dtype=float,
    )
    z_accels = np.array([
        _acceleration_at(state_hover, thrust, 0.0, params)["z_accel_m_s2"] for thrust in thrust_samples
    ])
    vertical_gain, intercept = np.polyfit(thrust_samples, z_accels, 1)
    hover_thrust = float(-intercept / vertical_gain)

    torque_samples = np.array([-0.12, -0.06, 0.06, 0.12], dtype=float)
    theta_accels = np.array([
        _acceleration_at(state_hover, params.hover_thrust_n, torque, params)["theta_accel_rad_s2"]
        for torque in torque_samples
    ])
    angular_gain, _ = np.polyfit(torque_samples, theta_accels, 1)

    tilted = np.zeros(6, dtype=float)
    tilted[2] = 0.08
    lateral_gain = _acceleration_at(tilted, params.hover_thrust_n, 0.0, params)["x_accel_m_s2"] / tilted[2]

    return [
        CoreFeatureArtifact(
            feature_id="hover_thrust",
            value=hover_thrust,
            lower_bound=0.98 * hover_thrust,
            upper_bound=1.02 * hover_thrust,
            confidence=0.92,
            units="N",
            method="vtol_vertical_thrust_sweep",
            source_experiment=ExperimentPrimitive.HOVER_THRUST,
        ),
        CoreFeatureArtifact(
            feature_id="vertical_input_gain",
            value=float(vertical_gain),
            lower_bound=0.98 * float(vertical_gain),
            upper_bound=1.02 * float(vertical_gain),
            confidence=0.92,
            units="m/s^2/N",
            method="vtol_vertical_thrust_sweep",
            source_experiment=ExperimentPrimitive.HOVER_THRUST,
        ),
        CoreFeatureArtifact(
            feature_id="angular_acceleration_gain",
            value=float(angular_gain),
            lower_bound=0.98 * float(angular_gain),
            upper_bound=1.02 * float(angular_gain),
            confidence=0.92,
            units="rad/s^2/Nm",
            method="vtol_small_torque_sweep",
            source_experiment=ExperimentPrimitive.PULSE,
        ),
        CoreFeatureArtifact(
            feature_id="lateral_coupling_gain",
            value=float(lateral_gain),
            lower_bound=min(0.98 * float(lateral_gain), 1.02 * float(lateral_gain)),
            upper_bound=max(0.98 * float(lateral_gain), 1.02 * float(lateral_gain)),
            confidence=0.88,
            units="m/s^2/rad",
            method="vtol_small_tilt_lateral_coupling",
            source_experiment=ExperimentPrimitive.PULSE,
        ),
    ]


def _feature_map(features: list[CoreFeatureArtifact]) -> dict[str, float]:
    return {feature.feature_id: feature.value for feature in features}


def _lateral_measurement(state: np.ndarray, config: VtolConfig) -> tuple[float, float]:
    x, _, theta, x_dot, _, theta_dot = [float(value) for value in state]
    offset = config.lateral_output_angle_coupling_m
    return x + offset * theta, x_dot + offset * theta_dot


def _conservative_gains(features: list[CoreFeatureArtifact]) -> dict[str, float]:
    fmap = _feature_map(features)
    return {
        "altitude_wn_rad_s": 1.20,
        "altitude_zeta": 0.90,
        "altitude_kp_accel": 1.20**2,
        "altitude_kd_accel": 2.0 * 0.90 * 1.20,
        "attitude_wn_rad_s": 4.30,
        "attitude_zeta": 0.90,
        "attitude_kp_accel": 4.30**2,
        "attitude_kd_accel": 2.0 * 0.90 * 4.30,
        "vertical_gain": fmap["vertical_input_gain"],
        "angular_gain": fmap["angular_acceleration_gain"],
    }


def vtol_operational_gains(features: list[CoreFeatureArtifact], gravity_m_s2: float = 9.81) -> dict[str, float]:
    """Feature-scaled gains used only after a full coupled software validation."""

    fmap = _feature_map(features)
    mass_estimate = fmap["hover_thrust"] / gravity_m_s2
    inertia_estimate = 1.0 / max(abs(fmap["angular_acceleration_gain"]), 1e-12)
    altitude_wn = 1.20
    altitude_zeta = 0.90
    attitude_wn = 4.30
    attitude_zeta = 0.90
    return {
        "kp_z": mass_estimate * altitude_wn**2,
        "kd_z": 2.0 * mass_estimate * altitude_zeta * altitude_wn,
        "kp_theta": inertia_estimate * attitude_wn**2,
        "kd_theta": 2.0 * inertia_estimate * attitude_zeta * attitude_wn,
        "kp_y": 0.34,
        "kd_y": 0.70,
    }


def _controller_command(
    state: np.ndarray,
    x_ref_m: float,
    z_ref_m: float,
    features: list[CoreFeatureArtifact],
    gains: dict[str, float],
    feedforward: dict[str, float],
    params: VtolParams,
    config: VtolConfig,
    controller_state: VtolControllerState,
    mode: str,
) -> dict[str, float | bool | str]:
    _, z, theta, _, z_dot, theta_dot = [float(value) for value in state]
    x, x_dot = _lateral_measurement(state, config)
    fmap = _feature_map(features)
    theta_ref = 0.0
    uses_cfdc_candidate = "kp_z" in gains or "kp_theta" in gains
    if uses_cfdc_candidate:
        if mode in {"position", "boundary"}:
            lateral_gain = fmap["lateral_coupling_gain"]
            if abs(lateral_gain) < 1e-9:
                raise ValueError("lateral_coupling_gain must be non-zero")
            desired_x_accel = controller_state.lateral_kp * (x_ref_m - x) - controller_state.lateral_kd * x_dot
            theta_ref = _clamp(
                desired_x_accel / lateral_gain,
                -config.max_tilt_ref_rad,
                config.max_tilt_ref_rad,
            )
        hover_thrust = feedforward.get("hover_thrust", fmap["hover_thrust"])
        thrust_cmd = (
            hover_thrust / max(0.20, math.cos(theta))
            + gains.get("kp_z", 0.0) * (z_ref_m - z)
            - gains.get("kd_z", 0.0) * z_dot
        )
        torque_cmd = gains.get("kp_theta", 0.0) * (theta_ref - theta) - gains.get("kd_theta", 0.0) * theta_dot
        controller_source = "cfdc_orchestrator"
    else:
        if mode in {"position", "boundary"}:
            desired_x_accel = controller_state.lateral_kp * (x_ref_m - x) - controller_state.lateral_kd * x_dot
            theta_ref = _clamp(
                desired_x_accel / fmap["lateral_coupling_gain"],
                -config.max_tilt_ref_rad,
                config.max_tilt_ref_rad,
            )

        altitude_accel_cmd = gains["altitude_kp_accel"] * (z_ref_m - z) - gains["altitude_kd_accel"] * z_dot
        thrust_cmd = fmap["hover_thrust"] / max(0.20, math.cos(theta)) + altitude_accel_cmd / gains["vertical_gain"]
        theta_accel_cmd = gains["attitude_kp_accel"] * (theta_ref - theta) - gains["attitude_kd_accel"] * theta_dot
        torque_cmd = theta_accel_cmd / gains["angular_gain"]
        controller_source = "internal_feature_conservative"
    thrust_n = _clamp(thrust_cmd, params.thrust_min_n, params.thrust_max_n)
    torque_n_m = _clamp(torque_cmd, -params.torque_limit_n_m, params.torque_limit_n_m)
    return {
        "thrust_n": thrust_n,
        "torque_n_m": torque_n_m,
        "theta_ref_rad": theta_ref,
        "thrust_saturated": abs(thrust_n - thrust_cmd) > 1e-9,
        "torque_saturated": abs(torque_n_m - torque_cmd) > 1e-9,
        "controller_source": controller_source,
        "hover_feedforward_n": feedforward.get("hover_thrust", fmap["hover_thrust"]),
    }


def _simulate_closed_loop(
    params: VtolParams,
    config: VtolConfig,
    features: list[CoreFeatureArtifact],
    mode: str,
    duration_s: float,
    initial_state: list[float],
    x_ref_m: float,
    z_ref_m: float,
    gains: dict[str, float] | None = None,
    feedforward: dict[str, float] | None = None,
    controller_state: VtolControllerState | None = None,
    allow_online_update: bool = False,
) -> tuple[list[dict[str, float | str]], VtolControllerState, list[dict[str, float | str | bool]]]:
    gains = dict(gains or _conservative_gains(features))
    feedforward = dict(feedforward or {})
    uses_external_gains = "kp_z" in gains or "kp_theta" in gains
    state = np.array(initial_state, dtype=float)
    if controller_state is None:
        if uses_external_gains:
            controller_state = VtolControllerState(
                lateral_kp=gains.get("kp_y", 0.0),
                lateral_kd=gains.get("kd_y", 0.0),
            )
        else:
            controller_state = VtolControllerState()
    records: list[dict[str, float | str]] = []
    events: list[dict[str, float | str | bool]] = [
        {
            "time_s": 0.0,
            "event": "controller_loaded",
            "controller_source": "cfdc_orchestrator" if uses_external_gains else "internal_feature_conservative",
            "uses_external_gains": uses_external_gains,
        }
    ]
    steps = int(duration_s / config.dt_s)
    for step in range(steps + 1):
        time_s = step * config.dt_s
        if allow_online_update and not uses_external_gains and step > 0 and abs(time_s - 3.0) < 0.5 * config.dt_s:
            recent = records[-int(1.0 / config.dt_s) :]
            if recent:
                max_height_loss = z_ref_m - min(float(row["z_m"]) for row in recent)
                max_tilt = max(abs(float(row["theta_rad"])) for row in recent)
                sat_fraction = sum(row["thrust_saturated"] == "yes" for row in recent) / len(recent)
                if max_height_loss < 0.08 and max_tilt < 0.35 and sat_fraction < 0.02:
                    controller_state.lateral_kp = 0.50
                    controller_state.lateral_kd = 0.85
                    controller_state.accepted_gain_updates += 1
                    events.append(
                        {
                            "time_s": time_s,
                            "event": "accepted_small_lateral_gain_update",
                            "lateral_kp": controller_state.lateral_kp,
                            "lateral_kd": controller_state.lateral_kd,
                        }
                    )
        command = _controller_command(state, x_ref_m, z_ref_m, features, gains, feedforward, params, config, controller_state, mode)
        records.append(
            {
                "time_s": time_s,
                "x_m": _lateral_measurement(state, config)[0],
                "physical_x_m": float(state[0]),
                "z_m": float(state[1]),
                "theta_rad": float(state[2]),
                "x_dot_m_s": _lateral_measurement(state, config)[1],
                "physical_x_dot_m_s": float(state[3]),
                "z_dot_m_s": float(state[4]),
                "theta_dot_rad_s": float(state[5]),
                "x_ref_m": x_ref_m,
                "z_ref_m": z_ref_m,
                "theta_ref_rad": float(command["theta_ref_rad"]),
                "thrust_n": float(command["thrust_n"]),
                "torque_n_m": float(command["torque_n_m"]),
                "thrust_saturated": "yes" if command["thrust_saturated"] else "no",
                "torque_saturated": "yes" if command["torque_saturated"] else "no",
                "lateral_kp": controller_state.lateral_kp,
                "lateral_kd": controller_state.lateral_kd,
                "phase": mode,
                "controller_source": str(command["controller_source"]),
                "hover_feedforward_n": float(command["hover_feedforward_n"]),
            }
        )
        if step < steps:
            state = rk4_step(
                _dynamics,
                state,
                config.dt_s,
                float(command["thrust_n"]),
                float(command["torque_n_m"]),
                params,
            )
    return records, controller_state, events


def _evaluate_records(
    records: list[dict[str, float | str]],
    config: VtolConfig,
    z_ref_m: float,
    primary_channel: str,
) -> tuple[
    dict[str, int | float | str | bool | None],
    dict[str, ChannelPerformanceMetrics],
    list[str],
]:
    final = records[-1]
    time_s = [float(row["time_s"]) for row in records]
    channels = {
        "lateral_position": calculate_channel_performance(
            time_s,
            [float(row["x_ref_m"]) for row in records],
            [float(row["x_m"]) for row in records],
            settling_band_fraction=config.settling_band_fraction,
        ),
        "altitude": calculate_channel_performance(
            time_s,
            [float(row["z_ref_m"]) for row in records],
            [float(row["z_m"]) for row in records],
            settling_band_fraction=config.settling_band_fraction,
            settling_band_absolute=0.02,
        ),
        "attitude": calculate_channel_performance(
            time_s,
            [float(row["theta_ref_rad"]) for row in records],
            [float(row["theta_rad"]) for row in records],
            settling_band_fraction=config.settling_band_fraction,
            settling_band_absolute=0.01,
        ),
    }
    primary = channels[primary_channel]
    min_z = min(float(row["z_m"]) for row in records)
    max_abs_tilt = max(abs(float(row["theta_rad"])) for row in records)
    max_abs_lateral_position = max(abs(float(row["x_m"])) for row in records)
    max_abs_theta_error = max(abs(float(row["theta_ref_rad"]) - float(row["theta_rad"])) for row in records)
    thrust_saturation_fraction = sum(row["thrust_saturated"] == "yes" for row in records) / len(records)
    torque_saturation_fraction = sum(row["torque_saturated"] == "yes" for row in records) / len(records)
    height_loss = z_ref_m - min_z
    violations: list[str] = []
    if height_loss > config.max_height_loss_m:
        violations.append("height_loss_limit")
    if max_abs_tilt > config.max_safe_tilt_rad:
        violations.append("tilt_safety_limit")
    if max_abs_theta_error > config.max_attitude_error_rad:
        violations.append("attitude_tracking_limit")
    if max_abs_lateral_position > config.max_abs_lateral_position_m:
        violations.append("lateral_position_limit")
    if thrust_saturation_fraction > config.max_saturation_fraction:
        violations.append("thrust_saturation_limit")
    if torque_saturation_fraction > config.max_saturation_fraction:
        violations.append("torque_saturation_limit")
    return {
        "final_error": primary.final_error,
        "abs_final_error": primary.abs_final_error,
        "overshoot": primary.overshoot,
        "settled": primary.settled,
        "settling_time_s": primary.settling_time_s,
        "final_output": primary.final_output,
        "saturation_fraction": max(thrust_saturation_fraction, torque_saturation_fraction),
        "final_x_m": float(final["x_m"]),
        "final_z_m": float(final["z_m"]),
        "final_theta_rad": float(final["theta_rad"]),
        "final_x_error_m": float(final["x_ref_m"]) - float(final["x_m"]),
        "final_z_error_m": float(final["z_ref_m"]) - float(final["z_m"]),
        "height_loss_m": height_loss,
        "max_abs_lateral_position_m": max_abs_lateral_position,
        "max_abs_tilt_rad": max_abs_tilt,
        "max_abs_attitude_error_rad": max_abs_theta_error,
        "thrust_saturation_fraction": thrust_saturation_fraction,
        "torque_saturation_fraction": torque_saturation_fraction,
        "nmp_undershoot": channels["lateral_position"].undershoot,
        "lateral_settled": channels["lateral_position"].settled,
        "lateral_settling_time_s": channels["lateral_position"].settling_time_s,
        "altitude_settled": channels["altitude"].settled,
        "altitude_settling_time_s": channels["altitude"].settling_time_s,
        "accepted": not violations,
    }, channels, violations


def _build_vtol_performance(
    *,
    primary_channel: str,
    channels: dict[str, ChannelPerformanceMetrics],
    metrics: dict[str, int | float | str | bool | None],
    config: VtolConfig,
    violations: list[str],
    success: bool,
    boundary_triggered: bool | None = None,
    boundary_reason: str | None = None,
) -> SimulationPerformanceSummary:
    return build_performance_summary(
        primary_channel=primary_channel,
        channels=channels,
        actuator_saturation_fractions={
            "thrust": float(metrics["thrust_saturation_fraction"]),
            "torque": float(metrics["torque_saturation_fraction"]),
        },
        state_boundaries={
            "max_abs_lateral_position_m": float(metrics["max_abs_lateral_position_m"]),
            "height_loss_m": float(metrics["height_loss_m"]),
            "max_abs_tilt_rad": float(metrics["max_abs_tilt_rad"]),
            "max_abs_attitude_error_rad": float(metrics["max_abs_attitude_error_rad"]),
        },
        limits={
            "max_abs_lateral_position_m": config.max_abs_lateral_position_m,
            "max_height_loss_m": config.max_height_loss_m,
            "max_abs_tilt_rad": config.max_safe_tilt_rad,
            "max_abs_attitude_error_rad": config.max_attitude_error_rad,
            "max_actuator_saturation_fraction": config.max_saturation_fraction,
            "max_nmp_undershoot": config.max_nmp_undershoot,
            "max_settling_time_s": config.max_settling_time_s,
        },
        violations=violations,
        success=success,
        boundary_triggered=boundary_triggered,
        boundary_reason=boundary_reason,
    )


def run_vtol_simulation(
    mode: str = "position",
    params: VtolParams | None = None,
    config: VtolConfig | None = None,
    features: list[CoreFeatureArtifact] | None = None,
    gains: dict[str, float] | None = None,
    feedforward: dict[str, float] | None = None,
    include_trajectory: bool = False,
) -> VtolSimulationResult:
    params = params or VtolParams()
    config = config or VtolConfig()
    features = list(features or extract_vtol_core_features(params))
    gains = dict(gains or {}) or None
    feedforward = dict(feedforward or {})
    events: list[dict[str, float | str | bool]]

    if mode == "altitude":
        records, _, events = _simulate_closed_loop(
            params,
            config,
            features,
            mode="altitude",
            duration_s=7.0,
            initial_state=[0.0, 0.35, 0.0, 0.0, 0.0, 0.0],
            x_ref_m=0.0,
            z_ref_m=config.altitude_ref_m,
            gains=gains,
            feedforward=feedforward,
            controller_state=VtolControllerState(lateral_kp=0.0, lateral_kd=0.0),
        )
    elif mode == "hover":
        records, _, events = _simulate_closed_loop(
            params,
            config,
            features,
            mode="hover",
            duration_s=8.0,
            initial_state=[0.0, 0.55, 0.16, 0.0, 0.0, 0.0],
            x_ref_m=0.0,
            z_ref_m=config.altitude_ref_m,
            gains=gains,
            feedforward=feedforward,
        )
    elif mode == "boundary":
        return run_vtol_boundary_scan(
            params,
            config,
            features=features,
            gains=gains,
            feedforward=feedforward,
            include_trajectory=include_trajectory,
        )
    else:
        records, _, events = _simulate_closed_loop(
            params,
            config,
            features,
            mode="position",
            duration_s=config.duration_s,
            initial_state=[0.0, config.altitude_ref_m, 0.0, 0.0, 0.0, 0.0],
            x_ref_m=config.position_ref_m,
            z_ref_m=config.altitude_ref_m,
            gains=gains,
            feedforward=feedforward,
            allow_online_update=True,
        )

    primary_channel = "lateral_position" if mode == "position" else "altitude"
    metrics, channels, violations = _evaluate_records(
        records,
        config,
        config.altitude_ref_m,
        primary_channel,
    )
    final = records[-1]
    required_channels = ["altitude"]
    if mode == "hover":
        required_channels.append("attitude")
    if mode == "position":
        required_channels.extend(["lateral_position", "attitude"])
    unsettled = [channel for channel in required_channels if not channels[channel].settled]
    for channel in unsettled:
        violations.append(f"{channel}_not_settled")
    late_channels = [
        channel
        for channel in required_channels
        if channels[channel].settling_time_s is not None
        and channels[channel].settling_time_s > config.max_settling_time_s
    ]
    for channel in late_channels:
        violations.append(f"{channel}_settling_time_limit")
    success = (
        bool(metrics["accepted"])
        and not unsettled
        and not late_channels
        and abs(float(metrics["final_z_error_m"])) < 0.08
    )
    if abs(float(metrics["final_z_error_m"])) >= 0.08:
        violations.append("final_altitude_error")
    if mode == "position":
        success = success and abs(float(metrics["final_x_error_m"])) < 0.18
        if abs(float(metrics["final_x_error_m"])) >= 0.18:
            violations.append("final_lateral_error")
    metrics["success"] = success
    metrics = {
        **metrics,
        "controller_source": records[-1]["controller_source"],
        "hover_feedforward_n": float(records[-1]["hover_feedforward_n"]),
    }
    performance = _build_vtol_performance(
        primary_channel=primary_channel,
        channels=channels,
        metrics=metrics,
        config=config,
        violations=violations,
        success=success,
    )
    return VtolSimulationResult(
        mode=mode,
        success=success,
        stop_reason="accepted" if success else "metric_limit",
        final_state=VtolState(
            x_m=float(final["x_m"]),
            z_m=float(final["z_m"]),
            theta_rad=float(final["theta_rad"]),
            x_dot_m_s=float(final["x_dot_m_s"]),
            z_dot_m_s=float(final["z_dot_m_s"]),
            theta_dot_rad_s=float(final["theta_dot_rad_s"]),
        ),
        performance=performance,
        metrics=metrics,
        features=features,
        events=events,
        trajectory=records if include_trajectory else [],
    )


def run_vtol_variation(
    params: VtolParams | None = None,
    config: VtolConfig | None = None,
    include_trajectory: bool = False,
) -> VtolVariationResult:
    nominal_params = params or VtolParams()
    base_config = config or VtolConfig(duration_s=25.0)
    if base_config.duration_s < 25.0:
        base_config = replace(base_config, duration_s=25.0)
    nominal_features = extract_vtol_core_features(nominal_params)
    mass_changed = replace(nominal_params, mass_kg=1.25 * nominal_params.mass_kg)
    inertia_changed = replace(
        nominal_params,
        pitch_inertia_kg_m2=1.50 * nominal_params.pitch_inertia_kg_m2,
    )
    both_changed = replace(
        mass_changed,
        pitch_inertia_kg_m2=1.50 * nominal_params.pitch_inertia_kg_m2,
    )
    scenario_specs = [
        ("nominal_updated_features", nominal_params, "updated", True),
        ("mass_plus_25_percent_stale_features", mass_changed, "stale", False),
        ("mass_plus_25_percent_updated_features", mass_changed, "updated", True),
        ("inertia_plus_50_percent_stale_features", inertia_changed, "stale", True),
        ("inertia_plus_50_percent_updated_features", inertia_changed, "updated", True),
        ("mass_plus_25_inertia_plus_50_updated_features", both_changed, "updated", True),
    ]
    scenarios: list[VtolVariationScenario] = []
    for scenario_id, scenario_params, feature_source, expected_success in scenario_specs:
        scenario_features = (
            nominal_features
            if feature_source == "stale"
            else extract_vtol_core_features(scenario_params)
        )
        simulation = run_vtol_simulation(
            mode="position",
            params=scenario_params,
            config=base_config,
            features=scenario_features,
            gains=vtol_operational_gains(
                scenario_features,
                scenario_params.gravity_m_s2,
            ),
            feedforward={
                "hover_thrust": _feature_map(scenario_features)["hover_thrust"],
            },
            include_trajectory=include_trajectory,
        )
        scenarios.append(
            VtolVariationScenario(
                scenario_id=scenario_id,
                feature_source=feature_source,
                mass_kg=scenario_params.mass_kg,
                pitch_inertia_kg_m2=scenario_params.pitch_inertia_kg_m2,
                expected_success=expected_success,
                expectation_met=simulation.success == expected_success,
                features=scenario_features,
                simulation=simulation,
            )
        )
    return VtolVariationResult(
        success=all(scenario.expectation_met for scenario in scenarios),
        scenarios=scenarios,
        updated_scenario_count=sum(scenario.feature_source == "updated" for scenario in scenarios),
        stale_scenario_count=sum(scenario.feature_source == "stale" for scenario in scenarios),
        notes=[
            "Updated scenarios re-extract hover thrust and angular acceleration gain from the changed software plant.",
            "This is an explicit stale-versus-updated feature study, not continuous FLL or RLS tracking.",
        ],
    )


def _linearize_hover(params: VtolParams) -> tuple[np.ndarray, np.ndarray]:
    state0 = np.zeros(6, dtype=float)
    thrust0 = params.hover_thrust_n
    torque0 = 0.0
    eps = 1e-6
    a_mat = np.zeros((6, 6), dtype=float)
    b_mat = np.zeros((6, 2), dtype=float)
    for column in range(6):
        delta = np.zeros(6, dtype=float)
        delta[column] = eps
        a_mat[:, column] = (
            _dynamics(state0 + delta, thrust0, torque0, params)
            - _dynamics(state0 - delta, thrust0, torque0, params)
        ) / (2.0 * eps)
    b_mat[:, 0] = (
        _dynamics(state0, thrust0 + eps, torque0, params)
        - _dynamics(state0, thrust0 - eps, torque0, params)
    ) / (2.0 * eps)
    b_mat[:, 1] = (
        _dynamics(state0, thrust0, torque0 + eps, params)
        - _dynamics(state0, thrust0, torque0 - eps, params)
    ) / (2.0 * eps)
    return a_mat, b_mat


def run_vtol_lqr_baseline(
    params: VtolParams | None = None,
    config: VtolConfig | None = None,
    include_trajectory: bool = False,
) -> VtolSimulationResult:
    params = params or VtolParams()
    config = config or VtolConfig(duration_s=15.0)
    a_mat, b_mat = _linearize_hover(params)
    q_mat = np.diag([20.0, 25.0, 35.0, 5.0, 8.0, 5.0])
    r_mat = np.diag([1.0, 0.25])
    riccati = solve_continuous_are(a_mat, b_mat, q_mat, r_mat)
    lqr_gain = np.linalg.solve(r_mat, b_mat.T @ riccati)
    state = np.array([0.0, config.altitude_ref_m, 0.0, 0.0, 0.0, 0.0], dtype=float)
    reference_state = np.array(
        [config.position_ref_m, config.altitude_ref_m, 0.0, 0.0, 0.0, 0.0],
        dtype=float,
    )
    records: list[dict[str, float | str]] = []
    steps = int(config.duration_s / config.dt_s)
    for step in range(steps + 1):
        time_s = step * config.dt_s
        delta_control = -lqr_gain @ (state - reference_state)
        raw_thrust = params.hover_thrust_n + float(delta_control[0])
        raw_torque = float(delta_control[1])
        thrust = _clamp(raw_thrust, params.thrust_min_n, params.thrust_max_n)
        torque = _clamp(raw_torque, -params.torque_limit_n_m, params.torque_limit_n_m)
        measured_x, measured_x_dot = _lateral_measurement(state, config)
        records.append(
            {
                "time_s": time_s,
                "x_m": measured_x,
                "physical_x_m": float(state[0]),
                "z_m": float(state[1]),
                "theta_rad": float(state[2]),
                "x_dot_m_s": measured_x_dot,
                "physical_x_dot_m_s": float(state[3]),
                "z_dot_m_s": float(state[4]),
                "theta_dot_rad_s": float(state[5]),
                "x_ref_m": config.position_ref_m,
                "z_ref_m": config.altitude_ref_m,
                "theta_ref_rad": 0.0,
                "thrust_n": thrust,
                "torque_n_m": torque,
                "thrust_saturated": "yes" if abs(thrust - raw_thrust) > 1e-9 else "no",
                "torque_saturated": "yes" if abs(torque - raw_torque) > 1e-9 else "no",
                "lateral_kp": 0.0,
                "lateral_kd": 0.0,
                "phase": "lqr_baseline",
                "controller_source": "full_model_lqr",
                "hover_feedforward_n": params.hover_thrust_n,
            }
        )
        if step < steps:
            state = rk4_step(_dynamics, state, config.dt_s, thrust, torque, params)

    metrics, channels, violations = _evaluate_records(
        records,
        config,
        config.altitude_ref_m,
        "lateral_position",
    )
    for channel in ["lateral_position", "altitude", "attitude"]:
        if not channels[channel].settled:
            violations.append(f"{channel}_not_settled")
        elif (
            channels[channel].settling_time_s is not None
            and channels[channel].settling_time_s > config.max_settling_time_s
        ):
            violations.append(f"{channel}_settling_time_limit")
    if channels["lateral_position"].abs_final_error >= 0.18:
        violations.append("final_lateral_error")
    if channels["altitude"].abs_final_error >= 0.08:
        violations.append("final_altitude_error")
    success = not violations
    metrics = {
        **metrics,
        "success": success,
        "controller_source": "full_model_lqr",
        "hover_feedforward_n": params.hover_thrust_n,
    }
    performance = _build_vtol_performance(
        primary_channel="lateral_position",
        channels=channels,
        metrics=metrics,
        config=config,
        violations=violations,
        success=success,
    )
    final = records[-1]
    return VtolSimulationResult(
        mode="lqr-baseline",
        success=success,
        stop_reason="accepted" if success else "metric_limit",
        final_state=VtolState(
            x_m=float(final["x_m"]),
            z_m=float(final["z_m"]),
            theta_rad=float(final["theta_rad"]),
            x_dot_m_s=float(final["x_dot_m_s"]),
            z_dot_m_s=float(final["z_dot_m_s"]),
            theta_dot_rad_s=float(final["theta_dot_rad_s"]),
        ),
        performance=performance,
        metrics=metrics,
        features=[],
        events=[
            {
                "time_s": 0.0,
                "event": "full_model_lqr_loaded",
                "controller_source": "full_model_lqr",
            }
        ],
        trajectory=records if include_trajectory else [],
    )


def run_vtol_boundary_scan(
    params: VtolParams | None = None,
    config: VtolConfig | None = None,
    features: list[CoreFeatureArtifact] | None = None,
    gains: dict[str, float] | None = None,
    feedforward: dict[str, float] | None = None,
    include_trajectory: bool = False,
) -> VtolSimulationResult:
    params = params or VtolParams()
    config = config or VtolConfig()
    features = list(features or extract_vtol_core_features(params))
    gains = dict(gains or {}) or None
    feedforward = dict(feedforward or {})
    candidates = [
        0.25,
        0.40,
        0.55,
        0.70,
        0.85,
        1.00,
        1.025,
        1.05,
        1.075,
        1.10,
        1.125,
        1.15,
        1.30,
        1.45,
        1.60,
        1.80,
        2.00,
        2.50,
        3.00,
        3.50,
        4.00,
        4.25,
        4.50,
    ]
    all_records: list[dict[str, float | str]] = []
    boundary_events: list[dict[str, int | float | str | bool | None]] = []
    last_records: list[dict[str, float | str]] = []
    last_accepted_gains: dict[str, float] = {}
    accepted_gain_history: list[dict[str, float]] = []
    for trial_index, lateral_kp in enumerate(candidates, start=1):
        controller_state = VtolControllerState(lateral_kp=lateral_kp, lateral_kd=1.60 * math.sqrt(lateral_kp))
        records, _, _ = _simulate_closed_loop(
            params,
            config,
            features,
            mode="boundary",
            duration_s=6.0,
            initial_state=[0.0, config.altitude_ref_m, 0.0, 0.0, 0.0, 0.0],
            x_ref_m=0.15,
            z_ref_m=config.altitude_ref_m,
            gains=gains,
            feedforward=feedforward,
            controller_state=controller_state,
        )
        metrics, _, safety_reasons = _evaluate_records(
            records,
            config,
            config.altitude_ref_m,
            "lateral_position",
        )
        reasons = list(safety_reasons)
        if float(metrics["nmp_undershoot"]) >= config.max_nmp_undershoot:
            reasons.insert(0, "nmp_undershoot")
        accepted = not reasons
        boundary_reason = "accepted" if accepted else "+".join(reasons)
        event = {
            "event": "candidate_trial",
            "trial_index": trial_index,
            "candidate_lateral_kp": lateral_kp,
            "candidate_lateral_kd": controller_state.lateral_kd,
            "accepted": accepted,
            "boundary_reason": boundary_reason,
            "nmp_undershoot": float(metrics["nmp_undershoot"]),
            "settled": bool(metrics["lateral_settled"]),
            "settling_time_s": metrics["lateral_settling_time_s"],
            "height_loss_m": float(metrics["height_loss_m"]),
            "max_abs_lateral_position_m": float(metrics["max_abs_lateral_position_m"]),
            "max_abs_tilt_rad": float(metrics["max_abs_tilt_rad"]),
            "thrust_saturation_fraction": float(metrics["thrust_saturation_fraction"]),
            "torque_saturation_fraction": float(metrics["torque_saturation_fraction"]),
            "controller_source": records[-1]["controller_source"],
        }
        boundary_events.append(event)
        all_records.extend(records)
        last_records = records
        if accepted:
            last_accepted_gains = {
                "kp_y": lateral_kp,
                "kd_y": controller_state.lateral_kd,
            }
            accepted_gain_history.append(last_accepted_gains)
        if not accepted:
            break
    rejected = [event for event in boundary_events if event["accepted"] is False]
    first_rejected = rejected[0] if rejected else None
    rollback_applied = False
    final_records = last_records or all_records
    if first_rejected and accepted_gain_history:
        for rollback_gains in reversed(accepted_gain_history):
            rollback_state = VtolControllerState(
                lateral_kp=rollback_gains["kp_y"],
                lateral_kd=rollback_gains["kd_y"],
            )
            candidate_records, _, _ = _simulate_closed_loop(
                params,
                config,
                features,
                mode="boundary",
                duration_s=config.boundary_validation_duration_s,
                initial_state=[0.0, config.altitude_ref_m, 0.0, 0.0, 0.0, 0.0],
                x_ref_m=0.15,
                z_ref_m=config.altitude_ref_m,
                gains=gains,
                feedforward=feedforward,
                controller_state=rollback_state,
            )
            candidate_metrics, candidate_channels, candidate_violations = _evaluate_records(
                candidate_records,
                config,
                config.altitude_ref_m,
                "lateral_position",
            )
            strict_reasons = list(candidate_violations)
            if float(candidate_metrics["nmp_undershoot"]) >= config.max_nmp_undershoot:
                strict_reasons.append("rollback_nmp_undershoot")
            for channel_name in ["lateral_position", "altitude", "attitude"]:
                if not candidate_channels[channel_name].settled:
                    strict_reasons.append(f"rollback_{channel_name}_not_settled")
                elif (
                    candidate_channels[channel_name].settling_time_s is not None
                    and candidate_channels[channel_name].settling_time_s
                    > config.max_settling_time_s
                ):
                    strict_reasons.append(f"rollback_{channel_name}_settling_time_limit")
            if candidate_channels["lateral_position"].abs_final_error >= 0.02:
                strict_reasons.append("rollback_final_lateral_error")
            if candidate_channels["altitude"].abs_final_error >= 0.08:
                strict_reasons.append("rollback_final_altitude_error")
            accepted_rollback = not strict_reasons
            boundary_events.append(
                {
                    "event": "rollback_validation",
                    "trial_index": len(boundary_events) + 1,
                    "candidate_lateral_kp": rollback_gains["kp_y"],
                    "candidate_lateral_kd": rollback_gains["kd_y"],
                    "accepted": accepted_rollback,
                    "boundary_reason": (
                        "rollback_validated" if accepted_rollback else "+".join(strict_reasons)
                    ),
                    "nmp_undershoot": float(candidate_metrics["nmp_undershoot"]),
                    "settled": bool(candidate_metrics["lateral_settled"]),
                    "settling_time_s": candidate_metrics["lateral_settling_time_s"],
                }
            )
            all_records.extend(candidate_records)
            final_records = candidate_records
            if accepted_rollback:
                rollback_applied = True
                last_accepted_gains = rollback_gains
                break
    metrics, channels, final_violations = _evaluate_records(
        final_records,
        config,
        config.altitude_ref_m,
        "lateral_position",
    )
    final = final_records[-1]
    boundary_reason = str(first_rejected["boundary_reason"]) if first_rejected else "not_triggered"
    performance_violations = list(final_violations)
    rollback_nmp_safe = float(metrics["nmp_undershoot"]) < config.max_nmp_undershoot
    if not rollback_nmp_safe:
        performance_violations.append("rollback_nmp_undershoot")
    if first_rejected is None:
        performance_violations.append("boundary_not_triggered")
    if first_rejected is not None and not rollback_applied:
        performance_violations.append("rollback_unavailable")
    for channel_name in ["lateral_position", "altitude", "attitude"]:
        if not channels[channel_name].settled:
            performance_violations.append(f"rollback_{channel_name}_not_settled")
        elif (
            channels[channel_name].settling_time_s is not None
            and channels[channel_name].settling_time_s > config.max_settling_time_s
        ):
            performance_violations.append(f"rollback_{channel_name}_settling_time_limit")
    if channels["lateral_position"].abs_final_error >= 0.02:
        performance_violations.append("rollback_final_lateral_error")
    if channels["altitude"].abs_final_error >= 0.08:
        performance_violations.append("rollback_final_altitude_error")
    success = bool(first_rejected) and rollback_applied and not performance_violations
    metrics = {
        **metrics,
        "success": success,
        "accepted": not final_violations and rollback_nmp_safe,
        "tested_candidate_count": len([event for event in boundary_events if event["event"] == "candidate_trial"]),
        "boundary_triggered": bool(first_rejected),
        "boundary_reason": boundary_reason,
        "boundary_nmp_undershoot": (
            float(first_rejected["nmp_undershoot"]) if first_rejected else 0.0
        ),
        "accepted_lateral_kp": last_accepted_gains.get("kp_y", 0.0),
        "accepted_lateral_kd": last_accepted_gains.get("kd_y", 0.0),
        "rollback_applied": rollback_applied,
        "controller_source": final["controller_source"],
        "hover_feedforward_n": float(final["hover_feedforward_n"]),
    }
    performance = _build_vtol_performance(
        primary_channel="lateral_position",
        channels=channels,
        metrics=metrics,
        config=config,
        violations=performance_violations,
        success=success,
        boundary_triggered=bool(first_rejected),
        boundary_reason=boundary_reason,
    )
    return VtolSimulationResult(
        mode="boundary",
        success=success,
        stop_reason="boundary_triggered" if first_rejected else "all_candidates_accepted",
        final_state=VtolState(
            x_m=float(final["x_m"]),
            z_m=float(final["z_m"]),
            theta_rad=float(final["theta_rad"]),
            x_dot_m_s=float(final["x_dot_m_s"]),
            z_dot_m_s=float(final["z_dot_m_s"]),
            theta_dot_rad_s=float(final["theta_dot_rad_s"]),
        ),
        performance=performance,
        metrics=metrics,
        features=features,
        events=boundary_events,
        trajectory=all_records if include_trajectory else [],
    )
