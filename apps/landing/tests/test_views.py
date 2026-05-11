"""Landing F1 tests — TESTING.md §Unit + INFRASTRUCTURE.md §3."""

import pytest
from django.test import Client
from django.urls import reverse

from apps.packages.factories import PackageFactory


@pytest.mark.django_db
class TestLandingPage:
    URL = reverse("landing:home")

    def test_anonymous_renders_200(self, client):
        response = client.get(self.URL)
        assert response.status_code == 200

    def test_all_main_sections_present(self, client):
        response = client.get(self.URL)
        body = response.content.decode()
        # Section IDs (anchors)
        assert 'id="hero-title"' in body or 'id="hero-' in body  # Hero
        assert 'id="features-title"' in body  # Features
        assert 'id="packages-title"' in body  # Packages
        assert 'id="faq-title"' in body  # FAQ
        assert 'id="booking-title"' in body  # Booking

    def test_packages_appear(self, client):
        PackageFactory(name="ZooPackage", display_order=1)
        response = client.get(self.URL)
        assert b"ZooPackage" in response.content

    def test_lead_form_embedded(self, client):
        response = client.get(self.URL)
        body = response.content.decode()
        assert "booking-form-container" in body
        assert "/api/leads/create/" in body

    def test_faqs_rendered(self, client):
        response = client.get(self.URL)
        # هل العنوان الأول من FAQS موجود؟
        assert "كيف تعمل خوارزميات؟".encode() in response.content

    def test_hero_video_background_present(self, client):
        body = client.get(self.URL).content.decode()
        assert "<video" in body
        assert "autoplay" in body
        assert "muted" in body
        assert "loop" in body
        assert "playsinline" in body
        assert "controls" not in body
        assert "videos/hero-training.webm" in body
        assert "videos/hero-training-poster.jpg" in body

    def test_mobile_header_navigation_uses_dropdown(self, client: Client) -> None:
        body = client.get(self.URL).content.decode()
        assert 'aria-label="فتح قائمة التنقل"' in body
        assert "md:hidden" in body
        assert "md:flex" in body
        assert "[&::-webkit-details-marker]:hidden" in body


@pytest.mark.django_db
class TestSEOMeta:
    URL = reverse("landing:home")

    def test_open_graph_tags(self, client):
        body = client.get(self.URL).content.decode()
        assert 'property="og:title"' in body
        assert 'property="og:description"' in body
        assert 'property="og:type"' in body
        assert 'property="og:locale"' in body
        assert 'property="og:url"' in body

    def test_twitter_card(self, client):
        body = client.get(self.URL).content.decode()
        assert 'name="twitter:card"' in body

    def test_canonical_link(self, client):
        body = client.get(self.URL).content.decode()
        assert 'rel="canonical"' in body

    def test_schema_org_jsonld_present(self, client):
        """Organization + Service + FAQPage."""
        body = client.get(self.URL).content.decode()
        assert "application/ld+json" in body
        assert '"@type": "Organization"' in body
        assert '"@type": "Service"' in body
        assert '"@type": "FAQPage"' in body

    def test_robots_meta_indexable(self, client):
        body = client.get(self.URL).content.decode()
        assert 'name="robots"' in body
        assert "index,follow" in body


@pytest.mark.django_db
class TestSitemap:
    def test_sitemap_xml_accessible(self, client):
        response = client.get("/sitemap.xml")
        assert response.status_code == 200
        assert b"<?xml" in response.content
        assert b"<urlset" in response.content

    def test_sitemap_includes_landing(self, client):
        response = client.get("/sitemap.xml")
        assert b"<loc>" in response.content


class TestRobotsTxt:
    def test_robots_txt_accessible(self, client):
        response = client.get("/robots.txt")
        assert response.status_code == 200
        assert response["Content-Type"].startswith("text/plain")

    def test_robots_disallows_admin_dashboard_api(self, client):
        body = client.get("/robots.txt").content.decode()
        assert "Disallow: /admin/" in body
        assert "Disallow: /dashboard/" in body
        assert "Disallow: /api/" in body

    def test_robots_links_sitemap(self, client):
        body = client.get("/robots.txt").content.decode()
        assert "Sitemap:" in body
        assert "/sitemap.xml" in body


@pytest.mark.django_db
class TestSplineFallback:
    """DESIGN_GUIDE.md §Spline tip — graceful fallback."""

    URL = reverse("landing:home")

    def test_no_spline_url_uses_fallback(self, client, settings):
        settings.SPLINE_SCENE_URL = ""
        body = client.get(self.URL).content.decode()
        # data-spline-url موجود لكن فارغ
        assert 'data-spline-url=""' in body
        # CSS fallback (hero-fallback class) موجود
        assert "hero-fallback" in body

    def test_with_spline_url_lazy_loads(self, client, settings):
        settings.SPLINE_SCENE_URL = "https://prod.spline.design/test/scene.splinecode"
        body = client.get(self.URL).content.decode()
        assert 'data-spline-url="https://prod.spline.design/test/scene.splinecode"' in body
        # script lazy-loader موجود
        assert "spline-viewer" in body

    def test_reduced_motion_css_present(self, client):
        body = client.get(self.URL).content.decode()
        assert "prefers-reduced-motion" in body
