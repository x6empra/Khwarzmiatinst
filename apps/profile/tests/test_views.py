"""Profile views tests — F9 + F10 (PERMISSIONS.md §Pages)."""

import pytest
from django.urls import reverse

from apps.accounts.factories import (
    InvestorFactory,
    ManagerFactory,
    SupervisorFactory,
)
from apps.leads.factories import LeadFactory


@pytest.mark.django_db
class TestOverview:
    URL = reverse("investor_profile:overview")

    def test_anonymous_redirects(self, client):
        response = client.get(self.URL)
        assert response.status_code == 302
        assert response.url.startswith("/accounts/")

    def test_short_profile_url_redirects_anonymous(self, client):
        response = client.get("/profile")
        assert response.status_code == 302
        assert response.url.startswith("/accounts/")

    def test_short_profile_url_investor_can_view(self, client):
        client.force_login(InvestorFactory(email="short@x.com"))
        response = client.get("/profile")
        assert response.status_code == 200
        assert (
            b"\xd8\xa8\xd9\x8a\xd8\xa7\xd9\x86\xd8\xa7\xd8\xaa\xd9\x8a" in response.content
        )  # "بياناتي"

    def test_supervisor_403(self, client):
        client.force_login(SupervisorFactory())
        assert client.get(self.URL).status_code == 403

    def test_manager_403(self, client):
        client.force_login(ManagerFactory())
        assert client.get(self.URL).status_code == 403

    def test_investor_can_view(self, client):
        client.force_login(InvestorFactory(email="me@x.com"))
        response = client.get(self.URL)
        assert response.status_code == 200
        assert (
            b"\xd8\xa8\xd9\x8a\xd8\xa7\xd9\x86\xd8\xa7\xd8\xaa\xd9\x8a" in response.content
        )  # "بياناتي"

    def test_post_updates_profile(self, client):
        user = InvestorFactory(email="me@x.com", first_name="قديم")
        client.force_login(user)
        response = client.post(
            self.URL,
            {
                "first_name": "جديد",
                "last_name": "اسم",
                "phone": "0501234567",
                "company_name": "معهد التميّز",
                "city": "الرياض",
                "bio": "نبذة قصيرة",
            },
        )
        assert response.status_code == 302
        user.refresh_from_db()
        user.profile.refresh_from_db()
        assert user.first_name == "جديد"
        assert user.phone == "0501234567"
        assert user.profile.company_name == "معهد التميّز"

    def test_invalid_phone_rejected(self, client):
        user = InvestorFactory()
        client.force_login(user)
        response = client.post(
            self.URL,
            {
                "first_name": "x",
                "last_name": "y",
                "phone": "INVALID",
                "company_name": "",
                "city": "",
                "bio": "",
            },
        )
        assert response.status_code == 200
        assert b"\xd8\xb1\xd9\x82\xd9\x85" in response.content  # "رقم"


@pytest.mark.django_db
class TestPasswordChange:
    URL = reverse("investor_profile:password")

    def test_supervisor_403(self, client):
        client.force_login(SupervisorFactory())
        assert client.get(self.URL).status_code == 403

    def test_investor_can_view(self, client):
        client.force_login(InvestorFactory())
        assert client.get(self.URL).status_code == 200

    def test_short_url_investor_can_view(self, client):
        client.force_login(InvestorFactory(email="password-short@x.com"))
        response = client.get("/profile/password")
        assert response.status_code == 200

    def test_changes_password(self, client):
        user = InvestorFactory(email="me@x.com", password="OldP@ss123")
        client.force_login(user)
        response = client.post(
            self.URL,
            {
                "old_password": "OldP@ss123",
                "new_password1": "NewP@ssw0rd!",
                "new_password2": "NewP@ssw0rd!",
            },
        )
        assert response.status_code == 302
        user.refresh_from_db()
        assert user.check_password("NewP@ssw0rd!")

    def test_wrong_old_password_rejected(self, client):
        user = InvestorFactory(email="me@x.com", password="OldP@ss123")
        client.force_login(user)
        response = client.post(
            self.URL,
            {
                "old_password": "WRONG",
                "new_password1": "NewP@ssw0rd!",
                "new_password2": "NewP@ssw0rd!",
            },
        )
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.check_password("OldP@ss123")  # لم تتغيّر

    def test_session_preserved_after_change(self, client):
        user = InvestorFactory(email="me@x.com", password="OldP@ss123")
        client.force_login(user)
        client.post(
            self.URL,
            {
                "old_password": "OldP@ss123",
                "new_password1": "NewP@ssw0rd!",
                "new_password2": "NewP@ssw0rd!",
            },
        )
        # المستخدم لا يزال مسجَّلاً
        assert "_auth_user_id" in client.session


@pytest.mark.django_db
class TestOrders:
    URL = reverse("investor_profile:orders")

    def test_supervisor_403(self, client):
        client.force_login(SupervisorFactory())
        assert client.get(self.URL).status_code == 403

    def test_short_url_investor_can_view(self, client):
        client.force_login(InvestorFactory(email="orders-short@x.com"))
        response = client.get("/profile/orders")
        assert response.status_code == 200

    def test_investor_sees_only_own(self, client):
        from apps.packages.factories import PackageFactory

        me = InvestorFactory(email="me@x.com")
        other = InvestorFactory(email="other@x.com")
        my_pkg = PackageFactory(name="MyPackage")
        their_pkg = PackageFactory(name="TheirPackage")
        LeadFactory(investor=me, package=my_pkg)
        LeadFactory(investor=other, package=their_pkg)

        client.force_login(me)
        response = client.get(self.URL)
        body = response.content.decode()
        assert "MyPackage" in body
        assert "TheirPackage" not in body

    def test_empty_state_no_orders(self, client):
        client.force_login(InvestorFactory())
        response = client.get(self.URL)
        assert response.status_code == 200
        assert "لم تقدّم أي طلب بعد".encode() in response.content

    def test_orders_render(self, client):
        me = InvestorFactory()
        client.force_login(me)
        LeadFactory(investor=me)
        response = client.get(self.URL)
        assert response.status_code == 200
