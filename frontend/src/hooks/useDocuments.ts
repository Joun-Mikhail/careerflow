import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { queryKeys } from '@/lib/queryClient';
import { aiApi, type TailorCvInput } from '@/services/ai';
import {
  certificatesApi,
  cvsApi,
  skillsApi,
  type CertificateInput,
  type CvUploadInput,
  type SkillInput,
} from '@/services/documents';

// --- CVs ---------------------------------------------------------------------

export function useCvs() {
  return useQuery({ queryKey: queryKeys.cvs, queryFn: cvsApi.list });
}

export function useUploadCv() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: CvUploadInput) => cvsApi.upload(input),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.cvs }),
  });
}

export function useUpdateCv() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, input }: { id: string; input: { title?: string; is_default?: boolean } }) =>
      cvsApi.update(id, input),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.cvs }),
  });
}

export function useDeleteCv() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => cvsApi.remove(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.cvs }),
  });
}

// --- Certificates ------------------------------------------------------------

export function useCertificates() {
  return useQuery({ queryKey: queryKeys.certificates, queryFn: certificatesApi.list });
}

export function useCreateCertificate() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: CertificateInput) => certificatesApi.create(input),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.certificates }),
  });
}

export function useDeleteCertificate() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => certificatesApi.remove(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.certificates }),
  });
}

// --- Skills ------------------------------------------------------------------

export function useSkills() {
  return useQuery({ queryKey: queryKeys.skills, queryFn: skillsApi.list });
}

export function useCreateSkill() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: SkillInput) => skillsApi.create(input),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.skills }),
  });
}

export function useDeleteSkill() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => skillsApi.remove(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.skills }),
  });
}

// --- AI tailoring ------------------------------------------------------------

export function useTailorCv() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: TailorCvInput) => aiApi.tailorCv(input),
    // A saved tailored CV becomes a new CV — refresh the list.
    onSuccess: (result) => {
      if (result.saved_cv_id) qc.invalidateQueries({ queryKey: queryKeys.cvs });
    },
  });
}
