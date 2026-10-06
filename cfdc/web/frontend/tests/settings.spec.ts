import { expect, test } from "./live-test";

test("manual settings validate and probe without startup environment", async ({
  page,
}) => {
  await page.route("**/api/v1/config{,?**}", (route) =>
    route.fulfill({
      json: {
        base_url: "",
        model: "",
        rag: { status: "ready", message: "ready" },
      },
    }),
  );
  let submitted: unknown;
  await page.route("**/api/v1/config/probe{,?**}", async (route) => {
    submitted = route.request().postDataJSON();
    await route.fulfill({
      json: { connected: true, message: "服务与模型可用。" },
    });
  });
  await page.goto("/");
  await page.getByRole("button", { name: "设置", exact: true }).click();
  const probe = page.getByRole("button", { name: "测试当前配置" });
  await probe.click();
  await expect(page.getByLabel("Base URL")).toBeFocused();
  await page.getByLabel("Base URL").fill("http://127.0.0.1:11434/v1");
  await page.getByLabel("Model").fill("gemma4:e4b");
  await page.getByLabel("API Key").fill("ollama");
  await probe.focus();
  await page.keyboard.press("Enter");
  await expect(page.getByText("已连接：服务与模型可用。")).toBeVisible();
  expect(submitted).toEqual({
    credentials: {
      base_url: "http://127.0.0.1:11434/v1",
      model: "gemma4:e4b",
      api_key: "ollama",
    },
  });
  await expect(
    page.getByRole("button", { name: "从启动环境导入地址和模型" }),
  ).not.toBeVisible();
  await expect(page.getByText(/环境未提供/)).not.toBeVisible();
});

test("live LLM form probe without server address/model presets", async ({
  page,
}) => {
  test.skip(
    process.env.CFDC_RUN_LIVE_LLM !== "1",
    "Opt-in configured API validation",
  );
  const modelBaseURL = process.env.CFDC_LLM_BASE_URL;
  const modelName = process.env.CFDC_LLM_MODEL;
  const modelAPIKey = process.env.CFDC_LLM_API_KEY;
  expect(modelBaseURL, "CFDC_LLM_BASE_URL is required").toBeTruthy();
  expect(Boolean(modelName?.trim()), "CFDC_LLM_MODEL is required").toBe(true);
  expect(Boolean(modelAPIKey?.trim()), "CFDC_LLM_API_KEY is required").toBe(
    true,
  );
  const config = await (await page.request.get("/api/v1/config")).json();
  expect(config.base_url).toBe("");
  expect(config.model).toBe("");
  for (const width of [1280, 390]) {
    await page.setViewportSize({ width, height: 844 });
    await page.goto("/");
    await page.getByRole("button", { name: "设置", exact: true }).click();
    await page.getByLabel("Base URL").fill(modelBaseURL!);
    await page.getByLabel("Model").fill(modelName!);
    await page.getByLabel("API Key").fill(modelAPIKey!);
    const probe = page.getByRole("button", { name: "测试当前配置" });
    await probe.focus();
    await page.keyboard.press("Enter");
    await expect(
      page.getByText("已连接：已连接服务并找到所选模型。"),
    ).toBeVisible();
    await page.getByRole("button", { name: "高级设置" }).click();
    await page
      .getByRole("button", { name: "从启动环境导入地址和模型" })
      .click();
    await expect(
      page.getByText("启动环境没有预设地址和模型，表单内容未更改。"),
    ).toBeVisible();
    await expect(
      page.getByText("已连接：已连接服务并找到所选模型。"),
    ).toBeVisible();
    await page.getByLabel("Model").fill("cfdc-nonexistent-validation-model");
    await expect(
      page.getByText("已连接：已连接服务并找到所选模型。"),
    ).not.toBeVisible();
    await probe.click();
    await expect(
      page.getByText("未连接：服务可连接，但未找到所选模型，请核对模型名称。"),
    ).toBeVisible();
    expect(
      (await page.getByLabel("API Key").inputValue()) === modelAPIKey,
    ).toBe(true);
    await page.getByLabel("Base URL").fill("http://127.0.0.1:1/v1");
    await probe.click();
    await expect(
      page.getByText(
        "未连接：连接探测失败，请检查服务地址、密钥及服务是否启动。",
      ),
    ).toBeVisible();
    expect(
      (await page.getByLabel("API Key").inputValue()) === modelAPIKey,
    ).toBe(true);
  }
});
