import { Alert, Descriptions, Space, Typography } from "antd";
import type { Obj } from "./api/types";

const object = (value: unknown): Obj =>
  value && typeof value === "object" && !Array.isArray(value)
    ? (value as Obj)
    : {};

export default function WorkflowGuide({ value }: { value?: Obj }) {
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
            label: "本步目的",
            children: String(value.purpose ?? ""),
          },
          {
            key: "actor",
            label: "由谁完成",
            children: String(value.actor ?? ""),
          },
        ]}
      />
      {steps.length > 0 && (
        <ol>
          {steps.map((step, index) => (
            <li key={index}>
              <Typography.Text strong>
                {String(step.title ?? `步骤 ${index + 1}`)}
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
          title="完成后进入"
          description={String(value.next_step)}
          type="info"
        />
      )}
    </Space>
  );
}
