import re
from collections import Counter
from pathlib import Path

import pytest

TECHNICAL_PATH = Path("dataset/control_problems.md")
ENGLISH_PATH = Path("dataset/control_problem_prompts.md")
CHINESE_PATH = Path("dataset/control_problem_prompts_cn.md")

ENGLISH_HEADINGS = [
    "Control Problem Description",
    "Existing-Record Diagnostic Measurement Response",
    "Profile Measurement Response (Natural Language)",
]
CHINESE_HEADINGS = [
    "控制问题描述",
    "已有记录诊断测量回复",
    "Profile 测量回复（自然语言）",
]
ENGLISH_OLD_HEADINGS = [
    "Observable Outputs",
    "Actuators",
    "Safety Bounds",
    "Forbidden Actions",
    "Dominant Time Scale (Seconds)",
    "Example Data (Natural Language)",
    "Example Data (JSON)",
]
CHINESE_OLD_HEADINGS = [
    "可观察输出",
    "执行器",
    "安全边界",
    "禁止实验动作",
    "主导时间尺度（秒）",
    "示例数据（自然语言）",
    "示例数据（JSON）",
]
MEASUREMENT_FIELDS = [
    "open_loop_stability",
    "minimum_phase",
    "significant_delay",
    "relative_degree",
    "controllability_observability",
    "nonlinearity_strength",
    "coupling_severity",
    "uncertainty_magnitude",
]
ENGLISH_LABELS = [
    "What happens after input restoration",
    "Initial output direction",
    "Time to first change",
    "Number of visible time scales",
    "Can the relevant motion be driven and recorded",
    "Do small positive and negative changes agree",
    "Which readings one action affects",
    "Change across load or operating condition",
]
CHINESE_LABELS = [
    "恢复输入后会怎样",
    "输出最初往哪边变化",
    "多久开始变化",
    "有几个明显快慢阶段",
    "关键运动能否被带动和记录",
    "小幅正反变化是否近似一致",
    "一个作用会影响哪些读数",
    "换负载或工况后变化多大",
]
ASSIGNMENT_TOKENS = [
    "input_change=",
    "steady_output_change=",
    "response_time_s=",
    "input_min=",
    "input_max=",
    "output_min=",
    "output_max=",
    "dead_time_s=",
    "acceleration_change=",
    "motion_time_scale_s=",
]
HAN_PATTERN = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")


def _technical_ids() -> list[int]:
    markdown = TECHNICAL_PATH.read_text(encoding="utf-8")
    matches = re.findall(r"^### (\d+)\. \[Ch(\d+)-(\d+)\] ", markdown, re.MULTILINE)
    ids = [int(global_id) for global_id, _chapter, _local_id in matches]
    chapter_counts = Counter(int(chapter) for _global_id, chapter, _local_id in matches)

    assert ids == list(range(1, 201))
    assert chapter_counts == Counter({chapter: 20 for chapter in range(1, 11)})
    return ids


def _field(entry: str, heading: str) -> str:
    match = re.search(
        rf"^### {re.escape(heading)}\s*$\n(.*?)(?=^### |^---\s*$|\Z)",
        entry,
        re.MULTILINE | re.DOTALL,
    )
    assert match is not None, f"missing heading: {heading}"
    return match.group(1).strip()


def _sentences(description: str, language: str) -> list[str]:
    if language == "en":
        return re.split(r"(?<=[.!?])\s+", description)
    return re.findall(r"[^。！？]+[。！？]", description)


