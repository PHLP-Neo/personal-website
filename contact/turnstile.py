import json
import logging
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings


logger = logging.getLogger(__name__)

VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


def verify_turnstile(token, remote_ip=""):
    """Validate a single-use Turnstile token with Cloudflare."""
    if not token or not settings.TURNSTILE_SECRET_KEY:
        return False

    payload = {
        "secret": settings.TURNSTILE_SECRET_KEY,
        "response": token,
    }

    if remote_ip:
        payload["remoteip"] = remote_ip

    request = Request(
        VERIFY_URL,
        data=urlencode(payload).encode("utf-8"),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=5) as response:
            result = json.load(response)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        logger.warning("Turnstile verification failed: %s", error)
        return False

    if not result.get("success"):
        return False

    expected_hostname = settings.TURNSTILE_EXPECTED_HOSTNAME
    return not expected_hostname or result.get("hostname") == expected_hostname
