# Control Agent

[中文说明](README_CN.md)

This repository is an independent software implementation of the Core-Feature-Driven Control (CFDC) workflow. Its scope is one end-to-end software simulation workflow.

## Workflow

```text
plain-language description
-> strict eight-field structural diagnosis
-> clarification when information is insufficient
-> deterministic classification into one of five canonical classes
-> constrained semantic selection from a versioned method-profile catalog
-> object-specific equipment-specification questions
-> deterministic compilation of explicit values and units into an approximate plant model
-> minimal core-feature extraction from that model's responses
-> an object-bound, unvalidated controller candidate
-> later real-object tuning (outside this iteration)
```

The LLM is used for language understanding, closed-catalog semantic selection, and organizing specifications explicitly supplied by the user. It may not estimate missing numbers, borrow Demo Fixture values, invent plant equations, or produce controller gains. Unit validation, formulas, model compilation, feature extraction, and controller computation are deterministic Python.

Completing all eight fields means only that structural diagnosis is complete. The ordinary user flow then stops at `awaiting_specifications`; it cannot call a standard Profile simulator, feature extraction, synthesis, Algorithm 1, or adaptation. Users may answer 1–4 questions about their equipment or paste a manual excerpt, advanced users may provide a complete numeric model, and a standard plant runs only after explicit Demo Fixture selection.

The eight diagnosis fields use strict assessments for stability, phase, delay, relative degree, controllability/observability, nonlinearity, coupling, and uncertainty. Classification reads these assessments only; explanatory text is not used for routing.

## Project Structure

| Path | Responsibility |
| --- | --- |
| `cfdc/` | Active Python package. Its top-level modules expose the programmatic pipeline, common validation, performance metrics, and demo entry points; the subpackages below own each workflow stage. |
| `cfdc/web/service.py` | Gradio-facing application service: validates form input, manages clarification sessions, and invokes the shared runtime. |
| `cfdc/web/presentation.py` | Converts typed reports into stage tables, status summaries, comparison views, and compact audit JSON. |
| `cfdc/web/ui.py` | Defines the Gradio layout, CSS, UI callbacks, and event bindings. |
| `cfdc/models/` | Strict Pydantic contracts shared by every stage: diagnosis, profile catalog, experiment records, core features, controllers, tuning state, tracking state, and final reports. |
| `cfdc/diagnosis/` | Stage 0 language diagnosis, the OpenAI-compatible LLM adapter, strict response validation, five-class classification, clarification sessions, safety checks, and offline diagnostic evaluation. |
| `cfdc/specifications/` | Allowed Class I–V, CartPole, and VTOL specification paths; object-specific questions; strict fact validation; and deterministic approximate-model compilation. |
| `cfdc/evidence/` | Complete numeric-model validation, user-model response generation, object/evidence hashing, and closed-loop model validation when user targets are complete. The measured-CSV backend is retained for later tuning, not used as the initial ordinary-user path. |
| `cfdc/workflow/` | Separates versioned control-method Profiles from Demo Plant Fixtures and implements candidate routes, capabilities, deterministic route compilation, and closed-catalog selection validation. |
| `cfdc/experiments/` | Parameterizes the safe experiment templates selected by a profile. It produces plans; the simulator produces the actual internal records. |
| `cfdc/sim/` | Deterministic software plants and experiment backends: scalar prototypes, CartPole, VTOL, 2x2 MIMO traces, benchmark runners, parameter-change scenarios, and stale/adapted comparisons. |
| `cfdc/features/` | Dispatches experiment traces to numerical extractors, aggregates repeated experiments, preserves trace hashes, and applies the feature quality gate. It does not read the natural-language description for feature matching. |
| `cfdc/controllers/` | Synthesizes conservative controllers from released core features, including PI/PD, nonlinear/cascaded templates, MIMO pairing, and half-strength decoupling. |
| `cfdc/online/` | Implements Algorithm 1, safe gain proposals, dwell evaluation, rollback/freeze behavior, FLL/RLS/hover tracking, and feature-driven controller updates. |
| `cfdc/runtime/` | End-to-end orchestration and bounded trial execution. This is where diagnosis, routing, automatic experiments, quality gates, synthesis, tuning, and adaptation are connected. |
| `cfdc/pipeline.py` | Small programmatic facade for applications that call the CFDC stages from Python instead of the CLI. |
| `cfdc/performance.py` | Shared channel and closed-loop performance metrics used by all simulator backends. |
| `cfdc/validation.py` | Cross-stage route, feature-completeness, and go/no-go validation helpers. |
| `dataset/` | Knowledge documents and prompts for 200 control problems. A symbolic “mathematical model” in Markdown is not a parameter-complete executable user plant, and these equations are not connected to this runtime. |
| `tests/` | Unit, integration, CLI, Class I-V end-to-end, retry/failure, Algorithm 1, tracking, CartPole, VTOL, and Class V regression tests. |
| `docs/` | Design notes and migration records for the current simulation-first architecture. |
| `archive/` | Historical implementation retained for reference only. Active code must not import it. |
| `outputs/` | Generated local reports and simulation output; it is not source code and is ignored by Git. |
| `tmp/` | Disposable local scratch data created during development or validation; it is ignored by Git and never imported by the runtime. |
| `main.py` | CLI entry point for natural-language runs, diagnostic sessions, developer routes, benchmarks, and evaluation. |
| `app.py` | Thin Gradio launcher that parses server arguments and starts the UI defined in `cfdc.web.ui`. |

