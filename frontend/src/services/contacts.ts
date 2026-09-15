import { api } from './api';

import type { Contact } from '@/lib/types';

export interface ContactInput {
  name: string;
  role?: string | null;
  email?: string | null;
  phone?: string | null;
  linkedin_url?: string | null;
  notes?: string | null;
  company_id?: string | null;
}

export interface ContactFilters {
  search?: string;
  company_id?: string;
}

export const contactsApi = {
  list: (filters: ContactFilters = {}) =>
    api.get<Contact[]>('/contacts', { params: filters }).then((r) => r.data),
  create: (input: ContactInput) => api.post<Contact>('/contacts', input).then((r) => r.data),
  update: (id: string, input: Partial<ContactInput>) =>
    api.patch<Contact>(`/contacts/${id}`, input).then((r) => r.data),
  remove: (id: string) => api.delete(`/contacts/${id}`).then(() => undefined),
};
