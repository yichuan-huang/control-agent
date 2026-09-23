// Opt-in release acceptance. Run in browser-live with /exchange mounted, then
// alternate with host MATLAB run_http_jobs(exchangeRoot/browser).
import assert from "node:assert/strict";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { chromium, expect } from "@playwright/test";

const baseURL = process.env.CFDC_E2E_URL;
const modelURL = process.env.CFDC_OLLAMA_BASE_URL;
const model = process.env.CFDC_OLLAMA_MODEL;
const modelKey = process.env.CFDC_OLLAMA_API_KEY;
const exchange = "/exchange";
const folder = path.join(exchange, "browser");
const caseIds = ["02_vacuum_hold", "05_ink_disturbance_recovery"];
const precheckLabels = {
  channels: "已核对测量与控制通道",
  units: "已核对数据单位",
  logger: "记录工具能够保存全部试验数据",
  "stop condition": "已核对停止条件",
  "initial condition": "已核对初始条件",
};

assert(baseURL && modelURL && modelKey && model === "gemma4:e4b");
const mode = process.argv[2];
assert(["init", "advance"].includes(mode), "Expected init or advance");

async function json(file) {
  return JSON.parse(await readFile(file, "utf8"));
}

async function summary(page, id) {
  const response = await page.request.get(`/api/v1/tasks/${id}`);
  assert.equal(response.status(), 200);
  return response.json();
}

async function report(page, id) {
  const response = await page.request.get(
    `/api/v1/tasks/${id}/downloads/report`,
  );
  assert.equal(response.status(), 200);
  return response.json();
}

async function completed(page, response) {
  assert.equal(response.status(), 202, await response.text());
  const receipt = await response.json();
  let operation;
  await expect
    .poll(
      async () => {
        const current = await page.request.get(
          `/api/v1/operations/${receipt.operation_id}`,
        );
        assert.equal(current.status(), 200);
        operation = await current.json();
        if (operation.status === "failed") {
          throw new Error(
            `Operation failed: ${JSON.stringify(operation.error)}`,
          );
        }
        return operation.status;
      },
      { timeout: 300_000, intervals: [500, 1000, 2000] },
    )
    .toBe("completed");
  assert(!operation.error, JSON.stringify(operation.error));
  return operation;
}

async function clickAction(page, id, title) {
  const pending = page.waitForResponse(
    (response) =>
      new URL(response.url()).pathname === `/api/v1/tasks/${id}/actions` &&
      response.request().method() === "POST",
  );
  await page.getByRole("button", { name: title, exact: true }).click();
  await completed(page, await pending);
  await page.reload();
  return summary(page, id);
}

async function download(page, label, target) {
  const pending = page.waitForEvent("download");
  await page.getByRole("link", { name: label, exact: true }).click();
  const item = await pending;
  await item.saveAs(target);
}

async function stageIdentification(page, caseId, id) {
  let current = await summary(page, id);
  if (current.workspace.action === "record_operator_report") {
    const packagePath = path.join(folder, `${caseId}-0-identification.zip`);
    await download(page, "下载采集请求包 ZIP", packagePath);
    for (const key of current.input_contract.operator_prechecks) {
      const option = page.getByRole("checkbox", {
        name: precheckLabels[key] ?? key,
      });
      await option.click();
      await expect(option).toBeChecked();
    }
    await page
      .getByLabel("操作员说明")
      .fill("软件仿真边界、通道、采样和停止条件已核对。");
    current = await clickAction(page, id, current.workspace.action_title);
  }
  assert.equal(current.workspace.action, "ingest_upload");
  return {
    case_id: caseId,
    case_dir: `simulations/${caseId}`,
    session_id: id,
    package_path: `browser/${caseId}-0-identification.zip`,
    kind: "identification",
    response_path: `browser/${caseId}-0-identification-response.json`,
  };
}

