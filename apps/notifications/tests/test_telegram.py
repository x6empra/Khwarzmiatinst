"""telegram.py tests — F7 (TESTING.md §Unit)."""

from unittest.mock import patch

import pytest

from apps.notifications.telegram import TelegramError, send_message


class TestTelegram:
    def test_dev_bypass_no_token(self, settings):
        settings.TELEGRAM_BOT_TOKEN = ""
        settings.TELEGRAM_ADMIN_CHAT_ID = "12345"
        result = send_message("hello")
        assert result is None  # silently skipped

    def test_dev_bypass_no_chat_id(self, settings):
        settings.TELEGRAM_BOT_TOKEN = "abc"
        settings.TELEGRAM_ADMIN_CHAT_ID = ""
        result = send_message("hello")
        assert result is None

    def test_success(self, settings):
        settings.TELEGRAM_BOT_TOKEN = "test-token"
        settings.TELEGRAM_ADMIN_CHAT_ID = "999"
        with patch("apps.notifications.telegram.urlopen") as mocked:
            mocked.return_value.__enter__.return_value.read.return_value = (
                b'{"ok": true, "result": {"message_id": 1}}'
            )
            result = send_message("hi")
        assert result["ok"] is True
        assert mocked.call_count == 1

    def test_telegram_error_on_api_failure(self, settings):
        settings.TELEGRAM_BOT_TOKEN = "test-token"
        settings.TELEGRAM_ADMIN_CHAT_ID = "999"
        with patch("apps.notifications.telegram.urlopen") as mocked:
            mocked.return_value.__enter__.return_value.read.return_value = (
                b'{"ok": false, "description": "bad request"}'
            )
            with pytest.raises(TelegramError):
                send_message("hi")

    def test_telegram_error_on_network(self, settings):
        settings.TELEGRAM_BOT_TOKEN = "test-token"
        settings.TELEGRAM_ADMIN_CHAT_ID = "999"
        from urllib.error import URLError

        with patch("apps.notifications.telegram.urlopen", side_effect=URLError("dns")):
            with pytest.raises(TelegramError):
                send_message("hi")
