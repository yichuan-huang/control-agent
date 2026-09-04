# Open-loop stability and operating-point evidence

## Definition

Open-loop stability describes what the measured plant does near a declared operating point when feedback is absent or held fixed. A response that settles is locally stable and self-regulating; a response that remains displaced or drifts can be marginal or integrating; a response that grows away from the operating point is unstable. These labels apply only to the tested variables, configuration, and region.

## Applicability

Use this distinction before selecting an experiment or controller profile. Do not infer stability from the object name, a closed-loop trace, one bounded time window, or the absence of a visible failure.

## Required evidence

Record the feedback condition, initial operating point, bounded perturbation, input and output units, observation horizon, constraints, and whether the response settles, persists, drifts, oscillates, or diverges. An unstable physical plant normally requires protected simulation or an already qualified stabilizing layer.

## Extraction method

Compare repeated small perturbations around the same operating point. Estimate the post-transient slope and envelope rather than classifying from a single sample. Treat a slope indistinguishable from the noise floor as inconclusive unless the observation horizon is long enough for the relevant time scale.

## Data-quality checks

Check feedback was actually disabled or fixed, actuator saturation was absent, timestamps are monotonic, the baseline was stationary, and repeated trials agree. Separate drift caused by disturbances or sensor bias from plant integration.

## Controller implications

Stable self-regulating evidence may support a conservative lag profile. Marginal motion requires bounded excitation and explicit state limits. Unstable evidence makes stabilization a prerequisite to performance tuning. The Registry and Kernel still decide which implemented route is admissible.

## Critic checks

Reject claims that generalize beyond the tested region, confuse closed-loop stability with open-loop stability, or treat missing evidence as stable behavior.

## Cannot prove

This card cannot prove global stability, identify a model order, authorize an open-loop hardware experiment, or select a controller.

## Source references

- `caltech-feedback-systems-2008`
- `repo-knowledge-registry-v1`
- `repo-mechanism-cards-v0.4`
