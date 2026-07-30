from django.db import models


class ContactMessage(models.Model):
    name = models.CharField(
        max_length=100,
    )

    email = models.EmailField()

    subject = models.CharField(
        max_length=150,
    )

    message = models.TextField(
        max_length=5000,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    read = models.BooleanField(
        default=False,
        help_text="Mark this after reviewing the message.",
    )

    archived = models.BooleanField(
        default=False,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name}: {self.subject}"
