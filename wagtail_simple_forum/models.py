# wagtail_simple_forum/models.py
import logging
from functools import cached_property, lru_cache

from django.conf import settings
from django.db import models
from django.db.models import Count
from django.utils import timezone
from django.utils.module_loading import import_string
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django_prose_editor.fields import ProseEditorField

logger = logging.getLogger(__name__)

FORUM_POST_EXTENSIONS = {
    "Bold": True,
    "Italic": True,
    "Blockquote": True,
    "BulletList": True,
    "ListItem": True,
    "OrderedList": True,
    "Link": {"enableTarget": True, "protocols": ["http", "https", "mailto"]},
    "Code": True,
    "CodeBlock": True,
}

_FORUM_AVATAR_SVG = (
    '<svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor" '
    'aria-hidden="true"><path d="M12 12c2.7 0 4.9-2.2 4.9-4.9S14.7 2.2 12 2.2 '
    '7.1 4.4 7.1 7.1 9.3 12 12 12zm0 2.5c-3.3 0-9.8 1.6-9.8 4.9v2.4h19.6v-2.4c0-3.3-6.5-4.9-9.8-4.9z"/></svg>'
)


@lru_cache(maxsize=1)
def _get_avatar_getter():
    raw = getattr(settings, "FORUM_AVATAR_URL_GETTER", None)
    if isinstance(raw, str):
        try:
            return import_string(raw)
        except ImportError:
            return None
    return raw if callable(raw) else None


class ForumAuthorDisplayMixin:
    """Shared display helpers for topics, posts, and private messages."""

    def _legacy_map(self):
        # Optional mapping of imported (legacy) users to Django accounts.
        # Accessed through getattr so hosts without the mapping skip it free.
        author = getattr(self, "author", None)
        if author:
            try:
                return author.forum_legacy_map
            except ForumLegacyUserMap.DoesNotExist:
                pass
            except AttributeError:
                pass
        return None

    def display_author_name(self):
        legacy_map = self._legacy_map()
        if legacy_map and legacy_map.display_name:
            return legacy_map.display_name
        author = getattr(self, "author", None)
        if author:
            return author.get_full_name() or author.get_username()
        return getattr(self, "author_name", "") or _("Anonymous")

    @cached_property
    def author_role(self):
        legacy_map = self._legacy_map()
        if legacy_map:
            if legacy_map.role == ForumLegacyUserMap.ROLE_ADMIN:
                return "admin"
            if legacy_map.role == ForumLegacyUserMap.ROLE_MODERATOR:
                return "moderator"

        author = getattr(self, "author", None)
        if not author:
            return "guest"

        if author.is_superuser:
            return "admin"

        is_staff_mod = (
            getattr(settings, "FORUM_STAFF_ARE_MODERATORS", True) and author.is_staff
        )
        has_perm_mod = author.has_perm(
            f"{ForumTopic._meta.app_label}.change_forumtopic"
        )

        moderator_groups = getattr(settings, "FORUM_MODERATOR_GROUPS", None)
        in_mod_group = bool(
            moderator_groups
            and author.groups.filter(name__in=moderator_groups).exists()
        )

        if is_staff_mod or has_perm_mod or in_mod_group:
            return "moderator"

        return "member"

    def get_author_role(self):
        return self.author_role

    @property
    def avatar_tag(self):
        author = getattr(self, "author", None)
        if author:
            getter = _get_avatar_getter()
            if getter:
                try:
                    url = getter(author)
                    if url:
                        from django.utils.html import format_html

                        return format_html(
                            '<img src="{}" class="forum-avatar" alt="">', url
                        )
                except Exception as e:
                    logger.exception(
                        f"Error resolving avatar for user #{author.pk}: {e}"
                    )

        role = self.author_role
        return mark_safe(
            f'<span class="forum-avatar forum-avatar--fallback forum-avatar--{role}">{_FORUM_AVATAR_SVG}</span>'
        )

    @property
    def author_badge_class(self):
        return self.author_role

    @property
    def author_badge_text(self):
        return {
            "admin": _("Admin"),
            "moderator": _("Moderator"),
            "member": _("Member"),
            "guest": _("Guest"),
        }[self.author_role]


