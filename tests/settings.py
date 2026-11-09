"""Минимальные настройки для регрессионных тестов плагина (Д61).

НЕ производственные: sqlite :memory:, секрет-заглушка. Пакет
wagtail_simple_forum должен резолвиться из site-packages (wheel 0.1.2).
"""
import os

SECRET_KEY = "d61-test-only-not-a-production-secret"
DEBUG = True
USE_TZ = True
USE_I18N = True
TIME_ZONE = "UTC"
STATIC_URL = "/static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "taggit",
    "modelcluster",
    "django_prose_editor",
    "wagtail",
    "wagtail.images",
    "wagtail.documents",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.search",
    "wagtail.admin",
    "wagtail.embeds",
    "wagtail_simple_forum",
]
MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [os.path.join(os.path.dirname(__file__), "stub_templates")],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
    ]},
}]
WAGTAIL_SITE_NAME = "test"
ROOT_URLCONF = "tests.urls_stub"
