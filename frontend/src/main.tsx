import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "@/lib/query-client";
import { useAuthStore } from "@/store/auth-store";
import App from "./App";
import "./index.css";

const root = createRoot(document.getElementById("root")!);

// Initialize auth state from localStorage
useAuthStore.getState().initialize();

root.render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </StrictMode>
);
