import { StrictMode, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "sonner";
import { queryClient } from "./lib/query-client.ts";
import { useAuthStore } from "./store/auth-store.ts";
import App from "./App.tsx";
import "./index.css";

const root = createRoot(document.getElementById("root")!);

function LoadingScreen() {
  return (
    <div className="flex h-screen w-screen items-center justify-center bg-background">
      <div className="flex flex-col items-center gap-3">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        <p className="text-sm text-muted-foreground">Loading...</p>
      </div>
    </div>
  );
}

function Root() {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    useAuthStore.getState().initialize().then(() => {
      setReady(true);
    });
  }, []);

  if (!ready) {
    return <LoadingScreen />;
  }

  return (
    <StrictMode>
      <QueryClientProvider client={queryClient}>
        <App />
        <Toaster
          position="top-right"
          richColors
          closeButton
          toastOptions={{
            style: {
              fontFamily: "inherit",
            },
          }}
        />
      </QueryClientProvider>
    </StrictMode>
  );
}

root.render(<Root />);
