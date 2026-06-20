import { useState } from 'react';

import { CompanyForm } from '@/components/forms/CompanyForm';
import { EmptyState, ErrorState, LoadingState } from '@/components/feedback/States';
import { BuildingIcon, ExternalLinkIcon, PlusIcon, SearchIcon, TrashIcon } from '@/components/icons';
import { Modal } from '@/components/ui/Modal';
import {
  useCompanies,
  useCreateCompany,
  useDeleteCompany,
  useUpdateCompany,
} from '@/hooks/useCompanies';
import { useDebouncedValue } from '@/hooks/useDebouncedValue';
import type { Company } from '@/lib/types';
import { ApiError } from '@/services/api';
import type { CompanyInput } from '@/services/companies';

export function CompaniesPage() {
  const [search, setSearch] = useState('');
  const debouncedSearch = useDebouncedValue(search, 300);
  const [editing, setEditing] = useState<Company | null>(null);
  const [creating, setCreating] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const { data, isLoading, isError, refetch } = useCompanies({
    q: debouncedSearch || undefined,
    sort: 'name',
    order: 'asc',
    page_size: 50,
  });
  const createCompany = useCreateCompany();
  const updateCompany = useUpdateCompany();
  const deleteCompany = useDeleteCompany();

  const closeModal = () => {
    setCreating(false);
    setEditing(null);
    setFormError(null);
  };

  async function handleSubmit(values: CompanyInput) {
    setFormError(null);
    try {
      if (editing) {
        await updateCompany.mutateAsync({ id: editing.id, input: values });
      } else {
        await createCompany.mutateAsync(values);
      }
      closeModal();
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : 'Could not save company.');
    }
  }

  const companies = data?.items ?? [];

  return (
    <>
      <div className="page-header">
        <div>
          <h1 className="page-title">Companies</h1>
          <p className="page-subtitle">Organizations you’re tracking or applying to.</p>
        </div>
        <button className="btn btn-primary" onClick={() => setCreating(true)}>
          <PlusIcon /> Add company
        </button>
      </div>

      <div className="toolbar">
        <div className="search">
          <SearchIcon />
          <input
            className="input"
            placeholder="Search companies…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      <div className="card">
        {isLoading ? (
          <LoadingState />
        ) : isError ? (
          <ErrorState error={null} onRetry={refetch} />
        ) : companies.length === 0 ? (
          <EmptyState
            icon={<BuildingIcon />}
            title="No companies yet"
            description="Add the companies you’re interested in to link them to applications."
            action={
              <button className="btn btn-primary" onClick={() => setCreating(true)}>
                Add your first company
              </button>
            }
          />
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Industry</th>
                  <th>Location</th>
                  <th>Website</th>
                  <th aria-label="Actions" />
                </tr>
              </thead>
              <tbody>
                {companies.map((company) => (
                  <tr key={company.id} onClick={() => setEditing(company)}>
                    <td style={{ fontWeight: 600 }}>{company.name}</td>
                    <td className="muted">{company.industry ?? '—'}</td>
                    <td className="muted">{company.location ?? '—'}</td>
                    <td onClick={(e) => e.stopPropagation()}>
                      {company.website ? (
                        <a
                          className="row"
                          style={{ color: 'var(--brand-600)', gap: 6 }}
                          href={company.website}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          Visit <ExternalLinkIcon width={14} height={14} />
                        </a>
                      ) : (
                        '—'
                      )}
                    </td>
                    <td onClick={(e) => e.stopPropagation()} style={{ textAlign: 'right' }}>
                      <button
                        className="btn-icon btn-ghost"
                        aria-label={`Delete ${company.name}`}
                        onClick={() => {
                          if (confirm(`Delete ${company.name}?`)) deleteCompany.mutate(company.id);
                        }}
                      >
                        <TrashIcon width={16} height={16} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <Modal
        open={creating || editing !== null}
        title={editing ? 'Edit company' : 'Add company'}
        onClose={closeModal}
      >
        <CompanyForm
          initial={editing ?? undefined}
          submitting={createCompany.isPending || updateCompany.isPending}
          error={formError}
          onSubmit={handleSubmit}
          onCancel={closeModal}
        />
      </Modal>
    </>
  );
}
