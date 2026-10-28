# wagtail_simple_forum/wagtail_hooks.py
from django.utils.translation import gettext_lazy as _
from wagtail import hooks
from wagtail.admin.viewsets.base import ViewSetGroup
from wagtail.admin.viewsets.model import ModelViewSet

from .models import (
    ForumCategory,
    ForumLegacyUserMap,
    ForumPost,
    ForumSection,
    ForumTopic,
)


class ForumCategoryViewSet(ModelViewSet):
    model = ForumCategory
    menu_label = _("Categories")
    menu_icon = "folder-open-1"
    inspect_view_enabled = True
    list_display = ("title", "order")
    form_fields = ["title", "order"]
    search_fields = ("title",)


class ForumSectionViewSet(ModelViewSet):
    model = ForumSection
    menu_label = _("Sections")
    menu_icon = "folder-open-inverse"
    inspect_view_enabled = True
    list_display = ("title", "category", "order", "slug")
    list_filter = ("category",)
    form_fields = ["category", "title", "slug", "description", "order"]
    search_fields = ("title", "slug", "description")


class ForumTopicViewSet(ModelViewSet):
    model = ForumTopic
    menu_label = _("Topics")
    menu_icon = "doc-full"
    inspect_view_enabled = True
    list_display = (
        "title",
        "section",
        "author_name",
        "is_approved",
        "is_pinned",
        "is_closed",
        "posts_count",
        "views_count",
    )
    list_filter = ("section", "is_approved", "is_pinned", "is_closed")
    # Derived statistics fields are excluded from edit form
    form_fields = [
        "section",
        "author",
        "author_name",
        "author_email",
        "title",
        "slug",
        "is_pinned",
        "is_closed",
        "is_approved",
    ]
    search_fields = ("title", "author_name", "slug")


class ForumPostViewSet(ModelViewSet):
    model = ForumPost
    menu_label = _("Posts")
    menu_icon = "pilcrow"
    inspect_view_enabled = True
    list_display = (
        "topic",
        "author_name",
        "is_approved",
        "is_deleted",
        "created_at",
        "edited_at",
    )
    list_filter = ("topic__section", "is_approved", "is_deleted")
    # System timestamps and editors are excluded from manual modification
    form_fields = [
        "topic",
        "author",
        "author_name",
        "author_email",
        "content",
        "is_approved",
        "is_deleted",
    ]
    search_fields = ("content", "author_name", "topic__title")


class ForumLegacyUserMapViewSet(ModelViewSet):
    model = ForumLegacyUserMap
    menu_label = _("Legacy users")
    menu_icon = "user"
    inspect_view_enabled = True
    list_display = ("legacy_id", "legacy_username", "display_name", "user", "role")
    list_filter = ("role",)
    form_fields = ["legacy_id", "legacy_username", "display_name", "user", "role"]
    search_fields = ("legacy_username", "display_name", "user__username")


class ForumAdminGroup(ViewSetGroup):
    menu_label = _("Forum")
    menu_icon = "comments"
    menu_order = 250
    items = (
        ForumCategoryViewSet("forum_categories"),
        ForumSectionViewSet("forum_sections"),
        ForumTopicViewSet("forum_topics"),
        ForumPostViewSet("forum_posts"),
        ForumLegacyUserMapViewSet("forum_legacy_users"),
    )


@hooks.register("register_admin_viewset")
def register_forum_group():
    return ForumAdminGroup()
