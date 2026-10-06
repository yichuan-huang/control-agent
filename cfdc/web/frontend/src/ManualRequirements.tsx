import { useI18n } from "./i18n";
import { Typography } from "antd";
import type { Obj } from "./api/types";
const object = (value: unknown): Obj =>
  value && typeof value === "object" && !Array.isArray(value)
    ? (value as Obj)
    : {};
export default function ManualRequirements({ value }: { value?: Obj }) {
  const { t: tr } = useI18n();

  if (!value) return null;
  const files = Array.isArray(value.files) ? value.files.map(object) : [];
  return (
    <>
      {typeof value.file_count === "number" && (
        <Typography.Paragraph strong>
          {tr("frontend.manualrequirements.file_count", {
            count: value.file_count,
          })}
        </Typography.Paragraph>
      )}
      {!!value.expected_format && (
        <Typography.Paragraph>
          {tr("frontend.manualrequirements.format_prefix")}
          {String(value.expected_format)}
          {typeof value.repeats === "number"
            ? tr("frontend.manualrequirements.repeats", {
                count: value.repeats,
              })
            : ""}
          {tr("frontend.manualrequirements.format_help")}
        </Typography.Paragraph>
      )}
      {!!files.length && (
        <div style={{ maxHeight: 240, overflow: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th style={{ textAlign: "left", padding: 8 }}>
                  {tr("frontend.manualrequirements.filename")}
                </th>
                <th style={{ textAlign: "left", padding: 8 }}>
                  {tr("frontend.manualrequirements.columns")}
                </th>
              </tr>
            </thead>
            <tbody>
              {files.map((row, index) => (
                <tr key={String(row.filename ?? index)}>
                  <td style={{ padding: 8, borderTop: "1px solid #eee" }}>
                    {String(row.filename ?? "")}
                  </td>
                  <td style={{ padding: 8, borderTop: "1px solid #eee" }}>
                    {(Array.isArray(row.columns) ? row.columns : [])
                      .map((column) => {
                        const item = object(column);
                        return `${String(item.name ?? column)}${item.unit ? ` (${String(item.unit)})` : ""}`;
                      })
                      .join("；")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
