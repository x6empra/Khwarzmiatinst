"""Form tests — TESTING.md §Unit."""

from typing import ClassVar

import pytest

from apps.accounts.factories import UserFactory
from apps.accounts.forms import LoginForm, RegisterForm


@pytest.mark.django_db
class TestRegisterForm:
    BASE: ClassVar[dict[str, str]] = {
        "first_name": "أحمد",
        "last_name": "محمد",
        "email": "ahmed@test.com",
        "phone": "0501234567",
        "password1": "StrongP@ss123",
        "password2": "StrongP@ss123",
    }

    def test_valid_form_creates_investor(self):
        form = RegisterForm(self.BASE)
        assert form.is_valid(), form.errors
        user = form.save()
        assert user.role == "investor"
        assert user.check_password("StrongP@ss123")

    def test_passwords_must_match(self):
        data = {**self.BASE, "password2": "MisMatch!1"}
        form = RegisterForm(data)
        assert not form.is_valid()
        assert "password2" in form.errors

    def test_short_password_rejected(self):
        data = {**self.BASE, "password1": "abc", "password2": "abc"}
        form = RegisterForm(data)
        assert not form.is_valid()

    def test_invalid_phone_rejected(self):
        data = {**self.BASE, "phone": "12345"}
        form = RegisterForm(data)
        assert not form.is_valid()
        assert "phone" in form.errors

    def test_duplicate_email_rejected(self):
        UserFactory(email="ahmed@test.com")
        form = RegisterForm(self.BASE)
        assert not form.is_valid()
        assert "email" in form.errors

    def test_role_cannot_be_overridden_from_form(self):
        """حتى لو أرسل المهاجم role=manager، يبقى investor."""
        data = {**self.BASE, "role": "manager"}
        form = RegisterForm(data)
        assert form.is_valid()
        user = form.save()
        assert user.role == "investor"


@pytest.mark.django_db
class TestLoginForm:
    def test_valid_credentials(self, rf):
        UserFactory(email="login@test.com", password="MyP@ssw0rd")
        form = LoginForm({"email": "login@test.com", "password": "MyP@ssw0rd"}, request=rf.get("/"))
        assert form.is_valid()
        assert form.get_user() is not None

    def test_invalid_credentials(self, rf):
        UserFactory(email="login@test.com", password="MyP@ssw0rd")
        form = LoginForm({"email": "login@test.com", "password": "wrong"}, request=rf.get("/"))
        assert not form.is_valid()

    def test_inactive_user_rejected(self, rf):
        UserFactory(email="off@test.com", password="MyP@ssw0rd", is_active=False)
        form = LoginForm({"email": "off@test.com", "password": "MyP@ssw0rd"}, request=rf.get("/"))
        assert not form.is_valid()
