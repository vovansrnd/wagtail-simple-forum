# Changelog — wagtail-simple-forum

All notable changes for this package are documented here. Version numbers below are **prepared release candidates** in this audit bundle; they are not a claim that those versions have already been uploaded to PyPI.

## [0.1.1] — 2026-10-29 — prepared, not yet published

- Sanitize stored post output including legacy-imported content; improve security guidance and operational migration checklist.
- Expanded installation, security, troubleshooting, storage/integration and multi-language documentation.
- Added translated README files for English, Russian, German, Spanish, French, Italian, Brazilian Portuguese, Dutch, Polish, Turkish, Simplified Chinese, Japanese and Korean.
- Static syntax/packaging checks are included in the release bundle. Complete Django/Wagtail integration tests and live storage/permission checks remain a release gate.

## Previous releases

See the package's release history on PyPI and its source repository, where available.

## 2026-10-29 — follow-up audit

- Fixed private-message template context names, hidden anti-spam fields, search result dates, and timestamp verification.
- Added per-session replay friction, prevented regular owners from editing/deleting posts in closed topics, and forced safe `rel` values on forum links.
- Prefetched author groups for moderator badges and documented the `EMAIL_TIMEOUT` requirement.

A runtime test pass on the host's Django/Wagtail versions is still required.
