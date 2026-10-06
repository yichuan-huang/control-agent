import { useI18n, type Translator } from "./i18n";
import { Descriptions, Typography } from "antd";
import type { Obj } from "./api/types";
function reviewText(tr: Translator) {
  const display = (value: unknown) =>
    value === null || value === undefined || value === ""
      ? tr("frontend.reviewdetails.not_provided")
      : String(value);
  const types: Record<string, string> = {
    local_setpoint_hold: tr("frontend.reviewdetails.hold"),
    transition_then_hold: tr("frontend.reviewdetails.transition"),
    disturbance_recovery_to_hold: tr("frontend.reviewdetails.recovery"),
  };
  const labels: Record<string, string> = {
    final_abs_error_max: tr("frontend.reviewdetails.final_error"),
    overshoot_max: tr("frontend.reviewdetails.overshoot"),
    settling_time_max_s: tr("frontend.reviewdetails.settling"),
    hold_duration_min_s: tr("frontend.reviewdetails.hold_duration"),
    perturbed_success_rate_min: tr("frontend.reviewdetails.success_rate"),
    required_phase_count_min: tr("frontend.reviewdetails.phase_count"),
    verified_handoff_count_min: tr("frontend.reviewdetails.handoff_count"),
    final_hold_duration_min_s: tr("frontend.reviewdetails.goal_hold"),
    recovery_abs_error_max: tr("frontend.reviewdetails.recovery_error"),
    recovery_time_max_s: tr("frontend.reviewdetails.recovery_time"),
    post_recovery_hold_duration_min_s: tr(
      "frontend.reviewdetails.post_recovery_hold",
    ),
    goal_region_entry_required: tr("frontend.reviewdetails.goal_entry"),
    evaluation_sample_time_s: tr(
      "frontend.reviewdetails.evaluation_sample_time",
    ),
    evaluation_horizon_s: tr("frontend.reviewdetails.run_duration"),
    evaluation_repeats: tr("frontend.reviewdetails.repeats"),
    clarification_rounds: tr("frontend.reviewdetails.clarification_rounds"),
    experiments: tr("frontend.reviewdetails.experiments"),
    same_failure_retries: tr("frontend.reviewdetails.failure_retries"),
    elapsed_time_s: tr("frontend.reviewdetails.elapsed_time"),
    distinct_experiments: tr("frontend.reviewdetails.experiment_types"),
    cumulative_excitation_time_s: tr("frontend.reviewdetails.excitation_time"),
  };
  const stopExplanation = tr("frontend.reviewdetails.stop_explanation");

  return { display, types, labels, stopExplanation };
}
export function DraftReview({ draft, task }: { draft: Obj; task?: Obj }) {
  const { t: tr } = useI18n();
  const { display, types, labels, stopExplanation } = reviewText(tr);

  const selected = (key: string) =>
    ((draft[key] ?? []) as string[])
      .map((name) => `${labels[name] ?? name}：${display(draft[name])}`)
      .join("；") || tr("frontend.reviewdetails.not_provided");
  const items = [
    ...(draft.external_data_enabled
      ? [
          [
            tr("frontend.reviewdetails.execution"),
            tr("frontend.reviewdetails.execution_help"),
          ],
        ]
      : []),
    [
      tr("frontend.reviewdetails.task_type"),
      types[String(draft.task_type)] ?? display(draft.task_type),
    ],
    [
      tr("frontend.reviewdetails.outputs"),
      ((draft.outputs ?? []) as string[][])
        .map((row) => row.filter(Boolean).join(" / "))
        .join("；"),
    ],
    [
      tr("frontend.charts.control_input"),
      ((draft.inputs ?? []) as string[][]).map((row) => row[0]).join("、"),
    ],
    [tr("frontend.reviewdetails.input_unit"), display(draft.input_unit)],
    [
      tr("frontend.reviewdetails.input_range"),
      tr("frontend.reviewdetails.range", {
        min: display(draft.input_min),
        max: display(draft.input_max),
      }),
    ],
    [tr("frontend.reviewdetails.stop_threshold"), display(draft.state_stop)],
    [
      tr("frontend.reviewdetails.reference"),
      draft.reference_enabled
        ? display(draft.reference)
        : tr("frontend.reviewdetails.not_provided"),
    ],
    [
      tr("frontend.reviewdetails.output_bounds"),
      draft.output_bounds_enabled
        ? tr("frontend.reviewdetails.output_range", {
            min: display(draft.output_min),
            max: display(draft.output_max),
          })
        : tr("frontend.reviewdetails.not_provided"),
    ],
    [
      tr("frontend.reviewdetails.performance"),
      selected("success_requirement_fields"),
    ],
    [tr("frontend.reviewdetails.entered_budgets"), selected("budget_fields")],
    [
      tr("frontend.reviewdetails.applied_defaults"),
      task?.budgets
        ? Object.entries(task.budgets as Obj)
            .map(([key, value]) => `${labels[key] ?? key}：${display(value)}`)
            .join("；")
        : tr("frontend.reviewdetails.validate_first"),
    ],
    [
      tr("frontend.reviewdetails.response_preference"),
      draft.response_time_preference_enabled
        ? display(draft.response_time_preference_s)
        : tr("frontend.reviewdetails.not_provided"),
    ],
  ];
  if (draft.external_data_enabled)
    items.push(
      [tr("frontend.reviewdetails.region"), display(draft.region_label)],
      [
        tr("frontend.reviewdetails.sample_time"),
        display(draft.evaluation_dt_s),
      ],
      [
        tr("frontend.reviewdetails.run_duration"),
        display(draft.evaluation_horizon_s),
      ],
      [tr("frontend.reviewdetails.repeats"), display(draft.evaluation_repeats)],
      [
        tr("frontend.reviewdetails.final_error"),
        display(draft.final_abs_error_max),
      ],
    );
  if (draft.task_type === "transition_then_hold")
    items.push(
      [
        tr("frontend.reviewdetails.initial_region"),
        display(draft.initial_region),
      ],
      [tr("frontend.reviewdetails.goal_region"), display(draft.goal_region)],
      [
        tr("frontend.reviewdetails.initial_output"),
        draft.initial_output_value_enabled
          ? display(draft.initial_output_value)
          : tr("frontend.reviewdetails.not_provided"),
      ],
      [
        tr("frontend.reviewdetails.intermediate_targets"),
        display(draft.intermediate_targets),
      ],
      ...(draft.external_data_enabled
        ? [
            [
              tr("frontend.reviewdetails.transition_deadline"),
              display(draft.transition_deadline_s),
            ],
            [
              tr("frontend.reviewdetails.verified_transitions"),
              display(draft.handoff_count_min),
            ],
          ]
        : []),
    );
  if (draft.task_type === "disturbance_recovery_to_hold")
    items.push(
      [
        tr("frontend.reviewdetails.disturbance_event"),
        display(draft.disturbance_event),
      ],
      [
        tr("frontend.reviewdetails.recovery_start"),
        display(draft.recovery_start_condition),
      ],
      [
        tr("frontend.reviewdetails.recovery_region"),
        display(draft.disturbance_hold_region),
      ],
      ...(draft.external_data_enabled
        ? [
            [
              tr("frontend.reviewdetails.disturbance_channel"),
              display(draft.disturbance_channel),
            ],
            [
              tr("frontend.reviewdetails.disturbance_timing"),
              `${display(draft.disturbance_start_s)} / ${display(draft.disturbance_duration_s)}`,
            ],
            [
              tr("frontend.reviewdetails.disturbance_amplitude"),
              display(draft.disturbance_amplitude),
            ],
            [
              tr("frontend.reviewdetails.recovery_time"),
              display(draft.recovery_deadline_s),
            ],
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
        {stopExplanation} {tr("frontend.reviewdetails.shared_input_help")}
      </Typography.Paragraph>
    </>
  );
}
export function TaskBounds({ task }: { task: Obj }) {
  const { t: tr } = useI18n();
  const { display, labels } = reviewText(tr);

  const budgets = task.budgets as Obj | undefined;
  const disturbance = (task.disturbance_contract ?? {}) as Obj;
  return (
    <Descriptions
      column={1}
      size="small"
      items={[
        {
          key: "reference",
          label: tr("frontend.reviewdetails.reference"),
          children: display(task.reference),
        },
        {
          key: "region",
          label: tr("frontend.reviewdetails.region"),
          children: display(task.operating_region),
        },
        {
          key: "criteria",
          label: tr("frontend.reviewdetails.performance"),
          children:
            Object.entries((task.success_requirements ?? {}) as Obj)
              .map(([key, value]) => `${labels[key] ?? key}：${display(value)}`)
              .join("；") || tr("frontend.reviewdetails.not_provided"),
        },
        ...(task.task_type === "transition_then_hold"
          ? [
              {
                key: "targets",
                label: tr("frontend.reviewdetails.phase_targets"),
                children: `${display(task.initial_output_value)} → ${[...((task.intermediate_targets ?? []) as unknown[]), task.reference].map(display).join(" → ")}`,
              },
            ]
          : []),
        ...(Object.keys(disturbance).length
          ? [
              {
                key: "disturbance",
                label: tr("frontend.reviewdetails.disturbance_settings"),
                children: tr("frontend.reviewdetails.disturbance_summary", {
                  channel: display(disturbance.channel),
                  start: display(disturbance.time_s),
                  amplitude: display(disturbance.amplitude),
                  duration: display(disturbance.duration_s),
                }),
              },
            ]
          : []),
        {
          key: "stop",
          label: tr("frontend.reviewdetails.stop_threshold"),
          children: display(task.state_stop),
        },
        {
          key: "budgets",
          label: tr("frontend.reviewdetails.applied_budgets"),
          children:
            budgets && Object.keys(budgets).length
              ? Object.entries(budgets)
                  .map(
                    ([key, value]) =>
                      `${labels[key] ?? key}：${display(value)}`,
                  )
                  .join("；")
              : tr("frontend.reviewdetails.not_provided"),
        },
      ]}
    />
  );
}
