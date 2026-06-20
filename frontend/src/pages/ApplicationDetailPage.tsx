import { useState } from 'react';
import type { ChangeEvent, FormEvent } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';

import { ApplicationForm } from '@/components/forms/ApplicationForm';
import { ErrorState, LoadingState } from '@/components/feedback/States';
import {
  CalendarIcon,
  ChevronLeftIcon,
  ExternalLinkIcon,
  PaperclipIcon,
  PlusIcon,
  TrashIcon,
} from '@/components/icons';
import { StatusBadge } from '@/components/ui/Badge';
import { Modal } from '@/components/ui/Modal';
import { useApplication, useDeleteApplication, useUpdateApplication } from '@/hooks/useApplications';
import {
  useAttachments,
  useCreateInterview,
  useCreateNote,
  useDeleteAttachment,
  useDeleteInterview,
  useDeleteNote,
  useInterviews,
  useNotes,
  useUploadAttachment,
} from '@/hooks/useApplicationDetails';
import { useCompany } from '@/hooks/useCompanies';
import { APPLICATION_STATUSES, INTERVIEW_MODES } from '@/lib/constants';
import {
  formatBytes,
  formatDate,
  formatDateTime,
  statusLabel,
  titleCase,
} from '@/lib/format';
import type { ApplicationStatus, AttachmentKind, InterviewMode } from '@/lib/types';
import { ApiError } from '@/services/api';
import { attachmentsApi } from '@/services/attachments';
import type { ApplicationInput } from '@/services/applications';

export function ApplicationDetailPage() {
  const { id = '' } = useParams();
  const navigate = useNavigate();

  const { data: application, isLoading, isError, refetch } = useApplication(id);
  const { data: company } = useCompany(application?.company_id ?? undefined);
  const updateApplication = useUpdateApplication();
  const deleteApplication = useDeleteApplication();
  const [editing, setEditing] = useState(false);
  const [editError, setEditError] = useState<string | null>(null);

  if (isLoading) return <LoadingState />;
  if (isError || !application) return <ErrorState error={null} onRetry={refetch} />;

  async function handleEdit(values: ApplicationInput) {
    setEditError(null);
    try {
      await updateApplication.mutateAsync({ id, input: values });
      setEditing(false);
    } catch (err) {
      setEditError(err instanceof ApiError ? err.message : 'Could not update application.');
    }
  }

  async function handleDelete() {
    if (!confirm('Delete this application? This cannot be undone.')) return;
    await deleteApplication.mutateAsync(id);
    navigate('/applications', { replace: true });
  }

  return (
    <>
      <Link to="/applications" className="btn btn-ghost btn-sm" style={{ alignSelf: 'flex-start' }}>
        <ChevronLeftIcon width={16} height={16} /> Back to pipeline
      </Link>

      <div className="page-header">
        <div>
          <div className="row" style={{ gap: 'var(--space-3)' }}>
            <h1 className="page-title">{application.role_title}</h1>
            <StatusBadge status={application.status} />
          </div>
          <p className="page-subtitle">{company?.name ?? 'No company linked'}</p>
        </div>
        <div className="row">
          <select
            className="select"
            value={application.status}
            onChange={(e) =>
              updateApplication.mutate({
                id,
                input: { status: e.target.value as ApplicationStatus },
              })
            }
            aria-label="Change status"
            style={{ width: 'auto' }}
          >
            {APPLICATION_STATUSES.map((s) => (
              <option key={s} value={s}>
                {statusLabel(s)}
              </option>
            ))}
          </select>
          <button className="btn btn-secondary" onClick={() => setEditing(true)}>
            Edit
          </button>
          <button className="btn-icon btn-ghost" onClick={handleDelete} aria-label="Delete application">
            <TrashIcon width={18} height={18} />
          </button>
        </div>
      </div>

      <div className="detail-grid">
        <div className="stack">
          <InterviewsSection applicationId={id} />
          <NotesSection applicationId={id} />
          <AttachmentsSection applicationId={id} />
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title">Details</span>
          </div>
          <div className="card-body">
            <dl className="meta-list">
              <dt>Company</dt>
              <dd>{company?.name ?? '—'}</dd>
              <dt>Salary</dt>
              <dd>
                {application.salary_min || application.salary_max
                  ? `${application.salary_min ?? '—'} – ${application.salary_max ?? '—'} ${application.salary_currency ?? ''}`
                  : '—'}
              </dd>
              <dt>Location</dt>
              <dd>{application.is_remote ? 'Remote' : (application.location ?? '—')}</dd>
              <dt>Source</dt>
              <dd>{application.source ?? '—'}</dd>
              <dt>Applied</dt>
              <dd>{formatDate(application.applied_at)}</dd>
            </dl>
            {application.application_url && (
              <a
                className="btn btn-secondary btn-block"
                style={{ marginTop: 'var(--space-4)' }}
                href={application.application_url}
                target="_blank"
                rel="noopener noreferrer"
              >
                View job posting <ExternalLinkIcon width={14} height={14} />
              </a>
            )}
          </div>
        </div>
      </div>

      <Modal open={editing} title="Edit application" onClose={() => setEditing(false)}>
        <ApplicationForm
          initial={application}
          companies={company ? [company] : []}
          submitting={updateApplication.isPending}
          error={editError}
          onSubmit={handleEdit}
          onCancel={() => setEditing(false)}
        />
      </Modal>
    </>
  );
}

