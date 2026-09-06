import { useQueryClient } from "@tanstack/react-query";
import { readRevision } from "./client";
import type { Summary } from "./types";
export function useTaskReader(task: Summary) {
  const cache = useQueryClient();
  return <T extends { revision: number }>(path: string) =>
    readRevision<T>(path, task.revision, () => {
      // Let the current summary refresh finish without restarting stale details.
      void cache.invalidateQueries(
        { queryKey: ["task", task.session_id], exact: true },
        { cancelRefetch: false },
      );
    });
}
