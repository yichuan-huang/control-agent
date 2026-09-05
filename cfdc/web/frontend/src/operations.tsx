import { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Alert, Button, Space, Spin } from "antd";
import { api, ApiError } from "./api/client";
import type { Operation } from "./api/types";
import { statusLabel } from "./labels";
import { requestIdentity } from "./safety";
export function useOperation(taskId?: string, active = true) {
  const location = useLocation();
  const scope = taskId
    ? `task:${taskId}`
    : `entry:${location.pathname}${location.search}`;
  const storageKey = `cfdc:operation:${scope}`;
  const [record, setRecord] = useState(() => ({
    scope,
    id: sessionStorage.getItem(storageKey) ?? "",
  }));
  const id =
    record.scope === scope
      ? record.id
      : (sessionStorage.getItem(storageKey) ?? "");
  const currentLocation = useRef(location.key);
  currentLocation.current = location.key;
  const originLocation = useRef(location.key);
  const [error, setError] = useState("");
  const [expiredScope, setExpiredScope] = useState("");
  const [sending, setSending] = useState(false);
  const identity = useRef(requestIdentity());
  const handled = useRef(new Set<string>());
  const navigate = useNavigate();
  const cache = useQueryClient();
  const query = useQuery({
    queryKey: ["operation", id],
    queryFn: () => api<Operation>(`/operations/${id}`),
    enabled: active && !!id,
    refetchInterval: (q) =>
      !q.state.error &&
      ["queued", "running"].includes(q.state.data?.status ?? "queued")
        ? 800
        : false,
    retry: false,
  });
  const op = active ? query.data : undefined;
  useEffect(() => {
    if (
      !active ||
      !id ||
      !(query.error instanceof ApiError) ||
      query.error.status !== 404 ||
      query.error.detail.code !== "operation_not_found"
    )
      return;
    if (sessionStorage.getItem(storageKey) === id) {
      sessionStorage.removeItem(storageKey);
    }
    setRecord({ scope, id: sessionStorage.getItem(storageKey) ?? "" });
    identity.current.clear();
    setExpiredScope(scope);
    cache.removeQueries({ queryKey: ["operation", id], exact: true });
    void cache.invalidateQueries({ queryKey: ["task"] });
  }, [active, id, query.error, scope, storageKey, cache]);
  useEffect(() => {
    if (!op) return;
    if (op.session_id) sessionStorage.setItem("cfdc:last-task", op.session_id);
    if (
      op.status === "completed" ||
      op.status === "failed" ||
      op.status === "interrupted"
    ) {
      if (handled.current.has(op.operation_id)) return;
      handled.current.add(op.operation_id);
      identity.current.clear();
      sessionStorage.removeItem(storageKey);
      void cache.invalidateQueries({ queryKey: ["task"] });
      if (
        !taskId &&
        op.session_id &&
        currentLocation.current === originLocation.current
      )
        navigate(`/tasks/${op.session_id}`);
    }
  }, [op, cache, navigate, storageKey, taskId]);
  async function submit(path: string, body: Record<string, unknown>) {
    originLocation.current = location.key;
    setSending(true);
    setError("");
    setExpiredScope("");
    try {
      const result = await api<Operation>(path, {
        ...body,
        request_id: identity.current.get(),
      });
      sessionStorage.setItem(storageKey, result.operation_id);
      setRecord({ scope, id: result.operation_id });
      cache.setQueryData(["operation", result.operation_id], result);
      return result;
    } catch (e) {
      if (e instanceof ApiError) {
        identity.current.clear();
        if (e.detail.latest_revision !== undefined)
          void cache.invalidateQueries({ queryKey: ["task"] });
      }
      setError(
        e instanceof Error ? e.message : "网络请求失败；重试会沿用请求标识。",
      );
      throw e;
    } finally {
      setSending(false);
    }
  }
  return {
    submit,
    busy:
      sending ||
      (active && !!id && (!op || ["queued", "running"].includes(op.status))),
    op,
    error,
    view: (
      <Space orientation="vertical" style={{ width: "100%" }}>
        {error && <Alert type="error" title={error} />}{" "}
        {active && expiredScope === scope && (
          <Alert
            type="warning"
            title="操作记录已失效，请核对任务现状后重新操作。草稿已保留，不会自动重放。"
          />
        )}
        {active && !!id && query.error && (
          <Alert
            type="error"
            title="无法读取操作状态"
            action={
              <Button onClick={() => void query.refetch()}>重新读取</Button>
            }
          />
        )}{" "}
        {op && (
          <Alert
            type={
              op.status === "failed" || op.status === "interrupted"
                ? "error"
                : op.status === "completed"
                  ? "success"
                  : "info"
            }
            title={
              <Space>
                {["queued", "running"].includes(op.status) && (
                  <Spin size="small" />
                )}
                操作：{statusLabel(op.status)}
              </Space>
            }
            description={
              op.error?.message ?? "操作记录可在刷新后恢复；不会自动重放。"
            }
          />
        )}
      </Space>
    ),
  };
}
