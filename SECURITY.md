# Security Policy

## Supported versions

CareerFlow is pre-1.0; security fixes land on `main`.

| Version | Supported |
| ------- | --------- |
| `main`  | ✅        |

## Reporting a vulnerability

Please **do not** open a public issue for security vulnerabilities.

Instead, report privately by opening a [GitHub security advisory](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability)
on this repository, or by emailing the maintainers. Include:

- a description of the issue and its impact,
- steps to reproduce (a proof of concept if possible),
- affected components and any suggested remediation.

You can expect an initial acknowledgement within a few days. Once a fix is
ready we will coordinate disclosure.

## Scope & hardening

The application's security design and the findings from the dedicated audit are
documented in:

- [docs/05-security-design.md](docs/05-security-design.md) — threat model and controls
- [docs/security-review.md](docs/security-review.md) — audit results

CI runs `bandit` (static analysis) and `pip-audit` (dependency CVEs) on every
change, and both must pass.
