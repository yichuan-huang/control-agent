import {
  render,
  screen,
  fireEvent,
  waitFor,
  cleanup,
} from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import { MemoryRouter, useNavigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useOperation } from "./operations";
afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  sessionStorage.clear();
});
function Subject() {
  const op = useOperation();
  const navigate = useNavigate();
  return (
    <>
      <button
        disabled={op.busy}
        onClick={() =>
          void op
            .submit("/tasks", { draft: { description: "test" } })
            .catch(() => {})
        }
      >
        Submit
      </button>
      <button onClick={() => navigate("/other")}>Other task</button>
      {op.view}
    </>
  );
}
function setup() {
  render(
    <QueryClientProvider
      client={
        new QueryClient({ defaultOptions: { queries: { retry: false } } })
      }
    >
      <MemoryRouter>
        <Subject />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}
test("failed transport is never automatically replayed and deliberate retry preserves identity", async () => {
  const bodies: Record<string, unknown>[] = [];
  vi.spyOn(globalThis, "fetch").mockImplementation(async (_url, init) => {
    bodies.push(JSON.parse(String(init?.body)));
    throw new TypeError("Network unavailable");
  });
  setup();
  fireEvent.click(screen.getByText("Submit"));
  await screen.findByText("Network unavailable");
  expect(bodies).toHaveLength(1);
  fireEvent.click(screen.getByText("Submit"));
  await waitFor(() => expect(bodies).toHaveLength(2));
  expect(bodies[0].request_id).toBe(bodies[1].request_id);
});
test("definite API rejection releases the identity for corrected input", async () => {
  const bodies: Record<string, unknown>[] = [];
  vi.spyOn(globalThis, "fetch").mockImplementation(async (_url, init) => {
    bodies.push(JSON.parse(String(init?.body)));
    return new Response(
      JSON.stringify({
        error: { code: "invalid", message: "Correct the draft" },
      }),
      { status: 422, headers: { "Content-Type": "application/json" } },
    );
  });
  setup();
  fireEvent.click(screen.getByText("Submit"));
  await screen.findByText("Correct the draft");
  fireEvent.click(screen.getByText("Submit"));
  await waitFor(() => expect(bodies).toHaveLength(2));
  expect(bodies[0].request_id).not.toBe(bodies[1].request_id);
});

test("missing operation unlocks the form without losing drafts or another scope", async () => {
  sessionStorage.setItem("cfdc:operation:entry:/", "missing");
  sessionStorage.setItem("cfdc:operation:entry:/other", "another-operation");
  sessionStorage.setItem("cfdc:draft", "preserved draft");
  const requests: string[] = [];
  vi.spyOn(globalThis, "fetch").mockImplementation(async (_url, init) => {
    requests.push(init?.method ?? "GET");
    return new Response(
      JSON.stringify({
        error: { code: "operation_not_found", message: "Missing" },
      }),
      { status: 404 },
    );
  });
  setup();
  await waitFor(() =>
    expect(screen.getByText("Submit").hasAttribute("disabled")).toBe(false),
  );
  expect(sessionStorage.getItem("cfdc:operation:entry:/")).toBeNull();
  expect(sessionStorage.getItem("cfdc:operation:entry:/other")).toBe(
    "another-operation",
  );
  expect(sessionStorage.getItem("cfdc:draft")).toBe("preserved draft");
  expect(screen.getByText(/操作记录已失效/)).toBeTruthy();
  expect(requests).toEqual(["GET"]);
  cleanup();
  setup();
  expect(screen.getByText("Submit").hasAttribute("disabled")).toBe(false);
  expect(requests).toEqual(["GET"]);
});

test.each(["network", "server", "other-404"])(
  "%s read failure preserves the pending operation for explicit retry",
  async (failure) => {
    sessionStorage.setItem("cfdc:operation:entry:/", "pending");
    const methods: string[] = [];
    vi.spyOn(globalThis, "fetch").mockImplementation(async (_url, init) => {
      methods.push(init?.method ?? "GET");
      if (failure === "network") throw new TypeError("Network unavailable");
      return new Response(
        JSON.stringify({
          error: { code: "request_failed", message: "Unavailable" },
        }),
        { status: failure === "server" ? 500 : 404 },
      );
    });
    setup();
    await screen.findByText("无法读取操作状态");
    expect(screen.getByText("Submit").hasAttribute("disabled")).toBe(true);
    expect(sessionStorage.getItem("cfdc:operation:entry:/")).toBe("pending");
    fireEvent.click(screen.getByText("重新读取"));
    await waitFor(() => expect(methods.length).toBeGreaterThanOrEqual(2));
    expect(methods.every((method) => method === "GET")).toBe(true);
  },
);

test("a late missing-operation response cannot clear the new page's operation", async () => {
  sessionStorage.setItem("cfdc:operation:entry:/", "missing");
  sessionStorage.setItem("cfdc:operation:entry:/other", "pending");
  let finishMissing!: (response: Response) => void;
  vi.spyOn(globalThis, "fetch").mockImplementation(async (url) => {
    if (String(url).endsWith("/missing"))
      return new Promise<Response>((resolve) => {
        finishMissing = resolve;
      });
    return new Response(
      JSON.stringify({
        operation_id: "pending",
        request_id: "request",
        session_id: null,
        status: "running",
        created_at: "2026-09-05T00:00:00Z",
        updated_at: "2026-09-05T00:00:00Z",
        result: null,
        error: null,
      }),
    );
  });
  setup();
  await waitFor(() => expect(finishMissing).toBeTypeOf("function"));
  fireEvent.click(screen.getByText("Other task"));
  finishMissing(
    new Response(
      JSON.stringify({
        error: { code: "operation_not_found", message: "Missing" },
      }),
      { status: 404 },
    ),
  );
  await screen.findByText("操作：", { exact: false });
  expect(sessionStorage.getItem("cfdc:operation:entry:/other")).toBe("pending");
  expect(screen.getByText("Submit").hasAttribute("disabled")).toBe(true);
  expect(screen.queryByText(/操作记录已失效/)).toBeNull();
});
