import { defineConfig } from "@playwright/test";
import { fileURLToPath } from "node:url";

const externalURL = process.env.CFDC_E2E_URL;
const baseURL = externalURL ?? "http://127.0.0.1:7867";
const live = process.env.CFDC_RUN_LIVE_LLM === "1";
// The pinned Playwright version otherwise captures form values in AI error context.
if (live) process.env.PLAYWRIGHT_NO_COPY_PROMPT = "1";
export default defineConfig({
  testDir: "tests",
  // The shared real API serializes mutations, including long Provider trials.
  workers: 1,
  retries: 0,
  preserveOutput: live ? "never" : "always",
  use: {
    baseURL,
    headless: true,
    trace: "off",
    video: "off",
    screenshot: "off",
  },
  timeout: 60000,
  reporter: "list",
  webServer: externalURL
    ? undefined
    : {
        command: "uv run --locked python scripts/serve_web_e2e.py",
        cwd: fileURLToPath(new URL("../../../", import.meta.url)),
        url: baseURL,
        reuseExistingServer: false,
        timeout: 60000,
        // Live credentials belong to the browser test, not server presets.
        env: {
          CFDC_LLM_BASE_URL: "",
          CFDC_LLM_MODEL: "",
          CFDC_LLM_API_KEY: "",
        },
      },
});
