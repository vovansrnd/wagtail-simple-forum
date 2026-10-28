# wagtail_simple_forum/templatetags/forum_tags.py
from django import template

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
