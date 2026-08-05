import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  RefreshCw,
  Filter,
  ChevronLeft,
  ChevronRight,
  ScrollText,
  Search,
  FileText,
  Copy,
  Check,
  X,
  Clock,
  Server,
  Hash,
  Activity,
  Layers,
  AlertCircle,
} from "lucide-react";
import { Button } from "../components/ui/button.tsx";
import { Badge } from "../components/ui/badge.tsx";
import { Input } from "../components/ui/input.tsx";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select.tsx";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../components/ui/table.tsx";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card.tsx";
import { Skeleton } from "../components/ui/skeleton.tsx";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "../components/ui/dialog.tsx";
import { getLogs } from "../services/logs.ts";
import type { LogEntry } from "../types/log.ts";

const LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"];

function getLevelColor(
  level: string,
): "default" | "secondary" | "destructive" | "outline" {
  switch (level) {
    case "ERROR":
    case "CRITICAL":
      return "destructive";
    case "WARNING":
      return "outline";
    case "INFO":
      return "secondary";
    default:
      return "default";
  }
}

function LogSkeleton() {
  return (
    <div className="space-y-3">
      {[...Array(5)].map((_, i) => (
        <div key={i} className="flex items-center gap-4">
          <Skeleton className="h-4 w-[100px] sm:w-[140px]" />
          <Skeleton className="h-4 w-[60px] sm:w-[80px]" />
          <Skeleton className="h-4 w-[80px] sm:w-[100px]" />
          <Skeleton className="h-4 flex-1" />
        </div>
      ))}
    </div>
  );
}

function FilterSkeleton() {
  return (
    <div className="flex flex-wrap items-center gap-3">
      <Skeleton className="h-9 w-full sm:w-[200px]" />
      <Skeleton className="h-9 w-full sm:w-[140px]" />
      <Skeleton className="h-9 w-full sm:w-[140px]" />
      <Skeleton className="h-9 w-full sm:w-[120px]" />
    </div>
  );
}

