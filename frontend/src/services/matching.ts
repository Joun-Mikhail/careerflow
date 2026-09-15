import { api } from './api';

import type { JobMatch } from '@/lib/types';

export interface ScoreMatchInput {
  cv_id?: string;
  cv_text?: string;
  job_ids?: string[];
  job_description?: string;
}

export const matchingApi = {
  /** Score a CV against stored jobs and/or an inline description, strongest first. */
  score: (input: ScoreMatchInput) =>
    api
      .post<{ results: JobMatch[] }>('/matching/score', input)
      .then((r) => r.data.results),
};
