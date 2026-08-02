from types import SimpleNamespace

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Project
from .validators import (
    MAX_PROJECT_REPORT_SIZE,
    validate_project_report_size,
)


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


class ProjectReportValidationTests(TestCase):
    def _project(self, report):
        return Project(
            title="Report test",
            slug="report-test",
            short_description="Test project",
            description="Test description",
            report=report,
        )

    def test_pdf_extension_is_accepted(self):
        project = self._project(
            SimpleUploadedFile(
                "report.pdf",
                b"%PDF-1.7 test",
                content_type="application/pdf",
            )
        )

        project.full_clean()

    def test_non_pdf_extension_is_rejected(self):
        project = self._project(
            SimpleUploadedFile(
                "report.txt",
                b"not a PDF",
                content_type="text/plain",
            )
        )

        with self.assertRaises(ValidationError) as error:
            project.full_clean()

        self.assertIn("report", error.exception.message_dict)

    def test_report_larger_than_fifty_megabytes_is_rejected(self):
        oversized_report = SimpleNamespace(
            size=MAX_PROJECT_REPORT_SIZE + 1,
        )

        with self.assertRaisesMessage(
            ValidationError,
            "Project reports must be 50 MB or smaller.",
        ):
            validate_project_report_size(oversized_report)

    def test_report_at_fifty_megabytes_is_accepted(self):
        report = SimpleNamespace(size=MAX_PROJECT_REPORT_SIZE)

        validate_project_report_size(report)
