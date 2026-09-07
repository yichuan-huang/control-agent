import { test, expect, type Page } from "@playwright/test";
async function completed(
  page: Page,
  response: { json: () => Promise<Record<string, unknown>> },
) {
  let operation = await response.json();
  await expect
    .poll(async () => {
      operation = await (
        await page.request.get(`/api/v1/operations/${operation.operation_id}`)
      ).json();
      return operation.status;
    })
    .toBe("completed");
  return operation;
}
test("external source and checklist survive refresh; recovery opens a new task without changing its parent", async ({
  page,
}) => {
  const task = {
    description: "External intensity control",
    task_type: "local_setpoint_hold",
    measured_signals: ["intensity"],
    control_input: "led_current",
    reference: 0.5,
    input_min: -1,
    input_max: 1,
    state_stop: 3,
    operating_region: "local",
    success_requirements: { final_abs_error_max: 0.1 },
    budgets: {
      evaluation_sample_time_s: 0.02,
      evaluation_horizon_s: 20,
      evaluation_repeats: 20,
    },
  };
  const created = await completed(
    page,
    await page.request.post("/api/v1/tasks", {
      data: {
        request_id: crypto.randomUUID(),
        task,
        confirmed: true,
        use_rag: false,
      },
    }),
  );
  const id = String(created.session_id);
  const summary = await (await page.request.get(`/api/v1/tasks/${id}`)).json();
  const assessments = {
    open_loop_stability: "stable",
    nonminimum_phase: "minimum_phase",
    significant_delay: "not_significant",
    relative_degree: "low",
    sensing_actuation_adequacy: "adequate",
    nonlinearity_strength: "weak",
    coupling_underactuation: "siso",
    uncertainty_variation: "small",
  };
  const answer = Object.fromEntries(
    Object.entries(assessments).map(([key, value]) => [
      key,
      {
        status: "known",
        assessment: value,
        evidence: "Synthetic fixture observation",
        confidence: 1,
      },
    ]),
  );
  await completed(
    page,
    await page.request.post(`/api/v1/tasks/${id}/actions`, {
      data: {
        request_id: crypto.randomUUID(),
        expected_revision: summary.revision,
        action: "answer",
        input: { mode: "json", text: JSON.stringify(answer) },
      },
    }),
  );
  await page.goto(`/tasks/${id}`);
  await page.getByRole("button", { name: "继续下一步", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "确认数据来源" }),
  ).toBeVisible();
  await page.getByLabel("外部软件仿真", { exact: true }).check();
  await page.getByRole("button", { name: "确认数据来源" }).click();
  await expect(
    page.getByRole("radio", { name: "检查完成，可以继续" }),
  ).toBeVisible();
  await expect(
    page.getByRole("link", { name: "下载操作包", exact: true }),
  ).toBeVisible();
  await page.reload();
  await expect(
    page.getByRole("radio", { name: "检查完成，可以继续" }),
  ).toBeVisible();
  await expect(
    page.getByText("打开专业 JSON 提交", { exact: true }),
  ).toHaveCount(0);
  const primary = await page
    .getByRole("button", { name: "确认操作检查", exact: true })
    .boundingBox();
  const recovery = await page
    .getByRole("button", { name: "重新采集并创建新任务" })
    .boundingBox();
  expect(primary).toBeTruthy();
  expect(recovery).toBeTruthy();
  expect(recovery!.y).toBeGreaterThan(primary!.y);
  await expect(page.getByText(/候选预算/)).toHaveCount(0);
  await page.screenshot({
    path: "../../../output/external-implementation/browser-ui/source-checklist.png",
    fullPage: true,
  });
  const before = await (await page.request.get(`/api/v1/tasks/${id}`)).json();
  await page.getByRole("button", { name: "重新采集并创建新任务" }).click();
  await expect
    .poll(() => new URL(page.url()).pathname)
    .not.toBe(`/tasks/${id}`);
  const after = await (await page.request.get(`/api/v1/tasks/${id}`)).json();
  expect(after.revision).toBe(before.revision);
  expect(after.external_workflow).toEqual(before.external_workflow);
  await expect(
    page.getByRole("heading", { name: /核对|任务|诊断|结构/ }).first(),
  ).toBeVisible();
  await page.screenshot({
    path: "../../../output/external-implementation/browser-ui/recovered-task.png",
    fullPage: true,
  });
});

