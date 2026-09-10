import { expect, test } from "@playwright/test";

const caseIds = [
  "dc_motor_speed_v1",
  "dc_motor_position_v1",
  "tclab_single_heater_v1",
  "quadruple_tank_nmp_v1",
  "tclab_dual_heater_v1",
  "dc_motor_speed_transition_hold_v1",
  "tclab_single_heater_transition_hold_v1",
  "quadruple_tank_transition_hold_v1",
  "dc_motor_speed_staged_transition_hold_v1",
  "tclab_single_heater_staged_transition_hold_v1",
  "quadruple_tank_staged_transition_hold_v1",
  "audit_class_i_level",
  "audit_class_ii_thermal",
  "audit_class_ii_oscillator",
  "audit_class_iii_motion",
  "audit_class_iv_nmp",
  "audit_class_iv_high_order",
  "audit_class_v_mimo",
];

for (const caseId of caseIds) {
  test(`catalog card ${caseId} validates and creates its registered binding`, async ({
    page,
  }) => {
    test.setTimeout(120_000);
    const errors: string[] = [];
    page.on("pageerror", (error) => errors.push(error.message));
    await page.goto("/cases");
    const catalogResponse = await page.request.get("/api/v1/cases");
    expect(catalogResponse.ok()).toBe(true);
    const catalog = await catalogResponse.json();
    expect(catalog.items.map((item: { id: string }) => item.id).sort()).toEqual(
      [...caseIds].sort(),
    );
    const card = catalog.items.find(
      (item: { id: string }) => item.id === caseId,
    );
    if (card.category === "audit")
      await page.getByText("审计案例", { exact: true }).first().click();
    const tile = page
      .locator(".ant-card")
      .filter({ has: page.getByText(card.title, { exact: true }) });
    await tile.getByTestId("case-open").click();
    await expect(page).toHaveURL(new RegExp(`/new\\?case=${caseId}$`));
    await expect(page.getByText("案例参数已锁定")).toBeVisible();
    const detailResponse = await page.request.get(`/api/v1/cases/${caseId}`);
    expect(detailResponse.ok()).toBe(true);
    const detail = await detailResponse.json();
    const validation = await page.request.post("/api/v1/drafts/validate", {
      data: { draft: detail.draft, case_id: caseId },
    });
    expect(validation.status()).toBe(200);
    expect((await validation.json()).task).toEqual(detail.task);
    await page.getByRole("button", { name: "设置", exact: true }).click();
    await page.getByRole("switch", { name: "新任务使用内置知识库" }).uncheck();
    await page.keyboard.press("Escape");
    await page
      .getByRole("checkbox", { name: "我已核对目标、软件试验边界与预算" })
      .check();
    const creation = page.waitForResponse(
      (response) =>
        new URL(response.url()).pathname === "/api/v1/tasks" &&
        response.request().method() === "POST",
    );
    await page.getByRole("button", { name: "确认软件边界并开始" }).click();
    const response = await creation;
    expect(response.status()).toBe(202);
    let operation = await response.json();
    await expect
      .poll(
        async () => {
          const result = await page.request.get(
            `/api/v1/operations/${operation.operation_id}`,
            { maxRetries: 1 },
          );
          expect(result.ok()).toBe(true);
          operation = await result.json();
          return operation.status;
        },
        { timeout: 60_000 },
      )
      .toBe("completed");
    expect(operation.error).toBeFalsy();
    await expect(page).toHaveURL(new RegExp(`/tasks/${operation.session_id}$`));
    const reportResponse = await page.request.get(
      `/api/v1/tasks/${operation.session_id}/downloads/report`,
    );
    expect(reportResponse.ok()).toBe(true);
    const report = await reportResponse.json();
    const binding = report.registered_case_binding;
    expect(binding.case_id).toBe(caseId);
    expect(binding.case_kind).toBe(
      card.category === "audit" ? "audit" : "training",
    );
    expect(binding.evidence_mode).toBe("automatic");
    expect(binding.binding_fingerprint).toBeTruthy();
    expect(binding.task_scope_fingerprint).toBeTruthy();
    for (const role of ["identification", "evaluation"]) {
      expect(report.provider_bindings[role]).toMatchObject({
        ...binding.provider_references[role],
        task_scope_fingerprint: binding.task_scope_fingerprint,
        registered_case_binding_fingerprint: binding.binding_fingerprint,
      });
    }
    expect(errors).toEqual([]);
  });
}
