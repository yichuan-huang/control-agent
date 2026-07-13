# Control Agent

[中文说明](README_CN.md)

This repository is an independent software implementation of the Core-Feature-Driven Control (CFDC) workflow. Its scope is one end-to-end software simulation workflow.

## Workflow

```text
plain-language description
-> strict eight-field structural diagnosis
-> clarification when information is insufficient
-> deterministic classification into one of five canonical classes
-> constrained semantic selection from a versioned simulation-profile catalog
-> automatic safe simulation experiments (3 attempts, up to 5 on quality failure)
-> deterministic minimal core-feature extraction
-> conservative initial controller synthesis
-> bounded Algorithm 1 gain refinement
-> feature tracking and adaptation after a simulated plant change
```

The LLM is used only for language understanding and closed-catalog semantic selection. It cannot invent feature IDs, experiments, controllers, plant equations, or gains. All numerical work is deterministic Python.

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
| `cfdc/workflow/` | Versioned simulation-profile catalog, candidate route construction, capability declarations, deterministic route compilation, and closed-catalog selection validation. |
| `cfdc/experiments/` | Parameterizes the safe experiment templates selected by a profile. It produces plans; the simulator produces the actual internal records. |
| `cfdc/sim/` | Deterministic software plants and experiment backends: scalar prototypes, CartPole, VTOL, 2x2 MIMO traces, benchmark runners, parameter-change scenarios, and stale/adapted comparisons. |
| `cfdc/features/` | Dispatches experiment traces to numerical extractors, aggregates repeated experiments, preserves trace hashes, and applies the feature quality gate. It does not read the natural-language description for feature matching. |
| `cfdc/controllers/` | Synthesizes conservative controllers from released core features, including PI/PD, nonlinear/cascaded templates, MIMO pairing, and half-strength decoupling. |
| `cfdc/online/` | Implements Algorithm 1, safe gain proposals, dwell evaluation, rollback/freeze behavior, FLL/RLS/hover tracking, and feature-driven controller updates. |
| `cfdc/runtime/` | End-to-end orchestration and bounded trial execution. This is where diagnosis, routing, automatic experiments, quality gates, synthesis, tuning, and adaptation are connected. |
| `cfdc/pipeline.py` | Small programmatic facade for applications that call the CFDC stages from Python instead of the CLI. |
| `cfdc/performance.py` | Shared channel and closed-loop performance metrics used by all simulator backends. |
| `cfdc/validation.py` | Cross-stage route, feature-completeness, and go/no-go validation helpers. |
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

Unknown concrete plants are mapped to a normalized profile. Results validate that archetype/profile workflow, not the physical performance of the user's device.

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

Open `http://127.0.0.1:7860`. The application presents the same deterministic pipeline as the CLI in stage-oriented tables, supports clarification in the browser, and keeps the compact audit JSON available in a separate tab. To expose it on another interface or port, use `python app.py --host 0.0.0.0 --port 7860`.

The default run mode is the natural-language workflow, where the entered description may be diagnosed with the configured LLM. CartPole and VTOL entries are developer validation scenarios: they always use preregistered descriptions, diagnoses, and profiles, never call the LLM, and ignore the natural-language form. Switching to a developer scenario disables but does not erase the form, so switching back restores the user's draft.

Run a plain-language problem through the full automatic simulation:

```bash
python main.py \
  --description "A first order temperature process settles after a small heater change." \
  --observed-output temperature \
  --actuator heater
```

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
  --llm-model "deepseek-chat" \
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

`SimulationExperimentRecord` is an internal artifact generated by the selected simulator. There is no CLI or route API for user-supplied experiment results or feature packets.

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

## Evidence Boundary

Every top-level report declares `software_simulation_only`. The project demonstrates workflow completeness, deterministic controller computation, rollback/freeze behavior, and simulated online adaptation for registered dynamics prototypes.

Remaining research work includes exact reproduction of the paper's CartPole and VTOL numerical targets, longer-horizon tracking studies, broader noise/disturbance sweeps, and additional validated Class IV/V profile backends.
