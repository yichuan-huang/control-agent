import { keepLocaleData, useI18n } from "./i18n";
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
  const { t: tr, locale, errorText } = useI18n();

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
    placeholderData: keepLocaleData(locale, [
      "task",
      task.session_id,
      locale,
      task.revision,
      "evidence-curves",
      selected?.value,
      selectedSignal,
      ...window,
    ]),
    queryKey: [
      "task",
      task.session_id,
      locale,
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
        {tr("frontend.datacurves.empty")}
      </Typography.Paragraph>
    );
  return (
    <Space
      data-testid="evidence-curves"
      orientation="vertical"
      style={{ width: "100%", marginTop: 20 }}
    >
      <Typography.Title level={5}>
        {tr("frontend.datacurves.title")}
      </Typography.Title>
      <Typography.Text type="secondary">
        {tr("frontend.datacurves.help")}
      </Typography.Text>
      <Space wrap>
        <Select
          aria-label={tr("frontend.datacurves.trial")}
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
          aria-label={tr("frontend.datacurves.signal")}
          style={{ minWidth: 140 }}
          value={selectedSignal}
          options={selected?.signals.map((value) => ({ value, label: value }))}
          onChange={setSignal}
        />
      </Space>
      <Space wrap>
        <InputNumber
          aria-label={tr("frontend.datacurves.window_start")}
          placeholder={tr("frontend.datacurves.start")}
          value={start}
          onChange={setStart}
        />
        <InputNumber
          aria-label={tr("frontend.datacurves.window_end")}
          placeholder={tr("frontend.datacurves.end")}
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
          {tr("frontend.datacurves.view_curves")}
        </Button>
        <Button onClick={() => changeWindow([null, null])}>
          {tr("frontend.datacurves.full_window")}
        </Button>
      </Space>
      {curve.isFetching && <Spin />}
      {curve.error && (
        <Alert type="error" title={errorText(curve.error)} />
      )}{" "}
      {curve.data && (
        <>
          <Typography.Text type="secondary">
            {tr("frontend.datacurves.trial_prefix")}
            {curve.data.trial_id} {tr("frontend.datacurves.original_prefix")}
            {curve.data.original_points}{" "}
            {tr("frontend.datacurves.displayed_prefix")}
            {curve.data.display_points}{" "}
            {tr("frontend.datacurves.revision_prefix")}
            {curve.data.revision}
          </Typography.Text>
          <Suspense fallback={<Spin />}>
            <Charts
              curve={curve.data}
              identity={JSON.stringify([
                task.session_id,
                task.revision,
                selected?.value,
                selectedSignal,
              ])}
              window={window}
              onWindowChange={changeWindow}
              outputTitle={tr("frontend.datacurves.chart_title")}
            />
          </Suspense>
        </>
      )}
    </Space>
  );
}
