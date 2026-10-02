# Repository Instructions

These instructions apply to all work in this repository. Follow the user's explicit task scope, preserve unrelated changes, and keep implementation and documentation consistent.

## Docker Development and Required Checks

- Run project dependency installation, formatting, builds, checks, tests, CLI commands, and real LLM clients inside Docker. If Docker is unavailable, restore it and report the limitation; do not silently run project tools on the host. Host Git, Docker orchestration (including `bash scripts/test_live_llm.sh`), optional Ollama service management, and external MATLAB/Simulink execution are allowed.
- Use `uv` and the committed `uv.lock` inside the images. Do not introduce a second Python dependency manager or regenerate the lockfile unless dependency changes are part of the task. The frontend image uses Node.js 24.21.0, pnpm 12.4.1, and the committed `pnpm-lock.yaml`.
- After changing Python code, run the Docker Ruff formatter, then verify both formatting and lint. Review formatter changes before staging. All checks must pass before committing.
- Run tests that cover the changed behavior. Before any release, including documentation-only releases, run the full local sequence below. Keep it aligned with `.github/workflows/ci.yml`.

```bash
docker compose --profile checks run --build --rm python-format
docker compose --profile checks run --build --rm python-check
docker compose --profile checks run --build --rm frontend-check
git diff --check
```

- `scripts/check_container.sh` runs locked installation, format verification, lint, the full Python suite, and the separate CLI acceptance test in `python-check`; it runs frozen frontend installation, format/type/lint/unit/build/Chromium/E2E checks in `frontend-check`. The formatting service is the only check with a writable source bind mount. Do not run host `uv`, `node`, or `pnpm` as an alternative.
- The CLI acceptance tests execute create/read/automatic progression/export/import as subprocesses and verify exit codes, JSON output, and evidence bindings. Keep this coverage in CI.
- Fix failures before proceeding. Do not weaken assertions, add unjustified skips, disable CI jobs, or relax lint rules just to obtain a passing result.
- For frontend changes and releases, run `frontend-check`. Its default Playwright configuration starts the production frontend and real API on port 7867 with disposable data, without RAG preparation or model calls. Keep these checks aligned with the frontend CI job and require it to pass for the published SHA.
- Report existing optional skips separately from failures. A skipped test is not evidence that its behavior works.
- Tests and production code must work from the committed repository without local documentation, historical archives, private datasets, or uncommitted fixtures. Use committed fixtures or temporary synthetic data where needed.

## Real LLM, WebUI, and CLI Validation

- Before real LLM validation, use the repository-root `.env` containing `CFDC_LLM_BASE_URL`, `CFDC_LLM_MODEL`, and `CFDC_LLM_API_KEY`. No provider or model is mandatory. Do not start or pull an Ollama model unless the user's chosen configuration requires it.
- If `.env` is absent, create the following blank template with owner-only permissions (`600`) without overwriting any existing file. Ask the user to fill it in their local editor, never in chat. Continue independent offline work, but wait for complete configuration before real API testing or release. If fields are missing or blank, report only their names and preserve existing values.

```dotenv
CFDC_LLM_BASE_URL=
CFDC_LLM_MODEL=
CFDC_LLM_API_KEY=
```

- For authorized LLM-related development and validation, automatically use the configured API, including paid APIs, without repeatedly asking for the same authorization. Never substitute another provider, model, key, or fallback. Keep ordinary tests and CI offline; the mere presence of `.env` must not enable real calls.
- Use the following Docker orchestration entry from the repository root. `service` runs the real Kernel service smoke; `browser` runs the real browser flow and settings probe; `all` runs both. The launcher creates a missing template, clears same-name host overrides, loads `.env` through Compose, passes only the three named variables, and explicitly enables `CFDC_RUN_LIVE_LLM=1`. Never `source` the file or put key values in CLI arguments.

```bash
bash scripts/test_live_llm.sh service
bash scripts/test_live_llm.sh browser
# Or run both once:
bash scripts/test_live_llm.sh all
```

