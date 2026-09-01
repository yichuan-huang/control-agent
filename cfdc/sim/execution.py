"""Actual sampled execution; contains no task-performance scoring logic.

Plant realizations are private provider state. Only measured samples leave this
module. Fractional input delays are integrated at their actual switching times.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from itertools import pairwise
from typing import Any, Protocol

import numpy as np
from scipy import linalg, signal


class Plant(Protocol):
    def measure(self) -> dict[str, float]: ...

    def advance(self, command: Mapping[str, float], dt: float) -> None: ...


@dataclass
class LinearPlant:
    """Strictly proper continuous LTI realization with exact ZOH integration."""

    a: np.ndarray
    b: np.ndarray
    c: np.ndarray
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    delays: Mapping[str, float] = field(default_factory=dict)
    initial_state: Sequence[float] | None = None
    _time: float = field(init=False, default=0.0)
    _history: list[tuple[float, np.ndarray]] = field(init=False, default_factory=list)
    _cache: dict[float, tuple[np.ndarray, np.ndarray]] = field(
        init=False, default_factory=dict
    )
    _state: np.ndarray = field(init=False)

    def __post_init__(self) -> None:
        self.a, self.b, self.c = (
            np.array(value, dtype=float, copy=True)
            for value in (self.a, self.b, self.c)
        )
        n = self.a.shape[0]
        if (
            self.a.shape != (n, n)
            or self.b.shape != (n, len(self.inputs))
            or self.c.shape != (len(self.outputs), n)
        ):
            raise ValueError("plant_realization_shape_mismatch")
        if not all(np.all(np.isfinite(value)) for value in (self.a, self.b, self.c)):
            raise ValueError("plant_realization_nonfinite")
        if any(
            not math.isfinite(float(value)) or float(value) < 0
            for value in self.delays.values()
        ) or not set(self.delays) <= set(self.inputs):
            raise ValueError("plant_delay_invalid")
        self._state = (
            np.zeros(n)
            if self.initial_state is None
            else np.array(self.initial_state, dtype=float, copy=True)
        )
        if self._state.shape != (n,) or not np.all(np.isfinite(self._state)):
            raise ValueError("plant_initial_state_invalid")

    @classmethod
    def from_transfer_matrix(
        cls,
        matrix: Sequence[Sequence[tuple[Sequence[float], Sequence[float]]]],
        *,
        inputs: tuple[str, ...],
        outputs: tuple[str, ...],
        delays: Mapping[str, float] | None = None,
    ) -> LinearPlant:
        if len(matrix) != len(outputs) or any(
            len(row) != len(inputs) for row in matrix
        ):
            raise ValueError("plant_transfer_matrix_shape_mismatch")
        systems = []
        for row, entries in enumerate(matrix):
            for column, (numerator, denominator) in enumerate(entries):
                a, b, c, d = signal.tf2ss(numerator, denominator)
                if np.any(np.abs(d) > 1e-14):
                    raise ValueError("plant_algebraic_feedthrough_not_supported")
                systems.append((row, column, a, b, c))
        total = sum(system[2].shape[0] for system in systems)
        a = linalg.block_diag(*(system[2] for system in systems))
        b = np.zeros((total, len(inputs)))
        c = np.zeros((len(outputs), total))
        offset = 0
        for row, column, branch_a, branch_b, branch_c in systems:
            end = offset + len(branch_a)
            b[offset:end, column] = branch_b[:, 0]
            c[row, offset:end] = branch_c[0]
            offset = end
        return cls(a, b, c, inputs, outputs, delays or {})

    def measure(self) -> dict[str, float]:
        return dict(zip(self.outputs, map(float, self.c @ self._state), strict=True))

    def _zoh(self, duration: float) -> tuple[np.ndarray, np.ndarray]:
        key = round(duration, 13)
        if key not in self._cache:
            n, m = self.b.shape
            augmented = np.zeros((n + m, n + m))
            augmented[:n, :n] = self.a
            augmented[:n, n:] = self.b
            exponential = linalg.expm(augmented * duration)
            self._cache[key] = exponential[:n, :n], exponential[:n, n:]
        return self._cache[key]

    def advance(self, command: Mapping[str, float], dt: float) -> None:
        if set(command) != set(self.inputs) or not math.isfinite(dt) or dt <= 0:
            raise ValueError("plant_command_or_sample_time_invalid")
        values = np.array([command[name] for name in self.inputs], dtype=float)
        if not np.all(np.isfinite(values)):
            raise ValueError("plant_command_nonfinite")
        self._history.append((self._time, values))
        end = self._time + dt
        boundaries = {self._time, end}
        for time, _ in self._history:
            for name in self.inputs:
                arrival = time + float(self.delays.get(name, 0.0))
                if self._time + 1e-12 < arrival < end - 1e-12:
                    boundaries.add(arrival)
        ordered = sorted(boundaries)
        for left, right in pairwise(ordered):
            applied = np.zeros(len(self.inputs))
            for column, name in enumerate(self.inputs):
                source_time = left - float(self.delays.get(name, 0.0))
                for time, past in reversed(self._history):
                    if time <= source_time + 1e-12:
                        applied[column] = past[column]
                        break
            ad, bd = self._zoh(right - left)
            self._state = ad @ self._state + bd @ applied
        self._time = end
        # Keep the one predecessor needed by the longest delay, so long runs
        # use bounded history and do not acquire quadratic simulation cost.
        threshold = end - max(self.delays.values(), default=0.0) - dt
        while len(self._history) > 2 and self._history[1][0] < threshold:
            self._history.pop(0)


@dataclass
class OscillatorPlant:
    """Local amplitude-dependent oscillator for public release experiments.

    q'' + (d0+d2*q²)q' + wn²*q = b*u. A negative d0 and positive d2
    represent a self-excited local oscillator. The coefficients never appear
    in emitted trace metadata or controller contexts.
    """

    natural_frequency: float
    damping_constant: float
    damping_quadratic: float
    input_gain: float
    input_name: str = "u"
    position_name: str = "position"
    velocity_name: str = "velocity"
    initial_position: float = 0.0
    initial_velocity: float = 0.0
    _state: np.ndarray = field(init=False)

    def __post_init__(self) -> None:
        self._state = np.array(
            [self.initial_position, self.initial_velocity], dtype=float
        )

    def measure(self) -> dict[str, float]:
        return {
            self.position_name: float(self._state[0]),
            self.velocity_name: float(self._state[1]),
        }

    def advance(self, command: Mapping[str, float], dt: float) -> None:
        u = float(command[self.input_name])

        def rhs(state: np.ndarray) -> np.ndarray:
            q, velocity = state
            return np.array(
                [
                    velocity,
                    self.input_gain * u
                    - self.natural_frequency**2 * q
                    - (self.damping_constant + self.damping_quadratic * q * q)
                    * velocity,
                ]
            )

        # RK4 substeps cap the integration step by the natural period scale;
        # controller sampling remains exactly the requested dt.
        count = max(1, math.ceil(dt * self.natural_frequency / 0.025))
        h = dt / count
        for _ in range(count):
            k1 = rhs(self._state)
            k2 = rhs(self._state + h * k1 / 2)
            k3 = rhs(self._state + h * k2 / 2)
            k4 = rhs(self._state + h * k3)
            self._state += h * (k1 + 2 * k2 + 2 * k3 + k4) / 6


@dataclass
class CartPoleLocalPlant:
    """Registered local balance chart; it makes no swing-up claim."""

    unstable_rate: float = 1.0
    input_gain: float = 1.0
    input_name: str = "u"
    state: np.ndarray = field(default_factory=lambda: np.zeros(4))

    def measure(self) -> dict[str, float]:
        return dict(
            zip(
                ("x", "x_dot", "theta", "theta_dot"),
                map(float, self.state),
                strict=True,
            )
        )

    def advance(self, command: Mapping[str, float], dt: float) -> None:
        u = float(command[self.input_name])
        x, velocity, theta, angular_rate = self.state
        acceleration = u - 0.15 * velocity
        angular_acceleration = (
            self.unstable_rate**2 * theta + self.input_gain * u - 0.1 * angular_rate
        )
        self.state = np.array(
            [
                x + dt * velocity,
                velocity + dt * acceleration,
                theta + dt * angular_rate,
                angular_rate + dt * angular_acceleration,
            ]
        )


@dataclass
class VTOLLocalPlant:
    """Planar near-hover chart with lateral, altitude and pitch states."""

    mass: float = 1.0
    inertia: float = 0.2
    gravity: float = 9.81
    state: np.ndarray = field(default_factory=lambda: np.zeros(6))

    def measure(self) -> dict[str, float]:
        return dict(
            zip(
                (
                    "x_m",
                    "z_m",
                    "pitch_rad",
                    "x_velocity_m_s",
                    "z_velocity_m_s",
                    "pitch_rate_rad_s",
                ),
                map(float, self.state),
                strict=True,
            )
        )

    def advance(self, command: Mapping[str, float], dt: float) -> None:
        thrust = float(command["thrust_n"])
        torque = float(command["torque_n_m"])
        x, z, pitch, vx, vz, pitch_rate = self.state
        ax = -thrust * math.sin(pitch) / self.mass
        az = thrust * math.cos(pitch) / self.mass - self.gravity
        angular_acceleration = torque / self.inertia
        self.state = np.array(
            [
                x + dt * vx,
                z + dt * vz,
                pitch + dt * pitch_rate,
                vx + dt * ax,
                vz + dt * az,
                pitch_rate + dt * angular_acceleration,
            ]
        )


@dataclass
class StaticMapPlant:
    """Hammerstein first-order channel with memory-free static input map."""

    tau: float
    linear: float
    cubic: float = 0.0
    positive_deadzone: float = 0.0
    negative_deadzone: float = 0.0
    input_name: str = "u"
    output_name: str = "y"
    value: float = 0.0

    def measure(self) -> dict[str, float]:
        return {self.output_name: self.value}

    def advance(self, command: Mapping[str, float], dt: float) -> None:
        u = float(command[self.input_name])
        shifted = (
            max(u - self.positive_deadzone, 0)
            if u >= 0
            else min(u + self.negative_deadzone, 0)
        )
        mapped = self.linear * shifted + self.cubic * shifted**3
        alpha = math.exp(-dt / self.tau)
        self.value = alpha * self.value + (1 - alpha) * mapped


def simulate_trial(
    request: Mapping[str, Any], scenario: Mapping[str, Any], plant: Plant
) -> dict[str, Any]:
    """Execute frozen commands against a plant, never read scoring thresholds."""
    from cfdc.controllers.execution import ControllerRuntime

    dt = float(request["sample_time_s"])
    horizon = float(request["horizon_s"])
    if not math.isfinite(dt) or not math.isfinite(horizon) or dt <= 0 or horizon <= 0:
        raise ValueError("execution_time_invalid")
    count = math.ceil(horizon / dt)
    if count > 1_000_000:
        raise ValueError("execution_sample_budget_exceeded")
    times = np.linspace(0.0, horizon, count + 1)
    actual_dt = float(times[1])
    runtime = ControllerRuntime(
        request["controller"], input_bounds=request["input_bounds"]
    )
    tracked = tuple(request["tracked_signals"])
    inputs = tuple(request["control_inputs"])
    trace: dict[str, Any] = {
        "time_s": [],
        "outputs": {name: [] for name in tracked},
        "measurements": {name: [] for name in request["measured_signals"]},
        "references": {name: [] for name in tracked},
        "control_inputs": {name: [] for name in inputs},
        "raw_control_inputs": {name: [] for name in inputs},
        "controller_states": [],
        "phase_ids": [],
    }
    events: list[dict[str, Any]] = []
    stop = {"triggered": False, "time_s": horizon, "reason": "horizon_complete"}
    references = dict(request["references"])
    phases = list(request.get("phases", []))
    phase_index = 0
    phase_entered = 0.0
    band_entered: float | None = None
    disturbance = scenario.get("disturbance", request.get("disturbance"))
    disturbance_recorded = False
    previous_sample = None
    for index, time in enumerate(times):
        t = float(time)
        measured = plant.measure()
        if not all(math.isfinite(value) for value in measured.values()):
            # Last finite sample is the only admissible end of an aborted
            # packet. Never replace a NaN with a fabricated measurement.
            stop = {
                "triggered": True,
                "time_s": trace["time_s"][-1] if trace["time_s"] else 0.0,
                "reason": "numerical_failure",
            }
            break
        phase_id = phases[phase_index]["phase_id"] if phases else "hold"
        if phases:
            phase = phases[phase_index]
            references.update(phase["references"])
            predicate = phase["exit_predicate"]
            if predicate["kind"] != "within_band":
                raise ValueError("unregistered_phase_predicate")
            within = abs(
                measured[predicate["signal"]] - float(predicate["target"])
            ) <= float(predicate["tolerance"])
            hysteresis = float(phase.get("hysteresis", 0.0))
            if (
                band_entered is not None
                and abs(measured[predicate["signal"]] - float(predicate["target"]))
                > float(predicate["tolerance"]) + hysteresis
            ):
                band_entered = None
            if within and band_entered is None:
                band_entered = t
            if (
                band_entered is not None
                and t - band_entered >= float(phase["dwell_s"]) - 1e-10
                and phase_index < len(phases) - 1
            ):
                before = previous_sample.state if previous_sample is not None else {}
                old_id = phase_id
                phase_index += 1
                phase = phases[phase_index]
                phase_id = phase["phase_id"]
                if phase["state_policy"] == "reset":
                    runtime.reset()
                elif phase["state_policy"] != "inherit":
                    raise ValueError("unregistered_phase_state_policy")
                references.update(phase["references"])
                phase_entered, band_entered = t, None
                events.append(
                    {
                        "kind": "handoff",
                        "time_s": t,
                        "sample_index": index,
                        "state_policy": phase["state_policy"],
                        "state_on_entry": {}
                        if phase["state_policy"] == "reset"
                        else dict(before),
                        "from_phase": old_id,
                        "to_phase": phase_id,
                        "state_before": dict(before),
                        "state_after": {},
                        "command_before": dict(previous_sample.control)
                        if previous_sample is not None
                        else {},
                        "command_after": {},
                    }
                )
            elif t - phase_entered > float(phase["timeout_s"]) + 1e-10:
                stop = {"triggered": True, "time_s": t, "reason": "phase_timeout"}
        sample = runtime.step(measured, references, actual_dt)
        if events and events[-1].get("kind") == "handoff" and events[-1]["time_s"] == t:
            events[-1].update(
                state_after=dict(sample.state), command_after=dict(sample.control)
            )
        for event in sample.events:
            events.append({**dict(event), "time_s": t})
        trace["time_s"].append(t)
        for name in request["measured_signals"]:
            trace["measurements"][name].append(float(measured[name]))
        for name in tracked:
            trace["outputs"][name].append(float(measured[name]))
            trace["references"][name].append(float(references[name]))
        for name in inputs:
            trace["control_inputs"][name].append(float(sample.control[name]))
            trace["raw_control_inputs"][name].append(float(sample.raw_control[name]))
        trace["controller_states"].append(dict(sample.state))
        trace["phase_ids"].append(phase_id)
        previous_sample = sample
        if (
            any(
                abs(value) > float(request["state_stop"]) for value in measured.values()
            )
            if request.get("state_stop") is not None
            else False
        ):
            stop = {"triggered": True, "time_s": t, "reason": "state_limit"}
        for name, bounds in request.get("state_bounds", {}).items():
            if not float(bounds[0]) <= measured[name] <= float(bounds[1]):
                stop = {"triggered": True, "time_s": t, "reason": "state_limit"}
        for name, bounds in request.get("controller_state_bounds", {}).items():
            if not float(bounds[0]) <= float(sample.state[name]) <= float(bounds[1]):
                stop = {
                    "triggered": True,
                    "time_s": t,
                    "reason": "controller_state_limit",
                }
        for name, bounds in request.get("output_bounds", {}).items():
            if not float(bounds[0]) <= measured[name] <= float(bounds[1]):
                stop = {"triggered": True, "time_s": t, "reason": "output_limit"}
        if stop["triggered"] or index == count:
            break
        applied = dict(sample.control)
        # Disturbances are physical input additions, not edits to the output
        # trace. Split integration at event boundaries even between samples.
        boundaries = [t, float(times[index + 1])]
        if disturbance:
            start = float(disturbance["time_s"])
            end = start + float(disturbance["duration_s"])
            boundaries.extend(
                point for point in (start, end) if t < point < times[index + 1]
            )
            if not disturbance_recorded and t <= start < times[index + 1]:
                events.append(
                    {"kind": "disturbance", **dict(disturbance), "sample_index": index}
                )
                disturbance_recorded = True
        ordered = sorted(set(boundaries))
        for left, right in pairwise(ordered):
            part = dict(applied)
            if disturbance and start <= left < end:
                part[str(disturbance["channel"])] += float(disturbance["amplitude"])
            plant.advance(part, right - left)
    return {
        "trial_id": scenario["trial_id"],
        "scenario_id": scenario["scenario_id"],
        "seed": scenario["seed"],
        "trajectory": trace,
        "stop_event": stop,
        "events": events,
    }
