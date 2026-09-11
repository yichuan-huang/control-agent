import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import { existsSync, readFileSync } from "node:fs";
import { dirname, extname, join } from "node:path";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const antdLayerCache = new Map<string, number>();
const resolvingAntdModules = new Set<string>();
const staticImportExpression =
  /\b(?:import|export)\s+(?:(?:[^"']|["'][^"']*["'])*?\s+from\s+)?["']([^"']+)["']/g;

function isAntdModule(id: string) {
  return (
    id.includes("/node_modules/antd/") ||
    id.includes("/node_modules/@ant-design/") ||
    id.includes("/node_modules/@rc-component/")
  );
}

function packageSpecifier(specifier: string) {
  const parts = specifier.split("/");
  if (specifier.startsWith("@")) {
    if (parts.length < 2) return undefined;
    return { name: parts.slice(0, 2).join("/"), subpath: parts.slice(2) };
  }
  return { name: parts[0], subpath: parts.slice(1) };
}

function resolveModulePath(path: string) {
  for (const candidate of [path, `${path}.js`, join(path, "index.js")]) {
    if (existsSync(candidate)) return candidate;
  }
  return undefined;
}

function resolveImport(id: string, specifier: string) {
  try {
    const parsed = packageSpecifier(specifier);
    if (
      parsed &&
      ["antd", "@ant-design", "@rc-component"].some(
        (name) => parsed.name === name || parsed.name.startsWith(`${name}/`),
      )
    ) {
      const packageJsonPath = require.resolve(`${parsed.name}/package.json`, {
        paths: [dirname(id)],
      });
      const packageRoot = dirname(packageJsonPath);
      if (parsed.subpath.length) {
        return resolveModulePath(join(packageRoot, ...parsed.subpath));
      }
      const packageJson = JSON.parse(readFileSync(packageJsonPath, "utf8")) as {
        module?: string;
      };
      return packageJson.module
        ? resolveModulePath(join(packageRoot, packageJson.module))
        : undefined;
    }
    return require.resolve(specifier, { paths: [dirname(id)] });
  } catch {
    return undefined;
  }
}

function antdLayer(id: string): number {
  const cached = antdLayerCache.get(id);
  if (cached !== undefined) return cached;
  if (resolvingAntdModules.has(id)) return 0;

  resolvingAntdModules.add(id);
  let layer = 0;
  if (existsSync(id) && extname(id) === ".js") {
    const source = readFileSync(id, "utf8");
    for (const match of source.matchAll(staticImportExpression)) {
      const dependency = resolveImport(id, match[1]);
      if (dependency && isAntdModule(dependency)) {
        layer = Math.max(layer, antdLayer(dependency) + 1);
      }
    }
  }
  resolvingAntdModules.delete(id);
  antdLayerCache.set(id, layer);
  return layer;
}

function manualChunks(id: string) {
  if (!id.includes("/node_modules/")) return undefined;
  if (id.includes("/plotly.js-basic-dist-min/")) return "plotly";
  if (
    id.includes("/react-dom/") ||
    id.includes("/react/") ||
    id.includes("/scheduler/")
  ) {
    return "react";
  }
  if (id.includes("/react-router/") || id.includes("/react-router-dom/")) {
    return "router";
  }
  if (
    id.includes("/react-markdown/") ||
    id.includes("/remark-") ||
    id.includes("/rehype-") ||
    id.includes("/unified/") ||
    id.includes("/micromark") ||
    id.includes("/mdast-") ||
    id.includes("/hast-") ||
    id.includes("/vfile")
  ) {
    return "markdown";
  }
  if (isAntdModule(id)) {
    const layer = antdLayer(id);
    if (layer <= 3) return "antd-primitives";
    if (layer <= 9) return "antd-core";
    if (layer <= 16) return "antd-foundation";
    return "antd-components";
  }
  return "vendor";
}

export default defineConfig({
  plugins: [react()],
  build: {
    chunkSizeWarningLimit: 1250,
    rollupOptions: {
      output: { manualChunks, onlyExplicitManualChunks: true },
    },
  },
  server: {
    proxy: { "/api": { target: "http://127.0.0.1:7860", changeOrigin: true } },
  },
  test: {
    environment: "jsdom",
    include: ["src/**/*.test.ts", "src/**/*.test.tsx"],
  },
});
