import { api } from './api';

import type {
  ConversionRates,
  DashboardSummary,
  IndustryCount,
  MonthCount,
  StatusCount,
} from '@/lib/types';

export const dashboardApi = {
  summary: () => api.get<DashboardSummary>('/dashboard/summary').then((r) => r.data),
};

export const analyticsApi = {
  applicationsByMonth: () =>
    api
      .get<{ items: MonthCount[] }>('/analytics/applications-by-month')
      .then((r) => r.data.items),
  statusDistribution: () =>
    api
      .get<{ items: StatusCount[] }>('/analytics/status-distribution')
      .then((r) => r.data.items),
  industryDistribution: () =>
    api
      .get<{ items: IndustryCount[] }>('/analytics/industry-distribution')
      .then((r) => r.data.items),
  conversion: () => api.get<ConversionRates>('/analytics/conversion').then((r) => r.data),
};
