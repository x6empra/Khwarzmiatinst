"""Celery tasks tests — F7 (TESTING.md §Unit)."""

from unittest.mock import patch

import pytest
from django.core import mail

from apps.leads.factories import LeadFactory
from apps.notifications.tasks import send_email_to_admin, send_telegram_to_admin


@pytest.mark.django_db
class TestSendTelegramTask:
    def test_calls_send_message_with_lead_info(self):
        lead = LeadFactory(name="أحمد", phone="0501234567", email="a@x.com")
        with patch("apps.notifications.tasks.send_message") as mocked:
            send_telegram_to_admin(lead.id)
        mocked.assert_called_once()
        text = mocked.call_args[0][0]
        assert "أحمد" in text
        assert "0501234567" in text
        assert "a@x.com" in text
        assert f"#{lead.id}" in text

    def test_missing_lead_swallowed(self):
        """لا يفشل لو حُذف الـ Lead (مثلاً سباق zoom)."""
        with patch("apps.notifications.tasks.send_message") as mocked:
            send_telegram_to_admin(99_999)
        mocked.assert_not_called()


@pytest.mark.django_db
class TestSendEmailTask:
    """نمسح outbox بعد LeadFactory لأن signal يرسل email تلقائياً (F7)."""

    def test_email_sent_with_correct_content(self):
        lead = LeadFactory(name="سارة", email="lead@x.com")
        mail.outbox = []  # اعزل عن signal email
        send_email_to_admin(lead.id)
        assert len(mail.outbox) == 1
        msg = mail.outbox[0]
        assert "سارة" in msg.subject
        assert lead.package.name in msg.subject
        assert "سارة" in msg.body
        assert "lead@x.com" in msg.body

    def test_html_alternative_attached(self):
        lead = LeadFactory(name="x")
        mail.outbox = []
        send_email_to_admin(lead.id)
        msg = mail.outbox[0]
        html_alts = [alt for alt in msg.alternatives if alt[1] == "text/html"]
        assert len(html_alts) == 1
        assert "خوارزميات" in html_alts[0][0]

    def test_recipient_uses_admin_email(self, settings):
        settings.ADMIN_NOTIFICATION_EMAIL = "ops@khawarizmiat.com"
        lead = LeadFactory()
        mail.outbox = []
        send_email_to_admin(lead.id)
        assert mail.outbox[0].to == ["ops@khawarizmiat.com"]

    def test_missing_lead_swallowed(self):
        send_email_to_admin(99_999)
        assert len(mail.outbox) == 0
