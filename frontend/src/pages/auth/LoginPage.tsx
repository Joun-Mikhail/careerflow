import { useState } from 'react';
import type { FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/contexts/ToastContext';
import { ApiError } from '@/services/api';

const DEMO_EMAIL = 'demo@careerflow.app';
const DEMO_PASSWORD = 'DemoPass123!';

export function LoginPage() {
  const { login } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function doLogin(creds: { email: string; password: string }) {
    setError(null);
    setSubmitting(true);
    try {
      await login(creds);
      toast.success('Welcome back!');
      navigate('/', { replace: true });
    } catch (err) {
      const message = err instanceof ApiError ? err.message : 'Unable to sign in. Please try again.';
      setError(message);
      toast.error(message);
    } finally {
      setSubmitting(false);
    }
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    doLogin({ email, password });
  }

  function handleTryDemo() {
    doLogin({ email: DEMO_EMAIL, password: DEMO_PASSWORD });
  }

  return (
    <form className="auth-card" onSubmit={handleSubmit}>
      <div>
        <h1 className="page-title">Welcome back</h1>
        <p className="muted">Sign in to continue tracking your job search.</p>
      </div>

      {error && <div className="form-error" role="alert">{error}</div>}

      <button
        className="btn btn-primary btn-block"
        type="button"
        disabled={submitting}
        onClick={handleTryDemo}
        style={{ fontSize: '1.05rem', padding: '0.75rem 1rem' }}
      >
        {submitting ? 'Launching demo…' : '▶ Try demo — no signup needed'}
      </button>

      <div className="divider">or sign in with your account</div>

      <div className="field">
        <label className="label" htmlFor="email">Email</label>
        <input
          id="email"
          className="input"
          type="email"
          autoComplete="email"
          placeholder="you@example.com"
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

      <button className="btn btn-secondary btn-block" type="submit" disabled={submitting}>
        {submitting ? 'Signing in…' : 'Sign in'}
      </button>

      <div className="divider" />
      <p className="muted" style={{ textAlign: 'center' }}>
        New to CareerFlow? <Link to="/register" style={{ color: 'var(--brand-600)', fontWeight: 600 }}>Create an account</Link>
      </p>
    </form>
  );
}
