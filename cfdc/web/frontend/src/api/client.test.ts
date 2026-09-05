import { afterEach, expect, test, vi } from "vitest";
import { readRevision } from "./client";
afterEach(() => vi.restoreAllMocks());
test("a newer recorded revision cannot be displayed under a stale task header", async () => {
  vi.spyOn(globalThis, "fetch").mockResolvedValue(
    new Response(JSON.stringify({ revision: 8, metrics: [["new"]] })),
  );
  let refresh = false;
  await expect(
    readRevision("/tasks/example/evaluations", 7, () => {
      refresh = true;
    }),
  ).rejects.toThrow("任务记录已更新");
  expect(refresh).toBe(true);
});
