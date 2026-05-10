"""DRF Lead API tests — F5/F6 (API.md §Leads)."""

import pytest

from apps.accounts.factories import InvestorFactory, ManagerFactory, SupervisorFactory
from apps.leads.factories import LeadFactory
from apps.leads.models import Lead, LeadStatus, StatusHistory


@pytest.mark.django_db
class TestLeadListAPI:
    URL = "/api/leads/"

    def test_anonymous_401(self, client):
        response = client.get(self.URL)
        assert response.status_code in (401, 403)

    def test_investor_403(self, client):
        client.force_login(InvestorFactory())
        response = client.get(self.URL)
        assert response.status_code == 403

    def test_supervisor_can_list(self, client):
        client.force_login(SupervisorFactory())
        LeadFactory.create_batch(3)
        response = client.get(self.URL)
        assert response.status_code == 200
        assert response.json()["count"] == 3

    def test_manager_can_list(self, client):
        client.force_login(ManagerFactory())
        LeadFactory.create_batch(2)
        response = client.get(self.URL)
        assert response.status_code == 200

    def test_filter_by_status(self, client):
        client.force_login(SupervisorFactory())
        LeadFactory(status=LeadStatus.NEW)
        LeadFactory(status=LeadStatus.CLOSED)
        response = client.get(self.URL + "?status=closed")
        results = response.json()["results"]
        assert len(results) == 1
        assert results[0]["status"] == "closed"

    def test_search_by_name(self, client):
        client.force_login(SupervisorFactory())
        LeadFactory(name="أحمد")
        LeadFactory(name="سارة")
        response = client.get(self.URL + "?search=أحمد")
        assert response.json()["count"] == 1


@pytest.mark.django_db
class TestLeadStatusUpdateAPI:
    def url(self, lead):
        return f"/api/leads/{lead.id}/status/"

    def test_supervisor_can_update_to_in_progress(self, client):
        sup = SupervisorFactory()
        client.force_login(sup)
        lead = LeadFactory(status=LeadStatus.NEW)
        response = client.patch(
            self.url(lead),
            {"status": "in_progress", "note": "ok"},
            content_type="application/json",
        )
        assert response.status_code == 200
        lead.refresh_from_db()
        assert lead.status == LeadStatus.IN_PROGRESS
        assert StatusHistory.objects.filter(lead=lead, to_status=LeadStatus.IN_PROGRESS).exists()

    def test_supervisor_cannot_cancel(self, client):
        sup = SupervisorFactory()
        client.force_login(sup)
        lead = LeadFactory()
        response = client.patch(
            self.url(lead),
            {"status": "cancelled"},
            content_type="application/json",
        )
        assert response.status_code == 403
        lead.refresh_from_db()
        assert lead.status == LeadStatus.NEW

    def test_manager_can_cancel(self, client):
        client.force_login(ManagerFactory())
        lead = LeadFactory()
        response = client.patch(
            self.url(lead),
            {"status": "cancelled"},
            content_type="application/json",
        )
        assert response.status_code == 200
        lead.refresh_from_db()
        assert lead.status == LeadStatus.CANCELLED

    def test_investor_403(self, client):
        client.force_login(InvestorFactory())
        lead = LeadFactory()
        response = client.patch(
            self.url(lead),
            {"status": "closed"},
            content_type="application/json",
        )
        assert response.status_code == 403

    def test_invalid_status_400(self, client):
        client.force_login(SupervisorFactory())
        lead = LeadFactory()
        response = client.patch(
            self.url(lead),
            {"status": "garbage"},
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_404_when_missing(self, client):
        client.force_login(SupervisorFactory())
        response = client.patch(
            "/api/leads/9999/status/",
            {"status": "closed"},
            content_type="application/json",
        )
        assert response.status_code == 404


@pytest.mark.django_db
class TestLeadDeleteAPI:
    def test_manager_can_delete(self, client):
        client.force_login(ManagerFactory())
        lead = LeadFactory()
        response = client.delete(f"/api/leads/{lead.id}/")
        assert response.status_code == 204
        assert not Lead.objects.filter(id=lead.id).exists()

    def test_supervisor_403(self, client):
        client.force_login(SupervisorFactory())
        lead = LeadFactory()
        response = client.delete(f"/api/leads/{lead.id}/")
        assert response.status_code == 403
        assert Lead.objects.filter(id=lead.id).exists()

    def test_investor_403(self, client):
        client.force_login(InvestorFactory())
        lead = LeadFactory()
        response = client.delete(f"/api/leads/{lead.id}/")
        assert response.status_code == 403
