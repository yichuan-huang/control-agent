import type { DTO } from "./types";
export class ApiError extends Error {
  constructor(
    public detail: DTO<"PublicError">,
    public status: number,
  ) {
    super(detail.message);
  }
}
export async function api<T>(path: string, body?: unknown): Promise<T> {
  const response = await fetch(
    `/api/v1${path}`,
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
        message: "请求失败，请检查输入并重试。",
      },
      response.status,
    );
  return data as T;
}
export const download = (id: string, kind: string, artifact?: string) =>
  `/api/v1/tasks/${encodeURIComponent(id)}/downloads/${kind}${artifact ? "?artifact_id=" + encodeURIComponent(artifact) : ""}`;

export async function readRevision<T extends { revision: number }>(
  path: string,
  revision: number,
  onStale: () => void,
): Promise<T> {
  const result = await api<T>(path);
  if (result.revision !== revision) {
    onStale();
    throw new ApiError(
      {
        code: "stale_revision",
        receipt_saved: false,
        message: "任务记录已更新，正在刷新当前步骤。",
        latest_revision: result.revision,
      },
      409,
    );
  }
  return result;
}
