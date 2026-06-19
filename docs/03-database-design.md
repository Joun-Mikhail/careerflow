# Database Design — CareerFlow

> **Version:** 1.0 · **Last updated:** 2026-06-19 · **Engine:** PostgreSQL 16

## 1. Conventions

These conventions apply to **every** table unless noted:

- **Primary key:** `id UUID` (default `gen_random_uuid()` server-side; generated
  in Python as a fallback for non-Postgres test backends).
- **Timestamps:** `created_at` and `updated_at` (`TIMESTAMPTZ`, not null,
  server-defaulted; `updated_at` maintained by the ORM `onupdate`).
- **Soft delete:** business entities carry `deleted_at TIMESTAMPTZ NULL`. A row
  with `deleted_at` set is excluded from default queries. Join tables and
  attachments are hard-deleted.
- **Ownership:** every user-owned table has `user_id UUID` referencing
  `users.id`, indexed, and used to scope every query.
- **Naming:** snake_case tables (plural) and columns; FKs named `<entity>_id`.

## 2. Entities & relationships (ERD)

```
                            ┌───────────┐
                            │   users   │
                            └─────┬─────┘
            ┌─────────────────────┼─────────────────────┬──────────────┐
            │ 1                   │ 1                    │ 1            │ 1
            ▼ N                   ▼ N                    ▼ N            ▼ N
      ┌───────────┐        ┌──────────────┐        ┌──────────┐  ┌───────────┐
      │ companies │        │ applications │        │  tasks   │  │   ...      │
      └─────┬─────┘ 1    N └──────┬───────┘        └──────────┘
            └────────────────────▶│  (company_id, nullable on set-null)
                                   │ 1
                 ┌─────────────────┼──────────────────┐
                 │ N               │ N                 │ N
                 ▼                 ▼                    ▼
          ┌────────────┐    ┌───────────┐       ┌──────────────┐
          │ interviews │    │   notes   │       │ attachments  │
          └────────────┘    └───────────┘       └──────────────┘
```

Cardinalities:

