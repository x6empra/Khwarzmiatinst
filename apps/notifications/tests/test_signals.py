"""Signal integration tests — F7 (TESTING.md §Unit)."""

from unittest.mock import patch

import pytest
from django.core import mail

from apps.leads.factories import LeadFactory


@pytest.mark.django_db
class TestLeadCreatedSignal:
    def test_signal_dispatches_telegram_task(self):
        with patch("apps.notifications.tasks.send_message") as tg:
            LeadFactory()
        tg.assert_called_once()

    def test_signal_dispatches_email_task(self):
        LeadFactory()
        # CELERY_TASK_ALWAYS_EAGER=True → الـ email أُرسل بالفعل
        assert len(mail.outbox) == 1

    def test_update_does_not_dispatch(self):
        lead = LeadFactory()
        mail.outbox = []  # reset
        with patch("apps.notifications.tasks.send_message") as tg:
            lead.notes = "تحديث"
            lead.save()
        tg.assert_not_called()
        assert len(mail.outbox) == 0
