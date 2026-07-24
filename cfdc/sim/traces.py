from __future__ import annotations

import numpy as np


def step_trace(
    static_gain: float,
    time_constant: float,
    dead_time: float = 0.0,
    inverse_response_severity: float = 0.0,
    sample_count: int = 1200,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    duration_s = max(30.0, 8.0 * (time_constant + dead_time))
    time_s = np.linspace(0.0, duration_s, sample_count)
    input_signal = np.zeros_like(time_s)
    input_signal[time_s >= 1.0] = 0.5
    effective_time = np.maximum(0.0, time_s - 1.0 - dead_time)
    output_signal = static_gain * 0.5 * (1.0 - np.exp(-effective_time / time_constant))
    if inverse_response_severity > 0.0:
        output_signal -= (
            inverse_response_severity
            * static_gain
            * 0.5
            * np.exp(-np.maximum(0.0, time_s - 1.0) / 0.8)
        )
        output_signal[time_s < 1.0] = 0.0
    return time_s, input_signal, output_signal


def modal_trace(
    omega_rad_s: float,
    damping_ratio: float = 0.08,
    duration_s: float = 8.0,
    sample_count: int = 1600,
) -> tuple[np.ndarray, np.ndarray]:
    time_s = np.linspace(0.0, duration_s, sample_count)
    output_signal = np.exp(-damping_ratio * omega_rad_s * time_s) * np.cos(
        omega_rad_s * time_s
    )
    return time_s, output_signal


def pulse_trace(
    gain: float,
    duration_s: float = 3.0,
    sample_count: int = 900,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    time_s = np.linspace(0.0, duration_s, sample_count)
    input_signal = np.zeros_like(time_s)
    input_signal[(time_s >= 0.4) & (time_s <= 0.6)] = 0.5
    input_signal[(time_s >= 1.5) & (time_s <= 1.7)] = -0.5
    return time_s, input_signal, gain * input_signal


def hover_trace(
    hover_thrust: float,
    duration_s: float = 8.0,
    sample_count: int = 800,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    time_s = np.linspace(0.0, duration_s, sample_count)
    thrust = np.clip(hover_thrust * time_s / 5.0, 0.0, 1.2 * hover_thrust)
    lift = (thrust >= hover_thrust).astype(float)
    return time_s, thrust, lift


def vtol_pulse_trace(
    angular_acceleration_gain: float,
    lateral_coupling_gain: float,
    duration_s: float = 3.0,
    sample_count: int = 900,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    time_s = np.linspace(0.0, duration_s, sample_count)
    command = np.zeros_like(time_s)
    command[(time_s >= 0.4) & (time_s <= 0.6)] = 0.4
    command[(time_s >= 1.5) & (time_s <= 1.7)] = -0.4
    angular_acceleration = angular_acceleration_gain * command
    tilt = 0.04 * command
    lateral_acceleration = -abs(lateral_coupling_gain) * tilt
    return time_s, command, angular_acceleration, tilt, lateral_acceleration


def bounded_scan_trace(
    coupling_gain: float,
    duration_s: float = 8.0,
    sample_count: int = 800,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    time_s = np.linspace(0.0, duration_s, sample_count)
    input_signal = np.zeros_like(time_s)
    input_signal[(time_s >= 1.0) & (time_s <= 4.0)] = 0.5
    primary_output = 2.0 * input_signal
    coupled_output = coupling_gain * primary_output
    return time_s, input_signal, primary_output, coupled_output
