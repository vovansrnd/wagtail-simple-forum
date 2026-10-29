# wagtail_simple_forum/views.py
import hashlib
import logging
import math
import secrets
from concurrent.futures import ThreadPoolExecutor
from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.core.cache import cache
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Count, F, OuterRef, Q, Subquery, Sum
from django.db.models.functions import Coalesce
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from .forms import (
    ForumPostEditForm,
    ForumReplyForm,
    ForumTopicForm,
    PrivateMessageReplyForm,
    PrivateMessageThreadForm,
)
from .models import (
    ForumCategory,
    ForumPost,
    ForumSection,
    ForumTopic,
    PrivateMessage,
    PrivateMessageThread,
)

logger = logging.getLogger(__name__)

_mail_pool = ThreadPoolExecutor(max_workers=4, thread_name_prefix="forum-mail")


# =========================================================
# HOST RESTRICTION & RATE LIMITING
# =========================================================
def _forum_allowed_on_host(request):
    allowed = getattr(settings, "FORUM_ALLOWED_HOSTS", None)
    if allowed is None:
        return True

    current_host = request.get_host().lower().split(":")[0].rstrip(".")
    normalized_allowed = {h.lower().split(":")[0].rstrip(".") for h in allowed}
    return current_host in normalized_allowed


def forum_host_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not _forum_allowed_on_host(request):
            raise Http404()
        return view_func(request, *args, **kwargs)

    return _wrapped


def _client_ip(request):
    """
    Best-effort client IP. Behind a reverse proxy REMOTE_ADDR is the proxy's
    address, so all visitors would share one rate-limit bucket and the view
    counter would under-count. Enable FORUM_TRUST_PROXY_HEADERS only when the
    proxy is known to overwrite X-Forwarded-For.
    """
    if getattr(settings, "FORUM_TRUST_PROXY_HEADERS", False):
        xff = request.META.get("HTTP_X_FORWARDED_FOR", "")
        if xff:
            return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def _check_rate_limit(request, action, limit, window):
    """
    Lightweight, cache-based rate limiter without external dependencies.
    Returns True if request is allowed, False if throttled.
    """
    if request.user.is_authenticated:
        ident = f"u_{request.user.pk}"
    else:
        ident = f"ip_{hashlib.md5(_client_ip(request).encode()).hexdigest()[:10]}"

    key = f"forum_rl_{action}_{ident}"
    current = cache.get(key, 0)
    if current >= limit:
        return False

    if current == 0:
        cache.set(key, 1, window)
    else:
        try:
            cache.incr(key)
        except Exception:
            cache.set(key, current + 1, window)
    return True


# =========================================================
# HELPERS
# =========================================================
def _is_moderator(user):
    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    is_staff_mod = (
        getattr(settings, "FORUM_STAFF_ARE_MODERATORS", True) and user.is_staff
    )
    has_perm_mod = user.has_perm(f"{ForumTopic._meta.app_label}.change_forumtopic")

    moderator_groups = getattr(settings, "FORUM_MODERATOR_GROUPS", None)
    in_mod_group = bool(
        moderator_groups and user.groups.filter(name__in=moderator_groups).exists()
    )

    return bool(is_staff_mod or has_perm_mod or in_mod_group)


def _require_authenticated(request):
    if request.user.is_authenticated:
        return None
    return redirect_to_login(request.get_full_path())


def _build_topic_slug(title):
    base = slugify(title, allow_unicode=True)[:200].rstrip("-") or "topic"
    slug = base
    i = 2
    while ForumTopic.objects.filter(slug=slug).exists():
        slug = f"{base}-{secrets.token_hex(2)}"
        i += 1
        if i > 5:
            slug = f"{base}-{secrets.token_hex(4)}"
            break
    return slug


def _get_author_fields(request, cleaned_data):
    if request.user.is_authenticated:
        user = request.user
        return {
            "author": user,
            "author_name": user.get_full_name() or user.get_username(),
            "author_email": getattr(user, "email", ""),
        }
    return {
        "author": None,
        "author_name": cleaned_data.get("author_name", "").strip(),
        "author_email": cleaned_data.get("author_email", "").strip(),
    }


