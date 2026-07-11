# CFDC Control-Agent Migration Implementation Plan

> **For agentic workers:** Execute this plan task-by-task with red-green-refactor TDD and a review checkpoint after each task.

**Goal:** Complete the paper-required CFDC route, release, online refinement, tracking, and multi-turn diagnosis capabilities while separating real LLM workflows from deterministic simulation fixtures.

**Architecture:** Add typed workflow artifacts to the existing Pydantic model layer, place route compilation under `cfdc/workflow`, quality evaluation under `cfdc/features`, reusable online logic under `cfdc/online`, and session orchestration under `cfdc/diagnosis`. Keep current route APIs compatible, but resolve and report a workflow mode before any synthetic data can be selected.

**Tech Stack:** Python 3.11+, Pydantic 2, NumPy, SciPy, pytest.

## Global Constraints

- `real` mode never loads synthetic experiment fixtures.
- an LLM diagnostic adapter implies `real` mode; explicit LLM plus `simulation` raises `ValueError`.
- `simulation` mode remains the default for adapter-free regression tests.
- controller synthesis requires an accepted feature-quality decision.
- Algorithm 1 uses multiplicative steps in the inclusive range 1.05-1.10.
- multi-turn session state must round-trip through JSON without API credentials.
- all additions remain software evidence and do not claim hardware safety.

---

### Task 1: Workflow Mode and Provenance Models

**Files:**
- Create: `cfdc/workflow/__init__.py`
- Create: `cfdc/workflow/mode.py`
- Modify: `cfdc/models/schemas.py`
- Modify: `cfdc/models/__init__.py`
- Modify: `cfdc/features/dispatcher.py`
- Modify: `cfdc/runtime/orchestrator.py`
- Modify: `cfdc/sim/traces.py`
- Test: `tests/test_workflow_modes.py`

**Interfaces:**
- Produces `WorkflowMode`, `DataProvenance`, and `resolve_workflow_mode(workflow_mode, diagnostic_adapter)`.
- Extends `ExperimentResult`, `CoreFeatureArtifact`, and `CFDCRunReport` with provenance/mode fields.

- [ ] Write tests proving adapter-free routes resolve to `simulation`, adapter-backed routes resolve to `real`, explicit LLM plus simulation raises, real mode without results has no synthetic artifacts, and simulation CartPole/VTOL fixtures are labeled synthetic.
- [ ] Run `pytest tests/test_workflow_modes.py -q` and confirm failure because the models and resolver do not exist.
- [ ] Add backward-compatible enum/default fields and a single shared mode resolver.
- [ ] Propagate every experiment result's provenance into its extracted feature artifacts.
- [ ] Remove the unconditional synthetic fallback from `run_cfdc_route`; guard fixture construction with resolved simulation mode.
- [ ] Run the focused test until green, then run `pytest tests/test_orchestrator.py tests/test_main_cli.py -q`.
- [ ] Commit the task.

### Task 2: CandidateRouteIR and Capability Compiler

**Files:**
- Create: `cfdc/workflow/routes.py`
- Create: `cfdc/workflow/capabilities.py`
- Modify: `cfdc/models/schemas.py`
- Modify: `cfdc/models/__init__.py`
- Modify: `cfdc/runtime/orchestrator.py`
- Test: `tests/test_workflow_compiler.py`

**Interfaces:**
- Produces `CandidateExperimentRequest`, `CandidateRouteIR`, `CapabilityGap`, `CompiledRoute`, `CapabilityCatalog`.
- Produces `build_candidate_route(...)` and `compile_candidate_route(...)`.

- [ ] Write JSON round-trip and hidden-parameter exclusion tests for CandidateRouteIR.
- [ ] Write compiler tests for supported routes, unknown primitive, missing signal, class/controller mismatch, missing tracker, MIMO matrix gap, and synthetic provenance in real mode.
- [ ] Run the focused tests and confirm missing-type/function failures.
- [ ] Implement the typed models, default capability catalog, route builder, and non-dropping compiler.
- [ ] Add candidate and compiled routes to `CFDCRunReport`; stop before experiments when blocking gaps exist.
- [ ] Run compiler and orchestrator tests, then commit.

