from pathlib import Path
from collections import Counter
import math
import re

import pytest


TECHNICAL_PATH = Path("dataset/control_problems.md")
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
ENGLISH_DIAGNOSTIC_LABELS = [
    "Open-loop stability:",
    "Phase behavior:",
    "Delay significance:",
    "Dynamic order:",
    "Sensing and actuation:",
    "Nonlinearity:",
    "Coupling:",
    "Uncertainty:",
]
CHINESE_DIAGNOSTIC_LABELS = [
    "开环稳定性：",
    "相位特性：",
    "迟延显著性：",
    "动态阶次：",
    "测量与执行：",
    "非线性：",
    "耦合关系：",
    "不确定性：",
]
ENGLISH_DIAGNOSTIC_DECLARATIONS = [
    "open-loop assessment",
    "phase assessment",
    "delay assessment",
    "relative degree is",
    "controllability and observability are",
    "the nonlinearity is therefore",
    "coupling is therefore",
    "model uncertainty is therefore",
]
CHINESE_DIAGNOSTIC_DECLARATIONS = [
    "开环判断",
    "相位判断",
    "迟延判断",
    "相对阶次为",
    "能控性和能观性",
    "非线性为",
    "耦合为",
    "模型不确定性为",
]
ENGLISH_ASSESSMENT_PATTERNS = [
    [
        ("stable", re.compile(r"settles or remains bounded")),
        ("marginal", re.compile(r"retain an offset or drift")),
        ("unstable", re.compile(r"continues to grow rather than return")),
    ],
    [
        ("minimum-phase", re.compile(r"follows its eventual direction and does not move the opposite way first")),
        ("non-minimum-phase", re.compile(r"moves in an unfavorable or opposite direction before turning")),
    ],
    [
        ("significant", re.compile(r"a visible pause separates the command")),
        ("not significant", re.compile(r"begins promptly without a separate silent interval")),
    ],
    [
        ("low", re.compile(r"no more than two dominant storage or integration stages")),
        ("high", re.compile(r"three or more successive storage or integration stages")),
    ],
    [
        ("adequate", re.compile(r"every relevant motion mode appear")),
        ("inadequate", re.compile(r"one pole-zero-canceled mode absent from the recordings and unreachable")),
    ],
    [
        ("weak", re.compile(r"small positive and negative trials remain smooth, reversible, and nearly proportional")),
        ("static-compensable", re.compile(r"departure from proportional behavior stays in this fixed input-output rule")),
        ("strong dynamic", re.compile(r"response law changes with the evolving state")),
    ],
    [
        ("single-input single-output", re.compile(r"one principal action-to-recording path")),
        ("weak multivariable", re.compile(r"several recordings share internal motion")),
        ("severe multivariable", re.compile(r"changing any one of several actuators")),
        ("underactuated", re.compile(r"fewer independent actuators than regulated coordinates")),
        ("cascaded", re.compile(r"outer response appears only through")),
    ],
    [
        ("small", re.compile(r"motion direction, response timing, and final level remain almost unchanged")),
        ("moderate", re.compile(r"shift the response rate and final level modestly")),
        ("large", re.compile(r"can materially (?:alter|change)")),
    ],
]
CHINESE_ASSESSMENT_PATTERNS = [
    [
        ("稳定", re.compile(r"会收敛或保持有界")),
        ("临界稳定", re.compile(r"保持偏差或继续漂移")),
        ("不稳定", re.compile(r"偏差会继续增大而不会自行返回")),
    ],
    [
        ("最小相位", re.compile(r"首次有效变化与最终方向一致，不会先向相反方向运动")),
        ("非最小相位", re.compile(r"首次有效变化会先沿不利或相反方向运动")),
    ],
    [
        ("显著", re.compile(r"命令与首次记录响应之间存在可见停顿")),
        ("不显著", re.compile(r"首次记录变化会及时开始，不会出现独立静默区间")),
    ],
    [
        ("低", re.compile(r"至多经过两个主导储能或积分环节")),
        ("高", re.compile(r"至少经过三个连续储能或积分环节")),
    ],
    [
        ("充分", re.compile(r"每个相关运动模态至少出现在一项记录中")),
        ("不充分", re.compile(r"一个极零相消模态不出现在记录中，也无法由给定激励到达")),
    ],
    [
        ("弱", re.compile(r"小幅正向和反向试验保持平滑、可逆且近似成比例")),
        ("静态可补偿", re.compile(r"偏离比例关系的现象只存在于这一固定输入输出规律中")),
        ("强动态", re.compile(r"响应规律会随状态演化")),
    ],
    [
        ("单输入单输出", re.compile(r"一条主要动作到记录量的通道")),
        ("弱多变量", re.compile(r"多个记录量共享内部运动")),
        ("强多变量", re.compile(r"改变任一执行器都会明显带动多个记录量")),
        ("欠驱动", re.compile(r"独立执行器少于受控坐标")),
        ("串级", re.compile(r"外层响应只能通过单独稳定的内层")),
    ],
    [
        ("小", re.compile(r"运动方向、响应时机和最终水平几乎不变")),
        ("中等", re.compile(r"只会适度改变响应速度和最终水平")),
        ("大", re.compile(r"都可能明显改变")),
    ],
]
ASSESSMENT_TRANSLATION = {
    "稳定": "stable",
    "临界稳定": "marginal",
    "不稳定": "unstable",
    "最小相位": "minimum-phase",
    "非最小相位": "non-minimum-phase",
    "显著": "significant",
    "不显著": "not significant",
    "低": "low",
    "高": "high",
    "充分": "adequate",
    "不充分": "inadequate",
    "弱": "weak",
    "静态可补偿": "static-compensable",
    "强动态": "strong dynamic",
    "单输入单输出": "single-input single-output",
    "弱多变量": "weak multivariable",
    "强多变量": "severe multivariable",
    "欠驱动": "underactuated",
    "串级": "cascaded",
    "小": "small",
    "中等": "moderate",
    "大": "large",
}


