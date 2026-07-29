import api from "@/lib/api";
import type { LogEntry, LogBatchIngest, LogIngestResponse } from "@/types/log";

export async function getLogs(skip = 0, limit = 100, level?: string): Promise<LogEntry[]> {
  const params = new URLSearchParams({ skip: String(skip), limit: String(limit) });
  if (level) params.append("level", level);
  const response = await api.get<LogEntry[]>(`/logs/?${params.toString()}`);
  return response.data;
}

export async function ingestLogs(batch: LogBatchIngest): Promise<LogIngestResponse> {
  const response = await api.post<LogIngestResponse>("/logs/ingest", batch);
  return response.data;
}
