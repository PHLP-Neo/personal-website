from django.conf import settings
from django.core.cache import cache
from django.utils.crypto import salted_hmac


def allow_contact_submission(request):
    """Allow a small number of contact attempts per client and time window."""
    client_address = (
        request.META.get("HTTP_X_REAL_IP")
        or request.META.get("REMOTE_ADDR")
        or "unknown"
    )
    client_hash = salted_hmac(
        "contact-rate-limit",
        client_address,
    ).hexdigest()
    cache_key = f"contact-rate-limit:{client_hash}"

    if cache.add(
        cache_key,
        1,
        timeout=settings.CONTACT_RATE_LIMIT_WINDOW,
    ):
        return True

    try:
        attempt_count = cache.incr(cache_key)
    except ValueError:
        cache.set(
            cache_key,
            1,
            timeout=settings.CONTACT_RATE_LIMIT_WINDOW,
        )
        return True

    return attempt_count <= settings.CONTACT_RATE_LIMIT
