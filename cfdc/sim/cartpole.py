from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import math

import numpy as np
from scipy.linalg import solve_continuous_are

from cfdc.models import (
    CartpoleSimulationResult,
    CartpoleState,
    OnlinePerformanceMetrics,
    SafeGainSearchState,
    TrialReport,
)
from cfdc.performance import build_performance_summary, calculate_channel_performance
from cfdc.sim.integrators import rk4_step


@dataclass(frozen=True)
class CartpoleParams:
    """CTMS-style cartpole settings used by the archived CFDC simulation."""

    cart_mass_kg: float = 0.5
    pole_mass_kg: float = 0.2
    com_length_m: float = 0.3
    pole_inertia_kg_m2: float = 0.006
    cart_friction_n_s_m: float = 0.1
    gravity_m_s2: float = 9.8
    force_limit_n: float = 10.0
    cart_position_limit_m: float = 2.4

    @property
    def effective_inertia_kg_m2(self) -> float:
        return self.pole_inertia_kg_m2 + self.pole_mass_kg * self.com_length_m**2

    @property
    def free_cart_natural_frequency_down_rad_s(self) -> float:
        denominator = self.effective_inertia_kg_m2 - (
            self.pole_mass_kg * self.com_length_m
        ) ** 2 / (self.cart_mass_kg + self.pole_mass_kg)
        return math.sqrt(self.pole_mass_kg * self.gravity_m_s2 * self.com_length_m / denominator)


@dataclass(frozen=True)
class CartpoleSwingupConfig:
    duration_s: float = 12.0
    dt_s: float = 0.002
    initial_angle_from_upright_rad: float = math.pi - 0.08
    capture_angle_rad: float = 0.35
    capture_rate_rad_s: float = 7.0
    normalized_energy_gain: float = 0.72
    swing_cart_position_gain: float = 0.7
    swing_cart_velocity_gain: float = 1.2
    pd_kp_step: float = 0.05
    pd_kd_step: float = 0.05
    pd_kp_update_period_s: float = 1.0
    pd_kd_update_period_s: float = 1.0
    pd_kp_max: float = 90.0
    pd_kd_max: float = 18.0
    pd_initial_kd_multiplier: float = 0.01
    pd_target_angle_rad: float = 0.12
    pd_target_rate_rad_s: float = 0.12
    pd_min_kp_before_damping: float = 20.0
    pd_min_kd_before_hold: float = 4.0
    pd_kd_hold_improvement_ratio: float = 0.9
    pd_kd_hold_timeout_s: float = 3.0
    pd_settle_time_s: float = 0.8
    outer_reference_m: float = 0.2
    outer_theta_ref_limit_rad: float = 0.08
    outer_kpy_initial: float = 0.01
    outer_kdy_initial: float = 0.02
    max_force_saturation_fraction: float = 0.30


def _wrap_angle(angle_rad: float) -> float:
    return (angle_rad + math.pi) % (2.0 * math.pi) - math.pi


def _dynamics(state: np.ndarray, force_n: float, params: CartpoleParams) -> np.ndarray:
    x, x_dot, theta, theta_dot = state
    del x
    cos_theta = math.cos(theta)
    sin_theta = math.sin(theta)
    mass_matrix = np.array(
        [
            [params.cart_mass_kg + params.pole_mass_kg, params.pole_mass_kg * params.com_length_m * cos_theta],
            [params.pole_mass_kg * params.com_length_m * cos_theta, params.effective_inertia_kg_m2],
        ],
        dtype=float,
    )
    rhs = np.array(
        [
            force_n
            - params.cart_friction_n_s_m * x_dot
            + params.pole_mass_kg * params.com_length_m * sin_theta * theta_dot**2,
            params.pole_mass_kg * params.gravity_m_s2 * params.com_length_m * sin_theta,
        ],
        dtype=float,
    )
    x_ddot, theta_ddot = np.linalg.solve(mass_matrix, rhs)
    return np.array([x_dot, x_ddot, theta_dot, theta_ddot], dtype=float)


def _rk4_step(state: np.ndarray, force_n: float, dt_s: float, params: CartpoleParams) -> np.ndarray:
    next_state = rk4_step(_dynamics, state, dt_s, force_n, params)
    next_state[2] = _wrap_angle(float(next_state[2]))
    return next_state


