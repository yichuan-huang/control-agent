# Control Agent

[中文说明](README_CN.md)

Control Agent is an independent implementation of the Core-Feature-Driven Control (CFDC) workflow. Release `v0.3.4` centers the project on an auditable Python Kernel with a guided WebUI, an expert JSON interface, deterministic software experiments, physical-experiment handoff, and a compatible CLI. It does not command physical hardware or certify hardware safety.

## Quick start

You can use a local model through Ollama or a hosted service such as DeepSeek API or OpenAI API. Choose the provider and model that suit your needs; Ollama is not required. Models interpret natural-language replies, while the Kernel decides routes, experiments, controllers, numerical evaluation, and final claims.

1. Install Git, `uv`, and [Node.js with npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm). npm normally ships with Node.js. Node.js 20.19+ or 22.12+ is required. Then download the project, install its dependencies, check the Python files, verify Node and npm, and perform the first-time frontend install and build:

```bash
git clone https://github.com/yichuan-huang/control-agent.git
cd control-agent
uv sync --locked
uv run --locked python -m compileall -q -x '(^|/)(frontend|gradio_archive)(/|$)' cfdc tests main.py app.py
node --version
npm --version
npm --prefix cfdc/web/frontend ci
npm --prefix cfdc/web/frontend run build
```

`uv` reads the Python version from `.python-version` and manages `.venv`. Commands using `uv run` do not require manual environment activation.

2. After that first-time `npm ci` and build, daily use requires only this command to start the WebUI:

```bash
uv run python app.py
```

The default entry is React + FastAPI, served from the same origin at `127.0.0.1:7860`. RAG dependencies are installed by default. RAG prepares in the background while the shell and settings remain available; the first encoder download may take time. Tasks requesting RAG cannot start while it is preparing or unavailable, and the UI reports the error. Disabling RAG changes only the binding for a future task; existing task snapshots remain immutable. Hugging Face uses its standard per-user model cache.

3. Open `http://127.0.0.1:7860`. For natural-language replies, fill in Base URL, Model, and API Key using your chosen provider from the table below. Choose a built-in case such as “01 | DC motor speed” in the Guided Workbench.

4. Follow the four guided steps: task and goal, measurements and inputs, constraints and preferences, then review the summary and confirm the software trial boundary. Registered case contracts are locked; converting to a custom task preserves form values and removes the case execution binding. Default-on RAG pins the server-prepared snapshot. The workspace follows the Kernel’s current next action until a user decision or terminal state.

Before a run, `uv run --locked python main.py --doctor` prints the same non-destructive environment report used by the WebUI. It checks Python, packaged resources, the writable session directory, the public case registry, optional RAG, and (only for loopback addresses) the configured Ollama service/model. The writable-directory check creates and immediately removes one bounded probe file.

Start with a built-in software case. A custom object does not automatically receive a simulation model. Physical or externally operated experiments are never run directly by the page; they continue through an operator bundle, operator confirmation, and protocol-bound data upload.

Built-in authority is granted by a server-side case ID and a fingerprinted `RegisteredCaseBinding`; editing browser JSON cannot select another Provider. To practise the teaching loop, choose a built-in case and click “Create teaching exercise”. The generated ZIP is software-only, consumes the reserved experiment budget, and is not evidence until it is downloaded and re-uploaded through the normal audit gates.

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

Other objectives fail closed. RAG use remains optional per task and, when enabled, is pinned to one validated index snapshot after background preparation succeeds.

The runtime defines four role boundaries: Diagnosis, Modeling, Controller, and Critic. The current Web natural-language path calls Diagnosis to extract the eight diagnostic dimensions, Modeling to extract allow-listed parameter facts, and Critic to review their normalized candidate with at most one correction. The Controller role remains available for constrained explanations and proposal interfaces; the guided automatic path uses deterministic controller synthesis. The Python Kernel is the only authority for state transitions, numerical work, route selection, safety gates, and claims. If an Agent call fails, that user reply is not committed to business state and the page returns an explicit error; previously recorded Kernel artifacts are not replaced by model output.

