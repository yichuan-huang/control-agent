import { afterEach, expect, test, vi } from "vitest";
import { publicJSON, redactLiveText } from "../scripts/live-output.mjs";

afterEach(() => vi.unstubAllEnvs());

test("redacts literal and escaped credentials in browser errors", () => {
  const key = 'synthetic-"key\\value';
  const text = `${key} ${JSON.stringify(key)} ${encodeURIComponent(key)}`;
  const result = redactLiveText(text, key);
  expect(result.includes(key)).toBe(false);
  expect(result.includes(JSON.stringify(key).slice(1, -1))).toBe(false);
  expect(result.includes(encodeURIComponent(key))).toBe(false);
  expect(result).toContain("[REDACTED]");
});

test("refuses to serialize a credential-bearing acceptance artifact", () => {
  vi.stubEnv("CFDC_LLM_API_KEY", "synthetic-artifact-secret");
  expect(() => publicJSON({ error: "echo synthetic-artifact-secret" })).toThrow(
    "Acceptance artifact contained credentials",
  );
  expect(publicJSON({ status: "passed" })).toBe('{\n  "status": "passed"\n}\n');
});
