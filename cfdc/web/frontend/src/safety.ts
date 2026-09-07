import type { Obj } from "./api/types";
const draftFields = new Set(
  "external_data_enabled region_label evaluation_dt_s evaluation_horizon_s evaluation_repeats transition_deadline_s handoff_count_min disturbance_channel disturbance_start_s disturbance_amplitude disturbance_duration_s recovery_deadline_s description task_type outputs inputs input_unit reference_enabled reference input_min input_max state_stop output_bounds_enabled output_min output_max initial_region goal_region initial_output_value_enabled initial_output_value intermediate_targets disturbance_event recovery_start_condition disturbance_hold_region success_requirement_fields final_abs_error_max overshoot_max settling_time_max_s hold_duration_min_s perturbed_success_rate_min response_time_preference_enabled response_time_preference_s budget_fields distinct_experiments cumulative_excitation_time_s".split(
    " ",
  ),
);
export function saveDraft(draft: Obj) {
  const clean = Object.fromEntries(
    Object.entries(draft).filter(([key]) => draftFields.has(key)),
  );
  try {
    sessionStorage.setItem("cfdc:draft", JSON.stringify(clean));
  } catch {
    /* Full storage must not discard the in-memory form. */
  }
}
export function readDraft(): Obj | null {
  try {
    const value: unknown = JSON.parse(
      sessionStorage.getItem("cfdc:draft") ?? "null",
    );
    if (!value || typeof value !== "object" || Array.isArray(value))
      return null;
    return Object.fromEntries(
      Object.entries(value).filter(([key]) => draftFields.has(key)),
    );
  } catch {
    return null;
  }
}
export function requestIdentity() {
  let id = "";
  return {
    get: () => id || (id = crypto.randomUUID()),
    clear: () => {
      id = "";
    },
  };
}
export function parseObject(text: string): Obj {
  const value: unknown = JSON.parse(text);
  if (!value || typeof value !== "object" || Array.isArray(value))
    throw new Error("请提交完整 JSON 对象。");
  return value as Obj;
}
