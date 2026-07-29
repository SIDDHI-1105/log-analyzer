export interface LogEntry {
  id: string;
  timestamp: string | null;
  level: string;
  message: string;
  service: string | null;
  host: string | null;
  trace_id: string | null;
  span_id: string | null;
  extra_data: Record<string, unknown> | null;
  created_at: string;
}

export interface LogEntryCreate {
  timestamp?: string | null;
  level?: string;
  message: string;
  service?: string | null;
  host?: string | null;
  trace_id?: string | null;
  span_id?: string | null;
  metadata?: Record<string, unknown>;
}

export interface LogBatchIngest {
  entries: LogEntryCreate[];
}

export interface LogIngestResponse {
  ingested: number;
  failed: number;
}
