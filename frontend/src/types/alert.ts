export type Severity = "DEBUG" | "INFO" | "WARNING" | "ERROR" | "CRITICAL";

export interface AlertRule {
  id: string;
  user_id: string;
  name: string;
  severity: Severity;
  threshold: number;
  time_window_seconds: number;
  match_pattern: string | null;
  notification_channels: string[];
  is_active: boolean;
  created_at: string;
}

export interface AlertRuleCreate {
  name: string;
  severity: Severity;
  threshold: number;
  time_window_seconds?: number;
  match_pattern?: string | null;
  notification_channels?: string[];
  is_active?: boolean;
}

export interface AlertRuleUpdate {
  name?: string;
  severity?: Severity;
  threshold?: number;
  time_window_seconds?: number;
  match_pattern?: string | null;
  notification_channels?: string[];
  is_active?: boolean;
}

export interface AlertHistory {
  id: string;
  rule_id: string;
  triggered_at: string;
  resolved_at: string | null;
  severity: string;
  details: Record<string, unknown> | null;
}
