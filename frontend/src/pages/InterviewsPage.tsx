import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { EmptyState, ErrorState } from '@/components/feedback/States';
import { TableSkeleton } from '@/components/feedback/Skeletons';
import { CalendarIcon } from '@/components/icons';
import { useApplications } from '@/hooks/useApplications';
import { useAllInterviews } from '@/hooks/useInterviewsAll';
import { formatDateTime, titleCase } from '@/lib/format';
import type { InterviewResult } from '@/lib/types';
import type { InterviewScope } from '@/services/interviews';

const SCOPES: { key: InterviewScope; label: string }[] = [
  { key: 'upcoming', label: 'Upcoming' },
  { key: 'past', label: 'Past' },
  { key: 'all', label: 'All' },
];

const RESULT_COLORS: Record<InterviewResult, string> = {
  pending: '#0ea5e9',
  passed: '#059669',
  failed: '#ef4444',
  cancelled: '#64748b',
};

export function InterviewsPage() {
  const navigate = useNavigate();
  const [scope, setScope] = useState<InterviewScope>('upcoming');
  const { data, isLoading, isError, refetch } = useAllInterviews({ scope, page_size: 100 });
  const { data: applicationData } = useApplications({ page_size: 100 });

  const roleFor = useMemo(() => {
    const map = new Map((applicationData?.items ?? []).map((a) => [a.id, a.role_title]));
    return (id: string) => map.get(id) ?? 'Application';
  }, [applicationData]);

  const interviews = data?.items ?? [];

  return (
    <>
      <div className="page-header">
        <div>
          <h1 className="page-title">Interviews</h1>
          <p className="page-subtitle">Every conversation across your pipeline.</p>
        </div>
      </div>

      <div className="toolbar">
        <div className="row" style={{ gap: 4 }}>
          {SCOPES.map((s) => (
            <button
              key={s.key}
              className={`btn btn-sm ${scope === s.key ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setScope(s.key)}
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>

      <div className="card">
        {isLoading ? (
          <TableSkeleton columns={5} />
        ) : isError ? (
          <ErrorState error={null} onRetry={refetch} />
        ) : interviews.length === 0 ? (
          <EmptyState
            icon={<CalendarIcon />}
            title="No interviews here"
            description="Interviews you schedule on an application appear in this list."
          />
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Role</th>
                  <th>When</th>
                  <th>Round</th>
                  <th>Mode</th>
                  <th>Result</th>
                </tr>
              </thead>
              <tbody>
                {interviews.map((iv) => (
                  <tr
                    key={iv.id}
                    onClick={() => navigate(`/applications/${iv.application_id}`)}
                  >
                    <td style={{ fontWeight: 600 }}>{roleFor(iv.application_id)}</td>
                    <td className="muted">{formatDateTime(iv.scheduled_at)}</td>
                    <td className="muted">{iv.round_type ?? '—'}</td>
                    <td className="muted">{titleCase(iv.mode)}</td>
                    <td>
                      <span className="chip" style={{ color: RESULT_COLORS[iv.result] }}>
                        {titleCase(iv.result)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </>
  );
}
