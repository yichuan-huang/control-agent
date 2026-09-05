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
import { api } from "./api/client";
import type { Config, DTO } from "./api/types";
import { useSettings, ragLabel } from "./context";
export default function Settings({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const { credentials, setCredentials, useRag, setUseRag, setConnection } =
    useSettings();
  const [busy, setBusy] = useState(false);
  const pending = useRef(false);
  const [fieldErrors, setFieldErrors] = useState<
    Partial<Record<keyof typeof credentials, string>>
  >({});
  const [probeResult, setProbeResult] = useState<{
    title: string;
    type: "success" | "error";
  }>();
  const [doctorResult, setDoctorResult] = useState<{
    title: string;
    type: "success" | "error";
  }>();
  const [environmentResult, setEnvironmentResult] = useState<{
    title: string;
    type: "success" | "warning" | "error" | "info";
  }>();
  const [checks, setChecks] = useState<
    { name: string; status: string; message: string }[]
  >([]);
  const config = useQuery({
    queryKey: ["config"],
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
        Object.fromEntries(
          missing.map(([field, label]) => [field, `请填写 ${label}。`]),
        ),
      );
      if (missing.length) {
        document.getElementById(missing[0][2])?.focus();
        return;
      }
      setProbeResult(undefined);
      setConnection("检测中");
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
        setDoctorResult({ title: "环境检查完成。", type: "success" });
      } else {
        const d = await api<DTO<"ProbeResponse">>("/config/probe", {
          credentials,
        });
        setConnection(d.connected ? "已连接" : "连接失败");
        setProbeResult({
          title: `${d.connected ? "已连接" : "未连接"}：${d.message}`,
          type: d.connected ? "success" : "error",
        });
      }
    } catch (e) {
      if (doctor) {
        setDoctorResult({
          title: `环境检查失败：${String(e)}`,
          type: "error",
        });
      } else {
        setConnection("连接失败");
        setProbeResult({
          title: `连接测试失败：${String(e)}`,
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
          title: "已应用环境中的 Base URL 和 Model。",
          type: "success",
        });
      } else if (baseUrl || model) {
        setEnvironmentResult({
          title: `环境未提供 ${baseUrl ? "Model" : "Base URL"}，已保留当前值。`,
          type: "warning",
        });
      } else {
        setEnvironmentResult({
          title: "启动环境没有预设地址和模型，表单内容未更改。",
          type: "info",
        });
      }
    } catch {
      setEnvironmentResult({
        title: "读取环境配置失败，已保留当前值。",
        type: "error",
      });
    } finally {
      pending.current = false;
      setBusy(false);
    }
  }
  return (
    <Drawer title="设置" open={open} onClose={onClose} size="min(500px, 100%)">
      <Typography.Paragraph>
        Ollama、DeepSeek API 与 OpenAI API 均可配置。连接状态由显式测试确认。
      </Typography.Paragraph>
      <Form layout="vertical" disabled={busy}>
        <Form.Item
          label="Base URL"
          htmlFor="base-url"
          required
          validateStatus={fieldErrors.base_url ? "error" : undefined}
          help={
            fieldErrors.base_url && (
              <span id="base-url-error">{fieldErrors.base_url}</span>
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
              <span id="model-error">{fieldErrors.model}</span>
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
              <span id="api-key-error">{fieldErrors.api_key}</span>
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
          凭据仅保存在本页内存中，刷新后请重新输入。
        </Typography.Paragraph>
        <Form.Item label="新任务使用内置知识库">
          <Switch
            aria-label="新任务使用内置知识库"
            checked={useRag}
            onChange={setUseRag}
          />
        </Form.Item>
        <Typography.Paragraph>
          填写的配置用于当前页面的模型请求，无需另外保存；可点击下方按钮测试连接。
        </Typography.Paragraph>
        <Space wrap>
          <Button type="primary" loading={busy} onClick={() => void run()}>
            测试当前配置
          </Button>
          <Button loading={busy} onClick={() => void run(true)}>
            环境检查
          </Button>
        </Space>
      </Form>
      <Space orientation="vertical" style={{ width: "100%", marginTop: 24 }}>
        {probeResult && (
          <Alert title={probeResult.title} type={probeResult.type} showIcon />
        )}
        {doctorResult && (
          <Alert title={doctorResult.title} type={doctorResult.type} showIcon />
        )}
        <Collapse
          items={[
            {
              key: "environment",
              label: "高级设置",
              children: (
                <Space orientation="vertical" style={{ width: "100%" }}>
                  <Typography.Paragraph>
                    从程序启动环境变量 CFDC_LLM_BASE_URL 和 CFDC_LLM_MODEL
                    读取地址和模型；缺项保留表单原值，API Key 始终保留。
                  </Typography.Paragraph>
                  <Button
                    disabled={busy}
                    loading={busy}
                    onClick={() => void applyEnvironment()}
                  >
                    从启动环境导入地址和模型
                  </Button>
                  {environmentResult && (
                    <Alert
                      title={environmentResult.title}
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
          title={`知识库：${ragLabel(config.data?.rag.status)}`}
          description={config.data?.rag.message}
        />
        {checks.length > 0 && (
          <Table
            size="small"
            rowKey="name"
            dataSource={checks}
            pagination={false}
            columns={[
              { title: "检查", dataIndex: "name" },
              { title: "状态", dataIndex: "status" },
              { title: "说明", dataIndex: "message" },
            ]}
          />
        )}
      </Space>
    </Drawer>
  );
}