def _guest_needs_moderation(request):
    return not request.user.is_authenticated and getattr(
        settings, "FORUM_MODERATE_GUESTS", True
    )


def _posts_per_page():
    return max(1, int(getattr(settings, "FORUM_TOPIC_POSTS_PER_PAGE", 20)))


def _topics_per_page():
    return max(1, int(getattr(settings, "FORUM_SECTION_TOPICS_PER_PAGE", 30)))


def _search_per_page():
    return max(1, int(getattr(settings, "FORUM_SEARCH_RESULTS_PER_PAGE", 20)))


def _forum_recipients():
    raw_admins = getattr(settings, "ADMINS", [])
    recipients = []
    for admin in raw_admins:
        if isinstance(admin, (tuple, list)):
            recipients.append(admin[1])
        elif isinstance(admin, str):
            recipients.append(admin)
    return recipients or [
        getattr(settings, "DEFAULT_FROM_EMAIL", "webmaster@localhost")
    ]


def _forum_absolute_url(path, request=None):
    if request:
        return request.build_absolute_uri(path)
    base = getattr(
        settings, "FORUM_BASE_URL", getattr(settings, "BASE_URL", "")
    ).rstrip("/")
    return f"{base}{path}" if base else path


def _display_user_name(user):
    if not user:
        return _("Deleted user")
    legacy_map = getattr(user, "forum_legacy_map", None)
    if legacy_map and legacy_map.display_name:
        return legacy_map.display_name
    return user.get_full_name() or user.get_username()


def _thread_other_user(thread, current_user):
    return thread.recipient if thread.starter_id == current_user.id else thread.starter


def _send_forum_mail(subject, body, recipients):
    recipients = [r for r in recipients if r]
    if not recipients:
        return

    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "webmaster@localhost")

    def send_email_task():
        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=from_email,
                recipient_list=recipients,
                fail_silently=False,
            )
        except Exception as e:
            logger.exception(f"Forum email delivery error: {e}")

    transaction.on_commit(lambda: _mail_pool.submit(send_email_task))


def _notify_admins_new_topic(topic, request=None):
    if not getattr(settings, "FORUM_NOTIFY_ADMINS", True):
        return
    url = _forum_absolute_url(
        reverse("wagtail_simple_forum:topic_view", kwargs={"slug": topic.slug}), request
    )
    _send_forum_mail(
        subject=_("[%(site)s] New forum topic: %(title)s")
        % {"site": getattr(settings, "SITE_NAME", "Site"), "title": topic.title},
        body=_(
            "A new forum topic has been created.\n\nTopic: %(title)s\nSection: %(section)s\nAuthor: %(author)s\nLink: %(url)s\n"
        )
        % {
            "title": topic.title,
            "section": topic.section.title,
            "author": topic.display_author_name(),
            "url": url,
        },
        recipients=_forum_recipients(),
    )


def _notify_admins_new_reply(topic, post, request=None):
    if not getattr(settings, "FORUM_NOTIFY_ADMINS", True):
        return
    url = _forum_absolute_url(
        reverse("wagtail_simple_forum:topic_view", kwargs={"slug": topic.slug})
        + f"#post-{post.id}",
        request,
    )
    _send_forum_mail(
        subject=_("[%(site)s] New reply in topic: %(title)s")
        % {"site": getattr(settings, "SITE_NAME", "Site"), "title": topic.title},
        body=_(
            "A new reply has been posted in the forum.\n\nTopic: %(title)s\nSection: %(section)s\nAuthor: %(author)s\nLink: %(url)s\n"
        )
        % {
            "title": topic.title,
            "section": topic.section.title,
            "author": post.display_author_name(),
            "url": url,
        },
        recipients=_forum_recipients(),
    )


