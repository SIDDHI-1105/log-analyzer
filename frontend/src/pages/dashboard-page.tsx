import { useQuery } from "@tanstack/react-query";
import { ScrollText, Bell, AlertTriangle, Activity } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { getLogs } from "@/services/logs";
import { getAlertRules } from "@/services/alerts";

export function DashboardPage() {
  const { data: logs, isLoading: logsLoading } = useQuery({
    queryKey: ["logs", "recent"],
    queryFn: () => getLogs({ skip: 0, limit: 10 }),
  });

  const { data: alertRules, isLoading: alertsLoading } = useQuery({
    queryKey: ["alert-rules"],
    queryFn: getAlertRules,
  });

  const logItems = logs?.items ?? [];
  const errorLogs = logItems.filter(
    (log) => log.level === "ERROR" || log.level === "CRITICAL",
  );
  const activeAlerts = alertRules?.filter((rule) => rule.is_active) ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="mt-2 text-muted-foreground">
          Overview of your observability platform
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Logs</CardTitle>
            <ScrollText className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {logsLoading ? "..." : (logs?.total ?? 0)}
            </div>
            <p className="text-xs text-muted-foreground">Total in database</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Active Alerts</CardTitle>
            <Bell className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {alertsLoading ? "..." : activeAlerts.length}
            </div>
            <p className="text-xs text-muted-foreground">Alert rules enabled</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Error Rate</CardTitle>
            <AlertTriangle className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {logsLoading
                ? "..."
                : logItems.length
                  ? Math.round((errorLogs.length / logItems.length) * 100)
                  : 0}
              %
            </div>
            <p className="text-xs text-muted-foreground">
              Errors in recent logs
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="size-4" />
              Recent Logs
            </CardTitle>
          </CardHeader>
          <CardContent>
            {logsLoading ? (
              <p className="text-sm text-muted-foreground">Loading logs...</p>
            ) : logItems.length > 0 ? (
              <div className="space-y-2">
                {logItems.slice(0, 5).map((log) => (
                  <div
                    key={log.id}
                    className="flex items-center justify-between rounded-lg border p-3"
                  >
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium">
                        {log.message}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {log.service || "unknown"}
                      </p>
                    </div>
                    <Badge
                      variant={
                        log.level === "ERROR" || log.level === "CRITICAL"
                          ? "destructive"
                          : "secondary"
                      }
                    >
                      {log.level}
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No logs found.</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bell className="size-4" />
              Active Alert Rules
            </CardTitle>
          </CardHeader>
          <CardContent>
            {alertsLoading ? (
              <p className="text-sm text-muted-foreground">Loading alerts...</p>
            ) : activeAlerts.length > 0 ? (
              <div className="space-y-2">
                {activeAlerts.slice(0, 5).map((rule) => (
                  <div
                    key={rule.id}
                    className="flex items-center justify-between rounded-lg border p-3"
                  >
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium">
                        {rule.name}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Threshold: {rule.threshold} in{" "}
                        {rule.time_window_seconds}s
                      </p>
                    </div>
                    <Badge variant="default">{rule.severity}</Badge>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">
                No active alert rules.
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
