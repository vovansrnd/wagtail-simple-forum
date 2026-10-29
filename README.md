# wagtail-simple-forum

**A lightweight forum integrated with Wagtail admin.** It provides categories, sections, topics, posts, private messages, moderation, notifications, search, rate limiting, and legacy-URL/import helpers. Content uses the site's Django users and the `django-prose-editor` / `nh3` stack rather than an external forum engine.

[English](README.md) · [Русский](README.ru.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [Italiano](README.it.md) · [Português (Brasil)](README.pt-BR.md) · [Nederlands](README.nl.md) · [Polski](README.pl.md) · [Türkçe](README.tr.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

## Features

- Category → section → topic → post hierarchy, with maintained counters and latest-activity metadata.
- Private-message inbox and conversation threads with pagination and optional recipient notifications.
- Guest posting controls: moderation, honeypot, a signed timestamp token, a signed math challenge, per-session replay detection, and cache-based rate limits.
- Topic moderation: pin/close, approve, soft-delete, moderator groups, and optional staff moderation.
- Search, view counters with time-based deduplication, Unicode slugs, and legacy forum redirects.
- Import command for the old `forum` app, preserving `legacy_id` links and legacy user mappings.
- Template overrides and CSS hooks for matching a site's theme.

## Audit/release status

This source bundle prepares version `0.1.1` for a possible next release. Static syntax/package checks have been run, but a full Django/Wagtail integration suite has not run in the bundle build environment. Do not upload to PyPI until the release checklist in `../../04-docs/UPGRADE_AND_RELEASE.md` is complete.

## Requirements and installation

Package metadata declares `wagtail>=6.0`, `django-prose-editor>=0.26`, and `nh3>=0.2.14`.

```bash
pip install wagtail-simple-forum
```

To install **the candidate source in this bundle** (rather than the already-published PyPI release), run from this package directory:

```bash
python -m pip install .
# For editable development instead:
python -m pip install -e .
```

`pip install wagtail-simple-forum` selects the version currently published on PyPI. The candidate version shown in `pyproject.toml` is not published by this archive operation; publish it only after the release checklist in `../../04-docs/UPGRADE_AND_RELEASE.md` passes.


Add the app after its dependencies:

```python
INSTALLED_APPS = [
    # ... Django and Wagtail apps ...
    "django_prose_editor",
    "wagtail_simple_forum",
]
```

Mount the routes. If you need redirects from an older forum, include the legacy URL patterns before Wagtail's catch-all route:

```python
from django.urls import include, path
from wagtail_simple_forum.legacy_urls import urlpatterns as legacy_forum_urls

urlpatterns = [
    path("forum/", include("wagtail_simple_forum.urls")),
    *legacy_forum_urls,
    # Wagtail's catch-all route goes last.
]
```

Then run:

```bash
python manage.py migrate wagtail_simple_forum
```

## Configuration

All options are optional. Defaults below reflect the current package source.

| Setting | Default | Purpose |
|---|---:|---|
| `FORUM_ALLOWED_HOSTS` | `None` | Restrict forum routes to a list of host names. `None` allows any host accepted by Django. Configure this on multi-site projects. |
| `FORUM_ALLOW_GUESTS` | `True` | Allow guest topics/replies. |
| `FORUM_MODERATE_GUESTS` | `True` | Send guest posts for moderation. |
| `FORUM_STAFF_ARE_MODERATORS` | `True` | Treat `is_staff` users as forum moderators. |
| `FORUM_MODERATOR_GROUPS` | `None` | Django group names that grant moderator capabilities. |
| `FORUM_TRUST_PROXY_HEADERS` | `False` | Trust proxy-supplied client IP headers; enable only behind a trusted, header-sanitizing proxy. |
| `FORUM_AVATAR_URL_GETTER` | `None` | Dotted import path to a callable `get_avatar_url(user) -> str`. |
| `FORUM_TRACK_VIEWS` | `True` | Enable topic view counts. |
| `FORUM_TOPIC_POSTS_PER_PAGE` | `20` | Posts per topic page. |
| `FORUM_SECTION_TOPICS_PER_PAGE` | `30` | Topics per section page. |
| `FORUM_SEARCH_RESULTS_PER_PAGE` | `20` | Search results per page. |
| `FORUM_MAX_POST_LENGTH` | `65535` | Maximum post length. |
| `FORUM_MAX_PM_LENGTH` | `20000` | Maximum private-message length. |
| `FORUM_NOTIFY_ADMINS` | `True` | Email administrators about new topics/replies. |
| `FORUM_NOTIFY_TOPIC_AUTHOR` | `True` | Notify a topic author about replies. |
| `FORUM_NOTIFY_PM_RECIPIENT` | `True` | Notify a private-message recipient. |
| `FORUM_LEGACY_REDIRECT_PERMANENT` | `True` | Use permanent (301) legacy redirects rather than temporary redirects. |
| `FORUM_BASE_URL` | `BASE_URL` or empty | Base URL used when generating absolute links in email. |

Example for a site that should not accept arbitrary hosts:

```python
FORUM_ALLOWED_HOSTS = ["forum.example.com"]
FORUM_ALLOW_GUESTS = True
FORUM_MODERATE_GUESTS = True
FORUM_MODERATOR_GROUPS = ["Forum moderators"]
FORUM_TRUST_PROXY_HEADERS = False
```

Email notifications require working Django email settings. Do not enable proxy-header trust unless the reverse proxy removes client-supplied versions of those headers and sets authoritative values.

## Customizing templates

Override `wagtail_simple_forum/base_forum.html` in your project to integrate site navigation, page width, fonts, and theme. The package ships an example template. Keep the block names used by the package templates when overriding the base. CSS is served from `wagtail_simple_forum/css/forum.css`; add theme overrides in your own static files rather than patching the package.

## Importing from the old `forum` app

The package includes an idempotent import command. Back up the database first, keep the old app installed during the dry run, and compare imported counts before switching traffic:

```bash
python manage.py migrate wagtail_simple_forum
python manage.py forum_import_from_app --source forum --dry-run
python manage.py forum_import_from_app --source forum
python manage.py forum_recalculate_stats
```

The old app must be available to Django while the importer reads it. After validating topics, posts, private messages, legacy IDs, users, and redirects, update URLs and then remove the old app only when no other code depends on its models. Keep a restorable database backup throughout the migration.

## Security and operations

- Run the package migrations and test posting as a guest, member, moderator, and administrator. Also verify that private-message inboxes and thread pages display paginated results, required hidden anti-spam fields are rendered, and closed topics cannot be edited/deleted by regular owners.
- Check rate limits, moderation, private-message access, signed-token expiry/replay behavior, and email content in a staging environment. Token reuse is tracked per browser session to remain compatible with shared page caches.
- Do not render stored post HTML with an unconditional `|safe`; use the package rendering/sanitization path.
- Test legacy redirects before making them permanent; permanent redirects can be cached by browsers and search engines.
- The source bundle does not include a full automated test suite or a version-by-version runtime compatibility matrix.

## Recommended combinations

- **`wagtail-mptt-comments`** is complementary for comments below individual articles; the forum provides longer discussions and private messaging.
- **`wagtail-prose-editor-images`** is useful if you want Wagtail's image chooser in custom Prose editor fields. The forum itself has its own post editor and does not require the chooser plugin.
- Image directory management is optional and independent of forum data.

## License and support

MIT. Source and issue tracker: [GitHub](https://github.com/vovansrnd/wagtail-simple-forum). Include package version and relevant Django/Wagtail settings in reports; never include tokens or private messages.
