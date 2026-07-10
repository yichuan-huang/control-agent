# Normalized Delay Diagnosis and CLI Experiment Ingress Design

**Date:** 2026-07-10

## Objective

Make delayed Class I behavior independent of LLM wording, preserve `dead_time`
through experiment planning and release gates, accept real experiment traces from
the CLI, and select an auditable PI strategy from the measured delay ratio.

## Scope

This change covers five connected behaviors:

1. Canonical significant-delay semantics.
2. A controller-release invariant for delayed plants.
3. Deterministic/LLM adapter-equivalence regression coverage.
4. CLI input for safety bounds, time-scale hints, and experiment traces.
5. Explicit ordinary-PI, delay-detuned-PI, and large-delay refusal branches.

It does not implement a Smith predictor. A Smith predictor requires a separate
controller specification with a sampled internal FOPDT model, delay buffer,
predictor state, reset behavior, and anti-windup semantics. Until that controller
and its robustness benchmarks exist, large-delay release remains fail-closed.

## Canonical Delay Model

Add a `DelayAssessment` string enum with exactly three values:

- `significant`
- `not_significant`
- `unknown`

Use a delay-specific diagnostic field that retains the existing diagnostic
metadata and explanatory text:

```python
class SignificantDelayField(DiagnosticField):
    assessment: DelayAssessment
```

`StructuralDiagnosis.significant_delay` uses this specialized type. Its
`value` remains human-readable evidence for backward-compatible reports, but
no classifier, safety gate, mechanism card, planner, or controller decision may
inspect that text. Those components consume only `assessment`.

The field enforces these consistency rules:

- `status == "unknown"` requires `assessment == "unknown"`.
- `assessment == "unknown"` requires `status == "unknown"`.
- `known` and `inferred` statuses require either `significant` or
  `not_significant`.

## Adapter Boundary and Compatibility

The deterministic adapter emits `assessment` directly. The LLM prompt requires
the same three canonical values and increments its prompt version.

For compatibility with existing saved payloads and real LLM responses, a single
normalizer at the structured-payload boundary maps recognized legacy phrases to
the enum. Negative phrases are checked before positive substrings such as
`significant delay`; unknown phrases are handled explicitly afterward.

Examples:

| Input phrase | Canonical assessment |
|---|---|
| `significant delay likely` | `significant` |
| `significant delay present` | `significant` |
| `noticeable dead time` | `significant` |
| `no significant delay reported` | `not_significant` |
| `negligible delay` | `not_significant` |
| `delay unknown` | `unknown` |
| `not enough information about first-motion delay` | `unknown` |

Unrecognized or contradictory phrases fail validation instead of reaching
deterministic control logic. The normalizer is the only compatibility layer that
may inspect legacy free text.

## Classification and Release Invariants

Class I classification requires `static_gain` and `time_constant`. It also
requires `dead_time` whenever `assessment == significant`.

The shared diagnostic release gate adds a defensive cross-field invariant:

```text
significant delay AND dead_time not in required_core_features => no_go
```

Once the classification correctly includes `dead_time`, the existing Stage 3
feature gate ensures that a controller cannot be synthesized without an actual
`dead_time` artifact. Tests must demonstrate that providing only `K` and `tau`
for a significant-delay diagnosis remains `experiments_required`.

## CLI Input Contract

Add these backward-compatible command-line flags:

```text
--safety-bound KEY=FLOAT       repeatable
--time-scale-hint-s FLOAT      optional, strictly positive
--experiment-result PATH      repeatable
```

Each `--experiment-result` path contains one `ExperimentResult` JSON object.
Files are parsed in command-line order with
`ExperimentResult.model_validate_json()`. Validation errors include the source
path and exit cleanly without a Python traceback.

Example:

```bash
python main.py \
  --description "A delayed oven process ..." \
  --observed-output "internal temperature" \
  --actuator "heater power setting" \
  --time-scale-hint-s 300 \
  --safety-bound output_min=20 \
  --safety-bound output_max=250 \
  --experiment-result oven-step-01.json
```

