# Backend Architecture Review (pre-frontend)

> Conducted after Phase 12, before frontend work begins. Goal: catch weak
> abstractions while the backend is small enough to fix cheaply.

## What was reviewed

The full backend: layering (router → service → repository → model), error
handling, configuration, and the cross-cutting helpers. The layering held up
well — routers stayed thin, business rules and ownership checks live in
services, and all SQL is confined to repositories.

## Findings & actions

| # | Finding | Severity | Action |
| --- | --- | --- | --- |
| 1 | Sort/order/pagination logic was duplicated verbatim in three repositories (`company`, `application`, `task`), each re-deriving `asc/desc` and the id tiebreaker. | Medium | Extracted `BaseRepository.apply_sort(...)`; the three repositories now call it. Removes ~5 lines of duplicated query plumbing each and guarantees consistent tiebreaking. |
| 2 | Every service repeated the `value = repo.get(...); if value is None: raise NotFoundError(...)` pattern (10+ sites). | Medium | Added `core.errors.ensure_found(value, message)`. Each lookup is now a single expressive line; parent-ownership checks reuse it too. |
| 3 | `StatsRepository.count_applications` was dead code — totals are derived from the status-distribution sum. | Low | Removed. |

## Considered but intentionally left as-is

- **Per-request `Service(db)` instantiation** in routers: lightweight and
  explicit; introducing DI providers would add indirection without real benefit
  at this size.
- **No `BaseService`**: services share little beyond the `get_or_404` pattern,
  which the `ensure_found` helper already covers. A base class would be
  premature.
- **`_ensure_*_owned` helpers per service**: they read clearly and each carries
  a domain-specific message; collapsing them further would obscure intent.

## Verification

After refactoring: `ruff` clean, `ruff format` clean, `mypy` clean (64 files),
and the full test suite green with no behavioural changes.
