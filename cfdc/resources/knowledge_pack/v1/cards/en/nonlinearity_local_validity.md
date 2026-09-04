# Static and dynamic nonlinearity with local validity

## Definition

A static nonlinearity maps the current input or state to an output without its own memory, as in dead zones, saturation, or a static calibration curve. A dynamic nonlinearity changes evolution through state, rate, history, or mode, as in hysteresis, friction with memory, state-dependent dynamics, and switching. A local linear approximation is valid only within the configuration and operating region supported by evidence.

## Applicability

Use this distinction when gains, time scales, signs, or modes vary with operating point or input history. Do not label every poor fit as nonlinearity before checking delay, disturbance, sensor faults, or insufficient excitation.

## Required evidence

Require repeated sweeps or perturbations across declared regions, both input directions where safe, synchronized traces, and uncertainty sufficient to distinguish variation from noise.

## Extraction method

Compare local gains and time scales across regions and directions. Static nonlinear behavior appears in repeatable instantaneous or steady mappings; dynamic nonlinear behavior appears in path, rate, or state dependence. Preserve each local estimate separately rather than averaging incompatible regions.

## Data-quality checks

Check actuator and sensor saturation, drift, thermal settling, rate dependence, hidden mode changes, initialization, and whether experiments followed the same trajectory.

## Controller implications

Local profiles may remain usable inside a qualified region with conservative limits and rollback. Severe or unsupported nonlinear behavior must stop route selection instead of being hidden inside one nominal gain.

## Critic checks

Reject global claims from one local experiment, averaged parameters across incompatible regions, and attempts to use a static correction for dynamic hysteresis without evidence.

## Cannot prove

This card cannot identify a global nonlinear model, establish a safe scheduling law, or authorize operation outside the validated region.

## Source references

- `caltech-feedback-systems-2008`
- `mit-underactuated-2024`
- `repo-mechanism-cards-v0.4`
