import { useEffect, useState } from "react";
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
import { api, ApiError } from "./api/client";
import type { Obj, CaseDetail, DTO } from "./api/types";
import { readDraft, saveDraft } from "./safety";
import { useSettings } from "./context";
import { useOperation } from "./operations";
import Markdown from "./Markdown";
import { DraftReview, stopExplanation } from "./ReviewDetails";
const requirements: Record<string, string> = {
  final_abs_error_max: "稳定后允许偏离目标多少",
  overshoot_max: "允许超过目标多少",
  settling_time_max_s: "希望多少秒内稳定",
  hold_duration_min_s: "至少保持多少秒",
  perturbed_success_rate_min: "重复试验成功率下限",
};
const budgets: Record<string, string> = {
  distinct_experiments: "最多尝试几种实验",
  cumulative_excitation_time_s: "累计激励时间上限 (s)",
};
export default function Wizard() {
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
  const [review, setReview] = useState("");
  const [error, setError] = useState("");
  const [validating, setValidating] = useState(false);
  const [confirmed, setConfirmed] = useState(false);
  const [evidence, setEvidence] = useState(restored.evidence);
  const { credentials, useRag } = useSettings();
  const operation = useOperation();
  const source = useQuery({
    queryKey: ["draft", caseId],
    queryFn: () =>
      caseId
        ? api<CaseDetail>(`/cases/${caseId}`)
        : api<DTO<"DraftResponse">>("/drafts/default"),
  });
  useEffect(() => {
    if (source.data) {
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
    queryKey: ["draft-review-resume", navigationKey],
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
  async function validate() {
    setValidating(true);
    setError("");
    try {
      const r = await api<DTO<"DraftValidationResponse">>("/drafts/validate", {
        draft: form.getFieldsValue(true),
        case_id: caseId,
      });
      setReview(r.summary);
      setValidatedTask(r.task);
      setStep(3);
    } catch (e) {
      if (e instanceof ApiError && e.detail.fields) {
        form.setFields(
          Object.entries(e.detail.fields).map(([name, message]) => ({
            name,
            errors: [message],
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
      setError(e instanceof Error ? e.message : String(e));
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
        {caseId ? "核对案例任务" : "定义我的控制任务"}
      </Typography.Title>
      <Steps
        current={step}
        items={["目标", "信号", "边界与要求", "核对"].map((title) => ({
          title,
        }))}
      />
      {source.error && (
        <Alert
          type="error"
          title={String(source.error)}
          action={
            <Button onClick={() => void source.refetch()}>重新读取</Button>
          }
        />
      )}
      {draftRejection && <Alert type="warning" title={draftRejection} />}
      {error && <Alert type="error" title={error} />}
      {resumedReview.error && (
        <Alert
          type="error"
          title="恢复的草稿需要重新核对；请返回边界页校验。"
        />
      )}{" "}
      {caseId && (
        <Alert
          title="案例参数已锁定"
          description="案例运行使用原始任务合同。修改前请复制为自己的任务。"
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
              复制为我的任务
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
              title="在浏览器中管理自己的控制任务"
              description="依次填写目标、信号和边界，核对后回答诊断问题。系统将提供采集协议、检查清单和数据模板；实际试验在应用外部完成，您使用自己的环境执行后，在任务页上传结果。系统计算特征、形成方案并引导冻结、评价、调优和独立确认，无需手写特征或控制器 JSON。"
            />
          )}
          <Form.Item name="description" label="设备与目标">
            <Input.TextArea
              rows={4}
              placeholder="描述设备、可测量的量，以及希望达到的目标"
            />
          </Form.Item>
          <Form.Item name="task_type" label="任务类型">
            <Select
              options={[
                { label: "保持在目标附近", value: "local_setpoint_hold" },
                { label: "变化到新目标后保持", value: "transition_then_hold" },
                {
                  label: "受到扰动后恢复并保持",
                  value: "disturbance_recovery_to_hold",
                },
              ]}
            />
          </Form.Item>
          {taskType === "transition_then_hold" && (
            <>
              {text("initial_region", "开始区域")}
              {text("goal_region", "目标区域")}
              {caseId
                ? optional(
                    "initial_output_value_enabled",
                    "填写初始输出值",
                    num("initial_output_value", "初始输出值"),
                  )
                : num("initial_output_value", "初始输出值")}
              {text("intermediate_targets", "中间目标（逗号分隔）")}
              {!caseId && (
                <>
                  {num("transition_deadline_s", "到达目标时间上限 (s)")}
                  {num("handoff_count_min", "最少验证阶段切换次数")}
                </>
              )}
            </>
          )}
          {taskType === "disturbance_recovery_to_hold" && (
            <>
              {text("disturbance_event", "扰动事件")}
              {text("recovery_start_condition", "恢复起点")}
              {text("disturbance_hold_region", "恢复后保持区域")}
              {!caseId && (
                <>
                  {text("disturbance_channel", "扰动输入通道名称")}
                  {num("disturbance_start_s", "扰动开始时间 (s)")}
                  {num("disturbance_amplitude", "扰动幅度（输入单位）")}
                  {num("disturbance_duration_s", "扰动持续时间 (s)")}
                  {num("recovery_deadline_s", "扰动后恢复时间上限 (s)")}
                </>
              )}
            </>
          )}
        </div>
        <div hidden={step !== 1}>
          <Typography.Title level={4}>测量输出</Typography.Title>
          <Form.List name="outputs">
            {(fields, { add, remove }) => (
              <>
                {fields.map((field) => (
                  <Space key={field.key} align="start" className="signal-row">
                    <Form.Item
                      name={[field.name, 0]}
                      label={`输出 ${field.name + 1} 名称`}
                    >
                      <Input />
                    </Form.Item>
                    <Form.Item name={[field.name, 1]} label="单位">
                      <Input />
                    </Form.Item>
                    <Button
                      aria-label={`删除输出 ${field.name + 1}`}
                      onClick={() => remove(field.name)}
                    >
                      删除
                    </Button>
                  </Space>
                ))}
                <Button onClick={() => add(["", ""])}>添加输出</Button>
              </>
            )}
          </Form.List>
          <Form.ErrorList errors={form.getFieldError("outputs")} />
          <Typography.Title level={4}>控制输入</Typography.Title>
          <Form.List name="inputs">
            {(fields, { add, remove }) => (
              <>
                {fields.map((field) => (
                  <Space key={field.key} align="start">
                    <Form.Item
                      name={[field.name, 0]}
                      label={`输入 ${field.name + 1} 名称`}
                    >
                      <Input />
                    </Form.Item>
                    <Button onClick={() => remove(field.name)}>删除</Button>
                  </Space>
                ))}
                <Button onClick={() => add([""])}>添加输入</Button>
              </>
            )}
          </Form.List>
          <Form.ErrorList errors={form.getFieldError("inputs")} />
          {text("input_unit", "输入单位")}
        </div>
        <div hidden={step !== 2}>
          <div className="field-grid">
            {num("input_min", "输入下限")}
            {num("input_max", "输入上限")}
            {num("state_stop", "软件试验停止阈值")}
          </div>
          <Typography.Paragraph type="secondary">
            {stopExplanation} 输入下限与上限共同应用于已声明的所有控制输入。
          </Typography.Paragraph>
          {caseId ? (
            optional(
              "reference_enabled",
              "设置参考目标",
              num("reference", "参考目标"),
            )
          ) : (
            <>
              <Form.Item name="external_data_enabled" hidden>
                <Input />
              </Form.Item>
              <Form.Item name="reference_enabled" hidden>
                <Input />
              </Form.Item>
              {num("reference", "参考目标")}
              {text("region_label", "评价区域（适用的工作范围）")}
              <Typography.Title level={4}>冻结评价设置</Typography.Title>
              <Typography.Paragraph>
                这些设置将在确认任务后用于生成完整运行清单。外部数据必须覆盖每次重复运行和全部输入输出。
              </Typography.Paragraph>
              <div className="field-grid">
                {num("evaluation_dt_s", "采样间隔 (s)")}
                {num("evaluation_horizon_s", "每次运行时长 (s)")}
                {num("evaluation_repeats", "重复运行次数")}
              </div>
              {num("final_abs_error_max", "稳定后允许偏离目标多少")}
            </>
          )}
          {optional(
            "output_bounds_enabled",
            "设置输出边界",
            <div className="field-grid">
              {num("output_min", "输出下限")}
              {num("output_max", "输出上限")}
            </div>,
          )}
          <ConfigProvider theme={{ token: { motion: false } }}>
            <Collapse
              activeKey={advanced ? ["optional"] : []}
              onChange={(keys) => setAdvanced(keys.length > 0)}
              items={[
                {
                  key: "optional",
                  label: "性能要求与预算（可选）",
                  forceRender: true,
                  children: (
                    <>
                      <Form.Item
                        name="success_requirement_fields"
                        label="明确的性能要求"
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
                        "填写响应时间偏好",
                        num("response_time_preference_s", "响应时间偏好 (s)"),
                      )}
                      <Form.Item name="budget_fields" label="实验预算">
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
        <Card title="任务核对">
          <Markdown>
            {review ||
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
                数据来源：
                {String((source.data as CaseDetail)?.data_source ?? "")}
              </Typography.Paragraph>
              <Select
                aria-label="证据模式"
                value={evidence}
                onChange={setEvidence}
                options={[
                  { value: "automatic", label: "自动案例实验" },
                  { value: "exercise_bundle", label: "教学练习包上传" },
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
            <summary>查看全部已填写参数</summary>
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
            我已核对目标、软件试验边界与预算
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
              确认软件边界并开始
            </Button>
          </div>
        </Card>
      )}
      <Space className="wizard-nav">
        {step > 0 && !caseId && (
          <Button onClick={() => setStep(step - 1)}>上一步</Button>
        )}
        {step < 2 && (
          <Button type="primary" onClick={() => setStep(step + 1)}>
            下一步
          </Button>
        )}
        {step === 2 && (
          <Button
            type="primary"
            loading={validating}
            onClick={() => void validate()}
          >
            校验并核对
          </Button>
        )}
      </Space>
      {operation.view}
    </div>
  );
}
