import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { queryKeys } from '@/lib/queryClient';
import { jobFiltersApi, jobsApi, type JobFilterInput } from '@/services/jobs';

export function useJobFilters() {
  return useQuery({ queryKey: queryKeys.jobFilters, queryFn: jobFiltersApi.list });
}

export function useJobs() {
  return useQuery({ queryKey: queryKeys.jobs, queryFn: jobsApi.list });
}

export function useCreateJobFilter() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: JobFilterInput) => jobFiltersApi.create(input),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.jobFilters }),
  });
}

export function useDeleteJobFilter() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => jobFiltersApi.remove(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.jobFilters }),
  });
}

export function useRunSearch() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => jobFiltersApi.search(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.jobs }),
  });
}
