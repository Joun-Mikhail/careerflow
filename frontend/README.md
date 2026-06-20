# CareerFlow Frontend

React + TypeScript single-page app built with Vite. Talks to the CareerFlow API
through a typed axios client and TanStack Query.

## Requirements

- Node.js ≥ 20

## Setup

```bash
npm install
cp .env.example .env   # optional; defaults proxy /api to localhost:8000
npm run dev            # http://localhost:5173
```

The dev server proxies `/api` to the backend (`http://localhost:8000`), so run
the backend alongside it — or use `docker compose up` from the repo root to run
the whole stack.

## Scripts

| Command | Description |
| --- | --- |
| `npm run dev` | Start the Vite dev server |
| `npm run build` | Type-check and produce a production build |
| `npm run preview` | Preview the production build locally |
| `npm run lint` | ESLint (zero warnings allowed) |
| `npm run typecheck` | `tsc --noEmit` |
| `npm test` | Run Vitest unit tests |
| `npm run format` | Format with Prettier |

## Structure

```
src/
├── pages/        route-level screens (auth, dashboard, applications, …)
├── layouts/      app shell (sidebar + topbar) and auth layout
├── components/   reusable UI, forms, icons, feedback states
├── hooks/        TanStack Query hooks per resource
├── services/     typed axios client + endpoint modules
├── contexts/     Auth and Theme providers
└── lib/          types, query client, formatting utilities, constants
```

Components never call the API directly — they use hooks in `hooks/`, which wrap
the `services/` modules in TanStack Query so caching and invalidation stay
consistent. Theming is a CSS custom-property token swap (`src/styles/tokens.css`).
