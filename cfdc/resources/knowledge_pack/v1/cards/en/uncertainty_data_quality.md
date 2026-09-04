# Uncertainty magnitude, repeatability, and data quality

## Definition

Uncertainty describes what the accepted evidence does not determine exactly. It may arise from noise, finite sampling, unmeasured disturbances, model mismatch, parameter variation, operating-region changes, or limited experiment duration. A point estimate without an uncertainty statement is not automatically decision-ready.

## Applicability

Use uncertainty whenever a feature, classification clue, model parameter, or performance metric is derived from data. Distinguish measurement uncertainty, repeatability variation, and structural model uncertainty.

## Required evidence

Retain raw trace provenance, units, sampling metadata, trial identity, region, preprocessing, estimator settings, confidence or interval information, and rejection reasons. Multiple trials should remain separate until their compatibility is established.

## Extraction method

Report intervals or bounded ranges using a method appropriate to the estimator and data volume. Compare variation with the decision boundary that would change the route or controller. Mark the outcome inconclusive when plausible values cross that boundary.

## Data-quality checks

Check missing or duplicated timestamps, non-finite values, inadequate duration, poor excitation, saturation, baseline drift, inconsistent units, outliers, sensor resolution, and disagreement between trials.

## Controller implications

Larger uncertainty requires detuning, narrower validity claims, more evidence, or a blocked decision. Controller qualification must evaluate bounded uncertainty through deterministic checks rather than accepting verbal confidence.

## Critic checks

Reject false precision, unexplained removal of trials, mixing of plants or regions, and conclusions whose uncertainty crosses a safety or compatibility boundary.

## Cannot prove

This card cannot choose a universal confidence level, turn low-quality data into evidence, or replace deterministic validation.

## Source references

- `caltech-feedback-systems-2008`
- `repo-knowledge-registry-v1`
- `repo-kernel-boundaries-v0.3.2`
