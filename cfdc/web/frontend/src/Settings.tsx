import { statusLabel } from "./labels";
import { keepLocaleData, useI18n, type MessageRef } from "./i18n";
import { useEffect, useRef, useState } from "react";
import {
  Alert,
  Button,
  Collapse,
  Drawer,
  Form,
  Input,
  Space,
  Switch,
  Table,
  Typography,
} from "antd";
import { useQuery } from "@tanstack/react-query";
import { useApi } from "./api/client";
import type { Config, DTO } from "./api/types";
import { useSettings, ragLabel } from "./context";
export default function Settings({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const { t: tr, locale, message, errorText } = useI18n();
  const { api } = useApi();

  const { credentials, setCredentials, useRag, setUseRag, setConnection } =
    useSettings();
  const [busy, setBusy] = useState(false);
  const pending = useRef(false);
  const [fieldErrors, setFieldErrors] = useState<
    Partial<Record<keyof typeof credentials, string>>
  >({});
  const [probeResult, setProbeResult] = useState<{
    title: MessageRef;
    cause?: unknown;
    type: "success" | "error";
  }>();
  const [doctorResult, setDoctorResult] = useState<{
    title: MessageRef;
    cause?: unknown;
    type: "success" | "error";
  }>();
  const [environmentResult, setEnvironmentResult] = useState<{
    title: MessageRef;
    cause?: unknown;
    type: "success" | "warning" | "error" | "info";
  }>();
  const [checks, setChecks] = useState<
    (DTO<"DoctorResponse">["checks"][number] & {
      message_ref?: MessageRef | null;
    })[]
  >([]);
  const config = useQuery({
    placeholderData: keepLocaleData(locale, ["config", locale]),
    queryKey: ["config", locale],
    queryFn: () => api<Config>("/config"),
    enabled: open,
    refetchInterval: (q) =>
      q.state.data?.rag.status === "preparing" ? 2000 : false,
  });
  const initialized = useRef(false);
  useEffect(() => {
    if (!config.data || initialized.current) return;
    initialized.current = true;
    setCredentials({
      ...credentials,
      base_url: credentials.base_url || config.data.base_url,
      model: credentials.model || config.data.model,
    });
  }, [config.data, credentials, setCredentials]);
  function editCredentials(next: string, field: keyof typeof credentials) {
    setProbeResult(undefined);
    setFieldErrors((previous) => ({ ...previous, [field]: undefined }));
    setCredentials({ ...credentials, [field]: next });
  }
  async function run(doctor = false) {
    if (pending.current) return;
    if (!doctor) {
      const fields = [
        ["base_url", "Base URL", "base-url"],
        ["model", "Model", "model"],
        ["api_key", "API Key", "api-key"],
      ] as const;
      const missing = fields.filter(([field]) => !credentials[field].trim());
      setFieldErrors(
        Object.fromEntries(missing.map(([field, label]) => [field, label])),
      );
      if (missing.length) {
        document.getElementById(missing[0][2])?.focus();
        return;
      }
      setProbeResult(undefined);
      setConnection("checking");
    }
    pending.current = true;
    setBusy(true);
    if (doctor) {
      setChecks([]);
      setDoctorResult(undefined);
    }
    try {
      if (doctor) {
        const d = await api<DTO<"DoctorResponse">>("/config/doctor", {
          credentials,
          use_rag: useRag,
        });
        setChecks(d.checks);
        setDoctorResult({
          title: { key: "frontend.settings.doctor_complete" },
          type: "success",
        });
      } else {
        const d = await api<DTO<"ProbeResponse">>("/config/probe", {
          credentials,
        });
        setConnection(d.connected ? "connected" : "failed");
        setProbeResult({
          title: {
            key: "frontend.settings.connection_result",
            params: {
              status: {
                key: d.connected
                  ? "frontend.settings.connected"
                  : "frontend.settings.not_connected",
              },
              message: d.message_ref ?? d.message,
            },
          },
          type: d.connected ? "success" : "error",
        });
      }
    } catch (e) {
      if (doctor) {
        setDoctorResult({
          title: { key: "frontend.settings.doctor_failed" },
          cause: e,
          type: "error",
        });
      } else {
        setConnection("failed");
        setProbeResult({
          title: { key: "frontend.settings.probe_failed" },
          cause: e,
          type: "error",
        });
      }
    } finally {
      pending.current = false;
      setBusy(false);
    }
  }
  async function applyEnvironment() {
    if (pending.current) return;
    pending.current = true;
    setBusy(true);
    setEnvironmentResult(undefined);
    try {
      const refreshed = await config.refetch({ throwOnError: true });
      const baseUrl = refreshed.data?.base_url.trim() ?? "";
      const model = refreshed.data?.model.trim() ?? "";
      const next = {
        base_url: baseUrl || credentials.base_url,
        model: model || credentials.model,
        api_key: credentials.api_key,
      };
      if (
        next.base_url !== credentials.base_url ||
        next.model !== credentials.model
      ) {
        setProbeResult(undefined);
        setFieldErrors((previous) => ({
          ...previous,
          base_url: next.base_url.trim() ? undefined : previous.base_url,
          model: next.model.trim() ? undefined : previous.model,
        }));
        setCredentials(next);
      }
      if (baseUrl && model) {
        setEnvironmentResult({
          title: { key: "frontend.settings.environment_applied" },
          type: "success",
        });
      } else if (baseUrl || model) {
        setEnvironmentResult({
          title: {
            key: "frontend.settings.environment_missing",
            params: { field: baseUrl ? "Model" : "Base URL" },
          },
          type: "warning",
        });
      } else {
        setEnvironmentResult({
          title: { key: "frontend.settings.environment_empty" },
          type: "info",
        });
      }
    } catch {
      setEnvironmentResult({
        title: { key: "frontend.settings.environment_failed" },
        type: "error",
      });
    } finally {
      pending.current = false;
      setBusy(false);
    }
  }
  return (
    <Drawer
      title={tr("frontend.app.settings")}
      open={open}
      onClose={onClose}
      size="min(500px, 100%)"
    >
      <Typography.Paragraph>
        {tr("frontend.settings.providers_help")}
      </Typography.Paragraph>
      <Form layout="vertical" disabled={busy}>
        <Form.Item
          label="Base URL"
          htmlFor="base-url"
          required
          validateStatus={fieldErrors.base_url ? "error" : undefined}
          help={
            fieldErrors.base_url && (
              <span id="base-url-error">
                {tr("frontend.settings.required_field", {
                  field: fieldErrors.base_url,
                })}
              </span>
            )
          }
        >
          <Input
            id="base-url"
            aria-invalid={!!fieldErrors.base_url}
            aria-describedby={
              fieldErrors.base_url ? "base-url-error" : undefined
            }
            value={credentials.base_url}
            placeholder={config.data?.base_url || "http://127.0.0.1:11434/v1"}
            onChange={(e) => editCredentials(e.target.value, "base_url")}
          />
        </Form.Item>
        <Form.Item
          label="Model"
          htmlFor="model"
          required
          validateStatus={fieldErrors.model ? "error" : undefined}
          help={
            fieldErrors.model && (
              <span id="model-error">
                {tr("frontend.settings.required_field", {
                  field: fieldErrors.model,
                })}
              </span>
            )
          }
        >
          <Input
            id="model"
            aria-invalid={!!fieldErrors.model}
            aria-describedby={fieldErrors.model ? "model-error" : undefined}
            value={credentials.model}
            placeholder={config.data?.model || "gemma4:e4b"}
            onChange={(e) => editCredentials(e.target.value, "model")}
          />
        </Form.Item>
        <Form.Item
          label="API Key"
          htmlFor="api-key"
          required
          validateStatus={fieldErrors.api_key ? "error" : undefined}
          help={
            fieldErrors.api_key && (
              <span id="api-key-error">
                {tr("frontend.settings.required_field", {
                  field: fieldErrors.api_key,
                })}
              </span>
            )
          }
        >
          <Input.Password
            id="api-key"
            aria-invalid={!!fieldErrors.api_key}
            aria-describedby={fieldErrors.api_key ? "api-key-error" : undefined}
            autoComplete="off"
            value={credentials.api_key}
            onChange={(e) => editCredentials(e.target.value, "api_key")}
          />
        </Form.Item>
        <Typography.Paragraph type="secondary">
          {tr("frontend.settings.credentials_help")}
        </Typography.Paragraph>
        <Form.Item label={tr("frontend.settings.use_rag")}>
          <Switch
            aria-label={tr("frontend.settings.use_rag")}
            checked={useRag}
            onChange={setUseRag}
          />
        </Form.Item>
        <Typography.Paragraph>
          {tr("frontend.settings.configuration_help")}
        </Typography.Paragraph>
        <Space wrap>
          <Button type="primary" loading={busy} onClick={() => void run()}>
            {tr("frontend.settings.test_connection")}
          </Button>
          <Button loading={busy} onClick={() => void run(true)}>
            {tr("frontend.settings.environment_check")}
          </Button>
        </Space>
      </Form>
      <Space orientation="vertical" style={{ width: "100%", marginTop: 24 }}>
        {probeResult && (
          <Alert
            title={message({
              ...probeResult.title,
              params: {
                ...probeResult.title.params,
                error: probeResult.cause ? errorText(probeResult.cause) : "",
              },
            })}
            type={probeResult.type}
            showIcon
          />
        )}
        {doctorResult && (
          <Alert
            title={message({
              ...doctorResult.title,
              params: {
                ...doctorResult.title.params,
                error: doctorResult.cause ? errorText(doctorResult.cause) : "",
              },
            })}
            type={doctorResult.type}
            showIcon
          />
        )}
        <Collapse
          items={[
            {
              key: "environment",
              label: tr("frontend.settings.advanced"),
              children: (
                <Space orientation="vertical" style={{ width: "100%" }}>
                  <Typography.Paragraph>
                    {tr("frontend.settings.environment_help")}
                  </Typography.Paragraph>
                  <Button
                    disabled={busy}
                    loading={busy}
                    onClick={() => void applyEnvironment()}
                  >
                    {tr("frontend.settings.import_environment")}
                  </Button>
                  {environmentResult && (
                    <Alert
                      title={message({
                        ...environmentResult.title,
                        params: {
                          ...environmentResult.title.params,
                          error: environmentResult.cause
                            ? errorText(environmentResult.cause)
                            : "",
                        },
                      })}
                      type={environmentResult.type}
                      showIcon
                    />
                  )}
                </Space>
              ),
            },
          ]}
        />
        <Alert
          title={tr("frontend.settings.rag_status", {
            status: ragLabel(config.data?.rag.status, tr),
          })}
          description={message(
            config.data?.rag.message_ref,
            config.data?.rag.message,
          )}
        />
        {checks.length > 0 && (
          <Table
            size="small"
            rowKey="name"
            dataSource={checks}
            pagination={false}
            columns={[
              { title: tr("frontend.settings.check"), dataIndex: "name" },
              {
                title: tr("frontend.externalworkflow.status"),
                dataIndex: "status",
                render: (value: string) => statusLabel(value, tr),
              },
              {
                title: tr("frontend.results.description"),
                dataIndex: "message",
                render: (_: unknown, row: (typeof checks)[number]) =>
                  message(row.message_ref, row.message),
              },
            ]}
          />
        )}
      </Space>
    </Drawer>
  );
}
