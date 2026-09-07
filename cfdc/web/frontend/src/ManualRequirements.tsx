import { Typography } from "antd";
import type { Obj } from "./api/types";
const object = (value: unknown): Obj =>
  value && typeof value === "object" && !Array.isArray(value)
    ? (value as Obj)
    : {};
export default function ManualRequirements({ value }: { value?: Obj }) {
  if (!value) return null;
  const files = Array.isArray(value.files) ? value.files.map(object) : [];
  return (
    <>
      {typeof value.file_count === "number" && (
        <Typography.Paragraph
          strong
        >{`本轮需回传 ${value.file_count} 个试次文件`}</Typography.Paragraph>
      )}
      {!!value.expected_format && (
        <Typography.Paragraph>
          数据格式：{String(value.expected_format)}
          {typeof value.repeats === "number"
            ? `；协议重复次数：${value.repeats}`
            : ""}
          。请保持请求包指定的文件名、列名和单位。
        </Typography.Paragraph>
      )}
      {!!files.length && (
        <div style={{ maxHeight: 240, overflow: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th style={{ textAlign: "left", padding: 8 }}>结果文件名</th>
                <th style={{ textAlign: "left", padding: 8 }}>
                  所需数据列与单位
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
