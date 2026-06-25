import { api } from './api';

import type { Job, JobSearchFilter } from '@/lib/types';

export interface JobFilterInput {
  name: string;
  title_keywords?: string | null;
  locations?: string | null;
  keywords?: string | null;
  remote?: boolean;
  salary_min?: number | null;
  salary_max?: number | null;
  is_active?: boolean;
}

export const jobFiltersApi = {
  list: () => api.get<JobSearchFilter[]>('/job-filters').then((r) => r.data),
  create: (input: JobFilterInput) =>
    api.post<JobSearchFilter>('/job-filters', input).then((r) => r.data),
  update: (id: string, input: Partial<JobFilterInput>) =>
    api.patch<JobSearchFilter>(`/job-filters/${id}`, input).then((r) => r.data),
  remove: (id: string) => api.delete(`/job-filters/${id}`).then(() => undefined),
  search: (id: string) => api.post<Job[]>(`/job-filters/${id}/search`).then((r) => r.data),
};

export const jobsApi = {
  list: () => api.get<Job[]>('/jobs').then((r) => r.data),
};
