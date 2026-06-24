import { useMemo, useState } from 'react';
import type { FormEvent } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';

import { EmptyState, ErrorState } from '@/components/feedback/States';
import { TableSkeleton } from '@/components/feedback/Skeletons';
import { DollarSignIcon, PlusIcon, TrashIcon } from '@/components/icons';
import { Modal } from '@/components/ui/Modal';
import { useApplications } from '@/hooks/useApplications';
import { useDeleteOffer, useOffers, useUpdateOffer } from '@/hooks/useOffers';
import { OFFER_DECISIONS, OFFER_DECISION_COLORS } from '@/lib/constants';
import { formatDate, formatSalaryRange, titleCase } from '@/lib/format';
import { offerSchema } from '@/lib/schemas';
import type { OfferDecision } from '@/lib/types';
import { ApiError } from '@/services/api';
import { offersApi } from '@/services/offers';

export function OffersPage() {
  const qc = useQueryClient();
  const { data, isLoading, isError, refetch } = useOffers({ page_size: 100 });
  const { data: applicationData } = useApplications({ page_size: 100 });
  const updateOffer = useUpdateOffer();
  const deleteOffer = useDeleteOffer();

  const [creating, setCreating] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const applications = useMemo(() => applicationData?.items ?? [], [applicationData]);
  const roleFor = useMemo(() => {
    const map = new Map(applications.map((a) => [a.id, a.role_title]));
    return (id: string) => map.get(id) ?? 'Application';
  }, [applications]);

  const createOffer = useMutation({
    mutationFn: ({ applicationId, input }: { applicationId: string; input: object }) =>
      offersApi.create(applicationId, input),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['offers'] });
      setCreating(false);
    },
  });

  const offers = data?.items ?? [];

  function handleSubmit(values: {
    application_id: string;
    base_salary: number | null;
    bonus: number | null;
    currency: string;
    equity?: string;
    benefits?: string;
    decision: string;
  }) {
    setFormError(null);
    createOffer.mutate(
      {
        applicationId: values.application_id,
        input: {
          base_salary: values.base_salary,
          bonus: values.bonus,
          currency: values.currency || null,
          equity: values.equity || null,
          benefits: values.benefits || null,
          decision: values.decision as OfferDecision,
        },
      },
      {
        onError: (err) =>
          setFormError(err instanceof ApiError ? err.message : 'Could not save offer.'),
      },
    );
  }

  return (
    <>
      <div className="page-header">
        <div>
          <h1 className="page-title">Offers</h1>
          <p className="page-subtitle">Compensation offers and where each one stands.</p>
        </div>
        <button
          className="btn btn-primary"
          onClick={() => setCreating(true)}
          disabled={applications.length === 0}
          title={applications.length === 0 ? 'Add an application first' : undefined}
        >
          <PlusIcon /> Add offer
        </button>
      </div>

      <div className="card">
        {isLoading ? (
          <TableSkeleton columns={6} />
        ) : isError ? (
          <ErrorState error={null} onRetry={refetch} />
        ) : offers.length === 0 ? (
          <EmptyState
            icon={<DollarSignIcon />}
            title="No offers yet"
            description="When you receive an offer, record its salary, benefits, and your decision here."
          />
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Role</th>
                  <th>Base</th>
                  <th>Bonus</th>
                  <th>Received</th>
                  <th>Decision</th>
                  <th aria-label="Actions" />
                </tr>
              </thead>
              <tbody>
                {offers.map((offer) => (
                  <tr key={offer.id}>
                    <td style={{ fontWeight: 600 }}>{roleFor(offer.application_id)}</td>
                    <td className="muted">
                      {offer.base_salary != null
                        ? formatSalaryRange(offer.base_salary, null, offer.currency)
                        : '—'}
                    </td>
                    <td className="muted">
                      {offer.bonus != null
                        ? formatSalaryRange(offer.bonus, null, offer.currency)
                        : '—'}
                    </td>
                    <td className="muted">{formatDate(offer.received_at)}</td>
                    <td>
                      <select
                        className="select"
                        value={offer.decision}
                        style={{
                          width: 'auto',
                          color: OFFER_DECISION_COLORS[offer.decision],
                          fontWeight: 600,
                        }}
                        onChange={(e) =>
                          updateOffer.mutate({
                            id: offer.id,
                            input: { decision: e.target.value as OfferDecision },
                          })
                        }
                      >
                        {OFFER_DECISIONS.map((d) => (
                          <option key={d} value={d}>
                            {titleCase(d)}
                          </option>
                        ))}
                      </select>
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <button
                        className="btn-icon btn-ghost"
                        aria-label="Delete offer"
                        onClick={() => deleteOffer.mutate(offer.id)}
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

      <Modal open={creating} title="Add offer" onClose={() => setCreating(false)}>
        <OfferForm
          applications={applications.map((a) => ({ id: a.id, label: a.role_title }))}
          submitting={createOffer.isPending}
          error={formError}
          onSubmit={handleSubmit}
          onCancel={() => setCreating(false)}
        />
      </Modal>
    </>
  );
}

interface OfferFormProps {
  applications: { id: string; label: string }[];
  submitting?: boolean;
  error?: string | null;
  onSubmit: (values: {
    application_id: string;
    base_salary: number | null;
    bonus: number | null;
    currency: string;
    equity?: string;
    benefits?: string;
    decision: string;
  }) => void;
  onCancel: () => void;
}

function OfferForm({ applications, submitting, error, onSubmit, onCancel }: OfferFormProps) {
  const [applicationId, setApplicationId] = useState(applications[0]?.id ?? '');
  const [baseSalary, setBaseSalary] = useState('');
  const [bonus, setBonus] = useState('');
  const [currency, setCurrency] = useState('USD');
  const [benefits, setBenefits] = useState('');
  const [decision, setDecision] = useState<OfferDecision>('pending');
  const [localError, setLocalError] = useState<string | null>(null);

  function handle(e: FormEvent) {
    e.preventDefault();
    const parsed = offerSchema.safeParse({
      application_id: applicationId,
      base_salary: baseSalary,
      bonus,
      currency,
      benefits,
      decision,
    });
    if (!parsed.success) {
      setLocalError(parsed.error.issues[0]?.message ?? 'Invalid input.');
      return;
    }
    setLocalError(null);
    onSubmit({
      application_id: parsed.data.application_id,
      base_salary: parsed.data.base_salary,
      bonus: parsed.data.bonus,
      currency: currency.trim(),
      benefits,
      decision,
    });
  }

  return (
    <form className="stack" onSubmit={handle}>
      {(localError || error) && <div className="form-error">{localError ?? error}</div>}
      <div className="field">
        <label className="label">Application</label>
        <select
          className="select"
          value={applicationId}
          onChange={(e) => setApplicationId(e.target.value)}
          required
        >
          {applications.map((a) => (
            <option key={a.id} value={a.id}>
              {a.label}
            </option>
          ))}
        </select>
      </div>
      <div className="form-row">
        <div className="field">
          <label className="label">Base salary</label>
          <input
            className="input"
            type="number"
            min={0}
            value={baseSalary}
            onChange={(e) => setBaseSalary(e.target.value)}
            placeholder="150000"
          />
        </div>
        <div className="field">
          <label className="label">Bonus</label>
          <input
            className="input"
            type="number"
            min={0}
            value={bonus}
            onChange={(e) => setBonus(e.target.value)}
            placeholder="20000"
          />
        </div>
      </div>
      <div className="form-row">
        <div className="field">
          <label className="label">Currency</label>
          <input
            className="input"
            value={currency}
            onChange={(e) => setCurrency(e.target.value)}
            maxLength={3}
          />
        </div>
        <div className="field">
          <label className="label">Decision</label>
          <select
            className="select"
            value={decision}
            onChange={(e) => setDecision(e.target.value as OfferDecision)}
          >
            {OFFER_DECISIONS.map((d) => (
              <option key={d} value={d}>
                {titleCase(d)}
              </option>
            ))}
          </select>
        </div>
      </div>
      <div className="field">
        <label className="label">Benefits</label>
        <textarea
          className="textarea"
          value={benefits}
          onChange={(e) => setBenefits(e.target.value)}
          placeholder="Health, 401k match, 4 weeks PTO…"
        />
      </div>
      <div className="row" style={{ justifyContent: 'flex-end' }}>
        <button type="button" className="btn btn-secondary" onClick={onCancel}>
          Cancel
        </button>
        <button type="submit" className="btn btn-primary" disabled={submitting}>
          {submitting ? 'Saving…' : 'Save offer'}
        </button>
      </div>
    </form>
  );
}
