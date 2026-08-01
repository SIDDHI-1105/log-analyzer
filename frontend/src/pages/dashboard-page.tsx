import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  ScrollText,
  Bell,
  AlertTriangle,
  Activity,
  Server,
  TrendingUp,
  Clock,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { getLogs } from "@/services/logs";
import { getAlertRules } from "@/services/alerts";
import { getStats, getTimeSeries } from "@/services/stats";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";

const TIME_RANGES = [
  { label: "24h", hours: 24 },
  { label: "7d", hours: 168 },
  { label: "30d", hours: 720 },
];

const LEVEL_COLORS = {
  DEBUG: "#6b7280",
  INFO: "#3b82f6",
  WARNING: "#f59e0b",
  ERROR: "#ef4444",
  CRITICAL: "#7f1d1d",
};

const PIE_COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#06b6d4", "#84cc16", "#f97316", "#6366f1"];

function StatsCard({
  title,
  value,
  icon: Icon,
  subtitle,
  loading,
}: {
  title: string;
  value: string | number;
  icon: React.ElementType;
  subtitle: string;
  loading: boolean;
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className="size-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        {loading ? (
          <Skeleton className="h-8 w-20" />
        ) : (
          <div className="text-2xl font-bold">{value}</div>
        )}
        <p className="text-xs text-muted-foreground">{subtitle}</p>
      </CardContent>
    </Card>
  );
}

export function DashboardPage() {
  const [timeRange, setTimeRange] = useState(24);

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ["stats", timeRange],
    queryFn: () => getStats(timeRange),
  });

  const { data: timeSeries, isLoading: seriesLoading } = useQuery({
    queryKey: ["timeseries", timeRange],
    queryFn: () => getTimeSeries(timeRange),
  });

  const { data: logs, isLoading: logsLoading } = useQuery({
    queryKey: ["logs", "recent"],
    queryFn: () => getLogs({ skip: 0, limit: 10 }),
  });

  const { data: alertRules, isLoading: alertsLoading } = useQuery({
    queryKey: ["alert-rules"],
    queryFn: getAlertRules,
  });

  const logItems = logs?.items ?? [];
  const activeAlerts = alertRules?.filter((rule) => rule.is_active) ?? [];

  const chartData = stats?.logs_by_level.map((item) => ({
    name: item.level,
    count: item.count,
    fill: LEVEL_COLORS[item.level as keyof typeof LEVEL_COLORS] || "#6b7280",
  })) ?? [];

  const serviceData = stats?.logs_by_service.map((item, index) => ({
    name: item.service,
    value: item.count,
    fill: PIE_COLORS[index % PIE_COLORS.length],
  })) ?? [];

  const timeSeriesData = timeSeries?.points.map((point) => ({
    time: new Date(point.timestamp).toLocaleDateString(undefined, {
      month: "short",
      day: "numeric",
      hour: timeSeries.interval === "hour" ? "numeric" : undefined,
    }),
    count: point.count,
  })) ?? [];

  const isLoading = statsLoading || seriesLoading;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="mt-2 text-muted-foreground">
            Overview of your observability platform
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Clock className="size-4 text-muted-foreground" />
          {TIME_RANGES.map((range) => (
            <Button
              key={range.hours}
              variant={timeRange === range.hours ? "default" : "outline"}
              size="sm"
              onClick={() => setTimeRange(range.hours)}
            >
              {range.label}
            </Button>
          ))}
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <StatsCard
          title="Total Logs"
          value={stats?.total_logs ?? 0}
          icon={ScrollText}
          subtitle={`Last ${timeRange >= 24 ? timeRange / 24 + "d" : timeRange + "h"}`}
          loading={isLoading}
        />
        <StatsCard
          title="Error Rate"
          value={`${stats?.error_rate ?? 0}%`}
          icon={AlertTriangle}
          subtitle="Errors + Critical"
          loading={isLoading}
        />
        <StatsCard
          title="Active Alerts"
          value={activeAlerts.length}
          icon={Bell}
          subtitle="Alert rules enabled"
          loading={alertsLoading}
        />
        <StatsCard
          title="Services"
          value={stats?.unique_services ?? 0}
          icon={Server}
          subtitle="Unique services"
          loading={isLoading}
        />
      </div>

      {/* Charts Row */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Bar Chart - Logs by Level */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-sm">
              <Activity className="size-4" />
              Logs by Level
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-[200px] w-full" />
            ) : chartData.every((d) => d.count === 0) ? (
              <div className="flex h-[200px] items-center justify-center text-sm text-muted-foreground">
                No data for selected period
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                  <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "6px",
                    }}
                  />
                  <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        {/* Line Chart - Volume Over Time */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-sm">
              <TrendingUp className="size-4" />
              Volume Over Time
            </CardTitle>
          </CardHeader>
          <CardContent>
            {seriesLoading ? (
              <Skeleton className="h-[200px] w-full" />
            ) : timeSeriesData.length === 0 ? (
              <div className="flex h-[200px] items-center justify-center text-sm text-muted-foreground">
                No data for selected period
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={timeSeriesData}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                  <XAxis dataKey="time" tick={{ fontSize: 10 }} angle={-45} textAnchor="end" height={60} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "6px",
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="count"
                    stroke="#3b82f6"
                    strokeWidth={2}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        {/* Pie Chart - Logs by Service */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-sm">
              <Server className="size-4" />
              Logs by Service
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-[200px] w-full" />
            ) : serviceData.length === 0 ? (
              <div className="flex h-[200px] items-center justify-center text-sm text-muted-foreground">
                No data for selected period
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={serviceData}
                    cx="50%"
                    cy="50%"
                    innerRadius={40}
                    outerRadius={70}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {serviceData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "6px",
                    }}
                  />
                  <Legend iconSize={8} wrapperStyle={{ fontSize: "12px" }} />
                </PieChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Bottom Row - Recent Logs & Active Alerts */}
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
              <div className="space-y-2">
                <Skeleton className="h-12 w-full" />
                <Skeleton className="h-12 w-full" />
                <Skeleton className="h-12 w-full" />
              </div>
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
              <div className="space-y-2">
                <Skeleton className="h-12 w-full" />
                <Skeleton className="h-12 w-full" />
                <Skeleton className="h-12 w-full" />
              </div>
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
