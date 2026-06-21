import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { ApplicationForm } from '@/components/forms/ApplicationForm';
import { EmptyState, ErrorState, LoadingState } from '@/components/feedback/States';
import { BriefcaseIcon, MapPinIcon, PlusIcon, SearchIcon } from '@/components/icons';
import { StatusBadge } from '@/components/ui/Badge';
import { Modal } from '@/components/ui/Modal';
import { useApplications, useCreateApplication } from '@/hooks/useApplications';
import { useCompanies } from '@/hooks/useCompanies';
import { useDebouncedValue } from '@/hooks/useDebouncedValue';
import { PIPELINE_STATUSES } from '@/lib/constants';
import { formatSalaryRange, statusLabel } from '@/lib/format';
import type { Application, ApplicationStatus } from '@/lib/types';
import { ApiError } from '@/services/api';
import type { ApplicationInput } from '@/services/applications';

type View = 'board' | 'list';

export function ApplicationsPage() {
  const navigate = useNavigate();
  const [view, setView] = useState<View>('board');
  const [search, setSearch] = useState('');
  const debouncedSearch = useDebouncedValue(search, 300);
  const [creating, setCreating] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const { data, isLoading, isError, refetch } = useApplications({
    q: debouncedSearch || undefined,
    page_size: 100,
  });
  const { data: companyData } = useCompanies({ page_size: 100, sort: 'name', order: 'asc' });
  const createApplication = useCreateApplication();

  const companies = useMemo(() => companyData?.items ?? [], [companyData]);
  const companyName = useMemo(() => {
    const map = new Map(companies.map((c) => [c.id, c.name]));
    return (id: string | null) => (id ? (map.get(id) ?? 'Unknown company') : 'No company');
  }, [companies]);

  const applications = useMemo(() => data?.items ?? [], [data]);
  const byStatus = useMemo(() => {
    const groups = new Map<ApplicationStatus, Application[]>();
    for (const status of PIPELINE_STATUSES) groups.set(status, []);
    for (const app of applications) {
      if (!groups.has(app.status)) groups.set(app.status, []);
      groups.get(app.status)!.push(app);
    }
    return groups;
  }, [applications]);

  async function handleCreate(values: ApplicationInput) {
    setFormError(null);
    try {
      await createApplication.mutateAsync(values);
      setCreating(false);
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : 'Could not create application.');
    }
  }

  return (
    <>
      <div className="page-header">
        <div>
          <h1 className="page-title">Applications</h1>
          <p className="page-subtitle">Your pipeline from wishlist to offer.</p>
        </div>
        <button className="btn btn-primary" onClick={() => setCreating(true)}>
          <PlusIcon /> Add application
        </button>
      </div>

      <div className="toolbar">
        <div className="search">
          <SearchIcon />
          <input
            className="input"
            placeholder="Search by role…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="row" style={{ gap: 4 }}>
          <button
            className={`btn btn-sm ${view === 'board' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setView('board')}
          >
            Board
          </button>
          <button
            className={`btn btn-sm ${view === 'list' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setView('list')}
          >
            List
          </button>
        </div>
      </div>

      {isLoading ? (
        <LoadingState />
      ) : isError ? (
        <ErrorState error={null} onRetry={refetch} />
      ) : applications.length === 0 ? (
        <div className="card">
          <EmptyState
            icon={<BriefcaseIcon />}
            title="No applications yet"
            description="Track your first role to start building your pipeline."
            action={
              <button className="btn btn-primary" onClick={() => setCreating(true)}>
                Add application
              </button>
            }
          />
        </div>
      ) : view === 'board' ? (
        <div className="kanban">
          {PIPELINE_STATUSES.map((status) => {
            const items = byStatus.get(status) ?? [];
            return (
              <div key={status} className="kanban-col">
                <div className="kanban-col-header">
                  <span>{statusLabel(status)}</span>
                  <span className="kanban-count">{items.length}</span>
                </div>
                {items.map((app) => (
                  <button
                    key={app.id}
                    className="kanban-card"
                    style={{ textAlign: 'left' }}
                    onClick={() => navigate(`/applications/${app.id}`)}
                  >
                    <span style={{ fontWeight: 600 }}>{app.role_title}</span>
                    <span className="subtle">{companyName(app.company_id)}</span>
                    <div className="row" style={{ gap: 6, flexWrap: 'wrap' }}>
                      {app.is_remote && <span className="chip">Remote</span>}
                      {app.location && (
                        <span className="chip">
                          <MapPinIcon width={12} height={12} /> {app.location}
                        </span>
                      )}
                    </div>
                    {(app.salary_min || app.salary_max) && (
                      <span className="subtle">
                        {formatSalaryRange(app.salary_min, app.salary_max, app.salary_currency)}
                      </span>
                    )}
                  </button>
                ))}
              </div>
            );
          })}
        </div>
      ) : (
        <div className="card">
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Role</th>
                  <th>Company</th>
                  <th>Status</th>
                  <th>Salary</th>
                  <th>Location</th>
                </tr>
              </thead>
              <tbody>
                {applications.map((app) => (
                  <tr key={app.id} onClick={() => navigate(`/applications/${app.id}`)}>
                    <td style={{ fontWeight: 600 }}>{app.role_title}</td>
                    <td className="muted">{companyName(app.company_id)}</td>
                    <td><StatusBadge status={app.status} /></td>
                    <td className="muted">
                      {formatSalaryRange(app.salary_min, app.salary_max, app.salary_currency)}
                    </td>
                    <td className="muted">
                      {app.is_remote ? 'Remote' : (app.location ?? '—')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <Modal open={creating} title="Add application" onClose={() => setCreating(false)}>
        <ApplicationForm
          companies={companies}
          submitting={createApplication.isPending}
          error={formError}
          onSubmit={handleCreate}
          onCancel={() => setCreating(false)}
        />
      </Modal>
    </>
  );
}
