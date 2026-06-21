# Production Deploy Runbook — Vercel + Railway + Neon

A step-by-step, copy-paste runbook to take CareerFlow live. It assumes the repo
is pushed to GitHub. Each platform step needs **your** account; the commands and
settings below are exact.

Estimated time: ~15 minutes.

---

## 0. Prerequisites

- The repository on GitHub.
- Free accounts on **Neon** (database), **Railway** (backend), **Vercel** (frontend).
- A strong JWT secret:
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(48))"
  ```

---

## 1. Database — Neon PostgreSQL

1. Create a Neon project → it provisions a Postgres database.
2. Copy the **connection string**. It looks like:
   ```
   postgres://USER:PASSWORD@ep-xxx.region.aws.neon.tech/neondb?sslmode=require
   ```
3. **Rewrite the scheme** for SQLAlchemy + psycopg (keep the rest, including
   `?sslmode=require`):
   ```
   postgresql+psycopg://USER:PASSWORD@ep-xxx.region.aws.neon.tech/neondb?sslmode=require
   ```
   Save this as `DATABASE_URL` for the next step.

Migrations are applied automatically by the backend on first boot — no manual
step needed. (To run them by hand: `DATABASE_URL=… alembic upgrade head` from
`backend/`.)

---

## 2. Backend — Railway

1. **New Project → Deploy from GitHub repo**, select this repository.
2. In the service **Settings**, set **Root Directory** to `backend`. Railway
   detects `backend/Dockerfile` and `backend/railway.json` (health check `/health`).
3. Add **Variables**:
   | Variable | Value |
   | --- | --- |
   | `DATABASE_URL` | the `postgresql+psycopg://…` string from step 1 |
   | `JWT_SECRET` | your generated secret |
   | `CAREERFLOW_ENV` | `production` |
   | `DEBUG` | `false` |
   | `CORS_ORIGINS` | `https://PLACEHOLDER.vercel.app` (update after step 3) |
   | `SEED_DEMO_DATA` | `true` for a public demo login, else `false` |
4. Deploy. Railway builds the image, runs migrations on start, and assigns a
   public domain — **Settings → Networking → Generate Domain**. Note it, e.g.
   `https://careerflow-api.up.railway.app`. This is your **backend URL**.
5. *(Optional, for attachments)* add a **Volume** mounted at `/app/var/uploads`
   so uploaded files survive redeploys.

**CLI alternative:**
```bash
npm i -g @railway/cli
railway login            # opens your browser
railway init             # or: railway link
railway up               # builds & deploys backend/
railway variables set JWT_SECRET=… DATABASE_URL=… CAREERFLOW_ENV=production DEBUG=false
```

---

## 3. Frontend — Vercel

1. **Add New Project → Import** the GitHub repo.
2. Set **Root Directory** to `frontend`. Vercel detects Vite and reads
   `frontend/vercel.json` (SPA fallback).
3. Add an **Environment Variable**:
   | Variable | Value |
   | --- | --- |
   | `VITE_API_BASE_URL` | `https://<your-railway-domain>/api/v1` |
4. Deploy. Vercel builds and assigns a domain, e.g.
   `https://careerflow.vercel.app`. This is your **frontend URL**.
5. **Go back to Railway** and set `CORS_ORIGINS` to the exact Vercel origin
   (`https://careerflow.vercel.app`), then redeploy the backend.

**CLI alternative:**
```bash
npm i -g vercel
cd frontend && vercel        # login + link, follow prompts
vercel env add VITE_API_BASE_URL    # paste the Railway /api/v1 URL
vercel --prod
```

---

## 4. Verification (do not skip)

Replace the hostnames with your real domains.

```bash
# Backend health + HTTPS
curl -i https://careerflow-api.up.railway.app/health
#   → HTTP/2 200 ... {"status":"ok"}

# API documentation is public
curl -sI https://careerflow-api.up.railway.app/api/docs | head -n1
#   → HTTP/2 200

# Register a real account
curl -s -X POST https://careerflow-api.up.railway.app/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"you@example.com","password":"Sup3rSecret!","full_name":"You"}'
#   → 201 with {user, token}

# Log in and capture the token
TOKEN=$(curl -s -X POST https://careerflow-api.up.railway.app/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"you@example.com","password":"Sup3rSecret!"}' | jq -r .token.access_token)

# Authenticated calls work end-to-end
curl -s https://careerflow-api.up.railway.app/api/v1/dashboard/summary \
  -H "Authorization: Bearer $TOKEN" | jq .totals
```

Then in the browser, open the **frontend URL** and verify: login (the demo
account works if `SEED_DEMO_DATA=true`), dashboard, applications board,
analytics, dark mode, and a CRUD round-trip (create/edit/delete a company).

Capture screenshots from the deployed URLs to replace those in
`docs/screenshots/` (regenerate with `frontend/scripts/screenshot.mjs` pointed
at the production `BASE_URL`).

---

## Single-platform alternative (Railway full-stack)

If you prefer one platform: deploy **two Railway services** from this repo — one
with root `backend` (as above) and one with root `frontend` (Dockerfile + Nginx).
Set the frontend service's Nginx `proxy_pass` (in `frontend/nginx.conf`) to the
backend service's internal URL, so the browser sees a single origin and CORS is
not involved. Add the Neon `DATABASE_URL` to the backend service. This trades
Vercel's CDN for a simpler, single-dashboard setup.

---

## Rollback

Both Railway and Vercel keep previous deployments. If a release misbehaves, use
the platform's **Rollback / Redeploy previous** action. Database migrations are
reversible (`alembic downgrade -1`) should a schema change need reverting.
