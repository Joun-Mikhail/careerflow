# Repository Audit (pre-documentation)

> A full-repository pass before the documentation phase, covering code smells,
> duplicated logic, weak documentation, inconsistent naming, and security
> concerns. Concrete issues were fixed in this pass; deliberate trade-offs are
> recorded as accepted.

## Method

Reviewed every backend module and frontend source file, cross-checked the docs
against the implementation, and re-ran the full quality gate (ruff, mypy,
bandit, pip-audit, pytest with coverage).

## Findings

### Fixed in this pass

| Area | Finding | Fix |
| --- | --- | --- |
| Weak documentation | `docs/04-api-design.md` claimed `GET /applications/{id}` "includes counts of interviews/notes", which the `ApplicationRead` schema does not return. | Corrected the doc to describe a plain retrieve. |
| Dead code | `DOCX_TYPE` constant in `tests/integration/test_attachments.py` was unused. | Removed. |

### Reviewed — no change needed

- **Layering & SoC:** routers stay thin; business rules live in services; all
  SQL is in repositories. Confirmed across every resource.
- **Duplicated logic:** the earlier sort/pagination and look-up-or-404
  duplication was already extracted (`apply_sort`, `ensure_found`) in the
  pre-frontend refactor. The remaining one-line `_ensure_application_owned`
  helpers per service are intentionally local and read clearly.
- **Naming:** parallel and consistent across layers (`Application` →
  `application.py` in models/schemas/repositories/services). Query keys,
  hooks, and service modules follow one convention each.
- **Security:** no open items — see [security-review.md](security-review.md).
  bandit and pip-audit are clean.
- **Types:** mypy passes with strict settings on the backend; the frontend uses
  strict TypeScript validated in CI.

### Accepted trade-offs (documented as known limitations)

- **Editing an application's company** from the detail page only offers the
  currently-linked company in the dropdown (the detail view loads one company,
  not the full list). Reassignment is possible from the create flow. Tracked in
  the README's *Known limitations*.
- **No embedded child counts** on the application read model; the detail page
  fetches interviews/notes/attachments separately. Acceptable for current data
  volumes.

## Result

Two concrete issues fixed; no high-impact smells, security concerns, or naming
inconsistencies found. The repository is ready for the documentation phase.
