import {
  act,
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import Expert from "./Expert";
import type { Summary } from "./api/types";
import { ApiError } from "./api/client";
import { I18nProvider, useI18n } from "./i18n";
const submit = vi.fn().mockResolvedValue({});
let operationError = "";
vi.mock("./operations", () => ({
  useOperation: () => ({
    submit,
    busy: false,
    view: operationError ? <div role="alert">{operationError}</div> : null,
  }),
}));
vi.mock("./context", () => ({
  useSettings: () => ({ credentials: {}, useRag: false }),
}));
vi.mock("@tanstack/react-query", () => ({
  useQuery: () => ({ data: undefined }),
}));
vi.mock("./api/useTaskReader", () => ({ useTaskReader: () => vi.fn() }));
vi.stubGlobal("matchMedia", () => ({
  matches: false,
  addListener: () => {},
  removeListener: () => {},
}));
vi.stubGlobal(
  "ResizeObserver",
  class {
    observe() {}
    unobserve() {}
    disconnect() {}
  },
);
const originalStyle = window.getComputedStyle;
window.getComputedStyle = (element) => originalStyle(element);
afterEach(() => {
  cleanup();
  submit.mockClear();
  operationError = "";
  vi.restoreAllMocks();
});

test("import rejection appears once in the operation view while upload failures stay visible", async () => {
  operationError = "Import rejected";
  submit.mockRejectedValueOnce(
    new ApiError(
      { code: "invalid_import", message: operationError, receipt_saved: false },
      422,
    ),
  );
  vi.spyOn(globalThis, "fetch").mockResolvedValue(
    new Response(
      JSON.stringify({ file_id: "upload-1", filename: "history.zip" }),
    ),
  );
  const { container } = render(<Expert onClose={() => {}} />);
  fireEvent.click(screen.getByRole("tab", { name: "历史公开包导入" }));
  await act(async () => {
    fireEvent.change(
      container.ownerDocument.querySelector('input[type="file"]')!,
      {
        target: {
          files: [
            new File(["example"], "history.zip", { type: "application/zip" }),
          ],
        },
      },
    );
  });
  await waitFor(() =>
    expect(submit).toHaveBeenCalledWith("/imports", { file_id: "upload-1" }),
  );
  expect(screen.getAllByText("Import rejected")).toHaveLength(1);
  vi.mocked(globalThis.fetch).mockRejectedValueOnce(
    new Error("Upload unavailable"),
  );
  await act(async () => {
    fireEvent.change(
      container.ownerDocument.querySelector('input[type="file"]')!,
      {
        target: {
          files: [
            new File(["retry"], "retry.zip", { type: "application/zip" }),
          ],
        },
      },
    );
  });
  expect(await screen.findByText("Error: Upload unavailable")).toBeTruthy();
  expect(submit).toHaveBeenCalledTimes(1);
});

test("successful artifact validation feedback changes language without replacing the JSON input", async () => {
  vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response("{}"));
  function Switch() {
    const { setLocale } = useI18n();
    return <button onClick={() => setLocale("zh-CN")}>Switch language</button>;
  }
  render(
    <I18nProvider initialLocale="en">
      <Switch />
      <Expert onClose={() => {}} />
    </I18nProvider>,
  );
  fireEvent.click(screen.getByRole("tab", { name: "Artifact validation" }));
  fireEvent.change(screen.getByLabelText("Expert JSON"), {
    target: { value: '{"说明":"原始文本"}' },
  });
  fireEvent.click(screen.getByRole("button", { name: "Validate artifact" }));
  expect(
    await screen.findByText(
      "Artifact contract is valid; validation does not grant permission to execute.",
    ),
  ).toBeTruthy();
  fireEvent.click(screen.getByText("Switch language"));
  expect(
    screen.getByText("产物合同校验通过；校验不授予执行权限。"),
  ).toBeTruthy();
  expect(
    (screen.getByLabelText("专家 JSON") as HTMLTextAreaElement).value,
  ).toBe('{"说明":"原始文本"}');
});
test("expert task action transmits original JSON text without reparsing Chinese and escapes", () => {
  render(
    <Expert
      task={
        {
          session_id: "A",
          revision: 3,
          workspace: {
            action: "answer_probe",
            actionable: true,
            action_title: "回答",
          },
          input_contract: {},
        } as Summary
      }
      onClose={() => {}}
    />,
  );
  fireEvent.click(screen.getByRole("tab", { name: "JSON 提交" }));
  const text = '{\n  "说明": "中文\\n换行\\\\path"\n}';
  fireEvent.change(screen.getByLabelText("专家 JSON"), {
    target: { value: text },
  });
  fireEvent.click(screen.getByRole("button", { name: "提交当前动作" }));
  expect(submit).toHaveBeenCalledWith(
    "/tasks/A/actions",
    expect.objectContaining({ input: { mode: "json", text } }),
  );
});
