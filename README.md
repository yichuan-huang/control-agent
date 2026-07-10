# Control Agent

[中文说明](README_CN.md)

Control Agent is a research prototype for helping non-expert users move from plain-language system descriptions to conservative, auditable control design workflows. The current implementation focuses on **Core-Feature-Driven Control (CFDC)**: natural-language diagnosis, safe experiment planning, deterministic core-feature extraction, conservative controller synthesis, online gain refinement, and software simulation.

This project is not a hardware deployment package. It is intended for structured software experiments, synthetic benchmarks, and early-stage validation of CFDC workflows.

## Project Status Checklist

Checked items have executable software evidence and automated test coverage. They do not imply complete target-metric reproduction or real-hardware validation.

### Completed

- [x] Structured Stage 0 diagnosis with eight diagnostic fields and clarification questions.
- [x] Five-archetype classification with structured required features and safety constraints.
- [x] Operator-facing safe experiment plans for free-decay, ramp/step, pulse, hover-thrust, and bounded-scan experiments.
- [x] Deterministic extraction of step, modal, pulse, hover-thrust, inverse-response, and coupling features.
- [x] Conservative controller synthesis for Classes I-V with explicit tunable gain names.
- [x] Structured go/no-go validation, bounded trial reports, rollback, and freeze behavior.
- [x] Cartpole stable demo using natural-frequency-only normalized-energy swing-up and nonlinear online PD gain search.
- [x] VTOL position stable demo with signed lateral coupling and validated vertical gain refinement.
- [x] VTOL NMP boundary demo with measured undershoot, candidate history, and rollback to the last safe lateral gains.
- [x] Seven-case feature-chain smoke benchmark with explicit `closed_loop_executed=false` labeling.
- [x] Deterministic `python main.py --validate-demo` validation for Cartpole, VTOL position, and VTOL boundary.
- [x] Unified simulation performance summaries with final error, overshoot, settling, saturation, capture, channel, boundary, and violation fields.
- [x] Python 3.11/3.13 CI, editable `.[test]` installation, and automated regression tests.

### Not Completed

- [ ] Complete Cartpole outer-position NMP search with a 19-20% target undershoot boundary.
- [ ] Full-model LQR baselines and fair CFDC/LQR numerical comparisons for both case studies.
- [ ] Reproduction of the VTOL target result: 14% undershoot and 3.1 s settling time.
- [ ] Long-horizon natural-frequency FLL tracking and 30 s `k_theta` RLS updates.
- [ ] Explicit payload-change simulation with online hover-thrust, vertical-gain, and lateral-loop re-tuning.
- [ ] Stable default validation for `vtol-altitude` and `vtol-hover`.
- [ ] Closed-loop simulations for every synthetic benchmark case and a dedicated Class V MIMO plant.
- [ ] Noise, disturbance, parameter-sweep, repeated-trial, and ablation experiments.
- [ ] Real experiment CSV/JSON import, hardware approval, actuator deployment, and physical validation.

### Needs Improvement

- [ ] Reduce Cartpole actuator saturation while preserving the upright handoff and travel limits.
- [ ] Improve VTOL position settling time and add an explicit settling-time acceptance threshold.
- [ ] Replace hand-selected boundary candidate schedules with a reusable constrained search policy.
- [ ] Strengthen confidence intervals with repeated trials, filtering checks, and data-quality rejection rules.
- [ ] Make experiment amplitude and duration depend on diagnosis, time-scale hints, forbidden actions, and safety bounds.
- [ ] Add persistent multi-turn diagnostic state and evaluate deterministic versus LLM-assisted diagnosis accuracy.
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
   - Rolls back unsafe increments. Tracked-feature update utilities exist, but payload tracking is not injected into the default demo routes.

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
- `ArchetypeClassification`: canonical class, control architecture, required features, and constraints.
- `ExperimentPlan`, `ExperimentInstruction`: safe experiment plans.
- `ExperimentTrace`, `ExperimentResult`: structured experiment data.
- `CoreFeatureArtifact`: scalar feature output with confidence and data-quality metadata.
- `ControllerCandidate`: synthesized controller architecture, gains, explicitly tunable gain names, feedforward terms, saturation, and constraints.
- `OnlineTuningState`, `SafeGainSearchState`, `FeatureTrackingUpdate`: online refinement and adaptation state.
- `TrialReport`: bounded safe-trial execution report.
- `ChannelPerformanceMetrics`, `SimulationPerformanceSummary`: typed per-channel and route-level performance reports.
- `CartpoleSimulationResult`, `VtolSimulationResult`: software simulation results with backward-compatible `metrics` and structured `performance` output.
- `CFDCRunReport`: end-to-end route report from `run_cfdc_route()`.
- `GoNoGoDecision`: deterministic validation result for routes, classes, and required features.

