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
