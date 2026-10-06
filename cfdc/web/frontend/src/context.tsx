import { createTranslator, type Translator } from "./i18n";
import { createContext, useContext, useState, type ReactNode } from "react";
import type { Credentials } from "./api/types";
const Context = createContext<{
  credentials: Credentials;
  setCredentials: (v: Credentials) => void;
  useRag: boolean;
  setUseRag: (v: boolean) => void;
  connection: string;
  setConnection: (v: string) => void;
}>({
  credentials: { base_url: "", model: "", api_key: "" },
  setCredentials: () => {},
  useRag: true,
  setUseRag: () => {},
  connection: "unchecked",
  setConnection: () => {},
});
export function SettingsProvider({ children }: { children: ReactNode }) {
  const [credentials, updateCredentials] = useState<Credentials>({
    base_url: "",
    model: "",
    api_key: "",
  });
  const [useRag, setUseRag] = useState(true);
  const [connection, setConnection] = useState("unchecked");
  function setCredentials(v: Credentials) {
    updateCredentials(v);
    setConnection("unchecked");
  }
  return (
    <Context.Provider
      value={{
        credentials,
        setCredentials,
        useRag,
        setUseRag,
        connection,
        setConnection,
      }}
    >
      {children}
    </Context.Provider>
  );
}
export const useSettings = () => useContext(Context);
export const ragLabel = (
  status?: string,
  tr: Translator = createTranslator("zh-CN"),
) =>
  ({
    ready: tr("frontend.context.ready"),
    preparing: tr("frontend.context.preparing"),
    error: tr("frontend.context.failed"),
  })[status ?? ""] ?? tr("frontend.context.loading");
export const connectionLabel = (status: string, tr: Translator) =>
  ({
    unchecked: tr("frontend.context.unchecked"),
    checking: tr("frontend.settings.checking"),
    connected: tr("frontend.settings.connected"),
    failed: tr("frontend.settings.connection_failed"),
  })[status] ?? status;
