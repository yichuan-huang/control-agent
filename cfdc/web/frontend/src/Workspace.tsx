import { keepLocaleData, useI18n } from "./i18n";
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
import { useApi } from "./api/client";
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
const Expert = lazy(() => import("./Expert"));
export function Protocol({ task }: { task: Summary }) {
  const { t: tr, locale, errorText } = useI18n();
  const { download } = useApi();

  const read = useTaskReader(task);
  const p = useQuery({
    placeholderData: keepLocaleData(locale, [
      "task",
      task.session_id,
      locale,
      task.revision,
      "protocol",
    ]),
    queryKey: ["task", task.session_id, locale, task.revision, "protocol"],
    queryFn: () =>
      read<DTO<"ProtocolView">>(`/tasks/${task.session_id}/protocol`),
  });
  return (
    <Card
      title={tr("frontend.workspace.protocol_receipts")}
      loading={p.isLoading}
    >
      {p.error && <Alert type="error" title={errorText(p.error)} />}
      <Markdown>{p.data?.summary ?? ""}</Markdown>
      <Typography.Paragraph>{p.data?.feedback}</Typography.Paragraph>
      <Space wrap>
        <a href={download(task.session_id, "protocol")}>
          {tr("frontend.workspace.download_protocol")}
        </a>
        <a href={download(task.session_id, "operator")}>
          {tr("frontend.workspace.download_operator")}
        </a>
        {!task.external_workflow && (
          <a href={download(task.session_id, "exercise")}>
            {tr("frontend.workspace.download_exercise")}
          </a>
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
  const { t: tr, locale, errorText } = useI18n();
  const { api, download } = useApi();
  const precheckLabels: Record<string, string> = {
    channels: tr("frontend.workspace.channels_checked"),
    units: tr("frontend.workspace.units_checked"),
    logger: tr("frontend.workspace.logger_checked"),
    "stop condition": tr("frontend.workspace.stop_checked"),
    "initial condition": tr("frontend.workspace.initial_checked"),
  };

  const task = useQuery({
    placeholderData: keepLocaleData(locale, ["task", id, locale]),
    queryKey: ["task", id, locale],
    queryFn: () => api<Summary>(`/tasks/${id}`),
    refetchOnWindowFocus: true,
  });
  const recent = useQuery({
    placeholderData: keepLocaleData(locale, ["task", id, locale, "operations"]),
    queryKey: ["task", id, locale, "operations"],
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
  const [error, setError] = useState<unknown>();
  const [expert, setExpert] = useState(false);
  const { credentials } = useSettings();
  const operation = useOperation(id);
  const t = task.data;
  if (!t)
    return task.error ? (
      <Alert
        type="error"
        title={errorText(task.error)}
        action={
          <Button onClick={() => void task.refetch()}>
            {tr("frontend.workspace.retry")}
          </Button>
        }
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
            {tr("frontend.workspace.identity", {
              id: id.slice(0, 12),
              revision: t.revision,
            })}
          </Typography.Text>
          <Typography.Title level={2}>{t.workspace.title}</Typography.Title>
        </div>
        <Space wrap>
          <Tag>{statusLabel(t.status, tr)}</Tag>
          <Button
            onClick={() => void Promise.all([task.refetch(), recent.refetch()])}
          >
            {tr("frontend.workspace.refresh")}
          </Button>
          <Button onClick={() => setExpert(true)}>
            {tr("frontend.expert.title")}
          </Button>
        </Space>
      </div>
      <Steps
        current={t.workspace.stage}
        items={[
          tr("frontend.workspace.define_task"),
          tr("frontend.workspace.get_evidence"),
          tr("frontend.workspace.build_solution"),
          tr("frontend.workspace.evaluate_confirm"),
        ].map((title) => ({ title }))}
      />
      <div className="workspace-grid">
        <main>
          <Card
            id="current-action"
            title={tr("frontend.workspace.current_step")}
          >
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
            {t.read_only && (
              <Alert title={tr("frontend.workspace.read_only")} />
            )}
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
                      {tr("frontend.workspace.confirm_boundaries")}
                    </Checkbox>
                  )}
                  {action === "record_operator_report" && (
                    <>
                      <Typography.Paragraph>
                        {tr("frontend.workspace.operator_purpose")}
                      </Typography.Paragraph>
                      <a href={download(id, "operator")}>
                        {tr("frontend.workspace.download_acquisition")}
                      </a>
                      <Typography.Paragraph>
                        {tr("frontend.workspace.operator_help")}
                      </Typography.Paragraph>
                      <Radio.Group
                        value={decision}
                        onChange={(e) => setDecision(e.target.value)}
                        options={[
                          {
                            label: tr("frontend.workspace.accepted"),
                            value: "accepted",
                          },
                          {
                            label: tr("frontend.workspace.clarification"),
                            value: "needs_clarification",
                          },
                          {
                            label: tr("frontend.workspace.refused"),
                            value: "refused",
                          },
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
                        aria-label={tr("frontend.workspace.operator_note")}
                        value={note}
                        onChange={(e) => setNote(e.target.value)}
                        placeholder={tr(
                          "frontend.workspace.operator_note_placeholder",
                        )}
                      />
                    </>
                  )}
                  {action === "ingest_upload" && (
                    <>
                      <Typography.Text strong>
                        {tr("frontend.workspace.download_step")}
                      </Typography.Text>
                      <a href={download(id, "operator")}>
                        {tr("frontend.workspace.download_acquisition")}
                      </a>
                      <Typography.Paragraph>
                        {tr("frontend.workspace.acquisition_purpose")}
                      </Typography.Paragraph>
                      <Typography.Text strong>
                        {tr("frontend.workspace.run_step")}
                      </Typography.Text>
                      <Typography.Paragraph>
                        {tr("frontend.workspace.run_help")}
                      </Typography.Paragraph>
                      <Typography.Text strong>
                        {tr("frontend.workspace.upload_step")}
                      </Typography.Text>
                      <Typography.Paragraph>
                        {tr("frontend.workspace.upload_help")}
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
                            .catch((e) => setError(e))
                            .finally(() => setUploading(false));
                          return false;
                        }}
                      >
                        <Button loading={uploading}>
                          {tr("frontend.workspace.choose_data")}
                        </Button>
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
                            {tr("frontend.externalworkflow.remove")}
                          </Button>
                        </Space>
                      ))}
                      <Typography.Paragraph>
                        {tr("frontend.workspace.after_upload")}
                      </Typography.Paragraph>
                      <Checkbox
                        checked={stopped}
                        onChange={(e) => setStopped(e.target.checked)}
                      >
                        {tr("frontend.workspace.stopped")}
                      </Checkbox>
                    </>
                  )}
                  {modes.includes("natural_language") && (
                    <>
                      {" "}
                      <Input.TextArea
                        aria-label={tr("frontend.workspace.reply")}
                        rows={7}
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                        placeholder={String(
                          t.input_contract.guidance ??
                            tr("frontend.workspace.reply_placeholder"),
                        )}
                      />
                      <Button
                        onClick={() =>
                          setText((previous) =>
                            tr("frontend.workspace.unknown_reply", {
                              previous: previous,
                              newline: previous ? "\n" : "",
                            }),
                          )
                        }
                      >
                        {tr("frontend.workspace.unknown")}
                      </Button>
                    </>
                  )}{" "}
                  {modes.length > 0 &&
                  !modes.includes("natural_language") &&
                  !["record_operator_report", "ingest_upload"].includes(
                    action,
                  ) ? (
                    <Button type="primary" onClick={() => setExpert(true)}>
                      {tr("frontend.workspace.expert_submit")}
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
                      {tr("frontend.workspace.bounded_help")}
                    </Typography.Text>
                  )}
                </Space>
              )}
            {!guidedExternal && !external?.recovery_required && externalView}
            {!!error && <Alert type="error" title={errorText(error)} />}{" "}
            {operation.view}
            {activeRecent && !operation.op && (
              <Alert
                title={tr("frontend.workspace.active_operation")}
                description={tr("frontend.workspace.active_operation_help")}
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
                    {tr("frontend.workspace.restore_tracking")}
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
                  label: tr("frontend.workspace.protocol_receipts"),
                  children: <Protocol task={t} />,
                },
              ]}
            />
          )}
          {t.workspace.result_visible && <Results task={t} />}
        </main>
        <aside>
          <Card title={tr("frontend.workspace.task_agreement")}>
            <Markdown>{t.workspace.task_summary}</Markdown>
            <TaskBounds task={t.task} />
            <Typography.Text type="secondary">
              {tr("frontend.workspace.rag_snapshot_prefix")}
              {t.rag_snapshot ?? tr("frontend.workspace.unbound")}
            </Typography.Text>
          </Card>
          <Card title={tr("frontend.workspace.task_records")}>
            <Space orientation="vertical">
              <a href={download(id, "bundle")}>
                {tr("frontend.workspace.export_bundle")}
              </a>
              <a href={download(id, "report")}>
                {tr("frontend.workspace.download_report")}
              </a>
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
                {tr("frontend.workspace.cancel_task")}
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
