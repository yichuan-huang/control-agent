import { expect, test } from "vitest";
import { saveDraft, readDraft, requestIdentity, parseObject } from "./safety";
test("persist only explicit draft fields, never nested credentials", () => {
  saveDraft({
    description: "heater",
    api_key: "secret",
    credentials: { api_key: "secret" },
    outputs: [["temperature", "C"]],
  });
  expect(sessionStorage.getItem("cfdc:draft")).not.toContain("secret");
  expect(readDraft()?.description).toBe("heater");
});
test("transport retry retains ID, definite completion starts next action", () => {
  const r = requestIdentity();
  expect(r.get()).toBe(r.get());
  const old = r.get();
  r.clear();
  expect(r.get()).not.toBe(old);
});
test("JSON submission accepts objects only", () => {
  expect(() => parseObject("[]")).toThrow();
  expect(() => parseObject("null")).toThrow();
  expect(parseObject('{"value":1}')).toEqual({ value: 1 });
});
test("external wizard settings survive refresh without persisting unknown data", () => {
  const draft = {
    external_data_enabled: true,
    region_label: "局部",
    evaluation_dt_s: 0.02,
    evaluation_horizon_s: 20,
    evaluation_repeats: 20,
    transition_deadline_s: 10,
    handoff_count_min: 1,
    disturbance_channel: "u",
    disturbance_start_s: 1,
    disturbance_amplitude: 0.1,
    disturbance_duration_s: 2,
    recovery_deadline_s: 10,
  };
  saveDraft({ ...draft, api_key: "never-store" });
  expect(readDraft()).toEqual(draft);
});
test("obsolete execution configuration is rejected instead of migrated", () => {
  const oldDraft = {
    description: "generic",
    execution_mode: "managed",
    runner_id: "local_python",
    model_id: "optical",
  };
  expect(() => saveDraft(oldDraft)).toThrow();
  sessionStorage.setItem("cfdc:draft", JSON.stringify(oldDraft));
  expect(readDraft()).toBeNull();
});
