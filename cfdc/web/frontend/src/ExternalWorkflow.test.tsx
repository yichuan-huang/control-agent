import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import ExternalWorkflow from "./ExternalWorkflow";
vi.stubGlobal("matchMedia", () => ({
  matches: false,
  addListener: () => {},
  removeListener: () => {},
}));
afterEach(cleanup);
test("external source selection submits explicit provenance without JSON", () => {
  const submit = vi.fn();
  render(
    <ExternalWorkflow
      sessionId="A"
      action="select_external_source"
      workflow={{}}
      busy={false}
      onSubmit={submit}
    />,
  );
  fireEvent.click(screen.getByLabelText("外部软件仿真"));
  fireEvent.click(screen.getByRole("button", { name: "确认数据来源" }));
  expect(submit).toHaveBeenCalledWith("select_external_source", {
    payload: { source_kind: "software" },
  });
  expect(screen.queryByText("打开专业 JSON 提交")).toBeNull();
});
test("freeze requires explicit review, and persistent failures and budgets remain visible", () => {
  const submit = vi.fn();
  render(
    <ExternalWorkflow
      sessionId="A"
      action="freeze"
      workflow={{
        source_kind: "measured",
        failure_reasons: ["run ID mismatch"],
        tuning: { attempts_used: 2, max_attempts: 4 },
        run: { stage: "confirmation", candidate_id: "candidate-2" },
      }}
      busy={false}
      onSubmit={submit}
    />,
  );
  const button = screen.getByRole("button", { name: "确认并冻结评价约定" });
  expect(button).toHaveProperty("disabled", true);
  expect(screen.getByText("run ID mismatch")).toBeTruthy();
  expect(screen.getByText(/2 \/ 4/)).toBeTruthy();
  fireEvent.click(screen.getByLabelText(/我已核对冻结/));
  fireEvent.click(button);
  expect(submit).toHaveBeenCalledWith("freeze", { confirmed: true });
});
test("fresh confirmation ZIP and recovery action are guided", () => {
  const submit = vi.fn();
  render(
    <ExternalWorkflow
      sessionId="A"
      action="submit_external_results"
      workflow={{ stage: "confirmation", recovery_available: true }}
      busy={false}
      onSubmit={submit}
    />,
  );
  expect(
    screen
      .getByRole("link", { name: "下载本轮完整运行包 ZIP" })
      .getAttribute("href"),
  ).toContain("external_run");
  expect(screen.getByText(/全新轨迹/)).toBeTruthy();
  fireEvent.click(screen.getByRole("button", { name: "重新采集并创建新任务" }));
  expect(submit).toHaveBeenCalledWith("restart_external_acquisition", {});
});
test("bounded tuning discloses proposed budget and frozen repetitions before starting", () => {
  render(
    <ExternalWorkflow
      sessionId="A"
      action="start_external_tuning"
      workflow={{
        evaluation_repeats: 20,
        proposed_tuning: { max_probes: 6, min_relative_improvement: 0.02 },
      }}
      busy={false}
      onSubmit={vi.fn()}
    />,
  );
  expect(screen.getByText(/最多 6 个候选/)).toBeTruthy();
  expect(screen.getByText(/至少 2%/)).toBeTruthy();
  expect(screen.getByText(/20 次/)).toBeTruthy();
});
test("pending accepted submission resumes processing without another upload", () => {
  const submit = vi.fn();
  render(
    <ExternalWorkflow
      sessionId="A"
      action="submit_external_results"
      workflow={{ resume_pending: true }}
      busy={false}
      onSubmit={submit}
    />,
  );
  fireEvent.click(screen.getByRole("button", { name: "完成已接收结果处理" }));
  expect(submit).toHaveBeenCalledWith("submit_external_results", {});
  expect(screen.queryByText("选择完整结果 ZIP")).toBeNull();
});

test("source selection exposes only generic provenance and external execution instructions", () => {
  render(
    <ExternalWorkflow
      sessionId="A"
      action="select_external_source"
      workflow={{}}
      busy={false}
      onSubmit={vi.fn()}
    />,
  );
  fireEvent.click(screen.getByLabelText("外部软件仿真"));
  expect(screen.queryByLabelText("由系统自动运行软件仿真")).toBeNull();
  expect(screen.queryByLabelText("手动运行并上传结果")).toBeNull();
  expect(screen.getByText(/实际试验在应用外部完成/)).toBeTruthy();
});
test("legacy recovery preserves evidence and requires a derived task without resuming execution", () => {
  const submit = vi.fn();
  render(
    <ExternalWorkflow
      sessionId="A"
      action=""
      workflow={{
        recovery_required: true,
        recovery_available: true,
        recovery_reason: "旧自动执行任务只保留历史证据，请创建新任务。",
      }}
      busy={false}
      onSubmit={submit}
    />,
  );
  expect(submit).not.toHaveBeenCalled();
  expect(screen.getByText(/旧自动执行任务只保留历史证据/)).toBeTruthy();
  expect(
    screen.queryByRole("button", { name: /继续自动|暂停自动/ }),
  ).toBeNull();
  fireEvent.click(screen.getByRole("button", { name: "重新采集并创建新任务" }));
  expect(submit).toHaveBeenCalledWith("restart_external_acquisition", {});
});
test("manual upload displays exact server filenames columns and units", () => {
  render(
    <ExternalWorkflow
      sessionId="A"
      action="submit_external_results"
      workflow={{}}
      requirements={{
        file_count: 2,
        repeats: 2,
        expected_format: "JSON",
        files: [
          {
            filename: "trial-0001.json",
            columns: [
              { name: "time_s", unit: "s" },
              { name: "intensity", unit: "a.u." },
            ],
          },
          {
            filename: "trial-0002.json",
            columns: [{ name: "time_s", unit: "s" }],
          },
        ],
      }}
      busy={false}
      onSubmit={vi.fn()}
    />,
  );
  expect(screen.getByText("本轮需回传 2 个试次文件")).toBeTruthy();
  expect(screen.getByText("trial-0001.json")).toBeTruthy();
  expect(screen.getByText(/intensity.*a.u./)).toBeTruthy();
  expect(screen.getByText(/请求包不含已完成的试验结果/)).toBeTruthy();
});

test("acquisition does not present an unused tuning budget as current work", () => {
  render(
    <ExternalWorkflow
      sessionId="A"
      action=""
      workflow={{
        stage: "awaiting_operator_report",
        tuning: { max_attempts: 6, attempts_used: 0, feedback_rounds_used: 0 },
      }}
      busy={false}
      onSubmit={vi.fn()}
    />,
  );
  expect(screen.queryByText(/候选预算/)).toBeNull();
});
