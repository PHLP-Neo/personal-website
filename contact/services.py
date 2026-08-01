import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

logger = logging.getLogger(__name__)


def send_contact_notification(contact_message):
    """Notify the site owner without risking the saved contact message."""
    recipient = settings.CONTACT_NOTIFICATION_EMAIL.strip()

    if not recipient:
        contact_message.notification_error = (
            "CONTACT_NOTIFICATION_EMAIL is not configured."
        )
        contact_message.save(update_fields=["notification_error"])
        logger.warning(
            "Contact notification skipped for message %s: no recipient configured.",
            contact_message.pk,
        )
        return False

    clean_subject = " ".join(
        contact_message.subject.splitlines()
    ).strip()

    context = {
        "contact_message": contact_message,
    }

    email = EmailMultiAlternatives(
        subject=f"[phlpneo.com] {clean_subject}",
        body=render_to_string(
            "contact/email/notification.txt",
            context,
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient],
        reply_to=[contact_message.email],
    )
    email.attach_alternative(
        render_to_string(
            "contact/email/notification.html",
            context,
        ),
        "text/html",
    )

    try:
        sent_count = email.send(fail_silently=False)

        if sent_count != 1:
            raise RuntimeError(
                f"Email backend reported {sent_count} messages sent."
            )
    except Exception as error:
        contact_message.notification_error = (
            f"{type(error).__name__}: {error}"
        )[:2000]
        contact_message.save(update_fields=["notification_error"])
        logger.exception(
            "Contact notification failed for message %s.",
            contact_message.pk,
        )
        return False

    contact_message.notification_sent_at = timezone.now()
    contact_message.notification_error = ""
    contact_message.save(
        update_fields=[
            "notification_sent_at",
            "notification_error",
        ]
    )
    return True
