import { defineConfig } from "@playwright/test";
import { fileURLToPath } from "node:url";

const externalURL = process.env.CFDC_E2E_URL;
const baseURL = externalURL ?? "http://127.0.0.1:7867";
export default defineConfig({
  testDir: "tests",
  use: {
    baseURL,
    headless: true,
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
      },
});
