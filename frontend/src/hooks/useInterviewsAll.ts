import { useQuery } from '@tanstack/react-query';

import { queryKeys } from '@/lib/queryClient';
import { interviewsApi } from '@/services/interviews';
import type { InterviewListParams } from '@/services/interviews';

/** Global, paginated interviews list (across all applications). */
export function useAllInterviews(params: InterviewListParams = {}) {
  return useQuery({
    queryKey: queryKeys.interviewsAll(params),
    queryFn: () => interviewsApi.list(params),
  });
}