def _technical_ids() -> list[int]:
    markdown = TECHNICAL_PATH.read_text(encoding="utf-8")
    matches = re.findall(
        r"^### (\d+)\. \[Ch(\d+)-(\d+)\] ", markdown, re.MULTILINE
    )
    ids = [int(global_id) for global_id, _chapter, _local_id in matches]
    chapter_counts = Counter(int(chapter) for _global_id, chapter, _local_id in matches)

    assert ids == list(range(1, 201))
    assert chapter_counts == Counter({chapter: 20 for chapter in range(1, 11)})
    for chapter in range(1, 11):
        local_ids = [
            int(local_id)
            for _global_id, item_chapter, local_id in matches
            if int(item_chapter) == chapter
        ]
        assert local_ids == list(range(1, 21))
    return ids


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
    expected_ids = _technical_ids()

    assert len(title_matches) == len(entries) == len(expected_ids)
    assert [int(number) for number, _ in title_matches] == expected_ids
    assert "~~~json" not in markdown

    parsed = []
    for index, ((number, title), entry) in enumerate(zip(title_matches, entries), 1):
        assert int(number) == index
        assert re.findall(r"^### (.+)$", entry, re.MULTILINE) == headings, index

        description = _field(entry, headings[0])
        paragraphs = [part.strip() for part in description.split("\n\n") if part.strip()]
        forbidden_labels = ENGLISH_DIAGNOSTIC_LABELS if language == "en" else CHINESE_DIAGNOSTIC_LABELS
        forbidden_declarations = ENGLISH_DIAGNOSTIC_DECLARATIONS if language == "en" else CHINESE_DIAGNOSTIC_DECLARATIONS
        assert len(paragraphs) == 1, (language, index, len(paragraphs))
        assert all(label not in description for label in forbidden_labels), (language, index)
        assert all(phrase not in description for phrase in forbidden_declarations), (language, index)
        if language == "en":
            sentences = re.split(r"(?<=[.!?])\s+", description)
        else:
            sentences = re.findall(r"[^。！？]+[。！？]", description)
        assert len(sentences) == 8, (language, index, len(sentences))
        assert not MATH_NOTATION_PATTERN.search(description), (language, index)
        assert "unknown" not in description.lower(), (language, index)
        assert "not enough information" not in description.lower(), (language, index)
        assert "?" not in description and "？" not in description, (language, index)

        patterns = ENGLISH_ASSESSMENT_PATTERNS if language == "en" else CHINESE_ASSESSMENT_PATTERNS
        assessments = []
        for sentence, choices in zip(sentences, patterns):
            matches = [assessment for assessment, pattern in choices if pattern.search(sentence)]
            assert len(matches) == 1, (language, index, sentence, matches)
            assessments.append(matches[0])

        outputs = _field(entry, headings[1])
        actuators = _field(entry, headings[2])
        actions = [line.strip() for line in _field(entry, headings[4]).splitlines() if line.strip()]
        time_scale = float(_field(entry, headings[5]))
        assert outputs and actuators and actions and time_scale > 0.0

        parsed.append(
            {
                "title": title,
                "description": description,
                "paragraphs": sentences,
                "assessments": assessments,
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

    assert len(english) == len(chinese) == len(_technical_ids())
    for index, (english_item, chinese_item) in enumerate(zip(english, chinese), 1):
        assert english_item["bounds"] == chinese_item["bounds"], index
        assert english_item["time_scale"] == chinese_item["time_scale"], index
        assert len(english_item["actions"]) == len(chinese_item["actions"]), index
        translated = [ASSESSMENT_TRANSLATION[value] for value in chinese_item["assessments"]]
        assert english_item["assessments"] == translated, index


def test_descriptions_are_problem_specific_instead_of_repeated_boilerplate():
    english = _parse_document(ENGLISH_PATH, ENGLISH_HEADINGS, "en")
    chinese = _parse_document(CHINESE_PATH, CHINESE_HEADINGS, "cn")

    assert len({item["description"] for item in english}) == 200
    assert len({item["description"] for item in chinese}) == 200
    for field_index in range(8):
        assert len({item["paragraphs"][field_index] for item in english}) >= 180
        assert len({item["paragraphs"][field_index] for item in chinese}) >= 180

    stale_boilerplate = [
        "is assessed explicitly",
        "follows the sign convention declared in the model",
        "contains the storage and integration stages stated in the technical model",
        "对象系数测量负载和执行器效率都作为不确定因素处理",
    ]
    joined = "\n".join([item["description"] for item in english + chinese])
    assert all(phrase not in joined for phrase in stale_boilerplate)
    assert english[125]["assessments"][4] == "inadequate"
    assert chinese[125]["assessments"][4] == "不充分"
    assert all(item["assessments"][4] == "adequate" for item in english[:125] + english[126:])

    expected_profiles = {
        62: ["unstable", "minimum-phase", "not significant", "low", "adequate", "weak", "single-input single-output", "small"],
        126: ["stable", "minimum-phase", "not significant", "low", "inadequate", "weak", "single-input single-output", "small"],
        161: ["unstable", "minimum-phase", "not significant", "low", "adequate", "strong dynamic", "single-input single-output", "moderate"],
        166: ["marginal", "minimum-phase", "not significant", "low", "adequate", "static-compensable", "single-input single-output", "small"],
        167: ["marginal", "minimum-phase", "not significant", "high", "adequate", "static-compensable", "single-input single-output", "small"],
        185: ["stable", "minimum-phase", "not significant", "low", "adequate", "weak", "severe multivariable", "large"],
        192: ["marginal", "minimum-phase", "not significant", "high", "adequate", "weak", "severe multivariable", "large"],
    }
    for problem_id, profile in expected_profiles.items():
        assert english[problem_id - 1]["assessments"] == profile


def test_descriptions_state_the_physical_situation_without_names_or_source_meta_commentary():
    english = _parse_document(ENGLISH_PATH, ENGLISH_HEADINGS, "en")
    chinese = _parse_document(CHINESE_PATH, CHINESE_HEADINGS, "cn")

    forbidden_english = [
        "source problem",
        "source method",
        "source includes",
        "source configuration",
        "untreated source",
        "original problem",
        "textbook",
        "The “",
        "In the “",
        "For “",
    ]
    forbidden_chinese = [
        "原题",
        "教材",
        "算例把",
        "未处理工况",
        "在“",
        "对于“",
    ]

    for item in english:
        assert item["title"] not in item["description"]
        assert all(phrase not in item["description"] for phrase in forbidden_english)
    for item in chinese:
        assert item["title"] not in item["description"]
        assert all(phrase not in item["description"] for phrase in forbidden_chinese)


def test_safety_bounds_and_forbidden_actions_are_risk_aware():
    english = _parse_document(ENGLISH_PATH, ENGLISH_HEADINGS, "en")
    chinese = _parse_document(CHINESE_PATH, CHINESE_HEADINGS, "cn")

    assert len({tuple(item["bounds"].items()) for item in english}) >= 4
    assert len({tuple(item["actions"]) for item in english}) >= 5
    for index, (english_item, chinese_item) in enumerate(zip(english, chinese), 1):
        bounds = english_item["bounds"]
        assert 0.0 < bounds["max_abs_reference_normalized"] <= 0.5, index
        assert 0.0 < bounds["max_abs_output_normalized"] <= 2.0, index
        assert 0.0 < bounds["max_abs_actuator_normalized"] <= 1.5, index
        assert len(english_item["actions"]) == len(chinese_item["actions"]) == 4, index
        high_risk = (
            english_item["assessments"][0] in {"marginal", "unstable"}
            or english_item["assessments"][5] in {"static-compensable", "strong dynamic"}
            or english_item["assessments"][6]
            in {"severe multivariable", "underactuated", "cascaded"}
        )
        if high_risk:
            assert bounds["max_abs_reference_normalized"] <= 0.25, index
            assert bounds["max_abs_actuator_normalized"] <= 1.0, index


def test_reviewed_observable_outputs_and_actuators_are_physical_or_declared_test_signals():
    english = _parse_document(ENGLISH_PATH, ENGLISH_HEADINGS, "en")
    chinese = _parse_document(CHINESE_PATH, CHINESE_HEADINGS, "cn")
    expected = {
        22: (("body displacement, wheel displacement, and suspension travel", "prescribed road-displacement test input"), ("车身位移、车轮位移与悬架行程", "给定路面位移测试输入")),
        60: (("regulated output response across the tested settings", "bounded controller command during proportional and integral setting sweeps"), ("不同设定下的受控输出响应", "比例与积分设定扫描中的有界控制命令")),
        62: (("pendulum angle and compensator output", "bounded dynamic-compensator command"), ("摆角与补偿器输出", "有界动态补偿器命令")),
        87: (("remote attitude and flexible deflection", "main-body torque"), ("远端姿态与柔性挠度", "主刚体力矩")),
        91: (("nominal output and flexible displacement", "notch-filtered actuator command"), ("标称输出与柔性位移", "陷波滤波后的执行器命令")),
        97: (("horizontal position, pitch attitude, and angular rate", "outer position command and inner rotor-torque command"), ("水平位置、俯仰姿态与角速度", "外层位置命令与内层旋翼力矩命令")),
        110: (("closed-loop output and open-loop frequency response", "bounded sinusoidal loop excitation"), ("闭环输出与开环频率响应", "有界正弦环路激励")),
        126: (("state trajectories and declared output response", "bounded state-space test excitation"), ("状态轨迹与指定输出响应", "有界状态空间测试激励")),
        167: (("regulated output, loop error, and saturated control signal", "saturated proportional command"), ("受控输出、环路误差与饱和控制信号", "饱和比例命令")),
        175: (("position and velocity", "bounded acceleration command"), ("位置与速度", "有界加速度命令")),
        185: (("aircraft rates, attitude, speed, altitude", "rudder, elevator, aileron, thrust"), ("飞机角速度、姿态、速度、高度", "方向舵、升降舵、副翼、推力")),
        192: (("position, attitude, angular rates, altitude", "four rotor thrust commands"), ("位置、姿态、角速度、高度", "四个旋翼推力命令")),
    }
    for problem_id, ((outputs_en, actuators_en), (outputs_cn, actuators_cn)) in expected.items():
        assert (english[problem_id - 1]["outputs"], english[problem_id - 1]["actuators"]) == (outputs_en, actuators_en)
        assert (chinese[problem_id - 1]["outputs"], chinese[problem_id - 1]["actuators"]) == (outputs_cn, actuators_cn)


def test_technical_corpus_has_four_required_fields_and_source_for_every_entry():
    markdown = TECHNICAL_PATH.read_text(encoding="utf-8")
    entries = re.split(
        r"^### \d+\. \[Ch\d+-\d+\] .+$", markdown, flags=re.MULTILINE
    )[1:]

    assert len(entries) == len(_technical_ids())
    for index, entry in enumerate(entries, 1):
        assert "**来源定位：**" in entry, index
        assert re.findall(r"^#### (.+)$", entry, re.MULTILINE) == [
            "问题表述",
            "数学模型",
            "解决方法",
            "控制器与参数",
        ], index


@pytest.mark.parametrize("chapter", range(1, 11), ids=lambda chapter: f"chapter-{chapter}")
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
        end = matches[position + 1].start() if position + 1 < len(matches) else len(markdown)
        chapter_entries.append((int(match.group(1)), markdown[match.end():end]))

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
        assert not re.search(r"\b(?:TODO|TBD)\b|待补|待定", model_text + method_text, re.IGNORECASE), global_id
