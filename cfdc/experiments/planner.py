from __future__ import annotations

from cfdc.models import (
    ArchetypeClass,
    ArchetypeClassification,
    CapabilityGap,
    ExperimentInstruction,
    ExperimentPlan,
    ExperimentPrimitive,
    StructuralDiagnosis,
    SystemDescription,
)


_PRIMITIVE_FORBIDDEN_ALIASES: dict[str, tuple[str, ...]] = {
    ExperimentPrimitive.FREE_DECAY.value: (
        "free decay",
        "free release",
        "release",
        "let go",
    ),
    ExperimentPrimitive.RAMP_STEP.value: ("ramp", "step", "input change"),
    ExperimentPrimitive.PULSE.value: ("pulse", "nudge", "push", "twist"),
    ExperimentPrimitive.HOVER_THRUST.value: ("hover", "lift", "thrust ramp"),
    ExperimentPrimitive.BOUNDED_SCAN.value: ("bounded scan", "scan"),
}


def _normalized(value: str) -> str:
    return " ".join(value.lower().replace("_", " ").replace("-", " ").split())


def _first_positive(
    bounds: dict[str, float],
    aliases: tuple[str, ...],
) -> tuple[str, float] | None:
    normalized = {_normalized(name): value for name, value in bounds.items()}
    for alias in aliases:
        value = normalized.get(_normalized(alias))
        if value is not None and value > 0.0:
            return alias, float(value)
    return None


def _forbidden(
    primitive: str,
    forbidden_actions: list[str],
) -> str | None:
    aliases = _PRIMITIVE_FORBIDDEN_ALIASES[primitive]
    for action in forbidden_actions:
        normalized_action = _normalized(action)
        if any(_normalized(alias) in normalized_action for alias in aliases):
            return action
    return None


def _duration_for(primitive: str, time_scale_s: float) -> float:
    if primitive == ExperimentPrimitive.PULSE.value:
        return min(0.5, max(0.02, 0.1 * time_scale_s))
    if primitive == ExperimentPrimitive.FREE_DECAY.value:
        return 6.0 * time_scale_s
    if primitive == ExperimentPrimitive.HOVER_THRUST.value:
        return 5.0 * time_scale_s
    return 8.0 * time_scale_s


def _bound_for_instruction(
    primitive: str,
    description: SystemDescription,
) -> tuple[float | None, str, str, float]:
    bounds = description.safety_bounds
    actuator = _first_positive(
        bounds,
        (
            "max_abs_control",
            "max_abs_force",
            "force_limit",
            "max_force",
            "max_torque",
            "max_abs_torque",
            "torque_limit",
        ),
    )
    thrust = _first_positive(
        bounds,
        ("max_thrust", "thrust_max", "max_abs_thrust", "thrust_limit"),
    )
    input_range = _first_positive(
        bounds,
        ("input_range", "actuator_range", "control_range", "command_range"),
    )
    state_range = _first_positive(
        bounds,
        ("state_range", "travel_range", "position_range", "angle_range"),
    )
    state_abs = _first_positive(
        bounds,
        (
            "max_abs_position",
            "position_limit",
            "max_abs_angle",
            "max_tilt_rad",
            "state_limit",
        ),
    )

    if primitive == ExperimentPrimitive.FREE_DECAY.value:
        if state_range is not None:
            name, value = state_range
            return 0.10 * value, "state_units", name, value
        if state_abs is not None:
            name, value = state_abs
            return 0.10 * (2.0 * value), "state_units", name, value
        return None, "state_units", "state_range", 0.0

    if primitive == ExperimentPrimitive.HOVER_THRUST.value:
        selected = thrust
        scale = 0.05
    elif primitive in {
        ExperimentPrimitive.RAMP_STEP.value,
        ExperimentPrimitive.BOUNDED_SCAN.value,
    }:
        if input_range is not None:
            name, value = input_range
            return 0.05 * value, "actuator_units", name, value
        if actuator is not None:
            name, value = actuator
            return 0.05 * (2.0 * value), "actuator_units", name, value
        return None, "actuator_units", "input_range", 0.0
    else:
        selected = actuator
        scale = 0.05

    if selected is None:
        return None, "actuator_units", "actuator_limit", 0.0
    name, value = selected
    return scale * value, "actuator_units", name, value


