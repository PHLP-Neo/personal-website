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
    response_status = 200

    if request.method == "POST":
        form = ContactMessageForm(request.POST)

        if form.is_valid():
            turnstile_valid = verify_turnstile(
                request.POST.get("cf-turnstile-response", ""),
                _client_ip(request),
            )

            if not turnstile_valid:
                form.add_error(
                    None,
                    "Human verification failed. Please try again.",
                )
            elif not allow_contact_submission(request):
                form.add_error(
                    None,
                    "Too many submissions. Please try again later.",
                )
                response_status = 429
            else:
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
        status=response_status,
    )
