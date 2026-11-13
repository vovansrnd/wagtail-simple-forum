# Changelog — wagtail-simple-forum

## [0.1.3] — 2026-11-14

- Skip redundant permission and moderator-group checks when staff users are already moderators by host configuration.
- Add dependency constraint `django-js-asset<5`: django-js-asset 5.x renames the
  import module and rejects import-map js lists, which breaks the media of
  django-prose-editor 0.27.x forms on fresh installs.


All notable changes for this package are documented here. PyPI availability is tracked per release: entries below describe the package state at that version; publication happens separately once approved.

## [0.1.2] — 2026-11-09

- Rebuilt so the wheel matches repository HEAD: PyPI's 0.1.1 was cut
  before the 2026-10-29 follow-up fixes (eb2f670) landed.
- Private messages: inbox/threads render the paginated `threads_page`
  context (the old `threads` variable no longer exists).
- Topic/reply forms render ALL hidden anti-spam fields again
  (submit_token, captcha challenge) instead of the removed
  `form.submit_time`.
- submit_token now signs the form creation timestamp server-side:
  maximum lifetime 12 h, submissions faster than 3 s are rejected,
  tampered signatures rejected; captcha signature uses salted HMAC.
- Per-session replay protection: consumed tokens are tracked in the
  session and rejected on reuse, consumed only after every field
  validates.
- Staff can edit posts in closed topics; redundant per-request group
  queries removed.
- 13 regression tests added (token states, captcha, templates) that
  run against the installed wheel.

**Rollback:** `pip install wagtail-simple-forum==0.1.1` (PyPI).
**Tested with:** Wagtail 8.0.1/8.1, Django 6.0.9, Python 3.14.

## [0.1.1] — 2026-10-29

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
