"""
reCAPTCHA v3 verification — F8.

في dev (لا توجد private key) → ترجع True (يسهّل الاختبار).
في production → Google siteverify + threshold check.
"""

from __future__ import annotations

import json
import logging
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings

logger = logging.getLogger(__name__)

VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"


def verify_recaptcha(token: str | None, *, remote_ip: str | None = None) -> tuple[bool, str | None]:
    """يرجع (passed, error_code_for_logs)."""
    secret = getattr(settings, "RECAPTCHA_PRIVATE_KEY", "")
    if not secret:
        logger.debug("recaptcha skipped (no RECAPTCHA_PRIVATE_KEY)")
        return True, None

    if not token:
        return False, "missing_token"

    payload = urlencode({"secret": secret, "response": token, "remoteip": remote_ip or ""}).encode(
        "utf-8"
    )

    try:
        request = Request(VERIFY_URL, data=payload, method="POST")
        with urlopen(request, timeout=5) as response:
            body = json.loads(response.read().decode("utf-8"))
    except (URLError, ValueError, TimeoutError) as exc:
        logger.warning("recaptcha api error: %s", exc)
        return False, "verify_error"

    if not body.get("success"):
        return False, f"google_rejected:{body.get('error-codes', [])}"

    score = float(body.get("score", 0))
    threshold = float(getattr(settings, "RECAPTCHA_REQUIRED_SCORE", 0.5))
    if score < threshold:
        return False, f"low_score:{score}"

    return True, None
