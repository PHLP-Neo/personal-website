from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import ContactMessageForm
from .services import send_contact_notification
from .throttling import allow_contact_submission
from .turnstile import verify_turnstile


def _client_ip(request):
    return request.META.get(
        "HTTP_X_REAL_IP",
        request.META.get("REMOTE_ADDR", ""),
    )


def contact(request):
    if request.method == "POST":
        form = ContactMessageForm(request.POST)

        if not allow_contact_submission(request):
            form.add_error(
                None,
                "Too many submissions. Please try again later.",
            )

            return render(
                request,
                "contact/contact.html",
                {
                    "form": form,
                    "turnstile_site_key": settings.TURNSTILE_SITE_KEY,
                },
                status=429,
            )

        if form.is_valid() and not verify_turnstile(
            request.POST.get("cf-turnstile-response", ""),
            _client_ip(request),
        ):
            form.add_error(
                None,
                "Human verification failed. Please try again.",
            )

        if form.is_valid():
            contact_message = form.save()

            send_contact_notification(contact_message)

            messages.success(
                request,
                "Your message has been submitted successfully.",
            )

            return redirect("contact:contact")

    else:
        form = ContactMessageForm()

    return render(
        request,
        "contact/contact.html",
        {
            "form": form,
            "turnstile_site_key": settings.TURNSTILE_SITE_KEY,
        },
    )
