import type { CSSProperties } from 'react';
import { Link } from 'react-router-dom';

import { EmptyState, ErrorState, LoadingState } from '@/components/feedback/States';
import {
  BriefcaseIcon,
  CalendarIcon,
  CheckSquareIcon,
  DashboardIcon,
} from '@/components/icons';
import { StatusBadge } from '@/components/ui/Badge';
import { useAuth } from '@/contexts/AuthContext';
import { useDashboard } from '@/hooks/useDashboard';
import { formatDate, formatDateTime, relativeFromNow } from '@/lib/format';

export function DashboardPage() {
  const { user } = useAuth();
  const { data, isLoading, isError, refetch } = useDashboard();

  if (isLoading) return <LoadingState />;
  if (isError || !data) return <ErrorState error={null} onRetry={refetch} />;

  const { totals, success_rate, upcoming_interviews, pending_tasks, recent_applications } = data;
  const firstName = user?.full_name?.split(' ')[0] ?? 'there';

  const stats = [
    { label: 'Applications', value: totals.applications, icon: BriefcaseIcon, accent: '#4f46e5' },
    { label: 'Interviews', value: totals.interviews, icon: CalendarIcon, accent: '#0ea5e9' },
    { label: 'Offers', value: totals.offers, icon: DashboardIcon, accent: '#059669' },
    { label: 'Success rate', value: `${success_rate}%`, icon: CheckSquareIcon, accent: '#d97706' },
  ];

  return (
    <>
      <div className="page-header">
        <div>
          <h1 className="page-title">Good to see you, {firstName} 👋</h1>
          <p className="page-subtitle">Here’s where your job search stands today.</p>
        </div>
        <Link to="/applications" className="btn btn-primary">
          <BriefcaseIcon /> View pipeline
        </Link>
      </div>

      <div className="stat-grid">
        {stats.map(({ label, value, icon: Icon, accent }) => (
          <div key={label} className="stat-card" style={{ '--accent': accent } as CSSProperties}>
            <span className="stat-icon">
              <Icon width={20} height={20} />
            </span>
            <span className="stat-label">{label}</span>
            <span className="stat-value">{value}</span>
          </div>
        ))}
      </div>

      <div className="detail-grid">
        <div className="card">
          <div className="card-header">
            <span className="card-title">Recent applications</span>
            <Link to="/applications" className="btn btn-ghost btn-sm">View all</Link>
          </div>
          {recent_applications.length === 0 ? (
            <EmptyState
              icon={<BriefcaseIcon />}
              title="No applications yet"
              description="Add your first application to start tracking your pipeline."
              action={<Link to="/applications" className="btn btn-primary">Add application</Link>}
            />
          ) : (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Role</th>
                    <th>Status</th>
                    <th>Applied</th>
                  </tr>
                </thead>
                <tbody>
                  {recent_applications.map((app) => (
                    <tr key={app.id}>
                      <td style={{ fontWeight: 600 }}>{app.role_title}</td>
                      <td><StatusBadge status={app.status} /></td>
                      <td className="muted">{formatDate(app.applied_at ?? app.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="stack">
          <div className="card">
            <div className="card-header">
              <span className="card-title">Upcoming interviews</span>
            </div>
            <div className="card-body">
              {upcoming_interviews.length === 0 ? (
                <p className="muted">No interviews scheduled.</p>
              ) : (
                <div className="timeline">
                  {upcoming_interviews.map((iv) => (
                    <div key={iv.id} className="timeline-item">
                      <div className="timeline-dot" />
                      <div>
                        <div style={{ fontWeight: 600 }}>{iv.role_title ?? 'Interview'}</div>
                        <div className="subtle">
                          {formatDateTime(iv.scheduled_at)} · {relativeFromNow(iv.scheduled_at)}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <span className="card-title">Pending tasks</span>
              <Link to="/tasks" className="btn btn-ghost btn-sm">View all</Link>
            </div>
            <div className="card-body">
              {pending_tasks.length === 0 ? (
                <p className="muted">You’re all caught up. 🎉</p>
              ) : (
                <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                  {pending_tasks.map((task) => (
                    <li key={task.id} className="row-between">
                      <span className="truncate">{task.title}</span>
                      <span className={`badge badge--${task.priority}`}>{task.priority}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