def _parameterize_plan(
    plan: ExperimentPlan,
    description: SystemDescription,
) -> ExperimentPlan:
    time_scale_s = description.time_scale_hint_s or 1.0
    sample_rate_hz = max(50.0 / time_scale_s, 20.0)
    instructions: list[ExperimentInstruction] = []
    gaps: list[CapabilityGap] = []

    for instruction in plan.instructions:
        primitive = str(instruction.primitive)
        forbidden_action = _forbidden(primitive, description.forbidden_actions)
        if forbidden_action is not None:
            gaps.append(
                CapabilityGap(
                    code="forbidden_experiment_action",
                    stage="experiment_design",
                    capability_id=primitive,
                    explanation=(
                        f"Experiment primitive '{primitive}' conflicts with forbidden "
                        f"action '{forbidden_action}'."
                    ),
                    required_next_action=(
                        "select a non-forbidden measurement protocol or revise the "
                        "operator-declared restriction"
                    ),
                )
            )
            continue

        amplitude, units, bound_name, bound_value = _bound_for_instruction(
            primitive,
            description,
        )
        using_normalized_fixture = amplitude is None
        if using_normalized_fixture:
            normalized_description = description.model_copy(
                update={
                    "safety_bounds": {
                        "max_abs_control": 1.0,
                        "max_abs_position": 1.0,
                        "max_thrust": 1.0,
                        "input_range": 2.0,
                        "state_range": 2.0,
                    }
                }
            )
            amplitude, units, _, _ = _bound_for_instruction(
                primitive,
                normalized_description,
            )
            bound_label = "normalized_fixture:max_abs_control_or_state=1.0"
            operating_region = "normalized_simulation_fixture_region"
        elif amplitude is None:
            bound_label = f"missing:{bound_name}"
            operating_region = "declared_safe_operating_region_pending_bound"
            gaps.append(
                CapabilityGap(
                    code="missing_numeric_safety_bound",
                    stage="experiment_design",
                    capability_id=primitive,
                    explanation=(
                        f"Simulation experiment '{primitive}' requires a positive numeric "
                        f"{bound_name}."
                    ),
                    resolvable_by_measurement=True,
                    required_next_action=(
                        f"declare and review {bound_name} before executing the experiment"
                    ),
                )
            )
        else:
            bound_label = f"declared:{bound_name}={bound_value:g}"
            operating_region = "declared_safe_operating_region"

        duration_s = _duration_for(primitive, time_scale_s)
        if amplitude is None:
            numeric_step = (
                f"Do not execute until {bound_name} is declared; then use duration "
                f"{duration_s:g} s and sample at {sample_rate_hz:g} Hz."
            )
        else:
            numeric_step = (
                f"Use input amplitude {amplitude:g} {units} for {duration_s:g} s "
                f"and sample at {sample_rate_hz:g} Hz."
            )
        instructions.append(
            instruction.model_copy(
                update={
                    "operator_steps": [*instruction.operator_steps, numeric_step],
                    "stop_conditions": [
                        *instruction.stop_conditions,
                        f"stop before crossing {bound_label}",
                    ],
                    "input_amplitude": amplitude,
                    "input_amplitude_units": units,
                    "duration_s": duration_s,
                    "sample_rate_hz": sample_rate_hz,
                    "operating_region": operating_region,
                    "required_safety_bounds": [bound_label],
                }
            )
        )

    return plan.model_copy(
        update={
            "instructions": instructions,
            "planning_gaps": gaps,
            "parameterization_status": "blocked" if gaps else "parameterized",
        }
    )


def _instruction(
    primitive: ExperimentPrimitive,
    title: str,
    steps: list[str],
    records: list[str],
    estimates: list[str],
    stop: list[str],
    safety_note: str,
) -> ExperimentInstruction:
    return ExperimentInstruction(
        primitive=primitive,
        title=title,
        operator_steps=steps,
        data_to_record=records,
        estimates=estimates,
        stop_conditions=stop,
        safety_note=safety_note,
    )


