"""Д67-С: replay-защита на уровне реальных HTTP-запросов с browser session.

Существующие тесты antispam работают с прямым SessionStore; здесь — полный
request lifecycle через тестовый клиент с куками: GET формы → POST валидных
данных (сессия сохраняет списанные токены) → повтор с ТОЙ ЖЕ browser session
отклоняется уже на следующем HTTP-запросе; другая browser session с тем же
cached form token не ломается. Заодно фиксируется обещание «GET не пишет
сессию» (совместимость с кешируемыми страницами).

Гарантия ограничена последовательным per-session replay detection:
параллельные double-submits одной сессии не атомарны (сессии Django без
блокировок) — формулировка в README это явно ограничивает.
"""
import re
import time as _real_time
from unittest import mock

from django.test import Client, TestCase

from wagtail_simple_forum.models import ForumCategory, ForumSection, ForumTopic

SESSION_KEY = "wagtail_simple_forum_used_antispam_tokens"
HIDDEN_FIELDS = ("submit_token", "captcha_a", "captcha_b", "captcha_ts", "captcha_sig")


class _BackdatedTokenClock:
    """Управляемое время форм вместо физического sleep.

    Первые два вызова time.time() внутри forms (подпись submit_token и
    captcha_ts при рендере GET) возвращают время на 10 секунд назад,
    все последующие — реальное. Валидация POST видит возраст токена ~10 с
    (порог 3 с) и свежесть капчи ~10 с (порог 12 ч) без реальных ожиданий.
    """

    def __init__(self, original_time):
        # оригинальная time.time захватывается ДО патча: forms.time — тот же
        # модуль-объект, патч заменяет его атрибут глобально
        self._original_time = original_time
        self.calls = 0

    def __call__(self):
        self.calls += 1
        return self._original_time() + (-10.0 if self.calls <= 2 else 0.0)


class _backdated_token:
    """Контекст: время forms идёт по _BackdatedTokenClock."""

    def __enter__(self):
        self.clock = _BackdatedTokenClock(_real_time.time)
        p = mock.patch("wagtail_simple_forum.forms.time.time", side_effect=self.clock)
        p.__enter__()
        self._patch = p
        return self

    def __exit__(self, *exc):
        return self._patch.__exit__(*exc)


def _extract_hidden(html):
    """Значения скрытых анти-спам полей из отрендеренной формы."""
    fields = {}
    for name in HIDDEN_FIELDS:
        m = re.search(r'name="%s"[^>]*value="([^"]*)"' % name, html)
        if m:
            fields[name] = m.group(1)
    return fields


class AntispamHTTPLifecycleTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        category = ForumCategory.objects.create(title="HTTP Категория")
        cls.section = ForumSection.objects.create(
            title="HTTP Раздел", slug="http-gen", category=category
        )

    def _client(self, ip):
        return Client(REMOTE_ADDR=ip)

    def _get_form(self, client):
        response = client.get(
            "/forum/section/http-gen/new/", REMOTE_ADDR=client.defaults.get("REMOTE_ADDR")
        )
        self.assertEqual(response.status_code, 200)
        return _extract_hidden(response.content.decode())

    def _post_topic(self, client, fields, title):
        data = {
            "title": title,
            "content": "<p>HTTP-тест сообщения</p>",
            "author_name": "Гость HTTP",
            "author_email": "guest@example.test",
            "website_url": "",
            # гость решает капчу: ответ = a + b из скрытых полей
            "captcha_answer": int(fields["captcha_a"]) + int(fields["captcha_b"]),
            **fields,
        }
        return client.post(
            "/forum/section/http-gen/new/", data,
            REMOTE_ADDR=client.defaults.get("REMOTE_ADDR"),
        )

    def test_get_does_not_write_session_state(self):
        """GET формы не пишет session (совместимость с кешируемыми страницами)."""
        with _backdated_token():
            client = self._client("203.0.113.50")
            self._get_form(client)
        self.assertIsNone(client.session.get(SESSION_KEY))

    def test_replay_rejected_on_second_http_post_same_browser_session(self):
        """Валидный POST сохраняет состояние сессии; повтор с той же browser
        session отклоняется уже на следующем HTTP-запросе."""
        with _backdated_token():
            client = self._client("203.0.113.51")
            fields = self._get_form(client)
            self.assertEqual(len(fields), len(HIDDEN_FIELDS))

            response = self._post_topic(client, fields, "Первый HTTP-топик")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ForumTopic.objects.count(), 1)

        # токены списаны в сессии этого браузера
        used = client.session.get(SESSION_KEY)
        self.assertTrue(used)
        self.assertEqual(len(used), 2)  # submit + captcha сигнатура

        # повтор с той же browser session — отклонён, топик не создан
        response = self._post_topic(client, fields, "Повторный HTTP-топик")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already been used")
        self.assertEqual(ForumTopic.objects.count(), 1)

    def test_other_browser_session_not_broken_by_shared_cached_token(self):
        """Отдельная browser session с тем же cached form token работает:
        replay-защита посессионная, а не глобальная."""
        with _backdated_token():
            first = self._client("203.0.113.52")
            fields = self._get_form(first)
            response = self._post_topic(first, fields, "Топик первой сессии")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ForumTopic.objects.count(), 1)

        second = self._client("203.0.113.53")  # новая browser session
        response = self._post_topic(second, fields, "Топик второй сессии")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ForumTopic.objects.count(), 2)

        # у второй сессии свои списанные токены
        self.assertTrue(second.session.get(SESSION_KEY))
