import { useI18n } from "./i18n";
import { Alert, Descriptions, Space, Typography } from "antd";
import type { Obj } from "./api/types";

const object = (value: unknown): Obj =>
  value && typeof value === "object" && !Array.isArray(value)
    ? (value as Obj)
    : {};

export default function WorkflowGuide({ value }: { value?: Obj }) {
  const { t: tr } = useI18n();

  if (!value) return null;
  const steps = Array.isArray(value.steps) ? value.steps.map(object) : [];
  return (
    <Space orientation="vertical" style={{ width: "100%" }}>
      {!!value.title && (
        <Typography.Title level={4}>{String(value.title)}</Typography.Title>
      )}
      <Descriptions
        size="small"
        column={1}
        items={[
          {
            key: "purpose",
            label: tr("frontend.workflowguide.purpose"),
            children: String(value.purpose ?? ""),
          },
          {
            key: "actor",
            label: tr("frontend.workflowguide.actor"),
            children: String(value.actor ?? ""),
          },
        ]}
      />
      {steps.length > 0 && (
        <ol>
          {steps.map((step, index) => (
            <li key={index}>
              <Typography.Text strong>
                {String(
                  step.title ??
                    tr("frontend.workflowguide.step_number", {
                      number: index + 1,
                    }),
                )}
              </Typography.Text>
              <Typography.Paragraph className="preserve">
                {String(step.description ?? "")}
              </Typography.Paragraph>
            </li>
          ))}
        </ol>
      )}
      {!!value.next_step && (
        <Alert
          title={tr("frontend.workflowguide.next_stage")}
          description={String(value.next_step)}
          type="info"
        />
      )}
    </Space>
  );
}