- `users 1—N companies`, `applications`, `tasks`
- `companies 1—N applications` (an application's company is optional)
- `applications 1—N interviews`, `notes`, `attachments`
- `tasks` may optionally reference an `application`

## 3. Tables

### 3.1 `users`

| Column | Type | Constraints |
| --- | --- | --- |
| `id` | UUID | PK |
| `email` | CITEXT / VARCHAR(320) | not null, **unique** |
| `hashed_password` | VARCHAR(255) | not null |
| `full_name` | VARCHAR(120) | null |
| `is_active` | BOOLEAN | not null, default true |
| `created_at` / `updated_at` | TIMESTAMPTZ | not null |

Indexes: unique on `email`.

### 3.2 `companies`

| Column | Type | Constraints |
| --- | --- | --- |
| `id` | UUID | PK |
| `user_id` | UUID | FK → users.id, not null, **on delete cascade** |
| `name` | VARCHAR(200) | not null |
| `website` | VARCHAR(500) | null |
| `industry` | VARCHAR(120) | null |
| `location` | VARCHAR(200) | null |
| `notes` | TEXT | null |
| `created_at` / `updated_at` / `deleted_at` | TIMESTAMPTZ | — |

Indexes: `(user_id)`, `(user_id, name)`, partial index on `deleted_at IS NULL`.

### 3.3 `applications`

| Column | Type | Constraints |
| --- | --- | --- |
| `id` | UUID | PK |
| `user_id` | UUID | FK → users.id, not null, on delete cascade |
| `company_id` | UUID | FK → companies.id, **null**, on delete set null |
| `role_title` | VARCHAR(200) | not null |
| `status` | ENUM `application_status` | not null, default `wishlist` |
| `salary_min` | INTEGER | null |
| `salary_max` | INTEGER | null |
| `salary_currency` | VARCHAR(3) | null (ISO 4217) |
| `location` | VARCHAR(200) | null |
| `is_remote` | BOOLEAN | not null, default false |
| `application_url` | VARCHAR(1000) | null |
| `source` | VARCHAR(120) | null |
| `applied_at` | TIMESTAMPTZ | null |
| `created_at` / `updated_at` / `deleted_at` | TIMESTAMPTZ | — |

Enum `application_status`: `wishlist, applied, assessment, interview,
final_interview, offer, rejected, accepted`.

Indexes: `(user_id)`, `(user_id, status)`, `(company_id)`, partial
`deleted_at IS NULL`. Check: `salary_max >= salary_min` when both present.

### 3.4 `interviews`

| Column | Type | Constraints |
| --- | --- | --- |
| `id` | UUID | PK |
| `user_id` | UUID | FK → users.id, not null, on delete cascade |
| `application_id` | UUID | FK → applications.id, not null, on delete cascade |
| `scheduled_at` | TIMESTAMPTZ | not null |
| `round_type` | VARCHAR(80) | null (e.g. "Phone screen", "System design") |
| `interviewer` | VARCHAR(200) | null |
| `mode` | ENUM `interview_mode` | not null, default `video` (`phone/video/onsite`) |
| `result` | ENUM `interview_result` | not null, default `pending` (`pending/passed/failed/cancelled`) |
| `notes` | TEXT | null |
| `created_at` / `updated_at` | TIMESTAMPTZ | — |

Indexes: `(user_id)`, `(application_id)`, `(user_id, scheduled_at)`.

### 3.5 `tasks`

| Column | Type | Constraints |
| --- | --- | --- |
| `id` | UUID | PK |
| `user_id` | UUID | FK → users.id, not null, on delete cascade |
| `application_id` | UUID | FK → applications.id, null, on delete set null |
| `title` | VARCHAR(200) | not null |
| `description` | TEXT | null |
| `priority` | ENUM `task_priority` | not null, default `medium` (`low/medium/high`) |
| `due_at` | TIMESTAMPTZ | null |
| `is_completed` | BOOLEAN | not null, default false |
| `completed_at` | TIMESTAMPTZ | null |
| `created_at` / `updated_at` | TIMESTAMPTZ | — |

Indexes: `(user_id)`, `(user_id, is_completed)`, `(user_id, due_at)`.

### 3.6 `notes`

| Column | Type | Constraints |
| --- | --- | --- |
| `id` | UUID | PK |
| `user_id` | UUID | FK → users.id, not null, on delete cascade |
| `application_id` | UUID | FK → applications.id, not null, on delete cascade |
| `body` | TEXT | not null (Markdown) |
| `created_at` / `updated_at` | TIMESTAMPTZ | — |

Indexes: `(application_id)`, `(user_id)`.

### 3.7 `attachments`

| Column | Type | Constraints |
| --- | --- | --- |
| `id` | UUID | PK |
| `user_id` | UUID | FK → users.id, not null, on delete cascade |
| `application_id` | UUID | FK → applications.id, not null, on delete cascade |
| `kind` | ENUM `attachment_kind` | not null (`resume/cover_letter/other`) |
| `original_filename` | VARCHAR(255) | not null |
| `stored_filename` | VARCHAR(255) | not null (opaque, server-generated) |
| `content_type` | VARCHAR(120) | not null |
| `size_bytes` | INTEGER | not null |
| `created_at` | TIMESTAMPTZ | not null |

Indexes: `(application_id)`, `(user_id)`.

## 4. Soft delete vs hard delete

- **Soft delete** (`companies`, `applications`): preserves history and lets the
  UI offer undo; default repository queries filter `deleted_at IS NULL`.
- **Hard delete** (`interviews`, `notes`, `tasks`, `attachments`): these are
  cheap to recreate and have no analytical value once removed; cascade with
  their parent.

## 5. Referential rules

- Deleting a **user** cascades to all owned rows (account deletion is total).
- Soft-deleting a **company** does not delete its applications; their
  `company_id` is retained, but if a company is *hard* purged, `company_id` is
  set null (applications survive without a company).
- Deleting an **application** cascades to its interviews, notes, and attachments
  (and nulls `tasks.application_id`).

## 6. Migration strategy

- The schema is owned by Alembic. The initial migration creates the enums,
  tables, indexes, and constraints described here.
- Migrations are **reversible** (`downgrade` implemented) and reviewed as code.
- `gen_random_uuid()` requires the `pgcrypto` extension (created in the first
  migration); the ORM also supplies a Python-side UUID default so the same
  models run on SQLite in tests.
