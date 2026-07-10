from __future__ import annotations

from cfdc.models import (
    ArchetypeClass,
    ArchetypeClassification,
    ExperimentInstruction,
    ExperimentPlan,
    ExperimentPrimitive,
    StructuralDiagnosis,
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

    return ExperimentPlan(archetype=classification.primary_class, instructions=instructions)