export default function LogsPage() {
  const [skip, setSkip] = useState(0);
  const [limit, setLimit] = useState(25);
  const [levelFilter, setLevelFilter] = useState<string>("ALL");
  const [serviceFilter, setServiceFilter] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedLog, setSelectedLog] = useState<LogEntry | null>(null);
  const [copied, setCopied] = useState(false);

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["logs", skip, limit, levelFilter, serviceFilter, searchQuery],
    queryFn: () =>
      getLogs({
        skip,
        limit,
        level: levelFilter === "ALL" ? undefined : levelFilter,
        service: serviceFilter === "ALL" ? undefined : serviceFilter,
        search: searchQuery || undefined,
      }),
  });

  const services = data?.items
    ? [...new Set(data.items.map((log) => log.service).filter(Boolean))].sort()
    : [];

  const handleCopyMessage = async (message: string) => {
    await navigator.clipboard.writeText(message);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleRefresh = () => {
    refetch();
  };

  const handleClearFilters = () => {
    setLevelFilter("ALL");
    setServiceFilter("ALL");
    setSearchQuery("");
    setSkip(0);
  };

  const totalPages = data ? Math.ceil(data.total / limit) : 0;
  const currentPage = Math.floor(skip / limit) + 1;
  const hasActiveFilters =
    levelFilter !== "ALL" || serviceFilter !== "ALL" || searchQuery !== "";

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div className="min-w-0">
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight flex items-center gap-2">
            <ScrollText className="h-6 w-6 sm:h-8 sm:w-8 text-primary shrink-0" />
            <span className="truncate">Log Explorer</span>
          </h1>
          <p className="text-muted-foreground mt-1 text-sm">
            Browse, search, and analyze application logs
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={handleRefresh}
          disabled={isLoading}
          className="shrink-0 self-start"
        >
          <RefreshCw
            className={`h-4 w-4 mr-2 shrink-0 ${isLoading ? "animate-spin" : ""}`}
          />
          Refresh
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <Filter className="h-4 w-4 shrink-0" />
            Filters
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && !data ? (
            <FilterSkeleton />
          ) : (
            <div className="flex flex-col sm:flex-row flex-wrap items-stretch sm:items-center gap-3">
              {/* Search */}
              <div className="relative w-full sm:w-auto sm:min-w-[200px] sm:max-w-[280px]">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search logs..."
                  value={searchQuery}
                  onChange={(e) => {
                    setSearchQuery(e.target.value);
                    setSkip(0);
                  }}
                  className="pl-9 w-full"
                />
              </div>

              {/* Level Filter */}
              <Select
                value={levelFilter}
                onValueChange={(value) => { if (!value) return;
                  setLevelFilter(value);
                  setSkip(0);
                }}
              >
                <SelectTrigger className="w-full sm:w-[140px]">
                  <SelectValue placeholder="Level" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="ALL">All Levels</SelectItem>
                  {LEVELS.map((level) => (
                    <SelectItem key={level} value={level}>
                      {level}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {/* Service Filter */}
              <Select
                value={serviceFilter}
                onValueChange={(value) => { if (!value) return;
                  setServiceFilter(value);
                  setSkip(0);
                }}
              >
                <SelectTrigger className="w-full sm:w-[180px]">
                  <SelectValue placeholder="Service" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="ALL">All Services</SelectItem>
                  {services.map((service) => (
                    <SelectItem key={service} value={service}>
                      {service}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {/* Page Size */}
              <Select
                value={String(limit)}
                onValueChange={(value) => { if (!value) return;
                  setLimit(Number(value));
                  setSkip(0);
                }}
              >
                <SelectTrigger className="w-full sm:w-[120px]">
                  <SelectValue placeholder="Per page" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="10">10 / page</SelectItem>
                  <SelectItem value="25">25 / page</SelectItem>
                  <SelectItem value="50">50 / page</SelectItem>
                  <SelectItem value="100">100 / page</SelectItem>
                </SelectContent>
              </Select>

              {/* Clear Filters */}
              {hasActiveFilters && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleClearFilters}
                  className="text-muted-foreground self-start sm:self-auto"
                >
                  <X className="h-4 w-4 mr-1 shrink-0" />
                  Clear
                </Button>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Logs Table */}
      <Card>
        <CardContent className="p-0">
          {isLoading && !data ? (
            <div className="p-4 sm:p-6">
              <LogSkeleton />
            </div>
          ) : isError ? (
            <div className="flex flex-col items-center justify-center py-12 sm:py-16 text-center px-4">
              <AlertCircle className="h-10 w-10 sm:h-12 sm:w-12 text-destructive mb-4" />
              <h3 className="text-base sm:text-lg font-semibold">Failed to load logs</h3>
              <p className="text-muted-foreground mt-1 mb-4 text-sm max-w-md">
                There was an error fetching the logs. Please try again.
              </p>
              <Button onClick={handleRefresh} variant="outline">
                <RefreshCw className="h-4 w-4 mr-2 shrink-0" />
                Retry
              </Button>
            </div>
          ) : data?.items.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 sm:py-16 text-center px-4">
              <FileText className="h-10 w-10 sm:h-12 sm:w-12 text-muted-foreground mb-4" />
              <h3 className="text-base sm:text-lg font-semibold">No logs found</h3>
              <p className="text-muted-foreground mt-1 max-w-md text-sm">
                {hasActiveFilters
                  ? "No logs match your current filters. Try adjusting or clearing your filters."
                  : "No logs are available yet. Logs will appear here once they are ingested."}
              </p>
              {hasActiveFilters && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleClearFilters}
                  className="mt-4"
                >
                  <X className="h-4 w-4 mr-2 shrink-0" />
                  Clear Filters
                </Button>
              )}
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-[120px] sm:w-[160px]">
                        <Clock className="h-3.5 w-3.5 inline mr-1 shrink-0" />
                        Timestamp
                      </TableHead>
                      <TableHead className="w-[80px] sm:w-[90px]">
                        <Activity className="h-3.5 w-3.5 inline mr-1 shrink-0" />
                        Level
                      </TableHead>
                      <TableHead className="w-[100px] sm:w-[140px]">
                        <Server className="h-3.5 w-3.5 inline mr-1 shrink-0" />
                        Service
                      </TableHead>
                      <TableHead className="min-w-[200px]">
                        <Layers className="h-3.5 w-3.5 inline mr-1 shrink-0" />
                        Message
                      </TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {data?.items.map((log) => (
                      <TableRow
                        key={log.id}
                        className="cursor-pointer hover:bg-muted/50 transition-colors"
                        onClick={() => setSelectedLog(log)}
                      >
                        <TableCell className="font-mono text-xs whitespace-nowrap">
                          {log.timestamp
                            ? new Date(log.timestamp).toLocaleString()
                            : new Date(log.created_at).toLocaleString()}
                        </TableCell>
                        <TableCell>
                          <Badge
                            variant={getLevelColor(log.level)}
                            className="text-xs"
                          >
                            {log.level}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-sm text-muted-foreground">
                          {log.service || "—"}
                        </TableCell>
                        <TableCell className="max-w-[200px] sm:max-w-[300px] md:max-w-[400px] lg:max-w-[500px] truncate text-sm">
                          {log.message}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>

              {/* Pagination */}
              <div className="flex flex-col sm:flex-row items-center justify-between gap-3 px-4 sm:px-6 py-4 border-t">
                <div className="text-xs sm:text-sm text-muted-foreground text-center sm:text-left">
                  Showing{" "}
                  <span className="font-medium">
                    {data?.total ? skip + 1 : 0}
                  </span>{" "}
                  to{" "}
                  <span className="font-medium">
                    {Math.min(skip + limit, data?.total || 0)}
                  </span>{" "}
                  of <span className="font-medium">{data?.total ?? 0}</span>{" "}
                  logs
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setSkip((s) => Math.max(0, s - limit))}
                    disabled={skip <= 0}
                    className="size-8 sm:h-8 sm:w-auto px-0 sm:px-2.5"
                  >
                    <ChevronLeft className="h-4 w-4 sm:mr-1" />
                    <span className="hidden sm:inline">Prev</span>
                  </Button>
                  <span className="text-xs sm:text-sm text-muted-foreground">
                    Page {currentPage} of {totalPages}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setSkip((s) => s + limit)}
                    disabled={!data || skip + limit >= data.total}
                    className="size-8 sm:h-8 sm:w-auto px-0 sm:px-2.5"
                  >
                    <span className="hidden sm:inline">Next</span>
                    <ChevronRight className="h-4 w-4 sm:ml-1" />
                  </Button>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* Log Detail Dialog */}
      <Dialog open={!!selectedLog} onOpenChange={() => setSelectedLog(null)}>
        <DialogContent className="max-w-[calc(100%-2rem)] sm:max-w-lg md:max-w-2xl max-h-[85vh] overflow-y-auto p-4 sm:p-6">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-base sm:text-lg">
              <FileText className="h-5 w-5 shrink-0" />
              Log Detail
            </DialogTitle>
          </DialogHeader>

          {selectedLog && (
            <div className="space-y-4 sm:space-y-6">
              {/* Level & Service */}
              <div className="flex flex-wrap items-center gap-2 sm:gap-3">
                <Badge
                  variant={getLevelColor(selectedLog.level)}
                  className="text-sm"
                >
                  {selectedLog.level}
                </Badge>
                <span className="text-sm text-muted-foreground flex items-center gap-1">
                  <Server className="h-3.5 w-3.5 shrink-0" />
                  {selectedLog.service || "—"}
                </span>
              </div>

              {/* Timestamp */}
              <div className="flex items-center gap-2 text-xs sm:text-sm text-muted-foreground">
                <Clock className="h-4 w-4 shrink-0" />
                {selectedLog.timestamp
                  ? new Date(selectedLog.timestamp).toLocaleString(undefined, {
                      weekday: "short",
                      year: "numeric",
                      month: "short",
                      day: "numeric",
                      hour: "2-digit",
                      minute: "2-digit",
                      second: "2-digit",
                      timeZoneName: "short",
                    })
                  : new Date(selectedLog.created_at).toLocaleString(undefined, {
                      weekday: "short",
                      year: "numeric",
                      month: "short",
                      day: "numeric",
                      hour: "2-digit",
                      minute: "2-digit",
                      second: "2-digit",
                      timeZoneName: "short",
                    })}
              </div>

              {/* Message */}
              <div className="space-y-2">
                <div className="flex items-center justify-between gap-2">
                  <label className="text-sm font-medium text-muted-foreground">
                    Message
                  </label>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleCopyMessage(selectedLog.message)}
                    className="h-8 shrink-0"
                  >
                    {copied ? (
                      <>
                        <Check className="h-4 w-4 mr-1 text-green-500 shrink-0" />
                        <span className="hidden sm:inline">Copied</span>
                      </>
                    ) : (
                      <>
                        <Copy className="h-4 w-4 mr-1 shrink-0" />
                        <span className="hidden sm:inline">Copy</span>
                      </>
                    )}
                  </Button>
                </div>
                <div className="bg-muted rounded-lg p-3 sm:p-4 font-mono text-xs sm:text-sm whitespace-pre-wrap break-all">
                  {selectedLog.message}
                </div>
              </div>

              {/* Metadata Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                {selectedLog.trace_id && (
                  <div className="space-y-1">
                    <label className="text-xs font-medium text-muted-foreground flex items-center gap-1">
                      <Hash className="h-3 w-3 shrink-0" />
                      Trace ID
                    </label>
                    <div className="font-mono text-xs sm:text-sm bg-muted rounded px-2 py-1 break-all">
                      {selectedLog.trace_id}
                    </div>
                  </div>
                )}

                {selectedLog.host && (
                  <div className="space-y-1">
                    <label className="text-xs font-medium text-muted-foreground flex items-center gap-1">
                      <Server className="h-3 w-3 shrink-0" />
                      Host
                    </label>
                    <div className="font-mono text-xs sm:text-sm bg-muted rounded px-2 py-1 break-all">
                      {selectedLog.host}
                    </div>
                  </div>
                )}

                {selectedLog.span_id && (
                  <div className="space-y-1">
                    <label className="text-xs font-medium text-muted-foreground">
                      Span ID
                    </label>
                    <div className="font-mono text-xs sm:text-sm bg-muted rounded px-2 py-1 break-all">
                      {selectedLog.span_id}
                    </div>
                  </div>
                )}

                <div className="space-y-1">
                  <label className="text-xs font-medium text-muted-foreground">
                    Log ID
                  </label>
                  <div className="font-mono text-xs sm:text-sm bg-muted rounded px-2 py-1 break-all">
                    {selectedLog.id}
                  </div>
                </div>
              </div>

              {/* Extra Data JSON */}
              {selectedLog.extra_data &&
                Object.keys(selectedLog.extra_data).length > 0 && (
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-muted-foreground">
                      Extra Data
                    </label>
                    <pre className="bg-muted rounded-lg p-3 sm:p-4 text-xs font-mono overflow-x-auto">
                      {JSON.stringify(selectedLog.extra_data, null, 2)}
                    </pre>
                  </div>
                )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
