# CareerFlow privacy policy

_Last updated: 2026-06-24_

CareerFlow ("the Service") is an open-source job-search tracker. This policy
explains what personal data we collect, why we collect it, where it is stored,
and how to delete it.

## Who we are

CareerFlow is maintained by Joun Mikhail and the open-source contributors listed
on [GitHub](https://github.com/Joun-Mikhail/careerflow). For privacy questions
or data-deletion requests, contact:

> **gptmath55@gmail.com**

## Data we store

When you create an account, the Service stores:

| Data | Source | Purpose |
| --- | --- | --- |
| Email address | You provide it at signup | Account login and password reset |
| Password hash (bcrypt) | Derived from your password | Authentication; the plain password is never stored |
| Full name (optional) | You provide it in Settings | Personalising the UI |
| Companies, applications, interviews, tasks, notes, offers | You enter them in the app | The job-search records you are tracking |
| File attachments (resumes, cover letters, etc.) | You upload them | Per-application document storage |
| JWT refresh-token rotation records | Issued by the server | Maintaining an authenticated session |
| Audit log entries (`login`, `register`, `password_changed`, `offer_decision`) | Generated server-side | Security and abuse monitoring |

We do **not** collect device identifiers, advertising IDs, contacts, microphone
or camera input, location data, or any third-party analytics signals beyond
what is documented below.

### Optional, opt-in third parties

| Service | When it runs | What it sees |
| --- | --- | --- |
| Sentry (error reporting) | Only if an operator sets `SENTRY_DSN` / `VITE_SENTRY_DSN` | Stack traces and the URL of failed requests, with PII scrubbed |

If you self-host CareerFlow, you control whether Sentry is enabled.

## Where data lives

- **Database** — application records and user accounts are stored in the
  PostgreSQL database configured by the operator (Railway-managed Postgres
  in the public reference deployment).
- **Attachments** — uploaded files are stored on the server's local disk under
  the `UPLOAD_DIR` configured by the operator.
- **Tokens** — JWT access and refresh tokens are stored in your device's
  `localStorage` (web) or the platform-equivalent key/value store (mobile).

We do not sell or share your data with advertisers, brokers, or third parties.

## How long we keep data

Account data is retained for as long as the account exists. Audit-log entries
are retained for **90 days** by the reference deployment.

You can delete your data at any time:

1. From the app: **Settings → Delete account** (where available) removes all
   user-scoped records, attachments, and audit entries.
2. By email: send a deletion request to **gptmath55@gmail.com**.

Self-hosted deployments are controlled by the operator running that instance.

## Children

CareerFlow is intended for users aged 16 and over. We do not knowingly collect
data from children under 16.

## Security

- Passwords are hashed with **bcrypt** (cost factor 12).
- JWT tokens are signed with HS256 and rotated on refresh.
- All API traffic in the reference deployment is served over HTTPS.
- Auth endpoints are rate-limited (10 requests/minute per IP) to slow brute
  force attempts.
- File uploads are size-capped, content-type-sniffed, and served with
  `Content-Disposition: attachment` and `X-Content-Type-Options: nosniff`.

No system is perfectly secure. Report vulnerabilities under our
[Security Policy](../SECURITY.md).

## Your rights (GDPR / UK GDPR)

If you are in the EU or UK, you have the right to:

- access your data (request a JSON export by emailing the address above),
- correct or update it,
- delete it,
- restrict or object to processing,
- lodge a complaint with your supervisory authority.

## Changes to this policy

Material changes will be announced via the
[CHANGELOG](../CHANGELOG.md). The "Last updated" date at the top of this file
reflects the most recent revision.
