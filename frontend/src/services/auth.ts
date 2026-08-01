import api from "@/lib/api";
import type { UserLogin, TokenResponse, User, UserUpdate, PasswordChange } from "@/types/auth";

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

export async function updateCurrentUser(data: UserUpdate): Promise<User> {
  const response = await api.put<User>("/auth/me", data);
  return response.data;
}

export async function changePassword(data: PasswordChange): Promise<{ message: string }> {
  const response = await api.post<{ message: string }>("/auth/change-password", data);
  return response.data;
}