async function openCase(browser, caseId) {
  const context = await browser.newContext({ baseURL, acceptDownloads: true });
  const page = await context.newPage();
  if (process.env.CFDC_RESUME_CASE_ID === caseId) {
    const id = process.env.CFDC_RESUME_SESSION_ID;
    assert(id, "CFDC_RESUME_SESSION_ID is required to resume a case");
    await page.goto(`/tasks/${id}`);
    const row = await stageIdentification(page, caseId, id);
    await context.close();
    return row;
  }
  const config = await json(
    path.join(exchange, "simulations", caseId, "case_config.json"),
  );
  const task = config.task;
  await page.goto("/new");
  await page.getByRole("button", { name: "设置", exact: true }).click();
  await page.getByLabel("Base URL").fill(modelURL);
  await page.getByLabel("Model").fill(model);
  await page.getByLabel("API Key").fill(modelKey);
  await page.getByRole("switch", { name: "新任务使用内置知识库" }).uncheck();
  await page.keyboard.press("Escape");
  await expect(page.getByLabel("Base URL")).toBeHidden();

  await page.getByLabel("设备与目标").fill(task.description);
  if (task.task_type === "disturbance_recovery_to_hold") {
    await page.getByLabel("任务类型", { exact: true }).click();
    await page.getByText("受到扰动后恢复并保持", { exact: true }).click();
    await expect(page.getByLabel("扰动事件", { exact: true })).toBeVisible();
    await page
      .getByLabel("扰动事件", { exact: true })
      .fill(task.disturbance_event);
    await page
      .getByLabel("恢复起点", { exact: true })
      .fill(task.recovery_start_condition);
    await page
      .getByLabel("恢复后保持区域", { exact: true })
      .fill(task.disturbance_hold_region);
    await page
      .getByLabel("扰动输入通道名称")
      .fill(task.disturbance_contract.channel);
    await page
      .getByLabel("扰动开始时间 (s)")
      .fill(String(task.disturbance_contract.time_s));
    await page
      .getByLabel("扰动幅度（输入单位）")
      .fill(String(task.disturbance_contract.amplitude));
    await page
      .getByLabel("扰动持续时间 (s)")
      .fill(String(task.disturbance_contract.duration_s));
    await page
      .getByLabel("扰动后恢复时间上限 (s)")
      .fill(String(task.success_requirements.recovery_time_max_s));
  }
  await page.getByRole("button", { name: "下一步", exact: true }).click();
  await page.getByLabel("输出 1 名称").fill(task.measured_signals[0]);
  await page
    .getByLabel("单位", { exact: true })
    .fill(task.signal_units[task.measured_signals[0]]);
  await page.getByLabel("输入 1 名称").fill(task.control_input);
  await page.getByLabel("输入单位", { exact: true }).fill(task.input_units);
  await page.getByRole("button", { name: "下一步", exact: true }).click();
  for (const [label, value] of [
    ["输入下限", task.input_min],
    ["输入上限", task.input_max],
    ["软件试验停止阈值", task.state_stop],
    ["参考目标", task.reference],
    ["采样间隔 (s)", task.budgets.evaluation_sample_time_s],
    ["每次运行时长 (s)", task.budgets.evaluation_horizon_s],
    ["重复运行次数", task.budgets.evaluation_repeats],
  ]) {
    await page.getByLabel(label, { exact: true }).fill(String(value));
  }
  await page
    .getByLabel("评价区域（适用的工作范围）")
    .fill(task.operating_region);
  await page
    .getByRole("spinbutton", { name: "稳定后允许偏离目标多少", exact: true })
    .fill(String(task.success_requirements.final_abs_error_max));
  await page.getByText("性能要求与预算（可选）", { exact: true }).click();
  for (const [name, value] of [
    ["允许超过目标多少", task.success_requirements.overshoot_max],
    ["希望多少秒内稳定", task.success_requirements.settling_time_max_s],
    ["至少保持多少秒", task.success_requirements.hold_duration_min_s],
    [
      "重复试验成功率下限",
      task.success_requirements.perturbed_success_rate_min,
    ],
  ]) {
    const option = page.getByRole("checkbox", { name, exact: true });
    await option.click();
    await expect(option).toBeChecked();
    await page
      .getByRole("spinbutton", { name, exact: true })
      .fill(String(value));
  }
  await page.getByRole("button", { name: "校验并核对" }).click();
  await page
    .getByRole("checkbox", { name: "我已核对目标、软件试验边界与预算" })
    .check();
  const pending = page.waitForResponse(
    (response) =>
      new URL(response.url()).pathname === "/api/v1/tasks" &&
      response.request().method() === "POST",
  );
  await page.getByRole("button", { name: "确认软件边界并开始" }).click();
  const creation = await completed(page, await pending);
  const id = creation.session_id;
  assert(id);
  await expect(page).toHaveURL(new RegExp(`/tasks/${id}$`));
  const created = await summary(page, id);
  assert.equal(created.workspace.action, "answer");
  assert.equal(created.task.reference, task.reference);
  assert.equal(
    created.task.budgets.evaluation_repeats,
    task.budgets.evaluation_repeats,
  );
  console.log("Diagnosing", caseId, id);
  await page.getByLabel("当前步骤回复").fill(config.diagnosis_text);
  let current = await clickAction(page, id, created.workspace.action_title);
  assert.equal(
    current.workspace.action,
    "advance",
    JSON.stringify(current.workspace),
  );
  current = await clickAction(page, id, current.workspace.action_title);
  assert.equal(current.workspace.action, "select_external_source");
  await page.getByRole("radio", { name: "外部软件仿真" }).check();
  current = await clickAction(page, id, "确认数据来源");
  assert.equal(current.workspace.action, "record_operator_report");
  const row = await stageIdentification(page, caseId, id);
  await context.close();
  return row;
}

