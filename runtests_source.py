"""Д67-C: запуск тестов против ИСХОДНИКОВ ветки d67-batch-c (source tree).

Отличие от runtests.py: НЕ требует wheel в site-packages — добавляет
корень репозитория в sys.path до site-packages.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")

import django

django.setup()

import unittest

loader = unittest.TestLoader()
suite = loader.discover("tests", top_level_dir=os.path.dirname(os.path.abspath(__file__)))
runner = unittest.TextTestRunner(verbosity=1)
result = runner.run(suite)
sys.exit(bool(result.failures or result.errors))