RAG is an optional local reference layer for each task. While the WebUI is available, the server builds or reuses `output/rag-index`, validates its schema, Registry fingerprint, packaged knowledge-pack version, calibrated retrieval settings, and file checksums, then loads and warms the encoder. An enabled session pins that exact snapshot. The current Web `user_reply` extraction deliberately receives no retrieved snippets so reference material cannot be mistaken for user facts. Retrieval remains available to other explicit role operations and extension entry points. “RAG enabled” therefore means that the prepared snapshot is pinned for the task, not that every Agent call performs retrieval.

## Core capabilities

The Kernel provides the following capabilities through versioned contracts, so experiments, evidence, controller decisions, and results can be inspected and validated.

- `cfdc-protocol/v2` compiles bounded SISO, repeated time-series, staircase, Class IV frequency/amplitude/release, unstable-balance, 2x2 MIMO, and multi-stage protocols. A Provider run recompiles and verifies every binding and fingerprint before execution.
- Operator handoff writes a card, precheck list, JSON schema, repeat CSV templates, and ZIP. CSV/JSON uploads pass authorization, format, session/protocol, repeat-count, timebase, waveform, safety-limit, and signal-quality gates. Rejected attempts append a receipt. They do not count as valid experiments, but failed attempts and requested excitation time still consume their separate pre-registered budgets.
- Registered cases also support a teaching-exercise ZIP. It contains a public manifest, protocol-bound CSV traces, and Chinese instructions; generation reserves software-experiment budget but never writes evidence. Re-uploading the ZIP is required and is checked by the same deterministic upload gates. The seven `audit_class_*` cases use independent current-version dynamics and evaluation Providers rather than aliases of the five engineering models.
- `cfdc-features/v2` derives source-bound intervals and bounded parameter domains for SISO adjacent structures, delay/NMP/integrating/second-order behavior, Step-B nonlinearity, Class IV behavior, local unstable balance, and 2x2 static/dynamic coupling. Missing evidence produces a named feature gap.
- The packaged route registry exposes 20 executable controller contracts plus explicit capability-gap routes. Controller proposals are restricted `ControllerIR`; deterministic synthesis and `cfdc-qualification/v2` return `offline_qualified`, `diagnostic_trial_only`, or `not_qualified`.
- Identification and evaluation Providers use separate immutable bindings. The independent `cfdc-independent-judge/v2.0` recomputes channel metrics from complete sampled trajectories and stop events, evaluates hard stability and limits first, then task-specific performance, perturbed repeats, the worst trial, and a 95% Wilson lower bound. Only stable performance gaps may enter bounded tuning; every accepted candidate receives a new freeze and must pass fresh confirmation.
- `cfdc-session/v4.0` adds a catalog-derived `RegisteredCaseBinding` and preserves revision checks, idempotent actions, stale-revision rejection, immutable artifact histories, and an append-only event chain.

The workflow exposes three separate readiness gates: legal evidence acquisition, evidence-supported route selection, and controller synthesis. Unknown dimensions block only actions that consume them. Every provider attempt is reserved before execution, so retries, excitation time, valid experiments, and distinct protocols remain separate audit quantities. Old sessions remain readable but immutable; a derived session copies only the task and human priors, never old features, qualification, or performance authority.

The executable capability catalog distinguishes registration from end-to-end validation. All 20 registered families have committed tests that synthesize a typed controller, qualify it from public evidence, freeze it, run a nonzero sampled closed loop, and recompute the result independently; each also has a family-relevant rejection case.

- SISO and integrating: `PI`, `delay_aware_PI`, `notch_then_PI`, `two_dof_pid`, `P_integrator`, `PD_integrator`, `lead_lag_series`, `two_dof_PI`.
- Static nonlinear: `local_PI_without_inverse`, `partial_inverse_then_PI`, `deadzone_right_inverse_then_PI`.
- High-order band-limited: `reduced_low_order_PI`, `phase_guarded_2dof_PI`.
- Local state and nonlinear: `cascaded_control`, `local_fixed_PID`, `scheduled_damping_PID`, `self_excitation_energy_guarded_PID`. The cascade runtime covers declared local CartPole and planar near-hover VTOL charts; it does not claim swing-up or global recovery.
- MIMO: `decentralized_channel_PI`, `static_decoupler_then_PI`, `lag_dynamic_decoupler_then_PI`.

## Development checks and optional RAG

Frontend local checks and development:

