import io
from unittest.mock import patch

from django.core import mail
from django.core.cache import cache
from django.core.mail.backends.base import BaseEmailBackend
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import ContactMessage
from .turnstile import verify_turnstile


class FailingEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        raise RuntimeError("Email provider unavailable")


@override_settings(
    SECURE_SSL_REDIRECT=False,
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    CONTACT_NOTIFICATION_EMAIL="owner@example.com",
    DEFAULT_FROM_EMAIL="Neo Portfolio <website@send.phlpneo.com>",
    TURNSTILE_SITE_KEY="1x00000000000000000000AA",
    TURNSTILE_SECRET_KEY="1x0000000000000000000000000000000AA",
    TURNSTILE_EXPECTED_HOSTNAME="www.phlpneo.com",
)
class ContactViewTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_contact_page_loads(self):
        response = self.client.get(reverse("contact:contact"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Get in touch")
        self.assertContains(response, "cf-turnstile")

    @patch("contact.views.verify_turnstile", return_value=True)
    def test_valid_message_is_saved(self, verify):
        response = self.client.post(
            reverse("contact:contact"),
            {
                "name": "Test User",
                "email": "test@example.com",
                "subject": "Test subject",
                "message": "Test message",
                "website": "",
                "cf-turnstile-response": "valid-token",
            },
            follow=True,
        )

        self.assertEqual(ContactMessage.objects.count(), 1)
        contact_message = ContactMessage.objects.get()
        self.assertIsNotNone(contact_message.notification_sent_at)
        self.assertEqual(contact_message.notification_error, "")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            "[phlpneo.com] Test subject",
        )
        self.assertEqual(mail.outbox[0].reply_to, ["test@example.com"])
        self.assertContains(response, "submitted successfully")
        verify.assert_called_once_with("valid-token", "127.0.0.1")

    def test_invalid_email_is_rejected(self):
        self.client.post(
            reverse("contact:contact"),
            {
                "name": "Test User",
                "email": "invalid-email",
                "subject": "Test subject",
                "message": "Test message",
                "website": "",
            },
        )

        self.assertEqual(ContactMessage.objects.count(), 0)

    @override_settings(
        EMAIL_BACKEND="contact.tests.FailingEmailBackend",
    )
    @patch("contact.views.verify_turnstile", return_value=True)
    def test_email_failure_does_not_lose_contact_message(self, verify):
        response = self.client.post(
            reverse("contact:contact"),
            {
                "name": "Test User",
                "email": "test@example.com",
                "subject": "Test subject",
                "message": "Test message",
                "website": "",
                "cf-turnstile-response": "valid-token",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "submitted successfully")
        contact_message = ContactMessage.objects.get()
        self.assertIsNone(contact_message.notification_sent_at)
        self.assertIn(
            "Email provider unavailable",
            contact_message.notification_error,
        )

    @patch("contact.views.verify_turnstile", return_value=False)
    def test_failed_human_verification_is_rejected(self, verify):
        response = self.client.post(
            reverse("contact:contact"),
            {
                "name": "Test User",
                "email": "test@example.com",
                "subject": "Test subject",
                "message": "Test message",
                "website": "",
                "cf-turnstile-response": "invalid-token",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Human verification failed")
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_honeypot_submission_is_rejected(self):
        self.client.post(
            reverse("contact:contact"),
            {
                "name": "Spam Bot",
                "email": "bot@example.com",
                "subject": "Spam",
                "message": "Spam message",
                "website": "https://spam.example.com",
            },
        )

        self.assertEqual(ContactMessage.objects.count(), 0)

    @override_settings(CONTACT_RATE_LIMIT=2)
    def test_excessive_contact_attempts_are_throttled(self):
        payload = {
            "name": "Test User",
            "email": "invalid-email",
            "subject": "Test subject",
            "message": "Test message",
            "website": "",
        }

        self.client.post(
            reverse("contact:contact"),
            payload,
            HTTP_X_REAL_IP="192.0.2.10",
        )
        self.client.post(
            reverse("contact:contact"),
            payload,
            HTTP_X_REAL_IP="192.0.2.10",
        )
        response = self.client.post(
            reverse("contact:contact"),
            payload,
            HTTP_X_REAL_IP="192.0.2.10",
        )

        self.assertEqual(response.status_code, 429)
        self.assertContains(
            response,
            "Too many submissions",
            status_code=429,
        )
        self.assertEqual(ContactMessage.objects.count(), 0)


@override_settings(
    TURNSTILE_SECRET_KEY="test-secret",
    TURNSTILE_EXPECTED_HOSTNAME="www.phlpneo.com",
)
class TurnstileVerificationTests(TestCase):
    @patch("contact.turnstile.urlopen")
    def test_successful_response_for_expected_hostname_is_accepted(self, urlopen):
        urlopen.return_value.__enter__.return_value = io.BytesIO(
            b'{"success": true, "hostname": "www.phlpneo.com"}'
        )

        self.assertTrue(verify_turnstile("valid-token", "192.0.2.1"))

    @patch("contact.turnstile.urlopen")
    def test_response_for_another_hostname_is_rejected(self, urlopen):
        urlopen.return_value.__enter__.return_value = io.BytesIO(
            b'{"success": true, "hostname": "attacker.example"}'
        )

        self.assertFalse(verify_turnstile("valid-token", "192.0.2.1"))

    def test_missing_token_is_rejected(self):
        self.assertFalse(verify_turnstile("", "192.0.2.1"))