def _notify_topic_author_on_reply(topic, post, request=None):
    if not getattr(settings, "FORUM_NOTIFY_TOPIC_AUTHOR", True):
        return
    recipient = (
        getattr(topic.author, "email", "")
        if topic.author
        else getattr(topic, "author_email", "")
    )
    if (
        not recipient
        or (post.author and topic.author_id == post.author_id)
        or (post.author_email and recipient == post.author_email)
    ):
        return

    url = _forum_absolute_url(
        reverse("wagtail_simple_forum:topic_view", kwargs={"slug": topic.slug})
        + f"#post-{post.id}",
        request,
    )
    _send_forum_mail(
        subject=_("New reply in your topic: %(title)s") % {"title": topic.title},
        body=_(
            "A new reply has been posted in your topic.\n\nTopic: %(title)s\nLink: %(url)s\n"
        )
        % {"title": topic.title, "url": url},
        recipients=[recipient],
    )


def _notify_pm_recipient(thread, pm, request=None):
    if not getattr(settings, "FORUM_NOTIFY_PM_RECIPIENT", True):
        return
    recipient = (
        thread.recipient if pm.author_id == thread.starter_id else thread.starter
    )
    if not recipient or not getattr(recipient, "email", ""):
        return

    url = _forum_absolute_url(
        reverse("wagtail_simple_forum:pm_thread", kwargs={"pk": thread.pk})
        + f"#pm-{pm.id}",
        request,
    )
    _send_forum_mail(
        subject=_("New private message: %(subject)s") % {"subject": thread.subject},
        body=_(
            "You have received a new private message.\n\nSubject: %(subject)s\nFrom: %(author)s\nLink: %(url)s\n"
        )
        % {
            "subject": thread.subject,
            "author": pm.display_author_name(),
            "url": url,
        },
        recipients=[recipient.email],
    )


# =========================================================
# FORUM VIEWS
# =========================================================
@forum_host_required
def forum_index(request):
    from django.db.models import Prefetch

    posts_total = (
        ForumTopic.objects.filter(section=OuterRef("pk"), is_approved=True)
        .order_by()
        .values("section_id")
        .annotate(total=Sum("posts_count"))
        .values("total")
    )

    section_qs = ForumSection.objects.annotate(
        topics_count=Count("topics", filter=Q(topics__is_approved=True), distinct=True),
        posts_count=Coalesce(Subquery(posts_total), 0),
    ).order_by("order", "title")

    categories = (
        ForumCategory.objects.annotate(sections_count=Count("sections", distinct=True))
        .prefetch_related(Prefetch("sections", queryset=section_qs))
        .order_by("order", "title")
    )

    return render(
        request, "wagtail_simple_forum/index.html", {"categories": categories}
    )


@forum_host_required
def section_view(request, slug):
    section = get_object_or_404(
        ForumSection.objects.select_related("category"), slug=slug
    )

    topics_qs = section.topics.select_related("author", "author__forum_legacy_map", "last_post_by", "last_post_by__forum_legacy_map").order_by(
        "-is_pinned", "-last_post_at", "-created_at", "-id"
    )

    can_mod = _is_moderator(request.user)
    if not can_mod:
        topics_qs = topics_qs.filter(is_approved=True)

    posts_per_page = _posts_per_page()
    paginator = Paginator(topics_qs, _topics_per_page())
    topics_page = paginator.get_page(request.GET.get("page"))

    topics = list(topics_page.object_list)
    for topic in topics:
        vis = topic.posts_count or 0
        topic.replies_count = max(vis - 1, 0)
        topic.last_page = max(1, math.ceil(vis / posts_per_page))

    topics_page.object_list = topics
    return render(
        request,
        "wagtail_simple_forum/section.html",
        {"section": section, "topics_page": topics_page, "can_moderate": can_mod},
    )


