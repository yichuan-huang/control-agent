import { Descriptions, Typography } from "antd";
import type { Obj } from "./api/types";
const display = (value: unknown) =>
  value === null || value === undefined || value === ""
    ? "未提供"
    : String(value);
const types: Record<string, string> = {
  local_setpoint_hold: "保持在目标附近",
  transition_then_hold: "变化到新目标后保持",
  disturbance_recovery_to_hold: "受到扰动后恢复并保持",
};
const labels: Record<string, string> = {
  final_abs_error_max: "终值绝对误差上限",
  overshoot_max: "超调上限",
  settling_time_max_s: "稳定时间上限 (s)",
  hold_duration_min_s: "保持时间下限 (s)",
  perturbed_success_rate_min: "重复试验成功率下限",
  clarification_rounds: "澄清轮次上限",
  experiments: "实验次数上限",
  same_failure_retries: "同类失败重试上限",
  elapsed_time_s: "累计耗时上限 (s)",
  distinct_experiments: "实验种类上限",
  cumulative_excitation_time_s: "累计激励时间上限 (s)",
};
export const stopExplanation =
  "任一被检查测量值的绝对值大于该阈值时停止或判定越界；不是与目标的偏差，也不是硬件急停。";
export function DraftReview({ draft, task }: { draft: Obj; task?: Obj }) {
  const selected = (key: string) =>
    ((draft[key] ?? []) as string[])
      .map((name) => `${labels[name] ?? name}：${display(draft[name])}`)
      .join("；") || "未提供";
  const items = [
    ["任务类型", types[String(draft.task_type)] ?? display(draft.task_type)],
    [
      "测量输出",
      ((draft.outputs ?? []) as string[][])
        .map((row) => row.filter(Boolean).join(" / "))
        .join("；"),
    ],
    [
      "控制输入",
      ((draft.inputs ?? []) as string[][]).map((row) => row[0]).join("、"),
    ],
    ["输入单位", display(draft.input_unit)],
    [
      "共享输入范围",
      `${display(draft.input_min)} 至 ${display(draft.input_max)}`,
    ],
    ["软件试验停止阈值", display(draft.state_stop)],
    ["参考目标", draft.reference_enabled ? display(draft.reference) : "未提供"],
    [
      "输出边界",
      draft.output_bounds_enabled
        ? `${display(draft.output_min)} 至 ${display(draft.output_max)}`
        : "未提供",
    ],
    ["性能要求", selected("success_requirement_fields")],
    ["已填写预算", selected("budget_fields")],
    [
      "实际应用预算（未填写项沿用内核默认）",
      task?.budgets
        ? Object.entries(task.budgets as Obj)
            .map(([key, value]) => `${labels[key] ?? key}：${display(value)}`)
            .join("；")
        : "请先校验任务",
    ],
    [
      "响应时间偏好 (s)",
      draft.response_time_preference_enabled
        ? display(draft.response_time_preference_s)
        : "未提供",
    ],
  ];
  if (draft.task_type === "transition_then_hold")
    items.push(
      ["开始区域", display(draft.initial_region)],
      ["目标区域", display(draft.goal_region)],
      [
        "初始输出",
        draft.initial_output_value_enabled
          ? display(draft.initial_output_value)
          : "未提供",
      ],
      ["中间目标", display(draft.intermediate_targets)],
    );
  if (draft.task_type === "disturbance_recovery_to_hold")
    items.push(
      ["扰动事件", display(draft.disturbance_event)],
      ["恢复起点", display(draft.recovery_start_condition)],
      ["恢复后保持区域", display(draft.disturbance_hold_region)],
    );
  return (
    <>
      <Descriptions
        size="small"
        bordered
        column={1}
        items={items.map(([label, children]) => ({
          key: label,
          label,
          children,
        }))}
      />
      <Typography.Paragraph type="secondary">
        {stopExplanation} 输入范围共同应用于已声明的控制输入。
      </Typography.Paragraph>
    </>
  );
}
export function TaskBounds({ task }: { task: Obj }) {
  const budgets = task.budgets as Obj | undefined;
  return (
    <Descriptions
      column={1}
      size="small"
      items={[
        {
          key: "stop",
          label: "软件试验停止阈值",
          children: display(task.state_stop),
        },
        {
          key: "budgets",
          label: "实际应用预算",
          children:
            budgets && Object.keys(budgets).length
              ? Object.entries(budgets)
                  .map(
                    ([key, value]) =>
                      `${labels[key] ?? key}：${display(value)}`,
                  )
                  .join("；")
              : "未提供",
        },
      ]}
    />
  );
}
