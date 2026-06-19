# Product Requirements Document — CareerFlow

> **Status:** Approved for build · **Version:** 1.0 · **Last updated:** 2026-06-19

## 1. Overview

CareerFlow is a SaaS web application that helps individual job seekers run their
job search like a pipeline. Instead of scattering applications across
spreadsheets, email threads, and sticky notes, users track every company,
application, interview, task, and note in one place — and see analytics that
tell them where their search is working and where it is stalling.

This document defines *what* CareerFlow does and *for whom*. The *how* lives in
the [Technical Architecture](02-technical-architecture.md),
[Database Design](03-database-design.md), and [API Design](04-api-design.md)
documents.

## 2. Problem statement

Job seekers routinely manage 20–80 active applications over a multi-month
search. The information that matters — which companies, what stage each
application is at, when the next interview is, who the interviewer was, what
follow-up is due — is fragmented across tools that were never designed for it.
The consequences are concrete:

- **Missed follow-ups.** A "thank-you" email or a recruiter ping never sent.
- **Double-applying** to the same company, or forgetting one was applied to.
- **No feedback loop.** No view of conversion rates, so the seeker can't tell
  whether the problem is volume, resume quality, or interview performance.
- **Interview-day scramble.** Notes from the phone screen aren't in front of
  the seeker when the on-site comes.

## 3. Goals & non-goals

### 3.1 Goals

- Provide a single source of truth for a personal job search.
- Make the *state* of every application obvious at a glance (pipeline view).
- Surface what needs attention *now* (upcoming interviews, due tasks).
- Quantify the search with analytics (conversion, volume over time).
- Be fast, secure, and pleasant enough to use daily.

### 3.2 Non-goals (v1)

- Multi-user collaboration / shared workspaces (single-user accounts only).
- Job-board scraping or automated application submission.
- Email or calendar integration (planned — see
  [Roadmap](../README.md#roadmap)).
- Native mobile apps (the web app is responsive instead).
- Recruiter- or employer-side features.

## 4. Target users & personas

| Persona | Description | Primary need |
| --- | --- | --- |
| **Active seeker (primary)** | Currently job-hunting, 20–80 applications in flight. | Stay organized; never miss a follow-up. |
| **Passive seeker** | Employed, exploring selectively. | Track a handful of high-value opportunities. |
| **Career switcher** | Applying across industries. | Compare where traction is coming from. |

## 5. User journeys

1. **Onboarding** — A new user registers, logs in, and lands on an empty
   dashboard with clear calls to action ("Add your first company").
2. **Logging an application** — The user creates (or selects) a company, then
   adds an application with role, status `Applied`, salary range, location, and
   the posting URL.
3. **Advancing the pipeline** — As the process moves, the user updates the
   application status (`Applied → Assessment → Interview → Offer`) and schedules
   interviews against it.
4. **Preparing for an interview** — Before an interview, the user opens the
   application, reviews prior interview notes and application notes, and checks
   off preparation tasks.
5. **Staying on top of follow-ups** — The dashboard shows pending tasks and
   upcoming interviews; the user works that list daily.
6. **Reflecting** — Periodically the user opens Analytics to see application
   volume by month, status distribution, and conversion rates.

## 6. Functional requirements

Requirements are labelled `FR-<area>-<n>` and referenced by tests and commits.

### 6.1 Authentication (`FR-AUTH`)

- `FR-AUTH-1` Users register with email + password.
- `FR-AUTH-2` Passwords are stored only as bcrypt hashes.
- `FR-AUTH-3` Users log in and receive a short-lived JWT access token.
- `FR-AUTH-4` All data endpoints require a valid token and are scoped to the
  authenticated user.
- `FR-AUTH-5` A user can retrieve their own profile (`/auth/me`).

### 6.2 Companies (`FR-CO`)

- `FR-CO-1` CRUD for companies (name, website, industry, location, notes).
- `FR-CO-2` List companies with pagination, search by name, and filter by
  industry.
- `FR-CO-3` Deleting a company soft-deletes it; its applications are handled per
  the rules in [Database Design §5](03-database-design.md#5-referential-rules).

### 6.3 Applications (`FR-APP`)

- `FR-APP-1` CRUD for applications, each linked to one company.
- `FR-APP-2` Status is one of: `Wishlist, Applied, Assessment, Interview,
  Final Interview, Offer, Rejected, Accepted`.
- `FR-APP-3` Fields: role title, status, salary min/max + currency, location,
  remote flag, application URL, source, applied date.
- `FR-APP-4` List with search (role/company), filter (status, company), sort
  (created, applied date, updated), and pagination.

### 6.4 Interviews (`FR-INT`)

- `FR-INT-1` CRUD for interviews, each linked to one application.
- `FR-INT-2` Fields: scheduled date/time, round type, interviewer name, mode
  (phone/video/onsite), result (`pending/passed/failed/cancelled`), notes.
- `FR-INT-3` An application may have many interviews.

### 6.5 Tasks (`FR-TASK`)

- `FR-TASK-1` CRUD for tasks; optionally linked to an application.
- `FR-TASK-2` Fields: title, description, priority (`low/medium/high`), due
  date, completed flag.
- `FR-TASK-3` Filter by completion/priority and sort by due date/priority.

### 6.6 Notes (`FR-NOTE`)

- `FR-NOTE-1` CRUD for notes attached to an application.
- `FR-NOTE-2` Body supports Markdown (rendered safely on the client).

### 6.7 Attachments (`FR-ATT`)

- `FR-ATT-1` Upload documents (resume, cover letter) linked to an application.
- `FR-ATT-2` Only allowed types (PDF, DOCX) up to a configured size limit.
- `FR-ATT-3` Store metadata (filename, content type, size); files live on disk
  outside the web root, served only to the owning user.

### 6.8 Dashboard & analytics (`FR-DASH`, `FR-ANALYTICS`)

- `FR-DASH-1` Summary counts: total applications, interviews, offers,
  rejections, success rate, upcoming interviews, pending tasks, recent activity.
- `FR-ANALYTICS-1` Charts: applications by month, status distribution, industry
  distribution, offer rate, interview rate.

## 7. Non-functional requirements

| Area | Requirement |
| --- | --- |
| **Performance** | List endpoints respond < 200 ms for typical data (p95, local). |
| **Security** | See [Security Design](05-security-design.md). All data user-scoped; JWT auth; input validation; secure file handling. |
| **Reliability** | Stateless API; migrations are reversible; no destructive operations without confirmation in the UI. |
| **Accessibility** | Keyboard-navigable, labelled forms, sufficient colour contrast in both themes. |
| **Portability** | Entire stack runs via `docker compose up`. |
| **Testability** | Backend ≥ 80% line coverage; deterministic test suite. |
| **Observability** | Structured request logging; health endpoint. |

## 8. Success metrics (illustrative for a portfolio context)

- A user can go from registration to a logged application in under two minutes.
- Dashboard reflects new data without a manual refresh (query invalidation).
- 100% of data endpoints reject unauthenticated and cross-user access.

## 9. Acceptance criteria

The product is "done" when every functional requirement above has: an
implemented endpoint/UI, automated test coverage, and documentation in the API
guide — and the [Final Quality Gate](../README.md) checklist passes.
