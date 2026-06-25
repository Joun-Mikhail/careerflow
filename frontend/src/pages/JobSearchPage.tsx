import { useState } from 'react';
import type { FormEvent } from 'react';

import { EmptyState, ErrorState } from '@/components/feedback/States';
import { TableSkeleton } from '@/components/feedback/Skeletons';
import { ExternalLinkIcon, PlusIcon, SearchIcon, TrashIcon } from '@/components/icons';
import { useToast } from '@/contexts/ToastContext';
import {
  useCreateJobFilter,
  useDeleteJobFilter,
  useJobFilters,
  useJobs,
  useRunSearch,
} from '@/hooks/useJobs';
import { ApiError } from '@/services/api';

function errorMessage(err: unknown, fallback: string): string {
  return err instanceof ApiError ? err.message : fallback;
}

function salaryLabel(min: number | null, max: number | null): string {
  if (min && max) return `${min.toLocaleString()}–${max.toLocaleString()}`;
  if (min) return `from ${min.toLocaleString()}`;
  if (max) return `up to ${max.toLocaleString()}`;
  return '—';
}

export function JobSearchPage() {
  const toast = useToast();
  const { data: filters, isLoading: filtersLoading } = useJobFilters();
  const { data: jobs, isLoading: jobsLoading, isError, refetch } = useJobs();
  const createFilter = useCreateJobFilter();
  const deleteFilter = useDeleteJobFilter();
  const runSearch = useRunSearch();

  const [name, setName] = useState('');
  const [titleKeywords, setTitleKeywords] = useState('');
  const [locations, setLocations] = useState('');
  const [remote, setRemote] = useState(false);
  const [salaryMin, setSalaryMin] = useState('');

  async function handleCreate(event: FormEvent) {
    event.preventDefault();
    if (!name.trim()) {
      toast.error('Give the filter a name.');
      return;
    }
    try {
      await createFilter.mutateAsync({
        name: name.trim(),
        title_keywords: titleKeywords || null,
        locations: locations || null,
        remote,
        salary_min: salaryMin ? Number(salaryMin) : null,
      });
      toast.success('Filter saved.');
      setName('');
      setTitleKeywords('');
      setLocations('');
      setRemote(false);
      setSalaryMin('');
    } catch (err) {
      toast.error(errorMessage(err, 'Could not save filter.'));
    }
  }

  function handleRun(id: string) {
    runSearch.mutate(id, {
      onSuccess: (results) => toast.success(`Found ${results.length} job${results.length === 1 ? '' : 's'}.`),
      onError: (e) => toast.error(errorMessage(e, 'Search failed.')),
    });
  }

  const savedFilters = filters ?? [];
  const foundJobs = jobs ?? [];

  return (
    <>
      <div className="page-header">
        <div>
          <h1 className="page-title">Job search</h1>
          <p className="page-subtitle">Save search filters and fetch matching jobs.</p>
        </div>
      </div>

      <form className="card" onSubmit={handleCreate}>
        <div className="card-body row" style={{ gap: 'var(--space-3)', flexWrap: 'wrap', alignItems: 'flex-end' }}>
          <div className="field" style={{ flex: '1 1 160px' }}>
            <label className="label" htmlFor="f-name">Filter name</label>
            <input id="f-name" className="input" value={name} placeholder="e.g. Remote backend"
              onChange={(e) => setName(e.target.value)} required />
          </div>
          <div className="field" style={{ flex: '1 1 180px' }}>
            <label className="label" htmlFor="f-title">Role keywords</label>
            <input id="f-title" className="input" value={titleKeywords} placeholder="e.g. Python Engineer"
              onChange={(e) => setTitleKeywords(e.target.value)} />
          </div>
          <div className="field" style={{ flex: '1 1 140px' }}>
            <label className="label" htmlFor="f-loc">Location</label>
            <input id="f-loc" className="input" value={locations} placeholder="e.g. London"
              onChange={(e) => setLocations(e.target.value)} />
          </div>
          <div className="field" style={{ flex: '0 1 130px' }}>
            <label className="label" htmlFor="f-sal">Min salary</label>
            <input id="f-sal" className="input" type="number" min={0} value={salaryMin}
              onChange={(e) => setSalaryMin(e.target.value)} />
          </div>
          <label className="row" style={{ gap: 8, paddingBottom: 8 }}>
            <input type="checkbox" checked={remote} onChange={(e) => setRemote(e.target.checked)} />
            Remote
          </label>
          <button className="btn btn-primary" type="submit" disabled={createFilter.isPending}>
            <PlusIcon /> Save filter
          </button>
        </div>
      </form>

      <div className="card">
        <div className="card-header"><span className="card-title">Saved filters</span></div>
        <div className="card-body">
          {filtersLoading ? (
            <TableSkeleton columns={2} rows={2} />
          ) : savedFilters.length === 0 ? (
            <p className="muted">No filters yet. Create one above to start searching.</p>
          ) : (
            <div className="stack" style={{ gap: 'var(--space-2)' }}>
              {savedFilters.map((f) => (
                <div key={f.id} className="row-between" style={{ gap: 'var(--space-3)' }}>
                  <div>
                    <span style={{ fontWeight: 600 }}>{f.name}</span>{' '}
                    <span className="subtle">
                      {[f.title_keywords, f.locations, f.remote ? 'Remote' : null]
                        .filter(Boolean)
                        .join(' · ') || 'Any role'}
                    </span>
                  </div>
                  <div className="row" style={{ gap: 4 }}>
                    <button className="btn btn-secondary btn-sm" disabled={runSearch.isPending}
                      onClick={() => handleRun(f.id)}>
                      <SearchIcon width={15} height={15} /> Run search
                    </button>
                    <button className="btn btn-ghost btn-sm" title="Delete"
                      onClick={() =>
                        deleteFilter.mutate(f.id, {
                          onError: (e) => toast.error(errorMessage(e, 'Delete failed.')),
                        })
                      }>
                      <TrashIcon width={16} height={16} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="card">
        <div className="card-header"><span className="card-title">Matching jobs</span></div>
        {jobsLoading ? (
          <TableSkeleton columns={4} />
        ) : isError ? (
          <ErrorState error={null} onRetry={refetch} />
        ) : foundJobs.length === 0 ? (
          <EmptyState icon={<SearchIcon />} title="No jobs yet"
            description="Run one of your filters to fetch matching jobs." />
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr><th>Role</th><th>Company</th><th>Location</th><th>Salary</th><th></th></tr>
              </thead>
              <tbody>
                {foundJobs.map((job) => (
                  <tr key={job.id}>
                    <td style={{ fontWeight: 600 }}>{job.title}</td>
                    <td className="muted">{job.company ?? '—'}</td>
                    <td className="muted">{job.remote ? 'Remote' : (job.location ?? '—')}</td>
                    <td className="muted">{salaryLabel(job.salary_min, job.salary_max)}</td>
                    <td>
                      <a className="btn btn-ghost btn-sm" href={job.url} target="_blank"
                        rel="noopener noreferrer" title="Open posting" style={{ justifyContent: 'flex-end' }}>
                        <ExternalLinkIcon width={16} height={16} />
                      </a>
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
