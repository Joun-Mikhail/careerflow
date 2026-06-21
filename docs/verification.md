# Runtime Verification

This records evidence from **actually building and running** CareerFlow. All
figures below come from real local runs — nothing here is mocked or fabricated.

## Build & quality gates

**Backend** (Python 3.11):

```
ruff check .            → All checks passed!
ruff format --check .   → 83 files already formatted
mypy app                → Success: no issues found in 65 source files
bandit -r app           → 0 issues
pip-audit               → No known vulnerabilities found
pytest                  → 86 passed  (~97% line coverage)
```

**Frontend** (Node 20):

```
tsc --noEmit            → clean
eslint . --max-warnings 0 → clean
vitest run              → 10 passed
vite build              → built; vendor chunks split (largest gzip ≈ 111 kB charts)
```

## End-to-end run

The full stack was started locally — FastAPI (Uvicorn) on `:8000` and the built
SPA served by `vite preview` on `:5173`, proxying `/api` to the backend — with
the demo data seeded.

- `GET /health` → `200 {"status":"ok"}`
- `POST /api/v1/auth/login` (through the SPA's `/api` proxy) with the demo
  credentials → `200`, returning a valid JWT (188 chars).
- After signing in through the UI, the dashboard rendered the seeded data,
  read back from the live DOM:
  - Applications **16**, Interviews **5**, Offers **1**, Success rate **12.5%**
    (= (1 offer + 1 accepted) / 16, correct).
  - Recent applications, upcoming interviews (with relative times), and pending
    tasks all populated.

## Screenshots

The images in [`screenshots/`](screenshots/) and the README were captured from
this run by `frontend/scripts/screenshot.mjs` (Puppeteer driving Chrome against
the live app). The demo GIF was produced by `frontend/scripts/demo-gif.mjs`.

## Public deployment

No public deployment was performed: hosting a live instance requires accounts
and credentials on a cloud provider, which are not available in this
environment. Rather than fabricate a live URL or deployment screenshots, this
document reports only what was actually executed locally. The
[deployment guide](deployment.md) gives complete, provider-agnostic steps to
publish the frontend, backend, and database when those credentials are
available; the container build path is exercised by the CI `docker` job.
