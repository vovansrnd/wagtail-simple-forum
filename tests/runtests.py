#!/usr/bin/env python
"""Д61: запуск регрессионных тестов антиполей/токена/шаблонов.

Гарантирует, что тестируется WHEEL-установка wagtail_simple_forum из
site-packages (версия из pyproject — 0.1.3 на ветке d67-batch-c), а не
editable-исходники: runtests падает, если
пакет импортировался из каталога исходников.

    python runtests.py
"""
import os
import sys

import django

# tests-пакет — в КОНЕЦ sys.path: site-packages (wheel из pyproject) должен
# выигрывать импорт wagtail_simple_forum у каталога исходников.
_repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (_tests_dir := os.path.dirname(os.path.abspath(__file__)), _repo_root):
    if _p not in sys.path:
        sys.path.append(_p)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")
django.setup()

import wagtail_simple_forum  # noqa: E402

_pkg = wagtail_simple_forum.__file__.replace(os.sep, "/")
if "site-packages" not in _pkg:
    sys.exit(f"ОШИБКА Д61: импортирован НЕ wheel: {_pkg}")
print("проверяемый пакет (wheel):", _pkg)

import django.conf  # noqa: E402
from django.test.utils import get_runner  # noqa: E402

runner = get_runner(django.conf.settings)(interactive=False, verbosity=2)
failures = runner.run_tests(["tests"])
sys.exit(bool(failures))
