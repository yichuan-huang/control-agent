# Eight-Paragraph Control Descriptions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert all 400 bilingual control-problem descriptions into one signal-introduction paragraph followed by eight detailed diagnostic paragraphs.

**Architecture:** Preserve the existing per-problem signals and verified diagnostic outcomes, then mechanically expand each current ten-sentence description into nine semantic paragraphs. Tests consume those paragraphs through the production grounding and diagnosis functions, so formatting alone cannot satisfy the acceptance gate.

**Tech Stack:** Markdown datasets, Python 3.11+, pytest, Pydantic diagnostic models.

## Global Constraints

- Modify both `dataset/control_problem_prompts.md` and `dataset/control_problem_prompts_cn.md` for all IDs 1 through 200.
- Each description has one introductory paragraph and eight ordered diagnostic paragraphs.
- Each diagnostic paragraph has at least two sentences and grounds its assigned field.
- Preserve bilingual diagnostic parity, system signals, Profile data, and special inadequate-observability semantics.
- Do not add physical-hardware commands or treat simulation boundaries as hardware authorization.

---

### Task 1: Lock the nine-paragraph dataset contract

**Files:**
- Modify: `tests/test_control_problem_prompts.py`

**Interfaces:**
- Consumes: `_field()`, `_sentences()`, `description_excerpt_answers_field()`, and `start_diagnostic_session()`.
- Produces: `_paragraphs()` and a paragraph-indexed guidance adapter used by all dataset acceptance tests.

- [ ] **Step 1: Write the failing structure and diagnostic tests**

  Change the parser expectation from one unbroken ten-sentence block to exactly
  nine paragraphs, require at least two sentences per paragraph, and select
  diagnostic evidence from paragraphs 2 through 9.

- [ ] **Step 2: Run the focused test and verify RED**

  Run: `pytest -q tests/test_control_problem_prompts.py`

  Expected: failures report one paragraph instead of nine for existing entries.

- [ ] **Step 3: Add bilingual semantic-parity coverage**

  For each paired problem, compare the literal eight `assessment` values
  returned by real diagnostic sessions.

### Task 2: Rewrite all bilingual descriptions

**Files:**
- Modify: `dataset/control_problem_prompts.md`
- Modify: `dataset/control_problem_prompts_cn.md`

**Interfaces:**
- Consumes: the current ten ordered sentences and their real deterministic
  diagnostic assessment values.
- Produces: 200 English and 200 Chinese nine-paragraph descriptions.

- [ ] **Step 1: Parse and validate every current description before rewriting**

  Require 200 unique entries per language, ten ordered source sentences per
  description, a complete diagnosis, and matching bilingual assessment values.

- [ ] **Step 2: Generate paragraph-specific elaborations**

  Preserve each existing evidence sentence and add an assessment-specific
  interpretation for minimum phase, delay, relative degree, stability,
  nonlinearity, controllability/observability, coupling, and uncertainty.

- [ ] **Step 3: Write the two Markdown datasets mechanically**

  Replace only each `Control Problem Description` / `控制问题描述` body. Leave
  titles and Profile measurement responses byte-for-byte unchanged.

- [ ] **Step 4: Run focused tests and verify GREEN**

  Run: `pytest -q tests/test_control_problem_prompts.py`

  Expected: every one of the 400 descriptions reaches `description_grounded`.

### Task 3: Verify and commit

**Files:**
- Verify: `dataset/control_problem_prompts.md`
- Verify: `dataset/control_problem_prompts_cn.md`
- Verify: `tests/test_control_problem_prompts.py`

**Interfaces:**
- Consumes: completed dataset and acceptance tests.
- Produces: a clean, committed `main` branch revision.

- [ ] **Step 1: Run the relevant flow suite**

  Run: `pytest -q tests/test_control_problem_prompts.py tests/test_description_grounded_flow.py`

- [ ] **Step 2: Run repository verification**

  Run: `pytest -q`

  Run: `python -m ruff check .`

  Run: `python -m compileall -q cfdc tests main.py`

  Run: `git diff --check`

- [ ] **Step 3: Inspect representative entries**

  Review IDs 1, 37, 126, 160, 192, and 200 in both languages for signal roles,
  significant-delay wording, inadequate observability, MIMO coupling, and
  cascade wording.

- [ ] **Step 4: Commit to main**

  Run: `git add docs/superpowers/specs/2026-08-11-eight-paragraph-prompt-descriptions-design.md docs/superpowers/plans/2026-08-11-eight-paragraph-prompt-descriptions.md dataset/control_problem_prompts.md dataset/control_problem_prompts_cn.md tests/test_control_problem_prompts.py`

  Run: `git commit -m "data: expand diagnostic prompt descriptions"`
