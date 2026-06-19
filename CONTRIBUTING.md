# Contributing to CareerFlow

Thanks for your interest in CareerFlow. This guide explains how to set up the
project, the conventions we follow, and how to get a change merged.

## Development setup

The fastest path is Docker:

```bash
docker compose up --build
```

To work on a single app natively, see the dedicated guides:

- **Backend:** `backend/README` section in the docs — `pip install -e ".[dev]"`,
  then `uvicorn app.main:app --reload`.
- **Frontend:** `npm install` then `npm run dev` inside `frontend/`.

## Branching & commits

- Branch from `main`: `feat/…`, `fix/…`, `docs/…`, `chore/…`.
- Commits follow **Conventional Commits**: `type(scope): summary`.
  Examples: `feat(applications): add status filter`,
  `test(auth): cover expired-token path`.
- Keep commits focused and the history readable; one logical change per commit.

## Code style

| Area | Tooling |
| --- | --- |
| Python | `ruff` (lint + format), `mypy` (types) |
| TypeScript | `eslint`, `prettier`, `tsc --noEmit` |

Run the backend checks before pushing:

```bash
cd backend
ruff check . && ruff format --check . && mypy app && pytest
```

And the frontend:

```bash
cd frontend
npm run lint && npm run typecheck && npm test && npm run build
```

CI runs the same checks; a PR must be green to merge.

## Tests

- New behaviour needs tests. Backend targets ≥ 80% line coverage.
- Bug fixes should include a regression test.

## Architectural conventions

- Respect the layering described in
  [Technical Architecture](docs/02-technical-architecture.md): routers stay thin,
  business logic lives in services, data access lives in repositories.
- All data access is scoped to the authenticated user.
- No secrets in the repo; configuration is environment-driven.

## Reporting issues

Open an issue describing the expected vs. actual behaviour, steps to reproduce,
and environment. Security issues should be reported privately (see
[Security Design](docs/05-security-design.md)).
