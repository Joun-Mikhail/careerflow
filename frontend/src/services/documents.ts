import { api } from './api';

import type { Certificate, Cv, Skill, SkillProficiency } from '@/lib/types';

// --- CVs ---------------------------------------------------------------------

export interface CvUploadInput {
  file: File;
  title?: string;
  makeDefault?: boolean;
}

export const cvsApi = {
  list: () => api.get<Cv[]>('/cvs').then((r) => r.data),
  upload: ({ file, title, makeDefault }: CvUploadInput) => {
    const form = new FormData();
    form.append('file', file);
    if (title) form.append('title', title);
    if (makeDefault) form.append('make_default', 'true');
    return api
      .post<Cv>('/cvs', form, { headers: { 'Content-Type': 'multipart/form-data' } })
      .then((r) => r.data);
  },
  update: (id: string, input: { title?: string; is_default?: boolean }) =>
    api.patch<Cv>(`/cvs/${id}`, input).then((r) => r.data),
  remove: (id: string) => api.delete(`/cvs/${id}`).then(() => undefined),
  downloadUrl: (id: string) => `/cvs/${id}/download`,
};

// --- Certificates ------------------------------------------------------------

export interface CertificateInput {
  name: string;
  issuer?: string;
  issued_on?: string;
  credential_url?: string;
  file?: File | null;
}

export const certificatesApi = {
  list: () => api.get<Certificate[]>('/certificates').then((r) => r.data),
  create: (input: CertificateInput) => {
    const form = new FormData();
    form.append('name', input.name);
    if (input.issuer) form.append('issuer', input.issuer);
    if (input.issued_on) form.append('issued_on', input.issued_on);
    if (input.credential_url) form.append('credential_url', input.credential_url);
    if (input.file) form.append('file', input.file);
    return api
      .post<Certificate>('/certificates', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      .then((r) => r.data);
  },
  remove: (id: string) => api.delete(`/certificates/${id}`).then(() => undefined),
};

// --- Skills ------------------------------------------------------------------

export interface SkillInput {
  name: string;
  category?: string | null;
  proficiency?: SkillProficiency | null;
}

export const skillsApi = {
  list: () => api.get<Skill[]>('/skills').then((r) => r.data),
  create: (input: SkillInput) => api.post<Skill>('/skills', input).then((r) => r.data),
  update: (id: string, input: Partial<SkillInput>) =>
    api.patch<Skill>(`/skills/${id}`, input).then((r) => r.data),
  remove: (id: string) => api.delete(`/skills/${id}`).then(() => undefined),
};

/**
 * Download an owner-only file (CV/certificate) through the authenticated axios
 * client, then trigger a browser save. A plain `<a href>` can't send the bearer
 * token, so we fetch the blob and synthesize the download.
 */
export async function downloadFile(path: string, filename: string): Promise<void> {
  const response = await api.get(path, { responseType: 'blob' });
  const url = URL.createObjectURL(response.data as Blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