/* -- Interviews ----------------------------------------------------------- */
function InterviewsSection({ applicationId }: { applicationId: string }) {
  const { data: interviews = [], isLoading } = useInterviews(applicationId);
  const createInterview = useCreateInterview(applicationId);
  const deleteInterview = useDeleteInterview(applicationId);
  const [open, setOpen] = useState(false);
  const [scheduledAt, setScheduledAt] = useState('');
  const [interviewer, setInterviewer] = useState('');
  const [roundType, setRoundType] = useState('');
  const [mode, setMode] = useState<InterviewMode>('video');

  async function add(e: FormEvent) {
    e.preventDefault();
    await createInterview.mutateAsync({
      scheduled_at: new Date(scheduledAt).toISOString(),
      interviewer: interviewer || null,
      round_type: roundType || null,
      mode,
    });
    setOpen(false);
    setScheduledAt('');
    setInterviewer('');
    setRoundType('');
  }

  return (
    <div className="card">
      <div className="card-header">
        <span className="card-title">Interviews</span>
        <button className="btn btn-secondary btn-sm" onClick={() => setOpen(true)}>
          <PlusIcon width={14} height={14} /> Add
        </button>
      </div>
      <div className="card-body">
        {isLoading ? (
          <p className="muted">Loading…</p>
        ) : interviews.length === 0 ? (
          <p className="muted">No interviews scheduled yet.</p>
        ) : (
          <div className="timeline">
            {interviews.map((iv) => (
              <div key={iv.id} className="timeline-item">
                <div className="timeline-dot" />
                <div className="row-between" style={{ alignItems: 'flex-start' }}>
                  <div>
                    <div style={{ fontWeight: 600 }}>
                      {iv.round_type ?? 'Interview'} · {titleCase(iv.mode)}
                    </div>
                    <div className="subtle">
                      <CalendarIcon width={12} height={12} /> {formatDateTime(iv.scheduled_at)}
                      {iv.interviewer ? ` · ${iv.interviewer}` : ''}
                    </div>
                  </div>
                  <div className="row" style={{ gap: 'var(--space-2)' }}>
                    <span className={`badge badge--${iv.result === 'passed' ? 'offer' : iv.result === 'failed' ? 'rejected' : 'applied'}`}>
                      {iv.result}
                    </span>
                    <button
                      className="btn-icon btn-ghost"
                      aria-label="Delete interview"
                      onClick={() => deleteInterview.mutate(iv.id)}
                    >
                      <TrashIcon width={14} height={14} />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <Modal open={open} title="Add interview" onClose={() => setOpen(false)}>
        <form className="stack" onSubmit={add}>
          <div className="field">
            <label className="label">Date & time</label>
            <input
              className="input"
              type="datetime-local"
              value={scheduledAt}
              onChange={(e) => setScheduledAt(e.target.value)}
              required
            />
          </div>
          <div className="form-row">
            <div className="field">
              <label className="label">Round</label>
              <input
                className="input"
                value={roundType}
                onChange={(e) => setRoundType(e.target.value)}
                placeholder="e.g. Technical screen"
              />
            </div>
            <div className="field">
              <label className="label">Mode</label>
              <select className="select" value={mode} onChange={(e) => setMode(e.target.value as InterviewMode)}>
                {INTERVIEW_MODES.map((m) => (
                  <option key={m} value={m}>
                    {titleCase(m)}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div className="field">
            <label className="label">Interviewer</label>
            <input
              className="input"
              value={interviewer}
              onChange={(e) => setInterviewer(e.target.value)}
              placeholder="e.g. Priya Sharma"
            />
          </div>
          <div className="row" style={{ justifyContent: 'flex-end' }}>
            <button type="button" className="btn btn-secondary" onClick={() => setOpen(false)}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={createInterview.isPending}>
              Add interview
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}

/* -- Notes ---------------------------------------------------------------- */
function NotesSection({ applicationId }: { applicationId: string }) {
  const { data: notes = [], isLoading } = useNotes(applicationId);
  const createNote = useCreateNote(applicationId);
  const deleteNote = useDeleteNote(applicationId);
  const [body, setBody] = useState('');

  async function add(e: FormEvent) {
    e.preventDefault();
    if (!body.trim()) return;
    await createNote.mutateAsync(body.trim());
    setBody('');
  }

  return (
    <div className="card">
      <div className="card-header">
        <span className="card-title">Notes</span>
      </div>
      <div className="card-body stack">
        <form className="stack" onSubmit={add}>
          <textarea
            className="textarea"
            value={body}
            onChange={(e) => setBody(e.target.value)}
            placeholder="Add a note (Markdown supported)…"
            style={{ minHeight: 80 }}
          />
          <div className="row" style={{ justifyContent: 'flex-end' }}>
            <button type="submit" className="btn btn-primary btn-sm" disabled={createNote.isPending}>
              Add note
            </button>
          </div>
        </form>
        {isLoading ? (
          <p className="muted">Loading…</p>
        ) : notes.length === 0 ? (
          <p className="muted">No notes yet.</p>
        ) : (
          notes.map((note) => (
            <div key={note.id} className="card" style={{ background: 'var(--bg-sunken)' }}>
              <div className="card-body">
                <div className="row-between" style={{ alignItems: 'flex-start' }}>
                  <pre
                    style={{
                      whiteSpace: 'pre-wrap',
                      fontFamily: 'inherit',
                      margin: 0,
                      fontSize: '0.9rem',
                    }}
                  >
                    {note.body}
                  </pre>
                  <button
                    className="btn-icon btn-ghost"
                    aria-label="Delete note"
                    onClick={() => deleteNote.mutate(note.id)}
                  >
                    <TrashIcon width={14} height={14} />
                  </button>
                </div>
                <div className="subtle" style={{ marginTop: 'var(--space-2)' }}>
                  {formatDateTime(note.created_at)}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

/* -- Attachments ---------------------------------------------------------- */
function AttachmentsSection({ applicationId }: { applicationId: string }) {
  const { data: attachments = [], isLoading } = useAttachments(applicationId);
  const upload = useUploadAttachment(applicationId);
  const deleteAttachment = useDeleteAttachment(applicationId);
  const [kind, setKind] = useState<AttachmentKind>('resume');
  const [error, setError] = useState<string | null>(null);

  async function onFile(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setError(null);
    try {
      await upload.mutateAsync({ file, kind });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Upload failed.');
    } finally {
      e.target.value = '';
    }
  }

  return (
    <div className="card">
      <div className="card-header">
        <span className="card-title">Attachments</span>
        <div className="row" style={{ gap: 'var(--space-2)' }}>
          <select
            className="select"
            value={kind}
            onChange={(e) => setKind(e.target.value as AttachmentKind)}
            style={{ width: 'auto' }}
          >
            <option value="resume">Resume</option>
            <option value="cover_letter">Cover letter</option>
            <option value="other">Other</option>
          </select>
          <label className="btn btn-secondary btn-sm">
            <PaperclipIcon width={14} height={14} /> Upload
            <input type="file" accept=".pdf,.docx" hidden onChange={onFile} />
          </label>
        </div>
      </div>
      <div className="card-body stack">
        {error && <div className="form-error">{error}</div>}
        {isLoading ? (
          <p className="muted">Loading…</p>
        ) : attachments.length === 0 ? (
          <p className="muted">No documents uploaded. Accepted: PDF, DOCX.</p>
        ) : (
          attachments.map((att) => (
            <div key={att.id} className="row-between">
              <div className="row" style={{ gap: 'var(--space-3)' }}>
                <PaperclipIcon width={16} height={16} />
                <div>
                  <div style={{ fontWeight: 550 }}>{att.original_filename}</div>
                  <div className="subtle">
                    {titleCase(att.kind)} · {formatBytes(att.size_bytes)}
                  </div>
                </div>
              </div>
              <div className="row" style={{ gap: 'var(--space-2)' }}>
                <a
                  className="btn btn-ghost btn-sm"
                  href={attachmentsApi.downloadUrl(att.id)}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Download
                </a>
                <button
                  className="btn-icon btn-ghost"
                  aria-label="Delete attachment"
                  onClick={() => deleteAttachment.mutate(att.id)}
                >
                  <TrashIcon width={14} height={14} />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
