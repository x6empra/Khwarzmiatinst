"""Site settings tests — admin-managed public contact/social settings."""

import pytest
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.urls import reverse

from apps.core.context_processors import site_settings
from apps.core.models import DEFAULT_COPYRIGHT_TEXT, SiteSettings


@pytest.mark.django_db
class TestSiteSettingsModel:
    def test_default_load_without_database_record(self) -> None:
        settings = SiteSettings.load()

        assert settings.pk is None
        assert settings.copyright_text == DEFAULT_COPYRIGHT_TEXT
        assert settings.has_social_links is False

    def test_contact_and_whatsapp_links_are_normalized(self) -> None:
        settings = SiteSettings.objects.create(
            contact_phone="0501234567",
            whatsapp_number="+966501234567",
        )

        assert settings.contact_phone_href == "tel:+966501234567"
        assert settings.whatsapp_url == "https://wa.me/966501234567"

    def test_only_one_settings_record_allowed(self) -> None:
        SiteSettings.objects.create(contact_phone="0501234567")

        with pytest.raises(ValidationError):
            SiteSettings.objects.create(whatsapp_number="0507654321")

    def test_social_links_state(self) -> None:
        settings = SiteSettings.objects.create(instagram_url="https://instagram.com/khawarizmiat")

        assert settings.has_social_links is True

    def test_invalid_phone_rejected(self) -> None:
        settings = SiteSettings(contact_phone="123")

        with pytest.raises(ValidationError):
            settings.full_clean()


@pytest.mark.django_db
class TestSiteSettingsAdmin:
    def test_site_settings_registered_in_django_admin(self) -> None:
        assert SiteSettings in admin.site._registry


@pytest.mark.django_db
class TestSiteSettingsContext:
    def test_context_processor_returns_settings(self, rf) -> None:
        SiteSettings.objects.create(contact_phone="0501234567")

        context = site_settings(rf.get("/"))

        assert context["site_settings"].contact_phone == "0501234567"


@pytest.mark.django_db
class TestSiteSettingsRendering:
    def test_footer_contact_links_render_from_settings(self, client) -> None:
        SiteSettings.objects.create(
            contact_phone="0501234567",
            whatsapp_number="0507654321",
            snapchat_url="https://snapchat.com/add/khawarizmiat",
            x_url="https://x.com/khawarizmiat",
            instagram_url="https://instagram.com/khawarizmiat",
            tiktok_url="https://www.tiktok.com/@khawarizmiat",
            copyright_text="خدمات خوارزميات · جميع الحقوق محفوظة",
        )

        body = client.get(reverse("landing:home")).content.decode()

        assert "tel:+966501234567" in body
        assert "https://wa.me/966507654321" in body
        assert ">واتساب<" in body
        assert 'aria-label="تواصل عبر واتساب"' not in body
        assert "fixed bottom-5" not in body
        assert 'aria-label="سناب شات"' in body
        assert 'aria-label="X"' in body
        assert 'aria-label="إنستقرام"' in body
        assert 'aria-label="تيك توك"' in body
        assert "خدمات خوارزميات · جميع الحقوق محفوظة" in body

    def test_footer_hides_empty_optional_links(self, client) -> None:
        body = client.get(reverse("landing:home")).content.decode()

        assert 'aria-label="تواصل عبر واتساب"' not in body
        assert 'aria-label="سناب شات"' not in body
        assert DEFAULT_COPYRIGHT_TEXT in body
