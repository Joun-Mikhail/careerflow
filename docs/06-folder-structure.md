# Folder Structure Plan — CareerFlow

> **Version:** 1.0 · **Last updated:** 2026-06-19

This is the target layout for the monorepo. It is the contract the
implementation phases build against.

## 1. Repository root

```
careerflow/
├── .github/workflows/        # CI pipelines
├── backend/                  # FastAPI service
├── frontend/                 # React + Vite SPA
├── docs/                     # Documentation (this folder)
│   └── diagrams/             # Architecture & ER diagrams, screenshots
├── docker-compose.yml        # Full-stack local orchestration
├── .editorconfig
├── .gitignore
├── LICENSE
├── CONTRIBUTING.md
└── README.md
```

## 2. Backend (`backend/`)

```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py               # shared dependencies (auth, db, pagination)
│   │   ├── router.py             # aggregates v1 routers
│   │   └── v1/
│   │       ├── auth.py
│   │       ├── companies.py
│   │       ├── applications.py
│   │       ├── interviews.py
│   │       ├── notes.py
│   │       ├── tasks.py
│   │       ├── attachments.py
│   │       ├── dashboard.py
│   │       └── analytics.py
│   ├── core/
│   │   ├── config.py             # typed Settings from env
│   │   ├── database.py           # engine + session factory + Base
│   │   ├── security.py           # hashing + JWT
│   │   ├── logging.py            # structured logging setup
│   │   ├── errors.py             # domain errors + HTTP mapping
│   │   └── pagination.py         # Page envelope helpers
│   ├── models/                   # SQLAlchemy models (one file per entity)
│   ├── schemas/                  # Pydantic request/response models
│   ├── repositories/             # data access (one per aggregate)
│   ├── services/                 # business logic (one per aggregate)
│   ├── main.py                   # FastAPI app factory + wiring
│   └── __init__.py
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/                 # migration scripts
├── tests/
│   ├── conftest.py               # fixtures: app, client, db, auth
│   ├── unit/                     # service-level tests
│   └── integration/              # endpoint tests through the ASGI app
├── alembic.ini
├── pyproject.toml                # deps, ruff, mypy, pytest, coverage config
├── Dockerfile
└── .env.example
```

### Naming & placement rules

- One model, one schema module, one repository, one service **per aggregate**;
  names stay parallel (`Application` → `application.py` in each layer).
- Routers contain no business logic; they import services.
- Anything reused across layers (errors, pagination, config) lives in `core/`.

## 3. Frontend (`frontend/`)

```
frontend/
├── src/
│   ├── main.tsx                  # app entry, providers
│   ├── App.tsx                   # router definition
│   ├── pages/
│   │   ├── auth/                 # Login, Register
│   │   ├── DashboardPage.tsx
│   │   ├── ApplicationsPage.tsx
│   │   ├── ApplicationDetailPage.tsx
│   │   ├── CompaniesPage.tsx
│   │   ├── TasksPage.tsx
│   │   └── AnalyticsPage.tsx
│   ├── layouts/
│   │   ├── AppLayout.tsx         # sidebar + topbar shell
│   │   └── AuthLayout.tsx
│   ├── components/
│   │   ├── ui/                   # Button, Input, Card, Modal, Badge, …
│   │   ├── charts/               # Recharts wrappers
│   │   └── feedback/             # Loading, Empty, Error states
│   ├── hooks/                    # TanStack Query hooks per resource
│   ├── services/                 # axios client + endpoint modules
│   ├── contexts/                 # AuthContext, ThemeContext
│   └── lib/                      # types, queryClient, utils
├── public/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── Dockerfile
├── nginx.conf                    # prod static serving + API proxy
└── .env.example
```

## 4. Documentation (`docs/`)

```
docs/
├── 01-product-requirements.md
├── 02-technical-architecture.md
├── 03-database-design.md
├── 04-api-design.md
├── 05-security-design.md
├── 06-folder-structure.md
├── security-review.md            # produced in Phase 15
└── diagrams/                     # exported architecture/ERD images, screenshots
```

## 5. Why a monorepo

Frontend and backend evolve together for a single product; a monorepo keeps the
API contract, types, and docs in lockstep, enables one CI pipeline, and lets
`docker compose up` orchestrate the whole stack from the root. The two apps stay
independently buildable and deployable.
