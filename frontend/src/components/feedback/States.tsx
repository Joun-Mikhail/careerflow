import type { ReactNode } from 'react';

import { ApiError } from '@/services/api';

export function LoadingState({ label = 'Loading…' }: { label?: string }) {
  return (
    <div className="center-state">
      <div className="stack" style={{ alignItems: 'center', gap: 'var(--space-3)' }}>
        <div className="spinner" />
        <span className="muted">{label}</span>
      </div>
    </div>
  );
}

export function ErrorState({ error, onRetry }: { error: unknown; onRetry?: () => void }) {
  const message =
    error instanceof ApiError
      ? error.message
      : 'Something went wrong while loading this view.';
  return (
    <div className="empty-state">
      <h3>Unable to load</h3>
      <p className="muted">{message}</p>
      {onRetry && (
        <button className="btn btn-secondary" onClick={onRetry}>
          Try again
        </button>
      )}
    </div>
  );
}

interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: ReactNode;
}

export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="empty-state">
      {icon && <div className="empty-icon">{icon}</div>}
      <h3>{title}</h3>
      {description && <p className="muted">{description}</p>}
      {action}
    </div>
  );
}

export function CardSkeleton({ rows = 3 }: { rows?: number }) {
  return (
    <div className="stack">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="skeleton" style={{ height: 56 }} />
      ))}
    </div>
  );
}
