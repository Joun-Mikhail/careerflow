import { api } from './api';

import type { Attachment, AttachmentKind } from '@/lib/types';

export const attachmentsApi = {
  listForApplication: (applicationId: string) =>
    api
      .get<Attachment[]>(`/applications/${applicationId}/attachments`)
      .then((r) => r.data),
  upload: (applicationId: string, file: File, kind: AttachmentKind) => {
    const form = new FormData();
    form.append('file', file);
    form.append('kind', kind);
    return api
      .post<Attachment>(`/applications/${applicationId}/attachments`, form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      .then((r) => r.data);
  },
  downloadUrl: (id: string) => `${api.defaults.baseURL}/attachments/${id}/download`,
  remove: (id: string) => api.delete(`/attachments/${id}`).then(() => undefined),
};
