"""View tests — TESTING.md §Unit + API.md §Leads."""

from unittest.mock import patch

import pytest
from django.urls import reverse

from apps.accounts.factories import InvestorFactory
from apps.leads.models import Lead, LeadStatus
from apps.packages.factories import PackageFactory


@pytest.fixture
def package(db):
    return PackageFactory(is_active=True)


@pytest.fixture
def base_data(package):
    return {
        "name": "أحمد محمد",
        "phone": "0501234567",
        "email": "ahmed@test.com",
        "package": package.id,
        "notes": "تفاصيل",
    }


URL = reverse("leads:create")


@pytest.mark.django_db
class TestLeadCreateJSON:
    def test_post_creates_lead_201(self, client, base_data):
        response = client.post(URL, base_data)
        assert response.status_code == 201, response.content
        body = response.json()
        assert body["success"] is True
        assert "lead_id" in body
        assert Lead.objects.filter(email="ahmed@test.com").exists()

    def test_invalid_data_400(self, client, base_data):
        response = client.post(URL, {**base_data, "phone": "x"})
        assert response.status_code == 400
        body = response.json()
        assert body["success"] is False
        assert "phone" in body["errors"]

    def test_inactive_package_400(self, client, base_data):
        from apps.packages.factories import PackageFactory
        inactive = PackageFactory(is_active=False)
        response = client.post(URL, {**base_data, "package": inactive.id})
        assert response.status_code == 400

    def test_anonymous_lead_has_no_investor(self, client, base_data):
        client.post(URL, base_data)
        lead = Lead.objects.get(email="ahmed@test.com")
        assert lead.investor is None
        assert lead.status == LeadStatus.NEW

    def test_authenticated_investor_linked(self, client, base_data):
        investor = InvestorFactory(email="me@x.com")
        client.force_login(investor)
        client.post(URL, base_data)
        lead = Lead.objects.get(email="ahmed@test.com")
        assert lead.investor == investor

    def test_ip_and_user_agent_captured(self, client, base_data):
        client.post(URL, base_data, HTTP_USER_AGENT="MyBot/1.0", REMOTE_ADDR="1.2.3.4")
        lead = Lead.objects.get(email="ahmed@test.com")
        assert lead.ip_address == "1.2.3.4"
        assert "MyBot/1.0" in lead.user_agent


@pytest.mark.django_db
class TestLeadCreateHTMX:
    HX = {"HTTP_HX_REQUEST": "true"}

    def test_htmx_success_returns_modal_html(self, client, base_data):
        response = client.post(URL, base_data, **self.HX)
        assert response.status_code == 200
        assert "تم استلام طلبك".encode() in response.content
        # success partial — no <form hx-post=...> remains
        assert b"hx-post" not in response.content

    def test_htmx_validation_error_returns_form(self, client, base_data):
        response = client.post(URL, {**base_data, "phone": "x"}, **self.HX)
        assert response.status_code == 400
        # form re-rendered with errors
        assert b"hx-post" in response.content

    def test_htmx_get_returns_empty_form(self, client):
        response = client.get(URL, **self.HX)
        assert response.status_code == 200
        assert b"hx-post" in response.content


@pytest.mark.django_db
class TestRecaptchaIntegration:
    def test_recaptcha_failure_blocks_save(self, client, base_data):
        with patch("apps.leads.views.verify_recaptcha", return_value=(False, "low_score")):
            response = client.post(URL, base_data)
        assert response.status_code == 400
        assert "recaptcha" in response.json()["errors"]
        assert not Lead.objects.exists()

    def test_dev_mode_bypass_passes(self, client, base_data, settings):
        """No private key → passes (dev)."""
        settings.RECAPTCHA_PRIVATE_KEY = ""
        response = client.post(URL, base_data)
        assert response.status_code == 201


@pytest.mark.django_db
class TestRateLimit:
    """rate-limit يُفعَّل لهذا الـ class فقط."""

    @pytest.fixture(autouse=True)
    def _enable_ratelimit(self, settings):
        settings.RATELIMIT_ENABLE = True

    def test_sixth_request_returns_429(self, client, base_data):
        for _ in range(5):
            client.post(URL, base_data, REMOTE_ADDR="9.9.9.9")
        response = client.post(URL, base_data, REMOTE_ADDR="9.9.9.9")
        assert response.status_code == 429
