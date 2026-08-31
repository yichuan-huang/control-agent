# Control Agent

[中文说明](README_CN.md)

Control Agent is an independent implementation of the Core-Feature-Driven Control (CFDC) workflow. Release `v0.3.0` centers the project on an auditable Python Kernel with a guided WebUI, an expert JSON interface, deterministic software experiments, physical-experiment handoff, and a compatible CLI. It does not command physical hardware or certify hardware safety.

## Quick start

You can use a local model through Ollama or a hosted service such as DeepSeek API or OpenAI API. Choose the provider and model that suit your needs; Ollama is not required. Models interpret natural-language replies, while the Kernel decides routes, experiments, controllers, numerical evaluation, and final claims.

1. With Git and `uv` installed, download the project, install its dependencies, and check the Python files:

```bash
git clone https://github.com/yichuan-huang/control-agent.git
cd control-agent
uv sync
uv run python -m compileall -q cfdc tests main.py app.py
```

`uv` reads the Python version from `.python-version` and manages `.venv`. Commands using `uv run` do not require manual environment activation.

2. Start the WebUI:

```bash
uv run python app.py
```

3. Open `http://127.0.0.1:7860`. For natural-language replies, fill in Base URL, Model, and API Key using your chosen provider from the table below. Choose a built-in case such as “01 | DC motor speed” in the Guided Workbench.

4. Disable local RAG unless an index has already been built. Create the task, confirm its boundaries, and submit the requested structural diagnosis. A built-in software case then advances through protocol compilation, public evidence, features, controller synthesis, qualification, freeze, and independent evaluation until it needs a user decision or reaches a terminal state.

Start with a built-in software case. A custom object does not automatically receive a simulation model. Physical or externally operated experiments are never run directly by the page; they continue through an operator bundle, operator confirmation, and protocol-bound data upload.

## Choose a model provider

Configure one provider. The model must support OpenAI-compatible Chat Completions and JSON output (`response_format: {"type": "json_object"}`), including the request parameters used by the application. Compatibility and model access depend on your provider; a model name alone does not guarantee support.

| Provider | Base URL | Model | API Key |
| --- | --- | --- | --- |
| Ollama (local, optional) | `http://127.0.0.1:11434/v1` | The exact model name from `ollama list` | `ollama` for the default local service |
| DeepSeek API | `https://api.deepseek.com` | For example, `deepseek-v4-pro` | Your DeepSeek API key |
| OpenAI API | `https://api.openai.com/v1` | A compatible Chat Completions model available to your API account | Your OpenAI API key |

