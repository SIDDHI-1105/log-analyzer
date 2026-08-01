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
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { getLogs } from "@/services/logs";
import type { LogEntry } from "@/types/log";

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
      <div className="flex items-center gap-4">
        <Skeleton className="h-4 w-[140px]" />
        <Skeleton className="h-4 w-[80px]" />
        <Skeleton className="h-4 w-[100px]" />
        <Skeleton className="h-4 flex-1" />
      </div>
      <div className="flex items-center gap-4">
        <Skeleton className="h-4 w-[140px]" />
        <Skeleton className="h-4 w-[80px]" />
        <Skeleton className="h-4 w-[100px]" />
        <Skeleton className="h-4 flex-1" />
      </div>
      <div className="flex items-center gap-4">
        <Skeleton className="h-4 w-[140px]" />
        <Skeleton className="h-4 w-[80px]" />
        <Skeleton className="h-4 w-[100px]" />
        <Skeleton className="h-4 flex-1" />
      </div>
      <div className="flex items-center gap-4">
        <Skeleton className="h-4 w-[140px]" />
        <Skeleton className="h-4 w-[80px]" />
        <Skeleton className="h-4 w-[100px]" />
        <Skeleton className="h-4 flex-1" />
      </div>
      <div className="flex items-center gap-4">
        <Skeleton className="h-4 w-[140px]" />
        <Skeleton className="h-4 w-[80px]" />
        <Skeleton className="h-4 w-[100px]" />
        <Skeleton className="h-4 flex-1" />
      </div>
    </div>
  );
}

