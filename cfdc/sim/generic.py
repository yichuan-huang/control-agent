from __future__ import annotations

from collections import deque

from cfdc.models import (
    BenchmarkRouteIR,
    ControllerCandidate,
    SimulationPerformanceSummary,
)
from cfdc.performance import build_performance_summary, calculate_channel_performance


SCALAR_BENCHMARK_FAMILIES = {
    "first_order_lag",
    "first_order_plus_dead_time",
    "double_integrator",
    "second_order_oscillator",
    "inverse_response",
    "unstable_second_order",
}


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def run_scalar_closed_loop(
    route: BenchmarkRouteIR,
    controller: ControllerCandidate,
) -> SimulationPerformanceSummary:
    """Execute a typed low-order benchmark route with shared performance gates."""

    if route.plant_family not in SCALAR_BENCHMARK_FAMILIES:
        raise ValueError(f"unsupported scalar benchmark family: {route.plant_family}")

    params = route.plant_params
    dt_s = route.dt_s
    reference = route.reference["output"]
    input_min = route.actuator_limits["input_min"]
    input_max = route.actuator_limits["input_max"]
    gains = controller.gains
    steps = int(round(route.horizon_s / dt_s))

    y = route.initial_state.get("output", 0.0)
    velocity = route.initial_state.get("velocity", 0.0)
    slow_state = route.initial_state.get("slow_state", 0.0)
    inverse_state = route.initial_state.get("inverse_state", 0.0)
    previous_input = 0.0
    integral = 0.0
    saturated_count = 0
    time_values: list[float] = []
    output_values: list[float] = []
    velocity_values: list[float] = []
    input_values: list[float] = []

    delay_steps = max(0, int(round(params.get("dead_time", 0.0) / dt_s)))
    delay_buffer: deque[float] = deque([0.0] * delay_steps)

    for step in range(steps + 1):
        time_s = step * dt_s
        if route.plant_family == "inverse_response":
            y = slow_state - params["inverse_response_severity"] * inverse_state

        error = reference - y
        integral_candidate = integral + error * dt_s
        if route.plant_family in {
            "double_integrator",
            "second_order_oscillator",
            "unstable_second_order",
        }:
            raw_input = gains.get("kp", 0.0) * error - gains.get("kd", 0.0) * velocity
        else:
            raw_input = (
                gains.get("kp", 0.0) * error + gains.get("ki", 0.0) * integral_candidate
            )
        control = _clamp(raw_input, input_min, input_max)
        saturated = abs(control - raw_input) > 1e-12
        saturated_count += int(saturated)
        if not saturated:
            integral = integral_candidate

        time_values.append(time_s)
        output_values.append(y)
        velocity_values.append(velocity)
        input_values.append(control)

        if step == steps:
            continue
        if route.plant_family in {"first_order_lag", "first_order_plus_dead_time"}:
            delay_buffer.append(control)
            applied_input = delay_buffer.popleft()
            y += dt_s * (
                (-y + params["static_gain"] * applied_input) / params["time_constant"]
            )
        elif route.plant_family == "double_integrator":
            acceleration = params["input_gain"] * control
            velocity += dt_s * acceleration
            y += dt_s * velocity
        elif route.plant_family == "second_order_oscillator":
            omega = params["natural_frequency"]
            damping = params["damping_ratio"]
            acceleration = (
                params["input_gain"] * control
                - 2.0 * damping * omega * velocity
                - omega**2 * y
            )
            velocity += dt_s * acceleration
            y += dt_s * velocity
        elif route.plant_family == "unstable_second_order":
            omega = params["natural_frequency"]
            acceleration = params["input_gain"] * control + omega**2 * y
            velocity += dt_s * acceleration
            y += dt_s * velocity
        else:
            slow_state += dt_s * (
                (-slow_state + params["static_gain"] * control)
                / params["time_constant"]
            )
            inverse_state += params["static_gain"] * (control - previous_input)
            inverse_state += dt_s * (-inverse_state / params["inverse_time_constant"])
            previous_input = control

    channel = calculate_channel_performance(
        time_values,
        reference,
        output_values,
        settling_band_absolute=route.performance_limits.get(
            "settling_band_absolute", 0.02
        ),
    )
    saturation_fraction = saturated_count / max(1, len(time_values))
    state_boundaries = {
        "max_abs_output": max(abs(value) for value in output_values),
        "max_abs_velocity": max(abs(value) for value in velocity_values),
        "max_abs_output_after_4s": max(
            (
                abs(value)
                for time_s, value in zip(time_values, output_values)
                if time_s >= 4.0
            ),
            default=0.0,
        ),
        "max_abs_input": max(abs(value) for value in input_values),
    }
    limits = {
        **route.performance_limits,
        **route.state_limits,
        **route.actuator_limits,
    }
    violations: list[str] = []
    if channel.abs_final_error > route.performance_limits.get(
        "max_abs_final_error", float("inf")
    ):
        violations.append("final_error_limit")
    if channel.overshoot > route.performance_limits.get("max_overshoot", float("inf")):
        violations.append("overshoot_limit")
    if not channel.settled:
        violations.append("output_not_settled")
    elif (
        channel.settling_time_s is not None
        and channel.settling_time_s
        > route.performance_limits.get("max_settling_time_s", float("inf"))
    ):
        violations.append("settling_time_limit")
    if saturation_fraction > route.performance_limits.get(
        "max_saturation_fraction", float("inf")
    ):
        violations.append("saturation_fraction_limit")
    for boundary_name in [
        "max_abs_output",
        "max_abs_velocity",
        "max_abs_output_after_4s",
    ]:
        if (
            boundary_name in route.state_limits
            and state_boundaries[boundary_name] > route.state_limits[boundary_name]
        ):
            violations.append(f"{boundary_name}_limit")

    return build_performance_summary(
        primary_channel="output",
        channels={"output": channel},
        actuator_saturation_fractions={"input": saturation_fraction},
        state_boundaries=state_boundaries,
        limits=limits,
        violations=violations,
        success=not violations,
    )
