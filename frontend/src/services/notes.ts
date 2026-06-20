import { api } from './api';

import type { Note } from '@/lib/types';

export const notesApi = {
  listForApplication: (applicationId: string) =>
    api.get<Note[]>(`/applications/${applicationId}/notes`).then((r) => r.data),
  create: (applicationId: string, body: string) =>
    api.post<Note>(`/applications/${applicationId}/notes`, { body }).then((r) => r.data),
  update: (id: string, body: string) =>
    api.patch<Note>(`/notes/${id}`, { body }).then((r) => r.data),
  remove: (id: string) => api.delete(`/notes/${id}`).then(() => undefined),
};
