export interface User {
  id: string;
  email: string;
  role: "admin" | "editor" | "viewer";
  is_active: boolean;
  avatar_url: string | null;
}

export interface UserCreate {
  email: string;
  password: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface UserUpdate {
  avatar_url: string | null;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}
