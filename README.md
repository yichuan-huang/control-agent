# Control Agent

[中文说明](README_CN.md)

Control Agent is a research prototype for helping non-expert users move from plain-language system descriptions to conservative, auditable control design workflows. The current implementation focuses on **Core-Feature-Driven Control (CFDC)**: natural-language diagnosis, safe experiment planning, deterministic core-feature extraction, conservative controller synthesis, online gain refinement, and software simulation.

This project is not a hardware deployment package. It is intended for structured software experiments, synthetic benchmarks, and early-stage validation of CFDC workflows.

## Project Status Checklist

Checked items have executable software evidence and automated test coverage. They do not imply complete target-metric reproduction or real-hardware validation.

### Completed

- [x] Structured Stage 0 diagnosis with eight diagnostic fields and clarification questions.
- [x] Five-archetype classification with structured required features and safety constraints.
- [x] Optional three-layer, 14-card mechanism catalog as supplemental audit labels; disabled by default and never a replacement for the five canonical archetypes.
- [x] Operator-facing safe experiment plans for free-decay, ramp/step, pulse, hover-thrust, and bounded-scan experiments.
- [x] Deterministic extraction of step, modal, pulse, hover-thrust, inverse-response, and coupling features.
- [x] Conservative controller synthesis for Classes I-V with explicit tunable gain names.
- [x] Structured go/no-go validation, bounded trial reports, rollback, and freeze behavior.
- [x] Cartpole stable demo using natural-frequency-only normalized-energy swing-up and nonlinear online PD gain search.
- [x] Cartpole outer-position NMP candidate search with measured undershoot, multi-step rollback, and long-horizon rollback verification.
- [x] VTOL position stable demo with signed lateral coupling and validated vertical gain refinement.
- [x] VTOL NMP boundary demo with measured undershoot, candidate history, and rollback to the last safe lateral gains.
- [x] Six-scenario VTOL mass/inertia variation study with explicit stale-versus-updated feature comparisons.
- [x] Full-model Cartpole and full-state VTOL LQR baselines with matched plant, initial condition, reference, horizon, and actuator limits.
- [x] Strict final-error, settling-time, saturation, state-boundary, and post-rollback validation gates for the main channels.
- [x] Seven-case generic closed-loop benchmark from typed `BenchmarkRouteIR` through experiments, features, controller synthesis, simulation, and performance judgment.
- [x] Canonical three-value delay assessment, delay/dead-time release invariants, and adapter-equivalence coverage.
- [x] Feature-scaled Class II/III PD synthesis and uncertainty-aware Class I ordinary PI, delay-detuned PI, and large-delay refusal branches.
- [x] CLI ingress for repeated safety bounds, positive time-scale hints, and complementary `ExperimentResult` JSON traces.
- [x] Offline diagnosis evaluation with eight prompt cases, four complex cases, saved deterministic responses, and archive-style feature precision/minimality, constraint isolation, dangerous false-positive, evidence, executability, testability, and missing-information audits.
- [x] Adapter-independent diagnostic safety normalization and release gating for explicit delay ambiguity, operating-point dependence, underactuated energy exchange, and strong MIMO/NMP evidence.
- [x] Frozen 12-case diagnostic specification with a versioned SHA-256 fingerprint, deterministic/LLM response snapshots, and metric-by-metric comparison tooling.
- [x] Parameterized minimal-core/noisy/full-model feature ablations for first-order and double-integrator plants.
- [x] Deterministic `python main.py --validate-demo` validation for Cartpole, VTOL position, VTOL boundary, and VTOL variation.
- [x] Unified simulation performance summaries with final error, overshoot, settling, saturation, capture, channel, boundary, and violation fields.
- [x] Python 3.11/3.13 CI, editable `.[test]` installation, and automated regression tests.

### Not Completed

