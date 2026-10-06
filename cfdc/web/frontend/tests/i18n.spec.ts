import { expect, test, type Page } from "@playwright/test";

async function selectLanguage(page: Page, language: "中文" | "English") {
  const picker = page.getByRole("radiogroup", {
    name: /^(Interface language|界面语言)$/,
  });
  await picker.getByText(language, { exact: true }).click();
  await expect(
    picker.getByRole("radio", { name: language, exact: true }),
  ).toBeChecked();
}

test.describe("English browser locale", () => {
  test.use({ locale: "en-GB" });
  test("defaults to English and preserves a draft, step, credentials, and validation while switching", async ({
    page,
  }) => {
    const requests: URL[] = [];
    page.on("request", (request) => {
      if (request.url().includes("/api/v1/"))
        requests.push(new URL(request.url()));
    });
    await page.goto("/new");
    await expect(page.locator("html")).toHaveAttribute("lang", "en");
    await page
      .getByLabel("Equipment and goal")
      .fill("用户原文 / original equipment description");
    await page.getByRole("button", { name: "Next", exact: true }).click();
    await page.getByLabel("Output 1 name").fill("custom_signal");
    await selectLanguage(page, "中文");
    await expect(page.getByLabel("输出 1 名称")).toHaveValue("custom_signal");
    await page.getByRole("button", { name: "上一步", exact: true }).click();
    await expect(page.getByLabel("设备与目标")).toHaveValue(
      "用户原文 / original equipment description",
    );
    await page.getByRole("button", { name: "设置", exact: true }).click();
    await page.getByLabel("Base URL").fill("https://example.invalid/v1");
    await page.getByLabel("Model").fill("user-model");
    await page.getByLabel("API Key").fill("browser-only-test-key");
    await page.keyboard.press("Escape");
    await selectLanguage(page, "English");
    await page.getByRole("button", { name: "Settings", exact: true }).click();
    await expect(page.getByLabel("API Key")).toHaveValue(
      "browser-only-test-key",
    );
    await expect(page.getByLabel("Model")).toHaveValue("user-model");
    await page.getByLabel("API Key").fill("");
    await page
      .getByRole("button", { name: "Test current configuration" })
      .click();
    await expect(page.getByText("Enter API Key.")).toBeVisible();
    await page.keyboard.press("Escape");
    await selectLanguage(page, "中文");
    await page.getByRole("button", { name: "设置", exact: true }).click();
    await expect(page.getByText("请填写 API Key。")).toBeVisible();
    expect(
      requests.every((url) =>
        ["en", "zh-CN"].includes(url.searchParams.get("locale") ?? ""),
      ),
    ).toBe(true);
    expect(
      await page.evaluate(
        () => JSON.stringify(localStorage) + JSON.stringify(sessionStorage),
      ),
    ).not.toContain("browser-only-test-key");
    await page.reload();
    await expect(page.locator("html")).toHaveAttribute("lang", "zh-CN");
    await expect(page.getByLabel("设备与目标")).toHaveValue(
      "用户原文 / original equipment description",
    );
  });

  test("cases, expert tools, and validation use English", async ({ page }) => {
    await page.goto("/cases");
    await expect(
      page.getByRole("heading", { name: "Choose a case" }),
    ).toBeVisible();
    const category = page.getByRole("radiogroup", { name: "Case category" });
    await expect(
      category.getByText("Engineering cases", { exact: true }),
    ).toBeVisible();
    await expect(
      category.getByRole("radio", { name: "Engineering cases" }),
    ).toBeChecked();
    await page.getByTestId("case-open").first().click();
    await expect(page.getByText("Case parameters are locked")).toBeVisible();
    await page
      .getByRole("checkbox", {
        name: "I have reviewed the goal, software trial boundaries, and budgets",
      })
      .check();
    await selectLanguage(page, "中文");
    await expect(
      page.getByRole("checkbox", { name: "我已核对目标、软件试验边界与预算" }),
    ).toBeChecked();
    await selectLanguage(page, "English");
    await page.getByRole("button", { name: "Import / Expert" }).click();
    await expect(
      page.getByRole("dialog", { name: "Expert tools" }),
    ).toBeVisible();
    await page.getByLabel("Expert JSON").fill("[]");
    await page.getByRole("button", { name: "Create unconfirmed task" }).click();
    await expect(
      page.getByText("Submit a complete JSON object."),
    ).toBeVisible();
  });
});

test.describe("Traditional Chinese browser locale", () => {
  test.use({ locale: "zh-TW" });
  test("maps the primary Chinese language to zh-CN", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("html")).toHaveAttribute("lang", "zh-CN");
    await expect(
      page.getByRole("button", { name: "设置", exact: true }),
    ).toBeVisible();
  });
});
