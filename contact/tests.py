from django.core import mail
from django.core.cache import cache
from django.core.mail.backends.base import BaseEmailBackend
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import ContactMessage


class FailingEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        raise RuntimeError("Email provider unavailable")


@override_settings(
    SECURE_SSL_REDIRECT=False,
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    CONTACT_NOTIFICATION_EMAIL="owner@example.com",
    DEFAULT_FROM_EMAIL="Neo Portfolio <website@send.phlpneo.com>",
)
class ContactViewTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_contact_page_loads(self):
        response = self.client.get(reverse("contact:contact"))

        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            "Get in touch",
        )

    def test_valid_message_is_saved(self):
        response = self.client.post(
            reverse("contact:contact"),
            {
                "name": "Test User",
                "email": "test@example.com",
                "subject": "Test subject",
                "message": "Test message",
                "website": "",
            },
            follow=True,
        )

        self.assertEqual(
            ContactMessage.objects.count(),
            1,
        )

        contact_message = ContactMessage.objects.get()

        self.assertIsNotNone(
            contact_message.notification_sent_at,
        )
        self.assertEqual(
            contact_message.notification_error,
            "",
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            "[phlpneo.com] Test subject",
        )
        self.assertEqual(
            mail.outbox[0].reply_to,
            ["test@example.com"],
        )

        self.assertContains(
            response,
            "submitted successfully",
        )

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

        self.assertEqual(
            ContactMessage.objects.count(),
            0,
        )

    @override_settings(
        EMAIL_BACKEND="contact.tests.FailingEmailBackend",
    )
    def test_email_failure_does_not_lose_contact_message(self):
        response = self.client.post(
            reverse("contact:contact"),
            {
                "name": "Test User",
                "email": "test@example.com",
                "subject": "Test subject",
                "message": "Test message",
                "website": "",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "submitted successfully",
        )

        contact_message = ContactMessage.objects.get()

        self.assertIsNone(
            contact_message.notification_sent_at,
        )
        self.assertIn(
            "Email provider unavailable",
            contact_message.notification_error,
        )

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

        self.assertEqual(
            ContactMessage.objects.count(),
            0,
        )

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
        self.assertEqual(
            ContactMessage.objects.count(),
            0,
        )