- [ ] Reproduction of the paper's Cartpole 19-20% undershoot value; the current software search enforces a 20% rejection threshold but does not reproduce that exact value.
- [ ] Reproduction of the VTOL target result: 14% undershoot and 3.1 s settling time.
- [ ] Long-horizon natural-frequency FLL tracking and 30 s `k_theta` RLS updates.
- [ ] Continuous payload-change adaptation with long-horizon hover-thrust and `k_theta` tracking; the six-scenario stale/updated study is implemented.
- [ ] Stable default validation for `vtol-altitude` and `vtol-hover`.
- [ ] Dedicated Class V MIMO plant and closed-loop controller validation.
- [ ] Noise, disturbance, parameter-sweep, and repeated-trial experiments beyond the initial feature ablations.
- [ ] Real experiment CSV import, hardware approval, actuator deployment, and physical validation.
- [ ] A real LLM response snapshot; the live comparison command is implemented, but no API credentials are present in the repository or default environment.

### Needs Improvement

- [ ] Reduce Cartpole actuator saturation while preserving the upright handoff and travel limits.
- [ ] Improve VTOL position settling time toward the paper's target; explicit settling-time acceptance thresholds are now enforced.
- [ ] Replace hand-selected boundary candidate schedules with a reusable constrained search policy.
- [ ] Strengthen confidence intervals with repeated trials, filtering checks, and data-quality rejection rules.
- [ ] Make experiment amplitude and duration depend on diagnosis, time-scale hints, forbidden actions, and safety bounds.
- [ ] Add persistent multi-turn diagnostic state and evaluate saved responses from one or more configured LLM APIs.
- [ ] Add evidence-ledger artifacts with source hashes, configuration versions, and claim-boundary summaries.
- [ ] Generate compact machine-readable and operator-facing reports for every stable and experimental route.

## Design Principles

- The LLM is limited to Stage 0 language understanding and structured diagnosis.
- Numeric control logic is implemented as deterministic Python code.
- Runtime interfaces use Pydantic models and JSON-compatible dictionaries, not free-form text.
- The system does not perform full parameter identification; it extracts the scalar core features required by the CFDC route.
- Every route produces auditable artifacts such as `go_no_go`, `evidence_boundary`, extracted features, controller candidates, and trial reports.

## CFDC Workflow

The current runtime follows a six-part loop:

1. **Stage 0: AI Diagnostic Engine and Language Understanding**
   - Reads a non-expert natural-language description.
   - Requests clarification when the description is under-specified.
   - Fills eight structural diagnosis fields: `open_loop_stability`, `minimum_phase`, `significant_delay`, `relative_degree`, `controllability_observability`, `nonlinearity_strength`, `coupling_severity`, and `uncertainty_magnitude`.

2. **Stage 1: Structural Diagnosis and Archetype Classification**
   - Maps the system to one of five CFDC canonical classes.
   - Produces the recommended control architecture, required core features, and safety constraints.
   - Optionally appends mechanism-card labels for audit and explanation. This opt-in layer does not change the canonical class, required features, safety constraints, experiment route, or controller.

3. **Stage 2: Safe Experiment Design**
   - Generates operator-facing safe experiment instructions.
   - Supports primitives such as free decay, ramp/step, pulse, hover-thrust, and bounded scan experiments.

4. **Stage 3: Core Feature Extraction**
   - Extracts scalar core features from structured experiment traces.
   - Uses deterministic estimators such as matched-filter-style frequency locking, low-pass steady-state detection, pulse integration, and ratio estimation.
   - Reports values, confidence bounds, and data-quality flags.

5. **Stage 4: Conservative Controller Synthesis**
   - Synthesizes conservative initial controllers from extracted features.
   - Uses de-tuning, saturation, cascaded architectures, online gain search, or MIMO pairing depending on the canonical class.