async function advanceCase(browser, job, round) {
  const context = await browser.newContext({ baseURL, acceptDownloads: true });
  const page = await context.newPage();
  const id = job.session_id;
  await page.goto(`/tasks/${id}`);
  let current = await summary(page, id);
  const expectedUploadAction =
    job.kind === "identification" ? "ingest_upload" : "submit_external_results";
  if (current.workspace.action === expectedUploadAction) {
    const result = await json(path.join(exchange, job.response_path));
    const files =
      job.kind === "identification" ? result.files : [result.result_zip];
    assert(files.length > 0);
    const absoluteFiles = files.map((file) => path.join(exchange, file));
    const uploadResponses = [];
    page.on("response", async (response) => {
      if (new URL(response.url()).pathname === "/api/v1/uploads") {
        uploadResponses.push({
          status: response.status(),
          body: await response.json(),
        });
      }
    });
    await page.locator('input[type="file"]').setInputFiles(absoluteFiles);
    await expect
      .poll(() => uploadResponses.length, { timeout: 20_000 })
      .toBe(absoluteFiles.length);
    assert(uploadResponses.every((response) => response.status === 200));
    assert.deepEqual(
      uploadResponses.map((response) => response.body.filename).sort(),
      absoluteFiles.map((file) => path.basename(file)).sort(),
    );
    const submit =
      job.kind === "identification"
        ? current.workspace.action_title
        : "校验并提交本轮轨迹";
    await expect(
      page.getByRole("button", { name: submit, exact: true }),
    ).toBeEnabled();
    current = await clickAction(page, id, submit);
  }
  const receiptReport = await report(page, id);
  if (job.kind === "identification") {
    assert.equal(receiptReport.evidence.length, 3);
    assert(
      receiptReport.upload_attempts.length > 0 &&
        receiptReport.upload_attempts.every(
          (attempt) => attempt.status === "accepted",
        ),
      "An identification upload was rejected",
    );
  } else {
    assert(
      receiptReport.external_workflow.receipts.length > 0 &&
        receiptReport.external_workflow.receipts.every(
          (receipt) => receipt.accepted,
        ),
      "An external evaluation receipt was rejected",
    );
  }
  if (current.workspace.action === "freeze") {
    const checkbox = page.getByRole("checkbox", {
      name: "我已核对冻结约定，确认进入开发评价",
    });
    await checkbox.click();
    await expect(checkbox).toBeChecked();
    current = await clickAction(page, id, "确认并冻结评价约定");
  }
  if (current.workspace.action === "start_external_tuning") {
    current = await clickAction(page, id, "开始有界外部调优");
  }
  if (
    [
      "performance_met",
      "capability_gap",
      "experiment_failed",
      "performance_not_met",
    ].includes(current.status)
  ) {
    const finalReport = await report(page, id);
    await writeFile(
      path.join(folder, `${job.case_id}-report.json`),
      JSON.stringify(finalReport, null, 2),
    );
    await page.reload();
    assert.equal((await summary(page, id)).status, current.status);
    await download(
      page,
      "导出完整公开包",
      path.join(folder, `${job.case_id}-export.zip`),
    );
    await context.close();
    return { terminal: current.status };
  }
  assert.equal(current.workspace.action, "prepare_external_run");
  current = await clickAction(page, id, "准备本轮外部运行包");
  assert.equal(current.workspace.action, "submit_external_results");
  const packageName = `${job.case_id}-${round}-evaluation.zip`;
  await download(
    page,
    "下载本轮完整运行包 ZIP",
    path.join(folder, packageName),
  );
  await context.close();
  return {
    job: {
      case_id: job.case_id,
      case_dir: job.case_dir,
      session_id: id,
      package_path: `browser/${packageName}`,
      kind: "evaluation",
      response_path: `browser/${job.case_id}-${round}-evaluation-response.json`,
    },
  };
}

await mkdir(folder, { recursive: true });
const browser = await chromium.launch({ headless: true });
try {
  if (mode === "init") {
    const jobs = [];
    for (const caseId of caseIds) {
      jobs.push(await openCase(browser, caseId));
      console.log("Created", caseId, jobs.at(-1).session_id);
    }
    await writeFile(
      path.join(folder, "state.json"),
      JSON.stringify({ round: 0, cases: jobs, terminal: {} }, null, 2),
    );
    await writeFile(
      path.join(folder, "jobs-exchange.json"),
      JSON.stringify(jobs, null, 2),
    );
  } else {
    const state = await json(path.join(folder, "state.json"));
    const jobs = await json(path.join(folder, "jobs-exchange.json"));
    const next = [];
    for (const job of jobs) {
      const result = await advanceCase(browser, job, state.round + 1);
      if (result.job) next.push(result.job);
      else state.terminal[job.case_id] = result.terminal;
      console.log(job.case_id, result.terminal ?? result.job.kind);
    }
    state.round += 1;
    await writeFile(
      path.join(folder, "state.json"),
      JSON.stringify(state, null, 2),
    );
    await writeFile(
      path.join(folder, "jobs-exchange.json"),
      JSON.stringify(next, null, 2),
    );
    console.log(
      `Round ${state.round}: ${next.length} MATLAB jobs; ${Object.keys(state.terminal).length}/${caseIds.length} terminal.`,
    );
  }
} finally {
  await browser.close();
}
