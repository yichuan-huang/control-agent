"""Sanitize historical execution records; no executable registry or bindings."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

VERSION = "cfdc-managed-execution/v1"


def public_managed_execution(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            k: public_managed_execution(v)
            for k, v in value.items()
            if k
            not in {
                "path",
                "bundle_path",
                "output_dir",
                "result_path",
                "package_path",
                "packet_path",
                "freeze_path",
                "directory",
            }
        }
    if isinstance(value, (list, tuple)):
        return [public_managed_execution(v) for v in value]
    return value
