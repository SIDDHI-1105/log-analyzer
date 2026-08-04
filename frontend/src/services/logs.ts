import api from "../lib/api";
import type { LogEntry, LogBatchIngest, LogIngestResponse } from "../types/log";

export interface GetLogsParams {
  skip?: number;
  limit?: number;
  level?: string;
  service?: string;
  search?: string;
}

export interface LogListResponse {
  items: LogEntry[];
  total: number;
  skip: number;
  limit: number;
}

export async function getLogs(
  params: GetLogsParams = {},
): Promise<LogListResponse> {
  const { skip = 0, limit = 50, level, service, search } = params;
  const queryParams = new URLSearchParams();
  queryParams.append("skip", String(skip));
  queryParams.append("limit", String(limit));
  if (level) queryParams.append("level", level);
  if (service) queryParams.append("service", service);
  if (search) queryParams.append("search", search);

  const response = await api.get<LogListResponse>(
    `/logs/?${queryParams.toString()}`,
  );
  return response.data;
}

export async function ingestLogs(
  batch: LogBatchIngest,
): Promise<LogIngestResponse> {
  const response = await api.post<LogIngestResponse>("/logs/ingest", batch);
  return response.data;
}
