import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ProtectedRoute } from "./components/layout/protected-route.tsx";
import { AppShell } from "./components/layout/app-shell.tsx";
import { LoginPage } from "./pages/login-page.tsx";
import { RegisterPage } from "./pages/register-page.tsx";
import { DashboardPage } from "./pages/dashboard-page.tsx";
import LogsPage from "./pages/logs-page.tsx";
import { AlertsPage } from "./pages/alerts-page.tsx";
import { SettingsPage } from "./pages/settings-page.tsx";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <AppShell>
                <Routes>
                  <Route
                    path="/"
                    element={<Navigate to="/dashboard" replace />}
                  />
                  <Route path="/dashboard" element={<DashboardPage />} />
                  <Route path="/logs" element={<LogsPage />} />
                  <Route path="/alerts" element={<AlertsPage />} />
                  <Route path="/settings" element={<SettingsPage />} />
                </Routes>
              </AppShell>
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
