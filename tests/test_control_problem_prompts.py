from pathlib import Path
import math
import re


ENGLISH_PATH = Path("dataset/control_problem_prompts.md")
CHINESE_PATH = Path("dataset/control_problem_prompts_cn.md")
ENGLISH_HEADINGS = [
    "Control Problem Description",
    "Observable Outputs",
    "Actuators",
    "Safety Bounds",
    "Forbidden Actions",
    "Dominant Time Scale (Seconds)",
]
CHINESE_HEADINGS = [
    "控制问题描述",
    "可观察输出",
    "执行器",
    "安全边界",
    "禁止实验动作",
    "主导时间尺度（秒）",
]
HAN_PATTERN = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")
MATH_NOTATION_PATTERN = re.compile(r"[0-9=<>+*/^\\{}\[\]$]")


def _field(entry: str, heading: str) -> str:
    match = re.search(
        rf"^### {re.escape(heading)}\s*$\n(.*?)(?=^### |^---\s*$|\Z)",
        entry,
        re.MULTILINE | re.DOTALL,
    )
    assert match is not None, f"missing heading: {heading}"
    return match.group(1).strip()


def _parse_bounds(raw: str) -> dict[str, float]:
    bounds = {}
    for line in raw.splitlines():
        name, separator, value = line.partition("=")
        assert name.strip() and separator and math.isfinite(float(value)), line
        bounds[name.strip()] = float(value)
    assert bounds
    return bounds


def _parse_document(path: Path, headings: list[str], language: str) -> list[dict]:
    markdown = path.read_text(encoding="utf-8")
    title_matches = re.findall(r"^## (\d+)\. (.+)$", markdown, re.MULTILINE)
    entries = re.split(r"^## \d+\. .+$", markdown, flags=re.MULTILINE)[1:]

    assert len(title_matches) == len(entries) == 20
    assert [int(number) for number, _ in title_matches] == list(range(1, 21))
    assert "~~~json" not in markdown

    parsed = []
    for index, ((number, title), entry) in enumerate(zip(title_matches, entries), 1):
        assert int(number) == index
        assert re.findall(r"^### (.+)$", entry, re.MULTILINE) == headings, index

        description = _field(entry, headings[0])
        if language == "en":
            sentences = re.split(r"(?<=[.!?])\s+", description)
        else:
            sentences = re.findall(r"[^。！？]+[。！？]", description)
        assert len(sentences) == 8, (language, index, len(sentences))
        assert not MATH_NOTATION_PATTERN.search(description), (language, index)

        outputs = _field(entry, headings[1])
        actuators = _field(entry, headings[2])
        actions = [line.strip() for line in _field(entry, headings[4]).splitlines() if line.strip()]
        time_scale = float(_field(entry, headings[5]))
        assert outputs and actuators and actions and time_scale > 0.0

        parsed.append(
            {
                "title": title,
                "description": description,
                "outputs": outputs,
                "actuators": actuators,
                "bounds": _parse_bounds(_field(entry, headings[3])),
                "actions": actions,
                "time_scale": time_scale,
            }
        )
    return parsed


def test_english_control_problem_prompts_are_fully_english_and_match_the_ui_contract():
    markdown = ENGLISH_PATH.read_text(encoding="utf-8")
    entries = _parse_document(ENGLISH_PATH, ENGLISH_HEADINGS, "en")

    assert not HAN_PATTERN.search(markdown)
    assert all(not HAN_PATTERN.search(item["title"]) for item in entries)


def test_chinese_control_problem_prompts_are_fully_translated_and_match_the_ui_contract():
    entries = _parse_document(CHINESE_PATH, CHINESE_HEADINGS, "cn")

    for item in entries:
        assert HAN_PATTERN.search(item["title"])
        assert HAN_PATTERN.search(item["description"])
        assert HAN_PATTERN.search(item["outputs"])
        assert HAN_PATTERN.search(item["actuators"])
        assert all(HAN_PATTERN.search(action) for action in item["actions"])


def test_english_and_chinese_prompt_documents_preserve_numeric_and_structural_parity():
    english = _parse_document(ENGLISH_PATH, ENGLISH_HEADINGS, "en")
    chinese = _parse_document(CHINESE_PATH, CHINESE_HEADINGS, "cn")

    assert len(english) == len(chinese) == 20
    for index, (english_item, chinese_item) in enumerate(zip(english, chinese), 1):
        assert english_item["bounds"] == chinese_item["bounds"], index
        assert english_item["time_scale"] == chinese_item["time_scale"], index
        assert len(english_item["actions"]) == len(chinese_item["actions"]), index