All models inherit from `CFDCModel`, reject unexpected fields and non-finite floating-point values by default, and support JSON round trips.

### `cfdc/diagnosis/`

This layer implements Stage 0 and Stage 1.

- `engine.py` provides the deterministic diagnostic adapter through `infer_structural_diagnosis()`.
- `classify_archetype()` maps the eight diagnosis fields to CFDC canonical classes.
- `llm.py` provides `OpenAICompatibleDiagnosticAdapter`, which uses the OpenAI Python SDK to call OpenAI-compatible `/chat/completions` APIs and requires strict JSON output. It is used only for language diagnosis, not numeric controller synthesis.

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

- Class I: `detuned_PI`
- Class II: `detuned_PD`
- Class III: `small_saturated_PD`
- Class IV stable inverse-response process: `detuned_PI_with_NMP_undershoot_guard`
- Class IV unstable pendulum-like process: `safe_online_gain_search`
- Class IV VTOL-like process: `cascaded_PD_with_hover_feedforward`
- Class V: `conservative_mimo_pairing`

Required features are validated before synthesis so incomplete inputs return structured errors instead of runtime `KeyError` failures.
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

Experimental route IDs:

- `generic`
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

- `cartpole.py`: cartpole / inverted-pendulum software plant.
- `vtol.py`: planar VTOL software plant. Its lateral output is measured at a fixed offset from the center of mass so the software plant exposes the RHP-zero inverse response used by the boundary demo.
- `benchmarks.py`: seven synthetic benchmark cases.
- `integrators.py`: shared fixed-step RK4 integration with held control inputs.
- `traces.py`: shared synthetic step, modal, pulse, hover, and coupling traces.

The Cartpole reference LQR path solves the continuous algebraic Riccati equation with SciPy rather than reconstructing the stable Hamiltonian eigenspace manually.

Every Cartpole and VTOL simulation exposes primary-channel fields such as `final_error`, `abs_final_error`, `overshoot`, `settling_time_s`, `final_output`, `saturation_fraction`, and `success`. The structured `performance` object also reports all output channels, actuator-specific saturation, state boundaries, configured limits, capture state, and violations. A response that never settles uses `settled=false` and `settling_time_s=null`.

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

The benchmark is a seven-case feature-chain smoke test. It does not execute closed-loop validation.

Validate the stable software demo routes:

```bash
python main.py --validate-demo
```

Run route-level simulations:

```bash
python main.py --run-route cartpole
python main.py --run-route vtol-position
python main.py --run-route vtol-boundary
```

Run the generic pipeline:

```bash
python main.py \
  --description "A first order temperature process settles after a small heater change." \
  --observed-output temperature \
  --actuator heater
```

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
- Safe experiment planning, feature extraction, and incomplete-feature no-go behavior.
- Controller de-tuning, safe gain search, rollback/freeze, feature tracking, and MIMO pairing.
- Runtime safety checks and `SafeTrialRunner`.
- Cartpole and VTOL route reports.
- Seven-case benchmark integration.

Run tests with:

```bash
python -m pytest
```

## Current Validation Snapshot

The latest local validation snapshot for the software prototype was:

```text
python -m compileall cfdc tests main.py
tests passed=60

cartpole      completed go True upright_handoff_window_reached
vtol-position completed go True accepted
vtol-boundary completed go True boundary_triggered / nmp_undershoot
demo          3 / 3 stable routes passed
benchmark     7 / 7 feature-chain smoke cases passed
```

This means the deterministic stable-demo routes are reproducible. It does not imply complete target-metric reproduction or real-hardware validation.

## Known Boundaries

- `vtol-altitude` and `vtol-hover` routes can run CFDC controllers, but default simulation metrics may still return `metric_limit`.
- The default VTOL routes do not fabricate a payload change; long-term hover-thrust and `k_theta` tracking remain future scenarios.
- Natural-frequency continuous tracking is not yet a full long-term small-dither FLL implementation.
- VTOL `k_theta` RLS tracking is not yet integrated as a long-term route-level closed loop.
- MIMO currently has pairing and decoupling synthesis, but no dedicated MIMO plant simulation.
- Real experiment log import, hardware approval, and actuator command deployment are not implemented.

## Suggested Next Steps

1. Add the Cartpole outer-loop 20% NMP boundary search and LQR comparison.
2. Reproduce the VTOL 14% undershoot / 3.1 s settling experiment and LQR comparison.
3. Add explicit payload-change scenarios with long-horizon hover-thrust and `k_theta` tracking.
4. Add noise, disturbance, parameter-sweep, and repeated-statistics experiments.
5. Import real experiment CSV/JSON logs into `ExperimentResult`.