```bash
npm --prefix cfdc/web/frontend ci
npm --prefix cfdc/web/frontend run typecheck
npm --prefix cfdc/web/frontend run lint
npm --prefix cfdc/web/frontend run format:check
npm --prefix cfdc/web/frontend test
npm --prefix cfdc/web/frontend run build
cd cfdc/web/frontend && npx playwright install chromium && cd ../../..
npm --prefix cfdc/web/frontend run test:e2e
npm --prefix cfdc/web/frontend run dev
```

Playwright starts the built UI and a real FastAPI service on `127.0.0.1:7867` with temporary data and no model calls. Set `CFDC_E2E_URL` to test an already running service. CI runs these frontend checks with Node 22 alongside Python 3.11–3.13 checks. For Vite development, run FastAPI in another terminal; Vite runs at `127.0.0.1:5173` and proxies `/api` to `127.0.0.1:7860`.

From the project directory, run the automated tests and Python checks:

```bash
uv lock --check
uv sync --locked
uv run --locked ruff format .
uv run --locked ruff format --check .
uv run --locked ruff check .
uv run --locked pytest -q
uv run --locked python main.py --benchmark > /tmp/cfdc-benchmark.json
uv run --locked python main.py --validate-demo
uv run --locked python scripts/benchmark_web_api.py
git diff --check
```

`uv` reads the pinned Python version from `.python-version`, creates `.venv`, and installs the project and development tools. No environment activation is needed when commands use `uv run`.

New indexes include two packaged sources by default: the authoritative, generated Registry artifacts and a versioned advisory knowledge pack with English and Chinese versions of twelve control-concept cards. The language variants share stable artifact-group identities and semantic versions while retaining separate content hashes and provenance. The pack has a central JSON manifest and schema, validity metadata, citation records, and 192 frozen evaluation cases: the original English/Chinese sets, one exposed regression set, and a replacement challenge holdout. Its text can explain registered choices but cannot change routes, numerical results, qualification, or authorization. New builds use immutable `cfdc-rag/v3` snapshots; valid `v2` and earlier-policy `v3` snapshots remain readable and are never rewritten in place.

To add local Markdown or PDF references, place them under `references`. Metadata-free legacy documents remain globally visible to structured scope filtering. Use `--knowledge-pack` for another validated pack, `--no-curated` to omit the packaged cards, or `--relevance-threshold` to record an explicit threshold in the new snapshot:

```bash
uv run --locked python -m cfdc.rag index --source-dir ./references --index-dir ./rag-index
uv run --locked python -m cfdc.rag inspect --index-dir ./rag-index
uv run --locked python -m cfdc.rag query --index-dir ./rag-index \
  --role critic --operation check --stage review \
  --language auto \
  --query "Why is uncertain right-half-plane zero cancellation unsafe?"
uv run --locked python -m cfdc.rag eval --index-dir ./rag-index \
  --bundled --split holdout --assert-acceptance
```

`--language` accepts `auto`, `en`, or `zh`. Automatic selection checks only the query summary for Han characters; explicit selection overrides it. Registry references are returned only when the summary contains an exact artifact, profile, or rule ID; structured class/profile fields remain scope filters and never become semantic query text. Advisory retrieval searches the preferred language first, can project a qualifying bilingual group to its requested language, returns at most two distinct curated concept groups, and leaves additional slots available to external documents. `rag eval --bundled` reports each gate dataset and the combined metrics; `--suite en`, `--suite zh`, or `--suite challenge` selects one, and `--assert-acceptance` exits nonzero on failure. Local source directories and generated indexes are not repository artifacts. The `user_reply` path never receives RAG references, and every other Agent reference is labeled as untrusted advisory material with its selected language, group, snapshot, citations, and provenance in the audit record.

Operational history is a separate offline index and is never mixed into RAG or injected into Agent prompts. Its JSON schema accepts equipment manuals, feature artifacts, controller freezes, qualification reports, performance baselines, adaptation episodes, degradation events, rollback reports, and maintenance records. Import verifies payload, configuration, and operating-region hashes as well as validity and same-identity supersedes relationships; only summaries and provenance enter the immutable snapshot. A query must exactly match plant, configuration, and operating-region fingerprints before validity, record-type, lexical, or dense ranking is applied. There is no cross-identity fallback, automatic session scan, write-back, monitoring, or hardware authorization.

