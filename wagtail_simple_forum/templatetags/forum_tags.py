# wagtail_simple_forum/templatetags/forum_tags.py
import nh3

from django import template
from django.utils.safestring import mark_safe

from wagtail_simple_forum.models import ForumPost, ForumTopic

register = template.Library()


@register.simple_tag
def get_latest_forum_posts(count=5):
    """Returns the most recent active posts across the forum."""
    return (
        ForumPost.objects.filter(
            is_approved=True, is_deleted=False, topic__is_approved=True
        )
        .select_related("topic", "author")
        .order_by("-created_at")[:count]
    )


@register.simple_tag
def get_latest_forum_topics(count=5):
    """Returns the most recent active topics (ideal for blog sidebars)."""
    return (
        ForumTopic.objects.filter(is_approved=True)
        .select_related("section", "author", "last_post_by")
        .order_by("-last_post_at", "-created_at")[:count]
    )


_FORUM_HTML_TAGS = {
    "p", "br", "b", "strong", "i", "em", "u", "s", "del",
    "blockquote", "ul", "ol", "li", "a", "code", "pre",
    "h2", "h3", "hr",
}
_FORUM_HTML_ATTRIBUTES = {"a": {"href", "title", "target"}}


@register.filter(is_safe=True)
def forum_html(value):
    """Safely render forum rich text, including content imported from legacy apps.

    Model/form validation is not enough: bulk imports may bypass it, so stored
    HTML is sanitized again at the output boundary.
    """
    if not value:
        return ""
    cleaned = nh3.clean(
        str(value),
        tags=_FORUM_HTML_TAGS,
        attributes=_FORUM_HTML_ATTRIBUTES,
        link_rel="nofollow ugc noopener noreferrer",
    )
    return mark_safe(cleaned)
