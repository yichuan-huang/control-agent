import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import Expert from "./Expert";
import type { Summary } from "./api/types";
const submit = vi.fn().mockResolvedValue({});
vi.mock("./operations", () => ({
  useOperation: () => ({ submit, busy: false, view: null }),
}));
vi.mock("./context", () => ({
  useSettings: () => ({ credentials: {}, useRag: false }),
}));
vi.mock("@tanstack/react-query", () => ({
  useQuery: () => ({ data: undefined }),
}));
vi.mock("./api/useTaskReader", () => ({ useTaskReader: () => vi.fn() }));
vi.stubGlobal("matchMedia", () => ({
  matches: false,
  addListener: () => {},
  removeListener: () => {},
}));
vi.stubGlobal(
  "ResizeObserver",
  class {
    observe() {}
    unobserve() {}
    disconnect() {}
  },
);
const originalStyle = window.getComputedStyle;
window.getComputedStyle = (element) => originalStyle(element);
afterEach(() => {
  cleanup();
  submit.mockClear();
});
test("expert task action transmits original JSON text without reparsing Chinese and escapes", () => {
  render(
    <Expert
      task={
        {
          session_id: "A",
          revision: 3,
          workspace: {
            action: "answer_probe",
            actionable: true,
            action_title: "回答",
          },
          input_contract: {},
        } as Summary
      }
      onClose={() => {}}
    />,
  );
  fireEvent.click(screen.getByRole("tab", { name: "JSON 提交" }));
  const text = '{\n  "说明": "中文\\n换行\\\\path"\n}';
  fireEvent.change(screen.getByLabelText("专家 JSON"), {
    target: { value: text },
  });
  fireEvent.click(screen.getByRole("button", { name: "提交当前动作" }));
  expect(submit).toHaveBeenCalledWith(
    "/tasks/A/actions",
    expect.objectContaining({ input: { mode: "json", text } }),
  );
});
