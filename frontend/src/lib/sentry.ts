import * as Sentry from '@sentry/react';

/**
 * Initialise Sentry browser error reporting when a DSN is configured via
 * `VITE_SENTRY_DSN`. A no-op otherwise, so local/dev builds need no setup.
 */
export function initSentry(): void {
  const dsn = import.meta.env.VITE_SENTRY_DSN;
  if (!dsn) return;
  Sentry.init({
    dsn,
    environment: import.meta.env.MODE,
    integrations: [Sentry.browserTracingIntegration()],
    tracesSampleRate: 0.1,
  });
}
