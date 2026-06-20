import { useState } from 'react';

import type { CompanyInput } from '@/services/companies';
import type { Company } from '@/lib/types';

interface CompanyFormProps {
  initial?: Company;
  submitting?: boolean;
  error?: string | null;
  onSubmit: (values: CompanyInput) => void;
  onCancel: () => void;
}

export function CompanyForm({ initial, submitting, error, onSubmit, onCancel }: CompanyFormProps) {
  const [values, setValues] = useState<CompanyInput>({
    name: initial?.name ?? '',
    website: initial?.website ?? '',
    industry: initial?.industry ?? '',
    location: initial?.location ?? '',
    notes: initial?.notes ?? '',
  });

  function update<K extends keyof CompanyInput>(key: K, value: CompanyInput[K]) {
    setValues((v) => ({ ...v, [key]: value }));
  }

  return (
    <form
      className="stack"
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit({
          ...values,
          website: values.website || null,
          industry: values.industry || null,
          location: values.location || null,
          notes: values.notes || null,
        });
      }}
    >
      {error && <div className="form-error">{error}</div>}
      <div className="field">
        <label className="label">Company name</label>
        <input
          className="input"
          value={values.name}
          onChange={(e) => update('name', e.target.value)}
          required
          autoFocus
        />
      </div>
      <div className="form-row">
        <div className="field">
          <label className="label">Industry</label>
          <input
            className="input"
            value={values.industry ?? ''}
            onChange={(e) => update('industry', e.target.value)}
            placeholder="e.g. Fintech"
          />
        </div>
        <div className="field">
          <label className="label">Location</label>
          <input
            className="input"
            value={values.location ?? ''}
            onChange={(e) => update('location', e.target.value)}
            placeholder="e.g. Remote"
          />
        </div>
      </div>
      <div className="field">
        <label className="label">Website</label>
        <input
          className="input"
          type="url"
          value={values.website ?? ''}
          onChange={(e) => update('website', e.target.value)}
          placeholder="https://example.com"
        />
      </div>
      <div className="field">
        <label className="label">Notes</label>
        <textarea
          className="textarea"
          value={values.notes ?? ''}
          onChange={(e) => update('notes', e.target.value)}
        />
      </div>
      <div className="row" style={{ justifyContent: 'flex-end' }}>
        <button type="button" className="btn btn-secondary" onClick={onCancel}>
          Cancel
        </button>
        <button type="submit" className="btn btn-primary" disabled={submitting}>
          {submitting ? 'Saving…' : 'Save company'}
        </button>
      </div>
    </form>
  );
}
