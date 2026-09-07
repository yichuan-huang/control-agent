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
  required_phase_count_min: "最少阶段数",
  verified_handoff_count_min: "最少验证切换次数",
  final_hold_duration_min_s: "目标保持时间 (s)",
  recovery_abs_error_max: "恢复误差上限",
  recovery_time_max_s: "恢复时间上限 (s)",
  post_recovery_hold_duration_min_s: "恢复后保持时间 (s)",
  goal_region_entry_required: "需要到达目标区域",
  evaluation_sample_time_s: "评价采样间隔 (s)",
  evaluation_horizon_s: "每次运行时长 (s)",
  evaluation_repeats: "重复运行次数",
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
    ...(draft.external_data_enabled
      ? [
          [
            "执行与回传",
            "在自己的环境执行协议，通过任务页下载请求、上传数据并查看结果",
          ],
        ]
      : []),
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
  if (draft.external_data_enabled)
    items.push(
      ["评价区域", display(draft.region_label)],
      ["采样间隔 (s)", display(draft.evaluation_dt_s)],
      ["每次运行时长 (s)", display(draft.evaluation_horizon_s)],
      ["重复运行次数", display(draft.evaluation_repeats)],
      ["终值绝对误差上限", display(draft.final_abs_error_max)],
    );
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
      ...(draft.external_data_enabled
        ? [
            ["到达目标时间上限 (s)", display(draft.transition_deadline_s)],
            ["最少验证阶段切换次数", display(draft.handoff_count_min)],
          ]
        : []),
    );
  if (draft.task_type === "disturbance_recovery_to_hold")
    items.push(
      ["扰动事件", display(draft.disturbance_event)],
      ["恢复起点", display(draft.recovery_start_condition)],
      ["恢复后保持区域", display(draft.disturbance_hold_region)],
      ...(draft.external_data_enabled
        ? [
            ["扰动输入通道", display(draft.disturbance_channel)],
            [
              "扰动开始 / 持续时间 (s)",
              `${display(draft.disturbance_start_s)} / ${display(draft.disturbance_duration_s)}`,
            ],
            ["扰动幅度", display(draft.disturbance_amplitude)],
            ["恢复时间上限 (s)", display(draft.recovery_deadline_s)],
          ]
        : []),
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
  const disturbance = (task.disturbance_contract ?? {}) as Obj;
  return (
    <Descriptions
      column={1}
      size="small"
      items={[
        {
          key: "reference",
          label: "参考目标",
          children: display(task.reference),
        },
        {
          key: "region",
          label: "评价区域",
          children: display(task.operating_region),
        },
        {
          key: "criteria",
          label: "性能要求",
          children:
            Object.entries((task.success_requirements ?? {}) as Obj)
              .map(([key, value]) => `${labels[key] ?? key}：${display(value)}`)
              .join("；") || "未提供",
        },
        ...(task.task_type === "transition_then_hold"
          ? [
              {
                key: "targets",
                label: "阶段目标",
                children: `${display(task.initial_output_value)} → ${[...((task.intermediate_targets ?? []) as unknown[]), task.reference].map(display).join(" → ")}`,
              },
            ]
          : []),
        ...(Object.keys(disturbance).length
          ? [
              {
                key: "disturbance",
                label: "扰动设置",
                children: `通道 ${display(disturbance.channel)}；开始 ${display(disturbance.time_s)} s；幅度 ${display(disturbance.amplitude)}；持续 ${display(disturbance.duration_s)} s`,
              },
            ]
          : []),
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
