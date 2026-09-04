# FOPDT step response and extraction of K, tau, and theta

## Definition

A first-order-plus-dead-time approximation represents a locally stable self-regulating response using a signed steady gain K, a dominant time constant tau, and a dead time theta. It is a compact control-oriented approximation, not a claim that the physical plant has exactly one state.

## Applicability

Use it only when a bounded step produces a repeatable approach toward a new steady value without material inverse response, instability, strong oscillation, or coupling that invalidates a scalar fit.

## Required evidence

Require pre-step and post-step steady regions, the applied input change, synchronized sampling, enough duration to observe the dominant settling behavior, known units, operating region, and repeated trials.

## Extraction method

Estimate K from steady output change divided by signed input change. Estimate theta from a documented onset or fitted delay. Estimate tau from the delayed response time to the first-order 63-percent level or from a constrained fit. Report the method and intervals for all three quantities.

## Data-quality checks

Check input delivery, baseline drift, final steady-state evidence, filtering, sampling resolution relative to theta, saturation, disturbances, residual structure, and consistency across step amplitudes and directions.

## Controller implications

Accepted K and tau may support the registered detuned PI profile; material theta selects its delay-aware variant. Tuning remains bounded by Registry preconditions and deterministic closed-loop qualification.

## Critic checks

Reject division by a negligible input step, unsigned gain, forced steady state, delay below resolution, and fits that hide inverse response or strong coupling.

## Cannot prove

This card cannot establish global linearity, guarantee a PI design, or justify copying example parameter values into the current plant.

## Source references

- `ntnu-simc-2003`
- `repo-knowledge-registry-v1`
- `repo-mechanism-cards-v0.4`
