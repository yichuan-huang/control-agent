import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { chromium, expect } from "@playwright/test";

const baseURL = process.env.CFDC_E2E_URL ?? "http://127.0.0.1:7865";
const projectRoot = fileURLToPath(new URL("../../../../", import.meta.url));
const outputDir = path.resolve(
  projectRoot,
  process.env.CFDC_TEACHING_OUTPUT ??
    "output/web-reorganization/teaching-browser",
);
await mkdir(outputDir, { recursive: true });

async function getJson(page, url) {
  const response = await page.request.get(`${baseURL}${url}`);
  if (!response.ok())
    throw new Error(`${url}: ${response.status()} ${await response.text()}`);
  return response.json();
}

async function waitForTaskAction(page, sessionId, action, timeout = 120_000) {
  let summary;
  await expect
    .poll(
      async () => {
        summary = await getJson(page, `/api/v1/tasks/${sessionId}`);
        return summary.workspace.action;
      },
      { timeout, intervals: [500, 800, 1200] },
    )
    .toBe(action);
  return summary;
}

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
const pageErrors = [];
const consoleErrors = [];
page.on("pageerror", (error) => pageErrors.push(error.message));
page.on("console", (message) => {
  if (message.type() === "error") consoleErrors.push(message.text());
});

try {
  await page.goto(baseURL);

  // Explicitly configure the required real local model and disable RAG for this
  // isolated server, whose startup deliberately skipped index preparation.
  await page.getByRole("button", { name: "设置" }).click();
  await page.getByLabel("Base URL").fill("http://127.0.0.1:11434/v1");
  await page.getByLabel("Model").fill("gemma4:e4b");
  await page.getByLabel("API Key").fill("ollama");
  await page.getByRole("switch", { name: "新任务使用内置知识库" }).uncheck();
  await page.getByRole("button", { name: "测试当前配置", exact: true }).click();
  await expect(page.getByText(/^已连接：/)).toBeVisible({ timeout: 120_000 });
  await page.screenshot({
    path: path.join(outputDir, "01-settings-connected.png"),
  });
  await page.keyboard.press("Escape");

  // Create a registered case through React in teaching mode. This operation
  // confirms the declared boundary and advances deterministic Kernel stages to
  // the exercise-bundle upload prompt.
  await page.getByRole("button", { name: "从案例开始" }).click();
  await page.locator("[data-testid=case-open]").first().click();
  await expect(page.getByText("案例参数已锁定")).toBeVisible();
  await page.getByLabel("证据模式").click();
  await page.getByTitle("教学练习包上传", { exact: true }).click();
  await page
    .getByRole("checkbox", { name: "我已核对目标、软件试验边界与预算" })
    .check();
  await page.getByRole("button", { name: "确认软件边界并开始" }).click();
  await expect(page).toHaveURL(/\/tasks\/cfdc-v4-/, { timeout: 120_000 });
  const sessionId = new URL(page.url()).pathname.split("/").at(-1);
  if (!sessionId)
    throw new Error("Task navigation did not expose a session id");
  let summary = await waitForTaskAction(page, sessionId, "ingest_upload");
  if (summary.registered_case_id == null)
    throw new Error("Teaching task lost its registered-case binding");
  await page.screenshot({
    path: path.join(outputDir, "02-teaching-upload-prompt.png"),
    fullPage: true,
  });

  // Download the exact bundle generated for this task through the React link.
  await page
    .getByRole("button", { name: "实验协议与上传回执", exact: true })
    .click();
  const downloadEvent = page.waitForEvent("download");
  await page.getByRole("link", { name: "下载练习包", exact: true }).click();
  const download = await downloadEvent;
  const originalBundle = path.join(outputDir, "original-teaching-bundle.zip");
  await download.saveAs(originalBundle);
  await expect(
    page.getByText("实验协议与上传回执", { exact: true }).nth(1),
  ).toBeVisible();

  const corruptFiles = [
    ["corrupted-upload.csv", "not,a,valid,protocol-bound,trace\n1,2\n"],
    ["corrupted-upload.json", "{ this is intentionally invalid JSON"],
    ["corrupted-upload.zip", "this is intentionally not a ZIP archive"],
  ];
  const rejected = [];
  let expectedAttemptCount = 0;
  for (const [filename, body] of corruptFiles) {
    const filePath = path.join(outputDir, filename);
    await writeFile(filePath, body);
    await page.locator('input[type="file"]').setInputFiles(filePath);
    await expect(page.getByText(filename, { exact: true })).toBeVisible();
    await page
      .getByRole("button", { name: "检查上传数据", exact: true })
      .click();
    expectedAttemptCount += 1;
    let report;
    await expect
      .poll(
        async () => {
          report = await getJson(
            page,
            `/api/v1/tasks/${sessionId}/downloads/report`,
          );
          return report.upload_attempts?.length ?? 0;
        },
        { timeout: 120_000, intervals: [500, 800, 1200] },
      )
      .toBe(expectedAttemptCount);
    summary = await waitForTaskAction(page, sessionId, "ingest_upload");
    const receipt = report.upload_attempts.at(-1);
    if (receipt?.status !== "rejected")
      throw new Error(`${filename} did not produce a formal rejected receipt`);
    rejected.push({
      filename,
      failed_gate: receipt.failed_gate,
      receipt_fingerprint:
        receipt.receipt_fingerprint ?? receipt.upload_fingerprint ?? null,
      revision: summary.revision,
    });
    await writeFile(
      path.join(outputDir, `${filename}.rejection-receipt.json`),
      `${JSON.stringify(receipt, null, 2)}\n`,
    );
    await page.screenshot({
      path: path.join(outputDir, `${filename}.rejected.png`),
      fullPage: true,
    });
    await expect(page.getByText(filename, { exact: true })).toBeVisible();
    await page
      .locator("button", { hasText: /移\s*除/ })
      .last()
      .click();
    await expect(page.getByText(filename, { exact: true })).toHaveCount(0);
  }

  // Re-upload the untouched generated bundle and verify recovery to the next
  // Kernel action with accepted evidence.
  await page.locator('input[type="file"]').setInputFiles(originalBundle);
  await expect(
    page.getByText("original-teaching-bundle.zip", { exact: true }),
  ).toBeVisible();
  await page.getByRole("button", { name: "检查上传数据", exact: true }).click();
  await expect
    .poll(
      async () => {
        summary = await getJson(page, `/api/v1/tasks/${sessionId}`);
        return summary.workspace.action;
      },
      { timeout: 120_000, intervals: [500, 800, 1200] },
    )
    .not.toBe("ingest_upload");
  const finalReport = await getJson(
    page,
    `/api/v1/tasks/${sessionId}/downloads/report`,
  );
  if (!finalReport.evidence?.length)
    throw new Error(
      "Valid original teaching bundle produced no accepted evidence",
    );
  if (finalReport.upload_attempts.at(-1)?.status !== "accepted")
    throw new Error("Valid original teaching bundle lacks an accepted receipt");
  await writeFile(
    path.join(outputDir, "final-report.json"),
    `${JSON.stringify(finalReport, null, 2)}\n`,
  );
  await page.screenshot({
    path: path.join(outputDir, "06-recovered-and-advanced.png"),
    fullPage: true,
  });

  if (pageErrors.length)
    throw new Error(`Browser page errors:\n${pageErrors.join("\n")}`);
  const result = {
    base_url: baseURL,
    session_id: sessionId,
    registered_case_id: summary.registered_case_id,
    final_revision: summary.revision,
    final_status: summary.status,
    final_action: summary.workspace.action,
    rejected,
    accepted_upload_receipt_fingerprint:
      finalReport.upload_attempts.at(-1)?.receipt_fingerprint ??
      finalReport.upload_attempts.at(-1)?.upload_fingerprint ??
      null,
    evidence_count: finalReport.evidence.length,
    page_errors: pageErrors,
    console_errors: consoleErrors,
    original_bundle_bytes: (await readFile(originalBundle)).length,
  };
  await writeFile(
    path.join(outputDir, "result.json"),
    `${JSON.stringify(result, null, 2)}\n`,
  );
  console.log(JSON.stringify(result));
} finally {
  await browser.close();
}
