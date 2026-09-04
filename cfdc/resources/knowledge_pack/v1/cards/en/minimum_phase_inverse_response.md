# Minimum phase, inverse response, and unsafe zero cancellation

## Definition

A measured inverse response initially moves in the direction opposite to its eventual steady change after a signed input perturbation. For an appropriate linear local model this can indicate non-minimum-phase behavior, but inverse-looking data can also result from sensor placement, hidden feedback, disturbances, mode switching, or timing errors.

## Applicability

Use the concept when a repeatable initial response direction conflicts with the final signed gain. Do not classify a plant as non-minimum phase from overshoot, dead time, noise, or one unreplicated transient.

## Required evidence

Require synchronized signed input-output traces, a known baseline, sufficient pre-response samples, repeated trials, uncertainty on the initial excursion and final gain, and evidence that saturation or a mode switch did not create the reversal.

## Extraction method

Determine the final signed gain, then quantify the largest statistically meaningful excursion in the opposite direction before the response crosses toward its final sign. Report the observation window and uncertainty; keep the result inconclusive when the initial excursion is comparable with noise or filtering delay.

## Data-quality checks

Check signal polarity, timestamp alignment, filtering phase, actuator direction, disturbances, and repeatability. Never repair an apparent sign conflict by silently flipping a channel.

## Controller implications

Non-minimum-phase evidence limits achievable outer-loop bandwidth and favors conservative reference shaping. Exact cancellation of an unstable or uncertain zero is unsafe. Only the registered NMP profile and its deterministic qualification checks may be used.

## Critic checks

Block zero-cancellation claims without a validated model, aggressive bandwidth claims that ignore the inverse excursion, and any attempt to turn a retrieved example into current-plant evidence.

## Cannot prove

This card cannot locate a zero, prove a transfer function, establish global behavior, or authorize the NMP controller route.

## Source references

- `caltech-feedback-systems-2008`
- `repo-knowledge-registry-v1`
- `repo-mechanism-cards-v0.4`
