# Security Review — CareerFlow

> **Phase 15 audit.** Conducted against the full backend after feature
> completion. Pairs with the design-time [Security Design Notes](05-security-design.md).
> Re-run the tooling commands below to reproduce.

## 1. Tooling results

| Tool | Scope | Result |
| --- | --- | --- |
| `bandit -r app` | Static analysis of backend source | **Pass** — 0 issues (one demo-credential false positive triaged with a justified `# nosec B105`). |
| `pip-audit` | Known CVEs in installed dependencies | **Pass** — 0 known vulnerabilities after upgrading `setuptools` and `pytest`. |
| `ruff` / `mypy` | Lint & types (defence against footguns) | **Pass** — clean. |

```bash
cd backend
bandit -r app -q
pip-audit
```

### Dependency findings & fixes

The initial audit flagged build/test tooling only — never the application's
runtime dependencies:

- `setuptools 65.5.0` (CVE-2024-6345, PYSEC-2025-49) — **fixed** by upgrading to
  ≥ 78.1.1.
- `pytest 8.4.2` (CVE-2025-71176, dev-only) — **fixed** by widening the pin to
  allow ≥ 9.0.3; the suite passes on the patched version.

The production container installs only runtime dependencies (FastAPI,
SQLAlchemy, psycopg, bcrypt, PyJWT, …), none of which had known
vulnerabilities.

## 2. Manual audit by area

### Authentication
- Passwords are hashed with **bcrypt** (`app/core/security.py`); the plaintext
  is never logged or returned. Length is bounded to bcrypt's 72-byte limit at
  the schema layer, so hashing never silently truncates.
- Tokens are signed JWTs with `exp`/`iat`; expiry and signature are validated
  centrally, and any failure maps to a uniform `401`.
- Login returns a **generic** "Invalid email or password" for unknown email,
  wrong password, and inactive account alike — no user enumeration.
- **Verified by tests:** expired/garbage tokens, wrong password, unknown email.

### Authorization (IDOR)
- Every repository query is scoped by `user_id`; the `BaseRepository.owned_query`
  helper makes this the default, not an opt-in.
- Cross-user access to an existing resource returns **404**, not 403, so
  existence is not leaked. **Verified by per-resource "scoped to owner" tests.**

### Input validation
- All request bodies/params are validated by Pydantic v2 (lengths, enums,
  ranges, email/URL formats); the salary range is cross-field validated.
- All persistence goes through SQLAlchemy bound parameters — **no string-built
  SQL**, so SQL injection is not reachable. Search uses parameterized `ILIKE`.

### File uploads
- Allow-list of content types (PDF, DOCX) plus a configurable size cap,
  enforced before the full payload is buffered (reads `max+1` bytes).
- Files are stored under a configured directory **outside any served path**,
  named with a server-generated UUID; `LocalFileStorage.path_for` additionally
  resolves and asserts containment to defend against traversal.
- Downloads stream through an **authenticated, ownership-checked** endpoint with
  `Content-Disposition: attachment` and `X-Content-Type-Options: nosniff`.
- **Verified by tests:** unsupported type rejected, empty file rejected,
  cross-user download returns 404.

### Configuration & secrets
- All secrets are environment-driven; `.env` is gitignored and `.env.example`
  documents every variable.
- The app **refuses to start in production** if `JWT_SECRET` is left at an
  insecure placeholder (`Settings.validate_for_runtime`).

### Transport & headers
- CORS is restricted to configured origins (never `*`).
- Security headers (`X-Content-Type-Options`, `X-Frame-Options`,
  `Referrer-Policy`) are applied by middleware on every response.

### Error handling
- Unexpected exceptions return a generic `500` with no stack trace or internals;
  validation errors are encoded safely (`jsonable_encoder`) into the standard
  envelope.

## 3. Residual risks (accepted for v1)

- **No refresh tokens / revocation list** — mitigated by short token lifetime.
- **No application-level rate limiting** — intended to live at the reverse proxy.
- **bcrypt 72-byte limit** — passwords are bounded at the schema layer and the
  behaviour is documented; acceptable for this scope.

No high- or medium-severity issues were found. All actionable findings were
fixed in this phase.
