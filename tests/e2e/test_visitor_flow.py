"""
E2E — Visitor flow (TESTING.md §E2E).

السيناريو 1: زائر يفتح / ويرى Hero + الباقات.
السيناريو 2: زائر يملأ نموذج الحجز ويرسل (HTMX).
السيناريو 8: محاولة spam → reCAPTCHA يرفض.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.django_db(transaction=True)


def test_visitor_sees_hero_and_packages(page: Page, live_server_url: str, seeded_packages) -> None:
    """السيناريو 1: زائر يفتح / ويرى Hero + الباقات."""
    page.goto(live_server_url + "/")

    # Hero — title page + h1 موجود
    import re

    expect(page).to_have_title(re.compile(r"خوارزميات"))
    expect(page.locator("#hero-title")).to_be_visible()

    # 3 باقات نشطة فقط (المخفية لا تظهر)
    expect(page.get_by_text("الباقة الذهبية").first).to_be_visible()
    expect(page.get_by_text("الباقة الفضية").first).to_be_visible()
    expect(page.get_by_text("الباقة البرونزية").first).to_be_visible()
    expect(page.get_by_text("مخفية")).to_have_count(0)

    # Booking section
    expect(page.locator("#booking-form")).to_be_visible()


def test_visitor_submits_lead_form_htmx(page: Page, live_server_url: str, seeded_packages) -> None:
    """السيناريو 2: زائر يملأ النموذج ويرسل (HTMX) → Modal أخضر + Lead في DB."""
    page.goto(live_server_url + "/#booking")

    page.fill('input[name="name"]', "أحمد المختبِر")
    page.fill('input[name="phone"]', "0501234567")
    page.fill('input[name="email"]', "ahmed.e2e@test.com")
    page.select_option('select[name="package"]', label="الباقة الذهبية")
    page.fill('textarea[name="notes"]', "اختبار E2E")

    page.click('#booking-form button[type="submit"]')

    # Success Modal
    expect(page.get_by_text("تم استلام طلبك")).to_be_visible(timeout=5_000)

    # Lead in DB
    from apps.leads.models import Lead

    assert Lead.objects.filter(email="ahmed.e2e@test.com").exists()


def test_visitor_invalid_phone_shows_error(
    page: Page, live_server_url: str, seeded_packages
) -> None:
    """السيناريو 8 جزئي: phone غير صالح → النموذج يعيد عرض الخطأ inline."""
    page.goto(live_server_url + "/#booking")

    page.fill('input[name="name"]', "خطأ")
    page.fill('input[name="phone"]', "INVALID")
    page.fill('input[name="email"]', "bad@test.com")
    page.select_option('select[name="package"]', label="الباقة الذهبية")

    page.click('#booking-form button[type="submit"]')

    # Form يبقى موجوداً — الخطأ تحت حقل phone
    expect(page.locator('input[name="phone"]')).to_be_visible(timeout=5_000)
    # رسالة الخطأ تأتي كـ <p role="alert"> — أي rule لها يبدأ بـ "رقم الجوال"
    error_alerts = page.locator('p[role="alert"]')
    expect(error_alerts.first).to_be_visible(timeout=5_000)
