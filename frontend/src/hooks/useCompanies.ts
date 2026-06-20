import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { queryKeys } from '@/lib/queryClient';
import { companiesApi } from '@/services/companies';
import type { CompanyInput, CompanyListParams } from '@/services/companies';

export function useCompanies(params: CompanyListParams = {}) {
  return useQuery({
    queryKey: queryKeys.companies(params),
    queryFn: () => companiesApi.list(params),
  });
}

export function useCompany(id: string | undefined) {
  return useQuery({
    queryKey: queryKeys.company(id ?? ''),
    queryFn: () => companiesApi.get(id as string),
    enabled: Boolean(id),
  });
}

export function useCreateCompany() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: CompanyInput) => companiesApi.create(input),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['companies'] }),
  });
}

export function useUpdateCompany() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, input }: { id: string; input: Partial<CompanyInput> }) =>
      companiesApi.update(id, input),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['companies'] }),
  });
}

export function useDeleteCompany() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => companiesApi.remove(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['companies'] }),
  });
}
