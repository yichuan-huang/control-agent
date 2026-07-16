from __future__ import annotations

import math

import numpy as np
from scipy import signal

from cfdc.evidence import plant_id_for_description
from cfdc.models import (
    CompiledSpecificationModel,
    RegisteredNonlinearModelSpec,
    SpecificationAssessment,
    SpecificationFact,
    SpecificationTemplate,
    StateSpaceModelSpec,
    SystemDescription,
    TransferFunctionModelSpec,
)
from cfdc.specifications.units import normalize_scalar_unit, resolve_unit


def _facts(assessment: SpecificationAssessment) -> dict[str, SpecificationFact]:
    if assessment.status != "ready":
        raise ValueError("only a ready specification assessment can be compiled")
    return {item.fact_id: item for item in assessment.facts}


def _scalar(facts: dict[str, SpecificationFact], fact_id: str) -> float:
    fact = facts[fact_id]
    if not isinstance(fact.value, float):
        raise ValueError(f"specification fact '{fact_id}' must be scalar")
    value, _ = normalize_scalar_unit(fact.value, fact.unit)
    return value


def _canonical_unit(unit: str) -> str:
    return resolve_unit(unit).canonical_unit


def _sources(*fact_ids: str) -> list[str]:
    return list(fact_ids)


def _signal_name(values: list[str], fallback: str) -> str:
    return values[0] if values else fallback


def _common_bounds(facts: dict[str, SpecificationFact]) -> dict[str, float]:
    bounds: dict[str, float] = {}
    for fact_id in ("input_min", "input_max", "output_min", "output_max"):
        if fact_id in facts:
            bounds[fact_id] = _scalar(facts, fact_id)
    if {"input_min", "input_max"}.issubset(bounds):
        bounds["input_range"] = bounds["input_max"] - bounds["input_min"]
        bounds["max_abs_control"] = max(
            abs(bounds["input_min"]), abs(bounds["input_max"])
        )
        bounds["per_input_limit"] = bounds["max_abs_control"]
    if {"output_min", "output_max"}.issubset(bounds):
        bounds["state_range"] = bounds["output_max"] - bounds["output_min"]
        bounds["max_abs_position"] = max(
            abs(bounds["output_min"]), abs(bounds["output_max"])
        )
    return bounds


def _first_order_model(
    description: SystemDescription,
    facts: dict[str, SpecificationFact],
    *,
    with_delay: bool,
):
    input_change = _scalar(facts, "input_change")
    output_change = _scalar(facts, "steady_output_change")
    if input_change == 0.0:
        raise ValueError("input_change must be non-zero")
    gain = output_change / input_change
    tau = _scalar(facts, "response_time_s")
    if tau <= 0.0:
        raise ValueError("response_time_s must be positive")
    delay = _scalar(facts, "dead_time_s") if with_delay else 0.0
    input_fact = facts["input_change"]
    output_fact = facts["steady_output_change"]
    model = TransferFunctionModelSpec(
        numerator=[gain],
        denominator=[tau, 1.0],
        input_delay_s=delay,
        input_signal_id=_signal_name(description.actuators, "input"),
        output_signal_id=_signal_name(description.observed_outputs, "output"),
        input_units=_canonical_unit(input_fact.unit),
        output_units=_canonical_unit(output_fact.unit),
    )
    derived = {"static_gain": gain, "time_constant": tau}
    sources = {
        "static_gain": _sources("input_change", "steady_output_change"),
        "time_constant": _sources("response_time_s"),
    }
    if with_delay:
        derived["dead_time"] = delay
        sources["dead_time"] = _sources("dead_time_s")
    return model, derived, sources, max(tau, delay, 1e-6), []


