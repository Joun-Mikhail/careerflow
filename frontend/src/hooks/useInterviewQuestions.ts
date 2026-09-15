import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { queryKeys } from '@/lib/queryClient';
import {
  interviewQuestionsApi,
  type InterviewQuestionFilters,
  type InterviewQuestionInput,
} from '@/services/interviewQuestions';

export function useInterviewQuestions(filters: InterviewQuestionFilters = {}) {
  return useQuery({
    queryKey: queryKeys.interviewQuestions(filters),
    queryFn: () => interviewQuestionsApi.list(filters),
  });
}

/** Every mutation invalidates the whole list, since a tag edit can move rows. */
function useInvalidateQuestions() {
  const qc = useQueryClient();
  return () => qc.invalidateQueries({ queryKey: ['interview-questions'] });
}

export function useCreateInterviewQuestion() {
  const invalidate = useInvalidateQuestions();
  return useMutation({
    mutationFn: (input: InterviewQuestionInput) => interviewQuestionsApi.create(input),
    onSuccess: invalidate,
  });
}

export function useUpdateInterviewQuestion() {
  const invalidate = useInvalidateQuestions();
  return useMutation({
    mutationFn: ({ id, input }: { id: string; input: Partial<InterviewQuestionInput> }) =>
      interviewQuestionsApi.update(id, input),
    onSuccess: invalidate,
  });
}

export function useDeleteInterviewQuestion() {
  const invalidate = useInvalidateQuestions();
  return useMutation({
    mutationFn: (id: string) => interviewQuestionsApi.remove(id),
    onSuccess: invalidate,
  });
}
