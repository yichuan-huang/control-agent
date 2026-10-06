import { keepLocaleData, useI18n, LocalizedError } from "./i18n";
import { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Alert, Button, Space, Spin } from "antd";
import { useApi, ApiError } from "./api/client";
import type { Operation } from "./api/types";
import { statusLabel } from "./labels";
import { requestIdentity } from "./safety";
export function useOperation(taskId?: string, active = true) {
  const { t: tr, locale, errorText } = useI18n();
  const { api } = useApi();

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
  const [error, setError] = useState<unknown>();
  const [expiredScope, setExpiredScope] = useState("");
  const [sending, setSending] = useState(false);
  const identity = useRef(requestIdentity());
  const handled = useRef(new Set<string>());
  const navigate = useNavigate();
  const cache = useQueryClient();
  const query = useQuery({
    placeholderData: keepLocaleData(locale, ["operation", locale, id]),
    queryKey: ["operation", locale, id],
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
    cache.removeQueries({ queryKey: ["operation", locale, id], exact: true });
    void cache.invalidateQueries({ queryKey: ["task"] });
  }, [active, id, query.error, scope, storageKey, cache, locale]);
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
        op.session_id &&
        op.session_id !== taskId &&
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
      cache.setQueryData(["operation", locale, result.operation_id], result);
      return result;
    } catch (e) {
      if (e instanceof ApiError) {
        identity.current.clear();
        if (e.detail.latest_revision !== undefined)
          void cache.invalidateQueries({ queryKey: ["task"] });
      }
      setError(
        e instanceof ApiError || e instanceof LocalizedError
          ? e
          : e instanceof Error
            ? e.message
            : new LocalizedError({ key: "frontend.operations.network_error" }),
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
    error: error ? errorText(error) : "",
    view: (
      <Space orientation="vertical" style={{ width: "100%" }}>
        {!!error && <Alert type="error" title={errorText(error)} />}{" "}
        {active && expiredScope === scope && (
          <Alert type="warning" title={tr("frontend.operations.expired")} />
        )}
        {active && !!id && query.error && (
          <Alert
            type="error"
            title={tr("frontend.operations.read_failed")}
            action={
              <Button onClick={() => void query.refetch()}>
                {tr("frontend.wizard.reload")}
              </Button>
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
                <span>
                  {tr("frontend.operations.operation_prefix")}
                  {statusLabel(op.status, tr)}
                </span>
              </Space>
            }
            description={
              op.error
                ? errorText({ detail: op.error })
                : tr("frontend.operations.recovery_help")
            }
          />
        )}
      </Space>
    ),
  };
}
