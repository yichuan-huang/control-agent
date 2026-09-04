# Hover or balance input and local thrust evidence

## Definition

A hover or balance input is the sustained actuator command needed to offset gravity, load, pressure, or another bias at a declared equilibrium. Feedback then regulates deviations around this feedforward balance. The value is configuration- and operating-region-specific.

## Applicability

Use this concept when zero input cannot hold the target equilibrium. It applies beyond aircraft to magnetic levitation, suspension, pressure balance, and load-bearing processes.

## Required evidence

Require the target equilibrium, vehicle or plant configuration, load, actuator mapping, units, bounded search region, input and state limits, measured hold duration, and repeatability. For physical equipment, use only an already authorized procedure.

## Extraction method

Estimate the balance input from a bounded scan or accepted steady interval in which drift remains within a declared tolerance. Estimate local input gains only from perturbations around that balance, keeping the feedforward term separate from feedback gains.

## Data-quality checks

Check load changes, battery or supply variation, actuator asymmetry, ground effects or environmental disturbances, saturation margin, sensor bias, and whether the apparent equilibrium is transient.

## Controller implications

The registered hover profile uses feedforward balance plus conservative cascaded feedback. Insufficient thrust margin, uncertain sign, or unsupported coupling blocks qualification. Simulation success never grants flight or hardware authority.

## Critic checks

Reject copied nominal thrust, balance values from another configuration, brief zero-crossing mistaken for equilibrium, and claims that ignore actuator headroom.

## Cannot prove

This card cannot certify flight safety, identify full vehicle dynamics, authorize hardware operation, or establish balance outside the tested configuration.

## Source references

- `mit-underactuated-2024`
- `repo-knowledge-registry-v1`
- `repo-mechanism-cards-v0.4`
