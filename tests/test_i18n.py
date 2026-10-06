from __future__ import annotations

import json
from importlib.resources import files
from string import Formatter

import pytest


def test_catalogs_have_identical_keys_and_named_parameters():
    root = files("cfdc").joinpath("resources/locales")
    en_files = {
        file.name
        for file in root.joinpath("en").iterdir()
        if file.name.endswith(".json")
    }
    zh_files = {
        file.name
        for file in root.joinpath("zh-CN").iterdir()
        if file.name.endswith(".json")
    }
    assert (
        en_files
        == zh_files
        == {"frontend.json", "web.json", "presentation.json", "doctor.json"}
    )
    formatter = Formatter()
    for name in en_files:
        en = json.loads(root.joinpath("en", name).read_text(encoding="utf-8"))
        zh = json.loads(root.joinpath("zh-CN", name).read_text(encoding="utf-8"))
        assert en.keys() == zh.keys(), name
        assert en, name
        for key in en:
            assert en[key] and zh[key], key
            assert {
                field
                for _, field, _, _ in formatter.parse(en[key])
                if field is not None
            } == {
                field
                for _, field, _, _ in formatter.parse(zh[key])
                if field is not None
            }, key


def test_messages_are_explicit_and_do_not_translate_parameter_values():
    from cfdc.i18n import message_ref, render_message, t

    assert t("web.error.case_not_found", "en") == "This built-in case was not found."
    assert t("web.error.case_not_found", "zh-CN") == "未找到此内置案例。"
    ref = message_ref("web.error.case_not_found")
    assert ref == {"key": "web.error.case_not_found", "params": {}}
    assert render_message(ref, "en") == t(ref["key"], "en")
    assert (
        render_message(
            message_ref("presentation.contract.unknown_action", action="原始值"), "en"
        )
        == "Unknown pending action: 原始值"
    )
    with pytest.raises(KeyError):
        t("missing.message", "en")
    with pytest.raises(ValueError):
        t("web.error.case_not_found", "fr")
