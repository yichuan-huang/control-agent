# Profile Seven-Field Prompt Format Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reformat all 200 English and 200 Chinese control-problem Profile responses so the seven common requested values are explicit, ordered natural-language answers followed by clearly marked additional Profile information.

**Architecture:** Keep the two prompt documents as the source of truth and extend their existing parser test as the format contract. The migration changes only the Profile response section of each entry: seven labeled answers come first, then all remaining model, record, timing, delay, and specialist Profile content is retained under an additional-information heading.

**Tech Stack:** Markdown datasets, Python `re`, pytest, Ruff.

## Global Constraints

- Modify `dataset/control_problem_prompts.md` and `dataset/control_problem_prompts_cn.md`; each must retain exactly 200 aligned entries.
- Preserve every control-problem description byte-for-byte.
- Preserve existing case values, units, model meaning, specialist Profile parameters, record configuration, and software-only safety statement.
- Do not add JSON, assignment tokens such as `input_change=`, or the removed eight-item measurement-response section.
- Put the seven fixed labels in the approved order and exactly once per Profile response.
- Retain non-seven-field content under `Additional information` / `额外信息`.

---

### Task 1: Lock the bilingual seven-field contract

**Files:**
- Modify: `tests/test_control_problem_prompts.py`
- Test: `tests/test_control_problem_prompts.py`

**Interfaces:**
- Consumes: `_parse_document(path, headings, language) -> list[dict]` and each parsed entry's `profile` string.
- Produces: `ENGLISH_PROFILE_LABELS`, `CHINESE_PROFILE_LABELS`, and regression assertions used to validate both prompt documents.

- [ ] **Step 1: Add fixed bilingual label constants**

```python
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
```

- [ ] **Step 2: Add the failing format test**

```python
@pytest.mark.parametrize(
    ("path", "headings", "language", "labels", "extra_heading"),
    [
        (ENGLISH_PATH, ENGLISH_HEADINGS, "en", ENGLISH_PROFILE_LABELS, "Additional information"),
        (CHINESE_PATH, CHINESE_HEADINGS, "cn", CHINESE_PROFILE_LABELS, "额外信息"),
    ],
)
def test_every_profile_response_lists_seven_answers_before_additional_information(
    path, headings, language, labels, extra_heading
):
    entries = _parse_document(path, headings, language)
    for index, entry in enumerate(entries, 1):
        profile = entry["profile"]
        positions = [profile.index(f"**{label}：**" if language == "cn" else f"**{label}:**") for label in labels]
        assert positions == sorted(positions), (language, index)
        assert all(profile.count(label) == 1 for label in labels), (language, index)
        assert profile.count(extra_heading) == 1, (language, index)
        assert positions[-1] < profile.index(extra_heading), (language, index)
```

- [ ] **Step 3: Run the focused test and verify RED**

Run: `pytest -q tests/test_control_problem_prompts.py -k seven_answers`

Expected: FAIL because the current compact paragraphs do not contain the seven fixed labels or the additional-information heading.

- [ ] **Step 4: Commit the RED test**

```bash
git add tests/test_control_problem_prompts.py
git commit -m "test: require explicit profile prompt answers"
```

### Task 2: Reformat all bilingual Profile responses

**Files:**
- Modify: `dataset/control_problem_prompts.md`
- Modify: `dataset/control_problem_prompts_cn.md`
- Test: `tests/test_control_problem_prompts.py`

**Interfaces:**
- Consumes: the seven values already expressed by each entry's natural-language Profile material and all remaining Profile paragraphs.
- Produces: the approved English and Chinese seven-answer blocks plus an additional-information block in every entry.

- [ ] **Step 1: Rewrite each English Profile lead block**

Use this exact structure, substituting the existing case-specific signal, number, and unit text without internal fact IDs:

```markdown
The seven required answers are:

- **Known input change:** ...
- **Final output change:** ...
- **63% response time:** ...
- **Input simulation lower bound:** ...
- **Input simulation upper bound:** ...
- **Output simulation lower bound:** ...
- **Output simulation upper bound:** ...

Additional information:

...
```

- [ ] **Step 2: Rewrite each Chinese Profile lead block**

Use the bilingual-equivalent structure and retain the same values and units as the aligned English entry:

```markdown
七项必填回答：

- **已知输入变化量：** ...
- **最终输出变化量：** ...
- **63% 响应时间：** ...
- **输入仿真下限：** ...
- **输入仿真上限：** ...
- **输出仿真下限：** ...
- **输出仿真上限：** ...

额外信息：

...
```

- [ ] **Step 3: Preserve the remaining Profile material**

Move pure delay, physical constants, transfer-function/state-space/nonlinear model declarations, sample interval, duration, initial condition, amplitude levels, parameter-variation cases, and disturbances below the additional-information heading. Keep the final software-simulation-only safety sentence unchanged.

- [ ] **Step 4: Run the focused tests and verify GREEN**

Run: `pytest -q tests/test_control_problem_prompts.py`

Expected: all prompt dataset tests PASS for 200 English and 200 Chinese entries.

- [ ] **Step 5: Review representative entries**

Inspect entries 1, 2, 25, 27, 80, 120, 160, and 200 in both files. Confirm seven labels are ordered, English/Chinese values align, specialist model data remains in additional information, and no description text changed.

- [ ] **Step 6: Commit the data migration**

```bash
git add dataset/control_problem_prompts.md dataset/control_problem_prompts_cn.md
git commit -m "data: label profile prompt measurements"
```

### Task 3: Complete repository verification

**Files:**
- Verify: `dataset/control_problem_prompts.md`
- Verify: `dataset/control_problem_prompts_cn.md`
- Verify: `tests/test_control_problem_prompts.py`

**Interfaces:**
- Consumes: the migrated prompt files and the completed dataset contract tests.
- Produces: final verification evidence for the main-branch change.

- [ ] **Step 1: Run the full test suite**

Run: `pytest -q`

Expected: all tests PASS; only previously documented SciPy numerical-conditioning warnings may remain.

- [ ] **Step 2: Run static and syntax checks**

Run: `python -m ruff check .`

Expected: `All checks passed!`

Run: `python -m compileall -q cfdc tests main.py`

Expected: exit code 0 with no output.

Run: `git diff --check`

Expected: exit code 0 with no whitespace errors.

- [ ] **Step 3: Confirm the final file scope**

Run: `git status --short`

Expected: only the two prompt datasets and their contract test are modified before the final commit.

- [ ] **Step 4: Commit any final test-only adjustments**

```bash
git add tests/test_control_problem_prompts.py
git commit -m "test: verify bilingual profile answer format"
```
