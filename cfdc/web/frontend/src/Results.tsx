import { lazy, Suspense, useState, useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Alert,
  Button,
  Card,
  InputNumber,
  Select,
  Space,
  Spin,
  Table,
  Tag,
  Typography,
} from "antd";
import { Link } from "react-router-dom";
import { download } from "./api/client";
import { useTaskReader } from "./api/useTaskReader";
import type { Curve, Evaluations, Summary } from "./api/types";
import type { WindowRange } from "./plotWindow";
const Charts = lazy(() => import("./Charts"));
export default function Results({ task }: { task: Summary }) {
  const read = useTaskReader(task);
  const [selection, setSelection] = useState("");
  const [signal, setSignal] = useState("");
  const [control, setControl] = useState("");
  const [start, setStart] = useState<number | null>(null);
  const [end, setEnd] = useState<number | null>(null);
  const [window, setWindow] = useState<[number | null, number | null]>([
    null,
    null,
  ]);
  const changeWindow = useCallback((next: WindowRange) => {
    setStart(next[0]);
    setEnd(next[1]);
    setWindow((previous) =>
      previous[0] === next[0] && previous[1] === next[1] ? previous : next,
    );
  }, []);
  const evaluation = useQuery({
    queryKey: [
      "task",
      task.session_id,
      task.revision,
      "evaluations",
      selection,
    ],
    queryFn: () =>
      read<Evaluations>(
        `/tasks/${task.session_id}/evaluations${selection ? "?selection=" + encodeURIComponent(selection) : ""}`,
      ),
  });
  const selected = evaluation.data?.options.find(
    (o) => o.value === (selection || evaluation.data?.selected_selection),
  );
  const signalValue = signal || selected?.signals[0] || "";
  const controlValue = control || selected?.control_signals?.[0] || "";
  const curve = useQuery({
    queryKey: [
      "task",
      task.session_id,
      task.revision,
      "curves",
      selected?.value,
      signalValue,
      controlValue,
      ...window,
    ],
    enabled: !!selected && !!signalValue,
    queryFn: () => {
      const p = new URLSearchParams({
        selection: selected!.value,
        signal: signalValue,
      });
      if (controlValue) p.set("control", controlValue);
      if (window[0] !== null) p.set("start", String(window[0]));
      if (window[1] !== null) p.set("end", String(window[1]));
      return read<Curve>(`/tasks/${task.session_id}/curves?${p}`);
    },
  });
  return (
    <Card title="评价结果">
      <Space orientation="vertical" style={{ width: "100%" }}>
        <Alert
          title={task.workspace.title}
          description={task.workspace.explanation}
          type="info"
        />
        <Typography.Paragraph>
          <strong>下一步：</strong>
          {task.workspace.actionable
            ? "回到当前步骤，按主要动作继续。"
            : task.status === "performance_met"
              ? "导出本次软件验证记录；如需验证其他目标或边界，可创建新任务。"
              : task.status === "capability_gap"
                ? "携带本次记录，在新任务中补充证据或重新定义目标与边界。"
                : task.status === "cancelled"
                  ? "导出已有记录，按需创建新任务。"
                  : "查看已记录结果，并按当前步骤继续。"}
        </Typography.Paragraph>
        <Space wrap>
          {task.workspace.actionable ? (
            <Button href="#current-action">回到当前动作</Button>
          ) : (
            <>
              <Button href={download(task.session_id, "bundle")}>
                导出软件验证记录
              </Button>
              <Link to="/new">创建新任务</Link>
            </>
          )}
        </Space>
        {evaluation.error && (
          <Alert type="error" title={String(evaluation.error)} />
        )}
        <Select
          aria-label="评价阶段与试次"
          showSearch={{ optionFilterProp: "label" }}
          style={{ width: "100%" }}
          value={selected?.value}
          placeholder="暂无已记录评价"
          options={evaluation.data?.options.map((o) => ({
            value: o.value,
            label: o.label,
          }))}
          onChange={(v) => {
            setSelection(v);
            setSignal("");
            setControl("");
            setWindow([null, null]);
            setStart(null);
            setEnd(null);
          }}
        />
        {selected && (
          <>
            <Tag>
              {evaluation.data?.selected_stage === "confirmation"
                ? "独立确认"
                : "开发评价"}
            </Tag>
            <Table
              size="small"
              scroll={{ x: 500 }}
              pagination={false}
              rowKey={(_, i) => String(i)}
              dataSource={evaluation.data?.metrics}
              columns={["指标", "要求", "记录值", "说明"].map((title, i) => ({
                title,
                render: (_: unknown, row: string[]) => row[i] ?? "",
              }))}
            />
            <Space wrap>
              <Select
                aria-label="输出信号"
                style={{ minWidth: 140 }}
                value={signalValue}
                options={selected.signals.map((value) => ({
                  value,
                  label: value,
                }))}
                onChange={setSignal}
              />
              <Select
                aria-label="控制输入信号"
                style={{ minWidth: 140 }}
                value={controlValue}
                options={selected.control_signals?.map((value) => ({
                  value,
                  label: value,
                }))}
                onChange={setControl}
              />
              <InputNumber
                aria-label="窗口开始秒"
                placeholder="开始 (s)"
                value={start}
                onChange={setStart}
              />
              <InputNumber
                aria-label="窗口结束秒"
                placeholder="结束 (s)"
                value={end}
                onChange={setEnd}
              />
              <Button
                disabled={start !== null && end !== null && start >= end}
                onClick={() => setWindow([start, end])}
              >
                应用窗口
              </Button>
              <Button
                onClick={() => {
                  setStart(null);
                  setEnd(null);
                  setWindow([null, null]);
                  setStart(null);
                  setEnd(null);
                }}
              >
                完整窗口
              </Button>
            </Space>
            {curve.error && <Alert type="error" title={String(curve.error)} />}{" "}
            {curve.data && (
              <>
                <Typography.Text type="secondary">
                  原始 {curve.data.original_points} 点 · 显示{" "}
                  {curve.data.display_points} 点 · 修订 {curve.data.revision}
                </Typography.Text>
                <Suspense fallback={<Spin />}>
                  <Charts
                    curve={curve.data}
                    window={window}
                    onWindowChange={changeWindow}
                  />
                </Suspense>
              </>
            )}
          </>
        )}
      </Space>
    </Card>
  );
}
