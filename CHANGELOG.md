# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- Drag-and-drop status changes on the pipeline board
- CSV/JSON export of the pipeline

## [1.0.0] — 2026-06-20

First complete release: a working full-stack job-application tracker.

### Added

- **Authentication** — email/password registration and login, bcrypt hashing,
  JWT sessions, and fully user-scoped data access.
- **Companies** — CRUD with search, industry filtering, and pagination.
- **Applications** — an eight-stage pipeline (wishlist → accepted) with salary,
  location, source, and links; Kanban board and list views; search, filtering,
  and sorting.
- **Interviews** — multiple rounds per application with mode, interviewer,
  result, and notes.
- **Tasks** — priorities, due dates, completion, and semantic priority sorting.
- **Notes** — Markdown notes per application.
- **Attachments** — validated, owner-only resume/cover-letter uploads.
- **Dashboard & analytics** — headline stats, upcoming interviews, pending
  tasks, and Recharts visualizations (applications over time, status and
  industry distribution, conversion rates).
- **Frontend** — React + TypeScript SPA with a bespoke design system, light/dark
  themes, and loading/empty/error states throughout.
- **Tooling** — Dockerized stack with one-command startup, GitHub Actions CI
  (lint, types, security scans, tests, image builds), and a seed script for a
  realistic demo dataset.

### Security

- Generic authentication errors (no user enumeration), input validation via
  Pydantic, parameterized queries, secure file handling, and CI-enforced
  `bandit` and `pip-audit` scans.

[Unreleased]: https://example.com/careerflow/compare/v1.0.0...HEAD
[1.0.0]: https://example.com/careerflow/releases/tag/v1.0.0
