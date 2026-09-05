import ReactMarkdown from "react-markdown";
/** No raw-HTML plugin: untrusted report prose stays text and safe Markdown. */
export default function Markdown({ children }: { children: string }) {
  return (
    <div className="report-prose">
      <ReactMarkdown>{children}</ReactMarkdown>
    </div>
  );
}
