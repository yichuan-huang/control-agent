import { useState } from "react";
import {
  Alert,
  Button,
  Checkbox,
  Descriptions,
  Radio,
  Space,
  Table,
  Typography,
  Upload,
} from "antd";
import { api, download } from "./api/client";
import ManualRequirements from "./ManualRequirements";
import type { DTO, Obj } from "./api/types";

export const externalActions = new Set([
  "select_external_source",
  "prepare_external_run",
  "submit_external_results",
  "start_external_tuning",
  "restart_external_acquisition",
]);
function object(value: unknown): Obj {
  return value && typeof value === "object" && !Array.isArray(value)
    ? (value as Obj)
    : {};
}
export default function ExternalWorkflow({
  sessionId,
  action,
  workflow,
  requirements,
  busy,
  onSubmit,
}: {
  sessionId: string;
  action: string;
  workflow: Obj;
  requirements?: Obj;
  busy: boolean;
  onSubmit: (action: string, input: Obj) => void;
}) {
  const [source, setSource] = useState<string>();
  const [confirmed, setConfirmed] = useState(false);
  const [files, setFiles] = useState<DTO<"UploadResponse">[]>([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const run = object(workflow.run ?? workflow.active_request);
  const tuning = object(workflow.tuning);
  const proposed = object(workflow.proposed_tuning ?? workflow.tuning);
  const sourceKind =
    workflow.source_kind ?? object(workflow.source).source_kind;
  const reasons = Array.isArray(workflow.failure_reasons)
    ? workflow.failure_reasons
    : [];
  const candidates = Array.isArray(workflow.candidates)
    ? workflow.candidates.map(object)
    : [];
  const stage = workflow.stage ?? run.stage;
  return (
    <Space orientation="vertical" style={{ width: "100%" }}>
      {!!sourceKind && (
        <Typography.Paragraph>
          数据来源：
          {sourceKind === "software" ? "外部软件仿真" : "外部实测数据"}
          。仅用于离线软件评价，任务不会操作硬件。
        </Typography.Paragraph>
      )}
      {workflow.recovery_required === true && (
        <Alert
          type="warning"
          title="当前证据需要重新采集"
          description={String(
            workflow.recovery_reason ??
              "使用下方入口创建新任务，并按新协议采集数据。原始记录保留。",
          )}
        />
      )}
      {reasons.map((reason, i) => (
        <Alert key={i} type="error" title={String(reason)} />
      ))}
      {!!(run.request_id ?? run.run_id) && (
        <Descriptions
          size="small"
          column={1}
          items={[
            {
              key: "stage",
              label: "本轮阶段",
              children:
                (
                  {
                    acquisition: "采集证据",
                    development: "开发评价",
                    tuning_probe: "调优候选评价",
                    confirmation: "独立确认",
                    fresh_confirmation: "独立确认",
                  } as Record<string, string>
                )[String(stage)] ?? String(stage ?? "待准备"),
            },
            {
              key: "candidate",
              label: "候选控制器",
              children: String(run.candidate_id ?? "待生成"),
            },
            {
              key: "request",
              label: "运行标识",
              children: String(run.request_id ?? run.run_id ?? "待生成"),
            },
          ]}
        />
      )}
      {typeof tuning.max_attempts === "number" &&
        (action === "start_external_tuning" ||
          candidates.length > 0 ||
          Number(tuning.attempts_used ?? 0) > 0 ||
          Number(tuning.feedback_rounds_used ?? 0) > 0) && (
          <Typography.Paragraph>
            候选预算：{String(tuning.attempts_used ?? 0)} /{" "}
            {String(tuning.max_attempts ?? "—")}；反馈轮次：
            {String(tuning.feedback_rounds_used ?? 0)} /{" "}
            {String(tuning.max_feedback_rounds ?? "—")}
          </Typography.Paragraph>
        )}
      {candidates.length > 0 && (
        <Table
          size="small"
          pagination={false}
          rowKey={(_, i) => String(i)}
          dataSource={candidates}
          columns={[
            { title: "候选", dataIndex: "candidate_id" },
            { title: "状态", dataIndex: "status" },
            {
              title: "结果 / 原因",
              render: (_, row) =>
                String(row.reason ?? row.failure_reason ?? ""),
            },
          ]}
        />
      )}
      {action === "select_external_source" && (
        <>
          <Radio.Group
            aria-label="外部数据来源"
            value={source}
            onChange={(event) => setSource(event.target.value)}
            options={[
              { label: "外部软件仿真", value: "software" },
              { label: "外部实测数据", value: "measured" },
            ]}
          />
          <Typography.Paragraph>
            选择本任务实际使用的数据来源；这只记录证据来源，不选择执行工具。实际试验在应用外部完成，您负责使用自己的仿真环境或实验设施执行，随后回到此页上传数据。每份运行记录必须保留来源与协议标识。
          </Typography.Paragraph>
          <Button
            type="primary"
            loading={busy}
            disabled={!source}
            onClick={() =>
              onSubmit(action, {
                payload: {
                  source_kind: source,
                },
              })
            }
          >
            确认数据来源
          </Button>
        </>
      )}
      {action === "freeze" && (
        <>
          <Alert
            title="冻结后按同一约定评价"
            description="核对任务侧栏中的参考目标、区域、采样间隔、时长、重复次数、性能要求，以及条件适用的阶段切换和扰动设置。"
          />
          <Checkbox
            checked={confirmed}
            onChange={(event) => setConfirmed(event.target.checked)}
          >
            我已核对冻结约定，确认进入开发评价
          </Checkbox>
          <Button
            type="primary"
            loading={busy}
            disabled={!confirmed}
            onClick={() => onSubmit(action, { confirmed: true })}
          >
            确认并冻结评价约定
          </Button>
        </>
      )}
      {action === "prepare_external_run" && (
        <Button
          type="primary"
          loading={busy}
          onClick={() => onSubmit(action, {})}
        >
          准备本轮外部运行包
        </Button>
      )}
      {action === "submit_external_results" &&
        workflow.resume_pending === true && (
          <>
            <Alert
              title="结果已接收，处理尚未完成"
              description="继续处理已保存的结果；无需再次上传轨迹。"
            />
            <Button
              type="primary"
              loading={busy}
              onClick={() => onSubmit(action, {})}
            >
              完成已接收结果处理
            </Button>
          </>
        )}
      {action === "submit_external_results" &&
        workflow.resume_pending !== true && (
          <>
            <Typography.Text strong>步骤 1 · 下载运行请求</Typography.Text>
            <a href={download(sessionId, "external_run")}>
              下载本轮完整运行包 ZIP
            </a>
            <Typography.Paragraph>
              请求包不含已完成的试验结果。由您在外部环境按照清单运行每条轨迹，填写模板中的完整时间序列、输入输出、运行标识与停止记录。下载文件不会推进任务。
            </Typography.Paragraph>
            {["confirmation", "fresh_confirmation"].includes(String(stage)) && (
              <Alert
                title="独立确认需要全新轨迹"
                description="使用本轮确认包重新运行，不能复用开发评价或调优的数据。"
              />
            )}
            <ManualRequirements value={requirements} />
            <Typography.Text strong>
              步骤 2 · 在外部执行并打包结果
            </Typography.Text>
            <Typography.Paragraph>
              由您使用自己的运行环境，按照本轮清单应用候选控制器、输入和停止条件，逐次保存完整记录。将填写完成的试次
              JSON 与原始 manifest.json 放在结果 ZIP
              根目录；不要直接回传请求包，也不要仅提交汇总指标。文件中的列和单位按本轮请求保持一致。实际试验在应用外部完成；本页只管理请求、数据和评价，不执行您的环境。
            </Typography.Paragraph>
            <Typography.Text strong>
              步骤 3 · 回到此页上传结果并校验
            </Typography.Text>
            <Typography.Paragraph>
              下一步：系统核对整包文件及协议绑定、计算评价结果并记录拒绝原因。评价
              ZIP 中任何试次未通过，整包均不接收；按回执修正并重新上传完整结果
              ZIP。通过后按当前阶段进入调优、全新独立确认或最终报告；无需提交特征或控制器
              JSON。
            </Typography.Paragraph>
            <Upload
              accept=".zip"
              showUploadList={false}
              beforeUpload={(file) => {
                const body = new FormData();
                body.append("file", file);
                body.append("session_id", sessionId);
                setUploading(true);
                setError("");
                void api<DTO<"UploadResponse">>("/uploads", body)
                  .then((value) => setFiles([value]))
                  .catch((value) => setError(String(value)))
                  .finally(() => setUploading(false));
                return false;
              }}
            >
              <Button loading={uploading} disabled={busy}>
                选择完整结果 ZIP
              </Button>
            </Upload>
            {files.map((file) => (
              <Space key={file.file_id}>
                {file.filename}
                <Button onClick={() => setFiles([])}>移除</Button>
              </Space>
            ))}
            <Button
              type="primary"
              loading={busy}
              disabled={!files.length || uploading}
              onClick={() =>
                onSubmit(action, {
                  file_ids: files.map((file) => file.file_id),
                })
              }
            >
              校验并提交本轮轨迹
            </Button>
          </>
        )}
      {action === "start_external_tuning" && (
        <>
          <Typography.Paragraph>
            最多 {String(proposed.max_probes ?? proposed.max_attempts ?? 6)}{" "}
            个候选；相对改进至少{" "}
            {Number(
              proposed.minimum_relative_improvement ??
                proposed.min_relative_improvement ??
                0.02,
            ) * 100}
            %。开发评价与独立确认按冻结约定重复{" "}
            {String(workflow.evaluation_repeats ?? proposed.repeats ?? 20)}{" "}
            次。每个候选使用独立运行包，独立确认需要全新轨迹。系统记录性能、失败原因与剩余预算，再决定下一步。
          </Typography.Paragraph>
          <Button
            type="primary"
            loading={busy}
            onClick={() => onSubmit(action, {})}
          >
            开始有界外部调优
          </Button>
        </>
      )}
      {(workflow.recovery_available === true ||
        action === "restart_external_acquisition") && (
        <>
          <Typography.Paragraph>
            重新采集会创建新任务。当前任务及其证据、失败原因和审计记录保留。
          </Typography.Paragraph>
          <Button
            loading={busy}
            onClick={() => onSubmit("restart_external_acquisition", {})}
          >
            重新采集并创建新任务
          </Button>
        </>
      )}
      {error && <Alert type="error" title={error} />}
    </Space>
  );
}
