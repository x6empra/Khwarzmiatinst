"""Package edit/create from Dashboard — Manager-only, features list parsing."""

import pytest
from django.urls import reverse

from apps.accounts.factories import (
    InvestorFactory,
    ManagerFactory,
    SupervisorFactory,
)
from apps.packages.factories import PackageFactory
from apps.packages.models import Package


@pytest.mark.django_db
class TestPackageEditPermissions:
    def test_anonymous_redirects(self, client):
        pkg = PackageFactory()
        response = client.get(reverse("dashboard:package_edit", args=[pkg.id]))
        assert response.status_code == 302

    def test_investor_403(self, client):
        pkg = PackageFactory()
        client.force_login(InvestorFactory())
        assert client.get(reverse("dashboard:package_edit", args=[pkg.id])).status_code == 403

    def test_supervisor_403(self, client):
        pkg = PackageFactory()
        client.force_login(SupervisorFactory())
        assert client.get(reverse("dashboard:package_edit", args=[pkg.id])).status_code == 403

    def test_manager_can_view(self, client):
        pkg = PackageFactory()
        client.force_login(ManagerFactory())
        response = client.get(reverse("dashboard:package_edit", args=[pkg.id]))
        assert response.status_code == 200


@pytest.mark.django_db
class TestPackageEdit:
    def _payload(self, pkg, **overrides):
        data = {
            "name": pkg.name,
            "slug": pkg.slug,
            "description": pkg.description,
            "price": str(pkg.price),
            "duration_months": pkg.duration_months,
            "display_order": pkg.display_order,
            "features": ["ميزة أ", "ميزة ب"],
        }
        # CheckboxInput يُرسَل فقط لو مفعّل
        if pkg.is_featured:
            data["is_featured"] = "on"
        if pkg.is_active:
            data["is_active"] = "on"
        data.update(overrides)
        return data

    def test_save_updates_features_as_json_list(self, client):
        client.force_login(ManagerFactory())
        pkg = PackageFactory(features=["قديم"])
        response = client.post(
            reverse("dashboard:package_edit", args=[pkg.id]),
            self._payload(pkg, features=["جديد 1", "جديد 2", "جديد 3"]),
        )
        assert response.status_code == 302
        pkg.refresh_from_db()
        assert pkg.features == ["جديد 1", "جديد 2", "جديد 3"]

    def test_empty_strings_in_features_stripped(self, client):
        client.force_login(ManagerFactory())
        pkg = PackageFactory(features=[])
        client.post(
            reverse("dashboard:package_edit", args=[pkg.id]),
            self._payload(pkg, features=["ميزة", "", "  ", "أخرى", "   "]),
        )
        pkg.refresh_from_db()
        assert pkg.features == ["ميزة", "أخرى"]

    def test_no_features_results_in_empty_list(self, client):
        client.force_login(ManagerFactory())
        pkg = PackageFactory(features=["قديم"])
        data = self._payload(pkg)
        data.pop("features")
        client.post(reverse("dashboard:package_edit", args=[pkg.id]), data)
        pkg.refresh_from_db()
        assert pkg.features == []

    def test_negative_price_rejected(self, client):
        client.force_login(ManagerFactory())
        pkg = PackageFactory()
        response = client.post(
            reverse("dashboard:package_edit", args=[pkg.id]),
            self._payload(pkg, price="-10"),
        )
        assert response.status_code == 200  # نموذج يُعاد عرضه بالأخطاء
        pkg.refresh_from_db()
        assert pkg.price != -10

    def test_zero_duration_rejected(self, client):
        client.force_login(ManagerFactory())
        pkg = PackageFactory(duration_months=6)
        response = client.post(
            reverse("dashboard:package_edit", args=[pkg.id]),
            self._payload(pkg, duration_months=0),
        )
        assert response.status_code == 200
        pkg.refresh_from_db()
        assert pkg.duration_months == 6

    def test_short_name_rejected(self, client):
        client.force_login(ManagerFactory())
        pkg = PackageFactory(name="الباقة الذهبية")
        response = client.post(
            reverse("dashboard:package_edit", args=[pkg.id]),
            self._payload(pkg, name="X"),
        )
        assert response.status_code == 200
        pkg.refresh_from_db()
        assert pkg.name == "الباقة الذهبية"

    def test_toggle_active_status(self, client):
        client.force_login(ManagerFactory())
        pkg = PackageFactory(is_active=True)
        data = self._payload(pkg)
        data.pop("is_active")  # checkbox غير مفعّل
        client.post(reverse("dashboard:package_edit", args=[pkg.id]), data)
        pkg.refresh_from_db()
        assert pkg.is_active is False

    def test_rendered_features_appear_in_form(self, client):
        client.force_login(ManagerFactory())
        pkg = PackageFactory(features=["unique-feature-text-123"])
        response = client.get(reverse("dashboard:package_edit", args=[pkg.id]))
        assert b"unique-feature-text-123" in response.content


@pytest.mark.django_db
class TestPackageCreate:
    URL = reverse("dashboard:package_create")

    def test_supervisor_403(self, client):
        client.force_login(SupervisorFactory())
        assert client.get(self.URL).status_code == 403

    def test_manager_can_view_empty_form(self, client):
        client.force_login(ManagerFactory())
        assert client.get(self.URL).status_code == 200

    def test_create_with_features(self, client):
        client.force_login(ManagerFactory())
        response = client.post(
            self.URL,
            {
                "name": "باقة بلاتينية جديدة",
                "slug": "platinum",
                "description": "وصف الباقة",
                "price": "4999.00",
                "duration_months": 12,
                "display_order": 0,
                "features": ["دعم 24/7", "تكامل مدفوعات"],
                "is_active": "on",
            },
        )
        assert response.status_code == 302
        pkg = Package.objects.get(slug="platinum")
        assert pkg.features == ["دعم 24/7", "تكامل مدفوعات"]
        assert pkg.is_active is True
