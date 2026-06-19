<div align="center">

# CareerFlow

**A modern SaaS platform for tracking job applications, interviews, tasks, and career opportunities.**

[Architecture](docs/02-technical-architecture.md) ·
[Database](docs/03-database-design.md) ·
[API](docs/04-api-design.md) ·
[Security](docs/05-security-design.md)

</div>

---

> **Project status:** Under active construction. This README is a working
> placeholder; the full recruiter-facing README — with screenshots, badges,
> architecture diagrams, and guides — is produced in Phase 18 of the build.

## What is CareerFlow?

Job seekers lose track of applications, interview schedules, recruiters, notes,
and follow-ups across spreadsheets and inboxes. CareerFlow centralizes the
entire job search into one professional platform: a pipeline of applications,
the interviews and tasks tied to them, and analytics that show what's working.

## Tech stack

| Area | Technologies |
| --- | --- |
| Frontend | React, TypeScript, Vite, React Router, TanStack Query, Recharts |
| Backend | Python, FastAPI, SQLAlchemy 2.0, Alembic |
| Database | PostgreSQL |
| Auth | JWT, bcrypt |
| DevOps | Docker, Docker Compose, GitHub Actions |
| Testing | Pytest (backend), Vitest (frontend) |

## Documentation

Planning and design documents live in [`docs/`](docs/):

1. [Product Requirements](docs/01-product-requirements.md)
2. [Technical Architecture](docs/02-technical-architecture.md)
3. [Database Design](docs/03-database-design.md)
4. [API Design](docs/04-api-design.md)
5. [Security Design](docs/05-security-design.md)
6. [Folder Structure Plan](docs/06-folder-structure.md)

## Quick start (target)

```bash
docker compose up --build
# Frontend: http://localhost:5173
# API docs: http://localhost:8000/api/docs
```

A full installation, development, deployment, and API guide will accompany the
Phase 18 documentation pass.

## License

[MIT](LICENSE)
