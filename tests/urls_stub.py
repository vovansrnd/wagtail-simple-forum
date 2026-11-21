"""Заглушка urlconf: реальные маршруты плагина под неймспейсом."""
from django.urls import include, path

urlpatterns = [path("forum/", include("wagtail_simple_forum.urls"))]