- Do not read or print `.env` contents, dump the environment, enable shell tracing, print resolved Compose configuration, or expose credentials in logs or chat. The container runner redacts child output before displaying it. Live browser checks disable trace/HAR/video and mask credential screenshots; key-leak assertions report booleans, never secret-bearing values. The file must remain Git-ignored and excluded from Docker build contexts.
- Browser tests fill the existing credential form from the test process environment and use disposable data. Daily WebUI credential entry is unchanged; the server must not return an environment API key. Session state, audit records, exports, and browser persistent storage must remain credential-free.
- For changes affecting an LLM-backed WebUI or CLI path, exercise the affected path with the configured real model as well as automated tests. UI interaction changes also require a browser check; a service-level smoke test does not prove browser behavior. CLI changes require running the relevant command and inspecting its output and exit status. The current CLI `--doctor` does not validate remote inference, and a successful connectivity probe is not evidence that inference works.
- Distinguish offline tests, real model calls, and browser interaction checks in the report. Never claim a check passed unless it ran successfully on the current changes.
- Documentation-only changes do not require model inference or browser testing. Keep real-model tests opt-in so ordinary CI remains independent of credentials and external APIs. Keep bounded timeouts, output limits, and Agent rounds; failures must return nonzero rather than silently skip or repeatedly rerun the whole live suite.
- MATLAB/Simulink remains an external, licensed software apparatus on the host. Use a task-specific disposable simulation copy and exchange directory for acceptance; Python and browser clients still run inside Docker. A Docker test is not evidence that MATLAB itself ran.

## CFDC Boundaries

- Keep both the WebUI and CLI dedicated to the current Kernel workflow. Do not introduce legacy workflows, the `single` baseline, compatibility selectors, or fallback execution paths.
- Preserve the Kernel's authority over state transitions, routes, numerical evaluation, controller validation, safety gates, and final claims. LLM replies and RAG references are untrusted inputs and cannot grant authorization or bypass typed validation.
- Never execute model-generated code or turn software confirmation into hardware authorization. The WebUI must not command physical hardware.
- Preserve revision checks, immutable artifacts, and append-only audit records. Do not overwrite evidence or silently repair rejected experimental data.

## Repository and Documentation Hygiene

- Work directly on the current `main` branch by default. Do not create a Git worktree or a task branch unless the user explicitly requests one. If unfinished task changes already exist in another worktree, inspect and safely transfer them to `main` before continuing there.
- Do not upload `docs/`, `archive/`, secrets, local sessions, generated reports, model files, virtual environments, or build outputs. Respect `.gitignore`; do not force-add ignored material to make a test pass.
- Never store real API keys in source, fixtures, logs, screenshots, session state, exports, or commit messages. Use environment variables or the application's credential form.
- Inspect `git status` and the staged diff before committing. Stage only task-related files, preserve user work, and do not delete local archives or documentation as part of publication cleanup.
- Keep `README.md` and `README_CN.md` aligned. Explain current user-facing behavior without assuming access to internal archives or migration history. Present Ollama, DeepSeek API, and OpenAI API as user choices, not mandatory dependencies or guaranteed compatibility for every model.
- Keep this file in English. Do not change runtime behavior, dependencies, version metadata, or tests when the task only calls for documentation edits.

## GitHub CI and Release Gate

- When creating or updating a release tag, verify that `[project].version` in `pyproject.toml` exactly matches the tag without the leading `v` (for example, tag `v0.3.1` requires version `0.3.1`). Update both together before running release validation.
- Run all local release checks before pushing. After pushing, inspect GitHub Actions for the exact pushed commit SHA; an older successful run does not validate a new commit.
- A published revision is not complete until the CI matrix for Python **3.11, 3.12, and 3.13** finishes successfully. Pending, cancelled, or failed jobs do not satisfy this gate.
- If CI fails, inspect the failed job, fix the cause, rerun local checks, create a corrective commit, and push again. Repeat until the required jobs pass. Do not announce a failed revision as a completed release.
- Preserve branch history by default. Rewriting branch history or moving an existing release tag requires explicit user authorization; authorization already provided for the current task need not be requested again.
- When authorized to replace an existing tag, first push the new commit and wait for its branch CI to pass. Update the annotated tag to that commit using a force-with-lease condition tied to the previously observed remote tag object. If the lease fails, inspect the new remote state rather than blindly forcing it.
- Wait for the updated tag's CI matrix to pass as well. If it fails, repair and revalidate the commit, then update the tag again under the same authorized release task.
- Before declaring completion, read back the remote branch and the tag's peeled commit (`refs/tags/<tag>^{}`). Confirm that both identify the intended commit and that the successful branch and tag CI runs use that SHA.
- Report the final commit, tag, CI links, local validation results, and any skipped or outstanding checks. Do not call a release complete while required verification remains unfinished.