@forum_host_required
def topic_create(request, slug):
    section = get_object_or_404(
        ForumSection.objects.select_related("category"), slug=slug
    )
    if not request.user.is_authenticated and not getattr(
        settings, "FORUM_ALLOW_GUESTS", True
    ):
        return redirect_to_login(request.get_full_path())

    if request.method == "POST":
        if not _check_rate_limit(request, "topic_create", limit=5, window=300):
            messages.error(
                request,
                _("You are creating topics too quickly. Please try again later."),
            )
            return redirect("wagtail_simple_forum:section_view", slug=section.slug)

        form = ForumTopicForm(request.POST, request=request)
        if form.is_valid():
            with transaction.atomic():
                author_fields = _get_author_fields(request, form.cleaned_data)
                needs_moderation = _guest_needs_moderation(request)

                topic = None
                for _attempt in range(5):
                    topic_slug = _build_topic_slug(form.cleaned_data["title"])
                    try:
                        with transaction.atomic():
                            topic = ForumTopic.objects.create(
                                section=section,
                                title=form.cleaned_data["title"],
                                slug=topic_slug,
                                is_approved=not needs_moderation,
                                posts_count=0 if needs_moderation else 1,
                                last_post_at=timezone.now(),
                                last_post_by=author_fields["author"],
                                **author_fields,
                            )
                            break
                    except IntegrityError:
                        continue

                if not topic:
                    topic = ForumTopic.objects.create(
                        section=section,
                        title=form.cleaned_data["title"],
                        slug=f"topic-{secrets.token_hex(6)}",
                        is_approved=not needs_moderation,
                        posts_count=0 if needs_moderation else 1,
                        last_post_at=timezone.now(),
                        last_post_by=author_fields["author"],
                        **author_fields,
                    )

                first_post = ForumPost.objects.create(
                    topic=topic,
                    content=form.cleaned_data["content"],
                    is_approved=not needs_moderation,
                    **author_fields,
                )
                _notify_admins_new_topic(topic, request)

            if topic.is_approved:
                messages.success(request, _("Topic created."))
                return redirect("wagtail_simple_forum:topic_view", slug=topic.slug)

            messages.success(request, _("Topic submitted for moderation."))
            return redirect("wagtail_simple_forum:section_view", slug=section.slug)
    else:
        form = ForumTopicForm(request=request)

    return render(
        request,
        "wagtail_simple_forum/topic_form.html",
        {"section": section, "form": form},
    )


@forum_host_required
def topic_view(request, slug):
    topic = get_object_or_404(
        ForumTopic.objects.select_related(
            "section",
            "section__category",
            "author",
            "author__forum_legacy_map",
            "last_post_by",
            "last_post_by__forum_legacy_map",
        ),
        slug=slug,
    )

    can_mod = _is_moderator(request.user)
    if not topic.is_approved and not can_mod:
        raise Http404()

    # Zero-session, zero-PII view counter using hashed IP in cache
    if request.method == "GET" and getattr(settings, "FORUM_TRACK_VIEWS", True):
        ip_hash = hashlib.md5(_client_ip(request).encode()).hexdigest()[:10]
        cache_key = f"forum_v_{topic.pk}_{ip_hash}"
        if cache.add(cache_key, 1, timeout=3600):
            ForumTopic.objects.filter(pk=topic.pk).update(
                views_count=F("views_count") + 1
            )
            topic.views_count += 1

    posts_per_page = _posts_per_page()
    posts_qs = topic.posts.select_related("author", "author__forum_legacy_map", "edited_by").prefetch_related("author__groups")
    if not can_mod:
        posts_qs = posts_qs.filter(is_approved=True, is_deleted=False)
    posts_qs = posts_qs.order_by("created_at", "id")

    paginator = Paginator(posts_qs, posts_per_page)
    posts_page = paginator.get_page(request.GET.get("page"))

    can_reply = (not topic.is_closed or can_mod) and (
        request.user.is_authenticated or getattr(settings, "FORUM_ALLOW_GUESTS", True)
    )

    if request.method == "POST":
        # Disallow replies if topic is closed
        if topic.is_closed and not can_mod:
            messages.error(request, _("This topic is closed for replies."))
            return redirect(
                f"{reverse('wagtail_simple_forum:topic_view', kwargs={'slug': topic.slug})}?page={posts_page.number}"
            )

        # Redirect to login if guest replies are disabled
        if not request.user.is_authenticated and not getattr(
            settings, "FORUM_ALLOW_GUESTS", True
        ):
            return redirect_to_login(request.get_full_path())

        if not _check_rate_limit(request, "reply_post", limit=15, window=300):
            messages.error(
                request, _("You are posting replies too quickly. Please wait a moment.")
            )
            return redirect(
                f"{reverse('wagtail_simple_forum:topic_view', kwargs={'slug': topic.slug})}?page={posts_page.number}"
            )

        form = ForumReplyForm(request.POST, request=request)
        if form.is_valid():
            with transaction.atomic():
                author_fields = _get_author_fields(request, form.cleaned_data)
                needs_moderation = _guest_needs_moderation(request)
                reply_post = ForumPost.objects.create(
                    topic=topic,
                    content=form.cleaned_data["content"],
                    is_approved=not needs_moderation,
                    **author_fields,
                )

                # Atomic O(1) counter update on approved replies
                if not needs_moderation:
                    ForumTopic.objects.filter(pk=topic.pk).update(
                        posts_count=F("posts_count") + 1,
                        last_post_at=reply_post.created_at,
                        last_post_by=reply_post.author,
                    )
                    topic.refresh_from_db(
                        fields=["posts_count", "last_post_at", "last_post_by"]
                    )

                _notify_admins_new_reply(topic, reply_post, request)
                if reply_post.is_approved:
                    _notify_topic_author_on_reply(topic, reply_post, request)

            last_page = max(1, math.ceil((topic.posts_count or 1) / posts_per_page))

            if reply_post.is_approved:
                messages.success(request, _("Reply posted."))
                return redirect(
                    f"{reverse('wagtail_simple_forum:topic_view', kwargs={'slug': topic.slug})}?page={last_page}#post-{reply_post.id}"
                )

            messages.success(request, _("Reply submitted for moderation."))
            return redirect(
                f"{reverse('wagtail_simple_forum:topic_view', kwargs={'slug': topic.slug})}?page={last_page}"
            )
    else:
        form = ForumReplyForm(request=request) if can_reply else None

    return render(
        request,
        "wagtail_simple_forum/topic.html",
        {
            "topic": topic,
            "posts_page": posts_page,
            "reply_form": form,
            "can_reply": can_reply,
            "can_moderate": can_mod,
        },
    )


