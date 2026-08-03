export interface ApiKey {
  id: string;
  name: string;
  key_prefix: string;
  is_active: boolean;
  last_used: string | null;
  expires_at: string | null;
  created_at: string;
}

export interface ApiKeyCreate {
  name: string;
}

export interface ApiKeyCreateResponse {
  id: string;
  name: string;
  key: string;
  key_prefix: string;
  is_active: boolean;
  expires_at: string | null;
  created_at: string;
}
