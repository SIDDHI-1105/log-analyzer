export interface Dashboard {
  id: string;
  user_id: string;
  name: string;
  widgets: Record<string, unknown>;
  created_at: string;
}

export interface DashboardCreate {
  name: string;
  widgets?: Record<string, unknown>;
}

export interface DashboardUpdate {
  name?: string;
  widgets?: Record<string, unknown>;
}