## Simulation Profiles

The five paper archetypes remain the only dynamical classes. Profiles are implementation routes within those classes:

- Class I: first-order lag, optionally with significant delay.
- Class II: second-order oscillator.
- Class III: pure or double integrator.
- Class IV: inverse response, generic unstable/higher-order, underactuated CartPole, or cascaded VTOL.
- Class V: a generic coupled 2x2 plant with matrix feature extraction, global pairing, and half-strength static decoupling.

A method Profile declares required features, signals, and a controller template; it no longer contributes user-object numbers. Plants covered by a whitelisted specification template may be compiled from explicit specifications. Unsupported higher-order or unstable plants stop and require a complete numeric model. CartPole, VTOL, and normalized scalar plants remain explicit Demo Fixtures whose results are always `demo_fixture_only`.

## Run

Install and test:

```bash
python -m pip install -e '.[test]'
pytest -q
python main.py --validate-demo
```

Start the Gradio application:

```bash
python app.py
```

Open `http://127.0.0.1:7860`. The application shows “structural diagnosis → specification model → core features → parameter candidate → validation.” After structural diagnosis it defaults to a natural-language specification dialogue, with complete numeric model and explicit Demo Fixture alternatives. CSV upload is not shown in this initial stage. Compact audit JSON remains available in a separate tab. To expose it on another interface or port, use `python app.py --host 0.0.0.0 --port 7860`.

The default run mode is the natural-language workflow, where the entered description may be diagnosed with the configured LLM. CartPole and VTOL entries are developer validation scenarios: they always use preregistered descriptions, diagnoses, and profiles, never call the LLM, and ignore the natural-language form. Switching to a developer scenario disables but does not erase the form, so switching back restores the user's draft.

Run structural diagnosis and receive object-specific specification questions:

```bash
python main.py \
  --description "A first order temperature process settles after a small heater change." \
  --observed-output temperature \
  --actuator heater
```

Submit known specifications, with repeatable `--specification-answer` if desired:

```bash
python main.py \
  --description "A first order temperature process settles after a small heater change." \
  --observed-output temperature \
  --actuator heater \
  --specification-text "Manual: input_change=1 kW; steady_output_change=10 degC; response_time_s=30 s; input_min=0 kW; input_max=2 kW; output_min=-20 degC; output_max=80 degC"
```

Without an LLM, the Web fallback accepts one `number + unit` answer per visible question line. Models compiled from declared language specifications always remain `declared_specification_model_only` and their controllers remain `candidate_unvalidated`.

Every numeric specification must include a unit, but the units shown by the UI are examples rather than a finite whitelist. Common spellings are normalized and converted to canonical units (`rad/s²` → `rad/s^2`, `1000 mV` → `1 V`, and `100 ms` → `0.1 s`). Device-specific command or sensor units such as `DAC_count` are accepted when the related input or output facts use them consistently. A missing unit produces another specification question, mixed opaque units require an explicit conversion relationship, and physical fields such as mass, time, and acceleration still enforce dimensional compatibility.

