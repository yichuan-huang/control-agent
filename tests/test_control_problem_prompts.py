"""Consume the published wizard instructions, not separately authored fixtures."""

import json
import math
import re
from copy import deepcopy
from pathlib import Path

import numpy as np
import pytest
from scipy import signal

from cfdc.kernel.cases import public_training_case
from cfdc.kernel.contracts import DIAGNOSTIC_IDS, TaskContract
from cfdc.kernel.session import registered_task_scope_fingerprint
from cfdc.web.drafts import (
    BUDGETS,
    DRAFT_FIELDS,
    REQUIREMENTS,
    DraftValidationError,
    case_draft,
    task_from_draft,
)
from tests.prompt_documents import read_draft_table, read_prompt_document

TECHNICAL_PATH = Path("dataset/control_problems.md")
ENGLISH_PATH = Path("dataset/control_problem_prompts.md")
CHINESE_PATH = Path("dataset/control_problem_prompts_cn.md")
DOCUMENTS = [ENGLISH_PATH, CHINESE_PATH]
CASES = [
    "dc_motor_speed_v1",
    "dc_motor_position_v1",
    "tclab_single_heater_v1",
    "quadruple_tank_nmp_v1",
    "tclab_dual_heater_v1",
    "tclab_single_heater_staged_transition_hold_v1",
]
ENTRIES = [(path, entry) for path in DOCUMENTS for entry in read_prompt_document(path)]


def _technical_ids() -> list[int]:
    return [
        int(value)
        for value in re.findall(
            r"^### (\d+)\. \[Ch\d+-\d+\]", TECHNICAL_PATH.read_text(), re.MULTILINE
        )
    ]


@pytest.mark.parametrize(
    "path,entry", ENTRIES, ids=[f"{p.stem}-{e['number']}" for p, e in ENTRIES]
)
def test_every_visible_wizard_draft_builds_current_task_contract(path, entry):
    form = entry["draft"]
    assert set(form) == set(DRAFT_FIELDS)
    task = TaskContract.from_user_input(task_from_draft(form))
    assert task.reference is not None
    assert task.output_min <= task.reference <= task.output_max
    assert task.state_stop > max(abs(task.output_min), abs(task.output_max))
    assert task.input_min < task.input_max
    assert task.budgets["distinct_experiments"] == form["distinct_experiments"]
    assert (
        task.budgets["cumulative_excitation_time_s"]
        == form["cumulative_excitation_time_s"]
    )
    assert task.budgets["clarification_rounds"] == 6
    assert task.budgets["same_failure_retries"] == 1
    assert task.budgets["elapsed_time_s"] == 7200
    assert task.measured_signals == tuple(row[0] for row in form["outputs"])
    assert task.control_inputs == tuple(row[0] for row in form["inputs"])
    assert task.signal_units == dict(form["outputs"])
    assert all(row[1] for row in form["outputs"])
    assert task.input_units
    for value in form.values():
        if isinstance(value, (float, int)):
            assert math.isfinite(value)
    for selection, fields in (
        ("success_requirement_fields", REQUIREMENTS),
        ("budget_fields", BUDGETS),
    ):
        assert len(form[selection]) == len(set(form[selection]))
        for name in fields:
            assert (form[name] is not None) == (name in form[selection])
    for enabled, value in (
        ("reference_enabled", "reference"),
        ("initial_output_value_enabled", "initial_output_value"),
        ("response_time_preference_enabled", "response_time_preference_s"),
    ):
        assert type(form[enabled]) is bool
        assert form[enabled] == (form[value] is not None)
    if task.task_type == "transition_then_hold":
        assert task.initial_region and task.goal_region
        assert task.output_min <= task.initial_output_value <= task.output_max
        assert all(
            task.output_min < value < task.output_max
            for value in task.intermediate_targets
        )
    else:
        assert not form["initial_region"] and not form["goal_region"]
        assert not form["initial_output_value_enabled"]
        assert not form["intermediate_targets"]
    if task.task_type == "disturbance_recovery_to_hold":
        assert task.disturbance_event and task.recovery_start_condition
        assert task.disturbance_hold_region
    else:
        assert not form["disturbance_event"]
        assert not form["recovery_start_condition"]
        assert not form["disturbance_hold_region"]
    assert re.findall(r"^\d+\. ([a-z_]+):", entry["diagnosis"], re.MULTILINE) == list(
        DIAGNOSTIC_IDS
    )
    assert len(re.findall(r"^### [1-7]\. ", entry["text"], re.MULTILINE)) == 7
    assert (
        f"[Ch{(entry['number'] - 1) // 20 + 1}-{(entry['number'] - 1) % 20 + 1:02d}]"
        in entry["source"]
    )


