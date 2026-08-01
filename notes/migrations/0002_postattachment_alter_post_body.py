import notes.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("notes", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="body",
            field=models.TextField(
                help_text=(
                    "Markdown supported. Embed a YouTube video on its own line "
                    "with [[youtube:https://www.youtube.com/watch?v=VIDEO_ID]]."
                ),
            ),
        ),
        migrations.CreateModel(
            name="PostAttachment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        help_text=(
                            "PNG, JPEG, WebP and animated GIF images are supported."
                        ),
                        upload_to=notes.models.post_attachment_path,
                    ),
                ),
                (
                    "alt_text",
                    models.CharField(
                        help_text="Describe the image for accessibility.",
                        max_length=200,
                    ),
                ),
                (
                    "caption",
                    models.CharField(blank=True, max_length=300),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attachments",
                        to="notes.post",
                    ),
                ),
            ],
            options={
                "ordering": ["created_at", "pk"],
            },
        ),
    ]
