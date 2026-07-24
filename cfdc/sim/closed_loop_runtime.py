"""Canonical linear closed-loop runtime for the interactive CFDC laboratory.

The existing evidence validator and demo simulators deliberately remain
unchanged.  This module is an independent sixth-stage runtime with a narrow,
typed controller surface.  Continuous plants are rolled out after zero-order
hold sampling, while their stability decision is made in the continuous
domain.  Delays are explicit in the rollout; a third-order Padé model is used
only as auxiliary continuous pole evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Mapping, Sequence

import numpy as np
from scipy import signal

from cfdc.lab import (
    ComplexValue,
    ControllerRuntimeSpec,
    FilteredPDControllerSpec,
    FilteredPIDControllerSpec,
    LagControllerSpec,
    LeadControllerSpec,
    NotchControllerSpec,
    PControllerSpec,
    PIControllerSpec,
    RegisteredControllerSpec,
    SimulationEvent,
    SimulationTrace,
    StateFeedbackControllerSpec,
    StabilityDecision,
)
from cfdc.models import StateSpaceModelSpec, TransferFunctionModelSpec
from cfdc.models.schemas import CFDCModel


_POLE_TOLERANCE = 1e-6
_SATURATION_LIMIT = 0.10
_MAX_SAMPLES = 20_000
_FLOAT_TOLERANCE = 1e-12
_FIXED_LEAD_LAG_CONTROLLER_ID = "fixed_lead_lag_cascade"
_FIXED_DISCRETE_LEAD_CONTROLLER_ID = "fixed_discrete_lead"


class LinearSimulationResult(CFDCModel):
    """Serializable outcome of one linear stability-only trial."""

    trace: SimulationTrace
    stability: StabilityDecision


@dataclass(frozen=True)
class _PlantRealization:
    domain: str
    simulation_a: np.ndarray
    simulation_b: np.ndarray
    simulation_c: np.ndarray
    simulation_d: np.ndarray
    analysis_a: np.ndarray
    analysis_b: np.ndarray
    analysis_c: np.ndarray
    analysis_d: np.ndarray
    rollout_continuous_a: np.ndarray | None
    rollout_continuous_b: np.ndarray | None
    initial_state: np.ndarray
    state_names: tuple[str, ...]
    input_names: tuple[str, ...]
    output_names: tuple[str, ...]
    delay_s: float
    delay_samples: int
    pole_analysis_method: str


@dataclass
class _ControllerState:
    values: np.ndarray
    digital_a: np.ndarray | None = None
    digital_b: np.ndarray | None = None
    digital_c: np.ndarray | None = None
    digital_d: float | None = None


@dataclass(frozen=True)
class _FractionalDelayPropagation:
    whole_samples: int
    first_a: np.ndarray
    first_b: np.ndarray
    second_a: np.ndarray
    second_b: np.ndarray


ReferenceValue = float | Sequence[float] | Mapping[str, float]
BoundMap = Mapping[str, tuple[float, float]]


def _as_matrix(values: list[list[float]]) -> np.ndarray:
    return np.asarray(values, dtype=float)


def _tf_state_space(
    numerator: Sequence[float], denominator: Sequence[float]
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    numerator_array = np.trim_zeros(np.asarray(numerator, dtype=float), "f")
    denominator_array = np.trim_zeros(np.asarray(denominator, dtype=float), "f")
    if numerator_array.size == 0:
        numerator_array = np.asarray([0.0])
    if denominator_array.size == 0:
        raise ValueError("transfer-function denominator cannot be zero")
    if numerator_array.size > denominator_array.size:
        raise ValueError("improper transfer functions are not supported")
    if not np.any(numerator_array):
        return (
            np.zeros((0, 0)),
            np.zeros((0, 1)),
            np.zeros((1, 0)),
            np.zeros((1, 1)),
        )
    if denominator_array.size == 1:
        return (
            np.zeros((0, 0)),
            np.zeros((0, 1)),
            np.zeros((1, 0)),
            np.asarray([[numerator_array[-1] / denominator_array[-1]]]),
        )
    a, b, c, d = signal.tf2ss(numerator_array, denominator_array)
    return (
        np.asarray(a, dtype=float),
        np.asarray(b, dtype=float),
        np.asarray(c, dtype=float),
        np.asarray(d, dtype=float),
    )


def _sample_state_space(
    a: np.ndarray,
    b: np.ndarray,
    c: np.ndarray,
    d: np.ndarray,
    sample_time_s: float,
    *,
    method: str = "zoh",
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    if a.shape[0] == 0:
        return a.copy(), b.copy(), c.copy(), d.copy()
    ad, bd, cd, dd, _ = signal.cont2discrete((a, b, c, d), sample_time_s, method=method)
    return (
        np.asarray(ad, dtype=float),
        np.asarray(bd, dtype=float),
        np.asarray(cd, dtype=float),
        np.asarray(dd, dtype=float),
    )


def _third_order_pade(delay_s: float) -> tuple[np.ndarray, np.ndarray]:
    """Return descending-power coefficients of the [3/3] Padé delay model."""

    delay = float(delay_s)
    numerator = np.asarray(
        [-(delay**3), 12.0 * delay**2, -60.0 * delay, 120.0],
        dtype=float,
    )
    denominator = np.asarray(
        [delay**3, 12.0 * delay**2, 60.0 * delay, 120.0],
        dtype=float,
    )
    return numerator, denominator


def _normalize_plant(
    model: TransferFunctionModelSpec | StateSpaceModelSpec,
    sample_time_s: float,
) -> _PlantRealization:
    if isinstance(model, TransferFunctionModelSpec):
        a, b, c, d = _tf_state_space(model.numerator, model.denominator)
        state_names = tuple(f"x{i + 1}" for i in range(a.shape[0]))
        input_names = (model.input_signal_id,)
        output_names = (model.output_signal_id,)
        initial_state = np.zeros(a.shape[0], dtype=float)
        delay_s = float(model.input_delay_s)
        if model.time_domain == "continuous":
            ad, bd, cd, dd = _sample_state_space(
                a, b, c, d, sample_time_s, method="zoh"
            )
            if delay_s > 0.0:
                pade_num, pade_den = _third_order_pade(delay_s)
                combined_num = np.polymul(
                    np.asarray(model.numerator, dtype=float), pade_num
                )
                combined_den = np.polymul(
                    np.asarray(model.denominator, dtype=float), pade_den
                )
                aa, ba, ca, da = _tf_state_space(combined_num, combined_den)
                pole_method = "third_order_pade_auxiliary"
            else:
                aa, ba, ca, da = a, b, c, d
                pole_method = "exact_continuous_interconnection"
            delay_samples = 0
        else:
            assert model.sample_time_s is not None
            if not math.isclose(
                model.sample_time_s,
                sample_time_s,
                rel_tol=0.0,
                abs_tol=1e-12,
            ):
                raise ValueError(
                    "discrete model sample time must match runtime sample time"
                )
            ratio = delay_s / sample_time_s
            rounded = round(ratio)
            if not math.isclose(ratio, rounded, rel_tol=0.0, abs_tol=1e-9):
                raise ValueError(
                    "discrete input delay must be an integral number of samples"
                )
            delay_samples = int(rounded)
            ad, bd, cd, dd = a, b, c, d
            if delay_samples:
                aa, ba, ca, da = _augment_discrete_input_delay(
                    a, b, c, d, delay_samples
                )
                pole_method = "exact_discrete_delay_augmentation"
            else:
                aa, ba, ca, da = a, b, c, d
                pole_method = "exact_discrete_interconnection"
        return _PlantRealization(
            domain=model.time_domain,
            simulation_a=ad,
            simulation_b=bd,
            simulation_c=cd,
            simulation_d=dd,
            analysis_a=aa,
            analysis_b=ba,
            analysis_c=ca,
            analysis_d=da,
            rollout_continuous_a=a if model.time_domain == "continuous" else None,
            rollout_continuous_b=b if model.time_domain == "continuous" else None,
            initial_state=initial_state,
            state_names=state_names,
            input_names=input_names,
            output_names=output_names,
            delay_s=delay_s,
            delay_samples=delay_samples,
            pole_analysis_method=pole_method,
        )

    _reject_duplicate_names(model.state_names, "state")
    _reject_duplicate_names(model.input_signal_ids, "input")
    _reject_duplicate_names(model.output_signal_ids, "output")
    a = _as_matrix(model.a)
    b = _as_matrix(model.b)
    c = _as_matrix(model.c)
    d = _as_matrix(model.d)
    if model.time_domain == "continuous":
        ad, bd, cd, dd = _sample_state_space(a, b, c, d, sample_time_s, method="zoh")
        pole_method = "exact_continuous_interconnection"
    else:
        assert model.sample_time_s is not None
        if not math.isclose(
            model.sample_time_s,
            sample_time_s,
            rel_tol=0.0,
            abs_tol=1e-12,
        ):
            raise ValueError(
                "discrete model sample time must match runtime sample time"
            )
        ad, bd, cd, dd = a, b, c, d
        pole_method = "exact_discrete_interconnection"
    return _PlantRealization(
        domain=model.time_domain,
        simulation_a=ad,
        simulation_b=bd,
        simulation_c=cd,
        simulation_d=dd,
        analysis_a=a,
        analysis_b=b,
        analysis_c=c,
        analysis_d=d,
        rollout_continuous_a=a if model.time_domain == "continuous" else None,
        rollout_continuous_b=b if model.time_domain == "continuous" else None,
        initial_state=np.asarray(model.initial_state, dtype=float),
        state_names=tuple(model.state_names),
        input_names=tuple(model.input_signal_ids),
        output_names=tuple(model.output_signal_ids),
        delay_s=0.0,
        delay_samples=0,
        pole_analysis_method=pole_method,
    )


def _reject_duplicate_names(names: Sequence[str], label: str) -> None:
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise ValueError(f"duplicate {label} names are not allowed: {duplicates}")


def _augment_discrete_input_delay(
    a: np.ndarray,
    b: np.ndarray,
    c: np.ndarray,
    d: np.ndarray,
    delay_samples: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Augment a discrete plant with an exact integral-sample input queue."""

    if delay_samples <= 0:
        return a, b, c, d
    state_count, input_count = b.shape
    queue_count = delay_samples * input_count
    aa = np.zeros((state_count + queue_count, state_count + queue_count))
    ba = np.zeros((state_count + queue_count, input_count))
    ca = np.zeros((c.shape[0], state_count + queue_count))
    da = np.zeros((c.shape[0], input_count))

    aa[:state_count, :state_count] = a
    aa[:state_count, state_count : state_count + input_count] = b
    ca[:, :state_count] = c
    ca[:, state_count : state_count + input_count] = d
    for queue_index in range(delay_samples - 1):
        row = state_count + queue_index * input_count
        column = row + input_count
        aa[row : row + input_count, column : column + input_count] = np.eye(input_count)
    last = state_count + (delay_samples - 1) * input_count
    ba[last : last + input_count, :] = np.eye(input_count)
    return aa, ba, ca, da


