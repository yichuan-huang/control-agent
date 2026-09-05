import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import Results from "./Results";
import { statusLabel } from "./labels";
import type { Summary } from "./api/types";
afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});
test("bare performance status cannot override unpublished confirmation projection", async () => {
  vi.spyOn(globalThis, "fetch").mockResolvedValue(
    new Response(JSON.stringify({ revision: 7, options: [], metrics: [] })),
  );
  vi.stubGlobal("matchMedia", () => ({
    matches: false,
    addListener: () => {},
    removeListener: () => {},
  }));
  const task = {
    session_id: "A",
    revision: 7,
    status: "performance_met",
    workspace: {
      title: "确认结果尚不能发布",
      explanation: "缺少绑定证据",
      actionable: false,
    },
  } as Summary;
  const { container } = render(
    <QueryClientProvider client={new QueryClient()}>
      <MemoryRouter>
        <span>{statusLabel(task.status)}</span>
        <Results task={task} />
      </MemoryRouter>
    </QueryClientProvider>,
  );
  await screen.findByText("确认结果尚不能发布");
  expect(screen.queryByText("独立确认已通过")).toBeNull();
  expect(container.querySelector(".ant-alert-success")).toBeNull();
});
