# Control Agent

[中文说明](README_CN.md)

This repository is an independent implementation of the Core-Feature-Driven Control (CFDC) workflow. It provides software-model simulation only: it does not command physical hardware or certify hardware safety.

## Main workflow

```text
1 Problem Description
→ 2 AI Measurement Plan
→ 3 Measurement Response
→ 4 System Classification
→ 5 Initial Controller
→ 6 Effect Validation and Tuning
```

The generic Web and CLI flow requires an OpenAI-compatible LLM provider. Start with one natural-language problem description; an optional description supplement may add facts from an existing record or manual. The AI then presents the fixed eight-item diagnostic checklist and measurement plan. Description supplements and measurement responses are separately limited to eight rounds. Unknown facts remain gaps and are never filled with invented defaults.

Measurement requests are `existing_records_only`: they tell you what existing record or manual passage to find and how to report it. They never prescribe physical-hardware amplitudes, durations, actions, or commands. The same measurement-response path later collects the numeric facts required by the selected Profile; there is no separate shortcut around the evidence gate.

Formal classification and closed-catalog Profile selection remain absent until all eight diagnostic fields have verified evidence. Classification selects a model family but never supplies plant numbers. Every coefficient, matrix element, physical parameter, operating range, and experiment condition must come from the problem statement, submitted record/manual facts, or a reproducible deterministic derivation. Once those inputs are sufficient, the backend deterministically compiles the model and creates an initial controller candidate.

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

Open `http://127.0.0.1:7860`. The generic Web workflow has one domain input, **Control Problem Description**, plus the required provider Base URL, Model, and API Key. There is no optional no-LLM mode. Its six progress stages are exactly Problem Description, AI Measurement Plan, Measurement Response, System Classification, Initial Controller, and Effect Validation and Tuning.

Once the eight diagnostic fields and selected-Profile facts are complete:

1. Confirm that the declared input/output ranges are boundaries for software simulation only, not hardware-safety certification.
2. The backend validates the Profile facts and deterministically compiles the plant model.
3. The Controller tab presents the initial unvalidated controller candidate.
4. Tuning & Adaptation receives that exact compiled model and controller and runs the first software trial.
5. The output curve shows the reference, initial-controller output, latest executed output when different, and lower/upper output bounds for every displayed channel.
6. Stability is mapped only from the deterministic `StabilityDecision`: stable, unstable, or inconclusive. A rolled-back latest trial stays visible as unaccepted evidence and never becomes the current safe controller.

The complete-specification path does not ask for the same model information again or require a second model-confirmation step.

There is no case selector, separate simulation laboratory, fixed MIMO demo, or continuous auto-tuning button in the main UI.

Base URL, Model, and API Key are required for the generic guided flow and are read directly from the current provider inputs. API keys are never stored in Gradio state, diagnostic/model/simulation sessions, audit JSON, logs, hashes, or exports.

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

1. Clone the repository and enter the project directory:

```bash
git clone https://github.com/yichuan-huang/control-agent.git
cd control-agent
```

2. Create and activate a Conda environment:

```bash
conda create -n control-agent python=3.11
conda activate control-agent
```

3. Install the project and test dependencies:

```bash
python -m pip install -e '.[test]'
```

4. Run the test suite and compile-check the source code:

```bash
pytest -q
python -m compileall -q cfdc tests
```

Use any OpenAI-compatible provider:

```bash
export CFDC_LLM_BASE_URL="https://your-provider.example"
export CFDC_LLM_MODEL="your-provider-model"
export CFDC_LLM_API_KEY="..."

python main.py --use-llm \
  --description "A spring-mass process oscillates after a force pulse." \
  --diagnostic-session-output session-v4.json
```

The same configuration may be supplied on the command line:

```bash
python main.py --use-llm \
  --llm-base-url "https://api.deepseek.com" \
  --llm-model "deepseek-v4-pro" \
  --llm-api-key "$DEEPSEEK_API_KEY" \
  --description "A heater changes a measured chamber temperature." \
  --diagnostic-session-output session-v4.json
```

The resume commands below assume the `CFDC_LLM_BASE_URL`, `CFDC_LLM_MODEL`, and
`CFDC_LLM_API_KEY` variables exported above are still set. Resume the saved v4
session with either inline text or one UTF-8 response file:

```bash
python main.py --use-llm \
  --diagnostic-session-input session-v4.json \
  --diagnostic-session-output session-v4-next.json \
  --measurement-response "Paste existing-record or manual findings here."

python main.py --use-llm \
  --diagnostic-session-input session-v4.json \
  --diagnostic-session-output session-v4-next.json \
  --measurement-response-file measurement-response.txt
```

`--measurement-response` and `--measurement-response-file` are mutually exclusive. A response requires `--diagnostic-session-input`; use `--diagnostic-description` separately when adding a description supplement. When the selected-Profile response supplies complete numeric simulation ranges, also pass `--confirm-simulation-bounds` to confirm their software-only meaning.

Persisted guided sessions use schema version `4.0`. Version 3 payloads are explicitly rejected rather than migrated, and older saved sessions are incompatible with this workflow; start a new v4 session from the original description.

## Evidence boundary

The application never sends hardware commands. Confirmation of input/output bounds authorizes only a bounded software simulation; it is not permission to actuate hardware and is not hardware-safety certification. An accepted result means only that the current confirmed software model satisfied the deterministic stability checks. An `example_hypothesis` remains a repeatable demonstration assumption. A `local_linear_hypothesis` is valid only inside its confirmed range. Neither is evidence of the real plant’s stability, robustness, performance, or safety.

## License

Copyright (C) 2026 Yichuan Huang

Licensed under the [GNU Affero General Public License v3.0 only](LICENSE), identified as `AGPL-3.0-only`. Commercial use is permitted subject to the license. If modified network-accessible versions are offered to users, the corresponding source obligations in the license apply.

Repository: https://github.com/yichuan-huang/control-agent
