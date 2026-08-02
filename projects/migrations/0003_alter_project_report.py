import django.core.validators
from django.db import migrations, models
import projects.validators


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0002_project_demo_description_project_demo_url"),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="report",
            field=models.FileField(
                blank=True,
                help_text="Optional PDF report. Maximum file size: 50 MB.",
                null=True,
                upload_to="projects/reports/",
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=["pdf"]
                    ),
                    projects.validators.validate_project_report_size,
                ],
            ),
        ),
    ]
