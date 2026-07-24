from __future__ import annotations

from cfdc.web.model_discovery_presentation import render_model_discovery
from tests.test_model_discovery_session import (
    session_with_questions,
    session_with_ready_result,
)


def test_question_view_combines_plain_question_example_and_adoption():
    view = render_model_discovery(session_with_questions())

    slot = view["questions"][0]
    assert slot["prompt"] == "你把加热功率从多少调到多少？"
    assert "500 W" in slot["example_text"]
    assert slot["adopt_label"] == "采用此示例值"
    assert slot["answer_text"] == ""


def test_generated_model_card_prefers_language_and_equations_over_json():
    view = render_model_discovery(session_with_ready_result())

    assert "AI 对系统的理解" in view["model_card_markdown"]
    assert "$$" in view["model_card_markdown"]
    assert "参数与来源" in view["model_card_markdown"]
    assert "执行器范围 heater_power" in view["model_card_markdown"]
    assert "输出范围 temperature" in view["model_card_markdown"]
    assert view["show_technical_json"] is True
    assert view["technical_json_open"] is False
    assert view["technical_json"]["model"]["kind"] == "transfer_function"
