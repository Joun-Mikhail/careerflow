import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

import { ErrorState, LoadingState } from '@/components/feedback/States';
import { useAnalytics } from '@/hooks/useDashboard';
import { STATUS_COLORS } from '@/lib/constants';
import { statusLabel, titleCase } from '@/lib/format';
import type { ApplicationStatus } from '@/lib/types';

const BRAND = '#4f46e5';

function monthLabel(month: string): string {
  const [year, m] = month.split('-');
  const date = new Date(Number(year), Number(m) - 1, 1);
  return date.toLocaleDateString(undefined, { month: 'short' });
}

export function AnalyticsPage() {
  const { data, isLoading, isError, refetch } = useAnalytics();

  if (isLoading) return <LoadingState />;
  if (isError || !data) return <ErrorState error={null} onRetry={refetch} />;

  const { byMonth, byStatus, byIndustry, conversion } = data;
  const monthData = byMonth.map((m) => ({ ...m, label: monthLabel(m.month) }));
  const statusData = byStatus
    .filter((s) => s.count > 0)
    .map((s) => ({ ...s, label: statusLabel(s.status as ApplicationStatus) }));

  return (
    <>
      <div className="page-header">
        <div>
          <h1 className="page-title">Analytics</h1>
          <p className="page-subtitle">Understand where your search is gaining traction.</p>
        </div>
      </div>

      <div className="stat-grid">
        <div className="stat-card">
          <span className="stat-label">Total applications</span>
          <span className="stat-value">{conversion.total_applications}</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Interview rate</span>
          <span className="stat-value">{conversion.interview_rate}%</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Offer rate</span>
          <span className="stat-value">{conversion.offer_rate}%</span>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <span className="card-title">Applications over the last 12 months</span>
        </div>
        <div className="card-body" style={{ height: 300 }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={monthData} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
              <defs>
                <linearGradient id="appsGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={BRAND} stopOpacity={0.35} />
                  <stop offset="100%" stopColor={BRAND} stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
              <XAxis dataKey="label" tick={{ fontSize: 12 }} stroke="var(--text-subtle)" />
              <YAxis allowDecimals={false} tick={{ fontSize: 12 }} stroke="var(--text-subtle)" />
              <Tooltip
                contentStyle={{
                  background: 'var(--bg-elevated)',
                  border: '1px solid var(--border)',
                  borderRadius: 8,
                  color: 'var(--text)',
                }}
              />
              <Area
                type="monotone"
                dataKey="count"
                name="Applications"
                stroke={BRAND}
                strokeWidth={2}
                fill="url(#appsGradient)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="detail-grid">
        <div className="card">
          <div className="card-header">
            <span className="card-title">Status distribution</span>
          </div>
          <div className="card-body" style={{ height: 300 }}>
            {statusData.length === 0 ? (
              <p className="muted">No applications to chart yet.</p>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={statusData}
                    dataKey="count"
                    nameKey="label"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={2}
                  >
                    {statusData.map((entry) => (
                      <Cell
                        key={entry.status}
                        fill={STATUS_COLORS[entry.status as ApplicationStatus] ?? BRAND}
                      />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      background: 'var(--bg-elevated)',
                      border: '1px solid var(--border)',
                      borderRadius: 8,
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title">Applications by industry</span>
          </div>
          <div className="card-body" style={{ height: 300 }}>
            {byIndustry.length === 0 ? (
              <p className="muted">Link companies with industries to see this chart.</p>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={byIndustry.map((i) => ({ ...i, label: titleCase(i.industry) }))}
                  layout="vertical"
                  margin={{ top: 4, right: 8, left: 8, bottom: 0 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" horizontal={false} />
                  <XAxis type="number" allowDecimals={false} tick={{ fontSize: 12 }} stroke="var(--text-subtle)" />
                  <YAxis
                    type="category"
                    dataKey="label"
                    width={110}
                    tick={{ fontSize: 12 }}
                    stroke="var(--text-subtle)"
                  />
                  <Tooltip
                    contentStyle={{
                      background: 'var(--bg-elevated)',
                      border: '1px solid var(--border)',
                      borderRadius: 8,
                    }}
                    cursor={{ fill: 'var(--surface-hover)' }}
                  />
                  <Bar dataKey="count" name="Applications" fill={BRAND} radius={[0, 6, 6, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
