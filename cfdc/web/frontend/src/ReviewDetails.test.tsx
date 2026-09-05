import { render, screen, cleanup } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import { DraftReview } from "./ReviewDetails";
afterEach(cleanup);
test("review distinguishes omitted form budgets from actual normalized Kernel defaults", () => {
  vi.stubGlobal("matchMedia", () => ({
    matches: false,
    addListener: () => {},
    removeListener: () => {},
  }));
  render(
    <DraftReview
      draft={{
        description: "heater",
        budget_fields: [],
        state_stop: 80,
        input_min: 0,
        input_max: 2,
      }}
      task={{
        budgets: {
          clarification_rounds: 6,
          distinct_experiments: 4,
          same_failure_retries: 1,
          elapsed_time_s: 7200,
          cumulative_excitation_time_s: 1800,
        },
      }}
    />,
  );
  expect(screen.getByText("实际应用预算（未填写项沿用内核默认）")).toBeTruthy();
  expect(screen.getByText(/澄清轮次上限：6；实验种类上限：4/)).toBeTruthy();
  expect(screen.getByText("80")).toBeTruthy();
});
