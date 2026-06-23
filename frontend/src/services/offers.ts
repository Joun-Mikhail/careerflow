import { api } from './api';

import type { Offer, OfferDecision, Page } from '@/lib/types';

export interface OfferInput {
  base_salary?: number | null;
  bonus?: number | null;
  equity?: string | null;
  currency?: string | null;
  benefits?: string | null;
  decision?: OfferDecision;
  received_at?: string | null;
  notes?: string | null;
}

export interface OfferListParams {
  page?: number;
  page_size?: number;
  decision?: OfferDecision;
}

export const offersApi = {
  list: (params: OfferListParams = {}) =>
    api.get<Page<Offer>>('/offers', { params }).then((r) => r.data),
  listForApplication: (applicationId: string) =>
    api.get<Offer[]>(`/applications/${applicationId}/offers`).then((r) => r.data),
  create: (applicationId: string, input: OfferInput) =>
    api.post<Offer>(`/applications/${applicationId}/offers`, input).then((r) => r.data),
  update: (id: string, input: OfferInput) =>
    api.patch<Offer>(`/offers/${id}`, input).then((r) => r.data),
  remove: (id: string) => api.delete(`/offers/${id}`).then(() => undefined),
};
