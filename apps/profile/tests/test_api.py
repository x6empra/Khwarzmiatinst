"""Profile API tests — F10 (API.md §Profile)."""

import pytest

from apps.accounts.factories import InvestorFactory, ManagerFactory, SupervisorFactory
from apps.leads.factories import LeadFactory


@pytest.mark.django_db
class TestProfileOrdersAPI:
    URL = "/api/profile/orders/"

    def test_anonymous_401(self, client):
        response = client.get(self.URL)
        assert response.status_code in (401, 403)

    def test_supervisor_403(self, client):
        client.force_login(SupervisorFactory())
        assert client.get(self.URL).status_code == 403

    def test_manager_403(self, client):
        client.force_login(ManagerFactory())
        assert client.get(self.URL).status_code == 403

    def test_investor_sees_only_own(self, client):
        me = InvestorFactory(email="me@x.com")
        other = InvestorFactory(email="other@x.com")
        LeadFactory(investor=me)
        LeadFactory(investor=me)
        LeadFactory(investor=other)

        client.force_login(me)
        response = client.get(self.URL)
        assert response.status_code == 200
        body = response.json()
        # IsInvestor own-only — يجب أن يرى 2 فقط
        assert body["count"] == 2

    def test_empty_for_new_investor(self, client):
        client.force_login(InvestorFactory())
        response = client.get(self.URL)
        assert response.status_code == 200
        assert response.json()["count"] == 0