def cartpole_energy_relative_to_upright(state: np.ndarray, params: CartpoleParams) -> float:
    theta = float(state[2])
    theta_dot = float(state[3])
    return 0.5 * params.effective_inertia_kg_m2 * theta_dot**2 + (
        params.pole_mass_kg * params.gravity_m_s2 * params.com_length_m * (math.cos(theta) - 1.0)
    )


def _linearize_upright(params: CartpoleParams) -> tuple[np.ndarray, np.ndarray]:
    state0 = np.zeros(4, dtype=float)
    force0 = 0.0
    eps = 1e-6
    a_mat = np.zeros((4, 4), dtype=float)
    b_mat = np.zeros((4, 1), dtype=float)
    for col in range(4):
        delta = np.zeros(4, dtype=float)
        delta[col] = eps
        a_mat[:, col] = (
            _dynamics(state0 + delta, force0, params)
            - _dynamics(state0 - delta, force0, params)
        ) / (2.0 * eps)
    b_mat[:, 0] = (
        _dynamics(state0, force0 + eps, params)
        - _dynamics(state0, force0 - eps, params)
    ) / (2.0 * eps)
    return a_mat, b_mat


def _continuous_lqr(a_mat: np.ndarray, b_mat: np.ndarray, q_mat: np.ndarray, r_mat: np.ndarray) -> np.ndarray:
    riccati = solve_continuous_are(a_mat, b_mat, q_mat, r_mat)
    return np.linalg.solve(r_mat, b_mat.T @ riccati)


class _HybridEnergyLQRController:
    def __init__(self, params: CartpoleParams, config: CartpoleSwingupConfig):
        self.params = params
        self.config = config
        a_mat, b_mat = _linearize_upright(params)
        q_mat = np.diag([1.0, 1.0, 80.0, 6.0])
        r_mat = np.array([[0.2]], dtype=float)
        self.lqr_gain = _continuous_lqr(a_mat, b_mat, q_mat, r_mat)

    def command(self, state: np.ndarray) -> tuple[float, str]:
        x, x_dot, theta, theta_dot = [float(value) for value in state]
        theta = _wrap_angle(theta)
        if abs(theta) < self.config.capture_angle_rad and abs(theta_dot) < self.config.capture_rate_rad_s:
            local_state = np.array([x, x_dot, theta, theta_dot], dtype=float)
            force = -float((self.lqr_gain @ local_state).item())
            mode = "balance_lqr"
        else:
            energy_error = cartpole_energy_relative_to_upright(state, self.params)
            desired_cart_accel = 30.0 * theta_dot * math.cos(theta) * energy_error
            force = (
                (self.params.cart_mass_kg + self.params.pole_mass_kg) * desired_cart_accel
                - self.config.swing_cart_position_gain * x
                - self.config.swing_cart_velocity_gain * x_dot
            )
            mode = "energy_swingup"
        return float(np.clip(force, -self.params.force_limit_n, self.params.force_limit_n)), mode


class _ExternalCFDCEnergyPDController:
    def __init__(
        self,
        config: CartpoleSwingupConfig,
        balance_gains: dict[str, float],
        natural_frequency_rad_s: float,
        force_limit_n: float,
    ):
        self.config = config
        self.kp = float(balance_gains.get("kp", 0.0))
        self.kd = float(balance_gains.get("kd", 0.0))
        self.natural_frequency_rad_s = float(natural_frequency_rad_s)
        self.force_limit_n = float(force_limit_n)

    def _swingup_force(self, state: np.ndarray) -> float:
        x, x_dot, theta, theta_dot = [float(value) for value in state]
        energy_error = 0.5 * theta_dot**2 + self.natural_frequency_rad_s**2 * (math.cos(theta) - 1.0)
        return (
            self.config.normalized_energy_gain
            * theta_dot
            * math.cos(theta)
            * energy_error
            - self.config.swing_cart_position_gain * x
            - self.config.swing_cart_velocity_gain * x_dot
        )

    def command(self, state: np.ndarray) -> tuple[float, str]:
        x = float(state[0])
        x_dot = float(state[1])
        theta = _wrap_angle(float(state[2]))
        theta_dot = float(state[3])
        if abs(theta) < self.config.capture_angle_rad and abs(theta_dot) < self.config.capture_rate_rad_s:
            theta_ref = self.config.outer_kpy_initial * (self.config.outer_reference_m - x) - self.config.outer_kdy_initial * x_dot
            theta_ref = float(np.clip(theta_ref, -self.config.outer_theta_ref_limit_rad, self.config.outer_theta_ref_limit_rad))
            force = self.kp * (theta - theta_ref) + self.kd * theta_dot
            mode = "balance_cfdc_pd"
        else:
            force = self._swingup_force(state)
            mode = "feature_energy_swingup"
        return float(np.clip(force, -self.force_limit_n, self.force_limit_n)), mode


