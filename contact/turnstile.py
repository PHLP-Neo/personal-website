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
    if not token:
        return False

    if not settings.TURNSTILE_SECRET_KEY:
        logger.error("Turnstile secret key is not configured.")
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
    except HTTPError as error:
        try:
            error_result = json.loads(error.read().decode("utf-8"))
            error_codes = error_result.get("error-codes", [])
        except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
            error_codes = ["unreadable-error-response"]

        logger.warning(
            "Turnstile rejected verification: http_status=%s error_codes=%s",
            error.code,
            error_codes,
        )
        return False
    except (URLError, TimeoutError) as error:
        logger.warning("Turnstile verification unavailable: %s", error)
        return False
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        logger.warning("Turnstile returned invalid JSON: %s", error)
        return False

    if not result.get("success"):
        logger.warning(
            "Turnstile rejected verification: error_codes=%s",
            result.get("error-codes", []),
        )
        return False

    expected_hostname = settings.TURNSTILE_EXPECTED_HOSTNAME
    actual_hostname = result.get("hostname")

    if expected_hostname and actual_hostname != expected_hostname:
        logger.warning(
            "Turnstile hostname mismatch: expected=%s actual=%s",
            expected_hostname,
            actual_hostname,
        )
        return False

    return True
