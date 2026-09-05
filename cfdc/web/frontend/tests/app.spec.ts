import { test, expect, type Page } from "@playwright/test";

test("deleted operation releases the wizard after a real 404 and stays cleared on refresh", async ({
  page,
}) => {
  const missingId = "00000000-0000-4000-8000-000000000000";
  await page.goto("/new");
  await page.getByLabel("设备与目标").fill("清理数据后保留的草稿");
  await page.evaluate((id) => {
    sessionStorage.setItem("cfdc:operation:entry:/new", id);
    sessionStorage.setItem(
      "cfdc:operation:task:unrelated",
      "preserve-other-task",
    );
  }, missingId);
  const mutations: string[] = [];
  page.on("request", (request) => {
    if (request.method() === "POST") mutations.push(request.url());
  });
  const missing = page.waitForResponse((response) =>
    response.url().endsWith(`/operations/${missingId}`),
  );
  await page.reload();
  expect((await missing).status()).toBe(404);
  await expect(page.getByText(/操作记录已失效/)).toBeVisible();
  await expect(page.getByLabel("设备与目标")).toBeEnabled();
  await expect(page.getByLabel("设备与目标")).toHaveValue(
    "清理数据后保留的草稿",
  );
  expect(
    await page.evaluate(() =>
      sessionStorage.getItem("cfdc:operation:entry:/new"),
    ),
  ).toBeNull();
  expect(
    await page.evaluate(() =>
      sessionStorage.getItem("cfdc:operation:task:unrelated"),
    ),
  ).toBe("preserve-other-task");
  await page.reload();
  await expect(page.getByLabel("设备与目标")).toBeEnabled();
  await expect(page.getByLabel("设备与目标")).toHaveValue(
    "清理数据后保留的草稿",
  );
  expect(mutations).toEqual([]);
});

async function disableRag(page: Page) {
  await page.getByRole("button", { name: "设置", exact: true }).click();
  await page.getByRole("switch", { name: "新任务使用内置知识库" }).uncheck();
  await page.keyboard.press("Escape");
}

for (const recovery of ["button", "poll"] as const) {
  test(`an operation discovered on a reopened task completes through ${recovery}`, async ({
    page,
  }) => {
    const detail = await (
      await page.request.get("/api/v1/cases/dc_motor_speed_v1")
    ).json();
    let op = await (
      await page.request.post("/api/v1/tasks", {
        data: {
          request_id: crypto.randomUUID(),
          task: detail.task,
          confirmed: false,
          use_rag: false,
        },
      })
    ).json();
    await expect
      .poll(async () => {
        op = await (
          await page.request.get(`/api/v1/operations/${op.operation_id}`)
        ).json();
        return op.status;
      })
      .toBe("completed");
    let pending = true;
    let mutations = 0;
    page.on("request", (request) => {
      if (request.method() === "POST") mutations += 1;
    });
    // Keep the real task/receipt and control only when its completion is visible.
    await page.route(
      `**/api/v1/tasks/${op.session_id}/operations`,
      async (route) => {
        const response = await route.fetch();
        const body = await response.json();
        if (pending)
          body.items = body.items.map((item: typeof op) =>
            item.operation_id === op.operation_id
              ? { ...item, status: "running", result: null }
              : item,
          );
        await route.fulfill({ response, json: body });
      },
    );
    await page.route(
      `**/api/v1/operations/${op.operation_id}`,
      async (route) => {
        pending = false;
        await route.continue();
      },
    );
    await page.goto(`/tasks/${op.session_id}`);
    await expect(page.getByText("此任务有正在执行的操作")).toBeVisible();
    if (recovery === "button") {
      await page.getByRole("button", { name: "恢复操作跟踪" }).click();
      await expect(page.getByText("操作：已完成")).toBeVisible();
    } else {
      pending = false;
    }
    await expect(page.getByText("此任务有正在执行的操作")).not.toBeVisible();
    expect(mutations).toBe(0);
  });
}

