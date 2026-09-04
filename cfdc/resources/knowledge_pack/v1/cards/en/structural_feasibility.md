# Relative degree, controllability, observability, and sensing adequacy

## Definition

Relative degree describes how many dynamic differentiations separate an input from a measured output in a local model. Controllability and observability are model-dependent properties of a declared state-space realization. They are not interchangeable with the practical questions of whether the available actuator influences the target or whether the available sensors reveal the state needed by a controller.

## Applicability

Use these concepts only after defining inputs, outputs, states, operating point, and model assumptions. For an unknown plant, first state the weaker experimental claims about actuation and sensing instead of asserting matrix properties.

## Required evidence

For relative degree, require an identified local input-output model or derivative structure supported by data. For controllability or observability, require validated state matrices and the state/output definitions. For practical adequacy, require bounded excitation and measurable response above uncertainty.

## Extraction method

Evaluate relative degree from a validated model representation. Evaluate controllability and observability using the corresponding rank or conditioning tests, while reporting numerical tolerance and model validity. Keep empirical influence and distinguishability as separate evidence when no state-space model exists.

## Data-quality checks

Check units and scaling, sampling rate, excitation richness, sensor bandwidth, collinearity, numerical conditioning, hidden constraints, and whether the proposed state is actually measured or estimated.

## Controller implications

High relative degree, weak actuation, or poor observability can make an otherwise plausible controller unsafe or unsupported. CFDC may request more evidence or stop at a capability gap; RAG cannot create observers, actuators, or controller topology.

## Critic checks

Reject rank claims without matrices, exact-rank conclusions without tolerance, and claims that a response in one output proves full-state controllability or observability.

## Cannot prove

This card cannot establish controllability or observability from prose, prove a minimal realization, or authorize an observer-based controller.

## Source references

- `caltech-feedback-systems-2008`
- `eth-control-systems-2017`
- `repo-knowledge-registry-v1`
