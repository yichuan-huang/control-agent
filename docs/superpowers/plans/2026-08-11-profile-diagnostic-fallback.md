# Profile Diagnostic Fallback Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prevent an ungrounded LLM diagnostic recheck from crashing a valid Profile measurement submission while preserving grounded contradiction invalidation.

**Architecture:** Validate official LLM measurement-extraction output at the adapter boundary with the existing grounding validator. When a Profile-stage call has a previous `ready` assessment and the new candidate is malformed or ungrounded, return a deep serialized copy of the previous trusted assessment; keep session-level validation strict for every other caller.

**Tech Stack:** Python 3.11+, Pydantic v2, OpenAI-compatible chat completions, pytest.

## Global Constraints

- Do not weaken `validate_grounded_measurement_assessment()` or `submit_profile_measurement_assessment()`.
- Fall back only when `previous_assessment.status == "ready"`.
- A grounded changed fact or conflict must still pass through and invalidate downstream state.
- The same raw Profile response must continue into specification extraction after fallback.
- Do not catch the error in Gradio or turn provider failures into fabricated diagnostic facts.

---

### Task 1: Reproduce the provider-boundary failure

**Files:**
- Modify: `tests/test_guided_measurement_flow.py`
- Test: `tests/test_guided_measurement_flow.py`

**Interfaces:**
- Consumes: `OpenAICompatibleDiagnosticAdapter.extract_measurements(description, measurement_plan, measurement_response, previous_assessment)`.
- Produces: regression tests for ungrounded Profile fallback and grounded diagnostic changes.

- [ ] **Step 1: Add a ready prior diagnostic assessment fixture inside the test**

Build the fixed measurement plan from `_description()`, then use `GuidedFakeAdapter` to create a complete `MeasurementAssessment(status="ready")` for all eight requests.

- [ ] **Step 2: Add a fake provider response with an unattested delay number**

Return a ready assessment that copies seven prior facts but replaces `significant_delay` with:

```python
MeasuredFact(
    request_id="significant_delay",
    source_excerpt="The declared software model has an input delay of 0 s.",
    numeric_value=1.5,
    unit="s",
)
```

Use a raw response containing both `63% response time is 1.5 s` and
`input delay is 0 s`. Assert that `extract_measurements()` returns the exact prior ready assessment.

- [ ] **Step 3: Add the grounded-change control test**

Replace one prior text fact with a changed fact whose `source_excerpt` and `text_value` both occur verbatim in the raw response. Assert that the adapter returns the changed candidate rather than the prior assessment.

- [ ] **Step 4: Run both tests and verify RED**

Run: `pytest -q tests/test_guided_measurement_flow.py -k 'profile_recheck'`

Expected: the ungrounded fallback test FAILS because the adapter currently returns the invalid candidate; the grounded-change control test PASSES or remains unaffected.

- [ ] **Step 5: Commit the RED tests**

```bash
git add tests/test_guided_measurement_flow.py
git commit -m "test: reproduce ungrounded profile recheck"
```

### Task 2: Validate and fall back inside the official LLM adapter

**Files:**
- Modify: `cfdc/diagnosis/llm.py`
- Test: `tests/test_guided_measurement_flow.py`

**Interfaces:**
- Consumes: `validate_grounded_measurement_assessment(plan, candidate, raw_response, previous_assessment=previous)`.
- Produces: a grounded candidate assessment or the exact previous ready assessment serialized as JSON-compatible data.

- [ ] **Step 1: Import the existing grounding validator**

Add `validate_grounded_measurement_assessment` beside the other imports from `cfdc.diagnosis.measurements`.

- [ ] **Step 2: Add the Profile-stage validation gate**

After parsing the provider JSON into `MeasurementAssessment`, validate it whenever `previous_assessment` is ready:

```python
if previous_assessment is not None and previous_assessment.status == "ready":
    try:
        validate_grounded_measurement_assessment(
            measurement_plan,
            assessment,
            measurement_response,
            previous_assessment=previous_assessment,
        )
    except ValueError:
        assessment = previous_assessment.model_copy(deep=True)
```

Include Pydantic schema-validation failures in the same ready-only fallback boundary; preserve the existing initial/partial diagnostic behavior.

- [ ] **Step 3: Run the focused tests and verify GREEN**

Run: `pytest -q tests/test_guided_measurement_flow.py -k 'profile_recheck or live_measurement_extraction_rejects_non_strict_payload or profile_only_response'`

Expected: all selected tests PASS.

- [ ] **Step 4: Run all guided/session/specification tests**

Run: `pytest -q tests/test_guided_measurement_flow.py tests/test_guided_measurement_sessions.py tests/test_description_grounded_flow.py tests/test_specification_evidence.py tests/test_gradio_app.py`

Expected: all tests PASS.

- [ ] **Step 5: Commit the production fix**

```bash
git add cfdc/diagnosis/llm.py
git commit -m "fix: ignore ungrounded profile diagnostic rechecks"
```

### Task 3: Final verification

**Files:**
- Verify: `cfdc/diagnosis/llm.py`
- Verify: `tests/test_guided_measurement_flow.py`

**Interfaces:**
- Consumes: final committed main-branch tree.
- Produces: repository-wide verification evidence.

- [ ] **Step 1: Run the full suite**

Run: `pytest -q`

Expected: all tests PASS; only the previously documented SciPy coefficient-conditioning warnings may remain.

- [ ] **Step 2: Run static and syntax checks**

Run: `python -m ruff check .`

Expected: `All checks passed!`

Run: `python -m compileall -q cfdc tests main.py`

Expected: exit code 0.

Run: `git diff --check`

Expected: exit code 0.

- [ ] **Step 3: Confirm a clean main branch**

Run: `git status --short`

Expected: no output after commits.
