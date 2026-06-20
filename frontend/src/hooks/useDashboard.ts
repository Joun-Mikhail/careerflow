import { useQuery } from '@tanstack/react-query';

import { queryKeys } from '@/lib/queryClient';
import { analyticsApi, dashboardApi } from '@/services/analytics';

export function useDashboard() {
  return useQuery({
    queryKey: queryKeys.dashboard,
    queryFn: () => dashboardApi.summary(),
  });
}

export function useAnalytics() {
  return useQuery({
    queryKey: queryKeys.analytics,
    queryFn: async () => {
      const [byMonth, byStatus, byIndustry, conversion] = await Promise.all([
        analyticsApi.applicationsByMonth(),
        analyticsApi.statusDistribution(),
        analyticsApi.industryDistribution(),
        analyticsApi.conversion(),
      ]);
      return { byMonth, byStatus, byIndustry, conversion };
    },
  });
}
