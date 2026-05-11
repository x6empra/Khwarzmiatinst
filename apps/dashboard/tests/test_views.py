"""Dashboard views tests — F5/F6 (PERMISSIONS.md §Pages)."""

import pytest
from django.urls import reverse

from apps.accounts.factories import InvestorFactory, ManagerFactory, SupervisorFactory
from apps.leads.factories import LeadFactory
from apps.leads.models import LeadStatus, StatusHistory


@pytest.mark.django_db
class TestDashboardHome:
    URL = reverse("dashboard:home")

    def test_anonymous_redirects_to_login(self, client):
        response = client.get(self.URL)
        assert response.status_code == 302
        assert "login" in response.url

    def test_investor_403(self, client):
        client.force_login(InvestorFactory())
        response = client.get(self.URL)
        assert response.status_code == 403

    def test_supervisor_renders_stats(self, client):
        client.force_login(SupervisorFactory())
        LeadFactory(status=LeadStatus.NEW)
        LeadFactory(status=LeadStatus.IN_PROGRESS)
        response = client.get(self.URL)
        assert response.status_code == 200
        assert "نظرة عامة".encode() in response.content

    def test_manager_renders(self, client):
        client.force_login(ManagerFactory())
        response = client.get(self.URL)
        assert response.status_code == 200


@pytest.mark.django_db
class TestLeadsList:
    URL = reverse("dashboard:leads")

    def test_anonymous_redirects(self, client):
        assert client.get(self.URL).status_code == 302

    def test_investor_403(self, client):
        client.force_login(InvestorFactory())
        assert client.get(self.URL).status_code == 403

    def test_supervisor_sees_leads(self, client):
        client.force_login(SupervisorFactory())
        LeadFactory(name="ZooLead")
        response = client.get(self.URL)
        assert response.status_code == 200
        assert b"ZooLead" in response.content

    def test_filter_by_status(self, client):
        client.force_login(SupervisorFactory())
        LeadFactory(name="OPEN", status=LeadStatus.NEW)
        LeadFactory(name="CLOSED", status=LeadStatus.CLOSED)
        response = client.get(self.URL + "?status=closed")
        assert b"CLOSED" in response.content
        assert b"OPEN" not in response.content

    def test_search_by_name(self, client):
        client.force_login(SupervisorFactory())
        LeadFactory(name="UniqueName")
        LeadFactory(name="OtherPerson")
        response = client.get(self.URL + "?q=UniqueName")
        assert b"UniqueName" in response.content
        assert b"OtherPerson" not in response.content


@pytest.mark.django_db
class TestLeadDetail:
    def test_supervisor_can_view(self, client):
        client.force_login(SupervisorFactory())
        lead = LeadFactory(name="DetailUser")
        response = client.get(reverse("dashboard:lead_detail", args=[lead.id]))
        assert response.status_code == 200
        assert b"DetailUser" in response.content

    def test_includes_history(self, client):
        sup = SupervisorFactory()
        client.force_login(sup)
        lead = LeadFactory()
        lead.update_status(LeadStatus.IN_PROGRESS, changed_by=sup, note="ملاحظة هنا")
        response = client.get(reverse("dashboard:lead_detail", args=[lead.id]))
        assert "ملاحظة هنا".encode() in response.content


@pytest.mark.django_db
class TestStatusHTMX:
    def url(self, lead):
        return reverse("dashboard:lead_status", args=[lead.id])

    def test_supervisor_changes_status(self, client):
        client.force_login(SupervisorFactory())
        lead = LeadFactory(status=LeadStatus.NEW)
        response = client.post(self.url(lead), {"status": "in_progress"})
        assert response.status_code == 200
        lead.refresh_from_db()
        assert lead.status == LeadStatus.IN_PROGRESS

    def test_response_is_html_partial(self, client):
        sup = SupervisorFactory()
        client.force_login(sup)
        lead = LeadFactory()
        response = client.post(self.url(lead), {"status": "closed"})
        assert b"badge-status-closed" in response.content
        assert b"<tr" in response.content

    def test_supervisor_cannot_cancel(self, client):
        client.force_login(SupervisorFactory())
        lead = LeadFactory()
        response = client.post(self.url(lead), {"status": "cancelled"})
        assert response.status_code == 403

    def test_manager_can_cancel(self, client):
        client.force_login(ManagerFactory())
        lead = LeadFactory()
        response = client.post(self.url(lead), {"status": "cancelled"})
        assert response.status_code == 200
        lead.refresh_from_db()
        assert lead.status == LeadStatus.CANCELLED

    def test_invalid_status_400(self, client):
        client.force_login(SupervisorFactory())
        lead = LeadFactory()
        response = client.post(self.url(lead), {"status": "X"})
        assert response.status_code == 400

    def test_audit_trail_recorded(self, client):
        sup = SupervisorFactory()
        client.force_login(sup)
        lead = LeadFactory()
        client.post(self.url(lead), {"status": "in_progress"})
        assert StatusHistory.objects.filter(lead=lead, changed_by=sup).count() == 1


@pytest.mark.django_db
class TestLeadDelete:
    def test_manager_can_delete(self, client):
        client.force_login(ManagerFactory())
        lead = LeadFactory()
        response = client.delete(reverse("dashboard:lead_delete", args=[lead.id]))
        assert response.status_code == 200
        from apps.leads.models import Lead

        assert not Lead.objects.filter(id=lead.id).exists()

    def test_supervisor_403(self, client):
        client.force_login(SupervisorFactory())
        lead = LeadFactory()
        response = client.delete(reverse("dashboard:lead_delete", args=[lead.id]))
        assert response.status_code == 403


@pytest.mark.django_db
class TestPackagesPage:
    URL = reverse("dashboard:packages")

    def test_supervisor_403(self, client):
        client.force_login(SupervisorFactory())
        assert client.get(self.URL).status_code == 403

    def test_manager_can_view(self, client):
        client.force_login(ManagerFactory())
        assert client.get(self.URL).status_code == 200


@pytest.mark.django_db
class TestUsersPage:
    URL = reverse("dashboard:users")

    def test_supervisor_403(self, client):
        client.force_login(SupervisorFactory())
        assert client.get(self.URL).status_code == 403

    def test_manager_can_view(self, client):
        client.force_login(ManagerFactory())
        InvestorFactory()
        assert client.get(self.URL).status_code == 200

    def test_role_filter(self, client):
        client.force_login(ManagerFactory(email="m@x.com"))
        InvestorFactory(email="inv@x.com")
        SupervisorFactory(email="sup@x.com")
        response = client.get(self.URL + "?role=investor")
        body = response.content.decode()
        assert "inv@x.com" in body
        assert "sup@x.com" not in body
