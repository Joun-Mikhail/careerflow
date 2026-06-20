import { QueryClient } from '@tanstack/react-query';

import { ApiError } from '@/services/api';

/** Shared TanStack Query client with sensible defaults for a CRUD app. */
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: (failureCount, error) => {
        // Do not retry auth/permission/validation errors — only transient ones.
        if (error instanceof ApiError && error.status >= 400 && error.status < 500) {
          return false;
        }
        return failureCount < 2;
      },
      refetchOnWindowFocus: false,
    },
  },
});

/** Centralized query keys keep cache invalidation consistent and typo-free. */
export const queryKeys = {
  me: ['me'] as const,
  dashboard: ['dashboard'] as const,
  companies: (params?: unknown) => ['companies', params] as const,
  company: (id: string) => ['companies', id] as const,
  applications: (params?: unknown) => ['applications', params] as const,
  application: (id: string) => ['applications', id] as const,
  interviews: (applicationId: string) => ['interviews', applicationId] as const,
  notes: (applicationId: string) => ['notes', applicationId] as const,
  attachments: (applicationId: string) => ['attachments', applicationId] as const,
  tasks: (params?: unknown) => ['tasks', params] as const,
  analytics: ['analytics'] as const,
};