def _capture_state_for_search(
    natural_frequency_rad_s: float,
    params: CartpoleParams,
    config: CartpoleSwingupConfig,
) -> tuple[np.ndarray, float]:
    controller = _ExternalCFDCEnergyPDController(
        config,
        {"kp": 0.0, "kd": 0.0},
        natural_frequency_rad_s,
        params.force_limit_n,
    )
    state = np.array(
        [0.0, 0.0, _wrap_angle(config.initial_angle_from_upright_rad), 0.0],
        dtype=float,
    )
    for step in range(int(config.duration_s / config.dt_s) + 1):
        time_s = step * config.dt_s
        theta = _wrap_angle(float(state[2]))
        if abs(theta) < config.capture_angle_rad and abs(float(state[3])) < config.capture_rate_rad_s:
            return state, time_s
        force = controller._swingup_force(state)
        force = float(np.clip(force, -params.force_limit_n, params.force_limit_n))
        state = _rk4_step(state, force, config.dt_s, params)
        if abs(float(state[0])) > params.cart_position_limit_m:
            break
    raise RuntimeError("normalized-energy swing-up did not reach the capture region")


def _run_balance_candidate(
    capture_state: np.ndarray,
    gains: dict[str, float],
    params: CartpoleParams,
    config: CartpoleSwingupConfig,
    duration_s: float,
) -> dict[str, float | bool]:
    state = capture_state.copy()
    max_abs_angle = abs(_wrap_angle(float(state[2])))
    max_abs_rate = abs(float(state[3]))
    max_abs_position = abs(float(state[0]))
    saturation_count = 0
    dwell_samples = max(1, int(round(0.4 / config.dt_s)))
    dwell: list[tuple[float, float]] = []
    safe = True

    for _ in range(max(1, int(round(duration_s / config.dt_s)))):
        x, x_dot = float(state[0]), float(state[1])
        theta = _wrap_angle(float(state[2]))
        theta_dot = float(state[3])
        theta_ref = config.outer_kpy_initial * (config.outer_reference_m - x) - config.outer_kdy_initial * x_dot
        theta_ref = float(np.clip(theta_ref, -config.outer_theta_ref_limit_rad, config.outer_theta_ref_limit_rad))
        raw_force = gains["kp"] * (theta - theta_ref) + gains["kd"] * theta_dot
        force = float(np.clip(raw_force, -params.force_limit_n, params.force_limit_n))
        saturation_count += abs(raw_force) >= 0.98 * params.force_limit_n
        state = _rk4_step(state, force, config.dt_s, params)
        angle = abs(_wrap_angle(float(state[2])))
        rate = abs(float(state[3]))
        position = abs(float(state[0]))
        max_abs_angle = max(max_abs_angle, angle)
        max_abs_rate = max(max_abs_rate, rate)
        max_abs_position = max(max_abs_position, position)
        dwell.append((angle, rate))
        if len(dwell) > dwell_samples:
            dwell.pop(0)
        if position > params.cart_position_limit_m or angle > 0.70:
            safe = False
            break

    dwell_passed = len(dwell) == dwell_samples and all(
        angle <= config.pd_target_angle_rad and rate <= config.pd_target_rate_rad_s
        for angle, rate in dwell
    )
    return {
        "safe": safe,
        "dwell_passed": dwell_passed,
        "final_angle_rad": _wrap_angle(float(state[2])),
        "final_rate_rad_s": float(state[3]),
        "max_abs_angle_rad": max_abs_angle,
        "max_abs_rate_rad_s": max_abs_rate,
        "max_abs_position_m": max_abs_position,
        "saturation_fraction": saturation_count / max(1, int(round(duration_s / config.dt_s))),
    }


