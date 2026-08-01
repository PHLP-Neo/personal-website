from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Post


@override_settings(SITE_URL="https://www.phlpneo.com")
class PostPaginationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        for number in range(10):
            Post.objects.create(
                title=f"Post {number}",
                slug=f"post-{number}",
                body="Test body",
                published=True,
            )

    def test_first_page_contains_nine_posts(self):
        response = self.client.get(reverse("notes:list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["posts"]), 9)
        self.assertContains(response, "?page=2")
        self.assertContains(
            response,
            '<link rel="canonical" href="https://www.phlpneo.com/notes/">',
            html=True,
        )

    def test_second_page_contains_remaining_post(self):
        response = self.client.get(reverse("notes:list"), {"page": 2})

        self.assertEqual(len(response.context["posts"]), 1)
        self.assertContains(
            response,
            '<link rel="canonical" href="https://www.phlpneo.com/notes/?page=2">',
            html=True,
        )
