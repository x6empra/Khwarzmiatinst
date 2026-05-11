"""View tests — TESTING.md §Unit."""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.accounts.factories import InvestorFactory


@pytest.mark.django_db
class TestRegisterView:
    def test_get_renders_form(self, client):
        response = client.get(reverse("accounts:register"))
        assert response.status_code == 200
        assert b"\xd8\xa5\xd9\x86\xd8\xb4\xd8\xa7\xd8\xa1" in response.content  # "إنشاء"

    def test_post_creates_user_and_logs_in(self, client):
        response = client.post(
            reverse("accounts:register"),
            {
                "first_name": "أحمد",
                "last_name": "محمد",
                "email": "new@test.com",
                "phone": "0501234567",
                "password1": "StrongP@ss123",
                "password2": "StrongP@ss123",
            },
        )
        assert response.status_code == 302  # redirect
        user_model = get_user_model()
        assert user_model.objects.filter(email="new@test.com").exists()
        # session-cookie يثبت تسجيل الدخول التلقائي
        assert "_auth_user_id" in client.session


@pytest.mark.django_db
class TestLoginView:
    def test_login_success(self, client):
        InvestorFactory(email="ok@test.com", password="MyP@ssw0rd")
        response = client.post(
            reverse("accounts:login"),
            {"email": "ok@test.com", "password": "MyP@ssw0rd"},
        )
        assert response.status_code == 302
        assert "_auth_user_id" in client.session

    def test_login_failure_renders_errors(self, client):
        response = client.post(
            reverse("accounts:login"),
            {"email": "bad@test.com", "password": "wrong"},
        )
        assert response.status_code == 200
        assert "_auth_user_id" not in client.session

    def test_remember_me_extends_session(self, client):
        InvestorFactory(email="r@test.com", password="MyP@ssw0rd")
        client.post(
            reverse("accounts:login"),
            {"email": "r@test.com", "password": "MyP@ssw0rd", "remember_me": "on"},
        )
        # 30 days = 2_592_000s
        assert client.session.get_expiry_age() > 29 * 24 * 3600

    def test_authenticated_redirected_from_login(self, client):
        user = InvestorFactory(email="me@test.com", password="MyP@ssw0rd")
        client.force_login(user)
        response = client.get(reverse("accounts:login"))
        assert response.status_code == 302


@pytest.mark.django_db
class TestLogoutView:
    def test_logout_clears_session(self, client):
        user = InvestorFactory(email="me@test.com", password="MyP@ssw0rd")
        client.force_login(user)
        assert "_auth_user_id" in client.session

        response = client.post(reverse("accounts:logout"))
        assert response.status_code == 302
        assert "_auth_user_id" not in client.session

    def test_logout_get_not_allowed(self, client):
        user = InvestorFactory()
        client.force_login(user)
        response = client.get(reverse("accounts:logout"))
        assert response.status_code == 405  # Method not allowed
