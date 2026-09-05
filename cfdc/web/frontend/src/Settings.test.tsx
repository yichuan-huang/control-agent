import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import "@testing-library/jest-dom/vitest";
import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import Settings from "./Settings";
import { SettingsProvider } from "./context";

const getComputedStyle = window.getComputedStyle.bind(window);
const config = (base_url = "", model = "") => ({
  base_url,
  model,
  rag: { status: "ready", message: "ready" },
  version: "0.3.4",
});

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

beforeEach(() => {
  vi.spyOn(window, "getComputedStyle").mockImplementation((element) =>
    getComputedStyle(element),
  );
  Object.defineProperty(window, "matchMedia", {
    writable: true,
    value: vi.fn().mockImplementation((query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  });
});

function json(body: unknown, status = 200) {
  return Promise.resolve(
    new Response(JSON.stringify(body), {
      status,
      headers: { "Content-Type": "application/json" },
    }),
  );
}

function setup(fetcher: typeof fetch) {
  vi.spyOn(globalThis, "fetch").mockImplementation(fetcher);
  render(
    <QueryClientProvider
      client={
        new QueryClient({ defaultOptions: { queries: { retry: false } } })
      }
    >
      <SettingsProvider>
        <Settings open onClose={() => {}} />
      </SettingsProvider>
    </QueryClientProvider>,
  );
}

async function enterCurrentCredentials() {
  await screen.findByText("知识库：已就绪");
  fireEvent.change(screen.getByLabelText("Base URL"), {
    target: { value: "https://current.example/v1" },
  });
  fireEvent.change(screen.getByLabelText("Model"), {
    target: { value: "current-model" },
  });
  fireEvent.change(screen.getByLabelText("API Key"), {
    target: { value: "current-secret" },
  });
}

test.each([
  {
    name: "applies a complete environment config",
    next: config("https://environment.example/v1", "environment-model"),
    base: "https://environment.example/v1",
    model: "environment-model",
    message: "已应用环境中的 Base URL 和 Model。",
    type: "success",
  },
  {
    name: "applies only the nonempty environment field",
    next: config("https://environment.example/v1", ""),
    base: "https://environment.example/v1",
    model: "current-model",
    message: "环境未提供 Model，已保留当前值。",
    type: "warning",
  },
  {
    name: "retains current fields when the environment has neither field",
    next: config(),
    base: "https://current.example/v1",
    model: "current-model",
    message: "启动环境没有预设地址和模型，表单内容未更改。",
    type: "info",
  },
])(
  "$name and always retains the API key",
  async ({ next, base, model, message, type }) => {
    let reads = 0;
    setup(async () => json(reads++ === 0 ? config() : next));
    await enterCurrentCredentials();

    fireEvent.click(screen.getByRole("button", { name: "高级设置" }));
    fireEvent.click(
      screen.getByRole("button", { name: "从启动环境导入地址和模型" }),
    );

    expect(await screen.findByText(message)).toBeInTheDocument();
    expect(screen.getByLabelText("Base URL")).toHaveValue(base);
    expect(screen.getByLabelText("Model")).toHaveValue(model);
    expect(screen.getByLabelText("API Key")).toHaveValue("current-secret");
    expect(screen.getByText(message).closest(".ant-alert")).toHaveClass(
      `ant-alert-${type}`,
    );
    expect(reads).toBe(2);
  },
);

test("retains every current credential when refreshing environment config fails", async () => {
  let reads = 0;
  setup(async () => {
    if (reads++ === 0) return json(config());
    throw new TypeError("offline");
  });
  await enterCurrentCredentials();

  fireEvent.click(screen.getByRole("button", { name: "高级设置" }));
  fireEvent.click(
    screen.getByRole("button", { name: "从启动环境导入地址和模型" }),
  );

  expect(
    await screen.findByText("读取环境配置失败，已保留当前值。"),
  ).toBeInTheDocument();
  expect(screen.getByLabelText("Base URL")).toHaveValue(
    "https://current.example/v1",
  );
  expect(screen.getByLabelText("Model")).toHaveValue("current-model");
  expect(screen.getByLabelText("API Key")).toHaveValue("current-secret");
});

test.each([
  [true, "已连接：服务与模型可用。"],
  [false, "未连接：找不到模型。"],
])(
  "clears probe connected=%s after applying different environment credentials",
  async (connected, message) => {
    setup(async (input, init) => {
      if (String(input).endsWith("/config/probe"))
        return json({
          connected,
          message: connected ? "服务与模型可用。" : "找不到模型。",
        });
      if (init?.method === "POST") throw new Error("unexpected POST");
      return json(
        config("https://environment.example/v1", "environment-model"),
      );
    });
    await enterCurrentCredentials();

    fireEvent.click(screen.getByRole("button", { name: "测试当前配置" }));
    expect(await screen.findByText(message)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "高级设置" }));
    fireEvent.click(
      screen.getByRole("button", { name: "从启动环境导入地址和模型" }),
    );

    expect(
      await screen.findByText("已应用环境中的 Base URL 和 Model。"),
    ).toBeInTheDocument();
    expect(screen.queryByText(message)).toBeNull();
  },
);

