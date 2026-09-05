import { mkdir } from "node:fs/promises";
import { chromium } from "@playwright/test";
const id = process.argv[2];
if (!id)
  throw new Error("Usage: node scripts/check-results.mjs <recorded-task-id>");
const baseURL = process.env.CFDC_E2E_URL ?? "http://127.0.0.1:5173";
const browser = await chromium.launch();
try {
  const page = await browser.newPage({
    viewport: { width: 1280, height: 900 },
  });
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto(`${baseURL}/tasks/${encodeURIComponent(id)}`);
  await page.getByText("评价结果", { exact: true }).waitFor();
  await page.locator(".js-plotly-plot").first().waitFor();
  const response = await page.request.get(
    `${baseURL}/api/v1/tasks/${encodeURIComponent(id)}/evaluations`,
  );
  const evaluations = await response.json();
  if (!evaluations.options.length)
    throw new Error("Recorded task has no evaluation options");
  const selected = evaluations.options.at(-1);
  await page.getByLabel("评价阶段与试次").fill(selected.label);
  await page.getByTitle(selected.label, { exact: true }).click();
  await page.getByLabel("窗口开始秒").fill("0");
  await page.getByLabel("窗口结束秒").fill("5");
  const curveResponse = page.waitForResponse(
    (r) => r.url().includes("/curves?") && r.url().includes("end=5"),
  );
  await page.getByRole("button", { name: "应用窗口" }).click();
  const curve = await (await curveResponse).json();
  if (curve.selection !== selected.value || curve.stage !== selected.stage)
    throw new Error("Selected trial/stage did not match curve");
  const drag = page.locator(".js-plotly-plot .nsewdrag").first();
  await drag.scrollIntoViewIfNeeded();
  await page.waitForFunction(
    () =>
      document.querySelector(".js-plotly-plot")?._fullLayout?.xaxis.range[1] <=
      5.1,
  );
  const box = await drag.boundingBox();
  if (!box) throw new Error("Plot zoom surface missing");
  const zoomResponse = page.waitForResponse(
    (r) =>
      r.url().includes("/curves?") &&
      new URL(r.url()).searchParams.has("start") &&
      new URL(r.url()).searchParams.get("start") !== "0",
  );
  await page.mouse.move(box.x + box.width * 0.2, box.y + box.height * 0.2);
  await page.mouse.down();
  await page.mouse.move(box.x + box.width * 0.7, box.y + box.height * 0.7, {
    steps: 10,
  });
  await page.mouse.up();
  const zoomHttp = await zoomResponse;
  const zoom = await zoomHttp.json();
  if (zoom.selection !== selected.value || zoom.stage !== selected.stage)
    throw new Error("Graph zoom switched the selected record");
  const zoomQuery = new URL(zoomHttp.url()).searchParams;
  await mkdir("test-results", { recursive: true });
  await page.screenshot({
    path: "test-results/recorded-results-desktop.png",
    fullPage: true,
  });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.waitForFunction(
    () =>
      document.documentElement.scrollWidth <= 390 &&
      [...document.querySelectorAll(".js-plotly-plot")].every(
        (e) => e._fullLayout?.width <= e.clientWidth + 1,
      ),
  );
  await page.screenshot({
    path: "test-results/recorded-results-mobile.png",
    fullPage: true,
  });
  const width = await page.evaluate(() => document.documentElement.scrollWidth);
  if (width > 390) throw new Error(`Mobile overflow ${width}`);
  if (errors.length) throw new Error(errors.join("\n"));
  console.log(
    JSON.stringify({
      session_id: id,
      selection: curve.selection,
      stage: curve.stage,
      available_stages: [...new Set(evaluations.options.map((o) => o.stage))],
      display_points: curve.display_points,
      window: [0, 5],
      graph_zoom_window: [
        Number(zoomQuery.get("start")),
        Number(zoomQuery.get("end")),
      ],
      mobileWidth: width,
      pageErrors: errors,
    }),
  );
} finally {
  await browser.close();
}
