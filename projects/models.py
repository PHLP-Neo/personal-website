from django.db import models
from django.urls import reverse


class Project(models.Model):
    class Status(models.TextChoices):
        COMPLETED = "completed", "Completed"
        IN_PROGRESS = "in_progress", "In progress"
        ARCHIVED = "archived", "Archived"

    title = models.CharField(
        max_length=150,
    )

    slug = models.SlugField(
        max_length=170,
        unique=True,
        help_text="Used in the project page URL.",
    )

    short_description = models.CharField(
        max_length=300,
        help_text="A concise summary for project cards.",
    )

    description = models.TextField(
        help_text="Full project description.",
    )

    role = models.CharField(
        max_length=200,
        blank=True,
        help_text="Your individual role, especially for group projects.",
    )

    technologies = models.CharField(
        max_length=500,
        blank=True,
        help_text="Comma-separated technologies.",
    )

    thumbnail = models.ImageField(
        upload_to="projects/thumbnails/",
        blank=True,
        null=True,
    )

    report = models.FileField(
        upload_to="projects/reports/",
        blank=True,
        null=True,
        help_text="Optional PDF report.",
    )

    repository_url = models.URLField(
        blank=True,
    )

    live_url = models.URLField(
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.COMPLETED,
    )

    featured = models.BooleanField(
        default=False,
        help_text="Display this project on the homepage.",
    )

    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers appear first.",
    )

    created_at = models.DateField(
        blank=True,
        null=True,
        help_text="Approximate project completion or creation date.",
    )

    published_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "display_order",
            "-created_at",
            "title",
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            "projects:detail",
            kwargs={"slug": self.slug},
        )

    def technology_list(self):
        return [
            technology.strip()
            for technology in self.technologies.split(",")
            if technology.strip()
        ]
