import { api } from './api';

import type { Application, ApplicationStatus, Page } from '@/lib/types';

export interface ApplicationInput {
  company_id?: string | null;
  role_title: string;
  status?: ApplicationStatus;
  salary_min?: number | null;
  salary_max?: number | null;
  salary_currency?: string | null;
  location?: string | null;
  is_remote?: boolean;
  application_url?: string | null;
  source?: string | null;
  applied_at?: string | null;
}

export interface ApplicationListParams {
  page?: number;
  page_size?: number;
  q?: string;
  status?: ApplicationStatus;
  company_id?: string;
  sort?: 'created_at' | 'updated_at' | 'applied_at';
  order?: 'asc' | 'desc';
}

export const applicationsApi = {
  list: (params: ApplicationListParams = {}) =>
    api.get<Page<Application>>('/applications', { params }).then((r) => r.data),
  get: (id: string) => api.get<Application>(`/applications/${id}`).then((r) => r.data),
  create: (input: ApplicationInput) =>
    api.post<Application>('/applications', input).then((r) => r.data),
  update: (id: string, input: Partial<ApplicationInput>) =>
    api.patch<Application>(`/applications/${id}`, input).then((r) => r.data),
  remove: (id: string) => api.delete(`/applications/${id}`).then(() => undefined),
};