def test_bilingual_ids_titles_numeric_values_and_signal_contracts_match_source():
    english, chinese = [read_prompt_document(path) for path in DOCUMENTS]
    assert (
        [e["number"] for e in english]
        == [e["number"] for e in chinese]
        == _technical_ids()
        == list(range(1, 201))
    )
    source_titles = re.findall(
        r"^### \d+\. \[Ch\d+-\d+\] (.+)$", TECHNICAL_PATH.read_text(), re.MULTILINE
    )
    translated_fields = {
        "description",
        "initial_region",
        "goal_region",
        "disturbance_event",
        "recovery_start_condition",
        "disturbance_hold_region",
    }
    for en, cn, title in zip(english, chinese, source_titles, strict=True):
        # The original prompt English titles sometimes expand corpus headings;
        # bilingual numbering, Chinese title, and source locator remain exact.
        assert cn["title"] == title.split(" / ")[0]
        for field in DRAFT_FIELDS:
            if field not in translated_fields:
                assert en["draft"][field] == cn["draft"][field], (en["number"], field)
        assert en["source"].split("[Ch")[1] == cn["source"].split("[Ch")[1]


@pytest.mark.parametrize("path", DOCUMENTS)
def test_guide_has_current_actions_credentials_and_no_legacy_runtime_promises(path):
    text = path.read_text()
    for marker in (
        "gemma4:e4b",
        "http://127.0.0.1:11434/v1",
        "ollama",
        "RAG",
        "确认软件边界并开始",
        "下载协议",
        "选择实验数据",
        "fresh confirmation",
    ):
        assert marker in text
    for removed in (
        "### Profile Measurement Response",
        "### Profile 测量回复",
        "accompanying existing software record",
        "配套已有软件记录",
        "Executable first-order Profile proxy",
        "可执行一阶 Profile 代理模型",
    ):
        assert removed not in text
    assert (
        "does not authorize commands to physical hardware" in text
        or "不授权对实体硬件下发命令" in text
    )


@pytest.mark.parametrize("path", DOCUMENTS)
def test_appendix_preserves_exact_registered_case_drafts_and_scope(path):
    text = path.read_text()
    for index, case_id in enumerate(CASES):
        start = text.index(f"### `{case_id}`")
        end = (
            text.index(f"### `{CASES[index + 1]}`")
            if index + 1 < len(CASES)
            else len(text)
        )
        form = read_draft_table(text[start:end])
        assert form == case_draft(case_id)
        task = TaskContract.from_user_input(task_from_draft(form, case_id=case_id))
        canonical = TaskContract.from_user_input(public_training_case(case_id)["task"])
        assert registered_task_scope_fingerprint(
            task
        ) == registered_task_scope_fingerprint(canonical)


@pytest.mark.parametrize("path", DOCUMENTS)
def test_representative_plant_units_states_and_adaptations(path):
    items = {e["number"]: e for e in read_prompt_document(path)}
    for n in (21, 23, 25, 33, 37, 58, 73, 126, 165, 196):
        assert (
            items[n]["draft"]["description"] in items[n]["text"]
            or "\\" in items[n]["draft"]["description"]
            or '"' in items[n]["draft"]["description"]
        )
    assert items[21]["draft"]["outputs"] == [["speed_deviation", "m/s"]]
    assert items[21]["draft"]["input_unit"] == "N"
    assert "1250" in items[21]["diagnosis"] and "25" in items[21]["diagnosis"]
    assert items[23]["draft"]["inputs"] == [["body_torque"]]
    assert items[23]["draft"]["outputs"] == [["attitude_angle", "rad"]]
    assert "1200" in items[23]["diagnosis"] and "0.01 rad/s^2" in items[23]["diagnosis"]
    assert len(items[25]["draft"]["inputs"]) == len(items[25]["draft"]["outputs"]) == 3
    assert items[25]["draft"]["input_unit"] == "Nm"
    assert items[33]["draft"]["outputs"] == [["motor_position", "rad"]]
    assert "0.005s^2+0.06s+0.1001" in items[33]["diagnosis"]
    assert items[37]["draft"]["input_unit"] == "percentage_point"
    assert items[37]["draft"]["outputs"] == [["outlet_temperature_deviation", "degC"]]
    assert "0.5 exp(-10s)/[(30s+1)(60s+1)]" in items[37]["diagnosis"]
    assert "30(s-6)/[s(s^2+4s+13)]" in items[58]["diagnosis"]
    assert items[58]["draft"]["input_unit"] == "deg"
    assert "natural_frequency" in items[58]["diagnosis"]
    assert (
        "do not submit that parameter" in items[58]["diagnosis"]
        or "不提交该参数" in items[58]["diagnosis"]
    )
    assert "SISO" in items[58]["diagnosis"].split("7. coupling_underactuation:")[1]
    assert items[73]["draft"]["task_type"] == "disturbance_recovery_to_hold"
    assert items[73]["draft"]["inputs"] == [["armature_voltage"]]
    assert "0.067/(0.00113s^2+0.0141s+0.032489)" in items[73]["diagnosis"]
    assert "0.233489" not in items[73]["text"]  # Old PID closed-loop polynomial.
    assert items[126]["draft"]["outputs"] == [["visible_output_y", "normalized_output"]]
    assert "1 < 2" in items[126]["diagnosis"] and "C=[0,1]" in items[126]["diagnosis"]
    assert items[165]["draft"]["inputs"] == [["virtual_power_command"]]
    assert items[165]["draft"]["input_unit"] == "W"
    assert items[165]["draft"]["input_min"] == 0
    assert (
        "1 W/V^2" in items[165]["diagnosis"] and "sqrt(u/k)" in items[165]["diagnosis"]
    )
    assert items[196]["draft"]["task_type"] == "transition_then_hold"
    assert items[196]["draft"]["intermediate_targets"] == "0.3, 0.6"
    assert items[196]["draft"]["input_min"] == 0
    assert items[196]["draft"]["input_unit"] == "normalized_input"


