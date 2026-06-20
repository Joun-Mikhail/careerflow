import { api } from './api';

import type { Company, Page } from '@/lib/types';

export interface CompanyInput {
  name: string;
  website?: string | null;
  industry?: string | null;
  location?: string | null;
  notes?: string | null;
}

export interface CompanyListParams {
  page?: number;
  page_size?: number;
  q?: string;
  industry?: string;
  sort?: 'created_at' | 'updated_at' | 'name';
  order?: 'asc' | 'desc';
}

export const companiesApi = {
  list: (params: CompanyListParams = {}) =>
    api.get<Page<Company>>('/companies', { params }).then((r) => r.data),
  get: (id: string) => api.get<Company>(`/companies/${id}`).then((r) => r.data),
  create: (input: CompanyInput) =>
    api.post<Company>('/companies', input).then((r) => r.data),
  update: (id: string, input: Partial<CompanyInput>) =>
    api.patch<Company>(`/companies/${id}`, input).then((r) => r.data),
  remove: (id: string) => api.delete(`/companies/${id}`).then(() => undefined),
};