@forum_host_required
def post_edit(request, pk):
    post = get_object_or_404(
        ForumPost.objects.select_related(
            "topic",
            "topic__section",
            "topic__section__category",
            "author",
            "author__forum_legacy_map",
            "edited_by",
        ),
        pk=pk,
    )

    can_mod = _is_moderator(request.user)
    is_owner = request.user.is_authenticated and post.author_id == request.user.id
    if not (can_mod or is_owner):
        return HttpResponseForbidden(_("Access denied."))
    if post.topic.is_closed and not can_mod:
        return HttpResponseForbidden(_("This topic is closed. Posts cannot be modified."))

    if post.is_deleted and not can_mod:
        raise Http404()

    if request.method == "POST":
        form = ForumPostEditForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.edited_at = timezone.now()
            post.edited_by = request.user if request.user.is_authenticated else None
            post.save(update_fields=["content", "edited_at", "edited_by", "updated_at"])

            # Compute precise page number using tie-break ordering
            preceding = (
                post.topic.posts.filter(is_approved=True, is_deleted=False)
                .filter(
                    Q(created_at__lt=post.created_at)
                    | Q(created_at=post.created_at, id__lt=post.id)
                )
                .count()
                + 1
            )
            target_page = max(1, math.ceil(preceding / _posts_per_page()))

            messages.success(request, _("Post updated."))
            return redirect(
                f"{reverse('wagtail_simple_forum:topic_view', kwargs={'slug': post.topic.slug})}?page={target_page}#post-{post.id}"
            )
    else:
        form = ForumPostEditForm(instance=post)

    return render(
        request, "wagtail_simple_forum/post_edit.html", {"post": post, "form": form}
    )


