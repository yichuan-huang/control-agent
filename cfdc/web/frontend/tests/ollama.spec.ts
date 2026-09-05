import { expect, test } from "@playwright/test";

test("live Ollama interprets a browser reply without persisting credentials", async ({
  page,
}) => {
  test.skip(
    process.env.CFDC_E2E_OLLAMA !== "1",
    "Opt-in local Ollama inference",
  );
  test.setTimeout(240000);
  await page.goto("/new");
  await page.getByRole("button", { name: "设置", exact: true }).click();
  await page.getByLabel("Base URL").fill("http://127.0.0.1:11434/v1");
  await page.getByLabel("Model").fill("gemma4:e4b");
  await page.getByLabel("API Key").fill("ollama");
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
  expect(JSON.stringify(report)).not.toContain("ollama");
  expect(
    await page.evaluate(
      () => JSON.stringify(sessionStorage) + JSON.stringify(localStorage),
    ),
  ).not.toContain("ollama");
});
