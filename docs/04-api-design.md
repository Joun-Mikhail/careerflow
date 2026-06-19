# API Design — CareerFlow

> **Version:** 1.0 · **Last updated:** 2026-06-19 · **Base path:** `/api/v1`

The API is REST-style over JSON, documented automatically via OpenAPI at
`/api/docs` (Swagger UI) and `/api/redoc`. This document is the human-readable
contract; the generated schema is the machine-readable source of truth.

## 1. Conventions

- **Versioning:** path-based (`/api/v1`). Breaking changes bump the version.
- **Auth:** `Authorization: Bearer <jwt>` on every endpoint except register,
  login, and health.
- **IDs:** UUID strings.
- **Timestamps:** ISO 8601 / RFC 3339 in UTC (`2026-06-19T14:30:00Z`).
- **Content type:** `application/json` (except attachment upload, which is
  `multipart/form-data`).
- **Scoping:** every resource is implicitly scoped to the authenticated user;
  accessing another user's resource returns `404` (not `403`, to avoid leaking
  existence).

## 2. Pagination, filtering, sorting

List endpoints share a query contract:

| Param | Meaning | Default |
| --- | --- | --- |
| `page` | 1-based page number | `1` |
| `page_size` | items per page (max 100) | `20` |
| `sort` | field to sort by (endpoint-specific allow-list) | `created_at` |
| `order` | `asc` \| `desc` | `desc` |
| `q` | free-text search (endpoint-specific fields) | — |

Paginated responses use a consistent envelope:

```json
{
  "items": [ ... ],
  "page": 1,
  "page_size": 20,
  "total": 137,
  "total_pages": 7
}
```

## 3. Error format

All errors share one shape, produced by the central exception handler:

```json
{
  "error": {
    "code": "not_found",
    "message": "Application not found.",
    "details": null
  }
}
```

| HTTP | `code` | When |
| --- | --- | --- |
| 400 | `bad_request` | Malformed request beyond schema validation. |
| 401 | `unauthorized` | Missing/invalid/expired token. |
| 403 | `forbidden` | Authenticated but not permitted (rare; cross-user is 404). |
| 404 | `not_found` | Resource missing or not owned by caller. |
| 409 | `conflict` | Uniqueness/state conflict (e.g. duplicate email). |
| 422 | `validation_error` | Pydantic field validation; `details` lists fields. |
| 500 | `internal_error` | Unexpected; details suppressed, logged server-side. |

## 4. Endpoints

### 4.1 Auth

| Method | Path | Description | Auth |
| --- | --- | --- | --- |
| `POST` | `/auth/register` | Create account → returns user + token | none |
| `POST` | `/auth/login` | Email+password → access token | none |
| `GET` | `/auth/me` | Current user profile | required |

`POST /auth/login` accepts `{ "email", "password" }` and returns:

```json
{ "access_token": "<jwt>", "token_type": "bearer", "expires_in": 3600 }
```

### 4.2 Companies

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/companies` | List (paginated; `q` on name; filter `industry`) |
| `POST` | `/companies` | Create |
| `GET` | `/companies/{id}` | Retrieve |
| `PATCH` | `/companies/{id}` | Partial update |
| `DELETE` | `/companies/{id}` | Soft delete (204) |

### 4.3 Applications

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/applications` | List; `q` on role; filters `status`, `company_id`; sort `created_at\|applied_at\|updated_at` |
| `POST` | `/applications` | Create |
| `GET` | `/applications/{id}` | Retrieve (includes counts of interviews/notes) |
| `PATCH` | `/applications/{id}` | Partial update (incl. status transition) |
| `DELETE` | `/applications/{id}` | Soft delete (204) |

### 4.4 Interviews

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/applications/{id}/interviews` | List interviews for an application |
| `POST` | `/applications/{id}/interviews` | Create interview |
| `GET` | `/interviews/{id}` | Retrieve |
| `PATCH` | `/interviews/{id}` | Update (incl. result) |
| `DELETE` | `/interviews/{id}` | Delete (204) |

### 4.5 Notes

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/applications/{id}/notes` | List notes |
| `POST` | `/applications/{id}/notes` | Create note |
| `PATCH` | `/notes/{id}` | Update |
| `DELETE` | `/notes/{id}` | Delete (204) |

### 4.6 Tasks

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/tasks` | List; filters `is_completed`, `priority`; sort `due_at\|priority\|created_at` |
| `POST` | `/tasks` | Create |
| `GET` | `/tasks/{id}` | Retrieve |
| `PATCH` | `/tasks/{id}` | Update |
| `POST` | `/tasks/{id}/complete` | Mark complete (sets `completed_at`) |
| `DELETE` | `/tasks/{id}` | Delete (204) |

### 4.7 Attachments

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/applications/{id}/attachments` | List metadata |
| `POST` | `/applications/{id}/attachments` | Upload (`multipart/form-data`: `file`, `kind`) |
| `GET` | `/attachments/{id}/download` | Stream file (owner only) |
| `DELETE` | `/attachments/{id}` | Delete file + metadata (204) |

### 4.8 Dashboard & analytics

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/dashboard/summary` | Counts + success rate + upcoming interviews + pending tasks + recent activity |
| `GET` | `/analytics/applications-by-month` | Time series (last 12 months) |
| `GET` | `/analytics/status-distribution` | Count per status |
| `GET` | `/analytics/industry-distribution` | Count per company industry |
| `GET` | `/analytics/conversion` | Offer rate & interview rate |

### 4.9 System

| Method | Path | Description | Auth |
| --- | --- | --- | --- |
| `GET` | `/health` | Liveness/readiness probe | none |

## 5. Example: create application

**Request**

```http
POST /api/v1/applications
Authorization: Bearer <jwt>
Content-Type: application/json

{
  "company_id": "0b3c…",
  "role_title": "Senior Backend Engineer",
  "status": "applied",
  "salary_min": 120000,
  "salary_max": 150000,
  "salary_currency": "USD",
  "location": "Remote",
  "is_remote": true,
  "application_url": "https://example.com/jobs/123",
  "source": "LinkedIn",
  "applied_at": "2026-06-18T09:00:00Z"
}
```

**Response `201 Created`**

```json
{
  "id": "a1b2…",
  "company_id": "0b3c…",
  "role_title": "Senior Backend Engineer",
  "status": "applied",
  "salary_min": 120000,
  "salary_max": 150000,
  "salary_currency": "USD",
  "location": "Remote",
  "is_remote": true,
  "application_url": "https://example.com/jobs/123",
  "source": "LinkedIn",
  "applied_at": "2026-06-18T09:00:00Z",
  "created_at": "2026-06-19T14:30:00Z",
  "updated_at": "2026-06-19T14:30:00Z"
}
```

## 6. Status transition rules

The API accepts any status value from the enum on update; it does **not**
enforce a strict state machine (a user may move an application backwards, e.g.
re-open after a rejection). Invalid *values* are rejected at validation (422).
This is a deliberate product choice favouring user flexibility over rigidity.
