import { useI18n } from "./i18n";
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
import { useApi } from "./api/client";
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
  const { t: tr, errorText } = useI18n();
  const { api, download } = useApi();
  const candidateStatuses: Record<string, string> = {
    pending: tr("frontend.externalworkflow.candidate_pending"),
    qualification_failed: tr(
      "frontend.externalworkflow.candidate_qualification_failed",
    ),
    hard_failure: tr("frontend.externalworkflow.candidate_hard_failure"),
    performance_met: tr("frontend.externalworkflow.candidate_performance_met"),
    performance_not_met: tr(
      "frontend.externalworkflow.candidate_performance_not_met",
    ),
  };

  const [source, setSource] = useState<string>();
  const [confirmed, setConfirmed] = useState(false);
  const [files, setFiles] = useState<DTO<"UploadResponse">[]>([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<unknown>();
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
          {tr("frontend.externalworkflow.source_prefix")}
          {sourceKind === "software"
            ? tr("frontend.externalworkflow.software")
            : tr("frontend.externalworkflow.measured")}
          {tr("frontend.externalworkflow.offline_only")}
        </Typography.Paragraph>
      )}
      {workflow.recovery_required === true && (
        <Alert
          type="warning"
          title={tr("frontend.externalworkflow.recovery_title")}
          description={String(
            workflow.recovery_reason ??
              tr("frontend.externalworkflow.recovery_help"),
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
              label: tr("frontend.externalworkflow.stage"),
              children:
                (
                  {
                    acquisition: tr("frontend.externalworkflow.acquisition"),
                    development: tr("frontend.expert.development"),
                    tuning_probe: tr("frontend.externalworkflow.tuning_probe"),
                    confirmation: tr("frontend.expert.confirmation"),
                    fresh_confirmation: tr("frontend.expert.confirmation"),
                  } as Record<string, string>
                )[String(stage)] ??
                String(
                  stage ?? tr("frontend.externalworkflow.pending_preparation"),
                ),
            },
            {
              key: "candidate",
              label: tr("frontend.externalworkflow.candidate_controller"),
              children: String(
                run.candidate_id ??
                  tr("frontend.externalworkflow.pending_generation"),
              ),
            },
            {
              key: "request",
              label: tr("frontend.externalworkflow.run_id"),
              children: String(
                run.request_id ??
                  run.run_id ??
                  tr("frontend.externalworkflow.pending_generation"),
              ),
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
            {tr("frontend.externalworkflow.candidate_budget_prefix")}
            {String(tuning.attempts_used ?? 0)} /{" "}
            {String(tuning.max_attempts ?? "—")}
            {tr("frontend.externalworkflow.feedback_budget_prefix")}
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
            {
              title: tr("frontend.externalworkflow.candidate"),
              dataIndex: "candidate_id",
            },
            {
              title: tr("frontend.externalworkflow.status"),
              dataIndex: "status",
              render: (status: string) => candidateStatuses[status] ?? status,
            },
            {
              title: tr("frontend.externalworkflow.result_reason"),
              render: (_, row) =>
                String(row.reason ?? row.failure_reason ?? ""),
            },
          ]}
        />
      )}
      {action === "select_external_source" && (
        <>
          <Radio.Group
            aria-label={tr("frontend.externalworkflow.source")}
            value={source}
            onChange={(event) => setSource(event.target.value)}
            options={[
              {
                label: tr("frontend.externalworkflow.software"),
                value: "software",
              },
              {
                label: tr("frontend.externalworkflow.measured"),
                value: "measured",
              },
            ]}
          />
          <Typography.Paragraph>
            {tr("frontend.externalworkflow.source_help")}
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
            {tr("frontend.externalworkflow.confirm_source")}
          </Button>
        </>
      )}
      {action === "freeze" && (
        <>
          <Alert
            title={tr("frontend.externalworkflow.freeze_title")}
            description={tr("frontend.externalworkflow.freeze_help")}
          />
          <Checkbox
            checked={confirmed}
            onChange={(event) => setConfirmed(event.target.checked)}
          >
            {tr("frontend.externalworkflow.freeze_confirm")}
          </Checkbox>
          <Button
            type="primary"
            loading={busy}
            disabled={!confirmed}
            onClick={() => onSubmit(action, { confirmed: true })}
          >
            {tr("frontend.externalworkflow.freeze_submit")}
          </Button>
        </>
      )}
      {action === "prepare_external_run" && (
        <Button
          type="primary"
          loading={busy}
          onClick={() => onSubmit(action, {})}
        >
          {tr("frontend.externalworkflow.prepare_run")}
        </Button>
      )}
      {action === "submit_external_results" &&
        workflow.resume_pending === true && (
          <>
            <Alert
              title={tr("frontend.externalworkflow.resume_title")}
              description={tr("frontend.externalworkflow.resume_help")}
            />
            <Button
              type="primary"
              loading={busy}
              onClick={() => onSubmit(action, {})}
            >
              {tr("frontend.externalworkflow.resume")}
            </Button>
          </>
        )}
      {action === "submit_external_results" &&
        workflow.resume_pending !== true && (
          <>
            <Typography.Text strong>
              {tr("frontend.externalworkflow.download_step")}
            </Typography.Text>
            <a href={download(sessionId, "external_run")}>
              {tr("frontend.externalworkflow.download_run")}
            </a>
            <Typography.Paragraph>
              {tr("frontend.externalworkflow.download_help")}
            </Typography.Paragraph>
            {["confirmation", "fresh_confirmation"].includes(String(stage)) && (
              <Alert
                title={tr("frontend.externalworkflow.fresh_title")}
                description={tr("frontend.externalworkflow.fresh_help")}
              />
            )}
            <ManualRequirements value={requirements} />
            <Typography.Text strong>
              {tr("frontend.externalworkflow.run_step")}
            </Typography.Text>
            <Typography.Paragraph>
              {tr("frontend.externalworkflow.run_help")}
            </Typography.Paragraph>
            <Typography.Text strong>
              {tr("frontend.externalworkflow.upload_step")}
            </Typography.Text>
            <Typography.Paragraph>
              {tr("frontend.externalworkflow.upload_help")}
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
                  .catch((value) => setError(value))
                  .finally(() => setUploading(false));
                return false;
              }}
            >
              <Button loading={uploading} disabled={busy}>
                {tr("frontend.externalworkflow.choose_results")}
              </Button>
            </Upload>
            {files.map((file) => (
              <Space key={file.file_id}>
                {file.filename}
                <Button onClick={() => setFiles([])}>
                  {tr("frontend.externalworkflow.remove")}
                </Button>
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
              {tr("frontend.externalworkflow.submit_results")}
            </Button>
          </>
        )}
      {action === "start_external_tuning" && (
        <>
          <Typography.Paragraph>
            {tr("frontend.externalworkflow.tuning_summary", {
              count: proposed.max_probes ?? proposed.max_attempts ?? 6,
              improvement:
                Number(
                  proposed.minimum_relative_improvement ??
                    proposed.min_relative_improvement ??
                    0.02,
                ) * 100,
              repeats: workflow.evaluation_repeats ?? proposed.repeats ?? 20,
            })}
          </Typography.Paragraph>
          <Button
            type="primary"
            loading={busy}
            onClick={() => onSubmit(action, {})}
          >
            {tr("frontend.externalworkflow.start_tuning")}
          </Button>
        </>
      )}
      {(workflow.recovery_available === true ||
        action === "restart_external_acquisition") && (
        <>
          <Typography.Paragraph>
            {tr("frontend.externalworkflow.restart_help")}
          </Typography.Paragraph>
          <Button
            loading={busy}
            onClick={() => onSubmit("restart_external_acquisition", {})}
          >
            {tr("frontend.externalworkflow.restart")}
          </Button>
        </>
      )}
      {!!error && <Alert type="error" title={errorText(error)} />}
    </Space>
  );
}
