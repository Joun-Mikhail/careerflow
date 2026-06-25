import { useRef, useState } from 'react';
import type { FormEvent } from 'react';

import { EmptyState, ErrorState } from '@/components/feedback/States';
import { TableSkeleton } from '@/components/feedback/Skeletons';
import { DownloadIcon, FileTextIcon, PlusIcon, TrashIcon } from '@/components/icons';
import { Modal } from '@/components/ui/Modal';
import { useToast } from '@/contexts/ToastContext';
import {
  useCertificates,
  useCreateCertificate,
  useCreateSkill,
  useCvs,
  useDeleteCertificate,
  useDeleteCv,
  useDeleteSkill,
  useSkills,
  useTailorCv,
  useUpdateCv,
  useUploadCv,
} from '@/hooks/useDocuments';
import { formatBytes, formatDate, titleCase } from '@/lib/format';
import type { Cv, SkillProficiency, TailorCvResult } from '@/lib/types';
import { ApiError } from '@/services/api';
import { cvsApi, downloadFile } from '@/services/documents';

type Tab = 'cvs' | 'certificates' | 'skills';

const TABS: { key: Tab; label: string }[] = [
  { key: 'cvs', label: 'CVs' },
  { key: 'certificates', label: 'Certificates' },
  { key: 'skills', label: 'Skills' },
];

function errorMessage(err: unknown, fallback: string): string {
  return err instanceof ApiError ? err.message : fallback;
}

