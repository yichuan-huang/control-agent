# Free decay, logarithmic decrement, and damping ratio

## Definition

A free-decay response of an underdamped local mode can reveal its damped frequency and decay rate after a small release or disturbance. Logarithmic decrement compares peak amplitudes separated by a known number of cycles and can be mapped to damping ratio under the standard second-order assumption.

## Applicability

Use this method only when the response contains repeatable alternating peaks from one dominant mode and the release remains inside a locally linear, safe region.

## Required evidence

Require timestamps, signed output, equilibrium baseline, peak locations and amplitudes, sampling rate, release condition, enough cycles, and uncertainty or repeat trials. The measurement bandwidth must resolve the mode.

## Extraction method

Estimate the damped period from peak spacing and compute damped frequency. Estimate logarithmic decrement across several cycles when possible to reduce quantization sensitivity, then infer damping ratio and natural frequency under the declared second-order model. Preserve the raw peaks and formula inputs.

## Data-quality checks

Check peak polarity, baseline removal, quantization, clipping, multiple modes, external forcing, time jitter, too few cycles, changing frequency, and noise-driven peak selection.

## Controller implications

Accepted frequency and damping evidence may support the registered oscillator or damping-PD route. High-frequency unmodeled modes require bandwidth limits; retrieved formulas cannot bypass the feature-quality gate.

## Critic checks

Reject damping estimates from monotone data, absolute-valued peaks without sign logic, one noisy peak pair, or a second-order interpretation when several comparable modes are visible.

## Cannot prove

This card cannot prove a unique global mode, structural damping physics, or hardware-safe excitation amplitude.

## Source references

- `umich-ctms-pendulum`
- `caltech-feedback-systems-2008`
- `repo-mechanism-cards-v0.4`
