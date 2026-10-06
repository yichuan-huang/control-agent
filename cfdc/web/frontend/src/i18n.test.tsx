import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import {
  I18nProvider,
  keepLocaleData,
  resolveLocale,
  translateMessage,
  useI18n,
} from "./i18n";
import en from "../../../resources/locales/en/frontend.json";
import zh from "../../../resources/locales/zh-CN/frontend.json";

afterEach(() => {
  cleanup();
  localStorage.clear();
  vi.restoreAllMocks();
});

test("stored locale wins, then only the primary browser language is used", () => {
  expect(resolveLocale("en", ["zh-CN"])).toBe("en");
  expect(resolveLocale(null, ["zh-TW", "en"])).toBe("zh-CN");
  expect(resolveLocale("fr", ["en-GB", "zh-CN"])).toBe("en");
  expect(resolveLocale(null, ["fr-FR"])).toBe("en");
});

test("frontend catalogs have matching keys and named parameters", () => {
  expect(Object.keys(en).sort()).toEqual(Object.keys(zh).sort());
  const parameters = (value: string) =>
    [...value.matchAll(/\{([a-zA-Z_][a-zA-Z0-9_]*)\}/g)]
      .map((match) => match[1])
      .sort();
  for (const key of Object.keys(en) as (keyof typeof en)[])
    expect(parameters(en[key]), key).toEqual(parameters(zh[key]));
  expect(
    translateMessage("en", { key: "missing.message" }, "保留原始返回内容"),
  ).toBe("保留原始返回内容");
  expect(translateMessage("en", { key: "constructor" }, "raw fallback")).toBe(
    "raw fallback",
  );
});

test("language placeholders never carry data across a revision or signal change", () => {
  const data = { revision: 4 };
  const retain = keepLocaleData("en", ["task", "A", "en", 4, "curve", "speed"]);
  expect(
    retain(data, { queryKey: ["task", "A", "zh-CN", 4, "curve", "speed"] }),
  ).toBe(data);
  expect(
    retain(data, { queryKey: ["task", "A", "zh-CN", 3, "curve", "speed"] }),
  ).toBeUndefined();
  expect(
    retain(data, {
      queryKey: ["task", "A", "zh-CN", 4, "curve", "temperature"],
    }),
  ).toBeUndefined();
});

function Sample() {
  const { t, locale, setLocale, message } = useI18n();
  return (
    <>
      <input aria-label="draft" defaultValue="用户原文 raw data" />
      <span>{t("frontend.app.settings")}</span>
      <output>{message({ key: "frontend.app.settings" }, "fallback")}</output>
      <button onClick={() => setLocale(locale === "en" ? "zh-CN" : "en")}>
        switch
      </button>
    </>
  );
}

test("switch updates translations and document language while preserving mounted state", () => {
  render(
    <I18nProvider initialLocale="en">
      <Sample />
    </I18nProvider>,
  );
  const input = screen.getByLabelText("draft");
  fireEvent.change(input, { target: { value: "Untranslated user edit" } });
  expect(screen.getAllByText("Settings")).toHaveLength(2);
  fireEvent.click(screen.getByText("switch"));
  expect(screen.getAllByText("设置")).toHaveLength(2);
  expect((input as HTMLInputElement).value).toBe("Untranslated user edit");
  expect(document.documentElement.lang).toBe("zh-CN");
  expect(localStorage.getItem("cfdc:locale")).toBe("zh-CN");
});

test("storage failure does not prevent language switching", () => {
  vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
    throw new Error("denied");
  });
  render(
    <I18nProvider initialLocale="en">
      <Sample />
    </I18nProvider>,
  );
  fireEvent.click(screen.getByText("switch"));
  expect(screen.getAllByText("设置")).toHaveLength(2);
});
