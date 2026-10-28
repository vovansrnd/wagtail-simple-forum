# wagtail_simple_forum/legacy_urls.py
import math
import re

from django.conf import settings
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import re_path, reverse

from .models import ForumPost, ForumSection, ForumTopic
from .views import _posts_per_page, _topics_per_page, forum_host_required

PERMANENT_REDIRECT = getattr(settings, "FORUM_LEGACY_REDIRECT_PERMANENT", True)


def _safe_int(value):
    """Safely extracts a 32-bit positive integer or returns None."""
    if not value:
        return None
    val_str = str(value).strip()
    if val_str.isdigit() and len(val_str) <= 10:
        val = int(val_str)
        return val if val <= 2147483647 else None
    return None


@forum_host_required
def legacy_viewtopic(request):
    pid = _safe_int(request.GET.get("pid") or request.GET.get("p"))
    topic_id = _safe_int(request.GET.get("id") or request.GET.get("t"))
    start = _safe_int(request.GET.get("start"))

    # Direct legacy post resolution with exact page calculation
    if pid:
        post = get_object_or_404(
            ForumPost.objects.filter(
                is_approved=True, is_deleted=False, topic__is_approved=True
            ).select_related("topic"),
            legacy_id=pid,
        )
        preceding = (
            post.topic.posts.filter(is_approved=True, is_deleted=False)
            .filter(
                Q(created_at__lt=post.created_at)
                | Q(created_at=post.created_at, id__lt=post.id)
            )
            .count()
            + 1
        )
        page_num = max(1, math.ceil(preceding / _posts_per_page()))

        base_url = reverse(
            "wagtail_simple_forum:topic_view", kwargs={"slug": post.topic.slug}
        )
        return redirect(
            f"{base_url}?page={page_num}#post-{post.id}", permanent=PERMANENT_REDIRECT
        )

    if topic_id:
        topic = get_object_or_404(
            ForumTopic.objects.filter(is_approved=True), legacy_id=topic_id
        )
        url = reverse("wagtail_simple_forum:topic_view", kwargs={"slug": topic.slug})
        if start:
            page_num = max(1, math.ceil((start + 1) / _posts_per_page()))
            url = f"{url}?page={page_num}"
        return redirect(url, permanent=PERMANENT_REDIRECT)

    raise Http404()


@forum_host_required
def legacy_viewforum(request):
    forum_id = _safe_int(request.GET.get("id") or request.GET.get("f"))
    start = _safe_int(request.GET.get("start"))

    if forum_id:
        section = get_object_or_404(ForumSection, legacy_id=forum_id)
        url = reverse(
            "wagtail_simple_forum:section_view", kwargs={"slug": section.slug}
        )
        if start:
            page_num = max(1, math.ceil((start + 1) / _topics_per_page()))
            url = f"{url}?page={page_num}"
        return redirect(url, permanent=PERMANENT_REDIRECT)

    raise Http404()


urlpatterns = [
    re_path(r"^(?:forum/)?viewtopic\.php$", legacy_viewtopic, name="legacy_viewtopic"),
    re_path(r"^(?:forum/)?viewforum\.php$", legacy_viewforum, name="legacy_viewforum"),
]
