import { useI18n } from "./i18n";
import { useEffect, useRef } from "react";
import type { PlotRelayoutEvent, PlotlyHTMLElement } from "plotly.js";
import type { Curve } from "./api/types";
import Plotly from "plotly.js-basic-dist-min";
import { plotWindow, type WindowRange } from "./plotWindow";
type PlotData = Pick<Curve, "output"> & Partial<Pick<Curve, "control">>;
export default function Charts({
  curve,
  identity = "",
  window: currentWindow = [null, null],
  onWindowChange,
  outputTitle,
}: {
  curve: PlotData;
  identity?: string;
  window?: WindowRange;
  onWindowChange?: (range: WindowRange) => void;
  outputTitle?: string;
}) {
  const { t: tr, locale } = useI18n();

  const output = useRef<HTMLDivElement>(null),
    control = useRef<HTMLDivElement>(null);
  const latestWindow = useRef<WindowRange>(currentWindow);
  latestWindow.current = currentWindow;
  const callback = useRef(onWindowChange);
  callback.current = onWindowChange;
  const [windowStart, windowEnd] = currentWindow;
  useEffect(() => {
    const a = output.current,
      b = control.current;
    if (!a) return;
    let disposed = false;
    const rendered: PlotlyHTMLElement[] = [];
    const layout = (title: string, units: string, series: Curve["output"]) => ({
      title: { text: title },
      uirevision: JSON.stringify([
        "cfdc-chart",
        identity,
        windowStart,
        windowEnd,
      ]),
      autosize: true,
      height: 300,
      margin: { l: 55, r: 15, t: 45, b: 45 },
      xaxis: {
        title: { text: tr("frontend.charts.time_axis") },
        autorange: windowStart === null && windowEnd === null,
        range:
          windowStart === null && windowEnd === null
            ? undefined
            : [
                windowStart ?? Math.min(...series.flatMap((item) => item.x)),
                windowEnd ?? Math.max(...series.flatMap((item) => item.x)),
              ],
      },
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
          series,
        ),
        {
          responsive: true,
          displaylogo: false,
          locale,
          locales: {
            "zh-CN": {
              dictionary: {
                "Download plot as a PNG": tr("frontend.charts.download_png"),
                Zoom: tr("frontend.charts.zoom"),
                Pan: tr("frontend.charts.pan"),
                "Box Select": tr("frontend.charts.box_select"),
                "Lasso Select": tr("frontend.charts.lasso_select"),
                "Zoom in": tr("frontend.charts.zoom_in"),
                "Zoom out": tr("frontend.charts.zoom_out"),
                Autoscale: tr("frontend.charts.autoscale"),
                "Reset axes": tr("frontend.charts.reset_axes"),
                "Toggle Spike Lines": tr("frontend.charts.spike_lines"),
                "Show closest data on hover": tr(
                  "frontend.charts.closest_hover",
                ),
                "Compare data on hover": tr("frontend.charts.compare_hover"),
                "Double-click to zoom back out": tr(
                  "frontend.charts.reset_hint",
                ),
              },
              format: { decimal: ".", thousands: ",", grouping: [3] },
            },
          },
        },
      ).then((node) => {
        if (!disposed) {
          node.on("plotly_relayout", changed);
          rendered.push(node);
        }
      });
    };
    plot(a, curve.output, outputTitle ?? tr("frontend.charts.output_title"));
    if (b && curve.control?.length)
      plot(b, curve.control, tr("frontend.charts.control_input"));
    const observer = new ResizeObserver(() => {
      void Plotly.Plots.resize(a);
      if (b) void Plotly.Plots.resize(b);
    });
    observer.observe(a);
    return () => {
      disposed = true;
      observer.disconnect();
      for (const node of rendered) node.removeAllListeners("plotly_relayout");
    };
  }, [curve, identity, outputTitle, tr, locale, windowStart, windowEnd]);
  useEffect(() => {
    const a = output.current,
      b = control.current;
    return () => {
      if (a) Plotly.purge(a);
      if (b) Plotly.purge(b);
    };
  }, []);
  return (
    <>
      <div className="plot-panel" ref={output} />
      {!!curve.control?.length && <div className="plot-panel" ref={control} />}
    </>
  );
}
