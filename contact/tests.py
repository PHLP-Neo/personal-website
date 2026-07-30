from django.test import TestCase
from django.urls import reverse

from .models import ContactMessage


class ContactViewTests(TestCase):
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
