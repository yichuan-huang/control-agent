import { expect, test, type Response, type Page } from "@playwright/test";

type Operation = {
  operation_id: string;
  status: string;
  error?: unknown;
  session_id?: string;
};

type Summary = {
  status: string;
  workspace: {
    action: string | null;
    action_title: string;
    actionable: boolean;
    title: string;
  };
  task: {
    success_requirements: { hold_duration_min_s?: number };
  };
};

type Evaluation = {
  status: string;
  performance_gate: { passed: boolean };
};

type Report = {
  status: string;
  registered_case_binding: { case_id: string };
  evidence: unknown[];
  qualification: { status: string };
  input_contract: { action: string | null };
  evaluation: Evaluation;
  confirmation?: { status: string };
  tuning?: { status: string; reason: string };
  evaluation_packets: Array<{ evaluation_split: string }>;
  evaluation_replays: Array<{ matches_previous: boolean }>;
};

type CaseFlow = {
  caseId: string;
  initialStatus: string;
  actions: Array<{ from: string; action: string; to: string }>;
  finalStatus: "capability_gap" | "performance_met";
  qualification: string;
};

const cases: CaseFlow[] = [
  {
    caseId: "dc_motor_speed_v1",
    initialStatus: "tuning_eligible",
    actions: [
      {
        from: "tuning_eligible",
        action: "run_feedback_iteration",
        to: "capability_gap",
      },
    ],
    finalStatus: "capability_gap",
    qualification: "offline_qualified",
  },
  {
    caseId: "dc_motor_position_v1",
    initialStatus: "capability_gap",
    actions: [],
    finalStatus: "capability_gap",
    qualification: "diagnostic_trial_only",
  },
  {
    caseId: "tclab_single_heater_v1",
    initialStatus: "tuning_eligible",
    actions: [
      {
        from: "tuning_eligible",
        action: "run_feedback_iteration",
        to: "awaiting_confirmation",
      },
      {
        from: "awaiting_confirmation",
        action: "confirm_result",
        to: "performance_met",
      },
    ],
    finalStatus: "performance_met",
    qualification: "offline_qualified",
  },
  {
    caseId: "quadruple_tank_nmp_v1",
    initialStatus: "performance_met",
    actions: [],
    finalStatus: "performance_met",
    qualification: "offline_qualified",
  },
  {
    caseId: "tclab_dual_heater_v1",
    initialStatus: "performance_met",
    actions: [],
    finalStatus: "performance_met",
    qualification: "offline_qualified",
  },
];

async function getJson<T>(page: Page, path: string): Promise<T> {
  // Retry one reset connection on read-only requests, never a task mutation.
  // Playwright still fails HTTP errors and a second ECONNRESET.
  const response = await page.request.get(path, { maxRetries: 1 });
  expect(response.ok(), `${path} returned ${response.status()}`).toBe(true);
  return response.json() as Promise<T>;
}

async function waitForCompletedOperation(
  page: Page,
  response: Response,
): Promise<Operation> {
  expect(response.status()).toBe(202);
  const receipt = (await response.json()) as Operation;
  let operation = receipt;
  await expect
    .poll(
      async () => {
        operation = await getJson<Operation>(
          page,
          `/api/v1/operations/${receipt.operation_id}`,
        );
        return operation.status;
      },
      { timeout: 60_000, intervals: [200, 400, 800] },
    )
    .toBe("completed");
  expect(operation.error).toBeFalsy();
  return operation;
}

async function disableRag(page: Page) {
  await page.getByRole("button", { name: "设置", exact: true }).click();
  await page.getByRole("switch", { name: "新任务使用内置知识库" }).uncheck();
  await page.keyboard.press("Escape");
}

async function expectWorkspaceState(
  page: Page,
  sessionId: string,
  expectedStatus: string,
): Promise<Summary> {
  const summary = await getJson<Summary>(page, `/api/v1/tasks/${sessionId}`);
  expect(summary.status).toBe(expectedStatus);
  if (summary.workspace.actionable) {
    await expect(
      page.getByRole("button", {
        name: summary.workspace.action_title,
        exact: true,
      }),
    ).toBeVisible({ timeout: 10_000 });
  } else {
    await expect(
      page.getByRole("heading", {
        name: summary.workspace.title,
        exact: true,
      }),
    ).toBeVisible({ timeout: 10_000 });
  }
  return summary;
}