6. **Online Optimization and Adaptation**
   - Applies small 5-10% gain refinements.
   - Monitors overshoot, settling time, integral absolute error, high-frequency control RMS, actuator saturation, and inverse-response undershoot.
   - Rolls back unsafe increments and re-validates the rollback over the configured long horizon.
   - Runs a deterministic VTOL mass/inertia study that compares stale features with features re-extracted from each changed software plant.

## Repository Layout

```text
.
├── cfdc/
│   ├── diagnosis/
│   ├── experiments/
│   ├── features/
│   ├── controllers/
│   ├── online/
│   ├── runtime/
│   ├── sim/
│   ├── models/
│   ├── performance.py
│   ├── pipeline.py
│   └── validation.py
├── tests/
├── main.py
├── pyproject.toml
├── requirements.txt
├── README.md
└── README_CN.md
```

## Main Modules

### `cfdc/models/`

`cfdc/models/schemas.py` defines the public structured artifacts used throughout the project:

- `SystemDescription`: user description, observed outputs, actuators, and safety boundaries.
- `StructuralDiagnosis`: Stage 0 diagnosis fields and clarification questions.
- `ArchetypeClassification`: canonical class, control architecture, required features, constraints, and optional supplemental mechanism-card labels.
- `ExperimentPlan`, `ExperimentInstruction`: safe experiment plans.
- `ExperimentTrace`, `ExperimentResult`: structured experiment data.
- `CoreFeatureArtifact`: scalar feature output with confidence and data-quality metadata.
- `ControllerCandidate`: synthesized controller architecture, gains, explicitly tunable gain names, feedforward terms, saturation, and constraints.
- `OnlineTuningState`, `SafeGainSearchState`, `FeatureTrackingUpdate`: online refinement and adaptation state.
- `TrialReport`: bounded safe-trial execution report.
- `ChannelPerformanceMetrics`, `SimulationPerformanceSummary`: typed per-channel and route-level performance reports.
- `CartpoleSimulationResult`, `VtolSimulationResult`: software simulation results with backward-compatible `metrics` and structured `performance` output.
- `CartpoleBoundaryResult`, `VtolVariationResult`: structured NMP search/rollback and six-scenario variation artifacts.
- `ControllerComparison`: matched-condition CFDC/LQR performance comparison.
- `BenchmarkRouteIR`, `ClosedLoopBenchmarkCaseResult`: typed generic benchmark route and closed-loop result.
- `DiagnosticEvaluationResult`, `FeatureAblationResult`: offline diagnosis scores and structured feature-ablation results.
- `CFDCRunReport`: end-to-end route report from `run_cfdc_route()`.
- `GoNoGoDecision`: deterministic validation result for routes, classes, and required features.

All models inherit from `CFDCModel`, reject unexpected fields and non-finite floating-point values by default, and support JSON round trips.

### `cfdc/diagnosis/`

This layer implements Stage 0 and Stage 1.

- `engine.py` provides the deterministic diagnostic adapter through `infer_structural_diagnosis()`.
- `classify_archetype()` maps the eight diagnosis fields to CFDC canonical classes.
- `mechanism_cards.py` loads and validates the complete three-layer, 14-card catalog and deterministically selects optional supplemental labels. The catalog is disabled by default and its labels never replace or modify the canonical archetype route.
- `control_mechanism_card_catalog.json` preserves the catalog metadata, evidence boundary, card roles, mechanism guidance, and layer membership.
- `llm.py` provides `OpenAICompatibleDiagnosticAdapter`, which uses the OpenAI Python SDK to call OpenAI-compatible `/chat/completions` APIs and requires strict JSON output. It is used only for language diagnosis, not numeric controller synthesis.
- `evaluation.py` scores the eight diagnostic fields, required-feature recall/precision/minimality, constraint isolation, dangerous false-positive control, evidence discipline, missing-information quality, experiment executability, controller testability, archetype classification, and controller-release gate over the 8+4 case catalog. It reports extra features and constraints incorrectly selected as core features. `saved_evaluation_responses.json` supports repeatable offline scoring.
- `safety.py` applies description-evidence rules and the controller-release gate after every adapter, so LLM and deterministic diagnosis share the same fail-closed boundary.
- The 12-case catalog and archive-audit scoring policy are frozen as `cfdc-diagnostic-12-v2-archive-audit` with a SHA-256 fingerprint. Saved snapshots are rejected if their catalog, scoring policy, membership, or ordering differs.

