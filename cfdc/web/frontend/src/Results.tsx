import { keepLocaleData, useI18n } from "./i18n";
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
import { useApi } from "./api/client";
import { useTaskReader } from "./api/useTaskReader";
import type { Curve, Evaluations, Summary } from "./api/types";
import type { WindowRange } from "./plotWindow";
const Charts = lazy(() => import("./Charts"));
export default function Results({ task }: { task: Summary }) {
  const { t: tr, locale, errorText } = useI18n();
  const { download } = useApi();

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
  const [showChart, setShowChart] = useState(false);
  const changeWindow = useCallback((next: WindowRange) => {
    setStart(next[0]);
    setEnd(next[1]);
    setWindow((previous) =>
      previous[0] === next[0] && previous[1] === next[1] ? previous : next,
    );
  }, []);
  const evaluation = useQuery({
    placeholderData: keepLocaleData(locale, [
      "task",
      task.session_id,
      locale,
      task.revision,
      "evaluations",
      selection,
    ]),
    queryKey: [
      "task",
      task.session_id,
      locale,
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
    placeholderData: keepLocaleData(locale, [
      "task",
      task.session_id,
      locale,
      task.revision,
      "curves",
      selected?.value,
      signalValue,
      controlValue,
      ...window,
    ]),
    queryKey: [
      "task",
      task.session_id,
      locale,
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
    <Card title={tr("frontend.results.title")}>
      <Space orientation="vertical" style={{ width: "100%" }}>
        <Alert
          title={task.workspace.title}
          description={task.workspace.explanation}
          type="info"
        />
        <Typography.Paragraph>
          <strong>{tr("frontend.results.next_prefix")}</strong>
          {task.workspace.actionable
            ? tr("frontend.results.next_action")
            : task.status === "performance_met"
              ? tr("frontend.results.next_success")
              : task.status === "capability_gap"
                ? tr("frontend.results.next_gap")
                : task.status === "cancelled"
                  ? tr("frontend.results.next_cancelled")
                  : tr("frontend.results.next_default")}
        </Typography.Paragraph>
        <Space wrap>
          {task.workspace.actionable ? (
            <Button href="#current-action">
              {tr("frontend.results.current_action")}
            </Button>
          ) : (
            <>
              <Button href={download(task.session_id, "bundle")}>
                {tr("frontend.results.export_validation")}
              </Button>
              <Link to="/new">{tr("frontend.results.create_new")}</Link>
            </>
          )}
        </Space>
        {evaluation.error && (
          <Alert type="error" title={errorText(evaluation.error)} />
        )}
        <Select
          aria-label={tr("frontend.results.stage_trial")}
          showSearch={{ optionFilterProp: "label" }}
          style={{ width: "100%" }}
          value={selected?.value}
          placeholder={tr("frontend.results.empty")}
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
            setShowChart(false);
          }}
        />
        {selected && (
          <>
            <Tag>
              {evaluation.data?.selected_stage === "confirmation"
                ? tr("frontend.expert.confirmation")
                : tr("frontend.expert.development")}
            </Tag>
            <Table
              size="small"
              scroll={{ x: 500 }}
              pagination={false}
              rowKey={(_, i) => String(i)}
              dataSource={evaluation.data?.metrics}
              columns={[
                tr("frontend.results.metric"),
                tr("frontend.results.requirement"),
                tr("frontend.results.recorded_value"),
                tr("frontend.results.description"),
              ].map((title, i) => ({
                title,
                render: (_: unknown, row: string[]) => row[i] ?? "",
              }))}
            />
            <Space wrap>
              <Select
                aria-label={tr("frontend.results.output_signal")}
                style={{ minWidth: 140 }}
                value={signalValue}
                options={selected.signals.map((value) => ({
                  value,
                  label: value,
                }))}
                onChange={(value) => {
                  setSignal(value);
                  setShowChart(false);
                }}
              />
              <Select
                aria-label={tr("frontend.results.control_signal")}
                style={{ minWidth: 140 }}
                value={controlValue}
                options={selected.control_signals?.map((value) => ({
                  value,
                  label: value,
                }))}
                onChange={(value) => {
                  setControl(value);
                  setShowChart(false);
                }}
              />
              <InputNumber
                aria-label={tr("frontend.results.window_start")}
                placeholder={tr("frontend.datacurves.start")}
                value={start}
                onChange={setStart}
              />
              <InputNumber
                aria-label={tr("frontend.results.window_end")}
                placeholder={tr("frontend.datacurves.end")}
                value={end}
                onChange={setEnd}
              />
              <Button
                disabled={start !== null && end !== null && start >= end}
                onClick={() => setWindow([start, end])}
              >
                {tr("frontend.results.apply_window")}
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
                {tr("frontend.results.full_window")}
              </Button>
            </Space>
            {curve.error && (
              <Alert type="error" title={errorText(curve.error)} />
            )}{" "}
            {curve.data && (
              <>
                <Typography.Text type="secondary">
                  {tr("frontend.results.original_prefix")}
                  {curve.data.original_points}{" "}
                  {tr("frontend.datacurves.displayed_prefix")}{" "}
                  {curve.data.display_points}{" "}
                  {tr("frontend.datacurves.revision_prefix")}
                  {curve.data.revision}
                </Typography.Text>
                <Button onClick={() => setShowChart(true)}>
                  {tr("frontend.results.view_curves")}
                </Button>
                {showChart && (
                  <Suspense fallback={<Spin />}>
                    <Charts
                      curve={curve.data}
                      identity={JSON.stringify([
                        task.session_id,
                        task.revision,
                        selected.value,
                        signalValue,
                        controlValue,
                      ])}
                      window={window}
                      onWindowChange={changeWindow}
                    />
                  </Suspense>
                )}
              </>
            )}
          </>
        )}
      </Space>
    </Card>
  );
}
