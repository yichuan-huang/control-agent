import re
from collections import Counter
from pathlib import Path
from typing import ClassVar

import pytest

from cfdc.diagnosis import start_diagnostic_session
from cfdc.diagnosis.measurements import description_excerpt_answers_field
from cfdc.models import SystemDescription

TECHNICAL_PATH = Path("dataset/control_problems.md")
ENGLISH_PATH = Path("dataset/control_problem_prompts.md")
CHINESE_PATH = Path("dataset/control_problem_prompts_cn.md")

ENGLISH_HEADINGS = [
    "Control Problem Description",
    "Profile Measurement Response (Natural Language)",
]
CHINESE_HEADINGS = [
    "控制问题描述",
    "Profile 测量回复（自然语言）",
]
SEVEN_FIELD_PROFILE_IDS = {*range(1, 22), 35, 38}
ENGLISH_PROFILE_LABELS = [
    "Known input change",
    "Final output change",
    "63% response time",
    "Input simulation lower bound",
    "Input simulation upper bound",
    "Output simulation lower bound",
    "Output simulation upper bound",
]
CHINESE_PROFILE_LABELS = [
    "已知输入变化量",
    "最终输出变化量",
    "63% 响应时间",
    "输入仿真下限",
    "输入仿真上限",
    "输出仿真下限",
    "输出仿真上限",
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


def _paragraphs(description: str) -> list[str]:
    return [item.strip() for item in re.split(r"\n\s*\n", description) if item.strip()]


class _DatasetDescriptionGuidanceAdapter:
    """Select the dedicated real paragraph for each checklist item."""

    _PARAGRAPH_BY_FIELD: ClassVar[dict[str, int]] = {
        "minimum_phase": 1,
        "significant_delay": 2,
        "relative_degree": 3,
        "open_loop_stability": 4,
        "nonlinearity_strength": 5,
        "controllability_observability": 6,
        "coupling_severity": 7,
        "uncertainty_magnitude": 8,
    }

    def __init__(self, language: str):
        self.language = language

    def guide_description(self, description, guidance):
        paragraphs = _paragraphs(description.text)
        resolved = []
        for item in guidance:
            paragraph_index = self._PARAGRAPH_BY_FIELD[item.diagnostic_field_id]
            candidate = paragraphs[paragraph_index]
            response = (
                candidate
                if description_excerpt_answers_field(
                    item.diagnostic_field_id,
                    candidate,
                    context=description.text,
                )
                else "unknown"
            )
            resolved.append({**item.model_dump(mode="json"), "response": response})
        return {
            "guidance": resolved,
            "observed_outputs": [],
            "actuators": [],
        }

    def phrase_measurement_plan(self, description, checklist, plan):
        del description, checklist
        return plan.model_dump(mode="json")


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
    assert "Existing-Record Diagnostic Measurement Response" not in markdown
    assert "已有记录诊断测量回复" not in markdown
    assert "open_loop_stability" not in markdown
    assert "binary_command" not in markdown
    assert not re.search(r"\b[A-Za-z][A-Za-z0-9_]*_unit\b", markdown)
    assert not any(token in markdown for token in ASSIGNMENT_TOKENS)

    old_headings = ENGLISH_OLD_HEADINGS if language == "en" else CHINESE_OLD_HEADINGS
    for old_heading in old_headings:
        assert f"### {old_heading}\n" not in markdown

    parsed = []
    for index, ((number, title), entry) in enumerate(zip(title_matches, entries), 1):
        assert int(number) == index
        assert re.findall(r"^### (.+)$", entry, re.MULTILINE) == headings, index

        description = _field(entry, headings[0])
        paragraphs = _paragraphs(description)
        assert len(paragraphs) == 9, (language, index, len(paragraphs))
        paragraph_sentences = [
            _sentences(paragraph, language) for paragraph in paragraphs
        ]
        assert all(2 <= len(items) <= 3 for items in paragraph_sentences), (
            language,
            index,
            [len(items) for items in paragraph_sentences],
        )
        sentences = [sentence for items in paragraph_sentences for sentence in items]
        assert "?" not in description and "？" not in description
        if language == "en":
            assert sentences[0].startswith(("This is ", "These are "))
            assert sentences[1].startswith(
                ("The control input is ", "The control inputs are ")
            )
        else:
            assert sentences[0].startswith("这是")
            assert sentences[1].startswith("控制输入是")

        profile = _field(entry, headings[1])
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
                "paragraphs": paragraphs,
                "sentences": sentences,
                "profile": profile,
            }
        )
    return parsed


@pytest.mark.parametrize(
    ("path", "headings", "language"),
    [
        (ENGLISH_PATH, ENGLISH_HEADINGS, "en"),
        (CHINESE_PATH, CHINESE_HEADINGS, "cn"),
    ],
)
def test_every_dataset_description_releases_all_eight_grounded_fields(
    path, headings, language
):
    entries = _parse_document(path, headings, language)
    adapter = _DatasetDescriptionGuidanceAdapter(language)

    for index, entry in enumerate(entries, 1):
        description = entry["description"]
        session = start_diagnostic_session(
            SystemDescription(text=description),
            diagnostic_adapter=adapter,
        )

        assert session.status == "description_grounded", (language, index)
        assert session.description_assessment is not None, (language, index)
        assert len(session.description_assessment.facts) == 8, (language, index)
        assert session.current_diagnosis.complete, (language, index)
        assert all(item.status == "inferred" for item in session.checklist), (
            language,
            index,
        )


