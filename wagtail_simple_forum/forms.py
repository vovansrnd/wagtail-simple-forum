# wagtail_simple_forum/forms.py
import hashlib
import random
import secrets
import time

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.signing import SignatureExpired, TimestampSigner
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from django_prose_editor.fields import ProseEditorFormField

from .models import FORUM_POST_EXTENSIONS, ForumPost

User = get_user_model()

FORUM_MAX_POST_LENGTH = getattr(settings, "FORUM_MAX_POST_LENGTH", 65535)
FORUM_MAX_PM_LENGTH = getattr(settings, "FORUM_MAX_PM_LENGTH", 20000)

_signer = TimestampSigner(salt="wagtail_simple_forum_antispam")


def _generate_captcha_signature(a, b, timestamp):
    """Generates cryptographic token to verify math captcha without session storage."""
    secret = settings.SECRET_KEY
    payload = f"{a}:{b}:{timestamp}:{secret}"
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


class ForumAntiSpamForm(forms.Form):
    website_url = forms.CharField(
        required=False,
        label=_("Your website"),
        widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off"}),
    )

    # Server-signed timestamp token (cannot be forged by clients)
    submit_token = forms.CharField(required=False, widget=forms.HiddenInput())

    # Stateless captcha fields (never touches session on GET)
    captcha_a = forms.IntegerField(required=False, widget=forms.HiddenInput())
    captcha_b = forms.IntegerField(required=False, widget=forms.HiddenInput())
    captcha_ts = forms.IntegerField(required=False, widget=forms.HiddenInput())
    captcha_sig = forms.CharField(required=False, widget=forms.HiddenInput())
    captcha_answer = forms.IntegerField(
        required=False, label=_("Check: how much is...?")
    )

    author_name = forms.CharField(required=False, max_length=150, label=_("Your name"))
    author_email = forms.EmailField(required=False, label=_("Email"))

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        is_auth = self.request and self.request.user.is_authenticated

        if not self.is_bound:
            self.fields["submit_token"].initial = _signer.sign(secrets.token_hex(8))

        if is_auth:
            user = self.request.user
            for f in ["author_name", "author_email", "captcha_answer", "website_url"]:
                self.fields[f].widget = forms.HiddenInput()
                self.fields[f].required = False

            self.fields["author_name"].initial = (
                user.get_full_name() or user.get_username()
            )
            self.fields["author_email"].initial = getattr(user, "email", "")
        else:
            self.fields["author_name"].required = True
            self.fields["author_email"].required = True
            self.fields["captcha_answer"].required = True

            # Generate fresh stateless challenge on unbound GET
            if not self.is_bound:
                a, b = random.randint(1, 10), random.randint(1, 10)
                ts = int(time.time())
                sig = _generate_captcha_signature(a, b, ts)

                self.fields["captcha_a"].initial = a
                self.fields["captcha_b"].initial = b
                self.fields["captcha_ts"].initial = ts
                self.fields["captcha_sig"].initial = sig
                self.fields["captcha_answer"].label = _(
                    "Check: how much is %(a)s + %(b)s?"
                ) % {"a": a, "b": b}
            else:
                try:
                    a = int(self.data.get("captcha_a", 0))
                    b = int(self.data.get("captcha_b", 0))
                    self.fields["captcha_answer"].label = _(
                        "Check: how much is %(a)s + %(b)s?"
                    ) % {"a": a, "b": b}
                except (ValueError, TypeError):
                    self.fields["captcha_answer"].label = _("Check: how much is...?")

        self.fields["author_name"].widget.attrs["placeholder"] = str(_("Your name *"))
        self.fields["author_email"].widget.attrs["placeholder"] = str(
            _("Email (private) *")
        )
        self.fields["captcha_answer"].widget.attrs["placeholder"] = str(_("Answer"))

    def clean_website_url(self):
        value = self.cleaned_data.get("website_url")
        if value:
            raise forms.ValidationError(_("Spam detected."), code="honeypot")
        return value

    def clean_submit_token(self):
        token = self.cleaned_data.get("submit_token", "")
        if not token:
            raise forms.ValidationError(
                _("Security verification token missing."), code="token_missing"
            )

        try:
            # Enforce maximum form lifetime (12 hours)
            _signer.unsign(token, max_age=43200)
        except SignatureExpired:
            raise forms.ValidationError(
                _("Form session expired. Please refresh the page."),
                code="token_expired",
            )
        except Exception:
            raise forms.ValidationError(
                _("Security verification failed."), code="token_invalid"
            )

        # Enforce minimum submission speed (at least 3 seconds)
        try:
            timestamp = int(_signer.timestamp(token))
            current_ts = int(_signer.timestamp(_signer.sign("now")))
            if current_ts - timestamp < 3:
                raise forms.ValidationError(
                    _("You submitted the form suspiciously fast."), code="too_fast"
                )
        except forms.ValidationError:
            raise
        except Exception:
            pass

        return token

    def clean_captcha_answer(self):
        if self.request and self.request.user.is_authenticated:
            return self.cleaned_data.get("captcha_answer")

        try:
            a = int(self.cleaned_data.get("captcha_a"))
            b = int(self.cleaned_data.get("captcha_b"))
            ts = int(self.cleaned_data.get("captcha_ts"))
            sig = self.cleaned_data.get("captcha_sig", "")
            user_ans = int(self.cleaned_data.get("captcha_answer", -999))
        except (ValueError, TypeError):
            raise forms.ValidationError(
                _("Invalid verification code."), code="captcha_invalid"
            )

        # 1. Verify cryptographic HMAC signature
        expected_sig = _generate_captcha_signature(a, b, ts)
        if not secrets.compare_digest(sig, expected_sig):
            raise forms.ValidationError(
                _("Verification signature mismatch."), code="captcha_tampered"
            )

        # 2. Challenge freshness (replay protection)
        if abs(int(time.time()) - ts) > 43200:
            raise forms.ValidationError(
                _("Form session expired. Please refresh the page."),
                code="captcha_expired",
            )

        # 3. Arithmetic verification
        if a + b != user_ans:
            raise forms.ValidationError(
                _("Incorrect answer to the verification question."),
                code="captcha_invalid",
            )

        return user_ans


