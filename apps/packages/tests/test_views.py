"""View tests — TESTING.md §Unit + API.md §Packages."""

import pytest
from django.urls import reverse

from apps.accounts.factories import InvestorFactory, ManagerFactory, SupervisorFactory
from apps.packages.factories import PackageFactory

# ── API: GET /api/packages/ ─────────────────────────────────────────────────


@pytest.mark.django_db
class TestPackageListAPI:
    URL = "/api/packages/"

    def test_anonymous_can_list(self, client):
        PackageFactory.create_batch(3)
        response = client.get(self.URL)
        assert response.status_code == 200

    def test_only_active_returned(self, client):
        PackageFactory(name="Active", is_active=True)
        PackageFactory(name="Hidden", is_active=False)
        response = client.get(self.URL)
        names = [pkg["name"] for pkg in response.json()["results"]]
        assert "Active" in names
        assert "Hidden" not in names

    def test_ordering_by_display_order(self, client):
        PackageFactory(name="Last", display_order=99)
        PackageFactory(name="First", display_order=1)
        response = client.get(self.URL)
        results = response.json()["results"]
        assert results[0]["name"] == "First"
        assert results[-1]["name"] == "Last"

    def test_response_shape_matches_api_contract(self, client):
        PackageFactory()
        response = client.get(self.URL)
        body = response.json()
        assert {"count", "next", "previous", "results"} <= set(body.keys())
        first = body["results"][0]
        for key in (
            "id",
            "name",
            "slug",
            "price",
            "duration_months",
            "features",
            "image_url",
            "is_featured",
        ):
            assert key in first


# ── API: GET /api/packages/<slug>/ ──────────────────────────────────────────


@pytest.mark.django_db
class TestPackageDetailAPI:
    def test_retrieve_by_slug(self, client):
        pkg = PackageFactory(name="X", slug="x-slug")
        response = client.get(f"/api/packages/{pkg.slug}/")
        assert response.status_code == 200
        assert response.json()["slug"] == "x-slug"

    def test_inactive_package_404(self, client):
        pkg = PackageFactory(slug="hidden", is_active=False)
        response = client.get(f"/api/packages/{pkg.slug}/")
        assert response.status_code == 404

    def test_nonexistent_404(self, client):
        response = client.get("/api/packages/does-not-exist/")
        assert response.status_code == 404


# ── HTML: GET /packages/ ────────────────────────────────────────────────────


@pytest.mark.django_db
class TestPackagesPage:
    URL = reverse("packages:list")

    def test_anonymous_renders_page(self, client):
        PackageFactory(name="ظاهرة")
        response = client.get(self.URL)
        assert response.status_code == 200
        assert "ظاهرة".encode() in response.content

    def test_empty_state_when_no_packages(self, client):
        response = client.get(self.URL)
        assert response.status_code == 200
        assert "لا توجد باقات معلَنة بعد".encode() in response.content

    def test_inactive_packages_hidden(self, client):
        PackageFactory(name="Visible", is_active=True)
        PackageFactory(name="Hidden", is_active=False)
        response = client.get(self.URL)
        body = response.content.decode()
        assert "Visible" in body
        assert "Hidden" not in body

    def test_package_image_rendered_from_model(self, client):
        pkg = PackageFactory(name="الباقة الذهبية", image="packages/package-gold.png")
        response = client.get(self.URL)
        body = response.content.decode()
        assert f'id="package-{pkg.slug}"' in body
        assert 'src="/media/packages/package-gold.png"' in body
        assert 'alt="صورة الباقة الذهبية"' in body

    def test_investor_supervisor_manager_can_view(self, client):
        """AllowAny — كل الأدوار تشاهد الباقات."""
        PackageFactory(name="P")
        for factory in (InvestorFactory, SupervisorFactory, ManagerFactory):
            client.force_login(factory())
            response = client.get(self.URL)
            assert response.status_code == 200
            client.logout()