def plan_safe_experiments(
    diagnosis: StructuralDiagnosis,
    classification: ArchetypeClassification,
    description: SystemDescription | None = None,
) -> ExperimentPlan:
    archetype = str(classification.primary_class)
    required_features = set(classification.required_core_features)
    instructions: list[ExperimentInstruction] = []

    if archetype == ArchetypeClass.CLASS_I_FIRST_ORDER_LAG.value:
        estimates = ["static_gain", "time_constant"]
        if "dead_time" in classification.required_core_features:
            estimates.append("dead_time")
        instructions.append(
            _instruction(
                ExperimentPrimitive.RAMP_STEP,
                "Small change recording",
                [
                    "Start recording the input setting and the measured output.",
                    "Move the input by a small amount that is well inside the safe range.",
                    "Hold it there until the output stops visibly changing.",
                    "Return the input to its original setting.",
                ],
                ["time", "input setting", "measured output"],
                estimates,
                ["stop if the output crosses a safety limit", "stop if the actuator sounds or feels abnormal"],
                "Use the smallest change that gives a clearly visible response.",
            )
        )
    elif archetype == ArchetypeClass.CLASS_II_SECOND_ORDER_OSCILLATOR.value:
        instructions.append(
            _instruction(
                ExperimentPrimitive.FREE_DECAY,
                "Gentle release recording",
                [
                    "Move the object a small distance away from its resting position.",
                    "Let go without pushing.",
                    "Record the motion until several back-and-forth swings are visible.",
                ],
                ["time", "measured position or angle"],
                ["natural_frequency", "damping_ratio"],
                ["stop if the motion grows instead of shrinking", "stop if the object approaches a travel limit"],
                "Keep the starting displacement small enough that the motion stays in the normal operating region.",
            )
        )
        instructions.append(
            _instruction(
                ExperimentPrimitive.PULSE,
                "Small force pulse recording",
                [
                    "Start recording the force command and measured acceleration.",
                    "Apply one short low-amplitude pulse near the resting position.",
                    "Repeat once with the pulse direction reversed.",
                ],
                ["time", "input setting", "acceleration"],
                ["input_gain"],
                ["stop if displacement approaches its bound", "stop if the actuator saturates"],
                "Keep the pulse short relative to the measured oscillation period.",
            )
        )
    elif archetype == ArchetypeClass.CLASS_III_DOUBLE_OR_PURE_INTEGRATOR.value:
        instructions.append(
            _instruction(
                ExperimentPrimitive.PULSE,
                "Brief nudge recording",
                [
                    "Start recording the input setting and the measured motion.",
                    "Apply a very short small nudge in one direction.",
                    "Wait until the motion is calm, then repeat once in the opposite direction.",
                ],
                ["time", "input setting", "measured position or speed"],
                ["input_gain"],
                ["stop if the object moves more than one quarter of the allowed travel", "stop if it does not slow down after the nudge"],
                "Use alternating directions to cancel offsets in the measurement.",
            )
        )
    elif archetype == ArchetypeClass.CLASS_IV_HIGHER_ORDER_UNSTABLE_NONLINEAR_OR_NMP.value:
        if {"local_static_gain", "local_time_constant", "gain_variation_ratio"} & required_features:
            instructions.append(
                _instruction(
                    ExperimentPrimitive.RAMP_STEP,
                    "Two-region local response recording",
                    [
                        "Choose the first declared safe operating point and record one small input change.",
                        "Return to steady operation before moving to the second declared safe operating point.",
                        "Repeat the same small input change at the second point.",
                        "Return immediately to the safer point after recording.",
                    ],
                    ["time", "input setting", "measured outputs", "operating-point label"],
                    ["local_static_gain", "local_time_constant", "gain_variation_ratio"],
                    [
                        "stop if temperature or conversion leaves its declared local band",
                        "stop if either local response fails to settle",
                    ],
                    "Do not extrapolate either local response beyond the two tested safe regions.",
                )
            )
        elif {"static_gain", "time_constant", "inverse_response_severity"} & required_features:
            estimates = []
            for feature_id in ["static_gain", "time_constant", "dead_time", "inverse_response_severity"]:
                if feature_id in required_features:
                    estimates.append(feature_id)
            instructions.append(
                _instruction(
                    ExperimentPrimitive.RAMP_STEP,
                    "Small change and first-motion recording",
                    [
                        "Start recording the input setting and the measured output.",
                        "Move the input by a small amount that stays well inside the safe range.",
                        "Watch whether the output first moves the expected way or briefly the opposite way.",
                        "Hold the input until the output is no longer visibly changing, then return it to the original setting.",
                    ],
                    ["time", "input setting", "measured output"],
                    estimates,
                    ["stop if the output crosses a safety limit", "stop if the first opposite motion is larger than the agreed safe amount"],
                    "Use a small change only; this recording is meant to reveal the first motion and final settled value.",
                )
            )
        elif "hover_thrust" in required_features:
            instructions.append(
                _instruction(
                    ExperimentPrimitive.HOVER_THRUST,
                    "Light-on-supports recording",
                    [
                        "Place the vehicle on its supports and start recording.",
                        "Increase the lift setting slowly until the supports just begin to feel light.",
                        "Immediately reduce the setting back to zero.",
                        "Repeat several times with the same slow motion.",
                    ],
                    ["time", "lift setting", "vertical motion or support-light signal"],
                    ["hover_thrust"],
                    ["stop if the vehicle leaves the supports", "stop if any tilt becomes visible"],
                    "This is a ground test; do not allow free flight during this recording.",
                )
            )
            instructions.append(
                _instruction(
                    ExperimentPrimitive.PULSE,
                    "Small twist recording",
                    [
                        "Secure the vehicle so it can only rotate by a small amount.",
                        "Press the test button for a short gentle twist.",
                        "Repeat once with the twist direction reversed.",
                    ],
                    ["time", "twist command", "angle rate"],
                    ["angular_acceleration_gain", "lateral_coupling_gain"],
                    ["stop if the angle nears the marked limit", "stop if the mount shifts"],
                    "The vehicle must remain restrained for this recording.",
                )
            )
        else:
            if "natural_frequency" in required_features:
                instructions.append(
                    _instruction(
                        ExperimentPrimitive.FREE_DECAY,
                        "Safe resting-motion recording",
                        [
                            "Put the system in its safest resting position.",
                            "Move the visible part a small distance and let it move freely.",
                            "Record the motion for a few seconds.",
                        ],
                        ["time", "measured angle or position"],
                        ["natural_frequency"],
                        ["stop if the motion grows", "stop if a marked boundary is approached"],
                        "Use only the stable resting position, not the unsafe target position.",
                    )
                )
            if "input_gain" in required_features:
                instructions.append(
                    _instruction(
                        ExperimentPrimitive.PULSE,
                        "Small push recording",
                        [
                            "Start recording.",
                            "Apply one short gentle push using the actuator.",
                            "Repeat in the opposite direction after the motion settles.",
                        ],
                        ["time", "input setting", "measured motion"],
                        ["input_gain"],
                        ["stop if motion exceeds the safe region", "stop if the actuator saturates"],
                        "Keep the push small enough that a person could safely stop the device.",
                    )
                )
            if "input_to_unactuated_coupling_gain" in required_features:
                instructions.append(
                    _instruction(
                        ExperimentPrimitive.PULSE,
                        "Small coupling-direction recording",
                        [
                            "Place the mechanism in its safest resting configuration and start recording both joint motions.",
                            "Apply one short low-amplitude torque pulse to the actuated joint.",
                            "Repeat once in the opposite direction after all motion settles.",
                        ],
                        ["time", "joint torque", "actuated-joint motion", "unactuated-joint motion"],
                        ["input_to_unactuated_coupling_gain"],
                        ["stop if either joint approaches its limit", "stop if the mechanism enters the upright capture region"],
                        "This probe establishes only local coupling direction and scale; it does not authorize swing-up.",
                    )
                )
    else:
        estimates = (
            ["local_gain_matrix", "local_time_constant", "pairing_indicator"]
            if "local_gain_matrix" in required_features
            else ["coupling_gain"]
        )
        instructions.append(
            _instruction(
                ExperimentPrimitive.BOUNDED_SCAN,
                "One-at-a-time movement map",
                [
                    "Start recording all measured outputs.",
                    "Move only the first input by a small amount and return it.",
                    "Repeat for each remaining input, one at a time.",
                    "Do not move two inputs at the same time during this first check.",
                ],
                ["time", "each input setting", "all measured outputs"],
                estimates,
                ["stop if any output crosses its safe band", "stop if one input causes an unexpectedly large motion"],
                "This check is only for deciding safe input-output pairing.",
            )
            )

    covered_features = {feature for instruction in instructions for feature in instruction.estimates}
    missing_features = required_features - covered_features
    if missing_features:
        missing = ", ".join(sorted(missing_features))
        raise ValueError(f"Experiment plan does not cover required core features: {missing}")

    plan = ExperimentPlan(
        archetype=classification.primary_class,
        instructions=instructions,
    )
    if description is None:
        return plan
    return _parameterize_plan(plan, description)
