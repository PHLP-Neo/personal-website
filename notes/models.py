from django.db import models
from django.urls import reverse
from django.utils import timezone


class Post(models.Model):
    title = models.CharField(
        max_length=200,
    )

    slug = models.SlugField(
        max_length=220,
        unique=True,
        help_text="Used in the post URL.",
    )

    summary = models.CharField(
        max_length=300,
        blank=True,
        help_text="Optional summary shown on the Notes page.",
    )

    body = models.TextField()

    image = models.ImageField(
        upload_to="notes/images/",
        blank=True,
        null=True,
    )

    published = models.BooleanField(
        default=False,
        help_text="Only published posts are visible publicly.",
    )

    published_at = models.DateTimeField(
        default=timezone.now,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-published_at",
            "-created_at",
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            "notes:detail",
            kwargs={"slug": self.slug},
        )
