import { useEffect, useRef } from "react";
import type { PlotRelayoutEvent, PlotlyHTMLElement } from "plotly.js";
import type { Curve } from "./api/types";
import Plotly from "plotly.js-dist-min";
import { plotWindow, type WindowRange } from "./plotWindow";
type PlotData = Pick<Curve, "output"> & Partial<Pick<Curve, "control">>;
export default function Charts({
  curve,
  window: currentWindow = [null, null],
  onWindowChange,
  outputTitle = "输出与参考目标",
}: {
  curve: PlotData;
  window?: WindowRange;
  onWindowChange?: (range: WindowRange) => void;
  outputTitle?: string;
}) {
  const output = useRef<HTMLDivElement>(null),
    control = useRef<HTMLDivElement>(null);
  const latestWindow = useRef<WindowRange>(currentWindow);
  latestWindow.current = currentWindow;
  const callback = useRef(onWindowChange);
  callback.current = onWindowChange;
  useEffect(() => {
    const a = output.current,
      b = control.current;
    if (!a) return;
    let disposed = false;
    const rendered: PlotlyHTMLElement[] = [];
    const layout = (title: string, units: string) => ({
      title: { text: title },
      autosize: true,
      height: 300,
      margin: { l: 55, r: 15, t: 45, b: 45 },
      xaxis: { title: { text: "时间 (s)" } },
      yaxis: { title: { text: units } },
      paper_bgcolor: "#fff",
      plot_bgcolor: "#fff",
      legend: { orientation: "h" as const },
    });
    const changed = (event: PlotRelayoutEvent) => {
      const next = plotWindow(
        event as Record<string, unknown>,
        latestWindow.current,
      );
      if (next && callback.current) {
        latestWindow.current = next;
        callback.current(next);
      }
    };
    const plot = (
      element: HTMLDivElement,
      series: Curve["output"],
      title: string,
    ) => {
      void Plotly.react(
        element,
        series.map((c) => ({
          x: c.x,
          y: c.y,
          name: c.name,
          mode: "lines" as const,
        })),
        layout(
          title,
          [...new Set(series.map((c) => c.unit).filter(Boolean))].join(" / "),
        ),
        { responsive: true, displaylogo: false },
      ).then((node) => {
        if (!disposed) {
          node.on("plotly_relayout", changed);
          rendered.push(node);
        }
      });
    };
    plot(a, curve.output, outputTitle);
    if (b && curve.control?.length) plot(b, curve.control, "控制输入");
    const observer = new ResizeObserver(() => {
      void Plotly.Plots.resize(a);
      if (b) void Plotly.Plots.resize(b);
    });
    observer.observe(a);
    return () => {
      disposed = true;
      observer.disconnect();
      for (const node of rendered) node.removeAllListeners("plotly_relayout");
      Plotly.purge(a);
      if (b) Plotly.purge(b);
    };
  }, [curve, outputTitle]);
  return (
    <>
      <div className="plot-panel" ref={output} />
      {!!curve.control?.length && <div className="plot-panel" ref={control} />}
    </>
  );
}
