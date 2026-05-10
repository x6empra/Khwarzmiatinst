"""
Smoke tests — Phase 0.

تتأكد أن الإعدادات الأساسية تعمل قبل بناء أي ميزة.
TESTING.md §QA — Phase 0 baseline.
"""

import pytest
from django.test import Client
from django.urls import reverse


def test_settings_loaded():
    """Django يقرأ الإعدادات بدون أخطاء."""
    from django.conf import settings

    assert settings.LANGUAGE_CODE == "ar"
    assert settings.TIME_ZONE == "Asia/Riyadh"
    assert settings.USE_I18N is True
    assert settings.USE_TZ is True


def test_validators_importable():
    """validators المركزية متاحة."""
    from apps.core.validators import GULF_PHONE_REGEX, phone_validator

    assert GULF_PHONE_REGEX
    assert phone_validator is not None


@pytest.mark.parametrize(
    "phone,valid",
    [
        ("0501234567", True),
        ("00966501234567", True),
        ("+966501234567", True),
        ("966501234567", True),
        ("123", False),
        ("abc", False),
        ("0401234567", False),  # 04 not in regex
    ],
)
def test_phone_validator(phone, valid):
    """phone validator يقبل الصيغ السعودية/الخليجية الصحيحة فقط."""
    from django.core.exceptions import ValidationError

    from apps.core.validators import phone_validator

    if valid:
        phone_validator(phone)
    else:
        with pytest.raises(ValidationError):
            phone_validator(phone)


@pytest.mark.django_db
def test_healthz_endpoint():
    """endpoint للـ liveness probe يعمل."""
    client = Client()
    response = client.get(reverse("core:healthz"))
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "khawarizmiat"}


@pytest.mark.django_db
def test_landing_home_renders():
    """الصفحة الرئيسية (F1) تُعرض على /."""
    client = Client()
    response = client.get(reverse("landing:home"))
    assert response.status_code == 200
    assert "خوارزميات".encode() in response.content


def test_rtl_in_base_template():
    """base.html يحتوي dir=rtl."""
    template = (
        __import__("django.template.loader", fromlist=["get_template"])
        .get_template("base.html")
        .template.source
    )
    assert 'dir="rtl"' in template
    assert 'lang="ar"' in template
