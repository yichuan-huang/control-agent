import { afterEach, expect, test, vi } from "vitest";
import { api, download, readRevision } from "./client";
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

test("concurrent requests and downloads retain their own explicit locale", async () => {
  const fetch = vi
    .spyOn(globalThis, "fetch")
    .mockImplementation(async () => new Response("{}"));
  await Promise.all([
    api("/tasks/A/curves?signal=voltage", undefined, "en"),
    api("/tasks/A/curves?signal=voltage", undefined, "zh-CN"),
  ]);
  expect(fetch.mock.calls.map(([url]) => String(url))).toEqual([
    "/api/v1/tasks/A/curves?signal=voltage&locale=en",
    "/api/v1/tasks/A/curves?signal=voltage&locale=zh-CN",
  ]);
  expect(download("A", "artifact", "report", "en")).toBe(
    "/api/v1/tasks/A/downloads/artifact?artifact_id=report&locale=en",
  );
});
