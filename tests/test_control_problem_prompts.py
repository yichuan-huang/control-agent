import math
import re
from collections import Counter
from functools import cache
from pathlib import Path
from typing import ClassVar

import numpy as np
import pytest
from scipy import signal

from cfdc.diagnosis import start_diagnostic_session
from cfdc.diagnosis.engine import DiagnosticEngine
from cfdc.diagnosis.measurements import description_excerpt_answers_field
from cfdc.models import SystemDescription
from cfdc.specifications import (
    assess_specification_text,
    build_initial_specification_assessment,
    compile_specification_model,
    default_specification_template_catalog,
)
from cfdc.workflow import (
    default_simulation_profile_catalog,
    deterministic_profile_selection,
    validate_semantic_selection,
)

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
UNIVERSAL_ENGLISH_PROFILE_LABELS = [
    "Known input change",
    "Input simulation lower bound",
    "Input simulation upper bound",
    "Output simulation lower bound",
    "Output simulation upper bound",
]
UNIVERSAL_CHINESE_PROFILE_LABELS = [
    "已知输入变化量",
    "输入仿真下限",
    "输入仿真上限",
    "输出仿真下限",
    "输出仿真上限",
]
PROFILE_REQUIRED_ENGLISH_LABELS = {
    "first_order_lag": [
        "Final output change",
        "63% response time",
    ],
    "first_order_lag_with_delay": [
        "Final output change",
        "63% response time",
        "Pure waiting time",
    ],
    "second_order_oscillator": [
        "Oscillation period",
        "Successive peak ratio",
        "Corresponding motion change",
    ],
    "double_integrator": [
        "Corresponding acceleration change",
        "Typical motion time scale",
    ],
    "nmp_inverse_response": [
        "Final output change",
        "Initial inverse change",
        "Inverse recovery time",
        "63% response time",
    ],
    "generic_unstable_higher_order": ["Complete numeric model"],
    "underactuated_cartpole": [
        "Cart mass",
        "Pole mass",
        "Center-of-mass length",
        "Pole inertia",
        "Cart friction",
        "Gravity",
        "Force limit",
        "Cart travel limit",
    ],
    "vtol_cascaded": [
        "Vehicle mass",
        "Pitch inertia",
        "Gravity",
        "Linear drag",
        "Pitch damping",
        "Minimum thrust",
        "Maximum thrust",
        "Torque limit",
        "Typical response time",
        "Maximum tilt",
        "Maximum altitude error",
    ],
    "mimo_2x2_coupled": [
        "Local input-output gain matrix",
        "Local response time",
    ],
}
PROFILE_REQUIRED_CHINESE_LABELS = {
    "first_order_lag": ["最终输出变化量", "63% 响应时间"],
    "first_order_lag_with_delay": [
        "最终输出变化量",
        "63% 响应时间",
        "纯等待时间",
    ],
    "second_order_oscillator": [
        "相邻同向峰值间隔",
        "相邻峰值幅度比例",
        "对应运动变化",
    ],
    "double_integrator": ["对应加速度变化", "典型运动时间尺度"],
    "nmp_inverse_response": [
        "最终输出变化量",
        "初始反向变化",
        "反向恢复时间",
        "63% 响应时间",
    ],
    "generic_unstable_higher_order": ["完整数值模型"],
    "underactuated_cartpole": [
        "小车质量",
        "摆杆质量",
        "摆杆质心距离",
        "摆杆转动惯量",
        "小车摩擦",
        "重力加速度",
        "推力限制",
        "小车行程",
    ],
    "vtol_cascaded": [
        "飞行器质量",
        "俯仰转动惯量",
        "重力加速度",
        "平移阻力",
        "俯仰阻尼",
        "最小推力",
        "最大推力",
        "最大俯仰转矩",
        "典型响应时间",
        "最大安全倾角",
        "最大高度误差",
    ],
    "mimo_2x2_coupled": ["局部输入输出影响矩阵", "局部响应时间"],
}
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
NUMERIC_TOKEN = re.compile(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?")
EXPECTED_PROFILE_COUNTS = {
    "first_order_lag": 79,
    "first_order_lag_with_delay": 9,
    "second_order_oscillator": 1,
    "double_integrator": 55,
    "generic_unstable_higher_order": 47,
    "underactuated_cartpole": 1,
    "vtol_cascaded": 4,
    "mimo_2x2_coupled": 4,
}
SOURCE_MEASUREMENT_IDS = {*range(1, 22), 35, 38}


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


@cache
def _selected_profile_id(description_text: str, language: str) -> str:
    if language == "cn":
        # Use the English technical selection as the canonical locked Profile
        # assignment.  This keeps bilingual entries aligned when a translated
        # phrase is classified differently by the language-sensitive adapter.
        chinese_entries = _parse_document(CHINESE_PATH, CHINESE_HEADINGS, "cn")
        english_entries = _parse_document(ENGLISH_PATH, ENGLISH_HEADINGS, "en")
        for index, entry in enumerate(chinese_entries):
            if entry["description"] == description_text:
                return _selected_profile_id(english_entries[index]["description"], "en")

    description = SystemDescription(text=description_text)
    adapter = _DatasetDescriptionGuidanceAdapter(language)
    session = start_diagnostic_session(description, diagnostic_adapter=adapter)
    diagnosis = session.current_diagnosis
    classification = DiagnosticEngine().classify(diagnosis, description)
    selection = deterministic_profile_selection(
        description,
        diagnosis,
        classification,
        default_simulation_profile_catalog(),
    )
    return selection.simulation_profile_id


def _profile_required_labels(profile_id: str, language: str) -> list[str]:
    universal = (
        UNIVERSAL_CHINESE_PROFILE_LABELS
        if language == "cn"
        else UNIVERSAL_ENGLISH_PROFILE_LABELS
    )
    required = (
        PROFILE_REQUIRED_CHINESE_LABELS
        if language == "cn"
        else PROFILE_REQUIRED_ENGLISH_LABELS
    )
    profile_fields = required[profile_id]
    if profile_id == "first_order_lag":
        return [universal[0], *profile_fields, *universal[1:]]
    if profile_id == "first_order_lag_with_delay":
        return [universal[0], *profile_fields, *universal[1:]]
    if profile_id == "second_order_oscillator":
        return [
            profile_fields[0],
            profile_fields[1],
            universal[0],
            profile_fields[2],
            *universal[1:],
        ]
    if profile_id == "double_integrator":
        return [universal[0], *profile_fields, *universal[1:]]
    if profile_id == "nmp_inverse_response":
        return [universal[0], *profile_fields, *universal[1:]]
    return [*profile_fields, *universal]


@pytest.mark.parametrize(
    ("path", "headings", "language", "extra_heading"),
    [
        (
            ENGLISH_PATH,
            ENGLISH_HEADINGS,
            "en",
            "Additional information:",
        ),
        (
            CHINESE_PATH,
            CHINESE_HEADINGS,
            "cn",
            "额外信息：",
        ),
    ],
)
def test_every_profile_response_lists_its_required_answers_before_additional_information(
    path, headings, language, extra_heading
):
    entries = _parse_document(path, headings, language)
    for index, entry in enumerate(entries, 1):
        profile = entry["profile"]
        required_heading = (
            "Profile 专用必填回答："
            if language == "cn"
            else "Profile-specific required answers:"
        )
        assumption = (
            "以下数值优先采用原控制问题或现有软件模型中的数据"
            if language == "cn"
            else "The values below preserve source data where available"
        )
        assert profile.count(required_heading) == 1, (language, index)
        assert assumption in profile, (language, index)
        assert "已声明的 Profile 参数" not in profile
        assert "Declared Profile parameters" not in profile
        labels = _profile_required_labels(
            _selected_profile_id(entry["description"], language), language
        )
        markers = [
            f"**{label}：**" if language == "cn" else f"**{label}:**"
            for label in labels
        ]
        positions = [profile.index(marker) for marker in markers]
        assert positions == sorted(positions), (language, index)
        for marker in markers:
            assert profile.count(marker) == 1, (language, index, marker)
            answer = re.search(rf"^- {re.escape(marker)} (.+)$", profile, re.MULTILINE)
            assert answer is not None and re.search(r"\d", answer.group(1)), (
                language,
                index,
                marker,
            )
        required_end = positions[-1]
        supplemental_heading = (
            "补充仿真测量："
            if language == "cn"
            else "Supplemental simulation measurements:"
        )
        assert profile.count(supplemental_heading) == 1, (language, index)
        assert profile.count(extra_heading) == 1, (language, index)
        assert required_end < profile.index(extra_heading), (language, index)


def _profile_answers(entry: dict, language: str) -> tuple[str, dict[str, str]]:
    profile_id = _selected_profile_id(entry["description"], language)
    labels = _profile_required_labels(profile_id, language)
    answers = {}
    for label in labels:
        colon = "：" if language == "cn" else ":"
        marker = f"**{label}{colon}**"
        match = re.search(
            rf"^- {re.escape(marker)} (.+)$", entry["profile"], re.MULTILINE
        )
        assert match is not None, (language, label)
        answers[label] = match.group(1)
    return profile_id, answers


def _numbers(text: str) -> list[float]:
    return [float(token) for token in NUMERIC_TOKEN.findall(text)]


def _time_numbers(text: str) -> list[float]:
    return [
        float(token)
        for token in re.findall(
            rf"({NUMERIC_TOKEN.pattern})\s*(?:s|秒)", text, re.IGNORECASE
        )
    ]


def test_profile_distribution_is_locked_and_every_numeric_answer_is_finite():
    time_labels = {
        "63% response time",
        "Pure waiting time",
        "Oscillation period",
        "Typical motion time scale",
        "Inverse recovery time",
        "Local response time",
        "63% 响应时间",
        "纯等待时间",
        "相邻同向峰值间隔",
        "典型运动时间尺度",
        "反向恢复时间",
        "局部响应时间",
        "典型响应时间",
    }
    for path, headings, language in (
        (ENGLISH_PATH, ENGLISH_HEADINGS, "en"),
        (CHINESE_PATH, CHINESE_HEADINGS, "cn"),
    ):
        entries = _parse_document(path, headings, language)
        distribution = Counter(
            _selected_profile_id(entry["description"], language) for entry in entries
        )
        assert distribution == EXPECTED_PROFILE_COUNTS, language
        for index, entry in enumerate(entries, 1):
            profile_id, answers = _profile_answers(entry, language)
            for label, answer in answers.items():
                values = _numbers(answer)
                assert values and all(math.isfinite(value) for value in values), (
                    language,
                    index,
                    label,
                    answer,
                )
                assert re.search(
                    r"(?:[A-Za-z]{1,}|%|单位|无量纲|档位|矩阵|模型|系数)", answer
                ), (language, index, label, answer)

            input_min = _numbers(
                answers[
                    "输入仿真下限"
                    if language == "cn"
                    else "Input simulation lower bound"
                ]
            )[0]
            input_max = _numbers(
                answers[
                    "输入仿真上限"
                    if language == "cn"
                    else "Input simulation upper bound"
                ]
            )[0]
            output_min = _numbers(
                answers[
                    "输出仿真下限"
                    if language == "cn"
                    else "Output simulation lower bound"
                ]
            )[0]
            output_max = _numbers(
                answers[
                    "输出仿真上限"
                    if language == "cn"
                    else "Output simulation upper bound"
                ]
            )[0]
            assert input_min < input_max, (language, index)
            assert output_min < output_max, (language, index)

            for label, answer in answers.items():
                if label in time_labels:
                    values = _time_numbers(answer)
                    assert values and all(value > 0 for value in values), (
                        language,
                        index,
                        label,
                        answer,
                    )

            if profile_id == "second_order_oscillator":
                ratio_label = (
                    "相邻峰值幅度比例" if language == "cn" else "Successive peak ratio"
                )
                ratio = _numbers(answers[ratio_label])[0]
                assert 0 < ratio < 1, (language, index, ratio)
            if profile_id == "mimo_2x2_coupled":
                matrix_label = (
                    "局部输入输出影响矩阵"
                    if language == "cn"
                    else "Local input-output gain matrix"
                )
                matrix_match = re.search(
                    r"\[\[([^\]]+)\],\s*\[([^\]]+)\]\]", answers[matrix_label]
                )
                assert matrix_match is not None, (language, index)
                rows = [_numbers(row) for row in matrix_match.groups()]
                assert len(rows) == 2 and all(len(row) == 2 for row in rows)
                assert all(math.isfinite(value) for row in rows for value in row)
            if profile_id == "generic_unstable_higher_order":
                model_label = (
                    "完整数值模型" if language == "cn" else "Complete numeric model"
                )
                assert re.search(
                    r"(?:numerator coefficients|matrix [ABCD]|registered nonlinear|分子系数|[ABCD]\s*(?:matrix|矩阵)|注册非线性)",
                    answers[model_label],
                    re.IGNORECASE,
                ), (language, index, answers[model_label])


def test_bilingual_profile_required_numbers_and_profile_headings_match():
    english = _parse_document(ENGLISH_PATH, ENGLISH_HEADINGS, "en")
    chinese = _parse_document(CHINESE_PATH, CHINESE_HEADINGS, "cn")
    assert len(english) == len(chinese) == 200
    for index, (english_entry, chinese_entry) in enumerate(zip(english, chinese), 1):
        english_profile, english_answers = _profile_answers(english_entry, "en")
        chinese_profile, chinese_answers = _profile_answers(chinese_entry, "cn")
        assert english_profile == chinese_profile, index
        english_labels = _profile_required_labels(english_profile, "en")
        chinese_labels = _profile_required_labels(chinese_profile, "cn")
        english_values = [
            value
            for label in english_labels
            for value in _numbers(english_answers[label])
        ]
        chinese_values = [
            value
            for label in chinese_labels
            for value in _numbers(chinese_answers[label])
        ]
        assert english_values == chinese_values, index


def test_profile_selection_reaches_the_expected_candidate_model_stage():
    english = _parse_document(ENGLISH_PATH, ENGLISH_HEADINGS, "en")
    representatives: dict[str, dict] = {}
    for entry in english:
        profile_id = _selected_profile_id(entry["description"], "en")
        representatives.setdefault(profile_id, entry)
    assert set(representatives) == set(EXPECTED_PROFILE_COUNTS)

    catalog = default_simulation_profile_catalog()
    adapter = _DatasetDescriptionGuidanceAdapter("en")
    for profile_id, entry in representatives.items():
        description = SystemDescription(text=entry["description"])
        session = start_diagnostic_session(description, diagnostic_adapter=adapter)
        classification = DiagnosticEngine().classify(
            session.current_diagnosis, description
        )
        selection = deterministic_profile_selection(
            description,
            session.current_diagnosis,
            classification,
            catalog,
        )
        assert selection.simulation_profile_id == profile_id
        selected_profile = validate_semantic_selection(
            selection, classification, catalog
        )
        assert selected_profile.required_feature_ids
        profile = entry["profile"]
        if profile_id == "generic_unstable_higher_order":
            assert "**Complete numeric model:**" in profile
        else:
            assert "Profile-specific required answers:" in profile


def test_every_compilable_chinese_profile_response_reaches_a_candidate_model():
    """Exercise the actual specification parser/compiler, not only label presence."""
    entries = _parse_document(CHINESE_PATH, CHINESE_HEADINGS, "cn")
    templates = {
        template.method_profile_id: template
        for template in default_specification_template_catalog().templates
    }
    compiled_counts = Counter()

    for index, entry in enumerate(entries, 1):
        profile_id = _selected_profile_id(entry["description"], "cn")
        if profile_id == "generic_unstable_higher_order":
            # This route deliberately hands its complete numeric plant model to
            # the higher-order workflow instead of compiling a scalar proxy.
            _assert_complete_numeric_model_handoff(entry, "cn", index)
            continue

        description = SystemDescription(text=entry["description"])
        template = templates[profile_id]
        previous = build_initial_specification_assessment(description, template)
        assessment = assess_specification_text(
            description,
            template,
            entry["profile"],
            previous=previous,
            method_profile_id=profile_id,
        )

        assert assessment.status == "ready", (
            index,
            profile_id,
            assessment.missing_fact_ids,
            assessment.rejected_facts,
            assessment.conflicts,
        )
        compiled = compile_specification_model(
            description=description,
            template=template,
            assessment=assessment,
        )
        assert compiled.template_id == template.template_id, (index, profile_id)
        compiled_counts[profile_id] += 1

    expected_compilable = Counter(EXPECTED_PROFILE_COUNTS)
    del expected_compilable["generic_unstable_higher_order"]
    assert compiled_counts == expected_compilable


def _transfer_function_coefficients(
    profile: str,
) -> tuple[np.ndarray, np.ndarray] | None:
    match = re.search(
        r"numerator coefficients are ([^;]+); its denominator coefficients are ([^;]+);",
        profile,
    )
    if match is None:
        return None
    try:
        numerator = np.array(
            [float(item.strip()) for item in match.group(1).split(",")]
        )
        denominator = np.array(
            [float(item.strip()) for item in match.group(2).split(",")]
        )
    except ValueError:
        return None
    return numerator, denominator


def _assert_complete_numeric_model_handoff(entry: dict, language: str, index: int):
    _profile_id, answers = _profile_answers(entry, language)
    label = "完整数值模型" if language == "cn" else "Complete numeric model"
    model = answers[label]
    values = _numbers(model)
    assert values and all(math.isfinite(value) for value in values), index

    if "transfer function" in model or "传递函数" in model:
        coefficient_patterns = (
            (
                r"numerator coefficients are ([^;]+)",
                r"denominator coefficients are ([^;]+)",
            ),
            (r"分子系数为([^；]+)", r"分母系数为([^；]+)"),
        )
        for numerator_pattern, denominator_pattern in coefficient_patterns:
            numerator = re.search(numerator_pattern, model)
            denominator = re.search(denominator_pattern, model)
            if numerator is not None and denominator is not None:
                numerator_values = _numbers(numerator.group(1))
                denominator_values = _numbers(denominator.group(1))
                assert numerator_values and denominator_values, index
                assert any(value != 0 for value in denominator_values), index
                return
        pytest.fail(f"entry {index} has no parseable transfer-function handoff")

    assert "state-space" in model or "状态空间" in model, index
    matrix_markers = (
        ("matrix A", "matrix B", "matrix C", "matrix D")
        if language == "en"
        else ("A 矩阵", "B 矩阵", "C 矩阵", "D 矩阵")
    )
    assert all(marker in model for marker in matrix_markers), index
    assert model.count("[") >= 4, index


def test_first_order_measurements_match_source_models_or_explicit_proxies():
    english = _parse_document(ENGLISH_PATH, ENGLISH_HEADINGS, "en")
    chinese = _parse_document(CHINESE_PATH, CHINESE_HEADINGS, "cn")

    for index, (entry, chinese_entry) in enumerate(zip(english, chinese), 1):
        profile_id, answers = _profile_answers(entry, "en")
        if profile_id not in {"first_order_lag", "first_order_lag_with_delay"}:
            continue

        coefficients = _transfer_function_coefficients(entry["profile"])
        record = re.search(
            r"uses a ([0-9.eE+-]+) s sample interval for ([0-9.eE+-]+) s,"
            r" starts the primary output at ([0-9.eE+-]+),",
            entry["profile"],
        )
        stable_model = False
        if coefficients is not None and record is not None:
            numerator, denominator = coefficients
            if len(denominator) >= 2 and 0 < len(numerator) <= len(denominator):
                poles = np.roots(denominator)
                dc_gain = (
                    numerator[-1] / denominator[-1]
                    if abs(denominator[-1]) > 1e-12
                    else math.nan
                )
                stable_model = (
                    bool(np.all(np.real(poles) < -1e-9))
                    and math.isfinite(dc_gain)
                    and abs(dc_gain) > 1e-12
                )

        if stable_model and index not in SOURCE_MEASUREMENT_IDS:
            dt, duration, initial_output = map(float, record.groups())
            input_change = _numbers(answers["Known input change"])[0]
            input_min = _numbers(answers["Input simulation lower bound"])[0]
            input_max = _numbers(answers["Input simulation upper bound"])[0]
            point_count = max(
                1001,
                min(100001, int(duration / max(dt, 1e-9)) + 1),
            )
            times = np.linspace(0.0, duration, point_count)
            _, unit_step = signal.step((numerator, denominator), T=times)
            expected_final = float(dc_gain * input_change)
            target = 0.6321205588 * expected_final
            response = unit_step * input_change
            crossings = (
                np.flatnonzero(response >= target)
                if expected_final > 0
                else np.flatnonzero(response <= target)
            )
            expected_time = (
                max(dt, float(times[crossings[0]]))
                if len(crossings)
                else max(20 * dt, duration / 8)
            )
            amplitudes = (
                -abs(input_min),
                -0.5 * abs(input_min),
                0.5 * abs(input_max),
                abs(input_max),
            )
            trajectories = [
                initial_output + multiplier * amplitude * unit_step
                for multiplier in (0.9, 1.0, 1.1)
                for amplitude in amplitudes
            ]
            raw_min = min(float(np.min(values)) for values in trajectories)
            raw_max = max(float(np.max(values)) for values in trajectories)
            span = raw_max - raw_min
            expected_min = raw_min - 0.1 * span
            expected_max = raw_max + 0.1 * span

            assert "model-derived" in answers["Final output change"], index
            assert _numbers(answers["Final output change"])[0] == pytest.approx(
                expected_final, rel=2e-5, abs=1e-8
            )
            assert _time_numbers(answers["63% response time"])[0] == pytest.approx(
                expected_time, rel=2e-5, abs=1e-8
            )
            assert _numbers(answers["Output simulation lower bound"])[
                0
            ] == pytest.approx(expected_min, rel=2e-5, abs=1e-8)
            assert _numbers(answers["Output simulation upper bound"])[
                0
            ] == pytest.approx(expected_max, rel=2e-5, abs=1e-8)
            continue

        if index in SOURCE_MEASUREMENT_IDS:
            continue

        english_proxy = re.search(
            r"\*\*Executable first-order Profile proxy:\*\* (.*?)(?=\n\n)",
            entry["profile"],
            re.DOTALL,
        )
        chinese_proxy = re.search(
            r"\*\*可执行一阶 Profile 代理模型:\*\* (.*?)(?=\n\n)",
            chinese_entry["profile"],
            re.DOTALL,
        )
        assert english_proxy is not None and chinese_proxy is not None, index
        proxy_values = _numbers(english_proxy.group(1))
        assert proxy_values == _numbers(chinese_proxy.group(1)), index
        input_change = _numbers(answers["Known input change"])[0]
        final_change = _numbers(answers["Final output change"])[0]
        response_time = _time_numbers(answers["63% response time"])[0]
        delay = (
            _time_numbers(answers["Pure waiting time"])[0]
            if profile_id == "first_order_lag_with_delay"
            else 0.0
        )
        assert final_change != 0, index
        assert proxy_values[:4] == pytest.approx(
            [final_change / input_change, response_time, 1.0, delay]
        )

        assert record is not None, index
        dt, duration, initial_output = map(float, record.groups())
        times = np.linspace(
            0.0,
            duration,
            max(1001, min(100001, int(duration / max(dt, 1e-9)) + 1)),
        )
        elapsed = np.maximum(times - delay, 0.0)
        unit_step = (final_change / input_change) * (
            1.0 - np.exp(-elapsed / response_time)
        )
        input_min = _numbers(answers["Input simulation lower bound"])[0]
        input_max = _numbers(answers["Input simulation upper bound"])[0]
        amplitudes = (
            -abs(input_min),
            -0.5 * abs(input_min),
            0.5 * abs(input_max),
            abs(input_max),
        )
        trajectories = [
            initial_output + multiplier * amplitude * unit_step
            for multiplier in (0.9, 1.0, 1.1)
            for amplitude in amplitudes
        ]
        raw_min = min(float(np.min(values)) for values in trajectories)
        raw_max = max(float(np.max(values)) for values in trajectories)
        span = raw_max - raw_min
        expected_min = raw_min - 0.1 * span
        expected_max = raw_max + 0.1 * span
        assert _numbers(answers["Output simulation lower bound"])[0] == pytest.approx(
            expected_min, rel=2e-5, abs=1e-8
        )
        assert _numbers(answers["Output simulation upper bound"])[0] == pytest.approx(
            expected_max, rel=2e-5, abs=1e-8
        )


def test_second_order_motion_answer_is_an_acceleration_measurement():
    english = _parse_document(ENGLISH_PATH, ENGLISH_HEADINGS, "en")
    chinese = _parse_document(CHINESE_PATH, CHINESE_HEADINGS, "cn")

    for entry, language in ((english[76], "en"), (chinese[76], "cn")):
        _profile_id, answers = _profile_answers(entry, language)
        label = "对应运动变化" if language == "cn" else "Corresponding motion change"
        assert "acceleration" in answers[label] or "加速度" in answers[label]
        assert "/s^2" in answers[label]


def test_declared_profile_parameter_shortcut_is_removed_everywhere():
    for path in (ENGLISH_PATH, CHINESE_PATH):
        text = path.read_text(encoding="utf-8")
        assert text.count("Declared Profile parameters") == 0
        assert text.count("已声明的 Profile 参数") == 0
        if path == ENGLISH_PATH:
            assert text.count("Profile-specific required answers:") == 200
        else:
            assert text.count("Profile 专用必填回答：") == 200


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
