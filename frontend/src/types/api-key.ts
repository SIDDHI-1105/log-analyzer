export interface ApiKey {
  id: string;
  name: string;
  last_used: string | null;
  expires_at: string | null;
}

export interface ApiKeyCreate {
  name: string;
}

export interface ApiKeyCreateResponse {
  id: string;
  name: string;
  key: string;
  expires_at: string | null;
  created_at: string;
}
