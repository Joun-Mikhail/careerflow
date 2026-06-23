/**
 * Axios instance shared by every API module.
 *
 * A request interceptor attaches the bearer access token; the response
 * interceptor normalizes the backend error envelope into an `ApiError` and,
 * on a 401, transparently tries to rotate tokens via the refresh endpoint
 * (single-flight) and retry the original request once before giving up and
 * clearing the session.
 */
import axios from 'axios';
import type { AxiosError, AxiosRequestConfig } from 'axios';

import type { ApiErrorBody, Token } from '@/lib/types';

const ACCESS_KEY = 'careerflow.token';
const REFRESH_KEY = 'careerflow.refresh';

export const tokenStore = {
  get: (): string | null => localStorage.getItem(ACCESS_KEY),
  getRefresh: (): string | null => localStorage.getItem(REFRESH_KEY),
  set: (access: string, refresh?: string): void => {
    localStorage.setItem(ACCESS_KEY, access);
    if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
  },
  clear: (): void => {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
  },
};

export class ApiError extends Error {
  code: string;
  status: number;
  details?: unknown;

  constructor(message: string, code: string, status: number, details?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.status = status;
    this.details = details;
  }
}

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';

export const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = tokenStore.get();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Allow the auth layer to react to forced logouts (e.g. expired refresh token).
let onUnauthorized: (() => void) | null = null;
export function setUnauthorizedHandler(handler: () => void): void {
  onUnauthorized = handler;
}

function normalizeError(error: AxiosError<ApiErrorBody>): ApiError {
  const status = error.response?.status ?? 0;
  const body = error.response?.data;
  if (body?.error) {
    return new ApiError(body.error.message, body.error.code, status, body.error.details);
  }
  return new ApiError(error.message || 'Network error. Please try again.', 'network_error', status);
}

// Single-flight refresh: concurrent 401s share one refresh request.
let refreshInFlight: Promise<string | null> | null = null;

async function rotateTokens(): Promise<string | null> {
  const refresh = tokenStore.getRefresh();
  if (!refresh) return null;
  try {
    // A bare client avoids recursing through this interceptor.
    const { data } = await axios.post<{ token: Token }>(`${BASE_URL}/auth/refresh`, {
      refresh_token: refresh,
    });
    tokenStore.set(data.token.access_token, data.token.refresh_token);
    return data.token.access_token;
  } catch {
    return null;
  }
}

interface RetriableConfig extends AxiosRequestConfig {
  _retry?: boolean;
  url?: string;
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ApiErrorBody>) => {
    const status = error.response?.status ?? 0;
    const original = error.config as RetriableConfig | undefined;
    const isAuthCall = original?.url?.includes('/auth/');

    if (status === 401 && original && !original._retry && !isAuthCall && tokenStore.getRefresh()) {
      original._retry = true;
      refreshInFlight ??= rotateTokens().finally(() => {
        refreshInFlight = null;
      });
      const newAccess = await refreshInFlight;
      if (newAccess) {
        original.headers = { ...original.headers, Authorization: `Bearer ${newAccess}` };
        return api(original);
      }
    }

    if (status === 401 && !isAuthCall) {
      tokenStore.clear();
      onUnauthorized?.();
    }
    return Promise.reject(normalizeError(error));
  },
);