### Task 3: Parameterized Safe Experiment Planner

**Files:**
- Modify: `cfdc/models/schemas.py`
- Modify: `cfdc/experiments/planner.py`
- Modify: `cfdc/pipeline.py`
- Modify: `cfdc/runtime/orchestrator.py`
- Test: `tests/test_parameterized_experiments.py`

**Interfaces:**
- Extends `plan_safe_experiments(diagnosis, classification, description=None, workflow_mode="simulation")`.
- Extends `ExperimentInstruction` with numeric experiment parameters and planning gaps.

- [ ] Write tests showing amplitude scales with actuator bounds, duration/sample rate scale with `time_scale_hint_s`, forbidden pulse/free-release actions are rejected, and real mode missing bounds produces a safety gap.
- [ ] Verify focused tests fail against the existing two-argument template planner.
- [ ] Implement canonical safety-bound aliases and deterministic sizing rules from the design spec.
- [ ] Preserve two-argument compatibility as unparameterized simulation-only planning.
- [ ] Update operator text to contain numeric values and update pipeline/orchestrator calls.
- [ ] Run experiment, pipeline, diagnostic-evaluation, and orchestrator tests, then commit.

### Task 4: Feature Provenance and Quality Release Gate

**Files:**
- Create: `cfdc/features/quality.py`
- Modify: `cfdc/features/__init__.py`
- Modify: `cfdc/features/dispatcher.py`
- Modify: `cfdc/models/schemas.py`
- Modify: `cfdc/controllers/synthesis.py`
- Modify: `cfdc/pipeline.py`
- Modify: `cfdc/runtime/orchestrator.py`
- Test: `tests/test_feature_quality_gate.py`

**Interfaces:**
- Produces `FeatureQualityPolicy`, `FeatureQualityIssue`, `FeatureQualityDecision`.
- Produces `evaluate_feature_quality(classification, features, workflow_mode, policy=None)`.

- [ ] Write tests rejecting confidence zero, overly wide bounds, invalid physical domains, missing real trace hash, and synthetic provenance in real mode; test repeat-experiment flags separately from refusal flags.
- [ ] Verify all new cases fail because current validation checks only IDs.
- [ ] Add artifact provenance fields and trace SHA-256 calculation for extracted real/synthetic results.
- [ ] Implement feature-specific domains and default quality thresholds.
- [ ] Gate both pipeline and route controller synthesis, mapping repeat to `experiments_required` and refusal to `rejected`.
- [ ] Use conservative confidence bounds in synthesis where a gain or time scale is inverted.
- [ ] Run focused, feature, controller, pipeline, and route tests, then commit.

### Task 5: Generic Paper Algorithm 1

**Files:**
- Create: `cfdc/online/algorithm1.py`
- Modify: `cfdc/online/__init__.py`
- Modify: `cfdc/models/schemas.py`
- Modify: `cfdc/sim/cartpole.py`
- Modify: `cfdc/sim/vtol.py`
- Test: `tests/test_algorithm1.py`
- Test: `tests/test_integration_benchmarks.py`

**Interfaces:**
- Produces `OnlineRefinementPolicy`, `Algorithm1State`, `Algorithm1Observation`.
- Produces `initialize_algorithm1`, `propose_algorithm1_candidate`, and `evaluate_algorithm1_probe`.

- [ ] Write state-machine tests for 1.05 multiplication, declared tunable gains only, dwell refusal, safe acceptance, first soft violation confirmation, second soft violation rollback/freeze, hard immediate rollback, iteration limit, and target completion.
- [ ] Verify focused tests fail for missing API.
- [ ] Implement the pure state machine without plant-specific code.
- [ ] Wrap CartPole and VTOL boundary trials as executors feeding Algorithm1 observations; remove new-route dependence on hand-authored candidate lists while retaining archived baseline helpers.
- [ ] Assert candidate histories use multiplicative 5-10 percent steps and rollback reports contain the restored gains.
- [ ] Run online, CartPole, VTOL, benchmark, and demo tests, then commit.

### Task 6: Continuous FLL, RLS, and Hover Tracking

