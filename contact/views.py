from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import ContactMessageForm
from .services import send_contact_notification
from .throttling import allow_contact_submission


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
                },
                status=429,
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
        },
    )