test("real API cases, locked review and clone preserve guided fields", async ({
  page,
}) => {
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "把控制目标，变成可验证的结果。" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "从案例开始" }).click();
  await page.locator("[data-testid=case-open]").first().click();
  await expect(page.getByText("案例参数已锁定")).toBeVisible();
  await page.getByRole("button", { name: "复制为我的任务" }).click();
  await expect(page.getByLabel("设备与目标")).not.toHaveValue("");
});
test("mobile guided draft survives reload, credentials do not persist", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/new");
  await page.getByLabel("设备与目标").fill("自定义温控任务");
  await page.getByRole("button", { name: "下一步", exact: true }).click();
  await page.reload();
  await expect(page.getByLabel("输出 1 名称")).toBeVisible();
  await page.getByRole("button", { name: "上一步", exact: true }).click();
  await expect(page.getByLabel("设备与目标")).toHaveValue("自定义温控任务");
  await expect(page.locator("body")).toHaveJSProperty("scrollWidth", 390);
  await page.getByRole("button", { name: "设置", exact: true }).click();
  await page.getByLabel("API Key").fill("temporary-test-key");
  expect(
    await page.evaluate(
      () => JSON.stringify(sessionStorage) + JSON.stringify(localStorage),
    ),
  ).not.toContain("temporary-test-key");
});

test("settings drawer stays inside the viewport when resized and opened at 390px", async ({
  page,
}) => {
  async function expectDrawerInsideViewport(
    expectedWidth: number,
    settle: "animation" | "layout" = "animation",
  ) {
    const dialog = page.getByRole("dialog", { name: "设置" });
    const panel = page.locator(".ant-drawer-content-wrapper");
    await expect(dialog).toBeVisible();
    if (settle === "animation") await page.waitForTimeout(500);
    else
      await page.evaluate(
        () =>
          new Promise<void>((resolve) =>
            requestAnimationFrame(() => resolve()),
          ),
      );
    const box = await panel.boundingBox();
    expect(box).toBeTruthy();
    expect(box!.x).toBeGreaterThanOrEqual(0);
    expect(box!.x + box!.width).toBeLessThanOrEqual(expectedWidth);
  }

  await page.setViewportSize({ width: 1280, height: 844 });
  await page.goto("/");
  await page.getByRole("button", { name: "设置", exact: true }).click();
  await expectDrawerInsideViewport(1280);

  await page.setViewportSize({ width: 390, height: 844 });
  await expectDrawerInsideViewport(390, "layout");
  await page.keyboard.press("Escape");
  await page.getByRole("button", { name: "设置", exact: true }).click();
  await expectDrawerInsideViewport(390);
  await expect(page.getByLabel("API Key")).toBeVisible();
  await page.getByRole("button", { name: "高级设置" }).click();
  await expect(
    page.getByRole("button", { name: "从启动环境导入地址和模型" }),
  ).toBeVisible();
});

test("environment settings refresh the real API and retain the in-memory key", async ({
  page,
}) => {
  const environment = await (await page.request.get("/api/v1/config")).json();
  await page.goto("/");
  await page.getByRole("button", { name: "设置", exact: true }).click();
  await page.getByLabel("Base URL").fill("https://current.example/v1");
  await page.getByLabel("Model").fill("current-model");
  await page.getByLabel("API Key").fill("temporary-browser-key");

  const refreshed = page.waitForResponse(
    (response) =>
      new URL(response.url()).pathname === "/api/v1/config" && response.ok(),
  );
  await page.getByRole("button", { name: "高级设置" }).click();
  await page.getByRole("button", { name: "从启动环境导入地址和模型" }).click();
  await refreshed;

  await expect(page.getByLabel("Base URL")).toHaveValue(
    environment.base_url || "https://current.example/v1",
  );
  await expect(page.getByLabel("Model")).toHaveValue(
    environment.model || "current-model",
  );
  await expect(page.getByLabel("API Key")).toHaveValue("temporary-browser-key");
  await expect(
    page.getByText(
      environment.base_url && environment.model
        ? "已应用环境中的 Base URL 和 Model。"
        : environment.base_url || environment.model
          ? `环境未提供 ${environment.base_url ? "Model" : "Base URL"}，已保留当前值。`
          : "启动环境没有预设地址和模型，表单内容未更改。",
    ),
  ).toBeVisible();
});

