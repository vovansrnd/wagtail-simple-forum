"""Д61: регрессионные тесты шаблонов eb2f670.

- topic_form.html: скрытые анти-поля (submit_token, captcha_sig, ...)
  снова рендерятся (раньше выводился только несуществующий
  form.submit_time).
- pm_inbox.html: список берётся из threads_page (пагинация), а не из
  несуществующего threads.
"""
from types import SimpleNamespace

from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.test import TestCase
from django.utils import timezone

from wagtail_simple_forum.forms import ForumTopicForm


class TopicFormHiddenFieldsTests(TestCase):
    def test_hidden_antispam_fields_rendered(self):
        html = render_to_string(
            "wagtail_simple_forum/topic_form.html",
            {"form": ForumTopicForm(), "section": SimpleNamespace(title="Раздел", slug="razdel")},
        )
        self.assertIn('name="submit_token"', html)
        self.assertIn('name="captcha_a"', html)
        self.assertIn('name="captcha_sig"', html)
        self.assertNotIn("submit_time", html)


class PmInboxThreadsPageTests(TestCase):
    def _ctx(self, objs):
        return {"threads_page": Paginator(objs, 10).page(1)}

    def _thread(self, pk, subject):
        return SimpleNamespace(
            pk=pk, subject=subject, other_user_display="Иван",
            messages_count=2, activity_at=timezone.now(),
        )

    def test_threads_page_object_list_rendered(self):
        html = render_to_string(
            "wagtail_simple_forum/pm_inbox.html",
            self._ctx([self._thread(1, "Тема-один"), self._thread(2, "Тема-два")]),
        )
        self.assertIn("Тема-один", html)
        self.assertIn("Тема-два", html)

    def test_empty_inbox_renders_else_branch(self):
        html = render_to_string("wagtail_simple_forum/pm_inbox.html", self._ctx([]))
        self.assertIn("no private messages", html)  # ветка {% else %} пустой пагинации