def _controller_continuous_realization(
    controller: ControllerRuntimeSpec,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    empty_a = np.zeros((0, 0))
    empty_b = np.zeros((0, 1))
    empty_c = np.zeros((1, 0))
    if isinstance(controller, PControllerSpec):
        return empty_a, empty_b, empty_c, np.asarray([[controller.kp]])
    if isinstance(controller, PIControllerSpec):
        if controller.ki == 0.0:
            return empty_a, empty_b, empty_c, np.asarray([[controller.kp]])
        return (
            np.asarray([[0.0]]),
            np.asarray([[1.0]]),
            np.asarray([[controller.ki]]),
            np.asarray([[controller.kp]]),
        )
    if isinstance(controller, FilteredPDControllerSpec):
        if controller.kd == 0.0:
            return empty_a, empty_b, empty_c, np.asarray([[controller.kp]])
        cutoff = controller.filter_cutoff_rad_s
        return (
            np.asarray([[-cutoff]]),
            np.asarray([[-cutoff]]),
            np.asarray([[controller.kd * cutoff]]),
            np.asarray([[controller.kp + controller.kd * cutoff]]),
        )
    if isinstance(controller, FilteredPIDControllerSpec):
        if controller.ki == 0.0:
            return _controller_continuous_realization(
                FilteredPDControllerSpec(
                    kp=controller.kp,
                    kd=controller.kd,
                    derivative_source="measurement",
                    filter_cutoff_rad_s=controller.filter_cutoff_rad_s,
                )
            )
        if controller.kd == 0.0:
            return _controller_continuous_realization(
                PIControllerSpec(kp=controller.kp, ki=controller.ki)
            )
        cutoff = controller.filter_cutoff_rad_s
        return (
            np.asarray([[0.0, 0.0], [0.0, -cutoff]]),
            np.asarray([[1.0], [-cutoff]]),
            np.asarray([[controller.ki, controller.kd * cutoff]]),
            np.asarray([[controller.kp + controller.kd * cutoff]]),
        )
    if isinstance(controller, RegisteredControllerSpec):
        if controller.controller_id != _FIXED_LEAD_LAG_CONTROLLER_ID:
            raise ValueError(
                "this registered controller has no continuous linear realization"
            )
        gain = 0.5 * controller.parameters["gain_scale"]
        numerator = gain * np.polymul([1.0, 2.0], [1.0, 0.1])
        denominator = np.polymul([1.0, 8.0], [1.0, 0.05])
        return _tf_state_space(numerator, denominator)
    numerator, denominator = _compensator_transfer_function(controller)
    return _tf_state_space(numerator, denominator)


def _compensator_transfer_function(
    controller: LeadControllerSpec | LagControllerSpec | NotchControllerSpec,
) -> tuple[list[float], list[float]]:
    if isinstance(controller, (LeadControllerSpec, LagControllerSpec)):
        return (
            [controller.gain, controller.gain * controller.zero_rad_s],
            [1.0, controller.pole_rad_s],
        )
    frequency = controller.center_frequency_rad_s
    return (
        [
            controller.gain,
            2.0 * controller.gain * controller.zero_damping_ratio * frequency,
            controller.gain * frequency**2,
        ],
        [
            1.0,
            2.0 * controller.pole_damping_ratio * frequency,
            frequency**2,
        ],
    )


def _controller_discrete_realization(
    controller: ControllerRuntimeSpec,
    sample_time_s: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    empty_a = np.zeros((0, 0))
    empty_b = np.zeros((0, 1))
    empty_c = np.zeros((1, 0))
    if isinstance(controller, PControllerSpec):
        return empty_a, empty_b, empty_c, np.asarray([[controller.kp]])
    if isinstance(controller, PIControllerSpec):
        if controller.ki == 0.0:
            return empty_a, empty_b, empty_c, np.asarray([[controller.kp]])
        return (
            np.asarray([[1.0]]),
            np.asarray([[sample_time_s]]),
            np.asarray([[controller.ki]]),
            np.asarray([[controller.kp]]),
        )
    if isinstance(controller, FilteredPDControllerSpec):
        if controller.kd == 0.0:
            return empty_a, empty_b, empty_c, np.asarray([[controller.kp]])
        cutoff = controller.filter_cutoff_rad_s
        alpha = math.exp(-cutoff * sample_time_s)
        return (
            np.asarray([[alpha]]),
            np.asarray([[-(1.0 - alpha)]]),
            np.asarray([[controller.kd * cutoff]]),
            np.asarray([[controller.kp + controller.kd * cutoff]]),
        )
    if isinstance(controller, FilteredPIDControllerSpec):
        if controller.ki == 0.0:
            return _controller_discrete_realization(
                FilteredPDControllerSpec(
                    kp=controller.kp,
                    kd=controller.kd,
                    derivative_source="measurement",
                    filter_cutoff_rad_s=controller.filter_cutoff_rad_s,
                ),
                sample_time_s,
            )
        if controller.kd == 0.0:
            return _controller_discrete_realization(
                PIControllerSpec(kp=controller.kp, ki=controller.ki),
                sample_time_s,
            )
        cutoff = controller.filter_cutoff_rad_s
        alpha = math.exp(-cutoff * sample_time_s)
        return (
            np.asarray([[1.0, 0.0], [0.0, alpha]]),
            np.asarray([[sample_time_s], [-(1.0 - alpha)]]),
            np.asarray([[controller.ki, controller.kd * cutoff]]),
            np.asarray([[controller.kp + controller.kd * cutoff]]),
        )
    if isinstance(controller, RegisteredControllerSpec):
        if controller.controller_id == _FIXED_DISCRETE_LEAD_CONTROLLER_ID:
            gain_scale = controller.parameters["gain_scale"]
            return _tf_state_space(
                [
                    45.56 * gain_scale,
                    -43.33 * gain_scale,
                ],
                [1.0, -0.7778],
            )
        if controller.controller_id != _FIXED_LEAD_LAG_CONTROLLER_ID:
            raise ValueError(
                "this registered controller has no discrete linear realization"
            )
    ac, bc, cc, dc = _controller_continuous_realization(controller)
    return _sample_state_space(ac, bc, cc, dc, sample_time_s, method="bilinear")


def _closed_loop_matrix(
    a: np.ndarray,
    b: np.ndarray,
    c: np.ndarray,
    d: np.ndarray,
    ac: np.ndarray,
    bc: np.ndarray,
    cc: np.ndarray,
    dc: np.ndarray,
) -> np.ndarray:
    """Exact negative-feedback interconnection, including direct feedthrough."""

    input_count = b.shape[1]
    if input_count != 1 or c.shape[0] != 1:
        raise ValueError("dynamic controllers require a SISO plant")
    loop_matrix = np.eye(input_count) + dc @ d
    try:
        inverse_loop = np.linalg.inv(loop_matrix)
    except np.linalg.LinAlgError as exc:
        raise ValueError(
            "controller/plant direct feedthrough creates a singular algebraic loop"
        ) from exc
    top_left = a - b @ inverse_loop @ dc @ c
    top_right = b @ inverse_loop @ cc
    if ac.shape[0] == 0:
        return top_left
    bottom_left = bc @ (-c + d @ inverse_loop @ dc @ c)
    bottom_right = ac - bc @ d @ inverse_loop @ cc
    return np.block([[top_left, top_right], [bottom_left, bottom_right]])


def _validate_runtime_compatibility(
    model: TransferFunctionModelSpec | StateSpaceModelSpec,
    plant: _PlantRealization,
    controller: ControllerRuntimeSpec,
) -> None:
    if isinstance(controller, RegisteredControllerSpec):
        if controller.controller_id == _FIXED_LEAD_LAG_CONTROLLER_ID:
            if plant.domain != "continuous":
                raise ValueError("fixed lead-lag cascade requires a continuous plant")
        elif controller.controller_id == _FIXED_DISCRETE_LEAD_CONTROLLER_ID:
            if plant.domain != "discrete":
                raise ValueError("fixed discrete lead requires a discrete plant")
        else:
            raise ValueError(
                "registered nonlinear/demo controllers are executed only by "
                "their matching registered adapter"
            )
    if isinstance(controller, StateFeedbackControllerSpec):
        if not isinstance(model, StateSpaceModelSpec):
            raise ValueError("state feedback requires an explicit state-space model")
        k = np.asarray(controller.gain_matrix, dtype=float)
        n = plant.simulation_a.shape[0]
        m = plant.simulation_b.shape[1]
        p = plant.simulation_c.shape[0]
        nr = np.asarray(controller.reference_gain_matrix, dtype=float)
        if k.shape != (m, n):
            raise ValueError(
                "state-feedback gain dimensions must be input_count x state_count"
            )
        if nr.shape != (m, p):
            raise ValueError(
                "state-feedback reference gain dimensions must be "
                "input_count x output_count"
            )
        if len(controller.equilibrium_state) != n:
            raise ValueError(
                "state-feedback equilibrium state dimensions must match plant"
            )
        if len(controller.equilibrium_input) != m:
            raise ValueError(
                "state-feedback equilibrium input dimensions must match plant"
            )
        return
    if plant.simulation_b.shape[1] != 1 or plant.simulation_c.shape[0] != 1:
        raise ValueError(
            "P/PI/filtered PD/PID/lead/lag/notch require a SISO plant; "
            "use explicit state_feedback for MIMO"
        )


def _normalize_reference(
    reference: ReferenceValue, output_names: tuple[str, ...]
) -> np.ndarray:
    if isinstance(reference, Mapping):
        unknown = sorted(set(reference) - set(output_names))
        missing = sorted(set(output_names) - set(reference))
        if unknown or missing:
            raise ValueError(
                f"reference channels must match outputs; missing={missing}, "
                f"unknown={unknown}"
            )
        values = [reference[name] for name in output_names]
    elif isinstance(reference, (int, float, np.floating)):
        if len(output_names) != 1:
            raise ValueError("a scalar reference is only valid for a SISO plant")
        values = [float(reference)]
    else:
        values = list(reference)
        if len(values) != len(output_names):
            raise ValueError("reference vector dimensions must match output_count")
    result = np.asarray(values, dtype=float)
    if not np.all(np.isfinite(result)):
        raise ValueError("reference values must be finite")
    return result


def _normalize_bounds(
    bounds: BoundMap | None,
    channel_names: tuple[str, ...],
    *,
    label: str,
) -> dict[str, tuple[float, float]]:
    if bounds is None:
        return {}
    unknown = sorted(set(bounds) - set(channel_names))
    if unknown:
        raise ValueError(f"unknown {label} bound channels: {unknown}")
    normalized: dict[str, tuple[float, float]] = {}
    for name, pair in bounds.items():
        if len(pair) != 2:
            raise ValueError(f"{label} bound for {name} must be (lower, upper)")
        lower, upper = float(pair[0]), float(pair[1])
        if not math.isfinite(lower) or not math.isfinite(upper):
            raise ValueError(f"{label} bounds must be finite")
        if lower >= upper:
            raise ValueError(f"{label} lower bound must be less than upper bound")
        normalized[name] = (lower, upper)
    return normalized


def _initialize_controller_state(
    controller: ControllerRuntimeSpec,
    sample_time_s: float,
    initial_output: float,
) -> _ControllerState:
    if isinstance(controller, (PControllerSpec, StateFeedbackControllerSpec)):
        return _ControllerState(values=np.zeros(0))
    if isinstance(controller, PIControllerSpec):
        return _ControllerState(values=np.asarray([0.0]))
    if isinstance(controller, FilteredPDControllerSpec):
        return _ControllerState(values=np.asarray([initial_output]))
    if isinstance(controller, FilteredPIDControllerSpec):
        return _ControllerState(values=np.asarray([0.0, initial_output]))
    if (
        isinstance(controller, RegisteredControllerSpec)
        and controller.controller_id == _FIXED_DISCRETE_LEAD_CONTROLLER_ID
    ):
        ad, bd, cd, dd = _controller_discrete_realization(controller, sample_time_s)
    else:
        ac, bc, cc, dc = _controller_continuous_realization(controller)
        ad, bd, cd, dd = _sample_state_space(
            ac, bc, cc, dc, sample_time_s, method="bilinear"
        )
    return _ControllerState(
        values=np.zeros(ad.shape[0]),
        digital_a=ad,
        digital_b=bd,
        digital_c=cd,
        digital_d=float(dd[0, 0]),
    )


def _siso_affine_control(
    controller: ControllerRuntimeSpec,
    state: _ControllerState,
    reference: float,
    state_projection: float,
    direct_feedthrough: float,
    *,
    measured_output: float | None,
) -> tuple[float, float]:
    """Return requested control and its feedback coefficient on the output."""

    if isinstance(controller, PControllerSpec):
        base, reference_gain, feedback_gain = 0.0, controller.kp, controller.kp
    elif isinstance(controller, PIControllerSpec):
        base = controller.ki * state.values[0]
        reference_gain, feedback_gain = controller.kp, controller.kp
    elif isinstance(controller, FilteredPDControllerSpec):
        cutoff = controller.filter_cutoff_rad_s
        base = controller.kd * cutoff * state.values[0]
        reference_gain = controller.kp
        feedback_gain = controller.kp + controller.kd * cutoff
    elif isinstance(controller, FilteredPIDControllerSpec):
        cutoff = controller.filter_cutoff_rad_s
        base = (
            controller.ki * state.values[0] + controller.kd * cutoff * state.values[1]
        )
        reference_gain = controller.kp
        feedback_gain = controller.kp + controller.kd * cutoff
    else:
        assert state.digital_c is not None and state.digital_d is not None
        base = float((state.digital_c @ state.values).item())
        reference_gain = state.digital_d
        feedback_gain = state.digital_d

    if measured_output is not None:
        return (
            base + reference_gain * reference - feedback_gain * measured_output,
            feedback_gain,
        )
    denominator = 1.0 + feedback_gain * direct_feedthrough
    if abs(denominator) <= _FLOAT_TOLERANCE:
        raise ValueError(
            "controller/plant direct feedthrough creates a singular algebraic loop"
        )
    request = (
        base + reference_gain * reference - feedback_gain * state_projection
    ) / denominator
    return request, feedback_gain


def _resolve_saturated_siso_algebraic_loop(
    controller: ControllerRuntimeSpec,
    state: _ControllerState,
    *,
    reference: float,
    state_projection: float,
    direct_feedthrough: float,
    actuator_bound: tuple[float, float] | None,
) -> tuple[float, float]:
    """Solve the scalar controller/direct-feedthrough/saturation relation.

    The relation is piecewise affine:

    ``requested = controller(reference, Cx + D * clip(requested))``.

    Enumerating its unsaturated, lower-saturated, and upper-saturated regions
    is exact and bounded.  It avoids both the inconsistent "solve then clip"
    trace and an arbitrary fixed-point iteration.  Pathological parameters can
    create multiple algebraic solutions; those are rejected explicitly.
    """

    unsaturated_request, _ = _siso_affine_control(
        controller,
        state,
        reference,
        state_projection,
        direct_feedthrough,
        measured_output=None,
    )
    if actuator_bound is None:
        return unsaturated_request, unsaturated_request

    lower, upper = actuator_bound
    request_candidates = [unsaturated_request]
    for applied_boundary in (lower, upper):
        measured_output = state_projection + direct_feedthrough * applied_boundary
        boundary_request, _ = _siso_affine_control(
            controller,
            state,
            reference,
            state_projection,
            direct_feedthrough,
            measured_output=measured_output,
        )
        request_candidates.append(boundary_request)

    consistent: list[tuple[float, float]] = []
    for request in request_candidates:
        applied = float(np.clip(request, lower, upper))
        measured_output = state_projection + direct_feedthrough * applied
        expected_request, _ = _siso_affine_control(
            controller,
            state,
            reference,
            state_projection,
            direct_feedthrough,
            measured_output=measured_output,
        )
        scale = max(1.0, abs(request), abs(expected_request))
        if abs(request - expected_request) > 1e-10 * scale:
            continue
        if not any(
            math.isclose(request, old_request, rel_tol=1e-10, abs_tol=1e-12)
            and math.isclose(applied, old_applied, rel_tol=1e-10, abs_tol=1e-12)
            for old_request, old_applied in consistent
        ):
            consistent.append((request, applied))

    if len(consistent) != 1:
        qualifier = "no" if not consistent else "multiple"
        raise ValueError(
            f"saturated direct-feedthrough algebraic loop has {qualifier} "
            "self-consistent solution"
        )
    return consistent[0]


def _update_controller_state(
    controller: ControllerRuntimeSpec,
    state: _ControllerState,
    *,
    reference: float,
    output: float,
    requested: float,
    applied: float,
    sample_time_s: float,
) -> None:
    error = reference - output
    saturated_high = applied < requested
    saturated_low = applied > requested
    if isinstance(controller, PIControllerSpec):
        drives_further = (saturated_high and controller.ki * error > 0.0) or (
            saturated_low and controller.ki * error < 0.0
        )
        if not drives_further:
            state.values[0] += sample_time_s * error
        if controller.integrator_limit is not None:
            state.values[0] = float(
                np.clip(
                    state.values[0],
                    -controller.integrator_limit,
                    controller.integrator_limit,
                )
            )
        return
    if isinstance(controller, FilteredPDControllerSpec):
        alpha = math.exp(-controller.filter_cutoff_rad_s * sample_time_s)
        state.values[0] = alpha * state.values[0] + (1.0 - alpha) * output
        return
    if isinstance(controller, FilteredPIDControllerSpec):
        drives_further = (saturated_high and controller.ki * error > 0.0) or (
            saturated_low and controller.ki * error < 0.0
        )
        if not drives_further:
            state.values[0] += sample_time_s * error
        if controller.integrator_limit is not None:
            state.values[0] = float(
                np.clip(
                    state.values[0],
                    -controller.integrator_limit,
                    controller.integrator_limit,
                )
            )
        alpha = math.exp(-controller.filter_cutoff_rad_s * sample_time_s)
        state.values[1] = alpha * state.values[1] + (1.0 - alpha) * output
        return
    if isinstance(controller, (PControllerSpec, StateFeedbackControllerSpec)):
        return
    assert state.digital_a is not None and state.digital_b is not None
    state.values = state.digital_a @ state.values + state.digital_b[:, 0] * error


def _history_command(
    command_history: list[np.ndarray],
    history_index: int,
    input_count: int,
) -> np.ndarray:
    if history_index < 0:
        return np.zeros(input_count)
    if history_index >= len(command_history):
        raise ValueError("delay history requested a future control sample")
    return command_history[history_index]


def _instantaneous_delayed_command(
    command_history: list[np.ndarray],
    sample_index: int,
    delay_s: float,
    sample_time_s: float,
    input_count: int,
    *,
    discrete_delay_samples: int,
) -> np.ndarray:
    """Return causal ZOH input at the exact sampled output time."""

    if discrete_delay_samples:
        history_index = sample_index - discrete_delay_samples
    else:
        delay_ratio = delay_s / sample_time_s
        # Every genuinely positive sub-sample delay reads the previous held
        # command at a sample instant, including delays smaller than floating
        # comparison tolerances.
        if 0.0 < delay_ratio < 1.0:
            history_index = sample_index - 1
            return _history_command(command_history, history_index, input_count)
        nearest_integer = round(delay_ratio)
        if nearest_integer >= 1 and math.isclose(
            delay_ratio,
            nearest_integer,
            rel_tol=0.0,
            abs_tol=1e-12,
        ):
            history_index = sample_index - nearest_integer
            return _history_command(command_history, history_index, input_count)
        source_position = sample_index - delay_ratio
        if source_position < -1e-12:
            return np.zeros(input_count)
        # A command changes at its sample boundary and is held until the next.
        history_index = math.floor(source_position)
    return _history_command(command_history, history_index, input_count)


def _fractional_delay_propagation(
    plant: _PlantRealization,
    sample_time_s: float,
) -> _FractionalDelayPropagation | None:
    if plant.domain != "continuous" or plant.delay_s <= 0.0:
        return None
    ratio = plant.delay_s / sample_time_s
    nearest_integer = round(ratio)
    if nearest_integer >= 1 and math.isclose(
        ratio,
        nearest_integer,
        rel_tol=0.0,
        abs_tol=1e-12,
    ):
        return None
    whole_samples = math.floor(ratio + 1e-12)
    fraction = ratio - whole_samples
    if fraction <= 0.0:
        return None
    assert plant.rollout_continuous_a is not None
    assert plant.rollout_continuous_b is not None
    a = plant.rollout_continuous_a
    b = plant.rollout_continuous_b
    dummy_c = np.zeros((1, a.shape[0]))
    dummy_d = np.zeros((1, b.shape[1]))
    first_a, first_b, _, _ = _sample_state_space(
        a,
        b,
        dummy_c,
        dummy_d,
        fraction * sample_time_s,
        method="zoh",
    )
    second_a, second_b, _, _ = _sample_state_space(
        a,
        b,
        dummy_c,
        dummy_d,
        (1.0 - fraction) * sample_time_s,
        method="zoh",
    )
    return _FractionalDelayPropagation(
        whole_samples=whole_samples,
        first_a=first_a,
        first_b=first_b,
        second_a=second_a,
        second_b=second_b,
    )


def _advance_continuous_delayed_state(
    plant: _PlantRealization,
    state: np.ndarray,
    command_history: list[np.ndarray],
    sample_index: int,
    sample_time_s: float,
    fractional: _FractionalDelayPropagation | None,
) -> np.ndarray:
    input_count = len(plant.input_names)
    if fractional is None:
        delay_samples = int(round(plant.delay_s / sample_time_s))
        delayed = _history_command(
            command_history, sample_index - delay_samples, input_count
        )
        return plant.simulation_a @ state + plant.simulation_b @ delayed

    first_input = _history_command(
        command_history,
        sample_index - fractional.whole_samples - 1,
        input_count,
    )
    second_input = _history_command(
        command_history,
        sample_index - fractional.whole_samples,
        input_count,
    )
    intermediate = fractional.first_a @ state + fractional.first_b @ first_input
    return fractional.second_a @ intermediate + fractional.second_b @ second_input


def _first_bound_violation(
    values: np.ndarray,
    names: tuple[str, ...],
    bounds: dict[str, tuple[float, float]],
) -> tuple[str, float, float] | None:
    for index, name in enumerate(names):
        if name not in bounds:
            continue
        lower, upper = bounds[name]
        value = float(values[index])
        if value < lower:
            return name, value, lower
        if value > upper:
            return name, value, upper
    return None


def _simulate(
    plant: _PlantRealization,
    controller: ControllerRuntimeSpec,
    reference: np.ndarray,
    *,
    actuator_bounds: dict[str, tuple[float, float]],
    state_bounds: dict[str, tuple[float, float]],
    output_bounds: dict[str, tuple[float, float]],
    horizon_s: float,
    sample_time_s: float,
) -> SimulationTrace:
    sample_count = int(math.floor(horizon_s / sample_time_s + 1e-12)) + 1
    if sample_count > _MAX_SAMPLES:
        raise ValueError("a simulation trial cannot exceed 20,000 samples")

    x = plant.initial_state.copy()
    initial_output = float(plant.simulation_c[0] @ x)
    controller_state = _initialize_controller_state(
        controller, sample_time_s, initial_output
    )
    times: list[float] = []
    references = {name: [] for name in plant.output_names}
    states = {name: [] for name in plant.state_names}
    outputs = {name: [] for name in plant.output_names}
    requested_controls = {name: [] for name in plant.input_names}
    applied_controls = {name: [] for name in plant.input_names}
    events: list[SimulationEvent] = []
    command_history: list[np.ndarray] = []
    first_saturation_recorded = False
    fractional_delay = _fractional_delay_propagation(plant, sample_time_s)

    if plant.delay_s > 0.0:
        events.append(
            SimulationEvent(
                kind="delay_buffer_active",
                sample_index=0,
                time_s=0.0,
                message=(
                    f"explicit input-delay buffer active for "
                    f"{float(plant.delay_s)} seconds"
                ),
            )
        )

    for sample_index in range(sample_count):
        time_s = sample_index * sample_time_s
        if not np.all(np.isfinite(x)) or not np.all(
            np.isfinite(controller_state.values)
        ):
            events.append(
                SimulationEvent(
                    kind="non_finite",
                    sample_index=sample_index,
                    time_s=float(time_s),
                    message=(
                        "non-finite state encountered; the attempted sample "
                        "was discarded"
                    ),
                )
            )
            break

        if isinstance(controller, StateFeedbackControllerSpec):
            k = np.asarray(controller.gain_matrix, dtype=float)
            nr = np.asarray(controller.reference_gain_matrix, dtype=float)
            xeq = np.asarray(controller.equilibrium_state, dtype=float)
            ueq = np.asarray(controller.equilibrium_input, dtype=float)
            equilibrium_output = plant.simulation_c @ xeq + plant.simulation_d @ ueq
            requested = ueq - k @ (x - xeq) + nr @ (reference - equilibrium_output)
            applied = requested.copy()
            for input_index, input_name in enumerate(plant.input_names):
                if input_name in actuator_bounds:
                    lower, upper = actuator_bounds[input_name]
                    applied[input_index] = np.clip(applied[input_index], lower, upper)
            plant_input = applied
            y = plant.simulation_c @ x + plant.simulation_d @ plant_input
        else:
            resolved_applied: float | None = None
            if plant.delay_s > 0.0:
                # The delayed plant input is independent of the current
                # command, so output can be measured before controller action.
                plant_input = _instantaneous_delayed_command(
                    command_history,
                    sample_index,
                    plant.delay_s,
                    sample_time_s,
                    len(plant.input_names),
                    discrete_delay_samples=plant.delay_samples,
                )
                y = plant.simulation_c @ x + plant.simulation_d @ plant_input
                request, _ = _siso_affine_control(
                    controller,
                    controller_state,
                    float(reference[0]),
                    float(plant.simulation_c[0] @ x),
                    float(plant.simulation_d[0, 0]),
                    measured_output=float(y[0]),
                )
            else:
                input_name = plant.input_names[0]
                request, resolved_applied = _resolve_saturated_siso_algebraic_loop(
                    controller,
                    controller_state,
                    reference=float(reference[0]),
                    state_projection=float(plant.simulation_c[0] @ x),
                    direct_feedthrough=float(plant.simulation_d[0, 0]),
                    actuator_bound=actuator_bounds.get(input_name),
                )
            requested = np.asarray([request])
            applied = (
                requested.copy()
                if resolved_applied is None
                else np.asarray([resolved_applied])
            )
            input_name = plant.input_names[0]
            if resolved_applied is None and input_name in actuator_bounds:
                lower, upper = actuator_bounds[input_name]
                applied[0] = np.clip(applied[0], lower, upper)
            if plant.delay_s <= 0.0:
                plant_input = applied
                y = plant.simulation_c @ x + plant.simulation_d @ plant_input
            command_history.append(applied.copy())
            if plant.delay_s > 0.0:
                plant_input = _instantaneous_delayed_command(
                    command_history,
                    sample_index,
                    plant.delay_s,
                    sample_time_s,
                    len(plant.input_names),
                    discrete_delay_samples=plant.delay_samples,
                )
                y = plant.simulation_c @ x + plant.simulation_d @ plant_input

        if not (
            np.all(np.isfinite(requested))
            and np.all(np.isfinite(applied))
            and np.all(np.isfinite(y))
        ):
            events.append(
                SimulationEvent(
                    kind="non_finite",
                    sample_index=sample_index,
                    time_s=float(time_s),
                    message=(
                        "non-finite output or control encountered; the "
                        "attempted sample was discarded"
                    ),
                )
            )
            break

        times.append(float(time_s))
        for index, name in enumerate(plant.output_names):
            references[name].append(float(reference[index]))
            outputs[name].append(float(y[index]))
        for index, name in enumerate(plant.state_names):
            states[name].append(float(x[index]))
        for index, name in enumerate(plant.input_names):
            requested_controls[name].append(float(requested[index]))
            applied_controls[name].append(float(applied[index]))
            if not first_saturation_recorded and not math.isclose(
                float(requested[index]),
                float(applied[index]),
                rel_tol=0.0,
                abs_tol=_FLOAT_TOLERANCE,
            ):
                lower, upper = actuator_bounds[name]
                limit = upper if requested[index] > applied[index] else lower
                events.append(
                    SimulationEvent(
                        kind="saturation",
                        sample_index=sample_index,
                        time_s=float(time_s),
                        message=f"{name} reached its actuator limit",
                        channel=name,
                        value=float(requested[index]),
                        limit=float(limit),
                    )
                )
                first_saturation_recorded = True

        violation = _first_bound_violation(x, plant.state_names, state_bounds)
        if violation is None:
            violation = _first_bound_violation(y, plant.output_names, output_bounds)
        if violation is not None:
            name, value, limit = violation
            events.append(
                SimulationEvent(
                    kind="hard_bound_violation",
                    sample_index=sample_index,
                    time_s=float(time_s),
                    message=f"{name} crossed its declared hard bound",
                    channel=name,
                    value=value,
                    limit=limit,
                )
            )
            break

        if sample_index == sample_count - 1:
            break

        if not isinstance(controller, StateFeedbackControllerSpec):
            _update_controller_state(
                controller,
                controller_state,
                reference=float(reference[0]),
                output=float(y[0]),
                requested=float(requested[0]),
                applied=float(applied[0]),
                sample_time_s=sample_time_s,
            )
        with np.errstate(over="ignore", invalid="ignore"):
            if plant.domain == "continuous" and plant.delay_s > 0.0:
                x = _advance_continuous_delayed_state(
                    plant,
                    x,
                    command_history,
                    sample_index,
                    sample_time_s,
                    fractional_delay,
                )
            else:
                x = plant.simulation_a @ x + plant.simulation_b @ plant_input

    return SimulationTrace(
        time_s=times,
        reference=references,
        states=states,
        outputs=outputs,
        requested_controls=requested_controls,
        applied_controls=applied_controls,
        events=events,
    )


def _closed_loop_poles(
    plant: _PlantRealization,
    controller: ControllerRuntimeSpec,
    sample_time_s: float,
) -> np.ndarray:
    if isinstance(controller, StateFeedbackControllerSpec):
        k = np.asarray(controller.gain_matrix, dtype=float)
        return np.linalg.eigvals(plant.analysis_a - plant.analysis_b @ k)
    if plant.domain == "continuous":
        ac, bc, cc, dc = _controller_continuous_realization(controller)
    else:
        ac, bc, cc, dc = _controller_discrete_realization(controller, sample_time_s)
    closed_loop = _closed_loop_matrix(
        plant.analysis_a,
        plant.analysis_b,
        plant.analysis_c,
        plant.analysis_d,
        ac,
        bc,
        cc,
        dc,
    )
    return np.linalg.eigvals(closed_loop)


def _continuous_delayed_sampled_plant(
    plant: _PlantRealization,
    sample_time_s: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Build the exact sampled queue model used by a continuous-delay rollout."""

    fractional = _fractional_delay_propagation(plant, sample_time_s)
    if fractional is None:
        delay_samples = int(round(plant.delay_s / sample_time_s))
        return _augment_discrete_input_delay(
            plant.simulation_a,
            plant.simulation_b,
            plant.simulation_c,
            plant.simulation_d,
            delay_samples,
        )

    state_count = plant.simulation_a.shape[0]
    input_count = plant.simulation_b.shape[1]
    queue_stages = fractional.whole_samples + 1
    queue_count = queue_stages * input_count
    augmented_a = np.zeros((state_count + queue_count, state_count + queue_count))
    augmented_b = np.zeros((state_count + queue_count, input_count))
    augmented_c = np.zeros((plant.simulation_c.shape[0], state_count + queue_count))
    augmented_d = np.zeros((plant.simulation_c.shape[0], input_count))

    # During each sample interval, the old delayed command acts for f*dt and
    # the next delayed command for (1-f)*dt.
    augmented_a[:state_count, :state_count] = fractional.second_a @ fractional.first_a
    augmented_a[
        :state_count,
        state_count : state_count + input_count,
    ] = fractional.second_a @ fractional.first_b
    if fractional.whole_samples == 0:
        augmented_b[:state_count, :] = fractional.second_b
    else:
        # Queue order is oldest to newest:
        # [u[k-q-1], u[k-q], ..., u[k-1]].  The second interval therefore
        # always uses queue block 1, not the newest block when q > 1.
        second_interval_queue_start = state_count + input_count
        augmented_a[
            :state_count,
            second_interval_queue_start : second_interval_queue_start + input_count,
        ] = fractional.second_b

    # At the sampled output instant, the fractional delay still selects the
    # older command u[k-q-1], including through direct feedthrough.
    augmented_c[:, :state_count] = plant.simulation_c
    augmented_c[:, state_count : state_count + input_count] = plant.simulation_d

    for queue_index in range(queue_stages - 1):
        row = state_count + queue_index * input_count
        column = row + input_count
        augmented_a[
            row : row + input_count,
            column : column + input_count,
        ] = np.eye(input_count)
    newest_queue_start = state_count + (queue_stages - 1) * input_count
    augmented_b[newest_queue_start : newest_queue_start + input_count, :] = np.eye(
        input_count
    )
    return augmented_a, augmented_b, augmented_c, augmented_d


def _sampled_implementation_spectral_radius(
    plant: _PlantRealization,
    controller: ControllerRuntimeSpec,
    sample_time_s: float,
) -> float:
    """Analyze the actual sampled map used by the rollout."""

    if plant.domain == "continuous" and plant.delay_s > 0.0:
        sampled_a, sampled_b, sampled_c, sampled_d = _continuous_delayed_sampled_plant(
            plant, sample_time_s
        )
    else:
        sampled_a = plant.simulation_a
        sampled_b = plant.simulation_b
        sampled_c = plant.simulation_c
        sampled_d = plant.simulation_d
    if isinstance(controller, StateFeedbackControllerSpec):
        k = np.asarray(controller.gain_matrix, dtype=float)
        if sampled_a.shape[0] != k.shape[1]:
            raise ValueError(
                "delayed sampled state-feedback analysis requires gains for "
                "all augmented queue states"
            )
        sampled_map = sampled_a - sampled_b @ k
    else:
        ac, bc, cc, dc = _controller_discrete_realization(controller, sample_time_s)
        sampled_map = _closed_loop_matrix(
            sampled_a,
            sampled_b,
            sampled_c,
            sampled_d,
            ac,
            bc,
            cc,
            dc,
        )
    sampled_poles = np.linalg.eigvals(sampled_map)
    if not np.all(np.isfinite(sampled_poles)):
        raise ValueError("sampled rollout pole analysis was non-finite")
    return (
        float(max(abs(pole) for pole in sampled_poles)) if sampled_poles.size else 0.0
    )


def _tail_error_contraction(trace: SimulationTrace) -> float:
    sample_count = len(trace.time_s)
    if sample_count == 0:
        return 0.0
    errors = np.zeros(sample_count)
    for name, reference_values in trace.reference.items():
        reference_array = np.asarray(reference_values)
        output_array = np.asarray(trace.outputs[name])
        # Normalize before subtraction so two individually finite extreme
        # values cannot overflow merely while computing this diagnostic.
        channel_scale = max(
            float(np.max(np.abs(reference_array))),
            float(np.max(np.abs(output_array))),
            1.0,
        )
        channel_error = np.abs(
            reference_array / channel_scale - output_array / channel_scale
        )
        errors = np.maximum(errors, channel_error)
    window = max(1, sample_count // 5)
    early_envelope = float(np.max(errors[:window]))
    late_envelope = float(np.max(errors[-window:]))
    scale = max(early_envelope, np.finfo(float).eps)
    return (early_envelope - late_envelope) / scale


def _saturation_fraction(trace: SimulationTrace) -> float:
    saturated_count = 0
    total_count = 0
    for name, requested_values in trace.requested_controls.items():
        requested = np.asarray(requested_values)
        applied = np.asarray(trace.applied_controls[name])
        saturated_count += int(
            np.count_nonzero(
                ~np.isclose(
                    requested,
                    applied,
                    rtol=0.0,
                    atol=_FLOAT_TOLERANCE,
                )
            )
        )
        total_count += requested.size
    return saturated_count / max(total_count, 1)


def _evaluate_stability(
    plant: _PlantRealization,
    controller: ControllerRuntimeSpec,
    trace: SimulationTrace,
    sample_time_s: float,
) -> StabilityDecision:
    pole_analysis_valid = True
    pole_analysis_error = ""
    try:
        with np.errstate(over="ignore", invalid="ignore"):
            poles = _closed_loop_poles(plant, controller, sample_time_s)
        if not np.all(np.isfinite(poles)):
            pole_analysis_valid = False
            pole_analysis_error = "closed-loop pole analysis was non-finite"
            poles = np.asarray([], dtype=complex)
    except (ValueError, np.linalg.LinAlgError) as exc:
        pole_analysis_valid = False
        pole_analysis_error = f"closed-loop pole analysis failed: {exc}"
        poles = np.asarray([], dtype=complex)
    pole_values = [
        ComplexValue(real=float(value.real), imaginary=float(value.imag))
        for value in sorted(
            poles, key=lambda item: (float(item.real), float(item.imag))
        )
    ]
    event_kinds = {event.kind for event in trace.events}
    trajectory_finite = "non_finite" not in event_kinds
    hard_bound_crossed = "hard_bound_violation" in event_kinds
    trajectory_bounded = not hard_bound_crossed
    saturation_fraction = _saturation_fraction(trace)
    contraction = _tail_error_contraction(trace)
    violations: list[str] = []
    evidence: list[str] = []
    sampled_rollout_status = "not_applicable"

    if plant.domain == "continuous":
        try:
            with np.errstate(over="ignore", invalid="ignore"):
                sampled_radius = _sampled_implementation_spectral_radius(
                    plant, controller, sample_time_s
                )
            if sampled_radius > 1.0 + _POLE_TOLERANCE:
                sampled_rollout_status = "unstable"
                trajectory_bounded = False
                violations.append("sampled_rollout_dynamics_unstable")
            elif sampled_radius < 1.0 - _POLE_TOLERANCE:
                sampled_rollout_status = "stable"
            else:
                sampled_rollout_status = "boundary"
                violations.append("sampled_rollout_dynamics_boundary")
            evidence.append(
                "actual sampled rollout-map spectral radius="
                f"{sampled_radius:.9g}; this numerical boundedness check is "
                "independent of reference-tracking performance"
            )
        except (ValueError, np.linalg.LinAlgError) as exc:
            sampled_rollout_status = "analysis_failed"
            violations.append("sampled_rollout_analysis_failed")
            evidence.append(f"sampled rollout-map analysis failed: {exc}")

    if plant.domain == "continuous":
        spectral_radius = None
        largest_real_part = (
            max(float(pole.real) for pole in poles) if poles.size else -math.inf
        )
        if not pole_analysis_valid:
            pole_status = "unstable"
            violations.append("non_finite_pole_analysis")
        elif largest_real_part > _POLE_TOLERANCE:
            pole_status = "unstable"
            violations.append("closed_loop_pole_outside_left_half_plane")
        elif largest_real_part < -_POLE_TOLERANCE:
            pole_status = "stable"
        else:
            pole_status = "boundary"
            violations.append("closed_loop_pole_in_numerical_boundary_band")
        if plant.pole_analysis_method == "third_order_pade_auxiliary":
            evidence.append(
                "Continuous delay used a third-order Padé approximation for "
                "auxiliary pole analysis only; rollout used the explicit "
                "time-domain delay buffer."
            )
        else:
            evidence.append(
                "Continuous poles were computed from the exact nominal "
                "linear interconnection."
            )
        evidence.append(
            pole_analysis_error
            if not pole_analysis_valid
            else (
                f"largest closed-loop pole real part={largest_real_part:.9g}; "
                "stable threshold is strictly below -1e-6"
            )
        )
    else:
        spectral_radius = float(max(abs(pole) for pole in poles)) if poles.size else 0.0
        if not pole_analysis_valid:
            pole_status = "unstable"
            violations.append("non_finite_pole_analysis")
            spectral_radius = float(np.finfo(float).max)
        elif spectral_radius > 1.0 + _POLE_TOLERANCE:
            pole_status = "unstable"
            violations.append("closed_loop_pole_outside_unit_disk")
        elif spectral_radius < 1.0 - _POLE_TOLERANCE:
            pole_status = "stable"
        else:
            pole_status = "boundary"
            violations.append("closed_loop_pole_in_numerical_boundary_band")
        if plant.delay_samples:
            evidence.append(
                "Discrete integral-sample input delay was included exactly "
                "as augmented queue states in pole analysis and rollout."
            )
        else:
            evidence.append(
                "Discrete poles were computed from the exact sampled "
                "linear interconnection."
            )
        evidence.append(
            pole_analysis_error
            if not pole_analysis_valid
            else (
                f"closed-loop spectral radius={spectral_radius:.9g}; stable "
                "threshold is strictly below 1-1e-6"
            )
        )

    if not trajectory_finite:
        violations.append("non_finite_trajectory")
    if hard_bound_crossed:
        violations.append("declared_hard_bound_violation")
    if saturation_fraction > _SATURATION_LIMIT:
        violations.append("sustained_actuator_saturation")

    if (
        pole_status == "unstable"
        or not trajectory_finite
        or not trajectory_bounded
        or saturation_fraction > _SATURATION_LIMIT
    ):
        status = "unstable"
    elif pole_status == "boundary" or sampled_rollout_status in {
        "boundary",
        "analysis_failed",
    }:
        status = "inconclusive"
    else:
        status = "stable"

    evidence.extend(
        [
            (
                "rollout remained finite"
                if trajectory_finite
                else "rollout stopped before a non-finite sample was stored"
            ),
            (
                "rollout stayed inside all declared hard state/output bounds"
                if trajectory_bounded
                else (
                    "rollout crossed a declared hard state/output bound"
                    if hard_bound_crossed
                    else (
                        "the actual sampled rollout map is numerically "
                        "unbounded at the requested sample time"
                    )
                )
            ),
            (
                f"actuator saturation fraction={saturation_fraction:.6g}; "
                "stable trials require at most 0.1"
            ),
            (
                "tail error-envelope contraction="
                f"{contraction:.6g}; recorded for iteration diagnostics and "
                "not used as a linear performance gate"
            ),
        ]
    )
    return StabilityDecision(
        status=status,
        analysis_domain=plant.domain,
        pole_analysis_method=plant.pole_analysis_method,
        poles=pole_values,
        spectral_radius=spectral_radius,
        trajectory_finite=trajectory_finite,
        trajectory_bounded=trajectory_bounded,
        tail_error_envelope_contraction=contraction,
        saturation_fraction=saturation_fraction,
        violations=list(dict.fromkeys(violations)),
        evidence=evidence,
    )


def run_linear_closed_loop(
    model: TransferFunctionModelSpec | StateSpaceModelSpec,
    controller: ControllerRuntimeSpec,
    *,
    reference: ReferenceValue,
    horizon_s: float,
    sample_time_s: float,
    actuator_bounds: BoundMap | None = None,
    state_bounds: BoundMap | None = None,
    output_bounds: BoundMap | None = None,
) -> LinearSimulationResult:
    """Run and evaluate one typed, stability-only linear closed-loop trial.

    ``actuator_bounds`` are saturation limits.  ``state_bounds`` and
    ``output_bounds`` are hard safety limits that abort a rollout immediately.
    No overshoot, settling-time, IAE, or other performance limit is accepted
    by this API.
    """

    horizon_s = float(horizon_s)
    sample_time_s = float(sample_time_s)
    if not math.isfinite(horizon_s) or horizon_s <= 0.0:
        raise ValueError("horizon_s must be finite and positive")
    if not math.isfinite(sample_time_s) or sample_time_s <= 0.0:
        raise ValueError("sample_time_s must be finite and positive")
    plant = _normalize_plant(model, sample_time_s)
    _validate_runtime_compatibility(model, plant, controller)
    reference_vector = _normalize_reference(reference, plant.output_names)
    actuator_limits = _normalize_bounds(
        actuator_bounds, plant.input_names, label="actuator"
    )
    state_limits = _normalize_bounds(state_bounds, plant.state_names, label="state")
    output_limits = _normalize_bounds(output_bounds, plant.output_names, label="output")
    trace = _simulate(
        plant,
        controller,
        reference_vector,
        actuator_bounds=actuator_limits,
        state_bounds=state_limits,
        output_bounds=output_limits,
        horizon_s=horizon_s,
        sample_time_s=sample_time_s,
    )
    stability = _evaluate_stability(plant, controller, trace, sample_time_s)
    return LinearSimulationResult(trace=trace, stability=stability)


__all__ = ["LinearSimulationResult", "run_linear_closed_loop"]
