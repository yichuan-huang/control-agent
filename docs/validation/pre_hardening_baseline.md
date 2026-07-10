# Pre-Hardening Baseline

Baseline commit: `61af3b1`

Environment used for the pre-hardening audit:

- Python 3.11.15
- NumPy 2.4.6
- Pydantic 2.13.4
- pytest 9.1.1

Observed baseline behavior before stable-demo hardening:

- 43 tests passed in the existing `cfdc` Conda environment.
- The seven-case benchmark reported 7/7 using feature-chain completion only.
- Cartpole, VTOL position, and VTOL boundary routes completed.
- VTOL altitude and hover returned `metric_limit` under their default scenarios.
- Cartpole gain-search termination used an `input_gain`-derived target.
- VTOL refinement changed the measured lateral coupling value and used untested candidate gains.
- VTOL boundary stopped on generic safety metrics rather than measured NMP undershoot.

This file records the pre-change state for comparison. These values are not acceptance targets.