**Files:**
- Create: `cfdc/online/tracking.py`
- Modify: `cfdc/online/__init__.py`
- Modify: `cfdc/models/schemas.py`
- Modify: `cfdc/runtime/orchestrator.py`
- Modify: `cfdc/sim/vtol.py`
- Test: `tests/test_continuous_tracking.py`

**Interfaces:**
- Produces `TrackingSchedulerState`, `FLLTrackerState`, `ScalarRLSTrackerState`, `HoverAverageTrackerState`, and `TrackingObservation`.
- Produces scheduler eligibility, FLL window update, scalar RLS update, hover-average update, and controller adaptation functions.

- [ ] Write tests for scheduler pause/resume, FLL convergence on a drifting sinusoid, rejection on weak lock, RLS convergence to a known scalar gain, degenerate regressor handling, hover time-constant update, 5 percent controller-update threshold, and 10 percent NMP-retune request.
- [ ] Verify focused tests fail for missing tracker APIs.
- [ ] Implement pure serializable tracker states and deterministic update functions.
- [ ] Add an orchestrator input/output path for tracking observations and persistent tracking states.
- [ ] Exercise VTOL variation through the same hover/RLS adaptation functions rather than direct feature replacement.
- [ ] Run tracking, online, VTOL, orchestrator, and variation tests, then commit.

### Task 7: Multi-Turn Diagnostic Session

**Files:**
- Create: `cfdc/diagnosis/session.py`
- Modify: `cfdc/diagnosis/__init__.py`
- Modify: `cfdc/models/schemas.py`
- Modify: `cfdc/runtime/orchestrator.py`
- Test: `tests/test_diagnostic_sessions.py`

**Interfaces:**
- Produces `DiagnosticTurn`, `DiagnosticSessionState`, `start_diagnostic_session`, and `continue_diagnostic_session`.

- [ ] Write tests for initial clarification, question/answer validation, accumulated evidence, JSON round-trip, maximum turns, fail-closed incomplete state, completion into CandidateRouteIR, and real-mode stop at experiments-required.
- [ ] Verify tests fail for missing session API.
- [ ] Implement serializable session state and description accumulation without storing adapter secrets.
- [ ] Re-run shared safety rules after every adapter response and compile a route only when all eight fields are resolved.
- [ ] Add optional session input/output fields to the orchestrator without changing stateless calls.
- [ ] Run diagnosis, LLM-adapter, pipeline, route, and session tests, then commit.

### Task 8: CLI Session and Workflow Controls

**Files:**
- Modify: `main.py`
- Modify: `README.md`
- Modify: `README_CN.md`
- Test: `tests/test_main_cli.py`

**Interfaces:**
- Adds `--workflow-mode`, `--diagnostic-session-input`, and `--diagnostic-session-output`.

- [ ] Write CLI tests for real/simulation resolution, invalid LLM/simulation combination, session JSON input/output, and absence of synthetic data in real reports.
- [ ] Verify tests fail because flags do not exist.
- [ ] Implement atomic session JSON writes through a temporary sibling file and rename.
- [ ] Document real versus simulation examples and evidence boundaries.
- [ ] Run CLI and documentation-related tests, then commit.

### Task 9: End-to-End Completion Audit

**Files:**
- Modify only files required by failures discovered in the audit.
- Test: full `tests/` suite.

**Interfaces:**
- Verifies every numbered acceptance criterion in the approved design specification.

- [ ] Run targeted commands for workflow modes, compiler gaps, experiment parameterization, feature quality, Algorithm 1, tracking, and sessions.
- [ ] Run `pytest -q` and record the exact pass/fail count.
- [ ] Run `python main.py --validate-demo`, `--benchmark`, `--feature-ablation`, and `--diagnostic-eval`; inspect semantic outputs rather than exit codes alone.
- [ ] Run a real-mode route with a diagnostic adapter and no experiment data; verify no synthetic trace/feature is present.
- [ ] Run a simulation-mode CartPole and VTOL route without experiment data; verify synthetic provenance is explicit.
- [ ] Search for old unconditional fixture fallbacks and empty tracking-update placeholders.
- [ ] Update README status checklists to match verified evidence.
- [ ] Commit final audit fixes only after all checks pass.
