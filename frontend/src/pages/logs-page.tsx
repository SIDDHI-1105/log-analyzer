import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { RefreshCw, Filter, ChevronLeft, ChevronRight, ScrollText } from "lucide-react";
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
import { getLogs } from "@/services/logs";
import type { LogEntry } from "@/types/log";

const LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"];

function getLevelColor(level: string): "default" | "secondary" | "destructive" | "outline" {
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

export function LogsPage() {
  const [skip, setSkip] = useState(0);
  const [limit] = useState(20);
  const [levelFilter, setLevelFilter] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState("");

  const { data: logs, isLoading, refetch } = useQuery({
    queryKey: ["logs", skip, limit, levelFilter],
    queryFn: () => getLogs(skip, limit, levelFilter || undefined),
  });

  const filteredLogs = logs?.filter((log: LogEntry) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      log.message.toLowerCase().includes(query) ||
      (log.service && log.service.toLowerCase().includes(query))
    );
  });

  const handlePrev = () => setSkip((prev) => Math.max(0, prev - limit));
  const handleNext = () => setSkip((prev) => prev + limit);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Log Explorer</h1>
          <p className="mt-2 text-muted-foreground">Search and filter your application logs</p>
        </div>
        <Button variant="outline" size="sm" onClick={() => refetch()}>
          <RefreshCw className="mr-2 size-4" />
          Refresh
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ScrollText className="size-5" />
            Logs
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-col gap-4 sm:flex-row">
            <div className="flex-1">
              <Input
                placeholder="Search logs by message or service..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <div className="w-full sm:w-48">
              <Select value={levelFilter} onValueChange={(value) => setLevelFilter(value ?? "")}>
                <SelectTrigger>
                  <Filter className="mr-2 size-4" />
                  <SelectValue placeholder="Filter by level" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Levels</SelectItem>
                  {LEVELS.map((level) => (
                    <SelectItem key={level} value={level}>
                      {level}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {isLoading ? (
            <p className="text-sm text-muted-foreground">Loading logs...</p>
          ) : filteredLogs && filteredLogs.length > 0 ? (
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[180px]">Timestamp</TableHead>
                    <TableHead className="w-[100px]">Level</TableHead>
                    <TableHead className="w-[150px]">Service</TableHead>
                    <TableHead>Message</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredLogs.map((log: LogEntry) => (
                    <TableRow key={log.id}>
                      <TableCell className="font-mono text-xs">
                        {log.timestamp
                          ? new Date(log.timestamp).toLocaleString()
                          : new Date(log.created_at).toLocaleString()}
                      </TableCell>
                      <TableCell>
                        <Badge variant={getLevelColor(log.level)}>{log.level}</Badge>
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {log.service || "—"}
                      </TableCell>
                      <TableCell className="max-w-md truncate">{log.message}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">No logs found.</p>
          )}

          <div className="flex items-center justify-between">
            <Button
              variant="outline"
              size="sm"
              onClick={handlePrev}
              disabled={skip === 0}
            >
              <ChevronLeft className="mr-2 size-4" />
              Previous
            </Button>
            <span className="text-sm text-muted-foreground">
              Page {Math.floor(skip / limit) + 1}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={handleNext}
              disabled={!logs || logs.length < limit}
            >
              Next
              <ChevronRight className="ml-2 size-4" />
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
