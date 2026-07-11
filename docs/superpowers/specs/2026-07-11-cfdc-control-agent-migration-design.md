# CFDC Control-Agent Migration Design

Date: 2026-07-11

Status: approved design

## Objective

Complete the CFDC workflow by migrating the archive capabilities that are required by the paper:

1. a typed `CandidateRouteIR`;
2. capability compilation and structured capability gaps;
3. a feature-quality release gate;
4. safety-bound and time-scale-aware experiment design;
5. a reusable implementation of paper Algorithm 1;
6. continuous FLL, hover-average, and RLS feature tracking;
7. serializable multi-turn diagnosis state.

The change must also separate real operation from deterministic simulation testing. Real workflows must never silently consume synthetic CartPole or VTOL experiment traces.

## Delivery Slices

The work is split into three independently testable slices:

1. Route and release foundation: workflow mode, route IR, capability compiler, quality gate, and parameterized experiments.
2. Online control: generic Algorithm 1 and continuous feature tracking.
3. Interactive diagnosis: multi-turn session state and end-to-end integration.

Existing public APIs remain available. New behavior is added through typed optional parameters and report fields rather than a wholesale orchestrator rewrite.

## Workflow Modes and Data Provenance

Add `WorkflowMode` with values `simulation` and `real`.

Public route APIs accept `workflow_mode: WorkflowMode | None`. Resolution is deterministic:

- an explicit `real` value selects the real workflow;
- an explicit `simulation` value selects deterministic testing only;
- `None` resolves to `real` when a diagnostic LLM adapter is supplied;
- `None` resolves to `simulation` when no diagnostic adapter is supplied;
- supplying an LLM adapter together with explicit `simulation` is rejected as an invalid configuration.

The resolved mode is stored in every `CFDCRunReport`.

In `real` mode:

- synthetic experiment fixtures are forbidden;
- Stage 2 may produce an experiment plan, but Stage 3 cannot proceed without caller-supplied `ExperimentResult` objects or caller-supplied reviewed features;
- features supplied directly must declare real or externally reviewed provenance;
- missing experiment data returns `experiments_required`, never `completed`;
- capability, data-quality, and safety failures are fail-closed.

In `simulation` mode:

- CartPole and VTOL routes may load deterministic synthetic fixtures when neither results nor features are supplied;
- every fixture and derived feature is labeled `synthetic_fixture`;
- reports retain the existing simulation-only evidence boundaries;
- this mode is used by regression tests, demonstrations, and benchmark suites.

## CandidateRouteIR

`CandidateRouteIR` is the deterministic handoff between diagnosis and execution. It does not contain hidden plant parameters or simulator ground truth.

It contains:

- `route_id` and `workflow_mode`;
- `canonical_class` and optional supplemental mechanism cards;
- a normalized control architecture identifier;
- typed experiment requests;
- required and optional core-feature IDs;
- a controller-template identifier and tunable gain names;
- an online-refinement policy;
- feature-tracking requests;
- validation metrics and safety constraints;
- evidence boundary and schema version.

Each experiment request contains a supported primitive, input and output signal IDs, feature IDs, amplitude, duration, sample rate, operating region, stop conditions, and provenance requirement.

The route IR is produced deterministically from `StructuralDiagnosis`, `ArchetypeClassification`, `SystemDescription`, and resolved workflow mode. An LLM may populate diagnosis fields, but it cannot directly authorize controller release or invent executable capabilities.

`BenchmarkRouteIR` remains separate. It continues to describe hidden simulator parameters and benchmark conditions and must not be accepted by the real workflow compiler.

## Capability Compiler and Gaps

Introduce a versioned `CapabilityCatalog` containing:

- supported experiment primitives and compatible classes;
- signal requirements for each primitive;
- feature extractors and their permitted experiment sources;
- controller templates, required feature sets, and compatible classes;
- online-refinement policies;
- tracking implementations;
- simulator fixtures available only in simulation mode.

`compile_candidate_route(route, catalog)` returns a `CompiledRoute` and never silently drops unsupported items. Compilation produces zero or more typed `CapabilityGap` objects with:

- a stable code;
- the affected stage and capability ID;
- a human-readable explanation;
- whether another measurement can resolve the gap;
- the required next action.

Blocking gaps include unknown primitives, missing signals, unsupported extractors, class/controller mismatch, missing tracking implementations, forbidden synthetic provenance in real mode, and unimplemented MIMO matrix routes. Any blocking gap makes the route no-go.

## Parameterized Safe Experiment Design

`plan_safe_experiments` is extended to consume `SystemDescription` and workflow mode. Existing two-argument calls remain supported for compatibility but produce unparameterized simulation-only plans.

Every new `ExperimentInstruction` includes numeric design parameters:

- `input_amplitude` and units when an actuator limit is available;
- `duration_s`;
- `sample_rate_hz`;
- `operating_region`;
- `required_safety_bounds`;
- `provenance_requirement`;
- existing operator steps and stop conditions.

Default deterministic sizing rules are:

- pulse amplitude: 5 percent of the applicable absolute actuator limit;
- step or ramp amplitude: 5 percent of the applicable input range;
- free-decay displacement: 10 percent of the applicable state range;
- pulse duration: 0.1 times the coarse time scale, clipped to 0.02-0.5 seconds;
- free-decay duration: 6 times the coarse time scale;
- step duration: 8 times the coarse time scale;
- sample rate: at least 50 samples per coarse time scale and never below 20 Hz;
- hover ramp duration: 5 times the coarse time scale with a 5 percent command increment.

The planner maps common safety-bound aliases to canonical actuator and state limits. In real mode, an experiment that lacks a required numeric safety bound becomes a capability/safety gap and requests clarification. In simulation mode, normalized fixture bounds may be used and must be labeled as such.

Any primitive named by `forbidden_actions` is rejected. Operator instructions include the numeric amplitude, duration, sample rate, and stop threshold rather than only words such as "small" or "brief".

## Feature Artifact Provenance and Quality Gate

Extend `CoreFeatureArtifact` with backward-compatible defaulted fields:

- `object_id`;
- `trace_sha256`;
- `experiment_protocol_version`;
- `estimator_version`;
- `operating_region`;
- `provenance`, with `synthetic_fixture`, `real_experiment`, and `externally_reviewed` values;
- `applicable_plant_families`;
- `invalidating_conditions`.

`evaluate_feature_quality(classification, features, workflow_mode, policy)` returns a `FeatureQualityDecision` with `accept`, `repeat_experiment`, or `refuse`.

Default release rules are:

- all required feature IDs must be present;
- values and confidence bounds must be physically valid for the feature type;
- confidence must be at least 0.70;
- relative confidence half-width must not exceed 0.50 for a nonzero feature;
- repeatable data-quality flags cause `repeat_experiment`;
- invalid physical sign/domain, zero critical denominator, non-finite provenance metadata, or forbidden synthetic provenance causes `refuse`;
- real mode accepts only `real_experiment` or `externally_reviewed` provenance;
- trace hashes are required for `real_experiment` provenance;
- controller synthesis runs only after an `accept` decision.

Uncertainty is propagated into controller synthesis by using the conservative gain or time-scale bound. Existing fixed detuning remains an additional margin, not a substitute for the quality gate.

## Generic Algorithm 1 State Machine

Introduce a generic `OnlineRefinementPolicy` and `Algorithm1State`. The state owns current accepted gains, candidate gains, previous safe gains, step fraction, dwell/probe counters, violation counters, history, and frozen reason.

The default step multiplier is 1.05. A configured value must be between 1.05 and 1.10 inclusive.

The state machine is:

1. propose a candidate by multiplying only declared tunable gains;
2. apply the candidate through a plant-specific trial executor;
3. enforce dwell time before evaluating a probe;
4. compute performance, NMP undershoot, high-frequency control RMS, saturation, oscillation, and state-boundary indicators;
5. immediately rollback and freeze on hard safety violations;
6. require two consecutive NMP or soft performance violations before rollback and freeze;
7. accept the candidate and make it the new safe point when no violation is present;
8. stop when a target is met, a configured iteration limit is reached, or a constraint freezes the search.

CartPole and VTOL provide trial executors and signal mappings. Candidate generation, dwell, consecutive violation handling, rollback, freeze, and history are shared. Existing hand-authored candidate lists remain available only as archived baseline fixtures and are not used by the new generic refinement path.

## Continuous Feature Tracking

Introduce three tracker types and a shared scheduler.

### FrequencyLockedLoopTracker

The FLL maintains a current angular frequency and a rolling window. At each eligible window it performs a narrow matched-filter search around the current frequency, estimates lock quality, and applies a bounded exponential update. The search band and smoothing gain are derived from the configured FLL bandwidth. Updates with inadequate lock quality are rejected without changing the controller.

### ScalarRLSTracker

The scalar RLS state contains parameter estimate, covariance, and forgetting factor. The default forgetting factor is 0.95. Each eligible `(regressor, response)` sample applies the standard scalar RLS update. Degenerate regressors are ignored and recorded.

### HoverAverageTracker

The hover tracker applies a time-constant-based exponential moving average to steady-state control effort. The default time constant is 10 seconds.

### TrackingScheduler

Tracking is eligible only when:

- the route is in a declared steady operating mode;
- tracking error is below the configured threshold;
- no hard safety limit is active;
- no aggressive maneuver flag is active;
- the tracker duty-cycle interval has elapsed.

