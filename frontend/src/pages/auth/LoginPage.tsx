import { useState } from 'react';
import type { FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import { useAuth } from '@/contexts/AuthContext';
import { ApiError } from '@/services/api';

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('demo@careerflow.app');
  const [password, setPassword] = useState('DemoPass123!');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login({ email, password });
      navigate('/', { replace: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Unable to sign in. Please try again.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="auth-card" onSubmit={handleSubmit}>
      <div>
        <h1 className="page-title">Welcome back</h1>
        <p className="muted">Sign in to continue tracking your job search.</p>
      </div>

      {error && <div className="form-error" role="alert">{error}</div>}

      <div className="field">
        <label className="label" htmlFor="email">Email</label>
        <input
          id="email"
          className="input"
          type="email"
          autoComplete="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </div>

      <div className="field">
        <label className="label" htmlFor="password">Password</label>
        <input
          id="password"
          className="input"
          type="password"
          autoComplete="current-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </div>

      <button className="btn btn-primary btn-block" type="submit" disabled={submitting}>
        {submitting ? 'Signing in…' : 'Sign in'}
      </button>

      <p className="subtle" style={{ textAlign: 'center' }}>
        Demo account is pre-filled — just press Sign in.
      </p>

      <div className="divider" />
      <p className="muted" style={{ textAlign: 'center' }}>
        New to CareerFlow? <Link to="/register" style={{ color: 'var(--brand-600)', fontWeight: 600 }}>Create an account</Link>
      </p>
    </form>
  );
}
