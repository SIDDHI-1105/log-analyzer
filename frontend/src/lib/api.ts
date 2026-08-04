import axios, { type AxiosError, type InternalAxiosRequestConfig } from "axios";
import { useAuthStore } from "../store/auth-store.ts";

// Use environment variable for API base URL, fallback to relative path for local dev
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api/v1";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem("access_token");
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Clear auth state gracefully instead of hard redirect
      useAuthStore.getState().clearAuth();
    }
    return Promise.reject(error);
  }
);

export default api;