Safety bounds and the time-scale hint populate `SystemDescription`; experiment
results are passed to `run_cfdc_pipeline()` or the generic route. Experiment
files are rejected when combined with benchmark-only or built-in Cartpole/VTOL
commands, because those commands own their simulation inputs.

Duplicate safety-bound keys are rejected to prevent silent command-line
overrides. Multiple experiment files may provide complementary estimates. If
their requested `estimates` overlap, the CLI rejects the input and names the
duplicate feature instead of inheriting the current silent first-occurrence
behavior. Repeated-trial statistical aggregation is a separate feature and is
not emulated by discarding later trials.

## Controller Strategy Selection

For Class I, derive conservative delay-ratio bounds from feature uncertainty:

```text
rho_nominal = theta.value / tau.value
rho_low     = theta.lower_bound / tau.upper_bound
rho_high    = theta.upper_bound / max(tau.lower_bound, epsilon)
```

Select the controller strategy from `rho_high`:

| Condition | Architecture | Behavior |
|---|---|---|
| no `dead_time`, or `rho_high < 0.1` | `detuned_PI` | Existing conservative Type I PI formula |
| `0.1 <= rho_high < 1.0` | `delay_detuned_PI` | Apply the existing `1 + rho_nominal` gain and integral-time detuning |
| `rho_high >= 1.0` | `large_delay_compensation_required` | Return `status="refuse"`; do not release PI |

The `0.1` boundary is a conservative engineering threshold for when delay should
be made explicit. The `1.0` large-delay boundary follows the paper's definition
of dead time comparable to or greater than the dominant time constant.

The candidate records `rho_nominal`, `rho_low`, and `rho_high` as auditable
design parameters. These are controller-design metadata, not tunable gains.
`ControllerCandidate` therefore gains a `design_parameters: dict[str, float]`
field rather than placing delay ratios in `gains`.

## Failure Behavior

- Invalid delay semantics: structured validation error; no classification.
- Significant delay with a classification missing `dead_time`: diagnostic
  `no_go` with `dead_time` listed as missing.
- Significant delay with no measured `dead_time`: Stage 3 `no_go`.
- `rho_high >= 1.0`: controller candidate is returned as `refuse`, with no
  claim that a safe large-delay controller has been produced. The pipeline and
  generic route return `status="rejected"` and `go_no_go.decision="no_go"`, not
  `controller_candidate_ready`.
- Invalid CLI safety bound or experiment file: concise `SystemExit` message that
  names the offending argument or path.

## Test Strategy

Use red-green-refactor cycles for each behavior:

1. Canonical enum round-trip and status/assessment consistency.
2. Parameterized legacy delay synonyms for all three assessments.
3. LLM-like and deterministic adapters produce identical class, required
   features, experiment estimates, and release decision for equivalent input.
4. Release invariant rejects a deliberately inconsistent classification.
5. End-to-end pipeline rejects `K/tau` without `theta` and accepts
   `K/tau/theta` only below the large-delay boundary.
6. CLI parsing propagates repeated safety bounds, time scale, and one or more
   complementary experiment files; invalid values, duplicate estimates, and
   invalid JSON fail clearly.
7. Controller threshold tests cover just below and at `0.1`, just below and at
   `1.0`, plus uncertainty intervals that cross a threshold.
8. Existing diagnostic evaluation, benchmark, Cartpole, VTOL, and full pytest
   suites remain green.

## Acceptance Criteria

- No downstream control decision searches `significant_delay.value` text.
- The user's LLM phrase `significant delay present` requires `dead_time` exactly
  as the deterministic adapter does.
- A significant-delay run cannot reach `controller_candidate_ready` with only
  `static_gain` and `time_constant`.
- CLI-provided oven trace JSON can complete Stage 3 and reach the appropriate
  Stage 4 branch.
- Large-delay uncertainty fails closed until a dedicated compensator is added.
- README examples and supported-controller documentation match the new behavior.
