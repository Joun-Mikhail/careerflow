import { useState } from 'react';
import type { FormEvent } from 'react';

import { LogOutIcon } from '@/components/icons';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/contexts/ToastContext';
import { initials } from '@/lib/format';
import { passwordChangeSchema, profileSchema } from '@/lib/schemas';
import { ApiError } from '@/services/api';
import { authApi } from '@/services/auth';

export function SettingsPage() {
  const { user, updateProfile, logout } = useAuth();

  return (
    <>
      <div className="page-header">
        <div>
          <h1 className="page-title">Settings</h1>
          <p className="page-subtitle">Manage your profile and account.</p>
        </div>
      </div>

      <div className="detail-grid">
        <div className="stack">
          <ProfileCard
            fullName={user?.full_name ?? ''}
            email={user?.email ?? ''}
            onSave={updateProfile}
          />
          <PasswordCard />
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title">Account</span>
          </div>
          <div className="card-body stack">
            <div className="row">
              <div className="avatar" style={{ width: 48, height: 48 }}>
                {initials(user?.full_name ?? null, user?.email ?? '')}
              </div>
              <div>
                <div style={{ fontWeight: 600 }}>{user?.full_name ?? 'Your account'}</div>
                <div className="subtle">{user?.email}</div>
              </div>
            </div>
            <hr className="divider" />
            <button className="btn btn-secondary" onClick={logout}>
              <LogOutIcon width={16} height={16} /> Sign out
            </button>
          </div>
        </div>
      </div>
    </>
  );
}

function ProfileCard({
  fullName,
  email,
  onSave,
}: {
  fullName: string;
  email: string;
  onSave: (fullName: string | null) => Promise<void>;
}) {
  const toast = useToast();
  const [value, setValue] = useState(fullName);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSaved(false);
    const parsed = profileSchema.safeParse({ full_name: value });
    if (!parsed.success) {
      setError(parsed.error.issues[0]?.message ?? 'Invalid input.');
      return;
    }
    setSaving(true);
    try {
      await onSave(value.trim() || null);
      setSaved(true);
      toast.success('Profile updated.');
    } catch (err) {
      const message = err instanceof ApiError ? err.message : 'Could not save profile.';
      setError(message);
      toast.error(message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="card">
      <div className="card-header">
        <span className="card-title">Profile</span>
      </div>
      <form className="card-body stack" onSubmit={handleSubmit}>
        {error && <div className="form-error">{error}</div>}
        {saved && <div className="subtle" style={{ color: 'var(--success)' }}>Profile saved.</div>}
        <div className="field">
          <label className="label">Email</label>
          <input className="input" value={email} disabled />
        </div>
        <div className="field">
          <label className="label">Full name</label>
          <input
            className="input"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            placeholder="Your name"
          />
        </div>
        <div className="row" style={{ justifyContent: 'flex-end' }}>
          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? 'Saving…' : 'Save profile'}
          </button>
        </div>
      </form>
    </div>
  );
}

function PasswordCard() {
  const toast = useToast();
  const [current, setCurrent] = useState('');
  const [next, setNext] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState(false);
  const [saving, setSaving] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setDone(false);
    const parsed = passwordChangeSchema.safeParse({
      current_password: current,
      new_password: next,
      confirm_password: confirm,
    });
    if (!parsed.success) {
      setError(parsed.error.issues[0]?.message ?? 'Invalid input.');
      return;
    }
    setSaving(true);
    try {
      await authApi.changePassword({ current_password: current, new_password: next });
      setDone(true);
      setCurrent('');
      setNext('');
      setConfirm('');
      toast.success('Password changed.');
    } catch (err) {
      const message = err instanceof ApiError ? err.message : 'Could not change password.';
      setError(message);
      toast.error(message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="card">
      <div className="card-header">
        <span className="card-title">Change password</span>
      </div>
      <form className="card-body stack" onSubmit={handleSubmit}>
        {error && <div className="form-error">{error}</div>}
        {done && (
          <div className="subtle" style={{ color: 'var(--success)' }}>Password updated.</div>
        )}
        <div className="field">
          <label className="label">Current password</label>
          <input
            className="input"
            type="password"
            value={current}
            onChange={(e) => setCurrent(e.target.value)}
            autoComplete="current-password"
          />
        </div>
        <div className="form-row">
          <div className="field">
            <label className="label">New password</label>
            <input
              className="input"
              type="password"
              value={next}
              onChange={(e) => setNext(e.target.value)}
              autoComplete="new-password"
            />
          </div>
          <div className="field">
            <label className="label">Confirm</label>
            <input
              className="input"
              type="password"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              autoComplete="new-password"
            />
          </div>
        </div>
        <div className="row" style={{ justifyContent: 'flex-end' }}>
          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? 'Updating…' : 'Update password'}
          </button>
        </div>
      </form>
    </div>
  );
}