export function DocumentsPage() {
  const [tab, setTab] = useState<Tab>('cvs');

  return (
    <>
      <div className="page-header">
        <div>
          <h1 className="page-title">Documents</h1>
          <p className="page-subtitle">Your CVs, certificates, and skills — reused across the app.</p>
        </div>
      </div>

      <div className="toolbar">
        <div className="row" style={{ gap: 4 }}>
          {TABS.map((t) => (
            <button
              key={t.key}
              className={`btn btn-sm ${tab === t.key ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setTab(t.key)}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {tab === 'cvs' && <CvsTab />}
      {tab === 'certificates' && <CertificatesTab />}
      {tab === 'skills' && <SkillsTab />}
    </>
  );
}

// --- CVs ---------------------------------------------------------------------

function CvsTab() {
  const toast = useToast();
  const { data, isLoading, isError, refetch } = useCvs();
  const upload = useUploadCv();
  const update = useUpdateCv();
  const remove = useDeleteCv();
  const fileRef = useRef<HTMLInputElement>(null);
  const [title, setTitle] = useState('');
  const [tailorOpen, setTailorOpen] = useState(false);

  async function handleUpload(event: FormEvent) {
    event.preventDefault();
    const file = fileRef.current?.files?.[0];
    if (!file) {
      toast.error('Choose a PDF or DOCX file first.');
      return;
    }
    try {
      await upload.mutateAsync({ file, title: title || undefined });
      toast.success('CV uploaded.');
      setTitle('');
      if (fileRef.current) fileRef.current.value = '';
    } catch (err) {
      toast.error(errorMessage(err, 'Could not upload CV.'));
    }
  }

  const cvs = data ?? [];

  return (
    <>
      <form className="card" onSubmit={handleUpload}>
        <div className="card-body row" style={{ gap: 'var(--space-3)', flexWrap: 'wrap', alignItems: 'flex-end' }}>
          <div className="field" style={{ flex: '1 1 220px' }}>
            <label className="label" htmlFor="cv-title">Title (optional)</label>
            <input id="cv-title" className="input" value={title} placeholder="e.g. Backend Engineer CV"
              onChange={(e) => setTitle(e.target.value)} />
          </div>
          <div className="field" style={{ flex: '1 1 220px' }}>
            <label className="label" htmlFor="cv-file">File (PDF or DOCX)</label>
            <input id="cv-file" ref={fileRef} className="input" type="file" accept=".pdf,.docx" />
          </div>
          <button className="btn btn-primary" type="submit" disabled={upload.isPending}>
            <PlusIcon /> {upload.isPending ? 'Uploading…' : 'Upload CV'}
          </button>
        </div>
      </form>

      <div className="toolbar">
        <span className="muted">Tailor a CV to a specific job with AI.</span>
        <button className="btn btn-secondary" onClick={() => setTailorOpen(true)}>
          ✦ Tailor with AI
        </button>
      </div>

      <div className="card">
        {isLoading ? (
          <TableSkeleton columns={4} />
        ) : isError ? (
          <ErrorState error={null} onRetry={refetch} />
        ) : cvs.length === 0 ? (
          <EmptyState icon={<FileTextIcon />} title="No CVs yet"
            description="Upload your first CV (PDF or DOCX) to reuse it across applications." />
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr><th>Title</th><th>Type</th><th>Size</th><th>Default</th><th></th></tr>
              </thead>
              <tbody>
                {cvs.map((cv) => (
                  <tr key={cv.id}>
                    <td style={{ fontWeight: 600 }}>{cv.title}</td>
                    <td className="muted">{cv.source === 'ai_tailored' ? 'AI-tailored' : 'Uploaded'}</td>
                    <td className="muted">{cv.size_bytes ? formatBytes(cv.size_bytes) : '—'}</td>
                    <td>
                      {cv.is_default ? (
                        <span className="chip" style={{ color: 'var(--success)' }}>Default</span>
                      ) : (
                        <button className="btn btn-ghost btn-sm"
                          onClick={() => update.mutate({ id: cv.id, input: { is_default: true } })}>
                          Set default
                        </button>
                      )}
                    </td>
                    <td>
                      <div className="row" style={{ gap: 4, justifyContent: 'flex-end' }}>
                        {cv.has_file && (
                          <button className="btn btn-ghost btn-sm" title="Download"
                            onClick={() =>
                              downloadFile(cvsApi.downloadUrl(cv.id), cv.original_filename ?? 'cv').catch(() =>
                                toast.error('Download failed.'),
                              )
                            }>
                            <DownloadIcon width={16} height={16} />
                          </button>
                        )}
                        <button className="btn btn-ghost btn-sm" title="Delete"
                          onClick={() => {
                            remove.mutate(cv.id, {
                              onSuccess: () => toast.success('CV deleted.'),
                              onError: (e) => toast.error(errorMessage(e, 'Delete failed.')),
                            });
                          }}>
                          <TrashIcon width={16} height={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <TailorCvModal cvs={cvs} open={tailorOpen} onClose={() => setTailorOpen(false)} />
    </>
  );
}

// --- AI tailoring modal ------------------------------------------------------

function TailorCvModal({ cvs, open, onClose }: { cvs: Cv[]; open: boolean; onClose: () => void }) {
  const toast = useToast();
  const tailor = useTailorCv();
  const textCvs = cvs.filter((c) => !c.has_file); // only text-based CVs can be tailored
  const [cvId, setCvId] = useState('');
  const [cvText, setCvText] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [includeCover, setIncludeCover] = useState(false);
  const [result, setResult] = useState<TailorCvResult | null>(null);
  const [saveTitle, setSaveTitle] = useState('');

  function reset() {
    setResult(null);
    setSaveTitle('');
  }

  async function handleGenerate(save: boolean) {
    if (jobDescription.trim().length < 20) {
      toast.error('Paste a job description (at least 20 characters).');
      return;
    }
    if (!cvId && cvText.trim().length === 0) {
      toast.error('Pick a text CV or paste your CV text.');
      return;
    }
    try {
      const res = await tailor.mutateAsync({
        cv_id: cvId || undefined,
        cv_text: cvText.trim() || undefined,
        job_description: jobDescription,
        include_cover_letter: includeCover,
        save_as_title: save ? saveTitle || 'Tailored CV' : undefined,
      });
      setResult(res);
      if (save && res.saved_cv_id) {
        toast.success('Saved as a new CV.');
        onClose();
        reset();
      }
    } catch (err) {
      toast.error(errorMessage(err, 'Tailoring failed.'));
    }
  }

  return (
    <Modal open={open} title="Tailor a CV with AI" onClose={onClose}>
      <div className="stack" style={{ gap: 'var(--space-3)' }}>
        {textCvs.length > 0 && (
          <div className="field">
            <label className="label" htmlFor="tailor-cv">Base CV (text-based)</label>
            <select id="tailor-cv" className="input" value={cvId}
              onChange={(e) => setCvId(e.target.value)}>
              <option value="">— Paste text instead —</option>
              {textCvs.map((c) => (
                <option key={c.id} value={c.id}>{c.title}</option>
              ))}
            </select>
          </div>
        )}
        {!cvId && (
          <div className="field">
            <label className="label" htmlFor="tailor-text">Your CV text</label>
            <textarea id="tailor-text" className="input" rows={5} value={cvText}
              placeholder="Paste your CV here (uploaded PDFs/DOCX can't be auto-read yet)."
              onChange={(e) => setCvText(e.target.value)} />
          </div>
        )}
        <div className="field">
          <label className="label" htmlFor="tailor-job">Job description</label>
          <textarea id="tailor-job" className="input" rows={5} value={jobDescription}
            placeholder="Paste the job description you're targeting."
            onChange={(e) => setJobDescription(e.target.value)} />
        </div>
        <label className="row" style={{ gap: 8 }}>
          <input type="checkbox" checked={includeCover}
            onChange={(e) => setIncludeCover(e.target.checked)} />
          Also write a cover letter
        </label>

        <button className="btn btn-primary" disabled={tailor.isPending}
          onClick={() => handleGenerate(false)}>
          {tailor.isPending ? 'Generating…' : '✦ Generate'}
        </button>

        {result && (
          <div className="stack" style={{ gap: 'var(--space-3)' }}>
            <div className="field">
              <label className="label">Tailored CV <span className="subtle">· via {result.provider}</span></label>
              <textarea className="input" rows={8} readOnly value={result.tailored_cv} />
            </div>
            {result.cover_letter && (
              <div className="field">
                <label className="label">Cover letter</label>
                <textarea className="input" rows={6} readOnly value={result.cover_letter} />
              </div>
            )}
            <div className="row" style={{ gap: 'var(--space-2)', alignItems: 'flex-end' }}>
              <div className="field" style={{ flex: 1 }}>
                <label className="label" htmlFor="save-title">Save as new CV titled</label>
                <input id="save-title" className="input" value={saveTitle}
                  placeholder="e.g. Tailored — Acme Backend" onChange={(e) => setSaveTitle(e.target.value)} />
              </div>
              <button className="btn btn-primary" disabled={tailor.isPending}
                onClick={() => handleGenerate(true)}>
                Save as new CV
              </button>
            </div>
          </div>
        )}
      </div>
    </Modal>
  );
}

// --- Certificates ------------------------------------------------------------

function CertificatesTab() {
  const toast = useToast();
  const { data, isLoading, isError, refetch } = useCertificates();
  const create = useCreateCertificate();
  const remove = useDeleteCertificate();
  const fileRef = useRef<HTMLInputElement>(null);
  const [name, setName] = useState('');
  const [issuer, setIssuer] = useState('');
  const [issuedOn, setIssuedOn] = useState('');

  async function handleCreate(event: FormEvent) {
    event.preventDefault();
    if (!name.trim()) {
      toast.error('Name is required.');
      return;
    }
    try {
      await create.mutateAsync({
        name: name.trim(),
        issuer: issuer || undefined,
        issued_on: issuedOn || undefined,
        file: fileRef.current?.files?.[0] ?? null,
      });
      toast.success('Certificate added.');
      setName('');
      setIssuer('');
      setIssuedOn('');
      if (fileRef.current) fileRef.current.value = '';
    } catch (err) {
      toast.error(errorMessage(err, 'Could not add certificate.'));
    }
  }

  const certs = data ?? [];

  return (
    <>
      <form className="card" onSubmit={handleCreate}>
        <div className="card-body row" style={{ gap: 'var(--space-3)', flexWrap: 'wrap', alignItems: 'flex-end' }}>
          <div className="field" style={{ flex: '1 1 200px' }}>
            <label className="label" htmlFor="cert-name">Name</label>
            <input id="cert-name" className="input" value={name} placeholder="e.g. AWS Solutions Architect"
              onChange={(e) => setName(e.target.value)} required />
          </div>
          <div className="field" style={{ flex: '1 1 160px' }}>
            <label className="label" htmlFor="cert-issuer">Issuer</label>
            <input id="cert-issuer" className="input" value={issuer}
              onChange={(e) => setIssuer(e.target.value)} />
          </div>
          <div className="field" style={{ flex: '0 1 160px' }}>
            <label className="label" htmlFor="cert-date">Issued on</label>
            <input id="cert-date" className="input" type="date" value={issuedOn}
              onChange={(e) => setIssuedOn(e.target.value)} />
          </div>
          <div className="field" style={{ flex: '1 1 180px' }}>
            <label className="label" htmlFor="cert-file">Proof (optional)</label>
            <input id="cert-file" ref={fileRef} className="input" type="file" accept=".pdf,.docx,.png,.jpg,.jpeg" />
          </div>
          <button className="btn btn-primary" type="submit" disabled={create.isPending}>
            <PlusIcon /> {create.isPending ? 'Adding…' : 'Add'}
          </button>
        </div>
      </form>

      <div className="card">
        {isLoading ? (
          <TableSkeleton columns={4} />
        ) : isError ? (
          <ErrorState error={null} onRetry={refetch} />
        ) : certs.length === 0 ? (
          <EmptyState icon={<FileTextIcon />} title="No certificates yet"
            description="Add your qualifications and credentials here." />
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr><th>Name</th><th>Issuer</th><th>Issued</th><th></th></tr>
              </thead>
              <tbody>
                {certs.map((cert) => (
                  <tr key={cert.id}>
                    <td style={{ fontWeight: 600 }}>{cert.name}</td>
                    <td className="muted">{cert.issuer ?? '—'}</td>
                    <td className="muted">{cert.issued_on ? formatDate(cert.issued_on) : '—'}</td>
                    <td>
                      <div className="row" style={{ gap: 4, justifyContent: 'flex-end' }}>
                        {cert.has_file && (
                          <button className="btn btn-ghost btn-sm" title="Download"
                            onClick={() =>
                              downloadFile(`/certificates/${cert.id}/download`, cert.original_filename ?? 'certificate').catch(() =>
                                toast.error('Download failed.'),
                              )
                            }>
                            <DownloadIcon width={16} height={16} />
                          </button>
                        )}
                        <button className="btn btn-ghost btn-sm" title="Delete"
                          onClick={() =>
                            remove.mutate(cert.id, {
                              onSuccess: () => toast.success('Certificate deleted.'),
                              onError: (e) => toast.error(errorMessage(e, 'Delete failed.')),
                            })
                          }>
                          <TrashIcon width={16} height={16} />
                        </button>
                      </div>
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

// --- Skills ------------------------------------------------------------------

const PROFICIENCIES: SkillProficiency[] = ['beginner', 'intermediate', 'advanced', 'expert'];

function SkillsTab() {
  const toast = useToast();
  const { data, isLoading, isError, refetch } = useSkills();
  const create = useCreateSkill();
  const remove = useDeleteSkill();
  const [name, setName] = useState('');
  const [category, setCategory] = useState('');
  const [proficiency, setProficiency] = useState<SkillProficiency | ''>('');

  async function handleCreate(event: FormEvent) {
    event.preventDefault();
    if (!name.trim()) {
      toast.error('Skill name is required.');
      return;
    }
    try {
      await create.mutateAsync({
        name: name.trim(),
        category: category || null,
        proficiency: proficiency || null,
      });
      toast.success('Skill added.');
      setName('');
      setCategory('');
      setProficiency('');
    } catch (err) {
      toast.error(errorMessage(err, 'Could not add skill.'));
    }
  }

  const skills = data ?? [];

  return (
    <>
      <form className="card" onSubmit={handleCreate}>
        <div className="card-body row" style={{ gap: 'var(--space-3)', flexWrap: 'wrap', alignItems: 'flex-end' }}>
          <div className="field" style={{ flex: '1 1 180px' }}>
            <label className="label" htmlFor="skill-name">Skill</label>
            <input id="skill-name" className="input" value={name} placeholder="e.g. TypeScript"
              onChange={(e) => setName(e.target.value)} required />
          </div>
          <div className="field" style={{ flex: '1 1 160px' }}>
            <label className="label" htmlFor="skill-cat">Category</label>
            <input id="skill-cat" className="input" value={category} placeholder="e.g. Languages"
              onChange={(e) => setCategory(e.target.value)} />
          </div>
          <div className="field" style={{ flex: '0 1 160px' }}>
            <label className="label" htmlFor="skill-prof">Proficiency</label>
            <select id="skill-prof" className="input" value={proficiency}
              onChange={(e) => setProficiency(e.target.value as SkillProficiency | '')}>
              <option value="">—</option>
              {PROFICIENCIES.map((p) => (
                <option key={p} value={p}>{titleCase(p)}</option>
              ))}
            </select>
          </div>
          <button className="btn btn-primary" type="submit" disabled={create.isPending}>
            <PlusIcon /> {create.isPending ? 'Adding…' : 'Add skill'}
          </button>
        </div>
      </form>

      <div className="card">
        <div className="card-body">
          {isLoading ? (
            <TableSkeleton columns={3} />
          ) : isError ? (
            <ErrorState error={null} onRetry={refetch} />
          ) : skills.length === 0 ? (
            <EmptyState icon={<FileTextIcon />} title="No skills yet"
              description="List your skills to power AI CV tailoring later." />
          ) : (
            <div className="row" style={{ gap: 'var(--space-2)', flexWrap: 'wrap' }}>
              {skills.map((skill) => (
                <span key={skill.id} className="chip" style={{ gap: 8 }}>
                  {skill.name}
                  {skill.proficiency && (
                    <span className="subtle">· {titleCase(skill.proficiency)}</span>
                  )}
                  <button className="btn-ghost" title="Remove" style={{ padding: 0, lineHeight: 1 }}
                    onClick={() =>
                      remove.mutate(skill.id, {
                        onError: (e) => toast.error(errorMessage(e, 'Delete failed.')),
                      })
                    }>
                    <TrashIcon width={13} height={13} />
                  </button>
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
