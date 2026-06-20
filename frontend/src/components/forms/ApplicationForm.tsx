import { useState } from 'react';

import { APPLICATION_STATUSES } from '@/lib/constants';
import { statusLabel } from '@/lib/format';
import type { Application, ApplicationStatus, Company } from '@/lib/types';
import type { ApplicationInput } from '@/services/applications';

interface ApplicationFormProps {
  initial?: Application;
  companies: Company[];
  submitting?: boolean;
  error?: string | null;
  onSubmit: (values: ApplicationInput) => void;
  onCancel: () => void;
}

function toNumber(value: string): number | null {
  if (value.trim() === '') return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

export function ApplicationForm({
  initial,
  companies,
  submitting,
  error,
  onSubmit,
  onCancel,
}: ApplicationFormProps) {
  const [roleTitle, setRoleTitle] = useState(initial?.role_title ?? '');
  const [status, setStatus] = useState<ApplicationStatus>(initial?.status ?? 'wishlist');
  const [companyId, setCompanyId] = useState(initial?.company_id ?? '');
  const [location, setLocation] = useState(initial?.location ?? '');
  const [isRemote, setIsRemote] = useState(initial?.is_remote ?? false);
  const [salaryMin, setSalaryMin] = useState(initial?.salary_min?.toString() ?? '');
  const [salaryMax, setSalaryMax] = useState(initial?.salary_max?.toString() ?? '');
  const [url, setUrl] = useState(initial?.application_url ?? '');
  const [source, setSource] = useState(initial?.source ?? '');

  return (
    <form
      className="stack"
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit({
          role_title: roleTitle,
          status,
          company_id: companyId || null,
          location: location || null,
          is_remote: isRemote,
          salary_min: toNumber(salaryMin),
          salary_max: toNumber(salaryMax),
          salary_currency: salaryMin || salaryMax ? 'USD' : null,
          application_url: url || null,
          source: source || null,
        });
      }}
    >
      {error && <div className="form-error">{error}</div>}
      <div className="field">
        <label className="label">Role title</label>
        <input
          className="input"
          value={roleTitle}
          onChange={(e) => setRoleTitle(e.target.value)}
          required
          autoFocus
          placeholder="e.g. Senior Backend Engineer"
        />
      </div>
      <div className="form-row">
        <div className="field">
          <label className="label">Company</label>
          <select
            className="select"
            value={companyId}
            onChange={(e) => setCompanyId(e.target.value)}
          >
            <option value="">— None —</option>
            {companies.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label className="label">Status</label>
          <select
            className="select"
            value={status}
            onChange={(e) => setStatus(e.target.value as ApplicationStatus)}
          >
            {APPLICATION_STATUSES.map((s) => (
              <option key={s} value={s}>
                {statusLabel(s)}
              </option>
            ))}
          </select>
        </div>
      </div>
      <div className="form-row">
        <div className="field">
          <label className="label">Salary min</label>
          <input
            className="input"
            type="number"
            min={0}
            value={salaryMin}
            onChange={(e) => setSalaryMin(e.target.value)}
            placeholder="120000"
          />
        </div>
        <div className="field">
          <label className="label">Salary max</label>
          <input
            className="input"
            type="number"
            min={0}
            value={salaryMax}
            onChange={(e) => setSalaryMax(e.target.value)}
            placeholder="150000"
          />
        </div>
      </div>
      <div className="form-row">
        <div className="field">
          <label className="label">Location</label>
          <input
            className="input"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="e.g. Remote"
          />
        </div>
        <div className="field">
          <label className="label">Source</label>
          <input
            className="input"
            value={source}
            onChange={(e) => setSource(e.target.value)}
            placeholder="e.g. LinkedIn"
          />
        </div>
      </div>
      <div className="field">
        <label className="label">Job posting URL</label>
        <input
          className="input"
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://…"
        />
      </div>
      <label className="row" style={{ gap: 'var(--space-2)' }}>
        <input
          type="checkbox"
          checked={isRemote}
          onChange={(e) => setIsRemote(e.target.checked)}
        />
        <span>Remote position</span>
      </label>
      <div className="row" style={{ justifyContent: 'flex-end' }}>
        <button type="button" className="btn btn-secondary" onClick={onCancel}>
          Cancel
        </button>
        <button type="submit" className="btn btn-primary" disabled={submitting}>
          {submitting ? 'Saving…' : 'Save application'}
        </button>
      </div>
    </form>
  );
}