for (const flow of cases) {
  test(`${flow.caseId} reaches its locked terminal result and refreshes the workspace`, async ({
    page,
  }) => {
    test.setTimeout(120_000);
    const pageErrors: string[] = [];
    let taskReads = 0;
    page.on("pageerror", (error) => pageErrors.push(error.message));
    page.on("request", (request) => {
      const path = new URL(request.url()).pathname;
      if (request.method() === "GET" && /^\/api\/v1\/tasks\/[^/]+$/.test(path))
        taskReads += 1;
    });

    await page.goto(`/new?case=${flow.caseId}`);
    await disableRag(page);
    await expect(page.getByText("案例参数已锁定")).toBeVisible();
    await page
      .getByRole("checkbox", { name: "我已核对目标、软件试验边界与预算" })
      .check();
    const creationResponse = page.waitForResponse(
      (response) =>
        new URL(response.url()).pathname === "/api/v1/tasks" &&
        response.request().method() === "POST",
    );
    await page.getByRole("button", { name: "确认软件边界并开始" }).click();
    const created = await waitForCompletedOperation(
      page,
      await creationResponse,
    );
    expect(created.session_id).toBeTruthy();
    const sessionId = created.session_id!;
    await expect(page).toHaveURL(new RegExp(`/tasks/${sessionId}$`), {
      timeout: 10_000,
    });
    let summary = await expectWorkspaceState(
      page,
      sessionId,
      flow.initialStatus,
    );

    for (const step of flow.actions) {
      expect(summary.status).toBe(step.from);
      expect(summary.workspace.action).toBe(step.action);
      const actionResponse = page.waitForResponse(
        (response) =>
          new URL(response.url()).pathname ===
            `/api/v1/tasks/${sessionId}/actions` &&
          response.request().method() === "POST",
      );
      await page
        .getByRole("button", {
          name: summary.workspace.action_title,
          exact: true,
        })
        .click();
      await waitForCompletedOperation(page, await actionResponse);
      summary = await expectWorkspaceState(page, sessionId, step.to);
    }

    const report = await getJson<Report>(
      page,
      `/api/v1/tasks/${sessionId}/downloads/report`,
    );
    expect(report.status).toBe(flow.finalStatus);
    expect(report.registered_case_binding.case_id).toBe(flow.caseId);
    expect(report.evidence).toHaveLength(3);
    expect(report.qualification.status).toBe(flow.qualification);
    expect(report.input_contract.action).toBeNull();

    if (flow.finalStatus === "performance_met") {
      expect(report.evaluation.status).toBe("performance_met");
      expect(report.evaluation.performance_gate.passed).toBe(true);
    }
    if (flow.caseId === "dc_motor_speed_v1") {
      expect(report.tuning?.status).toBe("exhausted");
      expect(report.tuning?.reason).toBe("no_strict_development_improvement");
    }
    if (flow.caseId === "tclab_single_heater_v1") {
      expect(report.confirmation?.status).toBe("performance_met");
      expect(report.evaluation_packets.at(-1)?.evaluation_split).toBe(
        "fresh_confirmation",
      );
      expect(report.evaluation_replays.at(-1)?.matches_previous).toBe(true);
    }

    expect(taskReads).toBeLessThanOrEqual(12);
    expect(pageErrors).toEqual([]);
  });
}

test("custom hold duration stays in seconds through review, creation, and workspace summary", async ({
  page,
}) => {
  test.setTimeout(120_000);
  const pageErrors: string[] = [];
  page.on("pageerror", (error) => pageErrors.push(error.message));

  await page.goto("/new");
  await disableRag(page);
  await page.getByLabel("设备与目标").fill("测试加热器保持温度");
  await page.getByRole("button", { name: "下一步", exact: true }).click();
  await page.getByLabel("输出 1 名称").fill("temperature");
  await page.getByLabel("单位", { exact: true }).fill("C");
  await page.getByLabel("输入 1 名称").fill("power");
  await page.getByLabel("输入单位").fill("W");
  await page.getByRole("button", { name: "下一步", exact: true }).click();
  await page.getByLabel("输入下限").fill("0");
  await page.getByLabel("输入上限").fill("100");
  await page.getByLabel("软件试验停止阈值").fill("100");
  await page.getByText("性能要求与预算（可选）", { exact: true }).click();
  const holdRequirement = page.getByRole("checkbox", {
    name: "至少保持多少秒",
    exact: true,
  });
  // Keyboard selection does not race the expanding panel's moving hit targets.
  await holdRequirement.press("Space");
  await expect(holdRequirement).toBeChecked();
  await page
    .getByRole("spinbutton", { name: "至少保持多少秒", exact: true })
    .fill("20");
  await page.getByRole("button", { name: "校验并核对" }).click();

  const review = page
    .locator(".ant-card")
    .filter({ has: page.getByText("任务核对", { exact: true }) });
  await expect(review).toContainText("保持时间不少于 20 s");
  await expect(review).toContainText("保持时间下限 (s)");
  await expect(review).not.toContainText("2000%");
  await page
    .getByRole("checkbox", { name: "我已核对目标、软件试验边界与预算" })
    .check();
  const creationResponse = page.waitForResponse(
    (response) =>
      new URL(response.url()).pathname === "/api/v1/tasks" &&
      response.request().method() === "POST",
  );
  await page.getByRole("button", { name: "确认软件边界并开始" }).click();
  const created = await waitForCompletedOperation(page, await creationResponse);
  expect(created.session_id).toBeTruthy();
  const sessionId = created.session_id!;
  await expect(page).toHaveURL(new RegExp(`/tasks/${sessionId}$`), {
    timeout: 10_000,
  });

  const summary = await getJson<Summary>(page, `/api/v1/tasks/${sessionId}`);
  expect(summary.task.success_requirements.hold_duration_min_s).toBe(20);
  const sidebar = page.locator("aside");
  await expect(sidebar).toContainText("保持时间不少于 20 s", {
    timeout: 10_000,
  });
  await expect(sidebar).not.toContainText("2000%");
  expect(pageErrors).toEqual([]);
});
