# Deployment Guide

CareerFlow is container-first, so the same images you run locally with
`docker compose up` are what you deploy. This guide covers the three pieces —
**database**, **backend**, and **frontend** — for the common hosting options,
plus a production checklist.

> These are real, provider-agnostic instructions. No managed instance is
> provisioned by this repository; you supply the hosting and credentials.

## Architecture recap

In production, Nginx (the frontend image) serves the built SPA and reverse-
proxies `/api` to the backend, so the browser talks to a single origin. The
backend connects to PostgreSQL and writes uploads to a persistent volume.

```
Browser ──▶ Frontend (Nginx: static + /api proxy) ──▶ Backend (FastAPI) ──▶ PostgreSQL
```

## 1. Database (PostgreSQL)

Use any PostgreSQL 14+ instance. Managed options keep this simple:

- **Neon**, **Supabase**, **Railway**, **Render PostgreSQL**, or **AWS RDS**.

Create a database and obtain its connection string, then convert it to the
SQLAlchemy + psycopg URL the backend expects:

```
postgresql+psycopg://USER:PASSWORD@HOST:5432/DBNAME
```

> Note the `+psycopg` driver suffix. If your provider hands you a
> `postgres://…` URL, rewrite the scheme to `postgresql+psycopg://…`.

Migrations are applied automatically by the backend container on startup
(`alembic upgrade head` runs in the entrypoint). To run them manually:

```bash
cd backend
DATABASE_URL="postgresql+psycopg://…" alembic upgrade head
```

## 2. Backend (FastAPI)

The backend ships as a container (`backend/Dockerfile`). Deploy it to any
container host — **Render**, **Railway**, **Fly.io**, **Google Cloud Run**, or a
VM running Docker.

**Required environment variables:**

| Variable | Example | Notes |
| --- | --- | --- |
| `DATABASE_URL` | `postgresql+psycopg://…` | From step 1 |
| `JWT_SECRET` | 48+ random chars | `python -c "import secrets; print(secrets.token_urlsafe(48))"` |
| `CAREERFLOW_ENV` | `production` | Enables fail-fast secret validation |
| `CORS_ORIGINS` | `https://app.example.com` | Your frontend origin(s), comma-separated |
| `SEED_DEMO_DATA` | `false` | Leave off in production |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Optional |

The image exposes port `8000`. Point your platform's health check at
`GET /health`. Mount a persistent volume at `/app/var/uploads` if you keep
local-disk attachments (or migrate to object storage — see the roadmap).

**Example — Fly.io:**

```bash
cd backend
fly launch --no-deploy            # generates fly.toml; set internal_port = 8000
fly secrets set JWT_SECRET=… DATABASE_URL=… CAREERFLOW_ENV=production CORS_ORIGINS=https://app.example.com
fly deploy
```

**Example — Render (Docker):** create a *Web Service* from `backend/`, set the
environment variables above, and set the health check path to `/health`.

## 3. Frontend (React SPA)

Two supported paths:

### a) Static hosting (Netlify / Vercel / Cloudflare Pages / S3 + CDN)

Build the static bundle and point it at your deployed API:

```bash
cd frontend
VITE_API_BASE_URL="https://api.example.com/api/v1" npm run build
# deploy the ./dist directory
```

Configure an SPA fallback so client routes resolve to `index.html`:

- **Netlify** — add `frontend/public/_redirects` containing `/*  /index.html  200`
- **Vercel** — a rewrite of `/(.*)` → `/index.html`

Make sure the backend's `CORS_ORIGINS` includes the static site's origin.

### b) Container behind Nginx (single origin)

Deploy `frontend/Dockerfile` to a container host. The bundled `nginx.conf`
proxies `/api` to a service named `backend`; update that `proxy_pass` upstream
to your backend's URL if they are not on the same Docker network. With this
path the browser never makes cross-origin calls, so CORS is a non-issue.

## 4. Full stack on a single VM (simplest)

On any VM with Docker installed:

```bash
git clone <repo-url> careerflow && cd careerflow
cp .env.example .env          # set a strong JWT_SECRET and DB credentials
docker compose up -d --build
```

Put a TLS-terminating reverse proxy (Caddy, Traefik, or Nginx) in front of the
`frontend` service on port 80, and you have the whole platform on one host.

## Production checklist

- [ ] `JWT_SECRET` is a strong, unique value (the app refuses to start in
      `production` with the placeholder).
- [ ] `CAREERFLOW_ENV=production` and `DEBUG=false`.
- [ ] `CORS_ORIGINS` lists only your real frontend origin(s).
- [ ] Database backups configured on the managed instance.
- [ ] HTTPS terminated at the proxy/CDN.
- [ ] `SEED_DEMO_DATA` disabled.
- [ ] Persistent volume (or object storage) configured for uploads.
- [ ] Health checks point at `/health`.