The scheduler pauses otherwise. A feature change greater than 5 percent produces a `FeatureTrackingUpdate`, smoothly recomputes dependent gains or feedforward terms, and records the pre-update controller. A hover-thrust change greater than 10 percent requests a restart of NMP outer-loop refinement from the current safe gains.

## Multi-Turn Diagnosis State

Introduce a JSON-round-trippable `DiagnosticSessionState` with:

- session ID and schema version;
- resolved workflow mode;
- initial and accumulated system descriptions;
- ordered turns containing questions, answers, and evidence;
- current diagnosis and classification;
- pending clarification questions;
- candidate/compiled route when available;
- status: `collecting_information`, `ready_for_experiments`, `experiments_required`, `ready_for_controller`, `refused`, or `complete`;
- a maximum of eight clarification turns.

`start_diagnostic_session` performs the first diagnosis. `continue_diagnostic_session` accepts answers keyed by the prior pending questions, appends evidence, rebuilds the description presented to the adapter, reruns the shared diagnostic safety rules, and advances only when all eight fields are resolved.

The library does not introduce a database. The caller persists the serialized session state. CLI support reads and writes session JSON files atomically through explicit arguments. Real sessions never store API keys or raw provider credentials.

After diagnosis becomes complete, the session compiles the candidate route. In real mode it stops at `experiments_required` until real experiment results or reviewed features are supplied. In simulation mode it may continue with fixtures.

## Orchestrator Data Flow

The final route flow is:

```text
resolve workflow mode
-> diagnose or resume session
-> build CandidateRouteIR
-> compile capabilities
-> parameterize safe experiments
-> obtain real results or simulation fixtures
-> extract features
-> feature-quality release gate
-> conservative controller synthesis
-> bounded trial
-> generic Algorithm 1 refinement
-> scheduled continuous tracking
-> structured report
```

No stage may infer success from the existence of a later-stage fixture. Reports keep separate fields for planned, supplied, synthetic, accepted, repeated, and refused evidence.

## Error and Status Semantics

Configuration errors such as LLM plus explicit simulation mode raise `ValueError` before diagnosis.

Discoverable workflow deficiencies do not raise generic runtime exceptions. They return structured no-go reports:

- missing information -> `need_more_information`;
- missing real experiment data -> `experiments_required`;
- capability gaps -> `rejected` with gap objects;
- repeatable feature-quality failure -> `experiments_required`;
- non-repeatable feature-quality or physical-domain failure -> `rejected`;
- online constraint -> `frozen` with restored safe gains;
- successful simulation-only execution -> `completed` with simulation evidence boundary.

## Compatibility

- Existing deterministic tests without an adapter resolve to simulation mode.
- Existing CartPole and VTOL demo commands continue to work using labeled fixtures.
- Generic routes without results still stop at `experiments_required` because no generic fixture is implied.
- Existing serialized artifacts remain valid because new fields have defaults.
- `BenchmarkRouteIR` and existing benchmark APIs remain unchanged except for provenance reporting.
- Deprecated implicit fixture behavior emits no separate warning because the resolved workflow mode is explicit in every report and CLI output.

## Testing Strategy and Acceptance Criteria

Implementation follows red-green-refactor TDD. New tests must first fail for the missing behavior.

Acceptance requires:

1. LLM real mode without experiment data returns `experiments_required` and contains no synthetic results or features.
2. Deterministic simulation mode runs existing CartPole and VTOL fixtures and labels them synthetic.
3. LLM plus explicit simulation mode is rejected.
4. Candidate routes round-trip through JSON and never contain hidden plant parameters.
5. Capability compilation reports stable blocking gap codes and never drops unsupported capabilities.
6. Parameterized experiments change with safety bounds and time-scale hints and reject forbidden actions.
7. Zero-confidence, wide-bound, invalid-domain, and synthetic-in-real features cannot release a controller.
8. Algorithm 1 uses 5-10 percent multiplicative steps, respects dwell, requires two consecutive soft violations, and restores the previous safe gains.
9. Hard safety violations rollback immediately.
10. FLL tracking converges on a drifting sinusoid within its declared search band.
11. Scalar RLS converges on a synthetic gain and pauses when the scheduler is ineligible.
12. Hover tracking updates feedforward only after the threshold and steady-state gates are satisfied.
13. Multi-turn diagnosis survives JSON round-trip and advances from clarification to experiment planning.
14. All existing tests remain green.
15. CLI and README document real versus simulation behavior without claiming physical validation.

## Out of Scope

- hardware deployment;
- database-backed session storage;
- training or fine-tuning an LLM;
- dynamic MIMO controller synthesis beyond capability-gap reporting;
- formal control-barrier or reachability certificates;
- replacing the paper's five canonical classes with mechanism cards;
- reproducing paper-specific performance numbers by hand tuning.
