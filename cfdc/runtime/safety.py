from __future__ import annotations

from cfdc.models import SafetyViolation, TrialSample


def check_sample_safety(
    sample: TrialSample,
    constraints: dict[str, float],
) -> list[SafetyViolation]:
    """Check one runtime sample against scalar safety constraints."""

    violations: list[SafetyViolation] = []

    def add_if_exceeds(key: str, observed: float, limit: float, label: str) -> None:
        if observed > limit:
            violations.append(
                SafetyViolation(
                    constraint=key,
                    observed_value=observed,
                    limit=limit,
                    time_s=sample.time_s,
                    message=f"{label} exceeded {limit}",
                )
            )

    if "max_abs_output" in constraints and "output" in sample.state:
        add_if_exceeds(
            "max_abs_output",
            abs(sample.state["output"]),
            constraints["max_abs_output"],
            "absolute output",
        )
    if "max_abs_control" in constraints and "input" in sample.control:
        add_if_exceeds(
            "max_abs_control",
            abs(sample.control["input"]),
            constraints["max_abs_control"],
            "absolute control",
        )
    if "max_abs_position" in constraints and "position" in sample.state:
        add_if_exceeds(
            "max_abs_position",
            abs(sample.state["position"]),
            constraints["max_abs_position"],
            "absolute position",
        )
    if "max_abs_angle" in constraints and "angle" in sample.state:
        add_if_exceeds(
            "max_abs_angle",
            abs(sample.state["angle"]),
            constraints["max_abs_angle"],
            "absolute angle",
        )
    if "min_altitude" in constraints and "altitude" in sample.state:
        observed = sample.state["altitude"]
        limit = constraints["min_altitude"]
        if observed < limit:
            violations.append(
                SafetyViolation(
                    constraint="min_altitude",
                    observed_value=observed,
                    limit=limit,
                    time_s=sample.time_s,
                    message=f"altitude below {limit}",
                )
            )
    if "max_abs_tilt" in constraints and "tilt" in sample.state:
        add_if_exceeds(
            "max_abs_tilt",
            abs(sample.state["tilt"]),
            constraints["max_abs_tilt"],
            "absolute tilt",
        )
    if "max_saturation_fraction" in constraints:
        saturated = sample.metadata.get("saturated")
        if saturated is True:
            add_if_exceeds(
                "instant_saturation",
                1.0,
                0.0,
                "actuator saturation event",
            )
    return violations