def _parse_document(path: Path, headings: list[str], language: str) -> list[dict]:
    markdown = path.read_text(encoding="utf-8")
    title_matches = re.findall(r"^## (\d+)\. (.+)$", markdown, re.MULTILINE)
    entries = re.split(r"^## \d+\. .+$", markdown, flags=re.MULTILINE)[1:]
    expected_ids = _technical_ids()

    assert len(title_matches) == len(entries) == len(expected_ids) == 200
    assert [int(number) for number, _title in title_matches] == expected_ids
    assert "<!-- GUIDED-UI-PROMPT-AUDIT: natural-language flow -->" in markdown
    assert "```json" not in markdown
    assert '"specification_facts"' not in markdown
    assert '"eight_segment_evidence"' not in markdown
    assert "binary_command" not in markdown
    assert not re.search(r"\b[A-Za-z][A-Za-z0-9_]*_unit\b", markdown)
    assert not any(token in markdown for token in ASSIGNMENT_TOKENS)

    old_headings = ENGLISH_OLD_HEADINGS if language == "en" else CHINESE_OLD_HEADINGS
    for old_heading in old_headings:
        assert f"### {old_heading}\n" not in markdown

    expected_labels = ENGLISH_LABELS if language == "en" else CHINESE_LABELS
    parsed = []
    for index, ((number, title), entry) in enumerate(zip(title_matches, entries), 1):
        assert int(number) == index
        assert re.findall(r"^### (.+)$", entry, re.MULTILINE) == headings, index

        description = _field(entry, headings[0])
        assert "\n\n" not in description, index
        sentences = _sentences(description, language)
        assert 6 <= len(sentences) <= 9, (language, index, len(sentences))
        assert "?" not in description and "？" not in description
        if language == "en":
            assert sentences[0].startswith(("This is ", "These are "))
            assert sentences[1].startswith(
                ("The control input is ", "The control inputs are ")
            )
        else:
            assert sentences[0].startswith("这是")
            assert sentences[1].startswith("控制输入是")

        measurement = _field(entry, headings[1])
        bullets = re.findall(
            r"^- \*\*(.+?)\*\* \(`([^`]+)`\): (.+)$",
            measurement,
            re.MULTILINE,
        )
        assert len(bullets) == 8, (language, index, len(bullets))
        assert [label for label, _field_id, _body in bullets] == expected_labels
        assert [field_id for _label, field_id, _body in bullets] == MEASUREMENT_FIELDS

        for field_id, (_label, _actual_field_id, body) in zip(
            MEASUREMENT_FIELDS, bullets
        ):
            assert body.strip(), (language, index, field_id)
            quote_match = re.search(r"[“\"]([^”\"]+)[”\"]", body)
            assert quote_match is not None, (language, index, field_id)
            assert quote_match.group(1) in description, (language, index, field_id)
        delay_body = bullets[2][2]
        delay_values = re.findall(r"-?\d+(?:\.\d+)?\s*s\b", delay_body)
        assert len(delay_values) >= 2, (language, index, delay_body)

        profile = _field(entry, headings[2])
        assert len(profile) >= 200, (language, index, len(profile))
        assert "```" not in profile
        if language == "en":
            assert (
                "The existing software record" in profile
                or "The declared software model" in profile
            )
            assert "software-simulation stopping boundaries only" in profile
            assert not HAN_PATTERN.search(title)
        else:
            assert "已有软件记录" in profile or "已有软件模型" in profile
            assert "只作为软件仿真的停止边界" in profile
            assert HAN_PATTERN.search(title)
            assert HAN_PATTERN.search(profile)

        parsed.append(
            {
                "title": title,
                "description": description,
                "sentences": sentences,
                "measurement": measurement,
                "bullets": bullets,
                "delay_values": delay_values,
                "profile": profile,
            }
        )
    return parsed


def test_english_prompts_match_the_guided_natural_language_ui_contract():
    markdown = ENGLISH_PATH.read_text(encoding="utf-8")
    entries = _parse_document(ENGLISH_PATH, ENGLISH_HEADINGS, "en")

    assert not HAN_PATTERN.search(markdown)
    assert len({item["description"] for item in entries}) == 200


def test_chinese_prompts_match_the_guided_natural_language_ui_contract():
    entries = _parse_document(CHINESE_PATH, CHINESE_HEADINGS, "cn")

    assert len({item["description"] for item in entries}) == 200
    assert all(HAN_PATTERN.search(item["description"]) for item in entries)


def test_bilingual_prompts_have_strict_structural_and_measurement_parity():
    english = _parse_document(ENGLISH_PATH, ENGLISH_HEADINGS, "en")
    chinese = _parse_document(CHINESE_PATH, CHINESE_HEADINGS, "cn")

    assert len(english) == len(chinese) == 200
    for index, (english_item, chinese_item) in enumerate(zip(english, chinese), 1):
        assert [item[1] for item in english_item["bullets"]] == MEASUREMENT_FIELDS, (
            index
        )
        assert [item[1] for item in chinese_item["bullets"]] == MEASUREMENT_FIELDS, (
            index
        )
        assert english_item["delay_values"] == chinese_item["delay_values"], index
        assert len(english_item["sentences"]) == len(chinese_item["sentences"]), index


