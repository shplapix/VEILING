import { apiClient } from "./client";
import { User } from "../types";

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export const login = async (
  email: string,
  password: string
): Promise<AuthResponse> => {
  const response = await apiClient.post<AuthResponse>("/auth/login", {
    email,
    password,
  });
  if (response.data.access_token) {
    localStorage.setItem("veiling_token", response.data.access_token);
  }
  return response.data;
};

export const register = async (
  email: string,
  password: string,
  fullName?: string,
  role: string = "SELLER"
): Promise<AuthResponse> => {
  const response = await apiClient.post<AuthResponse>("/auth/register", {
    email,
    password,
    full_name: fullName,
    role,
  });
  if (response.data.access_token) {
    localStorage.setItem("veiling_token", response.data.access_token);
  }
  return response.data;
};

export const getMe = async (): Promise<User> => {
  const response = await apiClient.get<User>("/auth/me");
  return response.data;
};

export const logout = (): void => {
  localStorage.removeItem("veiling_token");
};

export const getStoredToken = (): string | null => {
  return localStorage.getItem("veiling_token");
};
