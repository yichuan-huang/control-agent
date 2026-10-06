import { keepLocaleData, useI18n } from "./i18n";
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
import { useApi } from "./api/client";
import { useTaskReader } from "./api/useTaskReader";
import type { NodePage, DTO, Summary } from "./api/types";
import { parseObject } from "./safety";
import { useSettings } from "./context";
import { useOperation } from "./operations";

function NodeViewer({ task }: { task: Summary }) {
  const { t: tr, locale, errorText } = useI18n();
  const { download } = useApi();
  const artifactLabels: Record<string, string> = {
    report: tr("frontend.expert.full_report"),
    task: tr("frontend.expert.task_contract"),
    diagnostic: tr("frontend.expert.diagnosis"),
    evidence: tr("frontend.expert.public_evidence"),
    route: tr("frontend.expert.route"),
    features: tr("frontend.expert.features"),
    controller: tr("frontend.expert.controller"),
    qualification: tr("frontend.expert.qualification"),
    freeze: tr("frontend.expert.freeze"),
    evaluation: tr("frontend.expert.development"),
    confirmation: tr("frontend.expert.confirmation"),
    tuning: tr("frontend.expert.tuning"),
    events: tr("frontend.expert.events"),
    agent_records: tr("frontend.expert.agent_records"),
    phase_plan: tr("frontend.expert.phase_plan"),
    protocols: tr("frontend.expert.protocol"),
    operator_handoffs: tr("frontend.expert.handoffs"),
    upload_receipts: tr("frontend.expert.receipts"),
  };

  const read = useTaskReader(task);
  const [artifact, setArtifact] = useState("report");
  const [pointer, setPointer] = useState("");
  const [offset, setOffset] = useState(0);
  const catalog = useQuery({
    placeholderData: keepLocaleData(locale, [
      "task",
      task.session_id,
      locale,
      task.revision,
      "artifacts",
    ]),
    queryKey: ["task", task.session_id, locale, task.revision, "artifacts"],
    queryFn: () =>
      read<DTO<"ArtifactCatalog">>(`/tasks/${task.session_id}/artifacts`),
  });
  const page = useQuery({
    placeholderData: keepLocaleData(locale, [
      "task",
      task.session_id,
      locale,
      task.revision,
      "node",
      artifact,
      pointer,
      offset,
    ]),
    queryKey: [
      "task",
      task.session_id,
      locale,
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
        aria-label={tr("frontend.expert.choose_artifact")}
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
          {tr("frontend.expert.parent")}
        </Button>
        <Typography.Text code>{pointer || "/"}</Typography.Text>
        <a href={download(task.session_id, "artifact", artifact)}>
          {tr("frontend.expert.download_artifact")}
        </a>
      </Space>
      {page.error && <Alert type="error" title={errorText(page.error)} />}
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
            title: tr("frontend.expert.field"),
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
          { title: tr("frontend.expert.type"), dataIndex: "kind" },
          { title: tr("frontend.expert.preview"), dataIndex: "preview" },
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
        {tr("frontend.expert.artifact_help")}
      </Typography.Text>
    </Space>
  );
}
function Timeline({ task }: { task: Summary }) {
  const { t: tr, locale, errorText } = useI18n();

  const read = useTaskReader(task);
  const [offset, setOffset] = useState(0);
  const q = useQuery({
    placeholderData: keepLocaleData(locale, [
      "task",
      task.session_id,
      locale,
      task.revision,
      "events",
      offset,
    ]),
    queryKey: [
      "task",
      task.session_id,
      locale,
      task.revision,
      "events",
      offset,
    ],
    queryFn: () =>
      read<DTO<"SectionPage">>(
        `/tasks/${task.session_id}/sections/events?offset=${offset}&limit=50`,
      ),
  });
  return (
    <>
      {q.error && <Alert type="error" title={errorText(q.error)} />}{" "}
      <Typography.Paragraph>
        {tr("frontend.expert.timeline")}
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
            title: tr("frontend.expert.index"),
            width: 70,
            render: (_, __, index) => offset + index + 1,
          },
          {
            title: tr("frontend.expert.recorded_events"),
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
  const { t: tr, errorText } = useI18n();
  const { api, download } = useApi();
  const downloadLabels: Record<string, string> = {
    bundle: tr("frontend.expert.public_bundle"),
    report: tr("frontend.expert.raw_report"),
    protocol: tr("frontend.expert.protocol"),
    controller: tr("frontend.expert.controller"),
    qualification: tr("frontend.expert.qualification"),
    freeze: tr("frontend.expert.freeze"),
    evaluation: tr("frontend.expert.development"),
    confirmation: tr("frontend.expert.confirmation"),
    exercise: tr("frontend.expert.exercise_bundle"),
    operator: tr("frontend.expert.operator_bundle"),
    features: tr("frontend.expert.features"),
    feedback: tr("frontend.expert.feedback"),
    result: tr("frontend.expert.final_result"),
    audit: tr("frontend.expert.audit_log"),
    upload_receipt: tr("frontend.expert.receipts"),
  };

  const [tab, setTab] = useState(task ? "artifacts" : "submit");
  const [text, setText] = useState("");
  const [feedback, setFeedback] = useState<unknown>();
  const [busy, setBusy] = useState(false);
  const { credentials, useRag } = useSettings();
  const taskOperation = useOperation(task?.session_id, tab !== "import");
  const importOperation = useOperation(undefined, tab === "import");
  const operation = tab === "import" ? importOperation : taskOperation;
  async function validate() {
    setBusy(true);
    try {
      await api("/artifacts/validate", { payload: parseObject(text) });
      setFeedback({ message_ref: { key: "frontend.expert.valid_artifact" } });
    } catch (e) {
      setFeedback(e);
    } finally {
      setBusy(false);
    }
  }
  return (
    <Drawer
      title={tr("frontend.expert.title")}
      open
      onClose={onClose}
      size={860}
      destroyOnHidden
    >
      <Tabs
        activeKey={tab}
        onChange={setTab}
        items={[
          ...(task
            ? [
                { key: "artifacts", label: tr("frontend.expert.browse") },
                { key: "events", label: tr("frontend.expert.timeline_tab") },
              ]
            : []),
          {
            key: "submit",
            label: task
              ? tr("frontend.expert.submit_json")
              : tr("frontend.expert.full_task_contract"),
          },
          { key: "validate", label: tr("frontend.expert.validate_tab") },
          { key: "import", label: tr("frontend.expert.import_tab") },
          ...(task
            ? [{ key: "downloads", label: tr("frontend.expert.download") }]
            : []),
        ]}
      />
      {tab === "artifacts" && task && <NodeViewer task={task} />}{" "}
      {tab === "events" && task && <Timeline task={task} />}{" "}
      {["submit", "validate"].includes(tab) && (
        <Space orientation="vertical" style={{ width: "100%" }}>
          {task && tab === "submit" && (
            <Alert
              title={tr("frontend.expert.allowed_action", {
                action: task.workspace.action_title,
              })}
              description={String(task.input_contract.guidance ?? "")}
            />
          )}
          <Input.TextArea
            aria-label={tr("frontend.expert.json_label")}
            rows={14}
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder={tr("frontend.expert.json_placeholder")}
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
              {tr("frontend.expert.load_template")}
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
                  const payload = task ? undefined : parseObject(text);
                  void operation
                    .submit(
                      task ? `/tasks/${task.session_id}/actions` : "/tasks",
                      task
                        ? {
                            expected_revision: task.revision,
                            action: task.workspace.action,
                            input: { mode: "json", text },
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
                  setFeedback(e);
                }
              }
            }}
          >
            {tab === "validate"
              ? tr("frontend.expert.validate_artifact")
              : task
                ? tr("frontend.expert.submit_action")
                : tr("frontend.expert.create_unconfirmed")}
          </Button>
        </Space>
      )}
      {tab === "import" && (
        <>
          <Typography.Paragraph>
            {tr("frontend.expert.import_help")}
          </Typography.Paragraph>
          <Upload
            accept=".zip"
            showUploadList={false}
            beforeUpload={(file) => {
              const data = new FormData();
              data.append("file", file);
              setFeedback(undefined);
              setBusy(true);
              void api<DTO<"UploadResponse">>("/uploads", data)
                .then((r) =>
                  operation
                    .submit("/imports", { file_id: r.file_id })
                    .catch(() => {}),
                )
                .catch((e) => setFeedback(e))
                .finally(() => setBusy(false));
              return false;
            }}
          >
            <Button loading={busy || operation.busy}>
              {tr("frontend.expert.select_bundle")}
            </Button>
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
      {!!feedback && (
        <Alert style={{ marginTop: 16 }} title={errorText(feedback)} />
      )}{" "}
      {operation.view}
    </Drawer>
  );
}