@lru_cache(maxsize=8)
def search_cartpole_pd_gains(
    natural_frequency_rad_s: float,
    params: CartpoleParams | None = None,
    config: CartpoleSwingupConfig | None = None,
) -> tuple[SafeGainSearchState, list[TrialReport], list[dict[str, float | str | bool]]]:
    """Search PD gains from observed nonlinear trials without using the input gain."""

    params = params or CartpoleParams()
    config = config or CartpoleSwingupConfig()
    capture_state, capture_time_s = _capture_state_for_search(natural_frequency_rad_s, params, config)
    kd = config.pd_initial_kd_multiplier * natural_frequency_rad_s
    kp = 0.0
    events: list[dict[str, float | str | bool]] = [
        {
            "event": "capture_state_recorded",
            "time_s": capture_time_s,
            "cart_position_m": float(capture_state[0]),
            "pole_angle_rad": _wrap_angle(float(capture_state[2])),
            "pole_angular_velocity_rad_s": float(capture_state[3]),
        }
    ]
    trial_index = 0

    kp_outcome: dict[str, float | bool] = {}
    while kp + config.pd_kp_step <= config.pd_kp_max:
        trial_index += 1
        kp += config.pd_kp_step
        outcome = _run_balance_candidate(
            capture_state,
            {"kp": kp, "kd": kd},
            params,
            config,
            duration_s=0.35,
        )
        critical_reached = bool(outcome["safe"]) and float(outcome["final_rate_rad_s"]) <= 0.0
        events.append(
            {
                "event": "kp_trial",
                "trial_index": trial_index,
                "time_s": capture_time_s + trial_index * config.pd_kp_update_period_s,
                "kp": kp,
                "kd": kd,
                "accepted": critical_reached,
                **outcome,
            }
        )
        if critical_reached:
            kp_outcome = outcome
            break
    else:
        raise RuntimeError("cartpole Kp search exhausted its configured limit")

    kd_outcome: dict[str, float | bool] = {}
    while kd + config.pd_kd_step <= config.pd_kd_max:
        trial_index += 1
        kd += config.pd_kd_step
        outcome = _run_balance_candidate(
            capture_state,
            {"kp": kp, "kd": kd},
            params,
            config,
            duration_s=1.5,
        )
        accepted = bool(outcome["safe"]) and bool(outcome["dwell_passed"])
        events.append(
            {
                "event": "kd_trial",
                "trial_index": trial_index,
                "time_s": (
                    capture_time_s
                    + (trial_index - 1) * config.pd_kp_update_period_s
                    + config.pd_kd_update_period_s
                ),
                "kp": kp,
                "kd": kd,
                "accepted": accepted,
                **outcome,
            }
        )
        if accepted:
            kd_outcome = outcome
            break
    else:
        raise RuntimeError("cartpole Kd search exhausted its configured limit")

    accepted_gains = {"kp": kp, "kd": kd}
    state = SafeGainSearchState(
        accepted_gains=accepted_gains,
        search_direction={"kp": 1.0, "kd": 1.0},
        step_fraction=0.05,
        trial_index=trial_index,
        status="accepted",
        history=events,
    )
    reports = [
        TrialReport(
            trial_id="cartpole_kp_search",
            accepted=True,
            stop_reason="critical_stiffness_reached",
            duration_s=0.35,
            metrics=OnlinePerformanceMetrics(
                overshoot=0.0,
                settling_time_s=None,
                integral_absolute_error=0.0,
                high_frequency_control_rms=0.0,
                actuator_saturation_fraction=float(kp_outcome.get("saturation_fraction", 0.0)),
                nmp_undershoot=0.0,
            ),
            tested_gains={"kp": kp, "kd": config.pd_initial_kd_multiplier * natural_frequency_rad_s},
            accepted_gains={"kp": kp, "kd": config.pd_initial_kd_multiplier * natural_frequency_rad_s},
        ),
        TrialReport(
            trial_id="cartpole_kd_search",
            accepted=True,
            stop_reason="upright_dwell_reached",
            duration_s=1.5,
            metrics=OnlinePerformanceMetrics(
                overshoot=0.0,
                settling_time_s=1.5,
                integral_absolute_error=0.0,
                high_frequency_control_rms=0.0,
                actuator_saturation_fraction=float(kd_outcome.get("saturation_fraction", 0.0)),
                nmp_undershoot=0.0,
            ),
            tested_gains=accepted_gains,
            accepted_gains=accepted_gains,
        ),
    ]
    return state, reports, events