Provider documentation: [Ollama compatibility](https://docs.ollama.com/api/openai-compatibility), [DeepSeek configuration](https://api-docs.deepseek.com/), and [OpenAI Chat Completions](https://developers.openai.com/api/reference/resources/chat). Hosted services use your account's access and billing; no hosted API calls are needed merely to install the project.

If you choose Ollama, install it and start its local service. The desktop application may already have started it; otherwise run `ollama serve` in another terminal. Replace `your-model` below with the model you choose, then use that same name in the WebUI:

```bash
ollama pull your-model
ollama list
```

If you choose DeepSeek or OpenAI, skip the Ollama steps and enter your provider's settings directly. Keep real API keys out of source files, screenshots, and shared reports. The Kernel CLI section below explains environment variables and command-line configuration.

## Kernel workflow

The WebUI is dedicated to the current CFDC Kernel and follows its nine-stage state machine:

```text
1 Task -> 2 Diagnosis -> 3 Evidence -> 4 Route / Features
-> 5 Controller -> 6 Freeze -> 7 Evaluation
-> 8 Tuning / Confirmation -> 9 Result
```

The Kernel uses a revisioned `TaskContract`, append-only events, deterministic action IDs, stale-revision checks, and typed public artifacts. Generated code is never executed. Providers may return typed replies and public JSON/CSV evidence; route resolution, controller IR validation, freeze bindings, evaluation, and bounded tuning remain under deterministic Kernel contracts.

The registered software task types are:

- `local_setpoint_hold`
- `transition_then_hold`
- `disturbance_recovery_to_hold`

Other objectives fail closed. Local RAG is optional and, when enabled, is pinned to one validated index snapshot for the session.

The runtime defines four role boundaries: Diagnosis, Modeling, Controller, and Critic. The current Web natural-language path calls Diagnosis to extract the eight diagnostic dimensions, Modeling to extract allow-listed parameter facts, and Critic to review their normalized candidate with at most one correction. The Controller role remains available for constrained explanations and proposal interfaces; the guided automatic path uses deterministic controller synthesis. The Python Kernel is the only authority for state transitions, numerical work, route selection, safety gates, and claims. If an Agent call fails, that user reply is not committed to business state and the page returns an explicit error; previously recorded Kernel artifacts are not replaced by model output.

RAG is an optional local reference layer. An enabled session pins one index snapshot after validating its schema, Registry fingerprint, and file checksums. The current Web `user_reply` extraction deliberately receives no retrieved snippets so reference material cannot be mistaken for user facts. Retrieval remains available to other explicit role operations and extension entry points. “RAG enabled” therefore means that a validated snapshot is loaded and pinned, not that every Agent call performs retrieval.

## Core capabilities

The Kernel provides the following capabilities through versioned contracts, so experiments, evidence, controller decisions, and results can be inspected and validated.

- `cfdc-protocol/v1` compiles bounded SISO, repeated time-series, staircase, Class IV frequency/amplitude/release, unstable-balance, 2x2 MIMO, and multi-stage protocols. A Provider run recompiles and verifies every binding and fingerprint before execution.
- Operator handoff writes a card, precheck list, JSON schema, repeat CSV templates, and ZIP. CSV/JSON uploads pass authorization, format, session/protocol, repeat-count, timebase, waveform, safety-limit, and signal-quality gates. Rejected attempts append a receipt without consuming an accepted experiment.
- `cfdc-features/v1` derives source-bound intervals and bounded parameter domains for SISO adjacent structures, delay/NMP/integrating/second-order behavior, Step-B nonlinearity, Class IV behavior, local unstable balance, and 2x2 static/dynamic coupling. Missing evidence produces a named feature gap.
- The packaged route registry exposes 20 executable controller contracts plus explicit capability-gap routes. Controller proposals are restricted `ControllerIR`; deterministic synthesis and `cfdc-qualification/v1` return `offline_qualified`, `diagnostic_trial_only`, or `not_qualified`.
- Identification and evaluation Providers use separate immutable bindings. The independent judge evaluates stability first, then task-specific performance, perturbed repeats, and a 95% Wilson lower bound. Only stable performance gaps may enter bounded tuning; every accepted candidate receives a new freeze and must pass fresh confirmation.
- `cfdc-session/v2.0` preserves revision checks, idempotent actions, stale-revision rejection, immutable artifact histories, and an append-only event chain.

## Development checks and optional RAG

From the project directory, run the automated tests and Python checks:

```bash
uv sync
uv run pytest -q
uv run python -m compileall -q cfdc tests main.py app.py
```

`uv` reads the pinned Python version from `.python-version`, creates `.venv`, and installs the project and development tools. No environment activation is needed when commands use `uv run`.

To build and inspect a local RAG index, place Markdown or PDF references under `references`. The index also includes the versioned built-in Registry knowledge:

```bash
uv sync --extra rag
uv run python -m cfdc.rag index --source-dir ./references --index-dir ./rag-index
uv run python -m cfdc.rag inspect --index-dir ./rag-index
```

## Web interface

Start the application and open `http://127.0.0.1:7860`:

```bash
uv run python app.py
```

The Guided Workbench creates Kernel tasks from an explicit structured form. Every task requires a description, at least one measured output, at least one control input, finite input lower and upper bounds, and a positive `state_stop`. Output bounds are optional but must be supplied as a pair. `transition_then_hold` also requires an initial region and target region. `disturbance_recovery_to_hold` also requires a disturbance event, recovery start condition, and hold region. The form also accepts engineering units, performance thresholds, experiment budgets, timing preferences, initial values, and intermediate targets.

At each state the workbench presents one primary next action: confirm the task, answer a diagnostic question, select an experiment Provider, download an operator bundle, record the operator report, upload data, run isolated evaluation, accept bounded tuning, or confirm the result. Protocol waveforms, accepted public traces, feature intervals, qualification checks, reference/output/input/error plots, repeat confidence, and the nine-stage audit timeline are shown from Kernel artifacts.

The Expert Contracts tab accepts a full `TaskContract`, loads an existing Kernel session, submits typed action JSON, and validates a downloaded artifact fingerprint. It can export the protocol, operator bundle, upload receipt, feature artifact, Controller IR, qualification, freeze, evaluation, feedback, confirmation, final result, complete session audit, or the full result ZIP.

Web Agent orchestration is always `multi`. The page has no workflow-version selector and no Agent-mode selector. Provider configuration, the RAG switch, and the local index directory remain available. Advanced JSON remains available because it is the Kernel's typed public evidence and action interface.

The reply selector has the fixed values `natural_language` and `json`. The current Kernel input contract decides whether both can be selected, JSON is mandatory, or the selector is hidden for an action that takes no input. Confirmation, continue, replay, and terminal actions therefore cannot leave an invalid Radio value in Gradio state.

The WebUI does not load or run legacy sessions, does not expose the `single` baseline, and does not fall back to a compatibility workflow. A missing, unknown, or non-Kernel Web state is rejected with an explicit error. Use the CLI procedure below for legacy sessions.

Provider credentials are read from the current form values. API keys are not stored in Gradio state, Kernel sessions, audit JSON, logs, hashes, or exports.

The built-in selector contains 18 public cases:

- Five engineering training cases: `dc_motor_speed_v1`, `tclab_single_heater_v1`, `dc_motor_position_v1`, `quadruple_tank_nmp_v1`, and `tclab_dual_heater_v1`.
- Six transition variants: single and staged transition-hold versions of the motor-speed, single-heater, and quadruple-tank cases.
- Seven audit cases: `audit_class_i_level`, `audit_class_ii_thermal`, `audit_class_ii_oscillator`, `audit_class_iii_motion`, `audit_class_iv_nmp`, `audit_class_iv_high_order`, and `audit_class_v_mimo`.

## Kernel CLI

The CLI remains compatible with both workflows. Select the Kernel explicitly for a new custom task. The command stops at the next user or evidence boundary and prints the session ID and current input contract:

```bash
uv run python main.py --workflow-version kernel \
  --kernel-session-dir ./output/kernel-sessions \
  --description "A heater holds chamber temperature." \
  --observed-output temperature --actuator voltage \
  --safety-bound input_min=-1 --safety-bound input_max=1 \
  --safety-bound state_stop=3
```

Use `--kernel-session SESSION_ID`, a unique `--kernel-action`, and the typed option requested by `pending_actions` to continue. `--kernel-auto` executes deterministic steps until user input, external data, confirmation, a capability gap, or a terminal result is reached.

A registered engineering case can run through the software Provider chain in one command once its public diagnosis is supplied:

```bash
DIAGNOSIS_JSON='{
  "open_loop_stability":{"status":"known","assessment":"stable","evidence":"bounded public test","confidence":0.95},
  "nonminimum_phase":{"status":"known","assessment":"minimum_phase","evidence":"bounded public test","confidence":0.95},
  "significant_delay":{"status":"known","assessment":"not_significant","evidence":"bounded public test","confidence":0.95},
  "relative_degree":{"status":"known","assessment":"low","evidence":"bounded public test","confidence":0.95},
  "sensing_actuation_adequacy":{"status":"known","assessment":"adequate","evidence":"operator record","confidence":0.95},
  "nonlinearity_strength":{"status":"known","assessment":"weak","evidence":"bounded public test","confidence":0.95},
  "coupling_underactuation":{"status":"known","assessment":"siso","evidence":"declared interface","confidence":0.95},
  "uncertainty_variation":{"status":"known","assessment":"small","evidence":"repeated public tests","confidence":0.95}
}'

uv run python main.py --workflow-version kernel \
  --kernel-case dc_motor_speed_v1 \
  --kernel-action motor-run-001 \
  --confirm-kernel-budget \
  --kernel-answer "$DIAGNOSIS_JSON" \
  --kernel-advance --kernel-auto \
  --kernel-result-dir ./output/results \
  --kernel-export-bundle
```

For a physical or externally operated experiment, bind a public Provider contract and compile the handoff after diagnosis and route resolution:

```bash
uv run python main.py --workflow-version kernel --kernel-session SESSION_ID \
  --kernel-action physical-001 \
  --kernel-provider physical-provider.json \
  --kernel-compile-protocol --kernel-prepare-operator-handoff \
  --kernel-result-dir ./output/results

uv run python main.py --workflow-version kernel --kernel-session SESSION_ID \
  --kernel-action physical-002 \
  --kernel-operator-report operator-report.json \
  --kernel-upload repeat-01.csv --kernel-upload repeat-02.csv \
  --kernel-upload repeat-03.csv --kernel-auto
```

If a declared stop condition fired, add `--kernel-upload-stopped-on-limit`; the upload is recorded as a failed safety gate and is never repaired or counted as accepted evidence.

Provider settings for natural-language agent work can be supplied through `CFDC_LLM_BASE_URL`, `CFDC_LLM_MODEL`, and `CFDC_LLM_API_KEY`, or the corresponding `--llm-*` options. They affect role-scoped proposals and explanations only; the Kernel still decides routes, numerical results, and authorization.

The following example uses DeepSeek. Set `DEEPSEEK_API_KEY` in your local environment first. To use another provider, substitute its Base URL, model, and key from the table above:

```bash
uv run python main.py --use-llm \
  --workflow-version kernel \
  --llm-base-url "https://api.deepseek.com" \
  --llm-model "deepseek-v4-pro" \
  --llm-api-key "$DEEPSEEK_API_KEY" \
  --description "A heater changes a measured chamber temperature." \
  --observed-output temperature --actuator voltage \
  --safety-bound input_min=-1 --safety-bound input_max=1 \
  --safety-bound state_stop=3
```

## Legacy CLI procedure

Legacy is supported only through the CLI. All commands should explicitly select the compatibility workflow, the `single` Agent baseline, and disabled RAG. Replace the example provider values and Chinese placeholder text with facts for the actual control problem.

1. Export the OpenAI-compatible provider configuration:

```bash
export CFDC_LLM_BASE_URL="https://your-provider.example/v1"
export CFDC_LLM_MODEL="your-model"
export CFDC_LLM_API_KEY="..."
```

2. Create the first legacy diagnostic session:

```bash
uv run python main.py --workflow-version legacy \
  --use-llm --agent-mode single --no-rag \
  --description "控制问题描述" \
  --diagnostic-session-output legacy-01.json
```

3. If `legacy-01.json` still requests description facts, add the missing object, sensor, actuator, or behavior information and write a new file:

```bash
uv run python main.py --workflow-version legacy \
  --use-llm --agent-mode single --no-rag \
  --diagnostic-session-input legacy-01.json \
  --diagnostic-description "补充缺少的对象、传感器或执行器信息" \
  --diagnostic-session-output legacy-02.json
```

4. When the latest JSON requests selected-Profile parameters, submit the known values, units, sources, and software-simulation ranges:

```bash
uv run python main.py --workflow-version legacy \
  --use-llm --agent-mode single --no-rag \
  --diagnostic-session-input legacy-02.json \
  --measurement-response "已知参数、单位、来源和软件仿真范围" \
  --confirm-simulation-bounds \
  --diagnostic-session-output legacy-03.json
```

Always use a new `--diagnostic-session-output` path when continuing. This preserves each revision as an audit record and avoids overwriting the input session. Inspect the latest JSON before every continuation: use `--diagnostic-description` while its status asks for missing description or diagnostic facts; use `--measurement-response` only after it asks for Profile parameters. `--measurement-response-file` may be used instead for UTF-8 text, and is mutually exclusive with `--measurement-response`.

## Supported models, capability gaps, and physical boundary

The deterministic runtime supports continuous or discrete SISO transfer functions, continuous or discrete SISO/MIMO state-space models, registered nonlinear `underactuated_cartpole` and `vtol_cascaded` templates, and local linear hypotheses around a confirmed operating point and validity region.

LLM output cannot contain executable Python, MATLAB, ODE code, imports, callbacks, module paths, URLs, or expressions. A local model that leaves its confirmed validity region terminates as `inconclusive`. An unregistered topology, missing discriminator, unresolved high-order or nonlinear behavior, insufficient signed authority, or unsupported MIMO allocation terminates with a named `capability_gap`; the registry never substitutes a neighboring controller.

The WebUI never commands hardware. Physical support ends at engineering-unit normalization, preflight, operator handoff, protocol-bound data return, frozen-controller binding, and independent adjudication. `ready_for_operator_review` is not execution authorization. Confirmation of software bounds authorizes only a bounded simulation and is not hardware-safety certification.

## License

Copyright (C) 2026 Yichuan Huang

Licensed under the [GNU Affero General Public License v3.0 only](LICENSE), identified as `AGPL-3.0-only`. Commercial use is permitted subject to the license. When modified network-accessible versions are offered, they must satisfy the corresponding source obligations.

Repository: https://github.com/yichuan-huang/control-agent