def test_model_derived_representative_numeric_claims_are_consistent():
    # Independent source equations catch dimension/sign and source/closed-loop mixups.
    assert 500 / 50 == 10
    assert 1000 / 50 == 20
    assert 12 / 1200 == pytest.approx(0.01)
    motor_den = np.polymul([0.0113, 0.028], [0.1, 1])
    motor_den[-1] += 0.067**2
    assert motor_den == pytest.approx([0.00113, 0.0141, 0.032489])
    assert all(np.real(np.roots(motor_den)) < 0)
    a = np.diag([-3.0, -4.0])
    b = np.array([[1.0], [1.0]])
    c = np.array([[0.0, 1.0]])
    assert np.linalg.matrix_rank(np.hstack([b, a @ b])) == 2
    assert np.linalg.matrix_rank(np.vstack([c, c @ a])) == 1
    time = np.linspace(0, 12, 12001)
    _, altitude = signal.impulse(
        signal.TransferFunction([-30, 180], [1, 4, 13, 0]), T=time
    )
    assert altitude[1] < 0
    assert altitude[-1] == pytest.approx(180 / 13, abs=1e-6)
    for path in DOCUMENTS:
        item = read_prompt_document(path)[195]
        gain = 0.5226 * 0.0876 * 0.1438 / (0.1482 * 0.0863 * 0.0527)
        # The full model belongs in the original-scope section; the diagnostic
        # reply need not duplicate its coefficients or calculated static gain.
        assert str(round(gain, 3)) in item["text"]
        assert item["draft"]["reference"] / gain < item["draft"]["input_max"]


@pytest.mark.parametrize("path", DOCUMENTS)
def test_source_priors_preserve_binary_actuation_offsets_and_nondynamic_limits(path):
    items = {entry["number"]: entry for entry in read_prompt_document(path)}
    for number, item in items.items():
        assert "control_problems.md" in item["source"]
        assert (
            "Unknown" in item["diagnosis"]
            or "unknown" in item["diagnosis"]
            or "未知" in item["diagnosis"]
        )
        # Source mathematics can establish priors without fabricating measurements.
        if number not in (10, 21, 23, 25, 33, 37, 58, 73, 126, 165, 196):
            assert (
                "Source-model prior:" in item["diagnosis"]
                or "来源模型先验：" in item["diagnosis"]
            )
    assert items[1]["draft"]["final_abs_error_max"] == 0.5
    assert "{0,1}" in items[1]["diagnosis"]
    assert (
        "fractional" in items[1]["diagnosis"] or "分数加热命令" in items[1]["diagnosis"]
    )
    assert items[2]["draft"]["outputs"] == [["speed_deviation", "mph"]]
    assert items[2]["draft"]["reference"] == 5
    assert "65+speed_deviation" in items[2]["diagnosis"]
    assert "6.5+throttle_angle_deviation" in items[2]["diagnosis"]
    assert items[29]["draft"]["input_unit"] == "A"
    assert items[39]["draft"]["outputs"] == [["piston_position", "m"]]
    assert "-1" in items[101]["diagnosis"]
    assert (
        "improper" in items[101]["diagnosis"] or "非真有理" in items[101]["diagnosis"]
    )
    assert (
        "manipulated input" in items[176]["diagnosis"]
        or "可操纵输入" in items[176]["diagnosis"]
    )
    assert items[200]["draft"]["task_type"] == "local_setpoint_hold"
    assert (
        "unsupported" in items[200]["diagnosis"] or "不支持" in items[200]["diagnosis"]
    )