class _FeatureEnergyPDController:
    def __init__(self, params: CartpoleParams, config: CartpoleSwingupConfig):
        self.params = params
        self.config = config
        self.swingup_omega_rad_s = params.free_cart_natural_frequency_down_rad_s
        self.phase = "swingup"
        self.kp = 0.0
        self.kd = config.pd_initial_kd_multiplier * self.swingup_omega_rad_s
        self.last_update_s = -float("inf")
        self.phase_start_s = 0.0
        self.settle_start_s: float | None = None
        self.kd_search_start_rate = 0.0
        self.events: list[dict[str, float | str]] = []

    def _event(self, time_s: float, event: str, state: np.ndarray) -> None:
        self.events.append(
            {
                "time_s": time_s,
                "event": event,
                "phase": self.phase,
                "kp": self.kp,
                "kd": self.kd,
                "theta_from_upright_rad": _wrap_angle(float(state[2])),
                "angular_velocity_rad_s": float(state[3]),
                "cart_position_m": float(state[0]),
            }
        )

    def _swingup_force(self, state: np.ndarray) -> float:
        x, x_dot, theta, theta_dot = [float(value) for value in state]
        energy_error = 0.5 * theta_dot**2 + self.swingup_omega_rad_s**2 * (math.cos(theta) - 1.0)
        return (
            self.config.normalized_energy_gain
            * theta_dot
            * math.cos(theta)
            * energy_error
            - self.config.swing_cart_position_gain * x
            - self.config.swing_cart_velocity_gain * x_dot
        )

    def _pd_force(self, state: np.ndarray) -> float:
        theta = _wrap_angle(float(state[2]))
        theta_dot = float(state[3])
        theta_ref = 0.0
        if self.phase == "stable_pd_outer":
            x = float(state[0])
            x_dot = float(state[1])
            theta_ref = self.config.outer_kpy_initial * (self.config.outer_reference_m - x) - self.config.outer_kdy_initial * x_dot
            theta_ref = float(np.clip(theta_ref, -self.config.outer_theta_ref_limit_rad, self.config.outer_theta_ref_limit_rad))
        return self.kp * (theta - theta_ref) + self.kd * theta_dot

    def _update_search(self, time_s: float, state: np.ndarray) -> None:
        theta = _wrap_angle(float(state[2]))
        theta_dot = float(state[3])
        if self.phase == "search_kp":
            if time_s - self.last_update_s < self.config.pd_kp_update_period_s:
                return
            if self.kp >= self.config.pd_min_kp_before_damping and abs(theta) < self.config.capture_angle_rad:
                self.phase = "search_kd"
                self.phase_start_s = time_s
                self.kd_search_start_rate = abs(theta_dot)
                self.last_update_s = time_s
                self._event(time_s, "lock_kp_start_kd_search", state)
                return
            if self.kp + self.config.pd_kp_step <= self.config.pd_kp_max:
                self.kp += self.config.pd_kp_step
                self.last_update_s = time_s
                self._event(time_s, "increase_kp", state)
            else:
                self.phase = "failed"
                self._event(time_s, "fail_kp_limit", state)
        elif self.phase == "search_kd":
            if self.kd >= self.config.pd_min_kd_before_hold and abs(theta_dot) < self.config.pd_kd_hold_improvement_ratio * self.kd_search_start_rate:
                self.phase = "test_kd"
                self.phase_start_s = time_s
                self.settle_start_s = None
                self._event(time_s, "hold_kd_candidate", state)
                return
            if time_s - self.last_update_s < self.config.pd_kd_update_period_s:
                return
            if self.kd + self.config.pd_kd_step <= self.config.pd_kd_max:
                self.kd += self.config.pd_kd_step
                self.last_update_s = time_s
                self._event(time_s, "increase_kd", state)
            else:
                self.phase = "failed"
                self._event(time_s, "fail_kd_limit", state)
        elif self.phase == "test_kd":
            if abs(theta) < self.config.pd_target_angle_rad and abs(theta_dot) < self.config.pd_target_rate_rad_s:
                if self.settle_start_s is None:
                    self.settle_start_s = time_s
                    self._event(time_s, "settle_window_started", state)
                elif time_s - self.settle_start_s >= self.config.pd_settle_time_s:
                    self.phase = "stable_pd_outer"
                    self._event(time_s, "pd_search_success", state)
                return
            self.settle_start_s = None
            if time_s - self.phase_start_s >= self.config.pd_kd_hold_timeout_s:
                self.phase = "search_kd"
                self.phase_start_s = time_s
                self.kd_search_start_rate = abs(theta_dot)
                self.last_update_s = time_s
                self._event(time_s, "resume_kd_search", state)

    def command(self, state: np.ndarray, time_s: float) -> tuple[float, str]:
        theta = _wrap_angle(float(state[2]))
        theta_dot = float(state[3])
        if self.phase == "swingup":
            if abs(theta) < self.config.capture_angle_rad and abs(theta_dot) < self.config.capture_rate_rad_s:
                self.phase = "search_kp"
                self.phase_start_s = time_s
                self.last_update_s = time_s
                self._event(time_s, "capture_start_pd_search", state)
            else:
                force = self._swingup_force(state)
                return float(np.clip(force, -self.params.force_limit_n, self.params.force_limit_n)), "feature_energy_swingup"

        if self.phase in {"search_kp", "search_kd", "test_kd", "stable_pd_outer"}:
            self._update_search(time_s, state)
            mode = f"pd_{self.phase}"
            force = self._pd_force(state)
        else:
            mode = "pd_failed"
            force = 0.0
        return float(np.clip(force, -self.params.force_limit_n, self.params.force_limit_n)), mode