LLM environment variables:

```bash
export CFDC_LLM_BASE_URL="https://api.openai.com/v1"
export CFDC_LLM_MODEL="gpt-4o-mini"
export CFDC_LLM_API_KEY="..."
```

### `cfdc/experiments/`

`planner.py` implements Stage 2 through `plan_safe_experiments()`. Each `ExperimentInstruction` includes the primitive type, operator steps, signals to record, estimated features, stop conditions, and a safety note.

### `cfdc/features/`

This layer implements Stage 3 as deterministic NumPy/SciPy/Python extractors. SciPy supplies the low-pass recurrence, periodogram, and decay-peak detection primitives; CFDC-specific matched-filter refinement, feature formulas, confidence bounds, and data-quality rules remain explicit in the project.

Important functions include:

- `estimate_natural_frequency()`
- `estimate_damping_ratio()`
- `estimate_step_features()`
- `estimate_dead_time()`
- `estimate_inverse_response_severity()`
- `estimate_pulse_input_gain()`
- `estimate_hover_thrust()`
- `estimate_coupling_gain()`

`dispatcher.py` routes `ExperimentResult` objects to the appropriate extractor and handles common signal aliases.

### `cfdc/controllers/`

`synthesis.py` implements Stage 4 through `synthesize_controller()`.

Supported synthesis branches include:

- Class I with `rho_high < 0.1`: `detuned_PI`
- Class I with `0.1 <= rho_high < 1.0`: `delay_detuned_PI`
- Class I with `rho_high >= 1.0`: `large_delay_compensation_required` refusal
- Class II: `detuned_PD`
- Class III: `small_saturated_PD`
- Class IV stable inverse-response process: `detuned_PI_with_NMP_undershoot_guard`
- Class IV unstable pendulum-like process: `safe_online_gain_search`
- Class IV VTOL-like process: `cascaded_PD_with_hover_feedforward`
- Class V: `conservative_mimo_pairing`

Required features are validated before synthesis so incomplete inputs return structured errors instead of runtime `KeyError` failures.
Class II and III PD gains are scaled by measured `input_gain`. Class I selection uses conservative uncertainty bounds for `rho = dead_time/time_constant`; large-delay uncertainty fails closed until a dedicated compensator is implemented and validated.
Class V loop pairing uses SciPy's global maximum-weight linear assignment rather than row-by-row greedy selection, and reports unmatched channels for centralized review.

### `cfdc/online/`

`refinement.py` reuses the shared channel-performance calculations and implements conservative gain increments, rollback/freeze behavior, safe gain search for unstable plants, and tracked-feature adaptation.

### `cfdc/runtime/`

This layer connects Stage 0-4, online refinement, and simulation into executable routes.

- `trial.py`: `SafeTrialRunner`, a bounded software trial executor.
- `safety.py`: sample-level safety checks.
- `orchestrator.py`: `run_cfdc_route()`, the end-to-end route entry point.

Stable demo route IDs:

- `cartpole`
- `vtol-position`
- `vtol-boundary`
- `vtol-variation`

Experimental route IDs:

- `generic`
- `cartpole-boundary` (explicit Cartpole boundary route; currently runs the same complete Cartpole protocol)
- `vtol-altitude`
- `vtol-hover`

### `cfdc/validation.py`

This module provides deterministic gates:

- `validate_route_compatibility()`
- `validate_required_features()`
- `merge_go_no_go()`

These gates keep route/class mismatches and missing features as structured no-go reports.

### `cfdc/sim/`

