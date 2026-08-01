from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("contact", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="contactmessage",
            name="notification_error",
            field=models.TextField(
                blank=True,
                help_text="The most recent notification delivery error.",
            ),
        ),
        migrations.AddField(
            model_name="contactmessage",
            name="notification_sent_at",
            field=models.DateTimeField(
                blank=True,
                help_text=(
                    "When the owner notification email was sent successfully."
                ),
                null=True,
            ),
        ),
    ]
