from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Project


@override_settings(SITE_URL="https://www.phlpneo.com")
class ProjectPaginationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        for number in range(7):
            Project.objects.create(
                title=f"Project {number}",
                slug=f"project-{number}",
                short_description="Test project",
                description="Test description",
            )

    def test_first_page_contains_six_projects(self):
        response = self.client.get(reverse("projects:list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["projects"]), 6)
        self.assertContains(response, "?page=2")

    def test_second_page_contains_remaining_project(self):
        response = self.client.get(reverse("projects:list"), {"page": 2})

        self.assertEqual(len(response.context["projects"]), 1)
        self.assertContains(
            response,
            '<link rel="canonical" href="https://www.phlpneo.com/projects/?page=2">',
            html=True,
        )
