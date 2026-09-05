import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Alert,
  Button,
  Drawer,
  Input,
  Pagination,
  Select,
  Space,
  Table,
  Tabs,
  Typography,
  Upload,
} from "antd";
import { api, download } from "./api/client";
import { useTaskReader } from "./api/useTaskReader";
import type { NodePage, DTO, Summary } from "./api/types";
import { parseObject } from "./safety";
import { useSettings } from "./context";
import { useOperation } from "./operations";

const artifactLabels: Record<string, string> = {
  report: "完整报告",
  task: "任务合同",
  diagnostic: "结构诊断",
  evidence: "公开证据",
  route: "路线选择",
  features: "特征",
  controller: "控制器",
  qualification: "资格审查",
  freeze: "冻结快照",
  evaluation: "开发评价",
  confirmation: "独立确认",
  tuning: "有界调优",
  events: "审计事件",
  agent_records: "Agent 执行与参考来源",
  phase_plan: "阶段方案",
  protocols: "实验协议",
  operator_handoffs: "操作交接",
  upload_receipts: "上传回执",
};
const downloadLabels: Record<string, string> = {
  bundle: "完整公开包",
  report: "原始报告",
  protocol: "实验协议",
  controller: "控制器",
  qualification: "资格审查",
  freeze: "冻结快照",
  evaluation: "开发评价",
  confirmation: "独立确认",
  exercise: "教学练习包",
  operator: "操作包",
  features: "特征",
  feedback: "调优反馈",
  result: "最终结果",
  audit: "审计记录",
  upload_receipt: "上传回执",
};