@pytest.mark.parametrize(
    ("path", "headings", "language"),
    [
        (ENGLISH_PATH, ENGLISH_HEADINGS, "en"),
        (CHINESE_PATH, CHINESE_HEADINGS, "cn"),
    ],
)
def test_pole_zero_cancellation_description_preserves_inadequate_observability(
    path, headings, language
):
    entry = _parse_document(path, headings, language)[125]
    session = start_diagnostic_session(
        SystemDescription(text=entry["description"]),
        diagnostic_adapter=_DatasetDescriptionGuidanceAdapter(language),
    )

    assert session.status == "description_grounded"
    assert (
        session.current_diagnosis.controllability_observability.assessment
        == "inadequate"
    )


def test_english_prompts_match_the_guided_natural_language_ui_contract():
    markdown = ENGLISH_PATH.read_text(encoding="utf-8")
    entries = _parse_document(ENGLISH_PATH, ENGLISH_HEADINGS, "en")

    assert not HAN_PATTERN.search(markdown)
    assert len({item["description"] for item in entries}) == 200


def test_chinese_prompts_match_the_guided_natural_language_ui_contract():
    entries = _parse_document(CHINESE_PATH, CHINESE_HEADINGS, "cn")

    assert len({item["description"] for item in entries}) == 200
    assert all(HAN_PATTERN.search(item["description"]) for item in entries)


def test_bilingual_prompts_have_strict_two_stage_structural_parity():
    english = _parse_document(ENGLISH_PATH, ENGLISH_HEADINGS, "en")
    chinese = _parse_document(CHINESE_PATH, CHINESE_HEADINGS, "cn")

    assert len(english) == len(chinese) == 200
    for index, (english_item, chinese_item) in enumerate(zip(english, chinese), 1):
        assert len(english_item["paragraphs"]) == len(chinese_item["paragraphs"]), index


@pytest.mark.parametrize(
    ("path", "headings", "language", "labels", "extra_heading"),
    [
        (
            ENGLISH_PATH,
            ENGLISH_HEADINGS,
            "en",
            ENGLISH_PROFILE_LABELS,
            "Additional information:",
        ),
        (
            CHINESE_PATH,
            CHINESE_HEADINGS,
            "cn",
            CHINESE_PROFILE_LABELS,
            "额外信息：",
        ),
    ],
)
def test_every_profile_response_lists_its_required_answers_before_additional_information(
    path, headings, language, labels, extra_heading
):
    entries = _parse_document(path, headings, language)
    for index, entry in enumerate(entries, 1):
        profile = entry["profile"]
        if index in SEVEN_FIELD_PROFILE_IDS:
            markers = [
                f"**{label}：**" if language == "cn" else f"**{label}:**"
                for label in labels
            ]
            positions = [profile.index(marker) for marker in markers]
            assert positions == sorted(positions), (language, index)
            assert all(profile.count(marker) == 1 for marker in markers), (
                language,
                index,
            )
            for marker in markers:
                answer = re.search(
                    rf"^- {re.escape(marker)} (.+)$", profile, re.MULTILINE
                )
                assert answer is not None and re.search(r"\d", answer.group(1)), (
                    language,
                    index,
                    marker,
                )
            required_end = positions[-1]
        else:
            required_heading = (
                "Profile 专用必填回答："
                if language == "cn"
                else "Profile-specific required answers:"
            )
            parameters = (
                "**已声明的 Profile 参数：**"
                if language == "cn"
                else "**Declared Profile parameters:**"
            )
            model = (
                "**可执行软件模型：**"
                if language == "cn"
                else "**Executable software model:**"
            )
            for marker in (required_heading, parameters, model):
                assert profile.count(marker) == 1, (language, index, marker)
            assert not any(label in profile for label in labels), (language, index)
            required_end = profile.index(model)

        assert profile.count(extra_heading) == 1, (language, index)
        assert required_end < profile.index(extra_heading), (language, index)


def test_bilingual_descriptions_produce_the_same_eight_diagnostic_assessments():
    fields = tuple(_DatasetDescriptionGuidanceAdapter._PARAGRAPH_BY_FIELD)
    english = _parse_document(ENGLISH_PATH, ENGLISH_HEADINGS, "en")
    chinese = _parse_document(CHINESE_PATH, CHINESE_HEADINGS, "cn")
    english_adapter = _DatasetDescriptionGuidanceAdapter("en")
    chinese_adapter = _DatasetDescriptionGuidanceAdapter("cn")

    for index, (english_item, chinese_item) in enumerate(zip(english, chinese), 1):
        english_session = start_diagnostic_session(
            SystemDescription(text=english_item["description"]),
            diagnostic_adapter=english_adapter,
        )
        chinese_session = start_diagnostic_session(
            SystemDescription(text=chinese_item["description"]),
            diagnostic_adapter=chinese_adapter,
        )
        english_assessments = tuple(
            getattr(english_session.current_diagnosis, field).assessment
            for field in fields
        )
        chinese_assessments = tuple(
            getattr(chinese_session.current_diagnosis, field).assessment
            for field in fields
        )

        assert english_assessments == chinese_assessments, index


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
