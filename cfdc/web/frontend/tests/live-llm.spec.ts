import { expect, test } from "./live-test";

const modelBaseURL = process.env.CFDC_LLM_BASE_URL;
const modelName = process.env.CFDC_LLM_MODEL;
const modelAPIKey = process.env.CFDC_LLM_API_KEY;

test("live LLM interprets a browser reply without persisting credentials", async ({
  page,
}) => {
  test.skip(
    process.env.CFDC_RUN_LIVE_LLM !== "1",
    "Opt-in configured API inference",
  );
  test.setTimeout(240000);
  expect(modelBaseURL, "CFDC_LLM_BASE_URL is required").toBeTruthy();
  expect(Boolean(modelName?.trim()), "CFDC_LLM_MODEL is required").toBe(true);
  expect(Boolean(modelAPIKey?.trim()), "CFDC_LLM_API_KEY is required").toBe(
    true,
  );
  await page.goto("/new");
  await page.getByRole("button", { name: "设置", exact: true }).click();
  await page.getByLabel("Base URL").fill(modelBaseURL!);
  await page.getByLabel("Model").fill(modelName!);
  await page.getByLabel("API Key").fill(modelAPIKey!);
  await page.getByRole("switch", { name: "新任务使用内置知识库" }).uncheck();
  await page.keyboard.press("Escape");
  await page
    .getByLabel("设备与目标")
    .fill("直流电机速度控制：保持目标转速，电压为输入，测量角速度。");
  await page.getByRole("button", { name: "下一步", exact: true }).click();
  await page.getByLabel("输出 1 名称").fill("speed");
  await page.getByLabel("单位", { exact: true }).fill("rad/s");
  await page.getByLabel("输入 1 名称").fill("voltage");
  await page.getByLabel("输入单位").fill("V");
  await page.getByRole("button", { name: "下一步", exact: true }).click();
  await page.getByLabel("输入下限").fill("-1");
  await page.getByLabel("输入上限").fill("1");
  await page.getByLabel("软件试验停止阈值").fill("3");
  await page.getByLabel("参考目标", { exact: true }).fill("1");
  await page
    .getByLabel("评价区域（适用的工作范围）")
    .fill("local operating region");
  await page
    .getByRole("spinbutton", { name: "稳定后允许偏离目标多少", exact: true })
    .fill("0.1");
  await page.getByRole("button", { name: "校验并核对" }).click();
  await page
    .getByRole("checkbox", { name: "我已核对目标、软件试验边界与预算" })
    .check();
  await page.getByRole("button", { name: "确认软件边界并开始" }).click();
  await expect(page).toHaveURL(/\/tasks\/cfdc-v4-/);
  const id = new URL(page.url()).pathname.split("/").at(-1);
  const summary = await (await page.request.get(`/api/v1/tasks/${id}`)).json();
  expect(summary.workspace.action).toBe("answer");
  await page
    .getByLabel("当前步骤回复")
    .fill(
      "开环稳定；没有反向响应；纯延迟不显著；相对阶数较低；传感器和执行器足够；工作区内非线性较弱；对象是单输入单输出；实验间变化较小",
    );
  const submitted = page.waitForResponse(
    (response) =>
      response.url().endsWith(`/tasks/${id}/actions`) &&
      response.request().method() === "POST",
  );
  await page
    .getByRole("button", { name: summary.workspace.action_title, exact: true })
    .click();
  const receipt = await (await submitted).json();
  let operation;
  await expect
    .poll(
      async () => {
        operation = await (
          await page.request.get(`/api/v1/operations/${receipt.operation_id}`)
        ).json();
        return operation.status;
      },
      { timeout: 180000, intervals: [1000, 2000] },
    )
    .toBe("completed");
  const report = await (
    await page.request.get(`/api/v1/tasks/${id}/downloads/report`)
  ).json();
  expect(report.revision).toBeGreaterThan(summary.revision);
  expect(
    report.agent_records.map((record: { role: string }) => record.role),
  ).toEqual(expect.arrayContaining(["diagnosis", "critic"]));
  expect(report.diagnostic.entries).toEqual(
    expect.arrayContaining([
      expect.objectContaining({
        id: "open_loop_stability",
        status: "known",
        assessment: "stable",
      }),
    ]),
  );
  const reportLeaksKey = JSON.stringify(report).includes(modelAPIKey!);
  expect(reportLeaksKey, "Public report must not contain credentials").toBe(
    false,
  );
  const storage = await page.evaluate(
    () => JSON.stringify(sessionStorage) + JSON.stringify(localStorage),
  );
  const storageLeaksKey = storage.includes(modelAPIKey!);
  expect(storageLeaksKey, "Browser storage must not contain credentials").toBe(
    false,
  );
});
