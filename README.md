# Control Agent

[中文说明](README_CN.md)

This repository is an independent implementation of the Core-Feature-Driven Control (CFDC) workflow. It provides software-model simulation only: it does not command physical hardware or certify hardware safety.

## Main workflow

```text
1 Problem Description and Eight-Item Checklist
→ 2 System Classification
→ 3 Core-Parameter Measurement Plan
→ 4 Parameter Response and Model Compilation
→ 5 Initial Controller
→ 6 Effect Validation and Tuning
```

The generic Web and CLI flow requires an OpenAI-compatible LLM provider. Start with one natural-language problem description. The eight checklist items are structural description checks, not a second measurement form: AI-proposed excerpts must occur verbatim in the description, and the deterministic diagnostic backend must be able to interpret them. Missing or uninterpretable items stay open, and the user continues in the original description field. Description supplements and selected-Profile responses each have their own eight-round limit; unknown values remain gaps and are never replaced with invented defaults.

When all eight items are grounded, classification and closed-catalog Profile selection happen automatically. The completed checklist collapses to an auditable 8/8 summary, and the single response box shows only the concrete parameters still required by that Profile—for example, input/output changes and units, 63% response time, significant pure delay when applicable, and software-simulation input/output bounds. Parameters already stated explicitly in the description are prefilled. A response of “unknown” keeps the corresponding gap open.

Formal classification and Profile selection remain absent until all eight description fields have grounded evidence. Classification selects a model family but never supplies plant numbers. Every coefficient, matrix element, physical parameter, operating range, and experiment condition must come from the problem statement, submitted record/manual facts, or a reproducible deterministic derivation. Once the Profile inputs are sufficient, the backend deterministically compiles the model and creates an initial controller candidate.

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
uv run python app.py
```

Open `http://127.0.0.1:7860`. The generic Web workflow has one domain input, **Control Problem Description**, plus the required provider Base URL, Model, and API Key. There is no optional no-LLM mode and the Gradio UI provides no example cases. Its six progress stages are exactly Problem Description and Eight-Item Checklist, System Classification, Core-Parameter Measurement Plan, Parameter Response and Model Compilation, Initial Controller, and Effect Validation and Tuning.

Once the eight description checks and selected-Profile facts are complete:

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

2. Install uv and sync the project environment:

```bash
uv sync
```

uv reads the pinned Python version from `.python-version`, installs a managed Python 3.12
interpreter when needed, creates `.venv`, and installs the project plus development tools.
No environment activation is required when using `uv run`.

3. Run the test suite and compile-check the source code:

```bash
uv run pytest -q
uv run python -m compileall -q cfdc tests
```

Use any OpenAI-compatible provider:

```bash
export CFDC_LLM_BASE_URL="https://your-provider.example"
export CFDC_LLM_MODEL="your-provider-model"
export CFDC_LLM_API_KEY="..."

uv run python main.py --use-llm \
  --description "A spring-mass process oscillates after a force pulse." \
  --diagnostic-session-output session-v4.json
```

The same configuration may be supplied on the command line:

```bash
uv run python main.py --use-llm \
  --llm-base-url "https://api.deepseek.com" \
  --llm-model "deepseek-v4-pro" \
  --llm-api-key "$DEEPSEEK_API_KEY" \
  --description "A heater changes a measured chamber temperature." \
  --diagnostic-session-output session-v4.json
```

The resume commands below assume the `CFDC_LLM_BASE_URL`, `CFDC_LLM_MODEL`, and
`CFDC_LLM_API_KEY` variables exported above are still set. Resume the saved v4
session with either inline text or one UTF-8 response file. Once the checklist is
complete, this response is interpreted directly as selected-Profile parameters:

```bash
uv run python main.py --use-llm \
  --diagnostic-session-input session-v4.json \
  --diagnostic-session-output session-v4-next.json \
  --measurement-response "Input change is 1 deg; steady output change is 10 mph; response time is 5 s; input range is -3 to 3 deg; output range is 45 to 80 mph." \
  --confirm-simulation-bounds

uv run python main.py --use-llm \
  --diagnostic-session-input session-v4.json \
  --diagnostic-session-output session-v4-next.json \
  --measurement-response-file measurement-response.txt
```

`--measurement-response` and `--measurement-response-file` are mutually exclusive. A response requires `--diagnostic-session-input`. If the checklist is incomplete, use `--diagnostic-description` instead to extend the problem description; do not repeat the eight checklist excerpts as a measurement response. When the selected-Profile response supplies complete numeric simulation ranges, also pass `--confirm-simulation-bounds` to confirm their software-only meaning.

Persisted guided sessions use schema version `4.0`. Grounded, measurement-verified v4 sessions remain resumable; incomplete v4 sessions rebuild the checklist from their validated description excerpts instead of asking the user to repeat them. Version 3 payloads are explicitly rejected rather than migrated, and older saved sessions are incompatible with this workflow; start a new v4 session from the original description.

## Evidence boundary

The application never sends hardware commands. Confirmation of input/output bounds authorizes only a bounded software simulation; it is not permission to actuate hardware and is not hardware-safety certification. An accepted result means only that the current confirmed software model satisfied the deterministic stability checks. An `example_hypothesis` remains a repeatable demonstration assumption. A `local_linear_hypothesis` is valid only inside its confirmed range. Neither is evidence of the real plant’s stability, robustness, performance, or safety.

## License

Copyright (C) 2026 Yichuan Huang

Licensed under the [GNU Affero General Public License v3.0 only](LICENSE), identified as `AGPL-3.0-only`. Commercial use is permitted subject to the license. If modified network-accessible versions are offered to users, the corresponding source obligations in the license apply.

Repository: https://github.com/yichuan-huang/control-agent
