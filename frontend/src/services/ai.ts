import { api } from './api';

import type { TailorCvResult } from '@/lib/types';

export interface TailorCvInput {
  cv_id?: string;
  cv_text?: string;
  job_description: string;
  include_cover_letter?: boolean;
  save_as_title?: string;
}

export const aiApi = {
  tailorCv: (input: TailorCvInput) =>
    api.post<TailorCvResult>('/ai/tailor-cv', input).then((r) => r.data),
};
