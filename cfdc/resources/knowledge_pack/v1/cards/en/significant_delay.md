# Significant delay and relative delay

## Definition

Dead time is an interval between an input change and the earliest defensible output response. Its control significance is relative to the dominant response time, commonly summarized by a ratio such as dead time over time constant. A delay that is small for one bandwidth can be dominant for another.

## Applicability

Use this concept for transport, computation, sensing, communication, or actuation latency. Silence in the problem description is not evidence of zero delay.

## Required evidence

Require a synchronized input-output experiment, sampling period, baseline noise, actuator onset evidence, output detection rule, dominant time-scale estimate, and uncertainty intervals for both delay and response time.

## Extraction method

For a suitable self-regulating step response, estimate the first response time using a documented threshold or fitted FOPDT model, and compare it with the fitted time constant. Report the ratio with uncertainty rather than applying an unexplained universal cutoff.

## Data-quality checks

Check clock alignment, resampling, filters, command-to-actuator latency, missing samples, and whether a slow sensor is being mistaken for plant delay. Repeat at the same operating point.

## Controller implications

Material delay requires detuning and a lower closed-loop bandwidth. The registered delay-aware lag profile may be considered only after delay evidence is accepted. Retrieved tuning rules remain advisory and cannot bypass qualification.

## Critic checks

Reject delay estimates below time resolution, ratios built from unrelated trials, and claims that use delay to justify unsupported predictors or cancellation.

## Cannot prove

This card cannot prove that delay is constant, select a numerical PI gain, or authorize a Smith predictor or another unregistered topology.

## Source references

- `ntnu-simc-2003`
- `caltech-feedback-systems-2008`
- `repo-knowledge-registry-v1`
