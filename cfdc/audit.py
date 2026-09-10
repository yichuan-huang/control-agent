"""Credential sanitization for durable audit records."""

from __future__ import annotations

import math
import re
from collections.abc import Mapping, Sequence
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

_URL_RE = re.compile(r"https?://[^\s\"'<>]+", re.IGNORECASE)
_SENSITIVE_MARKERS = ("apikey", "authorization", "token", "secret", "password")


def _normalized_key(key: str) -> str:
    return re.sub(r"[_\-\s]", "", key).casefold()


def _sanitize_url(url: str) -> str:
    try:
        parsed = urlsplit(url)
    except ValueError:
        return "[REDACTED_URL]"
    host = parsed.hostname or ""
    if parsed.port:
        host = f"{host}:{parsed.port}"
    query: list[tuple[str, str]] = []
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        if any(marker in _normalized_key(key) for marker in _SENSITIVE_MARKERS):
            query.append(("redacted", "[REDACTED]"))
        else:
            query.append((key, value))
    return urlunsplit(
        (
            parsed.scheme,
            host,
            parsed.path,
            urlencode(query),
            "",
        )
    )


def _sanitize_string(text: str, secrets: Sequence[str]) -> str:
    clean = text
    for secret in sorted({item for item in secrets if item}, key=len, reverse=True):
        clean = clean.replace(secret, "[REDACTED]")
    clean = re.sub(
        r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+",
        "Bearer [REDACTED]",
        clean,
    )
    clean = re.sub(
        r"(?i)\b(api[_ -]?key|authorization|token|secret|password)"
        r"\s*[:=]\s*[^\s,;\"'}]+",
        lambda match: f"{match.group(1)}=[REDACTED]",
        clean,
    )
    clean = _URL_RE.sub(lambda match: _sanitize_url(match.group(0)), clean)
    return clean[:50_000]


def sanitize_for_audit(value: Any, *, secret_literals: Sequence[str] = ()) -> Any:
    """Recursively redact credentials and URL secrets before hashing/logging."""

    if isinstance(value, Mapping):
        result: dict[str, Any] = {}
        redacted_index = 0
        for key, item in value.items():
            if any(
                marker in _normalized_key(str(key)) for marker in _SENSITIVE_MARKERS
            ):
                redacted_index += 1
                result[f"redacted_{redacted_index}"] = "[REDACTED]"
            else:
                safe_key = _sanitize_string(str(key), secret_literals)
                if safe_key in result:
                    redacted_index += 1
                    safe_key = f"redacted_{redacted_index}"
                result[safe_key] = sanitize_for_audit(
                    item, secret_literals=secret_literals
                )
        return result
    if isinstance(value, (list, tuple)):
        return [
            sanitize_for_audit(item, secret_literals=secret_literals) for item in value
        ]
    if isinstance(value, str):
        return _sanitize_string(value, secret_literals)
    if isinstance(value, float) and not math.isfinite(value):
        return "[REDACTED_NON_FINITE]"
    return value
