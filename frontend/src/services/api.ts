/**
 * Axios instance shared by every API module.
 *
 * A request interceptor attaches the bearer token from local storage; a
 * response interceptor normalizes the backend error envelope into an
 * `ApiError` and clears the session on 401 so the app can redirect to login.
 */
import axios from 'axios';
import type { AxiosError } from 'axios';

import type { ApiErrorBody } from '@/lib/types';

const TOKEN_KEY = 'careerflow.token';

export const tokenStore = {
  get: (): string | null => localStorage.getItem(TOKEN_KEY),
  set: (token: string): void => localStorage.setItem(TOKEN_KEY, token),
  clear: (): void => localStorage.removeItem(TOKEN_KEY),
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

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '/api/v1',
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = tokenStore.get();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Allow the auth layer to react to forced logouts (e.g. expired token).
let onUnauthorized: (() => void) | null = null;
export function setUnauthorizedHandler(handler: () => void): void {
  onUnauthorized = handler;
}

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiErrorBody>) => {
    const status = error.response?.status ?? 0;
    const body = error.response?.data;

    if (status === 401) {
      tokenStore.clear();
      onUnauthorized?.();
    }

    if (body?.error) {
      return Promise.reject(
        new ApiError(body.error.message, body.error.code, status, body.error.details),
      );
    }
    return Promise.reject(
      new ApiError(
        error.message || 'Network error. Please try again.',
        'network_error',
        status,
      ),
    );
  },
);