@forum_host_required
@require_POST
def post_delete(request, pk):
    post = get_object_or_404(ForumPost.objects.select_related("topic", "author"), pk=pk)
    can_mod = _is_moderator(request.user)
    is_owner = request.user.is_authenticated and post.author_id == request.user.id

    if not (can_mod or is_owner):
        return HttpResponseForbidden(_("Access denied."))
    if post.topic.is_closed and not can_mod:
        return HttpResponseForbidden(_("This topic is closed. Posts cannot be modified."))

    first_post = (
        post.topic.posts.filter(is_deleted=False).order_by("created_at", "id").first()
    )
    if first_post and first_post.pk == post.pk:
        return HttpResponseForbidden(
            _("The first post cannot be deleted. Close or delete the topic instead.")
        )

    post.is_deleted = True
    post.save(update_fields=["is_deleted"])
    messages.success(request, _("Post deleted."))
    return redirect("wagtail_simple_forum:topic_view", slug=post.topic.slug)


@forum_host_required
@require_POST
def topic_close(request, slug):
    if not _is_moderator(request.user):
        return HttpResponseForbidden(_("Access denied."))
    topic = get_object_or_404(ForumTopic, slug=slug)
    topic.is_closed = not topic.is_closed
    topic.save(update_fields=["is_closed"])
    messages.success(
        request, _("Topic closed.") if topic.is_closed else _("Topic reopened.")
    )
    return redirect("wagtail_simple_forum:topic_view", slug=topic.slug)


@forum_host_required
@require_POST
def topic_pin(request, slug):
    if not _is_moderator(request.user):
        return HttpResponseForbidden(_("Access denied."))
    topic = get_object_or_404(ForumTopic, slug=slug)
    topic.is_pinned = not topic.is_pinned
    topic.save(update_fields=["is_pinned"])
    messages.success(
        request, _("Topic pinned.") if topic.is_pinned else _("Topic unpinned.")
    )
    return redirect("wagtail_simple_forum:topic_view", slug=topic.slug)


@forum_host_required
def forum_search(request):
    query = (request.GET.get("q") or "").strip()[:100]
    posts_per_page = _posts_per_page()

    if len(query) >= 3:
        if not _check_rate_limit(request, "search", limit=30, window=60):
            messages.error(
                request, _("Search rate limit exceeded. Please wait a minute.")
            )
            return render(
                request,
                "wagtail_simple_forum/search.html",
                {"query": query, "results_page": None},
            )

        topics_qs = (
            ForumTopic.objects.select_related(
                "section",
                "section__category",
                "author",
                "author__forum_legacy_map",
                "last_post_by",
                "last_post_by__forum_legacy_map",
            )
            .filter(
                Q(title__icontains=query)
                | Q(author_name__icontains=query)
                | Q(section__title__icontains=query)
                | Q(section__category__title__icontains=query)
                | Q(
                    posts__content__icontains=query,
                    posts__is_approved=True,
                    posts__is_deleted=False,
                )
                | Q(
                    posts__author_name__icontains=query,
                    posts__is_approved=True,
                    posts__is_deleted=False,
                )
            )
            .distinct()
        )
        if not _is_moderator(request.user):
            topics_qs = topics_qs.filter(is_approved=True)

        topics_qs = topics_qs.order_by("-is_pinned", "-last_post_at", "-created_at")
    else:
        topics_qs = ForumTopic.objects.none()

    paginator = Paginator(topics_qs, _search_per_page())
    results_page = paginator.get_page(request.GET.get("page"))

    topics = list(results_page.object_list)
    for topic in topics:
        vis = topic.posts_count or 0
        topic.last_page = max(1, math.ceil(vis / posts_per_page))
    results_page.object_list = topics
    return render(
        request,
        "wagtail_simple_forum/search.html",
        {"query": query, "results_page": results_page},
    )


# =========================================================
# PRIVATE MESSAGES
# =========================================================
@forum_host_required
def pm_inbox(request):
    auth_redirect = _require_authenticated(request)
    if auth_redirect:
        return auth_redirect

    threads_qs = (
        PrivateMessageThread.objects.filter(
            Q(starter=request.user) | Q(recipient=request.user)
        )
        .select_related(
            "starter",
            "starter__forum_legacy_map",
            "recipient",
            "recipient__forum_legacy_map",
        )
        .order_by("-last_message_at", "-created_at")
    )

    paginator = Paginator(threads_qs, 25)
    threads_page = paginator.get_page(request.GET.get("page"))

    threads = list(threads_page.object_list)
    for thread in threads:
        other_user = _thread_other_user(thread, request.user)
        thread.other_user = other_user
        thread.other_user_display = _display_user_name(other_user)
        thread.activity_at = thread.last_message_at or thread.created_at

    threads_page.object_list = threads
    return render(
        request, "wagtail_simple_forum/pm_inbox.html", {"threads_page": threads_page}
    )


