from __future__ import annotations


_TIME_UNIT_SCALE_SECONDS = {
    "s": 1.0,
    "sec": 1.0,
    "second": 1.0,
    "seconds": 1.0,
    "ms": 1e-3,
    "millisecond": 1e-3,
    "milliseconds": 1e-3,
    "us": 1e-6,
    "µs": 1e-6,
    "μs": 1e-6,
    "microsecond": 1e-6,
    "microseconds": 1e-6,
    "ns": 1e-9,
    "nanosecond": 1e-9,
    "nanoseconds": 1e-9,
    "min": 60.0,
    "minute": 60.0,
    "minutes": 60.0,
    "h": 3600.0,
    "hr": 3600.0,
    "hour": 3600.0,
    "hours": 3600.0,
}


def time_unit_scale_seconds(unit: str) -> float:
    """Return the scale to seconds for an explicitly declared timestamp unit."""

    token = str(unit).strip().casefold().replace(" ", "")
    try:
        return _TIME_UNIT_SCALE_SECONDS[token]
    except KeyError as exc:
        raise ValueError(
            f"time unit '{unit}' is not recognized as a duration unit"
        ) from exc