@pytest.mark.parametrize("path", DOCUMENTS)
def test_glucose_adaptation_defines_added_input_placement_and_absolute_bias(path):
    entry = read_prompt_document(path)[9]
    form, reply = entry["draft"], entry["diagnosis"]
    assert form["inputs"] == [["insulin_release_deviation"]]
    assert form["input_unit"] == "normalized_input"
    assert form["outputs"] == [["blood_glucose", "mg/dL"]]
    bias = float(re.search(r"blood_glucose=([\d.]+)\+delta_G", reply)[1])
    assert bias == form["reference"]
    # Parse the actual document's model, so swapped meal/command ports fail.
    a_values = re.search(r"A=(\[\[[\d.,+-]+\],\[[\d.,+-]+\]\])", reply)[1]
    b_values = re.search(r"B_u=(\[[\d.,+-]+\])\^T", reply)[1]
    c_values = re.search(r"C=(\[[\d.,+-]+\])", reply)[1]
    a = np.array(json.loads(a_values))
    b = np.array(json.loads(b_values)).reshape(2, 1)
    c = np.array(json.loads(c_values)).reshape(1, 2)
    assert b[0, 0] == 0 and b[1, 0] > 0
    assert "B_m=[1,0]^T" in reply
    numerator, denominator = signal.ss2tf(a, b, c, [[0]])
    assert denominator == pytest.approx([1, 0.1, 0.005])
    assert numerator[0] == pytest.approx([0, 0, -0.1], abs=1e-12)
    gain = (-c @ np.linalg.solve(a, b)).item()
    assert gain == pytest.approx(-20)
    assert bias + 0.1 * gain == pytest.approx(98)
    assert all(np.real(np.linalg.eigvals(a)) < 0)
    for command in (form["input_min"], form["input_max"]):
        assert form["output_min"] < bias + gain * command < form["output_max"]
    assert "added software assumptions" in reply or "新增软件假设" in reply


@pytest.mark.parametrize("path", DOCUMENTS)
def test_pupil_command_sign_uses_source_dilation_convention(path):
    entry = read_prompt_document(path)[12]
    form = entry["draft"]
    assert form["inputs"] == [["dilation_command_deviation"]]
    assert form["input_unit"] == "iris_command"
    assert form["outputs"] == [["pupil_diameter", "mm"]]
    # Read the declared nominal calibration from the actual paste-ready reply.
    gain = float(re.search(r"k_u=([+\d.]+) mm/iris_command", entry["diagnosis"])[1])
    assert gain > 0
    bias = float(re.search(r"D=([\d.]+)\+delta_D", entry["diagnosis"])[1])
    assert bias == form["reference"]
    for command in (form["input_min"], form["input_max"]):
        predicted = bias + gain * command
        assert form["output_min"] < predicted < form["output_max"]
        assert math.copysign(1, predicted - bias) == math.copysign(1, command)
    assert "conflicts" in entry["diagnosis"] or "冲突" in entry["diagnosis"]
    assert (
        "separate disturbance" in entry["diagnosis"]
        or "另一个扰动" in entry["diagnosis"]
    )


def test_parser_and_consumers_fail_on_visible_document_corruption(tmp_path):
    text = ENGLISH_PATH.read_text()
    duplicate = text.replace(
        "| Reference enabled | `reference_enabled` | `true` |",
        "| Reference enabled | `reference_enabled` | `true` |\n| Duplicate | `reference_enabled` | `true` |",
        1,
    )
    target = tmp_path / "duplicate.md"
    target.write_text(duplicate)
    with pytest.raises(ValueError, match="duplicate_draft_field"):
        read_prompt_document(target)
    # An edited visible bound reaches the actual consumer, with no parser fallback.
    target.write_text(
        text.replace(
            "| Input max | `input_max` | `1.0` |",
            "| Input max | `input_max` | `0.0` |",
            1,
        )
    )
    parsed = read_prompt_document(target)[0]
    with pytest.raises(DraftValidationError):
        task_from_draft(parsed["draft"])
    form = deepcopy(read_prompt_document(ENGLISH_PATH)[72]["draft"])
    form["disturbance_event"] = ""
    with pytest.raises(DraftValidationError):
        task_from_draft(form)


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
