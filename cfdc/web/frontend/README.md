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

For opt-in local validation, start the application with `docker compose up -d app`, then run `docker compose --profile checks run --build --rm -e CFDC_OLLAMA_API_KEY=ollama browser-live`. It connects to the application's loopback address from the same network namespace and uses the configured host Ollama service. Use a separate Compose project for disposable validation data.

For read-only visual validation of any existing task with recorded evaluation curves:

```sh
docker compose --profile checks run --rm browser-live node scripts/check-results.mjs <recorded-task-id>
```

This checks trial/stage identity, a requested 0–5 second window, Plotly layout at 390 pixels, and browser errors. Screenshots stay in the disposable container unless you bind-mount its `test-results/` directory. The supplied record must contain the requested window. No recorded task ID is embedded as a test fixture.

Settings keep credentials only in React memory. A refresh removes credentials. Session storage contains allowlisted task drafts and navigation/operation IDs only. A network retry retains its request ID; definite errors release it. The UI never automatically replays a mutation.

`docker compose --profile checks run --rm -e CFDC_OLLAMA_API_KEY=ollama browser-live node scripts/check-teaching.mjs` checks the teaching upload flow against the application with explicit local Ollama settings. Run it in a separate Compose project for disposable task data, and mount a temporary output directory if you need its screenshots. This includes rejected CSV/JSON/ZIP uploads and recovery using the original generated bundle.
