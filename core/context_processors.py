from django.conf import settings


def site_metadata(request):
    """Expose canonical site URLs to every public template."""
    return {
        "site_url": settings.SITE_URL,
        "canonical_url": f"{settings.SITE_URL}{request.path}",
    }
