import api from "@/lib/api";
import type { UserLogin, TokenResponse, User } from "@/types/auth";

export async function login(credentials: UserLogin): Promise<TokenResponse> {
  const response = await api.post<TokenResponse>("/auth/login", credentials);
  return response.data;
}

export async function register(credentials: UserLogin): Promise<TokenResponse> {
  const response = await api.post<TokenResponse>("/auth/register", credentials);
  return response.data;
}

export async function getCurrentUser(): Promise<User> {
  const response = await api.get<User>("/auth/me");
  return response.data;
}