test("shows doctor request failure, clears stale checks, and retains credentials", async () => {
  let doctorCalls = 0;
  setup(async (input) => {
    if (String(input).endsWith("/config/doctor")) {
      doctorCalls += 1;
      if (doctorCalls === 1)
        return json({
          checks: [{ name: "model", status: "ok", message: "模型可用" }],
        });
      throw new TypeError("doctor offline");
    }
    return json(config());
  });
  await enterCurrentCredentials();
  fireEvent.click(screen.getByRole("button", { name: "环境检查" }));
  expect(await screen.findByText("模型可用")).toBeInTheDocument();
  await waitFor(() =>
    expect(screen.getByRole("button", { name: "环境检查" })).not.toBeDisabled(),
  );

  fireEvent.click(screen.getByRole("button", { name: "环境检查" }));

  expect(
    await screen.findByText("环境检查失败：TypeError: doctor offline"),
  ).toBeInTheDocument();
  expect(screen.queryByText("模型可用")).toBeNull();
  expect(screen.getByLabelText("Base URL")).toHaveValue(
    "https://current.example/v1",
  );
  expect(screen.getByLabelText("Model")).toHaveValue("current-model");
  expect(screen.getByLabelText("API Key")).toHaveValue("current-secret");
});

test("editing credentials clears a stale probe result", async () => {
  setup(async (input) =>
    String(input).endsWith("/config/probe")
      ? json({ connected: false, message: "找不到模型。" })
      : json(config()),
  );
  await enterCurrentCredentials();
  fireEvent.click(screen.getByRole("button", { name: "测试当前配置" }));
  expect(await screen.findByText("未连接：找不到模型。")).toBeInTheDocument();

  fireEvent.change(screen.getByLabelText("Model"), {
    target: { value: "corrected-model" },
  });

  await waitFor(() =>
    expect(screen.queryByText("未连接：找不到模型。")).toBeNull(),
  );
});

test.each([
  config(),
  config("https://environment.example/v1", "environment-model"),
])(
  "tests handwritten credentials without importing startup configuration (%j)",
  async (environment) => {
    const requests: unknown[] = [];
    setup(async (input, init) => {
      if (String(input).endsWith("/config/probe")) {
        requests.push(JSON.parse(String(init?.body)));
        return json({ connected: true, message: "服务与模型可用。" });
      }
      return json(environment);
    });
    await enterCurrentCredentials();
    expect(
      screen.queryByRole("button", { name: "从启动环境导入地址和模型" }),
    ).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "测试当前配置" }));
    expect(await screen.findByText("已连接：服务与模型可用。")).toBeVisible();
    expect(requests).toEqual([
      {
        credentials: {
          base_url: "https://current.example/v1",
          model: "current-model",
          api_key: "current-secret",
        },
      },
    ]);
    expect(screen.queryByText(/环境未提供/)).toBeNull();
  },
);

test.each([
  ["Base URL", "base_url"],
  ["Model", "model"],
  ["API Key", "api_key"],
])(
  "focuses missing %s and does not submit invalid credentials",
  async (label) => {
    let submissions = 0;
    setup(async (_input, init) => {
      if (init?.method === "POST") submissions++;
      return json(config());
    });
    await enterCurrentCredentials();
    fireEvent.change(screen.getByLabelText(label), { target: { value: " " } });
    fireEvent.click(screen.getByRole("button", { name: "测试当前配置" }));
    expect(await screen.findByText(`请填写 ${label}。`)).toBeVisible();
    expect(screen.getByLabelText(label)).toHaveFocus();
    expect(submissions).toBe(0);
  },
);

test.each(["same", "empty", "failed"])(
  "retains connection after %s environment import",
  async (kind) => {
    let reads = 0;
    setup(async (input) => {
      if (String(input).endsWith("/config/probe"))
        return json({ connected: true, message: "服务与模型可用。" });
      if (reads++ === 0) return json(config());
      if (kind === "failed") throw new TypeError("offline");
      return json(
        kind === "same"
          ? config("https://current.example/v1", "current-model")
          : config(),
      );
    });
    await enterCurrentCredentials();
    fireEvent.click(screen.getByRole("button", { name: "测试当前配置" }));
    expect(await screen.findByText("已连接：服务与模型可用。")).toBeVisible();
    fireEvent.click(screen.getByRole("button", { name: "高级设置" }));
    fireEvent.click(
      screen.getByRole("button", { name: "从启动环境导入地址和模型" }),
    );
    await screen.findByText(
      kind === "same"
        ? "已应用环境中的 Base URL 和 Model。"
        : kind === "empty"
          ? "启动环境没有预设地址和模型，表单内容未更改。"
          : "读取环境配置失败，已保留当前值。",
    );
    expect(screen.getByText("已连接：服务与模型可用。")).toBeVisible();
    expect(screen.getByLabelText("API Key")).toHaveValue("current-secret");
  },
);

test("disables duplicate probes and retains credentials after request failure", async () => {
  let rejectProbe: (error: Error) => void = () => {};
  let submissions = 0;
  setup(async (input) => {
    if (String(input).endsWith("/config/probe")) {
      submissions++;
      return new Promise<Response>((_resolve, reject) => {
        rejectProbe = reject;
      });
    }
    return json(config());
  });
  await enterCurrentCredentials();
  const button = screen.getByRole("button", { name: "测试当前配置" });
  fireEvent.click(button);
  expect(button).toBeDisabled();
  fireEvent.click(button);
  expect(submissions).toBe(1);
  rejectProbe(new TypeError("offline"));
  expect(
    await screen.findByText("连接测试失败：TypeError: offline"),
  ).toBeVisible();
  expect(screen.getByLabelText("API Key")).toHaveValue("current-secret");
  expect(button).not.toBeDisabled();
});
