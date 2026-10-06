import { keepLocaleData, useI18n } from "./i18n";
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
import enUS from "antd/locale/en_US";
import { useApi } from "./api/client";
import type { DTO, Config } from "./api/types";
import Wizard from "./Wizard";
import Workspace from "./Workspace";
import Settings from "./Settings";
import { useSettings, ragLabel, connectionLabel } from "./context";
const Expert = lazy(() => import("./Expert"));
function Home() {
  const { t: tr, locale } = useI18n();
  const { api } = useApi();

  const navigate = useNavigate();
  const { connection } = useSettings();
  const config = useQuery({
    placeholderData: keepLocaleData(locale, ["config", locale]),
    queryKey: ["config", locale],
    queryFn: () => api<Config>("/config"),
    refetchInterval: (q) =>
      q.state.data?.rag.status === "preparing" ? 2000 : false,
  });
  const last = sessionStorage.getItem("cfdc:last-task");
  return (
    <>
      <section className="hero">
        <Tag color="blue">CFDC · EVIDENCE-DRIVEN CONTROL</Tag>
        <Typography.Title>{tr("frontend.app.hero_title")}</Typography.Title>
        <Typography.Paragraph>
          {tr("frontend.app.hero_description")}
        </Typography.Paragraph>
      </section>
      <div className="entry-grid">
        <Card title={tr("frontend.app.my_equipment")}>
          <Typography.Paragraph>
            {tr("frontend.app.my_equipment_help")}
          </Typography.Paragraph>
          <Button type="primary" size="large" onClick={() => navigate("/new")}>
            {tr("frontend.app.create_task")}
          </Button>
        </Card>
        <Card title={tr("frontend.app.built_in_cases")}>
          <Typography.Paragraph>
            {tr("frontend.app.built_in_cases_help")}
          </Typography.Paragraph>
          <Button
            type="primary"
            size="large"
            onClick={() => navigate("/cases")}
          >
            {tr("frontend.app.start_case")}
          </Button>
        </Card>
      </div>
      <Space wrap style={{ marginTop: 24 }}>
        <Tag>
          {tr("frontend.app.model_prefix")}
          {connectionLabel(connection, tr)}
        </Tag>
        <Tag>
          {tr("frontend.app.knowledge_prefix")}
          {ragLabel(config.data?.rag.status, tr)}
        </Tag>
      </Space>
      {last && (
        <Button
          style={{ marginTop: 24 }}
          onClick={() => navigate(`/tasks/${last}`)}
        >
          {tr("frontend.app.continue_task")}
        </Button>
      )}
    </>
  );
}
function Cases() {
  const { t: tr, locale, errorText } = useI18n();
  const { api } = useApi();

  const [category, setCategory] = useState("engineering");
  const navigate = useNavigate();
  const q = useQuery({
    placeholderData: keepLocaleData(locale, ["cases", locale]),
    queryKey: ["cases", locale],
    queryFn: () => api<DTO<"CaseList">>("/cases"),
  });
  return (
    <>
      <Typography.Title level={2}>
        {tr("frontend.app.choose_case")}
      </Typography.Title>
      <Typography.Paragraph>
        {tr("frontend.app.case_help")}
      </Typography.Paragraph>
      <Segmented
        aria-label={tr("frontend.app.case_category")}
        value={category}
        onChange={setCategory}
        options={[
          { value: "engineering", label: tr("frontend.app.engineering") },
          { value: "audit", label: tr("frontend.app.audit") },
        ]}
        style={{ marginBottom: 24 }}
      />
      {q.isLoading ? (
        <Spin />
      ) : q.error ? (
        <Empty description={errorText(q.error)} />
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
                    {c.category === "engineering"
                      ? tr("frontend.app.engineering")
                      : tr("frontend.app.audit")}
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
                  {tr("frontend.app.use_case")}
                </Button>
              </Card>
            ))}
        </div>
      )}
    </>
  );
}
export default function App() {
  const { t: tr, locale, setLocale } = useI18n();

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
      locale={locale === "zh-CN" ? zhCN : enUS}
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
          CFDC <span>{tr("frontend.app.brand")}</span>
        </Link>
        <Space wrap>
          <Segmented
            aria-label={tr("frontend.app.language")}
            value={locale}
            onChange={(value) => setLocale(value as "en" | "zh-CN")}
            options={[
              { value: "zh-CN", label: "中文" },
              { value: "en", label: "English" },
            ]}
          />
          <Link to="/new">{tr("frontend.app.new_task")}</Link>
          <Button type="text" onClick={() => setOpenTask(true)}>
            {tr("frontend.app.open_task")}
          </Button>
          <Link to="/cases">{tr("frontend.app.cases")}</Link>
          <Button type="text" onClick={() => setExpert(true)}>
            {tr("frontend.app.import_expert")}
          </Button>
          <Button
            aria-label={tr("frontend.app.settings")}
            onClick={() => setSettings(true)}
          >
            {tr("frontend.app.settings")}
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
              <Empty description={tr("frontend.app.not_found")}>
                <Link to="/">{tr("frontend.app.home")}</Link>
              </Empty>
            }
          />
        </Routes>
      </div>
      <footer>{tr("frontend.app.footer")}</footer>
      <Modal
        title={tr("frontend.app.open_task")}
        open={openTask}
        onCancel={() => setOpenTask(false)}
        okText={tr("frontend.app.open")}
        okButtonProps={{ disabled: !taskId.trim() }}
        onOk={() => {
          navigate(`/tasks/${encodeURIComponent(taskId.trim())}`);
          setOpenTask(false);
        }}
      >
        <Input
          aria-label={tr("frontend.app.task_id")}
          placeholder={tr("frontend.app.task_id_placeholder")}
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
