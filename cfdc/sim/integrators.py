from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np

DynamicsFn = Callable[..., np.ndarray]


def rk4_step(
    dynamics: DynamicsFn,
    state: np.ndarray,
    dt_s: float,
    *dynamics_args: Any,
) -> np.ndarray:
    """Advance one fixed step while holding control inputs constant."""

    if dt_s <= 0.0:
        raise ValueError("dt_s must be positive")
    k1 = dynamics(state, *dynamics_args)
    k2 = dynamics(state + 0.5 * dt_s * k1, *dynamics_args)
    k3 = dynamics(state + 0.5 * dt_s * k2, *dynamics_args)
    k4 = dynamics(state + dt_s * k3, *dynamics_args)
    return state + dt_s * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0
