# MIMO coupling, local gain matrices, pairing, and decoupling

## Definition

A local gain matrix records the steady signed effect of each manipulated input on each controlled output near one operating point. Coupling is material when cross-channel effects alter feasible pairings, bandwidths, constraints, or closed-loop interactions. Pairing indicators are decision aids, not proof that independent loops will work dynamically.

## Applicability

Use this method for multiple-input multiple-output systems after confirming consistent channel definitions and a safe one-input-at-a-time experiment. Do not infer severe coupling merely because several signals are correlated.

## Required evidence

Require synchronized responses of every relevant output to each bounded input perturbation, common operating point, signed units, steady or fitted local changes, uncertainty, constraints, and repeat trials.

## Extraction method

Form the 2×2 local gain matrix from signed response changes. Scale channels before comparing magnitudes. Evaluate the registered pairing indicator and inspect dynamic time-scale and inverse-response differences; a static pairing alone is insufficient when dynamics conflict.

## Data-quality checks

Check collinearity, disturbance correlation, input sequencing, recovery between probes, conditioning, sign consistency, saturation, missing cross-channel data, and operating-point drift.

## Controller implications

Evidence of weak coupling may support conservative independent loops. Material coupling may require the registered pairing or decoupling matrix with detuning. Aggressive inversion is unsafe for ill-conditioned, uncertain, delayed, or NMP channels.

## Critic checks

Reject scalar compression of a matrix experiment, unscaled magnitude comparisons, pairing based only on diagonal size, and use of an unregistered MIMO topology.

## Cannot prove

This card cannot establish global decoupling, dynamic interaction over all frequencies, or suitability of a controller without deterministic qualification.

## Source references

- `eth-control-systems-2017`
- `caltech-feedback-systems-2008`
- `repo-knowledge-registry-v1`
- `repo-mechanism-cards-v0.4`
