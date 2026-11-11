from types import SimpleNamespace
from unittest.mock import Mock

from django.test import SimpleTestCase, override_settings

from wagtail_simple_forum.models import ForumAuthorDisplayMixin


class _DisplayObject(ForumAuthorDisplayMixin):
    def __init__(self, author):
        self.author = author


class ForumAuthorRoleQueryTests(SimpleTestCase):
    @override_settings(FORUM_STAFF_ARE_MODERATORS=True, FORUM_MODERATOR_GROUPS=["mods"])
    def test_staff_moderator_short_circuits_permission_and_group_queries(self):
        author = SimpleNamespace(
            is_superuser=False,
            is_staff=True,
            has_perm=Mock(side_effect=AssertionError("has_perm must not run for staff moderator")),
        )
        self.assertEqual(_DisplayObject(author).author_role, "moderator")
        author.has_perm.assert_not_called()
        self.assertFalse(hasattr(author, "groups"), "staff fast-path must not inspect groups")

    @override_settings(FORUM_STAFF_ARE_MODERATORS=False, FORUM_MODERATOR_GROUPS=None)
    def test_staff_is_checked_by_permission_when_staff_setting_disabled(self):
        author = SimpleNamespace(
            is_superuser=False, is_staff=True, has_perm=Mock(return_value=False)
        )
        self.assertEqual(_DisplayObject(author).author_role, "member")
        author.has_perm.assert_called_once()

    @override_settings(FORUM_STAFF_ARE_MODERATORS=True, FORUM_MODERATOR_GROUPS=None)
    def test_non_staff_moderator_permission_is_still_respected(self):
        author = SimpleNamespace(
            is_superuser=False, is_staff=False, has_perm=Mock(return_value=True)
        )
        self.assertEqual(_DisplayObject(author).author_role, "moderator")
        author.has_perm.assert_called_once()
