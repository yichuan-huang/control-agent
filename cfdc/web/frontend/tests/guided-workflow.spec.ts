import { test, expect } from "@playwright/test";

test("legacy automatic task preserves recovery guidance across reload without executing", async ({
  page,
}) => {
  let operation = await (
    await page.request.post("/api/v1/tasks", {
      data: {
        request_id: crypto.randomUUID(),
        task: {
          description: "Managed UI progress fixture",
          measured_signals: ["y"],
          control_input: "u",
          input_min: -1,
          input_max: 1,
          state_stop: 3,
        },
        confirmed: false,
        use_rag: false,
      },
    })
  ).json();
  await expect
    .poll(async () => {
      operation = await (
        await page.request.get(`/api/v1/operations/${operation.operation_id}`)
      ).json();
      return operation.status;
    })
    .toBe("completed");
  const id = operation.session_id;
  const original = await (await page.request.get(`/api/v1/tasks/${id}`)).json();
  const mutations: string[] = [];
  page.on("request", (request) => {
    if (request.method() === "POST") mutations.push(request.url());
  });
  // A persisted legacy task is read-only; it must never restart on page load.
  await page.route(`**/api/v1/tasks/${id}`, (route) =>
    route.fulfill({
      json: {
        ...original,
        external_workflow: {
          source_kind: "software",
          recovery_required: true,
          recovery_available: true,
          recovery_reason: "旧自动执行任务已停止，请创建新任务重新采集。",
        },
        read_only: true,
        workspace: { ...original.workspace, action: "", actionable: false },
      },
    }),
  );
  await page.goto(`/tasks/${id}`);
  await expect(page.getByText(/旧自动执行任务已停止/)).toBeVisible();
  await expect(
    page.getByRole("button", { name: "重新采集并创建新任务" }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: /暂停自动|继续自动|选择完整结果 ZIP/ }),
  ).toHaveCount(0);
  await page.reload();
  await expect(page.getByText(/旧自动执行任务已停止/)).toBeVisible();
  expect(mutations).toEqual([]);
});

test("custom wizard restores only task details and has no execution or apparatus selector", async ({
  page,
}) => {
  await page.goto("/new");
  await page.evaluate(() =>
    sessionStorage.setItem(
      "cfdc:draft",
      JSON.stringify({
        description: "我的外部系统",
        execution_mode: "managed",
        runner_id: "local_python",
        model_id: "optical",
      }),
    ),
  );
  await page.reload();
  await expect(page.getByLabel("设备与目标")).toHaveValue("我的外部系统");
  await expect(page.getByText(/实际试验在应用外部完成/)).toBeVisible();
  await expect(
    page.getByRole("radio", { name: /自动运行|手动运行|光学|真空|墨水/ }),
  ).toHaveCount(0);
});
