from __future__ import annotations

import math
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class UnitResolution:
    raw_unit: str
    canonical_unit: str
    dimension: str
    scale: float = 1.0
    known: bool = True


_KNOWN_UNITS: dict[str, tuple[str, str, float]] = {
    "s": ("s", "time", 1.0),
    "ms": ("s", "time", 1e-3),
    "us": ("s", "time", 1e-6),
    "min": ("s", "time", 60.0),
    "h": ("s", "time", 3600.0),
    "V": ("V", "voltage", 1.0),
    "mV": ("V", "voltage", 1e-3),
    "kV": ("V", "voltage", 1e3),
    "A": ("A", "current", 1.0),
    "mA": ("A", "current", 1e-3),
    "W": ("W", "power", 1.0),
    "kW": ("W", "power", 1e3),
    "MW": ("W", "power", 1e6),
    "N": ("N", "force", 1.0),
    "Nm": ("Nm", "torque", 1.0),
    "Pa": ("Pa", "pressure", 1.0),
    "kPa": ("Pa", "pressure", 1e3),
    "MPa": ("Pa", "pressure", 1e6),
    "m": ("m", "length", 1.0),
    "cm": ("m", "length", 1e-2),
    "mm": ("m", "length", 1e-3),
    "rad": ("rad", "angle", 1.0),
    "deg": ("rad", "angle", math.pi / 180.0),
    "kg": ("kg", "mass", 1.0),
    "g": ("kg", "mass", 1e-3),
    "Hz": ("Hz", "frequency", 1.0),
    "kHz": ("Hz", "frequency", 1e3),
    "ratio": ("ratio", "dimensionless_ratio", 1.0),
    "%": ("ratio", "dimensionless_ratio", 1e-2),
    "normalized_input": ("normalized_input", "dimensionless_ratio", 1.0),
    "m/s^2": ("m/s^2", "linear_acceleration", 1.0),
    "rad/s^2": ("rad/s^2", "angular_acceleration", 1.0),
    "deg/s^2": ("rad/s^2", "angular_acceleration", math.pi / 180.0),
    "rad/s": ("rad/s", "angular_rate", 1.0),
    "rpm": ("rad/s", "angular_rate", 2.0 * math.pi / 60.0),
    "kg*m^2": ("kg*m^2", "rotational_inertia", 1.0),
    "N/m": ("N/m", "stiffness", 1.0),
    "Nm/rad": ("Nm/rad", "rotational_stiffness", 1.0),
    "N*s/m": ("N*s/m", "viscous_damping", 1.0),
    "Nm*s/rad": ("Nm*s/rad", "rotational_damping", 1.0),
    "degC": ("degC", "temperature_celsius", 1.0),
    "K": ("K", "temperature_kelvin", 1.0),
    "input_unit": ("input_unit", "declared_input_unit", 1.0),
    "output_unit": ("output_unit", "declared_output_unit", 1.0),
    "output/input": ("output/input", "gain_matrix_unit", 1.0),
    "structured_model": ("structured_model", "structured_model", 1.0),
}

_ALIASES = {
    "sec": "s",
    "second": "s",
    "seconds": "s",
    "millisecond": "ms",
    "milliseconds": "ms",
    "volt": "V",
    "volts": "V",
    "degree": "deg",
    "degrees": "deg",
    "°": "deg",
    "°c": "degC",
    "celsius": "degC",
    "n*m": "Nm",
    "n-m": "Nm",
    "kg·m^2": "kg*m^2",
    "n·s/m": "N*s/m",
}


def normalize_unit_token(unit: str) -> str:
    """Normalize typography and common spellings without inventing a unit."""

    token = str(unit).strip()
    if not token:
        raise ValueError("a specification value must include its unit")
    if any(ord(character) < 32 for character in token):
        raise ValueError("unit contains control characters")
    token = (
        token.replace("²", "^2")
        .replace("³", "^3")
        .replace("−", "-")
        .replace("·", "*")
        .replace("⋅", "*")
        .replace("×", "*")
    )
    token = re.sub(r"\s+", "", token)
    alias = _ALIASES.get(token) or _ALIASES.get(token.casefold())
    return alias or token


def resolve_unit(unit: str) -> UnitResolution:
    normalized = normalize_unit_token(unit)
    definition = _KNOWN_UNITS.get(normalized)
    if definition is None and normalized.endswith("/s^2"):
        base = resolve_unit(normalized[:-4])
        dimension = {
            "length": "linear_acceleration",
            "angle": "angular_acceleration",
        }.get(base.dimension, f"second_derivative:{base.dimension}")
        return UnitResolution(
            raw_unit=str(unit),
            canonical_unit=f"{base.canonical_unit}/s^2",
            dimension=dimension,
            scale=base.scale,
        )
    if definition is None and normalized.count("/") == 1:
        numerator_token, denominator_token = normalized.split("/", 1)
        numerator = resolve_unit(numerator_token)
        denominator = resolve_unit(denominator_token)
        if numerator.known and numerator.dimension in {"force", "torque"}:
            return UnitResolution(
                raw_unit=str(unit),
                canonical_unit=(
                    f"{numerator.canonical_unit}/{denominator.canonical_unit}"
                ),
                dimension=f"{numerator.dimension}_per_{denominator.dimension}",
                scale=numerator.scale / denominator.scale,
            )
    if definition is None:
        return UnitResolution(
            raw_unit=str(unit),
            canonical_unit=normalized,
            dimension=f"opaque:{normalized.casefold()}",
            known=False,
        )
    canonical, dimension, scale = definition
    return UnitResolution(
        raw_unit=str(unit),
        canonical_unit=canonical,
        dimension=dimension,
        scale=scale,
    )


def normalize_scalar_unit(value: float, unit: str) -> tuple[float, str]:
    resolution = resolve_unit(unit)
    return float(value) * resolution.scale, resolution.canonical_unit


def unit_family(unit: str) -> str:
    return resolve_unit(unit).dimension


def unit_is_compatible_with_examples(unit: str, examples: list[str]) -> bool:
    resolution = resolve_unit(unit)
    example_dimensions = {
        item.dimension
        for example in examples
        if (item := resolve_unit(example)).known
    }
    return resolution.known and resolution.dimension in example_dimensions


def unit_is_actuator_per_input(unit: str) -> bool:
    resolution = resolve_unit(unit)
    return resolution.known and (
        resolution.dimension.startswith("force_per_")
        or resolution.dimension.startswith("torque_per_")
    )
