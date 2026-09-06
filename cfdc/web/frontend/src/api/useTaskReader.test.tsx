import {
  act,
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import {
  QueryClient,
  QueryClientProvider,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import { useState } from "react";
import { api } from "./client";
import { useTaskReader } from "./useTaskReader";
import type { Summary } from "./types";

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

function Reader() {
  const cache = useQueryClient();
  const task = useQuery({
    queryKey: ["task", "A"],
    queryFn: () => api<Summary>("/tasks/A"),
  });
  const other = useQuery({
    queryKey: ["task", "B"],
    queryFn: () => api<Summary>("/tasks/B"),
  });
  return (
    <>
      <button
        onClick={() =>
          void cache.invalidateQueries({ queryKey: ["task", "A"] })
        }
      >
        Refresh
      </button>
      <span>Other revision {other.data?.revision}</span>
      {task.data && <Detail task={task.data} />}
    </>
  );
}

function Detail({ task }: { task: Summary }) {
  const read = useTaskReader(task);
  const [rejected, setRejected] = useState(0);
  const detail = useQuery({
    queryKey: ["task", "A", task.revision, "detail"],
    queryFn: () => read<{ revision: number; text: string }>("/tasks/A/detail"),
  });
  return (
    <>
      <span>Revision {task.revision}</span>
      <span>{detail.data?.text}</span>
      <span>Rejected {rejected}</span>
      <button
        onClick={async () => {
          const outcomes = await Promise.allSettled([
            read("/tasks/A/check"),
            read("/tasks/A/check"),
          ]);
          setRejected(
            outcomes.filter((result) => result.status === "rejected").length,
          );
        }}
      >
        Read stale details
      </button>
    </>
  );
}

function setup() {
  const summaries: Array<(response: Response) => void> = [];
  const details: Array<(response: Response) => void> = [];
  const otherReads = vi.fn();
  vi.spyOn(globalThis, "fetch").mockImplementation(async (url) => {
    if (String(url).endsWith("/check")) return response({ revision: 8 });
    if (String(url).endsWith("/tasks/B")) {
      otherReads();
      return response({ session_id: "B", revision: 4 });
    }
    return new Promise<Response>((resolve) => {
      (String(url).endsWith("/detail") ? details : summaries).push(resolve);
    });
  });
  const cache = new QueryClient({
    defaultOptions: { queries: { retry: false, staleTime: Infinity } },
  });
  cache.setQueryData(["task", "A"], { session_id: "A", revision: 7 });
  cache.setQueryData(["task", "B"], { session_id: "B", revision: 3 });
  cache.setQueryData(["task", "A", 7, "detail"], {
    revision: 7,
    text: "Previous detail",
  });
  render(
    <QueryClientProvider client={cache}>
      <Reader />
    </QueryClientProvider>,
  );
  return { summaries, details, otherReads };
}

function response(value: unknown) {
  return new Response(JSON.stringify(value));
}

test("newer detail preserves the in-flight summary and appears only under its new revision", async () => {
  const { summaries, details } = setup();
  fireEvent.click(screen.getByText("Refresh"));
  await waitFor(() => {
    expect(summaries).toHaveLength(1);
    expect(details).toHaveLength(1);
  });
  await act(async () =>
    details[0](response({ revision: 8, text: "New detail" })),
  );
  expect(screen.queryByText("New detail")).toBeNull();
  expect(summaries).toHaveLength(1);
  await act(async () =>
    summaries[0](response({ session_id: "A", revision: 8 })),
  );
  await screen.findByText("Revision 8");
  await waitFor(() => expect(details).toHaveLength(2));
  expect(screen.queryByText("Previous detail")).toBeNull();
  await act(async () =>
    details[1](response({ revision: 8, text: "New detail" })),
  );
  await screen.findByText("New detail");
});

test("repeated stale reads share one summary refresh without refetching cached details or another task", async () => {
  const { summaries, details, otherReads } = setup();
  fireEvent.click(screen.getByText("Read stale details"));
  await screen.findByText("Rejected 2");
  expect(summaries).toHaveLength(1);
  expect(details).toHaveLength(0);
  expect(otherReads).not.toHaveBeenCalled();
  expect(screen.getByText("Other revision 3")).toBeTruthy();
  expect(screen.queryByText("Revision 8")).toBeNull();
});