def _second_order_model(
    description: SystemDescription,
    facts: dict[str, SpecificationFact],
):
    assumptions: list[str] = []
    if "oscillation_period_s" in facts:
        period = _scalar(facts, "oscillation_period_s")
        if period <= 0.0:
            raise ValueError("oscillation_period_s must be positive")
        omega = 2.0 * math.pi / period
        ratio = _scalar(facts, "successive_peak_ratio")
        if not 0.0 < ratio < 1.0:
            raise ValueError("successive_peak_ratio must lie strictly between 0 and 1")
        decrement = math.log(1.0 / ratio)
        damping = decrement / math.sqrt((2.0 * math.pi) ** 2 + decrement**2)
        input_change = _scalar(facts, "input_change")
        if input_change == 0.0:
            raise ValueError("input_change must be non-zero")
        input_gain = _scalar(facts, "acceleration_change") / input_change
        sources = {
            "natural_frequency": _sources("oscillation_period_s"),
            "damping_ratio": _sources("successive_peak_ratio"),
            "input_gain": _sources("input_change", "acceleration_change"),
        }
        assumptions.append(
            "The declared peak interval is treated as the damped period; the small-damping canonical conversion is disclosed."
        )
    else:
        mass = _scalar(facts, "mass_kg")
        stiffness = _scalar(facts, "stiffness_n_m")
        viscous = _scalar(facts, "damping_n_s_m")
        actuator = _scalar(facts, "actuator_force_per_input")
        if mass <= 0.0 or stiffness <= 0.0 or viscous < 0.0:
            raise ValueError("mass and stiffness must be positive and damping non-negative")
        omega = math.sqrt(stiffness / mass)
        damping = viscous / (2.0 * math.sqrt(stiffness * mass))
        input_gain = actuator / mass
        sources = {
            "natural_frequency": _sources("mass_kg", "stiffness_n_m"),
            "damping_ratio": _sources("mass_kg", "stiffness_n_m", "damping_n_s_m"),
            "input_gain": _sources("mass_kg", "actuator_force_per_input"),
        }
    model = TransferFunctionModelSpec(
        numerator=[input_gain],
        denominator=[1.0, 2.0 * damping * omega, omega**2],
        input_signal_id=_signal_name(description.actuators, "input"),
        output_signal_id=_signal_name(description.observed_outputs, "position"),
        input_units=_canonical_unit(
            facts.get("input_change", facts.get("actuator_force_per_input")).unit
        ),
        output_units=_canonical_unit(
            facts.get("output_min", facts.get("output_max")).unit
            if facts.get("output_min", facts.get("output_max")) is not None
            else "position_unit"
        ),
    )
    return (
        model,
        {
            "natural_frequency": omega,
            "damping_ratio": damping,
            "input_gain": input_gain,
        },
        sources,
        max(2.0 * math.pi / omega, 1e-6),
        assumptions,
    )


def _double_integrator_model(
    description: SystemDescription,
    facts: dict[str, SpecificationFact],
):
    if "acceleration_change" in facts:
        input_change = _scalar(facts, "input_change")
        if input_change == 0.0:
            raise ValueError("input_change must be non-zero")
        input_gain = _scalar(facts, "acceleration_change") / input_change
        source_ids = _sources("input_change", "acceleration_change")
        input_units = facts["input_change"].unit
    else:
        mass = _scalar(facts, "mass_kg")
        if mass <= 0.0:
            raise ValueError("mass_kg must be positive")
        input_gain = _scalar(facts, "actuator_force_per_input") / mass
        source_ids = _sources("mass_kg", "actuator_force_per_input")
        input_units = facts["actuator_force_per_input"].unit
    model = TransferFunctionModelSpec(
        numerator=[input_gain],
        denominator=[1.0, 0.0, 0.0],
        input_signal_id=_signal_name(description.actuators, "input"),
        output_signal_id=_signal_name(description.observed_outputs, "position"),
        input_units=_canonical_unit(input_units),
        output_units=_canonical_unit(
            facts.get("output_min", facts.get("output_max")).unit
            if facts.get("output_min", facts.get("output_max")) is not None
            else "position_unit"
        ),
    )
    time_scale = _scalar(facts, "motion_time_scale_s")
    if time_scale <= 0.0:
        raise ValueError("motion_time_scale_s must be positive")
    return model, {"input_gain": input_gain}, {"input_gain": source_ids}, time_scale, []