def cartpole_swingup_force(
    state: np.ndarray,
    params: CartpoleParams | None = None,
    config: CartpoleSwingupConfig | None = None,
) -> tuple[float, str]:
    controller = _FeatureEnergyPDController(params or CartpoleParams(), config or CartpoleSwingupConfig())
    return controller.command(state, 0.0)


def simulate_cartpole_energy_swingup(
    initial_state: CartpoleState | None = None,
    params: CartpoleParams | None = None,
    config: CartpoleSwingupConfig | None = None,
    include_trajectory: bool = True,
    balance_gains: dict[str, float] | None = None,
    natural_frequency_rad_s: float | None = None,
    search_events: list[dict[str, int | float | str | bool | None]] | None = None,
) -> CartpoleSimulationResult:
    params = params or CartpoleParams()
    config = config or CartpoleSwingupConfig()
    controller = (
        _ExternalCFDCEnergyPDController(
            config,
            balance_gains,
            natural_frequency_rad_s or params.free_cart_natural_frequency_down_rad_s,
            params.force_limit_n,
        )
        if balance_gains is not None
        else _HybridEnergyLQRController(params, config)
    )
    start = initial_state or CartpoleState(
        cart_position_m=0.0,
        cart_velocity_m_s=0.0,
        pole_angle_rad=config.initial_angle_from_upright_rad,
        pole_angular_velocity_rad_s=0.0,
    )
    state = np.array(
        [start.cart_position_m, start.cart_velocity_m_s, _wrap_angle(start.pole_angle_rad), start.pole_angular_velocity_rad_s],
        dtype=float,
    )
    records: list[dict[str, float | str]] = []
    max_abs_x = abs(float(state[0]))
    max_abs_force = 0.0
    handoff_time: float | None = None
    stop_reason = "duration_elapsed"
    balance_hold_samples = 0
    balance_start_s: float | None = None
    balance_max_angle = 0.0
    balance_max_rate = 0.0
    saturated_samples = 0
    required_balance_samples = max(1, int(round(0.4 / config.dt_s)))
    steps = int(config.duration_s / config.dt_s)

    for step in range(steps + 1):
        time_s = step * config.dt_s
        if abs(float(state[0])) > params.cart_position_limit_m:
            stop_reason = "cart_position_limit_exceeded"
            break
        force, phase = controller.command(state)
        max_abs_force = max(max_abs_force, abs(force))
        saturated_samples += abs(force) >= 0.98 * params.force_limit_n
        theta = _wrap_angle(float(state[2]))
        records.append(
            {
                "time_s": time_s,
                "cart_position_m": float(state[0]),
                "cart_velocity_m_s": float(state[1]),
                "pole_angle_rad": theta,
                "pole_angular_velocity_rad_s": float(state[3]),
                "force_n": force,
                "phase": phase,
            }
        )
        if phase in {"balance_lqr", "balance_cfdc_pd"}:
            balance_start_s = time_s if balance_start_s is None else balance_start_s
            balance_max_angle = max(balance_max_angle, abs(theta))
            balance_max_rate = max(balance_max_rate, abs(float(state[3])))
        stable_window = phase in {"balance_lqr", "balance_cfdc_pd"} and abs(theta) < 0.12 and abs(float(state[3])) < 1.0
        balance_hold_samples = balance_hold_samples + 1 if stable_window else 0
        if handoff_time is None and balance_hold_samples >= required_balance_samples:
            handoff_time = time_s - (required_balance_samples - 1) * config.dt_s
            stop_reason = "upright_handoff_window_reached"
            break
        if step < steps:
            state = _rk4_step(state, force, config.dt_s, params)
            max_abs_x = max(max_abs_x, abs(float(state[0])))
    if handoff_time is None and balance_gains is not None:
        stop_reason = "cfdc_final_gains_failed_handoff"

    final_state = CartpoleState(
        cart_position_m=float(state[0]),
        cart_velocity_m_s=float(state[1]),
        pole_angle_rad=_wrap_angle(float(state[2])),
        pole_angular_velocity_rad_s=float(state[3]),
    )
    force_saturation_fraction = saturated_samples / max(1, len(records))
    capture_success = handoff_time is not None
    violations: list[str] = []
    if not capture_success:
        violations.append("capture_failed")
    if max_abs_x > params.cart_position_limit_m:
        violations.append("cart_position_limit")
    if max_abs_force > params.force_limit_n + 1e-9:
        violations.append("force_limit")
    if force_saturation_fraction > config.max_force_saturation_fraction:
        violations.append("force_saturation_fraction")
    success = not violations
    time_s = [float(row["time_s"]) for row in records]
    channels = {
        "pole_angle": calculate_channel_performance(
            time_s,
            0.0,
            [float(row["pole_angle_rad"]) for row in records],
            settling_band_fraction=0.02,
            settling_band_absolute=config.pd_target_angle_rad,
        ),
        "cart_position": calculate_channel_performance(
            time_s,
            config.outer_reference_m,
            [float(row["cart_position_m"]) for row in records],
            settling_band_fraction=0.02,
            settling_band_absolute=0.02,
        ),
    }
    performance = build_performance_summary(
        primary_channel="pole_angle",
        channels=channels,
        actuator_saturation_fractions={"force": force_saturation_fraction},
        state_boundaries={
            "max_abs_cart_position_m": max_abs_x,
            "max_abs_force_n": max_abs_force,
            "balance_max_abs_angle_rad": balance_max_angle,
            "balance_max_abs_rate_rad_s": balance_max_rate,
        },
        limits={
            "max_abs_cart_position_m": params.cart_position_limit_m,
            "max_abs_force_n": params.force_limit_n,
            "max_force_saturation_fraction": config.max_force_saturation_fraction,
            "capture_angle_rad": config.pd_target_angle_rad,
            "capture_rate_rad_s": 1.0,
        },
        violations=violations,
        success=success,
        capture_success=capture_success,
        capture_time_s=handoff_time,
    )
    return CartpoleSimulationResult(
        success=success,
        stop_reason=stop_reason,
        handoff_time_s=handoff_time,
        final_state=final_state,
        max_abs_cart_position_m=max_abs_x,
        max_abs_force_n=max_abs_force,
        sample_count=len(records),
        performance=performance,
        metrics={
            "final_error": performance.final_error,
            "abs_final_error": performance.abs_final_error,
            "overshoot": performance.overshoot,
            "settled": performance.settled,
            "settling_time_s": performance.settling_time_s,
            "final_output": performance.final_output,
            "saturation_fraction": performance.saturation_fraction,
            "success": performance.success,
            "capture_success": capture_success,
            "capture_time_s": handoff_time,
            "balance_start_time_s": balance_start_s if balance_start_s is not None else -1.0,
            "upright_dwell_time_s": 0.4 if handoff_time is not None else 0.0,
            "balance_max_abs_angle_rad": balance_max_angle,
            "balance_max_abs_rate_rad_s": balance_max_rate,
            "force_saturation_fraction": force_saturation_fraction,
            "max_abs_cart_position_m": max_abs_x,
        },
        events=list(search_events or []),
        final_gains=dict(balance_gains or {}),
        trajectory=records if include_trajectory else [],
    )
