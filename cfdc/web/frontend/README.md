# CFDC React frontend

React 19, TypeScript, Ant Design 6, React Router, TanStack Query and Vite. All workflow decisions and evaluation values come from the versioned Kernel API. Plotly and expert tools load on demand. Plot data are display samples; metrics remain the server's recorded metrics.

Install [Node.js and npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) before working on the frontend. npm normally ships with Node.js. Node.js 20.19+ or 22.12+ is required. From the repository root, verify the tools and perform the first-time install and production build:

```sh
node --version
npm --version
npm --prefix cfdc/web/frontend ci
npm --prefix cfdc/web/frontend run build
```

For daily use, start the complete application with one command:

```sh
uv run python app.py
```

Its default address is `http://127.0.0.1:7860`. For frontend development, start the API with that command from the repository root, then run in this directory:

```sh
npm ci
npm run dev
```

Vite serves `http://127.0.0.1:5173` and proxies `/api` to port 7860. Production `npm run build` creates the assets served by `app.py`; there is no separate production Node service.

Regenerate the checked-in API types after backend schema changes:

```sh
uv run --locked python scripts/export_web_openapi.py  # from repository root
npm run generate --prefix cfdc/web/frontend         # from repository root
```

Frontend checks, run from this directory:

```sh
npm run format:check
npm run typecheck
npm run lint
npm test
npm run build
npx playwright install chromium
npm run test:e2e
```

Playwright starts the built frontend and real API at `127.0.0.1:7867` with temporary data, which are removed when the server stops. RAG preparation and model calls are disabled for ordinary tests. `CFDC_E2E_URL` selects an already running service instead. Tests do not require credentials, historical local files or private datasets. The refresh test delays a real GET response while retaining the actual API response; it verifies task creation is not replayed. CI runs the same checks with Node 22.

For opt-in local validation, run `uv run --locked python scripts/serve_web_e2e.py --prepare-rag` from the repository root. Its disposable RAG index is built from packaged sources. Point `CFDC_E2E_URL` at this service, set `CFDC_E2E_OLLAMA=1` for the live settings check, and enter the required local model explicitly in the form.

For read-only visual validation of any existing task with recorded evaluation curves:

```sh
node scripts/check-results.mjs <recorded-task-id>
```

This checks trial/stage identity, a requested 0–5 second window, Plotly layout at 390 pixels, and browser errors; screenshots go to ignored `test-results/`. The supplied record must contain the requested window. No recorded task ID is embedded as a test fixture.

Settings keep credentials only in React memory. A refresh removes credentials. Session storage contains allowlisted task drafts and navigation/operation IDs only. A network retry retains its request ID; definite errors release it. The UI never automatically replays a mutation.

`node scripts/check-teaching.mjs` checks the teaching upload flow with explicit local Ollama settings. Set `CFDC_E2E_URL` to the validation service and `CFDC_TEACHING_OUTPUT` to a temporary output directory. This includes rejected CSV/JSON/ZIP uploads and recovery using the original generated bundle.
