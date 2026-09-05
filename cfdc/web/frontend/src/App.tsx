import { lazy, Suspense, useState } from "react";
import {
  Link,
  Route,
  Routes,
  useLocation,
  useNavigate,
} from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  Button,
  Modal,
  Input,
  Card,
  ConfigProvider,
  Empty,
  Space,
  Segmented,
  Spin,
  Tag,
  Typography,
} from "antd";
import zhCN from "antd/locale/zh_CN";
import { api } from "./api/client";
import type { DTO, Config } from "./api/types";
import Wizard from "./Wizard";
import Workspace from "./Workspace";
import Settings from "./Settings";
import { useSettings, ragLabel } from "./context";
const Expert = lazy(() => import("./Expert"));
function Home() {
  const navigate = useNavigate();
  const { connection } = useSettings();
  const config = useQuery({
    queryKey: ["config"],
    queryFn: () => api<Config>("/config"),
    refetchInterval: (q) =>
      q.state.data?.rag.status === "preparing" ? 2000 : false,
  });
  const last = sessionStorage.getItem("cfdc:last-task");
  return (
    <>
      <section className="hero">
        <Tag color="blue">CFDC · EVIDENCE-DRIVEN CONTROL</Tag>
        <Typography.Title>把控制目标，变成可验证的结果。</Typography.Title>
        <Typography.Paragraph>
          从任务边界开始，通过证据形成方案，再以独立试验核对结果。每一步都有记录。
        </Typography.Paragraph>
      </section>
      <div className="entry-grid">
        <Card title="我的设备与数据">
          <Typography.Paragraph>
            定义目标、测量信号和软件试验边界，逐步补全已知信息。
          </Typography.Paragraph>
          <Button type="primary" size="large" onClick={() => navigate("/new")}>
            创建我的任务
          </Button>
        </Card>
        <Card title="体验内置案例">
          <Typography.Paragraph>
            从加热器或电机案例开始，查看证据、控制器和评价如何衔接。
          </Typography.Paragraph>
          <Button
            type="primary"
            size="large"
            onClick={() => navigate("/cases")}
          >
            从案例开始
          </Button>
        </Card>
      </div>
      <Space wrap style={{ marginTop: 24 }}>
        <Tag>模型：{connection}</Tag>
        <Tag>知识库：{ragLabel(config.data?.rag.status)}</Tag>
      </Space>
      {last && (
        <Button
          style={{ marginTop: 24 }}
          onClick={() => navigate(`/tasks/${last}`)}
        >
          继续上次任务
        </Button>
      )}
    </>
  );
}
function Cases() {
  const [category, setCategory] = useState("engineering");
  const navigate = useNavigate();
  const q = useQuery({
    queryKey: ["cases"],
    queryFn: () => api<DTO<"CaseList">>("/cases"),
  });
  return (
    <>
      <Typography.Title level={2}>选择一个案例</Typography.Title>
      <Typography.Paragraph>
        工程案例展示完整流程；审计案例用于理解边界与拒绝原因。
      </Typography.Paragraph>
      <Segmented
        aria-label="案例分类"
        value={category}
        onChange={setCategory}
        options={[
          { value: "engineering", label: "工程案例" },
          { value: "audit", label: "审计案例" },
        ]}
        style={{ marginBottom: 24 }}
      />
      {q.isLoading ? (
        <Spin />
      ) : q.error ? (
        <Empty description={String(q.error)} />
      ) : (
        <div className="entry-grid">
          {q.data?.items
            .filter((c) => c.category === category)
            .map((c) => (
              <Card
                key={c.id}
                title={c.title}
                extra={
                  <Tag>
                    {c.category === "engineering" ? "工程案例" : "审计案例"}
                  </Tag>
                }
              >
                <Typography.Paragraph>{c.description}</Typography.Paragraph>
                <Typography.Paragraph type="secondary">
                  {c.data_source}
                </Typography.Paragraph>
                <Button
                  data-testid="case-open"
                  onClick={() =>
                    navigate(`/new?case=${encodeURIComponent(c.id)}`)
                  }
                >
                  查看并使用案例
                </Button>
              </Card>
            ))}
        </div>
      )}
    </>
  );
}
export default function App() {
  const location = useLocation();
  const navigate = useNavigate();
  const [openTask, setOpenTask] = useState(false);
  const [taskId, setTaskId] = useState("");
  const [settings, setSettings] = useState(false);
  const [expert, setExpert] = useState(
    () =>
      location.pathname !== "/new" &&
      !!sessionStorage.getItem(
        `cfdc:operation:entry:${location.pathname}${location.search}`,
      ),
  );
  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        token: {
          colorPrimary: "#176a73",
          borderRadius: 10,
          fontFamily:
            'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
        },
        components: { Button: { controlHeight: 38 }, Card: { paddingLG: 24 } },
      }}
    >
      <header className="topbar">
        <Link className="brand" to="/">
          CFDC <span>控制任务工作台</span>
        </Link>
        <Space wrap>
          <Link to="/new">新建任务</Link>
          <Button type="text" onClick={() => setOpenTask(true)}>
            打开任务
          </Button>
          <Link to="/cases">案例</Link>
          <Button type="text" onClick={() => setExpert(true)}>
            导入 / 专家
          </Button>
          <Button aria-label="设置" onClick={() => setSettings(true)}>
            设置
          </Button>
        </Space>
      </header>
      <div className="page">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/cases" element={<Cases />} />
          <Route path="/new" element={<Wizard key={location.search} />} />
          <Route path="/tasks/:id" element={<Workspace />} />
          <Route
            path="*"
            element={
              <Empty description="页面不存在">
                <Link to="/">返回首页</Link>
              </Empty>
            }
          />
        </Routes>
      </div>
      <footer>CFDC Kernel · 可追溯的证据与软件评价</footer>
      <Modal
        title="打开任务"
        open={openTask}
        onCancel={() => setOpenTask(false)}
        okText="打开"
        okButtonProps={{ disabled: !taskId.trim() }}
        onOk={() => {
          navigate(`/tasks/${encodeURIComponent(taskId.trim())}`);
          setOpenTask(false);
        }}
      >
        <Input
          aria-label="任务 ID"
          placeholder="输入任务 ID"
          value={taskId}
          onChange={(e) => setTaskId(e.target.value)}
          onPressEnter={() => {
            if (taskId.trim()) {
              navigate(`/tasks/${encodeURIComponent(taskId.trim())}`);
              setOpenTask(false);
            }
          }}
        />
      </Modal>
      <Settings open={settings} onClose={() => setSettings(false)} />
      {expert && (
        <Suspense fallback={<Spin />}>
          <Expert key={location.key} onClose={() => setExpert(false)} />
        </Suspense>
      )}
    </ConfigProvider>
  );
}
