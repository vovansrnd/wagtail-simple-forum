"""Д67-C: запуск тестов против ИСХОДНИКОВ ветки d67-batch-c (source tree).

Отличие от runtests.py: НЕ требует wheel в site-packages — добавляет
корень репозитория в sys.path до site-packages, поэтому пакет
импортируется из исходников. Тестовая БД создаётся DiscoverRunner'ом
(как в обычном Django-прогоне): голый unittest.discover не делает
setup_databases, из-за чего TestCase падали без таблиц.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")

import django

django.setup()

import django.conf  # noqa: E402
from django.test.utils import get_runner  # noqa: E402

runner = get_runner(django.conf.settings)(interactive=False, verbosity=1)
failures = runner.run_tests(["tests"])
sys.exit(bool(failures))
