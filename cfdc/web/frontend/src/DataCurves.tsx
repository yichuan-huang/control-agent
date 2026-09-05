import { lazy, Suspense, useCallback, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Alert,
  Button,
  InputNumber,
  Select,
  Space,
  Spin,
  Typography,
} from "antd";
import type { DTO, Summary } from "./api/types";
import { useTaskReader } from "./api/useTaskReader";
import type { WindowRange } from "./plotWindow";
const Charts = lazy(() => import("./Charts"));
export default function DataCurves({
  task,
  options,
}: {
  task: Summary;
  options: NonNullable<DTO<"ProtocolView">["evidence_options"]>;
}) {
  const read = useTaskReader(task);
  const [show, setShow] = useState(false);
  const [selection, setSelection] = useState("");
  const [signal, setSignal] = useState("");
  const [start, setStart] = useState<number | null>(null),
    [end, setEnd] = useState<number | null>(null);
  const [window, setWindow] = useState<WindowRange>([null, null]);
  const changeWindow = useCallback((next: WindowRange) => {
    setStart(next[0]);
    setEnd(next[1]);
    setWindow((previous) =>
      previous[0] === next[0] && previous[1] === next[1] ? previous : next,
    );
  }, []);
  const selected = selection
    ? options.find((o) => o.value === selection)
    : options[0];
  const selectedSignal = signal || selected?.signals[0] || "";
  const curve = useQuery({
    queryKey: [
      "task",
      task.session_id,
      task.revision,
      "evidence-curves",
      selected?.value,
      selectedSignal,
      ...window,
    ],
    enabled: show && !!selected && !!selectedSignal,
    queryFn: () => {
      const params = new URLSearchParams({
        selection: selected!.value,
        signal: selectedSignal,
      });
      if (window[0] !== null) params.set("start", String(window[0]));
      if (window[1] !== null) params.set("end", String(window[1]));
      return read<DTO<"EvidenceCurveView">>(
        `/tasks/${task.session_id}/evidence/curves?${params}`,
      );
    },
  });
  if (!options.length)
    return (
      <Typography.Paragraph type="secondary">
        暂无当前协议已通过的数据曲线。
      </Typography.Paragraph>
    );
  return (
    <Space
      data-testid="evidence-curves"
      orientation="vertical"
      style={{ width: "100%", marginTop: 20 }}
    >
      <Typography.Title level={5}>已通过的实验数据</Typography.Title>
      <Typography.Text type="secondary">
        仅显示当前协议已接受的数据。缩放图形会按所选时间窗口重新读取完整记录的显示采样。
      </Typography.Text>
      <Space wrap>
        <Select
          aria-label="实验数据试次"
          showSearch={{ optionFilterProp: "label" }}
          style={{ minWidth: 220, maxWidth: "100%" }}
          value={selected?.value}
          options={options.map((o) => ({ value: o.value, label: o.label }))}
          onChange={(value) => {
            setSelection(value);
            setSignal("");
            changeWindow([null, null]);
          }}
        />
        <Select
          aria-label="实验数据信号"
          style={{ minWidth: 140 }}
          value={selectedSignal}
          options={selected?.signals.map((value) => ({ value, label: value }))}
          onChange={setSignal}
        />
      </Space>
      <Space wrap>
        <InputNumber
          aria-label="实验窗口开始秒"
          placeholder="开始 (s)"
          value={start}
          onChange={setStart}
        />
        <InputNumber
          aria-label="实验窗口结束秒"
          placeholder="结束 (s)"
          value={end}
          onChange={setEnd}
        />
        <Button
          disabled={start !== null && end !== null && start >= end}
          onClick={() => {
            changeWindow([start, end]);
            setShow(true);
          }}
        >
          查看通过数据曲线
        </Button>
        <Button onClick={() => changeWindow([null, null])}>完整实验窗口</Button>
      </Space>
      {curve.isFetching && <Spin />}
      {curve.error && <Alert type="error" title={String(curve.error)} />}{" "}
      {curve.data && (
        <>
          <Typography.Text type="secondary">
            试次 {curve.data.trial_id} · 原始 {curve.data.original_points} 点 ·
            显示 {curve.data.display_points} 点 · 修订 {curve.data.revision}
          </Typography.Text>
          <Suspense fallback={<Spin />}>
            <Charts
              curve={curve.data}
              window={window}
              onWindowChange={changeWindow}
              outputTitle="实验数据曲线"
            />
          </Suspense>
        </>
      )}
    </Space>
  );
}
