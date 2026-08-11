# Eight-Paragraph Control Description Design

## Status

Approved by the user through the supplied thermostat reference description. The
reference fixes both the structure and the desired level of detail, so no open
design choice remains.

## Goal

Rewrite all 200 English and all 200 Chinese control-problem descriptions so an
introductory signal paragraph is followed by eight separate diagnostic
paragraphs. Each diagnostic paragraph must independently ground exactly one of
the checklist topics well enough for the deterministic diagnosis backend to
interpret it.

## Considered approaches

1. **Deterministic expansion of the already verified dataset (selected).** Keep
   the existing system-specific signals and diagnostic classifications, split
   the evidence into dedicated paragraphs, and add classification-specific
   explanatory sentences. This preserves the 200 problems while making the
   prose consistently detailed.
2. **Regenerate every description with an LLM.** This can produce more varied
   prose, but it risks invented signals, bilingual drift, and classifications
   that no longer match the supplied Profile data.
3. **Generate descriptions dynamically at runtime.** This avoids storing long
   prose, but it changes the dataset contract and makes the user-facing prompts
   depend on a generator rather than remaining auditable source material.

## Required structure

Every description has exactly nine paragraphs:

1. System, declared control input or inputs, primary controlled output or
   outputs, and any auxiliary synchronized readings.
2. Initial response direction and minimum-phase behavior.
3. Sample interval, first distinguishable response time, and whether a separate
   pure delay exists.
4. Number of dominant storage/integration stages and relative degree.
5. Behavior after the input returns to baseline and open-loop stability.
6. Positive/negative small-signal behavior and the kind of nonlinearity.
7. Whether the declared input can excite the important motion and whether the
   synchronized readings can reconstruct it.
8. Explicit input-to-reading influence and coupling structure.
9. The magnitude of changes across safe operating conditions and which core
   structural properties remain unchanged.

The first paragraph may contain two or more sentences. Every diagnostic
paragraph contains at least two sentences: one system-specific evidence
statement and one plain-language interpretation. Signal hierarchy must be
accurate: SISO problems name one primary controlled output and treat extra
readings as auxiliary; MIMO problems identify multiple primary outputs;
cascaded problems distinguish outer-loop and inner-loop readings.

## Grounding and semantic preservation

- All evidence remains in the description and is copied verbatim by the test
  adapter; no synthetic measurement history is introduced.
- Each of the eight paragraphs must pass
  `description_excerpt_answers_field()` for its assigned diagnostic field.
- A real `start_diagnostic_session()` call must reach `description_grounded`
  with eight facts and a complete deterministic diagnosis.
- English and Chinese versions of each problem must produce the same eight
  diagnostic assessments.
- The pole-zero cancellation problem keeps its deliberately inadequate
  controllability/observability result.
- Timing values and signal names continue to come from the existing problem and
  Profile record. Added prose may clarify a condition but must not change the
  model or Profile measurement data.

## Verification

The dataset test parses all 400 descriptions, asserts nine paragraphs and the
intro-plus-eight ordering, and submits each real diagnostic paragraph through
the production grounding and diagnosis path. A bilingual parity test compares
all eight assessment values for every problem. Full repository tests, Ruff,
compileall, and `git diff --check` must pass before completion.
