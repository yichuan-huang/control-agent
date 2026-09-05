import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import App from "./App";
import { SettingsProvider } from "./context";
import "./style.css";
const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, staleTime: 1000 },
    mutations: { retry: false },
  },
});
createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <SettingsProvider>
          <App />
        </SettingsProvider>
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>,
);
