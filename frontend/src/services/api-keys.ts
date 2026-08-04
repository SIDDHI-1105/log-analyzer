import api from "../lib/api";
import type { ApiKey, ApiKeyCreate, ApiKeyCreateResponse } from "../types/api-key";

export async function getApiKeys(): Promise<ApiKey[]> {
  const response = await api.get<ApiKey[]>("/api-keys/");
  return response.data;
}

export async function createApiKey(data: ApiKeyCreate): Promise<ApiKeyCreateResponse> {
  const response = await api.post<ApiKeyCreateResponse>("/api-keys/", data);
  return response.data;
}

export async function revokeApiKey(id: string): Promise<void> {
  await api.delete(`/api-keys/${id}`);
}
