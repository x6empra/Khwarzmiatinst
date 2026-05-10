"""
Telegram Bot helper (F7).

Dev bypass:
  - بدون TELEGRAM_BOT_TOKEN أو TELEGRAM_ADMIN_CHAT_ID → يطبع log ويرجع NOOP.
"""

from __future__ import annotations

import json
import logging
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings

logger = logging.getLogger(__name__)


class TelegramError(RuntimeError):
    """يُرفع لتمكين Celery من إعادة المحاولة."""


def _api_url(token: str, method: str) -> str:
    return f"https://api.telegram.org/bot{token}/{method}"


def send_message(text: str, *, parse_mode: str = "HTML") -> dict | None:
    """
    يرسل رسالة لمسؤولي خوارزميات.
    يرجع dict من ردّ Telegram، أو None في dev mode.
    يُرفع TelegramError عند الفشل (ليُعيد Celery المحاولة).
    """
    token = getattr(settings, "TELEGRAM_BOT_TOKEN", "") or ""
    chat_id = getattr(settings, "TELEGRAM_ADMIN_CHAT_ID", "") or ""

    if not token or not chat_id:
        logger.info("telegram skipped (no token/chat_id) — text=%s", text[:80])
        return None

    payload = urlencode(
        {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")

    request = Request(_api_url(token, "sendMessage"), data=payload, method="POST")
    try:
        with urlopen(request, timeout=10) as response:
            body = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        text_body = exc.read().decode("utf-8", errors="ignore") if hasattr(exc, "read") else str(exc)
        raise TelegramError(f"telegram HTTPError {exc.code}: {text_body}") from exc
    except (URLError, ValueError, TimeoutError) as exc:
        raise TelegramError(f"telegram connection error: {exc}") from exc

    if not body.get("ok"):
        raise TelegramError(f"telegram api: {body}")
    return body
