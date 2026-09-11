import { readdir, stat } from "node:fs/promises";
import { resolve } from "node:path";

const STANDARD_LIMIT_BYTES = 500_000;
const PLOTLY_LIMIT_BYTES = 1_250_000;
const assets = resolve(process.argv[2] ?? "dist", "assets");
const files = (await readdir(assets)).filter((file) => file.endsWith(".js"));
const plotly = files.filter((file) => /^plotly-[\w-]+\.js$/.test(file));

if (plotly.length !== 1) {
  throw new Error(
    `expected exactly one plotly chunk, found: ${plotly.join(", ") || "none"}`,
  );
}

const violations = [];
for (const file of files) {
  const bytes = (await stat(resolve(assets, file))).size;
  const limit = plotly.includes(file)
    ? PLOTLY_LIMIT_BYTES
    : STANDARD_LIMIT_BYTES;
  if (bytes > limit)
    violations.push(`${file}: ${bytes} bytes exceeds ${limit}`);
}

if (violations.length)
  throw new Error(`bundle budget exceeded\n${violations.join("\n")}`);
console.log(
  `Bundle budget passed: ${files.length} JS chunks; ${plotly[0]} <= ${PLOTLY_LIMIT_BYTES} bytes; all others <= ${STANDARD_LIMIT_BYTES} bytes.`,
);
