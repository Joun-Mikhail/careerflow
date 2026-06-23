import { api } from './api';

import type { Interview, InterviewMode, InterviewResult, Page } from '@/lib/types';

export interface InterviewInput {
  scheduled_at: string;
  round_type?: string | null;
  interviewer?: string | null;
  mode?: InterviewMode;
  result?: InterviewResult;
  notes?: string | null;
}

export type InterviewScope = 'all' | 'upcoming' | 'past';

export interface InterviewListParams {
  page?: number;
  page_size?: number;
  scope?: InterviewScope;
}

export const interviewsApi = {
  list: (params: InterviewListParams = {}) =>
    api.get<Page<Interview>>('/interviews', { params }).then((r) => r.data),
  listForApplication: (applicationId: string) =>
    api.get<Interview[]>(`/applications/${applicationId}/interviews`).then((r) => r.data),
  create: (applicationId: string, input: InterviewInput) =>
    api
      .post<Interview>(`/applications/${applicationId}/interviews`, input)
      .then((r) => r.data),
  update: (id: string, input: Partial<InterviewInput>) =>
    api.patch<Interview>(`/interviews/${id}`, input).then((r) => r.data),
  remove: (id: string) => api.delete(`/interviews/${id}`).then(() => undefined),
};