@forum_host_required
def pm_new(request, username=None):
    auth_redirect = _require_authenticated(request)
    if auth_redirect:
        return auth_redirect

    initial = {"recipient_username": username} if username else {}
    if request.method == "POST":
        if not _check_rate_limit(request, "pm_create", limit=10, window=600):
            messages.error(
                request, _("Private messaging rate limit reached. Please wait.")
            )
            return redirect("wagtail_simple_forum:pm_inbox")

        form = PrivateMessageThreadForm(request.POST, request=request)
        if form.is_valid():
            with transaction.atomic():
                thread = PrivateMessageThread.objects.create(
                    subject=form.cleaned_data["subject"],
                    starter=request.user,
                    recipient=form.recipient_user,
                    messages_count=1,
                    last_message_at=timezone.now(),
                )
                user = request.user
                pm = PrivateMessage.objects.create(
                    thread=thread,
                    author=user,
                    author_name=user.get_full_name() or user.get_username(),
                    content=form.cleaned_data["content"],
                )
                _notify_pm_recipient(thread, pm, request)
            messages.success(request, _("Private message sent."))
            return redirect("wagtail_simple_forum:pm_thread", pk=thread.pk)
    else:
        form = PrivateMessageThreadForm(request=request, initial=initial)
    return render(
        request,
        "wagtail_simple_forum/pm_new.html",
        {"form": form, "prefill_username": username or ""},
    )


@forum_host_required
def pm_thread(request, pk):
    auth_redirect = _require_authenticated(request)
    if auth_redirect:
        return auth_redirect

    # Enforce strict 404 for inaccessible threads (prevents IDOR and enumeration)
    thread = get_object_or_404(
        PrivateMessageThread.objects.filter(
            Q(starter=request.user) | Q(recipient=request.user)
        ).select_related(
            "starter",
            "starter__forum_legacy_map",
            "recipient",
            "recipient__forum_legacy_map",
        ),
        pk=pk,
    )

    other_user = _thread_other_user(thread, request.user)
    messages_qs = thread.messages.select_related("author", "author__forum_legacy_map").order_by("created_at", "id")

    paginator = Paginator(messages_qs, 25)
    messages_page = paginator.get_page(request.GET.get("page"))

    if request.method == "POST":
        if not _check_rate_limit(request, "pm_reply", limit=20, window=300):
            messages.error(request, _("You are sending messages too quickly."))
            return redirect(
                f"{reverse('wagtail_simple_forum:pm_thread', kwargs={'pk': thread.pk})}?page={messages_page.number}"
            )

        form = PrivateMessageReplyForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = request.user
                pm = PrivateMessage.objects.create(
                    thread=thread,
                    author=user,
                    author_name=user.get_full_name() or user.get_username(),
                    content=form.cleaned_data["content"],
                )

                # Atomic increment
                PrivateMessageThread.objects.filter(pk=thread.pk).update(
                    messages_count=F("messages_count") + 1,
                    last_message_at=pm.created_at,
                )
                thread.refresh_from_db(fields=["messages_count", "last_message_at"])

                _notify_pm_recipient(thread, pm, request)

            last_page = max(1, math.ceil((thread.messages_count or 1) / 25))
            messages.success(request, _("Message sent."))
            return redirect(
                f"{reverse('wagtail_simple_forum:pm_thread', kwargs={'pk': thread.pk})}?page={last_page}#pm-{pm.id}"
            )
    else:
        form = PrivateMessageReplyForm()

    return render(
        request,
        "wagtail_simple_forum/pm_thread.html",
        {
            "thread": thread,
            "messages_page": messages_page,
            "form": form,
            "other_user": other_user,
            "other_user_display": _display_user_name(other_user),
        },
    )
