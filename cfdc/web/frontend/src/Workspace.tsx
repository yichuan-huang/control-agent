import { lazy, Suspense, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  Alert,
  Button,
  Card,
  Checkbox,
  Collapse,
  Input,
  Radio,
  Space,
  Spin,
  Steps,
  Table,
  Tag,
  Typography,
  Upload,
} from "antd";
import { api, download } from "./api/client";
import type { Summary, DTO, Obj } from "./api/types";
import { useSettings } from "./context";
import { useOperation } from "./operations";
import Results from "./Results";
import Markdown from "./Markdown";
import { TaskBounds } from "./ReviewDetails";
import { statusLabel } from "./labels";
import { useTaskReader } from "./api/useTaskReader";
import DataCurves from "./DataCurves";
import ManualRequirements from "./ManualRequirements";
import WorkflowGuide from "./WorkflowGuide";
import ExternalWorkflow, { externalActions } from "./ExternalWorkflow";
const precheckLabels: Record<string, string> = {
  channels: "已核对测量与控制通道",
  units: "已核对数据单位",
  logger: "记录工具能够保存全部试验数据",
  "stop condition": "已核对停止条件",
  "initial condition": "已核对初始条件",
};
const Expert = lazy(() => import("./Expert"));
export function Protocol({ task }: { task: Summary }) {
  const read = useTaskReader(task);
  const p = useQuery({
    queryKey: ["task", task.session_id, task.revision, "protocol"],
    queryFn: () =>
      read<DTO<"ProtocolView">>(`/tasks/${task.session_id}/protocol`),
  });
  return (
    <Card title="实验协议与上传回执" loading={p.isLoading}>
      {p.error && <Alert type="error" title={String(p.error)} />}
      <Markdown>{p.data?.summary ?? ""}</Markdown>
      <Typography.Paragraph>{p.data?.feedback}</Typography.Paragraph>
      <Space wrap>
        <a href={download(task.session_id, "protocol")}>下载协议</a>
        <a href={download(task.session_id, "operator")}>下载操作包</a>
        {!task.external_workflow && (
          <a href={download(task.session_id, "exercise")}>下载练习包</a>
        )}
      </Space>
      {p.data?.accepted && (
        <Table
          scroll={{ x: 500 }}
          size="small"
          pagination={false}
          rowKey={(_, i) => String(i)}
          columns={p.data.preview.columns.map((title, i) => ({
            title,
            render: (_: unknown, row: unknown[]) => String(row[i] ?? ""),
          }))}
          dataSource={p.data.preview.rows}
        />
      )}
      {p.data && (
        <DataCurves task={task} options={p.data.evidence_options ?? []} />
      )}
    </Card>
  );
}
export default function Workspace() {
  const { id = "" } = useParams();
  return <WorkspaceSession key={id} id={id} />;
}
function WorkspaceSession({ id }: { id: string }) {
  const task = useQuery({
    queryKey: ["task", id],
    queryFn: () => api<Summary>(`/tasks/${id}`),
    refetchOnWindowFocus: true,
  });
  const recent = useQuery({
    queryKey: ["task", id, "operations"],
    queryFn: () => api<DTO<"OperationList">>(`/tasks/${id}/operations`),
    refetchInterval: (query) =>
      !query.state.error &&
      query.state.data?.items.some((item) =>
        ["queued", "running"].includes(item.status),
      )
        ? 800
        : false,
  });
  const latestRevision = Math.max(
    0,
    ...(recent.data?.items.map(
      (item) => item.result?.revision ?? item.error?.latest_revision ?? 0,
    ) ?? []),
  );
  const taskRevision = task.data?.revision;
  const refreshTask = task.refetch;
  useEffect(() => {
    if (taskRevision !== undefined && latestRevision > taskRevision)
      void refreshTask();
  }, [latestRevision, taskRevision, refreshTask]);
  const [text, setText] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  const [decision, setDecision] = useState("accepted");
  const [checks, setChecks] = useState<string[]>([]);
  const [note, setNote] = useState("");
  const [files, setFiles] = useState<{ file_id: string; filename: string }[]>(
    [],
  );
  const [stopped, setStopped] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [expert, setExpert] = useState(false);
  const { credentials } = useSettings();
  const operation = useOperation(id);
  const t = task.data;
  if (!t)
    return task.error ? (
      <Alert
        type="error"
        title={String(task.error)}
        action={<Button onClick={() => void task.refetch()}>重试</Button>}
      />
    ) : (
      <Spin />
    );
  const action = t.workspace.action;
  const external = (t as Summary & { external_workflow?: Obj })
    .external_workflow;
  const showProtocol =
    !!external && ["record_operator_report", "ingest_upload"].includes(action);
  const guidedExternal =
    !!external && (externalActions.has(action) || action === "freeze");
  const modes = (t.input_contract.allowed_modes ?? []) as string[];
  async function submit() {
    if (!t) return;
    const input =
      action === "confirm_task"
        ? { confirmed }
        : action === "record_operator_report"
          ? { payload: { decision, prechecks_completed: checks, note } }
          : action === "ingest_upload"
            ? {
                file_ids: files.map((f) => f.file_id),
                stopped_on_limit: stopped,
              }
            : modes.includes("natural_language")
              ? { text, mode: "natural_language" }
              : {};
    await operation
      .submit(`/tasks/${id}/actions`, {
        expected_revision: t.revision,
        action,
        input,
        credentials,
      })
      .catch(() => {});
  }
  const activeRecent = recent.data?.items.find((o) =>
    ["queued", "running"].includes(o.status),
  );
  const busy = operation.busy || !!activeRecent;
  const externalView = external && (
    <ExternalWorkflow
      key={`${id}:${t.revision}:${action}`}
      sessionId={id}
      action={
        guidedExternal &&
        (!t.read_only || external?.resume_pending === true) &&
        !external?.recovery_required
          ? action
          : ""
      }
      workflow={{
        ...external,
        evaluation_repeats: (t.task.budgets as Obj | undefined)
          ?.evaluation_repeats,
      }}
      requirements={t.upload_requirements ?? undefined}
      busy={busy}
      onSubmit={(externalAction, input) => {
        void operation
          .submit(`/tasks/${id}/actions`, {
            expected_revision: t.revision,
            action: externalAction,
            input,
            credentials,
          })
          .catch(() => {});
      }}
    />
  );
  return (
    <>
      <div className="workspace-heading">
        <div>
          <Typography.Text type="secondary">
            任务 {id.slice(0, 12)} · 修订 {t.revision}
          </Typography.Text>
          <Typography.Title level={2}>{t.workspace.title}</Typography.Title>
        </div>
        <Space wrap>
          <Tag>{statusLabel(t.status)}</Tag>
          <Button
            onClick={() => void Promise.all([task.refetch(), recent.refetch()])}
          >
            刷新
          </Button>
          <Button onClick={() => setExpert(true)}>专家工具</Button>
        </Space>
      </div>
      <Steps
        current={t.workspace.stage}
        items={["明确任务", "获取证据", "形成方案", "评价与确认"].map(
          (title) => ({ title }),
        )}
      />
      <div className="workspace-grid">
        <main>
          <Card id="current-action" title="当前步骤">
            <Typography.Paragraph className="preserve">
              {t.workspace.explanation}
            </Typography.Paragraph>
            {t.workspace.actionable && (
              <>
                <Typography.Title level={4}>
                  {t.workspace.action_title}
                </Typography.Title>
                <Typography.Paragraph>
                  {t.workspace.action_help}
                </Typography.Paragraph>
              </>
            )}
            <WorkflowGuide
              value={(t as Summary & { workflow_guide?: Obj }).workflow_guide}
            />
            {t.read_only && <Alert title="此任务只读" />}
            {(guidedExternal || external?.recovery_required === true) &&
              externalView}
            {t.workspace.actionable &&
              !t.read_only &&
              !guidedExternal &&
              !external?.recovery_required && (
                <Space orientation="vertical" style={{ width: "100%" }}>
                  {action === "confirm_task" && (
                    <Checkbox
                      checked={confirmed}
                      onChange={(e) => setConfirmed(e.target.checked)}
                    >
                      我已核对软件试验边界与预算
                    </Checkbox>
                  )}
                  {action === "record_operator_report" && (
                    <>
                      <Typography.Paragraph>
                        本步目的：确认您能按采集协议记录有效证据。由您下载并阅读采集请求包，核对每种试验的输入、时长、采样要求、文件模板和停止规则。
                      </Typography.Paragraph>
                      <a href={download(id, "operator")}>下载采集请求包 ZIP</a>
                      <Typography.Paragraph>
                        逐项检查下列条件并填写检查结论；不确定时选择“需要澄清”并说明缺少的条件。提交检查后，下一步是在您自己的环境中执行采集，再回到此页上传数据。此确认只用于工作流记录，不授权任何硬件操作。
                      </Typography.Paragraph>
                      <Radio.Group
                        value={decision}
                        onChange={(e) => setDecision(e.target.value)}
                        options={[
                          { label: "检查完成，可以继续", value: "accepted" },
                          { label: "需要澄清", value: "needs_clarification" },
                          { label: "拒绝执行", value: "refused" },
                        ]}
                      />
                      <Checkbox.Group
                        options={(
                          (t.input_contract.operator_prechecks ??
                            []) as string[]
                        ).map((value) => ({
                          value,
                          label: precheckLabels[value] ?? value,
                        }))}
                        value={checks}
                        onChange={(v) => setChecks(v as string[])}
                      />
                      <Input.TextArea
                        aria-label="操作员说明"
                        value={note}
                        onChange={(e) => setNote(e.target.value)}
                        placeholder="操作检查说明"
                      />
                    </>
                  )}
                  {action === "ingest_upload" && (
                    <>
                      <Typography.Text strong>
                        1 · 下载并核对本任务的采集要求
                      </Typography.Text>
                      <a href={download(id, "operator")}>下载采集请求包 ZIP</a>
                      <Typography.Paragraph>
                        本步目的：提供能支持控制方案的原始证据。请求包包含协议、试验清单和待填写的数据模板；下载请求包不会完成采集。按下面的文件名、列名、单位与重复次数准备记录。
                      </Typography.Paragraph>
                      <Typography.Text strong>
                        2 · 由您在外部环境执行采集
                      </Typography.Text>
                      <Typography.Paragraph>
                        实际试验在应用外部完成。使用自己的仿真环境或实验设施，按协议逐项设置初始条件、输入和采样间隔，记录全部时间点的输入与输出。触及限制时立即在外部停止并如实保留停止记录；不要补造、覆盖或修改被拒绝的证据。
                      </Typography.Paragraph>
                      <Typography.Text strong>
                        3 · 回到此页上传并提交校验
                      </Typography.Text>
                      <Typography.Paragraph>
                        用真实记录填写请求包的数据模板，保持原文件名与协议标识；按下列格式上传结果文件或结果
                        ZIP。不要直接上传空模板。已接收的试次会保留，按回执补充缺失文件；只有本地选中文件后，还需点击下方提交按钮。
                      </Typography.Paragraph>
                      <ManualRequirements
                        value={
                          (t as Summary & { upload_requirements?: Obj })
                            .upload_requirements
                        }
                      />
                      <Upload
                        multiple
                        accept=".csv,.json,.zip"
                        showUploadList={false}
                        beforeUpload={(file) => {
                          const body = new FormData();
                          body.append("file", file);
                          body.append("session_id", id);
                          setUploading(true);
                          void api<DTO<"UploadResponse">>("/uploads", body)
                            .then((v) => setFiles((old) => [...old, v]))
                            .catch((e) => setError(String(e)))
                            .finally(() => setUploading(false));
                          return false;
                        }}
                      >
                        <Button loading={uploading}>选择实验数据</Button>
                      </Upload>
                      {files.map((f) => (
                        <Space key={f.file_id}>
                          {f.filename}
                          <Button
                            size="small"
                            onClick={() =>
                              setFiles(
                                files.filter((v) => v.file_id !== f.file_id),
                              )
                            }
                          >
                            移除
                          </Button>
                        </Space>
                      ))}
                      <Typography.Paragraph>
                        完成后：系统校验原始数据、自动提取特征、合成并审查候选控制器。无需您提交特征或控制器
                        JSON；通过后进入评价约定的冻结确认，未通过则在本页显示原因和可执行的下一步。
                      </Typography.Paragraph>
                      <Checkbox
                        checked={stopped}
                        onChange={(e) => setStopped(e.target.checked)}
                      >
                        实验触及限制，已停止
                      </Checkbox>
                    </>
                  )}
                  {modes.includes("natural_language") && (
                    <>
                      {" "}
                      <Input.TextArea
                        aria-label="当前步骤回复"
                        rows={7}
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                        placeholder={String(
                          t.input_contract.guidance ??
                            "描述已观察到的现象；不知道的内容可以写不知道。",
                        )}
                      />
                      <Button
                        onClick={() =>
                          setText(
                            (previous) =>
                              `${previous}${previous ? "\n" : ""}对于当前问题，我不知道或没有测过。`,
                          )
                        }
                      >
                        不知道 / 没有测过
                      </Button>
                    </>
                  )}{" "}
                  {modes.length > 0 &&
                  !modes.includes("natural_language") &&
                  !["record_operator_report", "ingest_upload"].includes(
                    action,
                  ) ? (
                    <Button type="primary" onClick={() => setExpert(true)}>
                      打开专业 JSON 提交
                    </Button>
                  ) : (
                    <Button
                      type="primary"
                      loading={busy}
                      disabled={
                        uploading ||
                        (action === "confirm_task" && !confirmed) ||
                        (action === "ingest_upload" && !files.length)
                      }
                      onClick={() => void submit()}
                    >
                      {t.workspace.action_title}
                    </Button>
                  )}
                  {action === "run_feedback_iteration" && (
                    <Typography.Text type="secondary">
                      每次点击仅执行当前有界调优步骤，下一阶段由 Kernel 决定。
                    </Typography.Text>
                  )}
                </Space>
              )}
            {!guidedExternal && !external?.recovery_required && externalView}
            {error && <Alert type="error" title={error} />} {operation.view}
            {activeRecent && !operation.op && (
              <Alert
                title="此任务有正在执行的操作"
                description="正在等待持久化操作完成。"
                action={
                  <Button
                    onClick={() => {
                      sessionStorage.setItem(
                        `cfdc:operation:task:${id}`,
                        activeRecent.operation_id,
                      );
                      window.location.reload();
                    }}
                  >
                    恢复操作跟踪
                  </Button>
                }
              />
            )}
          </Card>
          {showProtocol && <Protocol task={t} />}
          {!showProtocol && (
            <Collapse
              items={[
                {
                  key: "protocol",
                  label: "实验协议与上传回执",
                  children: <Protocol task={t} />,
                },
              ]}
            />
          )}
          {t.workspace.result_visible && <Results task={t} />}
        </main>
        <aside>
          <Card title="任务约定">
            <Markdown>{t.workspace.task_summary}</Markdown>
            <TaskBounds task={t.task} />
            <Typography.Text type="secondary">
              知识库快照：{t.rag_snapshot ?? "未绑定"}
            </Typography.Text>
          </Card>
          <Card title="任务记录">
            <Space orientation="vertical">
              <a href={download(id, "bundle")}>导出完整公开包</a>
              <a href={download(id, "report")}>下载原始报告</a>
              <Button
                danger
                disabled={
                  busy ||
                  t.read_only ||
                  ["performance_met", "capability_gap", "cancelled"].includes(
                    t.status,
                  )
                }
                onClick={() =>
                  void operation
                    .submit(`/tasks/${id}/actions`, {
                      expected_revision: t.revision,
                      action: "cancel",
                      credentials,
                    })
                    .catch(() => {})
                }
              >
                取消任务
              </Button>
            </Space>
          </Card>
        </aside>
      </div>
      {expert && (
        <Suspense fallback={<Spin />}>
          <Expert task={t} onClose={() => setExpert(false)} />
        </Suspense>
      )}
    </>
  );
}
