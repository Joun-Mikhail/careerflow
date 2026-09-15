import { api } from './api';

import type { InterviewQuestion } from '@/lib/types';

export interface InterviewQuestionInput {
  question: string;
  answer?: string | null;
  tags?: string | null;
  application_id?: string | null;
  asked?: boolean;
}

export interface InterviewQuestionFilters {
  tag?: string;
  application_id?: string;
}

export const interviewQuestionsApi = {
  list: (filters: InterviewQuestionFilters = {}) =>
    api
      .get<InterviewQuestion[]>('/interview-questions', { params: filters })
      .then((r) => r.data),
  create: (input: InterviewQuestionInput) =>
    api.post<InterviewQuestion>('/interview-questions', input).then((r) => r.data),
  update: (id: string, input: Partial<InterviewQuestionInput>) =>
    api.patch<InterviewQuestion>(`/interview-questions/${id}`, input).then((r) => r.data),
  remove: (id: string) => api.delete(`/interview-questions/${id}`).then(() => undefined),
};
