import { keepLocaleData, useI18n } from "./i18n";
import { useEffect, useRef, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  Alert,
  Button,
  Card,
  Checkbox,
  Collapse,
  ConfigProvider,
  Form,
  Input,
  InputNumber,
  Select,
  Space,
  Steps,
  Typography,
} from "antd";
import { useApi, ApiError } from "./api/client";
import type { Obj, CaseDetail, DTO } from "./api/types";
import { readDraft, saveDraft } from "./safety";
import { useSettings } from "./context";
import { useOperation } from "./operations";
import Markdown from "./Markdown";
import { DraftReview } from "./ReviewDetails";
export default function Wizard() {
  const { t: tr, locale, message, errorText } = useI18n();
  const { api } = useApi();
  const requirements: Record<string, string> = {
    final_abs_error_max: tr("frontend.wizard.allowed_error"),
    overshoot_max: tr("frontend.wizard.allowed_overshoot"),
    settling_time_max_s: tr("frontend.wizard.desired_settling"),
    hold_duration_min_s: tr("frontend.wizard.desired_hold"),
    perturbed_success_rate_min: tr("frontend.reviewdetails.success_rate"),
  };
  const budgets: Record<string, string> = {
    distinct_experiments: tr("frontend.wizard.experiment_budget"),
    cumulative_excitation_time_s: tr("frontend.reviewdetails.excitation_time"),
  };

  const [params] = useSearchParams();
  const caseId = params.get("case") ?? "";
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const navigationKey = caseId
    ? `cfdc:wizard:case:${caseId}`
    : "cfdc:wizard:custom";
  const [draftRejection, setDraftRejection] = useState(() => {
    let reason = "";
    if (!caseId)
      readDraft((message) => {
        reason = message;
      });
    return reason;
  });
  const [restored] = useState(() => {
    if (draftRejection) return { step: 0, evidence: "automatic" };
    try {
      const value = JSON.parse(sessionStorage.getItem(navigationKey) ?? "{}");
      return {
        step:
          Number.isInteger(value.step) && value.step >= 0 && value.step <= 3
            ? value.step
            : 0,
        evidence:
          value.evidence === "exercise_bundle"
            ? "exercise_bundle"
            : "automatic",
      };
    } catch {
      return { step: 0, evidence: "automatic" };
    }
  });
  const [step, setStep] = useState(caseId ? 3 : restored.step);
  const [advanced, setAdvanced] = useState(false);
  const [validatedTask, setValidatedTask] = useState<Obj>();
  const [review, setReview] = useState<{
    summary: string;
    locale: string;
    draft: Obj;
  }>();
  const [error, setError] = useState<unknown>();
  const [validating, setValidating] = useState(false);
  const [confirmed, setConfirmed] = useState(false);
  const [evidence, setEvidence] = useState(restored.evidence);
  const { credentials, useRag } = useSettings();
  const operation = useOperation();
  const source = useQuery({
    placeholderData: keepLocaleData(locale, ["draft", locale, caseId]),
    queryKey: ["draft", locale, caseId],
    queryFn: () =>
      caseId
        ? api<CaseDetail>(`/cases/${caseId}`)
        : api<DTO<"DraftResponse">>("/drafts/default"),
  });
  const initializedDraft = useRef(false);
  useEffect(() => {
    if (source.data && !initializedDraft.current) {
      initializedDraft.current = true;
      form.setFieldsValue(
        caseId
          ? source.data.draft
          : {
              transition_deadline_s: 10,
              handoff_count_min: 1,
              recovery_deadline_s: 10,
              evaluation_dt_s: 0.02,
              evaluation_horizon_s: 20,
              evaluation_repeats: 20,
              ...source.data.draft,
              ...(readDraft() ?? {}),
              external_data_enabled: true,
              reference_enabled: true,
              initial_output_value_enabled: true,
              success_requirement_fields: Array.from(
                new Set([
                  "final_abs_error_max",
                  ...((readDraft()?.success_requirement_fields ??
                    source.data.draft.success_requirement_fields ??
                    []) as string[]),
                ]),
              ),
            },
      );
    }
  }, [source.data, caseId, form]);
  useEffect(() => {
    sessionStorage.setItem(navigationKey, JSON.stringify({ step, evidence }));
  }, [navigationKey, step, evidence]);
  const resumedReview = useQuery({
    placeholderData: keepLocaleData(locale, [
      "draft-review-resume",
      locale,
      navigationKey,
    ]),
    queryKey: ["draft-review-resume", locale, navigationKey],
    enabled: !caseId && restored.step === 3 && !!source.data,
    retry: false,
    queryFn: () =>
      api<DTO<"DraftValidationResponse">>("/drafts/validate", {
        draft: {
          ...source.data!.draft,
          ...(readDraft() ?? {}),
          external_data_enabled: true,
          reference_enabled: true,
        },
        case_id: "",
      }),
  });
  const taskType = Form.useWatch("task_type", form);
  const values = Form.useWatch([], form) ?? {};
  const translatedReview = useQuery({
    queryKey: ["draft-review", locale, review?.draft],
    enabled: !!review && locale !== review.locale,
    retry: false,
    queryFn: () =>
      api<DTO<"DraftValidationResponse">>("/drafts/validate", {
        draft: review!.draft,
        case_id: caseId,
      }),
  });
  useEffect(() => {
    if (!(error instanceof ApiError) || !error.detail.fields) return;
    form.setFields(
      Object.entries(error.detail.fields)
        .filter(([name]) => form.getFieldError(name).length > 0)
        .map(([name, fallback]) => ({
          name,
          errors: [message(error.detail.field_message_refs?.[name], fallback)],
        })),
    );
  }, [error, form, message]);
  async function validate() {
    setValidating(true);
    setError("");
    try {
      const draft = form.getFieldsValue(true);
      const r = await api<DTO<"DraftValidationResponse">>("/drafts/validate", {
        draft,
        case_id: caseId,
      });
      setReview({ summary: r.summary, locale, draft });
      setValidatedTask(r.task);
      setStep(3);
    } catch (e) {
      if (e instanceof ApiError && e.detail.fields) {
        form.setFields(
          Object.entries(e.detail.fields).map(([name, fallback]) => ({
            name,
            errors: [message(e.detail.field_message_refs?.[name], fallback)],
          })),
        );
        const field = Object.keys(e.detail.fields)[0];
        if (field in requirements || field in budgets) setAdvanced(true);
        setStep(
          [
            "description",
            "task_type",
            "initial_region",
            "goal_region",
            "disturbance_event",
            "recovery_start_condition",
            "disturbance_hold_region",
            "initial_output_value",
            "intermediate_targets",
            "transition_deadline_s",
            "handoff_count_min",
            "disturbance_channel",
            "disturbance_start_s",
            "disturbance_amplitude",
            "disturbance_duration_s",
            "recovery_deadline_s",
          ].includes(field)
            ? 0
            : ["outputs", "inputs", "input_unit"].includes(field)
              ? 1
              : 2,
        );
        setTimeout(
          () =>
            form.scrollToField(
              field === "outputs" || field === "inputs" ? [field, 0, 0] : field,
              { focus: true },
            ),
          50,
        );
      }
      setError(e);
    } finally {
      setValidating(false);
    }
  }
  const text = (key: string, label: string) => (
    <Form.Item name={key} label={label}>
      <Input />
    </Form.Item>
  );
  const num = (key: string, label: string) => (
    <Form.Item name={key} label={label}>
      <InputNumber style={{ width: "100%" }} />
    </Form.Item>
  );
  const optional = (key: string, label: string, children: React.ReactNode) => (
    <>
      <Form.Item name={key} valuePropName="checked">
        <Checkbox>{label}</Checkbox>
      </Form.Item>
      {values[key] && children}
    </>
  );
  return (
    <div className="narrow">
      <Typography.Title level={2}>
        {caseId
          ? tr("frontend.wizard.review_case")
          : tr("frontend.wizard.define_task")}
      </Typography.Title>
      <Steps
        current={step}
        items={[
          tr("frontend.wizard.goal"),
          tr("frontend.wizard.signals"),
          tr("frontend.wizard.boundaries"),
          tr("frontend.wizard.review"),
        ].map((title) => ({
          title,
        }))}
      />
      {source.error && (
        <Alert
          type="error"
          title={errorText(source.error)}
          action={
            <Button onClick={() => void source.refetch()}>
              {tr("frontend.wizard.reload")}
            </Button>
          }
        />
      )}
      {draftRejection && (
        <Alert type="warning" title={tr("frontend.safety.legacy_draft")} />
      )}
      {!!error && <Alert type="error" title={errorText(error)} />}
      {resumedReview.error && (
        <Alert type="error" title={tr("frontend.wizard.restored_review")} />
      )}{" "}
      {caseId && (
        <Alert
          title={tr("frontend.wizard.case_locked")}
          description={tr("frontend.wizard.case_locked_help")}
          action={
            <Button
              onClick={() => {
                saveDraft(source.data?.draft ?? {});
                sessionStorage.setItem(
                  "cfdc:wizard:custom",
                  JSON.stringify({ step: 0, evidence: "automatic" }),
                );
                navigate("/new");
                setStep(0);
              }}
            >
              {tr("frontend.wizard.copy_case")}
            </Button>
          }
        />
      )}
      <Form
        form={form}
        layout="vertical"
        disabled={source.isLoading || !!caseId || operation.busy}
        onValuesChange={() => {
          if (!caseId) {
            saveDraft(form.getFieldsValue(true));
            setDraftRejection("");
          }
          setConfirmed(false);
        }}
        preserve
      >
        <div hidden={step !== 0}>
          {!caseId && (
            <Alert
              title={tr("frontend.wizard.custom_title")}
              description={tr("frontend.wizard.custom_help")}
            />
          )}
          <Form.Item
            name="description"
            label={tr("frontend.wizard.description")}
          >
            <Input.TextArea
              rows={4}
              placeholder={tr("frontend.wizard.description_placeholder")}
            />
          </Form.Item>
          <Form.Item
            name="task_type"
            label={tr("frontend.reviewdetails.task_type")}
          >
            <Select
              options={[
                {
                  label: tr("frontend.reviewdetails.hold"),
                  value: "local_setpoint_hold",
                },
                {
                  label: tr("frontend.reviewdetails.transition"),
                  value: "transition_then_hold",
                },
                {
                  label: tr("frontend.reviewdetails.recovery"),
                  value: "disturbance_recovery_to_hold",
                },
              ]}
            />
          </Form.Item>
          {taskType === "transition_then_hold" && (
            <>
              {text(
                "initial_region",
                tr("frontend.reviewdetails.initial_region"),
              )}
              {text("goal_region", tr("frontend.reviewdetails.goal_region"))}
              {caseId
                ? optional(
                    "initial_output_value_enabled",
                    tr("frontend.wizard.enable_initial_output"),
                    num(
                      "initial_output_value",
                      tr("frontend.wizard.initial_output_value"),
                    ),
                  )
                : num(
                    "initial_output_value",
                    tr("frontend.wizard.initial_output_value"),
                  )}
              {text(
                "intermediate_targets",
                tr("frontend.wizard.intermediate_targets"),
              )}
              {!caseId && (
                <>
                  {num(
                    "transition_deadline_s",
                    tr("frontend.reviewdetails.transition_deadline"),
                  )}
                  {num(
                    "handoff_count_min",
                    tr("frontend.reviewdetails.verified_transitions"),
                  )}
                </>
              )}
            </>
          )}
          {taskType === "disturbance_recovery_to_hold" && (
            <>
              {text(
                "disturbance_event",
                tr("frontend.reviewdetails.disturbance_event"),
              )}
              {text(
                "recovery_start_condition",
                tr("frontend.reviewdetails.recovery_start"),
              )}
              {text(
                "disturbance_hold_region",
                tr("frontend.reviewdetails.recovery_region"),
              )}
              {!caseId && (
                <>
                  {text(
                    "disturbance_channel",
                    tr("frontend.wizard.disturbance_channel"),
                  )}
                  {num(
                    "disturbance_start_s",
                    tr("frontend.wizard.disturbance_start"),
                  )}
                  {num(
                    "disturbance_amplitude",
                    tr("frontend.wizard.disturbance_amplitude"),
                  )}
                  {num(
                    "disturbance_duration_s",
                    tr("frontend.wizard.disturbance_duration"),
                  )}
                  {num(
                    "recovery_deadline_s",
                    tr("frontend.wizard.recovery_deadline"),
                  )}
                </>
              )}
            </>
          )}
        </div>
        <div hidden={step !== 1}>
          <Typography.Title level={4}>
            {tr("frontend.reviewdetails.outputs")}
          </Typography.Title>
          <Form.List name="outputs">
            {(fields, { add, remove }) => (
              <>
                {fields.map((field) => (
                  <Space key={field.key} align="start" className="signal-row">
                    <Form.Item
                      name={[field.name, 0]}
                      label={tr("frontend.wizard.output_name", {
                        number: field.name + 1,
                      })}
                    >
                      <Input />
                    </Form.Item>
                    <Form.Item
                      name={[field.name, 1]}
                      label={tr("frontend.wizard.unit")}
                    >
                      <Input />
                    </Form.Item>
                    <Button
                      aria-label={tr("frontend.wizard.delete_output", {
                        number: field.name + 1,
                      })}
                      onClick={() => remove(field.name)}
                    >
                      {tr("frontend.wizard.delete")}
                    </Button>
                  </Space>
                ))}
                <Button onClick={() => add(["", ""])}>
                  {tr("frontend.wizard.add_output")}
                </Button>
              </>
            )}
          </Form.List>
          <Form.ErrorList errors={form.getFieldError("outputs")} />
          <Typography.Title level={4}>
            {tr("frontend.charts.control_input")}
          </Typography.Title>
          <Form.List name="inputs">
            {(fields, { add, remove }) => (
              <>
                {fields.map((field) => (
                  <Space key={field.key} align="start">
                    <Form.Item
                      name={[field.name, 0]}
                      label={tr("frontend.wizard.input_name", {
                        number: field.name + 1,
                      })}
                    >
                      <Input />
                    </Form.Item>
                    <Button onClick={() => remove(field.name)}>
                      {tr("frontend.wizard.delete")}
                    </Button>
                  </Space>
                ))}
                <Button onClick={() => add([""])}>
                  {tr("frontend.wizard.add_input")}
                </Button>
              </>
            )}
          </Form.List>
          <Form.ErrorList errors={form.getFieldError("inputs")} />
          {text("input_unit", tr("frontend.reviewdetails.input_unit"))}
        </div>
        <div hidden={step !== 2}>
          <div className="field-grid">
            {num("input_min", tr("frontend.wizard.input_min"))}
            {num("input_max", tr("frontend.wizard.input_max"))}
            {num("state_stop", tr("frontend.reviewdetails.stop_threshold"))}
          </div>
          <Typography.Paragraph type="secondary">
            {tr("frontend.reviewdetails.stop_explanation")}{" "}
            {tr("frontend.wizard.input_bounds_help")}
          </Typography.Paragraph>
          {caseId ? (
            optional(
              "reference_enabled",
              tr("frontend.wizard.enable_reference"),
              num("reference", tr("frontend.reviewdetails.reference")),
            )
          ) : (
            <>
              <Form.Item name="external_data_enabled" hidden>
                <Input />
              </Form.Item>
              <Form.Item name="reference_enabled" hidden>
                <Input />
              </Form.Item>
              {num("reference", tr("frontend.reviewdetails.reference"))}
              {text("region_label", tr("frontend.wizard.region"))}
              <Typography.Title level={4}>
                {tr("frontend.wizard.frozen_evaluation")}
              </Typography.Title>
              <Typography.Paragraph>
                {tr("frontend.wizard.evaluation_help")}
              </Typography.Paragraph>
              <div className="field-grid">
                {num(
                  "evaluation_dt_s",
                  tr("frontend.reviewdetails.sample_time"),
                )}
                {num(
                  "evaluation_horizon_s",
                  tr("frontend.reviewdetails.run_duration"),
                )}
                {num(
                  "evaluation_repeats",
                  tr("frontend.reviewdetails.repeats"),
                )}
              </div>
              {num("final_abs_error_max", tr("frontend.wizard.allowed_error"))}
            </>
          )}
          {optional(
            "output_bounds_enabled",
            tr("frontend.wizard.enable_output_bounds"),
            <div className="field-grid">
              {num("output_min", tr("frontend.wizard.output_min"))}
              {num("output_max", tr("frontend.wizard.output_max"))}
            </div>,
          )}
          <ConfigProvider theme={{ token: { motion: false } }}>
            <Collapse
              activeKey={advanced ? ["optional"] : []}
              onChange={(keys) => setAdvanced(keys.length > 0)}
              items={[
                {
                  key: "optional",
                  label: tr("frontend.wizard.optional_requirements"),
                  forceRender: true,
                  children: (
                    <>
                      <Form.Item
                        name="success_requirement_fields"
                        label={tr("frontend.wizard.explicit_requirements")}
                      >
                        <Checkbox.Group
                          options={Object.entries(requirements).map(
                            ([value, label]) => ({
                              value,
                              label,
                              disabled:
                                !caseId && value === "final_abs_error_max",
                            }),
                          )}
                        />
                      </Form.Item>
                      {((values.success_requirement_fields ?? []) as string[])
                        .filter(
                          (key) => caseId || key !== "final_abs_error_max",
                        )
                        .map((key) => (
                          <div key={key}>{num(key, requirements[key])}</div>
                        ))}
                      {optional(
                        "response_time_preference_enabled",
                        tr("frontend.wizard.enable_response_preference"),
                        num(
                          "response_time_preference_s",
                          tr("frontend.reviewdetails.response_preference"),
                        ),
                      )}
                      <Form.Item
                        name="budget_fields"
                        label={tr("frontend.wizard.budget")}
                      >
                        <Checkbox.Group
                          options={Object.entries(budgets).map(
                            ([value, label]) => ({
                              value,
                              label,
                            }),
                          )}
                        />
                      </Form.Item>
                      {((values.budget_fields ?? []) as string[]).map((key) => (
                        <div key={key}>{num(key, budgets[key])}</div>
                      ))}
                    </>
                  ),
                },
              ]}
            />
          </ConfigProvider>
        </div>
      </Form>
      {step === 3 && (
        <Card title={tr("frontend.wizard.task_review")}>
          <Markdown>
            {(locale !== review?.locale
              ? translatedReview.data?.summary
              : undefined) ||
              review?.summary ||
              resumedReview.data?.summary ||
              String(
                source.data && "description" in source.data
                  ? source.data.description
                  : (form.getFieldValue("description") ?? ""),
              )}
          </Markdown>
          {caseId && (
            <>
              <Typography.Paragraph>
                {String((source.data as CaseDetail)?.scope ?? "")}
              </Typography.Paragraph>
              <Typography.Paragraph>
                {tr("frontend.externalworkflow.source_prefix")}
                {String((source.data as CaseDetail)?.data_source ?? "")}
              </Typography.Paragraph>
              <Select
                aria-label={tr("frontend.wizard.evidence_mode")}
                value={evidence}
                onChange={setEvidence}
                options={[
                  {
                    value: "automatic",
                    label: tr("frontend.wizard.automatic_evidence"),
                  },
                  {
                    value: "exercise_bundle",
                    label: tr("frontend.wizard.exercise_upload"),
                  },
                ]}
              />
            </>
          )}
          <DraftReview
            task={
              caseId
                ? (source.data as CaseDetail)?.task
                : (validatedTask ?? resumedReview.data?.task)
            }
            draft={
              caseId ? (source.data?.draft ?? {}) : form.getFieldsValue(true)
            }
          />
          <details>
            <summary>{tr("frontend.wizard.all_parameters")}</summary>
            <pre>
              {JSON.stringify(
                caseId ? source.data?.draft : form.getFieldsValue(true),
                null,
                2,
              )}
            </pre>
          </details>
          <Checkbox
            checked={confirmed}
            onChange={(e) => setConfirmed(e.target.checked)}
          >
            {tr("frontend.wizard.confirm_boundaries")}
          </Checkbox>
          <div>
            <Button
              type="primary"
              disabled={
                !confirmed ||
                source.isLoading ||
                source.isError ||
                (!caseId && !(validatedTask ?? resumedReview.data?.task))
              }
              loading={operation.busy}
              onClick={() =>
                void operation
                  .submit("/tasks", {
                    draft: form.getFieldsValue(true),
                    case_id: caseId,
                    evidence_mode: evidence,
                    confirmed,
                    use_rag: useRag,
                    credentials,
                  })
                  .catch(() => {})
              }
            >
              {tr("frontend.wizard.start")}
            </Button>
          </div>
        </Card>
      )}
      <Space className="wizard-nav">
        {step > 0 && !caseId && (
          <Button onClick={() => setStep(step - 1)}>
            {tr("frontend.wizard.previous")}
          </Button>
        )}
        {step < 2 && (
          <Button type="primary" onClick={() => setStep(step + 1)}>
            {tr("frontend.wizard.next")}
          </Button>
        )}
        {step === 2 && (
          <Button
            type="primary"
            loading={validating}
            onClick={() => void validate()}
          >
            {tr("frontend.wizard.validate")}
          </Button>
        )}
      </Space>
      {operation.view}
    </div>
  );
}
