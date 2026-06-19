# Security Design Notes — CareerFlow

> **Version:** 1.0 · **Last updated:** 2026-06-19

This document records the threat model, the controls in place, and the residual
risks accepted for v1. The implemented audit and findings live in
[Phase 15 — Security Review](../README.md#security) and `docs/security-review.md`
(produced during that phase).

## 1. Assets & threat model

| Asset | Threat | Primary control |
| --- | --- | --- |
| User credentials | Theft, brute force | bcrypt hashing, generic auth errors, rate-limit-ready design |
| Session tokens | Theft, forgery, replay | Signed short-lived JWT, HTTPS in prod, no token in logs |
| User data (applications, etc.) | Cross-user access (IDOR) | Mandatory user-scoping in every repository query |
| Uploaded files | Malicious upload, path traversal, info leak | Type/size validation, opaque server-side filenames, storage outside web root, owner-only download |
| Secrets (DB URL, JWT key) | Disclosure | Env-only config; never committed; `.env` gitignored |

Out of scope for v1: multi-tenant isolation beyond per-user scoping, DDoS
mitigation, and WAF (handled at the infrastructure layer in real deployments).

## 2. Authentication

- Passwords hashed with **bcrypt** via `passlib`; cost factor configurable.
- Passwords are validated for a minimum length on registration; never logged,
  never returned.
- Login returns a **JWT access token** signed with HS256 using a secret from the
  environment. Tokens carry `sub` (user id), `exp`, and `iat`.
- Token lifetime is short (default 60 min) and configurable. Refresh-token
  rotation is a documented future improvement.
- Authentication failures return a **generic** message ("Invalid credentials")
  to avoid user enumeration.

## 3. Authorization

- Every data endpoint depends on `get_current_user`, which validates the token
  signature and expiry and loads the active user.
- **Authorization is enforced in the service/repository layers**, not the
  router. Repositories take an `owner` and filter by `user_id`; a resource that
  exists but belongs to another user is reported as **404**.
- There is no admin/role system in v1; every authenticated user is a normal
  owner of their own data.

## 4. Input validation

- All request bodies and query params are validated by **Pydantic v2** schemas
  at the API edge (length limits, enums, ranges, URL/email formats).
- The database enforces a second layer: not-null, unique, FK, and check
  constraints.
- Search/filter inputs are bound parameters via SQLAlchemy — **no string-built
  SQL**, eliminating SQL injection.

## 5. File upload security

- **Allow-list** of content types (PDF, DOCX) validated by both declared
  content type and extension; size capped by config (default 5 MB).
- Stored under a configured directory **outside any static/served path**; the
  filename on disk is a server-generated UUID (`stored_filename`), so the
  original name cannot drive path traversal.
- Downloads stream through an authenticated endpoint that re-checks ownership;
  files are never exposed by a guessable static URL.
- `Content-Disposition: attachment` is set so browsers download rather than
  render potentially active content.

## 6. Transport & headers

- HTTPS terminates at the reverse proxy (Nginx) in production.
- CORS is restricted to configured origins (the SPA origin), not `*`.
- Security headers (`X-Content-Type-Options`, `X-Frame-Options`,
  `Referrer-Policy`) are set via middleware.

## 7. Secrets & configuration

- All secrets come from environment variables loaded into a typed `Settings`.
- `.env` is gitignored; `.env.example` documents variables with safe
  placeholders.
- The application refuses to start in a non-debug profile if `JWT_SECRET` is the
  default placeholder.

## 8. Error handling & logging

- Unexpected exceptions return a generic `500` with no stack trace or internals.
- Logs are structured and request-scoped and **must not contain** passwords,
  tokens, or full PII.

## 9. Dependency & supply-chain hygiene

- Dependencies are pinned; CI runs a vulnerability scan (`pip-audit`) and a
  static security linter (`bandit`) on the backend.
- Frontend dependencies are audited in CI (`npm audit`).

## 10. Residual risks accepted for v1

- No refresh tokens / token revocation list (mitigated by short lifetime).
- No application-level rate limiting (designed to be added at the proxy).
- Single-region, single-node storage (portfolio scope).