function NodeViewer({ task }: { task: Summary }) {
  const read = useTaskReader(task);
  const [artifact, setArtifact] = useState("report");
  const [pointer, setPointer] = useState("");
  const [offset, setOffset] = useState(0);
  const catalog = useQuery({
    queryKey: ["task", task.session_id, task.revision, "artifacts"],
    queryFn: () =>
      read<DTO<"ArtifactCatalog">>(`/tasks/${task.session_id}/artifacts`),
  });
  const page = useQuery({
    queryKey: [
      "task",
      task.session_id,
      task.revision,
      "node",
      artifact,
      pointer,
      offset,
    ],
    queryFn: () =>
      read<NodePage>(
        `/tasks/${task.session_id}/artifacts/${encodeURIComponent(artifact)}/node?${new URLSearchParams({ pointer, offset: String(offset), limit: "50" })}`,
      ),
  });
  return (
    <Space orientation="vertical" style={{ width: "100%" }}>
      <Select
        aria-label="选择产物"
        showSearch={{ optionFilterProp: "label" }}
        style={{ width: "100%" }}
        value={artifact}
        options={catalog.data?.items.map((i) => ({
          value: i.id,
          label: `${artifactLabels[i.id] ?? i.label} (${i.id})`,
        }))}
        onChange={(v) => {
          setArtifact(v);
          setPointer("");
          setOffset(0);
        }}
      />
      <Space wrap>
        <Button
          disabled={!pointer}
          onClick={() => {
            setPointer(pointer.slice(0, pointer.lastIndexOf("/")));
            setOffset(0);
          }}
        >
          上一级
        </Button>
        <Typography.Text code>{pointer || "/"}</Typography.Text>
        <a href={download(task.session_id, "artifact", artifact)}>
          下载完整产物
        </a>
      </Space>
      {page.error && <Alert type="error" title={String(page.error)} />}
      <Table
        size="small"
        scroll={{ x: 480, y: 420 }}
        virtual
        loading={page.isLoading}
        rowKey="pointer"
        pagination={false}
        dataSource={page.data?.items}
        columns={[
          {
            title: "字段",
            dataIndex: "key",
            render: (v, row) => (
              <Button
                type="link"
                disabled={!row.expandable}
                onClick={() => {
                  setPointer(row.pointer);
                  setOffset(0);
                }}
              >
                {v}
              </Button>
            ),
          },
          { title: "类型", dataIndex: "kind" },
          { title: "预览", dataIndex: "preview" },
        ]}
      />
      {page.data?.kind === "string" && <pre>{page.data.text}</pre>}
      {page.data?.kind === "value" && (
        <pre>{JSON.stringify(page.data.value)}</pre>
      )}
      <Pagination
        current={offset / (page.data?.kind === "string" ? 8192 : 50) + 1}
        total={page.data?.total ?? 0}
        pageSize={page.data?.kind === "string" ? 8192 : 50}
        showSizeChanger={false}
        onChange={(p) =>
          setOffset((p - 1) * (page.data?.kind === "string" ? 8192 : 50))
        }
      />
      <Typography.Text type="secondary">
        逐层加载当前页；完整原始记录通过下载保留。
      </Typography.Text>
    </Space>
  );
}
function Timeline({ task }: { task: Summary }) {
  const read = useTaskReader(task);
  const [offset, setOffset] = useState(0);
  const q = useQuery({
    queryKey: ["task", task.session_id, task.revision, "events", offset],
    queryFn: () =>
      read<DTO<"SectionPage">>(
        `/tasks/${task.session_id}/sections/events?offset=${offset}&limit=50`,
      ),
  });
  return (
    <>
      {q.error && <Alert type="error" title={String(q.error)} />}{" "}
      <Typography.Paragraph>
        任务 → 诊断 → 取证 → 路线／特征 → 控制器 → 冻结 → 评价 → 调优／确认 →
        结果
      </Typography.Paragraph>
      <Table
        size="small"
        virtual
        scroll={{ x: 640, y: 420 }}
        loading={q.isLoading}
        pagination={false}
        rowKey={(_, index) => String(offset + (index ?? 0))}
        dataSource={q.data?.items}
        columns={[
          {
            title: "序号",
            width: 70,
            render: (_, __, index) => offset + index + 1,
          },
          {
            title: "已记录事件（按原始顺序）",
            render: (_, row) => (
              <Typography.Text style={{ whiteSpace: "pre-wrap" }}>
                {JSON.stringify(row)}
              </Typography.Text>
            ),
          },
        ]}
      />
      <Pagination
        total={q.data?.total}
        pageSize={50}
        current={offset / 50 + 1}
        onChange={(p) => setOffset((p - 1) * 50)}
      />
    </>
  );
}
export default function Expert({
  task,
  onClose,
}: {
  task?: Summary;
  onClose: () => void;
}) {
  const [tab, setTab] = useState(task ? "artifacts" : "submit");
  const [text, setText] = useState("");
  const [feedback, setFeedback] = useState("");
  const [busy, setBusy] = useState(false);
  const { credentials, useRag } = useSettings();
  const taskOperation = useOperation(task?.session_id, tab !== "import");
  const importOperation = useOperation(undefined, tab === "import");
  const operation = tab === "import" ? importOperation : taskOperation;
  async function validate() {
    setBusy(true);
    try {
      await api("/artifacts/validate", { payload: parseObject(text) });
      setFeedback("产物合同校验通过；校验不授予执行权限。");
    } catch (e) {
      setFeedback(String(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <Drawer title="专家工具" open onClose={onClose} size={860} destroyOnHidden>
      <Tabs
        activeKey={tab}
        onChange={setTab}
        items={[
          ...(task
            ? [
                { key: "artifacts", label: "产物浏览" },
                { key: "events", label: "九阶段时间线 / 审计" },
              ]
            : []),
          { key: "submit", label: task ? "JSON 提交" : "完整任务合同" },
          { key: "validate", label: "产物校验" },
          { key: "import", label: "历史公开包导入" },
          ...(task ? [{ key: "downloads", label: "下载" }] : []),
        ]}
      />
      {tab === "artifacts" && task && <NodeViewer task={task} />}{" "}
      {tab === "events" && task && <Timeline task={task} />}{" "}
      {["submit", "validate"].includes(tab) && (
        <Space orientation="vertical" style={{ width: "100%" }}>
          {task && tab === "submit" && (
            <Alert
              title={`当前允许动作：${task.workspace.action_title}`}
              description={String(task.input_contract.guidance ?? "")}
            />
          )}
          <Input.TextArea
            aria-label="专家 JSON"
            rows={14}
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="粘贴完整 JSON 对象"
          />
          {task && tab === "submit" && (
            <Button
              onClick={() =>
                setText(
                  JSON.stringify(
                    task.input_contract.json_template ?? {},
                    null,
                    2,
                  ),
                )
              }
            >
              载入当前字段模板
            </Button>
          )}
          <Button
            loading={busy || operation.busy}
            disabled={
              tab === "submit" &&
              !!task &&
              (!task.workspace.actionable || task.read_only)
            }
            onClick={() => {
              if (tab === "validate") void validate();
              else {
                try {
                  const payload = parseObject(text);
                  void operation
                    .submit(
                      task ? `/tasks/${task.session_id}/actions` : "/tasks",
                      task
                        ? {
                            expected_revision: task.revision,
                            action: task.workspace.action,
                            input: { mode: "json", payload },
                            credentials,
                          }
                        : {
                            task: payload,
                            confirmed: false,
                            use_rag: useRag,
                            credentials,
                          },
                    )
                    .catch(() => {});
                } catch (e) {
                  setFeedback(String(e));
                }
              }
            }}
          >
            {tab === "validate"
              ? "校验产物"
              : task
                ? "提交当前动作"
                : "创建未确认任务"}
          </Button>
        </Space>
      )}
      {tab === "import" && (
        <>
          <Typography.Paragraph>
            导入后需重新确认任务边界；不会继承案例执行权限或知识库绑定。
          </Typography.Paragraph>
          <Upload
            accept=".zip"
            showUploadList={false}
            beforeUpload={(file) => {
              const data = new FormData();
              data.append("file", file);
              setBusy(true);
              void api<DTO<"UploadResponse">>("/uploads", data)
                .then((r) =>
                  operation.submit("/imports", { file_id: r.file_id }),
                )
                .catch((e) => setFeedback(String(e)))
                .finally(() => setBusy(false));
              return false;
            }}
          >
            <Button loading={busy || operation.busy}>选择历史公开 ZIP</Button>
          </Upload>
        </>
      )}
      {tab === "downloads" && task && (
        <Space wrap>
          {Object.entries(downloadLabels).map(([kind, label]) => (
            <Button key={kind} href={download(task.session_id, kind)}>
              {label}
            </Button>
          ))}
        </Space>
      )}
      {feedback && <Alert style={{ marginTop: 16 }} title={feedback} />}{" "}
      {operation.view}
    </Drawer>
  );
}
