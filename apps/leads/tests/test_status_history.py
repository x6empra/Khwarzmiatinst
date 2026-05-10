"""StatusHistory model + Lead.update_status — TESTING.md (F6)."""

import pytest

from apps.accounts.factories import ManagerFactory, SupervisorFactory
from apps.leads.factories import LeadFactory
from apps.leads.models import LeadStatus, StatusHistory


@pytest.mark.django_db
class TestStatusHistory:
    def test_update_status_creates_audit_entry(self):
        lead = LeadFactory(status=LeadStatus.NEW)
        user = SupervisorFactory()
        entry = lead.update_status(LeadStatus.IN_PROGRESS, changed_by=user, note="تواصلت")
        assert isinstance(entry, StatusHistory)
        assert entry.from_status == LeadStatus.NEW
        assert entry.to_status == LeadStatus.IN_PROGRESS
        assert entry.changed_by == user
        assert entry.note == "تواصلت"

    def test_update_status_updates_lead(self):
        lead = LeadFactory(status=LeadStatus.NEW)
        lead.update_status(LeadStatus.CLOSED, changed_by=ManagerFactory())
        lead.refresh_from_db()
        assert lead.status == LeadStatus.CLOSED

    def test_invalid_status_raises(self):
        lead = LeadFactory()
        with pytest.raises(ValueError):
            lead.update_status("WRONG", changed_by=None)

    def test_history_ordering_descending(self):
        lead = LeadFactory()
        sup = SupervisorFactory()
        lead.update_status(LeadStatus.IN_PROGRESS, changed_by=sup)
        lead.update_status(LeadStatus.CLOSED, changed_by=sup)
        history = list(lead.history.all())
        # newest first
        assert history[0].to_status == LeadStatus.CLOSED
        assert history[1].to_status == LeadStatus.IN_PROGRESS

    def test_history_cascade_on_lead_delete(self):
        lead = LeadFactory()
        lead.update_status(LeadStatus.CLOSED, changed_by=ManagerFactory())
        lead_id = lead.id
        lead.delete()
        assert StatusHistory.objects.filter(lead_id=lead_id).count() == 0

    def test_changed_by_set_null_on_user_delete(self):
        sup = SupervisorFactory()
        lead = LeadFactory()
        entry = lead.update_status(LeadStatus.IN_PROGRESS, changed_by=sup)
        sup.delete()
        entry.refresh_from_db()
        assert entry.changed_by is None
