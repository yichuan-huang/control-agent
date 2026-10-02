import { test as base, expect } from "@playwright/test";
import { redactLiveText } from "../scripts/live-output.mjs";

// This fixture runs before page teardown writes Playwright's error-context file.
export const test = base.extend<{ credentialSafeErrors: void }>({
  credentialSafeErrors: [
    async ({ page }, use, testInfo) => {
      void page;
      await use();
      if (process.env.CFDC_RUN_LIVE_LLM !== "1") return;
      for (const error of testInfo.errors) {
        if (error.message) error.message = redactLiveText(error.message);
        if (error.stack) error.stack = redactLiveText(error.stack);
        if (error.value) error.value = redactLiveText(error.value);
        if (error.errorContext)
          error.errorContext = redactLiveText(error.errorContext);
      }
    },
    { auto: true },
  ],
});

export { expect };
