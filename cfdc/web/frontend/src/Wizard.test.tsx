import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import Wizard from "./Wizard";
vi.mock("./operations", () => ({
  useOperation: () => ({ submit: vi.fn(), busy: false, view: null }),
}));
vi.mock("./context", () => ({
  useSettings: () => ({ credentials: {}, useRag: false }),
}));
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
afterEach(() => {
  cleanup();
  sessionStorage.clear();
  vi.restoreAllMocks();
});
test("custom wizard collects evaluation settings before task confirmation", async () => {
  const fetch = vi.spyOn(globalThis, "fetch").mockResolvedValue(
    new Response(
      JSON.stringify({
        draft: {
          description: "外部系统",
          task_type: "local_setpoint_hold",
          outputs: [["y", "m"]],
          inputs: [["u"]],
        },
      }),
    ),
  );
  render(
    <QueryClientProvider client={new QueryClient()}>
      <MemoryRouter>
        <Wizard />
      </MemoryRouter>
    </QueryClientProvider>,
  );
  await waitFor(() =>
    expect(
      (screen.getByLabelText("设备与目标") as HTMLInputElement).value,
    ).toBe("外部系统"),
  );
  fireEvent.click(screen.getByText("下一步", { exact: true }));
  fireEvent.click(screen.getByText("下一步", { exact: true }));
  expect(screen.getByLabelText("评价区域（适用的工作范围）")).toBeTruthy();
  expect(
    (screen.getByLabelText("采样间隔 (s)") as HTMLInputElement).value,
  ).toBe("0.02");
  expect(
    (screen.getByLabelText("每次运行时长 (s)") as HTMLInputElement).value,
  ).toBe("20");
  expect(
    (screen.getByLabelText("重复运行次数") as HTMLInputElement).value,
  ).toBe("20");
  fireEvent.click(screen.getByText("性能要求与预算（可选）", { exact: true }));
  const overshoot = screen.getByRole("checkbox", {
    name: "允许超过目标多少",
  });
  fireEvent.click(overshoot);
  expect(overshoot).toHaveProperty("checked", true);
  fireEvent.click(screen.getByText("校验并核对", { exact: true }));
  await waitFor(() => expect(fetch).toHaveBeenCalledTimes(2));
  const body = JSON.parse(String(fetch.mock.calls[1][1]?.body));
  expect(body.draft).toMatchObject({
    external_data_enabled: true,
    reference_enabled: true,
    evaluation_dt_s: 0.02,
    evaluation_repeats: 20,
  });
}, 15000);
test("rejecting a retired draft starts a fresh custom task", async () => {
  sessionStorage.setItem("cfdc:wizard:custom", JSON.stringify({ step: 3 }));
  sessionStorage.setItem(
    "cfdc:draft",
    JSON.stringify({
      description: "我的外部系统",
      execution_mode: "managed",
      runner_id: "local_python",
      model_id: "optical",
    }),
  );
  const original = sessionStorage.getItem("cfdc:draft");
  const fetch = vi.spyOn(globalThis, "fetch").mockResolvedValue(
    new Response(
      JSON.stringify({
        draft: {
          description: "默认任务",
          task_type: "local_setpoint_hold",
          outputs: [["y", "m"]],
          inputs: [["u"]],
        },
      }),
    ),
  );
  render(
    <QueryClientProvider client={new QueryClient()}>
      <MemoryRouter>
        <Wizard />
      </MemoryRouter>
    </QueryClientProvider>,
  );
  await waitFor(() =>
    expect(
      (screen.getByLabelText("设备与目标") as HTMLInputElement).value,
    ).toBe("默认任务"),
  );
  expect(screen.getByText(/已拒绝恢复含旧实验配置的草稿/)).toBeTruthy();
  expect(sessionStorage.getItem("cfdc:draft")).toBe(original);
  expect(
    fetch.mock.calls.some((call) =>
      String(call[0]).includes("drafts/validate"),
    ),
  ).toBe(false);
  expect(screen.getByLabelText("设备与目标").closest("[hidden]")).toBeNull();
  fireEvent.change(screen.getByLabelText("设备与目标"), {
    target: { value: "新任务" },
  });
  expect(screen.queryByText(/已拒绝恢复含旧实验配置的草稿/)).toBeNull();
  expect(sessionStorage.getItem("cfdc:draft")).not.toBe(original);
  expect(screen.queryByLabelText("由系统自动运行软件仿真")).toBeNull();
  expect(screen.getByText(/实际试验在应用外部完成/)).toBeTruthy();
  fireEvent.click(screen.getByText("下一步", { exact: true }));
  fireEvent.click(screen.getByText("下一步", { exact: true }));
  fireEvent.click(screen.getByText("校验并核对", { exact: true }));
  await waitFor(() =>
    expect(
      fetch.mock.calls.some((call) =>
        String(call[0]).includes("drafts/validate"),
      ),
    ).toBe(true),
  );
  const call = fetch.mock.calls.find((call) =>
    String(call[0]).includes("drafts/validate"),
  );
  const draft = JSON.parse(String(call?.[1]?.body)).draft;
  expect(draft.description).toBe("新任务");
  expect(draft).not.toHaveProperty("execution_mode");
  expect(draft).not.toHaveProperty("runner_id");
  expect(draft).not.toHaveProperty("model_id");
}, 15000);
