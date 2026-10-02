// Only selected by check-live-redaction.mjs with synthetic credentials.
import { expect, test } from "../live-test";

test("synthetic credential failure is redacted before artifacts", async () => {
  expect(process.env.CFDC_LLM_API_KEY).toBe("deliberately-different-value");
});
