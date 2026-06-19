# Technical Architecture — CareerFlow

> **Version:** 1.0 · **Last updated:** 2026-06-19

This document describes the system structure, the technology choices and *why*
they were made, the request lifecycle, and the boundaries between components.

## 1. System context

CareerFlow is a classic three-tier web application:

```
┌──────────────┐      HTTPS / JSON      ┌──────────────┐     TCP      ┌──────────────┐
│   Browser    │  ───────────────────▶  │   FastAPI    │  ─────────▶  │  PostgreSQL  │
│ React SPA    │  ◀───────────────────  │   backend    │  ◀─────────  │              │
│ (Vite build) │                        │  (Uvicorn)   │              │              │
└──────────────┘                        └──────┬───────┘              └──────────────┘
                                                │
                                                ▼
                                         Local file storage
                                         (attachments, off web root)
```

In production the React SPA is built to static assets and served by Nginx,
which also reverse-proxies `/api` to the backend. See
[DevOps](../README.md#deployment) and `docker-compose.yml`.

## 2. Technology choices & rationale

| Layer | Choice | Why |
| --- | --- | --- |
| Frontend framework | **React + TypeScript** | Ubiquitous, strongly typed, great ecosystem; recruiter-recognizable. |
| Build tool | **Vite** | Fast dev server and lean production builds. |
| Routing | **React Router** | Standard client-side routing for an SPA. |
| Server state | **TanStack Query** | Caching, background refetch, and cache invalidation remove hand-rolled state plumbing and keep the dashboard fresh. |
| Charts | **Recharts** | Declarative, composable charting that fits React idioms. |
| API framework | **FastAPI** | Async, type-driven, automatic OpenAPI docs, Pydantic validation at the edge. |
| ORM | **SQLAlchemy 2.0** | Mature, explicit, typed `Mapped[...]` models. |
| Migrations | **Alembic** | First-class SQLAlchemy migrations, reversible. |
| Database | **PostgreSQL** | Relational data with strong constraints, native UUID/JSON, robust indexing. |
| Auth | **JWT + bcrypt** (`passlib`) | Stateless API auth; bcrypt is the well-understood default for password hashing. |
| Containerization | **Docker + Compose** | One-command, reproducible local environment. |
| CI | **GitHub Actions** | Lint, test, build, and security checks on every push. |

## 3. Backend architecture — layered & dependency-directed

The backend follows a strict layering. **Dependencies point inward**; an outer
layer may call the layer directly beneath it, never the reverse, and never skips
a layer for business logic.

```
            HTTP request
                 │
                 ▼
┌──────────────────────────────────────────────────────────┐
│  api/ (routers)   — HTTP concerns only: routing, status    │
│                     codes, dependency wiring, (de)serialize │
├──────────────────────────────────────────────────────────┤
│  services/        — business logic, orchestration,         │
│                     authorization, cross-entity rules       │
├──────────────────────────────────────────────────────────┤
│  repositories/    — data access; the ONLY layer that       │
│                     issues SQLAlchemy queries               │
├──────────────────────────────────────────────────────────┤
│  models/          — SQLAlchemy ORM entities (the schema)   │
└──────────────────────────────────────────────────────────┘
   schemas/  — Pydantic request/response contracts (cross-cutting)
   core/     — config, security, db session, logging, errors (cross-cutting)
```

### Layer responsibilities & rules

- **`api/` (routers).** Translate HTTP ⇄ Python. Parse path/query/body into
  schemas, call exactly one service method, map the result (or domain error) to
  a status code. **No business logic, no direct DB access.**
- **`services/`.** The heart of the application. Enforce business rules (e.g.
  "a user may only see their own applications"), orchestrate repositories, raise
  typed domain errors (`NotFoundError`, `PermissionDeniedError`,
  `ConflictError`). Services receive a DB session and repositories via
  constructor/dependency injection.
- **`repositories/`.** Encapsulate persistence. One repository per aggregate
  (User, Company, Application, …). Expose intention-revealing methods
  (`get_by_id_for_owner`, `list_paginated`) rather than leaking query builders.
  This is the **only** place SQLAlchemy `select()`/`session` is used for domain
  data.
- **`models/`.** SQLAlchemy 2.0 declarative models; the source of truth for the
  schema, mirrored by Alembic migrations.
- **`schemas/`.** Pydantic v2 models for input validation and output shaping.
  Request and response schemas are distinct; internal fields never leak.
- **`core/`.** Configuration (`Settings` from env), security primitives
  (hashing, JWT), the SQLAlchemy engine/session factory, structured logging, and
  the central exception-to-HTTP mapping.

### Why this matters

Separation of concerns makes each layer independently testable: services are
unit-tested with fake/SQLite-backed repositories; repositories are tested
against a real database; routers are covered by integration tests through the
ASGI app. It also keeps routes thin and prevents the "fat controller" anti-
pattern that makes codebases look AI-generated and hard to maintain.

## 4. Request lifecycle (example: `POST /api/v1/applications`)

1. **Router** receives the request; FastAPI validates the JSON body against
   `ApplicationCreate` and injects the current user via the `get_current_user`
   dependency (which validates the JWT).
2. Router calls `ApplicationService.create(owner=user, data=payload)`.
3. **Service** verifies the referenced company belongs to the user, applies
   business rules, and calls `ApplicationRepository.add(...)`.
4. **Repository** persists the `Application` model and flushes.
5. Service returns the ORM object; the router serializes it through
   `ApplicationRead` and responds `201 Created`.
6. Any domain error raised in the service is converted to the correct HTTP
   status by the central exception handler in `core/`.

## 5. Frontend architecture

```
src/
├── pages/        — route-level screens (Dashboard, Applications, …)
├── layouts/      — app shell (sidebar + topbar), auth layout
├── components/   — reusable presentational + small composite UI
├── hooks/        — TanStack Query hooks (useApplications, useAuth, …)
├── services/     — typed API client (axios) + endpoint modules
├── contexts/     — cross-cutting React contexts (auth, theme)
└── lib/          — utilities, types, query client config
```

- **Data flow.** Components never call `axios` directly. They use hooks in
  `hooks/`, which wrap `services/` calls in TanStack Query. Mutations invalidate
  the relevant query keys so the UI stays consistent.
- **Auth.** A token is held in memory + persisted; an axios interceptor attaches
  the `Authorization` header and redirects to login on `401`.
- **Theming.** A `ThemeContext` toggles a `data-theme` attribute; styles use CSS
  custom properties so dark mode is a token swap, not a re-render of logic.

## 6. System boundaries

- The **frontend trusts nothing**: every protected action goes through the API,
  which re-authorizes server-side. Client-side guards are UX, not security.
- The **API owns all business rules and authorization.** No rule lives only in
  the UI.
- The **database enforces integrity** (FKs, unique constraints, not-null) as a
  backstop independent of application code.
- **File storage** is a separate concern: files are written under a configured
  directory outside any statically served path and streamed back only to the
  owning user.

## 7. Configuration & environments

All configuration comes from environment variables, loaded into a typed
`Settings` object (`core/config.py`). Nothing secret is committed; `.env.example`
documents every variable. Profiles: local (Compose), test (SQLite/ephemeral
Postgres), and a production-shaped Docker build.

## 8. Cross-cutting concerns

- **Error handling:** domain errors → HTTP via one handler; unexpected errors
  are logged and returned as a generic 500 (no internals leaked).
- **Logging:** structured, request-scoped, no secrets/PII in logs.
- **Validation:** Pydantic at the edge; DB constraints as the backstop.
- **Testing:** see [Testing Strategy](../README.md#testing) and `backend/tests`.
