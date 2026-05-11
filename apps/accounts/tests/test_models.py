"""Model tests — TESTING.md §Unit."""

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from apps.accounts.models import Role

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    def test_create_user_defaults_to_investor(self):
        user = User.objects.create_user(
            email="a@b.com", password="Strong1!@", first_name="x", last_name="y"
        )
        assert user.role == Role.INVESTOR
        assert user.is_investor
        assert not user.is_supervisor
        assert not user.is_manager
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser

    def test_create_supervisor_is_staff(self):
        """Signal: supervisor → is_staff=True تلقائياً."""
        user = User.objects.create_user(
            email="s@b.com",
            password="Strong1!@",
            first_name="x",
            last_name="y",
            role=Role.SUPERVISOR,
        )
        assert user.is_supervisor
        assert user.is_staff_role
        assert user.is_staff is True

    def test_create_manager_is_staff(self):
        user = User.objects.create_user(
            email="m@b.com", password="Strong1!@", first_name="x", last_name="y", role=Role.MANAGER
        )
        assert user.is_manager
        assert user.is_staff is True

    def test_email_required(self):
        with pytest.raises(ValueError, match="الإيميل مطلوب"):
            User.objects.create_user(email="", password="pwd", first_name="x", last_name="y")

    def test_email_normalized(self):
        user = User.objects.create_user(
            email="A@B.COM", password="Strong1!@", first_name="x", last_name="y"
        )
        assert user.email == "A@b.com"

    def test_email_unique(self):
        User.objects.create_user(
            email="dup@x.com", password="Strong1!@", first_name="x", last_name="y"
        )
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                email="dup@x.com", password="Strong1!@", first_name="x", last_name="y"
            )

    def test_full_name(self):
        user = User(first_name="أحمد", last_name="محمد")
        assert user.full_name == "أحمد محمد"
        assert user.get_full_name() == "أحمد محمد"
        assert user.get_short_name() == "أحمد"

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            email="admin@x.com", password="Strong1!@", first_name="A", last_name="B"
        )
        assert admin.is_staff
        assert admin.is_superuser
        assert admin.role == Role.MANAGER

    def test_manager_filters(self):
        User.objects.create_user(
            email="i@x.com", password="Strong1!@", first_name="x", last_name="y", role=Role.INVESTOR
        )
        User.objects.create_user(
            email="s@x.com",
            password="Strong1!@",
            first_name="x",
            last_name="y",
            role=Role.SUPERVISOR,
        )
        User.objects.create_user(
            email="m@x.com", password="Strong1!@", first_name="x", last_name="y", role=Role.MANAGER
        )

        assert User.objects.investors().count() == 1
        assert User.objects.supervisors().count() == 1
        assert User.objects.managers().count() == 1
        assert User.objects.staff_roles().count() == 2