def test_profile_responses_preserve_representative_problem_data_as_natural_language():
    english = _parse_document(ENGLISH_PATH, ENGLISH_HEADINGS, "en")
    chinese = _parse_document(CHINESE_PATH, CHINESE_HEADINGS, "cn")

    thermostat_en = english[0]["profile"]
    thermostat_cn = chinese[0]["profile"]
    assert "50 degF" in thermostat_en and "144000 s" in thermostat_en
    assert "50 degF" in thermostat_cn and "144000 s" in thermostat_cn

    cruise_en = english[1]["profile"]
    cruise_cn = chinese[1]["profile"]
    for value in ("1 deg", "10 mph", "5 s", "45 mph", "80 mph"):
        assert value in cruise_en
        assert value in cruise_cn

    assert "transfer function" in english[20]["profile"]
    assert "state-space" in english[24]["profile"]
    assert "registered nonlinear" in english[26]["profile"]
    assert "传递函数" in chinese[20]["profile"]
    assert "状态空间" in chinese[24]["profile"]
    assert "注册非线性" in chinese[26]["profile"]


def test_prompt_documents_do_not_authorize_physical_hardware_actions():
    english = ENGLISH_PATH.read_text(encoding="utf-8")
    chinese = CHINESE_PATH.read_text(encoding="utf-8")

    assert english.count("not commands or permissions for a physical system") == 200
    assert chinese.count("不是对实体系统的命令或操作许可") == 200
    assert "do not authorize commands to physical hardware" in english
    assert "不授权对实体硬件下发命令" in chinese


def test_technical_corpus_has_four_required_fields_and_source_for_every_entry():
    markdown = TECHNICAL_PATH.read_text(encoding="utf-8")
    entries = re.split(r"^### \d+\. \[Ch\d+-\d+\] .+$", markdown, flags=re.MULTILINE)[
        1:
    ]

    assert len(entries) == len(_technical_ids())
    for index, entry in enumerate(entries, 1):
        assert "**来源定位：**" in entry, index
        assert re.findall(r"^#### (.+)$", entry, re.MULTILINE) == [
            "问题表述",
            "数学模型",
            "解决方法",
            "控制器与参数",
            "示例数据与理论计算",
        ], index
        example_match = re.search(
            r"^#### 示例数据与理论计算\s*$\n(.*)\Z",
            entry,
            re.MULTILINE | re.DOTALL,
        )
        assert example_match is not None, index
        example = example_match.group(1)
        assert "**示例数据：**" in example, index
        assert "**理论计算：**" in example, index
        assert "**八段核对：**" in example, index


def test_prompt_documents_describe_data_without_textbook_provenance_claims():
    assert "textbook" not in ENGLISH_PATH.read_text(encoding="utf-8").lower()
    assert "教材" not in CHINESE_PATH.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "chapter", range(1, 11), ids=lambda chapter: f"chapter-{chapter}"
)
def test_technical_corpus_has_reproducible_derivations_for_each_chapter(chapter):
    markdown = TECHNICAL_PATH.read_text(encoding="utf-8")
    matches = list(
        re.finditer(
            r"^### (\d+)\. \[Ch(\d+)-(\d+)\] .+$",
            markdown,
            flags=re.MULTILINE,
        )
    )
    chapter_entries = []
    for position, match in enumerate(matches):
        if int(match.group(2)) != chapter:
            continue
        end = (
            matches[position + 1].start()
            if position + 1 < len(matches)
            else len(markdown)
        )
        chapter_entries.append((int(match.group(1)), markdown[match.end() : end]))

    assert len(chapter_entries) == 20
    for global_id, entry in chapter_entries:
        model = re.search(
            r"^#### 数学模型\s*$\n(.*?)(?=^#### 解决方法\s*$)",
            entry,
            flags=re.MULTILINE | re.DOTALL,
        )
        method = re.search(
            r"^#### 解决方法\s*$\n(.*?)(?=^#### 控制器与参数\s*$)",
            entry,
            flags=re.MULTILINE | re.DOTALL,
        )
        assert model is not None, global_id
        assert method is not None, global_id
        model_text = model.group(1).strip()
        method_text = method.group(1).strip()

        for marker in ("**假设与变量：**", "**建模推导：**", "**模型结果：**"):
            assert marker in model_text, (global_id, marker)
        for marker in ("**求解目标：**", "**求解步骤：**", "**结果校核：**"):
            assert marker in method_text, (global_id, marker)

        assert len(re.findall(r"^\d+\. ", model_text, re.MULTILINE)) >= 3, global_id
        assert len(re.findall(r"^\d+\. ", method_text, re.MULTILINE)) >= 3, global_id
        assert len(re.sub(r"\s+", "", model_text)) >= 260, global_id
        assert len(re.sub(r"\s+", "", method_text)) >= 220, global_id
        assert len(re.findall(r"\\\(|\\\[", model_text)) >= 3, global_id
        assert not re.search(
            r"\b(?:TODO|TBD)\b|待补|待定", model_text + method_text, re.IGNORECASE
        ), global_id