class ForumCategory(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    order = models.IntegerField(default=0, verbose_name=_("Order"))
    legacy_id = models.PositiveIntegerField(null=True, blank=True, unique=True)

    class Meta:
        ordering = ["order", "title"]
        verbose_name = _("Forum Category")
        verbose_name_plural = _("Forum Categories")

    def __str__(self):
        return self.title


class ForumSection(models.Model):
    category = models.ForeignKey(
        ForumCategory,
        on_delete=models.CASCADE,
        related_name="sections",
        verbose_name=_("Category"),
    )
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    slug = models.SlugField(
        max_length=255, unique=True, allow_unicode=True, verbose_name=_("Slug")
    )
    description = models.TextField(blank=True, verbose_name=_("Description"))
    order = models.IntegerField(default=0, verbose_name=_("Order"))
    legacy_id = models.PositiveIntegerField(null=True, blank=True, unique=True)

    class Meta:
        ordering = ["order", "title"]
        verbose_name = _("Forum Section")
        verbose_name_plural = _("Forum Sections")

    def __str__(self):
        return self.title


class ForumTopic(ForumAuthorDisplayMixin, models.Model):
    section = models.ForeignKey(
        ForumSection,
        on_delete=models.CASCADE,
        related_name="topics",
        verbose_name=_("Section"),
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="forum_topics",
        verbose_name=_("Author (User)"),
    )
    author_name = models.CharField(
        max_length=255, blank=True, verbose_name=_("Author name")
    )
    author_email = models.EmailField(blank=True, verbose_name=_("Author Email"))
    title = models.CharField(max_length=255, verbose_name=_("Topic Title"))
    slug = models.SlugField(
        max_length=255, unique=True, allow_unicode=True, verbose_name=_("Slug")
    )

    created_at = models.DateTimeField(
        default=timezone.now, db_index=True, verbose_name=_("Created at")
    )
    views_count = models.PositiveIntegerField(default=0, verbose_name=_("Views"))
    is_pinned = models.BooleanField(default=False, verbose_name=_("Pinned"))
    is_closed = models.BooleanField(default=False, verbose_name=_("Closed"))
    is_approved = models.BooleanField(default=True, verbose_name=_("Approved"))

    posts_count = models.PositiveIntegerField(default=0, verbose_name=_("Total posts"))
    last_post_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Last post at")
    )
    last_post_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        verbose_name=_("Last post by"),
    )
    legacy_id = models.PositiveIntegerField(null=True, blank=True, unique=True)

    class Meta:
        ordering = ["-is_pinned", "-last_post_at", "-created_at"]
        verbose_name = _("Forum Topic")
        verbose_name_plural = _("Forum Topics")
        indexes = [
            models.Index(
                fields=["section", "is_approved", "is_pinned", "-last_post_at"],
                name="forum_topic_list_idx",
            ),
        ]

    def __str__(self):
        return self.title

    def recalculate_stats(self):
        """Full statistics recalculation used after moderation or deletions."""
        visible_posts = self.posts.filter(is_deleted=False, is_approved=True)
        total_count = visible_posts.count()
        last_post = (
            visible_posts.order_by("-created_at", "-id")
            .select_related("author")
            .first()
        )

        self.posts_count = total_count
        self.last_post_at = last_post.created_at if last_post else self.created_at
        self.last_post_by = (
            last_post.author if last_post and last_post.author_id else None
        )
        self.save(update_fields=["posts_count", "last_post_at", "last_post_by"])