This layer contains software plants and synthetic benchmarks.

- `cartpole.py`: cartpole / inverted-pendulum plant, outer-position NMP search, long-horizon rollback validation, and full-model LQR baseline.
- `vtol.py`: planar VTOL plant, full-state LQR baseline, and mass/inertia variation study. Its lateral output is measured at a fixed offset from the center of mass so the software plant exposes the RHP-zero inverse response used by the boundary demo.
- `generic.py`: shared scalar closed-loop plants and performance gates for first-order, delayed, double-integrator, oscillator, and inverse-response routes.
- `benchmarks.py`: seven typed benchmark routes plus structured feature ablations. Cartpole and VTOL reuse their existing simulation modules.
- `integrators.py`: shared fixed-step RK4 integration with held control inputs.
- `traces.py`: shared synthetic step, modal, pulse, hover, and coupling traces.

The Cartpole reference LQR path solves the continuous algebraic Riccati equation with SciPy rather than reconstructing the stable Hamiltonian eigenspace manually.

Every Cartpole and VTOL simulation exposes primary-channel fields such as `final_error`, `abs_final_error`, `overshoot`, `settling_time_s`, `final_output`, `saturation_fraction`, and `success`. The structured `performance` object also reports all output channels, actuator-specific saturation, state boundaries, configured limits, capture state, and violations. Major routes reject responses that miss their final-error or explicit settling-time limits, exceed saturation or state boundaries, or fail long-horizon rollback validation.

## Installation With Conda

Use conda only to create and activate the Python environment. Install all Python packages with pip.

```bash
conda create -n control-agent python=3.11 -y
conda activate control-agent
python -m pip install --upgrade pip
python -m pip install -e '.[test]'
```

The project requires Python 3.11 or newer.

## Quick Checks

```bash
python -m compileall cfdc tests main.py
python -m pytest
python main.py --benchmark
python main.py --validate-demo
```

## CLI Examples

Run the benchmark suite:

```bash
python main.py --benchmark
```

The benchmark executes all seven routes through diagnosis, experiment planning, feature extraction, controller synthesis, closed-loop simulation, and the shared performance judge. Each result reports `closed_loop_executed=true` and its execution backend.

Run the feature ablations and offline diagnostic evaluator:

```bash
python main.py --feature-ablation
python main.py --diagnostic-eval
python main.py --diagnostic-eval-current
python main.py --diagnostic-eval-llm
python main.py --diagnostic-eval-llm-saved
```

`--diagnostic-eval` replays the committed deterministic responses; `--diagnostic-eval-current` evaluates a fresh deterministic response snapshot. `--diagnostic-eval-llm` calls the configured API for the same frozen 12 cases, saves only structured diagnostic artifacts, and compares all diagnostic and archive-audit metrics against the deterministic baseline. Use `--diagnostic-llm-output PATH` to override the default LLM snapshot path. `--diagnostic-eval-llm-saved` repeats the comparison without another API call.

Validate the stable software demo routes:

```bash
python main.py --validate-demo
```

Run route-level simulations:

```bash
python main.py --run-route cartpole
python main.py --run-route cartpole-boundary
python main.py --run-route vtol-position
python main.py --run-route vtol-boundary
python main.py --run-route vtol-variation
```

Run the generic pipeline:

```bash
python main.py \
  --description "A first order temperature process settles after a small heater change." \
  --observed-output temperature \
  --actuator heater
```

Supply safety metadata and one or more complementary experiment traces:

```bash
python main.py \
  --description "A delayed oven process settles after a heater change." \
  --observed-output "internal temperature" \
  --actuator "heater power setting" \
  --time-scale-hint-s 300 \
  --safety-bound output_min=20 \
  --safety-bound output_max=250 \
  --experiment-result oven-step-01.json
```

Each experiment file must contain one validated `ExperimentResult` JSON object. Duplicate safety keys and overlapping feature estimates are rejected instead of silently overriding or discarding input.

