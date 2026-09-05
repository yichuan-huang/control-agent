import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Protocol } from "./Workspace";
import type { Summary } from "./api/types";
afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});
test("newer protocol receipt and preview are withheld until summary refresh", async () => {
  vi.spyOn(globalThis, "fetch").mockResolvedValue(
    new Response(
      JSON.stringify({
        revision: 8,
        summary: "NEW RECEIPT",
        accepted: true,
        feedback: "NEW FEEDBACK",
        preview: { columns: ["value"], rows: [[991]] },
        evidence_options: [],
      }),
    ),
  );
  const cache = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  const invalidate = vi.spyOn(cache, "invalidateQueries");
  render(
    <QueryClientProvider client={cache}>
      <Protocol task={{ session_id: "A", revision: 7 } as Summary} />
    </QueryClientProvider>,
  );
  await screen.findByText(/任务记录已更新/);
  expect(screen.queryByText("NEW RECEIPT")).toBeNull();
  expect(screen.queryByText("NEW FEEDBACK")).toBeNull();
  expect(screen.queryByText("991")).toBeNull();
  expect(invalidate).toHaveBeenCalledWith({ queryKey: ["task", "A"] });
});