Advanced callers may use `--model-spec model.json` for a complete numeric transfer function, state-space model, or whitelisted nonlinear template. Only a complete `--validation-spec validation.json` can yield `validated_in_simulation` on that user model. `--demo-fixture` explicitly runs a standard plant and is mutually exclusive with user specifications or evidence.

Use an OpenAI-compatible LLM for both structured diagnosis and constrained profile selection:

```bash
# Required provider configuration. These values are not limited to OpenAI/GPT.
export CFDC_LLM_BASE_URL="https://your-provider.example/v1"
export CFDC_LLM_API_KEY="..."
export CFDC_LLM_MODEL="your-provider-model"

python main.py --use-llm \
  --description "A rod on a cart falls over when upright; I measure cart position and rod angle." \
  --observed-output "cart position" \
  --observed-output "rod angle" \
  --actuator "cart motor force"
```

`CFDC_LLM_BASE_URL` must point to the provider's OpenAI-compatible API root, normally ending in `/v1`, not necessarily to `/chat/completions`. The adapter accepts either form and normalizes it. Configuration precedence is CLI flags, then `CFDC_LLM_*`, then `CONTROL_PROJECT_LLM_*`, then standard `OPENAI_*` variables.

The same settings can be supplied entirely on the command line:

```bash
python main.py --use-llm \
  --llm-base-url "https://api.deepseek.com/v1" \
  --llm-model "deepseek-v4-pro" \
  --llm-api-key "$DEEPSEEK_API_KEY" \
  --description "A spring-mass process oscillates after a force pulse." \
  --observed-output position \
  --actuator force
```

For a local OpenAI-compatible server such as Ollama:

```bash
export CFDC_LLM_BASE_URL="http://localhost:11434/v1"
export CFDC_LLM_MODEL="qwen2.5:14b"
export CFDC_LLM_API_KEY="ollama"
```

See [`.env.example`](.env.example) for a provider-neutral template. The CLI does not load `.env` automatically; export the variables in your shell (or source them with shell export enabled) or pass the flags explicitly.

Built-in developer validation routes do not require an LLM:

```bash
python main.py --run-route cartpole
python main.py --run-route vtol-position
python main.py --run-route vtol-boundary
python main.py --run-route vtol-variation
python main.py --benchmark
python main.py --diagnostic-eval
```

`SimulationExperimentRecord` is an internal artifact generated by an audited model/data adapter. Core features cannot be uploaded directly. The `--trace-manifest` backend remains for future real-tuning integration, but the Gradio specification stage does not ask ordinary users for CSV files or repeated tests.

## Clarification Sessions

Create a session for an incomplete description:

```bash
python main.py --description "I have a machine." \
  --diagnostic-session-output session.json
```

The report exposes stable question IDs. Resume with keyed answers or a revised description:

```bash
python main.py --diagnostic-session-input session.json \
  --diagnostic-answer "q_1234567890=The output settles after a small input." \
  --diagnostic-session-output session.json

python main.py --diagnostic-session-input session.json \
  --diagnostic-description "It is a measured thermal process driven by a heater." \
  --diagnostic-session-output session.json
```

After structural diagnosis, the same schema-v3 session stores specification templates, answer history, confirmed facts, gaps/conflicts, and the compiled-model hash. Resume it with `--specification-answer`. Complete v1/v2 sessions migrate to `awaiting_specifications`; old controller-release state is not restored.

## Evidence Boundary

Reports distinguish `structural_diagnosis_only`, `declared_specification_model_only`, `user_object_model_validated_in_simulation`, and `demo_fixture_only`. Declared specifications can produce only an unvalidated candidate. A complete user model is called simulation-validated only when user validation conditions are complete and pass. No state claims physical-machine safety, and the software never sends hardware commands.

Remaining research work includes exact reproduction of the paper's CartPole and VTOL numerical targets, longer-horizon tracking studies, broader noise/disturbance sweeps, and additional validated Class IV/V profile backends.
