import { useQueryClient } from "@tanstack/react-query";
import { readRevision } from "./client";
import type { Summary } from "./types";
import { useI18n } from "../i18n";
export function useTaskReader(task: Summary) {
  const cache = useQueryClient();
  const { locale } = useI18n();
  return <T extends { revision: number }>(path: string) =>
    readRevision<T>(
      path,
      task.revision,
      () => {
        // Let the current summary refresh finish without restarting stale details.
        void cache.invalidateQueries(
          { queryKey: ["task", task.session_id, locale], exact: true },
          { cancelRefetch: false },
        );
      },
      locale,
    );
}
