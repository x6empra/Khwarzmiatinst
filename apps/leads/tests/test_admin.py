"""Admin access tests for leads."""

from typing import cast

import pytest
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory
from django.urls import reverse

from apps.accounts.models import User
from apps.leads.admin import LeadAdmin
from apps.leads.models import Lead
from apps.packages.models import Package


def create_role_user(*, email: str, role: str) -> User:
    user_model = get_user_model()
    return cast(
        User,
        user_model.objects.create_user(
            email=email,
            password="Test1234!",
            first_name="Test",
            last_name="User",
            role=role,
        ),
    )


def create_package(*, slug: str) -> Package:
    return Package.objects.create(
        name=f"باقة {slug}",
        slug=slug,
        description="وصف الباقة",
        price="99.00",
        duration_months=1,
        features=["ميزة"],
    )


def create_lead(*, slug: str) -> Lead:
    return Lead.objects.create(
        name=f"طلب {slug}",
        phone="0501234567",
        email=f"{slug}@khawarizmiat.test",
        package=create_package(slug=slug),
    )


@pytest.mark.django_db
class TestLeadAdminAccess:
    def test_manager_can_open_leads_changelist(self, client: Client) -> None:
        create_lead(slug="manager-admin-lead")
        user = create_role_user(email="manager-admin@khawarizmiat.test", role="manager")
        client.force_login(user)

        response = client.get(reverse("admin:leads_lead_changelist"))

        assert response.status_code == 200

    def test_supervisor_can_open_leads_changelist(self, client: Client) -> None:
        create_lead(slug="supervisor-admin-lead")
        user = create_role_user(email="supervisor-admin@khawarizmiat.test", role="supervisor")
        client.force_login(user)

        response = client.get(reverse("admin:leads_lead_changelist"))

        assert response.status_code == 200

    def test_manager_can_open_lead_change_form(self, client: Client) -> None:
        lead = create_lead(slug="manager-admin-change")
        user = create_role_user(email="manager-change@khawarizmiat.test", role="manager")
        client.force_login(user)

        response = client.get(reverse("admin:leads_lead_change", args=[lead.pk]))

        assert response.status_code == 200

    def test_supervisor_can_open_lead_change_form(self, client: Client) -> None:
        lead = create_lead(slug="supervisor-admin-change")
        user = create_role_user(email="supervisor-change@khawarizmiat.test", role="supervisor")
        client.force_login(user)

        response = client.get(reverse("admin:leads_lead_change", args=[lead.pk]))

        assert response.status_code == 200

    def test_manager_can_open_lead_add_form(self, client: Client) -> None:
        user = create_role_user(email="manager-add@khawarizmiat.test", role="manager")
        client.force_login(user)

        response = client.get(reverse("admin:leads_lead_add"))

        assert response.status_code == 200

    def test_supervisor_can_open_lead_add_form(self, client: Client) -> None:
        user = create_role_user(email="supervisor-add@khawarizmiat.test", role="supervisor")
        client.force_login(user)

        response = client.get(reverse("admin:leads_lead_add"))

        assert response.status_code == 200

    def test_manager_has_delete_permission(self, rf: RequestFactory) -> None:
        user = create_role_user(email="manager-delete@khawarizmiat.test", role="manager")
        request = rf.get("/")
        request.user = user
        lead_admin = admin.site._registry[Lead]

        assert isinstance(lead_admin, LeadAdmin)
        assert lead_admin.has_delete_permission(request)

    def test_supervisor_has_delete_permission(self, rf: RequestFactory) -> None:
        user = create_role_user(email="supervisor-delete@khawarizmiat.test", role="supervisor")
        request = rf.get("/")
        request.user = user
        lead_admin = admin.site._registry[Lead]

        assert isinstance(lead_admin, LeadAdmin)
        assert lead_admin.has_delete_permission(request)

    def test_supervisor_can_open_lead_delete_confirmation(self, client: Client) -> None:
        lead = create_lead(slug="supervisor-admin-delete")
        user = create_role_user(email="supervisor-delete-form@khawarizmiat.test", role="supervisor")
        client.force_login(user)

        response = client.get(reverse("admin:leads_lead_delete", args=[lead.pk]))

        assert response.status_code == 200

    def test_investor_cannot_open_leads_changelist(self, client: Client) -> None:
        user = create_role_user(email="investor-admin@khawarizmiat.test", role="investor")
        client.force_login(user)

        response = client.get(reverse("admin:leads_lead_changelist"))

        assert response.status_code == 302
        assert response["Location"].startswith("/admin/login/")
