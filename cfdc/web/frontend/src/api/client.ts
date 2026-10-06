import type { DTO } from "./types";
import { useMemo } from "react";
import {
  useI18n,
  type Locale,
  type MessageRef,
  translateMessage,
} from "../i18n";
export class ApiError extends Error {
  constructor(
    public detail: DTO<"PublicError"> & {
      message_ref?: MessageRef | null;
      field_message_refs?: Record<string, MessageRef> | null;
    },
    public status: number,
  ) {
    super(detail.message);
  }
}
export function localizedPath(path: string, locale: Locale) {
  const [pathname, query = ""] = path.split("?");
  const params = new URLSearchParams(query);
  params.set("locale", locale);
  return `${pathname}?${params}`;
}
export async function api<T>(
  path: string,
  body?: unknown,
  locale: Locale = "zh-CN",
): Promise<T> {
  const response = await fetch(
    localizedPath(`/api/v1${path}`, locale),
    body === undefined
      ? {}
      : {
          method: "POST",
          headers:
            body instanceof FormData
              ? {}
              : { "Content-Type": "application/json" },
          body: body instanceof FormData ? body : JSON.stringify(body),
        },
  );
  const data = await response.json();
  if (!response.ok)
    throw new ApiError(
      data.error ?? {
        code: "request_failed",
        receipt_saved: false,
        message: translateMessage(locale, {
          key: "frontend.api.request_failed",
        }),
        message_ref: { key: "frontend.api.request_failed" },
      },
      response.status,
    );
  return data as T;
}
export const download = (
  id: string,
  kind: string,
  artifact?: string,
  locale: Locale = "zh-CN",
) =>
  localizedPath(
    `/api/v1/tasks/${encodeURIComponent(id)}/downloads/${kind}${artifact ? "?artifact_id=" + encodeURIComponent(artifact) : ""}`,
    locale,
  );

export async function readRevision<T extends { revision: number }>(
  path: string,
  revision: number,
  onStale: () => void,
  locale: Locale = "zh-CN",
): Promise<T> {
  const result = await api<T>(path, undefined, locale);
  if (result.revision !== revision) {
    onStale();
    throw new ApiError(
      {
        code: "stale_revision",
        receipt_saved: false,
        message: translateMessage(locale, {
          key: "frontend.api.stale_revision",
        }),
        message_ref: { key: "frontend.api.stale_revision" },
        latest_revision: result.revision,
      },
      409,
    );
  }
  return result;
}

export function useApi() {
  const { locale } = useI18n();
  return useMemo(
    () => ({
      api: <T>(path: string, body?: unknown) => api<T>(path, body, locale),
      download: (id: string, kind: string, artifact?: string) =>
        download(id, kind, artifact, locale),
    }),
    [locale],
  );
}
