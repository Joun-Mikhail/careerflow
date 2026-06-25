import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { queryKeys } from '@/lib/queryClient';
import { applicationsApi } from '@/services/applications';
import type {
  ApplicationInput,
  ApplicationListParams,
  ImportFromUrlInput,
} from '@/services/applications';

function invalidateApplications(qc: ReturnType<typeof useQueryClient>) {
  qc.invalidateQueries({ queryKey: ['applications'] });
  qc.invalidateQueries({ queryKey: queryKeys.dashboard });
  qc.invalidateQueries({ queryKey: queryKeys.analytics });
}

export function useApplications(params: ApplicationListParams = {}) {
  return useQuery({
    queryKey: queryKeys.applications(params),
    queryFn: () => applicationsApi.list(params),
  });
}

export function useApplication(id: string | undefined) {
  return useQuery({
    queryKey: queryKeys.application(id ?? ''),
    queryFn: () => applicationsApi.get(id as string),
    enabled: Boolean(id),
  });
}

export function useCreateApplication() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: ApplicationInput) => applicationsApi.create(input),
    onSuccess: () => invalidateApplications(qc),
  });
}

export function useUpdateApplication() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, input }: { id: string; input: Partial<ApplicationInput> }) =>
      applicationsApi.update(id, input),
    onSuccess: (_data, { id }) => {
      invalidateApplications(qc);
      qc.invalidateQueries({ queryKey: queryKeys.application(id) });
    },
  });
}

export function useImportApplicationFromUrl() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: ImportFromUrlInput) => applicationsApi.importFromUrl(input),
    onSuccess: () => {
      invalidateApplications(qc);
      qc.invalidateQueries({ queryKey: ['companies'] });
    },
  });
}

export function useDeleteApplication() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => applicationsApi.remove(id),
    onSuccess: () => invalidateApplications(qc),
  });
}
