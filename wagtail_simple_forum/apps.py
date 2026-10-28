# wagtail_simple_forum/apps.py
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WagtailSimpleForumConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "wagtail_simple_forum"
    verbose_name = _("Wagtail Simple Forum")

    def ready(self):
        # Register signals for automated statistics recalculation
        import wagtail_simple_forum.signals  # noqa
