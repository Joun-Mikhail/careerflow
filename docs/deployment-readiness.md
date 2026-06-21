# Deployment Readiness Report

Pre-deployment audit of CareerFlow for a **Vercel (frontend) + Railway
(backend) + Neon (PostgreSQL)** topology. Each area was reviewed against the
running code; issues found are marked **Fixed** with the change, or **Action**
where the step belongs to the deploying operator.

## Summary

Three real, deploy-blocking issues were found and fixed in code; the rest are
configuration the operator supplies at deploy time. The application is ready to
deploy once the platform accounts and environment variables are in place.

## Audit

### Environment variables — ✅ OK
- All config is env-driven via a typed `Settings` (`app/core/config.py`); no
  secrets are read from anywhere else.
- `.env` is gitignored; `.env.example` (backend, frontend, root) documents every
  variable. No secrets are committed.

### Dockerfiles — ⚠️ Fixed
- **Issue:** the backend image hard-coded `--port 8000` in an exec-form `CMD`,
  so Railway's injected `$PORT` was ignored and its health check would fail.
  **Fix:** `CMD` is now a shell form honouring `${PORT:-8000}`.
- Backend runs as a non-root user; deps are layer-cached; the entrypoint applies
  migrations before serving. Frontend image builds the SPA and serves it via
  Nginx.

### CORS — ⚠️ Fixed
- **Issue:** `allow_credentials=True` combined with `allow_headers=["*"]` is
  invalid under the CORS spec and breaks cross-origin preflight (Vercel → Railway).
  **Fix:** credentials disabled (auth uses a Bearer header, not cookies), so
  wildcard headers are valid again.
- **Action:** set `CORS_ORIGINS` on the backend to the deployed frontend origin
  (e.g. `https://careerflow.vercel.app`).

### JWT — ✅ OK / Action
- Signed HS256 tokens with `exp`/`iat`; short default lifetime.
- The app **refuses to boot** in `production` if `JWT_SECRET` is a placeholder
  (`Settings.validate_for_runtime`).
- **Action:** set a strong `JWT_SECRET` (`python -c "import secrets; print(secrets.token_urlsafe(48))"`).

### Production settings — ✅ Fixed/OK
- `DEBUG` defaults to `False`; `CAREERFLOW_ENV` defaults to `local`.
- **Added:** `Strict-Transport-Security` header is emitted when
  `CAREERFLOW_ENV=production`. Existing headers: `X-Content-Type-Options`,
  `X-Frame-Options`, `Referrer-Policy`.
- **Action:** set `CAREERFLOW_ENV=production` and `DEBUG=false` on the backend.

### File uploads — ⚠️ Known limitation (Action)
- Attachments are written to local disk (`var/uploads`). On Railway's ephemeral
  filesystem these are lost on redeploy.
  **Action:** attach a Railway **Volume** mounted at `/app/var/uploads` to
  persist them, or migrate to object storage (tracked in *Future improvements*).
  All other features are fully stateless and need no volume.

### Database migrations — ✅ OK
- Alembic migration is reversible and applied automatically on container start.
- **Action:** Neon connection strings come as `postgres://…`; rewrite the scheme
  to `postgresql+psycopg://…` for `DATABASE_URL`.

### Secrets / hardcoded values / localhost — ✅ OK
- No hardcoded credentials. The only `localhost` references are the **dev/preview**
  Vite proxy and the default `CORS_ORIGINS` fallback — both overridden by env in
  production. The demo password is a documented public demo credential, flagged
  with `# nosec`.

## Changes applied in this audit

| File | Change |
| --- | --- |
| `backend/Dockerfile` | `CMD` honours `$PORT` (Railway). |
| `backend/app/main.py` | CORS `allow_credentials=False`; HSTS in production. |
| `frontend/vercel.json` | Vite build + SPA-fallback rewrite. |
| `backend/railway.json` | Dockerfile build + `/health` health check. |

## Verification after fixes

- Backend: `ruff` ✅, `mypy` ✅ (65 files), `pytest` ✅ (86 tests).
- The deploy steps themselves are in [deploy-runbook.md](deploy-runbook.md).
