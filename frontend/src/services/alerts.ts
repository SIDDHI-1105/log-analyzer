import api from "@/lib/api";
import type { AlertRule, AlertRuleCreate, AlertHistory } from "@/types/alert";

export async function getAlertRules(): Promise<AlertRule[]> {
  const response = await api.get<AlertRule[]>("/alerts/rules");
  return response.data;
}

export async function createAlertRule(rule: AlertRuleCreate): Promise<AlertRule> {
  const response = await api.post<AlertRule>("/alerts/rules", rule);
  return response.data;
}

export async function getAlertHistory(): Promise<AlertHistory[]> {
  const response = await api.get<AlertHistory[]>("/alerts/history");
  return response.data;
}
