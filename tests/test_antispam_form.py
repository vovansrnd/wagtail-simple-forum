"""Д61: регрессионные тесты антиполей/токена ForumAntiSpamForm.

Пять состояний submit_token по фактической реализации (forms.py):
верный (возраст >= 3 c и <= 12 ч), отсутствующий, неверный (подпись),
просроченный (> 43200 с), повторно использованный (посессионный список
sha256). Плюс капча: подпись/ответ/свежесть, и списание токена только
после валидации ВСЕХ полей.
"""
import time

from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.db import SessionStore
from django.core.signing import TimestampSigner
from django.test import RequestFactory, TestCase

from wagtail_simple_forum.forms import (
    ForumAntiSpamForm,
    _generate_captcha_signature,
    _signer,
)

A, B = 3, 4


def _request():
    req = RequestFactory().post("/")
    req.session = SessionStore()
    req.user = AnonymousUser()
    return req


def _payload(token_ts=None, **overrides):
    token_ts = int(time.time()) - 10 if token_ts is None else token_ts
    data = {
        "submit_token": _signer.sign(str(token_ts)),
        "captcha_a": A,
        "captcha_b": B,
        "captcha_ts": int(time.time()) - 10,
        "captcha_sig": _generate_captcha_signature(A, B, int(time.time()) - 10),
        "captcha_answer": A + B,
        "website_url": "",
        "author_name": "Иван",
        "author_email": "ivan@example.test",
    }
    data.update(overrides)
    return data


class SubmitTokenTests(TestCase):
    def _form(self, **overrides):
        req = _request()
        return ForumAntiSpamForm(request=req, data=_payload(**overrides)), req

    def test_valid_token_age_10s_passes(self):
        form, _ = self._form()
        self.assertTrue(form.is_valid(), form.errors)

    def test_missing_token_rejected(self):
        form, _ = self._form(submit_token="")
        self.assertFalse(form.is_valid())
        self.assertIn("token missing", str(form.errors["submit_token"]))

    def test_invalid_token_rejected(self):
        form, _ = self._form(submit_token="forged:123:abcdef")
        self.assertFalse(form.is_valid())
        self.assertIn("Security verification failed.", str(form.errors["submit_token"]))

    def test_expired_token_rejected(self):
        form, _ = self._form(token_ts=int(time.time()) - 44000)
        self.assertFalse(form.is_valid())
        self.assertIn("Form session expired.", str(form.errors["submit_token"]))

    def test_too_fast_submission_rejected(self):
        form, _ = self._form(token_ts=int(time.time()))
        self.assertFalse(form.is_valid())
        self.assertIn("suspiciously fast", str(form.errors["submit_token"]))

    def test_reused_token_rejected_in_same_session(self):
        req = _request()
        payload = _payload()
        first = ForumAntiSpamForm(request=req, data=payload)
        self.assertTrue(first.is_valid(), first.errors)
        second = ForumAntiSpamForm(request=req, data=dict(payload))
        self.assertFalse(second.is_valid())
        self.assertIn("already been used", str(second.errors))

    def test_token_not_consumed_when_other_field_fails(self):
        req = _request()
        bad = _payload(captcha_answer=A + B + 1)  # неверный ответ капчи
        first = ForumAntiSpamForm(request=req, data=bad)
        self.assertFalse(first.is_valid())
        self.assertIn("captcha_answer", first.errors)
        # токен НЕ списан (списание только после валидации всех полей):
        retry = ForumAntiSpamForm(request=req, data=_payload())
        self.assertTrue(retry.is_valid(), retry.errors)


class CaptchaTests(TestCase):
    def _form(self, **overrides):
        req = _request()
        return ForumAntiSpamForm(request=req, data=_payload(**overrides)), req

    def test_tampered_captcha_signature_rejected(self):
        form, _ = self._form(captcha_sig="0" * 32)
        self.assertFalse(form.is_valid())
        self.assertIn("Verification signature mismatch.", str(form.errors))

    def test_wrong_answer_rejected(self):
        form, _ = self._form(captcha_answer=A + B + 1)
        self.assertFalse(form.is_valid())
        self.assertIn("captcha_answer", form.errors)

    def test_stale_captcha_challenge_rejected(self):
        old = int(time.time()) - 44000
        form, _ = self._form(
            captcha_ts=old,
            captcha_sig=_generate_captcha_signature(A, B, old),
        )
        self.assertFalse(form.is_valid())
        self.assertIn("Form session expired.", str(form.errors))
