# Controller qualification, bounded changes, rollback, and authority

## Definition

Controller qualification is a deterministic evaluation of an implemented controller candidate against declared evidence, constraints, stability checks, and performance requirements. Advisory knowledge can explain why a registered method may be relevant, but cannot select, compile, qualify, execute, or approve it.

## Applicability

Apply this boundary to detuned PI, damping PD, saturated PD, cascaded control, NMP outer-loop limits, delay-aware PI, MIMO pairing or decoupling, and every gain change supported by the Registry.

## Required evidence

Require an accepted plant/model artifact, compatible Profile, registered controller template, explicit gains and bounds, actuator amplitude and slew limits, simulation configuration, qualification report, immutable ControllerFreeze, and independent evaluation where required.

## Extraction method

There is no LLM extraction route for authorization. The Kernel validates typed artifacts, executes registered numerical code, records revisions, and compares results with fixed gates. A proposed gain change must remain inside the existing topology and declared bounds and must preserve a recoverable prior freeze.

## Data-quality checks

Check evidence identity and revision, units, finite trajectories, amplitude and slew limits, saturation, sign ambiguity, uncertainty, missing trials, unsupported topology, and whether the evaluation is independent of tuning.

## Controller implications

Failed or inconclusive qualification remains failed or inconclusive. Roll back when bounded adaptation degrades a protected criterion. Software simulation qualification is not physical-hardware authorization, and the WebUI must never command hardware.

## Critic checks

Block unsafe zero cancellation, evidence-free controller selection, invented gains, topology changes, hidden saturation, stale evidence, and any claim that RAG or an LLM overrules the Kernel.

## Cannot prove

This card cannot authorize hardware, convert a simulation result into field approval, create a missing capability, or change final success and failure verdicts.

## Source references

- `repo-knowledge-registry-v1`
- `repo-kernel-boundaries-v0.3.2`
- `ntnu-simc-2003`
- `caltech-feedback-systems-2008`
