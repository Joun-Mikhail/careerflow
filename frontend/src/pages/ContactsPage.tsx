import { useState } from 'react';
import type { FormEvent } from 'react';

import { EmptyState, ErrorState } from '@/components/feedback/States';
import { TableSkeleton } from '@/components/feedback/Skeletons';
import { ExternalLinkIcon, PlusIcon, TrashIcon, UsersIcon } from '@/components/icons';
import { useToast } from '@/contexts/ToastContext';
import { useCompanies } from '@/hooks/useCompanies';
import { useContacts, useCreateContact, useDeleteContact } from '@/hooks/useContacts';
import { useDebouncedValue } from '@/hooks/useDebouncedValue';
import { ApiError } from '@/services/api';

function errorMessage(err: unknown, fallback: string): string {
  return err instanceof ApiError ? err.message : fallback;
}

export function ContactsPage() {
  const toast = useToast();
  const [search, setSearch] = useState('');
  const debouncedSearch = useDebouncedValue(search, 300);
  const { data: contacts, isLoading, isError, refetch } = useContacts(
    debouncedSearch.trim() ? { search: debouncedSearch.trim() } : {},
  );
  const { data: companiesPage } = useCompanies({ page: 1, page_size: 100 });
  const createContact = useCreateContact();
  const deleteContact = useDeleteContact();

  const [name, setName] = useState('');
  const [role, setRole] = useState('');
  const [email, setEmail] = useState('');
  const [companyId, setCompanyId] = useState('');

  const companies = companiesPage?.items ?? [];
  const companyName = (id: string | null) =>
    id ? (companies.find((c) => c.id === id)?.name ?? '—') : '—';

  async function handleCreate(event: FormEvent) {
    event.preventDefault();
    if (!name.trim()) {
      toast.error('A name is the one thing a contact needs.');
      return;
    }
    try {
      await createContact.mutateAsync({
        name: name.trim(),
        role: role.trim() || null,
        email: email.trim() || null,
        company_id: companyId || null,
      });
      toast.success('Contact saved.');
      setName('');
      setRole('');
      setEmail('');
      setCompanyId('');
    } catch (err) {
      toast.error(errorMessage(err, 'Could not save that contact.'));
    }
  }

  const found = contacts ?? [];

  return (
    <>
      <div className="page-header">
        <div>
          <h1 className="page-title">Contacts</h1>
          <p className="page-subtitle">
            Recruiters, hiring managers and referrers — and who they belong to.
          </p>
        </div>
      </div>

      <form className="card" onSubmit={handleCreate}>
        <div
          className="card-body row"
          style={{ gap: 'var(--space-3)', flexWrap: 'wrap', alignItems: 'flex-end' }}
        >
          <div className="field" style={{ flex: '1 1 160px' }}>
            <label className="label" htmlFor="c-name">Name</label>
            <input
              id="c-name"
              className="input"
              value={name}
              placeholder="e.g. Dana Reed"
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>
          <div className="field" style={{ flex: '1 1 160px' }}>
            <label className="label" htmlFor="c-role">Role</label>
            <input
              id="c-role"
              className="input"
              value={role}
              placeholder="e.g. Technical Recruiter"
              onChange={(e) => setRole(e.target.value)}
            />
          </div>
          <div className="field" style={{ flex: '1 1 180px' }}>
            <label className="label" htmlFor="c-email">Email</label>
            <input
              id="c-email"
              className="input"
              type="email"
              value={email}
              placeholder="optional"
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div className="field" style={{ flex: '1 1 160px' }}>
            <label className="label" htmlFor="c-company">Company</label>
            <select
              id="c-company"
              className="input"
              value={companyId}
              onChange={(e) => setCompanyId(e.target.value)}
            >
              <option value="">No company</option>
              {companies.map((company) => (
                <option key={company.id} value={company.id}>{company.name}</option>
              ))}
            </select>
          </div>
          <button className="btn btn-primary" type="submit" disabled={createContact.isPending}>
            <PlusIcon /> Add contact
          </button>
        </div>
      </form>

      <div className="card">
        <div className="card-header row-between" style={{ gap: 'var(--space-3)', flexWrap: 'wrap' }}>
          <span className="card-title">People</span>
          <input
            className="input"
            style={{ width: 'auto', minWidth: 200 }}
            value={search}
            placeholder="Search name, role or email"
            aria-label="Search contacts"
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        {isLoading ? (
          <TableSkeleton columns={4} />
        ) : isError ? (
          <ErrorState error={null} onRetry={refetch} />
        ) : found.length === 0 ? (
          <EmptyState
            icon={<UsersIcon />}
            title={debouncedSearch.trim() ? 'No matches' : 'No contacts yet'}
            description={
              debouncedSearch.trim()
                ? 'Try a different name, role or email.'
                : 'Add the recruiter you just spoke to before you forget their name.'
            }
          />
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Name</th><th>Role</th><th>Company</th><th>Email</th><th></th>
                </tr>
              </thead>
              <tbody>
                {found.map((contact) => (
                  <tr key={contact.id}>
                    <td style={{ fontWeight: 600 }}>
                      {contact.name}
                      {contact.linkedin_url && (
                        <a
                          className="subtle"
                          href={contact.linkedin_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          title="Open LinkedIn profile"
                          style={{ marginLeft: 6 }}
                        >
                          <ExternalLinkIcon width={13} height={13} />
                        </a>
                      )}
                    </td>
                    <td className="muted">{contact.role ?? '—'}</td>
                    <td className="muted">{companyName(contact.company_id)}</td>
                    <td className="muted">
                      {contact.email ? (
                        <a href={`mailto:${contact.email}`}>{contact.email}</a>
                      ) : (
                        '—'
                      )}
                    </td>
                    <td>
                      <button
                        className="btn btn-ghost btn-sm"
                        title="Delete"
                        style={{ justifyContent: 'flex-end' }}
                        onClick={() =>
                          deleteContact.mutate(contact.id, {
                            onError: (e) => toast.error(errorMessage(e, 'Delete failed.')),
                          })
                        }
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
    </>
  );
}
