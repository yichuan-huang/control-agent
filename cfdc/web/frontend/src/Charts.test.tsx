import { act, cleanup, render, waitFor } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
const { handlers } = vi.hoisted(() => ({
  handlers: [] as ((event: Record<string, unknown>) => void)[],
}));
vi.mock("plotly.js-dist-min", () => ({
  default: {
    react: async (element: HTMLElement) =>
      Object.assign(element, {
        on: (
          _event: string,
          handler: (event: Record<string, unknown>) => void,
        ) => handlers.push(handler),
        removeAllListeners: () => {},
      }),
    Plots: { resize: () => {} },
    purge: () => {},
  },
}));
import Charts from "./Charts";
afterEach(() => {
  cleanup();
  handlers.length = 0;
  vi.unstubAllGlobals();
});
test("Plotly relayout forwards zoom and reset once and ignores resize", async () => {
  vi.stubGlobal(
    "ResizeObserver",
    class {
      observe() {}
      disconnect() {}
    },
  );
  const changed = vi.fn();
  render(
    <Charts
      curve={{
        output: [{ name: "temperature", x: [0, 10], y: [0, 1], unit: "C" }],
      }}
      onWindowChange={changed}
    />,
  );
  await waitFor(() => expect(handlers).toHaveLength(1));
  act(() => {
    handlers[0]({ "xaxis.range[0]": 2, "xaxis.range[1]": 8 });
    handlers[0]({ "xaxis.range[0]": 2, "xaxis.range[1]": 8 });
    handlers[0]({ autosize: true });
  });
  expect(changed).toHaveBeenCalledTimes(1);
  expect(changed).toHaveBeenLastCalledWith([2, 8]);
  act(() => handlers[0]({ "xaxis.autorange": true }));
  expect(changed).toHaveBeenLastCalledWith([null, null]);
});