Build, inspect, and query a local history index with the independent CLI. The source file must conform to the packaged schema; generated `operational-history` data is ignored by Git:

```bash
uv run python -m cfdc.history index \
  --source ./operational-history/records.json \
  --index-dir ./operational-history/index
uv run python -m cfdc.history inspect \
  --index-dir ./operational-history/index
uv run python -m cfdc.history query \
  --index-dir ./operational-history/index \
  --plant-id plant-a \
  --configuration-fingerprint 0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef \
  --operating-region-fingerprint fedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210 \
  --record-type rollback_report \
  --as-of 2026-09-03T00:00:00Z
```

The historical Gradio application is available in the [v0.3.3 source](https://github.com/yichuan-huang/control-agent/tree/v0.3.3). The current release runs independently of historical checkouts.

## Web interface

Start the application and open `http://127.0.0.1:7860`:

```bash
uv run python app.py
```

In Settings, enter Base URL, Model, and API Key, then choose **测试当前配置** (Test current configuration). Requests use the current form values without a separate save or environment-variable setup. A successful probe confirms service connectivity and model availability, not full inference compatibility. **高级设置** (Advanced settings) contains the optional startup-environment import for address and model; it always preserves the in-memory key.

The built-in knowledge base dependencies are installed by default. The managed index contains only Registry artifacts and packaged English/Chinese knowledge cards. `CFDC_RAG_INDEX_DIR` may override server-side storage; browser inputs cannot choose an index path.

The Guided Workbench creates Kernel tasks from an explicit structured form. Every task requires a description, at least one measured output, at least one control input, finite input lower and upper bounds, and a positive `state_stop`. Output bounds are optional but must be supplied as a pair. `transition_then_hold` also requires an initial region and target region. `disturbance_recovery_to_hold` also requires a disturbance event, recovery start condition, and hold region. The form also accepts engineering units, performance thresholds, experiment budgets, timing preferences, initial values, and intermediate targets.

The workspace presents one primary next action at each state: diagnostic reply, evidence handoff or upload, bounded tuning, and fresh result confirmation. It retains the nine-stage append-only audit timeline. Registered cases show learning goals and evidence boundaries. Protocol previews, recorded trajectories, metrics, confidence, and readiness come from Kernel artifacts. Full JSON trees, audit records, and selectable curves load on demand in expert and result views; display sampling never changes numerical evaluation or replay.

The Expert Contracts tab accepts a full `TaskContract`, loads an existing Kernel session, submits typed action JSON, and validates a downloaded artifact fingerprint. It can export the protocol, operator bundle, upload receipt, feature artifact, Controller IR, qualification, freeze, evaluation, feedback, confirmation, final result, complete session audit, or the full result ZIP.

Web Agent orchestration is always `multi`. The page has no workflow-version selector and no Agent-mode selector. Provider configuration and the default-on built-in RAG switch remain available; the local index directory is server-managed and is not a browser input. Advanced JSON remains available because it is the Kernel's typed public evidence and action interface.

The Kernel input contract determines whether natural language, typed JSON, or a button without input is appropriate. Every mutation checks the session revision and request identity. Reloading reconnects to its recorded operation; an interrupted operation is reported without automatic replay. Retrying is an explicit user action.

The WebUI does not load or run legacy sessions, does not expose the `single` baseline, and does not fall back to a compatibility workflow. A missing, unknown, or non-Kernel Web state is rejected with an explicit error. Use the CLI procedure below for legacy sessions.

Unfinished drafts persist in this browser tab’s `sessionStorage`. Provider credentials remain in volatile memory and must be entered again after reload; API keys are excluded from drafts, Kernel sessions, audit JSON, logs, hashes, and exports. The history import API accepts only `request_id` and an uploaded `file_id`. Imported public facts require fresh boundary confirmation and never inherit registered case execution authority or RAG bindings.

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

To use the teaching loop instead of automatic software evidence, add
`--kernel-evidence-mode exercise_bundle --kernel-prepare-training-exercise`.
The command stops with an `awaiting_evidence` session; upload the downloaded
`training_exercise_bundle.zip` later with `--kernel-upload` so the normal gates
can accept it.

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