class ForumTopicForm(ForumAntiSpamForm):
    title = forms.CharField(max_length=200, label=_("Topic title"))
    content = ProseEditorFormField(
        extensions=FORUM_POST_EXTENSIONS,
        sanitize=True,
        label=_("First message"),
    )

    def clean_title(self):
        title = self.cleaned_data.get("title", "").strip()
        if len(title) < 3:
            raise forms.ValidationError(_("Title is too short."))
        return title

    def clean_content(self):
        content = self.cleaned_data.get("content", "").strip()
        if len(content) > FORUM_MAX_POST_LENGTH:
            raise forms.ValidationError(
                _("Message is too long (limit: %(limit)s characters).")
                % {"limit": FORUM_MAX_POST_LENGTH}
            )
        text_content = strip_tags(content).strip()
        if len(text_content) < 3:
            raise forms.ValidationError(_("Message is too short."))
        return content


class ForumReplyForm(ForumAntiSpamForm):
    content = ProseEditorFormField(
        extensions=FORUM_POST_EXTENSIONS,
        sanitize=True,
        label=_("Reply"),
    )

    def clean_content(self):
        content = self.cleaned_data.get("content", "").strip()
        if len(content) > FORUM_MAX_POST_LENGTH:
            raise forms.ValidationError(
                _("Message is too long (limit: %(limit)s characters).")
                % {"limit": FORUM_MAX_POST_LENGTH}
            )
        text_content = strip_tags(content).strip()
        if len(text_content) < 3:
            raise forms.ValidationError(_("Reply is too short."))
        return content


class ForumPostEditForm(forms.ModelForm):
    class Meta:
        model = ForumPost
        fields = ["content"]

    def clean_content(self):
        content = self.cleaned_data.get("content", "").strip()
        if len(content) > FORUM_MAX_POST_LENGTH:
            raise forms.ValidationError(_("Message is too long."))
        text_content = strip_tags(content).strip()
        if len(text_content) < 3:
            raise forms.ValidationError(_("Message is too short."))
        return content


class PrivateMessageThreadForm(forms.Form):
    recipient_username = forms.CharField(max_length=150, label=_("To"))
    subject = forms.CharField(max_length=255, label=_("Subject"))
    content = ProseEditorFormField(
        extensions=FORUM_POST_EXTENSIONS,
        sanitize=True,
        label=_("Message"),
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        self.fields["recipient_username"].widget.attrs["placeholder"] = str(
            _("Username")
        )
        self.fields["subject"].widget.attrs["placeholder"] = str(_("Message subject"))
        self.recipient_user = None

    def clean_recipient_username(self):
        username = (self.cleaned_data.get("recipient_username") or "").strip()
        if len(username) < 2:
            raise forms.ValidationError(_("Please specify a recipient."))

        username_field = getattr(User, "USERNAME_FIELD", "username")
        try:
            user = User.objects.get(**{f"{username_field}__iexact": username})
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            raise forms.ValidationError(_("Recipient not found or unavailable."))

        if not getattr(user, "is_active", True):
            raise forms.ValidationError(_("Recipient account is deactivated."))

        if (
            self.request
            and self.request.user.is_authenticated
            and user.id == self.request.user.id
        ):
            raise forms.ValidationError(_("You cannot send a message to yourself."))

        self.recipient_user = user
        return username

    def clean_subject(self):
        subject = (self.cleaned_data.get("subject") or "").strip()
        if len(subject) < 3:
            raise forms.ValidationError(_("Subject is too short."))
        return subject

    def clean_content(self):
        content = self.cleaned_data.get("content", "").strip()
        if len(content) > FORUM_MAX_PM_LENGTH:
            raise forms.ValidationError(_("Message is too long."))
        text_content = strip_tags(content).strip()
        if len(text_content) < 2:
            raise forms.ValidationError(_("Message is too short."))
        return content


class PrivateMessageReplyForm(forms.Form):
    content = ProseEditorFormField(
        extensions=FORUM_POST_EXTENSIONS,
        sanitize=True,
        label=_("Reply"),
    )

    def clean_content(self):
        content = self.cleaned_data.get("content", "").strip()
        if len(content) > FORUM_MAX_PM_LENGTH:
            raise forms.ValidationError(_("Message is too long."))
        text_content = strip_tags(content).strip()
        if len(text_content) < 2:
            raise forms.ValidationError(_("Message is too short."))
        return content
