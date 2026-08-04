import api from "../lib/api.ts";

export interface LevelCount {
  level: string;
  count: number;
}

export interface ServiceCount {
  service: string;
  count: number;
}

export interface StatsResponse {
  total_logs: number;
  error_count: number;
  warning_count: number;
  info_count: number;
  debug_count: number;
  critical_count: number;
  error_rate: number;
  logs_by_level: LevelCount[];
  logs_by_service: ServiceCount[];
  unique_services: number;
  time_range_hours: number;
}

export interface TimeSeriesPoint {
  timestamp: string;
  count: number;
}

export interface TimeSeriesResponse {
  interval: string;
  points: TimeSeriesPoint[];
}

export async function getStats(hours = 24): Promise<StatsResponse> {
  const response = await api.get<StatsResponse>(`/stats/?hours=${hours}`);
  return response.data;
}

export async function getTimeSeries(hours = 24): Promise<TimeSeriesResponse> {
  const response = await api.get<TimeSeriesResponse>(`/stats/timeseries?hours=${hours}`);
  return response.data;
}
