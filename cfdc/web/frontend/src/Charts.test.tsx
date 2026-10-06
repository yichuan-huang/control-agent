import {
  act,
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import { useState } from "react";
import type { WindowRange } from "./plotWindow";
const { handlers, plots, purged } = vi.hoisted(() => ({
  handlers: [] as ((event: Record<string, unknown>) => void)[],
  plots: vi.fn(),
  purged: vi.fn(),
}));
vi.mock("plotly.js-basic-dist-min", () => ({
  default: {
    react: async (
      element: HTMLElement,
      data: unknown,
      layout: unknown,
      config: unknown,
    ) => {
      plots(element, data, layout, config);
      return Object.assign(element, {
        on: (
          _event: string,
          handler: (event: Record<string, unknown>) => void,
        ) => handlers.push(handler),
        removeAllListeners: () => {},
      });
    },
    Plots: { resize: () => {} },
    purge: purged,
  },
}));
import Charts from "./Charts";
import { I18nProvider, useI18n } from "./i18n";
afterEach(() => {
  cleanup();
  handlers.length = 0;
  plots.mockClear();
  purged.mockClear();
  vi.unstubAllGlobals();
});

test("switching locale updates chart labels and toolbar without purging the zoomed plot or translating signal names", async () => {
  vi.stubGlobal(
    "ResizeObserver",
    class {
      observe() {}
      disconnect() {}
    },
  );
  const curve = {
    output: [{ name: "测量原名", x: [0, 10], y: [0, 1], unit: "C" }],
  };
  function Plot() {
    const { setLocale } = useI18n();
    return (
      <>
        <button onClick={() => setLocale("en")}>English</button>
        <Charts curve={curve} window={[2, 8]} />
      </>
    );
  }
  render(
    <I18nProvider initialLocale="zh-CN">
      <Plot />
    </I18nProvider>,
  );
  await waitFor(() => expect(plots).toHaveBeenCalledTimes(1));
  const initialElement = plots.mock.calls[0][0];
  expect(plots.mock.calls[0][3].locales["zh-CN"].dictionary["Zoom"]).toBe(
    "缩放",
  );
  fireEvent.click(screen.getByText("English"));
  await waitFor(() => expect(plots).toHaveBeenCalledTimes(2));
  expect(plots.mock.calls[1][0]).toBe(initialElement);
  expect(plots.mock.calls[1][1][0].name).toBe("测量原名");
  expect(plots.mock.calls[1][2].title.text).toBe("Output and reference target");
  expect(plots.mock.calls[1][2].uirevision).toBe(
    plots.mock.calls[0][2].uirevision,
  );
  expect(plots.mock.calls[1][3].locale).toBe("en");
  expect(purged).not.toHaveBeenCalled();
});

test("zooming then selecting a cached or full time window updates mounted plot axes", async () => {
  vi.stubGlobal(
    "ResizeObserver",
    class {
      observe() {}
      disconnect() {}
    },
  );
  const cachedCurve = {
    output: [{ name: "speed", x: [0, 10], y: [0, 1], unit: "rad/s" }],
  };
  function ControlledPlot() {
    const [window, setWindow] = useState<WindowRange>([null, null]);
    return (
      <>
        <button onClick={() => setWindow([1, 9])}>Cached window</button>
        <button onClick={() => setWindow([null, null])}>Full window</button>
        <Charts
          curve={cachedCurve}
          window={window}
          onWindowChange={setWindow}
        />
      </>
    );
  }
  render(<ControlledPlot />);
  await waitFor(() => expect(handlers).toHaveLength(1));
  act(() => handlers.at(-1)!({ "xaxis.range[0]": 2, "xaxis.range[1]": 8 }));
  await waitFor(() =>
    expect(plots.mock.calls.at(-1)![2].xaxis.range).toEqual([2, 8]),
  );
  const zoomRevision = plots.mock.calls.at(-1)![2].uirevision;
  fireEvent.click(screen.getByText("Cached window"));
  await waitFor(() =>
    expect(plots.mock.calls.at(-1)![2].xaxis.range).toEqual([1, 9]),
  );
  fireEvent.click(screen.getByText("Full window"));
  await waitFor(() =>
    expect(plots.mock.calls.at(-1)![2].xaxis.autorange).toBe(true),
  );
  expect(plots.mock.calls.at(-1)![2].xaxis.range).toBeUndefined();
  expect(plots.mock.calls.at(-1)![2].uirevision).not.toBe(zoomRevision);
  expect(purged).not.toHaveBeenCalled();
});

test("switching cached signals resets axis view identity without changing the time window", async () => {
  vi.stubGlobal(
    "ResizeObserver",
    class {
      observe() {}
      disconnect() {}
    },
  );
  const cached = {
    temperature: {
      output: [{ name: "temperature", x: [0, 10], y: [50, 100], unit: "C" }],
    },
    speed: {
      output: [{ name: "speed", x: [0, 10], y: [0, 1], unit: "rad/s" }],
    },
  };
  function CachedSignals() {
    const [signal, setSignal] = useState<keyof typeof cached>("temperature");
    return (
      <>
        <button onClick={() => setSignal("speed")}>Cached speed</button>
        <Charts
          curve={cached[signal]}
          identity={`trial-1:${signal}`}
          window={[2, 8]}
        />
      </>
    );
  }
  render(<CachedSignals />);
  await waitFor(() => expect(handlers).toHaveLength(1));
  act(() => handlers.at(-1)!({ "yaxis.range[0]": 60, "yaxis.range[1]": 70 }));
  const temperatureRevision = plots.mock.calls.at(-1)![2].uirevision;
  const element = plots.mock.calls.at(-1)![0];
  fireEvent.click(screen.getByText("Cached speed"));
  await waitFor(() => expect(plots).toHaveBeenCalledTimes(2));
  expect(plots.mock.calls.at(-1)![0]).toBe(element);
  expect(plots.mock.calls.at(-1)![2].xaxis.range).toEqual([2, 8]);
  expect(plots.mock.calls.at(-1)![2].yaxis.title.text).toBe("rad/s");
  expect(plots.mock.calls.at(-1)![2].uirevision).not.toBe(temperatureRevision);
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
