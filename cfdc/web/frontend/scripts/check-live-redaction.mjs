import assert from "node:assert/strict";
import { mkdtemp, readFile, readdir, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("../", import.meta.url));
const temporary = await mkdtemp(path.join(os.tmpdir(), "cfdc-redaction-"));
const key = "synthetic-credential-error-canary";
try {
  const config = path.join(temporary, "playwright.config.mts");
  await writeFile(
    config,
    `import base from ${JSON.stringify(path.join(root, "playwright.config.ts"))};\n` +
      `export default { ...base, testDir: ${JSON.stringify(path.join(root, "tests/fixtures"))}, testMatch: "**/credential-error.fixture.ts", outputDir: ${JSON.stringify(path.join(temporary, "results"))}, preserveOutput: "always", webServer: undefined };\n`,
  );
  const result = spawnSync(
    "pnpm",
    ["exec", "playwright", "test", "-c", config],
    {
      cwd: root,
      env: {
        ...process.env,
        CFDC_RUN_LIVE_LLM: "1",
        CFDC_LLM_BASE_URL: "https://synthetic.invalid",
        CFDC_LLM_MODEL: "synthetic-model",
        CFDC_LLM_API_KEY: key,
      },
      encoding: "utf8",
      timeout: 60000,
    },
  );
  assert.equal(result.status, 1, "The synthetic test must fail deliberately");
  const output = result.stdout + result.stderr;
  assert(!output.includes(key), "Browser failure output exposed a credential");
  assert(
    output.includes("[REDACTED]"),
    "The intended credential assertion did not run",
  );
  const files = await readdir(path.join(temporary, "results"), {
    recursive: true,
  });
  const contexts = files.filter((name) => name.endsWith("error-context.md"));
  assert.equal(contexts.length, 1, "Expected one deliberate failure artifact");
  for (const file of contexts) {
    const content = await readFile(
      path.join(temporary, "results", file),
      "utf8",
    );
    assert(
      !content.includes(key),
      "Browser failure artifact exposed a credential",
    );
    assert(content.includes("[REDACTED]"));
  }
  console.log(
    "Synthetic browser failure output and artifact redaction passed; no API calls.",
  );
} finally {
  await rm(temporary, { recursive: true, force: true });
}
