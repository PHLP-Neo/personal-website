from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils import timezone

from .markdown import render_markdown


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

    body = models.TextField(
        help_text=(
            "Markdown supported. Embed a YouTube video on its own line with "
            "[[youtube:https://www.youtube.com/watch?v=VIDEO_ID]]."
        ),
    )

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

    @cached_property
    def rendered_body(self):
        return render_markdown(self.body)


def post_attachment_path(instance, filename):
    return f"notes/attachments/{instance.post.slug}/{filename}"


class PostAttachment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="attachments",
    )

    image = models.ImageField(
        upload_to=post_attachment_path,
        help_text="PNG, JPEG, WebP and animated GIF images are supported.",
    )

    alt_text = models.CharField(
        max_length=200,
        help_text="Describe the image for accessibility.",
    )

    caption = models.CharField(
        max_length=300,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["created_at", "pk"]

    def __str__(self):
        return f"{self.post.title}: {self.alt_text}"

    def markdown_reference(self):
        if not self.image:
            return ""

        alt_text = self.alt_text.replace("\\", "\\\\").replace("]", "\\]")
        reference = f"![{alt_text}]({self.image.url})"

        if self.caption:
            return f"{reference}\n\n*{self.caption}*"

        return reference
