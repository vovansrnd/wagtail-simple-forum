"""Д67-С: fast-path модератора на уровне запросов (views._is_moderator).

Зеркало fast-path ForumAuthorDisplayMixin.author_role: staff при
FORUM_STAFF_ARE_MODERATORS=True признаётся модератором немедленно — без
has_perm() (обращение к таблицам permissions) и без запроса групп.
Семантика or-комбинации не меняется: superuser → admin-путь, staff →
модератор, permission → модератор, группа → модератор, остальное — нет.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db import connection
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext

from wagtail_simple_forum.views import _is_moderator

User = get_user_model()


class ModeratorRequestLevelTests(TestCase):
    @override_settings(FORUM_STAFF_ARE_MODERATORS=True, FORUM_MODERATOR_GROUPS=["mods"])
    def test_staff_short_circuits_perm_and_group_queries(self):
        """Staff-модератор: ноль SQL-запросов внутри _is_moderator."""
        staff = User.objects.create_user(
            username="mod-staff", password="pw", is_staff=True
        )
        fresh = User.objects.get(pk=staff.pk)  # fresh-объект: кешей прав нет
        with CaptureQueriesContext(connection) as ctx:
            self.assertTrue(_is_moderator(fresh))
        self.assertEqual(len(ctx), 0)

    def test_superuser_is_moderator(self):
        superuser = User.objects.create_user(
            username="mod-root", password="pw", is_superuser=True
        )
        self.assertTrue(_is_moderator(superuser))

    @override_settings(FORUM_STAFF_ARE_MODERATORS=False, FORUM_MODERATOR_GROUPS=None)
    def test_staff_not_moderator_when_setting_disabled(self):
        staff = User.objects.create_user(
            username="mod-staff-off", password="pw", is_staff=True
        )
        self.assertFalse(_is_moderator(staff))

    @override_settings(FORUM_STAFF_ARE_MODERATORS=False, FORUM_MODERATOR_GROUPS=None)
    def test_permission_based_moderator_without_staff_flag(self):
        user = User.objects.create_user(username="mod-perm", password="pw")
        perm = Permission.objects.get(
            content_type__app_label="wagtail_simple_forum",
            codename="change_forumtopic",
        )
        user.user_permissions.add(perm)
        self.assertTrue(_is_moderator(User.objects.get(pk=user.pk)))

    @override_settings(FORUM_STAFF_ARE_MODERATORS=False, FORUM_MODERATOR_GROUPS=["mods"])
    def test_group_based_moderator(self):
        user = User.objects.create_user(username="mod-group", password="pw")
        group = Group.objects.create(name="mods")
        user.groups.add(group)
        self.assertTrue(_is_moderator(User.objects.get(pk=user.pk)))

    def test_anonymous_is_not_moderator(self):
        from django.contrib.auth.models import AnonymousUser

        self.assertFalse(_is_moderator(AnonymousUser()))

    def test_plain_member_is_not_moderator(self):
        member = User.objects.create_user(username="plain-member", password="pw")
        self.assertFalse(_is_moderator(member))
