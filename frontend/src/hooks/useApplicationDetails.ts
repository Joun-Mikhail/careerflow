import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { queryKeys } from '@/lib/queryClient';
import type { AttachmentKind } from '@/lib/types';
import { attachmentsApi } from '@/services/attachments';
import { interviewsApi } from '@/services/interviews';
import type { InterviewInput } from '@/services/interviews';
import { notesApi } from '@/services/notes';

/* -- Interviews ----------------------------------------------------------- */
export function useInterviews(applicationId: string) {
  return useQuery({
    queryKey: queryKeys.interviews(applicationId),
    queryFn: () => interviewsApi.listForApplication(applicationId),
  });
}

export function useCreateInterview(applicationId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: InterviewInput) => interviewsApi.create(applicationId, input),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.interviews(applicationId) });
      qc.invalidateQueries({ queryKey: queryKeys.dashboard });
    },
  });
}

export function useDeleteInterview(applicationId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => interviewsApi.remove(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.interviews(applicationId) }),
  });
}

/* -- Notes ---------------------------------------------------------------- */
export function useNotes(applicationId: string) {
  return useQuery({
    queryKey: queryKeys.notes(applicationId),
    queryFn: () => notesApi.listForApplication(applicationId),
  });
}

export function useCreateNote(applicationId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: string) => notesApi.create(applicationId, body),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.notes(applicationId) }),
  });
}

export function useDeleteNote(applicationId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => notesApi.remove(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.notes(applicationId) }),
  });
}

/* -- Attachments ---------------------------------------------------------- */
export function useAttachments(applicationId: string) {
  return useQuery({
    queryKey: queryKeys.attachments(applicationId),
    queryFn: () => attachmentsApi.listForApplication(applicationId),
  });
}

export function useUploadAttachment(applicationId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ file, kind }: { file: File; kind: AttachmentKind }) =>
      attachmentsApi.upload(applicationId, file, kind),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.attachments(applicationId) }),
  });
}

export function useDeleteAttachment(applicationId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => attachmentsApi.remove(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.attachments(applicationId) }),
  });
}