for (const kind of ["transition", "disturbance"] as const) {
  test(`custom ${kind} wizard reviews all freeze settings before confirmation`, async ({
    page,
  }) => {
    await page.goto("/new");
    await page.getByLabel("设备与目标").fill("Synthetic external control task");
    await page.getByLabel("任务类型", { exact: true }).click();
    await page
      .getByText(
        kind === "transition" ? "变化到新目标后保持" : "受到扰动后恢复并保持",
        { exact: true },
      )
      .click();
    if (kind === "transition") {
      await page.getByLabel("开始区域", { exact: true }).fill("near zero");
      await page.getByLabel("目标区域", { exact: true }).fill("near 0.5");
      await page.getByLabel("初始输出值", { exact: true }).fill("0");
      await page.getByLabel("中间目标（逗号分隔）").fill("0.2");
      await page.getByLabel("最少验证阶段切换次数").fill("2");
    } else {
      await page
        .getByLabel("扰动事件", { exact: true })
        .fill("brief input pulse");
      await page.getByLabel("恢复起点", { exact: true }).fill("pulse ends");
      await page.getByLabel("恢复后保持区域", { exact: true }).fill("near 0.5");
      await page.getByLabel("扰动输入通道名称").fill("u");
      await page.getByLabel("扰动开始时间 (s)").fill("1");
      await page.getByLabel("扰动幅度（输入单位）").fill("0.1");
      await page.getByLabel("扰动持续时间 (s)").fill("1");
    }
    await page.getByRole("button", { name: "下一步", exact: true }).click();
    await page.getByLabel("输出 1 名称").fill("y");
    await page.getByLabel("单位", { exact: true }).fill("m");
    await page.getByLabel("输入 1 名称").fill("u");
    await page.getByLabel("输入单位", { exact: true }).fill("V");
    await page.getByRole("button", { name: "下一步", exact: true }).click();
    await page.getByLabel("输入下限").fill("-1");
    await page.getByLabel("输入上限").fill("1");
    await page.getByLabel("软件试验停止阈值").fill("3");
    await page.getByLabel("参考目标", { exact: true }).fill("0.5");
    await page
      .getByLabel("评价区域（适用的工作范围）")
      .fill("local operating region");
    await page
      .getByRole("spinbutton", { name: "稳定后允许偏离目标多少", exact: true })
      .fill("0.1");
    await page.getByText("性能要求与预算（可选）", { exact: true }).click();
    const overshoot = page.getByRole("checkbox", {
      name: "允许超过目标多少",
      exact: true,
    });
    // This Form-controlled group commits after the pointer event returns.
    await overshoot.click();
    await expect(overshoot).toBeChecked();
    await page
      .getByRole("spinbutton", { name: "允许超过目标多少", exact: true })
      .fill("0.1");
    await page.getByRole("button", { name: "校验并核对" }).click();
    await expect(page.getByText("任务核对", { exact: true })).toBeVisible();
    await expect(
      page.getByRole("button", { name: "确认软件边界并开始" }),
    ).toBeDisabled();
    await expect(
      page
        .getByText(
          kind === "transition"
            ? "到达目标时间上限 (s)"
            : "扰动开始 / 持续时间 (s)",
          { exact: true },
        )
        .last(),
    ).toBeVisible();
    await page.screenshot({
      path: `../../../output/external-implementation/browser-ui/${kind}-review.png`,
      fullPage: true,
    });
  });
}
