# Control Agent

[中文说明](README_CN.md)

This repository is an independent implementation of the Core-Feature-Driven Control (CFDC) workflow. It provides software-model simulation only: it does not command physical hardware or certify hardware safety.

## Main workflow

```text
plain-language control problem
→ structural diagnosis and five-class classification
→ eight-field and supplemental numeric specifications
→ deterministic plant-model compilation
→ Stage-5 unvalidated controller candidate
→ initial-controller effect-validation trial
→ stability decision
→ constrained AI gain proposal and user approval
→ stop at the first stable or terminal result
```

Classification helps select a model family, but it never supplies plant numbers. Every coefficient, matrix element, physical parameter, operating range, and experiment condition must come from the problem statement, the submitted specifications, or a reproducible deterministic derivation. Once those inputs are sufficient to compile the model, the main workflow does not collect them again.

The runtime does not look up a model by question number, case ID, or Profile. The 200 Markdown problems under `dataset/` are offline research and evaluation data only.

## Supported models

- Continuous or discrete SISO transfer functions, including explicit input delay.
- Continuous or discrete SISO/MIMO state-space models.
- Registered nonlinear `underactuated_cartpole` and `vtol_cascaded` templates.
- Local linear transfer-function or state-space hypotheses around a user-confirmed operating point and validity region.

The LLM may return strict typed data only. Arbitrary Python, MATLAB, ODE strings, imports, callbacks, URLs, module paths, and expression evaluation are rejected. A local model that leaves its confirmed validity range terminates as `inconclusive`; gain tuning cannot continue on that model.

## Web interface

Start the application:

```bash
python app.py
```

Open `http://127.0.0.1:7860`. Once the eight structural fields and supplemental numeric specifications are complete:

1. The backend validates the specifications and compiles the plant model.
2. The Controller tab presents the Stage-5 initial controller.
3. Tuning & Adaptation automatically receives that compiled model and controller.
4. Run the initial-controller effect validation.
5. A stable trial completes Effect Validation with a green check. Otherwise, request one whitelisted AI gain update, review the difference, and approve or reject the next trial.

The complete-specification path does not ask for the same model information again or require a second model-confirmation step.

There is no case selector, separate simulation laboratory, fixed MIMO demo, or continuous auto-tuning button in the main UI.

Base URL, Model, and API Key are read directly from the current provider inputs only when an unstable result requires an AI gain request. API keys are never stored in Gradio state, model/simulation sessions, audit JSON, logs, hashes, or exports.

## Project layout

| Path | Responsibility |
| --- | --- |
| `cfdc/lab/model_contracts.py` | Strict model-question, fact, envelope, operating-range, and experiment contracts. |
| `cfdc/lab/model_discovery.py` | Revisioned and hashed model-discovery state machine. |
| `cfdc/lab/model_discovery_llm.py` | Sanitized LLM request/response validation for `need_more`, `ready`, and `rejected`. |
| `cfdc/lab/controller_compatibility.py` | Controller/model compatibility and typed deterministic replacement proposals. |
| `cfdc/lab/model_validity.py` | Runtime validity guard for local linear hypotheses. |
| `cfdc/lab/resources/` | Versioned generic model-question examples, independent of the 200-problem dataset. |
| `cfdc/web/linked_tuning_service.py` | Compiled plant model and Stage-5 controller → effect-validation simulation session. |
| `cfdc/web/model_discovery_presentation.py` | Plain-language and mathematical model card. |
| `cfdc/web/linked_tuning_ui.py` | Tuning & Adaptation effect validation, AI gain proposal, and approval UI. |
| `cfdc/sim/` | Deterministic linear, CartPole, and VTOL simulation backends. |
| `dataset/` | Raw 200-problem Markdown dataset; not imported by production code. |
| `tests/` | Contract, safety, state-machine, simulation, Web, and end-to-end tests. |

## Install and test

```bash
python -m pip install -e '.[test]'
pytest -q
python -m compileall -q cfdc tests
```

Use any OpenAI-compatible provider:

```bash
export CFDC_LLM_BASE_URL="https://your-provider.example/v1"
export CFDC_LLM_MODEL="your-provider-model"
export CFDC_LLM_API_KEY="..."

python main.py --use-llm \
  --description "A spring-mass process oscillates after a force pulse." \
  --observed-output position \
  --actuator force
```

The same configuration may be supplied on the command line:

```bash
python main.py --use-llm \
  --llm-base-url "https://api.deepseek.com/v1" \
  --llm-model "deepseek-v4-pro" \
  --llm-api-key "$DEEPSEEK_API_KEY" \
  --description "A heater changes a measured chamber temperature." \
  --observed-output temperature \
  --actuator heater
```

## Evidence boundary

An accepted result means only that the current confirmed software model satisfied the implemented stability checks. An `example_hypothesis` remains a repeatable demonstration assumption. A `local_linear_hypothesis` is valid only inside its confirmed range. Neither is evidence of the real plant’s stability, robustness, performance, or safety.

## License

Copyright (C) 2026 Yichuan Huang

Licensed under the [GNU Affero General Public License v3.0 only](LICENSE), identified as `AGPL-3.0-only`. Commercial use is permitted subject to the license. If modified network-accessible versions are offered to users, the corresponding source obligations in the license apply.

Repository: https://github.com/yichuan-huang/control-agent