test("custom wizard validates field focus then creates a revisioned task", async ({
  page,
}) => {
  await page.goto("/new");
  await page.getByLabel("设备与目标").fill("测试加热器保持温度");
  await page.getByRole("button", { name: "下一步", exact: true }).click();
  await page.getByLabel("输出 1 名称").fill("temperature");
  await page.getByLabel("单位", { exact: true }).fill("C");
  await page.getByLabel("输入 1 名称").fill("power");
  await page.getByLabel("输入单位").fill("W");
  await page.getByRole("button", { name: "下一步", exact: true }).click();
  await page.getByRole("button", { name: "校验并核对" }).click();
  await expect(page.getByLabel("输入下限")).toBeFocused();
  await page.getByLabel("输入下限").fill("0");
  await page.getByLabel("输入上限").fill("100");
  await page.getByLabel("软件试验停止阈值").fill("100");
  await page.getByRole("button", { name: "校验并核对" }).click();
  await page
    .getByRole("checkbox", { name: "我已核对目标、软件试验边界与预算" })
    .check();
  const resumed = page.waitForResponse((r) =>
    r.url().includes("/drafts/validate"),
  );
  await page.reload();
  expect((await resumed).ok()).toBe(true);
  await expect(
    page.getByText("实际应用预算（未填写项沿用内核默认）"),
  ).toBeVisible();
  await expect(
    page.getByRole("checkbox", { name: "我已核对目标、软件试验边界与预算" }),
  ).not.toBeChecked();
  await disableRag(page);
  await page
    .getByRole("checkbox", { name: "我已核对目标、软件试验边界与预算" })
    .check();
  await page.getByRole("button", { name: "确认软件边界并开始" }).click();
  await expect(page).toHaveURL(/\/tasks\//, { timeout: 30000 });
  await expect(page.getByText(/修订 \d+/)).toBeVisible();
  await page.getByRole("button", { name: "不知道 / 没有测过" }).click();
  await expect(page.getByLabel("当前步骤回复")).toHaveValue(
    "对于当前问题，我不知道或没有测过。",
  );
  await page.getByLabel("当前步骤回复").fill("暂时不知道，请保留我的草稿");
  await page.getByRole("button", { name: "补充已知现象", exact: true }).click();
  await expect(page.getByText(/此步骤需要模型/)).toBeVisible();
  await expect(page.getByLabel("当前步骤回复")).toHaveValue(
    "暂时不知道，请保留我的草稿",
  );
});

test("artifact browser loads only bounded nodes on demand and real downloads work", async ({
  page,
}) => {
  const requests: string[] = [];
  page.on("request", (r) => requests.push(r.url()));
  await page.goto("/cases");
  await page.locator("[data-testid=case-open]").first().click();
  await disableRag(page);
  await page
    .getByRole("checkbox", { name: "我已核对目标、软件试验边界与预算" })
    .check();
  await page.getByRole("button", { name: "确认软件边界并开始" }).click();
  await expect(page).toHaveURL(/\/tasks\//, { timeout: 30000 });
  expect(requests.filter((u) => u.includes("/artifacts"))).toHaveLength(0);
  await page.getByRole("button", { name: "专家工具", exact: true }).click();
  await expect(
    page.getByRole("columnheader", { name: "字段", exact: true }),
  ).toBeVisible();
  await expect
    .poll(() =>
      requests.some((u) => u.includes("/node?") && u.includes("limit=50")),
    )
    .toBe(true);
  const downloadEvent = page.waitForEvent("download");
  await page.getByRole("link", { name: "下载完整产物" }).click();
  expect((await downloadEvent).suggestedFilename()).toMatch(/json$/);
});

test("refresh recovers the operation receipt without replaying task creation", async ({
  page,
}) => {
  let creations = 0;
  page.on("request", (r) => {
    if (r.method() === "POST" && new URL(r.url()).pathname === "/api/v1/tasks")
      creations++;
  });
  await page.route("**/api/v1/operations/*", async (route) => {
    const response = await route.fetch();
    await new Promise((resolve) => setTimeout(resolve, 350));
    await route.fulfill({ response });
  });
  await page.goto("/cases");
  await page.locator("[data-testid=case-open]").first().click();
  await disableRag(page);
  await page
    .getByRole("checkbox", { name: "我已核对目标、软件试验边界与预算" })
    .check();
  const receipt = page.waitForResponse(
    (r) =>
      new URL(r.url()).pathname === "/api/v1/tasks" &&
      r.request().method() === "POST",
  );
  await page.getByRole("button", { name: "确认软件边界并开始" }).click();
  await receipt;
  await expect
    .poll(() =>
      page.evaluate(() =>
        sessionStorage.getItem(
          `cfdc:operation:entry:${location.pathname}${location.search}`,
        ),
      ),
    )
    .toBeTruthy();
  await page.reload();
  await expect(page).toHaveURL(/\/tasks\//, { timeout: 30000 });
  expect(creations).toBe(1);
});

test("expert contract creation stays unconfirmed and receives no case permissions", async ({
  page,
}) => {
  const catalog = await (await page.request.get("/api/v1/cases")).json();
  const detail = await (
    await page.request.get(`/api/v1/cases/${catalog.items[0].id}`)
  ).json();
  await page.goto("/");
  await disableRag(page);
  await page.getByRole("button", { name: "导入 / 专家" }).click();
  await page.getByLabel("专家 JSON").fill(JSON.stringify(detail.task));
  await page
    .getByRole("button", { name: "创建未确认任务", exact: true })
    .click();
  await expect(page).toHaveURL(/\/tasks\//, { timeout: 30000 });
  const summary = await (
    await page.request.get(
      `/api/v1/tasks/${new URL(page.url()).pathname.split("/").at(-1)}`,
    )
  ).json();
  expect(summary.revision).toBe(1);
  expect(summary.workspace.action).toBe("confirm_task");
  expect(summary.registered_case_id).toBeNull();
});

test("opening another task clears the previous task reply", async ({
  page,
}) => {
  const cases = await (await page.request.get("/api/v1/cases")).json();
  const detail = await (
    await page.request.get(`/api/v1/cases/${cases.items[0].id}`)
  ).json();
  async function create() {
    const response = await page.request.post("/api/v1/tasks", {
      data: {
        request_id: crypto.randomUUID(),
        task: detail.task,
        confirmed: true,
        use_rag: false,
      },
    });
    expect(response.status()).toBe(202);
    const operation = await response.json();
    let completed = operation;
    await expect
      .poll(
        async () => {
          completed = await (
            await page.request.get(
              `/api/v1/operations/${operation.operation_id}`,
            )
          ).json();
          return completed.status;
        },
        { timeout: 30000 },
      )
      .toBe("completed");
    return completed.session_id as string;
  }
  const first = await create();
  const second = await create();
  await page.goto(`/tasks/${first}`);
  await page.getByLabel("当前步骤回复").fill("只属于任务 A 的草稿");
  await page.getByRole("button", { name: "打开任务", exact: true }).click();
  await page.getByLabel("任务 ID").fill(second);
  await page.getByLabel("任务 ID").press("Enter");
  await expect(page).toHaveURL(new RegExp(second));
  await expect(page.getByLabel("当前步骤回复")).toHaveValue("");
  await page
    .getByRole("button", { name: "实验协议与上传回执", exact: true })
    .click();
  await expect(page.getByText("下载协议", { exact: true })).toBeVisible();
});

test("accepted experiment curve loads lazily and graph zoom requests a real window", async ({
  page,
}) => {
  await page.goto("/new?case=dc_motor_speed_v1");
  await disableRag(page);
  await page
    .getByRole("checkbox", { name: "我已核对目标、软件试验边界与预算" })
    .check();
  await page.getByRole("button", { name: "确认软件边界并开始" }).click();
  await expect(page).toHaveURL(/\/tasks\//, { timeout: 30000 });
  const urls: string[] = [];
  page.on("request", (r) => {
    if (r.url().includes("/evidence/curves?")) urls.push(r.url());
  });
  await page
    .getByRole("button", { name: "实验协议与上传回执", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "已通过的实验数据" }),
  ).toBeVisible();
  expect(urls).toHaveLength(0);
  const initialResponse = page.waitForResponse((r) =>
    r.url().includes("/evidence/curves?"),
  );
  await page
    .getByRole("button", { name: "查看通过数据曲线", exact: true })
    .click();
  const initial = await (await initialResponse).json();
  expect(initial.stage).toBe("evidence");
  const drag = page
    .getByTestId("evidence-curves")
    .locator(".js-plotly-plot .nsewdrag")
    .first();
  await drag.scrollIntoViewIfNeeded();
  const box = await drag.boundingBox();
  expect(box).toBeTruthy();
  const zoomResponse = page.waitForResponse(
    (r) =>
      r.url().includes("/evidence/curves?") &&
      new URL(r.url()).searchParams.has("start"),
  );
  await page.mouse.move(box!.x + box!.width * 0.2, box!.y + box!.height * 0.2);
  await page.mouse.down();
  await page.mouse.move(box!.x + box!.width * 0.7, box!.y + box!.height * 0.7, {
    steps: 10,
  });
  await page.mouse.up();
  const response = await zoomResponse;
  const zoomed = await response.json();
  expect(zoomed.stage).toBe("evidence");
  expect(zoomed.protocol_fingerprint).toBe(initial.protocol_fingerprint);
  expect(zoomed.fingerprint).toBe(initial.fingerprint);
  expect(new URL(response.url()).searchParams.has("end")).toBe(true);
  await page.waitForTimeout(300);
  expect(urls).toHaveLength(2);
});

test("pending task operation stays scoped across navigation and refresh", async ({
  page,
}) => {
  const detail = await (
    await page.request.get("/api/v1/cases/dc_motor_speed_v1")
  ).json();
  async function create() {
    const receipt = await (
      await page.request.post("/api/v1/tasks", {
        data: {
          request_id: crypto.randomUUID(),
          task: detail.task,
          confirmed: false,
          use_rag: false,
        },
      })
    ).json();
    let op = receipt;
    await expect
      .poll(async () => {
        op = await (
          await page.request.get(`/api/v1/operations/${receipt.operation_id}`)
        ).json();
        return op.status;
      })
      .toBe("completed");
    return op.session_id as string;
  }
  const a = await create(),
    b = await create();
  await page.goto(`/tasks/${a}`);
  let release!: () => void;
  const gate = new Promise<void>((resolve) => {
    release = resolve;
  });
  await page.route("**/api/v1/operations/*", async (route) => {
    const response = await route.fetch();
    await gate;
    await route.fulfill({ response });
  });
  const summary = await (await page.request.get(`/api/v1/tasks/${a}`)).json();
  await page
    .getByRole("checkbox", { name: "我已核对软件试验边界与预算" })
    .check();
  await page
    .getByRole("button", { name: summary.workspace.action_title, exact: true })
    .click();
  await expect
    .poll(() =>
      page.evaluate(
        (id) => sessionStorage.getItem(`cfdc:operation:task:${id}`),
        a,
      ),
    )
    .toBeTruthy();
  await page.reload();
  await expect(page.getByText("无法读取操作状态")).not.toBeVisible();
  await page.getByRole("button", { name: "打开任务", exact: true }).click();
  await page.getByLabel("任务 ID").fill(b);
  await page.getByLabel("任务 ID").press("Enter");
  await expect(page).toHaveURL(new RegExp(b));
  await expect(page.getByText(/操作：/)).not.toBeVisible();
  await page
    .getByRole("checkbox", { name: "我已核对软件试验边界与预算" })
    .check();
  await expect(
    page.getByRole("button", {
      name: summary.workspace.action_title,
      exact: true,
    }),
  ).toBeEnabled();
  release();
  await page.waitForTimeout(1200);
  await expect(page).toHaveURL(new RegExp(b));
  await page.goto(`/tasks/${a}`);
  await expect(page.getByText("操作：已完成")).toBeVisible();
  await expect
    .poll(() =>
      page.evaluate(
        (id) => sessionStorage.getItem(`cfdc:operation:task:${id}`),
        a,
      ),
    )
    .toBeNull();
});

test("case evidence choice survives refresh independently of custom draft", async ({
  page,
}) => {
  await page.goto("/new?case=dc_motor_speed_v1");
  await page.getByLabel("证据模式").click();
  await page.getByText("教学练习包上传", { exact: true }).click();
  await page
    .getByRole("checkbox", { name: "我已核对目标、软件试验边界与预算" })
    .check();
  await page.reload();
  await expect(page.getByText("教学练习包上传", { exact: true })).toBeVisible();
  await expect(
    page.getByRole("checkbox", { name: "我已核对目标、软件试验边界与预算" }),
  ).not.toBeChecked();
  await page.getByRole("button", { name: "复制为我的任务" }).click();
  await expect(page.getByLabel("设备与目标")).toBeVisible();
});

for (const reload of [false, true])
  test(`import from task drawer opens imported task (refresh=${reload})`, async ({
    page,
  }) => {
    const detail = await (
      await page.request.get("/api/v1/cases/dc_motor_speed_v1")
    ).json();
    let op = await (
      await page.request.post("/api/v1/tasks", {
        data: {
          request_id: crypto.randomUUID(),
          task: detail.task,
          confirmed: false,
          use_rag: false,
        },
      })
    ).json();
    await expect
      .poll(async () => {
        op = await (
          await page.request.get(`/api/v1/operations/${op.operation_id}`)
        ).json();
        return op.status;
      })
      .toBe("completed");
    const a = op.session_id;
    const zip = await (
      await page.request.get(`/api/v1/tasks/${a}/downloads/bundle`)
    ).body();
    await page.goto(`/tasks/${a}`);
    await page.getByRole("button", { name: "专家工具", exact: true }).click();
    await page.getByRole("tab", { name: "历史公开包导入" }).click();
    let release!: () => void;
    const gate = new Promise<void>((resolve) => {
      release = resolve;
    });
    await page.route("**/api/v1/operations/*", async (route) => {
      const response = await route.fetch();
      await gate;
      await route.fulfill({ response });
    });
    await page.locator('input[type="file"]').setInputFiles({
      name: "public.zip",
      mimeType: "application/zip",
      buffer: zip,
    });
    await expect
      .poll(() =>
        page.evaluate(
          (id) => sessionStorage.getItem(`cfdc:operation:entry:/tasks/${id}`),
          a,
        ),
      )
      .toBeTruthy();
    expect(
      await page.evaluate(
        (id) => sessionStorage.getItem(`cfdc:operation:task:${id}`),
        a,
      ),
    ).toBeNull();
    if (reload) {
      await page.reload();
      await expect(page.getByRole("dialog")).toBeVisible();
    }
    release();
    await expect
      .poll(() => new URL(page.url()).pathname)
      .not.toBe(`/tasks/${a}`);
    const b = new URL(page.url()).pathname.split("/").at(-1);
    const summary = await (await page.request.get(`/api/v1/tasks/${b}`)).json();
    expect(summary.workspace.action).toBe("confirm_task");
    expect(summary.rag_snapshot).toBeNull();
  });

test("pending creation cannot cross same-path different-case navigation", async ({
  page,
}) => {
  const catalog = await (await page.request.get("/api/v1/cases")).json();
  const other = catalog.items.find(
    (item: { id: string }) => item.id !== "dc_motor_speed_v1",
  ).id;
  await page.goto("/new?case=dc_motor_speed_v1");
  await disableRag(page);
  let release!: () => void;
  const gate = new Promise<void>((resolve) => {
    release = resolve;
  });
  await page.route("**/api/v1/operations/*", async (route) => {
    const response = await route.fetch();
    await gate;
    await route.fulfill({ response });
  });
  await page
    .getByRole("checkbox", { name: "我已核对目标、软件试验边界与预算" })
    .check();
  await page.getByRole("button", { name: "确认软件边界并开始" }).click();
  await expect
    .poll(() =>
      page.evaluate(() =>
        sessionStorage.getItem(
          "cfdc:operation:entry:/new?case=dc_motor_speed_v1",
        ),
      ),
    )
    .toBeTruthy();
  await page.goto(`/new?case=${other}`);
  await expect(page.getByText(/操作：/)).not.toBeVisible();
  await page
    .getByRole("checkbox", { name: "我已核对目标、软件试验边界与预算" })
    .check();
  await expect(
    page.getByRole("button", { name: "确认软件边界并开始" }),
  ).toBeEnabled();
  release();
  await page.waitForTimeout(1000);
  await expect(page).toHaveURL(new RegExp(`case=${other}`));
  await page.goto("/new?case=dc_motor_speed_v1");
  await expect(page).toHaveURL(/\/tasks\//, { timeout: 30000 });
});