Opt in to supplemental mechanism-card labels:

```bash
python main.py --run-route cartpole --use-mechanism-cards
```

Without `--use-mechanism-cards`, `classification.supplemental_mechanism_cards` is an empty list. Programmatic callers use the same explicit `use_mechanism_cards=True` option on `DiagnosticEngine`, `run_cfdc_pipeline()`, or `run_cfdc_route()`.

Run LLM-assisted diagnosis:

```bash
python main.py \
  --use-llm \
  --description "A rod on a cart falls over when upright. I can measure cart position and rod angle." \
  --observed-output "cart position" \
  --observed-output "rod angle" \
  --actuator "cart motor force"
```

Print a full route report:

```bash
python main.py --run-route cartpole --full-report
```

Include simulated trajectory output:

```bash
python main.py --run-route cartpole --include-trajectory
```

## Tests

The test suite covers:

- Pydantic model round trips, diagnosis, and classification.
- Complete mechanism-card catalog validation, default-off behavior, deterministic opt-in labels, and proof that opt-in does not change controller synthesis.
- Safe experiment planning, feature extraction, and incomplete-feature no-go behavior.
- Feature-scaled and delay-aware controller synthesis, safe gain search, rollback/freeze, feature tracking, and MIMO pairing.
- Runtime safety checks and `SafeTrialRunner`.
- Cartpole and VTOL route reports, NMP rollback histories, variation scenarios, and LQR comparisons.
- Seven-case closed-loop benchmark integration, parameterized feature ablations, and 8+4 offline diagnosis scoring.

Run tests with:

```bash
python -m pytest
```

## Current Validation Snapshot

The latest local validation snapshot for the software prototype was:

```text
python -m compileall cfdc tests main.py
tests passed=95

cartpole      completed go True NMP boundary / rollback verified
vtol-position completed go True accepted
vtol-boundary completed go True boundary_triggered / nmp_undershoot
vtol-variation completed go True 6 / 6 expectations met
demo          4 / 4 stable routes passed
benchmark     7 / 7 generic closed-loop cases passed
ablation      2 cases / 6 trials, expected comparisons passed
diagnosis     12 / 12 strict archive-audit cases passed, 0 premature releases or dangerous false-positive controls detected
```

This means the deterministic stable-demo routes are reproducible. It does not imply complete target-metric reproduction or real-hardware validation.

## Known Boundaries

- `vtol-altitude` and `vtol-hover` routes can run CFDC controllers, but default simulation metrics may still return `metric_limit`.
- `vtol-variation` re-extracts features separately for changed software plants; it is not continuous in-flight hover-thrust or `k_theta` tracking.
- Natural-frequency continuous tracking is not yet a full long-term small-dither FLL implementation.
- VTOL `k_theta` RLS tracking is not yet integrated as a long-term route-level closed loop.
- MIMO currently has pairing and decoupling synthesis, but no dedicated MIMO plant simulation.
- The shared gate now blocks the three previously detected premature releases. Complex CSTR, Acrobot, and matrix-valued MIMO routes remain experiment plans only because their deterministic controller synthesis is not implemented.
- No real LLM comparison snapshot is committed yet; `--diagnostic-eval-llm` requires configured API credentials and records the model and prompt version in the saved structured artifact.
- Real experiment log import, hardware approval, and actuator command deployment are not implemented.

## Suggested Next Steps

1. Reproduce the paper's Cartpole 19-20% undershoot value with a reusable constrained candidate policy.
2. Reproduce the VTOL 14% undershoot / 3.1 s settling experiment.
3. Extend the six-scenario payload study into long-horizon hover-thrust and `k_theta` tracking.
4. Run and preserve LLM response snapshots for comparison against the frozen deterministic baseline.
5. Add noise, disturbance, parameter-sweep, and repeated-statistics experiments.
6. Import real experiment CSV/JSON logs into `ExperimentResult`.
