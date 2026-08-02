from django.core.exceptions import ValidationError


MAX_PROJECT_REPORT_SIZE = 50 * 1024 * 1024


def validate_project_report_size(report):
    if report.size > MAX_PROJECT_REPORT_SIZE:
        raise ValidationError(
            "Project reports must be 50 MB or smaller.",
            code="project_report_too_large",
        )