function FilterSkeleton() {
  return (
    <div className="flex items-center gap-4">
      <Skeleton className="h-9 w-[200px]" />
      <Skeleton className="h-9 w-[140px]" />
      <Skeleton className="h-9 w-[140px]" />
      <Skeleton className="h-9 w-[120px]" />
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

  // Derive distinct services from logs data
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
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <ScrollText className="h-8 w-8 text-primary" />
            Log Explorer
          </h1>
          <p className="text-muted-foreground mt-1">
            Browse, search, and analyze application logs
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={handleRefresh}
          disabled={isLoading}
        >
          <RefreshCw
            className={`h-4 w-4 mr-2 ${isLoading ? "animate-spin" : ""}`}
          />
          Refresh
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <Filter className="h-4 w-4" />
            Filters
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && !data ? (
            <FilterSkeleton />
          ) : (
            <div className="flex flex-wrap items-center gap-4">
              {/* Search */}
              <div className="relative">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search logs..."
                  value={searchQuery}
                  onChange={(e) => {
                    setSearchQuery(e.target.value);
                    setSkip(0);
                  }}
                  className="pl-9 w-[280px]"
                />
              </div>

              {/* Level Filter */}
              <Select
                value={levelFilter}
                onValueChange={(value) => {
                  setLevelFilter(value);
                  setSkip(0);
                }}
              >
                <SelectTrigger className="w-[140px]">
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
                onValueChange={(value) => {
                  setServiceFilter(value);
                  setSkip(0);
                }}
              >
                <SelectTrigger className="w-[180px]">
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
                onValueChange={(value) => {
                  setLimit(Number(value));
                  setSkip(0);
                }}
              >
                <SelectTrigger className="w-[120px]">
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
                  className="text-muted-foreground"
                >
                  <X className="h-4 w-4 mr-1" />
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
            <div className="p-6">
              <LogSkeleton />
            </div>
          ) : isError ? (
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <AlertCircle className="h-12 w-12 text-destructive mb-4" />
              <h3 className="text-lg font-semibold">Failed to load logs</h3>
              <p className="text-muted-foreground mt-1 mb-4">
                There was an error fetching the logs. Please try again.
              </p>
              <Button onClick={handleRefresh} variant="outline">
                <RefreshCw className="h-4 w-4 mr-2" />
                Retry
              </Button>
            </div>
          ) : data?.items.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <FileText className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold">No logs found</h3>
              <p className="text-muted-foreground mt-1 max-w-md">
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
                  <X className="h-4 w-4 mr-2" />
                  Clear Filters
                </Button>
              )}
            </div>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[160px]">
                      <Clock className="h-3.5 w-3.5 inline mr-1" />
                      Timestamp
                    </TableHead>
                    <TableHead className="w-[90px]">
                      <Activity className="h-3.5 w-3.5 inline mr-1" />
                      Level
                    </TableHead>
                    <TableHead className="w-[140px]">
                      <Server className="h-3.5 w-3.5 inline mr-1" />
                      Service
                    </TableHead>
                    <TableHead>
                      <Layers className="h-3.5 w-3.5 inline mr-1" />
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
                      <TableCell className="max-w-[500px] truncate text-sm">
                        {log.message}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              {/* Pagination */}
              <div className="flex items-center justify-between px-6 py-4 border-t">
                <div className="text-sm text-muted-foreground">
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
                  >
                    <ChevronLeft className="h-4 w-4" />
                  </Button>
                  <span className="text-sm text-muted-foreground">
                    Page {currentPage} of {totalPages}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setSkip((s) => s + limit)}
                    disabled={!data || skip + limit >= data.total}
                  >
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* Log Detail Dialog */}
      <Dialog open={!!selectedLog} onOpenChange={() => setSelectedLog(null)}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Log Detail
            </DialogTitle>
          </DialogHeader>

          {selectedLog && (
            <div className="space-y-6">
              {/* Level & Service */}
              <div className="flex items-center gap-3">
                <Badge
                  variant={getLevelColor(selectedLog.level)}
                  className="text-sm"
                >
                  {selectedLog.level}
                </Badge>
                <span className="text-sm text-muted-foreground flex items-center gap-1">
                  <Server className="h-3.5 w-3.5" />
                  {selectedLog.service || "—"}
                </span>
              </div>

              {/* Timestamp */}
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Clock className="h-4 w-4" />
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
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium text-muted-foreground">
                    Message
                  </label>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleCopyMessage(selectedLog.message)}
                    className="h-8"
                  >
                    {copied ? (
                      <>
                        <Check className="h-4 w-4 mr-1 text-green-500" />
                        Copied
                      </>
                    ) : (
                      <>
                        <Copy className="h-4 w-4 mr-1" />
                        Copy
                      </>
                    )}
                  </Button>
                </div>
                <div className="bg-muted rounded-lg p-4 font-mono text-sm whitespace-pre-wrap break-all">
                  {selectedLog.message}
                </div>
              </div>

              {/* Metadata Grid */}
              <div className="grid grid-cols-2 gap-4">
                {selectedLog.trace_id && (
                  <div className="space-y-1">
                    <label className="text-xs font-medium text-muted-foreground flex items-center gap-1">
                      <Hash className="h-3 w-3" />
                      Trace ID
                    </label>
                    <div className="font-mono text-sm bg-muted rounded px-2 py-1 break-all">
                      {selectedLog.trace_id}
                    </div>
                  </div>
                )}

                {selectedLog.host && (
                  <div className="space-y-1">
                    <label className="text-xs font-medium text-muted-foreground flex items-center gap-1">
                      <Server className="h-3 w-3" />
                      Host
                    </label>
                    <div className="font-mono text-sm bg-muted rounded px-2 py-1">
                      {selectedLog.host}
                    </div>
                  </div>
                )}

                {selectedLog.span_id && (
                  <div className="space-y-1">
                    <label className="text-xs font-medium text-muted-foreground">
                      Span ID
                    </label>
                    <div className="font-mono text-sm bg-muted rounded px-2 py-1 break-all">
                      {selectedLog.span_id}
                    </div>
                  </div>
                )}

                <div className="space-y-1">
                  <label className="text-xs font-medium text-muted-foreground">
                    Log ID
                  </label>
                  <div className="font-mono text-sm bg-muted rounded px-2 py-1 break-all">
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
                    <pre className="bg-muted rounded-lg p-4 text-xs font-mono overflow-x-auto">
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
