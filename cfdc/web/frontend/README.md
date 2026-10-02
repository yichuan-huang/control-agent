# CFDC React frontend

React 19, TypeScript, Ant Design 6, React Router, TanStack Query and Vite. All workflow decisions and evaluation values come from the versioned Kernel API. Plotly and expert tools load on demand. Plot data are display samples; metrics remain the server's recorded metrics.

The Docker build pins Node.js 24.21.0, pnpm 12.4.1, and the committed `pnpm-lock.yaml`. From the repository root, build and start the application:

```sh
docker compose up --build -d app
```

For later starts:

```sh
docker compose up -d app
```

Its default address is `http://127.0.0.1:7860`. Run all frontend checks in Docker from the repository root:

```sh
docker compose --profile checks run --build --rm frontend-check
```

The build stage produces the assets served by `app.py`; no separate production Node service is needed. The check stage runs format, type, lint, unit, build, and Playwright checks.

Regenerate the checked-in API types after backend schema changes:

```sh
docker compose --profile checks run --rm \
  -v "$PWD/cfdc/web/frontend/openapi.json:/app/cfdc/web/frontend/openapi.json" \
  frontend-check python /app/scripts/export_web_openapi.py
docker compose --profile checks run --rm \
  -v "$PWD/cfdc/web/frontend/src/api/schema.d.ts:/app/cfdc/web/frontend/src/api/schema.d.ts" \
  frontend-check pnpm run generate
```

Playwright starts the built frontend and real API at `127.0.0.1:7867` with temporary data, which are removed when the server stops. RAG preparation and model calls are disabled for ordinary tests. `CFDC_E2E_URL` selects an already running service instead. Tests do not require credentials, historical local files or private datasets. The refresh test delays a real GET response while retaining the actual API response; it verifies task creation is not replayed. CI runs the same checks with pnpm 12.4.1 and Node.js 24.21.0.

For opt-in real API validation, run `bash scripts/test_live_llm.sh browser` from the repository root. If `.env` is absent, the launcher creates an empty owner-only template and asks you to fill `CFDC_LLM_BASE_URL`, `CFDC_LLM_MODEL`, and `CFDC_LLM_API_KEY` in your local editor. Existing values are never overwritten or printed. The entry loads the file through Compose, clears same-name host overrides, and explicitly enables `CFDC_RUN_LIVE_LLM=1`. The container starts the production frontend and real API with disposable data, while the test process fills the existing credential form. No provider or model is mandatory. `service` runs the Kernel service smoke and `all` runs both. Ordinary checks and CI never enable inference. Live test output is redacted before display; traces, HAR, video and automatic screenshots are disabled.

For read-only visual validation of any existing task with recorded evaluation curves:

```sh
docker compose --profile checks run --rm browser-live node scripts/check-results.mjs <recorded-task-id>
```

This checks trial/stage identity, a requested 0–5 second window, Plotly layout at 390 pixels, and browser errors. Screenshots stay in the disposable container unless you bind-mount its `test-results/` directory. The supplied record must contain the requested window. No recorded task ID is embedded as a test fixture.

Settings keep credentials only in React memory. A refresh removes credentials. Session storage contains allowlisted task drafts and navigation/operation IDs only. A network retry retains its request ID; definite errors release it. The UI never automatically replays a mutation.

For auxiliary acceptance against an existing application, `browser-live` shares that application's network namespace. Use a separate Compose project for disposable data. The teaching check includes rejected CSV/JSON/ZIP uploads and recovery using the original generated bundle. After filling `.env`, run:

```sh
CFDC_PORT=7868 docker compose -p cfdc-validation up --build --wait -d app
env -u CFDC_LLM_BASE_URL -u CFDC_LLM_MODEL -u CFDC_LLM_API_KEY \
  docker compose --env-file .env -p cfdc-validation --profile checks run --build --rm \
  -e CFDC_RUN_LIVE_LLM=1 -e CFDC_LLM_BASE_URL -e CFDC_LLM_MODEL -e CFDC_LLM_API_KEY \
  browser-live python /app/scripts/run_live_llm.py command node scripts/check-teaching.mjs
```

Keep the redacting runner around auxiliary scripts too. Credential screenshots are masked. Generated acceptance artifacts remain local; do not persist traces, HAR, videos, credentials, or browser storage state. See the simulation acceptance instructions for the explicit MATLAB handoff; ordinary browser validation does not run MATLAB.
