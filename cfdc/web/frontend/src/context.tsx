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
  connection: "未检测",
  setConnection: () => {},
});
export function SettingsProvider({ children }: { children: ReactNode }) {
  const [credentials, updateCredentials] = useState<Credentials>({
    base_url: "",
    model: "",
    api_key: "",
  });
  const [useRag, setUseRag] = useState(true);
  const [connection, setConnection] = useState("未检测");
  function setCredentials(v: Credentials) {
    updateCredentials(v);
    setConnection("未检测");
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
export const ragLabel = (status?: string) =>
  ({ ready: "已就绪", preparing: "准备中", error: "失败" })[status ?? ""] ??
  "读取中";
