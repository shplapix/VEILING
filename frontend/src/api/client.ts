import axios from "axios";

const getBaseUrl = (): string => {
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL as string;
  }
  if (typeof window !== "undefined" && window.location) {
    if (window.location.port === "5173") {
      return "/api/v1";
    }
    const protocol = window.location.protocol === "https:" ? "https:" : "http:";
    const host = window.location.hostname || "127.0.0.1";
    return `${protocol}//${host}:8000/api/v1`;
  }
  return "http://127.0.0.1:8000/api/v1";
};

export const apiClient = axios.create({
  baseURL: getBaseUrl(),
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("veiling_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
