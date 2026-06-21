# Portfolio Package — CareerFlow

Ready-to-use copy for showcasing CareerFlow. Replace `‹frontend-url›` /
`‹repo-url›` with your live links once deployed.

## GitHub repository description

> CareerFlow — a full-stack SaaS for tracking job applications, interviews,
> tasks, and offers. FastAPI + PostgreSQL backend, React + TypeScript SPA,
> Dockerized with CI. Clean layered architecture, ~97% backend test coverage.

## GitHub topics

`fastapi` · `react` · `typescript` · `postgresql` · `sqlalchemy` · `docker`
· `github-actions` · `jwt` · `vite` · `tanstack-query` · `saas` ·
`clean-architecture` · `pytest`

## LinkedIn project description

> **CareerFlow — Job-search tracking SaaS**
> Designed and built a production-grade SaaS that turns a chaotic job search
> into a managed pipeline: a Kanban board of applications across eight stages,
> interview and task tracking, document uploads, and analytics on conversion.
> Backend in FastAPI/SQLAlchemy with a strict layered architecture (routers →
> services → repositories) and ~97% test coverage; React + TypeScript frontend
> with a bespoke design system, light/dark themes, and TanStack Query. Fully
> containerized with GitHub Actions CI (lint, types, security scans, tests,
> image builds) and a documented Vercel + Railway + Neon deployment.

## CV bullet points

- Built a full-stack SaaS (FastAPI, React/TypeScript, PostgreSQL) with a layered,
  test-driven backend reaching ~97% line coverage across 86 tests.
- Designed a normalized schema (7 entities, UUID keys, soft deletes, indexed
  foreign keys) with reversible Alembic migrations.
- Implemented JWT auth with bcrypt and strict per-user data scoping; passed a
  self-run security audit (Bandit, pip-audit, manual IDOR/CORS/upload review).
- Containerized the stack (Docker Compose) and set up GitHub Actions CI running
  lint, type-checks, security scans, tests, and image builds on every push.
- Shipped a polished SPA: Kanban pipeline, dashboard, and Recharts analytics
  with light/dark theming and full loading/empty/error states.

## Interview talking points

- **Layered architecture & why:** routers hold only HTTP concerns, services own
  business rules and authorization, repositories own all SQL. Keeps routes thin,
  units testable, and SQL in one place.
- **Authorization model:** every query is user-scoped via a base-repository
  helper; cross-user access returns 404 (no existence leak).
- **Testing strategy:** in-memory SQLite for fast, isolated tests; the same ORM
  runs on PostgreSQL in production via a portable UUID type.
- **Found-by-running bugs:** a CORS credentials/wildcard conflict and a
  pydantic-settings env-parsing crash — both caught by actually running the
  stack, not just reading code.

## STAR stories

**1 — Reliable cross-environment data layer**
- *Situation:* the app targets PostgreSQL but the test suite needs to be fast
  and dependency-free.
- *Task:* run identical models on both without per-environment branching.
- *Action:* implemented a portable `GUID` type (native `uuid` on Postgres,
  `CHAR(32)` on SQLite) and time-bucketed analytics in Python instead of DB-
  specific date functions.
- *Result:* one model layer, 86 tests on in-memory SQLite, production on
  Postgres — no divergence.

**2 — Catching production bugs before users did**
- *Situation:* preparing for deployment to Vercel + Railway + Neon.
- *Task:* prove the stack actually runs, not just compiles.
- *Action:* ran the full stack locally and drove the UI; discovered `$PORT`
  wasn't honoured (Railway health checks would fail), CORS credentials clashed
  with wildcard headers cross-origin, and a comma-separated `CORS_ORIGINS`
  crashed startup.
- *Result:* fixed all three with regression tests/config and a documented,
  verifiable deploy runbook.

## Portfolio case study (short)

CareerFlow centralizes a job search — companies, applications, interviews,
tasks, notes, attachments — into one workspace with analytics. The interesting
engineering is in the **boundaries**: a dependency-directed backend that keeps
business logic out of routes and SQL out of services, paired with a frontend
where components never touch the API directly (TanStack Query hooks wrap a typed
client, so caching and invalidation are consistent). It was built phase by phase
with a green quality gate (ruff, mypy, bandit, pip-audit, pytest; ESLint, tsc,
Vitest) enforced in CI on every commit.

## Technical deep dive

- **Request lifecycle:** Pydantic validates input → router calls one service
  method → service authorizes and orchestrates repositories → repository issues
  parameterized SQL → ORM object serialized through a response schema. Domain
  errors map to a single consistent error envelope.
- **Pagination/sorting:** a generic `BaseRepository.apply_sort` + `paginate`
  with an allow-listed sort map and a stable id tiebreaker.
- **Analytics:** aggregate queries in a dedicated `StatsRepository`; month
  bucketing in Python for portability; conversion = (offers + accepted) / total.

## Architecture explanation

Three tiers (SPA → API → PostgreSQL) with attachments on a volume. The backend's
inward-pointing dependency rule and the frontend's service/hook/page split are
the core ideas; see [02-technical-architecture.md](02-technical-architecture.md)
and the diagrams in [diagrams/](diagrams/).

## Trade-off analysis

- **Synchronous SQLAlchemy** over async: simpler reasoning and trivially
  testable; FastAPI still serves concurrently via its threadpool. Acceptable for
  this workload.
- **Local-disk attachments** over object storage: fewer moving parts for v1;
  documented as a known limitation with a clear migration path.
- **No strict status state-machine:** users can move applications backward
  (e.g. re-open after rejection) — flexibility over rigidity, validated values
  only.
- **JWT without refresh tokens:** short-lived tokens keep v1 simple; rotation is
  a planned improvement.

## Lessons learned

- Running the app surfaces a different (and more important) class of bug than
  reading it — the deploy-blockers were all runtime/config, not logic.
- A portable data type and Python-side aggregation removed an entire category of
  environment-specific test flakiness.
- Enforcing the same quality gate locally and in CI from commit one kept the
  codebase releasable at every step.
