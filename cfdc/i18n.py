"""Explicit presentation messages shared with the browser, never artifact translation."""

from __future__ import annotations

import json
from collections.abc import Mapping
from functools import lru_cache
from importlib.resources import files
from typing import Any, Literal

Locale = Literal["en", "zh-CN"]


@lru_cache(maxsize=2)
def catalog(locale: Locale) -> dict[str, str]:
    if locale not in {"en", "zh-CN"}:
        raise ValueError("unsupported_locale")
    directory = files("cfdc").joinpath("resources", "locales", locale)
    messages: dict[str, str] = {}
    for path in sorted(directory.iterdir(), key=lambda item: item.name):
        if path.name.endswith(".json"):
            values = json.loads(path.read_text(encoding="utf-8"))
            if messages.keys() & values.keys():
                raise ValueError("duplicate_message_key")
            messages.update(values)
    return messages


def has_message(key: str) -> bool:
    return key in catalog("en")


def t(key: str, locale: Locale = "zh-CN", **params: Any) -> str:
    messages = catalog(locale)
    template = messages.get(key)
    if template is None:
        template = catalog("en")[key]
    return template.format(**params)


def message_ref(key: str, **params: Any) -> dict[str, Any]:
    return {"key": key, "params": params}


def render_message(ref: Mapping[str, Any], locale: Locale = "zh-CN") -> str:
    return t(str(ref["key"]), locale, **dict(ref.get("params") or {}))