def _inverse_response_severity_for_zero(
    *,
    zero_time_s: float,
    time_constant_s: float,
    recovery_time_s: float,
) -> float:
    """Evaluate the canonical model with the same baseline/tail rule as extraction."""

    duration_s = 8.0 * max(time_constant_s, recovery_time_s)
    time_s = np.linspace(0.0, duration_s, 3201)
    input_signal = np.zeros_like(time_s)
    input_signal[len(time_s) // 10 :] = 1.0
    model = signal.TransferFunction(
        [-zero_time_s, 1.0],
        [
            time_constant_s * recovery_time_s,
            time_constant_s + recovery_time_s,
            1.0,
        ],
    )
    _, response, _ = signal.lsim(model, U=input_signal, T=time_s)
    head = max(3, len(response) // 10)
    tail = max(3, len(response) // 5)
    baseline = float(np.median(response[:head]))
    settled = float(np.median(response[-tail:]))
    total_change = settled - baseline
    if abs(total_change) <= 1e-12:
        raise ValueError("canonical inverse-response model has no resolvable final change")
    reverse = (
        max(0.0, baseline - float(np.min(response)))
        if total_change >= 0.0
        else max(0.0, float(np.max(response)) - baseline)
    )
    return reverse / abs(total_change)


def _calibrate_inverse_zero_time(
    *,
    target_severity: float,
    time_constant_s: float,
    recovery_time_s: float,
) -> float:
    """Find the RHP-zero time that reproduces the explicitly declared undershoot."""

    if target_severity <= 0.0:
        raise ValueError("inverse_peak_change must describe a non-zero reverse motion")
    lower = 0.0
    upper = max(time_constant_s, recovery_time_s)
    for _ in range(20):
        if _inverse_response_severity_for_zero(
            zero_time_s=upper,
            time_constant_s=time_constant_s,
            recovery_time_s=recovery_time_s,
        ) >= target_severity:
            break
        upper *= 2.0
    else:
        raise ValueError("declared inverse-response severity cannot be represented by the canonical template")

    for _ in range(50):
        midpoint = 0.5 * (lower + upper)
        observed = _inverse_response_severity_for_zero(
            zero_time_s=midpoint,
            time_constant_s=time_constant_s,
            recovery_time_s=recovery_time_s,
        )
        if observed < target_severity:
            lower = midpoint
        else:
            upper = midpoint
    return 0.5 * (lower + upper)


def _nmp_model(description: SystemDescription, facts: dict[str, SpecificationFact]):
    input_change = _scalar(facts, "input_change")
    steady = _scalar(facts, "steady_output_change")
    inverse = abs(_scalar(facts, "inverse_peak_change"))
    if input_change == 0.0 or steady == 0.0:
        raise ValueError("inverse-response input and steady output changes must be non-zero")
    gain = steady / input_change
    tau = _scalar(facts, "response_time_s")
    fast_tau = _scalar(facts, "inverse_recovery_time_s")
    if tau <= 0.0 or fast_tau <= 0.0:
        raise ValueError("inverse-response time values must be positive")
    severity = inverse / abs(steady)
    zero_time = _calibrate_inverse_zero_time(
        target_severity=severity,
        time_constant_s=tau,
        recovery_time_s=fast_tau,
    )
    model = TransferFunctionModelSpec(
        numerator=[-gain * zero_time, gain],
        denominator=[tau * fast_tau, tau + fast_tau, 1.0],
        input_signal_id=_signal_name(description.actuators, "input"),
        output_signal_id=_signal_name(description.observed_outputs, "output"),
        input_units=_canonical_unit(facts["input_change"].unit),
        output_units=_canonical_unit(facts["steady_output_change"].unit),
    )
    return (
        model,
        {
            "static_gain": gain,
            "time_constant": tau,
            "inverse_response_severity": severity,
        },
        {
            "static_gain": _sources("input_change", "steady_output_change"),
            "time_constant": _sources("response_time_s"),
            "inverse_response_severity": _sources(
                "inverse_peak_change", "steady_output_change", "inverse_recovery_time_s"
            ),
        },
        max(tau, fast_tau),
        [
            "The compiler uses a disclosed two-pole/right-half-plane-zero canonical approximation; its zero is deterministically calibrated so the simulated reverse-motion ratio matches the declared behavior, and it is not an identified full plant model."
        ],
    )


def _registered_model(
    description: SystemDescription,
    facts: dict[str, SpecificationFact],
    template_id: str,
):
    if template_id == "underactuated_cartpole":
        parameter_ids = {
            "cart_mass_kg", "pole_mass_kg", "com_length_m",
            "pole_inertia_kg_m2", "cart_friction_n_s_m", "gravity_m_s2",
            "force_limit_n", "cart_position_limit_m",
        }
        parameters = {
            fact_id: _scalar(facts, fact_id) for fact_id in parameter_ids
        }
        input_ids = description.actuators or ["force"]
        output_ids = description.observed_outputs or ["position", "angle"]
        model = RegisteredNonlinearModelSpec(
            template_id="underactuated_cartpole",
            parameters=parameters,
            initial_state={"position_m": 0.0, "velocity_m_s": 0.0, "angle_rad": 0.0, "angular_rate_rad_s": 0.0},
            input_signal_ids=input_ids,
            output_signal_ids=output_ids,
            signal_units={
                **{signal_id: "N" for signal_id in input_ids},
                **{
                    signal_id: "m" if index == 0 else "rad"
                    for index, signal_id in enumerate(output_ids)
                },
            },
        )
        omega = math.sqrt(parameters["gravity_m_s2"] / parameters["com_length_m"])
        return model, {"natural_frequency": omega}, {
            "natural_frequency": _sources(
                "cart_mass_kg", "pole_mass_kg", "com_length_m",
                "pole_inertia_kg_m2", "gravity_m_s2"
            )
        }, 1.0 / omega, ["Zero initial state is used for specification-model feature scheduling only."]
    parameter_ids = {
        "mass_kg", "pitch_inertia_kg_m2", "gravity_m_s2",
        "linear_drag_n_s_m", "pitch_damping_n_m_s", "thrust_min_n",
        "thrust_max_n", "torque_limit_n_m",
    }
    parameters = {fact_id: _scalar(facts, fact_id) for fact_id in parameter_ids}
    input_ids = description.actuators or ["thrust", "torque"]
    output_ids = description.observed_outputs or ["position", "altitude", "pitch"]
    model = RegisteredNonlinearModelSpec(
        template_id="vtol_cascaded",
        parameters=parameters,
        initial_state={
            "x_m": 0.0,
            "z_m": 0.0,
            "pitch_rad": 0.0,
            "x_velocity_m_s": 0.0,
            "z_velocity_m_s": 0.0,
            "pitch_rate_rad_s": 0.0,
        },
        input_signal_ids=input_ids,
        output_signal_ids=output_ids,
        signal_units={
            **{
                signal_id: "N" if index == 0 else "Nm"
                for index, signal_id in enumerate(input_ids)
            },
            **{
                signal_id: "rad" if index == len(output_ids) - 1 else "m"
                for index, signal_id in enumerate(output_ids)
            },
        },
    )
    return model, {
        "hover_thrust": parameters["mass_kg"] * parameters["gravity_m_s2"],
        "angular_acceleration_gain": 1.0 / parameters["pitch_inertia_kg_m2"],
        "lateral_coupling_gain": parameters["gravity_m_s2"],
    }, {
        "hover_thrust": _sources("mass_kg", "gravity_m_s2"),
        "angular_acceleration_gain": _sources("pitch_inertia_kg_m2"),
        "lateral_coupling_gain": _sources("gravity_m_s2"),
    }, _scalar(facts, "response_time_s"), [
        "Zero hover initial state is used for specification-model feature scheduling only.",
        "Initial vertical bandwidth uses the disclosed CFDC specification-policy factor 0.1 divided by the declared response time.",
    ]


def _mimo_model(description: SystemDescription, facts: dict[str, SpecificationFact]):
    matrix = facts["local_gain_matrix"].value
    if not isinstance(matrix, list) or len(matrix) != 2 or any(
        not isinstance(row, list) or len(row) != 2 for row in matrix
    ):
        raise ValueError("local_gain_matrix must be an explicit 2x2 matrix")
    tau = _scalar(facts, "local_time_constant_s")
    if tau <= 0.0:
        raise ValueError("local_time_constant_s must be positive")
    gain = [[float(value) for value in row] for row in matrix]
    model = StateSpaceModelSpec(
        a=[[-1.0 / tau, 0.0], [0.0, -1.0 / tau]],
        b=[[value / tau for value in row] for row in gain],
        c=[[1.0, 0.0], [0.0, 1.0]],
        d=[[0.0, 0.0], [0.0, 0.0]],
        state_names=["local_output_state_1", "local_output_state_2"],
        input_signal_ids=description.actuators[:2] or ["input_1", "input_2"],
        output_signal_ids=description.observed_outputs[:2] or ["output_1", "output_2"],
        initial_state=[0.0, 0.0],
        signal_units={name: "declared_unit" for name in [*description.actuators, *description.observed_outputs]},
    )
    return model, {"local_gain_matrix": gain, "local_time_constant": tau}, {
        "local_gain_matrix": _sources("local_gain_matrix"),
        "local_time_constant": _sources("local_time_constant_s"),
    }, tau, ["A common first-order local time constant is used for both declared output channels."]


def compile_specification_model(
    *,
    description: SystemDescription,
    template: SpecificationTemplate,
    assessment: SpecificationAssessment,
    plant_id: str | None = None,
) -> CompiledSpecificationModel:
    facts = _facts(assessment)
    if template.compiler_id == "first_order":
        components = _first_order_model(description, facts, with_delay=False)
    elif template.compiler_id == "first_order_delay":
        components = _first_order_model(description, facts, with_delay=True)
    elif template.compiler_id == "second_order":
        components = _second_order_model(description, facts)
    elif template.compiler_id == "double_integrator":
        components = _double_integrator_model(description, facts)
    elif template.compiler_id == "nmp_inverse_response":
        components = _nmp_model(description, facts)
    elif template.compiler_id == "cartpole":
        components = _registered_model(description, facts, "underactuated_cartpole")
    elif template.compiler_id == "vtol":
        components = _registered_model(description, facts, "vtol_cascaded")
    elif template.compiler_id == "mimo_first_order":
        components = _mimo_model(description, facts)
    else:
        raise ValueError(
            "this method profile cannot be compiled from natural-language specifications; provide a complete numeric model"
        )
    model, derived, sources, time_scale, assumptions = components
    bounds = _common_bounds(facts)
    if template.compiler_id == "cartpole":
        position_limit = _scalar(facts, "cart_position_limit_m")
        force_limit = _scalar(facts, "force_limit_n")
        bounds.update({
            "max_abs_force": force_limit,
            "input_min": -force_limit,
            "input_max": force_limit,
            "max_abs_position": position_limit,
            "output_min": -position_limit,
            "output_max": position_limit,
            "state_range": 2.0 * position_limit,
        })
    elif template.compiler_id == "vtol":
        bounds.update({
            "gravity": _scalar(facts, "gravity_m_s2"),
            "max_torque": _scalar(facts, "torque_limit_n_m"),
            "min_thrust": _scalar(facts, "thrust_min_n"),
            "max_thrust": _scalar(facts, "thrust_max_n"),
            "max_tilt_rad": _scalar(facts, "max_tilt_rad"),
            "max_altitude_error": _scalar(facts, "max_altitude_error"),
            "vertical_bandwidth_rad_s": 0.1
            / _scalar(facts, "response_time_s"),
        })
    elif template.compiler_id == "double_integrator":
        bounds.update({
            "initial_bandwidth_rad_s": 0.1
            / _scalar(facts, "motion_time_scale_s"),
            "initial_damping_ratio": 1.15,
        })
        assumptions.append(
            "Initial bandwidth uses the versioned CFDC specification-policy factor 0.1 divided by the declared motion time; damping ratio 1.15 is a disclosed dimensionless conservative policy value."
        )
    return CompiledSpecificationModel(
        plant_id=plant_id or plant_id_for_description(description),
        template_id=template.template_id,
        model=model,
        derived_features=derived,
        parameter_sources=sources,
        safety_bounds=bounds,
        time_scale_hint_s=max(float(time_scale), 1e-6),
        assumptions=assumptions,
    )