class ForumPost(ForumAuthorDisplayMixin, models.Model):
    topic = models.ForeignKey(
        ForumTopic,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name=_("Topic"),
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="forum_posts",
        verbose_name=_("Author (User)"),
    )
    author_name = models.CharField(
        max_length=255, blank=True, verbose_name=_("Author name")
    )
    author_email = models.EmailField(blank=True, verbose_name=_("Author Email"))
    content = ProseEditorField(
        extensions=FORUM_POST_EXTENSIONS,
        sanitize=True,
        verbose_name=_("Message text"),
    )
    created_at = models.DateTimeField(
        default=timezone.now, db_index=True, verbose_name=_("Created at")
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))
    edited_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Edited at"))
    edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        verbose_name=_("Edited by"),
    )
    is_approved = models.BooleanField(default=True, verbose_name=_("Approved"))
    is_deleted = models.BooleanField(default=False, verbose_name=_("Deleted"))
    legacy_id = models.PositiveIntegerField(null=True, blank=True, unique=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = _("Forum Post")
        verbose_name_plural = _("Forum Posts")
        indexes = [
            models.Index(
                fields=["topic", "is_deleted", "is_approved", "created_at"],
                name="forum_post_thread_idx",
            ),
        ]

    def __str__(self):
        return f"Post in '{self.topic.title}'"


class ForumLegacyUserMap(models.Model):
    """
    Links an imported (legacy) forum account to a Django user, keeping the
    display name and role the account had on the source forum. Optional:
    hosts that did not import data simply have no rows here.
    """

    ROLE_ADMIN = "admin"
    ROLE_MODERATOR = "moderator"
    ROLE_USER = "user"
    ROLE_CHOICES = (
        (ROLE_ADMIN, _("Admin")),
        (ROLE_MODERATOR, _("Moderator")),
        (ROLE_USER, _("User")),
    )

    legacy_id = models.PositiveIntegerField(unique=True)
    legacy_username = models.CharField(max_length=200, blank=True)
    display_name = models.CharField(max_length=255, blank=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="forum_legacy_map",
    )
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default=ROLE_USER
    )

    class Meta:
        verbose_name = _("Legacy user map")
        verbose_name_plural = _("Legacy user maps")
        ordering = ["legacy_id"]

    def __str__(self):
        return f"{self.legacy_username or self.legacy_id} -> {self.user}"

    @property
    def role_label(self):
        return dict(self.ROLE_CHOICES).get(self.role, _("User"))


class PrivateMessageThread(models.Model):
    subject = models.CharField(max_length=255, verbose_name=_("Subject"))
    starter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pm_threads_started",
        verbose_name=_("Sender"),
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pm_threads_received",
        verbose_name=_("Recipient"),
    )
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    last_message_at = models.DateTimeField(null=True, blank=True, db_index=True)
    messages_count = models.PositiveIntegerField(default=0)
    legacy_id = models.PositiveIntegerField(unique=True, null=True, blank=True)

    class Meta:
        ordering = ["-last_message_at", "-created_at"]
        verbose_name = _("Private Message Thread")
        verbose_name_plural = _("Private Message Threads")

    def recalculate_stats(self):
        agg = self.messages.aggregate(total=Count("id"))
        last = self.messages.order_by("-created_at", "-id").first()
        self.messages_count = agg["total"] or 0
        self.last_message_at = last.created_at if last else self.created_at
        self.save(update_fields=["messages_count", "last_message_at"])

    def __str__(self):
        return self.subject


class PrivateMessage(ForumAuthorDisplayMixin, models.Model):
    thread = models.ForeignKey(
        PrivateMessageThread,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name=_("Thread"),
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pm_messages",
        verbose_name=_("Author"),
    )
    author_name = models.CharField(
        max_length=255, blank=True, verbose_name=_("Author name")
    )
    content = ProseEditorField(
        extensions=FORUM_POST_EXTENSIONS,
        sanitize=True,
        verbose_name=_("Message"),
    )
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    edited_at = models.DateTimeField(null=True, blank=True)
    legacy_id = models.PositiveIntegerField(unique=True, null=True, blank=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = _("Private Message")
        verbose_name_plural = _("Private Messages")

    def __str__(self):
        return f"PM in {self.thread.subject}"
