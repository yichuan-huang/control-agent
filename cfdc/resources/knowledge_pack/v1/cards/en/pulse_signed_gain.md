# Pulse-based signed input gain and sign ambiguity

## Definition

A short bounded pulse can estimate the signed influence of an input on velocity, acceleration, or another local response when a sustained step would cause excessive drift. The sign is part of the feature and must follow declared channel conventions.

## Applicability

Use pulse probing for integrating, drifting, oscillatory, or bounded-motion systems when the pulse duration is long enough to be measurable but short enough to remain inside state and actuator limits.

## Required evidence

Require the actual applied waveform, input and output signs and units, pre-pulse baseline, timestamps, state limits, actuator limits, post-pulse observation, and at least one safe repeat or opposite-polarity check when allowed.

## Extraction method

Compute the relevant change in slope, velocity, acceleration, or impulse response using the registered feature extractor for the selected profile. Propagate uncertainty from baseline and sampling. Report gain sign and magnitude separately.

## Data-quality checks

Check amplitude and slew limits, clipping, dead zone, pulse timing, initial motion, disturbance, sensor differentiation noise, post-pulse boundary approach, and consistency of positive and negative probes.

## Controller implications

The signed gain can set feedback polarity and scale a registered PD or local model. Ambiguous sign is a hard stop because the wrong sign can create positive feedback. Gain updates must stay bounded and rollback-capable.

## Critic checks

Reject gains derived from commanded rather than applied input, silent sign flips, division by an unresolved response, or averaging opposite signs.

## Cannot prove

This card cannot establish a global input gain, authorize a pulse on hardware, or infer sign from an object name or retrieved example.

## Source references

- `caltech-feedback-systems-2008`
- `repo-knowledge-registry-v1`
- `repo-mechanism-cards-v0.4`
